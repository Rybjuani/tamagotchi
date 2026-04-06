from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass

from PySide6.QtCore import QObject, QTimer, Signal

from ..config import ANIMATION_MS


@dataclass(frozen=True)
class AnimationFrame:
    time_value: float
    breath: float
    blink: float
    sway: float
    bounce: float
    aura: float
    emotion: str
    emotion_strength: float


class PetAnimator(QObject):
    frame_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._start = time.monotonic()
        self._emotion = "idle"
        self._emotion_until = 0.0
        self._emotion_strength = 0.0
        self._blink_start = random.uniform(2.0, 3.6)
        self._blink_length = 0.22
        self._next_blink = random.uniform(3.4, 5.2)
        self._timer = QTimer(self)
        self._timer.setInterval(ANIMATION_MS)
        self._timer.timeout.connect(self.frame_changed.emit)
        self._timer.start()

    def trigger(self, emotion: str, duration_ms: int = 1200) -> None:
        self._emotion = emotion
        self._emotion_until = time.monotonic() + (duration_ms / 1000.0)
        self._emotion_strength = 1.0
        self.frame_changed.emit()

    def snapshot(self) -> AnimationFrame:
        now = time.monotonic()
        elapsed = now - self._start
        blink_progress = 0.0
        cycle_pos = (elapsed - self._blink_start) % self._next_blink
        if 0.0 <= cycle_pos <= self._blink_length:
            mid = self._blink_length / 2
            distance = abs(cycle_pos - mid) / mid
            blink_progress = 1.0 - min(1.0, distance)

        if now > self._emotion_until:
            self._emotion = "idle"
            self._emotion_strength = max(0.0, self._emotion_strength - 0.08)
        else:
            remaining = max(0.0, self._emotion_until - now)
            self._emotion_strength = min(1.0, 0.25 + remaining)

        breath = math.sin(elapsed * 2.0) * 0.55
        sway = math.sin(elapsed * 1.35 + 0.8) * 0.55
        bounce = 0.0
        if self._emotion in {"pet", "joy", "eat", "celebrate"}:
            bounce = max(0.0, math.sin(elapsed * 8.2)) * 1.05
            sway *= 1.2
        elif self._emotion in {"angry", "evolve"}:
            bounce = math.sin(elapsed * 12.0) * 0.36
            sway *= 0.7
        elif self._emotion in {"sleep"}:
            breath *= 0.45
            sway *= 0.18
        elif self._emotion in {"sick"}:
            breath *= 0.18
            sway = math.sin(elapsed * 5.0) * 0.22
        elif self._emotion in {"bored"}:
            breath *= 0.55
            sway *= 0.22
        elif self._emotion in {"relief"}:
            sway *= 0.28
        aura = math.sin(elapsed * 3.6) * 0.5 + 0.5
        return AnimationFrame(
            time_value=elapsed,
            breath=breath,
            blink=blink_progress,
            sway=sway,
            bounce=bounce,
            aura=aura,
            emotion=self._emotion,
            emotion_strength=self._emotion_strength,
        )
