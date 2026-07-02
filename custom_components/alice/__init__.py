"""The Alice integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_SARCASM_LEVEL,
    DOMAIN,
    SERVICE_REBUILD_SENTENCES,
    SERVICE_RELOAD_PACKS,
    SERVICE_SET_MOOD,
    STATUS_IDLE,
)
from .extension_registry import discover_alice_extensions, rebuild_custom_sentences
from .redqueen import RedQueenState

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["conversation", "sensor"]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Alice from YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Alice from a config entry."""
    redqueen = RedQueenState(
        sarcasm_level=entry.data.get(CONF_SARCASM_LEVEL, 50),
        persona_style=entry.data.get("default_persona", "redqueen"),
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "redqueen": redqueen,
        "status": STATUS_IDLE,
        "extensions": [],
    }

    async def async_set_mood(call) -> None:
        mood = call.data.get("mood")
        if mood and redqueen.set_mood(mood):
            _LOGGER.info("Alice mood set to %s", mood)

    async def async_rebuild_sentences(call) -> None:
        language = call.data.get("language", entry.data.get("default_language", "de"))
        files = await rebuild_custom_sentences(hass, language)
        _LOGGER.info("Collected %s sentence files for %s", len(files), language)

    async def async_reload_packs(_call) -> None:
        extensions = await discover_alice_extensions(hass)
        hass.data[DOMAIN][entry.entry_id]["extensions"] = extensions
        _LOGGER.info("Reloaded %s Alice extensions", len(extensions))

    hass.services.async_register(DOMAIN, SERVICE_SET_MOOD, async_set_mood)
    hass.services.async_register(DOMAIN, SERVICE_REBUILD_SENTENCES, async_rebuild_sentences)
    hass.services.async_register(DOMAIN, SERVICE_RELOAD_PACKS, async_reload_packs)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
