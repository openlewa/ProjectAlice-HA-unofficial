"""Alice conversation agent skeleton."""

from __future__ import annotations

import logging
from typing import Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from .const import STATUS_IDLE, STATUS_THINKING
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
        return ["de", "en"]

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Handle Alice-specific commands and delegate the rest to Home Assistant."""
        language = user_input.language or self._entry.data.get("default_language", "de")
        text = (user_input.text or "").strip().lower()
        response = intent.IntentResponse(language=language)

        if text in {"wie ist deine laune", "what is your mood"}:
            response.async_set_speech(
                f"Meine Laune ist {self._redqueen.mood}."
                if language == "de"
                else f"My mood is {self._redqueen.mood}."
            )
            return conversation.ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )

        if text in {
            "aktiviere sperrmodus",
            "aktiviere containment modus",
            "sperrmodus an",
            "enable containment mode",
            "activate containment mode",
            "turn on containment mode",
        }:
            if "alice_containment_alarm" in self.hass.config.components:
                message = await handle_enable_containment(self.hass)
                response.async_set_speech(message)
            else:
                response.async_set_speech(
                    "Containment Alarm ist nicht installiert."
                    if language == "de"
                    else "Containment Alarm is not installed."
                )
            return conversation.ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )

        if text in {
            "deaktiviere sperrmodus",
            "sperrmodus aus",
            "beende sperrmodus",
            "disable containment mode",
            "turn off containment mode",
            "deactivate containment mode",
        }:
            if "alice_containment_alarm" in self.hass.config.components:
                message = await handle_disable_containment(self.hass)
                response.async_set_speech(message)
            else:
                response.async_set_speech(
                    "Containment Alarm ist nicht installiert."
                    if language == "de"
                    else "Containment Alarm is not installed."
                )
            return conversation.ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )

        if text.startswith("bestätige alarm mit pin ") or text.startswith(
            "confirm alarm with pin "
        ):
            pin = text.rsplit(" ", 1)[-1]
            if "alice_containment_alarm" in self.hass.config.components:
                message = await handle_acknowledge_alarm(self.hass, pin)
                response.async_set_speech(message)
            else:
                response.async_set_speech(
                    "Containment Alarm ist nicht installiert."
                    if language == "de"
                    else "Containment Alarm is not installed."
                )
            return conversation.ConversationResult(
                response=response, conversation_id=user_input.conversation_id
            )

        response.async_set_speech(
            "Ich habe den Befehl noch nicht gelernt, Operator."
            if language == "de"
            else "I have not learned that command yet, Operator."
        )
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
