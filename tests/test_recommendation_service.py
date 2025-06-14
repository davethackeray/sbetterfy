import pytest
from unittest.mock import patch, MagicMock
from recommendation_service import RecommendationService

@pytest.fixture
def recommendation_service():
    """Fixture to create a RecommendationService instance with a mocked API key."""
    return RecommendationService(api_key="mock_api_key")

def test_validate_api_key_success(recommendation_service):
    """Test that validate_api_key returns True with a valid API key."""
    with patch('google.generativeai.list_models') as mock_list_models:
        mock_list_models.return_value = ["model1", "model2"]
        
        result = recommendation_service.validate_api_key()
        assert result is True

def test_validate_api_key_failure(recommendation_service):
    """Test that validate_api_key returns False with an invalid API key."""
    with patch('google.generativeai.list_models') as mock_list_models:
        mock_list_models.side_effect = Exception("API key invalid")
        
        result = recommendation_service.validate_api_key()
        assert result is False

def test_get_recommendations_basic(recommendation_service):
    """Test basic functionality of get_recommendations with mocked Spotify and AI responses."""
    mock_spotify = MagicMock()
    mock_spotify.get_liked_songs.return_value = [
        {"name": "Song 1", "artists": [{"name": "Artist 1"}], "album": {"release_date": "2020-01-01"}},
        {"name": "Song 2", "artists": [{"name": "Artist 2"}], "album": {"release_date": "2019-01-01"}}
    ]
    mock_spotify.search_track.return_value = {"uri": "spotify:track:123", "name": "Recommended Song", "artists": [{"name": "Artist 3"}], "album": {"images": [{"url": "image_url"}]}}
    
    with patch.object(recommendation_service, '_generate_recommendation_prompt') as mock_prompt:
        with patch.object(recommendation_service, '_parse_recommendations') as mock_parse:
            mock_prompt.return_value = "mock prompt"
            mock_parse.return_value = [
                {"title": "Recommended Song", "artist": "Artist 3", "reason": "Good match"}
            ]
            
            recommendations = recommendation_service.get_recommendations(
                spotify=mock_spotify,
                count=1,
                discovery_level=50,
                min_year=1900,
                max_popularity=100,
                genres=[],
                moods=[]
            )
            assert len(recommendations["tracks"]) == 1
            assert recommendations["tracks"][0]["name"] == "Recommended Song"
            assert recommendations["tracks"][0]["reason"] == "Good match"

# Additional tests can be added for edge cases, different parameters, and error handling.
