# Operations Manual for sBetterfy

This operations manual provides a high-level overview of the internal workings of sBetterfy, a Spotify AI Recommendations web application. It is intended for developers and maintainers to understand the application's architecture, key processes, and logic flows. The descriptions are provided in pseudocode to abstract implementation details while focusing on the operational structure.

## Table of Contents
- [Application Overview](#application-overview)
- [Architecture](#architecture)
- [Key Components](#key-components)
- [Operational Flows](#operational-flows)
- [Maintenance and Troubleshooting](#maintenance-and-troubleshooting)

## Application Overview

sBetterfy integrates with Spotify's API to fetch user data (liked songs, top tracks) and uses Google AI to generate personalised music recommendations. The application manages user authentication, credential storage, API interactions, and playlist creation.

**Primary Objectives**:
- Securely authenticate users with Spotify using OAuth 2.0 PKCE flow.
- Store and manage user credentials and API keys securely.
- Fetch and analyse Spotify user data.
- Generate AI-based music recommendations.
- Create Spotify playlists from recommendations.

## Architecture

sBetterfy follows a modular web application architecture built with Flask, a Python micro-framework. The high-level structure is as follows:

```
sBetterfy/
├── main.py              // Application entry point and configuration
├── database.py          // Database setup and ORM models
├── user_service.py      // User data and credential management
├── spotify_service.py   // Spotify API interactions
├── recommendation_service.py // AI recommendation logic
├── blueprints/          // Modular Flask blueprints for routing
│   ├── auth.py          // Authentication and user setup routes
│   └── api.py           // API endpoints for recommendations
├── templates/           // HTML templates for UI
├── static/              // CSS, JavaScript, and other static assets
└── migrations/          // Database schema migrations with Alembic
```

**Pseudocode for Application Initialisation**:
```
FUNCTION initialise_app():
    CONFIGURE Flask app with environment variables
    INITIALISE database connection with SQLite
    REGISTER blueprints for authentication and API routes
    SET UP session management for user tracking
    RETURN configured app instance
```

## Key Components

### 1. User Service (`user_service.py`)
Manages user data, including Spotify credentials and API keys, with encryption for security.

**Pseudocode for User Data Management**:
```
FUNCTION save_user_credentials(user_id, spotify_client_id, spotify_client_secret):
    ENCRYPT client_id and client_secret using encryption_key
    STORE encrypted credentials in database for user_id
    RETURN success status

FUNCTION get_spotify_credentials(user_id):
    RETRIEVE encrypted credentials from database for user_id
    DECRYPT credentials using encryption_key
    RETURN decrypted client_id and client_secret

FUNCTION save_spotify_tokens(user_id, tokens):
    ENCRYPT access_token and refresh_token
    UPDATE user record in database with encrypted tokens
    RETURN success status

FUNCTION has_gemini_api_key(user_id):
    CHECK if user_id has a stored Google AI API key in database
    RETURN boolean indicating presence of API key
```

### 2. Spotify Service (`spotify_service.py`)
Handles interactions with Spotify API, including authentication, data fetching, and playlist creation.

**Pseudocode for Spotify Authentication (PKCE Flow)**:
```
FUNCTION get_auth_url(state):
    GENERATE random code_verifier (128 characters)
    COMPUTE code_challenge as base64_urlsafe_sha256(code_verifier)
    CONSTRUCT auth_url with client_id, redirect_uri, scope, code_challenge, and state
    RETURN auth_url for user redirection

FUNCTION get_tokens(code):
    IF code_verifier not set, RAISE error
    PREPARE basic auth header with client_id and client_secret
    SEND POST request to Spotify token endpoint with code, redirect_uri, and code_verifier
    IF response status is 200:
        CLEAR code_verifier
        RETURN token data (access_token, refresh_token)
    ELSE:
        RETURN null
```

**Pseudocode for Spotify API Requests**:
```
FUNCTION make_api_request(endpoint, method='GET', data=None, params=None):
    IF no tokens available, RETURN null
    IF method is GET:
        CHECK cache for endpoint and params
        IF cached response exists and not expired, RETURN cached response
    APPLY rate limiting by throttling requests to 10 per second
    CONSTRUCT request with endpoint, headers (Bearer token), and data/params
    SEND request to Spotify API
    IF response status is 401 (unauthorised):
        REFRESH token and retry request
    IF response status not in (200, 201), RETURN null
    IF method is GET:
        CACHE response with timestamp, enforcing max cache size of 1000 entries
    RETURN response data
```

### 3. Recommendation Service (`recommendation_service.py`)
Generates music recommendations using Google AI based on Spotify user data.

**Pseudocode for Recommendation Generation**:
```
FUNCTION generate_recommendations(user_id, spotify_data):
    RETRIEVE Google AI API key for user_id
    FORMAT spotify_data (liked songs, top tracks) into prompt for AI
    SEND request to Google AI API with prompt and API key
    IF response successful:
        PARSE AI response for recommended tracks and explanations
        RETURN list of recommendations
    ELSE:
        RETURN empty list or error message
```

### 4. Authentication Blueprint (`blueprints/auth.py`)
Manages user authentication, setup, and session handling.

**Pseudocode for User Login Flow**:
```
FUNCTION login():
    IF user_id already in session, REDIRECT to dashboard
    GENERATE temporary user_id
    STORE user_id in session as temp_user_id
    RENDER setup_spotify.html with base_url for redirect URI

FUNCTION authorize_spotify():
    RETRIEVE user_id from session (temp_user_id or user_id)
    IF no user_id, REDIRECT to login
    FETCH Spotify credentials for user_id
    IF no credentials, REDIRECT to login
    INITIALISE SpotifyService with credentials
    GET auth_url from SpotifyService with user_id as state
    REDIRECT user to auth_url

FUNCTION callback():
    EXTRACT code and state from request parameters
    IF no code or state, REDIRECT to index
    SET user_id = state
    FETCH Spotify credentials for user_id
    INITIALISE SpotifyService with credentials
    EXCHANGE code for tokens using SpotifyService
    IF tokens received:
        FETCH user profile using access_token
        SAVE tokens for user_id
        UPDATE session with user_id, spotify_user_id, display_name
        IF user has Google AI API key:
            REDIRECT to dashboard
        ELSE:
            REDIRECT to setup_api
    ELSE:
        REDIRECT to login
```

### 5. Database Management (`database.py` and `migrations/`)
Handles data storage and schema evolution using SQLAlchemy and Alembic.

**Pseudocode for Database Setup**:
```
FUNCTION get_engine():
    CONFIGURE SQLAlchemy engine with SQLite URL
    RETURN engine instance

FUNCTION define_models():
    DEFINE User model with fields:
        id (primary key)
        spotify_client_id (encrypted)
        spotify_client_secret (encrypted)
        spotify_access_token (encrypted)
        spotify_refresh_token (encrypted)
        gemini_api_key (encrypted)
        encryption_key
    RETURN model definitions for ORM use
```

## Operational Flows

### User Setup and Authentication Flow
```
START:
    USER accesses root URL
    IF user_id in session:
        REDIRECT to dashboard
    ELSE:
        RENDER index.html for login
    USER clicks login:
        GENERATE temp_user_id
        RENDER setup_spotify.html
    USER enters Spotify credentials:
        SAVE credentials for temp_user_id
        REDIRECT to authorize_spotify
    USER authorises via Spotify:
        REDIRECT to callback with code and state
        EXCHANGE code for tokens
        UPDATE session with user data
        IF Google AI API key set:
            REDIRECT to dashboard
        ELSE:
            REDIRECT to setup_api
    USER enters Google AI API key:
        SAVE API key for user_id
        REDIRECT to dashboard
END
```

### Recommendation Generation Flow
```
START:
    USER on dashboard clicks "Generate Recommendations"
    FETCH Spotify data (liked songs, top tracks) using SpotifyService
    FORMAT data into AI prompt
    SEND prompt to Google AI API via RecommendationService
    RECEIVE recommendations from AI
    DISPLAY recommendations to user
    USER selects tracks for playlist:
        PROMPT for playlist name
        CALL SpotifyService to create playlist with selected tracks
        DISPLAY success message with playlist link
END
```

## Maintenance and Troubleshooting

### Database Maintenance
```
PROCEDURE update_database_schema():
    IF new schema changes needed:
        GENERATE new migration script with Alembic
        REVIEW migration script for accuracy
        APPLY migration with 'alembic upgrade head'
    ELSE:
        CHECK current migration status with 'alembic current'
        IF not at head, APPLY 'alembic upgrade head'
```

### API Rate Limiting and Errors
```
PROCEDURE handle_api_errors():
    MONITOR Spotify API responses for status codes
    IF status code 429 (Too Many Requests):
        LOG rate limit exceeded
        INCREASE wait time in rate limiting logic
        RETRY request after delay
    IF status code 401 (Unauthorised):
        REFRESH token and retry
    IF persistent errors:
        NOTIFY admin for credential or configuration check
```

### Cache Management
```
PROCEDURE manage_cache():
    MONITOR cache size against max_cache_size
    IF approaching limit:
        LOG cache nearing capacity
        EVICT oldest entries based on timestamp
    PERIODICALLY check for expired entries:
        REMOVE entries older than cache_expiry
```

### Security Checks
```
PROCEDURE security_audit():
    VERIFY encryption_key in dev_master_key.txt is valid for Fernet
    CHECK all sensitive data fields are encrypted in database
    CONFIRM PKCE flow is used for Spotify authentication
    IF vulnerabilities found:
        UPDATE security protocols
        NOTIFY development team for immediate action
```

---

This operations manual provides a foundation for understanding and maintaining sBetterfy. For detailed implementation specifics, refer to the source code and inline documentation. Regular updates to this manual may be necessary as the application evolves.
