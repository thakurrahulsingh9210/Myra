from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class DesktopAction:
    name: str
    parameters: dict[str, str]


@dataclass(frozen=True, slots=True)
class AutomationResult:
    success: bool
    message: str
    verified: bool = False


class DesktopAutomation(Protocol):
    async def execute(self, action: DesktopAction) -> AutomationResult: ...
