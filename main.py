from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import os
from dotenv import load_dotenv
import secrets
import uuid
from spotify_service import SpotifyService
from recommendation_service import RecommendationService
from user_service import UserService
from database import init_db

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

# Initialize database
init_db()

# Initialize user service
user_service = UserService()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login')
def login():
    user_id = str(uuid.uuid4())  # Generate temp ID until Spotify auth
    session['temp_user_id'] = user_id
    return render_template('setup_spotify.html', base_url=os.environ.get('BASE_URL', request.url_root.rstrip('/')))

@app.route('/api/save-spotify-creds', methods=['POST'])
def save_spotify_creds():
    if 'temp_user_id' not in session and 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
        
    user_id = session.get('user_id', session.get('temp_user_id'))
    data = request.json
    client_id = data.get('client_id')
    client_secret = data.get('client_secret')
    
    if not client_id or not client_secret:
        return jsonify({"error": "Client ID and Client Secret are required"}), 400
    
    # Validate credentials
    sp = SpotifyService(client_id, client_secret)
    if not sp.validate_credentials():
        return jsonify({"error": "Invalid Spotify credentials"}), 400
    
    user_service.save_spotify_credentials(user_id, client_id, client_secret)
    return jsonify({"status": "success"})

@app.route('/authorize-spotify')
def authorize_spotify():
    user_id = session.get('temp_user_id', session.get('user_id'))
    if not user_id:
        return redirect(url_for('login'))
    
    creds = user_service.get_spotify_credentials(user_id)
    if not creds:
        return redirect(url_for('login'))
    
    sp = SpotifyService(creds['client_id'], creds['client_secret'])
    return redirect(sp.get_auth_url(user_id))

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        return redirect(url_for('index'))
    
    # Verify state matches user_id
    user_id = state
    if not user_id:
        return redirect(url_for('index'))
    
    # Get Spotify credentials
    creds = user_service.get_spotify_credentials(user_id)
    if not creds:
        return redirect(url_for('login'))
    
    # Exchange code for tokens
    sp = SpotifyService(creds['client_id'], creds['client_secret'])
    tokens = sp.get_tokens(code)
    if not tokens:
        return redirect(url_for('login'))
    
    # Get user profile
    user_profile = sp.get_user_profile(tokens['access_token'])
    if not user_profile:
        return redirect(url_for('login'))
    
    # Save user and tokens
    spotify_user_id = user_profile['id']
    user_service.save_spotify_tokens(user_id, tokens)
    
    # Set session
    session.pop('temp_user_id', None)
    session['user_id'] = user_id
    session['spotify_user_id'] = spotify_user_id
    session['display_name'] = user_profile.get('display_name', spotify_user_id)
    
    # Check if user has Google AI API key
    if user_service.has_gemini_api_key(user_id):
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('setup_api'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    has_api_key = user_service.has_gemini_api_key(user_id)
    
    return render_template('dashboard.html', 
                          display_name=session.get('display_name', 'User'),
                          has_api_key=has_api_key)

@app.route('/setup-api')
def setup_api():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    return render_template('setup_api.html')

@app.route('/setup-spotify')
def setup_spotify():
    if 'temp_user_id' not in session and 'user_id' not in session:
        return redirect(url_for('login'))
    
    base_url = os.environ.get('BASE_URL', request.url_root.rstrip('/'))
    return render_template('setup_spotify.html', base_url=base_url)

@app.route('/api/save-api-key', methods=['POST'])
def save_api_key():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({"error": "API key is required"}), 400
    
    # Validate API key
    recommendation_service = RecommendationService(api_key)
    if not recommendation_service.validate_api_key():
        return jsonify({"error": "Invalid Google AI API key"}), 400
    
    # Save API key
    user_service.save_gemini_api_key(session['user_id'], api_key)
    
    return jsonify({"status": "success"})

@app.route('/api/validate-spotify-creds')
def validate_spotify_creds():
    user_id = session.get('user_id', session.get('temp_user_id'))
    if not user_id:
        return jsonify({"valid": False})
        
    creds = user_service.get_spotify_credentials(user_id)
    if not creds:
        return jsonify({"valid": False})
        
    try:
        sp = SpotifyService(creds['client_id'], creds['client_secret'])
        if sp.validate_credentials():
            return jsonify({"valid": True})
        return jsonify({"valid": False})
    except:
        return jsonify({"valid": False})

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session['user_id']
    
    # Get API key
    gemini_api_key = user_service.get_gemini_api_key(user_id)
    if not gemini_api_key:
        return jsonify({"error": "Google AI API key not set"}), 400
    
    # Get Spotify credentials and tokens
    spotify_creds = user_service.get_spotify_credentials(user_id)
    if not spotify_creds:
        return jsonify({"error": "Spotify credentials not set"}), 400
        
    spotify_tokens = user_service.get_spotify_tokens(user_id)
    if not spotify_tokens:
        return jsonify({"error": "Spotify authentication failed"}), 400
    
    # Get request data
    data = request.json
    count = int(data.get('count', 20))
    discovery_level = int(data.get('discovery_level', 50))
    min_year = int(data.get('min_year', 1900))
    max_popularity = int(data.get('max_popularity', 100))
    genres = data.get('genres', [])
    moods = data.get('moods', [])
    
    # Initialize services
    spotify = SpotifyService(
        spotify_creds['client_id'], 
        spotify_creds['client_secret'], 
        spotify_tokens
    )
    recommendation_service = RecommendationService(gemini_api_key)
    
    # Get recommendations
    try:
        recommendations = recommendation_service.get_recommendations(
            spotify,
            count=count,
            discovery_level=discovery_level,
            min_year=min_year,
            max_popularity=max_popularity,
            genres=genres,
            moods=moods
        )
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/create-playlist', methods=['POST'])
def create_playlist():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session['user_id']
    
    # Get Spotify credentials and tokens
    spotify_creds = user_service.get_spotify_credentials(user_id)
    if not spotify_creds:
        return jsonify({"error": "Spotify credentials not set"}), 400
        
    spotify_tokens = user_service.get_spotify_tokens(user_id)
    if not spotify_tokens:
        return jsonify({"error": "Spotify authentication failed"}), 400
    
    # Get request data
    data = request.json
    playlist_name = data.get('name', 'AI Generated Playlist')
    track_uris = data.get('track_uris', [])
    
    if not track_uris:
        return jsonify({"error": "No tracks provided"}), 400
    
    # Create playlist
    spotify = SpotifyService(
        spotify_creds['client_id'], 
        spotify_creds['client_secret'], 
        spotify_tokens
    )
    playlist = spotify.create_playlist(playlist_name, track_uris)
    
    if not playlist:
        return jsonify({"error": "Failed to create playlist"}), 500
    
    return jsonify(playlist)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
