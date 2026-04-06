from __future__ import annotations

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget

from ..animation.animator import PetAnimator
from ..config import BOTTOM_BUTTON_Y, PALETTE, SCREEN_RECT, WINDOW_HEIGHT, WINDOW_WIDTH
from ..pet.model import PetData
from .controls_widget import ControlsWidget
from .screen_widget import ScreenWidget


class ShellWidget(QWidget):
    def __init__(self, animator: PetAnimator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_offset: QPoint | None = None

        self.screen = ScreenWidget(animator, self)
        self.screen.setGeometry(SCREEN_RECT)

        self.controls = ControlsWidget(self)
        self.controls.move(39, 280)

    def set_pet(self, pet: PetData) -> None:
        self.screen.set_pet(pet)

    def toggle_stats(self) -> None:
        self.screen.toggle_stats()

    def mousePressEvent(self, event) -> None:  # noqa: D401, ANN001
        if event.button() == Qt.MouseButton.LeftButton:
            top_level = self.window()
            self._drag_offset = event.globalPosition().toPoint() - top_level.frameGeometry().topLeft()

    def mouseMoveEvent(self, event) -> None:  # noqa: D401, ANN001
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            top_level = self.window()
            top_level.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event) -> None:  # noqa: D401, ANN001
        self._drag_offset = None

    def paintEvent(self, event) -> None:  # noqa: D401, ANN001
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        shell_rect = QRectF(16, 10, self.width() - 32, self.height() - 22)
        path = self._shell_path(shell_rect)

        for offset, alpha in ((8, 34), (5, 48), (3, 70)):
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(14, 8, 8, alpha))
            painter.drawPath(path.translated(0, offset))

        outer = QLinearGradient(shell_rect.topLeft(), shell_rect.bottomLeft())
        outer.setColorAt(0.0, QColor(PALETTE["shell_highlight"]))
        outer.setColorAt(0.4, QColor(PALETTE["shell_base"]))
        outer.setColorAt(1.0, QColor(PALETTE["shell_shadow"]))
        painter.setBrush(outer)
        painter.setPen(QPen(QColor(PALETTE["shell_accent_dark"]), 2.2))
        painter.drawPath(path)

        inner = self._shell_path(shell_rect.adjusted(12, 14, -12, -18))
        painter.setBrush(QColor(255, 255, 255, 38))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(inner)

        ring_rect = QRectF(self.width() / 2 - 28, 0, 56, 34)
        painter.setBrush(QColor(PALETTE["shell_base"]))
        painter.setPen(QPen(QColor(PALETTE["shell_accent_dark"]), 2.0))
        painter.drawEllipse(ring_rect)
        painter.setBrush(QColor(24, 14, 16))
        painter.drawEllipse(ring_rect.adjusted(12, 8, -12, -8))

        self._draw_bezel(painter)
        self._draw_details(painter)

    def _shell_path(self, rect: QRectF) -> QPainterPath:
        cx = rect.center().x()
        top = rect.top()
        bottom = rect.bottom()
        left = rect.left()
        right = rect.right()
        path = QPainterPath()
        path.moveTo(cx, top + 8)
        path.cubicTo(right - 18, top + 26, right - 4, rect.top() + rect.height() * 0.36, right - 18, rect.top() + rect.height() * 0.73)
        path.cubicTo(right - 30, bottom - 14, cx + 44, bottom - 2, cx, bottom - 2)
        path.cubicTo(cx - 44, bottom - 2, left + 30, bottom - 14, left + 18, rect.top() + rect.height() * 0.73)
        path.cubicTo(left + 4, rect.top() + rect.height() * 0.36, left + 18, top + 26, cx, top + 8)
        path.closeSubpath()
        return path

    def _draw_bezel(self, painter: QPainter) -> None:
        bezel = QRectF(SCREEN_RECT).adjusted(-10, -10, 10, 10)
        painter.setBrush(QColor(PALETTE["bezel_outer"]))
        painter.setPen(QPen(QColor("#1e1a1d"), 1.8))
        painter.drawRoundedRect(bezel, 24, 24)

        inner = bezel.adjusted(8, 8, -8, -8)
        gradient = QLinearGradient(inner.topLeft(), inner.bottomLeft())
        gradient.setColorAt(0.0, QColor(PALETTE["bezel_inner"]))
        gradient.setColorAt(1.0, QColor("#2e2b2a"))
        painter.setBrush(gradient)
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1.0))
        painter.drawRoundedRect(inner, 18, 18)

    def _draw_details(self, painter: QPainter) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(PALETTE["shell_inner"]))
        painter.drawRoundedRect(QRectF(60, 274, self.width() - 120, 104), 26, 26)

        painter.setBrush(QColor(PALETTE["shell_accent_dark"]))
        for x_pos in (116, 130, 144, 158, 172, 186, 200):
            painter.drawEllipse(QRectF(x_pos, 58, 4, 4))

        painter.setPen(QPen(QColor(255, 255, 255, 55), 1.4))
        painter.drawArc(QRectF(72, 48, self.width() - 144, 40), 20 * 16, 130 * 16)

        gloss = QRadialGradient(QPointF(104, 94), 160)
        gloss.setColorAt(0.0, QColor(255, 255, 255, 85))
        gloss.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(gloss)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(40, 40, 190, 180))
