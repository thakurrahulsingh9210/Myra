from __future__ import annotations

import asyncio
import platform
from pathlib import Path

from .contracts import SpeechResult, Transcription


class FasterWhisperSpeechToText:
    """Offline STT using a pre-downloaded faster-whisper model directory."""

    def __init__(self, model_path: str | Path, device: str = "cpu", compute_type: str = "int8", model=None):
        if model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError("Install myra-pc[offline] to use offline speech recognition") from exc
            path = Path(model_path).expanduser()
            if not path.exists():
                raise FileNotFoundError(f"Offline Whisper model directory not found: {path}")
            model = WhisperModel(str(path), device=device, compute_type=compute_type, local_files_only=True)
        self._model = model

    async def transcribe(self, audio: bytes, language_hint: str | None = None) -> Transcription:
        import tempfile

        def _request():
            with tempfile.NamedTemporaryFile(suffix=".wav") as audio_file:
                audio_file.write(audio)
                audio_file.flush()
                lang = "hi" if language_hint == "hi-IN" else "en" if language_hint == "en-IN" else None
                segments, info = self._model.transcribe(audio_file.name, language=lang, beam_size=5, vad_filter=True)
                text = " ".join(segment.text.strip() for segment in segments).strip()
                return Transcription(text=text, language=getattr(info, "language", lang), is_final=True)
        return await asyncio.to_thread(_request)


class WindowsTextToSpeech:
    """Offline Windows SAPI TTS through pyttsx3. Speech is synthesized to a WAV file."""

    def __init__(self, rate: int = 185, volume: float = 1.0, engine_factory=None):
        if platform.system() != "Windows":
            raise RuntimeError("Windows offline TTS requires Windows 10/11 and SAPI")
        if engine_factory is None:
            try:
                import pyttsx3
            except ImportError as exc:
                raise RuntimeError("Install myra-pc[offline] to use Windows TTS") from exc
            engine_factory = pyttsx3.init
        self._engine_factory = engine_factory
        self.rate = rate
        self.volume = max(0.0, min(1.0, volume))

    async def synthesize(self, text: str, language: str, voice: str | None = None) -> SpeechResult:
        if not text.strip():
            raise ValueError("Text to speak cannot be empty")
        import tempfile

        def _synthesize():
            engine = self._engine_factory("sapi5")
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            if voice:
                engine.setProperty("voice", voice)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as target:
                path = target.name
            try:
                engine.save_to_file(text, path)
                engine.runAndWait()
                return Path(path).read_bytes()
            finally:
                Path(path).unlink(missing_ok=True)
                engine.stop()
        audio = await asyncio.to_thread(_synthesize)
        return SpeechResult(provider="windows-sapi", audio_bytes=audio, content_type="audio/wav")
