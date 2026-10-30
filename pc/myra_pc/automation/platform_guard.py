from __future__ import annotations

import platform


class UnsupportedPlatformError(RuntimeError):
    pass


def require_windows() -> None:
    """Fail closed rather than pretending Windows controls work on another OS."""
    if platform.system() != "Windows":
        raise UnsupportedPlatformError(
            "Windows desktop automation is available only when Myra runs on Windows 10/11."
        )
