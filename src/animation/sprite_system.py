from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QBrush,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QRadialGradient,
)

from ..pet.evolution import get_stage_profile
from ..pet.model import PetData
from .animator import AnimationFrame


def _color(hex_code: str, alpha: int = 255) -> QColor:
    color = QColor(hex_code)
    color.setAlpha(alpha)
    return color


def _hair_polygon(head: QRectF, spikes: int, stray_hair: float, sway: float) -> QPolygonF:
    top = head.top() - head.height() * 0.26
    left = head.left() - head.width() * 0.10
    right = head.right() + head.width() * 0.10
    base_y = head.top() + head.height() * 0.33
    points = [QPointF(left, base_y)]
    span = right - left
    for index in range(spikes):
        ratio = index / max(1, spikes - 1)
        peak_x = left + span * ratio
        wave = math.sin((ratio * math.pi * 3.0) + sway * 0.6) * head.width() * 0.018
        center_boost = 1.0 - abs(0.5 - ratio) * 1.8
        peak_y = (
            top
            - (0.05 + stray_hair * 0.05) * head.height()
            - (index % 2) * head.height() * 0.07
            - max(0.0, center_boost) * head.height() * 0.08
        )
        points.append(QPointF(peak_x + wave, peak_y))
    points.append(QPointF(right, base_y))
    points.append(QPointF(head.right() - head.width() * 0.10, head.center().y() - head.height() * 0.08))
    points.append(QPointF(head.left() + head.width() * 0.10, head.center().y() - head.height() * 0.08))
    return QPolygonF(points)


