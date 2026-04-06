from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

from .app import SukunatchiApplication


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sukunatchi desktop pet")
    parser.add_argument("--screenshot", type=Path, help="Save a screenshot and exit.")
    parser.add_argument("--delay-ms", type=int, default=1200, help="Delay before screenshot capture.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    qt_app = QApplication(sys.argv)
    app = SukunatchiApplication(qt_app)
    app.window.show()

    if args.screenshot:
        target = args.screenshot
        deadline = time.monotonic() + (args.delay_ms / 1000.0)
        while time.monotonic() < deadline:
            qt_app.processEvents()
            time.sleep(0.04)
        target.parent.mkdir(parents=True, exist_ok=True)
        image = QImage(app.window.size(), QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        app.window.render(painter, QPoint())
        painter.end()
        image.save(str(target))
        return 0

    return qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
