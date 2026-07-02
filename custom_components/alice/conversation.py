"""Alice conversation agent skeleton."""

from __future__ import annotations

import logging
from typing import Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from .const import SUPPORTED_LANGUAGES
from .conversation_phrases import (
    DISABLE_CONTAINMENT,
    ENABLE_CONTAINMENT,
    MOOD_QUERIES,
    extract_pin,
    matches_phrase,
    message,
    normalize_language,
)
from .intent_handlers import (
    handle_acknowledge_alarm,
    handle_disable_containment,
    handle_enable_containment,
)

_LOGGER = logging.getLogger(__name__)


class AliceConversationEntity(conversation.ConversationEntity):
    """Expose Alice as a Home Assistant conversation agent."""

    _attr_has_entity_name = True
    _attr_name = "Alice"
    _attr_unique_id = "alice_conversation_agent"

    def __init__(self, entry: ConfigEntry, redqueen) -> None:
        self._entry = entry
        self._redqueen = redqueen
        self._attr_device_info = {
            "identifiers": {("alice", entry.entry_id)},
            "name": "Alice",
            "manufacturer": "Project Alice",
            "model": "Personality Platform",
        }

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        return SUPPORTED_LANGUAGES

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Handle Alice-specific commands and delegate the rest to Home Assistant."""
        language = normalize_language(
            user_input.language or self._entry.data.get("default_language", "de")
        )
        text = (user_input.text or "").strip().lower()
        response = intent.IntentResponse(language=language)

        if text in MOOD_QUERIES.get(language, set()):
            response.async_set_speech(
                message("mood", language, mood=self._redqueen.mood)
            )
            return conversation.ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )

        if matches_phrase(text, ENABLE_CONTAINMENT):
            if "alice_containment_alarm" in self.hass.config.components:
                speech = await handle_enable_containment(self.hass)
                response.async_set_speech(speech)
            else:
                response.async_set_speech(message("containment_missing", language))
            return conversation.ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )

        if matches_phrase(text, DISABLE_CONTAINMENT):
            if "alice_containment_alarm" in self.hass.config.components:
                speech = await handle_disable_containment(self.hass)
                response.async_set_speech(speech)
            else:
                response.async_set_speech(message("containment_missing", language))
            return conversation.ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )

        pin = extract_pin(user_input.text or "", language)
        if pin is not None:
            if "alice_containment_alarm" in self.hass.config.components:
                speech = await handle_acknowledge_alarm(self.hass, pin)
                response.async_set_speech(speech)
            else:
                response.async_set_speech(message("containment_missing", language))
            return conversation.ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )

        response.async_set_speech(message("unknown_command", language))
        return conversation.ConversationResult(
            response=response, conversation_id=user_input.conversation_id
        )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the Alice conversation agent."""
    redqueen = hass.data["alice"][entry.entry_id]["redqueen"]
    async_add_entities([AliceConversationEntity(entry, redqueen)])
