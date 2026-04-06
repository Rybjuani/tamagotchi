from __future__ import annotations

import random
import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QWidget

from ..ui.dialogs import DIALOG_STYLE


class ReactionGameDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Slash Reflex")
        self.setModal(True)
        self.setFixedSize(250, 240)
        self.setStyleSheet(DIALOG_STYLE)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)

        self.rounds = 3
        self.round_index = 0
        self.score_total = 0
        self.final_score = 0
        self._ready_at = 0.0
        self._armed = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.title = QLabel("Slash Reflex")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 16px; font-weight: 700;")
        self.status = QLabel("Tap Start, then hit the red seal as soon as it appears.")
        self.status.setWordWrap(True)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.target = QPushButton("WAIT")
        self.target.setEnabled(False)
        self.target.setFixedHeight(88)
        self.target.setStyleSheet(
            "QPushButton { background: #9ba88a; border-radius: 18px; font-size: 18px; }"
            "QPushButton:disabled { color: #f0f0e8; }"
        )

        self.action = QPushButton("Start")
        self.action.clicked.connect(self._action_clicked)
        self.target.clicked.connect(self._target_clicked)

        layout.addWidget(self.title)
        layout.addWidget(self.status)
        layout.addWidget(self.target)
        layout.addWidget(self.action)

    def _action_clicked(self) -> None:
        if self.round_index >= self.rounds:
            self.accept()
            return
        self._start_round()

    def _start_round(self) -> None:
        self._armed = False
        self.target.setEnabled(False)
        self.target.setText("WAIT")
        self.target.setStyleSheet(
            "QPushButton { background: #9ba88a; border-radius: 18px; font-size: 18px; }"
            "QPushButton:disabled { color: #f0f0e8; }"
        )
        self.status.setText(f"Round {self.round_index + 1}/{self.rounds}. Wait for the seal.")
        self.action.setEnabled(False)
        QTimer.singleShot(random.randint(700, 1800), self._arm_target)

    def _arm_target(self) -> None:
        self._armed = True
        self._ready_at = time.monotonic()
        self.target.setEnabled(True)
        self.target.setText("SLASH")
        self.target.setStyleSheet("QPushButton { background: #d85d66; border-radius: 18px; font-size: 18px; }")
        self.status.setText("Now.")

    def _target_clicked(self) -> None:
        if not self._armed:
            return
        elapsed_ms = (time.monotonic() - self._ready_at) * 1000.0
        round_score = max(20, int(100 - elapsed_ms / 7.0))
        self.score_total += round_score
        self.round_index += 1
        self._armed = False
        self.target.setEnabled(False)
        self.target.setText(f"{int(elapsed_ms)} ms")
        self.target.setStyleSheet(
            "QPushButton { background: #f0d4b7; color: #402c2b; border-radius: 18px; font-size: 18px; }"
        )
        if self.round_index >= self.rounds:
            self.final_score = int(self.score_total / self.rounds)
            self.status.setText(f"Average {self.final_score}. Sukuna approves.")
            self.action.setText("Close")
        else:
            self.status.setText(f"Round score {round_score}. Again.")
            self.action.setText("Next")
        self.action.setEnabled(True)
