"""Tests for Alice user memory."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALICE = ROOT / "custom_components" / "alice"


def _load_module(name: str, filename: str):
    path = ALICE / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


const = _load_module("alice.const", "const.py")
user_memory = _load_module("alice.user_memory", "user_memory.py")
runtime = _load_module("alice.runtime", "runtime.py")

UserMemory = user_memory.UserMemory
set_runtime_status = runtime.set_runtime_status
ROLE_KIDS = const.ROLE_KIDS
ROLE_OPERATOR = const.ROLE_OPERATOR
ROLE_COMMANDER = const.ROLE_COMMANDER


def test_resolve_user_id_prefers_home_assistant_user():
    memory = UserMemory()
    assert memory.resolve_user_id("ha-user", "media_player.kitchen") == "ha-user"


def test_resolve_user_id_falls_back_to_device_identity():
    memory = UserMemory()
    assert memory.resolve_user_id(None, "media_player.kitchen") == "device:media_player.kitchen"


def test_resolve_user_id_falls_back_to_guest():
    memory = UserMemory()
    assert memory.resolve_user_id(None, None) == "guest"


def test_set_role_and_title_persist_in_profile():
    memory = UserMemory()
    assert memory.set_role("operator-1", ROLE_COMMANDER) is True
    assert memory.set_title("operator-1", "Facility Manager") is True
    profile = memory.get_profile("operator-1")
    assert profile.role == ROLE_COMMANDER
    assert profile.title == "Facility Manager"


def test_kids_role_blocks_security_configuration():
    memory = UserMemory()
    memory.set_role("child-1", ROLE_KIDS)
    assert memory.is_kids_role("child-1") is True
    assert memory.can_configure_security("child-1") is False


def test_operator_role_allows_default_permissions():
    memory = UserMemory()
    profile = memory.get_profile("operator-1")
    assert profile.role == ROLE_OPERATOR
    assert memory.can_create_global_automations("operator-1") is False
    assert memory.can_configure_security("operator-1") is False


def test_user_memory_roundtrip_dict():
    memory = UserMemory()
    memory.set_preferred_name("operator-1", "Alex")
    memory.adjust_relationship("operator-1", 15)
    restored = UserMemory.from_dict(memory.to_dict())
    profile = restored.get_profile("operator-1")
    assert profile.preferred_name == "Alex"
    assert profile.relationship == 15


def test_runtime_status_notifies_listeners():
    calls: list[str] = []
    runtime_state = {"status": "Idle", "listeners": [lambda: calls.append(runtime_state["status"])]}
    set_runtime_status(runtime_state, "Thinking")
    assert calls == ["Thinking"]


def test_alice_status_includes_voice_pipeline_states():
    assert const.STATUS_STT == "STT"
    assert const.STATUS_TTS == "TTS"
    assert const.ALICE_STATUSES == ["Idle", "STT", "Thinking", "TTS"]
