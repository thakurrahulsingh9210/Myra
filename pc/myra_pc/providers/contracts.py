from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Transcription:
    text: str
    language: str | None = None
    is_final: bool = True


@dataclass(frozen=True, slots=True)
class SpeechResult:
    provider: str
    audio_bytes: bytes
    content_type: str = "audio/wav"


class SpeechToText(Protocol):
    async def transcribe(self, audio: bytes, language_hint: str | None = None) -> Transcription: ...


class TextToSpeech(Protocol):
    async def synthesize(self, text: str, language: str, voice: str | None = None) -> SpeechResult: ...


class AssistantBrain(Protocol):
    async def respond(self, text: str, language: str | None = None) -> str: ...
