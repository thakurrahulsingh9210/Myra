from __future__ import annotations
import asyncio

class OpenAIAssistantBrain:
    """OpenAI Responses API adapter."""
    def __init__(self, api_key=None, model="gpt-4.1-mini", client=None):
        if client is None:
            try: from openai import OpenAI
            except ImportError as exc: raise RuntimeError("Install myra-pc[online] to use OpenAI") from exc
            client = OpenAI(api_key=api_key)
        self._client, self.model = client, model
    async def respond(self, text, language=None):
        if not text.strip(): raise ValueError("Prompt cannot be empty")
        instructions = "You are Myra, a helpful Windows desktop assistant. Reply in the user's language. Understand Hindi, English, and mixed Hindi-English. Never claim to have performed an action."
        if language: instructions += f" Preferred response language: {language}."
        def request():
            result = self._client.responses.create(model=self.model, instructions=instructions, input=text)
            answer = getattr(result, "output_text", "")
            if not answer: raise RuntimeError("OpenAI returned an empty response")
            return answer.strip()
        return await asyncio.to_thread(request)

class GeminiAssistantBrain:
    """Google Gemini SDK adapter; reads GEMINI_API_KEY from environment by default."""
    def __init__(self, api_key=None, model="gemini-2.5-flash", client=None):
        if client is None:
            try: from google import genai
            except ImportError as exc: raise RuntimeError("Install myra-pc[online] to use Gemini") from exc
            client = genai.Client(api_key=api_key)
        self._client, self.model = client, model
    async def respond(self, text, language=None):
        if not text.strip(): raise ValueError("Prompt cannot be empty")
        prompt = ("You are Myra, a helpful Windows desktop assistant. Reply in the user's language. "
                  "Understand Hindi, English, and mixed Hindi-English. Never claim to have performed an action.\n"
                  f"Preferred language: {language or 'automatically match the user'}.\nUser: {text}")
        def request():
            result = self._client.models.generate_content(model=self.model, contents=prompt)
            answer = getattr(result, "text", None)
            if not answer: raise RuntimeError("Gemini returned an empty response")
            return answer.strip()
        return await asyncio.to_thread(request)

class FallbackAssistantBrain:
    """Try configured brains in order and report failures if all fail."""
    def __init__(self, providers):
        self.providers = tuple(providers)
        if not self.providers: raise ValueError("At least one AI provider is required")
    async def respond(self, text, language=None):
        failures = []
        for provider in self.providers:
            try: return await provider.respond(text, language)
            except Exception as exc: failures.append(f"{type(provider).__name__}: {exc}")
        raise RuntimeError("All AI providers failed: " + " | ".join(failures))
