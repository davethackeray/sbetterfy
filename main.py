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
    SESSION_COOKIE_SECURE=True,  # Ensures cookies are only sent over HTTPS
    SESSION_COOKIE_HTTPONLY=True,  # Prevents client-side scripts from accessing cookies
    SESSION_COOKIE_SAMESITE='Strict'  # Protects against CSRF by restricting cookie to same-site requests
)

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
