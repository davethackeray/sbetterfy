from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify, flash
import uuid
from spotify_service import SpotifyService
from user_service import UserService
import os

auth_bp = Blueprint('auth', __name__)
user_service = UserService()

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))
    return render_template('index.html')

@auth_bp.route('/login')
def login():
    user_id = str(uuid.uuid4())  # Generate temp ID until Spotify auth
    session['temp_user_id'] = user_id
    return render_template('setup_spotify.html', base_url=os.environ.get('BASE_URL', request.url_root.rstrip('/')))

@auth_bp.route('/authorize-spotify')
def authorize_spotify():
    user_id = session.get('temp_user_id', session.get('user_id'))
    if not user_id:
        flash("Session expired or invalid. Please start over.", "error")
        return redirect(url_for('auth.login'))
    
    creds = user_service.get_spotify_credentials(user_id)
    if not creds:
        flash("Spotify credentials not found. Please set up your credentials first.", "error")
        return redirect(url_for('auth.login'))
    
    sp = SpotifyService(creds['client_id'], creds['client_secret'])
    return redirect(sp.get_auth_url(user_id))

@auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        flash("Authorization code not received from Spotify. Please try again.", "error")
        return redirect(url_for('auth.index'))
    
    # Verify state matches user_id
    user_id = state
    if not user_id:
        flash("Invalid state parameter. Please try again.", "error")
        return redirect(url_for('auth.index'))
    
    # Get Spotify credentials
    creds = user_service.get_spotify_credentials(user_id)
    if not creds:
        flash("Spotify credentials not found. Please set up your credentials.", "error")
        return redirect(url_for('auth.login'))
    
    # Exchange code for tokens
    sp = SpotifyService(creds['client_id'], creds['client_secret'])
    tokens = sp.get_tokens(code)
    if not tokens:
        flash("Failed to obtain tokens from Spotify. Please check your credentials and try again.", "error")
        return redirect(url_for('auth.login'))
    
    # Get user profile
    user_profile = sp.get_user_profile(tokens['access_token'])
    if not user_profile:
        flash("Failed to retrieve user profile from Spotify. Please try again.", "error")
        return redirect(url_for('auth.login'))
    
    # Save user and tokens
    spotify_user_id = user_profile['id']
    try:
        user_service.save_spotify_tokens(user_id, tokens)
    except Exception as e:
        flash(f"Error saving Spotify tokens: {str(e)}. Please try again.", "error")
        return redirect(url_for('auth.login'))
    
    # Set session
    session.pop('temp_user_id', None)
    session['user_id'] = user_id
    session['spotify_user_id'] = spotify_user_id
    session['display_name'] = user_profile.get('display_name', spotify_user_id)
    
    flash("Successfully connected to Spotify!", "success")
    # Check if user has Google AI API key
    if user_service.has_gemini_api_key(user_id):
        return redirect(url_for('auth.dashboard'))
    else:
        return redirect(url_for('auth.setup_api'))

@auth_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for('auth.index'))
    
    user_id = session['user_id']
    has_api_key = user_service.has_gemini_api_key(user_id)
    
    return render_template('dashboard.html', 
                          display_name=session.get('display_name', 'User'),
                          has_api_key=has_api_key)

@auth_bp.route('/setup-api')
def setup_api():
    if 'user_id' not in session:
        flash("Please log in to set up API keys.", "error")
        return redirect(url_for('auth.index'))
    
    return render_template('setup_api.html')

@auth_bp.route('/setup-spotify')
def setup_spotify():
    if 'temp_user_id' not in session and 'user_id' not in session:
        flash("Session expired. Please start over.", "error")
        return redirect(url_for('auth.login'))
    
    base_url = os.environ.get('BASE_URL', request.url_root.rstrip('/'))
    return render_template('setup_spotify.html', base_url=base_url)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.index'))
