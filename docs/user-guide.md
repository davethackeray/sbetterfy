# User Guide for sBetterfy

Welcome to sBetterfy, your personalised Spotify AI Recommendations app. This guide will walk you through the steps to set up and use the application to get music recommendations based on your Spotify listening habits, powered by AI. Please follow the instructions below to get started.

**Note**: This guide uses British English spelling and terminology.

## Table of Contents
- [Getting Started](#getting-started)
- [Setting Up Spotify Developer Credentials](#setting-up-spotify-developer-credentials)
- [Connecting Your Spotify Account](#connecting-your-spotify-account)
- [Setting Up Google AI API Key](#setting-up-google-ai-api-key)
- [Using the Dashboard](#using-the-dashboard)
- [Generating AI Recommendations](#generating-ai-recommendations)
- [Troubleshooting](#troubleshooting)
- [Logging Out](#logging-out)

## Getting Started

sBetterfy is a web application that integrates with your Spotify account to analyse your music preferences and generate personalised playlists using AI. To begin, you need a Spotify account and access to the internet.

1. **Access the Application**: Open your web browser and navigate to the sBetterfy URL provided by your administrator or hosting service.
2. **Initial Screen**: You will see the welcome page with options to log in or set up your credentials if it's your first time using the app.

## Setting Up Spotify Developer Credentials

To interact with Spotify's API, you must create a Spotify Developer application to obtain the necessary credentials (Client ID and Client Secret).

1. **Visit Spotify Developer Dashboard**:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
   - Sign in with your Spotify account credentials.
2. **Create an App**:
   - Click on "Create app".
   - Fill in the app details:
     - **App name**: "AI Music Recommendations" (or any name you prefer).
     - **App description**: "Personal app for AI music recommendations".
     - **Redirect URI**: Enter the URL provided on the sBetterfy setup page (it will look something like `http://your-base-url/callback`).
     - **Website**: Enter the base URL of your sBetterfy app.
   - Accept the terms and click "Save".
3. **Retrieve Credentials**:
   - Once the app is created, you will see your Client ID.
   - Click "Show Client Secret" to reveal your Client Secret.
   - Copy both the Client ID and Client Secret.
4. **Enter Credentials in sBetterfy**:
   - Return to the sBetterfy app, navigate to the Spotify setup page.
   - Paste your Client ID and Client Secret into the respective fields.
   - Click "Save Credentials". If successful, you will see a confirmation message.

## Connecting Your Spotify Account

After saving your Spotify credentials, you need to authorise sBetterfy to access your Spotify data.

1. **Initiate Authorisation**:
   - Click on "Connect with Spotify" from the setup page or dashboard.
   - You will be redirected to Spotify's authorisation page.
2. **Grant Permissions**:
   - Review the permissions requested by sBetterfy (e.g., access to your library, playlists, and top tracks).
   - Click "Agree" to authorise the app.
3. **Return to sBetterfy**:
   - After authorisation, you will be redirected back to sBetterfy.
   - If successful, you will see a welcome message or be taken to your dashboard.

## Setting Up Google AI API Key

sBetterfy uses Google AI to generate music recommendations based on your Spotify data. You need to set up a Google AI API key for this feature.

1. **Visit Google AI Studio**:
   - Go to [Google AI Studio](https://aistudio.google.com).
   - Sign in with your Google account.
   - Accept the terms of service if prompted.
2. **Generate API Key**:
   - Click on "Get API key" in the top right corner (or navigate to "API keys" via your profile).
   - Click "Create API key" and name it (e.g., "Spotify Recommendations").
   - Copy the generated API key.
3. **Enter API Key in sBetterfy**:
   - Return to the sBetterfy app, navigate to the API setup page.
   - Paste your API key into the provided field.
   - Click "Save API Key". If successful, you will see a confirmation message and be redirected to the dashboard.

## Using the Dashboard

The dashboard is your central hub in sBetterfy where you can view your Spotify profile information and access core features.

1. **Profile Information**:
   - At the top, you will see your Spotify display name or user ID.
2. **Status Indicators**:
   - Check if your Spotify connection and Google AI API key are set up correctly (indicated by status messages or icons).
3. **Actions**:
   - **Generate Recommendations**: Click to request AI-generated music recommendations based on your Spotify data.
   - **View Playlists**: See playlists created by sBetterfy with AI recommendations.
   - **Setup Options**: Links to reconfigure Spotify credentials or API keys if needed.

## Generating AI Recommendations

sBetterfy's core feature is generating personalised music recommendations using AI.

1. **Request Recommendations**:
   - From the dashboard, click on "Generate Recommendations" or a similar button.
   - The app will analyse your Spotify data (liked songs, top tracks) and send it to the AI service.
2. **Review Recommendations**:
   - Once processed, you will see a list of recommended tracks.
   - Each recommendation may include track name, artist, and a brief explanation of why it was suggested.
3. **Create Playlist**:
   - Select tracks you like from the recommendations.
   - Click "Create Playlist" to save these tracks as a new playlist in your Spotify account.
   - Name the playlist as desired, and it will be created with the selected tracks.

## Troubleshooting

If you encounter issues while using sBetterfy, consider the following steps:

1. **Connection Problems**:
   - **Spotify Connection Failed**: Ensure your Spotify credentials are correct. Revisit the Spotify Developer Dashboard to verify your Client ID and Secret. Check if the Redirect URI matches exactly with what sBetterfy expects.
   - **API Key Issues**: If your Google AI API key is not working, generate a new one from Google AI Studio and update it in sBetterfy.
2. **Authorisation Errors**:
   - If Spotify authorisation fails, ensure you have granted all requested permissions. You may need to log out and restart the authorisation process.
3. **Recommendation Failures**:
   - If no recommendations are generated, check if both Spotify and Google AI API are properly connected. Ensure you have sufficient data in your Spotify account (liked songs, playlists) for analysis.
4. **General Errors**:
   - Look for error messages in the notification area at the top of the page. These messages will provide clues about what went wrong.
   - If problems persist, try logging out and logging back in to refresh your session.

## Logging Out

When you are finished using sBetterfy, you can log out to secure your session.

1. **Access Logout Option**:
   - From the dashboard or any page, look for a "Logout" or "Sign Out" button, usually in the header or user menu.
2. **Confirm Logout**:
   - Click the logout button. You will be redirected to the welcome page, and your session will be cleared.

---

Thank you for using sBetterfy. We hope this app enhances your music discovery experience with personalised AI recommendations. If you have further questions or need assistance, please contact the support team or refer to additional documentation provided with the app.
