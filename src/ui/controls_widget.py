from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QPushButton, QWidget

from ..config import PALETTE


class SymbolButton(QPushButton):
    def __init__(self, symbol: str, tooltip: str, compact: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.symbol = symbol
        self.compact = compact
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        if compact:
            self.setFixedSize(28, 28)
        else:
            self.setFixedSize(40, 40)

    def paintEvent(self, event) -> None:  # noqa: D401, ANN001
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(2, 2, -2, -2)

        shadow = QColor(PALETTE["button_face_dark"])
        shadow.setAlpha(160)
        painter.setBrush(shadow)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(rect.translated(0, 2))

        if self.isDown():
            fill = QColor(PALETTE["button_face_dark"])
        elif self.underMouse():
            fill = QColor(PALETTE["button_face_light"])
        else:
            fill = QColor(PALETTE["button_face"])
        painter.setBrush(fill)
        painter.drawEllipse(rect)

        gloss = rect.adjusted(5, 4, -5, -rect.height() // 2)
        gloss.setHeight(max(8, gloss.height()))
        painter.setBrush(QColor(255, 255, 255, 54))
        painter.drawEllipse(gloss)

        self._draw_symbol(painter, QRectF(rect))

    def _draw_symbol(self, painter: QPainter, rect: QRectF) -> None:
        pen = QPen(QColor(PALETTE["button_symbol"]), 2.1 if self.compact else 2.7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        cx = rect.center().x()
        cy = rect.center().y()

        if self.symbol == "meal":
            painter.drawArc(QRectF(cx - 7, cy - 1, 14, 8), 0, 180 * 16)
            painter.drawLine(QPointF(cx - 9, cy + 2), QPointF(cx + 9, cy + 2))
            painter.drawLine(QPointF(cx + 4, cy - 7), QPointF(cx + 8, cy - 2))
        elif self.symbol == "snack":
            candy = QPainterPath()
            candy.moveTo(cx - 4, cy - 5)
            candy.lineTo(cx + 4, cy - 5)
            candy.lineTo(cx + 6, cy)
            candy.lineTo(cx + 4, cy + 5)
            candy.lineTo(cx - 4, cy + 5)
            candy.lineTo(cx - 6, cy)
            candy.closeSubpath()
            painter.drawPath(candy)
            painter.drawLine(QPointF(cx - 6, cy), QPointF(cx - 11, cy - 4))
            painter.drawLine(QPointF(cx - 6, cy), QPointF(cx - 11, cy + 4))
            painter.drawLine(QPointF(cx + 6, cy), QPointF(cx + 11, cy - 4))
            painter.drawLine(QPointF(cx + 6, cy), QPointF(cx + 11, cy + 4))
        elif self.symbol == "clean":
            painter.drawPath(self._sparkle_path(cx, cy))
        elif self.symbol == "med":
            painter.drawRoundedRect(QRectF(cx - 8, cy - 7, 16, 14), 4, 4)
            painter.drawLine(QPointF(cx, cy - 4), QPointF(cx, cy + 4))
            painter.drawLine(QPointF(cx - 4, cy), QPointF(cx + 4, cy))
        elif self.symbol == "sleep":
            moon = QPainterPath()
            moon.addEllipse(QRectF(cx - 7, cy - 8, 12, 12))
            cut = QPainterPath()
            cut.addEllipse(QRectF(cx - 3, cy - 9, 12, 12))
            painter.drawPath(moon.subtracted(cut))
        elif self.symbol == "play":
            painter.drawEllipse(QRectF(cx - 6, cy - 6, 12, 12))
            painter.drawLine(QPointF(cx, cy - 7), QPointF(cx, cy + 7))
            painter.drawLine(QPointF(cx - 7, cy), QPointF(cx + 7, cy))
        elif self.symbol == "discipline":
            painter.drawLine(QPointF(cx, cy - 8), QPointF(cx, cy + 2))
            painter.drawEllipse(QRectF(cx - 1, cy + 6, 2, 2))
        elif self.symbol == "stats":
            painter.drawLine(QPointF(cx - 8, cy + 6), QPointF(cx - 8, cy - 1))
            painter.drawLine(QPointF(cx, cy + 6), QPointF(cx, cy - 6))
            painter.drawLine(QPointF(cx + 8, cy + 6), QPointF(cx + 8, cy - 3))
        elif self.symbol == "menu":
            painter.drawEllipse(QRectF(cx - 7, cy - 2, 4, 4))
            painter.drawEllipse(QRectF(cx - 2, cy - 2, 4, 4))
            painter.drawEllipse(QRectF(cx + 3, cy - 2, 4, 4))

    def _sparkle_path(self, cx: float, cy: float) -> QPainterPath:
        sparkle = QPainterPath()
        sparkle.moveTo(cx, cy - 8)
        sparkle.lineTo(cx + 2.2, cy - 2.2)
        sparkle.lineTo(cx + 8, cy)
        sparkle.lineTo(cx + 2.2, cy + 2.2)
        sparkle.lineTo(cx, cy + 8)
        sparkle.lineTo(cx - 2.2, cy + 2.2)
        sparkle.lineTo(cx - 8, cy)
        sparkle.lineTo(cx - 2.2, cy - 2.2)
        sparkle.closeSubpath()
        return sparkle


class ControlsWidget(QWidget):
    action = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(258, 134)
        self._buttons: list[SymbolButton] = []
        self._build()

    def _build(self) -> None:
        items = [
            ("meal", "Meal", True, (0, 0)),
            ("snack", "Snack", True, (38, 0)),
            ("clean", "Clean", True, (76, 0)),
            ("med", "Medicine", True, (114, 0)),
            ("sleep", "Sleep / lights", True, (152, 0)),
            ("play", "Play", True, (190, 0)),
            ("discipline", "Discipline", False, (24, 64)),
            ("stats", "Stats", False, (109, 64)),
            ("menu", "Settings", False, (194, 64)),
        ]
        for symbol, tooltip, compact, (x_pos, y_pos) in items:
            button = SymbolButton(symbol, tooltip, compact, self)
            button.move(x_pos, y_pos)
            button.clicked.connect(lambda _checked=False, name=symbol: self.action.emit(name))
            self._buttons.append(button)

    def paintEvent(self, event) -> None:  # noqa: D401, ANN001
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        panel = QRectF(self.rect().adjusted(0, 8, 0, 0))
        panel.setHeight(panel.height() - 8)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(40, 22, 21, 26))
        painter.drawRoundedRect(panel, 28, 28)
