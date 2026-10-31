from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass

from .providers.contracts import SpeechToText, TextToSpeech, Transcription, SpeechResult


class ProviderUnavailable(RuntimeError):
    pass


class FallbackSpeechToText:
    """Try providers in order; failures are collected and raised if all providers fail."""
    def __init__(self, providers: Sequence[SpeechToText]):
        if not providers:
            raise ValueError("At least one STT provider is required")
        self.providers = tuple(providers)

    async def transcribe(self, audio: bytes, language_hint: str | None = None) -> Transcription:
        errors = []
        for provider in self.providers:
            try:
                return await provider.transcribe(audio, language_hint)
            except Exception as exc:
                errors.append(f"{type(provider).__name__}: {exc}")
        raise ProviderUnavailable("All speech recognition providers failed: " + " | ".join(errors))


class FallbackTextToSpeech:
    def __init__(self, providers: Sequence[TextToSpeech]):
        if not providers:
            raise ValueError("At least one TTS provider is required")
        self.providers = tuple(providers)

    async def synthesize(self, text: str, language: str, voice: str | None = None) -> SpeechResult:
        errors = []
        for provider in self.providers:
            try:
                return await provider.synthesize(text, language, voice)
            except Exception as exc:
                errors.append(f"{type(provider).__name__}: {exc}")
        raise ProviderUnavailable("All speech synthesis providers failed: " + " | ".join(errors))


@dataclass(frozen=True, slots=True)
class MicrophoneConfig:
    sample_rate: int = 16_000
    channels: int = 1
    block_size: int = 1_600
    device: int | str | None = None
    queue_blocks: int = 20


class MicrophoneStream:
    """Async iterator of PCM16 microphone chunks, backed by optional sounddevice."""
    def __init__(self, config: MicrophoneConfig = MicrophoneConfig(), input_stream_factory=None):
        self.config = config
        self._factory = input_stream_factory
        self._queue: asyncio.Queue[bytes | BaseException | None] | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._stream = None
        self._closed = False

    async def __aenter__(self):
        if self._factory is None:
            try:
                import sounddevice as sd
            except ImportError as exc:
                raise RuntimeError("Install myra-pc[audio] to capture microphone audio") from exc
            self._factory = sd.InputStream
        self._loop = asyncio.get_running_loop()
        self._queue = asyncio.Queue(maxsize=self.config.queue_blocks)

        def callback(indata, frames, time_info, status):
            if self._closed or self._loop is None or self._queue is None:
                return
            chunk = bytes(indata)
            def enqueue():
                assert self._queue is not None
                if self._queue.full():
                    try:
                        self._queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                self._queue.put_nowait(chunk)
            self._loop.call_soon_threadsafe(enqueue)

        self._stream = self._factory(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype="int16",
            blocksize=self.config.block_size,
            device=self.config.device,
            callback=callback,
        )
        self._stream.start()
        return self

    def __aiter__(self) -> AsyncIterator[bytes]:
        return self._iterate()

    async def _iterate(self):
        if self._queue is None:
            raise RuntimeError("Use MicrophoneStream with 'async with'")
        while not self._closed:
            item = await self._queue.get()
            if item is None:
                break
            if isinstance(item, BaseException):
                raise item
            yield item

    async def __aexit__(self, exc_type, exc, tb):
        self._closed = True
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
        if self._queue is not None:
            try:
                self._queue.put_nowait(None)
            except asyncio.QueueFull:
                pass
        return False


class SpeechInterrupt:
    """Cancellation token for speech generation/playback; also stops sounddevice output."""
    def __init__(self):
        self._event = asyncio.Event()

    @property
    def interrupted(self) -> bool:
        return self._event.is_set()

    def interrupt(self) -> None:
        self._event.set()
        try:
            import sounddevice as sd
            sd.stop()
        except ImportError:
            pass

    async def wait(self) -> None:
        await self._event.wait()

    def reset(self) -> None:
        self._event.clear()

    async def run(self, awaitable):
        work = asyncio.create_task(awaitable)
        stop = asyncio.create_task(self.wait())
        done, pending = await asyncio.wait({work, stop}, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
        if stop in done:
            if not work.done():
                work.cancel()
            raise asyncio.CancelledError("Speech interrupted by user")
        stop.cancel()
        await asyncio.gather(stop, return_exceptions=True)
        return await work
