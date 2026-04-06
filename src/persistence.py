from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any

from .config import DEFAULT_SETTINGS, SAVE_DIR, SAVE_FILE
from .pet.model import PetData


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    return value


def load_state() -> dict[str, Any]:
    if not SAVE_FILE.exists():
        return {
            "settings": DEFAULT_SETTINGS.copy(),
            "pet": PetData().to_dict(),
        }
    try:
        payload = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "settings": DEFAULT_SETTINGS.copy(),
            "pet": PetData().to_dict(),
        }

    settings = DEFAULT_SETTINGS.copy()
    settings.update(payload.get("settings", {}))
    pet_payload = payload.get("pet", {})
    return {"settings": settings, "pet": pet_payload}


def save_state(pet: PetData, settings: dict[str, Any]) -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "settings": settings,
        "pet": _to_jsonable(pet),
    }
    SAVE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
