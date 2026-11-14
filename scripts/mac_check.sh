#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [[ ! -x .venv/bin/python ]]; then
  echo "Missing Mac virtual environment. Set it up using the README instructions." >&2
  exit 2
fi
# Rebuild original Mac-only PDFKit evidence when volatile /private/tmp is cleared
# (e.g. reboot). Never log or commit copyrighted syllabus passages.
SOURCE_SCRATCH_MISSING=0
for page in {13..73}; do
  if [[ ! -s "/private/tmp/kb56_page_${page}.txt" ]]; then
    SOURCE_SCRATCH_MISSING=1
    break
  fi
done
if [[ ! -s /private/tmp/kb51_official_page_35.png ]]; then
  SOURCE_SCRATCH_MISSING=1
fi
if [[ "$SOURCE_SCRATCH_MISSING" == 1 ]]; then
  PDF_SOURCE="${STEM_MATH_OFFICIAL_PDF:-$HOME/Library/Application Support/STEMMentor/sources/official_math_2020.pdf}"
  if [[ ! -f "$PDF_SOURCE" ]]; then
    echo "Pinned official PDF missing: $PDF_SOURCE. Set STEM_MATH_OFFICIAL_PDF to a locally authorized copy." >&2
    exit 12
  fi
  swift scripts/kb_mac_restore_pdfkit_source.swift "$PDF_SOURCE" \
    curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json /private/tmp
fi
# Verify all 188 physical PDF pages against the pinned licensed original, not
# only the previous 61-page excerpt. No source text is saved or committed.
KB116_PDF="${STEM_MATH_OFFICIAL_PDF:-$HOME/Library/Caches/stem-mentor-source-review/highschool_math_standard_2020.pdf}"
KB116_TMP="$(mktemp /private/tmp/stem-kb116-full-XXXXXX)"
if ! swift scripts/kb_batch116_full_pdf_manifest.swift "$KB116_PDF" "$KB116_TMP" ||
   ! cmp -s "$KB116_TMP" docs/evaluation/KB_BATCH116_FULL_PDF_FINGERPRINTS.json; then
  rm -f "$KB116_TMP"
  echo "Batch116 complete-source PDFKit manifest mismatch or missing licensed original" >&2
  exit 13
