from __future__ import annotations

from dataclasses import dataclass

from ..config import REAL_SECONDS_PER_PET_HOUR
from .evolution import display_stage_name, maybe_evolve
from .model import PetData


@dataclass
class UpdateReport:
    changed: bool = False
    message: str | None = None
    sound: str | None = None
    animation: str | None = None
    evolved_to: str | None = None
    alert_started: bool = False


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _sleep_window(pet: PetData) -> bool:
    clock_hour = pet.pet_age_hours % 24.0
    return clock_hour >= 21.0 or clock_hour < 7.0


def _attention_reason(pet: PetData) -> str | None:
    if pet.sick:
        return "sick"
    if pet.poop_count > 0:
        return "dirty"
    if pet.hunger < 34:
        return "hunger"
    if pet.happiness < 28:
        return "fun"
    if _sleep_window(pet) and not pet.sleeping and pet.energy < 44:
        return "sleep"
    return None


def _set_attention(pet: PetData, reason: str) -> bool:
    already = pet.attention and pet.attention_reason == reason
    pet.attention = True
    pet.attention_reason = reason
    if not already:
        pet.attention_timer = 0.0
    return not already


def _clear_attention(pet: PetData) -> None:
    pet.attention = False
    pet.attention_reason = None
    pet.attention_timer = 0.0
    pet.misbehaving = False


def _resolve_attention_if_needed(pet: PetData) -> None:
    if pet.misbehaving:
        return
    reason = _attention_reason(pet)
    if reason is None:
        _clear_attention(pet)
    else:
        _set_attention(pet, reason)


def _refresh_passive_mood(pet: PetData) -> None:
    if pet.pending_evolution:
        pet.mood = "celebrate"
    elif pet.sick:
        pet.mood = "sick"
    elif pet.sleeping:
        pet.mood = "sleep"
    elif pet.attention and pet.misbehaving:
        pet.mood = "angry"
    elif pet.poop_count > 0:
        pet.mood = "dirty"
    elif pet.happiness < 28:
        pet.mood = "bored"
    elif pet.energy < 24:
        pet.mood = "sleepy"
    else:
        pet.mood = "idle"


def _care_snapshot(pet: PetData) -> float:
    base = (pet.hunger + pet.happiness + pet.health + pet.energy + pet.discipline) / 5.0
    penalties = pet.poop_count * 8.0
    penalties += 14.0 if pet.sick else 0.0
    penalties += pet.sleep_debt * 1.4
    penalties += pet.snack_overload * 0.8
    penalties += pet.care_mistakes * 0.12
    return _clamp(base - penalties)


