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

def test_save_spotify_tokens(user_service, mock_session):
    """Test saving Spotify tokens for a user."""
    user_id = "test_user"
    tokens = {
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "expires_in": 3600
    }
    
    with patch('user_service.get_session', return_value=mock_session):
        user_service.save_spotify_tokens(user_id, tokens)
        mock_session.execute.assert_called()
        mock_session.commit.assert_called_once()

def test_get_spotify_tokens(user_service, mock_session):
    """Test retrieving Spotify tokens for a user."""
    user_id = "test_user"
    mock_result = MagicMock()
    mock_result.fetchone.return_value = {
        "spotify_access_token": "mock_access_token",
        "spotify_refresh_token": "mock_refresh_token",
        "spotify_expires_in": 3600
    }
    
    with patch('user_service.get_session', return_value=mock_session):
        mock_session.execute.return_value = mock_result
        tokens = user_service.get_spotify_tokens(user_id)
        assert tokens["access_token"] == "mock_access_token"
        assert tokens["refresh_token"] == "mock_refresh_token"
        assert tokens["expires_in"] == 3600

def test_get_spotify_tokens_none(user_service, mock_session):
    """Test retrieving Spotify tokens when none exist for the user."""
    user_id = "test_user"
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    
    with patch('user_service.get_session', return_value=mock_session):
        mock_session.execute.return_value = mock_result
        tokens = user_service.get_spotify_tokens(user_id)
        assert tokens is None

def test_get_gemini_api_key(user_service, mock_session):
    """Test retrieving Gemini API key for a user."""
    user_id = "test_user"
    mock_result = MagicMock()
    mock_result.fetchone.return_value = {"gemini_api_key": "mock_api_key"}
    
    with patch('user_service.get_session', return_value=mock_session):
        mock_session.execute.return_value = mock_result
        api_key = user_service.get_gemini_api_key(user_id)
        assert api_key == "mock_api_key"

def test_get_gemini_api_key_none(user_service, mock_session):
    """Test retrieving Gemini API key when none exists for the user."""
    user_id = "test_user"
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    
    with patch('user_service.get_session', return_value=mock_session):
        mock_session.execute.return_value = mock_result
        api_key = user_service.get_gemini_api_key(user_id)
        assert api_key is None

# Additional tests can be added for other edge cases like database errors, invalid user IDs, etc.
