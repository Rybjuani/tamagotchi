#!/usr/bin/env bash
set -euo pipefail
cd "/home/rybjuani/Escritorio/tamagotchi"
exec python3 -m src.main "$@"
