"""Exact supporting mathematical oracles for Batch10 authored lessons.
Proves only finite instances/identities listed here, not complete prose proofs.
"""
from __future__ import annotations

import itertools
import json
import math
from fractions import Fraction
from pathlib import Path

import pytest
from sympy import Integer, Rational, Symbol, cos, sin, pi, log, simplify

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/"knowledge/deep/v1/algebra_geometry_probability_batch10.json"
EXPECTED_IDS={
 "math.hs.exponent.monotone","math.hs.logarithm.product-law",
 "math.hs.sequence.square-sum","math.hs.sequence.cube-sum",
 "math.hs.vector.parallelogram","math.hs.probability.variance-covariance",
 "math.hs.probability.bernoulli-variance","math.hs.probability.complement-independence",
 "math.hs.geometry.circle-complete-square","math.hs.geometry.ellipse-parameter",
 "math.hs.counting.pascal-identity",
}

def test_batch10_source_is_deterministic_and_teacher_only():
    from backend.app.deep_knowledge import lessons
    from collections import Counter
    import subprocess,sys
    rows=json.loads(DOC.read_text(encoding="utf8"))
    assert {x["id"] for x in rows}==EXPECTED_IDS
    assert len(rows)==len(EXPECTED_IDS)
    assert all(x["review"] == {"status":"REVIEW_PENDING","reviewer_id":None,"reviewed_at":None,"review_record":None} for x in rows)
    assert all(x["teacher_solution_visibility"]=="TEACHER_ONLY" for x in rows)
    assert all(len(x["proof_steps"])>=3 and len(x["worked_examples"])>=2 and len(x["hint_ladder"])>=3 for x in rows)
    assert len({x.id for x in lessons()})==len(lessons())
    assert subprocess.run([sys.executable,str(ROOT/"scripts/build_kb_batch10_lessons.py"),"--check"],
          capture_output=True,check=False).returncode==0

@pytest.mark.parametrize("a", [Fraction(2),Fraction(3),Fraction(1,2),Fraction(1,3),Fraction(3,4)])
@pytest.mark.parametrize("x,y",[(-4,-1),(-2,0),(-1,2),(0,3),(1,4)])
def test_exponential_monotonicity_with_exact_rationals(a,x,y):
    assert x<y
    assert (a**x<a**y) == (a>1)
    assert (a**x>a**y) == (a<1)

@pytest.mark.parametrize("a",[2,3,5,7])
@pytest.mark.parametrize("i,j",list(itertools.product(range(-3,4),range(-3,4))))
def test_log_product_powers_without_float(a,i,j):
    # Choose x=a^i and y=a^j, positive exact rationals
    x=Rational(a)**i; y=Rational(a)**j
    assert x>0 and y>0
    assert simplify(x*y - Rational(a)**(i+j)) == 0
    # Check the actual logarithm expression (not only the underlying powers).
    lhs=log(x*y,a)
    rhs=log(x,a)+log(y,a)
    assert simplify(lhs-rhs)==0
    assert simplify(lhs-(i+j))==0

