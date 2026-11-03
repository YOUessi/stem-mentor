"""Batch16: independent exact bounded subclaims, not natural-language proof certification."""
from __future__ import annotations
import copy
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import pytest
import sympy as sp
from pydantic import ValidationError
from app.deep_knowledge import DeepLesson, lessons, curriculum
from app.objective_proposals import editorial_review_queue, validate_proposals
from app.deep_retrieval import student_evidence_lookup

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"curriculum/highschool_math/author_draft_batch16.json"
TARGETS=ROOT/"curriculum/highschool_math/elective_b_c_d_e_atomic_candidates_batch16.json"
ROWS=json.loads(SRC.read_text(encoding="utf8"))
MAP=json.loads(TARGETS.read_text(encoding="utf8"))

def test_all_twelve_editorial_drafts_are_structurally_valid_and_unapproved():
    assert len(ROWS)==len(MAP)==12
    assert len(lessons())==224 and len(curriculum())==161
    assert {x["id"] for x in MAP}=={r["curriculum_ids"][0] for r in ROWS}
    assert len({r["id"] for r in ROWS})==12
    assert {r["curriculum_ids"][0] for r in ROWS}=={"HS-MATH-"+str(n) for n in range(139,151)}
    assert {r["id"] for r in ROWS}.issubset({r.id for r in lessons()})
    for r in ROWS:
        doc=DeepLesson.model_validate(r)
        assert doc.kind=="theorem" and doc.review.status=="REVIEW_PENDING"
        assert doc.review.reviewer_id is None
        assert doc.teacher_solution_visibility=="TEACHER_ONLY"
        assert len(doc.proof_steps)>=3 and len(doc.worked_examples)==2
        assert all(e.check and len(e.steps)>=2 for e in doc.worked_examples)
    for x in MAP:
        assert x["source"]["teacher_review"]=="PENDING"
        assert x["source"]["mapping_type"]=="ENGINEERING_INTERPRETATION"
        assert x["editorial_objective_id"].startswith("HS-STD2020-ELECTIVE_")

def test_proposal_scope_is_clearly_unverified_and_no_student_data_released():
    a=editorial_review_queue()
    assert validate_proposals(a)
    assert a["total_source_objective_candidates"]==132
    assert a["total_deep_draft_lessons"]==224
    assert a["proposed_objectives"]==132 and a["proposed_edges"]==154
    assert sum(x["without_suggestion"] for x in a["by_track"].values())==0
    assert a["official_atomic_denominator"] is None
    assert a["official_coverage_percent"] is None
    assert a["independent_teacher_approved_matches"]==0
    assert a["student_published_knowledge_count"]==0
    assert student_evidence_lookup("逻辑斯蒂复利与平均律")["status"]=="NO_APPROVED_EVIDENCE"

def test_payload_cannot_self_approve_or_expose_teacher_solution():
    v=copy.deepcopy(ROWS[0])
    v["review"]["status"]="APPROVED"
    v["review"]["reviewer_id"]="fake"
    v["review"]["reviewed_at"]="2026-11-03"
    v["review"]["review_record"]="author signature"
    with pytest.raises(ValidationError):DeepLesson.model_validate(v)
    v=copy.deepcopy(ROWS[1])
    v["teacher_solution_visibility"]="STUDENT_VISIBLE"
    with pytest.raises(ValidationError):DeepLesson.model_validate(v)

@pytest.mark.parametrize("n",range(1,51))
def test_sequence_continuity_x_square(n):
    x=F(3)+F(1,n)
    assert abs(x*x-9)==F(6,n)+F(1,n*n)
    assert x*x>=9

@pytest.mark.parametrize("x,y",product(range(-4,5),repeat=2))
def test_second_derivative_convexity_jensen_exact(x,y):
    x,y=F(x),F(y)
    for lam in (F(0),F(1,4),F(1,2),F(3,4),F(1)):
        lhs=(lam*x+(1-lam)*y)**2
        rhs=lam*x*x+(1-lam)*y*y
        assert rhs-lhs==lam*(1-lam)*(x-y)**2>=0
    # Strict convexity does not require f''(0)>0 for f=x^4.
    assert sp.diff(sp.Symbol("u")**4,sp.Symbol("u"),2).subs("u",0)==0

@pytest.mark.parametrize("a,b",product(range(0,5),range(1,6)))
def test_integral_nonnegative_polynomial_area(a,b):
    if a>b:return
    x=sp.Symbol("x",real=True)
    assert sp.integrate(x,(x,a,b))==sp.Rational(b*b-a*a,2)
    assert sp.Rational(b*b-a*a,2)>=0

