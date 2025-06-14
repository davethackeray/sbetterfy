from cryptography.fernet import Fernet
from database import get_db_connection
import os

class UserService:
    def __init__(self):
        self.master_key = os.environ.get('MASTER_ENCRYPTION_KEY')
        if not self.master_key:
            # Fallback to a local key file for development purposes
            key_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dev_master_key.txt')
            if os.path.exists(key_file_path):
                with open(key_file_path, 'r') as key_file:
                    self.master_key = key_file.read().strip()
            else:
                raise ValueError("MASTER_ENCRYPTION_KEY environment variable not set and no local key file found at 'dev_master_key.txt'")
    
    def _get_user_cipher(self, user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT encryption_key FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        
        if user and user['encryption_key']:
            # Decrypt the user's encryption key using the master key
            master_cipher = Fernet(self.master_key)
            user_key = master_cipher.decrypt(user['encryption_key'].encode())
            return Fernet(user_key)
        return None

    def _generate_user_key(self, user_id):
        user_key = Fernet.generate_key()
        master_cipher = Fernet(self.master_key)
        encrypted_key = master_cipher.encrypt(user_key).decode()
        
        conn = get_db_connection()
        conn.execute('INSERT OR REPLACE INTO users (id, encryption_key) VALUES (?, ?)', 
                    (user_id, encrypted_key))
        conn.commit()
        conn.close()
        
        return Fernet(user_key)

    def save_spotify_credentials(self, user_id, client_id, client_secret):
        cipher = self._get_user_cipher(user_id) or self._generate_user_key(user_id)
        
        encrypted_client_id = cipher.encrypt(client_id.encode()).decode()
        encrypted_client_secret = cipher.encrypt(client_secret.encode()).decode()
        
        conn = get_db_connection()
        conn.execute('''
            UPDATE users 
            SET spotify_client_id = ?, spotify_client_secret = ?
            WHERE id = ?
        ''', (encrypted_client_id, encrypted_client_secret, user_id))
        conn.commit()
        conn.close()

    def get_spotify_credentials(self, user_id):
        conn = get_db_connection()
        user = conn.execute('''
            SELECT spotify_client_id, spotify_client_secret 
            FROM users WHERE id = ?
        ''', (user_id,)).fetchone()
        conn.close()
        
        if not user or not user['spotify_client_id']:
            return None
            
        cipher = self._get_user_cipher(user_id)
        if not cipher:
            return None
            
        return {
            'client_id': cipher.decrypt(user['spotify_client_id'].encode()).decode(),
            'client_secret': cipher.decrypt(user['spotify_client_secret'].encode()).decode()
        }
    
    def save_spotify_tokens(self, user_id, tokens):
        """Save Spotify tokens for a user"""
        cipher = self._get_user_cipher(user_id) or self._generate_user_key(user_id)
        
        # Encrypt tokens
        encrypted_access = cipher.encrypt(tokens['access_token'].encode()).decode()
        encrypted_refresh = cipher.encrypt(tokens['refresh_token'].encode()).decode()
        
        conn = get_db_connection()
        conn.execute(
            'UPDATE users SET spotify_access_token = ?, spotify_refresh_token = ? WHERE id = ?',
            (encrypted_access, encrypted_refresh, user_id)
        )
        conn.commit()
        conn.close()
    
    def get_spotify_tokens(self, user_id):
        """Get Spotify tokens for a user"""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT spotify_access_token, spotify_refresh_token FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        conn.close()
        
        if not user or not user['spotify_access_token'] or not user['spotify_refresh_token']:
            return None
        
        cipher = self._get_user_cipher(user_id)
        if not cipher:
            return None
            
        # Decrypt tokens
        access_token = cipher.decrypt(user['spotify_access_token'].encode()).decode()
        refresh_token = cipher.decrypt(user['spotify_refresh_token'].encode()).decode()
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    
    def save_gemini_api_key(self, user_id, api_key):
        """Save Google AI API key for a user"""
        cipher = self._get_user_cipher(user_id) or self._generate_user_key(user_id)
        
        # Encrypt API key
        encrypted_key = cipher.encrypt(api_key.encode()).decode()
        
        conn = get_db_connection()
        conn.execute(
            'UPDATE users SET gemini_api_key = ? WHERE id = ?',
            (encrypted_key, user_id)
        )
        conn.commit()
        conn.close()
    
    def get_gemini_api_key(self, user_id):
        """Get Google AI API key for a user"""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT gemini_api_key FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        conn.close()
        
        if not user or not user['gemini_api_key']:
            return None
        
        cipher = self._get_user_cipher(user_id)
        if not cipher:
            return None
            
        # Decrypt API key
        return cipher.decrypt(user['gemini_api_key'].encode()).decode()
    
    def has_gemini_api_key(self, user_id):
        """Check if a user has set up their Google AI API key"""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT gemini_api_key FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        conn.close()
        
        return user is not None and user['gemini_api_key'] is not None
        
    def has_spotify_credentials(self, user_id):
        """Check if a user has set up their Spotify credentials"""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT spotify_client_id, spotify_client_secret FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        conn.close()
        
        return user is not None and user['spotify_client_id'] is not None and user['spotify_client_secret'] is not None
