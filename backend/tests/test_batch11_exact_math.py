"""Exact finite/sample oracle checks for the 12 Batch11 REVIEW_PENDING theorem drafts.

They do not constitute formal verification of the entire theorem proof, and
never mark a draft as APPROVED or expose teacher solutions to student endpoints.
"""
from __future__ import annotations

import itertools
import json
import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest
from sympy import Symbol, Rational, sqrt, simplify

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/"knowledge/deep/v1/algebra_count_geometry_probability_batch11.json"
NAMES={
 "math.hs.logarithm.quotient-law","math.hs.logarithm.change-base",
 "math.hs.quadratic.discriminant-roots","math.hs.quadratic.vieta-real",
 "math.hs.sequence.telescoping","math.hs.sequence.odd-square-sum",
 "math.hs.counting.ordered-arrangements","math.hs.counting.combination-symmetry",
 "math.hs.vector.pythagorean-dot","math.hs.probability.union-bound-two",
 "math.hs.geometry.centroid-median","math.hs.probability.indicator-linearity",
}

def _rows():
    return json.loads(PATH.read_text(encoding="utf8"))


def test_authored_content_schema_and_no_fake_approval():
    from backend.app.deep_knowledge import lessons
    r=_rows()
    assert len(r)==12
    assert {p["id"] for p in r}==NAMES
    assert {p["kind"] for p in r}=={"theorem"}
    assert all(p["review"]["status"]=="REVIEW_PENDING" for p in r)
    assert all(p["teacher_solution_visibility"]=="TEACHER_ONLY" for p in r)
    assert all(len(p["proof_steps"])>=3 and len(p["worked_examples"])>=2 for p in r)
    assert len(lessons())==213
    assert subprocess.run(
       [sys.executable,str(ROOT/"scripts/build_kb_batch11_lessons.py"),"--check"],
       check=False,capture_output=True).returncode==0

@pytest.mark.parametrize("a", [2,3,5])
@pytest.mark.parametrize("i,j",itertools.product(range(-4,5),repeat=2))
def test_quotient_log_law_positive_powers(a,i,j):
    # Exact powers: log_a(a**i/a**j)=(i-j).
    x=Rational(a)**i
    y=Rational(a)**j
    assert x>0 and y>0
    assert simplify(x/y-Rational(a)**(i-j))==0

@pytest.mark.parametrize("a,b", [(2,4),(3,9),(4,2),(8,2),(9,3),(16,4)])
@pytest.mark.parametrize("k", range(-5,6))
def test_change_base_with_integer_powers(a,b,k):
    # Choose x=a^k, then log_a(x)=k and log_b(x)/log_b(a)=k.
    from sympy import log
    x=Rational(a)**k
    assert simplify(log(x,a)-k)==0
    assert simplify(log(x,b)/log(a,b)-k)==0

@pytest.mark.parametrize("a",[-5,-3,-1,1,2,4])
@pytest.mark.parametrize("r1,r2",list(itertools.product(range(-5,6,2),repeat=2)))
def test_quadratic_roots_and_vieta_exact(a,r1,r2):
    # Construct coefficient triple from exact roots, covers Δ=0 and Δ>0.
    b=-a*(r1+r2)
    c=a*r1*r2
    discr=b*b-4*a*c
    assert discr==a*a*(r1-r2)**2>=0
    assert (r1+r2)==Fraction(-b,a)
    assert (r1*r2)==Fraction(c,a)
    def f(x):
        return a*x*x+b*x+c
    assert f(r1)==f(r2)==0
    assert simplify((-b+sqrt(discr))/(2*a)-r1)==0 or simplify((-b-sqrt(discr))/(2*a)-r1)==0
    assert simplify((-b+sqrt(discr))/(2*a)-r2)==0 or simplify((-b-sqrt(discr))/(2*a)-r2)==0

