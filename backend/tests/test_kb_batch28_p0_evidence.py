"""Negative, property and independent SymPy checks for 35 historical P0 steps.

No global theorem certification or teacher approval is implied by these tests.
"""
import copy
import json
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path

import pytest
import sympy as sp

from app.kb_batch28_condition_oracles import SUPPORTED, evaluate

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch28_p0_evidence as build

MANIFEST=json.loads(build.MANIFEST.read_text(encoding="utf-8"))
REPORT=json.loads(build.REPORT.read_text(encoding="utf-8"))

def exact(op, data):
    r=evaluate(op,data)
    assert r["status"]=="VERIFIED_FINITE_INSTANCE",r
    assert not any(r[k] for k in ("complete_theorem_certified","teacher_approved",
                                 "student_step_verified","official_curriculum_atom_verified"))
    return r["witness"]

def test_report_reproducible_and_all_127_kept_unverified():
    assert json.loads(build.build())==REPORT
    s=REPORT["summary"]
    assert s["total_historical_p0"]==127
    assert s["p0_with_curated_hypotheses_and_counterexamples"]==35
    assert s["p0_not_yet_curated"]==92
    assert s["distinct_guarded_exact_oracles"]==17
    assert s["exact_valid_fixtures_passed"]==s["negative_condition_fixtures_rejected"]==17
    assert s["full_formal_proofs_certified"]==s["teacher_approvals"]==0
    assert s["all_unverified_proof_steps"]==538
    assert s["official_verified_atomic_denominator"] is None
    assert len(REPORT["reviewed_step_proposals"])==35
    assert len(REPORT["unresolved_p0_step_ids"])==92
    assert set(x["risk_step_id"] for x in REPORT["reviewed_step_proposals"]).isdisjoint(REPORT["unresolved_p0_step_ids"])

