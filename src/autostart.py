from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

from .config import APP_NAME, PROJECT_ROOT


AUTOSTART_DIR = Path.home() / ".config" / "autostart"
DESKTOP_FILE = AUTOSTART_DIR / "sukunatchi.desktop"


def desktop_entry() -> str:
    command = f"cd {shlex.quote(str(PROJECT_ROOT))} && {shlex.quote(sys.executable)} -m src.main"
    return f"""[Desktop Entry]
Type=Application
Version=1.0
Name={APP_NAME}
Comment=Pocket Sukuna tamagotchi
Exec=/bin/bash -lc {shlex.quote(command)}
Path={PROJECT_ROOT}
Terminal=false
X-GNOME-Autostart-enabled=true
Categories=Game;
"""


def install_autostart() -> Path:
    AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)
    DESKTOP_FILE.write_text(desktop_entry(), encoding="utf-8")
    return DESKTOP_FILE


def remove_autostart() -> bool:
    if DESKTOP_FILE.exists():
        DESKTOP_FILE.unlink()
        return True
    return False


def is_autostart_enabled() -> bool:
    return DESKTOP_FILE.exists()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage Sukunatchi autostart")
    parser.add_argument("command", choices=["install", "remove", "status"])
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.command == "install":
        print(install_autostart())
    elif args.command == "remove":
        print(remove_autostart())
    else:
        print(is_autostart_enabled())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
