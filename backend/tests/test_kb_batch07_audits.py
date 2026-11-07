"""Batch07: status-aware syllabus and editor-only proof risk audit regressions."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.build_kb_batch07_audit import build, sha
from app.deep_knowledge import lessons
from app.deep_retrieval import EditorOnlyError, editor_draft_search, student_evidence_lookup

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

ELECTIVES = read("curriculum/highschool_math/elective_track_crosswalk_batch07.json")
CONFLICTS = read("docs/evaluation/KB_CONFLICT_RISK_BATCH07.json")
PROOFS = read("docs/evaluation/KB_PROOF_OBLIGATIONS_BATCH07.json")
EXPECTED_TRACKS = ["ELECTIVE_A", "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E"]

def test_reproducible_reports_and_full_schema():
    result = subprocess.run([sys.executable, "scripts/build_kb_batch07_audit.py", "--check"],
        cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr + result.stdout
    assert len(build()) == 3

def test_elective_tracks_not_silently_marked_completed():
    s = ELECTIVES["summary"]
    assert s == {
        "elective_tracks":5, "high_level_theme_slots":18,
        "atomic_subtopics_verified":0, "legacy_extension_topics_without_explicit_track":7,
        "teacher_approved_elective_lessons":0, "mapped_draft_links":0,
    }
    assert ELECTIVES["tracks"] == EXPECTED_TRACKS
    assert all(x["status"] == "ELECTIVE_TRACK_NOT_ASSIGNED"
               for x in ELECTIVES["unassigned_legacy_extension_topics"])

@pytest.mark.parametrize("row",ELECTIVES["theme_candidates"],
                         ids=lambda x:x["key"])
def test_each_track_theme_is_only_a_slot_not_a_completed_lesson(row):
    assert row["track"] in EXPECTED_TRACKS
    assert row["mapping_status"] == "HIGH_LEVEL_THEME_ONLY_NOT_ATOMIC"
    assert row["human_review"] == "PENDING"
    assert row["verified_official_atom_ids"] == []
    assert row["approved_deep_lesson_ids"] == []
    assert row["assigned_legacy_engineering_topic_ids"] == []

def test_legacy_extension_topics_still_no_official_track():
    original = read("curriculum/highschool_math/curriculum_map.json")["coverage"]
    raw = {x["id"] for x in original if x["level"] == "选修拓展" and not x.get("elective_track")}
    listed = {x["id"] for x in ELECTIVES["unassigned_legacy_extension_topics"]}
    assert raw == listed and len(raw) == 7

def test_all_conflicts_have_unresolved_review_risk_and_independent_sources():
    assert CONFLICTS["summary"]["conflict_count"] == 10
    assert CONFLICTS["summary"]["automatically_resolved"] == 0
    assert CONFLICTS["summary"]["conflicts_with_changed_math_risk_fields"] == 10

@pytest.mark.parametrize("row",CONFLICTS["conflicts"], ids=lambda x:x["id"])
def test_conflict_retains_original_provenance_and_high_risk_differences(row):
    source = read("docs/evaluation/KB_BATCH02_RECONCILIATION.json")
    parent = next(x for x in source["unresolved_conflicts"] if x["id"] == row["id"])
    old = next(x for x in read(parent["existing_source"]) if x["id"] == row["id"])
    new = next(x for x in read(parent["candidate_source"]) if x["id"] == row["id"])
    assert sha(old) == row["active_sha256"]
    assert sha(new) == row["candidate_sha256"]
    assert row["decision"] == "HOLD_BOTH_SOURCE_VERSIONS"
    assert row["evidence_status"] == "MATH_NOT_INDEPENDENTLY_ADJUDICATED"
    assert row["mathematical_risk_fields"]
    assert row["review_hint"] and len(row["review_hint"]) > 18
    assert row["candidate_boundaries"] == new["boundaries"]
    assert row["active_boundaries"] == old["boundaries"]

def test_all_current_drafts_have_explicit_unverified_step_obligations():
    s = PROOFS["summary"]
    from app.deep_knowledge import lessons
    docs=lessons()
    # Historical 451 unverified obligations belong to 224 frozen drafts.
    # New Batch21 proof steps are independently versioned in the 474-step union.
    from scripts.build_kb_batch21_proof_union import build as build_proof_union
    union = build_proof_union()
    new_ids = {r["lesson_id"] for r in union["new_proof_review_queue"]}
    assert s["deep_draft_lessons"] == 224
    new_lesson_ids = {r["id"] for r in json.loads((ROOT / "knowledge/deep/v1/elective_gap_batch21.json").read_text(encoding="utf-8"))}
    batch22_ids = {r["id"] for r in json.loads((ROOT / "knowledge/deep/v1/elective_gap_batch22.json").read_text(encoding="utf-8"))}
    from scripts.build_kb_batch22_proof_and_scope import build as build_current_review
    latest_proofs, _ = build_current_review()
    latest = json.loads(latest_proofs)
    assert s["deep_draft_lessons"] + 11 == union["summary"]["current_draft_lessons"] == 235  # frozen Batch21 report
    assert len(docs) == latest["summary"]["current_draft_lessons"] == 247
    assert s["theorems"] + sum(x.kind == "theorem" for x in docs
          if x.id in new_lesson_ids | batch22_ids) == sum(x.kind == "theorem" for x in docs)
    assert s["proof_step_obligations_not_formally_verified"] == 451
    assert (s["proof_step_obligations_not_formally_verified"]
            + len(union["new_proof_review_queue"])
            + len(latest["new_review_obligations"])
            == sum(len(x.proof_steps) for x in docs) == 497)
    # Historical, Batch21 and Batch22 reviews remain separate, with no automatic certification.
    assert new_ids <= new_lesson_ids
    assert {x["id"] for x in PROOFS["lessons"]} | new_lesson_ids | batch22_ids == {x.id for x in docs}
    assert s["existing_supporting_oracles_linked"] >= 48
    assert s["theorems_with_whole_proof_certification"] == 0
    assert s["teacher_approved"] == 0
    assert s["student_solution_steps_verified"] == 0
    assert len(PROOFS["lessons"]) == 224
    assert not any(x["formal_natural_language_proof_verified"] for x in PROOFS["lessons"])

@pytest.mark.parametrize("row",PROOFS["lessons"], ids=lambda x:x["id"])
def test_each_lesson_requires_real_review_and_does_not_claim_full_proof(row):
    assert row["human_review"] == "PENDING"
    assert row["review_status"] == "REVIEW_PENDING"
    assert row["math_truth_status"] == "NOT_CERTIFIED"
    assert row["teacher_solution_visibility"] == "TEACHER_ONLY"
    assert row["counterexample_count"] >= 1
    assert row["worked_example_count"] >= 2
    if row["kind"] == "theorem":
        assert len(row["theorem_assumptions"]) >= 1
        assert len(row["proof_step_obligations"]) >= 3
        assert all(x["status"] == "NOT_FORMALLY_VERIFIED" and
                   x["claim"] and x["reason"] for x in row["proof_step_obligations"])
    else:
        assert not row["proof_step_obligations"] or row["kind"]=="method"

def test_student_evidence_and_external_routes_remain_fail_closed():
    from app.main import app
    for query in ("微积分", "证明", "正弦定理", "f(x)"):
        d = student_evidence_lookup(query)
        assert d["status"] == "NO_APPROVED_EVIDENCE"
        assert d["candidates"] == [] and not d["teacher_solution_exposed"]
        with pytest.raises(EditorOnlyError):
            editor_draft_search(query)
    for route in app.routes:
        assert not ("editor" in route.path or "/proof-obligation" in route.path or
                    "/elective-track" in route.path)

def test_without_schemas_even_candidate_review_is_never_authentication():
    from app.deep_knowledge import DeepLesson
    original = next(x for x in lessons() if x.kind == "theorem")
    payload = original.model_dump(mode="json")
    payload["review"] = {"status":"APPROVED",
        "reviewer_id":"fake", "reviewed_at":"2026-11-03",
        "review_record":"synthetic"}
    with pytest.raises(ValueError, match="disabled"):
        DeepLesson.model_validate(payload)
