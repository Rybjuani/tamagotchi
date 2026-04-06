from __future__ import annotations

import math
import wave
from pathlib import Path

from .config import AUDIO_DIR


SOUND_PATTERNS = {
    "click": [(980, 0.045, 0.42), (1320, 0.035, 0.25)],
    "alert": [(1200, 0.05, 0.38), (860, 0.05, 0.32), (1200, 0.05, 0.38)],
    "eat": [(640, 0.04, 0.35), (760, 0.04, 0.32), (540, 0.05, 0.22)],
    "clean": [(1480, 0.03, 0.28), (1740, 0.04, 0.24), (2080, 0.05, 0.20)],
    "sleep": [(740, 0.06, 0.28), (560, 0.07, 0.24), (420, 0.08, 0.2)],
    "wake": [(420, 0.05, 0.22), (620, 0.05, 0.24), (880, 0.06, 0.28)],
    "game": [(780, 0.04, 0.3), (980, 0.04, 0.3), (1320, 0.06, 0.34)],
    "sick": [(300, 0.08, 0.3), (240, 0.08, 0.32), (200, 0.1, 0.28)],
    "evolve": [(560, 0.05, 0.26), (720, 0.05, 0.28), (980, 0.06, 0.3), (1320, 0.09, 0.36)],
}


def _emit_square(frequency: float, duration: float, volume: float, sample_rate: int = 22050) -> bytes:
    count = int(duration * sample_rate)
    frames = bytearray()
    attack = max(1, int(count * 0.04))
    release = max(1, int(count * 0.09))
    for index in range(count):
        phase = math.sin((index / sample_rate) * frequency * math.tau)
        sample = 1.0 if phase >= 0 else -1.0
        env = 1.0
        if index < attack:
            env = index / attack
        elif index > count - release:
            env = max(0.0, (count - index) / release)
        value = int(sample * volume * env * 32767)
        frames.extend(value.to_bytes(2, byteorder="little", signed=True))
    return bytes(frames)


def _write_pattern(path: Path, pattern: list[tuple[float, float, float]]) -> None:
    silence = b"\x00\x00" * 350
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(22050)
        for frequency, duration, volume in pattern:
            handle.writeframes(_emit_square(frequency, duration, volume))
            handle.writeframes(silence)


def ensure_audio_assets() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for name, pattern in SOUND_PATTERNS.items():
        path = AUDIO_DIR / f"{name}.wav"
        if not path.exists():
            _write_pattern(path, pattern)
