"""Exact, *bounded* counterexample/example checks for Batch63 manuscripts.

No function proves a general theorem or validates arbitrary student work.
All outputs identify the finite case actually checked; invalid premises raise.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import gcd
import sympy as sp

VALIDITY="FINITE_EXACT_CASE_ONLY"
class FailedPremise(ValueError):
    pass
def require(ok, explanation):
    if not ok: raise FailedPremise(explanation)
def Q(x):
    return F(x)
def negative_multiplier(a,b,c):
    a,b,c=map(Q,(a,b,c))
    require(a<b and c<0,"requires strict inequality and negative multiplier")
    return a*c>b*c
def finite_quantifier_negation(truth_values):
    require(isinstance(truth_values,(tuple,list)),"explicit finite domain required")
    require(all(type(v) is bool for v in truth_values),"each predicate must be Boolean")
    return (not all(truth_values))==any(not p for p in truth_values) and (
           (not any(truth_values))==all(not p for p in truth_values))
def quadratic_two_root_sign(a,r1,r2,x):
    a,r1,r2,x=map(Q,(a,r1,r2,x))
    require(a!=0 and r1<r2,"requires nonzero quadratic coefficient and distinct real roots")
    val=a*(x-r1)*(x-r2)
    return (val>0)-(val<0)
def rational_base_allowed(base,m,n):
    base=Q(base)
    require(type(m) is int and type(n) is int and n>0 and
            gcd(abs(m),n)==1,"reduced integer rational exponent required")
    return not ((base<0 and n%2==0) or (base==0 and m<=0))
def power_minus_eight_two_thirds():
    x=sp.real_root(-8,3)**2
    return sp.simplify(x)==4
def trig_tangent_identity(angle):
    # Exact, closed angles only: a symbolic cos(x) != 0 comparison is not
    # evidence that the denominator remains nonzero for every real x.
    angle=sp.sympify(angle)
    require(bool(angle.is_number) and not angle.atoms(sp.Float),
            "only exact numeric angle witnesses are supported")
    sine=sp.simplify(sp.sin(angle));cosine=sp.simplify(sp.cos(angle))
    require(cosine.is_zero is False,"cosine must be provably nonzero")
    return sp.simplify(1+(sine/cosine)**2-1/cosine**2)==0
def quadratic_bisection_one_step():
    x=sp.symbols("x", real=True)
    f=x*x-2
    a,b,m=F(1),F(2),F(3,2)
    vals=[sp.expand(f).subs(x,sp.Rational(z.numerator,z.denominator)) for z in (a,b,m)]
    require(vals[0]<0 and vals[1]>0 and vals[2]>0,
            "bisection sign assumptions fail")
    return (a,m,tuple(vals))
def vector_basis_coefficients(u,v,w):
    ux,uy=map(Q,u);vx,vy=map(Q,v);wx,wy=map(Q,w)
    det=ux*vy-uy*vx
    require(det!=0,"basis vectors must be noncollinear")
    alpha=(wx*vy-wy*vx)/det
    beta=(ux*wy-uy*wx)/det
    require(alpha*ux+beta*vx==wx and alpha*uy+beta*vy==wy,
            "linear coordinate solution inconsistent")
    return alpha,beta
def ssa_A_30_degrees(a,b):
    # Specialized acute A=30° geometry only; NOT a general SSA solver.
    a,b=map(Q,(a,b));require(a>0 and b>0,"positive sides required")
    h=b/2 # b*sin(30°)
    if a<h:return 0
    if a==h:return 1
    if a>=b:return 1
    return 2
def complex_divide(z1,z2):
    a,b=map(Q,z1);c,d=map(Q,z2)
    denominator=c*c+d*d
    require(denominator>0,"nonzero complex divisor required")
    re=(a*c+b*d)/denominator
    im=(b*c-a*d)/denominator
    require(re*c-im*d==a and re*d+im*c==b,
            "exact multiplication round-trip failed")
    return re,im
def spatial_lines_location(z_for_second):
    # Specific straight lines l1=(t,0,0), l2=(0,s,z).
    z=Q(z_for_second)
    # Directions (1,0,0) and (0,1,0) are nonparallel.
    return "INTERSECT_AT_ORIGIN" if z==0 else "SKEW"
def _distinct_event_keys(event_keys,space):
    # A mathematical event is a SET of outcomes, not a multiset. Repeating
    # an outcome in a list must never inflate the counted probability.
    require(isinstance(event_keys,(list,tuple,set,frozenset)),
            "event must be an explicit finite collection of outcomes")
    try:
        keys=set(event_keys)
    except TypeError as error:
        raise FailedPremise("event outcomes must be hashable") from error
    require(len(keys)==len(event_keys),"event outcome repeated")
    require(keys<=set(space),"event outside sample space")
    return keys
def finite_event_probability(weights,event_keys):
    require(isinstance(weights,dict) and bool(weights),"explicit probability space")
    require(all(type(p) in (int,F) for p in weights.values()),
            "exact integer or Fraction probability weights required")
    weights={k:Q(v) for k,v in weights.items()}
    require(all(p>=0 for p in weights.values()) and sum(weights.values())==1,
            "probability weights must be nonnegative and sum to one")
    keys=_distinct_event_keys(event_keys,weights)
    return sum((weights[k] for k in keys),F(0))
def classical_count_only_if_equiprobable(weights,event_keys):
    require(isinstance(weights,dict) and bool(weights),"explicit probability space")
    require(all(type(p) in (int,F) for p in weights.values()),
            "exact integer or Fraction probability weights required")
    ps=[Q(p) for p in weights.values()]
    require(ps and all(p==ps[0] for p in ps),
            "classical counting requires equiprobability")
    require(sum(ps)==1,"invalid probability measure")
    keys=_distinct_event_keys(event_keys,weights)
    return F(len(keys),len(ps))
def square_finite_increment(x0,h):
    x0,h=map(Q,(x0,h))
    derivative_part=2*x0*h
    actual=(x0+h)**2-x0**2
    return derivative_part,actual,actual-derivative_part

def run_review_witnesses():
    return dict(
      domain=VALIDITY,
      negative_multiplier=negative_multiplier(2,5,-3),
      quantifier=finite_quantifier_negation([True,False]),
      quadratic_between=quadratic_two_root_sign(1,1,2,F(3,2)),
      rational_real_power=rational_base_allowed(-8,2,3) and power_minus_eight_two_thirds(),
      trig_identity=trig_tangent_identity(sp.pi/4),
      bisection=str(quadratic_bisection_one_step()[1]),
      planar_basis=[str(v) for v in vector_basis_coefficients((1,0),(1,1),(3,2))],
      ssa_solutions=ssa_A_30_degrees(5,8),
      complex_quotient=[str(v) for v in complex_divide((3,4),(1,2))],
      skew=spatial_lines_location(1),
      weighted_probability=str(finite_event_probability({"a":F(1,10),"b":F(2,10),"c":F(7,10)},["a","b"])),
      differential=[str(v) for v in square_finite_increment(2,1)],
      is_general_proof=False,can_certify_student_open_text=False)
