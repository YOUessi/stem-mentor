"""Batch121 source-locked editorial lineage, exact lesson examples and fail-closed gates."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch121_editorial_scope as b
import build_kb_batch121_deep_lessons as depth
from kb_batch121_editorial_catalog import ROWS
from app.deep_knowledge import public_summary

DATA=json.loads(b.OUT.read_text(encoding="utf-8"))
QUEUE=json.loads(b.QUEUE.read_text(encoding="utf-8"))
COVER=json.loads(b.COVER.read_text(encoding="utf-8"))
LESSONS=json.loads(depth.OUT.read_text(encoding="utf-8"))
MATH=json.loads(depth.ORACLE.read_text(encoding="utf-8"))
LOCKS=json.loads(b.LOCKS.read_text(encoding="utf-8"))

@pytest.mark.parametrize("row",DATA["candidates"],ids=lambda x:x["local_key"])
def test_source_pinned_original_math_editorials_stay_unapproved(row):
    assert row["review_status"]=="REVIEW_PENDING"
    assert row["teacher_evidence"] is None and row["official_atom_id"] is None
    assert row["official_atom_certified"] is False
    assert row["student_authoritative"] is False and row["proof_verification"]=="UNVERIFIED"
    assert row["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert row["source"]["source_span_sha256"]==LOCKS[row["local_key"]]
    assert len(row["applicability"])>=22 and len(row["invalid_use"])>=20
    assert row["source"]["matching_layout_cues"]
    assert row["source"]["original_pdf_sha256"]==b.evidence.PDF_SHA

@pytest.mark.parametrize("row",QUEUE,ids=lambda x:x["cue_id"])
def test_every_cue_has_exactly_one_auditable_status_without_forged_approval(row):
    assert row["disposition"] in ("EDITORIAL_CANDIDATE_LINKED","UNRESOLVED_EDITORIAL_SPLIT_OR_NON_ATOM")
    assert bool(row["linked_editorial_candidate_ids"])==(row["disposition"]=="EDITORIAL_CANDIDATE_LINKED")
    assert row["official_atom_id"] is None
    assert row["teacher_approved"] is False and row["student_authoritative"] is False
    assert len(row["source_line_sha256"])==64
    assert row["course_track"] in set(b.TRACKS)|{"ELECTIVE_UNASSIGNED"}

@pytest.mark.parametrize("track",list(b.TRACKS)+["ELECTIVE_UNASSIGNED"])
def test_no_track_infers_official_denominator(track):
    row=COVER["per_track"][track]
    assert row["official_atom_denominator"] is None and row["official_coverage_fraction"] is None
    assert row["source_cues_linked"]+row["source_cues_unresolved"]==row["source_layout_cues"]
    assert row["teacher_approved"]==row["student_authoritative"]==0

@pytest.mark.parametrize("row",LESSONS,ids=lambda x:x["id"])
def test_deep_original_lesson_has_all_teaching_components_and_no_leaks(row):
    assert row["teacher_review_status"]=="REVIEW_PENDING"
    assert row["teacher_evidence"] is None and row["student_authoritative"] is False
    assert row["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert row["proof_step_machine_certified"] is False
    assert len(row["reasoned_steps"])>=3 and len(row["teacher_examples"])==2
    assert len(row["student_hint_ladder"])==3
    assert row["formal_definition_or_statement"] and row["symbols"] and row["applicability"]
    assert row["why_it_works"] and row["boundary_and_counterexample"] and row["typical_wrong_solution"]
    assert row["why_wrong"] and row["near_transfer"] and row["far_transfer"]

@pytest.mark.parametrize("attack",[
 lambda d:d.update(official_atom_census_complete=True),
 lambda d:d.update(official_atom_total_denominator=143),
 lambda d:d.update(teacher_approved_count=1),
 lambda d:d.update(student_authoritative_count=1),
 lambda d:d.update(source_text_committed=True),
 lambda d:d.update(new_candidate_count=31),
 lambda d:d.update(cumulative_editorial_candidate_count=405),
 lambda d:d["candidates"][0].update(review_status="APPROVED"),
 lambda d:d["candidates"][0].update(teacher_evidence={"reviewer":"fake"}),
 lambda d:d["candidates"][0].update(student_authoritative=True),
 lambda d:d["candidates"][0].update(proof_verification="CERTIFIED"),
 lambda d:d["candidates"][0].update(official_atom_certified=True),
 lambda d:d["candidates"][0].update(teacher_solution_visibility="STUDENT"),
 lambda d:d["candidates"][0].update(course_track="ELECTIVE_E"),
 lambda d:d["candidates"][0].update(prerequisite_candidate_ids=["unknown"]),
 lambda d:d["candidates"][0].update(applicability="no math"),
 lambda d:d["candidates"][0].update(invalid_use="no counterexample"),
 lambda d:d["candidates"][0]["source"].update(printed_page=73),
 lambda d:d["candidates"][0]["source"].update(start_line=2),
 lambda d:d["candidates"][0]["source"].update(source_span_sha256="0"*64),
 lambda d:d["candidates"][0]["source"].update(matching_layout_cues=[]),
 lambda d:d["candidates"].append(copy.deepcopy(d["candidates"][0])),
],ids=lambda f:f.__code__.co_firstlineno)
def test_forged_scope_or_approval_rejected(attack):
    bad=copy.deepcopy(DATA)
    attack(bad)
    with pytest.raises(ValueError):
        b.validate(bad)

@pytest.mark.parametrize("edit",[
 lambda d:d[0].update(official_atom_id="FAKE"),
 lambda d:d[0].update(student_authoritative=True),
 lambda d:d[0].update(teacher_approved=True),
 lambda d:d[0].update(disposition="EDITORIAL_CANDIDATE_LINKED"),
 lambda d:d[0].update(cue_id="syllabus-cue-fake"),
 lambda d:d[0].update(source_line_sha256="bad"),
 lambda d:d.pop(),
])
def test_cue_disposition_data_cannot_be_silently_rewritten(edit):
    bad=copy.deepcopy(QUEUE)
    edit(bad)
    with pytest.raises(ValueError):
        b.validate_queue(DATA,bad,COVER)

@pytest.mark.parametrize("edit",[
 lambda d:d[0].update(teacher_review_status="APPROVED"),
 lambda d:d[0].update(teacher_evidence={"name":"fake"}),
 lambda d:d[0].update(student_authoritative=True),
 lambda d:d[0].update(teacher_solution_visibility="STUDENT"),
 lambda d:d[0].update(proof_step_machine_certified=True),
 lambda d:d[0].update(math_example_exact_checks_passed=999),
 lambda d:d[0].update(boundary_and_counterexample=""),
 lambda d:d[0].update(formal_definition_or_statement="false"),
 lambda d:d[0].update(candidate_id="unknown"),
 lambda d:d[0].update(teacher_examples=[]),
])
def test_forged_proof_and_student_authority_rejected(edit):
    bad=copy.deepcopy(LESSONS)
    edit(bad)
    with pytest.raises(ValueError):
        depth.validate(bad)

@pytest.mark.parametrize("case",sorted(MATH["details_by_candidate"]))
def test_independent_exact_math_evaluation_against_frozen_oracles(case):
    assert depth.oracle()["details_by_candidate"][case]=={"exact_worked_cases":2,"exact_negative_cases":1}
    assert MATH["general_formal_proofs_certified"]==0
    assert MATH["student_free_text_verified"] is False

def test_census_coverage_and_all_generated_artifacts_deterministic():
    assert b.validate(DATA)
    assert b.validate_queue(DATA,QUEUE,COVER)
    assert depth.validate(LESSONS)
    assert len(ROWS)==30 and len(LESSONS)==8
    assert b.build()==DATA and b.review_queue(DATA)==QUEUE and b.coverage(DATA,QUEUE)==COVER
    assert depth.build()==LESSONS and depth.oracle()==MATH
    assert len(QUEUE)==405 and COVER["cues_linked"]==174 and COVER["cues_unresolved"]==231
    assert COVER["cumulative_editorial_candidates"]==143
    assert all(x["official_atom_denominator"] is None for x in COVER["per_track"].values())
    assert b.REPORT.read_text(encoding="utf-8")==b.render(DATA,QUEUE,COVER)
    assert depth.REPORT.read_text(encoding="utf-8")==depth.render(LESSONS)
    assert MATH["exact_worked_example_checks_passed"]==16
    assert MATH["boundary_negative_checks_passed"]==8

def test_student_retrieval_not_promoted_by_editorial_drafts():
    pub=json.dumps(public_summary(),ensure_ascii=False)
    assert "hs-semantic-pilot-121" not in pub
    assert "kb_batch121_eight_depth_lessons" not in pub
    assert "kb_batch121_semantic_editorials" not in pub
