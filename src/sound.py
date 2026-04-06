from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QSoundEffect

from .config import AUDIO_DIR, DEFAULT_SETTINGS


class SoundManager(QObject):
    def __init__(self, muted: bool | None = None, volume: float | None = None) -> None:
        super().__init__()
        self._muted = DEFAULT_SETTINGS["muted"] if muted is None else muted
        self._volume = DEFAULT_SETTINGS["volume"] if volume is None else volume
        self._paths = {path.stem: path for path in AUDIO_DIR.glob("*.wav")}
        self._effects: dict[str, QSoundEffect] = {}

    def _effect_for(self, name: str) -> QSoundEffect | None:
        effect = self._effects.get(name)
        if effect is not None:
            return effect
        wav_path = self._paths.get(name)
        if wav_path is None:
            return None
        effect = QSoundEffect(self)
        effect.setSource(QUrl.fromLocalFile(str(wav_path)))
        effect.setLoopCount(1)
        effect.setVolume(self._volume)
        self._effects[name] = effect
        return effect

    def set_muted(self, muted: bool) -> None:
        self._muted = muted

    def set_volume(self, volume: float) -> None:
        self._volume = volume
        for effect in self._effects.values():
            effect.setVolume(volume)

    @property
    def muted(self) -> bool:
        return self._muted

    def play(self, name: str) -> None:
        if self._muted:
            return
        effect = self._effect_for(name)
        if effect is None:
            return
        effect.stop()
        effect.play()
