from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QWidget

from ..autostart import install_autostart, is_autostart_enabled, remove_autostart
from ..animation.animator import PetAnimator
from ..config import WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from ..minigames.reaction_game import ReactionGameDialog
from ..minigames.timing_game import TimingGameDialog
from ..pet.state_machine import PetEngine
from ..sound import SoundManager
from .dialogs import GamePickerDialog
from .shell_widget import ShellWidget


class MainWindow(QWidget):
    def __init__(
        self,
        engine: PetEngine,
        sound_manager: SoundManager,
        settings: dict[str, object],
        persist_callback: Callable[[], None],
    ) -> None:
        super().__init__()
        self.engine = engine
        self.sound_manager = sound_manager
        self.settings = settings
        self.persist_callback = persist_callback
        self.animator = PetAnimator()
        self.shell = ShellWidget(self.animator, self)

        self._apply_window_flags()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle(WINDOW_TITLE)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.engine.pet_changed.connect(self.shell.set_pet)
        self.engine.message_changed.connect(self.shell.screen.set_message)
        self.engine.request_sound.connect(self.sound_manager.play)
        self.engine.request_animation.connect(self.animator.trigger)
        self.shell.controls.action.connect(self._on_action)
        self.shell.screen.pet_clicked.connect(self.engine.pet_clicked)

        self.shell.set_pet(self.engine.pet)
        self.move(40, 40)

    def _apply_window_flags(self) -> None:
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if bool(self.settings.get("always_on_top", True)):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

    def _toggle_stats(self) -> None:
        self.shell.toggle_stats()

    def _on_action(self, action: str) -> None:
        if action == "play":
            self._open_game_picker()
            return
        if action == "menu":
            self.sound_manager.play("click")
            self._show_context_menu(self.mapToGlobal(self.rect().center()))
            return
        if action == "stats":
            self.sound_manager.play("click")
            self._toggle_stats()
            return
        self.engine.handle_action(action)

    def contextMenuEvent(self, event) -> None:  # noqa: D401, ANN001
        self._show_context_menu(event.globalPos())

    def _show_context_menu(self, global_pos: QPoint) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu {
                background: #f5ead7;
                border: 1px solid #8b2234;
                padding: 6px;
                border-radius: 12px;
            }
            QMenu::item {
                padding: 6px 18px;
                border-radius: 8px;
                color: #41272a;
            }
            QMenu::item:selected {
                background: #e6c59d;
            }
            """
        )
        pin_action = QAction("Always on top", self, checkable=True)
        pin_action.setChecked(bool(self.settings.get("always_on_top", True)))
        mute_action = QAction("Mute retro beeps", self, checkable=True)
        mute_action.setChecked(bool(self.settings.get("muted", False)))
        autostart_action = QAction("Install autostart", self)
        remove_autostart_action = QAction("Remove autostart", self)
        remove_autostart_action.setEnabled(is_autostart_enabled())
        reset_action = QAction("Reset pet", self)
        quit_action = QAction("Quit", self)

        pin_action.triggered.connect(lambda _checked=False: self.toggle_always_on_top())
        mute_action.triggered.connect(lambda _checked=False: self.toggle_muted())
        autostart_action.triggered.connect(lambda _checked=False: self._install_autostart())
        remove_autostart_action.triggered.connect(lambda _checked=False: self._remove_autostart())
        reset_action.triggered.connect(lambda _checked=False: self._reset_pet())
        quit_action.triggered.connect(lambda _checked=False: self._close_and_persist())

        for action in (pin_action, mute_action, autostart_action, remove_autostart_action, reset_action, quit_action):
            menu.addAction(action)
        menu.exec(global_pos)

    def toggle_always_on_top(self) -> None:
        self.settings["always_on_top"] = not bool(self.settings.get("always_on_top", True))
        position = self.pos()
        self._apply_window_flags()
        self.show()
        self.move(position)
        self.persist_callback()

    def toggle_muted(self) -> None:
        new_value = not bool(self.settings.get("muted", False))
        self.settings["muted"] = new_value
        self.sound_manager.set_muted(new_value)
        self.persist_callback()

    def _open_game_picker(self) -> None:
        picker = GamePickerDialog(self)
        if picker.exec() != picker.DialogCode.Accepted or picker.selection is None:
            return
        if picker.selection == "reaction":
            dialog = ReactionGameDialog(self)
            game_name = "Slash Reflex"
        else:
            dialog = TimingGameDialog(self)
            game_name = "Black Flash"
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.engine.apply_game_result(game_name, dialog.final_score)

    def _install_autostart(self) -> None:
        install_autostart()
        self.shell.screen.set_message("Autostart enabled.")
        self.persist_callback()

    def _remove_autostart(self) -> None:
        remove_autostart()
        self.shell.screen.set_message("Autostart removed.")
        self.persist_callback()

    def _reset_pet(self) -> None:
        self.engine.reset_pet()
        self.persist_callback()

    def _close_and_persist(self) -> None:
        self.persist_callback()
        self.close()

    def closeEvent(self, event) -> None:  # noqa: D401, ANN001
        self.persist_callback()
        super().closeEvent(event)
