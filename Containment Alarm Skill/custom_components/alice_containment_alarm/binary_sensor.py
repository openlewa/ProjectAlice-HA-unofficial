"""Binary sensor platform for Alice Containment Alarm."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up containment binary sensors."""
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ContainmentModeBinarySensor(controller, entry)])


class ContainmentModeBinarySensor(BinarySensorEntity):
    """Expose whether containment mode is active."""

    _attr_has_entity_name = True
    _attr_name = "Containment Mode"
    _attr_unique_id = f"{DOMAIN}_containment_mode"
    _attr_icon = "mdi:shield-lock"

    def __init__(self, controller, entry: ConfigEntry) -> None:
        self._controller = controller
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Project Alice",
            "model": "Containment Alarm",
        }
        controller.add_listener(self.async_write_ha_state)

    @property
    def is_on(self) -> bool:
        return self._controller.runtime.active
