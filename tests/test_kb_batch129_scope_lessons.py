"""Batch129 source anchored seven-track deep lesson and review-authority integrity tests."""
from __future__ import annotations
import copy,hashlib,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch129_scope_reviews as src
import build_kb_batch129_lessons as deep
from app.deep_knowledge import public_summary
SOURCE=json.loads(src.OUT.read_text(encoding="utf-8"))
LOCKS=json.loads(src.LOCKS.read_text(encoding="utf-8"))
LESSONS=json.loads(deep.OUT.read_text(encoding="utf-8"))
ORACLES=json.loads(deep.ORACLES.read_text(encoding="utf-8"))

@pytest.mark.parametrize("record",SOURCE["records"],ids=lambda x:x["candidate_id"])
def test_28_syllabus_original_line_fingerprints_on_mac(record):
    key=record["candidate_id"];lock=record["source"];p=lock["page"]
    raw=src.prior.prior.previous.source_pages()[p][lock["start_line"]-1:lock["end_line"]]
    assert len(raw)==len(lock["line_sha256"])
    assert [hashlib.sha256(line.encode()).hexdigest() for line in raw]==lock["line_sha256"]
    assert hashlib.sha256("\n".join(raw).encode()).hexdigest()==lock["span_sha256"]
    assert lock==LOCKS[key]
    assert record["source_pdf_sha256"]==src.prior.prior.provenance.old.previous.base_scope.evidence.PDF_SHA

@pytest.mark.parametrize("record",SOURCE["records"],ids=lambda x:x["candidate_id"])
def test_28_contexts_are_not_teacher_certifications_or_official_atoms(record):
    assert record["teacher_status"]=="REVIEW_PENDING"
    assert record["teacher_signature"] is None and record["official_atom_id"] is None
    assert record["student_authoritative"] is False
    assert record["mathematics_formally_certified"] is False
    assert len(record["editorial_interpretation"])>=28
    assert len(record["outstanding_risk"])>=28
    assert len(record["proposed_teaching_targets"])==2
    for sub in record["proposed_teaching_targets"]:
        assert sub["official_atom_id"] is None
        assert sub["student_authoritative"] is False
        assert sub["teacher_status"]=="REVIEW_PENDING"

