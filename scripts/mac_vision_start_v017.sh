#!/usr/bin/env bash
# Mac-only development server. Tang is optional and never used for source work.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$(uname)" != "Darwin" ]]; then
  echo "The native Vision helper requires macOS." >&2
  exit 2
fi
ENVFILE="$HOME/.config/stem-mentor/v016-formula.env"
if [[ -f "$ENVFILE" ]]; then
  set -a
  source "$ENVFILE"
  set +a
fi
if [[ ! -x "$ROOT/backend/native/.build/vision_ocr" ]]; then
  bash "$ROOT/scripts/build_vision_ocr.sh"
fi
export STEM_MENTOR_DB="$ROOT/backend/data/v017_synthetic_only.sqlite3"
cd "$ROOT/backend"
exec "$ROOT/.venv/bin/python" -m uvicorn app.main:app \
  --host 127.0.0.1 --port 18917 --workers 1
