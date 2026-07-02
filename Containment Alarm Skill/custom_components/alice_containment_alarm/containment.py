"""Containment Mode state machine for Alice."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.util import dt as dt_util

from .const import (
    DEFAULT_ALARM_CYCLE_PAUSE,
    DEFAULT_ALARM_MAX_DURATION,
    DEFAULT_PIN_ATTEMPTS,
    DEFAULT_PIN_TIMEOUT,
    SECURITY_GREEN,
    SECURITY_RED,
    SECURITY_YELLOW,
)

_LOGGER = logging.getLogger(__name__)


def hash_pin(pin: str, salt: str) -> str:
    """Hash a PIN using PBKDF2."""
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        pin.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    )
    return digest.hex()


def verify_pin(pin: str, salt: str, pin_hash: str) -> bool:
    """Verify a PIN against its stored hash."""
    return hash_pin(pin, salt) == pin_hash


@dataclass
class ContainmentRuntime:
    """Mutable runtime state for containment mode."""

    active: bool = False
    security_level: str = SECURITY_GREEN
    open_contacts: list[str] = field(default_factory=list)
    alarm_active: bool = False
    acoustic_alarm_active: bool = False
    pin_attempts_remaining: int = DEFAULT_PIN_ATTEMPTS
    pin_listening: bool = False
    last_acoustic_alarm_at: datetime | None = None
    acoustic_window_expired: bool = False
    alarm_cycle_count: int = 0
    _cancel_pin_timer: Any = None
    _cancel_alarm_timer: Any = None
    _cancel_acoustic_limit_timer: Any = None


class ContainmentController:
    """Coordinates containment activation, alarms, and PIN handling."""

    def __init__(
        self,
        hass: HomeAssistant,
        contact_sensor_ids: list[str],
        pin_hash: str | None,
        pin_salt: str | None,
        voice_pin_enabled: bool,
        alarm_cycle_pause: int = DEFAULT_ALARM_CYCLE_PAUSE,
        alarm_max_duration: int = DEFAULT_ALARM_MAX_DURATION,
    ) -> None:
        self.hass = hass
        self.contact_sensor_ids = contact_sensor_ids
        self.pin_hash = pin_hash
        self.pin_salt = pin_salt
        self.voice_pin_enabled = voice_pin_enabled
        self.alarm_cycle_pause = alarm_cycle_pause
        self.alarm_max_duration = alarm_max_duration
        self.runtime = ContainmentRuntime()
        self._listeners: list[Any] = []

    def add_listener(self, callback) -> None:
        """Register a state change listener."""
        self._listeners.append(callback)

    async def _notify(self) -> None:
        for callback in self._listeners:
            await callback()

    def get_open_contacts(self) -> list[str]:
        """Return friendly names of currently open contact sensors."""
        open_contacts: list[str] = []
        for entity_id in self.contact_sensor_ids:
            state = self.hass.states.get(entity_id)
            if state is None:
                continue
            if state.state in {"on", "open", "true"}:
                open_contacts.append(state.attributes.get("friendly_name", entity_id))
        return open_contacts

    async def enable(self) -> dict[str, Any]:
        """Activate containment mode and evaluate contact sensors."""
        self.runtime.active = True
        self.runtime.open_contacts = self.get_open_contacts()

        if self.runtime.open_contacts:
            self.runtime.security_level = SECURITY_YELLOW
            result = {
                "security_level": SECURITY_YELLOW,
                "warning_required": True,
                "open_contacts": self.runtime.open_contacts,
            }
        else:
            self.runtime.security_level = SECURITY_GREEN
            result = {
                "security_level": SECURITY_GREEN,
                "warning_required": False,
                "open_contacts": [],
            }

        await self._notify()
        return result

    async def disable(self) -> None:
        """Deactivate containment mode and reset alarm state."""
        self._clear_timers()
        self.runtime = ContainmentRuntime()
        await self._notify()

    async def handle_contact_opened(self, entity_id: str) -> dict[str, Any] | None:
        """Raise alarm when a monitored contact opens during active containment."""
        if not self.runtime.active:
            return None

        self.runtime.open_contacts = self.get_open_contacts()
        if entity_id not in self.contact_sensor_ids:
            return None

        self.runtime.security_level = SECURITY_RED
        self.runtime.alarm_active = True
        self.runtime.pin_attempts_remaining = DEFAULT_PIN_ATTEMPTS

        if not self.runtime.acoustic_window_expired:
            await self._start_acoustic_alarm_cycle()

        if self.voice_pin_enabled and self.pin_hash and self.pin_salt:
            await self._start_pin_window()

        await self._notify()
        return {
            "security_level": SECURITY_RED,
            "trigger": entity_id,
            "open_contacts": self.runtime.open_contacts,
            "voice_pin_required": self.voice_pin_enabled,
        }

    async def acknowledge_pin(self, pin: str) -> bool:
        """Validate a spoken or entered PIN."""
        if not self.pin_hash or not self.pin_salt:
            return False
        if not verify_pin(pin, self.pin_salt, self.pin_hash):
            self.runtime.pin_attempts_remaining -= 1
            await self._notify()
            return False

        await self._deactivate_alarm()
        return True

    async def acknowledge_trusted_event(self, source: str) -> None:
        """Deactivate alarm from NFC tag or smart lock event."""
        _LOGGER.info("Containment alarm acknowledged via trusted source: %s", source)
        await self._deactivate_alarm()

    async def _deactivate_alarm(self) -> None:
        self._clear_timers()
        self.runtime.alarm_active = False
        self.runtime.acoustic_alarm_active = False
        self.runtime.pin_listening = False
        self.runtime.security_level = (
            SECURITY_YELLOW if self.runtime.open_contacts else SECURITY_GREEN
        )
        await self._notify()

    async def _start_pin_window(self) -> None:
        self.runtime.pin_listening = True
        self._cancel_pin_timer = async_track_point_in_time(
            self.hass,
            self._handle_pin_timeout,
            dt_util.utcnow() + timedelta(seconds=DEFAULT_PIN_TIMEOUT),
        )

    async def _handle_pin_timeout(self, _now: datetime) -> None:
        if not self.runtime.pin_listening:
            return
        self.runtime.pin_attempts_remaining -= 1
        self.runtime.pin_listening = False
        await self._notify()
        if (
            self.runtime.pin_attempts_remaining > 0
            and self.runtime.alarm_active
            and self.voice_pin_enabled
        ):
            await self._start_pin_window()

    async def _start_acoustic_alarm_cycle(self) -> None:
        if self.runtime.acoustic_window_expired:
            return

        self.runtime.acoustic_alarm_active = True
        self.runtime.last_acoustic_alarm_at = dt_util.utcnow()
        self.runtime.alarm_cycle_count += 1

        if self.runtime._cancel_acoustic_limit_timer is None:
            self.runtime._cancel_acoustic_limit_timer = async_track_point_in_time(
                self.hass,
                self._handle_acoustic_limit,
                dt_util.utcnow() + timedelta(seconds=self.alarm_max_duration),
            )

        self._cancel_alarm_timer = async_track_point_in_time(
            self.hass,
            self._handle_alarm_pause,
            dt_util.utcnow() + timedelta(seconds=self.alarm_cycle_pause),
        )

    async def _handle_alarm_pause(self, _now: datetime) -> None:
        if not self.runtime.alarm_active or self.runtime.acoustic_window_expired:
            self.runtime.acoustic_alarm_active = False
            await self._notify()
            return

        self.runtime.acoustic_alarm_active = False
        await self._notify()

        if self.runtime.alarm_active and not self.runtime.acoustic_window_expired:
            self._cancel_alarm_timer = async_track_point_in_time(
                self.hass,
                self._resume_acoustic_alarm,
                dt_util.utcnow() + timedelta(seconds=self.alarm_cycle_pause),
            )

    async def _resume_acoustic_alarm(self, _now: datetime) -> None:
        if self.runtime.alarm_active and not self.runtime.acoustic_window_expired:
            await self._start_acoustic_alarm_cycle()

    async def _handle_acoustic_limit(self, _now: datetime) -> None:
        self.runtime.acoustic_window_expired = True
        self.runtime.acoustic_alarm_active = False
        await self._notify()

    def _clear_timers(self) -> None:
        for timer in (
            self.runtime._cancel_pin_timer,
            self.runtime._cancel_alarm_timer,
            self.runtime._cancel_acoustic_limit_timer,
        ):
            if timer:
                timer()
        self.runtime._cancel_pin_timer = None
        self.runtime._cancel_alarm_timer = None
        self.runtime._cancel_acoustic_limit_timer = None
