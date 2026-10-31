import asyncio
import unittest
from myra_pc.voice import MicrophoneConfig, MicrophoneStream

class FakeInputStream:
    def __init__(self, **kwargs):
        self.callback = kwargs["callback"]
        self.closed = False
    def start(self): pass
    def stop(self): pass
    def close(self): self.closed = True

class MicrophoneTests(unittest.IsolatedAsyncioTestCase):
    async def test_stream_delivers_pcm_chunks_and_closes(self):
        holder = {}
        def factory(**kwargs):
            holder["stream"] = FakeInputStream(**kwargs)
            return holder["stream"]
        async with MicrophoneStream(MicrophoneConfig(queue_blocks=2), factory) as mic:
            holder["stream"].callback(b"pcm16", 3, None, None)
            await asyncio.sleep(0)
            chunk = await anext(mic.__aiter__())
            self.assertEqual(chunk, b"pcm16")
        self.assertTrue(holder["stream"].closed)

if __name__ == "__main__":
    unittest.main()
