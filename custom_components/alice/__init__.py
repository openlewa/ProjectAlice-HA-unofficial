"""The Alice integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_DEFAULT_LANGUAGE,
    CONF_SARCASM_LEVEL,
    DOMAIN,
    SERVICE_REBUILD_SENTENCES,
    SERVICE_RELOAD_PACKS,
    SERVICE_SET_MOOD,
    SERVICE_SET_USER_NAME,
    SERVICE_SET_USER_ROLE,
    SERVICE_SET_USER_TITLE,
    STATUS_IDLE,
    STORAGE_KEY,
    STORAGE_USERS_KEY,
    STORAGE_VERSION,
    SUPPORTED_LANGUAGES,
)
from .extension_registry import discover_alice_extensions, rebuild_custom_sentences
from .redqueen import RedQueenState
from .user_memory import UserMemory

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["conversation", "sensor"]


async def _save_user_memory(store: Store, user_memory: UserMemory) -> None:
    stored = await store.async_load() or {}
    stored[STORAGE_USERS_KEY] = user_memory.to_dict()
    await store.async_save(stored)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Alice from YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Alice from a config entry."""
    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    stored = await store.async_load() or {}
    user_memory = UserMemory.from_dict(stored.get(STORAGE_USERS_KEY))

    redqueen = RedQueenState(
        sarcasm_level=entry.data.get(CONF_SARCASM_LEVEL, 50),
        persona_style=entry.data.get("default_persona", "redqueen"),
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "redqueen": redqueen,
        "user_memory": user_memory,
        "status": STATUS_IDLE,
        "extensions": [],
        "listeners": [],
        "store": store,
        "persist_user_memory": lambda: _save_user_memory(store, user_memory),
    }

    async def async_set_mood(call) -> None:
        mood = call.data.get("mood")
        if mood and redqueen.set_mood(mood):
            _LOGGER.info("Alice mood set to %s", mood)

    async def async_set_user_role(call) -> None:
        user_id = user_memory.resolve_user_id(
            call.data.get("user_id"),
            call.data.get("device_id"),
        )
        role = call.data.get("role")
        if role and user_memory.set_role(user_id, role):
            await _save_user_memory(store, user_memory)
            _LOGGER.info("Alice role for %s set to %s", user_id, role)

    async def async_set_user_title(call) -> None:
        user_id = user_memory.resolve_user_id(
            call.data.get("user_id"),
            call.data.get("device_id"),
        )
        title = call.data.get("title")
        if title and user_memory.set_title(user_id, title):
            await _save_user_memory(store, user_memory)
            _LOGGER.info("Alice title for %s set to %s", user_id, title)

    async def async_set_user_name(call) -> None:
        user_id = user_memory.resolve_user_id(
            call.data.get("user_id"),
            call.data.get("device_id"),
        )
        name = call.data.get("name")
        if name and user_memory.set_preferred_name(user_id, name):
            await _save_user_memory(store, user_memory)
            _LOGGER.info("Alice preferred name for %s updated", user_id)

    async def async_rebuild_sentences(call) -> None:
        language = call.data.get("language")
        languages = [language] if language else list(SUPPORTED_LANGUAGES)
        for lang in languages:
            result = await rebuild_custom_sentences(hass, lang)
            _LOGGER.info(
                "Exported %s sentence sources for %s (%s conflicts)",
                len(result.source_files),
                lang,
                len(result.conflicts),
            )

    async def async_reload_packs(_call) -> None:
        extensions = await discover_alice_extensions(hass)
        hass.data[DOMAIN][entry.entry_id]["extensions"] = extensions
        _LOGGER.info("Reloaded %s Alice extensions", len(extensions))
        default_language = entry.data.get(CONF_DEFAULT_LANGUAGE, "de")
        await rebuild_custom_sentences(hass, default_language)

    hass.services.async_register(DOMAIN, SERVICE_SET_MOOD, async_set_mood)
    hass.services.async_register(DOMAIN, SERVICE_SET_USER_ROLE, async_set_user_role)
    hass.services.async_register(DOMAIN, SERVICE_SET_USER_TITLE, async_set_user_title)
    hass.services.async_register(DOMAIN, SERVICE_SET_USER_NAME, async_set_user_name)
    hass.services.async_register(DOMAIN, SERVICE_REBUILD_SENTENCES, async_rebuild_sentences)
    hass.services.async_register(DOMAIN, SERVICE_RELOAD_PACKS, async_reload_packs)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    default_language = entry.data.get(CONF_DEFAULT_LANGUAGE, "de")
    await rebuild_custom_sentences(hass, default_language)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
