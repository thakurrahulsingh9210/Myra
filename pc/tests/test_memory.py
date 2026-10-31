import tempfile, unittest
from pathlib import Path
from myra_pc.memory import ConversationMemory, MemoryAssistant
class FakeBrain:
    async def respond(self,text,language=None): self.prompt=text; return "Namaste"
class Tests(unittest.TestCase):
    def test_retention(self):
        with tempfile.TemporaryDirectory() as d:
            m=ConversationMemory(Path(d)/"m.db",2);m.add("user","one");m.add("assistant","two");m.add("user","three");self.assertEqual([x["content"] for x in m.recent()],["two","three"])
    def test_clear(self):
        with tempfile.TemporaryDirectory() as d:
            m=ConversationMemory(Path(d)/"m.db");m.add("user","hello");self.assertEqual(m.clear(),1);self.assertEqual(m.recent(),[])
    def test_bad_role(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): ConversationMemory(Path(d)/"m.db").add("system","secret")
class AsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_context_and_exchange(self):
        with tempfile.TemporaryDirectory() as d:
            m=ConversationMemory(Path(d)/"m.db");b=FakeBrain();a=MemoryAssistant(b,m);await a.respond("Hi Myra");self.assertEqual([x["role"] for x in m.recent()],["user","assistant"]);await a.respond("Remember greeting");self.assertIn("Hi Myra",b.prompt)
