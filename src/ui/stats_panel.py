from __future__ import annotations

from ..pet.evolution import display_stage_name
from ..pet.model import PetData


def build_stat_rows(pet: PetData) -> list[tuple[str, float]]:
    return [
        ("HNG", pet.hunger),
        ("JOY", pet.happiness),
        ("HLT", pet.health),
        ("NRG", pet.energy),
        ("DSC", pet.discipline),
    ]


def build_meta_lines(pet: PetData) -> list[str]:
    return [
        display_stage_name(pet.stage),
        f"Age {pet.pet_age_hours / 24.0:.1f}d   Wt {pet.weight:.1f}kg",
        f"Mistakes {pet.care_mistakes}   Wins {pet.games_won}/{pet.games_played}",
    ]
