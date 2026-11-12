"""Independently check bounded exact example calculations and invalid-condition witnesses.

These checks are separate from the authored lesson prose but do not formally prove
theorems over every possible real parameter.
"""
import math
from fractions import Fraction as F
import pytest
import sympy as s

@pytest.mark.parametrize("x",[-5,-2,-1,1,2,5])
def test_negative_power_domain_and_reciprocal(x):
    assert x!=0
    assert F(1,x)*x==1

@pytest.mark.parametrize("a,m,n,expected",[
    (16,3,4,8),(9,-1,2,F(1,3)),(81,3,4,27),(25,-3,2,F(1,125))])
def test_positive_fractional_powers_exact(a,m,n,expected):
    assert a>0 and n>0
    assert s.simplify(s.Integer(a)**s.Rational(m,n)-expected)==0

@pytest.mark.parametrize("a",[-1,-4,-16])
def test_even_root_excludes_negative_reals(a):
    assert s.sqrt(a).is_real is False

@pytest.mark.parametrize("a,x,y",[
    (2,F(1,2),F(3,2)),(3,0,2),(F(1,3),1,2),(F(1,2),-1,1)])
def test_exponential_monotonic_reverses_by_base(a,x,y):
    assert x<y
    x=s.Rational(x.numerator,x.denominator) if isinstance(x,F) else x
    y=s.Rational(y.numerator,y.denominator) if isinstance(y,F) else y
    ax=s.Pow(s.Rational(a.numerator,a.denominator),x) if isinstance(a,F) else s.Pow(a,x)
    ay=s.Pow(s.Rational(a.numerator,a.denominator),y) if isinstance(a,F) else s.Pow(a,y)
    if a>1:assert bool(ax<ay)
    else:assert bool(ax>ay)

@pytest.mark.parametrize("base,x,expected",[(2,8,3),(3,9,2),(5,125,3),(10,1000,3)])
def test_logarithm_exponent_and_change_base(base,x,expected):
    assert s.log(x,base)==expected
    assert s.simplify(s.log(x)/s.log(base)-expected)==0

def test_log_domain_and_invalid_log_sum():
    x=s.symbols("x",real=True)
    assert s.solve_univariate_inequality(x*x-4>0,x,relational=False)==s.Union(
        s.Interval.open(-s.oo,-2),s.Interval.open(2,s.oo))
    assert s.log(10,2)!=s.log(2,2)+s.log(8,2)

@pytest.mark.parametrize("sample,expected",[
    ((1,0,1,1),F(3,4)),((0,0,0),F(0)),((1,1,1,1,0,0),F(2,3))])
def test_bernoulli_moment_method(sample,expected):
    assert all(x in (0,1) for x in sample)
    phat=F(sum(sample),len(sample))
    assert phat==expected and F(0)<=phat<=F(1)

@pytest.mark.parametrize("n,k",[(1,0),(1,1),(3,2),(4,4),(5,2),(6,0),(6,3)])
def test_bernoulli_mle_global_optimum_over_discrete_candidates(n,k):
    assert n>=1 and 0<=k<=n
    p=F(k,n)
    def likelihood(q):
        return (q**k)*((1-q)**(n-k))
    # Rational grid including the analytic optimum and endpoints.
    grid=[F(i,120) for i in range(121)]+[p]
    assert likelihood(p)==max(likelihood(q) for q in grid)
    if 0<k<n:
        assert p>0 and p<1
    else:assert p in (0,1)

@pytest.mark.parametrize("n,alpha,rejected",[
    (10,F(1,20),True),(10,F(1,100),True),(8,F(1,100),True),
    (8,F(1,1000),False)])
def test_right_tail_p_value_for_all_heads(n,alpha,rejected):
    p=F(1,2**n)
    assert (p<alpha)==rejected
    assert p!=F(1,2)

@pytest.mark.parametrize("points,unique,expected_slope",[
    (((0,1),(1,3),(2,5)),True,F(2)),
    (((1,2),(2,2),(3,2)),True,F(0)),
    (((1,2),(1,4),(1,6)),False,None),
    (((-1,1),(0,2),(1,3)),True,F(1))])
def test_centered_least_squares_solution_and_nonidentifiability(points,unique,expected_slope):
    n=len(points)
    xb=sum(F(x) for x,_ in points)/n
    yb=sum(F(y) for _,y in points)/n
    sxx=sum((F(x)-xb)**2 for x,_ in points)
    sxy=sum((F(x)-xb)*(F(y)-yb) for x,y in points)
    if unique:
        assert sxx>0 and sxy/sxx==expected_slope
        beta=sxy/sxx;intercept=yb-beta*xb
        # The unique algebraic minimum against independent perturbations.
        def loss(a,b):return sum((F(y)-a-b*F(x))**2 for x,y in points)
        best=loss(intercept,beta)
        for delta in [F(-1),F(0),F(1)]:
            for eps in [F(-1),F(0),F(1)]:
                assert loss(intercept+delta,beta+eps)>=best
    else:
        assert sxx==0
        # Distinct parameter pairs produce same fitted values.
        assert [F(4)+F(0)*x for x,_ in points]==[F(3)+F(1)*x for x,_ in points]
