"""Alice intent handlers for containment extension commands."""

from __future__ import annotations

from homeassistant.core import HomeAssistant


async def handle_enable_containment(hass: HomeAssistant) -> str:
    """Enable containment mode through the extension service."""
    await hass.services.async_call(
        "alice_containment_alarm",
        "enable_containment_mode",
        blocking=True,
    )
    return "Containment mode enabled."


async def handle_disable_containment(hass: HomeAssistant) -> str:
    """Disable containment mode through the extension service."""
    await hass.services.async_call(
        "alice_containment_alarm",
        "disable_containment_mode",
        blocking=True,
    )
    return "Containment mode disabled."


async def handle_acknowledge_alarm(hass: HomeAssistant, pin: str) -> str:
    """Acknowledge an active alarm with PIN."""
    await hass.services.async_call(
        "alice_containment_alarm",
        "acknowledge_alarm",
        {"pin": pin},
        blocking=True,
    )
    return "Alarm acknowledgement requested."
