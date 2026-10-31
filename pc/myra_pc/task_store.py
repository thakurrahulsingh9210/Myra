from __future__ import annotations
import json, sqlite3
from contextlib import contextmanager
from collections.abc import Iterator
from pathlib import Path
from .models import TaskPlan, TaskStatus
class TaskStore:
    """Local SQLite task journal; it does not execute tasks."""
    def __init__(self, database_path: Path | str):
        self.database_path=Path(database_path).expanduser(); self.database_path.parent.mkdir(parents=True,exist_ok=True); self._initialize()
    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection=sqlite3.connect(self.database_path); connection.row_factory=sqlite3.Row
        try: yield connection; connection.commit()
        except Exception: connection.rollback(); raise
        finally: connection.close()
    def _initialize(self):
        with self._connect() as db: db.execute("CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY,title TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,steps_json TEXT NOT NULL)")
    def add(self, plan: TaskPlan):
        steps=[{"description":s.description,"action":s.action,"risk":s.risk.value,"parameters":s.parameters} for s in plan.steps]
        with self._connect() as db: db.execute("INSERT INTO tasks(task_id,title,status,created_at,steps_json) VALUES(?,?,?,?,?)",(plan.task_id,plan.title,plan.status.value,plan.created_at,json.dumps(steps)))
    def update_status(self, task_id: str, status: TaskStatus) -> bool:
        with self._connect() as db: return db.execute("UPDATE tasks SET status=? WHERE task_id=?",(status.value,task_id)).rowcount==1
    def get(self, task_id: str):
        with self._connect() as db: row=db.execute("SELECT * FROM tasks WHERE task_id=?",(task_id,)).fetchone()
        return dict(row) if row else None
    def list_recent(self, limit=50):
        if limit<1 or limit>500: raise ValueError("limit must be between 1 and 500")
        with self._connect() as db: rows=db.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
        return [dict(row) for row in rows]
