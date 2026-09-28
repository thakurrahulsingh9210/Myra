# Myra AI Assistant

Native Android voice assistant built with Kotlin, Jetpack Compose, Auth0, and OpenAI Realtime.

## Baseline
- Android API 26+
- Java/Kotlin 17
- Auth0.Android 4.0.1
- Jetpack Compose
- OpenAI Realtime over WebRTC
- Backend-issued short-lived Realtime credentials

## Security
The Android app never contains a permanent OpenAI API key. It calls the Myra backend with an Auth0 access token; the backend validates the user and mints a short-lived Realtime credential.

## Setup
1. Create an Auth0 Native Application.
2. Put the Auth0 domain/client ID in `app/src/main/res/values/strings.xml`.
3. Configure the Auth0 callback for package `com.myra.assistant`.
4. Deploy the backend in `backend/` and set the backend URL in the app.
5. Put the OpenAI API key only in the backend environment.
6. Open the project in Android Studio and sync Gradle.

The initial WebRTC engine is isolated behind `RealtimeVoiceEngine` so transport details can evolve without coupling the UI or action engine to the provider.
