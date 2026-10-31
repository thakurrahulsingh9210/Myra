# Myra AI — Windows PC Edition

Windows 10/11 desktop assistant foundation for Hindi (hi-IN) and English (en-IN), with hybrid online/offline architecture.

Stage 1: Environment-backed settings, task models, SQLite task journal, fail-closed risk policy.
Stage 2: OpenAI STT/TTS, offline faster-whisper STT, Windows SAPI TTS, microphone PCM16 capture, fallback and interruption. Offline Hindi speech depends on a compatible Windows Hindi SAPI voice.
Stage 3: OpenAI Responses API and Google Gemini SDK adapters; provider fallback; local SQLite conversation history with bounded retention and clear operation; structured task planner validates JSON and calculates risk locally. Plans are proposals only and are never executed by the planner.

Install with Python 3.11+: from pc, create a venv, activate it, then run pip install -e ".[audio,offline,online,test]". Run tests using python -m unittest discover -s tests -v.

Set OPENAI_API_KEY and/or GEMINI_API_KEY in the process environment or Windows Credential Manager. Never commit credentials. Gemini SDK reads GEMINI_API_KEY by default.

Example composition: construct FallbackAssistantBrain([OpenAIAssistantBrain(), GeminiAssistantBrain()]), wrap it with MemoryAssistant and ConversationMemory, and create TaskPlanner(brain).

Unknown actions are blocked by local policy. Controlled and critical actions require confirmation. Conversation history remains local in SQLite. The planner never executes actions or runs shell commands.
