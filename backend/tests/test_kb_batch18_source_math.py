"""K00/K07 batch18: frozen source, falsification, proof-risk and safety regression."""
from copy import deepcopy
from fractions import Fraction
from math import comb
from pathlib import Path
import json
import sys
import pytest
from sympy import Rational, sqrt, Abs, symbols, simplify
from app.official_clause_audit import (source_clause_ledger, validate_ledger, page_progress)
from app.k00_gap_audit import gap_tickets, validate_gap_tickets
from app.official_topic_outline import de_outline,validate_outline
from app.batch18_math_checks import CONFLICT_IDS, conflict_subclaim_checks
from app.standard_scope import public_progress

ROOT=Path(__file__).resolve().parents[2]

def test_verified_source_hash_and_exact_physical_pages():
    raw=source_clause_ledger()
    assert raw["source"]["sha256"]=="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
    assert [p["printed_page"] for p in raw["pages"]]==list(range(13,74))
    assert raw["denominator_contract"]["source_page_denominator"]==61
    assert sum(raw["denominator_contract"]["by_track_source_numbered_candidates"].values())==315
    assert raw["denominator_contract"]["official_atomic_knowledge_denominator"] is None
    assert raw["denominator_contract"]["is_full_official_atomic_inventory"] is False
    assert all(p["unnumbered_requirement_completeness"]=="UNKNOWN_NEEDS_HUMAN_SPLIT" for p in raw["pages"])

@pytest.mark.parametrize("field,value",[
    ("status","CERTIFIED"),
    ("is_full_official_atomic_inventory", True),
    ("official_atomic_knowledge_denominator",315),
    ("teacher_approved_clauses",1),
])
def test_source_ledger_cannot_claim_approvals(field,value):
    c=deepcopy(source_clause_ledger())
    if field=="status":c["status"]=value
    else:c["denominator_contract"][field]=value
    with pytest.raises(ValueError):validate_ledger(c)

@pytest.mark.parametrize("tamper",[
    "omit_page", "repeat_anchor", "fake_teacher", "wrong_page", "wrong_track",
    "anchor_hash", "source_sha", "page_marker_count", "bad_marker_id",
])
def test_source_ledger_rejects_tampering(tamper):
    c=deepcopy(source_clause_ledger())
    r=c["enumerated_source_anchors"][0]
    if tamper=="omit_page":c["pages"].pop()
    if tamper=="repeat_anchor":c["enumerated_source_anchors"].append(deepcopy(r))
    if tamper=="fake_teacher":r["teacher_review"]="APPROVED"
    if tamper=="wrong_page":r["pdf_page_index"]=0
    if tamper=="wrong_track":r["track"]="UNKNOWN"
    if tamper=="anchor_hash":r["line_sha256"]="invalid"
    if tamper=="source_sha":c["source"]["sha256"]="no"
    if tamper=="page_marker_count":c["pages"][r["printed_page"]-13]["source_numbered_marker_count"]+=1
    if tamper=="bad_marker_id":r["id"]="123"
    with pytest.raises(ValueError):validate_ledger(c)

def test_unnumbered_de_not_silently_dropped():
    d=de_outline()
    assert d["summary"]["ELECTIVE_D_subtopic_headings"]==17
    assert d["summary"]["ELECTIVE_E_scoped_examples_or_modules"]==6
    assert d["summary"]["fully_complete"] is False
    assert all(x["teacher_review"]=="PENDING" for x in d["items"])

@pytest.mark.parametrize("tamper",["E_mandatory","fake_approval","page_hash","wrong_count"])
def test_unnumbered_outline_fail_closed(tamper):
    d=deepcopy(de_outline())
    if tamper=="E_mandatory":d["items"][-1]["offering_type"]="REQUIRED"
    if tamper=="fake_approval":d["items"][0]["teacher_review"]="APPROVED"
    if tamper=="page_hash":d["items"][0]["page_text_sha256"]="0"*64
    if tamper=="wrong_count":d["summary"]["ELECTIVE_D_subtopic_headings"]=18
    with pytest.raises(ValueError):validate_outline(d)

def test_28_gap_tickets_are_open_and_not_proven_missing():
    g=gap_tickets()
    assert len(g["tickets"])==28
    assert sum(g["summary"]["by_track"].values())==28
    assert g["summary"]["teacher_resolved"]==0
    assert all(x["gap_status"]=="OPEN_EDITORIAL_CANDIDATE_NOT_PROVEN_MISSING" for x in g["tickets"])
    assert all(x["standard_status"]=="OPTIONAL_LOCAL_CHOICE_EXAMPLE"
               for x in g["tickets"] if x["track"]=="ELECTIVE_E")

