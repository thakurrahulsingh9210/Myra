# Myra AI — Windows PC Edition

Windows 10/11 desktop assistant foundation for Hindi and English, with hybrid online/offline architecture.

Stage 1: Settings, task models, SQLite task journal, fail-closed risk policy.
Stage 2: OpenAI STT/TTS, offline faster-whisper STT, Windows SAPI TTS, microphone PCM16 capture, fallback and interruption.
Stage 3: OpenAI and Gemini adapters, provider fallback, local SQLite conversation history, structured planner with local risk calculation.
Stage 4: Allow-listed app launch; HTTP/HTTPS URL launch; workspace-confined file search/read/create/rename/move/delete; optional bounded mouse and keyboard controls. Mutations and simulated input require confirmation. No arbitrary shell or PowerShell execution.

Install Python 3.11+: create and activate a virtual environment, then run pip install -e ".[audio,offline,online,desktop,test]". Run tests with python -m unittest discover -s tests -v.

Set OPENAI_API_KEY and/or GEMINI_API_KEY in process environment or Windows Credential Manager. Never commit credentials. Faster-whisper must use a separately downloaded local model. Hindi offline speech depends on an installed compatible Windows Hindi SAPI voice.

Stage 4 is an action-adapter foundation. UI Automation inspection, screenshot-grounded interaction, reliable window targeting, browser DOM automation, and actual Windows 10/11 testing remain pending. Planner never executes actions. Unknown actions remain blocked; controlled and critical actions require confirmation.
