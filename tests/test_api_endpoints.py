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

# Additional integration tests can be added for other endpoints like /authorize-spotify, /callback, /api/recommendations, etc.
