"""Alice extension registry."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

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


async def rebuild_custom_sentences(hass: HomeAssistant, language: str) -> list[str]:
    """Collect sentence file paths from discovered Alice extensions."""
    sentence_files: list[str] = []
    for extension in await discover_alice_extensions(hass):
        integration = await async_get_integration(hass, extension["integration_domain"])
        sentence_path = Path(integration.file_path) / "sentences" / f"{language}.yaml"
        if sentence_path.exists():
            sentence_files.append(str(sentence_path))
    return sentence_files
