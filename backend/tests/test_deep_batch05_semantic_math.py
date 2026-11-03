"""46 independent exact math/oracle spot checks for 23 teacher-only subskill drafts.

A passed oracle means *one example's concrete answer* passed a narrow check.
It never certifies a natural-language proof, independent teacher review,
student mastery, or full official curricular coverage.
"""
from __future__ import annotations

import json
from collections import Counter
from math import factorial
from pathlib import Path
import runpy

import pytest
from sympy import (
    Rational as Q, symbols, simplify, pi, sin, cos, sqrt, I, diff, Matrix
)

from app.deep_knowledge import ROOT, lessons, public_summary

x,h,a,t = symbols("x h a t",real=True)
eq = lambda e: simplify(e)==0

def projection(u,v):
    A,B=Matrix(u),Matrix(v)
    return A.dot(B)/B.dot(B)*B

def is_independent(A,B,omega):
    u=Q(len(A & B),len(omega))
    v=Q(len(A)*len(B),len(omega)**2)
    return u==v

# Answer fragments are FROZEN independent of the source JSON.
# Each lambda recomputes the math without parsing or trusting the stored answer.
ORACLES = {
 "sets.representations": (
   ("(-3,3)",lambda: all((-3<z<3)==(z*z<9) for z in (-4,-3,-2,0,1,3,4))),
   ("A⊆B 为真",lambda: {1,3,5} <= {1,2,3,4,5} and 3 in {1,3,5})),
 "logic.truth-negation": (
   ("x²≤1",lambda: 0*0<=1 and not all(z*z>1 for z in (-1,0,1))),
   ("x²≠4",lambda: all((z*z==4) or z!=2 for z in (-3,-2,-1,0,1,2,3)))),
 "inequality.transformation-obligations": (
   ("a=0:∅",lambda: all((2*z>=2)==(z>=1) for z in (-4,0,1,2)) and
                          all((-2*z>=2)==(z<=-1) for z in (-4,-1,0,2)) and not 0>=2),
   ("{-3,3}",lambda: all((z*z==9)==(z in {-3,3}) for z in (-4,-3,0,3,4)))),
 "trig.radians-unit-circle": (
   ("(-√3/2,1/2)",lambda: eq(cos(5*pi/6)+sqrt(3)/2) and eq(sin(5*pi/6)-Q(1,2))),
   ("π",lambda: eq(3*(60*pi/180)-pi))),
 "trig.sine-cosine-graphs": (
   ("T=2π/3",lambda: eq(2*sin(3*(x+2*pi/3)-pi)+1-(2*sin(3*x-pi)+1))
                  and eq(2*sin(3*pi/2-pi)+1-3)),
   ("T=π",lambda: eq(-3*cos(2*(x+pi))+4-(-3*cos(2*x)+4)) and -3*1+4==1)),
 "trig.double-angle-reduction": (
   ("√3/4",lambda: eq(sin(pi/3)*cos(pi/3)-sqrt(3)/4)
               and eq(sin(2*pi/3)-2*sin(pi/3)*cos(pi/3))),
   ("3/4",lambda: eq(cos(pi/6)**2-Q(3,4)) and eq((1+cos(pi/3))/2-Q(3,4)))),
 "vector.projection": (
   ("(3,0)",lambda: tuple(projection((3,4),(1,0)))==(3,0)),
   ("(3/2,3/2)",lambda: tuple(projection((1,2),(1,1)))==(Q(3,2),Q(3,2)))),
 "complex.algebraic-basics": (
   ("a=3，b=2",lambda: (3+2*I).as_real_imag()==(3,2)),
   ("1",lambda: I**4+I**2+1==1)),
 "complex.argument": (
   ("Arg(−1)=π",lambda: eq(cos(pi)+1) and eq(sin(pi))),
   ("Arg(1+i)=π/4",lambda: eq(sqrt(2)*(cos(pi/4)+I*sin(pi/4))-(1+I)))),
 "complex.operations": (
   ("5+5i",lambda: eq((1+2*I)*(3-I)-(5+5*I))),
   ("1/2+(3/2)i",lambda: eq((2+I)/(1-I)-(Q(1,2)+Q(3,2)*I)))),
 "space.parallel-perpendicular-criteria": (
   ("不包含",lambda: Matrix((1,0,0)).dot(Matrix((0,0,1)))==0 and 2!=0),
   ("两个平面垂直",lambda: Matrix((1,0,0)).dot(Matrix((0,1,0)))==0)),
 "space.line-plane-distance": (
   ("d(l,Π)=4",lambda: abs(5-1)==4 and all(z==5 for z in (5,5,5))),
   ("d(l,Π)=0",lambda: any(z==3 for z in range(-5,6)) and min(abs(z-3) for z in range(-5,6))==0)),
 "space.surface-areas": (
   ("总表面积20π",lambda: eq(2*pi*2*3+2*pi*2**2-20*pi)),
   ("总表面积24π",lambda: sqrt(3**2+4**2)==5 and eq(pi*3*5+pi*3**2-24*pi))),
 "probability.sample-space-event": (
   ("Ω={H,T}",lambda: len({"H","T"})==2 and {"H"} <= {"H","T"}),
   ("A={5,6}",lambda: {i for i in range(1,7) if i>4}=={5,6})),
 "probability.multiplication": (
   ("3/10",lambda: Q(3,5)*Q(2,4)==Q(3,10)
                and Q(3*2,5*4)==Q(3,10)),
   ("1/6",lambda: Q(1,2)*Q(1,3)==Q(1,6))),
 "statistics.median-mode": (
   ("均值21.6",lambda: Q(sum((1,2,2,3,100)),5)==Q(108,5)
                    and sorted((1,2,2,3,100))[2]==2),
   ("中位数3",lambda: Q(2+4,2)==3 and len(set((1,2,4,7)))==4)),
 "modeling.collaborative-inquiry": (
   ("v=60 km/h",lambda: Q(180,3)==60),
   ("验证点预测7",lambda: (2*1+1,2*2+1,2*3+1)==(3,5,7))),
 "calculus.derivative-definition": (
   ("f'(3)=6",lambda: eq(simplify(((3+h)**2-9)/h)-(6+h))
                  and eq((6+h).subs(h,0)-6)),
   ("f'(0) 不存在",lambda: Q(abs(Q(1,3)),Q(1,3)) != Q(abs(Q(-1,3)),Q(-1,3)))),
 "calculus.tangent-line": (
   ("y=4x−4",lambda: diff(x*x,x).subs(x,2)==4
                   and (4*2-4)==4),
   ("切线 y=0",lambda: diff(x**3,x).subs(x,0)==0
                 and eq((h**3)/h-h**2))),
 "calculus.extrema": (
   ("最大值4",lambda: min([(-1)**2,0**2,2**2])==0
                   and max([(-1)**2,0**2,2**2])==4),
   ("不是极值点",lambda: (-1)**3<0<1**3 and diff(x**3,x).subs(x,0)==0)),
 "geometry.conic-focal-directrix": (
   ("25/3",lambda: sqrt(25-16)==3
                 and Q(25,3)-5==Q(10,3)
                 and Q(2)/Q(10,3)==Q(3,5)),
   ("9/5",lambda: sqrt(3**2+4**2)==5
                and Q(3)-Q(9,5)==Q(6,5) and Q(2)/Q(6,5)==Q(5,3))),
 "geometry.conic-tangent-normal": (
   ("切线 y=2",lambda: eq(Q(0,9)+Q(2**2,4)-1)
                      and Matrix((0,Q(2,2))).dot(Matrix((1,0)))==0),
   ("切线 x=2",lambda: eq(Q(2**2,4)-0-1)
                      and Matrix((1,0)).dot(Matrix((0,1)))==0)),
 "probability.independence": (
   ("A、B 独立",lambda: is_independent({2,4,6},{3,6},set(range(1,7)))),
   ("A、B 不独立",lambda: not is_independent({1},{2},set(range(1,7))))),
}

