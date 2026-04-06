from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QDialog, QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget

from ..ui.dialogs import DIALOG_STYLE


class TimingGameDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Black Flash")
        self.setModal(True)
        self.setFixedSize(252, 220)
        self.setStyleSheet(
            DIALOG_STYLE
            + """
            QProgressBar {
                border: 1px solid #8b2234;
                border-radius: 10px;
                background: #f8efe2;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #d85d66;
                border-radius: 10px;
            }
            """
        )
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)

        self.rounds = 3
        self.round_index = 0
        self.score_total = 0
        self.final_score = 0
        self.position = 0
        self.direction = 1
        self.running = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Black Flash")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: 700;")
        self.status = QLabel("Stop the meter as close to 50 as possible.")
        self.status.setWordWrap(True)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)

        self.action = QPushButton("Start")
        self.action.clicked.connect(self._action_clicked)

        layout.addWidget(title)
        layout.addWidget(self.status)
        layout.addWidget(self.bar)
        layout.addWidget(self.action)

        self._timer = QTimer(self)
        self._timer.setInterval(24)
        self._timer.timeout.connect(self._advance)

    def _action_clicked(self) -> None:
        if self.round_index >= self.rounds:
            self.accept()
            return
        if not self.running:
            self._start_round()
        else:
            self._stop_round()

    def _start_round(self) -> None:
        self.running = True
        self.position = 0
        self.direction = 1
        self.bar.setValue(self.position)
        self.status.setText(f"Round {self.round_index + 1}/{self.rounds}. Hit near 50.")
        self.action.setText("Slash")
        self._timer.start()

    def _advance(self) -> None:
        self.position += self.direction * 4
        if self.position >= 100:
            self.position = 100
            self.direction = -1
        elif self.position <= 0:
            self.position = 0
            self.direction = 1
        self.bar.setValue(self.position)

    def _stop_round(self) -> None:
        self._timer.stop()
        self.running = False
        round_score = max(10, 100 - abs(self.position - 50) * 2)
        self.score_total += round_score
        self.round_index += 1
        if self.round_index >= self.rounds:
            self.final_score = int(self.score_total / self.rounds)
            self.status.setText(f"Average {self.final_score}. Clean hit.")
            self.action.setText("Close")
        else:
            self.status.setText(f"Round score {round_score}. Again.")
            self.action.setText("Next")
