from __future__ import annotations

import asyncio
import io

from .contracts import SpeechResult, Transcription


class OpenAISpeechToText:
    """OpenAI transcription adapter. Requires the optional openai package and API key."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini-transcribe", client=None):
        if client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError("Install myra-pc[online] to use OpenAI speech recognition") from exc
            client = OpenAI(api_key=api_key)
        self._client = client
        self.model = model

    async def transcribe(self, audio: bytes, language_hint: str | None = None) -> Transcription:
        def _request():
            audio_file = io.BytesIO(audio)
            audio_file.name = "myra-audio.wav"
            kwargs = {"model": self.model, "file": audio_file}
            if language_hint in {"hi", "hi-IN"}:
                kwargs["language"] = "hi"
            elif language_hint in {"en", "en-IN"}:
                kwargs["language"] = "en"
            # For Hindi-English code switching, omit language for automatic detection.
            result = self._client.audio.transcriptions.create(**kwargs)
            return Transcription(text=result.text.strip(), language=language_hint, is_final=True)
        return await asyncio.to_thread(_request)


class OpenAITextToSpeech:
    """OpenAI TTS adapter returning WAV audio bytes for downstream playback."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini-tts", voice: str = "alloy", client=None):
        if client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError("Install myra-pc[online] to use OpenAI TTS") from exc
            client = OpenAI(api_key=api_key)
        self._client = client
        self.model = model
        self.voice = voice

    async def synthesize(self, text: str, language: str, voice: str | None = None) -> SpeechResult:
        if not text.strip():
            raise ValueError("Text to speak cannot be empty")

        def _request():
            response = self._client.audio.speech.create(
                model=self.model,
                voice=voice or self.voice,
                input=text,
                response_format="wav",
                instructions=("Speak naturally and clearly in Hindi." if language.startswith("hi") else
                              "Speak naturally and clearly in Indian English."),
            )
            return response.content

        audio = await asyncio.to_thread(_request)
        return SpeechResult(provider="openai", audio_bytes=audio, content_type="audio/wav")