fi
rm -f "$KB116_TMP"
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
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch112.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch113.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch114.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch115.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch116_inventory.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch116_condition_audit.py --check
.venv/bin/python scripts/build_kb_batch117.py --check
.venv/bin/python -m pytest -q tests/test_kb_batch117.py
.venv/bin/python scripts/build_kb_batch117_scope_segments.py --check
.venv/bin/python -m pytest -q tests/test_kb_batch117_example_oracles.py tests/test_kb_batch117_scope_segments.py
.venv/bin/python scripts/build_kb_batch118_source_atom_ledger.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch118_lessons.py --check
.venv/bin/python -m pytest -q tests/test_kb_batch118.py tests/test_kb_batch118_math_oracles.py
.venv/bin/python scripts/build_kb_batch119_semantic_pilot.py --check --verify-local-source
.venv/bin/python -m pytest -q tests/test_kb_batch119_semantic_pilot.py
.venv/bin/python scripts/build_kb_batch119_proof_reviews.py --check
.venv/bin/python -m pytest -q tests/test_kb_batch119_proof_reviews.py
.venv/bin/python scripts/build_kb_batch120_semantic_expansion.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch120_math_oracles.py --check
.venv/bin/python -m pytest -q tests/test_kb_batch120_semantic_expansion.py
.venv/bin/python scripts/build_kb_batch120_proof_lessons.py --check
.venv/bin/python scripts/build_kb_batch121_editorial_scope.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch121_deep_lessons.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch121_scope_and_lessons.py
.venv/bin/python scripts/build_kb_batch122_semantic_census.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch122_depth.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch122_scope_depth_math.py
.venv/bin/python scripts/build_kb_batch123_semantic_census.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch123_depth.py --check
.venv/bin/python scripts/build_kb_batch124_scope.py --check --verify-local-source
.venv/bin/python scripts/build_kb_batch124_depth.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch124_scope_depth_math.py
# Batch125: entire historical provenance grade, six unlinked numbered
# clauses, and all ten unresolved mathematical conflicts. Never approve here.
.venv/bin/python scripts/build_kb_batch125_provenance.py --check
.venv/bin/python scripts/build_kb_batch125_math_risk.py --check
.venv/bin/python scripts/build_kb_batch125_six_requirements.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch125_provenance_math.py tests/test_kb_batch125_six_clauses.py
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch123_scope_depth_math.py
.venv/bin/python -m pytest -q tests/test_kb_batch120_proof_lessons.py
PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch107_lessons.py --check
# Batch126: 26 source-locked context interpretations, 6 unlinked numbered cues,
# 12 finite exact witnesses. No auto-certified knowledge or official denominator.
.venv/bin/python scripts/build_kb_batch126_context_evidence.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch126_context_attestation.py
# Batch127: 28 seven-track source dossiers, eight full pending lessons, 32 finite oracles.
.venv/bin/python scripts/build_kb_batch127_source_review.py --check
.venv/bin/python scripts/build_kb_batch127_deep_lessons.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch127_source_lessons.py
# Batch128: 28 additional exact-source semantic interpretations / 56 provisional splits;
# 20 new P0 historical proof guard cards (40 finite exact checks). No auto approval.
.venv/bin/python scripts/build_kb_batch128_source_ledger.py --check
.venv/bin/python scripts/build_kb_batch128_p0_proof_guards.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch128_source_proof.py
# Batch130: original private PDF line replay + 53 contextual cases + eight teacher manuscripts.
.venv/bin/python scripts/build_kb_batch130_core_source.py --check
.venv/bin/python scripts/build_kb_batch130_deep_lessons.py --check
.venv/bin/python scripts/check_kb_batch130_offline.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch130_scope_lessons.py
# Batch131: rehash original 43 PDFKit spans on Mac, replay offline trust boundary and exact math.
.venv/bin/python scripts/build_kb_batch131_contexts.py --check-mac
.venv/bin/python scripts/build_kb_batch131_contexts.py --check-offline
.venv/bin/python scripts/check_kb_batch131_exact_cases.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch131_context_math.py
# Batch132: all 39 remaining elective historic context reviews (Mac original PDF),
# eight full elective manuscripts, 16 exact teacher examples and eight negative cases.
.venv/bin/python scripts/build_kb_batch132_electives.py --check-mac
.venv/bin/python scripts/build_kb_batch132_electives.py --check-offline
.venv/bin/python scripts/build_kb_batch132_lessons.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch132_electives.py
# Batch133 independently checks source PDFKit on Mac and bounded official atomization only.
.venv/bin/python scripts/build_kb_batch133_atomization.py --check-mac
.venv/bin/python scripts/build_kb_batch133_atomization.py --check-offline
.venv/bin/python scripts/build_kb_batch133_lessons.py --check
.venv/bin/python scripts/check_kb_batch133_math.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch133_atomization.py
# Batch134: Mac original PDF verification remains in Batch133 upstream replay.
# These new checks enforce source-locked DAG, teacher-only eight lessons and math oracle.
.venv/bin/python scripts/build_kb_batch134_graph.py --check
.venv/bin/python scripts/build_kb_batch134_lessons.py --check
.venv/bin/python scripts/check_kb_batch134_math.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch134_proof_graph.py
# Batch135: eight additional original teacher drafts, 24 finite and four symbolic
# subclaim checks, and a 22-document review-only FTS/API exposure contract.
.venv/bin/python scripts/build_kb_batch135_lessons.py --check
.venv/bin/python scripts/check_kb_batch135_math.py --check
.venv/bin/python scripts/build_kb_batch135_coverage.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch135_integrated.py tests/test_kb_batch135_coverage.py
.venv/bin/python scripts/build_kb_batch136_lessons.py --check
.venv/bin/python scripts/check_kb_batch136_math.py --check
.venv/bin/python scripts/build_kb_batch136_coverage.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch136_pilot.py
# Batch137: complete all seven remaining bounded editorial manuscripts, exact oracle, 41-draft privacy ledger.
.venv/bin/python scripts/build_kb_batch137_lessons.py --check
.venv/bin/python scripts/check_kb_batch137_math.py --check
.venv/bin/python scripts/build_kb_batch137_coverage.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch137_closure.py
.venv/bin/python scripts/build_kb_batch138_electives.py --check-mac
.venv/bin/python scripts/check_kb_batch138_math.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch138_electives.py
# Batch139: eight more original core/selective/A teacher drafts, 32 independent finite exact cases,
# Mac-only source PDFKit re-attestation, fail-closed 57-manuscript editorial search and student privacy.
.venv/bin/python scripts/build_kb_batch139_core.py --check-mac
.venv/bin/python scripts/check_kb_batch139_math.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch139_core.py
# Batch140: 24 historical P0 proof-step review cards, source SHA locks and 48 finite exact checks.
# Original P0 proof steps remain NOT_FORMALLY_VERIFIED and student evidence denied.
.venv/bin/python scripts/build_kb_batch140_proof_guards.py --check
.venv/bin/python scripts/check_kb_batch140_math.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch140_p0_proof_guards.py
# Batch141: migrate all 47 remaining P0 to source-fingerprinted teacher-pending cards.
# 12 selected mathematical obligations receive 24 independent finite SymPy cases.
.venv/bin/python scripts/build_kb_batch141_lineage.py --check
.venv/bin/python scripts/check_kb_batch141_math.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch141_p0_lineage.py
# Batch142: finish 35 remaining KB141 source-locked P0 finite math obligations,
# expose seven-track UNKNOWN denominator accounting and student fail-closed guards.
.venv/bin/python scripts/check_kb_batch142_remaining_oracles.py --check
.venv/bin/python scripts/build_kb_batch142_ledger.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch142_p0_exact_scope.py
# Batch143: eight original cross-domain teacher-only full manuscripts; Mac-only original PDF line replay,
# exact finite oracle, seven-track truthful denominator, gated FTS and API leak regression.
.venv/bin/python scripts/build_kb_batch143_lessons.py --check-mac
.venv/bin/python scripts/check_kb_batch143_math.py --check
.venv/bin/python scripts/build_kb_batch143_source_gap.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch143_eight_math_integrity.py tests/test_kb_batch143_source_to_depth_gaps.py
# Batch144: ten source-locked, seven-track teacher-only manuscripts and independent math guards.
.venv/bin/python scripts/build_kb_batch144_lessons.py --check-mac
.venv/bin/python scripts/check_kb_batch144_math.py --check
.venv/bin/python scripts/build_kb_batch144_crosswalk.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch144_seven_track.py
# Batch146: ten original source-locked seven-track lessons; 40 exact bounded
# tests and 85 draft safe editor index, 44/239 historical editorial matches.
.venv/bin/python scripts/build_kb_batch146_lessons.py --check-mac
.venv/bin/python scripts/check_kb_batch146_math.py --check
.venv/bin/python scripts/build_kb_batch146_crosswalk.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch146_math_depth.py
# Batch147: ten source-hashed original math lessons, exact finite oracles and privacy guard.
.venv/bin/python scripts/build_kb_batch147_lessons.py --check-mac
.venv/bin/python scripts/check_kb_batch147_math.py --check
.venv/bin/python scripts/build_kb_batch147_crosswalk.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch147_math_depth.py
.venv/bin/python scripts/audit_kb_batch147_source_edges.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch147_source_edges.py
# Batch148: full numbered source-marker audit (no false official atom denominator)
# and all ten unresolved mathematical conflict families with finite symbolic checks.
.venv/bin/python scripts/build_kb_batch148_official_clause_gate.py --check
.venv/bin/python scripts/review_kb_batch148_conflicts.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch148_source_math_gate.py
# Batch149: 10 original source-hashed deep lessons and no teacher-approval spoofing;
# 40 independent finite math guards, SHA-only D/E unnumbered candidate queue,
# 64/239 editorial-linked pending drafts, and 105 local editor-only FTS entries.
.venv/bin/python scripts/build_kb_batch149_lessons.py --check-mac
.venv/bin/python scripts/check_kb_batch149_math.py --check
.venv/bin/python scripts/build_kb_batch149_unnumbered_elective_queue.py --check-mac
.venv/bin/python scripts/build_kb_batch149_crosswalk.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch149_depth_scope.py
# Batch150: Mac-only original 122-line PDFKit SHA replay and C/D/E source boundary
# (official atom denominators remain unknown; provisional topics are NOT lessons).
.venv/bin/python scripts/build_kb_batch150_de_boundary.py --check --mac-replay
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch150_de_boundary.py
echo "[1/4] Backend regression tests"
.venv/bin/python scripts/build_kb_batch129_scope_reviews.py --check
.venv/bin/python scripts/build_kb_batch129_lessons.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch129_scope_lessons.py

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