def apply_time_passage(pet: PetData, real_seconds: float) -> UpdateReport:
    report = UpdateReport(changed=real_seconds > 0.0)
    pet_hours = min(72.0, max(0.0, real_seconds / REAL_SECONDS_PER_PET_HOUR))
    while pet_hours > 0.0:
        chunk = min(0.5, pet_hours)
        pet_hours -= chunk

        pet.pet_age_hours += chunk

        if pet.lights_off:
            pet.sleeping = True
        elif not pet.lights_off:
            pet.sleeping = False

        if pet.sleeping:
            pet.energy = _clamp(pet.energy + 10.0 * chunk)
            pet.hunger = _clamp(pet.hunger - 3.4 * chunk)
            pet.happiness = _clamp(pet.happiness + 0.4 * chunk)
            pet.sleep_debt = max(0.0, pet.sleep_debt - 1.1 * chunk)
            pet.digestion_hours += 0.42 * chunk
        else:
            pet.energy = _clamp(pet.energy - 4.6 * chunk)
            pet.hunger = _clamp(pet.hunger - 5.1 * chunk)
            pet.happiness = _clamp(pet.happiness - 2.4 * chunk)
            pet.digestion_hours += 0.88 * chunk
            if _sleep_window(pet):
                pet.sleep_debt += 1.4 * chunk
                pet.health = _clamp(pet.health - 1.0 * chunk)

        if pet.digestion_hours >= 3.2:
            fresh = int(pet.digestion_hours // 3.2)
            pet.poop_count += fresh
            pet.digestion_hours -= fresh * 3.2
            if pet.poop_count > 0 and _set_attention(pet, "dirty"):
                report.alert_started = True
                report.message = report.message or "Clean this shrine."
                report.sound = report.sound or "alert"

        if pet.poop_count > 0:
            pet.happiness = _clamp(pet.happiness - 0.8 * chunk)
        if pet.poop_count >= 2:
            pet.health = _clamp(pet.health - 1.2 * chunk)

        if pet.hunger < 25:
            pet.health = _clamp(pet.health - 1.2 * chunk)
        if pet.energy < 18 and not pet.sleeping:
            pet.health = _clamp(pet.health - 1.0 * chunk)
        if pet.happiness < 22:
            pet.health = _clamp(pet.health - 0.7 * chunk)

        risk = 0.0
        risk += pet.poop_count * 0.35
        risk += max(0.0, 28.0 - pet.hunger) / 22.0
        risk += max(0.0, 24.0 - pet.energy) / 20.0
        risk += max(0.0, pet.sleep_debt - 2.0) * 0.16
        risk += pet.snack_overload * 0.05
        if risk > 0.0:
            pet.illness_meter += chunk * risk
        else:
            pet.illness_meter = max(0.0, pet.illness_meter - chunk * 0.5)

        if not pet.sick and pet.illness_meter >= 5.6:
            pet.sick = True
            pet.sickness_events += 1
            if _set_attention(pet, "sick"):
                report.alert_started = True
            report.message = "Cursed fever."
            report.sound = "sick"
            report.animation = "sick"

        if pet.sick:
            pet.health = _clamp(pet.health - 1.6 * chunk)
            pet.happiness = _clamp(pet.happiness - 0.8 * chunk)

        pet.snack_overload = max(0.0, pet.snack_overload - 0.12 * chunk)

        reason = _attention_reason(pet)
        if reason is not None and not pet.misbehaving:
            if _set_attention(pet, reason):
                report.alert_started = True
                if report.message is None:
                    report.message = {
                        "hunger": "Hungry.",
                        "fun": "Bored already.",
                        "dirty": "Clean this shrine.",
                        "sick": "Cursed fever.",
                        "sleep": "Too tired to reign.",
                    }[reason]
                report.sound = report.sound or "alert"
        elif reason is None and not pet.misbehaving:
            _clear_attention(pet)

        if not pet.attention and not pet.sleeping and reason is None:
            pet.mischief_meter += chunk * max(0.4, (90.0 - pet.discipline) / 36.0)
            if pet.mischief_meter >= 6.0:
                pet.mischief_meter = 0.0
                pet.misbehaving = True
                if _set_attention(pet, "mischief"):
                    report.alert_started = True
                    report.message = "He wants attention."
                    report.sound = report.sound or "alert"
        else:
            pet.mischief_meter = max(0.0, pet.mischief_meter - chunk * 0.5)

        if pet.attention:
            pet.attention_timer += chunk
            if pet.misbehaving and pet.attention_timer >= 2.5:
                pet.discipline = _clamp(pet.discipline - 5.0)
                pet.happiness = _clamp(pet.happiness - 4.0)
                _clear_attention(pet)
                report.message = report.message or "Ignored his tantrum."
            elif not pet.misbehaving and pet.attention_timer >= 2.5:
                pet.care_mistakes += 1
                pet.health = _clamp(pet.health - 3.6)
                pet.happiness = _clamp(pet.happiness - 2.8)
                pet.attention_timer = 0.0

        if pet.poop_count == 0 and not pet.sick and pet.hunger > 54 and pet.happiness > 46 and pet.energy > 44:
            pet.health = _clamp(pet.health + 0.45 * chunk)

        pet.care_score_total += _care_snapshot(pet)
        pet.care_score_samples += 1

        evolved_to = maybe_evolve(pet)
        if evolved_to:
            report.evolved_to = evolved_to
            report.message = f"Evolved into {display_stage_name(evolved_to)}."
            report.sound = "evolve"
            report.animation = "evolve"

    _refresh_passive_mood(pet)
    return report


def perform_action(pet: PetData, action: str) -> UpdateReport:
    report = UpdateReport(changed=True)

    if action == "meal":
        pet.sleeping = False
        pet.lights_off = False
        pet.hunger = _clamp(pet.hunger + 26.0)
        pet.happiness = _clamp(pet.happiness + 4.0)
        pet.health = _clamp(pet.health + 2.0)
        pet.weight += 0.45
        pet.digestion_hours += 1.3
        pet.snack_overload = max(0.0, pet.snack_overload - 0.6)
        report.message = "Meat accepted."
        report.sound = "eat"
        report.animation = "eat"
    elif action == "snack":
        pet.sleeping = False
        pet.lights_off = False
        pet.happiness = _clamp(pet.happiness + 16.0)
        pet.hunger = _clamp(pet.hunger + 5.0)
        pet.weight += 0.22
        pet.snack_overload += 1.3
        if pet.snack_overload > 4.0:
            pet.health = _clamp(pet.health - 2.2)
            pet.illness_meter += 0.8
        report.message = "A sweet tribute."
        report.sound = "eat"
        report.animation = "joy"
    elif action == "clean":
        if pet.poop_count == 0:
            report.message = "Already spotless."
            report.sound = "click"
            report.animation = "relief"
        else:
            pet.poop_count = 0
            pet.health = _clamp(pet.health + 6.0)
            pet.happiness = _clamp(pet.happiness + 8.0)
            report.message = "Filth erased."
            report.sound = "clean"
            report.animation = "relief"
    elif action == "med":
        if pet.sick:
            pet.sick = False
            pet.illness_meter = max(0.0, pet.illness_meter - 4.8)
            pet.health = _clamp(pet.health + 14.0)
            report.message = "The curse settles."
            report.sound = "clean"
            report.animation = "relief"
        else:
            pet.happiness = _clamp(pet.happiness - 1.5)
            report.message = "No medicine needed."
            report.sound = "click"
            report.animation = "angry"
    elif action == "sleep":
        pet.lights_off = not pet.lights_off
        pet.sleeping = pet.lights_off
        if pet.sleeping:
            report.message = "Lights out."
            report.sound = "sleep"
            report.animation = "sleep"
        else:
            report.message = "Rise."
            report.sound = "wake"
            report.animation = "wake"
    elif action == "discipline":
        if pet.misbehaving or pet.attention_reason == "mischief":
            pet.discipline = _clamp(pet.discipline + 10.0)
            pet.happiness = _clamp(pet.happiness - 4.0)
            report.message = "He accepts the correction."
        elif pet.attention:
            pet.discipline = _clamp(pet.discipline - 3.0)
            pet.happiness = _clamp(pet.happiness - 5.0)
            report.message = "That was not the issue."
        else:
            pet.discipline = _clamp(pet.discipline - 1.0)
            pet.happiness = _clamp(pet.happiness - 1.0)
            report.message = "No lesson was needed."
        report.sound = "alert"
        report.animation = "angry"
        _clear_attention(pet)

    _resolve_attention_if_needed(pet)
    _refresh_passive_mood(pet)
    return report


def pet_click_response(pet: PetData) -> UpdateReport:
    report = UpdateReport(changed=True, sound="click")
    if pet.sleeping:
        report.message = "Let him sleep."
        report.animation = "sleep"
    elif pet.sick:
        pet.happiness = _clamp(pet.happiness + 2.0)
        report.message = "He leans into the touch."
        report.animation = "relief"
    elif pet.attention and pet.misbehaving:
        report.message = "Smug, isn't he."
        report.animation = "angry"
    else:
        pet.happiness = _clamp(pet.happiness + 4.0)
        report.message = "He allows it."
        report.animation = "pet"
    _resolve_attention_if_needed(pet)
    _refresh_passive_mood(pet)
    return report


def reward_game_result(pet: PetData, game_name: str, score: int) -> UpdateReport:
    reward = max(4, min(22, round(6 + score * 0.16)))
    pet.games_played += 1
    if score >= 70:
        pet.games_won += 1
    pet.happiness = _clamp(pet.happiness + reward)
    pet.energy = _clamp(pet.energy - 5.0)
    pet.weight = max(3.5, pet.weight - 0.18)
    if pet.attention_reason == "fun":
        _clear_attention(pet)
    _refresh_passive_mood(pet)
    return UpdateReport(
        changed=True,
        message=f"{game_name}: +{reward} joy.",
        sound="game",
        animation="celebrate" if score >= 80 else "joy",
    )
