"""RedQueen mood and persona state model."""

from __future__ import annotations

from dataclasses import dataclass, field

from .const import MOOD_FRIENDLY, MOODS


@dataclass
class RedQueenState:
    """Runtime RedQueen personality state."""

    mood: str = MOOD_FRIENDLY
    sarcasm_level: int = 50
    persona_style: str = "redqueen"
    relationships: dict[str, int] = field(default_factory=dict)
    user_titles: dict[str, str] = field(default_factory=dict)

    def set_mood(self, mood: str) -> bool:
        if mood not in MOODS:
            return False
        self.mood = mood
        return True

    def adjust_relationship(self, user_id: str, delta: int) -> int:
        score = self.relationships.get(user_id, 0) + delta
        self.relationships[user_id] = max(-100, min(100, score))
        return self.relationships[user_id]
