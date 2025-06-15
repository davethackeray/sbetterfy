import pytest
from unittest.mock import patch, MagicMock
from spotify_service import SpotifyService

@pytest.fixture
def spotify_service():
    """Fixture to create a SpotifyService instance with mocked credentials."""
    return SpotifyService(client_id="mock_client_id", client_secret="mock_client_secret")

def test_validate_credentials_success(spotify_service):
    """Test that validate_credentials returns True with valid credentials."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "mock_token"}
        mock_post.return_value = mock_response
        
        result = spotify_service.validate_credentials()
        assert result is True

def test_validate_credentials_failure(spotify_service):
    """Test that validate_credentials returns False with invalid credentials."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        result = spotify_service.validate_credentials()
        assert result is False

def test_get_auth_url(spotify_service):
    """Test that get_auth_url generates the correct authorization URL."""
    user_id = "test_user"
    auth_url = spotify_service.get_auth_url(user_id)
    assert "client_id=mock_client_id" in auth_url
    assert "response_type=code" in auth_url
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fcallback" in auth_url
    assert f"state={user_id}" in auth_url
    assert "scope=user-read-private+user-read-email+user-library-read+playlist-modify-public+playlist-modify-private" in auth_url

def test_get_tokens_success(spotify_service):
    """Test that get_tokens returns tokens with a valid authorization code."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response
        
        tokens = spotify_service.get_tokens("mock_code")
        assert tokens["access_token"] == "mock_access_token"
        assert tokens["refresh_token"] == "mock_refresh_token"
        assert tokens["expires_in"] == 3600

def test_get_tokens_failure(spotify_service):
    """Test that get_tokens returns None when token request fails."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        tokens = spotify_service.get_tokens("invalid_code")
        assert tokens is None

def test_get_user_profile_success(spotify_service):
    """Test that get_user_profile returns user data with a valid access token."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "mock_user_id",
            "display_name": "Mock User"
        }
        mock_get.return_value = mock_response
        
        profile = spotify_service.get_user_profile("mock_access_token")
        assert profile["id"] == "mock_user_id"
        assert profile["display_name"] == "Mock User"

def test_get_user_profile_failure(spotify_service):
    """Test that get_user_profile returns None when request fails."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        profile = spotify_service.get_user_profile("invalid_token")
        assert profile is None
# Additional tests can be added for other methods like get_liked_songs, search_track, create_playlist, etc.
