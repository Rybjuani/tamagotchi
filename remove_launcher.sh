#!/usr/bin/env bash
set -euo pipefail

TARGET="${HOME}/.local/bin/sukunatchi"

if [[ -f "${TARGET}" ]]; then
  rm -f "${TARGET}"
  echo "Removed ${TARGET}"
else
  echo "Launcher not installed at ${TARGET}"
fi
