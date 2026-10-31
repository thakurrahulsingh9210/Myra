from __future__ import annotations
import json
from dataclasses import dataclass
from .models import RiskLevel, TaskPlan, TaskStep
from .safety import classify_action

@dataclass(frozen=True, slots=True)
class PlannedAction:
    action: str
    description: str
    parameters: dict[str, str]
    risk: RiskLevel

@dataclass(frozen=True, slots=True)
class StructuredPlan:
    title: str
    summary: str
    actions: tuple[PlannedAction, ...]
    @property
    def needs_confirmation(self):
        return any(a.risk in {RiskLevel.CONTROLLED, RiskLevel.CRITICAL} for a in self.actions)

class TaskPlanner:
    """Validate AI-proposed JSON into a plan. Never executes actions."""
    def __init__(self, brain, max_actions=12): self.brain, self.max_actions = brain, max_actions
    async def plan(self, request, language=None):
        prompt = ("Create a safe proposed desktop task plan. Return ONLY JSON with shape "
          '{"title":"...","summary":"...","actions":[{"action":"open_app","description":"...","parameters":{"app":"notepad"}}]}. '
          f"Maximum {self.max_actions} actions. Registered actions only: read_screen, open_app, switch_window, search_files, read_file, create_file, rename_file, move_file, send_message, upload_file, delete_file, empty_recycle_bin, purchase, transfer_money, shutdown, restart, change_security_settings. "
          "Never propose shell commands, scripts, credential extraction, security bypass, or hidden actions. If no action fits, return an empty actions array. User request: " + request)
        return self.parse(await self.brain.respond(prompt, language))
    def parse(self, raw):
        try: data = json.loads(raw)
        except json.JSONDecodeError as exc: raise ValueError("AI planner returned invalid JSON") from exc
        if not isinstance(data, dict) or not isinstance(data.get("actions"), list): raise ValueError("Plan must be an object with an actions array")
        title, summary = data.get("title"), data.get("summary", "")
        if not isinstance(title, str) or not title.strip() or not isinstance(summary, str): raise ValueError("Plan title and summary must be strings")
        if len(data["actions"]) > self.max_actions: raise ValueError("Plan exceeds maximum action count")
        actions = []
        for item in data["actions"]:
            if not isinstance(item, dict): raise ValueError("Each action must be an object")
            action, description, params = item.get("action"), item.get("description"), item.get("parameters", {})
            if not isinstance(action, str) or not isinstance(description, str): raise ValueError("Action and description are required strings")
            if not isinstance(params, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k,v in params.items()): raise ValueError("Action parameters must be string-to-string values")
            if len(params) > 20 or any(len(k) > 80 or len(v) > 1000 for k,v in params.items()): raise ValueError("Action parameters exceed size limits")
            actions.append(PlannedAction(action, description, dict(params), classify_action(action)))
        return StructuredPlan(title.strip(), summary, tuple(actions))
    @staticmethod
    def to_task_plan(plan):
        return TaskPlan(title=plan.title, steps=tuple(TaskStep(a.description, a.action, a.risk, a.parameters) for a in plan.actions))
