from __future__ import annotations

from PySide6.QtWidgets import QApplication

from .assets import ensure_audio_assets
from .persistence import load_state, save_state
from .pet.model import PetData
from .pet.state_machine import PetEngine
from .sound import SoundManager
from .ui.main_window import MainWindow


class SukunatchiApplication:
    def __init__(self, qt_app: QApplication) -> None:
        ensure_audio_assets()
        self.qt_app = qt_app
        self.qt_app.setApplicationName("Sukunatchi")
        payload = load_state()
        self.settings = payload["settings"]
        self.pet = PetData.from_dict(payload["pet"])
        self.engine = PetEngine(self.pet)
        self.sound_manager = SoundManager(
            muted=bool(self.settings.get("muted", False)),
            volume=float(self.settings.get("volume", 0.62)),
        )
        self.window = MainWindow(self.engine, self.sound_manager, self.settings, self.persist)
        self.engine.persist_requested.connect(self.persist)
        self.engine.emit_state()

    def persist(self) -> None:
        save_state(self.engine.pet, self.settings)

    def run(self) -> int:
        self.window.show()
        return self.qt_app.exec()
