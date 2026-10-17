#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [[ ! -x .venv/bin/python ]]; then
  echo "Missing Mac virtual environment. Set it up using the README instructions." >&2
  exit 2
fi
echo "[1/4] Backend regression tests"
(cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest -q)
echo "[2/4] Simulated tutor policy"
(cd backend && PYTHONPATH=. ../.venv/bin/python evaluate_policy.py)
echo "[3/4] Structured retrieval hard negatives"
(cd backend && PYTHONPATH=. ../.venv/bin/python evaluate_v05.py)
echo "[4/4] Frontend JavaScript syntax"
node --check apps/web/app.js
node --check apps/web/study_tools.js
node --check apps/web/study_tools.js
echo "Offline macOS simulation checks complete; no model API used."
