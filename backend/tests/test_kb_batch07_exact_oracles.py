"""110 independent, exact, narrow mathematical regression cases for the ten disputed lesson themes.

The checked expressions here are separate from both versions of the teaching
text. They establish specific truths/counterexamples, not complete proofs or
a license to auto-merge conflicting drafts.
"""
from __future__ import annotations

from math import comb
import pytest
from sympy import Rational, Symbol, sqrt, sin, pi, simplify

CASES = list(range(1,12))

@pytest.mark.parametrize("seed", CASES)
def test_composition_domain_and_order(seed):
    x=Symbol("x",real=True)
    a=seed
    g=x-a
    inner=sqrt(g)
    assert simplify(inner.subs(x,a+seed)-sqrt(seed)) == 0
    assert bool(g.subs(x,a-1)<0)
    # Conversely g(f(x)) can be defined for a different set; composition order matters.
    assert simplify(sqrt(x).subs(x,seed)-a) == sqrt(seed)-a

@pytest.mark.parametrize("seed", CASES)
def test_parity_requires_symmetric_domain(seed):
    x=Symbol("x",real=True)
    k=seed
    f=x**k
    assert simplify(f.subs(x,-x)-(-1)**k*f)==0
    # The interval [0,seed] is not symmetric about zero.
    assert -seed not in range(0,seed+1)
    assert simplify((x**2).subs(x,-x)-x**2) == 0

@pytest.mark.parametrize("seed", CASES)
def test_piecewise_branch_at_boundary(seed):
    x=Symbol("x",real=True)
    b=seed
    left=x+b
    right=x**2+b
    # x=0 belongs to the right branch exclusively.
    assert right.subs(x,0)==b
    assert left.subs(x,-1)==b-1
    assert right.subs(x,1)==b+1
    assert sum(v for v in (0<0, 0>=0) if v)==1

@pytest.mark.parametrize("seed", CASES)
def test_ivt_sign_change_sufficient_not_necessary(seed):
    x=Symbol("x",real=True)
    root=seed
    f=x-root
    assert f.subs(x,root-1)==-1
    assert f.subs(x,root+1)==1
    assert f.subs(x,root)==0
    # Both endpoints positive, but roots exist inside.
    g=(x-root)**2-1
    assert g.subs(x,root-2)>0 and g.subs(x,root+2)>0
    assert g.subs(x,root-1)==0

@pytest.mark.parametrize("seed", CASES)
def test_point_line_distance_and_scaling(seed):
    x,y=seed,seed+1
    a,b,c=3,4,-seed
    numerator=abs(a*x+b*y+c)
    distance=Rational(numerator,5)
    assert distance>=0
    # Rescaling coefficients does not change the geometric line/distance.
    k=seed+1
    assert Rational(abs(k*(a*x+b*y+c)),5*k)==distance

@pytest.mark.parametrize("seed", CASES)
def test_binomial_mass_sum_and_p_boundary(seed):
    n=seed
    p=Rational(1,3)
    probs=[comb(n,k)*p**k*(1-p)**(n-k) for k in range(n+1)]
    assert sum(probs)==1
    assert all(0<=v<=1 for v in probs)
    assert sum(comb(n,k)*(Rational(0))**k*(1-Rational(0))**(n-k) for k in range(n+1))==1
    assert sum(comb(n,k)*(Rational(1))**k*(1-Rational(1))**(n-k) for k in range(n+1))==1

@pytest.mark.parametrize("seed", CASES)
def test_hypergeometric_valid_support_and_nonreplacement(seed):
    N=20
    K=seed
    n=4
    lower=max(0,n-(N-K))
    upper=min(n,K)
    pmf=lambda k: Rational(comb(K,k)*comb(N-K,n-k),comb(N,n)) if lower<=k<=upper else Rational(0)
    assert sum(pmf(k) for k in range(n+1))==1
    assert all(pmf(k)>=0 for k in range(n+1))
    assert pmf(-1)==0 and pmf(n+1)==0
    # For 1 success ball, drawing two successes without replacement is impossible.
    assert Rational(comb(1,2)*comb(19,0),comb(20,2))==0
    assert Rational(1,20)**2>0

@pytest.mark.parametrize("seed", CASES)
def test_regression_slope_and_correlation_not_causality(seed):
    xs=list(range(4))
    ys=[seed+2*x for x in xs]
    mx=Rational(sum(xs),len(xs))
    my=Rational(sum(ys),len(ys))
    sxx=sum((x-mx)**2 for x in xs)
    sxy=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    assert simplify(sxy/sxx)==2
    # Constant x has zero variance; slope denominator would be zero.
    assert sum((seed-Rational(4*seed,4))**2 for _ in xs)==0

@pytest.mark.parametrize("seed", CASES)
def test_triangle_included_angle_and_degenerate_boundary(seed):
    a,b=seed,seed+1
    assert simplify(Rational(a*b,2)*sin(pi/2)-Rational(a*b,2))==0
    assert simplify(Rational(a*b,2)*sin(pi/6)-Rational(a*b,4))==0
    assert simplify(Rational(a*b,2)*sin(0))==0
    # Zero angle gives zero area, not a nondegenerate triangle.

@pytest.mark.parametrize("seed", CASES)
def test_vector_additivity_distributive_coordinates(seed):
    u=(seed,seed+1)
    v=(-seed,2*seed)
    scalar=seed-3
    lhs=tuple(scalar*(x+y) for x,y in zip(u,v))
    rhs=tuple(scalar*x+scalar*y for x,y in zip(u,v))
    assert lhs==rhs
    assert tuple(u[i]+v[i] for i in range(2))==(0,3*seed+1)
