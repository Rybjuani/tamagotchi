from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ..animation.animator import PetAnimator
from ..animation.sprite_system import draw_character
from ..config import PALETTE
from ..pet.model import PetData
from .stats_panel import build_meta_lines, build_stat_rows


class ScreenWidget(QWidget):
    pet_clicked = Signal()

    def __init__(self, animator: PetAnimator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.animator = animator
        self.animator.frame_changed.connect(self.update)
        self.pet = PetData()
        self.message = self.pet.last_message
        self.show_stats = False
        self.setFixedSize(188, 158)

    def set_pet(self, pet: PetData) -> None:
        self.pet = pet
        self.message = pet.last_message
        self.update()

    def set_message(self, message: str) -> None:
        self.message = message
        self.update()

    def toggle_stats(self) -> None:
        self.show_stats = not self.show_stats
        self.update()

    def mousePressEvent(self, event) -> None:  # noqa: D401, ANN001
        if event.button() == Qt.MouseButton.LeftButton:
            self.pet_clicked.emit()

    def paintEvent(self, event) -> None:  # noqa: D401, ANN001
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        panel = QRectF(self.rect()).adjusted(2, 2, -2, -2)

        bg = QLinearGradient(panel.topLeft(), panel.bottomLeft())
        if self.pet.sleeping:
            bg.setColorAt(0.0, QColor("#d8dde9"))
            bg.setColorAt(1.0, QColor("#c3cedd"))
        else:
            bg.setColorAt(0.0, QColor(PALETTE["screen_bg"]))
            bg.setColorAt(1.0, QColor(PALETTE["screen_shade"]))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg)
        painter.drawRoundedRect(panel, 22, 22)

        painter.setPen(QPen(QColor(255, 255, 255, 60), 1.3))
        painter.drawRoundedRect(panel.adjusted(4, 4, -4, -4), 18, 18)

        painter.setPen(QPen(QColor(55, 63, 57, 20), 1.0))
        for y_pos in range(16, self.height(), 6):
            painter.drawLine(8, y_pos, self.width() - 8, y_pos)

        self._draw_status(painter, panel)
        self._draw_message(painter, panel)

        play_rect = QRectF(panel.left() + 16, panel.top() + 34, panel.width() - 32, panel.height() - 46)
        painter.setPen(QPen(QColor(PALETTE["screen_dark"]), 2.0))
        painter.drawLine(play_rect.left() + 8, play_rect.bottom() - 8, play_rect.right() - 10, play_rect.bottom() - 8)
        draw_character(painter, play_rect, self.pet, self.animator.snapshot())

        if self.show_stats:
            self._draw_stats_overlay(painter, panel)

    def _draw_status(self, painter: QPainter, panel: QRectF) -> None:
        icons: list[tuple[str, QColor]] = []
        if self.pet.attention:
            icons.append(("!", QColor("#a6363f")))
        if self.pet.sick:
            icons.append(("+", QColor("#6f9256")))
        if self.pet.poop_count:
            icons.append(("D", QColor("#855e33")))
        if self.pet.sleeping:
            icons.append(("Z", QColor("#566f96")))
        x_pos = panel.left() + 12
        font = QFont("DejaVu Sans", 8)
        font.setBold(True)
        painter.setFont(font)
        for text, color in icons:
            badge = QRectF(x_pos, panel.top() + 10, 18, 18)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(badge)
            painter.setPen(QPen(QColor("#fff9f1"), 1.0))
            painter.drawText(badge, Qt.AlignmentFlag.AlignCenter, text)
            x_pos += 22

    def _draw_message(self, painter: QPainter, panel: QRectF) -> None:
        bubble = QRectF(panel.left() + 10, panel.top() + 8, panel.width() - 20, 22)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 96))
        painter.drawRoundedRect(bubble, 10, 10)
        font = QFont("DejaVu Sans", 6)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor(PALETTE["screen_text"]), 1.0))
        metrics = QFontMetrics(font)
        message = metrics.elidedText(self.message, Qt.TextElideMode.ElideRight, int(bubble.width() - 14))
        painter.drawText(bubble.adjusted(8, 0, -8, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, message)

    def _draw_stats_overlay(self, painter: QPainter, panel: QRectF) -> None:
        overlay = panel.adjusted(18, 34, -18, -14)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(26, 30, 27, 172))
        painter.drawRoundedRect(overlay, 14, 14)

        title_font = QFont("DejaVu Sans", 7)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(QPen(QColor("#f9f7f2"), 1.0))
        meta_lines = build_meta_lines(self.pet)
        painter.drawText(overlay.adjusted(10, 8, -10, 0), meta_lines[0])

        stats = build_stat_rows(self.pet)
        small_font = QFont("DejaVu Sans", 6)
        painter.setFont(small_font)
        y_pos = overlay.top() + 28
        for label, value in stats:
            painter.setPen(QPen(QColor("#f0eee7"), 1.0))
            painter.drawText(int(overlay.left() + 10), int(y_pos + 7), label)
            bar = QRectF(overlay.left() + 34, y_pos, overlay.width() - 46, 8)
            painter.setBrush(QColor(255, 255, 255, 26))
            painter.drawRoundedRect(bar, 4, 4)
            fill = QRectF(bar.left(), bar.top(), bar.width() * max(0.0, min(1.0, value / 100.0)), bar.height())
            painter.setBrush(QColor("#d85d66"))
            painter.drawRoundedRect(fill, 4, 4)
            y_pos += 15

        meta_font = QFont("DejaVu Sans", 6)
        painter.setFont(meta_font)
        painter.setPen(QPen(QColor("#faf6ee"), 1.0))
        painter.drawText(overlay.adjusted(10, int(overlay.height()) - 34, -10, -18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, meta_lines[1])
        painter.drawText(overlay.adjusted(10, int(overlay.height()) - 18, -10, -4), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, meta_lines[2])
