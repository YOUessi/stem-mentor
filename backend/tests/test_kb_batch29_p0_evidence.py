"""Batch29: negative gates and independent exact property checks for 48 new P0 editorial reviews."""
import copy
import json
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path

import pytest
import sympy as sp
from app.kb_batch29_exact_witnesses import SUPPORTED,evaluate

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch29_p0_evidence as build

MANIFEST=json.loads(build.MANIFEST.read_text(encoding="utf8"))
REPORT=json.loads(build.REPORT.read_text(encoding="utf8"))

def exact(op,data):
    out=evaluate(op,data)
    assert out["status"]=="VERIFIED_FINITE_INSTANCE",out
    assert all(out[k] is False for k in ("complete_theorem_certified","student_step_verified",
                                      "teacher_approved","official_curriculum_atom_verified"))
    return out["witness"]

def test_all_127_step_hashes_and_48_new_subclaims_are_reproducible():
    assert json.loads(build.build())==REPORT
    q=REPORT["summary"]
    assert q["total_historical_p0"]==127
    assert (q["previously_curated_p0"],q["newly_curated_p0"],q["still_missing_curated_conditions"])==(35,48,44)
    assert q["total_with_editorial_condition_proposals"]==83
    assert q["formally_certified_historical_steps"]==q["teacher_approvals"]==q["student_published_lessons"]==0
    assert q["unverified_proof_steps_total"]==538
    assert all(q["official_"+k+"_atom_denominator"] is None for k in ("compulsory","selective","elective"))
    assert len(REPORT["new_editorial_step_proposals"])==48
    assert len(REPORT["previous_step_ids"])==35
    assert len(REPORT["remaining_unreviewed_step_ids"])==44
    assert len(set(REPORT["previous_step_ids"]) |
               set(REPORT["remaining_unreviewed_step_ids"]) |
               set(r["risk_step_id"] for r in REPORT["new_editorial_step_proposals"]))==127

