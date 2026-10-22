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
node --check apps/web/ipad/ink_core.js
node --check apps/web/ipad/storage.js
node --check apps/web/ipad/app.js
node --check apps/web/transfer.js
node --check apps/web/study_tools.js
for module in apps/web/lab/plot2d.js apps/web/lab/triangle.js apps/web/lab/scene3d.js apps/web/lab/exploration_math.js apps/web/lab/explorers2d.js apps/web/lab/sections3d.js apps/web/lab/controller.js; do
  node --check "$module"
done
node --test tests/node/*.test.cjs
echo "Offline macOS simulation checks complete; no model API used."

for module in apps/web/lab/foundations_math.js apps/web/lab/interval_math.js apps/web/lab/foundations2d.js apps/web/lab/numberline.js apps/web/lab/sequences_math.js apps/web/lab/sequence_policy.js apps/web/lab/sequences2d.js apps/web/lab/extrema_math.js apps/web/lab/extrema2d.js apps/web/lab/probability_math.js apps/web/lab/probability2d.js; do
  node --check "$module"
done
