"""K00/K01/K07/K09 evidence hardening; no teacher/proof approval by test suite."""
import copy
from fractions import Fraction
from math import comb
import json
from pathlib import Path

import pytest
from sympy import Rational, Symbol, limit

from app.official_clause_audit import (
    PINNED_LEDGER_SHA256, PINNED_PDF_SHA256, canonical_ledger_sha256,
    source_clause_ledger, validate_ledger, TRACKS,
)
from app.batch18_math_checks import CONFLICT_IDS, conflict_subclaim_checks
from app.standard_scope import public_progress
from app.k00_review_queue import public_review_summary

ROOT = Path(__file__).resolve().parents[2]
sys_path = ROOT / "scripts"
import sys
sys.path.insert(0, str(sys_path))
from build_kb_batch20_k00_review_queue import build, validate_queue

def test_pinned_official_source_is_original_snapshot():
    a = source_clause_ledger()
    assert canonical_ledger_sha256(a) == PINNED_LEDGER_SHA256
    assert a["source"]["sha256"] == PINNED_PDF_SHA256
    assert len(a["pages"]) == 61
    assert len(a["enumerated_source_anchors"]) == 315

@pytest.mark.parametrize("tamper", [
    "pdf_hash_valid_hex", "page_hash_valid_hex", "line_hash_valid_hex",
    "marker_valid_text", "page_track", "source_title", "contract_reason",
    "source_page_count", "swap_line_hashes", "different_url",
])
def test_valid_looking_source_evidence_forgery_rejected(tamper):
    a=copy.deepcopy(source_clause_ledger())
    rows=a["enumerated_source_anchors"]
    if tamper == "pdf_hash_valid_hex": a["source"]["sha256"]="f"*64
    elif tamper == "page_hash_valid_hex": a["pages"][0]["pdf_text_sha256"]="f"*64
    elif tamper == "line_hash_valid_hex": rows[0]["line_sha256"]="f"*64
    elif tamper == "marker_valid_text": rows[0]["marker"]="（２）"
    elif tamper == "page_track": a["pages"][0]["tracks_present"]=["COMPULSORY","ELECTIVE_A"]
    elif tamper == "source_title": a["source"]["title"]="Unknown standard"
    elif tamper == "contract_reason": a["denominator_contract"]["reason"]="Everything certified"
    elif tamper == "source_page_count": a["source"]["pdf_total_pages"]=999
    elif tamper == "swap_line_hashes": rows[0]["line_sha256"],rows[1]["line_sha256"]=rows[1]["line_sha256"],rows[0]["line_sha256"]
    elif tamper == "different_url": a["source"]["url"]="https://attacker.invalid/standard.pdf"
    assert canonical_ledger_sha256(a) != PINNED_LEDGER_SHA256
    with pytest.raises(ValueError):
        validate_ledger(a)

def test_review_queue_counts_and_source_track_coverage_do_not_claim_official_atoms():
    q=build()
    assert validate_queue(q)==q
    assert len(q["review_queue"])==427
    assert q["summary"]["task_counts_by_kind"] == {
        "SOURCE_PAGE_SPLIT": 61, "NUMBERED_MARKER_SPLIT": 315,
        "UNNUMBERED_DE_HEADING_SPLIT": 23, "EDITORIAL_GAP_DECISION": 28,
    }
    assert [x["track"] for x in q["tracks"]]==list(TRACKS)
    assert sum(x["numbered_source_marker_candidates"] for x in q["tracks"])==315
    assert sum(x["d_e_unnumbered_heading_candidates"] for x in q["tracks"])==23
    assert sum(x["editorial_gap_tickets_open"] for x in q["tracks"])==28
    assert sum(x["editorial_learning_objective_candidates"] for x in q["tracks"])==132
    assert all(x["verified_official_atomic_denominator"] is None for x in q["tracks"])
    assert all(x["official_coverage_rate"] is None and x["teacher_verified_knowledge_atoms"]==0
               for x in q["tracks"])
    assert all(x["review_status"]=="HUMAN_CURRICULUM_AND_MATH_REVIEW_PENDING"
               and not x["teacher_approved"] and not x["student_publishable"]
               and not x["counts_as_verified_atomic_skill"]
               for x in q["review_queue"])
    assert len({x["id"] for x in q["review_queue"]})==427
    assert all(len(x["source_page_sha256"])==64 for x in q["review_queue"])

