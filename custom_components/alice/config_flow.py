"""Config flow for Alice."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_AMBIENT_CHATTER,
    CONF_DEFAULT_LANGUAGE,
    CONF_DEFAULT_PERSONA,
    CONF_LLM_ENABLED,
    CONF_SARCASM_LEVEL,
    DEFAULT_LANGUAGE,
    DEFAULT_PERSONA,
    DEFAULT_SARCASM_LEVEL,
    DOMAIN,
    SUPPORTED_LANGUAGES,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_DEFAULT_LANGUAGE, default=DEFAULT_LANGUAGE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=SUPPORTED_LANGUAGES,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(CONF_DEFAULT_PERSONA, default=DEFAULT_PERSONA): cv.string,
        vol.Optional(CONF_SARCASM_LEVEL, default=DEFAULT_SARCASM_LEVEL): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=100)
        ),
        vol.Optional(CONF_LLM_ENABLED, default=False): cv.boolean,
        vol.Optional(CONF_AMBIENT_CHATTER, default=False): cv.boolean,
    }
)


class AliceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Alice."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Alice", data=user_input)

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)
