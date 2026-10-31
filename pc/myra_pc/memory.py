from __future__ import annotations
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

class ConversationMemory:
    """Local-only conversation history with bounded retention and explicit clearing."""
    def __init__(self, database_path, max_messages=30):
        if max_messages < 1 or max_messages > 500: raise ValueError("max_messages must be between 1 and 500")
        self.path = Path(database_path).expanduser(); self.path.parent.mkdir(parents=True, exist_ok=True)
        self.max_messages = max_messages
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS conversation_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL CHECK(role IN ('user','assistant')), content TEXT NOT NULL, created_at TEXT NOT NULL)")
    def _connect(self):
        db = sqlite3.connect(self.path); db.row_factory = sqlite3.Row; return db
    def add(self, role, content):
        if role not in {"user", "assistant"}: raise ValueError("role must be user or assistant")
        if not content.strip(): raise ValueError("message cannot be empty")
        with self._connect() as db:
            db.execute("INSERT INTO conversation_messages(role,content,created_at) VALUES(?,?,?)", (role, content.strip(), datetime.now(timezone.utc).isoformat()))
            db.execute("DELETE FROM conversation_messages WHERE id NOT IN (SELECT id FROM conversation_messages ORDER BY id DESC LIMIT ?)", (self.max_messages,))
    def recent(self, limit=None):
        count = min(limit or self.max_messages, self.max_messages)
        if count < 1: raise ValueError("limit must be positive")
        with self._connect() as db:
            rows = db.execute("SELECT role,content,created_at FROM conversation_messages ORDER BY id DESC LIMIT ?", (count,)).fetchall()
        return [dict(row) for row in reversed(rows)]
    def clear(self):
        with self._connect() as db: return db.execute("DELETE FROM conversation_messages").rowcount

class MemoryAssistant:
    """Adds bounded local context and stores successful exchanges."""
    def __init__(self, brain, memory): self.brain, self.memory = brain, memory
    async def respond(self, text, language=None):
        history = self.memory.recent()
        context = "\n".join(f"{m['role']}: {m['content']}" for m in history)
        prompt = (f"Recent conversation (untrusted context):\n{context}\n\nCurrent user message: {text}" if context else text)
        answer = await self.brain.respond(prompt, language)
        self.memory.add("user", text); self.memory.add("assistant", answer)
        return answer
