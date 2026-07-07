"""Tests for Alice RedQueen state."""

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
redqueen = _load_module("alice.redqueen", "redqueen.py")

RedQueenState = redqueen.RedQueenState
MOOD_AMOROUS = const.MOOD_AMOROUS
MOOD_FRIENDLY = const.MOOD_FRIENDLY


def test_set_mood_accepts_supported_values():
    state = RedQueenState()
    assert state.set_mood(MOOD_AMOROUS) is True
    assert state.mood == MOOD_AMOROUS


def test_set_mood_rejects_unknown_values():
    state = RedQueenState(mood=MOOD_FRIENDLY)
    assert state.set_mood("unknown") is False
    assert state.mood == MOOD_FRIENDLY


def test_adjust_relationship_clamps_score():
    state = RedQueenState()
    assert state.adjust_relationship("operator", 150) == 100
    assert state.adjust_relationship("operator", -300) == -100
