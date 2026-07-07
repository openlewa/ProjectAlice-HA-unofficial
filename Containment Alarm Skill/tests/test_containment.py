"""Unit tests for containment state machine."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
import types
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "alice_containment_alarm"


def _install_homeassistant_stubs() -> None:
    homeassistant = types.ModuleType("homeassistant")
    core = types.ModuleType("homeassistant.core")
    helpers_event = types.ModuleType("homeassistant.helpers.event")
    util_dt = types.ModuleType("homeassistant.util.dt")

    class HomeAssistant:
        pass

    def async_track_point_in_time(hass, callback, point_in_time):
        return lambda: None

    def utcnow():
        return datetime.utcnow()

    core.HomeAssistant = HomeAssistant
    helpers_event.async_track_point_in_time = async_track_point_in_time
    util_dt.utcnow = utcnow

    sys.modules["homeassistant"] = homeassistant
    sys.modules["homeassistant.core"] = core
    sys.modules["homeassistant.helpers"] = types.ModuleType("homeassistant.helpers")
    sys.modules["homeassistant.helpers.event"] = helpers_event
    sys.modules["homeassistant.util"] = types.ModuleType("homeassistant.util")
    sys.modules["homeassistant.util.dt"] = util_dt


def _load_module(name: str, filename: str):
    path = COMPONENT / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_install_homeassistant_stubs()
const = _load_module("alice_containment_alarm.const", "const.py")
containment = _load_module("alice_containment_alarm.containment", "containment.py")

ContainmentController = containment.ContainmentController
hash_pin = containment.hash_pin
verify_pin = containment.verify_pin
SECURITY_GREEN = const.SECURITY_GREEN
SECURITY_RED = const.SECURITY_RED
SECURITY_YELLOW = const.SECURITY_YELLOW


class _FakeStates:
    def __init__(self, states: dict[str, str]):
        self._states = states

    class _State:
        def __init__(self, state: str, friendly_name: str):
            self.state = state
            self.attributes = {"friendly_name": friendly_name}

    def get(self, entity_id: str):
        value = self._states.get(entity_id)
        if value is None:
            return None
        return self._State(value, entity_id)


class _FakeHass:
    def __init__(self, states: dict[str, str]):
        self.states = _FakeStates(states)


class _ImmediateController(ContainmentController):
    async def _notify(self) -> None:
        return None


def test_enable_with_closed_contacts_sets_green():
    async def run():
        hass = _FakeHass({"binary_sensor.front_door": "off"})
        controller = _ImmediateController(
            hass=hass,
            contact_sensor_ids=["binary_sensor.front_door"],
            pin_hash=None,
            pin_salt=None,
            voice_pin_enabled=True,
        )

        result = await controller.enable()

        assert result["security_level"] == SECURITY_GREEN
        assert controller.runtime.active is True

    asyncio.run(run())


def test_enable_with_open_contacts_sets_yellow():
    async def run():
        hass = _FakeHass({"binary_sensor.kitchen_window": "on"})
        controller = _ImmediateController(
            hass=hass,
            contact_sensor_ids=["binary_sensor.kitchen_window"],
            pin_hash=None,
            pin_salt=None,
            voice_pin_enabled=True,
        )

        result = await controller.enable()

        assert result["security_level"] == SECURITY_YELLOW
        assert result["open_contacts"] == ["binary_sensor.kitchen_window"]

    asyncio.run(run())


def test_contact_open_while_active_triggers_red_alarm():
    async def run():
        hass = _FakeHass({"binary_sensor.terrace_door": "off"})
        controller = _ImmediateController(
            hass=hass,
            contact_sensor_ids=["binary_sensor.terrace_door"],
            pin_hash="abc",
            pin_salt="salt",
            voice_pin_enabled=True,
        )
        await controller.enable()

        result = await controller.handle_contact_opened("binary_sensor.terrace_door")

        assert result is not None
        assert result["security_level"] == SECURITY_RED
        assert controller.runtime.alarm_active is True

    asyncio.run(run())


def test_pin_hash_roundtrip():
    pin_hash = hash_pin("1234", "testsalt")
    assert verify_pin("1234", "testsalt", pin_hash) is True
    assert verify_pin("0000", "testsalt", pin_hash) is False


def test_correct_pin_deactivates_alarm():
    async def run():
        salt = "testsalt"
        pin_hash = hash_pin("1234", salt)
        hass = _FakeHass({"binary_sensor.terrace_door": "on"})
        controller = _ImmediateController(
            hass=hass,
            contact_sensor_ids=["binary_sensor.terrace_door"],
            pin_hash=pin_hash,
            pin_salt=salt,
            voice_pin_enabled=True,
        )
        await controller.enable()
        await controller.handle_contact_opened("binary_sensor.terrace_door")

        assert await controller.acknowledge_pin("1234") is True
        assert controller.runtime.alarm_active is False
        assert controller.runtime.security_level == SECURITY_YELLOW

    asyncio.run(run())
