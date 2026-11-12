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
.venv/bin/python scripts/author_kb_batch45.py --check
PYTHONPATH=backend .venv/bin/python -m app.kb_batch45_review --check
PYTHONPATH=backend .venv/bin/python -m app.kb_batch46_review --check
.venv/bin/python scripts/author_kb_batch47.py --check
PYTHONPATH=backend .venv/bin/python -m app.kb_batch47_review --check
.venv/bin/python scripts/author_kb_batch48.py --check
PYTHONPATH=backend .venv/bin/python -m app.kb_batch48_review --check
.venv/bin/python scripts/author_kb_batch49.py --check
PYTHONPATH=backend .venv/bin/python -m app.kb_batch49_review --check
PYTHONPATH=backend .venv/bin/python -m app.kb_batch50_review --check
.venv/bin/python scripts/build_kb_batch51_official_source_gate.py --check
.venv/bin/python scripts/build_kb_batch52_critical_requirement_crosswalk.py --check
.venv/bin/python scripts/build_kb_batch53_cross_page_review.py --check
.venv/bin/python scripts/author_kb_batch54_legacy_scope.py --check
.venv/bin/python scripts/build_kb_batch55_conflict_review.py --check
.venv/bin/python scripts/build_kb_batch56_source_span_review.py --check
.venv/bin/python scripts/build_kb_batch57_source_review.py --check
.venv/bin/python scripts/build_kb_batch58_competency_coverage.py --check
.venv/bin/python scripts/build_kb_batch59_selective_source_review.py --check
.venv/bin/python scripts/author_kb_batch59_selective_assessments.py --check
.venv/bin/python scripts/build_kb_batch60_elective_source_review.py --check
.venv/bin/python scripts/build_kb_batch61_requirement_anchors.py --check
.venv/bin/python scripts/build_kb_batch62_anchor_triage.py --check
.venv/bin/python scripts/build_kb_batch63_atom_context.py --check
.venv/bin/python scripts/validate_kb_batch63_risk_lessons.py --check
.venv/bin/python scripts/build_kb_batch64_deep_competency.py --check --verify-local
.venv/bin/python scripts/build_kb_batch65_substantive_lessons.py --check --verify-local
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch66_competency_evidence.py --check
.venv/bin/python scripts/build_kb_batch67_clause_review.py --check --verify-local
.venv/bin/python scripts/build_kb_batch68_counterparts.py --check --verify-local
.venv/bin/python scripts/build_kb_batch69_remaining.py --check --verify-local
.venv/bin/python scripts/build_kb_batch70_conflict_review.py --check
.venv/bin/python scripts/build_kb_batch71_modelling.py --check
.venv/bin/python scripts/build_kb_batch72_independent_evidence.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch73_page_partition.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch74_unmarked_review.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch74_geometry_theorems.py --check
.venv/bin/python scripts/build_kb_batch74_page35_visual.py --check --verify-local-image
.venv/bin/python scripts/build_kb_batch75_clause_splits.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch75_lessons.py --check
.venv/bin/python scripts/build_kb_batch76_equivalence.py --check
.venv/bin/python scripts/build_kb_batch76_eight_lessons.py --check
.venv/bin/python scripts/build_kb_batch76_progress.py --check
.venv/bin/python scripts/build_kb_batch77_missing_lessons.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch78_proof_review.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch78_scope_graph.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch79_proof_conditions.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch80_eight_cards.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch80_review_queue.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch81_twelve_cards.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch81_risk_census.py --check
.venv/bin/python scripts/build_kb_batch81_semantic_triage.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch82_conflict_evidence.py --check
.venv/bin/python scripts/build_kb_batch83_semantic_coverage.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch84_semantic_review.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch84_math_cards.py --check
.venv/bin/python scripts/build_kb_batch85_semantic_review.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch85_p0_history.py --check
.venv/bin/python scripts/build_kb_batch86_semantic_review.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch86_p0_reviews.py --check
.venv/bin/python scripts/build_kb_batch87_semantic_review.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch87_math_lessons.py --check
.venv/bin/python scripts/build_kb_batch87_candidate_census.py --check
.venv/bin/python scripts/build_kb_batch88_relations.py --check
.venv/bin/python scripts/build_kb_batch89_proofs_and_scope.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch90_relations.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch91_source_lessons.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch92_relations.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch93_candidate_triage.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch94_deep_scope.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch95_depth.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch96_depth.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch96_candidate_matrix.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch97_depth.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch97_candidate_matrix.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch98_depth.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch98_scope_matrix.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch99_scope_matrix.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch99_seven_track_guard.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch99_prerequisite_gap.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch100_depth.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch100_coverage.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch101_review_queue.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch101_math_pairs.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch101_coverage.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch102_math_pairs.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch103_math_pairs.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch104_deep.py --check
.venv/bin/python scripts/build_kb_batch104_source_structure.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch105_crosspage_atoms.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch106_scope_conditions.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch106_deep.py --check
.venv/bin/python scripts/build_kb_batch107_source.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch108_scope.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch108_lessons.py --check
.venv/bin/python scripts/build_kb_batch109_scope.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch109_lessons.py --check
.venv/bin/python scripts/build_kb_batch110_scope.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch110_lessons.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch110_coverage.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch111.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch107_lessons.py --check
echo "[1/4] Backend regression tests"
(cd backend && PYTHONPATH=.:.. ../.venv/bin/python -m pytest -q)
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
