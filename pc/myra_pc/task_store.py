from __future__ import annotations
import json,sqlite3
from datetime import datetime,timezone
from contextlib import contextmanager
from collections.abc import Iterator
from pathlib import Path
from .models import TaskPlan,TaskStatus
class TaskStore:
 """Local SQLite task and event journal."""
 def __init__(self,database_path:Path|str):
  self.database_path=Path(database_path).expanduser();self.database_path.parent.mkdir(parents=True,exist_ok=True);self._initialize()
 @contextmanager
 def _connect(self)->Iterator[sqlite3.Connection]:
  db=sqlite3.connect(self.database_path);db.row_factory=sqlite3.Row
  try:yield db;db.commit()
  except Exception:db.rollback();raise
  finally:db.close()
 def _initialize(self):
  with self._connect() as db:
   db.execute("CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY,title TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,steps_json TEXT NOT NULL)")
   db.execute("CREATE TABLE IF NOT EXISTS task_events (event_id INTEGER PRIMARY KEY AUTOINCREMENT,task_id TEXT NOT NULL,event_type TEXT NOT NULL,created_at TEXT NOT NULL,payload_json TEXT NOT NULL,FOREIGN KEY(task_id) REFERENCES tasks(task_id))")
 def add(self,plan:TaskPlan):
  steps=[{"description":s.description,"action":s.action,"risk":s.risk.value,"parameters":s.parameters} for s in plan.steps]
  with self._connect() as db:db.execute("INSERT INTO tasks(task_id,title,status,created_at,steps_json) VALUES(?,?,?,?,?)",(plan.task_id,plan.title,plan.status.value,plan.created_at,json.dumps(steps)))
 def update_status(self,task_id:str,status:TaskStatus)->bool:
  with self._connect() as db:return db.execute("UPDATE tasks SET status=? WHERE task_id=?",(status.value,task_id)).rowcount==1
 def get(self,task_id:str):
  with self._connect() as db:row=db.execute("SELECT * FROM tasks WHERE task_id=?",(task_id,)).fetchone()
  return dict(row) if row else None
 def list_recent(self,limit=50):
  if limit<1 or limit>500:raise ValueError("limit must be between 1 and 500")
  with self._connect() as db:rows=db.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
  return [dict(r) for r in rows]
 def record_event(self,task_id:str,event_type:str,payload:dict):
  if not event_type or len(event_type)>80:raise ValueError("event_type must contain 1 to 80 characters")
  raw=json.dumps(payload,ensure_ascii=False)
  if len(raw)>16000:raise ValueError("event payload exceeds 16 KB")
  with self._connect() as db:
   if not db.execute("SELECT 1 FROM tasks WHERE task_id=?",(task_id,)).fetchone():raise KeyError(f"Unknown task: {task_id}")
   db.execute("INSERT INTO task_events(task_id,event_type,created_at,payload_json) VALUES(?,?,?,?)",(task_id,event_type,datetime.now(timezone.utc).isoformat(),raw))
 def list_events(self,task_id:str)->list[dict]:
  with self._connect() as db:rows=db.execute("SELECT event_id,event_type,created_at,payload_json FROM task_events WHERE task_id=? ORDER BY event_id",(task_id,)).fetchall()
  return [{"event_id":r["event_id"],"event_type":r["event_type"],"created_at":r["created_at"],"payload":json.loads(r["payload_json"])} for r in rows]
