"""Alice conversation agent skeleton."""

from __future__ import annotations

import asyncio
import logging
from typing import Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from .const import (
    STATUS_STT,
    STATUS_THINKING,
    STATUS_TTS,
    SUPPORTED_LANGUAGES,
)
from .conversation_phrases import (
    DISABLE_CONTAINMENT,
    ENABLE_CONTAINMENT,
    MOOD_QUERIES,
    extract_pin,
    extract_preferred_name,
    matches_phrase,
    message,
    normalize_language,
)
from .intent_handlers import (
    handle_acknowledge_alarm,
    handle_disable_containment,
    handle_enable_containment,
)
from .runtime import reset_runtime_status, set_runtime_status
from .user_memory import UserMemory

_LOGGER = logging.getLogger(__name__)
_TTS_IDLE_DELAY_SECONDS = 2.0


class AliceConversationEntity(conversation.ConversationEntity):
    """Expose Alice as a Home Assistant conversation agent."""

    _attr_has_entity_name = True
    _attr_name = "Alice"
    _attr_unique_id = "alice_conversation_agent"

    def __init__(
        self,
        entry: ConfigEntry,
        redqueen,
        user_memory: UserMemory,
        runtime: dict,
    ) -> None:
        self._entry = entry
        self._redqueen = redqueen
        self._user_memory = user_memory
        self._runtime = runtime
        self._attr_device_info = {
            "identifiers": {("alice", entry.entry_id)},
            "name": "Alice",
            "manufacturer": "Project Alice",
            "model": "Personality Platform",
        }

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        return SUPPORTED_LANGUAGES

    def _resolve_user_id(self, user_input: conversation.ConversationInput) -> str:
        return self._user_memory.resolve_user_id(
            getattr(user_input, "user_id", None),
            getattr(user_input, "device_id", None),
        )

    def _schedule_idle_after_tts(self) -> None:
        async def _runner() -> None:
            await asyncio.sleep(_TTS_IDLE_DELAY_SECONDS)
            if self._runtime.get("status") == STATUS_TTS:
                reset_runtime_status(self._runtime)

        self.hass.async_create_task(_runner())

    def _finish(
        self,
        response: intent.IntentResponse,
        conversation_id: str | None,
    ) -> conversation.ConversationResult:
        result = conversation.ConversationResult(
            response=response,
            conversation_id=conversation_id,
        )
        if response.speech:
            set_runtime_status(self._runtime, STATUS_TTS)
            self._schedule_idle_after_tts()
        else:
            reset_runtime_status(self._runtime)
        return result

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Handle Alice-specific commands and delegate the rest to Home Assistant."""
        set_runtime_status(self._runtime, STATUS_STT)
        set_runtime_status(self._runtime, STATUS_THINKING)
        try:
            language = normalize_language(
                user_input.language or self._entry.data.get("default_language", "de")
            )
            text = (user_input.text or "").strip().lower()
            response = intent.IntentResponse(language=language)
            user_id = self._resolve_user_id(user_input)

            if text in MOOD_QUERIES.get(language, set()):
                response.async_set_speech(
                    message("mood", language, mood=self._redqueen.mood)
                )
                return self._finish(response, user_input.conversation_id)

            preferred_name = extract_preferred_name(user_input.text or "", language)
            if preferred_name and self._user_memory.set_preferred_name(
                user_id, preferred_name
            ):
                persist = self._runtime.get("persist_user_memory")
                if persist is not None:
                    await persist()
                response.async_set_speech(
                    message("name_saved", language, name=preferred_name)
                )
                return self._finish(response, user_input.conversation_id)

            if matches_phrase(text, ENABLE_CONTAINMENT):
                if "alice_containment_alarm" in self.hass.config.components:
                    speech = await handle_enable_containment(self.hass)
                    response.async_set_speech(speech)
                else:
                    response.async_set_speech(message("containment_missing", language))
                return self._finish(response, user_input.conversation_id)

            if matches_phrase(text, DISABLE_CONTAINMENT):
                if "alice_containment_alarm" in self.hass.config.components:
                    speech = await handle_disable_containment(self.hass)
                    response.async_set_speech(speech)
                else:
                    response.async_set_speech(message("containment_missing", language))
                return self._finish(response, user_input.conversation_id)

            pin = extract_pin(user_input.text or "", language)
            if pin is not None:
                if "alice_containment_alarm" in self.hass.config.components:
                    speech = await handle_acknowledge_alarm(self.hass, pin)
                    response.async_set_speech(speech)
                else:
                    response.async_set_speech(message("containment_missing", language))
                return self._finish(response, user_input.conversation_id)

            profile = self._user_memory.get_profile(user_id)
            response.async_set_speech(
                message("unknown_command", language, name=profile.display_name())
            )
            return self._finish(response, user_input.conversation_id)
        except Exception:
            reset_runtime_status(self._runtime)
            raise


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the Alice conversation agent."""
    runtime = hass.data["alice"][entry.entry_id]
    async_add_entities(
        [
            AliceConversationEntity(
                entry,
                runtime["redqueen"],
                runtime["user_memory"],
                runtime,
            )
        ]
    )
