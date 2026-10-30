# Myra AI — Windows PC Edition (Stage 1 foundation)

This is a new Windows desktop application area inside the existing Myra repository. The existing Android application and backend are preserved.

## Target
- Windows 10 and Windows 11
- Hindi (hi-IN) and English (en-IN)
- Hybrid online/offline architecture
- Local SQLite task journal

## Stage 1 currently includes
- Environment-backed settings with hybrid mode defaults
- Typed task, step, risk, and status models
- Fail-closed action risk policy
- Local SQLite task journal
- Provider contracts for STT, TTS, and the AI brain
- Desktop automation contract and Windows platform guard
- Unit tests for settings, safety policy, and task persistence

## Run the foundation tests
From this directory, using Python 3.11 or later, run:
python -m unittest discover -s tests -v

No cloud credentials are needed for these tests. No PC actions are executed by this foundation stage.

## Next stages
1. Implement online/offline STT and TTS provider adapters.
2. Implement a real Windows desktop UI and microphone lifecycle.
3. Add allow-listed Windows UI Automation actions with per-action verification.
4. Add AI planning and controlled execution behind the safety policy.

Never run arbitrary model-generated shell commands. Unknown actions are blocked by default. File changes, messages, uploads, and other controlled actions require confirmation; critical actions require explicit confirmation immediately before execution.
