"""User Memory for Alice."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .const import (
    DEFAULT_HUMOR_LEVEL,
    DEFAULT_USER_ROLE,
    ROLE_ADMINISTRATOR,
    ROLE_COMMANDER,
    ROLE_KIDS,
    ROLE_OPERATOR,
    ROLES,
)

GUEST_USER_ID = "guest"


@dataclass
class UserProfile:
    """Per-user preferences and permissions."""

    preferred_name: str | None = None
    title: str | None = None
    role: str = DEFAULT_USER_ROLE
    preferred_voice: str | None = None
    persona_style: str | None = None
    humor_level: int = DEFAULT_HUMOR_LEVEL
    relationship: int = 0

    def display_name(self) -> str:
        """Return the best available name for greetings."""
        return self.preferred_name or self.title or "Operator"


class UserMemory:
    """Stores and resolves Alice user profiles."""

    def __init__(self, profiles: dict[str, UserProfile] | None = None) -> None:
        self._profiles = profiles or {}

    def resolve_user_id(
        self,
        user_id: str | None = None,
        device_id: str | None = None,
        fallback_user_id: str | None = None,
    ) -> str:
        """Resolve a stable user key from Assist context.

        Priority:
        1. Home Assistant ``user_id`` from Assist when the speaker is logged in
        2. Explicit ``fallback_user_id`` from services or future config mapping
        3. ``device:{device_id}`` when only the Assist device/satellite is known
        4. ``guest`` when no identity is available
        """
        if user_id:
            return user_id
        if fallback_user_id:
            return fallback_user_id
        if device_id:
            return f"device:{device_id}"
        return GUEST_USER_ID

    def get_profile(self, user_id: str) -> UserProfile:
        """Return an existing profile or a default profile."""
        return self._profiles.setdefault(user_id, UserProfile())

    def set_preferred_name(self, user_id: str, preferred_name: str) -> bool:
        name = preferred_name.strip()
        if not name:
            return False
        profile = self.get_profile(user_id)
        profile.preferred_name = name[:64]
        return True

    def set_title(self, user_id: str, title: str) -> bool:
        cleaned = title.strip()
        if not cleaned or len(cleaned) > 64:
            return False
        profile = self.get_profile(user_id)
        profile.title = cleaned
        return True

    def set_role(self, user_id: str, role: str) -> bool:
        normalized = role.strip().lower()
        if normalized not in ROLES:
            return False
        profile = self.get_profile(user_id)
        profile.role = normalized
        return True

    def set_preferred_voice(self, user_id: str, voice: str) -> bool:
        cleaned = voice.strip()
        if not cleaned:
            return False
        profile = self.get_profile(user_id)
        profile.preferred_voice = cleaned[:64]
        return True

    def set_persona_style(self, user_id: str, persona_style: str) -> bool:
        cleaned = persona_style.strip()
        if not cleaned:
            return False
        profile = self.get_profile(user_id)
        profile.persona_style = cleaned[:64]
        return True

    def set_humor_level(self, user_id: str, humor_level: int) -> bool:
        if humor_level < 0 or humor_level > 100:
            return False
        profile = self.get_profile(user_id)
        profile.humor_level = humor_level
        return True

    def adjust_relationship(self, user_id: str, delta: int) -> int:
        profile = self.get_profile(user_id)
        profile.relationship = max(-100, min(100, profile.relationship + delta))
        return profile.relationship

    def can_configure_security(self, user_id: str) -> bool:
        """Return whether the user may configure security routines."""
        return self.get_profile(user_id).role in {ROLE_ADMINISTRATOR, ROLE_COMMANDER}

    def can_create_global_automations(self, user_id: str) -> bool:
        """Return whether the user may create global automations."""
        return self.get_profile(user_id).role in {ROLE_ADMINISTRATOR, ROLE_COMMANDER}

    def is_kids_role(self, user_id: str) -> bool:
        return self.get_profile(user_id).role == ROLE_KIDS

    def to_dict(self) -> dict[str, Any]:
        return {
            user_id: asdict(profile) for user_id, profile in self._profiles.items()
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> UserMemory:
        profiles: dict[str, UserProfile] = {}
        for user_id, payload in (data or {}).items():
            if isinstance(payload, dict):
                profiles[user_id] = UserProfile(**payload)
        return cls(profiles)
