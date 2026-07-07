"""Sensor platform for Alice."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ALICE_STATUSES, STATUS_IDLE
from .runtime import add_runtime_listener


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alice sensors."""
    runtime = hass.data["alice"][entry.entry_id]
    async_add_entities(
        [
            AliceStatusSensor(entry, runtime),
            AliceMoodSensor(entry, runtime),
        ]
    )


class AliceBaseSensor(SensorEntity):
    """Shared Alice sensor behavior."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, runtime: dict) -> None:
        self._entry = entry
        self._runtime = runtime
        self._attr_device_info = {
            "identifiers": {("alice", entry.entry_id)},
            "name": "Alice",
            "manufacturer": "Project Alice",
            "model": "Personality Platform",
        }
        add_runtime_listener(runtime, self.async_write_ha_state)


class AliceStatusSensor(AliceBaseSensor):
    """Expose Alice processing status."""

    _attr_name = "Status"
    _attr_unique_id = "alice_status"
    _attr_icon = "mdi:robot"

    @property
    def native_value(self) -> str:
        return self._runtime.get("status", STATUS_IDLE)

    @property
    def extra_state_attributes(self) -> dict:
        return {"available_statuses": ALICE_STATUSES}


class AliceMoodSensor(AliceBaseSensor):
    """Expose current RedQueen mood."""

    _attr_name = "Mood"
    _attr_unique_id = "alice_mood"
    _attr_icon = "mdi:emoticon"

    @property
    def native_value(self) -> str:
        return self._runtime["redqueen"].mood
