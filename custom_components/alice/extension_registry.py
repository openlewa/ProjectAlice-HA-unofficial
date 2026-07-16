"""Alice extension registry."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .sentence_export import SentenceExportResult, export_custom_sentences

_LOGGER = logging.getLogger(__name__)


async def discover_alice_extensions(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Discover installed integrations that expose alice_extension.json."""
    extensions: list[dict[str, Any]] = []
    for domain in sorted(hass.config.components):
        try:
            integration = await async_get_integration(hass, domain)
        except Exception:  # noqa: BLE001
            continue

        manifest_path = Path(integration.file_path) / "alice_extension.json"
        if not manifest_path.exists():
            continue

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            _LOGGER.warning("Invalid alice_extension.json in %s", domain)
            continue

        manifest["integration_domain"] = domain
        extensions.append(manifest)

    return extensions


async def collect_sentence_sources(
    hass: HomeAssistant,
    language: str,
) -> list[tuple[str, Path]]:
    """Collect base and extension sentence file paths for a language."""
    sources: list[tuple[str, Path]] = []

    alice_integration = await async_get_integration(hass, "alice")
    base_sentence_path = Path(alice_integration.file_path) / "sentences" / f"{language}.yaml"
    sources.append(("alice", base_sentence_path))

    for extension in await discover_alice_extensions(hass):
        integration = await async_get_integration(hass, extension["integration_domain"])
        sentence_path = Path(integration.file_path) / "sentences" / f"{language}.yaml"
        sources.append((extension["integration_domain"], sentence_path))

    return sources


async def rebuild_custom_sentences(hass: HomeAssistant, language: str) -> SentenceExportResult:
    """Aggregate and export consolidated custom sentences for Speech-to-Phrase."""
    output_dir = Path(hass.config.config_dir) / "custom_sentences"
    source_paths = await collect_sentence_sources(hass, language)
    result = export_custom_sentences(output_dir, language, source_paths)

    if result.conflicts:
        for conflict in result.conflicts:
            _LOGGER.warning("Alice sentence conflict (%s): %s", conflict.kind, conflict.message)

    if result.output_path:
        _LOGGER.info(
            "Exported Alice custom sentences for %s to %s from %s sources",
            language,
            result.output_path,
            len(result.source_files),
        )
    else:
        _LOGGER.warning("No Alice sentence sources found for %s", language)

    return result
