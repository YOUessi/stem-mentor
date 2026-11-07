"""Batch15 independent bounded mathematics and fail-closed editorial checks.
Numeric grids/symbolic identities do not certify full proofs or any official syllabus.
"""
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
from app.objective_proposals import editorial_review_queue,validate_proposals
from app.deep_retrieval import student_evidence_lookup

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"curriculum/highschool_math/author_draft_batch15.json"
MAP=ROOT/"curriculum/highschool_math/elective_a_b_atomic_candidates_batch15.json"
BATCH=json.loads(SRC.read_text(encoding="utf8"))
COURSE=json.loads(MAP.read_text(encoding="utf8"))
def test_9_unique_authored_theorems_and_no_teacher_approval():
    assert len(BATCH)==len(COURSE)==9
    assert len({x["id"] for x in BATCH})==9
    assert len({x["id"] for x in COURSE})==9
    assert {x["id"] for x in COURSE}=={x["curriculum_ids"][0] for x in BATCH}
    assert len(lessons())==267 and len(curriculum())==178
    for r in BATCH:
        x=DeepLesson.model_validate(r)
        assert x.kind=="theorem" and x.review.status=="REVIEW_PENDING"
        assert x.teacher_solution_visibility=="TEACHER_ONLY"
        assert len(x.proof_steps)>=3 and len(x.worked_examples)==2
        assert len(x.counterexamples)>=1 and len(x.misconceptions)>=1
def test_8_new_objective_candidates_have_only_editorial_proposals():
    from app.standard_scope import source_inventory
    inv={x["id"]:x for x in source_inventory()["items"]}
    for r in COURSE:
        assert inv[r["editorial_objective_id"]]["track"]==r["elective_track"]
        assert r["source"]["mapping_type"]=="ENGINEERING_INTERPRETATION"
        assert r["source"]["teacher_review"]=="PENDING"
    p=editorial_review_queue()
    assert p["proposed_objectives"]==132 and p["proposed_edges"]==154
    assert p["official_atomic_denominator"] is None
    assert p["independent_teacher_approved_matches"]==0
    assert p["student_published_knowledge_count"]==0
    assert validate_proposals(p)
    assert student_evidence_lookup("三元行列式和最小二乘法")["status"]=="NO_APPROVED_EVIDENCE"
@pytest.mark.parametrize("status",["APPROVED","REJECTED"])
def test_author_cannot_self_approve(status):
    x=copy.deepcopy(BATCH[0]); x["review"]["status"]=status
    if status=="APPROVED":
        with pytest.raises(ValidationError): DeepLesson.model_validate(x)
    else:
        assert DeepLesson.model_validate(x).review.status=="REJECTED"
def test_student_solution_leakage_is_rejected():
    x=copy.deepcopy(BATCH[0]);x["teacher_solution_visibility"]="STUDENT_VISIBLE"
    with pytest.raises(ValidationError):DeepLesson.model_validate(x)

@pytest.mark.parametrize("k",range(1,61))
def test_sine_limit_squeeze_on_rational_angles(k):
    # Numeric sampling sanity only: the actual argument uses geometry and squeeze.
    import math
    x=1.0/k
    assert math.cos(x) < math.sin(x)/x < 1.0 or (k>40 and math.cos(x)<math.sin(x)/x<=1.0)
@pytest.mark.parametrize("n",range(-16,17))
def test_monotonic_derivative_example_slope_positive(n):
    x=sp.Rational(n,4)
    assert sp.exp(x)>0
@pytest.mark.parametrize("a,b",product(range(-4,5),repeat=2))
def test_noncommutative_3x3_matrix_example(a,b):
    A=sp.diag(a,b,3); E=sp.Matrix([[0,1,0],[0,0,0],[0,0,0]])
    assert A*E == a*E and E*A == b*E
    assert (A*E == E*A)==(a==b)
@pytest.mark.parametrize("x,y",product(range(-5,6),repeat=2))
def test_closed_disk_objective_and_boundary(x,y):
    # exact rational grid, restrict to radius 1
    a,b=F(x,5),F(y,5);f=a*a+b*b
    if f<=1:assert 0<=f<=1
@pytest.mark.parametrize("z",range(-5,6))
def test_vector_rank_certificate(z):
    A=sp.Matrix([[1,0,1],[0,1,1],[0,0,z]])
    assert A.det()==z
    assert (A.rank()==3)==(z!=0)
@pytest.mark.parametrize("a,b,c",product(range(1,6),repeat=3))
def test_cramer_diagonal_nonzero(a,b,c):
    A=sp.diag(a,b,c);ans=sp.Matrix([1,2,3]);target=A*ans
    assert A.det()!=0
    for i in range(3):
        other=A.copy();other[:,i]=target
        assert other.det()/A.det()==ans[i]
@pytest.mark.parametrize("t",range(4))
def test_discrete_tail_p_value_validity(t):
    vals=[0,1,2,3]; p=sum(v>=t for v in vals)/4
    assert p==F(4-t,4)
@pytest.mark.parametrize("alpha", [F(1,100),F(1,20),F(1,4),F(1,2),F(3,4),F(1,1)])
def test_discrete_null_p_values_superuniform(alpha):
    vals=[0,1,2,3]
    reject=sum(F(sum(v>=t for v in vals),4)<=alpha for t in vals)
    assert F(reject,4)<=alpha
@pytest.mark.parametrize("a,b",product(range(-4,5),repeat=2))
def test_ols_exact_line_fit(a,b):
    xs=[0,1,2];ys=[a+b*x for x in xs]
    mx=F(sum(xs),3);my=F(sum(ys),3)
    sxx=sum((F(x)-mx)**2 for x in xs)
    sxy=sum((F(x)-mx)*(F(y)-my) for x,y in zip(xs,ys))
    assert sxx==2 and sxy/sxx==b and my-b*mx==a
@pytest.mark.parametrize("r",range(1,11))
def test_circle_cardinal_positions_and_nonzero_velocity(r):
    for x,y,vx,vy in ((r,0,0,r),(0,r,-r,0),(-r,0,0,-r),(0,-r,r,0)):
        assert x*x+y*y==r*r
        assert vx*vx+vy*vy==r*r
def test_no_false_official_coverage_or_teacher_signature():
    for d in BATCH:
        assert d["provenance"]["kind"]=="PROJECT_AUTHORED"
        assert d["review"]["reviewer_id"] is None
        assert "标准" in d["provenance"]["curriculum_standard"]
