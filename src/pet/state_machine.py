from __future__ import annotations

from dataclasses import replace

from PySide6.QtCore import QObject, QTimer, Signal

from ..config import DEFAULT_MESSAGE, TICK_MS
from .model import PetData
from .rules import UpdateReport, apply_time_passage, perform_action, pet_click_response, reward_game_result
from .timers import RealtimeClock, seconds_since_iso, utc_now_iso


class PetEngine(QObject):
    pet_changed = Signal(object)
    message_changed = Signal(str)
    request_sound = Signal(str)
    request_animation = Signal(str)
    persist_requested = Signal()

    def __init__(self, pet: PetData) -> None:
        super().__init__()
        self.pet = pet
        self._clock = RealtimeClock()
        self._save_accumulator = 0.0
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(TICK_MS)
        self._tick_timer.timeout.connect(self._tick)

        offline_seconds = seconds_since_iso(self.pet.last_updated)
        if offline_seconds > 1.0:
            self._apply_report(apply_time_passage(self.pet, offline_seconds), play_sound=False)
        self.pet.last_updated = utc_now_iso()
        self._clock.reset()
        self._tick_timer.start()

    def emit_state(self) -> None:
        self.pet_changed.emit(replace(self.pet))
        self.message_changed.emit(self.pet.last_message)

    def _apply_report(self, report: UpdateReport, *, play_sound: bool = True, request_persist: bool = False) -> None:
        if report.message:
            self.pet.last_message = report.message
            self.message_changed.emit(report.message)
        if play_sound and report.sound:
            self.request_sound.emit(report.sound)
        if report.animation:
            self.request_animation.emit(report.animation)
        self.pet.pending_evolution = None
        self.pet.last_updated = utc_now_iso()
        self.pet_changed.emit(replace(self.pet))
        if request_persist:
            self.persist_requested.emit()

    def _tick(self) -> None:
        delta = self._clock.consume()
        if delta <= 0.0:
            return
        report = apply_time_passage(self.pet, delta)
        self._save_accumulator += delta
        self._apply_report(report, request_persist=self._save_accumulator >= 10.0)
        if self._save_accumulator >= 10.0:
            self._save_accumulator = 0.0

    def handle_action(self, action: str) -> None:
        if action == "stats":
            self.request_sound.emit("click")
            return
        report = perform_action(self.pet, action)
        self._save_accumulator = 0.0
        self._apply_report(report, request_persist=True)

    def pet_clicked(self) -> None:
        report = pet_click_response(self.pet)
        self._save_accumulator = 0.0
        self._apply_report(report, request_persist=True)

    def apply_game_result(self, game_name: str, score: int) -> None:
        report = reward_game_result(self.pet, game_name, score)
        self._save_accumulator = 0.0
        self._apply_report(report, request_persist=True)

    def reset_pet(self) -> None:
        self.pet = PetData()
        self.pet.last_message = DEFAULT_MESSAGE
        self.pet.last_updated = utc_now_iso()
        self._save_accumulator = 0.0
        self.emit_state()
        self.persist_requested.emit()