@pytest.mark.parametrize("tamper", [
    "approve","release","count_as_atom","delete_task","duplicate_id",
    "fake_page_hash","false_complete","false_denominator","false_track_coverage",
    "change_source_id","relabel_source_track","turn_D_into_national_mandatory",
])
def test_review_worklist_fails_closed_for_mutations(tamper):
    q=build()
    r=q["review_queue"][0]
    if tamper=="approve":r["teacher_approved"]=True
    elif tamper=="release":r["student_publishable"]=True
    elif tamper=="count_as_atom":r["counts_as_verified_atomic_skill"]=True
    elif tamper=="delete_task":q["review_queue"].pop()
    elif tamper=="duplicate_id":q["review_queue"][1]["id"]=r["id"]
    elif tamper=="fake_page_hash":r["source_page_sha256"]="a"*64
    elif tamper=="false_complete":q["summary"]["complete_syllabus_inventory"]=True
    elif tamper=="false_denominator":q["summary"]["official_atomic_denominator"]=427
    elif tamper=="false_track_coverage":q["tracks"][0]["official_coverage_rate"]=1.0
    elif tamper=="change_source_id":r["source_id"]="FAKE"
    elif tamper=="relabel_source_track":q["review_queue"][61]["track"]="ELECTIVE_D"
    elif tamper=="turn_D_into_national_mandatory":q["tracks"][-2]["needs_full_human_atomization"]=False
    with pytest.raises(ValueError):
        validate_queue(q)

def test_existing_api_only_exposes_reviewer_task_counts_and_unknown_official_coverage():
    api=public_progress()
    summary=api["k00_human_review_worklist"]
    assert summary==public_review_summary()
    assert summary["review_tasks_not_unique_atoms"]==427
    assert summary["editorial_objective_candidates_not_verified_atoms"]==132
    assert summary["official_atomic_denominator"] is None
    assert not summary["complete"] and not summary["student_publishable"]
    assert "teacher_solution" not in json.dumps(api)

def test_piecewise_original_domain_and_continuity_check_are_not_identity_mapping():
    rows=conflict_subclaim_checks()
    assert len(rows)==10
    assert len(rows["math.hs.function.piecewise"]["exact_observations"])==4
    claims=[x["claim"] for x in rows["math.hs.function.piecewise"]["exact_observations"]]
    assert any("undefined" in x for x in claims)
    assert not any("no forced discontinuity" in x for x in claims)
    x=Symbol("x",real=True)
    assert limit(x/x,x,0)==1
    with pytest.raises(ZeroDivisionError):
        Fraction(0,0)

@pytest.mark.parametrize("value", [i for i in range(-120,121) if i!=0])
def test_piecewise_quotient_equals_one_only_on_original_nonzero_domain(value):
    assert Fraction(value,value)==1
    assert Fraction(value,value)!=value if value!=1 else True

@pytest.mark.parametrize("a",range(-15,16))
@pytest.mark.parametrize("b",range(-15,16))
def test_algebraic_cancellation_preserves_excluded_pole(a,b):
    # This finite exact oracle is NOT a verification of arbitrary student steps.
    if b==0:
        with pytest.raises(ZeroDivisionError):
            Fraction(a,b)
    else:
        assert Fraction(a,b)*b==a

@pytest.mark.parametrize("N",range(1,10))
@pytest.mark.parametrize("K",range(10))
@pytest.mark.parametrize("n",range(10))
def test_hypergeometric_only_with_feasible_population_parameters(N,K,n):
    if 0<=K<=N and 0<=n<=N:
        assert sum(Rational(comb(K,k)*comb(N-K,n-k),comb(N,n))
                   for k in range(max(0,n-(N-K)),min(K,n)+1))==1
    else:
        assert K>N or n>N

def test_33_local_checks_cannot_adjudicate_10_conflicts():
    checks=conflict_subclaim_checks()
    assert set(checks)==set(CONFLICT_IDS)
    assert sum(len(c["exact_observations"]) for c in checks.values())==33
    assert all(
        c["teacher_review"]=="PENDING" and not c["full_natural_language_proof_certified"]
        and not c["source_versions_adjudicated"]
        for c in checks.values()
    )
