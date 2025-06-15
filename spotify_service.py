import os
import requests
import base64
import urllib.parse
import hashlib
import secrets
import string
from urllib.parse import urlencode

class SpotifyService:
    def __init__(self, client_id=None, client_secret=None, tokens=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = os.environ.get('BASE_URL', '') + '/callback'
        self.tokens = tokens
        self.base_url = 'https://api.spotify.com/v1'
        # In-memory cache for API responses
        self._cache = {}
        # Default cache expiration time in seconds (5 minutes)
        self._default_cache_expiry = 300
        # Extended cache expiration for less frequently changing data (1 hour)
        self._extended_cache_expiry = 3600
        # Track cache timestamps
        self._cache_timestamps = {}
        # Maximum cache size to prevent memory issues
        self._max_cache_size = 1000
        # Store code verifier for PKCE
        self._code_verifier = None
    
    def get_auth_url(self, state=None):
        """Generate the Spotify authorization URL with PKCE"""
        if not self.client_id:
            raise ValueError("Spotify client ID not configured")
            
        # Generate a code verifier (random string)
        alphabet = string.ascii_letters + string.digits
        self._code_verifier = ''.join(secrets.choice(alphabet) for _ in range(128))
        
        # Generate code challenge (base64 URL encoded SHA256 hash of verifier)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(self._code_verifier.encode('ascii')).digest()
        ).decode('ascii').rstrip('=')
        
        scope = 'user-library-read playlist-modify-public user-top-read'
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': scope,
            'show_dialog': 'true',
            'code_challenge_method': 'S256',
            'code_challenge': code_challenge
        }
        
        if state:
            params['state'] = state
            
        return f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    
    def get_tokens(self, code):
        """Exchange authorization code for access and refresh tokens with PKCE"""
        if not self.client_id or not self.client_secret:
            raise ValueError("Spotify credentials not configured")
            
        if not self._code_verifier:
            raise ValueError("Code verifier not set for PKCE flow")
            
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'code_verifier': self._code_verifier
        }
        
        response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
        
        if response.status_code != 200:
            return None
        
        # Clear the code verifier after use
        self._code_verifier = None
        return response.json()
    
    def refresh_token(self):
        """Refresh the access token using the refresh token"""
        if not self.tokens or 'refresh_token' not in self.tokens:
            return False
        
        if not self.client_id or not self.client_secret:
            return False
            
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.tokens['refresh_token']
        }
        
        response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
        
        if response.status_code != 200:
            return False
        
        new_tokens = response.json()
        self.tokens['access_token'] = new_tokens['access_token']
        if 'refresh_token' in new_tokens:
            self.tokens['refresh_token'] = new_tokens['refresh_token']
        
        return True
    
    def _get_cache_key(self, endpoint, params=None):
        """Generate a unique cache key based on endpoint and parameters"""
        key = endpoint
        if params:
            # Sort params to ensure consistent keys regardless of order
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            key += ":" + urllib.parse.urlencode(sorted_params)
        return key

    def _get_from_cache(self, key, expiry=None):
        """Retrieve data from cache if it exists and is not expired"""
        import time
        if key in self._cache:
            timestamp = self._cache_timestamps.get(key, 0)
            expiry_time = expiry if expiry is not None else self._default_cache_expiry
            if time.time() - timestamp < expiry_time:
                return self._cache[key]
            else:
                # Remove expired cache entry
                del self._cache[key]
                del self._cache_timestamps[key]
        return None

    def _set_to_cache(self, key, data, expiry=None):
        """Store data in cache with a timestamp, limit cache size"""
        import time
        # Limit cache size by removing oldest entries if necessary
        if len(self._cache) >= self._max_cache_size:
            oldest_key = min(self._cache_timestamps, key=lambda k: self._cache_timestamps[k])
            del self._cache[oldest_key]
            del self._cache_timestamps[oldest_key]
        self._cache[key] = data
        self._cache_timestamps[key] = time.time()

    def make_api_request(self, endpoint, method='GET', data=None, params=None, cache_expiry=None):
        """Make a request to the Spotify API with automatic token refresh and caching for GET requests"""
        if not self.tokens:
            return None
        
        # For GET requests, check cache first
        if method == 'GET':
            cache_key = self._get_cache_key(endpoint, params)
            # Use provided cache expiry or default to standard expiry
            expiry = cache_expiry if cache_expiry is not None else self._default_cache_expiry
            cached_response = self._get_from_cache(cache_key, expiry)
            if cached_response is not None:
                return cached_response
        
        url = f"{self.base_url}/{endpoint}"
        headers = {'Authorization': f"Bearer {self.tokens['access_token']}"}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                headers['Content-Type'] = 'application/json'
                response = requests.put(url, headers=headers, json=data)
            else:
                return None
            
            # If token expired, refresh and retry
            if response.status_code == 401 and self.refresh_token():
                return self.make_api_request(endpoint, method, data, params, cache_expiry)
            
            if response.status_code not in (200, 201):
                return None
            
            response_data = response.json()
            # Cache successful GET responses
            if method == 'GET':
                expiry = cache_expiry if cache_expiry is not None else self._default_cache_expiry
                self._set_to_cache(cache_key, response_data, expiry)
            
            return response_data
        except Exception:
            return None
    
    def get_user_profile(self, access_token=None):
        """Get the current user's profile, use extended cache as profile data changes infrequently"""
        if access_token:
            headers = {'Authorization': f"Bearer {access_token}"}
            response = requests.get(f"{self.base_url}/me", headers=headers)
            if response.status_code != 200:
                return None
            return response.json()
        
        return self.make_api_request('me', cache_expiry=self._extended_cache_expiry)
    
    def get_liked_songs(self, limit=50):
        """Get the user's liked songs"""
        songs = []
        offset = 0
        
        while True:
            params = {'limit': 50, 'offset': offset}
            response = self.make_api_request('me/tracks', params=params)
            
            if not response or 'items' not in response:
                break
            
            items = response['items']
            if not items:
                break
            
            for item in items:
                track = item['track']
                artists = [artist['name'] for artist in track['artists']]
                songs.append({
                    'name': track['name'],
                    'artist': ', '.join(artists),
                    'uri': track['uri'],
                    'popularity': track['popularity'],
                    'album': track['album']['name'],
                    'release_date': track['album']['release_date']
                })
            
            offset += len(items)
            if len(items) < 50 or offset >= limit:
                break
        
        return songs
    
    def create_playlist(self, name, track_uris):
        """Create a playlist with the given tracks, invalidate user playlists cache after creation"""
        # Get user ID
        user_profile = self.get_user_profile()
        if not user_profile:
            return None
        
        user_id = user_profile['id']
        
        # Create playlist
        data = {
            'name': name,
            'description': 'Generated by AI based on your music taste',
            'public': True
        }
        
        playlist = self.make_api_request(f'users/{user_id}/playlists', method='POST', data=data)
        if not playlist:
            return None
        
        # Add tracks to playlist (in batches of 100)
        playlist_id = playlist['id']
        
        for i in range(0, len(track_uris), 100):
            batch = track_uris[i:i+100]
            data = {'uris': batch}
            self.make_api_request(f'playlists/{playlist_id}/tracks', method='POST', data=data)
        
        # Invalidate cache for user playlists to ensure updated list is fetched next time
        cache_key = self._get_cache_key(f'users/{user_id}/playlists')
        if cache_key in self._cache:
            del self._cache[cache_key]
            del self._cache_timestamps[cache_key]
        
        return {
            'id': playlist['id'],
            'name': playlist['name'],
            'url': playlist['external_urls']['spotify'],
            'tracks': len(track_uris)
        }
    
    def search_tracks(self, query, limit=10):
        """Search for tracks on Spotify"""
        params = {
            'q': query,
            'type': 'track',
            'limit': limit
        }
        
        response = self.make_api_request('search', params=params)
        
        if not response or 'tracks' not in response:
            return []
        
        tracks = []
        for item in response['tracks']['items']:
            artists = [artist['name'] for artist in item['artists']]
            tracks.append({
                'name': item['name'],
                'artist': ', '.join(artists),
                'uri': item['uri'],
                'popularity': item['popularity'],
                'album': item['album']['name'],
                'release_date': item['album']['release_date'],
                'preview_url': item['preview_url']
            })
        
        return tracks
        
    def validate_credentials(self):
        """Validate that the Spotify credentials are working"""
        try:
            auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            headers = {
                'Authorization': f'Basic {auth_header}',
            }
            response = requests.get('https://accounts.spotify.com/api/token', headers=headers)
            # We expect a 400 with invalid_client error if credentials are wrong
            # We expect a 400 with invalid_request error if credentials are correct but request is incomplete
            if response.status_code == 400 and 'error' in response.json():
                return response.json()['error'] != 'invalid_client'
            return False
        except Exception:
            return False
