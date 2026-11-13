"""Batch125 regression: provenance grades, six missing numbered clauses, all 10
unresolved conflicts, exact math negative witnesses, no forged authority."""
import copy, json, sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch125_provenance as p
import build_kb_batch125_math_risk as m
from app.deep_knowledge import public_summary

PROVENANCE=json.loads(p.OUT.read_text())
RESIDUAL=json.loads(p.QUE.read_text())
MATHEMATICS=json.loads(m.OUT.read_text())

@pytest.mark.parametrize("record",PROVENANCE["records"],ids=lambda x:x["candidate_id"])
def test_all_239_candidates_have_non_certifying_source_grade(record):
    assert record["evidence_grade"] in p.GRADES
    assert record["teacher_approved"] is False
    assert record["official_atom_id"] is None
    assert record["student_authoritative"] is False
    assert record["needs_human_semantic_check"] is True
    assert len(record["span_sha256"])==64

@pytest.mark.parametrize("record",RESIDUAL,ids=lambda x:x["cue_id"])
def test_all_135_unlinked_layout_cues_require_review_not_fake_exclusion(record):
    assert record["review_action"] in {
        "HEADING_ONLY_REVIEW_CHILD_REQUIREMENTS",
        "SUBTOPIC_LABEL_REVIEW_NEIGHBORING_REQUIREMENTS",
        "NUMBERED_CLAUSE_REVIEW_CONTEXT_AND_ATOMS"}
    assert record["is_official_atom"] is None
    assert record["teacher_review"]=="REVIEW_PENDING"
    assert len(record["source_line_sha256"])==64

@pytest.mark.parametrize("record",MATHEMATICS["packets"],ids=lambda x:x["id"])
def test_ten_conflicts_are_not_resolved_by_a_finite_counterexample(record):
    assert record["teacher_status"]=="REVIEW_PENDING"
    assert record["teacher_signature"] is None
    assert record["whole_proof_formally_certified"] is False
    assert record["student_freeform_certified"] is False
    assert record["student_publishable"] is False
    assert record["finite_legal_instance_checked"] is True
    assert record["finite_invalid_assumption_checked"] is True
    assert len(record["required_precondition"])>15
    assert len(record["invalid_case_explained"])>20
    assert len(record["far_transfer_prompt"])>16

@pytest.mark.parametrize("case_no",range(10))
def test_each_conflict_independent_sympy_oracle_has_legal_and_invalid_case(case_no):
    assert m.exact_witnesses()[case_no]==(True,True)

@pytest.mark.parametrize("record",[
    lambda x:x.update(official_atom_denominator=405),
    lambda x:x.update(official_census_complete=True),
    lambda x:x.update(teacher_approved=1),
    lambda x:x.update(student_authoritative=1),
    lambda x:x.update(candidates=240),
    lambda x:x["candidate_evidence_grades"].update(NUMBERED_ANCHOR_PRESENT_NOT_CERTIFIED=239),
    lambda x:x["records"][0].update(student_authoritative=True),
    lambda x:x["records"][0].update(teacher_approved=True),
    lambda x:x["records"][0].update(official_atom_id="FAKE"),
    lambda x:x["records"][0].update(evidence_grade="OPTIONAL_EXAMPLE_NOT_REQUIRED_ATOM"),
    lambda x:x["records"][0].update(course_track="ELECTIVE_D"),
    lambda x:x["records"][0].update(span_sha256="FAKE"),
    lambda x:x["records"][0].update(marker_ids=[]),
    lambda x:x["records"][0].update(printed_page=999),
    lambda x:x["records"].append(copy.deepcopy(x["records"][0])),
    lambda x:x["source_artifact_sha256"].update(layout_124="FORGED"),
])
def test_provenance_forgery_is_rejected(record):
    d=copy.deepcopy(PROVENANCE)
    record(d)
    with pytest.raises((ValueError,KeyError)):p.validate(d,RESIDUAL)