@pytest.mark.parametrize("lesson",LESSONS,ids=lambda x:x["candidate_id"])
def test_nine_complete_teacher_only_manuscripts(lesson):
    assert lesson["teacher_review_status"]=="REVIEW_PENDING"
    assert lesson["teacher_review_evidence"] is None
    assert lesson["formal_proof_certified"] is False
    assert lesson["student_authoritative"] is False
    assert lesson["free_student_step_verified"] is False
    assert lesson["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert lesson["candidate_id"] in LOCKS
    assert lesson["source"]==LOCKS[lesson["candidate_id"]]
    assert len(lesson["reasoned_steps"])==3
    assert len(lesson["teacher_examples"])==2
    assert len(lesson["student_hint_ladder"])==3
    for example in lesson["teacher_examples"]:
        assert len(example["steps"])==2
        assert example["answer"] and example["oracle_explanation"]
    assert lesson["near_transfer"] and lesson["far_transfer"]
    assert lesson["invalid_boundary"] and lesson["typical_wrong_solution"]

@pytest.mark.parametrize("lesson",LESSONS,ids=lambda x:x["candidate_id"])
def test_teacher_examples_have_two_independent_math_checks(lesson):
    suff=lesson["candidate_id"].removeprefix("hs-semantic-pilot-")
    assert len(ORACLES["worked_checks"][suff])==2
    assert all(ORACLES["worked_checks"][suff])
    assert ORACLES["invalid_check_results"][suff] is True
    assert ORACLES["cross_check_results"][suff] is True

@pytest.mark.parametrize("mutation",[
    lambda x:x.update(official_atom_denominator=104),
    lambda x:x["per_track_official_atom_denominator"].update(ELECTIVE_E=4),
    lambda x:x.update(total_context_checked=239),
    lambda x:x.update(not_context_checked=0),
    lambda x:x.update(historical_candidates=238),
    lambda x:x.update(source_layout_cues=404),
    lambda x:x.update(teacher_approved=1),
    lambda x:x.update(student_authoritative=1),
    lambda x:x.update(provisional_teaching_targets=239),
    lambda x:x["records"][0].update(teacher_status="APPROVED"),
    lambda x:x["records"][0].update(teacher_signature="invented"),
    lambda x:x["records"][0].update(official_atom_id="fake"),
    lambda x:x["records"][0].update(student_authoritative=True),
    lambda x:x["records"][0].update(mathematics_formally_certified=True),
    lambda x:x["records"][0]["source"].update(span_sha256="0"*64),
    lambda x:x["records"][0]["proposed_teaching_targets"][0].update(teacher_status="APPROVED"),
    lambda x:x["records"][0]["proposed_teaching_targets"][0].update(official_atom_id="FRAUD"),
    lambda x:x["records"].pop(),
    lambda x:x["records"].append(copy.deepcopy(x["records"][0])),
    lambda x:x["counts_by_track"].update(COMPULSORY=9),
    lambda x:x["per_track_editorial_census"]["ELECTIVE_E"].update(source_context_checked=100),
    lambda x:x.update(source_text_embedded=True)
])
def test_22_forged_curriculum_scope_mutations_fail_closed(mutation):
    obj=copy.deepcopy(SOURCE);mutation(obj)
    with pytest.raises((ValueError,KeyError)):
        src.validate(obj,LOCKS,regen=False)

@pytest.mark.parametrize("mutation",[
    lambda x:x[0].update(teacher_review_status="APPROVED"),
    lambda x:x[0].update(teacher_review_evidence={"reviewer":"FAKE"}),
    lambda x:x[0].update(student_authoritative=True),
    lambda x:x[0].update(formal_proof_certified=True),
    lambda x:x[0].update(free_student_step_verified=True),
    lambda x:x[0].update(teacher_solution_visibility="PUBLIC"),
    lambda x:x[0]["teacher_examples"].pop(),
    lambda x:x[0]["student_hint_ladder"].pop(),
    lambda x:x[0]["reasoned_steps"].pop(),
    lambda x:x.pop(),
    lambda x:x.append(copy.deepcopy(x[0]))
])
def test_11_forged_or_truncated_deep_lesson_mutations_fail_closed(mutation):
    docs=copy.deepcopy(LESSONS);mutation(docs)
    with pytest.raises((ValueError,KeyError)):
        deep.validate(docs,regen=False)

def test_scope_rebuilder_and_lesson_rebuilder_deterministic():
    expected,locks=src.build()
    assert expected==SOURCE and locks==LOCKS
    assert src.OUT.read_text(encoding="utf-8")==src.enc(SOURCE)
    assert src.LOCKS.read_text(encoding="utf-8")==src.enc(LOCKS)
    assert src.REPORT.read_text(encoding="utf-8")==src.render(SOURCE)
    assert deep.build()==LESSONS and deep.exact_checks()==ORACLES
    assert deep.OUT.read_text(encoding="utf-8")==deep.enc(LESSONS)
    assert deep.ORACLES.read_text(encoding="utf-8")==deep.enc(ORACLES)
    assert deep.REPORT.read_text(encoding="utf-8")==deep.render(LESSONS,ORACLES)

def test_seven_track_denominators_are_explicitly_unknown():
    assert SOURCE["total_context_checked"]==104 and SOURCE["not_context_checked"]==135
    assert SOURCE["historical_candidates"]==239
    assert set(SOURCE["counts_by_track"])==set(src.TRACKS)
    assert {r["course_track"] for r in LESSONS}==set(src.TRACKS)
    assert all(row["official_atom_denominator"] is None for row in SOURCE["per_track_editorial_census"].values())
    assert ORACLES["general_theorem_proofs_formally_certified"]==0
    assert ORACLES["student_free_steps_verified"]==0

def test_student_authority_view_never_contains_draft_teacher_answers():
    public=json.dumps(public_summary(),ensure_ascii=False)
    assert "kb129-deep-" not in public
    assert "KB_BATCH129" not in public
    assert "teacher_examples" not in public
    assert "formal_definition_or_theorem" not in public
