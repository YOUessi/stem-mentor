"""Independent exact checks for Batch14 elective A/B proof *subclaims*.

These are bounded mathematical oracles: they do not certify all 364 proof
obligations or authorize student evidence. No LLM is used as its own judge.
"""
from __future__ import annotations
import copy
from fractions import Fraction
from itertools import product
from pathlib import Path
import json
import pytest
import sympy as sp
from pydantic import ValidationError
from app.deep_knowledge import DeepLesson, lessons, curriculum, coverage_report
from app.objective_proposals import editorial_review_queue, validate_proposals
from app.deep_retrieval import student_evidence_lookup

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"curriculum/highschool_math/author_draft_batch14.json"
COURSE=ROOT/"curriculum/highschool_math/elective_a_b_atomic_candidates_batch14.json"
BATCH=json.loads(SRC.read_text(encoding="utf8"))
COURSE_ROWS=json.loads(COURSE.read_text(encoding="utf8"))
IDS={x["id"] for x in BATCH}

def test_elective_candidates_have_distinct_engineering_ids_and_real_objective_targets():
    from app.standard_scope import source_inventory
    official_candidates={x["id"]:x for x in source_inventory()["items"]}
    assert len(BATCH)==len(COURSE_ROWS)==16
    assert len(IDS)==16 and len({x["id"] for x in COURSE_ROWS})==16
    assert set(x["curriculum_ids"][0] for x in BATCH)==set(x["id"] for x in COURSE_ROWS)
    for x in COURSE_ROWS:
        obj=official_candidates[x["editorial_objective_id"]]
        assert obj["track"]==x["elective_track"]
        assert x["level"]=="选修拓展"
        assert x["source"]["teacher_review"]=="PENDING"
    assert len(curriculum())==161

def test_source_schema_mathematical_proof_obligations_are_not_approvals():
    assert len(lessons())==224
    for d in BATCH:
        item=DeepLesson.model_validate(d)
        assert item.kind=="theorem" and len(item.proof_steps)>=3
        assert len(item.worked_examples)>=2 and len(item.hint_ladder)>=3
        assert len(item.counterexamples)>=1
        assert item.review.status=="REVIEW_PENDING"
        assert item.teacher_solution_visibility=="TEACHER_ONLY"
        assert all(len(z.claim)>=12 and len(z.reason)>=12 for z in item.proof_steps)

@pytest.mark.parametrize("bad",["APPROVED","STUDENT_VISIBLE"])
def test_new_drafts_cannot_promote_to_student_authority(bad):
    doc=copy.deepcopy(BATCH[0])
    if bad=="APPROVED": doc["review"]["status"]=bad
    else: doc["teacher_solution_visibility"]=bad
    with pytest.raises(ValidationError):
        DeepLesson.model_validate(doc)

def test_16_editorial_proposals_still_do_not_certify_any_objective():
    d=editorial_review_queue()
    assert len(d["items"])==132
    assert d["total_deep_draft_lessons"]==224
    assert d["official_atomic_denominator"] is None
    assert d["official_coverage_percent"] is None
    assert d["independent_teacher_approved_matches"]==0
    assert d["student_published_knowledge_count"]==0
    assert validate_proposals(d)
    proposals={x["lesson_id"] for row in d["items"] for x in row["proposed_deep_lessons"]}
    assert IDS.issubset(proposals)
    assert student_evidence_lookup("数列极限的严格 epsilon N 证明")["status"]=="NO_APPROVED_EVIDENCE"

@pytest.mark.parametrize("eps",[Fraction(1,1000),Fraction(1,101),Fraction(1,10),Fraction(1,3),Fraction(2,1)])
def test_epsilon_n_1_over_n(eps):
    N=int(Fraction(1,1)/eps)+1
    for n in range(N,N+30):
        assert Fraction(1,n)<eps

@pytest.mark.parametrize("n",range(1,90))
def test_bounded_monotone_sequence_has_correct_obvious_example(n):
    a=Fraction(n-1,n)
    b=Fraction(n,n+1)
    assert a<=b<1
    assert abs(Fraction(1,n))<=1

@pytest.mark.parametrize("a,eps",list(product([-4,-1,0,2,100],[Fraction(1,10),Fraction(1,101),Fraction(3,2)])))
def test_square_limit_epsilon_delta_sampled_points(a,eps):
    delta=min(Fraction(1,1),eps/Fraction(1+2*abs(a),1))
    for sign in [-1,1]:
        x=Fraction(a,1)+sign*delta/Fraction(2,1)
        assert 0<abs(x-a)<delta
        assert abs(x*x-a*a)<eps

