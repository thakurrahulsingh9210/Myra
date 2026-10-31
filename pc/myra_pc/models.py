from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4
class RiskLevel(str, Enum):
 SAFE="safe"; CONTROLLED="controlled"; CRITICAL="critical"; BLOCKED="blocked"
class TaskStatus(str, Enum):
 PLANNED="planned"; RUNNING="running"; COMPLETED="completed"; FAILED="failed"; BLOCKED="blocked"; NEEDS_CONFIRMATION="needs_confirmation"; CANCELLED="cancelled"; COMPLETED_UNVERIFIED="completed_unverified"
@dataclass(frozen=True, slots=True)
class TaskStep:
 description:str
 action:str
 risk:RiskLevel
 parameters:dict[str,str]=field(default_factory=dict)
@dataclass(frozen=True, slots=True)
class TaskPlan:
 title:str
 steps:tuple[TaskStep,...]=field(default_factory=tuple)
 task_id:str=field(default_factory=lambda:str(uuid4()))
 created_at:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat())
 status:TaskStatus=TaskStatus.PLANNED
