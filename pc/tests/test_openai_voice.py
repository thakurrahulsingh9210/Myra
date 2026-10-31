import unittest
from myra_pc.providers.openai_voice import OpenAISpeechToText, OpenAITextToSpeech

class FakeTranscriptions:
    def __init__(self): self.kwargs = None
    def create(self, **kwargs):
        self.kwargs = kwargs
        return type("Result", (), {"text": "नमस्ते Myra"})()

class FakeSpeech:
    def create(self, **kwargs):
        self.kwargs = kwargs
        return type("Response", (), {"content": b"RIFF-fake-wav"})()

class FakeAudio:
    def __init__(self):
        self.transcriptions = FakeTranscriptions()
        self.speech = FakeSpeech()

class FakeClient:
    def __init__(self): self.audio = FakeAudio()

class OpenAIVoiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_stt_hindi_hint_and_code_switch_autodetect(self):
        client = FakeClient()
        stt = OpenAISpeechToText(client=client)
        result = await stt.transcribe(b"RIFF-audio", "hi-IN")
        self.assertEqual(result.text, "नमस्ते Myra")
        self.assertEqual(client.audio.transcriptions.kwargs["language"], "hi")
        await stt.transcribe(b"RIFF-audio", None)
        self.assertNotIn("language", client.audio.transcriptions.kwargs)

    async def test_tts_returns_wav_bytes(self):
        client = FakeClient()
        result = await OpenAITextToSpeech(client=client).synthesize("नमस्ते", "hi-IN")
        self.assertEqual(result.provider, "openai")
        self.assertEqual(result.audio_bytes, b"RIFF-fake-wav")
        self.assertEqual(client.audio.speech.kwargs["response_format"], "wav")

if __name__ == "__main__":
    unittest.main()
