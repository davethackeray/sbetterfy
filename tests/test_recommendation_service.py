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

def test_get_recommendations_empty_liked_songs(recommendation_service):
    """Test get_recommendations when user has no liked songs."""
    mock_spotify = MagicMock()
    mock_spotify.get_liked_songs.return_value = []
    
    with patch.object(recommendation_service, '_generate_recommendation_prompt') as mock_prompt:
        with patch.object(recommendation_service, '_parse_recommendations') as mock_parse:
            mock_prompt.return_value = "mock prompt for no liked songs"
            mock_parse.return_value = [
                {"title": "Generic Song", "artist": "Generic Artist", "reason": "Based on general trends"}
            ]
            mock_spotify.search_track.return_value = {"uri": "spotify:track:456", "name": "Generic Song", "artists": [{"name": "Generic Artist"}], "album": {"images": [{"url": "image_url"}]}}
            
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
            assert recommendations["tracks"][0]["name"] == "Generic Song"
            assert recommendations["tracks"][0]["reason"] == "Based on general trends"

def test_get_recommendations_with_genres_and_moods(recommendation_service):
    """Test get_recommendations with specific genres and moods."""
    mock_spotify = MagicMock()
    mock_spotify.get_liked_songs.return_value = [
        {"name": "Song 1", "artists": [{"name": "Artist 1"}], "album": {"release_date": "2020-01-01"}}
    ]
    
    with patch.object(recommendation_service, '_generate_recommendation_prompt') as mock_prompt:
        with patch.object(recommendation_service, '_parse_recommendations') as mock_parse:
            mock_prompt.return_value = "mock prompt with genres and moods"
            mock_parse.return_value = [
                {"title": "Mood Song", "artist": "Mood Artist", "reason": "Matches mood and genre"}
            ]
            mock_spotify.search_track.return_value = {"uri": "spotify:track:789", "name": "Mood Song", "artists": [{"name": "Mood Artist"}], "album": {"images": [{"url": "image_url"}]}}
            
            recommendations = recommendation_service.get_recommendations(
                spotify=mock_spotify,
                count=1,
                discovery_level=75,
                min_year=2000,
                max_popularity=80,
                genres=["rock", "indie"],
                moods=["energetic", "happy"]
            )
            assert len(recommendations["tracks"]) == 1
            assert recommendations["tracks"][0]["name"] == "Mood Song"
            assert mock_prompt.call_args[0][2] == ["rock", "indie"]  # Check genres passed to prompt
            assert mock_prompt.call_args[0][3] == ["energetic", "happy"]  # Check moods passed to prompt

def test_get_recommendations_parsing_failure(recommendation_service):
    """Test get_recommendations when AI response parsing fails."""
    mock_spotify = MagicMock()
    mock_spotify.get_liked_songs.return_value = [
        {"name": "Song 1", "artists": [{"name": "Artist 1"}], "album": {"release_date": "2020-01-01"}}
    ]
    
    with patch.object(recommendation_service, '_generate_recommendation_prompt') as mock_prompt:
        with patch.object(recommendation_service, '_parse_recommendations') as mock_parse:
            mock_prompt.return_value = "mock prompt"
            mock_parse.side_effect = ValueError("Failed to parse AI response")
            
            recommendations = recommendation_service.get_recommendations(
                spotify=mock_spotify,
                count=5,
                discovery_level=50,
                min_year=1900,
                max_popularity=100,
                genres=[],
                moods=[]
            )
            assert len(recommendations["tracks"]) == 0  # Should return empty list on parsing failure

# Additional tests can be added for other edge cases like API failures, invalid parameters, etc.
