"""Batch142 exact mathematical witnesses and fail-closed seven-track publication gates."""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import check_kb_batch142_remaining_oracles as exact
import build_kb_batch142_ledger as ledger
import build_kb_batch141_lineage as previous
from app.kb_batch139_index import student_evidence_lookup, public_coverage, editor_preview_search

@pytest.fixture(scope="module")
def report():
    return json.loads(exact.OUT.read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def cover():
    return json.loads(ledger.OUT.read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def source():
    return previous.build()


def test_recomputed_oracle_and_all_remaining_35(report,source):
    assert exact.verify_report(report)
    pending={r["historical_proof_step_id"] for r in source["records"]
             if r["independent_exact_case_status"]=="NOT_IN_THIS_BATCH_ORACLE"}
    assert pending=={r["historical_step_id"] for r in report["cases"]}
    assert len(pending)==35
    assert report["new_legal_cases"]==35
    assert report["new_invalid_precondition_cases"]==35
    assert report["all_kb141_lineage_rows_with_finite_witnesses"]==47


@pytest.mark.parametrize("i",range(35))
def test_each_legal_exact_witness_evaluated_and_source_locked(i,report,source):
    card=report["cases"][i]
    upstream={r["historical_proof_step_id"]:r for r in source["records"]}[card["historical_step_id"]]
    assert card["historical_step_sha256"]==upstream["historical_step_sha256"]
    assert card["legal_exact_case_pass"] is True
    assert len(card["legal_case"])>=18
    assert card["scope"]=="TWO_EXACT_FINITE_WITNESSES_NOT_UNIVERSAL_PROOF"


@pytest.mark.parametrize("i",range(35))
def test_each_invalid_precondition_has_independent_exact_case(i,report):
    row=report["cases"][i]
    assert row["invalid_precondition_case_pass"] is True
    assert len(row["invalid_case"])>=18
    assert "NOT_UNIVERSAL_PROOF" in row["scope"]


@pytest.mark.parametrize("i",range(35))
def test_each_case_cannot_publish_or_certify(i,report):
    row=report["cases"][i]
    assert row["formal_proof_certified"] is False
    assert row["teacher_approved"] is False
    assert row["student_step_verified"] is False
    assert row["student_publishable"] is False


@pytest.mark.parametrize("i",range(35))
def test_source_card_and_exact_case_are_distinct(i,report,source):
    case=report["cases"][i]
    source_row={r["historical_proof_step_id"]:r for r in source["records"]}[case["historical_step_id"]]
    assert source_row["original_claim"]
    assert source_row["original_reason"]
    assert source_row["general_proof_certified"] is False
    assert source_row["teacher_review_status"]=="REVIEW_PENDING"
    assert case["historical_step_sha256"]==source_row["historical_step_sha256"]


@pytest.mark.parametrize("field,bad",[
    ("newly_oracled_in_this_batch",47),
    ("new_legal_cases",0),
    ("new_invalid_precondition_cases",0),
    ("all_kb141_lineage_rows_with_finite_witnesses",127),
    ("historical_p0_denominator",47),
    ("historical_formally_unverified_steps",0),
    ("unresolved_math_conflicts",0),
    ("official_course_atom_denominators",{"COMPULSORY":113}),
    ("teacher_approvals",1),
    ("student_authoritative_releases",1),
    ("p0_universally_proven_from_this_batch",35),
    ("student_free_form_step_verified",35)
])
def test_forged_aggregate_or_certification_is_rejected(field,bad,report):
    corrupted=copy.deepcopy(report)
    corrupted[field]=bad
    with pytest.raises(ValueError):
        exact.verify_report(corrupted)


@pytest.mark.parametrize("field,bad",[
    ("historical_step_sha256","f"*64),
    ("legal_exact_case_pass",False),
    ("invalid_precondition_case_pass",False),
    ("legal_case","未验证"),
    ("invalid_case","没有反例"),
    ("formal_proof_certified",True),
    ("teacher_approved",True),
    ("student_step_verified",True),
    ("student_publishable",True)
])
def test_forged_case_math_or_status_is_rejected(field,bad,report):
    corrupted=copy.deepcopy(report)
    corrupted["cases"][0][field]=bad
    with pytest.raises(ValueError):
        exact.verify_report(corrupted)


def test_seven_track_coverage_derivation_and_report(cover):
    assert ledger.validate(cover)
    assert ledger.MD.read_text(encoding="utf-8")==ledger.render(cover)
    assert cover["official_course_atom_census_complete"] is False
    assert cover["historical_engineering_map_is_not_denominator"]==113
    assert cover["existing_teacher_only_draft_manuscripts"]==57
    assert sum(x["provisional_teacher_manuscripts"] for x in cover["per_track"].values())==57
    assert set(cover["per_track"])==set(previous.TRACKS)
    assert cover["historical_p0_proof_step_denominator"]==127
    assert cover["independently_checked_kb141_steps_now"]==47
    assert cover["historical_formally_uncertified_proof_steps"]==538


@pytest.mark.parametrize("track",previous.TRACKS)
def test_no_track_converts_editorial_candidate_into_official_denominator(track,cover):
    item=cover["per_track"][track]
    assert item["official_atom_denominator"] is None
    assert item["official_atoms_audited_as_complete"] is None
    assert item["official_coverage_ratio"] is None
    assert item["teacher_approved"]==item["student_authoritative"]==0
    assert item["track_publishable"] is False


@pytest.mark.parametrize("field,bad",[
    ("all_seven_official_coverage_ratio",1.0),
    ("official_denominators_known",True),
    ("official_course_atom_census_complete",True),
    ("human_teacher_approvals",57),
    ("student_authoritative_releases",57),
    ("general_formal_proof_certificates",47),
    ("historical_formally_uncertified_proof_steps",0),
    ("kb141_subset_without_exact_witness",35),
    ("unresolved_math_conflicts",0),
])
def test_ledger_premature_approval_and_false_completion_is_rejected(field,bad,cover):
    spoof=copy.deepcopy(cover)
    spoof[field]=bad
    with pytest.raises(ValueError):
        ledger.validate(spoof)


@pytest.mark.parametrize("track",previous.TRACKS)
def test_ledger_rejects_fake_official_track_denominators(track,cover):
    spoof=copy.deepcopy(cover)
    spoof["per_track"][track]["official_atom_denominator"]=57
    spoof["per_track"][track]["official_coverage_ratio"]=1.0
    with pytest.raises(ValueError):
        ledger.validate(spoof)


@pytest.mark.parametrize("query",[
    "正弦定理","复数有理化","凸性","二次函数的极限","线性方程组行变换",
    "Bernoulli概率估计","两平面垂直","斐波那契","切线极线","平面向量投影"])
def test_student_search_does_not_expose_teacher_solution_after_new_oracles(query):
    result=student_evidence_lookup(query)
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert result["candidates"]==[]
    assert result["teacher_solution_exposed"] is False
    assert result["unverified_content_exposed"] is False


def test_no_student_promotion_through_existing_editorial_index(cover):
    actual=public_coverage()
    assert actual["editorial_review_manuscripts"]==57
    assert actual["teacher_approved"]==0
    assert actual["student_authoritative"]==0
    with pytest.raises(PermissionError):
        editor_preview_search("正弦定理",scope="STUDENT")