# Batch151: ten additional source-locked teacher-only lessons and exact finite mathematical guards.
.venv/bin/python scripts/build_kb_batch151_lessons.py --check-mac
.venv/bin/python scripts/build_kb_batch151_crosswalk.py --check
.venv/bin/python scripts/check_kb_batch151_math.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch151_depth_integrity.py

# Batch152: ten Mac PDFKit source-hashed teacher-only lesson manuscripts, 40 exact
# bounded math witnesses, C/D/E unapproved proposal overlap review, editor-only FTS.
.venv/bin/python scripts/author_kb_batch152_data.py --check
.venv/bin/python scripts/build_kb_batch152_lessons.py --check-mac
.venv/bin/python scripts/build_kb_batch152_crosswalk.py --check
.venv/bin/python scripts/build_kb_batch152_semantic_gate.py --check
.venv/bin/python scripts/check_kb_batch152_math.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch152_integration.py

# Batch153: Mac-source SHA rehash, ten source-locked original rigorous teacher-only
# manuscripts, 40 independent finite SymPy witnesses and non-leaking editor FTS.
.venv/bin/python scripts/author_kb_batch153_data.py --check
.venv/bin/python scripts/build_kb_batch153_lessons.py --check-mac
.venv/bin/python scripts/build_kb_batch153_crosswalk.py --check
.venv/bin/python scripts/check_kb_batch153_math.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch153_integrity.py

