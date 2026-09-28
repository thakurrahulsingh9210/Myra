# Myra Realtime backend

The backend is responsible for validating the Auth0 access token, enforcing account policy, minting a short-lived OpenAI Realtime client credential, and never exposing the permanent OpenAI API key to Android.

Environment: `OPENAI_API_KEY`, `AUTH0_DOMAIN`, `AUTH0_AUDIENCE`.

The Android client should call `POST /api/realtime-token` with its Auth0 access token.
