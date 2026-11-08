"""Batch25 independent exact witnesses + full K00/K07/K09 review queue regression."""
import copy
import json
import sys
from collections import Counter
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path

import pytest
import sympy as sp

from app.deep_knowledge import lessons
from app.kb_batch25_math import SUPPORTED, evaluate

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch25_risk_triage as proof
import build_kb_batch25_scope_queue as scope
import build_kb_batch25_content_readiness as quality

def read(rel):return json.loads((ROOT/rel).read_text(encoding="utf-8"))
RISKS=read("docs/evaluation/KB_BATCH25_P0_PROOF_AND_CONFLICT_TRIAGE.json")
PAGES=read("docs/evaluation/KB_BATCH25_K00_PAGE_REVIEW_MATRIX.json")
READY=read("docs/evaluation/KB_BATCH25_LESSON_REVIEW_READINESS.json")

def test_all_three_reports_reproduce_and_never_claim_authority():
    assert json.loads(proof.build())==RISKS
    assert json.loads(scope.build())==PAGES
    assert json.loads(quality.build())==READY
    assert RISKS["summary"]["p0_historical_steps_attested"]==127
    assert RISKS["summary"]["conflicting_versions_reviewed_as_finite_instances"]==10
    assert RISKS["summary"]["conflicts_resolved"]==0
    assert RISKS["summary"]["mathematical_proofs_formally_certified"]==0
    assert PAGES["summary"]["pages_queued"]==61
    assert PAGES["summary"]["pages_rechecked_against_original_pdf"]==0
    assert PAGES["summary"]["numbered_marker_occurrences"]==315
    assert PAGES["summary"]["official_atoms_human_verified"]==0
    assert READY["summary"]["draft_lessons"]==287
    assert READY["summary"]["total_unverified_proof_steps"]==538
    assert READY["summary"]["teacher_side_examples"]==574
    assert len(READY["items"])==len(lessons())
    for report in (PAGES,RISKS,READY):
        assert report["summary"]["verified_official_atomic_denominator"] is None

def test_proof_p0_original_full_id_coverage_and_all_unverified():
    original=read("docs/evaluation/KB_BATCH18_SOURCE_AND_PROOF_RISK_AUDIT.json")
    p0={x["id"] for x in original["proof_review_queue"] if x["priority"]=="P0_GUARD_AND_COUNTEREXAMPLE"}
    assert len(p0)==127==len(RISKS["p0_review_queue"])
    assert {x["id"] for x in RISKS["p0_review_queue"]}==p0
    assert all(x["proof_status"]=="NOT_FORMALLY_VERIFIED" and
               x["teacher_review"]=="PENDING" and
               not x["student_publishable"] and
               not x["finite_instance_certificate"] for x in RISKS["p0_review_queue"])
    assert sum(RISKS["summary"]["p0_by_risk_group"].values())>=127

def test_ten_conflicts_have_one_explicit_restricted_case_each():
    assert {x["id"] for x in RISKS["conflict_finite_evidence"]}==set(proof.FIXTURES)
    assert {x["restricted_oracle"] for x in RISKS["conflict_finite_evidence"]}==SUPPORTED
    for c in RISKS["conflict_finite_evidence"]:
        o=evaluate(c["restricted_oracle"],c["operand_fixture"])
        assert o==c["finite_check_result"]
        assert c["version_winner"] is None
        assert c["independent_math_adjudication"] is False
        assert c["teacher_review"]=="PENDING"

def test_all_61_pages_are_explicit_unreviewed_and_full_7_tracks_preserved():
    assert [p["printed_page"] for p in PAGES["pages"]]==list(range(13,74))
    assert sum(x["numbered_occurrences"] for x in PAGES["pages"])==315
    assert sum(len(x["editorial_objective_ids"]) for x in PAGES["pages"])==132
    assert sum(len(x["unnumbered_de_heading_ids"]) for x in PAGES["pages"])==23
    assert sum(len(x["open_editorial_gap_ids"]) for x in PAGES["pages"])==28
    assert all(not p["original_pdf_page_rechecked"] and not p["official_page_complete"]
               and p["official_atoms_verified"] is None for p in PAGES["pages"])
    assert len(PAGES["tracks"])==7
    assert all(x["verified_official_atomic_denominator"] is None for x in PAGES["tracks"])

