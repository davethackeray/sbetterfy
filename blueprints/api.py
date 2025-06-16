from flask import Blueprint, request, session, jsonify
from spotify_service import SpotifyService
from recommendation_service import RecommendationService
from user_service import UserService

api_bp = Blueprint('api', __name__)
user_service = UserService()

@api_bp.route('/api/save-spotify-creds', methods=['POST'])
def save_spotify_creds():
    if 'temp_user_id' not in session and 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
        
    user_id = session.get('user_id', session.get('temp_user_id'))
    data = request.json
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request format"}), 400
        
    client_id = data.get('client_id')
    client_secret = data.get('client_secret')
    
    if not client_id or not client_secret:
        return jsonify({"error": "Client ID and Client Secret are required"}), 400
        
    if not isinstance(client_id, str) or not isinstance(client_secret, str):
        return jsonify({"error": "Client ID and Client Secret must be strings"}), 400
        
    if len(client_id) < 10 or len(client_secret) < 10:
        return jsonify({"error": "Client ID and Client Secret must be of sufficient length"}), 400
    
    # Validate credentials
    sp = SpotifyService(client_id, client_secret)
    if not sp.validate_credentials():
        return jsonify({"error": "Invalid Spotify credentials"}), 400
    
    user_service.save_spotify_credentials(user_id, client_id, client_secret)
    return jsonify({"status": "success"})

@api_bp.route('/api/save-api-key', methods=['POST'])
def save_api_key():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request format"}), 400
        
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({"error": "API key is required"}), 400
        
    if not isinstance(api_key, str):
        return jsonify({"error": "API key must be a string"}), 400
        
    if len(api_key) < 10:
        return jsonify({"error": "API key must be of sufficient length"}), 400
    
    # Validate API key
    recommendation_service = RecommendationService(api_key)
    if not recommendation_service.validate_api_key():
        return jsonify({"error": "Invalid Google AI API key"}), 400
    
    # Save API key
    user_service.save_gemini_api_key(session['user_id'], api_key)
    
    return jsonify({"status": "success"})

@api_bp.route('/api/validate-spotify-creds')
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

@api_bp.route('/api/recommendations', methods=['POST'])
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
    
    # Get request data with input validation
    data = request.json
    try:
        count = int(data.get('count', 20))
        if not 1 <= count <= 50:
            return jsonify({"error": "Count must be between 1 and 50"}), 400
            
        discovery_level = int(data.get('discovery_level', 50))
        if not 0 <= discovery_level <= 100:
            return jsonify({"error": "Discovery level must be between 0 and 100"}), 400
            
        min_year = int(data.get('min_year', 1900))
        if not 1900 <= min_year <= 2025:
            return jsonify({"error": "Minimum year must be between 1900 and 2025"}), 400
            
        max_popularity = int(data.get('max_popularity', 100))
        if not 0 <= max_popularity <= 100:
            return jsonify({"error": "Maximum popularity must be between 0 and 100"}), 400
            
        genres = data.get('genres', [])
        if not isinstance(genres, list):
            return jsonify({"error": "Genres must be a list"}), 400
            
        moods = data.get('moods', [])
        if not isinstance(moods, list):
            return jsonify({"error": "Moods must be a list"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input format for parameters"}), 400
    
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

@api_bp.route('/api/create-playlist', methods=['POST'])
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
    
    # Get request data with input validation
    data = request.json
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request format"}), 400
        
    playlist_name = data.get('name', 'AI Generated Playlist')
    if not isinstance(playlist_name, str):
        return jsonify({"error": "Playlist name must be a string"}), 400
        
    if len(playlist_name) > 100:
        return jsonify({"error": "Playlist name must not exceed 100 characters"}), 400
        
    track_uris = data.get('track_uris', [])
    if not isinstance(track_uris, list):
        return jsonify({"error": "Track URIs must be a list"}), 400
        
    if not track_uris:
        return jsonify({"error": "No tracks provided"}), 400
        
    if len(track_uris) > 100:
        return jsonify({"error": "Too many tracks, maximum allowed is 100"}), 400
        
    for uri in track_uris:
        if not isinstance(uri, str) or not uri.startswith('spotify:track:'):
            return jsonify({"error": "Invalid track URI format"}), 400
    
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

@api_bp.route('/api/genres', methods=['GET'])
def get_genres():
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
    
    # Initialize Spotify service
    spotify = SpotifyService(
        spotify_creds['client_id'], 
        spotify_creds['client_secret'], 
        spotify_tokens
    )
    
    # Fetch available genres
    genres = spotify.get_available_genres()
    if not genres:
        return jsonify({"error": "Failed to fetch genres from Spotify"}), 500
    
    return jsonify({"genres": genres})
