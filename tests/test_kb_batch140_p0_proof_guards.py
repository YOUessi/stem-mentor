"""Batch140: negative regression of source-locked P0 mathematical risk cards."""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"backend"),str(ROOT/"scripts")]
import build_kb_batch140_proof_guards as audit
import check_kb_batch140_math as oracle
from app.kb_batch139_index import student_evidence_lookup

@pytest.fixture(scope="module")
def report():
    return json.loads(audit.OUT.read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def cases():
    return json.loads(oracle.OUT.read_text(encoding="utf-8"))

def test_all_artifacts_rebuild_exactly_from_frozen_original_steps(report,cases):
    assert report==audit.build()
    assert audit.MD.read_text(encoding="utf-8")==audit.render(report)
    assert cases==oracle.evidence()
    assert report["old_unverified_proof_step_count"]==538
    assert report["p0_step_denominator"]==127
    assert report["p0_with_distinct_review_cards"]==36+20+24==80
    assert report["p0_without_review_cards"]==47
    assert report["unresolved_conflicts"]==10
    # Distinguish legacy editorial-review coverage from newer cards.
    assert report["earlier_kb28_29_30_editorial_records"]=={"KB_BATCH28":35,"KB_BATCH29":48,"KB_BATCH30":44}
    assert report["p0_with_any_earlier_editorial_review"]==127
    assert report["p0_without_any_earlier_editorial_review"]==0
    assert report["source_card_lineage_not_global_first_review_count"] is True

@pytest.mark.parametrize("index",range(24))
def test_each_card_locked_to_original_claim_reason_and_unapproved(index,report):
    r=report["records"][index]
    assert r["historical_proof_step_id"]==audit.CASES[index][0]
    assert r["historical_step_sha256"]
    assert r["necessary_preconditions"] and r["step_justification_review"]
    assert r["non_applicable_boundary"]
    assert r["finite_example_verdict"]=="EXACT_FINITE_WITNESS_ONLY"
    assert r["invalid_condition_verdict"]=="PRECONDITION_NOT_ESTABLISHED"
    assert r["teacher_review_status"]=="REVIEW_PENDING"
    assert r["teacher_signature"] is None
    assert r["student_publishable"] is False
    assert r["quantified_general_proof_certified"] is False
    assert r["original_step_formally_verified"] is False

@pytest.mark.parametrize("index",range(24))
def test_sympy_oracle_independently_matches_exact_step(index,report,cases):
    c=cases["cases"][index]
    assert c["historical_step_id"]==report["records"][index]["historical_proof_step_id"]
    assert c["oracle_key"]==report["records"][index]["independent_oracle_key"]
    assert c["positive_case_pass"] is True and c["invalid_premise_pass"] is True
    assert c["status"]=="FINITE_EXACT_CASES_NOT_GENERAL_PROOF"

@pytest.mark.parametrize("index",range(24))
@pytest.mark.parametrize("field,bogus",[
   ("historical_step_sha256","f"*64),
   ("historical_proof_step_id","math.hs.bogus.step#4"),
   ("original_claim","伪造的数学推导陈述"),
   ("original_reason","没有数学前提的推导"),
   ("necessary_preconditions","所有实数直接除以零都是合法的。"),
   ("step_justification_review","只要语言模型相信就是形式证明。"),
   ("non_applicable_boundary","错误地认定所有退化都符合原命题。"),
   ("independent_oracle_key","forged-oracle"),
   ("teacher_review_status","APPROVED"),
   ("teacher_signature",{"name":"AI-Teacher","approved":True}),
   ("student_publishable",True),
   ("quantified_general_proof_certified",True),
   ("original_step_formally_verified",True),
])
def test_invalid_review_mutations_rejected(index,field,bogus,report):
    copy_report=copy.deepcopy(report)
    copy_report["records"][index][field]=bogus
    with pytest.raises((ValueError,KeyError,AssertionError)):
        audit.validate(copy_report)

@pytest.mark.parametrize("key,value",[
   ("old_unverified_proof_step_count",0),
   ("p0_step_denominator",80),
   ("p0_with_distinct_review_cards",127),
   ("p0_without_review_cards",0),
   ("independent_finite_cases_expected",480),
   ("all_steps_formally_certified",538),
   ("teacher_approved",1),
   ("student_authoritative",1),
   ("p0_with_any_earlier_editorial_review",36),
   ("p0_without_any_earlier_editorial_review",47),
   ("source_card_lineage_not_global_first_review_count",False),
])
def test_aggregate_status_forgery_rejected(key,value,report):
    forged=copy.deepcopy(report)
    forged[key]=value
    with pytest.raises((ValueError,KeyError,AssertionError)):
        audit.validate(forged)

def test_unchanged_official_denominator_and_student_fails_closed(cases):
    assert cases["scope"]=="48_EXACT_FINITE_CASES_NOT_UNIVERSAL_PROOFS"
    assert cases["positive_boundary_count"]==24
    assert cases["invalid_premise_count"]==24
    assert cases["general_proof_certified"]==0
    assert cases["teacher_approved"]==0
    assert cases["student_free_text_verified"]==0
    assert cases["official_course_denominators"] is None
    for q in ("余弦定理","对数乘法","费马引理","柯西不等式","空间基底"):
        result=student_evidence_lookup(q)
        assert result["status"]=="NO_APPROVED_EVIDENCE"
        assert result["candidates"]==[]
        assert not result["teacher_solution_exposed"]
        assert not result["unverified_content_exposed"]