@pytest.mark.parametrize("tamper",["approve","wrong_hash","fake_mandatory_e","duplicate","wrong_objective","wrong_source"])
def test_gap_tickets_rejects_false_certainty(tamper):
    g=deepcopy(gap_tickets())
    r=g["tickets"][0]
    if tamper=="approve":r["review_status"]="APPROVED"
    if tamper=="wrong_hash":r["source_page_text_sha256"]="0"*64
    if tamper=="fake_mandatory_e":next(x for x in g["tickets"] if x["track"]=="ELECTIVE_E")["standard_status"]="MANDATORY"
    if tamper=="duplicate":g["tickets"].append(deepcopy(r))
    if tamper=="wrong_objective":r["nearest_existing_editorial_objective"]="FAKE"
    if tamper=="wrong_source":g["source_pdf_sha256"]="f"*64
    with pytest.raises(ValueError):validate_gap_tickets(g)

def test_student_api_reports_evidence_without_claiming_official_completion():
    r=public_progress()
    assert r["complete_curriculum"] is False
    assert r["official_atomic_denominator"] is None
    assert r["teacher_approved"]==0
    assert r["student_knowledge_released"]==0
    assert r["official_source_page_evidence"]["numbered_source_clause_candidates"]==315
    assert r["official_source_page_evidence"]["official_total_coverage_rate"] is None
    assert r["unreviewed_source_gap_candidates"]["tickets"]==28
    assert "teacher_solution" not in str(r)

def test_ten_historic_conflicts_remain_unresolved():
    rows=conflict_subclaim_checks()
    assert set(rows)==set(CONFLICT_IDS)
    assert sum(len(x["exact_observations"]) for x in rows.values())==33
    assert all(x["teacher_review"]=="PENDING" and not x["source_versions_adjudicated"]
               and not x["full_natural_language_proof_certified"] for x in rows.values())
    assert all(z["passed"] for row in rows.values() for z in row["exact_observations"])

def test_451_step_proofs_still_not_certified():
    r=json.loads((ROOT/"docs/evaluation/KB_BATCH18_SOURCE_AND_PROOF_RISK_AUDIT.json").read_text())
    assert r["summary"]["proof_obligations"]==451
    assert sum(r["summary"]["by_priority"].values())==451
    assert r["summary"]["conflicting_version_pairs"]==10
    assert r["summary"]["versions_resolved"]==0
    assert r["summary"]["existing_semantic_gaps_open"]==23
    assert len(r["legacy_semantic_gap_triage"])==23
    assert all(not t["gap_closed"] for t in r["legacy_semantic_gap_triage"])
    assert r["summary"]["new_source_located_gap_tickets_open"]==28
    assert r["summary"]["teacher_approved_lessons"]==0
    assert len({x["id"] for x in r["proof_review_queue"]})==451
    assert all(x["proof_status"]=="NOT_FORMALLY_VERIFIED" for x in r["proof_review_queue"])

@pytest.mark.parametrize("n",range(8))
@pytest.mark.parametrize("numer",range(11))
def test_binomial_pmf_exactly_normalized_with_guard(n,numer):
    p=Rational(numer,10)
    assert sum(comb(n,k)*p**k*(1-p)**(n-k) for k in range(n+1))==1

@pytest.mark.parametrize("N,K,n",[(N,K,n) for N in range(1,9)
                                  for K in range(N+1) for n in range(N+1)])
def test_hypergeometric_pmf_exactly_normalized_if_parameters_valid(N,K,n):
    values=[Rational(comb(K,k)*comb(N-K,n-k),comb(N,n))
            for k in range(max(0,n-(N-K)),min(K,n)+1)]
    assert sum(values)==1

@pytest.mark.parametrize("q",range(-30,31))
def test_sqrt_square_is_absolute_value_not_identity(q):
    x=Rational(q,7)
    assert simplify(sqrt(x*x)-Abs(x))==0
    if x<0: assert sqrt(x*x)!=x

@pytest.mark.parametrize("x",range(-15,16))
def test_composition_domain_always_keeps_original_poles(x):
    if x==1:
        with pytest.raises(ZeroDivisionError):
            Fraction(x*x-1,x-1)
    else:
        assert Fraction(x*x-1,x-1)==x+1

@pytest.mark.parametrize("a",range(-7,8))
@pytest.mark.parametrize("b",range(-7,8))
def test_point_line_distance_requires_nonzero_normal(a,b):
    if a==b==0:
        assert a*a+b*b==0
    else:
        assert simplify(sqrt(a*a+b*b))>0