@pytest.mark.parametrize("scale",range(1,31))
def test_rescale_time_linear_quadratic_and_exponential(scale):
    u=sp.Symbol("u", real=True)
    t=sp.Symbol("t", real=True)
    a,b,c=sp.symbols("a b c",real=True)
    assert sp.expand((a*t*t+b*t+c).subs(t,scale*u))==a*scale**2*u*u+b*scale*u+c
    assert sp.exp(2*t).subs(t,scale*u)==sp.exp(2*scale*u)

@pytest.mark.parametrize("r,m,cycles",product((F(0),F(1,10),F(1,5)),(1,2,4),(0,1,3)))
def test_compound_interest_recurrence_equals_power(r,m,cycles):
    i=r/m
    v=F(100)
    for _ in range(cycles):
        v*=1+i
    assert v==F(100)*(1+i)**cycles
    if cycles==m:
        assert v/F(100)-1==(1+r/m)**m-1

@pytest.mark.parametrize("a,b,c,d1,d2",product((F(0),F(1,3),F(1,2)),(F(0),F(1,4)),(F(0),F(1,2)),(F(0),F(2)),(F(0),F(3))))
def test_triangular_io_solution_and_nonnegative(a,b,c,d1,d2):
    x2=d2/(1-b)
    x1=(d1+c*x2)/(1-a)
    assert x1>=0 and x2>=0
    assert x1==a*x1+c*x2+d1
    assert x2==b*x2+d2
    assert (1-a)*(1-b)>0

@pytest.mark.parametrize("r,u0",product(range(0,11),repeat=2))
def test_logistic_interval_invariant_exact(r,u0):
    r,u=F(r,10),F(u0,10)
    for _ in range(5):
        nxt=u+r*u*(1-u)
        assert 0<=u<=nxt<=1
        u=nxt
def test_logistic_large_r_breaks_interval():
    assert F(3,5)+F(3)*F(3,5)*F(2,5)==F(33,25)>1

@pytest.mark.parametrize("x,y",product(range(-4,5),repeat=2))
def test_rotation_90_distance_and_orthogonality(x,y):
    x,y=F(x),F(y)
    R=sp.Matrix([[0,-1],[1,0]])
    v=sp.Matrix([x,y])
    assert R.T*R==sp.eye(2)
    assert (R*v).dot(R*v)==v.dot(v)
    assert (R*v)==sp.Matrix([-y,x])

@pytest.mark.parametrize("n",range(1,26))
def test_fibonacci_binet_and_ratio_approximation(n):
    vals=[0,1,1]
    for _ in range(3,n+3):vals.append(vals[-1]+vals[-2])
    a,b=vals[n],vals[n+1]
    assert a>0 and b>0
    phi=(1+sp.sqrt(5))/2;psi=(1-sp.sqrt(5))/2
    assert sp.simplify((phi**n-psi**n)/sp.sqrt(5)-a)==0
    # Exact identity: F_(n+1)/F_n - phi = psi**n/F_n; bound decays exponentially.
    assert sp.simplify((sp.Rational(b,a)-phi) - psi**n/a)==0
    assert sp.simplify(abs(psi)**n)<1

@pytest.mark.parametrize("n",range(-16,17))
def test_equal_temperament_octave_relation(n):
    f0=sp.Integer(440)
    f=lambda k:f0*2**sp.Rational(k,12)
    assert sp.simplify(f(n+12)/f(n)-2)==0
    assert f(n)>0

@pytest.mark.parametrize("a,b",product(range(4),repeat=2))
def test_square_rotation_group_law(a,b):
    assert (a+b)%4 in range(4)
    assert (a+(4-a)%4)%4==0
    assert ((a+b)%4+3)%4==(a+(b+3)%4)%4

@pytest.mark.parametrize("n,i",product(range(1,8),(F(0),F(1,20),F(1,10),F(1,3),F(-1,10))))
def test_annuity_exact_geometric_and_zero_interest(n,i):
    C=F(110)
    direct=sum((C/(1+i)**k for k in range(1,n+1)),F(0))
    closed=(C*(1-(1+i)**(-n))/i if i else C*n)
    assert direct==closed
    shifted=sum((C/(1+i)**(k-1) for k in range(1,n+1)),F(0))
    assert shifted==(1+i)*direct

def test_negative_examples_are_not_promoted_to_positive_claims():
    assert F(110,1)/F(11,10)+F(110,1)/(F(11,10)**2)==F(2100,11)
    assert F(100)*F(101,100)**12>F(112)
    assert sum((x-F(1) for x in (F(0),F(1),F(2))),F(0))==0
    assert (F(3,5)+3*F(3,5)*F(2,5))>1
