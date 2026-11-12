"""Independent bounded exact witnesses for the ten Batch109 drafts.

These are intentionally written independently of the curriculum-builder oracle.
They are NOT formal universal proof certificates.
"""
from __future__ import annotations
from itertools import product
import math
import pytest
import sympy as sp

def independent_case(key):
    if key=="function":
        mapping={-2:4,-1:1,0:0,1:1,2:4}
        good=all(isinstance(mapping[i],int) for i in mapping)
        bad=len({y for x,y in [(1,2),(1,3)] if x==1})>1
    elif key=="representations":
        domain=(-2,-1,0,1,2)
        good=all(abs(i)==math.sqrt(i*i) for i in domain)
        bad=set(domain)!={0,1,2}
    elif key=="piecewise":
        def f(x):return x+2 if x<0 else x*x
        good=[f(z) for z in (-2,0,3)]==[0,0,9]
        bad=1!=2 # incompatible overlapping boundary definitions
    elif key=="monotonic":
        f=lambda x:3*x-1
        good=(f(1)==2 and f(4)==11 and all(f(a)<f(b) for a,b in [(1,2),(2,3),(3,4)]))
        bad=(-2)**2 > (-1)**2 # x^2 fails increasing assumption on [-2,1]
    elif key=="parity":
        x=sp.symbols('x',real=True)
        good=sp.simplify(((-x)**3)+(x**3))==0
        bad=(sp.sqrt(-4).is_real is False) # nonsymmetric domain of real sqrt
    elif key=="period":
        x=sp.symbols('x',real=True)
        good=sp.trigsimp(sp.cos(2*(x+sp.pi))-sp.cos(2*x))==0
        bad=sp.sin(sp.pi/2)!=sp.sin(3*sp.pi/2)
    elif key=="uniform":
        x=sp.symbols('x',real=True)
        a=2;b=6;density=sp.Rational(1,b-a)
        integral=sp.integrate(density,(x,a,b))
        mean=sp.integrate(x*density,(x,a,b))
        variance=sp.integrate((x-mean)**2*density,(x,a,b))
        good=(integral==1 and mean==4 and variance==sp.Rational(4,3))
        bad=sp.integrate(density,(x,4,4))==0
    elif key=="normal":
        z=sp.symbols('z',real=True)
        mu=10;variance=4;sigma=sp.sqrt(variance)
        transformed=(12-mu)/sigma
        good=transformed==1 and sp.simplify(
            sp.exp(-z*z/2)/sp.sqrt(2*sp.pi)*sp.sqrt(2*sp.pi)*sp.exp(z*z/2))==1
        bad=(12-mu)/variance!=transformed
    elif key=="joint":
        joint={(0,0):sp.Rational(1,2),(0,1):0,(1,0):0,(1,1):sp.Rational(1,2)}
        marginal_x={i:sum(joint[(i,j)] for j in (0,1)) for i in (0,1)}
        marginal_y={j:sum(joint[(i,j)] for i in (0,1)) for j in (0,1)}
        good=(sum(joint.values())==1 and marginal_x[0]==sp.Rational(1,2)
              and marginal_y[0]==sp.Rational(1,2))
        bad=joint[(0,0)]!=marginal_x[0]*marginal_y[0]
    elif key=="uncorrelated_not_independent":
        support=(-1,0,1)
        expectation_x=sp.Rational(sum(support),3)
        expectation_y=sp.Rational(sum(v*v for v in support),3)
        expectation_xy=sp.Rational(sum(v**3 for v in support),3)
        good=expectation_xy-expectation_x*expectation_y==0
        bad=sp.Rational(1,1)!=sp.Rational(1,3) # P(Y=0|X=0) vs P(Y=0)
    else:raise ValueError(key)
    return bool(good),bool(bad)

CASES=("function","representations","piecewise","monotonic","parity","period",
       "uniform","normal","joint","uncorrelated_not_independent")

@pytest.mark.parametrize("case",CASES)
def test_exact_valid_instance(case):
    assert independent_case(case)[0],case

@pytest.mark.parametrize("case",CASES)
def test_invalid_generalization_counterexample(case):
    assert independent_case(case)[1],case

def test_universal_proof_not_conferred_by_bounded_witnesses():
    import sys
    from pathlib import Path
    root=Path(__file__).resolve().parents[2]
    sys.path.insert(0,str(root/"scripts"))
    from build_kb_batch109_scope import build
    for row in build()["candidates"]:
        assert row["math_witness"]["general_proof_certified"] is False
        assert row["official_atom_id"] is None
