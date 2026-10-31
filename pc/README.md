# Myra AI — Windows PC Edition

Windows 10/11 desktop assistant foundation for Hindi and English, with hybrid online/offline architecture.

Stage 1: Settings, task models, SQLite task journal, fail-closed risk policy.
Stage 2: OpenAI STT/TTS, offline faster-whisper STT, Windows SAPI TTS, microphone PCM16 capture, fallback and interruption.
Stage 3: OpenAI and Gemini adapters, provider fallback, local SQLite conversation history, structured planner with local risk calculation.
Stage 4: Allow-listed app launch; HTTP/HTTPS URL launch; workspace-confined file search/read/create/rename/move/delete; optional bounded mouse and keyboard controls. Mutations and simulated input require confirmation.
Stage 5: Sequential plan execution; local risk recalculation before each action; per-step approval for controlled/critical actions; fail-closed unknown actions; cancellation and fail-fast errors; SQLite event journal; separate completed and completed-unverified statuses.

Install Python 3.11+: create and activate a virtual environment, then run pip install -e ".[audio,offline,online,desktop,test]". Run tests with python -m unittest discover -s tests -v.

Set OPENAI_API_KEY and/or GEMINI_API_KEY in process environment or Windows Credential Manager. Never commit credentials. Faster-whisper must use a separately downloaded local model. Hindi offline speech depends on an installed compatible Windows Hindi SAPI voice.

The planner only proposes actions. The executor connects proposals to the registered Windows action adapter. Safe registered actions may run automatically; controlled and critical actions require a real per-step user confirmation callback. Never use an always-true callback in production. The executor is synchronous, so desktop UI applications should run it off the UI thread.

UI Automation and screenshot-grounded verification, browser DOM automation, interrupted-task resume, robust window targeting, and actual Windows 10/11 hardware testing remain pending. A successful action with verified=False is reported as completed_unverified, not verified completion. Conversation history is stored locally but is sent as context to the selected online AI provider when online memory is used; do not store secrets in conversation history.
