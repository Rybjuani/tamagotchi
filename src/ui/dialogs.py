from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QWidget


DIALOG_STYLE = """
QDialog {
    background: #f3e6d3;
    border: 2px solid #8b2234;
    border-radius: 16px;
}
QLabel {
    color: #3c2a2b;
}
QPushButton {
    background: #c65b62;
    color: #fff7f1;
    border: 1px solid #8b2234;
    border-radius: 12px;
    padding: 8px 12px;
    font-weight: 700;
}
QPushButton:hover {
    background: #d97179;
}
QPushButton:pressed {
    background: #8b343f;
}
"""


class GamePickerDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.selection: str | None = None
        self.setWindowTitle("Choose a Game")
        self.setModal(True)
        self.setFixedSize(236, 188)
        self.setStyleSheet(DIALOG_STYLE)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        title = QLabel("Play")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: 700;")
        description = QLabel("Pick a quick retro game to raise joy.")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        reflex_button = QPushButton("Slash Reflex")
        timing_button = QPushButton("Black Flash")
        cancel_button = QPushButton("Cancel")

        reflex_button.clicked.connect(lambda: self._choose("reaction"))
        timing_button.clicked.connect(lambda: self._choose("timing"))
        cancel_button.clicked.connect(self.reject)

        for widget in (title, description, reflex_button, timing_button, cancel_button):
            layout.addWidget(widget)

    def _choose(self, selection: str) -> None:
        self.selection = selection
        self.accept()
