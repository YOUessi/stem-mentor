#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [[ ! -x .venv/bin/python ]]; then
  echo "Missing Mac virtual environment. Set it up using the README instructions." >&2
  exit 2
fi
echo "[0/4] Batch24+25 source/P0/math/review guards"
.venv/bin/python scripts/author_kb_batch24.py --check
.venv/bin/python scripts/build_kb_batch24_scope.py --check
.venv/bin/python scripts/build_kb_batch24_integrity.py --check
.venv/bin/python scripts/build_kb_batch24_progress.py --check
.venv/bin/python scripts/build_kb_batch25_scope_queue.py --check
.venv/bin/python scripts/build_kb_batch25_risk_triage.py --check
.venv/bin/python scripts/build_kb_batch25_content_readiness.py --check
.venv/bin/python scripts/build_kb_batch26_source_reextract.py --check
.venv/bin/python scripts/build_kb_batch26_graph_progress.py --check
.venv/bin/python scripts/build_kb_batch28_p0_evidence.py --check
.venv/bin/python scripts/build_kb_batch29_p0_evidence.py --check
.venv/bin/python scripts/build_kb_batch30_p0_audit.py --check
.venv/bin/python scripts/build_kb_batch30_k00_page52.py --check
.venv/bin/python scripts/build_kb_batch31_atomic_core.py --check
.venv/bin/python scripts/build_kb_batch31_graph.py --check
.venv/bin/python scripts/build_kb_batch32_source_atoms.py --check
.venv/bin/python scripts/build_kb_batch32_math_links.py --check
.venv/bin/python scripts/build_kb_batch33_elective_scope.py --check
.venv/bin/python scripts/build_kb_batch33_draft_crosswalk.py --check
.venv/bin/python scripts/build_kb_batch33_math_finite_audit.py --check
.venv/bin/python scripts/build_kb_batch34_editorial_review.py --check
.venv/bin/python scripts/build_kb_batch35_editorial_review.py --check
.venv/bin/python scripts/build_kb_batch36_legacy_scope_review.py --check
.venv/bin/python scripts/author_kb_batch37_scope.py --check
.venv/bin/python scripts/author_kb_batch38_partial.py --check
.venv/bin/python scripts/author_kb_batch39_remaining.py --check
.venv/bin/python scripts/build_kb_batch40_official_clauses.py --check
PYTHONPATH=backend .venv/bin/python -m app.kb_batch41_core_review --check
PYTHONPATH=backend .venv/bin/python -m app.kb_batch42_review --check
PYTHONPATH=backend .venv/bin/python -m app.kb_batch42_coverage --check
.venv/bin/python scripts/build_kb_batch43_seed.py --check
PYTHONPATH=backend .venv/bin/python -m app.kb_batch43_review --check
PYTHONPATH=backend .venv/bin/python -m app.kb_batch44_review --check
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