# Batch154: all 61 source pages / 315 markers / 122 CDE lines / 32 proposals.
.venv/bin/python scripts/build_kb_batch154_scope_graph.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch154_scope_graph.py
# Batch154: 10 original Mac source-lock teacher drafts and independent 40 exact math guards.
.venv/bin/python scripts/author_kb_batch154_data.py --check
.venv/bin/python scripts/build_kb_batch154_lessons.py --check-mac
.venv/bin/python scripts/build_kb_batch154_crosswalk.py --check
.venv/bin/python scripts/check_kb_batch154_math.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch154_math_depth.py

# Batch154: replay archived real Mac stdout+exit SHA and reject evidence forgery.
.venv/bin/python scripts/build_kb_batch154_execution_manifest.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch154_archived_evidence.py

# Batch155: 315 layout marker + 32 unnumbered CDE obligations across 61 pages,
# 239 editorial leads/145 pending drafts; fail-closed review and 30 exact guards.
.venv/bin/python scripts/build_kb_batch155_review_matrix.py --check
.venv/bin/python scripts/check_kb_batch155_exact_cases.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch155_scope_math_integrity.py

# Batch155: 8 previously source-line-unlocked candidates rehashed against Mac original,
# reconcile 145 manuscript schema/provenance fields without certifying math or teacher approval.
.venv/bin/python scripts/build_kb_batch155_eight_line_locks.py --check-mac
PYTHONPATH=backend .venv/bin/python scripts/audit_kb_batch155_draft_readiness.py --check
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch155_draft_readiness.py
