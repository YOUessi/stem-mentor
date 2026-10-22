#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENVFILE="$HOME/.config/stem-mentor/v016-formula.env"
if [[ ! -f "$ENVFILE" ]]; then
  echo "Missing private local formula connection token" >&2
  exit 2
fi
set -a
source "$ENVFILE"
set +a
if [[ "$(uname)" == "Darwin" ]] && [[ ! -x "$ROOT/backend/native/.build/vision_ocr" ]]; then
  bash "$ROOT/scripts/build_vision_ocr.sh"
fi
cd "$ROOT/backend"
exec "$ROOT/.venv/bin/python" -m uvicorn app.main:app \
  --host 127.0.0.1 --port 18916