@pytest.mark.parametrize("p",MANIFEST["profiles"],ids=lambda x:x["operation"])
def test_20_original_math_domain_profiles_have_positive_and_refusal(p):
    good=evaluate(p["operation"],p["valid_exact_fixture"])
    bad=evaluate(p["operation"],p["invalid_fixture"])
    assert good["status"]=="VERIFIED_FINITE_INSTANCE"
    assert bad["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert p["teacher_review"]=="PENDING"
    assert p["status"]=="EDITORIAL_CONDITION_PROPOSAL_NOT_PROOF"
    assert all(good[x] is False and bad[x] is False for x in ("teacher_approved","complete_theorem_certified","student_step_verified","official_curriculum_atom_verified"))

@pytest.mark.parametrize("record",REPORT["new_editorial_step_proposals"],ids=lambda x:x["risk_step_id"])
def test_each_of_48_frozen_original_steps_requires_teacher_and_proof_review(record):
    assert len(record["claim_reason_sha256"])==64
    assert len(record["source_claim"])>=12
    assert len(record["source_reason"])>=12
    assert record["math_status"]=="BOUNDED_EXACT_WITNESSES_ONLY_NOT_PROOF"
    assert record["proof_status"]=="NOT_FORMALLY_VERIFIED"
    assert record["teacher_review"]=="PENDING"
    assert record["human_math_review"]=="PENDING"
    assert record["student_publishable"] is False
    assert record["complete_proof_certified"] is False

@pytest.mark.parametrize("mutation",["review","proof","student","duplicate","prior-overlap","fake","remove","empty","unknown"])
def test_mutations_cannot_promote_or_forge_48_historical_steps(mutation):
    m=copy.deepcopy(MANIFEST)
    if mutation=="review":m["teacher_review"]="APPROVED"
    elif mutation=="proof":m["complete_proof_certificates"]=48
    elif mutation=="student":m["student_visibility"]="STUDENT"
    elif mutation=="duplicate":m["profiles"][1]["risk_step_ids"].append(m["profiles"][0]["risk_step_ids"][0])
    elif mutation=="prior-overlap":m["profiles"][0]["risk_step_ids"][0]="math.hs.logarithm.product-law#1"
    elif mutation=="fake":m["profiles"][0]["risk_step_ids"][0]="math.hs.fake#1"
    elif mutation=="remove":m["profiles"][0]["risk_step_ids"].pop()
    elif mutation=="empty":m["profiles"][0]["explanatory_counterexample"]=""
    elif mutation=="unknown":m["profiles"][0]["operation"]="eval_arbitrary"
    with pytest.raises(ValueError):build.build(manifest=m)

def test_original_source_sha_tampering_is_blocked():
    h=build.load(build.HISTORY)
    h["p0_review_queue"][0]["verified_original_step_sha256"]="x"*64
    # First risk may not be in this batch; mutate an assuredly covered source step.
    risk_id=REPORT["new_editorial_step_proposals"][0]["risk_step_id"]
    for r in h["p0_review_queue"]:
        if r["id"]==risk_id:r["verified_original_step_sha256"]="x"*64
    with pytest.raises(ValueError):build.build(history=h)

def test_old_35_step_partition_cannot_be_rewritten():
    p=build.load(build.PREVIOUS)
    p["unresolved_p0_step_ids"].pop()
    with pytest.raises(ValueError):build.build(previous=p)

@pytest.mark.parametrize("u,v",list(product(product(range(-2,3),repeat=2),repeat=2)))
def test_metric_polynomial_expansion_exact_with_zero_vectors(u,v):
    w=exact("metric_expansion",dict(u=list(u),v=list(v)))
    nu=sum(a*a for a in u);nv=sum(a*a for a in v);dot=sum(a*b for a,b in zip(u,v))
    assert F(w["plus_norm2"])==nu+nv+2*dot
    assert F(w["minus_norm2"])==nu+nv-2*dot
    assert w["pythagorean_iff"]==(dot==0)
    assert w["parallelogram"] is True

@pytest.mark.parametrize("a,b,c,x",[(a,b,c,x) for a,b,c,x in product((-2,-1,0,1,2),repeat=4) if a])
def test_quadratic_completion_identity_using_sympy(a,b,c,x):
    w=exact("quadratic_vertex",dict(a=a,b=b,c=c,x=x))
    assert sp.Rational(w["value"])==sp.Rational(w["completed_square"])==a*x*x+b*x+c
    assert sp.Rational(w["vertex"])==sp.Rational(-b,2*a)
    assert sp.Rational(w["extremal_value"])==sp.Rational(4*a*c-b*b,4*a)

@pytest.mark.parametrize("a,b,c,d",[(a,b,c,d) for a,b,c,d in product((-2,-1,0,1,2),repeat=4) if c or d])
def test_complex_quotient_reconstructs_dividend_over_exact_gaussian_rationals(a,b,c,d):
    w=exact("complex_quotient",dict(a=a,b=b,c=c,d=d))
    assert F(w["product_re"])==a and F(w["product_im"])==b
    assert sp.simplify(sp.Rational(w["real"])+sp.I*sp.Rational(w["imag"])-(a+b*sp.I)/(c+d*sp.I))==0

@pytest.mark.parametrize("a,b",list(product(product(range(-2,3),repeat=2),repeat=2)))
def test_nonzero_projection_residual_orthogonality_and_pythagoras(a,b):
    if b==(0,0):
        assert evaluate("vector_projection",dict(a=list(a),b=list(b)))["status"]=="CONDITIONS_NOT_ESTABLISHED"
        return
    w=exact("vector_projection",dict(a=list(a),b=list(b)))
    pp=[F(v) for v in w["projection"]]
    assert sum((pp[i]*b[i] for i in range(2)),F(0))==sum(a[i]*b[i] for i in range(2))
    assert F(w["residual_dot_direction"])==0
    assert sum(a[i]*a[i] for i in range(2))==sum(z*z for z in pp)+F(w["residual_squared"])

@pytest.mark.parametrize("n,q,a",[(n,q,a) for n,q,a in product(range(1,17),(-2,-1,0,1,2),(-2,0,3))])
def test_geometric_and_arithmetic_series_plus_square_sum_exact(n,q,a):
    w=exact("finite_series",dict(n=n,q=q,a=a,diff=3))
    assert F(w["geometric"])==F(w["geometric_closed"])
    assert F(w["arithmetic"])==F(w["arithmetic_closed"])
    assert int(w["square_sum"])==int(w["square_closed"])==sum(k*k for k in range(1,n+1))

@pytest.mark.parametrize("A,B,C,D",[(A,B,C,D) for A,B,C,D in product((-1,0,1),repeat=4) if (A or B) and (C or D)])
def test_line_normal_parallel_and_perpendicular_determinants(A,B,C,D):
    w=exact("line_relations",dict(A=A,B=B,C=C,D=D))
    assert w["parallel"]==(A*D-B*C==0)
    assert w["perpendicular"]==(A*C+B*D==0)

@pytest.mark.parametrize("x,y,p",[(x,y,p) for x,y,p in product(range(-2,3),range(-2,3),(1,2,3))])
def test_point_line_distance_against_sympy(x,y,p):
    w=exact("point_line_distance",dict(A=p,B=1,C=-2,x=x,y=y))
    assert sp.Rational(w["distance_squared"])==sp.Rational((p*x+y-2)**2,p*p+1)

@pytest.mark.parametrize("x",range(-5,6))
@pytest.mark.parametrize("a",[-3,-1,1,3])
def test_quadratic_sign_outside_inside_and_roots(x,a):
    w=exact("quadratic_sign",dict(a=a,r1=-2,r2=3,x=x))
    v=a*(x+2)*(x-3)
    assert F(w["value"])==v
    if x in (-2,3):assert w["sign_matches_leading"] is None
    else:assert w["sign_matches_leading"]==(x<-2 or x>3)

@pytest.mark.parametrize("A,B",[(A,B) for A,B in product((-2,-1,0,1,2),repeat=2) if A or B])
def test_line_general_nonzero_normal_is_real_line(A,B):
    w=exact("line_general",dict(A=A,B=B,x0=1,y0=2,x=1+B,y=2-A))
    assert w["point_on_line"] is True
    assert F(w["evaluation"])==0

@pytest.mark.parametrize("weights",[
    ["1/2","1/2","0"],["1/3","1/3","1/3"],["0","1/2","1/2"],
])
@pytest.mark.parametrize("A",[[0],[1],[2],[0,1],[1,2],[0,2],[0,1,2]])
@pytest.mark.parametrize("B",[[0],[1],[2],[0,1],[1,2],[0,2],[0,1,2]])
def test_conditional_probability_multiplies_only_for_positive_denominator(weights,A,B):
    pa=sum(F(weights[i]) for i in A)
    r=evaluate("conditional_probability",dict(weights=weights,A=A,B=B))
    if pa==0:assert r["status"]=="CONDITIONS_NOT_ESTABLISHED"
    else:
        assert r["status"]=="VERIFIED_FINITE_INSTANCE"
        w=r["witness"]
        assert F(w["p_b_given_a"])*pa==sum((F(weights[i]) for i in set(A)&set(B)),F(0))

@pytest.mark.parametrize("a,b,c,d",[(a,b,c,d) for a,b,c,d in product((-2,-1,0,1,2),repeat=4) if a*d-b*c])
def test_matrix_inverse_sympy_exact(a,b,c,d):
    w=exact("matrix_inverse_2",dict(a=a,b=b,c=c,d=d))
    assert [F(x) for x in w["left_identity"]]==[1,0,0,1]
    mat=sp.Matrix([[a,b],[c,d]])
    inv=mat.inv()
    assert [sp.Rational(x) for x in w["inverse"]]==list(inv)

@pytest.mark.parametrize("d",[
    dict(u=[0,0,1],v=[1,0,0],w=[0,1,0]),
    dict(u=[1,0,0],v=[0,1,0],w=[0,0,1]),
    dict(u=[0,1,0],v=[1,0,0],w=[0,0,1]),
])
def test_plane_spanning_independence_and_zero_dot_products(d):
    w=exact("plane_perpendicular",d)
    assert w["u_parallel_plane_normal"] is True
    assert F(w["plane_direction_cross_norm2"])>0

def test_invalid_conditions_do_not_claim_mathematical_falsehoods_as_proofs():
    cases=[
       ("metric_expansion",{"u":[1,2],"v":[1,2,3]}),
       ("quadratic_vertex",{"a":0,"b":3,"c":2,"x":1}),
       ("point_line_distance",{"A":0,"B":0,"C":1,"x":0,"y":0}),
       ("finite_composition",{"f":{"1":1},"g":{"2":9},"x":2}),
       ("ellipse_parametric",{"a":0,"b":2,"c":1,"s":0}),
       ("orthogonal_isometry",{"Q":[[2,0],[0,1]],"u":[1,2]}),
    ]
    for op,args in cases:
        r=evaluate(op,args)
        assert r["status"]=="CONDITIONS_NOT_ESTABLISHED"
        assert not r["student_step_verified"] and not r["complete_theorem_certified"]

def test_all_287_existing_lessons_remain_teacher_only_without_releasing_this_manifest():
    from scripts.kb_frozen_batch24 import frozen_batch24_lessons
    data=frozen_batch24_lessons()
    assert len(data)==287
    assert all(x.review.status=="REVIEW_PENDING" and x.teacher_solution_visibility=="TEACHER_ONLY" for x in data)
    # These editorial files live outside knowledge/deep and are never accepted as published lessons.
    assert not any("batch29" in x.id for x in data)
