from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from ..config import DEFAULT_MESSAGE


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class PetData:
    name: str = "Sukuna"
    created_at: str = field(default_factory=utc_now_iso)
    last_updated: str = field(default_factory=utc_now_iso)
    pet_age_hours: float = 0.0
    hunger: float = 82.0
    happiness: float = 76.0
    health: float = 88.0
    energy: float = 86.0
    discipline: float = 54.0
    weight: float = 11.8
    poop_count: int = 0
    sick: bool = False
    sleeping: bool = False
    lights_off: bool = False
    attention: bool = False
    attention_reason: str | None = None
    misbehaving: bool = False
    stage: str = "seed"
    mood: str = "idle"
    care_mistakes: int = 0
    snack_overload: float = 0.0
    sleep_debt: float = 0.0
    illness_meter: float = 0.0
    digestion_hours: float = 0.0
    attention_timer: float = 0.0
    mischief_meter: float = 0.0
    care_score_total: float = 0.0
    care_score_samples: int = 0
    evolution_level: int = 0
    pending_evolution: str | None = None
    last_message: str = DEFAULT_MESSAGE
    sickness_events: int = 0
    games_played: int = 0
    games_won: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PetData":
        defaults = cls().to_dict()
        defaults.update(payload or {})
        return cls(**defaults)
