# Security Guidelines for sBetterfy

## Overview
This document outlines the security protocols, encryption methods, and best practices for the 'sBetterfy' project, a Flask-based web application integrating Spotify with Google Gemini AI for personalized music recommendations. Adhering to these guidelines ensures the protection of user data, prevents unauthorized access, and mitigates potential vulnerabilities. These guidelines are intended for developers, AI SWE agents, and contributors working on the project as of June 14, 2025.

## 1. Data Encryption
### 1.1 Key Management
- **Master Encryption Key**: The master encryption key is used to encrypt and decrypt user-specific encryption keys. It is sourced from the environment variable 'MASTER_ENCRYPTION_KEY'. For development environments, a fallback mechanism exists to use a local file 'dev_master_key.txt' if the environment variable is not set.
  - **Development**: The file 'dev_master_key.txt' must be excluded from version control (listed in '.gitignore') and should only be used for non-production purposes. It contains a development key with a warning not to use in production.
  - **Production**: In production environments, use a secure secrets management solution (e.g., HashiCorp Vault, AWS Secrets Manager) to store and retrieve the master key dynamically. Avoid hardcoding or storing keys in environment variables directly accessible in code repositories.
- **User-Specific Keys**: Each user has a unique encryption key stored in the database, encrypted by the master key. These keys are used to encrypt user data such as Spotify credentials and API keys.

### 1.2 Encryption Implementation
- **Library**: Use the 'cryptography' library's Fernet (symmetric encryption) for encrypting sensitive user data.
- **Usage**: All sensitive data (Spotify client ID, client secret, access tokens, refresh tokens, Google Gemini AI API keys) must be encrypted before storage in the SQLite database and decrypted only when needed for API calls.
- **Best Practice**: Ensure encryption and decryption operations are performed in secure, isolated functions within 'user_service.py' to minimize exposure of plaintext data in memory.

## 2. Session Security
- **Configuration**: Flask session cookies are configured with the following security attributes in 'main.py':
  - `SESSION_COOKIE_SECURE=True`: Ensures cookies are only sent over HTTPS connections.
  - `SESSION_COOKIE_HTTPONLY=True`: Prevents client-side scripts from accessing cookies, mitigating XSS attacks.
  - `SESSION_COOKIE_SAMESITE='Strict'`: Restricts cookies to same-site requests, protecting against CSRF attacks.
- **Secret Key**: The Flask application secret key is sourced from the environment variable 'SECRET_KEY', with a fallback to a randomly generated key if not set. In production, always set 'SECRET_KEY' to a secure, unpredictable value.
- **Best Practice**: Regularly rotate the secret key in production environments and ensure it is stored securely (not in version control).

## 3. Input Validation and Sanitization
- **API Endpoints**: All API endpoints receiving user input must implement comprehensive input validation to prevent injection attacks and abuse.
  - **Implemented Endpoints**: As of June 14, 2025, the following endpoints in 'main.py' have robust validation:
    - `/api/recommendations`: Validates count (1-50), discovery level (0-100), minimum year (1900-2025), maximum popularity (0-100), and ensures genres and moods are lists.
    - `/api/save-spotify-creds`: Validates client ID and client secret as strings with minimum length requirements.
    - `/api/save-api-key`: Validates API key as a string with a minimum length requirement.
    - `/api/create-playlist`: Validates playlist name as a string (max 100 characters), track URIs as a list (max 100 items), and ensures URI format starts with 'spotify:track:'.
  - **Validation Rules**: Check for correct data types, enforce reasonable bounds, and sanitize inputs to remove malicious content.
- **Best Practice**: Use libraries or custom functions to sanitize inputs (e.g., strip potentially harmful characters or scripts). Log validation failures for monitoring potential attack attempts without exposing sensitive details.