def test_all_287_content_items_keep_teacher_solution_separate():
    assert len(READY["items"])==287
    assert all(x["structurally_valid_unreviewed"] and
               all(x["required_field_presence"].values()) and
               x["review_state"]=="REVIEW_PENDING" and
               x["official_atomic_ids_verified"]==[] and
               x["independent_mathematical_proof_certificate"] is None and
               not x["student_challenge_teacher_solution_visible"]
               for x in READY["items"])
    assert sum(x["proof_step_count"] for x in READY["items"])==538
    assert sum(x["teacher_side_worked_examples"] for x in READY["items"])==574

def test_guard_mutations_risk_step_hash_and_track_page(monkeypatch):
    real=proof.read
    def changed(path):
        d=copy.deepcopy(real(path))
        if path==proof.HISTORY:
            row=next(r for r in d["proof_review_queue"]
                     if r["priority"]=="P0_GUARD_AND_COUNTEREXAMPLE")
            row["claim_reason_sha256"]="f"*64
        return d
    monkeypatch.setattr(proof,"read",changed)
    with pytest.raises(ValueError,match="P0 proof"):proof.build()
    monkeypatch.undo()
    old=scope.load
    def missing_page(path):
        d=copy.deepcopy(old(path))
        if path==scope.SOURCE:d["pages"][0]["source_numbered_marker_count"]=500
        return d
    monkeypatch.setattr(scope,"load",missing_page)
    with pytest.raises(ValueError,match="marker count"):scope.build()

@pytest.mark.parametrize("op", sorted(SUPPORTED))
def test_no_arbitrary_free_text_or_malicious_operand_is_evaluated(op):
    for bad in (None, [], {"student_answer":"Hence every theorem is true"},
                {"x":"__import__('os').system('echo unsafe')"},
                {"x":10**100}, {"x":True}):
        r=evaluate(op,bad)
        assert r["status"]=="CONDITIONS_NOT_ESTABLISHED"
        for x in ("student_step_verified","complete_theorem_certified",
                  "teacher_approved","official_curriculum_atom_verified"):
            assert r[x] is False
assert evaluate("unbounded_user_proof",{"claim":"1=2"})["status"]=="UNSUPPORTED"

@pytest.mark.parametrize("x,shift",product(range(-4,5),repeat=2))
def test_reciprocal_composition_original_domain(x,shift):
    r=evaluate("composition_reciprocal",{"x":x,"shift":shift})
    if x+shift==0:assert r["status"]=="CONDITIONS_NOT_ESTABLISHED"
    else:
        assert r["status"]=="VERIFIED_FINITE_INSTANCE"
        assert F(r["witness"]["output"])==F(1,x+shift)

@pytest.mark.parametrize("x,t",product(range(-5,6),repeat=2))
def test_piecewise_half_open_boundary_unique_branch(x,t):
    r=evaluate("piecewise_endpoint",{"x":x,"threshold":t})
    assert r["status"]=="VERIFIED_FINITE_INSTANCE"
    assert r["witness"]["branch"]==("LEFT_LT" if x<t else "RIGHT_GE")
    assert F(r["witness"]["output"])==(x*x if x<t else 2*x)

@pytest.mark.parametrize("coeffs,x",product(([0,2],[1,0,3],[0,0,4],[0,1,0,2]),range(-4,5)))
def test_pointwise_parity_never_global_proof(coeffs,x):
    r=evaluate("parity_polynomial_at_point",{"coefficients":coeffs,"x":x})
    p=sp.Poly(sum(a*sp.Symbol("t")**i for i,a in enumerate(coeffs)),sp.Symbol("t"))
    fx=p.eval(x);fm=p.eval(-x)
    assert r["witness"]["global_parity_certified"] is False
    assert F(r["witness"]["f_x"])==fx
    assert F(r["witness"]["f_minus_x"])==fm

@pytest.mark.parametrize("a,b,k",product(range(-3,4),range(-3,4),(-1,0,1,4)))
def test_ivt_endpoint_sign_does_not_claim_uniqueness(a,b,k):
    r=evaluate("ivt_polynomial_endpoints",{"a":a,"b":b,"k":k})
    if a>=b:assert r["status"]=="CONDITIONS_NOT_ESTABLISHED"
    else:
        assert r["witness"]["strict_opposite_sign"]==((a*a-k)*(b*b-k)<0)
        assert r["witness"]["uniqueness_established"] is False

