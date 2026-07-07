"""Runtime helpers for Alice."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .const import STATUS_IDLE


def set_runtime_status(runtime: dict[str, Any], status: str) -> None:
    """Update Alice status and notify listeners."""
    runtime["status"] = status
    for listener in runtime.get("listeners", []):
        listener()


def add_runtime_listener(runtime: dict[str, Any], listener: Callable[[], None]) -> None:
    """Register a callback for runtime state changes."""
    runtime.setdefault("listeners", []).append(listener)


def reset_runtime_status(runtime: dict[str, Any]) -> None:
    """Return Alice to idle state."""
    set_runtime_status(runtime, STATUS_IDLE)