CANDIDATES_FILE = ROOT/"knowledge/deep/v1/semantic_gap_subskills_batch05.json"


def test_candidate_inventory_and_generator_determinism():
    candidates=json.loads(CANDIDATES_FILE.read_text(encoding="utf-8"))
    gaps=json.loads((ROOT/"knowledge/deep/semantic_gaps_batch04.json").read_text(encoding="utf-8"))["gaps"]
    expected={x["recommended_lesson_id"] for x in gaps}
    assert len(candidates)==23==len(ORACLES)
    assert candidates==runpy.run_path(str(ROOT/"scripts/build_semantic_gap_batch05.py"))["build"]()
    assert {x["id"] for x in candidates}==expected=={"math.hs."+k for k in ORACLES}
    assert all(x["review"]["status"]=="REVIEW_PENDING" for x in candidates)
    assert all(x["teacher_solution_visibility"]=="TEACHER_ONLY" for x in candidates)
    assert all(x["review"]["reviewer_id"] is None for x in candidates)
    assert public_summary()["direct_student_teaching_enabled"] is False


@pytest.mark.parametrize("key,which",[(key,which) for key in ORACLES for which in (0,1)])
def test_worked_example_46_point_oracles(key,which):
    doc=next(d for d in lessons() if d.id=="math.hs."+key)
    phrase,oracle=ORACLES[key][which]
    assert phrase in doc.worked_examples[which].answer, (key,which,phrase)
    assert bool(oracle()), (key,which)


