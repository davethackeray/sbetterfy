# Testing Guidelines for sBetterfy

## Overview
This document outlines the testing strategy and guidelines for the 'sBetterfy' project, ensuring high-quality, reliable code through a comprehensive test suite. Testing is a critical component of reducing technical debt and maintaining scalability, aligning with the project's goals as of June 14, 2025.

## Testing Principles
- **Isolation**: Unit tests must isolate components using mocks and stubs to test functionality without external dependencies (e.g., API calls, database access).
- **Coverage**: Aim for high test coverage of core modules ('spotify_service.py', 'recommendation_service.py', 'user_service.py') and API endpoints ('main.py') to catch regressions early.
- **Automation**: Tests should be automated using pytest to run on every code change, ideally integrated into a CI/CD pipeline (Phase 6 of the roadmap).
- **Clarity**: Test names and assertions must clearly describe the behavior being tested (e.g., `test_validate_credentials_success` for successful credential validation).
- **Maintainability**: Keep tests DRY (Don't Repeat Yourself) by using fixtures and helper functions to avoid duplication.

## Test Structure
Tests are organized in the 'tests/' directory with the following structure:
- **Unit Tests**: Individual files per module (e.g., `test_spotify_service.py`, `test_recommendation_service.py`, `test_user_service.py`) focusing on isolated component behavior.
- **Integration Tests**: Files like `test_api_endpoints.py` to validate end-to-end functionality across multiple components (e.g., API routes interacting with services).
- **Future Categories**: Additional directories or files for performance tests, security tests, or UI tests as the project evolves.

## Writing Tests
### Unit Tests
- **Purpose**: Verify the behavior of individual functions or classes in isolation.
- **Tools**: Use `unittest.mock` for mocking external dependencies (e.g., API calls with `requests` or database interactions).
- **Example**: In `test_spotify_service.py`, mock `requests.post` to test `validate_credentials()` without making real API calls.
- **Guidelines**:
  - Each test method should test one specific behavior or edge case.
  - Use fixtures to set up reusable test data or mocked objects (e.g., a `spotify_service` fixture with mock credentials).
  - Assert specific outcomes rather than broad checks (e.g., `assert result is True` instead of `assert result`).

### Integration Tests
- **Purpose**: Validate interactions between components, such as API endpoints calling service methods and returning expected responses.
- **Tools**: Use Flask's `test_client()` to simulate HTTP requests and mock service responses to avoid real database or API interactions.
- **Example**: In `test_api_endpoints.py`, test the `/api/save-spotify-creds` endpoint by mocking `UserService` methods and verifying HTTP status codes and JSON responses.
- **Guidelines**:
  - Test both success and failure paths (e.g., authenticated vs. unauthenticated requests).
  - Mock underlying services to focus on endpoint logic rather than full system behavior.
  - Check response status codes, headers, and body content for correctness.

### Running Tests
- **Command**: Run tests with `pytest tests/` from the project root to execute all test files in the 'tests/' directory.
- **Coverage**: Use `pytest --cov` (with `pytest-cov` plugin) to measure test coverage once set up in CI/CD.
- **Environment**: Ensure tests run in a clean environment without real database or API access; all external interactions must be mocked.
- **Frequency**: Run tests locally before committing code and automate execution on every pull request or push in the CI pipeline (Phase 6).

## Test Coverage Goals
- **Initial Goal**: Achieve at least 80% coverage for core modules ('spotify_service.py', 'recommendation_service.py', 'user_service.py') and critical API endpoints in 'main.py'.
- **Long-Term Goal**: Reach 90%+ coverage as the test suite expands to include edge cases, error handling, and additional features.
- **Focus Areas**: Prioritize testing for security-sensitive operations (e.g., credential storage) and complex logic (e.g., recommendation generation).

## Mocking Strategy
- **External APIs**: Mock all external API calls (e.g., Spotify API, Google Gemini AI) using `unittest.mock.patch` to simulate success and failure responses.
- **Database**: Mock database interactions by patching `get_session()` or specific database methods to return predefined data or simulate errors.
- **Session Management**: Use Flask's `session_transaction()` in integration tests to simulate user sessions without real authentication.

## Test Maintenance
- **Update Tests**: Update test cases whenever code changes affect functionality, ensuring mocks reflect the latest API or database behavior.
- **Refactor Tests**: Periodically refactor tests to remove duplication and improve readability, especially as fixtures grow.
- **Document Failures**: Log known test failures or flaky tests in 'memory-bank/progress.md' under "Known Issues" until resolved.

## Future Enhancements
- **Performance Testing**: Add tests to measure latency and resource usage for critical paths like recommendation generation (Phase 7).
- **Security Testing**: Develop tests for vulnerabilities like injection attacks or session hijacking once security audits are complete (Phase 1).
- **UI Testing**: Explore tools like Selenium or Playwright for testing frontend interactions as UI complexity increases (Phase 7).
- **CI/CD Integration**: Automate test execution with coverage reporting in the CI/CD pipeline (Phase 6), failing builds below coverage thresholds.

## Running Tests for the First Time
To run the initial test suite:
```bash
pytest tests/ -v
```
This command runs all tests in the 'tests/' directory with verbose output to see which tests pass or fail.

This guideline will be updated as the testing framework evolves, ensuring alignment with the project's quality standards and roadmap objectives.
