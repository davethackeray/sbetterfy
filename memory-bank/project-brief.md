# Project Brief: sBetterfy

## Overview
**sBetterfy** is a Flask-based web application designed to integrate with Spotify to provide personalized music recommendations using Google Gemini AI. The application allows users to authenticate with Spotify, input their developer credentials, and receive AI-generated music recommendations based on their liked songs and customizable preferences such as genres, moods, discovery level, and release year range.

## Project Analysis
Through a thorough review of the project files, the following key components and functionalities were identified:

- **Main Application Logic (`main.py`)**: Serves as the core of the application with Flask routing, session management, and API endpoints for user authentication, Spotify credential management, and recommendation generation.
- **Spotify Integration (`spotify_service.py`)**: Handles Spotify API interactions including authentication, token management, fetching user data (liked songs, profile), creating playlists, and searching tracks.
- **Recommendation Engine (`recommendation_service.py`)**: Utilizes Google Gemini AI to generate music recommendations based on user preferences and liked songs, with verification of tracks via Spotify search.
- **User Data Management (`user_service.py`)**: Manages storage and retrieval of sensitive user data (Spotify credentials, tokens, API keys) using Fernet encryption for security.
- **Database (`database.py`)**: Uses SQLite to store user data with a simple schema, initialized at application startup.
- **Onboarding Templates (`setup_spotify.html`, `setup_api.html`)**: Provide user interfaces for setting up Spotify Developer credentials and Google Gemini AI API keys with guided tutorials.

## Proposed Improvements
During the planning phase, a comprehensive set of improvements was proposed to enhance the project across multiple dimensions:

1. **Security Enhancements**:
   - Implement robust key management for encryption beyond environment variables.
   - Configure secure session cookies with attributes like `Secure`, `HttpOnly`, and `SameSite=Strict`.
   - Strengthen input validation for API endpoints to prevent abuse.

2. **Performance Optimizations**:
   - Cache Spotify API responses for frequently accessed data to reduce latency.
   - Optimize recommendation processing by batching search requests.
   - Add database indexes to improve query performance.

3. **Code Maintainability and Structure**:
   - Use Flask blueprints for better routing modularity.
   - Enhance error handling with specific exception types.
   - Improve documentation with detailed docstrings and comments.

4. **User Experience Improvements**:
   - Provide descriptive feedback in API responses for better user guidance.
   - Extend recommendation customization with additional parameters like tempo or energy.

5. **Technical Debt Reduction**:
   - Introduce database migration tools like Alembic for schema evolution.
   - Develop a test suite for reliability and refactoring support.

6. **Automation and CI/CD**:
   - Set up automated testing and deployment pipelines to enforce coding standards.

7. **Onboarding Process**:
   - Ensure a seamless, frictionless setup for Spotify Developer Apps and Google Gemini AI API keys with guided tutorials and validation feedback.

## Actions Taken
As part of the implementation phase, the following actions have been completed:

- **Documentation and AI SWE Guidelines**: Created `docs/ai_swe_guidelines.json` to define machine-readable rules for maintaining focus on the roadmap, ensuring deep analysis before changes, frequent testing, and regular GitHub commits.
- **Onboarding Verification**: Confirmed that `setup_spotify.html` and `setup_api.html` already provide a comprehensive onboarding experience with step-by-step guides for Spotify and Google AI setup.
- **Security Improvements**: Updated `main.py` to configure secure session cookies with protective attributes (`Secure`, `HttpOnly`, `SameSite=Strict`).
- **Input Validation**: Enhanced the `/api/recommendations` endpoint in `main.py` with bounds checking for parameters (e.g., count between 1-50, discovery level between 0-100) to ensure reliability and prevent errors.

## Next Steps
- **Further Security Enhancements**: Explore advanced key management solutions for encryption.
- **Performance Tuning**: Implement caching for Spotify API calls and optimize database queries with indexes.
- **Testing Framework**: Begin developing unit and integration tests for critical components.
- **User Experience**: Add more customization options for recommendations and improve error messaging in the UI.

## Conclusion
The 'sBetterfy' project has a solid foundation with effective Spotify and AI integration for music recommendations. The implemented improvements address immediate security and usability concerns, while the proposed roadmap aims to reduce technical debt and enhance scalability. This brief serves as a record of discoveries, discussions, and actions taken during the analysis and initial enhancement phase of the project on June 14, 2025.
