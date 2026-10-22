#!/usr/bin/env bash
set -euo pipefail
ROOT="$HOME/projects/stem-mentor-formula-v016"
if [[ ! -f "$ROOT/.formula.env" ]]; then
  echo "Missing private .formula.env (never commit secrets)" >&2
  exit 2
fi
set -a
source "$ROOT/.formula.env"
set +a
if [[ -z "$STEM_FORMULA_SERVICE_TOKEN" ]]; then
  echo "Missing worker token" >&2
  exit 3
fi
cd "$ROOT"
exec "$ROOT/.venv/bin/python" -m uvicorn backend.services.formula_worker:app \
  --host 127.0.0.1 --port 18931 --workers 1
