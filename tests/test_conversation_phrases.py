"""Tests for localized Alice conversation phrases."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ALICE = Path(__file__).resolve().parents[1] / "custom_components" / "alice"


def _load_module(name: str, filename: str):
    path = ALICE / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


const = _load_module("alice.const", "const.py")
phrases = _load_module("alice.conversation_phrases", "conversation_phrases.py")


def test_supported_languages_include_all_requested_locales():
    assert const.SUPPORTED_LANGUAGES == [
        "de",
        "en",
        "fr",
        "it",
        "es",
        "zh",
        "ja",
        "ko",
        "pt",
    ]


def test_enable_containment_matches_french_phrase():
    assert phrases.matches_phrase(
        "active le protocole de confinement",
        phrases.ENABLE_CONTAINMENT,
    )


def test_enable_containment_matches_german_re_term():
    assert phrases.matches_phrase(
        "aktiviere abriegelungsprotokoll",
        phrases.ENABLE_CONTAINMENT,
    )


def test_extract_pin_from_japanese_phrase():
    assert phrases.extract_pin("pin 1234 でアラームを確認", "ja") == "1234"


def test_extract_preferred_name_from_german_phrase():
    assert phrases.extract_preferred_name("nenn mich Alex", "de") == "Alex"


def test_extract_preferred_name_from_english_phrase():
    assert phrases.extract_preferred_name("call me Operator", "en") == "Operator"
