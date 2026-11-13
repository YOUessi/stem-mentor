"""Batch141: source lineage, conditional mathematical guard and fail-closed negative tests."""
import copy
import json
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"backend"),str(ROOT/"scripts")]
import build_kb_batch141_lineage as author
import check_kb_batch141_math as oracle
from app.kb_batch139_index import student_evidence_lookup

@pytest.fixture(scope="module")
def report():
    return json.loads(author.OUT.read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def cases():
    return json.loads(oracle.OUT.read_text(encoding="utf-8"))

def test_frozen_lineage_rebuild_and_complete_p0(report):
    assert report==author.build()
    assert author.MD.read_text(encoding="utf-8")==author.render(report)
    assert report["previous_source_card_union"]==80
    assert report["new_source_locked_legacy_cards"]==47
    assert report["new_format_p0_union"]==127
    assert report["historical_p0_denominator"]==127
    assert report["p0_without_new_format_card"]==0
    assert report["all_p0_with_prior_editorial_notes"]==127
    assert report["historical_proof_steps"]==538
    assert report["original_math_conflicts_unresolved"]==10
    assert report["review_without_new_exact_case"]==35

@pytest.mark.parametrize("i",range(47))
def test_each_migrated_step_is_locked_to_the_correct_historical_review(i,report):
    row=report["records"][i]
    assert row["historical_proof_step_id"]==author.previous.build()["remaining_p0_step_ids"][i]
    assert row["historical_step_sha256"] and row["legacy_editorial_record_sha256"]
    assert row["necessary_preconditions"] and row["legacy_counterexample_or_boundary"]
    assert row["justification_status"]=="HISTORIC_EXPLANATION_ONLY_REQUIRES_INDEPENDENT_PROOF_REVIEW"
    assert row["general_proof_certified"] is False
    assert row["original_step_formally_verified"] is False
    assert row["student_free_text_verified"] is False
    assert row["teacher_review_status"]=="REVIEW_PENDING"
    assert row["teacher_signature"] is None and row["student_publishable"] is False
    assert row["course_family_provisional"].endswith("_UNRESOLVED")

@pytest.mark.parametrize("i",range(12))
def test_independent_sympy_exact_case_links_to_review_id(i,report,cases):
    case=cases["cases"][i]
    assert case["historical_step_id"]==author.EXACT_IDS[i]
    assert case["historical_step_id"] in {r["historical_proof_step_id"] for r in report["records"]}
    assert case["legal_exact_case_pass"] is True
    assert case["invalid_precondition_case_pass"] is True
    assert case["verdict"]=="TWO_FINITE_CASES_NOT_A_GENERAL_PROOF"
    assert case["teacher_approved"] is False and case["student_step_verified"] is False

def test_independent_oracle_is_recomputed_not_trusted(cases):
    assert cases==oracle.evidence()
    assert cases["positive_or_boundary_cases"]==12
    assert cases["invalid_premise_cases"]==12
    assert cases["formal_proofs_certified"]==0
    assert cases["official_course_denominators"] is None

@pytest.mark.parametrize("i",range(47))
@pytest.mark.parametrize("field,bad",[
 ("historical_step_sha256","0"*64),
 ("original_claim","伪造的证明"),
 ("original_reason","不证明也成立"),
 ("historical_risk_groups",["FORGED"]),
 ("necessary_preconditions","所有条件都不需要考虑"),
 ("legacy_counterexample_or_boundary","所有边界都不存在"),
 ("legacy_editorial_record_sha256","f"*64),
 ("legacy_editorial_source","docs/evaluation/forged.json"),
 ("legacy_editorial_operation","FORGED"),
 ("justification_status","FORMALLY_VERIFIED"),
 ("independent_exact_case_status","24_FINITE_CASES_IN_SEPARATE_ORACLE_FAKE"),
 ("course_family_provisional","COMPULSORY"),
 ("general_proof_certified",True),
 ("original_step_formally_verified",True),
 ("student_free_text_verified",True),
 ("teacher_review_status","APPROVED"),
 ("teacher_signature",{"name":"imaginary","approved":True}),
 ("student_publishable",True),
])
def test_corrupt_source_premise_status_or_teacher_review_must_fail(i,field,bad,report):
    spoof=copy.deepcopy(report)
    spoof["records"][i][field]=bad
    with pytest.raises((ValueError,AssertionError,KeyError)):
        author.validate(spoof)

@pytest.mark.parametrize("field,bad",[
 ("historical_proof_steps",127),
 ("historical_p0_denominator",80),
 ("previous_source_card_union",127),
 ("new_source_locked_legacy_cards",0),
 ("new_format_p0_union",538),
 ("p0_without_new_format_card",47),
 ("all_p0_with_prior_editorial_notes",0),
 ("original_math_conflicts_unresolved",0),
 ("independent_exact_witnessed_steps",47),
 ("independent_exact_case_count",94),
 ("review_without_new_exact_case",0),
 ("official_course_atom_denominators",{"COMPULSORY":999}),
 ("official_coverage_fraction",1.0),
 ("human_teacher_approvals",47),
 ("general_formal_proof_certificates",47),
 ("student_authoritative_publications",47),
 ("student_free_form_step_certifications",47),
])
def test_aggregate_false_completion_or_approval_is_rejected(field,bad,report):
    spoof=copy.deepcopy(report)
    spoof[field]=bad
    with pytest.raises((ValueError,AssertionError,KeyError)):
        author.validate(spoof)

@pytest.mark.parametrize("query",[
 "直线法向量","余弦降幂","复数除法","空间二面角","圆锥体积","条件概率",
 "切线方程","贝叶斯概率","伯努利最大似然","向量投影",
])
def test_student_evidence_must_remain_closed_even_with_all_p0_cards(query):
    result=student_evidence_lookup(query)
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert result["candidates"]==[]
    assert result["teacher_solution_exposed"] is False
    assert result["unverified_content_exposed"] is False
