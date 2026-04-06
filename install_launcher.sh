#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
TARGET="${BIN_DIR}/sukunatchi"

mkdir -p "${BIN_DIR}"
cat > "${TARGET}" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "${PROJECT_DIR}"
exec python3 -m src.main "\$@"
EOF

chmod +x "${TARGET}"
echo "Installed launcher at ${TARGET}"
