"""Batch64 exact, tightly bounded witness functions for teaching draft examples.

Do not use these functions to certify a general theorem or unrestricted
student-written proof. Each method accepts explicit finite/arithmetic inputs.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import comb, isqrt

class FailedPremise(ValueError):
    """A mathematical hypothesis or the bounded exact input contract failed."""

def rat(v):
    if type(v) not in (int,F):
        raise FailedPremise("only exact integer or Fraction accepted")
    return F(v)

def finite_membership(x):
    x=rat(x)
    if x.denominator!=1: raise FailedPremise("set predicate restricted to integers")
    return x*x==4

def subset_relation(a,b):
    if type(a) not in (set,frozenset) or type(b) not in (set,frozenset):
        raise FailedPremise("finite sets required")
    return a<=b, a==b, a<b

def complement(universe,part):
    if type(universe) not in (set,frozenset) or type(part) not in (set,frozenset):
        raise FailedPremise("finite sets required")
    if not part<=universe: raise FailedPremise("A must be a subset of U")
    return universe-part

def finite_implication(domain,p,q):
    if type(domain) not in (tuple,list) or len(domain)==0 or len(set(domain))!=len(domain):
        raise FailedPremise("finite nonempty unique domain required")
    if not callable(p) or not callable(q): raise FailedPremise("predicates required")
    values=[(p(x),q(x)) for x in domain]
    if not all(type(a) is bool and type(b) is bool for a,b in values):
        raise FailedPremise("predicates must return bool")
    return all(not a or b for a,b in values)

def _square_root_rational(x):
    x=rat(x)
    if x<0: raise FailedPremise("square root requires nonnegative")
    a,b=isqrt(x.numerator),isqrt(x.denominator)
    if a*a!=x.numerator or b*b!=x.denominator:
        raise FailedPremise("witness only supports exact rational square roots")
    return F(a,b)

def arithmetic_geometric(a,b):
    a,b=rat(a),rat(b)
    if a<0 or b<0: raise FailedPremise("a and b must be nonnegative")
    am=(a+b)/2
    gm=_square_root_rational(a*b)
    assert am>=gm
    return am,gm,am==gm

def finite_function_is_single_valued(pairs):
    if type(pairs) is not list or len(pairs)==0:
        raise FailedPremise("nonempty list of graph observations required")
    out={}
    for pair in pairs:
        if type(pair) not in (list,tuple) or len(pair)!=2:
            raise FailedPremise("each observation is a (x,y) pair")
        x,y=pair
        if type(x) not in (int,F) or type(y) not in (int,F):
            raise FailedPremise("exact rational graph coordinates only")
        if x in out and out[x]!=y:return False
        out[x]=y
    return True

def exponent_comparison(base,x1,x2):
    base=rat(base)
    if not (base>0 and base!=1):
        raise FailedPremise("strict exponential monotonicity requires a>0 and a!=1")
    if type(x1) is not int or type(x2) is not int or x1==x2:
        raise FailedPremise("distinct integer exponents only in this finite witness")
    v1,v2=base**x1,base**x2
    return v1,v2, v1<v2

def log_power_identity(base,x,p,q):
    base,x=rat(base),rat(x)
    if base<=0 or base==1 or x<=0:
        raise FailedPremise("log domain base>0,base!=1,x>0")
    if type(p) is not int or type(q) is not int or q<=0:
        raise FailedPremise("exponent must be exact p/q with q positive")
    # a**(p/q)=x iff a**p=x**q for positive a and x.
    return base**p==x**q

def tangent_quadrant(k):
    if type(k) is not int:
        raise FailedPremise("angle must be integer multiple of pi/2")
    sin=(0,1,0,-1)[k%4]
    cos=(1,0,-1,0)[k%4]
    if cos==0:raise FailedPremise("undefined tangent: cos(theta)=0")
    return F(sin,cos)

def normalized_period(amplitude,omega):
    amplitude,omega=rat(amplitude),rat(omega)
    if amplitude==0 or omega==0:
        raise FailedPremise("no smallest positive period for constant sine")
    # Returns T/(2*pi) exactly; symbolic pi is intentionally not approximated.
    return 1/abs(omega)

def simple_random_sample(N,n):
    if type(N) is not int or type(n) is not int or not (1<=n<=N):
        raise FailedPremise("1<=n<=N required")
    total=comb(N,n)
    inclusion=F(comb(N-1,n-1),total)
    return total,F(1,total),inclusion

def complex_parts_equal(a,b,c,d):
    a,b,c,d=map(rat,(a,b,c,d))
    return a==c and b==d

def model_residuals(observations,a,b,query_x):
    a,b,q=rat(a),rat(b),rat(query_x)
    if type(observations) is not list or len(observations)==0:
        raise FailedPremise("nonempty observed data needed")
    data=[]
    for p in observations:
        if type(p) not in (tuple,list) or len(p)!=2:
            raise FailedPremise("2D observation expected")
        x,y=map(rat,p)
        data.append((x,y))
    xs=[x for x,_ in data]
    return [y-(a*x+b) for x,y in data], a*q+b, q<min(xs) or q>max(xs)

def line_parallel_z_plane(point,direction):
    if type(point) not in (list,tuple) or type(direction) not in (list,tuple) or len(point)!=3 or len(direction)!=3:
        raise FailedPremise("3D rational point and direction required")
    p=tuple(map(rat,point))
    d=tuple(map(rat,direction))
    if not any(d): raise FailedPremise("line requires nonzero direction")
    return d[2]==0 and p[2]!=0
