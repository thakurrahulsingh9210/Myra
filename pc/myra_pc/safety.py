from __future__ import annotations

from .models import RiskLevel


# Explicit allow-list: unknown actions are blocked until reviewed and registered.
_ACTION_RISKS: dict[str, RiskLevel] = {
    "read_screen": RiskLevel.SAFE,
    "open_app": RiskLevel.SAFE,
    "switch_window": RiskLevel.SAFE,
    "search_files": RiskLevel.SAFE,
    "read_file": RiskLevel.SAFE,
    "create_file": RiskLevel.CONTROLLED,
    "rename_file": RiskLevel.CONTROLLED,
    "move_file": RiskLevel.CONTROLLED,
    "send_message": RiskLevel.CONTROLLED,
    "upload_file": RiskLevel.CONTROLLED,
    "delete_file": RiskLevel.CRITICAL,
    "empty_recycle_bin": RiskLevel.CRITICAL,
    "purchase": RiskLevel.CRITICAL,
    "transfer_money": RiskLevel.CRITICAL,
    "shutdown": RiskLevel.CRITICAL,
    "restart": RiskLevel.CRITICAL,
    "change_security_settings": RiskLevel.CRITICAL,
    "run_arbitrary_shell": RiskLevel.BLOCKED,
    "disable_security_software": RiskLevel.BLOCKED,
    "bypass_access_controls": RiskLevel.BLOCKED,
}


def classify_action(action: str) -> RiskLevel:
    """Return the registered risk for an action; unknown actions fail closed."""
    return _ACTION_RISKS.get(action.strip().lower(), RiskLevel.BLOCKED)


def can_auto_execute(action: str) -> bool:
    return classify_action(action) is RiskLevel.SAFE


def requires_confirmation(action: str) -> bool:
    return classify_action(action) in {RiskLevel.CONTROLLED, RiskLevel.CRITICAL}