@pytest.mark.parametrize("A,B,C,x,y",product((-2,0,3),(-1,0,2),(0,3),(-2,1),(0,2)))
def test_point_line_distance_square_exact(A,B,C,x,y):
    r=evaluate("point_line_distance_squared",{"A":A,"B":B,"C":C,"x":x,"y":y})
    if A==0 and B==0:assert r["status"]=="CONDITIONS_NOT_ESTABLISHED"
    else:assert F(r["witness"]["distance_squared"])==F((A*x+B*y+C)**2,A*A+B*B)

@pytest.mark.parametrize("n,k,p",product(range(0,11),range(0,11),("0","1/4","1/2","1")))
def test_binomial_exact_independent_recurrence(n,k,p):
    r=evaluate("binomial_point_mass",{"n":n,"k":k,"p":p})
    if k>n:assert r["status"]=="CONDITIONS_NOT_ESTABLISHED"
    else:
        P=F(p);independent=F(comb(n,k))*P**k*(1-P)**(n-k)
        assert F(r["witness"]["probability"])==independent

@pytest.mark.parametrize("N,K,n",product((1,2,5,8),range(0,9),range(0,9)))
def test_hypergeometric_support_and_sum_to_one(N,K,n):
    if K>N or n>N:return
    total=F(0)
    for k in range(max(0,n-(N-K)),min(n,K)+1):
        r=evaluate("hypergeometric_point_mass",{"N":N,"K":K,"n":n,"k":k})
        assert r["status"]=="VERIFIED_FINITE_INSTANCE"
        total+=F(r["witness"]["probability"])
    assert total==1

@pytest.mark.parametrize("xs,ys",[
 ([1,2,3],[2,4,6]),([0,1,2],[2,0,-2]),([1,1,1],[1,2,3]),
 ([0,2,4],[1,1,1]),([1,2,5],[4,2,0]),([0,3],[0,2])])
def test_regression_exact_variance_guard(xs,ys):
    r=evaluate("regression_slope",{"xs":xs,"ys":ys})
    if len(set(xs))==1:assert r["status"]=="CONDITIONS_NOT_ESTABLISHED"
    else:
        slope=sp.Rational(len(xs)*sum(a*b for a,b in zip(xs,ys))-sum(xs)*sum(ys),
                         len(xs)*sum(x*x for x in xs)-sum(xs)**2)
        assert F(r["witness"]["slope"])==slope
        assert r["witness"]["causation_certified"] is False

@pytest.mark.parametrize("a,b,c,d",product(range(-2,3),repeat=4))
def test_triangle_det_exact_with_collinear_refusal(a,b,c,d):
    r=evaluate("triangle_double_area",{"P":[0,0],"Q":[a,b],"R":[c,d]})
    det=a*d-b*c
    if det==0:assert r["status"]=="CONDITIONS_NOT_ESTABLISHED"
    else:assert F(r["witness"]["double_area"])==abs(det)

@pytest.mark.parametrize("a,b",product(range(-3,4),repeat=2))
def test_vector_linear_combination_exact(a,b):
    u=[1,-2,3];v=[4,0,-1]
    r=evaluate("vector_linear_combination",{"u":u,"v":v,"a":a,"b":b})
    assert r["status"]=="VERIFIED_FINITE_INSTANCE"
    assert [F(x) for x in r["witness"]["result"]]==[a*x+b*y for x,y in zip(u,v)]

@pytest.mark.parametrize("op,data",[
 ("composition_reciprocal",{"x":2,"shift":-2}),
 ("parity_polynomial_at_point",{"coefficients":[1,2],"x":False}),
 ("piecewise_endpoint",{"x":"1/0","threshold":1}),
 ("ivt_polynomial_endpoints",{"a":2,"b":2,"k":1}),
 ("point_line_distance_squared",{"A":0,"B":0,"C":1,"x":2,"y":3}),
 ("binomial_point_mass",{"n":5,"k":6,"p":"1/2"}),
 ("binomial_point_mass",{"n":4,"k":2,"p":"-1/4"}),
 ("hypergeometric_point_mass",{"N":5,"K":3,"n":4,"k":0}),
 ("regression_slope",{"xs":[1,1,1],"ys":[1,2,3]}),
 ("triangle_double_area",{"P":[0,0],"Q":[1,1],"R":[2,2]}),
 ("vector_linear_combination",{"u":[1,2],"v":[1],"a":1,"b":2}),
 ("vector_linear_combination",{"u":[1,2],"v":[1,2],"a":"999999999","b":2}),
])
def test_ten_conflict_hazard_classes_refused(op,data):
    r=evaluate(op,data)
    assert r["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert r["student_step_verified"] is False
    assert r["teacher_approved"] is False
