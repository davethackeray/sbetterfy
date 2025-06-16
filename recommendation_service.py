import google.generativeai as genai
import json
import re

class RecommendationService:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
    
    def validate_api_key(self):
        """Validate that the API key works"""
        try:
            response = self.model.generate_content("Hello")
            return True
        except Exception:
            return False
    
    def get_recommendations(self, spotify_service, count=20, discovery_level=50, min_year=1900, max_popularity=100, genres=None, moods=None, tempo=None, energy=None):
        """Get song recommendations based on user's liked songs and preferences"""
        # Get user's liked songs
        liked_songs = spotify_service.get_liked_songs(limit=100)
        
        if not liked_songs:
            raise Exception("Could not retrieve liked songs from Spotify. Please ensure your Spotify account is connected.")
        
        # Prepare prompt for Gemini
        prompt = self._create_recommendation_prompt(
            liked_songs, 
            count, 
            discovery_level, 
            min_year, 
            max_popularity,
            genres,
            moods,
            tempo,
            energy
        )
        
        # Generate recommendations
        try:
            response = self.model.generate_content(prompt)
            print("Gemini API Response:", response.text)
            recommendations = self._parse_recommendations(response.text)
            print("Parsed Recommendations:", recommendations)
            
            if not recommendations:
                raise Exception("No valid recommendations could be parsed from the AI response.")
            
            # Verify songs on Spotify in batches to reduce API call overhead
            verified_recommendations = []
            batch_size = 5  # Process multiple searches in a batch
            max_attempts = min(len(recommendations), count * 3)  # Attempt to verify more than needed to account for failures
            
            for i in range(0, max_attempts, batch_size):
                batch = recommendations[i:i + batch_size]
                for rec in batch:
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
                        print("Verified Recommendations (limited to requested count):", verified_recommendations)
                        return verified_recommendations
            
            print("Verified Recommendations (all processed):", verified_recommendations)
            if not verified_recommendations:
                raise Exception("No recommendations could be verified on Spotify. The AI might have suggested tracks that don't exist or aren't available on Spotify. Please try adjusting your preferences or generating a new set of recommendations.")
            return verified_recommendations
        except Exception as e:
            print("Error in recommendation process:", str(e))
            error_msg = str(e)
            if "API key" in error_msg or "authentication" in error_msg.lower():
                raise Exception("There seems to be an issue with the Google Gemini AI API key. Please verify your API key in the setup page.")
            elif "Spotify" in error_msg:
                raise Exception("Error connecting to Spotify. Please ensure your Spotify account is connected properly via the authentication process.")
            else:
                raise Exception(f"Error generating recommendations: {error_msg}. Please try again or adjust your preferences.")
    
    def _create_recommendation_prompt(self, liked_songs, count, discovery_level, min_year, max_popularity, genres=None, moods=None, tempo=None, energy=None):
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
        
        # Tempo filter
        tempo_text = ""
        if tempo:
            if tempo == "slow":
                tempo_text = "The recommendations should have a slow tempo (below 100 BPM).\n"
            elif tempo == "medium":
                tempo_text = "The recommendations should have a medium tempo (100-140 BPM).\n"
            elif tempo == "fast":
                tempo_text = "The recommendations should have a fast tempo (above 140 BPM).\n"
        
        # Energy filter
        energy_text = ""
        if energy:
            if energy == "low":
                energy_text = "The recommendations should have low energy, suitable for relaxing or background listening.\n"
            elif energy == "medium":
                energy_text = "The recommendations should have medium energy, suitable for casual listening or moderate activities.\n"
            elif energy == "high":
                energy_text = "The recommendations should have high energy, suitable for workouts or dancing.\n"
        
        prompt = f"""Based on the following list of songs that I like, recommend {count} new songs that I might enjoy.

My liked songs:
{songs_text}

{genres_text}
{moods_text}
{discovery_text}
{year_text}
{popularity_text}
{tempo_text}
{energy_text}

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
        
        # Fallback 1: Try to parse line by line with "by" or "-" separator
        recommendations = []
        lines = response_text.split('\n')
        
        for line in lines:
            # Remove any leading numbers or bullet points
            line = re.sub(r'^\s*[\d\.\-\*]+\s*', '', line).strip()
            # Look for patterns like "Title by Artist" or "Title - Artist"
            match = re.search(r'"?([^"]+)"?\s+(?:by|-)\s*([^,]+)', line, re.IGNORECASE)
            if match:
                title = match.group(1).strip().strip('"')
                artist = match.group(2).strip().strip('"')
                if title and artist:  # Ensure both fields are non-empty
                    recommendations.append({'title': title, 'artist': artist})
        
        if recommendations:
            return recommendations
            
        # Fallback 2: If no "by" or "-" separator, try splitting on last comma
        for line in lines:
            line = re.sub(r'^\s*[\d\.\-\*]+\s*', '', line).strip()
            if ',' in line:
                parts = line.rsplit(',', 1)
                if len(parts) == 2:
                    title = parts[0].strip().strip('"')
                    artist = parts[1].strip().strip('"')
                    if title and artist:  # Ensure both fields are non-empty
                        recommendations.append({'title': title, 'artist': artist})
        
        return recommendations

    def get_filter_extreme_suggestions(self, spotify_service, liked_songs):
        """Get song suggestions at extreme ends of filters based on user's liked songs"""
        # Prepare prompt for Gemini to suggest songs for extreme ends of filters
        prompt = self._create_filter_extreme_prompt(liked_songs)
        
        # Generate suggestions
        try:
            response = self.model.generate_content(prompt)
            print("Gemini API Response for Filter Extremes:", response.text)
            suggestions = self._parse_filter_extreme_suggestions(response.text)
            print("Parsed Filter Extreme Suggestions:", suggestions)
            
            if not suggestions:
                raise Exception("No valid filter extreme suggestions could be parsed from the AI response.")
            
            # Verify songs on Spotify
            verified_suggestions = []
            for category in suggestions:
                verified_category = {
                    'filter': category['filter'],
                    'extreme': category['extreme'],
                    'tracks': []
                }
                for rec in category['tracks']:
                    query = f"track:{rec['title']} artist:{rec['artist']}"
                    search_results = spotify_service.search_tracks(query, limit=1)
                    
                    if search_results:
                        track = search_results[0]
                        verified_category['tracks'].append({
                            'title': track['name'],
                            'artist': track['artist'],
                            'uri': track['uri'],
                            'album': track['album'],
                            'album_cover': track.get('album_cover', ''),
                            'release_date': track['release_date'],
                            'popularity': track['popularity'],
                            'preview_url': track.get('preview_url'),
                            'tempo': rec.get('tempo', 'N/A'),
                            'energy': rec.get('energy', 'N/A'),
                            'genre': rec.get('genre', 'N/A'),
                            'mood': rec.get('mood', 'N/A')
                        })
                
                verified_suggestions.append(verified_category)
            
            print("Verified Filter Extreme Suggestions:", verified_suggestions)
            return verified_suggestions
        except Exception as e:
            print("Error in filter extreme suggestion process:", str(e))
            error_msg = str(e)
            if "API key" in error_msg or "authentication" in error_msg.lower():
                raise Exception("There seems to be an issue with the Google Gemini AI API key. Please verify your API key in the setup page.")
            elif "Spotify" in error_msg:
                raise Exception("Error connecting to Spotify. Please ensure your Spotify account is connected properly via the authentication process.")
            else:
                raise Exception(f"Error generating filter extreme suggestions: {error_msg}. Please try again.")
    
    def _create_filter_extreme_prompt(self, liked_songs):
        """Create a prompt for the Gemini model to suggest songs at extreme ends of filters"""
        # Format liked songs for the prompt
        songs_text = "\n".join([f"- {song['name']} by {song['artist']}" for song in liked_songs[:50]])
        
        prompt = f"""Based on the following list of songs that I like, suggest songs that represent the extreme ends of the following music filters: Target Tempo (Slowest and Fastest), Target Energy (Lowest and Highest), and Moods (Calmest and Most Energetic). Provide 6 songs for each extreme category (total of 36 songs across all categories).

My liked songs:
{songs_text}

For each category, suggest songs that I might enjoy based on my liked songs, but ensure they represent the extreme ends of each filter. Include metadata for each song to explain why it fits the extreme category.

Format your response as a JSON array of objects, each object representing a category with 'filter' (e.g., 'Target Tempo'), 'extreme' (e.g., 'Slowest'), and 'tracks' as an array of objects with 'title', 'artist', 'tempo' (for Tempo), 'energy' (for Energy), 'genre', and 'mood' fields. Do not include any explanations or other text outside the JSON array.
"""
        return prompt
    
    def _parse_filter_extreme_suggestions(self, response_text):
        """Parse the filter extreme suggestions from the model response"""
        # Try to extract JSON from the response
        json_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
        
        if json_match:
            try:
                suggestions = json.loads(json_match.group(0))
                return suggestions
            except json.JSONDecodeError:
                pass
        
        # Fallback: If JSON parsing fails, return empty list
        return []