@pytest.mark.parametrize("record",[
    lambda x:x.pop(),
    lambda x:x[0].update(is_official_atom=True),
    lambda x:x[0].update(teacher_review="APPROVED"),
    lambda x:x[0].update(source_line_sha256="BOGUS"),
    lambda x:x[0].update(course_track="ELECTIVE_E"),
    lambda x:x[0].update(review_action="CERTIFIED"),
    lambda x:x[0].update(previous_nonatom_proposal_pending=True),
    lambda x:x[0].update(cue_kind="NUMBERED_REQUIREMENT_CUE"),
])
def test_residual_source_or_status_forgery_is_rejected(record):
    d=copy.deepcopy(RESIDUAL)
    record(d)
    with pytest.raises((ValueError,KeyError)):p.validate(PROVENANCE,d)

@pytest.mark.parametrize("record",[
    lambda x:x.update(conflicts_resolved_this_batch=1),
    lambda x:x.update(proof_steps_certified_this_batch=10),
    lambda x:x.update(student_authoritative=True),
    lambda x:x.update(teacher_approved=True),
    lambda x:x.update(historical_unverified_proof_steps=0),
    lambda x:x["packets"][0].update(teacher_status="APPROVED"),
    lambda x:x["packets"][0].update(student_publishable=True),
    lambda x:x["packets"][0].update(teacher_signature={"reviewer":"fake"}),
    lambda x:x["packets"][0].update(whole_proof_formally_certified=True),
    lambda x:x["packets"][0].update(finite_invalid_assumption_checked=False),
    lambda x:x["source_conflict_sha256"] and x.update(source_conflict_sha256="BOGUS"),
])
def test_math_approval_census_spoof_rejected(record):
    d=copy.deepcopy(MATHEMATICS)
    record(d)
    with pytest.raises(ValueError):m.validate(d)

def test_scope_audit_exposes_real_provenance_shortfall_and_no_fake_denominator():
    g=PROVENANCE["candidate_evidence_grades"]
    assert g=={
       "HEADING_OR_SUBTOPIC_ONLY_REQUIRES_CLAUSE":109,
       "NO_LAYOUT_MARKER_ALTERNATE_EVIDENCE_REVIEW":10,
       "NUMBERED_ANCHOR_PRESENT_NOT_CERTIFIED":108,
       "OPTIONAL_EXAMPLE_NOT_REQUIRED_ATOM":12}
    assert PROVENANCE["residual_cue_kinds"]=={
      "TOPIC_CUE":53,"SUBTOPIC_CUE":76,"NUMBERED_REQUIREMENT_CUE":6}
    assert PROVENANCE["prior_nonatom_proposals_unadjudicated"]==3
    assert PROVENANCE["official_atom_denominator"] is None
    assert all(v["official_atom_denominator"] is None
      for v in PROVENANCE["per_track"].values())
    assert p.validate(PROVENANCE,RESIDUAL)

def test_full_proof_debt_preserved_and_exact_checked_but_unapproved():
    assert MATHEMATICS["historical_unverified_proof_steps"]==538
    assert MATHEMATICS["historical_conflicts_unresolved"]==10
    assert MATHEMATICS["exact_legal_witnesses_passed"]==10
    assert MATHEMATICS["invalid_premise_witnesses_passed"]==10
    assert m.validate(MATHEMATICS)

def test_student_retrieval_does_not_expose_batch125_teacher_cases():
    data=json.dumps(public_summary(),ensure_ascii=False)
    assert "KB125-CONFLICT" not in data
    assert "KB_BATCH125_CONFLICT_RISK_REVIEW" not in data
    assert "invalid_case_explained" not in data

def test_all_generated_source_and_math_files_are_exactly_reproducible():
    assert p.OUT.read_text()==p.serial(PROVENANCE)
    assert p.QUE.read_text()==p.serial(RESIDUAL)
    assert p.REPORT.read_text()==p.render(PROVENANCE,RESIDUAL)
    assert m.OUT.read_text()==m.serial(MATHEMATICS)
    assert m.REPORT.read_text()==m.render(MATHEMATICS)