@pytest.mark.parametrize("a",[-3,-2,-1,1,2,3])
@pytest.mark.parametrize("b",range(-5,6))
def test_quadratic_negative_discriminant_witness(a,b):
    c=(b*b//(4*a)+1) if a>0 else -(b*b//(4*(-a))+1)
    # Force strict negative Δ by taking c of a's sign and sufficiently large magnitude.
    c=(abs(b*b)+4*abs(a)*abs(a)+1)*(1 if a>0 else -1)
    delta=b*b-4*a*c
    assert delta<0
    # Complete square shows no real root on this domain.
    z=Symbol("x",real=True)
    completed=(2*a*z+b)**2-delta
    assert delta<0
    assert simplify(completed-4*a*(a*z*z+b*z+c))==0

@pytest.mark.parametrize("n",range(1,101))
def test_telescoping_odd_square_sums(n):
    b=lambda k:k*k+2*k+3
    direct=sum(b(k+1)-b(k) for k in range(1,n+1))
    assert direct==b(n+1)-b(1)
    assert sum(2*k-1 for k in range(1,n+1))==n*n
    assert sum(Fraction(1,k)-Fraction(1,k+1) for k in range(1,n+1))==1-Fraction(1,n+1)

@pytest.mark.parametrize("n",range(0,10))
@pytest.mark.parametrize("k",range(0,10))
def test_arrangements_and_subset_complement_exact(n,k):
    if k>n:
        # Do not apply a factorial with a negative argument.
        assert not (0<=k<=n)
        return
    counted=sum(1 for _ in itertools.permutations(range(n),k))
    computed=math.factorial(n)//math.factorial(n-k)
    assert counted==computed
    assert math.comb(n,k)==math.comb(n,n-k)
    assert sum(1 for _ in itertools.combinations(range(n),k))==math.comb(n,k)

@pytest.mark.parametrize("u,v",itertools.product(
 [(0,0),(3,0),(1,1),(2,-2),(-5,3)],[(0,0),(0,4),(1,-1),(3,5),(-2,2)]))
def test_pythagorean_dot_iff_equality(u,v):
    dot=u[0]*v[0]+u[1]*v[1]
    normsq=lambda x:x[0]**2+x[1]**2
    combined=(u[0]+v[0],u[1]+v[1])
    holds=normsq(combined)==normsq(u)+normsq(v)
    assert holds==(dot==0)
    assert normsq(combined)==normsq(u)+normsq(v)+2*dot

@pytest.mark.parametrize("mask_a,mask_b",itertools.product(range(16),repeat=2))
def test_two_event_union_bound_finite_uniform(mask_a,mask_b):
    a={i for i in range(4) if mask_a&(1<<i)}
    b={i for i in range(4) if mask_b&(1<<i)}
    pa,pb,pab,punion=(Fraction(len(s),4) for s in (a,b,a&b,a|b))
    assert punion==pa+pb-pab
    assert punion<=pa+pb
    assert (punion==pa+pb)==(pab==0)

@pytest.mark.parametrize("a,b,c",[
 ((0,0),(6,0),(0,6)),((1,1),(4,1),(1,4)),((0,0),(2,2),(3,1)),
 ((-3,4),(3,5),(1,-4)),((3,-3),(-1,4),(5,2)),((0,0),(0,4),(5,0)),
])
def test_centroid_exact_internal_ratio(a,b,c):
    mid=tuple(Fraction(b[i]+c[i],2) for i in (0,1))
    centroid=tuple(Fraction(a[i]+b[i]+c[i],3) for i in (0,1))
    for i in (0,1):
        assert centroid[i]==a[i]+Fraction(2,3)*(mid[i]-a[i])
        assert centroid[i]==b[i]+Fraction(2,3)*(Fraction(a[i]+c[i],2)-b[i])
        assert centroid[i]==c[i]+Fraction(2,3)*(Fraction(a[i]+b[i],2)-c[i])
    # Three test points are noncollinear; a==mid would make an invalid ratio.
    area2=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    assert area2!=0
    assert centroid!=mid

@pytest.mark.parametrize("mask_a,mask_b",itertools.product(range(16),repeat=2))
def test_indicator_expectation_even_when_events_dependent(mask_a,mask_b):
    a={i for i in range(4) if mask_a&(1<<i)}
    b={i for i in range(4) if mask_b&(1<<i)}
    n=[int(i in a)+int(i in b) for i in range(4)]
    en=Fraction(sum(n),4)
    pa=Fraction(len(a),4)
    pb=Fraction(len(b),4)
    assert en==pa+pb
    # Expected count is not generally the probability of either event happening.
    if a&b:
        assert en>Fraction(len(a|b),4)

def test_counterexamples_and_definition_domains():
    from sympy import log
    assert log(Rational(-1)*Rational(-1),2)==0
    assert log(-1,2).is_real is False
    assert not (0>0)
    assert (1+1j).real==1
    assert math.comb(7,5)==21
    assert sum((k+1)**2-k*k for k in range(1,5))==24
    assert sum(1 for _ in itertools.permutations(range(3),2))==6!=9
    assert 3*3+4*4==25
    assert 2*2!=1*1+1*1 # u=v=(1,0) false Pythagorean without dot 0

@pytest.mark.parametrize("id,index,expected",[
 ("math.hs.logarithm.quotient-law",0,"3"),
 ("math.hs.logarithm.quotient-law",1,"x=1"),
 ("math.hs.logarithm.change-base",0,"3/2"),
 ("math.hs.logarithm.change-base",1,"1/2"),
 ("math.hs.quadratic.discriminant-roots",0,"x=2 或 x=3"),
 ("math.hs.quadratic.discriminant-roots",1,"0 个实根"),
 ("math.hs.quadratic.vieta-real",0,"和 5，积 6"),
 ("math.hs.quadratic.vieta-real",1,"和 -2，积 1"),
 ("math.hs.sequence.telescoping",0,"24"),
 ("math.hs.sequence.telescoping",1,"5/6"),
 ("math.hs.sequence.odd-square-sum",0,"25"),
 ("math.hs.sequence.odd-square-sum",1,"100"),
 ("math.hs.counting.ordered-arrangements",0,"20"),
 ("math.hs.counting.ordered-arrangements",1,"24"),
 ("math.hs.counting.combination-symmetry",0,"21"),
 ("math.hs.counting.combination-symmetry",1,"都为 1"),
 ("math.hs.vector.pythagorean-dot",0,"25"),
 ("math.hs.vector.pythagorean-dot",1,"4"),
 ("math.hs.probability.union-bound-two",0,"0.8"),
 ("math.hs.probability.union-bound-two",1,"1/2"),
 ("math.hs.geometry.centroid-median",0,"G=(2,2)"),
 ("math.hs.geometry.centroid-median",1,"G=(2,2)"),
 ("math.hs.probability.indicator-linearity",0,"1"),
 ("math.hs.probability.indicator-linearity",1,"1"),
])
def test_authored_example_answer_field_link(id,index,expected):
    row=next(x for x in _rows() if x["id"]==id)
    assert row["worked_examples"][index]["answer"]==expected
