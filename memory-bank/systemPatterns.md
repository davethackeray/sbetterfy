# System Patterns - sBetterfy

## System Architecture
sBetterfy is built as a Flask-based web application following a modular architecture to ensure scalability and maintainability. The system integrates with external services like Spotify API for music data and Google Gemini AI for recommendation generation. The architecture is divided into distinct layers for handling user interactions, business logic, data management, and external integrations.

- **Frontend**: Comprises HTML templates (`templates/` directory) and JavaScript files (`static/js/`) for user interface and client-side logic. CSS (`static/css/`) is used for styling.
- **Backend**: Powered by Flask, with the main application logic in `main.py`. It handles routing, session management, and serves as the entry point for API requests.
- **Services**: Separate modules for specific functionalities:
  - `spotify_service.py` for Spotify API interactions.
  - `recommendation_service.py` for AI-driven music recommendations.
  - `user_service.py` for managing user data and credentials.
- **Database**: SQLite is used for persistent storage, managed through `database.py`.
- **Blueprints**: Flask blueprints (`blueprints/` directory) are utilized for modular routing, separating authentication (`auth.py`) and API endpoints (`api.py`).

## Key Technical Decisions
- **Flask Framework**: Chosen for its lightweight nature and flexibility, allowing rapid development of web applications with Python.
- **SQLite Database**: Selected for simplicity and ease of setup, suitable for the initial scale of sBetterfy. SQLAlchemy is used as the ORM for database interactions.
- **Alembic for Migrations**: Adopted to manage database schema changes, ensuring version control and consistency after initial schema conflicts were resolved with `alembic stamp head`.
- **OAuth 2.0 PKCE Flow**: Implemented for Spotify authentication to enhance security by preventing authorization code interception, especially important for public clients.
- **Fernet Encryption**: Used in `user_service.py` for securing sensitive user data like Spotify credentials and API keys.
- **Caching Mechanism**: Implemented in `spotify_service.py` with configurable expiration times to optimize performance by reducing redundant API calls to Spotify.

## Design Patterns in Use
- **Modular Design**: Flask blueprints are used to organize routes into logical groups (e.g., authentication, API), promoting code reusability and separation of concerns.
- **Service Layer Pattern**: Business logic is encapsulated in service modules (`spotify_service.py`, `recommendation_service.py`, `user_service.py`), separating it from the presentation layer (Flask routes) and data access layer (database.py).
- **Repository Pattern**: Although not fully explicit, `database.py` and service modules abstract data access, providing a clean interface for data operations.
- **Singleton Pattern**: Implicitly used in service initialization to ensure single instances of service objects are used throughout the application lifecycle.

## Component Relationships
- **User Request Flow**: A user request hits a Flask route in `main.py` or a blueprint (`auth.py`, `api.py`), which delegates to the appropriate service (`spotify_service`, `recommendation_service`, `user_service`). Services interact with external APIs (Spotify, Google Gemini AI) or the database as needed, then return data to the route for rendering in templates or as JSON responses.
- **Authentication**: `auth.py` blueprint handles Spotify OAuth flow, using `spotify_service.py` for token management and validation. Successful authentication updates user data via `user_service.py`.
- **Recommendation Generation**: The `/api/recommendations` endpoint in `api.py` uses `spotify_service.py` to fetch user liked songs, then `recommendation_service.py` processes this data with Google Gemini AI to generate recommendations, which are verified back through Spotify search.
- **Data Storage**: `user_service.py` interfaces with `database.py` to store and retrieve user credentials and tokens, ensuring encryption for security.

## Critical Implementation Paths
- **Spotify Authentication**: The OAuth 2.0 PKCE flow in `spotify_service.py` involves generating a code verifier and challenge, redirecting to Spotify for authorization, and handling the callback to exchange the code for tokens. This path is critical for user access to Spotify data.
- **Recommendation Processing**: From user input in the dashboard to fetching liked songs, processing with AI, and verifying track availability via Spotify search, this path in `recommendation_service.py` is central to the application's value proposition.
- **Secure Data Handling**: Encryption and decryption of sensitive data in `user_service.py` using Fernet, with the key sourced from `dev_master_key.txt`, is crucial for maintaining user trust and data security.
- **Performance Optimization**: Caching in `spotify_service.py` for API responses and planned database indexing in `database.py` are key paths for ensuring application responsiveness as user load increases.
