# Sukunatchi

Compact Linux desktop pet built with Python and PySide6. The window is shaped and scaled like a late-90s Tamagotchi toy, with a custom chibi anime mascot inspired by Sukuna, retro beeps, classic care mechanics, local persistence, minigames, evolution paths and Linux autostart support.

## Features

- Compact frameless gadget window with toy-like shell and small on-screen footprint
- Original code-drawn Sukuna-like mascot with breathing, blink, pet, joy, anger, sleep, sickness and evolution reactions
- Classic care loop: meal, snack, hygiene, medicine, discipline, sleep, alerts and local save state
- Stats tracking: hunger, joy, health, energy, discipline, age, weight, mistakes, win count and evolution stage
- Two minigames: `Slash Reflex` and `Black Flash`
- Multiple Sukuna-themed evolution outcomes, including poor-care and superior-care routes
- Retro local audio generated in `assets/audio`
- Always-on-top toggle, mute toggle and Linux autostart installer/remover

## Requirements

- Python 3.11+
- PySide6 6.6+

Install dependency:

```bash
python3 -m pip install -r requirements.txt
```

## Run

```bash
python3 -m src.main
```

Install a global terminal launcher:

```bash
./install_launcher.sh
```

Then run from anywhere:

```bash
sukunatchi
```

Controls:

- Click the mascot to pet him.
- Top small buttons: meal, snack, clean, medicine, sleep, play.
- Bottom buttons: discipline, stats overlay, settings/menu.
- Right click the shell for the same settings menu.

## Autostart

Install:

```bash
./install_autostart.sh
```

Remove:

```bash
./remove_autostart.sh
```

This manages `~/.config/autostart/sukunatchi.desktop`.

## Project Layout

```text
assets/
  audio/
src/
  animation/
  minigames/
  pet/
  ui/
  app.py
  autostart.py
  config.py
  main.py
  persistence.py
  sound.py
install_autostart.sh
remove_autostart.sh
requirements.txt
```

## Technical Notes

- Visual shell, controls and mascot are drawn locally with Qt painting code.
- Save data is stored as JSON in `~/.local/share/sukunatchi/save.json`.
- Retro beep assets are generated locally on first run, so the project does not depend on external media.
