# Build Roadmap - sBetterfy

## Overview
This document outlines the development roadmap for sBetterfy, a Flask-based web application integrating Spotify and Google Gemini AI for personalized music recommendations. The focus is on achieving a robust Minimum Viable Product (MVP) for v1 by prioritizing core functionality, user experience, performance, security, and essential documentation. This roadmap serves as a manifest of tasks for the AI SWE agent to ensure structured progress toward v1 completion.

## v1 Priorities and Task Manifest

### 1. Core Functionality
Tasks in this category ensure the fundamental features of sBetterfy are fully operational and reliable, delivering the primary value proposition of personalized music recommendations.

- **Task 1.1: Refine Spotify Authentication Flow** (Completed)
  - **Objective**: Ensure the OAuth 2.0 PKCE flow in `spotify_service.py` is robust, handling edge cases like token expiration and refresh failures.
  - **Action**: Review and enhance error handling for authentication processes, ensuring users can authenticate seamlessly.
  - **Expected Outcome**: Zero authentication failures due to unhandled errors, providing a smooth entry point for users.
  - **Status**: Completed with improved error handling for token refresh and API requests.

- **Task 1.2: Stabilize Credential Setup**
  - **Objective**: Enhance validation and error handling for Spotify Developer credentials and Google Gemini AI API keys.
  - **Action**: Update `setup_spotify.js` and `setup.js` with comprehensive input validation; ensure secure storage via `user_service.py`.
  - **Expected Outcome**: Users can input credentials without errors, with clear feedback on invalid inputs, securely stored for API interactions.
  - **Deliverables**:
    - **1.2.1: Enhance Input Validation for Spotify Credentials** - Update `setup_spotify.js` to include robust validation checks for Client ID and Client Secret fields, ensuring proper format and providing user feedback. **Effort: Small (1-2 hours)**
    - **1.2.2: Enhance Input Validation for Google Gemini AI API Key** - Update `setup.js` to validate API key input format and provide clear error messages for invalid entries. **Effort: Small (1-2 hours)**
    - **1.2.3: Improve Error Handling for Credential Storage** - Enhance backend logic in `user_service.py` to handle errors during credential storage with detailed feedback to the frontend. **Effort: Medium (3-5 hours)**

- **Task 1.3: Optimize Recommendation Engine**
  - **Objective**: Improve reliability of recommendation generation using Google Gemini AI.
  - **Action**: Refine integration in `recommendation_service.py`, ensuring track verification via Spotify search works for all inputs.
  - **Expected Outcome**: Accurate and relevant recommendations generated consistently, verified against Spotify's database.
  - **Deliverables**:
    - **1.3.1: Refine AI Integration for Reliability** - Update `recommendation_service.py` to handle edge cases in Google Gemini AI responses, ensuring consistent recommendation output. **Effort: Medium (3-5 hours)**
    - **1.3.2: Improve Track Verification Process** - Optimize the Spotify search integration in `recommendation_service.py` to verify tracks more efficiently, reducing failures. **Effort: Medium (3-5 hours)**

- **Task 1.4: Enable Playlist Creation**
  - **Objective**: Confirm recommended tracks can be saved as playlists on Spotify directly from the app.
  - **Action**: Fix any integration issues between `spotify_service.py` and frontend components for playlist creation.
  - **Expected Outcome**: Users can save recommendations as Spotify playlists with a single click, completing the core user journey.
  - **Deliverables**:
    - **1.4.1: Fix Playlist Creation Integration** - Resolve any issues in `spotify_service.py` related to creating playlists on Spotify, ensuring proper API calls. **Effort: Medium (3-5 hours)**
    - **1.4.2: Update Frontend for Playlist Saving** - Enhance `dashboard.js` to allow users to save selected recommendations as playlists with a single click, including error feedback. **Effort: Small (1-2 hours)**

### 2. User Experience
Tasks focus on refining the setup and recommendation processes to be intuitive and user-friendly, critical for user adoption and satisfaction.

