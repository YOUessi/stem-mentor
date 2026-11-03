"""Independent, bounded evidence for seven new draft lessons. NOT formal proof."""
import itertools
from fractions import Fraction
from math import comb

import pytest
from sympy import Rational, Symbol, diff, simplify, sqrt

from app.deep_knowledge import lessons

x = Symbol("x", real=True)
NEW = {
    "math.hs.calculus.chain-rule", "math.hs.calculus.quotient-rule",
    "math.hs.calculus.fermat-stationary", "math.hs.vector.cauchy-schwarz",
    "math.hs.counting.binomial-sum", "math.hs.probability.expectation-linearity",
    "math.hs.function.bisection-root",
}


def test_each_new_lesson_is_deep_draft_with_proof_and_boundaries():
    all_docs={lesson.id:lesson for lesson in lessons()}
    assert NEW.issubset(all_docs)
    assert len(all_docs) == 153
    for identifier in NEW:
        doc=all_docs[identifier]
        assert doc.kind=="theorem" and doc.review.status=="REVIEW_PENDING"
        assert doc.teacher_solution_visibility=="TEACHER_ONLY"
        assert doc.provenance.permission=="PROJECT_AUTHORED"
        assert len(doc.proof_steps)>=3 and len(doc.worked_examples)>=2
        assert len(doc.counterexamples)>=1 and len(doc.hint_ladder)>=3
        assert doc.assumptions and doc.boundaries


@pytest.mark.parametrize("inner,outer", [
    (2*x+1, lambda y:y**3),
    (x*x+1,lambda y:sqrt(y)),
    (3*x-5,lambda y:y*y-1),
    (x**3+1,lambda y:y**4),
    (-x*x-2,lambda y:y**2),
    (x+1,lambda y:y**5),
])
def test_chain_rule_exact(inner,outer):
    y=Symbol("y",real=True)
    h=outer(inner)
    chain=diff(outer(y),y).subs(y,inner)*diff(inner,x)
    assert simplify(diff(h,x)-chain)==0


@pytest.mark.parametrize("u,v", [
    (x*x+1,x+1), (1,x*x+1),
    (2*x+3,3*x-1), (x**3+1,x*x+1),
    (x*x-1,x-1), (x*x+7,2*x-9),
])
def test_quotient_rule_symbolic(u,v):
    assert simplify(diff(u/v,x)-(diff(u,x)*v-u*diff(v,x))/v**2)==0


@pytest.mark.parametrize("f,point,minimum", [
    (x*x,0,True),(x**4,0,True),(-x*x,0,False),
    ((x-2)**2,2,True),(-((x+3)**2),-3,False),
])
def test_fermat_necessary_at_extremum(f,point,minimum):
    assert diff(f,x).subs(x,point)==0
    for delta in [Rational(-1,3),Rational(-1,10),Rational(1,10),Rational(1,3)]:
        diffval=f.subs(x,point+delta)-f.subs(x,point)
        assert diffval>=0 if minimum else diffval<=0


def test_fermat_converse_and_nondifferentiable_counterexamples():
    assert diff(x**3,x).subs(x,0)==0
    assert (-1)**3 < 0 < 1**3
    assert abs(Rational(-1,2))>0 and abs(Rational(1,2))>0
    assert Rational(abs(Rational(1,4)),Rational(1,4))==1
    assert Rational(abs(Rational(-1,4)),Rational(-1,4))==-1


@pytest.mark.parametrize("u,v", list(itertools.product(
    [(0,0),(1,0),(0,1),(1,2),(-1,3),(2,-5),(3,3)],
    repeat=2,
)))
def test_vector_cauchy_schwarz_exact_2d(u,v):
    dot=sum(a*b for a,b in zip(u,v))
    uu=sum(a*a for a in u)
    vv=sum(b*b for b in v)
    determinant=u[0]*v[1]-u[1]*v[0]
    assert uu*vv-dot*dot==determinant*determinant>=0
    assert (uu*vv==dot*dot)==(determinant==0)


@pytest.mark.parametrize("n",range(0,25))
def test_binomial_coefficient_sum_and_signed_boundary(n):
    total=sum(comb(n,k) for k in range(n+1))
    alternating=sum((-1)**k*comb(n,k) for k in range(n+1))
    assert total==2**n
    assert alternating==(1 if n==0 else 0)


@pytest.mark.parametrize("values", [
    ((0,0),(1,1)),
    ((0,1),(1,0)),
    ((2,-1),(1,3)),
    ((0,4),(0,5)),
    ((1,2),(-1,2)),
])
@pytest.mark.parametrize("a,b",[(-3,2),(0,1),(1,1),(3,-2)])
def test_expectation_linearity_without_independence(values,a,b):
    xs,ys=values
    weights=(Fraction(1,3),Fraction(2,3))
    direct=sum(p*(a*xx+b*yy) for p,xx,yy in zip(weights,xs,ys))
    split=a*sum(p*xx for p,xx in zip(weights,xs))+b*sum(p*yy for p,yy in zip(weights,ys))
    assert direct==split


@pytest.mark.parametrize("f,lo,hi,expected", [
    (lambda t:t*t-2,1,2,sqrt(2)),
    (lambda t:t*t*t-2,1,2,2**(Rational(1,3))),
    (lambda t:t-3,2,4,3),
    (lambda t:t*t*t-t-1,1,2,None),
])
@pytest.mark.parametrize("steps",[1,2,3,6,12])
def test_bisection_invariant_and_midpoint_error(f,lo,hi,expected,steps):
    lo,hi=Rational(lo),Rational(hi)
    original_width=hi-lo
    if f((lo+hi)/2)==0:
        assert f((lo+hi)/2)==0
        return
    assert f(lo)*f(hi)<0
    for i in range(steps):
        mid=(lo+hi)/2
        if f(mid)==0:
            assert f(mid)==0
            return
        if f(lo)*f(mid)<0:
            hi=mid
        else:
            lo=mid
        assert f(lo)*f(hi)<0
        assert hi-lo==Rational(original_width,2**(i+1))
        assert (hi-lo)/2==Rational(original_width,2**(i+2))


def test_batch09_draft_script_is_importable_without_writing():
    import importlib.util
    from pathlib import Path
    path=Path(__file__).resolve().parents[2]/"scripts/build_kb_batch09_lessons.py"
    spec=importlib.util.spec_from_file_location("build_batch09",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert len(module.LESSONS)==7 and len(module.build())>10000
