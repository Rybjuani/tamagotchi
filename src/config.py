from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRect


APP_NAME = "Sukunatchi"
WINDOW_TITLE = "Sukunatchi"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
AUDIO_DIR = ASSETS_DIR / "audio"
SAVE_DIR = Path.home() / ".local" / "share" / "sukunatchi"
SAVE_FILE = SAVE_DIR / "save.json"

WINDOW_WIDTH = 336
WINDOW_HEIGHT = 486
SHELL_MARGIN = 12
SCREEN_RECT = QRect(74, 102, 188, 158)
ACTION_ROW_Y = 289
BOTTOM_BUTTON_Y = 359

TICK_MS = 1000
ANIMATION_MS = 80
REAL_SECONDS_PER_PET_HOUR = 60

DEFAULT_SETTINGS = {
    "always_on_top": True,
    "muted": False,
    "volume": 0.62,
}

DEFAULT_MESSAGE = "Ready to rule."

PALETTE = {
    "shell_base": "#ead0aa",
    "shell_shadow": "#b68c68",
    "shell_highlight": "#f8e8d4",
    "shell_accent": "#8b2234",
    "shell_accent_dark": "#5a1520",
    "shell_inner": "#d9b58f",
    "bezel_outer": "#322930",
    "bezel_inner": "#5a514f",
    "screen_bg": "#f0f3ea",
    "screen_shade": "#cfd9ca",
    "screen_dark": "#7c8f84",
    "screen_text": "#38413b",
    "button_face": "#c65b62",
    "button_face_dark": "#8b343f",
    "button_face_light": "#eb9aa0",
    "button_symbol": "#fff5f1",
    "status_good": "#d75d5d",
    "status_warn": "#cc8d3c",
    "status_bad": "#738c6f",
    "aura": "#b62946",
}

STAGE_NAMES = {
    "seed": "Cursed Seed",
    "brat": "Brat Sukuna",
    "vessel": "Vessel Heir",
    "prince": "Cursed Prince",
    "heir": "Heian Heir",
    "fallen_king": "Fallen King",
    "domain_lord": "Domain Lord",
    "malevolent_sovereign": "Malevolent Sovereign",
}
