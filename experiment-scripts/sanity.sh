#!/usr/bin/env bash
# One-command WSL2 sanity gate for the G1 campaign (not the 160-run suite).
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"
if [[ ! -f simulator/tooling/activate.sh ]]; then
  echo "Missing pinned environment activation script; run the bootstrap first." >&2
  exit 2
fi
# shellcheck disable=SC1091
source simulator/tooling/activate.sh
exec "$ROOT/simulator/ns-3.48/.venv/bin/python" "$SCRIPT_DIR/sanity.py" "$@"
