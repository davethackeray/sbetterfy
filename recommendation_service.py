import google.generativeai as genai
import json
import re

class RecommendationService:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    
    def validate_api_key(self):
        """Validate that the API key works"""
        try:
            response = self.model.generate_content("Hello")
            return True
        except Exception:
            return False
    
    def get_recommendations(self, spotify_service, count=20, discovery_level=50, min_year=1900, max_popularity=100, genres=None, moods=None):
        """Get song recommendations based on user's liked songs and preferences"""
        # Get user's liked songs
        liked_songs = spotify_service.get_liked_songs(limit=100)
        
        if not liked_songs:
            raise Exception("Could not retrieve liked songs from Spotify")
        
        # Prepare prompt for Gemini
        prompt = self._create_recommendation_prompt(
            liked_songs, 
            count, 
            discovery_level, 
            min_year, 
            max_popularity,
            genres,
            moods
        )
        
        # Generate recommendations
        try:
            response = self.model.generate_content(prompt)
            recommendations = self._parse_recommendations(response.text)
            
            # Verify songs on Spotify
            verified_recommendations = []
            for rec in recommendations:
                query = f"track:{rec['title']} artist:{rec['artist']}"
                search_results = spotify_service.search_tracks(query, limit=1)
                
                if search_results:
                    track = search_results[0]
                    verified_recommendations.append({
                        'title': track['name'],
                        'artist': track['artist'],
                        'uri': track['uri'],
                        'album': track['album'],
                        'release_date': track['release_date'],
                        'popularity': track['popularity'],
                        'preview_url': track.get('preview_url')
                    })
                
                if len(verified_recommendations) >= count:
                    break
            
            return verified_recommendations
        except Exception as e:
            raise Exception(f"Error generating recommendations: {str(e)}")
    
    def _create_recommendation_prompt(self, liked_songs, count, discovery_level, min_year, max_popularity, genres=None, moods=None):
        """Create a prompt for the Gemini model"""
        # Format liked songs for the prompt
        songs_text = "\n".join([f"- {song['name']} by {song['artist']}" for song in liked_songs[:50]])
        
        # Format genres and moods if provided
        genres_text = ""
        if genres and len(genres) > 0:
            genres_text = f"The recommendations should focus on these genres: {', '.join(genres)}.\n"
        
        moods_text = ""
        if moods and len(moods) > 0:
            moods_text = f"The recommendations should match these moods: {', '.join(moods)}.\n"
        
        # Adjust discovery level text
        if discovery_level < 30:
            discovery_text = "The recommendations should be very similar to my liked songs."
        elif discovery_level < 70:
            discovery_text = "The recommendations should balance similarity with discovery of new sounds."
        else:
            discovery_text = "The recommendations should be adventurous and introduce me to new sounds while still matching my taste."
        
        # Year filter
        year_text = f"Only include songs released in or after {min_year}.\n"
        
        # Popularity filter (lower means more obscure)
        popularity_text = ""
        if max_popularity < 80:
            popularity_text = "Include some lesser-known tracks that I might not have discovered yet.\n"
        
        prompt = f"""Based on the following list of songs that I like, recommend {count} new songs that I might enjoy.

My liked songs:
{songs_text}

{genres_text}
{moods_text}
{discovery_text}
{year_text}
{popularity_text}

Format your response as a JSON array of objects with 'title' and 'artist' fields only. Do not include any explanations or other text outside the JSON array.
"""
        return prompt
    
    def _parse_recommendations(self, response_text):
        """Parse the recommendations from the model response"""
        # Try to extract JSON from the response
        json_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
        
        if json_match:
            try:
                recommendations = json.loads(json_match.group(0))
                return recommendations
            except json.JSONDecodeError:
                pass
        
        # Fallback: Try to parse line by line
        recommendations = []
        lines = response_text.split('\n')
        
        for line in lines:
            # Look for patterns like "Title by Artist" or "Title - Artist"
            match = re.search(r'"?([^"]+)"?\s+(?:by|-)(?:\s+|(?:\s*))([^,]+)', line)
            if match:
                title = match.group(1).strip().strip('"')
                artist = match.group(2).strip().strip('"')
                recommendations.append({'title': title, 'artist': artist})
        
        return recommendations