- **Task 2.1: Refine Setup Process**
  - **Objective**: Streamline onboarding for non-technical users.
  - **Action**: Enhance `setup_spotify.html` and `setup_api.html` with additional feedback mechanisms and tooltips to guide credential setup.
  - **Expected Outcome**: A frictionless setup experience with clear guidance, reducing user drop-off during onboarding.
  - **Deliverables**:
    - **2.1.1: Add Tooltips to Setup Templates** - Enhance `setup_spotify.html` and `setup_api.html` with tooltips and additional guidance for credential input. **Effort: Small (1-2 hours)**
    - **2.1.2: Improve Feedback During Setup** - Update frontend scripts to provide real-time feedback during setup steps. **Effort: Small (1-2 hours)**

- **Task 2.2: Enhance Recommendation Customization**
  - **Objective**: Allow users to fine-tune recommendations with additional parameters.
  - **Action**: Update `dashboard.js` to include customization options like tempo and energy for recommendation criteria.
  - **Expected Outcome**: Users can tailor recommendations to match specific moods or activities, increasing engagement.
  - **Deliverables**:
    - **2.2.1: Add New Customization Parameters** - Update `dashboard.js` to include additional parameters like tempo and energy for recommendations. **Effort: Medium (3-5 hours)**
    - **2.2.2: Backend Support for New Parameters** - Modify `recommendation_service.py` to process new customization parameters in AI requests. **Effort: Medium (3-5 hours)**

- **Task 2.3: Improve Feedback Mechanisms**
  - **Objective**: Ensure consistent user feedback across all interactions.
  - **Action**: Extend the flash message system to all user actions in templates and frontend scripts for clear, descriptive feedback.
  - **Expected Outcome**: Users receive immediate, understandable feedback on every action or error, enhancing usability.
  - **Deliverables**:
    - **2.3.1: Extend Flash Messages to All Actions** - Ensure flash messages are used for all user interactions across templates and scripts. **Effort: Medium (3-5 hours)**

### 3. Performance Optimization
Tasks aim to ensure responsiveness and efficiency, as latency can significantly impact user satisfaction.

- **Task 3.1: Expand API Caching**
  - **Objective**: Reduce latency by caching frequently accessed Spotify API data.
  - **Action**: Build on existing caching in `spotify_service.py` for user profiles and liked songs.
  - **Expected Outcome**: Faster response times for common user actions, improving perceived performance.
  - **Deliverables**:
    - **3.1.1: Cache User Profile Data** - Update `spotify_service.py` to cache user profile data with appropriate expiration times. **Effort: Small (1-2 hours)**
    - **3.1.2: Cache Liked Songs Data** - Implement caching for liked songs retrieval in `spotify_service.py` to reduce API calls. **Effort: Small (1-2 hours)**

- **Task 3.2: Database Query Optimization**
  - **Objective**: Improve database performance for scalability.
  - **Action**: Add indexes to SQLite database in `database.py` to optimize query performance.
  - **Expected Outcome**: Quicker data retrieval and storage operations, preparing for increased user load.
  - **Deliverables**:
    - **3.2.1: Identify Performance Bottlenecks** - Analyze database queries in `database.py` to identify slow operations needing optimization. **Effort: Medium (3-5 hours)**
    - **3.2.2: Add Database Indexes** - Implement indexes on frequently queried fields in the SQLite database to improve performance. **Effort: Small (1-2 hours)**

- **Task 3.3: Batch Recommendation Processing**
  - **Objective**: Minimize API calls during recommendation generation.
  - **Action**: Optimize `recommendation_service.py` to batch Spotify search requests for recommended tracks.
  - **Expected Outcome**: Reduced API load and faster recommendation generation, enhancing user experience.
  - **Deliverables**:
    - **3.3.1: Optimize Spotify Search Requests** - Update `recommendation_service.py` to batch search requests for recommended tracks, minimizing API calls. **Effort: Medium (3-5 hours)**

### 4. Security Enhancements
Tasks address remaining security concerns to maintain user trust, especially with sensitive data handling.

