"""Sensor platform for Alice Containment Alarm."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_ALARM_ACTIVE,
    ATTR_OPEN_CONTACTS,
    ATTR_PIN_ATTEMPTS_REMAINING,
    ATTR_SECURITY_LEVEL,
    DOMAIN,
)
from .containment import ContainmentController


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up containment sensors."""
    controller: ContainmentController = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            ContainmentSecurityLevelSensor(controller, entry),
            ContainmentOpenContactsSensor(controller, entry),
        ]
    )


class ContainmentBaseSensor(SensorEntity):
    """Shared containment sensor behavior."""

    _attr_has_entity_name = True

    def __init__(self, controller: ContainmentController, entry: ConfigEntry) -> None:
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
    def available(self) -> bool:
        return True


class ContainmentSecurityLevelSensor(ContainmentBaseSensor):
    """Expose the current security level."""

    _attr_name = "Security Level"
    _attr_unique_id = f"{DOMAIN}_security_level"
    _attr_icon = "mdi:shield-alert"

    @property
    def native_value(self) -> str:
        return self._controller.runtime.security_level

    @property
    def extra_state_attributes(self) -> dict:
        runtime = self._controller.runtime
        return {
            ATTR_ALARM_ACTIVE: runtime.alarm_active,
            ATTR_PIN_ATTEMPTS_REMAINING: runtime.pin_attempts_remaining,
        }


class ContainmentOpenContactsSensor(ContainmentBaseSensor):
    """Expose currently open monitored contacts."""

    _attr_name = "Open Contacts"
    _attr_unique_id = f"{DOMAIN}_open_contacts"
    _attr_icon = "mdi:door-open"

    @property
    def native_value(self) -> str:
        contacts = self._controller.runtime.open_contacts
        return str(len(contacts))

    @property
    def extra_state_attributes(self) -> dict:
        return {ATTR_OPEN_CONTACTS: self._controller.runtime.open_contacts}
