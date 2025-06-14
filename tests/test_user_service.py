import pytest
from unittest.mock import patch, MagicMock
from user_service import UserService
from database import get_session

@pytest.fixture
def user_service():
    """Fixture to create a UserService instance."""
    return UserService()

@pytest.fixture
def mock_session():
    """Fixture to mock a database session."""
    return MagicMock()

def test_save_spotify_credentials(user_service, mock_session):
    """Test saving Spotify credentials for a user."""
    user_id = "test_user"
    client_id = "mock_client_id"
    client_secret = "mock_client_secret"
    
    with patch('user_service.get_session', return_value=mock_session):
        user_service.save_spotify_credentials(user_id, client_id, client_secret)
        mock_session.execute.assert_called()
        mock_session.commit.assert_called_once()

def test_get_spotify_credentials(user_service, mock_session):
    """Test retrieving Spotify credentials for a user."""
    user_id = "test_user"
    mock_result = MagicMock()
    mock_result.fetchone.return_value = {"spotify_client_id": "mock_client_id", "spotify_client_secret": "mock_client_secret"}
    
    with patch('user_service.get_session', return_value=mock_session):
        mock_session.execute.return_value = mock_result
        creds = user_service.get_spotify_credentials(user_id)
        assert creds == {"client_id": "mock_client_id", "client_secret": "mock_client_secret"}

def test_save_gemini_api_key(user_service, mock_session):
    """Test saving Gemini API key for a user."""
    user_id = "test_user"
    api_key = "mock_api_key"
    
    with patch('user_service.get_session', return_value=mock_session):
        user_service.save_gemini_api_key(user_id, api_key)
        mock_session.execute.assert_called()
        mock_session.commit.assert_called_once()

def test_has_gemini_api_key(user_service, mock_session):
    """Test checking if a user has a Gemini API key set."""
    user_id = "test_user"
    mock_result = MagicMock()
    mock_result.fetchone.return_value = {"gemini_api_key": "mock_api_key"}
    
    with patch('user_service.get_session', return_value=mock_session):
        mock_session.execute.return_value = mock_result
        result = user_service.has_gemini_api_key(user_id)
        assert result is True

# Additional tests can be added for other methods like save_spotify_tokens, get_spotify_tokens, etc.
