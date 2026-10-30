from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class RunMode(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    HYBRID = "hybrid"


@dataclass(frozen=True, slots=True)
class Settings:
    run_mode: RunMode = RunMode.HYBRID
    primary_language: str = "hi-IN"
    secondary_language: str = "en-IN"
    database_path: Path = Path.home() / ".myra" / "tasks.sqlite3"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        mode_value = os.getenv("MYRA_RUN_MODE", RunMode.HYBRID.value).strip().lower()
        try:
            mode = RunMode(mode_value)
        except ValueError as exc:
            raise ValueError("MYRA_RUN_MODE must be online, offline, or hybrid") from exc

        db_value = os.getenv("MYRA_DATABASE_PATH", "~/.myra/tasks.sqlite3")
        return cls(
            run_mode=mode,
            primary_language=os.getenv("MYRA_PRIMARY_LANGUAGE", "hi-IN"),
            secondary_language=os.getenv("MYRA_SECONDARY_LANGUAGE", "en-IN"),
            database_path=Path(db_value).expanduser(),
            log_level=os.getenv("MYRA_LOG_LEVEL", "INFO").upper(),
        )