@pytest.mark.parametrize("profile",MANIFEST["profiles"],ids=[p["operation"] for p in MANIFEST["profiles"]])
def test_all_17_curated_condition_families_have_valid_and_invalid_exact_cases(profile):
    assert profile["operation"] in SUPPORTED
    assert exact(profile["operation"],profile["valid_exact_fixture"])
    bad=evaluate(profile["operation"],profile["invalid_fixture"])
    assert bad["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert not bad["teacher_approved"] and not bad["complete_theorem_certified"]

@pytest.mark.parametrize("row",REPORT["reviewed_step_proposals"],ids=[r["risk_step_id"] for r in REPORT["reviewed_step_proposals"]])
def test_each_of_35_original_steps_has_hash_and_review_gates(row):
    assert len(row["claim_reason_sha256"])==64
    assert row["math_status"]=="CONDITION_WITNESSES_ONLY_NOT_PROOF"
    assert row["teacher_review"]=="PENDING"
    assert row["human_mathematical_review"]=="PENDING"
    assert row["complete_proof_certified"] is False
    assert row["student_publishable"] is False
    assert row["bounded_valid_instance"]["status"]=="VERIFIED_FINITE_INSTANCE"
    assert row["bounded_invalid_case"]["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_mutation_rejects_fake_signoff_duplicate_or_missing_risk():
    for change in ("approve","duplicate","unknown","garbage_operator","fake_extra_certificates","short_content"):
        x=copy.deepcopy(MANIFEST)
        if change=="approve":x["teacher_review"]="APPROVED"
        elif change=="duplicate":x["profiles"][1]["risk_step_ids"].append(x["profiles"][0]["risk_step_ids"][0])
        elif change=="unknown":x["profiles"][0]["risk_step_ids"][0]="math.hs.fake.proof#1"
        elif change=="garbage_operator":x["profiles"][0]["operation"]="arbitrary_eval"
        elif change=="fake_extra_certificates":x["complete_proof_certificates"]=35
        elif change=="short_content":x["profiles"][0]["explanatory_counterexample"]="wrong"
        with pytest.raises(ValueError):build.build(manifest=x)

def test_mutated_original_step_sha_not_accepted():
    y=json.loads(build.HISTORY.read_text(encoding="utf-8"))
    y["p0_review_queue"][0]["verified_original_step_sha256"]="f"*64
    with pytest.raises(ValueError):
        build.build(history=y)

@pytest.mark.parametrize("n",range(-2,3))
@pytest.mark.parametrize("m",range(-2,3))
def test_cauchy_lagrange_exact_identity_and_zero_cases(n,m):
    w=exact("cauchy_schwarz",{"u":[n,m],"v":[m,n]})
    assert F(w["gap"])==F(w["sum_minor_squares"])==(n*n-m*m)**2
    assert F(w["gap"])>=0

@pytest.mark.parametrize("a,b,c",[(a,b,c) for a,b,c in product(range(-3,4),repeat=3) if a])
def test_quadratic_discriminant_matches_exact_symbolic_classification(a,b,c):
    w=exact("quadratic_discriminant",dict(a=a,b=b,c=c))
    delta=b*b-4*a*c
    assert F(w["delta"])==delta
    assert w["real_root_count"]==(0 if delta<0 else 1 if delta==0 else 2)
    assert F(w["vertex_value"])==F(4*a*c-b*b,4*a)

@pytest.mark.parametrize("p,x,y",[(p,x,y) for p in (-2,-1,1,2) for x in range(-3,4) for y in range(-3,4)])
def test_focus_directrix_equivalence_under_nonzero_p(p,x,y):
    w=exact("parabola_focus",dict(p=p,x=x,y=y))
    assert w["equal_distances"]==(y*y==4*p*x)==w["standard_equation_holds"]
    assert F(w["focus_distance_squared"])-F(w["directrix_distance_squared"])==y*y-4*p*x

@pytest.mark.parametrize("N,K,n",[(N,K,n) for N in range(1,9) for K in range(N+1) for n in range(N+1)])
def test_hypergeometric_probabilities_sum_to_one_independently(N,K,n):
    support=range(max(0,n-(N-K)),min(n,K)+1)
    s=sum((F(exact("hypergeometric",dict(N=N,K=K,n=n,k=k))["point_probability"]) for k in support),F(0))
    assert s==1

@pytest.mark.parametrize("A,B,C,r",[(A,B,C,r) for A in (-2,0,1) for B in (-1,0,2) if A or B for C in (-3,0,1) for r in (1,2)])
def test_line_circle_distance_and_intersection_rule(A,B,C,r):
    w=exact("line_circle",dict(A=A,B=B,C=C,cx=0,cy=0,r=r))
    d2=F(C*C,A*A+B*B)
    assert F(w["distance_squared"])==d2
    assert w["intersection_count"]==(0 if d2>r*r else 1 if d2==r*r else 2)

@pytest.mark.parametrize("r1,r2,d",[(r1,r2,d) for r1 in (1,2,3) for r2 in (1,2,3) for d in range(6)])
def test_circle_circle_coincident_tangent_disjoint(r1,r2,d):
    w=exact("circle_circle",dict(x1=0,y1=0,r1=r1,x2=d,y2=0,r2=r2))
    expected=("INFINITE" if r1==r2 else 0) if d==0 else (
       0 if d>r1+r2 or d<abs(r1-r2) else 1 if d in (r1+r2,abs(r1-r2)) else 2)
    assert w["intersection_count"]==expected

@pytest.mark.parametrize("u,v,x",[(u,v,x) for u in (-2,-1,0,1,2) for v in (-2,0,1,2) for x in (-1,0,1,2) if (v+x)!=0])
def test_quotient_polynomial_derivative_vs_sympy(u,v,x):
    # U(t)=u+3t; V(t)=v+t (nonzero at sample point).
    w=exact("quotient_polynomial_derivative",dict(u=[u,3],v=[v,1],x=x))
    t=sp.Symbol("t")
    expected=sp.diff((u+3*t)/(v+t),t).subs(t,x)
    assert sp.Rational(w["derivative"])==sp.simplify(expected)

def test_probability_zero_mass_intersection_is_not_empty_and_not_disjoint():
    w=exact("union_probability",dict(n=3,A=[0,1],B=[1,2],weights=["1/2","0","1/2"]))
    assert F(w["p_union"])==F(w["p_a"])+F(w["p_b"])
    assert w["zero_probability_does_not_imply_empty"] is True

@pytest.mark.parametrize("bad",[
  {"base":1,"x":4,"y":8},{"base":-2,"x":4,"y":8},{"base":2,"x":-4,"y":-8},
  {"base":2,"x":0,"y":8},{"base":"NaN","x":4,"y":8},
])
def test_log_product_unsafe_input_is_never_promoted(bad):
    r=evaluate("log_product_domain",bad)
    assert r["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert not r["complete_theorem_certified"] and not r["student_step_verified"]

def test_unknown_or_malformed_proof_data_fail_closed():
    assert evaluate("sympy_eval",{"expr":"__import__('os').system('false')"})["status"]=="UNSUPPORTED"
    for bad in ({"a":True,"b":2,"c":1},{"a":1.0,"b":2,"c":1},{"a":"1e999","b":2,"c":1}):
        assert evaluate("quadratic_discriminant",bad)["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert evaluate("circle_circle",{"x1":0})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert evaluate("quadratic_discriminant",["a",1,2])["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_required_strict_boundary_rejections():
    cases=[
      ("point_plane_distance",dict(P=[1,2,3],Q=[0,0,0],normal=[0,0,0])),
      ("vector_angle",dict(u=[0,0],v=[1,1])),
      ("amgm_rational_roots",dict(a=-1,b=9)),
      ("ellipse_tangent",dict(a=2,b=1,x0=0,y0=0,x=2,y=0)),
      ("line_circle",dict(A=0,B=0,C=1,cx=0,cy=0,r=1)),
      ("parabola_focus",dict(p=0,x=0,y=0)),
      ("quotient_polynomial_derivative",dict(u=[1,2],v=[-1,1],x=1)),
    ]
    for op,data in cases:
        assert evaluate(op,data)["status"]=="CONDITIONS_NOT_ESTABLISHED",(op,data)
