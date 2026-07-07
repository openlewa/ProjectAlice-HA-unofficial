"""Config flow for Alice Containment Alarm."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_ALARM_MEDIA_PLAYERS,
    CONF_ALARM_VOLUME,
    CONF_CONTACT_SENSORS,
    CONF_EXTERNAL_SIRENS,
    CONF_NFC_TAGS,
    CONF_SMART_LOCKS,
    CONF_VOICE_PIN_ENABLED,
    CONF_WARNING_MEDIA_PLAYERS,
    CONF_WARNING_VOLUME,
    DEFAULT_ALARM_VOLUME,
    DEFAULT_WARNING_VOLUME,
    DOMAIN,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="Containment Alarm"): cv.string,
        vol.Required(CONF_CONTACT_SENSORS): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["binary_sensor", "sensor"])
        ),
        vol.Optional(CONF_WARNING_MEDIA_PLAYERS, default=[]): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["media_player"])
        ),
        vol.Optional(CONF_ALARM_MEDIA_PLAYERS, default=[]): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["media_player"])
        ),
        vol.Optional(CONF_EXTERNAL_SIRENS, default=[]): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=["switch", "siren", "script", "alarm_control_panel"]
            )
        ),
        vol.Optional(CONF_WARNING_VOLUME, default=DEFAULT_WARNING_VOLUME): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional(CONF_ALARM_VOLUME, default=DEFAULT_ALARM_VOLUME): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional(CONF_VOICE_PIN_ENABLED, default=True): cv.boolean,
        vol.Optional(CONF_NFC_TAGS, default=[]): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["tag"])
        ),
        vol.Optional(CONF_SMART_LOCKS, default=[]): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["lock"])
        ),
    }
)


class AliceContainmentAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Alice Containment Alarm."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)
