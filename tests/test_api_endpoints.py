import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from main import app

@pytest.fixture
def client():
    """Fixture to create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_user_service():
    """Fixture to mock UserService methods."""
    with patch('main.user_service') as mock:
        yield mock

@pytest.fixture
def mock_spotify_service():
    """Fixture to mock SpotifyService methods."""
    with patch('main.SpotifyService') as mock:
        yield mock

@pytest.fixture
def mock_recommendation_service():
    """Fixture to mock RecommendationService methods."""
    with patch('main.RecommendationService') as mock:
        yield mock

def test_index_route(client):
    """Test the index route redirects to dashboard if user is logged in."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user'
    response = client.get('/')
    assert response.status_code == 302
    assert response.location.endswith('/dashboard')

def test_index_route_no_session(client):
    """Test the index route renders index.html if user is not logged in."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'index.html' in response.data  # Assuming template rendering check

def test_login_route(client):
    """Test the login route generates a temporary user ID and renders setup template."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'setup_spotify.html' in response.data  # Assuming template rendering check
    with client.session_transaction() as sess:
        assert 'temp_user_id' in sess

def test_save_spotify_creds_success(client, mock_user_service):
    """Test saving Spotify credentials with valid data."""
    with client.session_transaction() as sess:
        sess['temp_user_id'] = 'test_user'
    mock_user_service.get_spotify_credentials.return_value = None
    mock_user_service.save_spotify_credentials.return_value = None
    
    response = client.post('/api/save-spotify-creds', json={
        'client_id': 'mock_client_id',
        'client_secret': 'mock_client_secret'
    })
    assert response.status_code == 200
    assert response.json == {"status": "success"}

def test_save_spotify_creds_unauthenticated(client):
    """Test saving Spotify credentials without authentication."""
    response = client.post('/api/save-spotify-creds', json={
        'client_id': 'mock_client_id',
        'client_secret': 'mock_client_secret'
    })
    assert response.status_code == 401
    assert "error" in response.json

def test_authorize_spotify_success(client, mock_user_service):
    """Test /authorize-spotify route with valid user ID and credentials."""
    with client.session_transaction() as sess:
        sess['temp_user_id'] = 'test_user'
    mock_user_service.get_spotify_credentials.return_value = {
        'client_id': 'mock_client_id',
        'client_secret': 'mock_client_secret'
    }
    with patch('main.SpotifyService.get_auth_url') as mock_get_auth_url:
        mock_get_auth_url.return_value = "https://accounts.spotify.com/authorize?client_id=mock_client_id&..."
        response = client.get('/authorize-spotify')
        assert response.status_code == 302
        assert response.location.startswith("https://accounts.spotify.com/authorize")

def test_authorize_spotify_no_user_id(client):
    """Test /authorize-spotify route without a user ID in session."""
    response = client.get('/authorize-spotify')
    assert response.status_code == 302
    assert response.location.endswith('/login')

def test_authorize_spotify_no_credentials(client, mock_user_service):
    """Test /authorize-spotify route when no Spotify credentials are found."""
    with client.session_transaction() as sess:
        sess['temp_user_id'] = 'test_user'
    mock_user_service.get_spotify_credentials.return_value = None
    response = client.get('/authorize-spotify')
    assert response.status_code == 302
    assert response.location.endswith('/login')

def test_dashboard_authenticated(client):
    """Test /dashboard route when user is authenticated."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user'
        sess['display_name'] = 'Test User'
    with patch('main.user_service.has_gemini_api_key', return_value=True):
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'dashboard.html' in response.data  # Assuming template rendering check

def test_dashboard_not_authenticated(client):
    """Test /dashboard route when user is not authenticated."""
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert response.location.endswith('/')

def test_save_api_key_success(client, mock_user_service):
    """Test /api/save-api-key route with valid API key."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user'
    with patch('main.RecommendationService.validate_api_key', return_value=True):
        with patch('main.user_service.save_gemini_api_key') as mock_save:
            response = client.post('/api/save-api-key', json={'api_key': 'mock_api_key'})
            assert response.status_code == 200
            assert response.json == {"status": "success"}
            mock_save.assert_called_once_with('test_user', 'mock_api_key')

def test_save_api_key_invalid(client, mock_user_service):
    """Test /api/save-api-key route with invalid API key."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user'
    with patch('main.RecommendationService.validate_api_key', return_value=False):
        response = client.post('/api/save-api-key', json={'api_key': 'invalid_key'})
        assert response.status_code == 400
        assert "error" in response.json
        assert response.json["error"] == "Invalid Google AI API key"

def test_save_api_key_unauthenticated(client):
    """Test /api/save-api-key route without authentication."""
    response = client.post('/api/save-api-key', json={'api_key': 'mock_api_key'})
    assert response.status_code == 401
    assert "error" in response.json

# Additional integration tests can be added for other endpoints like /callback, /api/recommendations, /api/create-playlist, etc.
