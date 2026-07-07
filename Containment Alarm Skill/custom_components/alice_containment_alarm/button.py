"""Button platform for Alice Containment Alarm."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up containment buttons."""
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            EnableContainmentButton(controller, entry),
            DisableContainmentButton(controller, entry),
            TestAlarmOutputButton(controller, entry),
        ]
    )


class ContainmentButton(ButtonEntity):
    """Shared button behavior."""

    _attr_has_entity_name = True

    def __init__(self, controller, entry: ConfigEntry) -> None:
        self._controller = controller
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Project Alice",
            "model": "Containment Alarm",
        }


class EnableContainmentButton(ContainmentButton):
    """Enable containment mode."""

    _attr_name = "Enable Containment Mode"
    _attr_unique_id = f"{DOMAIN}_enable_containment"
    _attr_icon = "mdi:shield-check"

    async def async_press(self) -> None:
        await self._controller.enable()


class DisableContainmentButton(ContainmentButton):
    """Disable containment mode."""

    _attr_name = "Disable Containment Mode"
    _attr_unique_id = f"{DOMAIN}_disable_containment"
    _attr_icon = "mdi:shield-off"

    async def async_press(self) -> None:
        await self._controller.disable()


class TestAlarmOutputButton(ContainmentButton):
    """Trigger a short alarm output test."""

    _attr_name = "Test Alarm Output"
    _attr_unique_id = f"{DOMAIN}_test_alarm_output"
    _attr_icon = "mdi:alarm-light"

    async def async_press(self) -> None:
        self._controller.runtime.acoustic_alarm_active = True
        await self._controller._notify()
        self._controller.runtime.acoustic_alarm_active = False
        await self._controller._notify()
