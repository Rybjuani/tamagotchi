from __future__ import annotations

from dataclasses import dataclass

from ..config import STAGE_NAMES
from .model import PetData


@dataclass(frozen=True)
class StageProfile:
    key: str
    title: str
    head_scale: float
    body_scale: float
    hair_spikes: int
    aura_strength: float
    robe_trim: str
    smirk: float
    menace: float
    stray_hair: float


STAGE_PROFILES = {
    "seed": StageProfile("seed", STAGE_NAMES["seed"], 0.92, 0.76, 5, 0.00, "#734046", 0.10, 0.20, 0.20),
    "brat": StageProfile("brat", STAGE_NAMES["brat"], 0.96, 0.82, 6, 0.08, "#6f2025", 0.22, 0.38, 0.36),
    "vessel": StageProfile("vessel", STAGE_NAMES["vessel"], 1.00, 0.90, 7, 0.12, "#8a2634", 0.28, 0.48, 0.18),
    "prince": StageProfile("prince", STAGE_NAMES["prince"], 1.03, 0.95, 8, 0.22, "#972838", 0.32, 0.60, 0.22),
    "heir": StageProfile("heir", STAGE_NAMES["heir"], 1.02, 0.98, 8, 0.28, "#a5313d", 0.34, 0.70, 0.16),
    "fallen_king": StageProfile("fallen_king", STAGE_NAMES["fallen_king"], 1.04, 0.98, 8, 0.18, "#5e1d20", 0.10, 0.55, 0.42),
    "domain_lord": StageProfile("domain_lord", STAGE_NAMES["domain_lord"], 1.08, 1.06, 9, 0.42, "#b33144", 0.38, 0.84, 0.18),
    "malevolent_sovereign": StageProfile("malevolent_sovereign", STAGE_NAMES["malevolent_sovereign"], 1.10, 1.10, 10, 0.62, "#c11d34", 0.46, 1.00, 0.12),
}


def get_stage_profile(stage_key: str) -> StageProfile:
    return STAGE_PROFILES.get(stage_key, STAGE_PROFILES["vessel"])


def display_stage_name(stage_key: str) -> str:
    return get_stage_profile(stage_key).title


EVOLUTION_THRESHOLDS = (4.0, 14.0, 30.0)


def care_average(pet: PetData) -> float:
    if pet.care_score_samples <= 0:
        return (pet.hunger + pet.happiness + pet.health + pet.energy + pet.discipline) / 5.0
    return pet.care_score_total / pet.care_score_samples


def maybe_evolve(pet: PetData) -> str | None:
    if pet.evolution_level >= len(EVOLUTION_THRESHOLDS):
        return None
    if pet.pet_age_hours < EVOLUTION_THRESHOLDS[pet.evolution_level]:
        return None

    average = care_average(pet)
    mistakes = pet.care_mistakes + pet.sickness_events

    if pet.evolution_level == 0:
        next_stage = "brat" if average < 44 else "vessel"
    elif pet.evolution_level == 1:
        if average < 42 or mistakes >= 5:
            next_stage = "fallen_king"
        elif average < 80:
            next_stage = "prince"
        else:
            next_stage = "heir"
    else:
        if average < 46 or mistakes >= 9:
            next_stage = "fallen_king"
        elif average > 82 and pet.discipline >= 70 and pet.snack_overload < 7.0:
            next_stage = "malevolent_sovereign"
        else:
            next_stage = "domain_lord"

    pet.stage = next_stage
    pet.evolution_level += 1
    pet.pending_evolution = next_stage
    return next_stage