@pytest.mark.parametrize("n",range(1,71))
def test_sums_of_squares_cubes_against_exact_finite_sum(n):
    assert sum(k*k for k in range(1,n+1)) == n*(n+1)*(2*n+1)//6
    assert sum(k**3 for k in range(1,n+1)) == (n*(n+1)//2)**2

@pytest.mark.parametrize("u,v",list(itertools.product(
 [(0,0),(1,0),(1,2),(-2,4),(3,-1)],
 [(0,0),(1,0),(0,3),(2,-2),(-1,5)])))
def test_parallelogram_identity_two_dimensions(u,v):
    normsq=lambda p:sum(z*z for z in p)
    add=tuple(a+b for a,b in zip(u,v)); sub=tuple(a-b for a,b in zip(u,v))
    assert normsq(add)+normsq(sub)==2*normsq(u)+2*normsq(v)
    assert len(u)==len(v)==2

@pytest.mark.parametrize("p,q",[ (Fraction(i,10),Fraction(j,10)) for i in range(11) for j in range(11)])
def test_variance_covariance_for_two_bernoulli_independent(p,q):
    # Full 4-outcome joint distribution; independent here, but general identity also checked below.
    outcomes=[(x,y,(p if x else 1-p)*(q if y else 1-q)) for x in (0,1) for y in (0,1)]
    assert sum(prob for _,_,prob in outcomes)==1
    ex=sum(x*w for x,y,w in outcomes); ey=sum(y*w for x,y,w in outcomes)
    vx=sum((x-ex)**2*w for x,y,w in outcomes)
    vy=sum((y-ey)**2*w for x,y,w in outcomes)
    cv=sum((x-ex)*(y-ey)*w for x,y,w in outcomes)
    vs=sum(((x+y)-(ex+ey))**2*w for x,y,w in outcomes)
    assert vs==vx+vy+2*cv
    assert cv==0

@pytest.mark.parametrize("p",[Fraction(i,20) for i in range(21)])
def test_bernoulli_variance_exact_including_endpoints(p):
    e=p; e2=p
    assert e2-e*e==p*(1-p)
    assert p*(1-p)<=Fraction(1,4)
    assert (p*(1-p)==0) == (p in (0,1))

@pytest.mark.parametrize("joint",[tuple(map(Fraction, row)) for row in
 ((0,0,1,0),(1,0,0,0),(0,0,0,1),(1,2,3,4),(1,1,1,1),(2,0,0,2),(1,0,0,1))])
def test_general_variance_covariance_for_dependent_joint(joint):
    total=sum(joint)
    assert total>0
    pts=list(itertools.product((0,1),repeat=2))
    weights=[x/total for x in joint]
    ex=sum(x*w for (x,y),w in zip(pts,weights))
    ey=sum(y*w for (x,y),w in zip(pts,weights))
    vx=sum((x-ex)**2*w for (x,y),w in zip(pts,weights))
    vy=sum((y-ey)**2*w for (x,y),w in zip(pts,weights))
    cov=sum((x-ex)*(y-ey)*w for (x,y),w in zip(pts,weights))
    summ=sum((x+y-ex-ey)**2*w for (x,y),w in zip(pts,weights))
    assert summ==vx+vy+2*cov

@pytest.mark.parametrize("a,b",itertools.product(range(1,15),repeat=2))
def test_complement_independence_over_finite_counting_spaces(a,b):
    # Ω has 14×14 equiprobable outcomes, A iff x<a, B iff y<b
    n=14
    assert a<=n and b<=n
    omega=[(x,y) for x in range(n) for y in range(n)]
    event_a=lambda x,y: x<a
    event_b=lambda x,y: y<b
    def prob(predicate):
        return Fraction(sum(bool(predicate(x,y)) for x,y in omega),len(omega))
    for aa,bb in ((True,True),(False,True),(True,False),(False,False)):
        A=lambda x,y: event_a(x,y) if aa else not event_a(x,y)
        B=lambda x,y: event_b(x,y) if bb else not event_b(x,y)
        assert prob(lambda x,y:A(x,y) and B(x,y)) == prob(A)*prob(B)

@pytest.mark.parametrize("d,e,f",list(itertools.product(range(-3,4,2),range(-3,4,2),range(-3,4))))
def test_complete_square_equivalence(d,e,f):
    x,y=Symbol("x"),Symbol("y")
    r2=Rational(d*d+e*e,4)-f
    original=x*x+y*y+d*x+e*y+f
    # use exact Rational not floating half
    exact=(x+Rational(d,2))**2+(y+Rational(e,2))**2-r2
    assert simplify(exact-original)==0

@pytest.mark.parametrize("a,b,t",[(a,b,t) for a in (1,2,3) for b in (1,2,4) for t in (0,pi/2,pi,3*pi/2)])
def test_ellipse_parametric_special_angles_exact(a,b,t):
    xx=a*cos(t); yy=b*sin(t)
    assert simplify(xx**2/(a*a)+yy**2/(b*b)-1)==0

@pytest.mark.parametrize("n",range(2,46))
def test_pascal_recurrence_for_every_interior_k(n):
    for k in range(1,n):
        assert math.comb(n,k)==math.comb(n-1,k-1)+math.comb(n-1,k)

def test_zero_covariance_does_not_imply_independence():
    points=(-1,0,1)
    weights=(Fraction(1,3),)*3
    xmean=sum(w*x for x,w in zip(points,weights))
    ymean=sum(w*x*x for x,w in zip(points,weights))
    cov=sum(w*(x-xmean)*(x*x-ymean) for x,w in zip(points,weights))
    assert cov==0
    assert Fraction(1,3) != Fraction(1,3)*Fraction(1,3)
    assert sum(w for x,w in zip(points,weights) if x==0)==Fraction(1,3)


def test_known_negative_examples_really_invalidate_overclaims():
    assert Fraction(1,2)**(-1) > Fraction(1,2)**2
    assert 1**2 == 1**5  # base a=1: not strictly increasing
    assert sum(k*k for k in range(1,3)) == 5 != (1+2)**2
    assert sum(k**3 for k in range(1,3)) == 9 != (1+4)**3
    u,v=(1,0),(0,1)
    l1=lambda w:sum(abs(z) for z in w)
    assert l1((u[0]+v[0],u[1]+v[1]))**2+l1((u[0]-v[0],u[1]-v[1]))**2 != 2*l1(u)**2+2*l1(v)**2
    assert Fraction(1,4)+Fraction(1,4) != 1  # X=Y Bernoulli: Var(X+Y)=1
    assert Rational(0**2+0**2,4)-1<0  # x²+y²+1=0 has r²=-1, no real points
    assert math.comb(3,1) != 2*math.comb(2,1)  # double counting

# These 22 explicit outcome checks are separate from the parametric subclaim tests.
# Matching an authored answer string is NOT a formal audit of the entire worked solution.
@pytest.mark.parametrize("lesson_id,idx,expected",[
    ("math.hs.exponent.monotone",0,"9<243"),
    ("math.hs.exponent.monotone",1,"2>1/4"),
    ("math.hs.logarithm.product-law",0,"5"),
    ("math.hs.logarithm.product-law",1,"x=3"),
    ("math.hs.sequence.square-sum",0,"30"),
    ("math.hs.sequence.square-sum",1,"385"),
    ("math.hs.sequence.cube-sum",0,"36"),
    ("math.hs.sequence.cube-sum",1,"225"),
    ("math.hs.vector.parallelogram",0,"30"),
    ("math.hs.vector.parallelogram",1,"4+0=2+2"),
    ("math.hs.probability.variance-covariance",0,"1"),
    ("math.hs.probability.variance-covariance",1,"0"),
    ("math.hs.probability.bernoulli-variance",0,"1/4"),
    ("math.hs.probability.bernoulli-variance",1,"4/25"),
    ("math.hs.probability.complement-independence",0,"1/4"),
    ("math.hs.probability.complement-independence",1,"0.32"),
    ("math.hs.geometry.circle-complete-square",0,"半径 2"),
    ("math.hs.geometry.circle-complete-square",1,"(-1,2)"),
    ("math.hs.geometry.ellipse-parameter",0,"(0,2)"),
    ("math.hs.geometry.ellipse-parameter",1,"(-2,0)"),
    ("math.hs.counting.pascal-identity",0,"10=4+6"),
    ("math.hs.counting.pascal-identity",1,"20"),
])
def test_authored_worked_example_expected_outputs(lesson_id,idx,expected):
    docs={row["id"]:row for row in json.loads(DOC.read_text(encoding="utf8"))}
    assert expected in docs[lesson_id]["worked_examples"][idx]["answer"]
    assert docs[lesson_id]["worked_examples"][idx]["steps"]
    assert docs[lesson_id]["worked_examples"][idx]["check"]