def _face_marks(painter: QPainter, head: QRectF, menace: float) -> None:
    mark_pen = QPen(_color("#4d1720"), 3.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(mark_pen)

    forehead = QPainterPath()
    forehead.moveTo(head.center().x() - head.width() * 0.22, head.top() + head.height() * 0.24)
    forehead.cubicTo(
        head.center().x() - head.width() * 0.08,
        head.top() + head.height() * (0.15 - menace * 0.03),
        head.center().x() + head.width() * 0.08,
        head.top() + head.height() * (0.15 - menace * 0.03),
        head.center().x() + head.width() * 0.22,
        head.top() + head.height() * 0.24,
    )
    painter.drawPath(forehead)

    center_mark = QPainterPath()
    center_mark.moveTo(head.center().x(), head.top() + head.height() * 0.24)
    center_mark.lineTo(head.center().x(), head.top() + head.height() * 0.38)
    painter.drawPath(center_mark)

    for direction in (-1.0, 1.0):
        upper = QPainterPath()
        upper.moveTo(head.center().x() + head.width() * 0.11 * direction, head.center().y() - head.height() * 0.10)
        upper.cubicTo(
            head.center().x() + head.width() * 0.23 * direction,
            head.center().y() - head.height() * 0.15,
            head.center().x() + head.width() * 0.28 * direction,
            head.center().y() - head.height() * 0.01,
            head.center().x() + head.width() * 0.18 * direction,
            head.center().y() + head.height() * 0.04,
        )
        painter.drawPath(upper)

        lower = QPainterPath()
        lower.moveTo(head.center().x() + head.width() * 0.16 * direction, head.center().y() + head.height() * 0.07)
        lower.cubicTo(
            head.center().x() + head.width() * 0.27 * direction,
            head.center().y() + head.height() * 0.11,
            head.center().x() + head.width() * 0.22 * direction,
            head.center().y() + head.height() * 0.25,
            head.center().x() + head.width() * 0.14 * direction,
            head.center().y() + head.height() * 0.28,
        )
        painter.drawPath(lower)


def _draw_aura(painter: QPainter, rect: QRectF, strength: float, phase: float, corrupted: bool) -> None:
    if strength <= 0.02:
        return
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    for index in range(4):
        bubble = QRectF(
            rect.left() + rect.width() * (0.1 + index * 0.18),
            rect.top() + rect.height() * (0.08 + math.sin(phase * 6.0 + index) * 0.02),
            rect.width() * 0.28,
            rect.height() * 0.56,
        )
        gradient = QRadialGradient(bubble.center(), bubble.width() * 0.5)
        if corrupted:
            gradient.setColorAt(0.0, _color("#6f2d34", int(48 + strength * 40)))
            gradient.setColorAt(1.0, _color("#000000", 0))
        else:
            gradient.setColorAt(0.0, _color("#bf263f", int(60 + strength * 90)))
            gradient.setColorAt(1.0, _color("#ffffff", 0))
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(bubble)
    painter.restore()


def draw_character(painter: QPainter, rect: QRectF, pet: PetData, frame: AnimationFrame) -> None:
    profile = get_stage_profile(pet.stage)
    mood = frame.emotion if frame.emotion != "idle" else pet.mood
    painter.save()

    corrupted = pet.stage in {"brat", "fallen_king"}
    aura_strength = profile.aura_strength + (0.14 if mood in {"angry", "joy"} else 0.0)
    _draw_aura(painter, rect, aura_strength, frame.aura, corrupted)

    base_y = rect.bottom() - 22 - frame.breath * 1.8 - frame.bounce * 2.0
    body_h = rect.height() * 0.42 * profile.body_scale
    head_d = rect.width() * 0.36 * profile.head_scale
    body_rect = QRectF(
        rect.center().x() - rect.width() * 0.16,
        base_y - body_h,
        rect.width() * 0.32,
        body_h,
    )
    head_rect = QRectF(
        rect.center().x() - head_d / 2 + frame.sway * 1.8,
        body_rect.top() - head_d * 0.86,
        head_d,
        head_d * 0.92,
    )

    robe_path = QPainterPath()
    robe_path.moveTo(body_rect.center().x(), body_rect.top() - 4)
    robe_path.lineTo(body_rect.right() + 10, body_rect.top() + body_rect.height() * 0.36)
    robe_path.lineTo(body_rect.right() - 4, body_rect.bottom())
    robe_path.lineTo(body_rect.left() + 4, body_rect.bottom())
    robe_path.lineTo(body_rect.left() - 10, body_rect.top() + body_rect.height() * 0.36)
    robe_path.closeSubpath()

    robe_gradient = QLinearGradient(body_rect.topLeft(), body_rect.bottomRight())
    robe_gradient.setColorAt(0.0, _color("#191515"))
    robe_gradient.setColorAt(0.6, _color("#2b2426"))
    robe_gradient.setColorAt(1.0, _color("#0d0b0c"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(robe_gradient))
    painter.drawPath(robe_path)

    trim_pen = QPen(_color(profile.robe_trim), 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(trim_pen)
    painter.drawLine(
        QPointF(body_rect.center().x(), body_rect.top() + 6),
        QPointF(body_rect.center().x(), body_rect.bottom() - 6),
    )
    painter.drawArc(
        QRectF(body_rect.left() + 6, body_rect.top() + 8, body_rect.width() - 12, body_rect.height() * 0.55),
        25 * 16,
        130 * 16,
    )

    hand_pen = QPen(_color("#f5d2c2"), 11.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(hand_pen)
    arm_height = body_rect.top() + body_rect.height() * (0.30 if mood == "angry" else 0.44)
    if mood in {"joy", "pet"}:
        painter.drawLine(QPointF(body_rect.left() + 10, arm_height), QPointF(body_rect.left() - 14, arm_height - 12))
        painter.drawLine(QPointF(body_rect.right() - 10, arm_height), QPointF(body_rect.right() + 14, arm_height - 12))
    elif mood == "sleep":
        painter.drawLine(QPointF(body_rect.left() + 10, arm_height), QPointF(body_rect.left() - 6, arm_height + 8))
        painter.drawLine(QPointF(body_rect.right() - 10, arm_height), QPointF(body_rect.right() + 6, arm_height + 8))
    else:
        painter.drawLine(QPointF(body_rect.left() + 12, arm_height), QPointF(body_rect.left() - 10, arm_height + frame.sway * 2.0))
        painter.drawLine(QPointF(body_rect.right() - 12, arm_height), QPointF(body_rect.right() + 10, arm_height - frame.sway * 2.0))

    neck_shadow = QRadialGradient(head_rect.center(), head_rect.width() * 0.62)
    neck_shadow.setColorAt(0.0, _color("#f1d3c3"))
    neck_shadow.setColorAt(1.0, _color("#e8b9ac"))
    painter.setBrush(QBrush(neck_shadow))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(head_rect)

    painter.setBrush(_color("#ecc0b3"))
    painter.drawEllipse(QRectF(head_rect.left() - 7, head_rect.center().y() - 7, 10, 14))
    painter.drawEllipse(QRectF(head_rect.right() - 3, head_rect.center().y() - 7, 10, 14))

    hair = QPainterPath()
    hair.addPolygon(_hair_polygon(head_rect, profile.hair_spikes, profile.stray_hair, frame.sway))
    hair.closeSubpath()
    painter.setBrush(_color("#eaa2b7"))
    painter.drawPath(hair)

    bangs = QPainterPath()
    bangs.moveTo(head_rect.left() + head_rect.width() * 0.10, head_rect.top() + head_rect.height() * 0.34)
    bangs.lineTo(head_rect.center().x() - head_rect.width() * 0.18, head_rect.top() + head_rect.height() * 0.02)
    bangs.lineTo(head_rect.center().x() - head_rect.width() * 0.03, head_rect.top() + head_rect.height() * 0.26)
    bangs.lineTo(head_rect.center().x(), head_rect.top() - head_rect.height() * 0.02)
    bangs.lineTo(head_rect.center().x() + head_rect.width() * 0.10, head_rect.top() + head_rect.height() * 0.24)
    bangs.lineTo(head_rect.center().x() + head_rect.width() * 0.24, head_rect.top() + head_rect.height() * 0.03)
    bangs.lineTo(head_rect.right() - head_rect.width() * 0.10, head_rect.top() + head_rect.height() * 0.34)
    painter.setBrush(_color("#f7becb"))
    painter.drawPath(bangs)

    side_lock_pen = QPen(_color("#eaa2b7"), 8.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(side_lock_pen)
    painter.drawLine(
        QPointF(head_rect.left() + 6, head_rect.top() + head_rect.height() * 0.28),
        QPointF(head_rect.left() - 4, head_rect.bottom() - 14),
    )
    painter.drawLine(
        QPointF(head_rect.right() - 6, head_rect.top() + head_rect.height() * 0.28),
        QPointF(head_rect.right() + 4, head_rect.bottom() - 14),
    )

    brow_pen = QPen(_color("#2c1d20"), 3.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(brow_pen)
    brow_y = head_rect.center().y() - head_rect.height() * 0.09
    menace = profile.menace
    painter.drawLine(
        QPointF(head_rect.center().x() - head_rect.width() * 0.28, brow_y + menace * 2.0),
        QPointF(head_rect.center().x() - head_rect.width() * 0.06, brow_y - 2.6 - menace * 2.0),
    )
    painter.drawLine(
        QPointF(head_rect.center().x() + head_rect.width() * 0.06, brow_y - 2.6 - menace * 2.0),
        QPointF(head_rect.center().x() + head_rect.width() * 0.28, brow_y + menace * 2.0),
    )

    blink_scale = max(0.14, 1.0 - frame.blink * 0.92)
    eye_w = head_rect.width() * 0.18
    eye_h = head_rect.height() * 0.10 * blink_scale
    eye_y = head_rect.center().y() - head_rect.height() * 0.01
    lash_pen = QPen(_color("#221619"), 2.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    for direction in (-1.0, 1.0):
        eye_rect = QRectF(
            head_rect.center().x() + direction * head_rect.width() * 0.15 - eye_w / 2,
            eye_y,
            eye_w,
            eye_h,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_color("#f9ede8"))
        painter.drawRoundedRect(eye_rect, eye_h, eye_h)
        if frame.blink < 0.4:
            painter.setBrush(_color("#961929"))
            pupil = QRectF(
                eye_rect.left() + eye_w * 0.31,
                eye_rect.top() + eye_h * 0.08,
                eye_w * 0.36,
                eye_h * 0.82,
            )
            painter.drawRoundedRect(pupil, pupil.height() * 0.45, pupil.height() * 0.45)
            painter.setBrush(_color("#ffffff"))
            painter.drawEllipse(QRectF(pupil.left() + pupil.width() * 0.60, pupil.top() + 1.0, 2.6, 2.6))
        painter.setPen(lash_pen)
        painter.drawLine(
            QPointF(eye_rect.left() - 1, eye_rect.top() + eye_rect.height() * 0.42),
            QPointF(eye_rect.right() + 1, eye_rect.top() + eye_rect.height() * 0.16),
        )

    _face_marks(painter, head_rect, menace)

    mouth_pen = QPen(_color("#702027"), 2.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(mouth_pen)
    mouth = QPainterPath()
    mouth_left = head_rect.center().x() - head_rect.width() * 0.08
    mouth_y = head_rect.center().y() + head_rect.height() * 0.18
    mouth.moveTo(mouth_left, mouth_y)
    if mood in {"angry"}:
        mouth.cubicTo(mouth_left + 4, mouth_y + 2, mouth_left + 10, mouth_y + 2, mouth_left + 16, mouth_y - 1)
    elif mood in {"sleep"}:
        mouth.cubicTo(mouth_left + 3, mouth_y + 1.5, mouth_left + 8, mouth_y + 1.5, mouth_left + 14, mouth_y)
    else:
        mouth.cubicTo(mouth_left + 5, mouth_y + 3 + profile.smirk * 3.4, mouth_left + 10, mouth_y + 4, mouth_left + 18, mouth_y - 1)
    painter.drawPath(mouth)

    if mood == "eat":
        painter.setBrush(_color("#7b151e"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(head_rect.center().x() + 9, head_rect.center().y() + 18, 6, 6))

    if pet.poop_count > 0:
        painter.setBrush(_color("#724d2c"))
        painter.drawEllipse(QRectF(rect.left() + 18, rect.bottom() - 24, 18, 12))
        painter.drawEllipse(QRectF(rect.left() + 22, rect.bottom() - 34, 12, 12))

    if pet.sick:
        sick_pen = QPen(_color("#7c9c60"), 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(sick_pen)
        painter.drawArc(QRectF(head_rect.right() - 8, head_rect.top() - 4, 16, 20), 90 * 16, 200 * 16)
        painter.drawArc(QRectF(head_rect.right() + 4, head_rect.top() + 10, 14, 16), 70 * 16, 220 * 16)

    if pet.sleeping:
        sleep_pen = QPen(_color("#445c8e"), 2.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(sleep_pen)
        painter.drawText(QRectF(rect.right() - 44, rect.top() + 8, 32, 28), Qt.AlignmentFlag.AlignCenter, "Z")
        painter.drawText(QRectF(rect.right() - 28, rect.top() + 20, 24, 20), Qt.AlignmentFlag.AlignCenter, "z")

    if mood in {"joy", "pet"}:
        painter.setBrush(_color("#d8435e", 180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(head_rect.left() - 10, head_rect.top() + 16, 8, 8))
        painter.drawEllipse(QRectF(head_rect.right() + 2, head_rect.top() + 10, 8, 8))

    painter.restore()