- **Task 4.1: Advanced Key Management**
  - **Objective**: Implement robust encryption key management beyond environment variables.
  - **Action**: Develop a secure key management solution for `user_service.py` to protect sensitive data.
  - **Expected Outcome**: Enhanced security for user credentials and tokens, reducing risk of data breaches.
  - **Deliverables**:
    - **4.1.1: Research Key Management Options** - Investigate secure key management solutions (e.g., environment variable alternatives, key vaults) suitable for `user_service.py`. **Effort: Medium (3-5 hours)**
    - **4.1.2: Implement Key Management Solution** - Integrate the chosen key management solution to securely handle encryption keys for user data. **Effort: Large (6-10 hours)**

- **Task 4.2: Strengthen Input Validation**
  - **Objective**: Prevent potential abuse or injection attacks on API endpoints.
  - **Action**: Enhance input validation for all endpoints in `main.py` and blueprints (`api.py`, `auth.py`).
  - **Expected Outcome**: Robust protection against malicious inputs, ensuring application integrity.
  - **Deliverables**:
    - **4.2.1: Audit API Endpoints for Vulnerabilities** - Review all endpoints in `main.py`, `api.py`, and `auth.py` for potential input validation weaknesses. **Effort: Medium (3-5 hours)**
    - **4.2.2: Implement Robust Validation Checks** - Add comprehensive input validation to prevent injection attacks or abuse, updating error responses for clarity. **Effort: Large (6-10 hours)**

### 5. Documentation
Tasks ensure clear documentation for users and developers to support onboarding and future development.

- **Task 5.1: User Documentation**
  - **Objective**: Provide detailed guidance for end-users.
  - **Action**: Expand `docs/user-guide.md` with instructions on setup, customization, and usage of sBetterfy.
  - **Expected Outcome**: Users can easily understand and use the application without external support.
  - **Deliverables**:
    - **5.1.1: Update User Guide** - Enhance `docs/user-guide.md` with detailed instructions on setup, customization, and usage. **Effort: Medium (3-5 hours)**

- **Task 5.2: Technical Documentation**
  - **Objective**: Support future development and maintenance.
  - **Action**: Update `docs/` with comprehensive documentation for API endpoints, database schema, and security protocols.
  - **Expected Outcome**: Developers have clear references for extending or maintaining sBetterfy.
  - **Deliverables**:
    - **5.2.1: Document API Endpoints** - Add detailed documentation for all API endpoints in `docs/`. **Effort: Medium (3-5 hours)**
    - **5.2.2: Document Database Schema and Security Protocols** - Update `docs/` with schema details and security protocols. **Effort: Medium (3-5 hours)**

## Deprioritized for v1 (Post-MVP Focus)
These tasks are important for long-term scalability and reliability but are not critical for the v1 launch and will be addressed post-MVP:

- **Testing**: Resolve test failures (Fernet key formatting, blueprint endpoint naming, service method mismatches) and develop a full test suite. Currently paused per user request, to be revisited after v1.
  - **Deliverable 5.1: Create Unit Tests for Services** - Write unit tests for `spotify_service.py`, `recommendation_service.py`, and `user_service.py`. **Effort: Large (6-10 hours)**
  - **Deliverable 5.2: Create Integration Tests for Endpoints** - Develop integration tests for API endpoints in `api.py` and `auth.py`. **Effort: Large (6-10 hours)**
- **CI/CD Pipeline**: Set up automated testing and deployment pipelines to streamline development and ensure quality for future releases.

## Conclusion
This roadmap prioritizes tasks that deliver a functional, user-friendly, and performant MVP for sBetterfy v1, focusing on core music recommendation features and essential user experience enhancements. By following this manifest, the AI SWE agent will ensure structured progress toward a successful v1 launch, with deprioritized tasks scheduled for post-launch iterations to further enhance scalability and reliability. The detailed deliverables and effort estimations provide a clear plan for implementation, allowing for prioritization based on complexity and time requirements.
