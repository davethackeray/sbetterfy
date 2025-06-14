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

# Additional tests can be added for other methods like get_tokens, get_user_profile, etc.