@pytest.mark.parametrize("a,b",[(a,b) for a in range(-5,5) for b in range(a+1,6)])
def test_mean_value_quadratic_slope(a,b):
    c=Fraction(a+b,2)
    secant=Fraction(b*b-a*a,b-a)
    assert a<c<b
    assert 2*c==secant

@pytest.mark.parametrize("n",range(1,75))
def test_riemann_left_right_sums_bracket_area(n):
    b=sp.Rational(3,2)
    left=b**2*sp.Rational(n-1,2*n)
    right=b**2*sp.Rational(n+1,2*n)
    assert left<=b**2/2<=right
    assert sp.simplify(right-left-b**2/n)==0

def test_exact_riemann_limit_ftc_and_partials():
    n,t,x,y=sp.symbols("n t x y",integer=True,positive=True)
    assert sp.limit(sp.Rational(1,2)*(n+1)/n,n,sp.oo)==sp.Rational(1,2)
    F=sp.integrate(t*t,(t,0,x))
    assert sp.simplify(sp.diff(F,x)-x*x)==0
    f=x*x*y+3*y*y
    assert sp.diff(f,x)==2*x*y
    assert sp.diff(f,y)==x*x+6*y

@pytest.mark.parametrize("a,b,c,d",product([-2,-1,0,1,2],repeat=4))
def test_2x2_inverse_or_singular_exact(a,b,c,d):
    A=sp.Matrix([[a,b],[c,d]])
    delta=a*d-b*c
    assert A.det()==delta
    if delta:
        B=sp.Matrix([[d,-b],[-c,a]])/delta
        assert A*B==sp.eye(2) and B*A==sp.eye(2)
    else:
        assert A.rank()<2

@pytest.mark.parametrize("scale",[-3,-1,1,2,5])
def test_gaussian_elementary_operations_preserve_solution_set(scale):
    x,y=sp.symbols("x y")
    E=[x+y-3, x-y-1]
    original=sp.linsolve(E,[x,y])
    assert sp.linsolve([E[1],E[0]],[x,y])==original
    assert sp.linsolve([scale*E[0],E[1]],[x,y])==original
    assert sp.linsolve([E[0],E[1]+scale*E[0]],[x,y])==original
    assert original==sp.FiniteSet((2,1))

def test_covariance_affine_and_uncorrelated_not_independent():
    sample=[-1,0,1]
    mean=lambda v:sp.Rational(sum(v),len(v))
    cov=lambda X,Y:sum((x-mean(X))*(y-mean(Y)) for x,y in zip(X,Y))/len(X)
    X=sample;Y=[x*x for x in X]
    assert cov(X,Y)==0
    assert cov([3*x+2 for x in X],[-2*y+1 for y in Y])==-6*cov(X,Y)
    Z=[0,1];W=[1,0]
    assert cov(Z,W)==-sp.Rational(1,4)

@pytest.mark.parametrize("n,k",[(n,k) for n in range(1,14) for k in range(n+1)])
def test_bernoulli_mle_bounded_rational_grid(n,k):
    optimum=sp.Rational(k,n)
    likelihood=lambda p:p**k*(1-p)**(n-k)
    best=likelihood(optimum)
    for j in range(0,n*4+1):
        p=sp.Rational(j,n*4)
        assert best>=likelihood(p)
    if 0<k<n:
        p=sp.symbols("p",positive=True)
        score=k/p-(n-k)/(1-p)
        assert sp.simplify(score.subs(p,optimum))==0
    else:
        assert optimum in (0,1)

def test_ivt_and_inverse_direction_counterexample():
    f=lambda x:x*x*x-2
    assert f(1)<0 and f(2)>0
    # These endpoint signs require interval continuity; a jump need not hit 0.
    g=lambda x:-1 if x<0 else 1
    assert g(-1)<0<g(1)
    assert not any(g(sp.Rational(i,10))==0 for i in range(-20,21))

def test_whole_proof_status_remains_uncertified():
    r=coverage_report()
    assert r["kinds"]["theorem"]==136
    assert all(d.review.status=="REVIEW_PENDING" for d in lessons())
    assert not r["human_teacher_review_complete"]
    assert not r["direct_student_teaching_enabled"]
