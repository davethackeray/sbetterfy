from flask import Flask
import os
from dotenv import load_dotenv
import secrets
from database import init_db
from blueprints.auth import auth_bp
from blueprints.api import api_bp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

# Configure session cookies for security
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to False for development over HTTP; change to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,  # Prevents client-side scripts from accessing cookies
    SESSION_COOKIE_SAMESITE='Lax',  # Set to Lax to allow cookies on cross-site requests after redirects
    PERMANENT_SESSION_LIFETIME=3600  # Session lifetime in seconds (1 hour)
)

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
