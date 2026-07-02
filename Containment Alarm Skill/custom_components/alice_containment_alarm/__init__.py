"""The Alice Containment Alarm integration."""

from __future__ import annotations

import logging
import secrets
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_ALARM_MEDIA_PLAYERS,
    CONF_ALARM_VOLUME,
    CONF_CONTACT_SENSORS,
    CONF_EXTERNAL_SIRENS,
    CONF_NFC_TAGS,
    CONF_PIN_HASH,
    CONF_SMART_LOCKS,
    CONF_VOICE_PIN_ENABLED,
    CONF_WARNING_MEDIA_PLAYERS,
    CONF_WARNING_VOLUME,
    DEFAULT_ALARM_VOLUME,
    DEFAULT_WARNING_VOLUME,
    DOMAIN,
    SERVICE_ACKNOWLEDGE_ALARM,
    SERVICE_DISABLE,
    SERVICE_ENABLE,
    SERVICE_SET_PIN,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .containment import ContainmentController, hash_pin

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["binary_sensor", "sensor", "button"]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Alice Containment Alarm from YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Alice Containment Alarm from a config entry."""
    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    stored = await store.async_load() or {}
    pin_hash = stored.get(CONF_PIN_HASH)
    pin_salt = stored.get("pin_salt")

    controller = ContainmentController(
        hass=hass,
        contact_sensor_ids=entry.data.get(CONF_CONTACT_SENSORS, []),
        pin_hash=pin_hash,
        pin_salt=pin_salt,
        voice_pin_enabled=entry.data.get(CONF_VOICE_PIN_ENABLED, True),
    )
    controller.runtime_data = {
        "warning_media_players": entry.data.get(CONF_WARNING_MEDIA_PLAYERS, []),
        "alarm_media_players": entry.data.get(CONF_ALARM_MEDIA_PLAYERS, []),
        "external_sirens": entry.data.get(CONF_EXTERNAL_SIRENS, []),
        "warning_volume": entry.data.get(CONF_WARNING_VOLUME, DEFAULT_WARNING_VOLUME),
        "alarm_volume": entry.data.get(CONF_ALARM_VOLUME, DEFAULT_ALARM_VOLUME),
        "nfc_tags": entry.data.get(CONF_NFC_TAGS, []),
        "smart_locks": entry.data.get(CONF_SMART_LOCKS, []),
        "store": store,
    }

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = controller

    async def _handle_contact_change(event: Event) -> None:
        entity_id = event.data.get("entity_id")
        if isinstance(entity_id, str):
            await controller.handle_contact_opened(entity_id)

    unsubscribe_contacts = async_track_state_change_event(
        hass,
        entry.data.get(CONF_CONTACT_SENSORS, []),
        _handle_contact_change,
    )

    async def _handle_trusted_change(event: Event) -> None:
        entity_id = event.data.get("entity_id")
        if not isinstance(entity_id, str):
            return
        if entity_id in entry.data.get(CONF_NFC_TAGS, []):
            await controller.acknowledge_trusted_event(f"nfc:{entity_id}")
        if entity_id in entry.data.get(CONF_SMART_LOCKS, []):
            state = hass.states.get(entity_id)
            if state and state.state == "unlocked":
                await controller.acknowledge_trusted_event(f"lock:{entity_id}")

    trusted_entities = entry.data.get(CONF_NFC_TAGS, []) + entry.data.get(
        CONF_SMART_LOCKS, []
    )
    unsubscribe_trusted = async_track_state_change_event(
        hass, trusted_entities, _handle_trusted_change
    )

    async def async_enable(_call) -> None:
        await controller.enable()

    async def async_disable(_call) -> None:
        await controller.disable()

    async def async_acknowledge_alarm(call) -> None:
        pin = call.data.get("pin")
        if pin:
            await controller.acknowledge_pin(str(pin))

    async def async_set_pin(call) -> None:
        pin = str(call.data.get("pin", ""))
        if len(pin) < 4:
            _LOGGER.warning("PIN must be at least 4 characters")
            return
        salt = secrets.token_hex(16)
        stored[CONF_PIN_HASH] = hash_pin(pin, salt)
        stored["pin_salt"] = salt
        await store.async_save(stored)
        controller.pin_hash = stored[CONF_PIN_HASH]
        controller.pin_salt = salt

    hass.services.async_register(DOMAIN, SERVICE_ENABLE, async_enable)
    hass.services.async_register(DOMAIN, SERVICE_DISABLE, async_disable)
    hass.services.async_register(
        DOMAIN, SERVICE_ACKNOWLEDGE_ALARM, async_acknowledge_alarm
    )
    hass.services.async_register(DOMAIN, SERVICE_SET_PIN, async_set_pin)

    entry.async_on_unload(unsubscribe_contacts)
    entry.async_on_unload(unsubscribe_trusted)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)
    if unload_ok:
        controller: ContainmentController = hass.data[DOMAIN].pop(entry.entry_id)
        controller._clear_timers()
    return unload_ok
