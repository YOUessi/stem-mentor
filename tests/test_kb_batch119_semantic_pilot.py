"""Batch119 semantic candidate integrity, false-certification and exact-math regression."""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch119_semantic_pilot as b
import build_kb_batch118_source_atom_ledger as prev

DATA=json.loads(b.OUT.read_text())
MATH=json.loads(b.MATH.read_text())
COVER=json.loads(b.COVER.read_text())

@pytest.mark.parametrize("row",DATA["candidates"],ids=lambda r:r["local_key"])
def test_lineage_conditions_and_review_status(row):
    s=row["source"]
    prior=json.loads(prev.OUT.read_text())
    page=prior["pages"][s["printed_page"]-13]
    assert s["frozen_page_sha256"]==page["source_page_sha256"]
    assert s["physical_page_index"]==s["printed_page"]+7
    assert s["start_line"]<=s["end_line"]<=page["source_line_count"]
    assert all(prev.track_at(s["printed_page"],line)==row["course_track"]
               for line in range(s["start_line"],s["end_line"]+1))
    assert row["review_status"]=="REVIEW_PENDING"
    assert row["teacher_evidence"] is None and row["official_atom_id"] is None
    assert row["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert row["student_authoritative"] is False
    assert row["proof_verification"]=="UNVERIFIED"
    assert len(row["applicability"])>=7 and len(row["invalid_use"])>=10

@pytest.mark.parametrize("track",b.TRACKS)
def test_track_has_provisional_pilot_not_official_denominator(track):
    t=DATA["by_track"][track]
    assert t["pilot_count"]>0
    assert t["official_atom_denominator"] is None
    assert COVER["official_atom_denominators"][track] is None
    assert not t["whole_track_complete"]
    assert t["teacher_approved"]==0

@pytest.mark.parametrize("damage",[
    lambda d:d.update(official_atom_total_denominator=49),
    lambda d:d.update(official_atom_census_complete=True),
    lambda d:d.update(teacher_approved_count=1),
    lambda d:d.update(student_authoritative_count=1),
    lambda d:d.update(source_text_committed=True),
    lambda d:d.update(source_cues_not_linked=0),
    lambda d:d["by_track"]["ELECTIVE_E"].update(official_atom_denominator=4),
    lambda d:d["by_track"]["COMPULSORY"].update(whole_track_complete=True),
    lambda d:d["candidates"][0].update(official_atom_id="fake"),
    lambda d:d["candidates"][0].update(review_status="APPROVED"),
    lambda d:d["candidates"][0].update(student_authoritative=True),
    lambda d:d["candidates"][0].update(proof_verification="CERTIFIED"),
    lambda d:d["candidates"][0]["source"].update(start_line=999),
    lambda d:d["candidates"][0]["source"].update(source_span_sha256="broken"),
    lambda d:d["candidates"][0]["source"].update(physical_page_index=1),
    lambda d:d["candidates"][0]["source"].update(frozen_page_sha256="0"*64),
    lambda d:d["candidates"][0].update(course_track="ELECTIVE_C"),
    lambda d:d["candidates"][0]["source"].update(matching_layout_cues=["fake"]),
    lambda d:d["candidates"][0].update(prerequisite_candidate_ids=["not-an-atom"]),
    lambda d:d["candidates"][0].update(applicability=""),
    lambda d:d["candidates"][0].update(teacher_solution_visibility="STUDENT"),
    lambda d:d["candidates"][-1].update(elective_e_optional_example=False),
    lambda d:d["candidates"].append(copy.deepcopy(d["candidates"][0])),
])
def test_forged_approvals_invalid_source_and_inflated_counts_fail(damage):
    clone=copy.deepcopy(DATA)
    damage(clone)
    with pytest.raises(ValueError):b.validate(clone)

@pytest.mark.parametrize("case",MATH["case_names"])
def test_independent_finite_case_is_registered_and_not_general_proof(case):
    assert case in b.math_checks()["case_names"]
    assert MATH["formal_general_proofs_certified"]==0
    assert MATH["teacher_approved"]==0
    assert not MATH["student_free_text_verified"]

def test_reproducible_artifacts_and_strict_unreleased_coverage():
    assert b.validate(DATA)
    assert DATA==b.build(use_local=False)
    assert MATH==b.math_checks()
    assert COVER["semantic_pilot_candidates"]==len(DATA["candidates"])==49
    assert sum(COVER["per_track_pilot"].values())==49
    assert DATA["source_cues_linked"]+DATA["source_cues_not_linked"]==405
    assert not COVER["whole_curriculum_completed"]
    assert COVER["teacher_approved"]==COVER["student_authoritative_releases"]==0
    assert b.MD.read_text()==b.markdown(DATA,MATH)

def test_challenge_tutor_never_reads_review_pending_candidate_as_authority():
    from app.deep_knowledge import public_summary
    rendered=json.dumps(public_summary(),ensure_ascii=False)
    assert "hs-semantic-pilot-119" not in rendered
    assert "k00_batch119_semantic_atom_pilot" not in rendered
