import asyncio
import unittest

from myra_pc.providers.contracts import SpeechResult, Transcription
from myra_pc.voice import FallbackSpeechToText, FallbackTextToSpeech, ProviderUnavailable, SpeechInterrupt


class BrokenSTT:
    async def transcribe(self, audio, language_hint=None):
        raise RuntimeError("offline model unavailable")


class WorkingSTT:
    async def transcribe(self, audio, language_hint=None):
        return Transcription("नमस्ते Myra", "hi", True)


class BrokenTTS:
    async def synthesize(self, text, language, voice=None):
        raise RuntimeError("network unavailable")


class WorkingTTS:
    async def synthesize(self, text, language, voice=None):
        return SpeechResult("local-test", b"wav", "audio/wav")


class VoiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_stt_falls_back_to_next_provider(self):
        result = await FallbackSpeechToText([BrokenSTT(), WorkingSTT()]).transcribe(b"audio", "hi-IN")
        self.assertEqual(result.text, "नमस्ते Myra")

    async def test_tts_falls_back_to_next_provider(self):
        result = await FallbackTextToSpeech([BrokenTTS(), WorkingTTS()]).synthesize("Hello", "en-IN")
        self.assertEqual(result.provider, "local-test")

    async def test_all_provider_failures_are_reported(self):
        with self.assertRaises(ProviderUnavailable):
            await FallbackSpeechToText([BrokenSTT()]).transcribe(b"audio")

    async def test_interrupt_cancels_pending_speech_task(self):
        controller = SpeechInterrupt()
        async def long_speech():
            await asyncio.sleep(30)
        task = asyncio.create_task(controller.run(long_speech()))
        await asyncio.sleep(0)
        controller.interrupt()
        with self.assertRaises(asyncio.CancelledError):
            await task

    async def test_interrupt_can_be_reset(self):
        controller = SpeechInterrupt()
        controller.interrupt()
        self.assertTrue(controller.interrupted)
        controller.reset()
        self.assertFalse(controller.interrupted)


if __name__ == "__main__":
    unittest.main()
