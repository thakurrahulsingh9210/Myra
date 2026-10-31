import unittest
from types import SimpleNamespace
from myra_pc.providers.ai_brains import OpenAIAssistantBrain, GeminiAssistantBrain, FallbackAssistantBrain
class FakeResponses:
    def create(self, **kwargs): return SimpleNamespace(output_text="नमस्ते! How can I help?")
class FakeOpenAI: responses=FakeResponses()
class FakeModels:
    def generate_content(self, **kwargs): return SimpleNamespace(text="Hello from Gemini")
class FakeGemini: models=FakeModels()
class FailingBrain:
    async def respond(self,text,language=None): raise RuntimeError("offline")
class Tests(unittest.IsolatedAsyncioTestCase):
    async def test_openai(self): self.assertIn("नमस्ते",await OpenAIAssistantBrain(client=FakeOpenAI()).respond("hello"))
    async def test_gemini(self): self.assertEqual(await GeminiAssistantBrain(client=FakeGemini()).respond("hello"),"Hello from Gemini")
    async def test_fallback(self):
        brain=FallbackAssistantBrain([FailingBrain(),OpenAIAssistantBrain(client=FakeOpenAI())]); self.assertIn("How can I help",await brain.respond("hi","hi-IN"))
    async def test_empty_list(self):
        with self.assertRaises(ValueError): FallbackAssistantBrain([])
