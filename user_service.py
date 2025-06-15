from cryptography.fernet import Fernet, InvalidToken
from database import get_session
import os
import logging

# Set up logging for error tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        # Prioritize local key file for development and testing
        key_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dev_master_key.txt')
        if os.path.exists(key_file_path):
            with open(key_file_path, 'r') as key_file:
                self.master_key = key_file.read().strip()
            print(f"Loaded master key from file: {key_file_path}")
        else:
            self.master_key = os.environ.get('MASTER_ENCRYPTION_KEY')
            if not self.master_key:
                raise ValueError("MASTER_ENCRYPTION_KEY environment variable not set and no local key file found at 'dev_master_key.txt'")
            else:
                print("Loaded master key from environment variable")
    
    def _get_user_cipher(self, user_id):
        # Note: Consider reusing sessions within a request context for performance
        # if multiple database operations are performed in a single request.
        try:
            session = get_session()
            user = session.execute('SELECT encryption_key FROM users WHERE id = ?', (user_id,)).fetchone()
            session.close()
            
            if user and hasattr(user, 'encryption_key') and user.encryption_key:
                # Decrypt the user's encryption key using the master key
                try:
                    master_cipher = Fernet(self.master_key)
                    user_key = master_cipher.decrypt(user.encryption_key.encode())
                    return Fernet(user_key)
                except InvalidToken as e:
                    logger.error(f"Decryption failed for user {user_id} encryption key: {e}")
                    return None
            return None
        except Exception as e:
            logger.error(f"Database error while fetching cipher for user {user_id}: {e}")
            return None

    def _generate_user_key(self, user_id):
        try:
            user_key = Fernet.generate_key()
            master_cipher = Fernet(self.master_key)
            encrypted_key = master_cipher.encrypt(user_key).decode()
            
            session = get_session()
            session.execute('INSERT OR REPLACE INTO users (id, encryption_key) VALUES (?, ?)', 
                        (user_id, encrypted_key))
            session.commit()
            session.close()
            
            return Fernet(user_key)
        except Exception as e:
            logger.error(f"Error generating user key for user {user_id}: {e}")
            raise

    def save_spotify_credentials(self, user_id, client_id, client_secret):
        try:
            cipher = self._get_user_cipher(user_id) or self._generate_user_key(user_id)
            
            if not cipher:
                raise ValueError(f"Failed to obtain cipher for user {user_id}")
                
            encrypted_client_id = cipher.encrypt(client_id.encode()).decode()
            encrypted_client_secret = cipher.encrypt(client_secret.encode()).decode()
            
            session = get_session()
            session.execute('''
                UPDATE users 
                SET spotify_client_id = ?, spotify_client_secret = ?
                WHERE id = ?
            ''', (encrypted_client_id, encrypted_client_secret, user_id))
            session.commit()
            session.close()
        except Exception as e:
            logger.error(f"Error saving Spotify credentials for user {user_id}: {e}")
            raise

    def get_spotify_credentials(self, user_id):
        try:
            # Fetch credentials and encryption key in a single query to reduce database roundtrips
            session = get_session()
            user = session.execute('''
                SELECT spotify_client_id, spotify_client_secret, encryption_key
                FROM users WHERE id = ?
            ''', (user_id,)).fetchone()
            session.close()
            
            if not user or not hasattr(user, 'spotify_client_id') or not user.spotify_client_id:
                return None
                
            cipher = None
            if hasattr(user, 'encryption_key') and user.encryption_key:
                try:
                    master_cipher = Fernet(self.master_key)
                    user_key = master_cipher.decrypt(user.encryption_key.encode())
                    cipher = Fernet(user_key)
                except InvalidToken as e:
                    logger.error(f"Decryption failed for user {user_id} encryption key: {e}")
                    return None
            if not cipher:
                return None
                
            return {
                'client_id': cipher.decrypt(user.spotify_client_id.encode()).decode(),
                'client_secret': cipher.decrypt(user.spotify_client_secret.encode()).decode()
            }
        except Exception as e:
            logger.error(f"Error retrieving Spotify credentials for user {user_id}: {e}")
            return None
    
    def save_spotify_tokens(self, user_id, tokens):
        """Save Spotify tokens for a user"""
        try:
            cipher = self._get_user_cipher(user_id) or self._generate_user_key(user_id)
            
            if not cipher:
                raise ValueError(f"Failed to obtain cipher for user {user_id}")
                
            # Encrypt tokens
            encrypted_access = cipher.encrypt(tokens['access_token'].encode()).decode()
            encrypted_refresh = cipher.encrypt(tokens['refresh_token'].encode()).decode()
            
            session = get_session()
            session.execute(
                'UPDATE users SET spotify_access_token = ?, spotify_refresh_token = ? WHERE id = ?',
                (encrypted_access, encrypted_refresh, user_id)
            )
            session.commit()
            session.close()
        except Exception as e:
            logger.error(f"Error saving Spotify tokens for user {user_id}: {e}")
            raise
    
    def get_spotify_tokens(self, user_id):
        """Get Spotify tokens for a user"""
        try:
            # Fetch tokens and encryption key in a single query to reduce database roundtrips
            session = get_session()
            user = session.execute(
                'SELECT spotify_access_token, spotify_refresh_token, encryption_key FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            session.close()
            
            if not user or not hasattr(user, 'spotify_access_token') or not user.spotify_access_token or not hasattr(user, 'spotify_refresh_token') or not user.spotify_refresh_token:
                return None
            
            cipher = None
            if hasattr(user, 'encryption_key') and user.encryption_key:
                try:
                    master_cipher = Fernet(self.master_key)
                    user_key = master_cipher.decrypt(user.encryption_key.encode())
                    cipher = Fernet(user_key)
                except InvalidToken as e:
                    logger.error(f"Decryption failed for user {user_id} encryption key: {e}")
                    return None
            if not cipher:
                return None
                
            # Decrypt tokens
            access_token = cipher.decrypt(user.spotify_access_token.encode()).decode()
            refresh_token = cipher.decrypt(user.spotify_refresh_token.encode()).decode()
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except Exception as e:
            logger.error(f"Error retrieving Spotify tokens for user {user_id}: {e}")
            return None
    
    def save_gemini_api_key(self, user_id, api_key):
        """Save Google AI API key for a user"""
        try:
            cipher = self._get_user_cipher(user_id) or self._generate_user_key(user_id)
            
            if not cipher:
                raise ValueError(f"Failed to obtain cipher for user {user_id}")
                
            # Encrypt API key
            encrypted_key = cipher.encrypt(api_key.encode()).decode()
            
            session = get_session()
            session.execute(
                'UPDATE users SET gemini_api_key = ? WHERE id = ?',
                (encrypted_key, user_id)
            )
            session.commit()
            session.close()
        except Exception as e:
            logger.error(f"Error saving Gemini API key for user {user_id}: {e}")
            raise
    
    def get_gemini_api_key(self, user_id):
        """Get Google AI API key for a user"""
        try:
            # Fetch API key and encryption key in a single query to reduce database roundtrips
            session = get_session()
            user = session.execute(
                'SELECT gemini_api_key, encryption_key FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            session.close()
            
            if not user or not hasattr(user, 'gemini_api_key') or not user.gemini_api_key:
                return None
            
            cipher = None
            if hasattr(user, 'encryption_key') and user.encryption_key:
                try:
                    master_cipher = Fernet(self.master_key)
                    user_key = master_cipher.decrypt(user.encryption_key.encode())
                    cipher = Fernet(user_key)
                except InvalidToken as e:
                    logger.error(f"Decryption failed for user {user_id} encryption key: {e}")
                    return None
            if not cipher:
                return None
                
            # Decrypt API key
            return cipher.decrypt(user.gemini_api_key.encode()).decode()
        except Exception as e:
            logger.error(f"Error retrieving Gemini API key for user {user_id}: {e}")
            return None
    
    def has_gemini_api_key(self, user_id):
        """Check if a user has set up their Google AI API key"""
        try:
            session = get_session()
            user = session.execute(
                'SELECT gemini_api_key FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            session.close()
            
            return user is not None and hasattr(user, 'gemini_api_key') and user.gemini_api_key is not None
        except Exception as e:
            logger.error(f"Error checking Gemini API key for user {user_id}: {e}")
            return False
        
    def has_spotify_credentials(self, user_id):
        """Check if a user has set up their Spotify credentials"""
        try:
            session = get_session()
            user = session.execute(
                'SELECT spotify_client_id, spotify_client_secret FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            session.close()
            
            return user is not None and hasattr(user, 'spotify_client_id') and user.spotify_client_id is not None and hasattr(user, 'spotify_client_secret') and user.spotify_client_secret is not None
        except Exception as e:
            logger.error(f"Error checking Spotify credentials for user {user_id}: {e}")
            return False
