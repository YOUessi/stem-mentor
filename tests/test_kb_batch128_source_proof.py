"""Batch128 exact source provenance, provisional split and bounded P0 math review regression."""
from __future__ import annotations
import copy
import hashlib
import json
import sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch128_source_ledger as src
import build_kb_batch128_p0_proof_guards as proof
from app.deep_knowledge import public_summary

SOURCE=json.loads(src.OUT.read_text(encoding="utf8"))
LOCKS=json.loads(src.LOCKS.read_text(encoding="utf8"))
PROOFS=json.loads(proof.OUT.read_text(encoding="utf8"))

@pytest.mark.parametrize("record",SOURCE["records"], ids=lambda r:r["candidate_id"])
def test_28_new_source_line_hashes_verified_on_original_mac_pdf(record):
    page=record["source"]["page"]
    a=record["source"]["start_line"]
    b=record["source"]["end_line"]
    lines=src.prior.previous.source_pages()[page][a-1:b]
    assert record["source"]==LOCKS[record["candidate_id"]]
    assert [hashlib.sha256(s.encode()).hexdigest() for s in lines]==record["source"]["line_sha256"]
    assert hashlib.sha256("\n".join(lines).encode()).hexdigest()==record["source"]["span_sha256"]
    assert record["source_pdf_sha256"]==src.prior.provenance.old.previous.base_scope.evidence.PDF_SHA

@pytest.mark.parametrize("record",SOURCE["records"],ids=lambda r:r["candidate_id"])
def test_each_source_split_has_two_pending_not_official_subtargets(record):
    assert record["teacher_status"]=="REVIEW_PENDING"
    assert record["teacher_evidence"] is None
    assert record["student_authoritative"] is False
    assert record["official_atom_id"] is None
    assert record["classification_is_human_pending"] is True
    assert len(record["subtargets"])==2
    assert all(s["official_atom_id"] is None and s["student_authoritative"] is False
               and s["teacher_status"]=="REVIEW_PENDING" for s in record["subtargets"])

@pytest.mark.parametrize("card",PROOFS["records"],ids=lambda r:r["historical_proof_step_id"])
def test_20_p0_guarded_steps_remain_unverified_teacher_only(card):
    assert card["historical_step_formally_certified"] is False
    assert card["general_quantified_proof_certified"] is False
    assert card["student_publishable"] is False
    assert card["teacher_signature"] is None
    assert card["teacher_status"]=="REVIEW_PENDING"
    assert card["bounded_valid_witness_passed"] is True
    assert card["bounded_invalid_case_rejected"] is True
    assert len(card["review_of_justification"])>=29

@pytest.mark.parametrize("row",proof.CASES,ids=lambda r:r[0])
def test_exact_math_boundary_oracle_is_independent_of_review_status(row):
    good,bad=proof.oracle(row[-1])
    assert bool(good) is True
    assert bool(bad) is True
    assert PROOFS["historical_formally_verified_steps"]==0

@pytest.mark.parametrize("mutation", [
    lambda x:x.update(official_atom_denominator=239),
    lambda x:x["per_track_editorial_census"]["ELECTIVE_E"].update(official_atom_denominator=8),
    lambda x:x["per_track_editorial_census"]["COMPULSORY"].update(context_reviewed=999),
    lambda x:x["per_track_official_atom_denominator"].update(ELECTIVE_E=8),
    lambda x:x.update(reviewed_historical_candidates_total=239),
    lambda x:x.update(still_not_context_reviewed=0),
    lambda x:x.update(provisional_editorial_subtargets=239),
    lambda x:x.update(student_authoritative=1),
    lambda x:x.update(teacher_approved=1),
    lambda x:x["records"][0].update(teacher_status="APPROVED"),
    lambda x:x["records"][0].update(student_authoritative=True),
    lambda x:x["records"][0].update(official_atom_id="FALSE"),
    lambda x:x["records"][0]["subtargets"][0].update(official_atom_id="FALSE"),
    lambda x:x["records"][0]["source"].update(span_sha256="0"*64),
    lambda x:x["records"].pop(),
    lambda x:x["records"].append(copy.deepcopy(x["records"][0])),
    lambda x:x.update(source_text_embedded=True),
    lambda x:x["counts_by_track"].update(COMPULSORY=28),
])
def test_source_fraud_and_incomplete_census_rejected(mutation):
    data=copy.deepcopy(SOURCE)
    mutation(data)
    with pytest.raises((ValueError,KeyError)):
        src.validate(data,LOCKS,compare=True)

@pytest.mark.parametrize("mutation", [
    lambda x:x.update(historical_formally_verified_steps=1),
    lambda x:x.update(high_risk_without_review_cards_after_batch=0),
    lambda x:x.update(high_risk_with_review_cards_after_batch=127),
    lambda x:x.update(teacher_approved=1),
    lambda x:x.update(student_authoritative=1),
    lambda x:x.update(finite_exact_positive_cases=538),
    lambda x:x["records"][0].update(historical_step_formally_certified=True),
    lambda x:x["records"][0].update(general_quantified_proof_certified=True),
    lambda x:x["records"][0].update(student_publishable=True),
    lambda x:x["records"][0].update(teacher_status="APPROVED"),
    lambda x:x["records"][0].update(original_step_sha256="0"*64),
    lambda x:x["records"].pop(),
    lambda x:x["records"].append(copy.deepcopy(x["records"][0])),
])
def test_p0_proof_fraud_and_truncation_rejected(mutation):
    data=copy.deepcopy(PROOFS)
    mutation(data)
    with pytest.raises((ValueError,KeyError)):
        proof.validate(data,compare=True)

def test_new_p0_guards_are_disjoint_from_previously_guarded_steps():
    queue=json.loads(proof.QUEUE.read_text())
    indexed={r["id"]:r for r in queue["step_review_queue"]}
    assert len(indexed)==538
    assert len([r for r in indexed.values() if r["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE"])==127
    assert len([r for r in indexed.values() if r["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE" and r["review_card_id"]])==36
    for card in PROOFS["records"]:
        historical=indexed[card["historical_proof_step_id"]]
        assert historical["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE"
        assert historical["review_card_id"] is None
        assert historical["source_sha256"]==card["original_step_sha256"]

def test_deterministic_rebuild_and_public_authority_fail_closed():
    assert SOURCE==src.build()[0]
    assert LOCKS==src.build()[1]
    assert PROOFS==proof.build()
    assert src.OUT.read_text()==src.encode(SOURCE)
    assert src.MD.read_text()==src.render(SOURCE)
    assert proof.OUT.read_text()==proof.enc(PROOFS)
    assert proof.MD.read_text()==proof.render(PROOFS)
    assert src.validate(SOURCE,LOCKS) and proof.validate(PROOFS)
    text=json.dumps(public_summary(),ensure_ascii=False)
    assert "KB_BATCH128" not in text
    assert "kb128-proposed-" not in text
    assert "historical_proof_step_id" not in text
    assert "original_claim" not in text
