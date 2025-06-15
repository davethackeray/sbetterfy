# Technical Context - sBetterfy

## Technologies Used
- **Flask**: A lightweight Python web framework used for building the backend of sBetterfy, handling routing, session management, and API endpoint creation.
- **Python**: The primary programming language for backend development, including service logic and data processing.
- **SQLite**: A lightweight, file-based database used for storing user data and credentials, chosen for its simplicity and ease of setup.
- **SQLAlchemy**: An ORM (Object-Relational Mapping) library for Python, used to interact with the SQLite database in a more Pythonic way.
- **Alembic**: A database migration tool for SQLAlchemy, used to manage schema changes and maintain version control of the database structure.
- **Fernet**: A symmetric encryption library used to secure sensitive user data such as Spotify credentials and API keys.
- **Spotify API**: An external API for fetching user data (liked songs, profile), creating playlists, and searching tracks, integrated via OAuth 2.0 with PKCE flow for security.
- **Google Gemini AI**: An AI service used for generating personalized music recommendations based on user preferences and liked songs.
- **HTML/CSS/JavaScript**: Frontend technologies for creating user interfaces (`templates/` for HTML, `static/css/` for CSS, `static/js/` for JavaScript), providing interactivity and visual feedback.
- **Jinja2**: A templating engine used with Flask to render dynamic content in HTML templates.

## Development Setup
- **Environment**: Development is conducted on a Windows 11 system with PowerShell as the default shell.
- **Project Directory**: The project resides in `c:/Users/Thack/Documents/_projects/sbetterfy`, containing all source code, static files, templates, and documentation.
- **Dependencies**: Managed via `requirements.txt`, listing all Python packages required for the project (e.g., Flask, SQLAlchemy, Alembic, etc.).
- **Database Initialization**: The SQLite database is initialized through `database.py` at application startup, creating necessary tables if they don't exist.
- **Encryption Key**: Stored in `dev_master_key.txt`, used by Fernet for encrypting sensitive data. This key must be correctly formatted to avoid errors in encryption/decryption processes.
- **Configuration**: Environment variables and configuration settings are managed via `.env` file for sensitive information like API keys (though advanced key management is planned for future security enhancements).

## Technical Constraints
- **Scale**: SQLite is suitable for small to medium-scale applications but may face performance issues with a large user base. Future scalability plans involve database optimization and potential migration to a more robust database system if needed.
- **API Rate Limits**: Spotify API has rate limits on requests, necessitating caching mechanisms to avoid hitting these limits during frequent data fetches.
- **Security**: Handling sensitive user data requires strict adherence to security best practices, including secure session management (e.g., secure cookies with `Secure`, `HttpOnly`, `SameSite=Strict` attributes) and encryption.
- **Browser Compatibility**: Frontend JavaScript and CSS must be compatible with major browsers to ensure a consistent user experience across different platforms.

## Dependencies
- **External Libraries**: Key Python libraries include Flask for web framework, SQLAlchemy for database ORM, Alembic for migrations, and cryptography for Fernet encryption. Full list in `requirements.txt`.
- **External Services**: Spotify API for music data and user interactions, Google Gemini AI for recommendation generation. Both require API keys and credentials to be set up by users during onboarding.
- **Internal Modules**: The application relies on internal service modules (`spotify_service.py`, `recommendation_service.py`, `user_service.py`) and database interactions (`database.py`), which are interdependent for core functionalities like authentication and recommendation generation.

## Tool Usage Patterns
- **Git and GitHub**: Used for version control and collaboration. Frequent commits are encouraged to track changes and ensure project history is preserved, as per user instructions.
- **VSCode**: The primary IDE for development, with visible files and open tabs indicating active work areas. It provides integration with Git for committing changes and viewing project structure.
- **Pytest**: Framework for writing and running tests, though testing is currently paused as per user request. Test files are located in the `tests/` directory.
- **Alembic Commands**: Used for database migration management. Commands like `alembic stamp head` have been used to align migration history with existing schema, and future schema changes will use `alembic revision` and `alembic upgrade`.
- **Documentation Tools**: Markdown files in `memory-bank/` and `docs/` directories for maintaining project documentation, ensuring continuity after memory resets as per user guidelines.