## 4. Authentication and Authorization
- **Spotify Authentication**: User authentication with Spotify is handled via OAuth 2.0 through 'spotify_service.py'. Ensure redirect URIs and client credentials are securely stored (encrypted in the database) and not exposed in client-side code.
- **Session Management**: User sessions are managed with temporary IDs before Spotify authentication and permanent IDs post-authentication. Ensure session data is minimal and does not store sensitive information directly (e.g., tokens should be in the database, not session).
- **Best Practice**: Implement token expiration checks and refresh mechanisms in 'spotify_service.py' to prevent unauthorized access with expired tokens. Regularly audit authentication flows for vulnerabilities.

## 5. Database Security
- **SQLite Usage**: The current database is SQLite, which is file-based. Ensure the database file (e.g., 'sbetterfy.db') is stored in a secure location with restricted file permissions and excluded from version control (listed in '.gitignore').
- **Query Safety**: Use parameterized queries in all database operations (as implemented in 'database.py' and 'user_service.py') to prevent SQL injection attacks.
- **Best Practice**: In production, consider transitioning to a more robust database like PostgreSQL with built-in user authentication and encryption features. Encrypt sensitive fields at rest using the mechanisms described in section 1.2.

## 6. API Security
- **Rate Limiting**: Currently not implemented. Consider adding rate limiting to API endpoints to prevent abuse and denial-of-service attacks.
- **CORS Policies**: Ensure Cross-Origin Resource Sharing (CORS) is configured appropriately if the API is accessed from different domains, restricting access to trusted origins only.
- **Best Practice**: Use HTTPS for all API communications (enforced by session cookie settings). Implement API key or token-based authentication for future external API consumers if applicable.

## 7. Logging and Monitoring
- **Logging**: Avoid logging sensitive information (e.g., encryption keys, user tokens, API keys) in plaintext. Current logging is minimal; enhance with structured logging to track security events (e.g., failed login attempts, validation errors) without exposing sensitive data.
- **Monitoring**: Implement monitoring for unusual activity (e.g., repeated failed API calls) in future phases to detect potential attacks early.
- **Best Practice**: Store logs in a secure, centralized location in production environments and rotate logs regularly to manage size and exposure risk.

## 8. Secure Development Practices
- **Code Review**: All code changes, especially those involving security (e.g., encryption, authentication), must be reviewed for potential vulnerabilities before merging.
- **Dependency Management**: Regularly update dependencies listed in 'requirements.txt' to patch known vulnerabilities. Use tools like 'pip-audit' to identify insecure packages.
- **Secrets Management**: Never hardcode secrets or keys in source code. Use environment variables or secure secrets management as described in section 1.1.
- **AI SWE Guidelines**: Adhere to the rules in 'docs/ai_swe_guidelines.json', ensuring deep analysis before changes, frequent testing, and regular commits to maintain security integrity during development.

## 9. Security Audit and Testing
- **Audit Plan**: Conduct periodic security audits to identify vulnerabilities in authentication, data storage, and API interactions. This is a pending task (Task 1.3 from the roadmap) to be addressed with external tools or services.
- **Penetration Testing**: Perform penetration testing to simulate attacks (e.g., XSS, CSRF, SQL injection) and address findings. This should be scheduled after initial security enhancements are in place.
- **Progress Update**: As of June 14, 2025, initial security enhancements like session security and input validation are in progress or completed (Phase 1). Full security audit and penetration testing are scheduled for Weeks 1-3 as part of Phase 1: Foundation and Security Enhancements.
- **Best Practice**: Document audit and testing results in 'memory-bank/security-audit-reports.md' for future reference and continuous improvement.

## 10. Incident Response
- **Plan**: Develop an incident response plan for security breaches (e.g., data leaks, unauthorized access). This includes identifying the breach, containing it, notifying affected users, and patching the vulnerability.
- **Communication**: Ensure transparent communication with users in case of a breach, following legal and ethical guidelines for data protection.
- **Best Practice**: Maintain a draft incident response plan in 'docs/incident-response-plan.md' and update it based on audit findings and evolving threats.

## Conclusion
Security is a foundational aspect of the 'sBetterfy' project to protect user data and maintain trust. By following these guidelines, developers and AI SWE agents ensure that security is integrated into every phase of development, from coding to deployment. This document will be updated as new security practices are implemented or as threats evolve, aligning with the project's roadmap for continuous improvement.