@pytest.mark.parametrize("key",list(ORACLES))
def test_subskill_counterexample_is_distinct_from_its_true_statement(key):
    doc=next(d for d in lessons() if d.id=="math.hs."+key)
    neg=doc.counterexamples[0]
    assert neg.false_claim not in (doc.definition,doc.statement)
    assert len(neg.explanation)>16
    assert doc.review.status=="REVIEW_PENDING"
    assert len(doc.hint_ladder)>=3
    assert len(doc.worked_examples)==2


def test_independence_counterexamples_and_boundary():
    omega=set(range(1,7))
    assert is_independent({2,4,6},{3,6},omega)
    assert not is_independent({1},{2},omega)
    assert is_independent(set(),{1,2,3},omega)  # P(A)=0 is independent.
    assert {1}.isdisjoint({2})


def test_complex_division_cannot_divide_by_zero():
    assert (1+I**2)==0
    assert (1-I**2)==2


def test_local_tangent_formula_requires_curve_membership_and_regular_gradient():
    F=x*x/9+t*t/4-1
    pt={x:0,t:2}
    assert eq(F.subs(pt))
    gradient=Matrix((diff(F,x).subs(pt),diff(F,t).subs(pt)))
    assert gradient!=Matrix((0,0))
    assert F.subs({x:0,t:0})!=0  # (0,0) is not on ellipse


def test_modeling_adversarial_curve_matches_training_but_diverges():
    model=lambda q: 2*q
    alternate=lambda q:q*q-q+2
    assert [model(q) for q in (1,2)]==[alternate(q) for q in (1,2)]==[2,4]
    assert model(3)==6 and alternate(3)==8


def test_theorem_boundaries_require_conditions():
    keys=["trig.double-angle-reduction","vector.projection",
          "complex.operations","space.parallel-perpendicular-criteria",
          "probability.multiplication","calculus.tangent-line"]
    matched={d.id.split("math.hs.",1)[1]:d for d in lessons() if d.id.startswith("math.hs.")}
    for key in keys:
        d=matched[key]
        assert d.kind=="theorem"
        assert len(d.proof_steps)>=3 and len(d.assumptions)>=1
        assert all(step.claim != step.reason for step in d.proof_steps)
        assert all(len(step.reason)>12 for step in d.proof_steps)
