# Myra AI — Windows PC Edition

Windows 10/11 desktop assistant foundation for Hindi (hi-IN) and English (en-IN) with hybrid online/offline design.

## Stage 1 foundation
- Environment-backed settings, task models, SQLite task journal
- Fail-closed action risk policy and automation contracts

## Stage 2 voice engine
- OpenAI speech-to-text adapter (gpt-4o-mini-transcribe by default)
- OpenAI text-to-speech adapter (gpt-4o-mini-tts by default)
- Offline faster-whisper STT using a pre-downloaded local model directory (local_files_only=True)
- Offline Windows SAPI TTS through pyttsx3 (Windows 10/11 only)
- Async microphone PCM16 streaming via sounddevice
- STT/TTS provider fallback chains
- Speech interruption/cancellation controller
- Hindi, English, and code-switching support: pass hi-IN or en-IN for a known language; pass None for automatic language detection/code-switching

## Install
Use Python 3.11+.

```powershell
cd pc
py -3.11 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[audio,offline,online,test]"
python -m unittest discover -s tests -v
```

The faster-whisper model must be downloaded separately and placed in a local folder; runtime loading is local-only and does not download a model. Set MYRA_WHISPER_MODEL_PATH to that folder. The installed SAPI voice determines Hindi availability; Windows offline Hindi speech requires a compatible Hindi voice installed in Windows.

Set OPENAI_API_KEY in the process environment or Windows Credential Manager for online OpenAI features. Do not put real secrets in .env.example or Git.

## Microphone example

```python
async with MicrophoneStream() as microphone:
    async for pcm16_chunk in microphone:
        # Accumulate/VAD-segment chunks into a complete WAV before STT.
        ...
```

The microphone stream produces raw PCM16 chunks at 16 kHz mono by default. A production VAD/utterance segmenter and audio playback/UI lifecycle are Stage 2 follow-up work; this stream alone is not a full always-listening assistant.

## Safety
This stage provides voice I/O components only. It does not execute PC actions. Unknown actions remain blocked by default. Do not pass model-generated shell commands to a terminal.
