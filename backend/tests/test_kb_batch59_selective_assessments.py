"""Batch59 teacher-only assessment schema, math premise and safety regressions."""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import sys

import pytest
from app.kb_batch59_math_guards import check

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import author_kb_batch59_selective_assessments as A

RAW=A.load(A.SEED)
CROSS=A.build()
ROWS=CROSS["rows"]


def test_all_selective_attainment_and_activity_sources_have_review_draft_not_approval():
    assert len(RAW)==len(ROWS)==14
    assert CROSS["source_requirements"]==14
    assert CROSS["teacher_only_review_drafts"]==14
    assert CROSS["total_distinct_noncontent_requirements_unmapped"]==42
    assert CROSS["teacher_verified_assessments"]==0
    assert CROSS["live_student_attempts"]==0
    assert CROSS["mathematical_general_proofs_certified"]==0
    assert all(v is None for v in CROSS["official_atomic_denominator"].values())
    assert all(not r["curriculum_competency_achieved"] for r in ROWS)
    assert all(not r["independent_teacher_rubric_verified"] for r in ROWS)

@pytest.mark.parametrize("i",range(14))
def test_every_original_assessment_has_reasoned_steps_counterexample_hints_and_rubric(i):
    item=RAW[i];row=ROWS[i]
    assert row["source_requirement_id"]==item["source_requirement_id"]
    assert row["assessment_id"]==item["assessment_id"]
    assert item["approval_state"]=="REVIEW_PENDING"
    assert item["visibility"]=="TEACHER_ONLY"
    assert item["general_math_certificate"]=="NOT_FORMALLY_CERTIFIED"
    assert len(item["reasoning_steps"])>=3
    assert all(x["reason"] and x["claim"] for x in item["reasoning_steps"])
    assert len(item["hint_ladder"])==3
    assert item["typical_wrong_method"] and item["counterexample_or_failure"]
    assert item["near_transfer"] and item["far_transfer"] and item["rubric"]
    assert not row["real_student_response_evaluated"]
    assert not row["independent_teacher_rubric_verified"]
    assert not row["student_publishable"]
    assert row["source_span_id"].startswith("P")

@pytest.mark.parametrize("i",range(14))
def test_forged_teacher_signature_or_release_is_never_allowed(i):
    fake=deepcopy(RAW)
    fake[i]["approval_state"]="APPROVED"
    fake[i]["student_publishable"]=True
    fake[i]["real_teacher_signature"]="FAKE"
    with pytest.raises(ValueError,match="forged teacher approval"):
        A.build(manuscripts=fake)

@pytest.mark.parametrize("i",range(14))
def test_missing_reason_and_hint_ladder_are_rejected(i):
    fake=deepcopy(RAW)
    fake[i]["reasoning_steps"][0]["reason"]=""
    with pytest.raises(ValueError,match="reasoning steps"):
        A.build(manuscripts=fake)
    fake=deepcopy(RAW)
    fake[i]["hint_ladder"]=["直接公布完整教师答案"]
    with pytest.raises(ValueError,match="three-level"):
        A.build(manuscripts=fake)

def test_incorrect_source_binding_and_extra_fields_are_rejected():
    fake=deepcopy(RAW)
    fake[0]["source_requirement_id"]=fake[1]["source_requirement_id"]
    with pytest.raises(ValueError,match="duplicated"):
        A.build(manuscripts=fake)
    fake=deepcopy(RAW)
    fake[0]["source_requirement_id"]="KB59-C-P038-S001"
    with pytest.raises(ValueError,match="non-achievement"):
        A.build(manuscripts=fake)
    fake=deepcopy(RAW)
    fake[0]["llm_auto_approved"]=True
    with pytest.raises(ValueError,match="missing or extra"):
        A.build(manuscripts=fake)

def test_unmapped_competencies_not_erased_by_manuscript_count():
    audit=A.SOURCE.build()
    audit["competency_requirement_queue"][0]["coverage"]="CERTIFIED"
    with pytest.raises(ValueError,match="drafts cannot erase"):
        A.build(source=audit)

def test_rendered_markdown_and_machine_crosswalk_reproducible():
    assert A.COVER.read_text(encoding="utf8")==json.dumps(CROSS,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    assert A.OUT.read_text(encoding="utf8")==A.render(CROSS,RAW)
    assert "TEACHER_ONLY" in A.OUT.read_text(encoding="utf8")
    assert "教师真实审核数为0" in A.OUT.read_text(encoding="utf8")

def test_examples_exact_arithmetic_derivative_basis_and_ellipse():
    assert check("arithmetic_partial_sum",first=12,difference=3,n=6)["values"]["sum"]==117
    assert check("affine_square_derivative",a=2,b=1,x=3)["values"]["derivative_at_x"]==28
    assert check("space_basis_coordinates",basis=((1,0,0),(1,1,0),(0,0,2)),vector=(5,3,4))["values"]["coordinates"]==(2,3,2)
    assert check("ellipse_focal_parameters",a=5,c=3)["values"]["b_squared"]==16
    assert not any(r["bounded_exact_witness_families"] and r["curriculum_competency_achieved"] for r in ROWS)

def test_counting_hypergeom_pearson_ols_chisquare_exact_against_teaching_examples():
    assert check("binomial_coefficient",n=5,k=2)["values"]["coefficient"]==10
    assert check("binomial_coefficient",n=4,k=2)["values"]["coefficient"]==6
    assert check("hypergeometric_probability",population=10,successes=4,draws=3,observed=2)["values"]["probability"]==Fraction(3,10)
    assert check("pearson_squared",xs=(1,2,3),ys=(2,4,6))["values"]["r_squared"]==1
    out=check("least_squares",xs=(1,2,3),ys=(2,4,6))["values"]
    assert (out["slope"],out["intercept"])==(2,0)
    assert check("two_by_two_chi_square",table=((10,20),(20,10)))["values"]["chi_square"]==Fraction(20,3)

@pytest.mark.parametrize("i",[0,2,4,7,10,13])
def test_unapproved_assessment_source_not_retrievable_to_student(i):
    from app.deep_retrieval import student_evidence_lookup
    from app.model_tutor_draft import draft_next_question
    candidate=RAW[i]["source_requirement_id"]
    r=student_evidence_lookup(candidate,limit=3)
    assert r["status"]=="NO_APPROVED_EVIDENCE"
    assert r["candidates"]==[] and not r["teacher_solution_exposed"]
    draft=draft_next_question(candidate,mode="GUIDE",help_requested=True,
                             consent_to_cloud=True,operator_scope="EDITOR_LOCAL",
                             provider_url="https://api.openai.com/v1/chat/completions",
                             provider_model="offline-test-do-not-call")
    assert draft.status=="BLOCKED" and not draft.model_called and not draft.student_visible
