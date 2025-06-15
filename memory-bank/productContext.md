# Product Context - sBetterfy

## Why This Project Exists
sBetterfy is created to provide users with a personalized music recommendation experience by leveraging Spotify's vast music library and the power of Google Gemini AI. It aims to bridge the gap between Spotify's user data and advanced AI capabilities to offer tailored music suggestions that align with individual tastes and preferences.

## Problems It Solves
- **Generic Recommendations**: Standard Spotify recommendations may not always capture the nuanced preferences of users. sBetterfy uses AI to analyze liked songs and user-defined parameters to deliver more personalized suggestions.
- **User Control**: Users often lack fine-grained control over recommendation criteria. sBetterfy allows customization of genres, moods, discovery levels, and release year ranges to refine the recommendation output.
- **Integration Complexity**: Setting up developer credentials and API keys for Spotify and AI services can be daunting. sBetterfy simplifies this with a guided onboarding process to make the integration accessible to non-technical users.

## How It Should Work
- **Authentication**: Users authenticate with Spotify to grant access to their liked songs and playlist creation capabilities.
- **Credential Setup**: Through an intuitive interface, users input their Spotify Developer credentials and Google Gemini AI API keys, which are securely stored.
- **Recommendation Generation**: Users specify their preferences (genres, moods, etc.), and the application fetches their liked songs from Spotify, processes them with Google Gemini AI, and generates a list of recommended tracks.
- **Playlist Creation**: Recommended tracks can be saved as playlists on the user's Spotify account directly from the application.
- **Feedback Loop**: The system provides clear feedback on actions, errors, and setup processes to ensure users are informed at every step.

## User Experience Goals
- **Simplicity**: The setup process for Spotify Developer Apps and Google Gemini AI API keys should be frictionless, with step-by-step guides and validation feedback to assist users.
- **Customization**: Offer extensive options for users to tailor their music recommendations, ensuring the results match their current mood or interest.
- **Feedback**: Implement consistent and descriptive feedback mechanisms (like flash messages) across the application to guide users through successful actions and errors.
- **Responsiveness**: Ensure the application is performant, with minimal latency in generating recommendations and interacting with Spotify's API, achieved through caching and optimized queries.
- **Security**: Maintain user trust by securely handling sensitive data (credentials, tokens) with encryption and secure authentication flows like OAuth 2.0 PKCE.
