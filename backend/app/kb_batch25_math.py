"""Batch25: bounded, exact *instance* checks for ten high-risk math conflicts.

No arbitrary expressions, no eval/SymPy string parsing, no student free-text
certification. A finite witness is not a universal theorem proof or approval.
"""
from __future__ import annotations

import re
from fractions import Fraction
from math import comb

MAX = 10**6
SUPPORTED = frozenset({
    "composition_reciprocal", "parity_polynomial_at_point", "piecewise_endpoint",
    "ivt_polynomial_endpoints", "point_line_distance_squared", "binomial_point_mass",
    "hypergeometric_point_mass", "regression_slope", "triangle_double_area",
    "vector_linear_combination",
})

class DomainError(ValueError):
    pass

def rational(value):
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise DomainError("rational must be integer or canonical integer/fraction string")
    s = str(value)
    if not re.fullmatch(r"-?(0|[1-9]\d{0,6})(?:/[1-9]\d{0,6})?", s):
        raise DomainError("invalid rational literal or unbounded precision")
    f = Fraction(s)
    if max(abs(f.numerator), f.denominator) > MAX:
        raise DomainError("rational exceeds exact arithmetic limit")
    return f

def integer(value, low=0, high=100):
    if type(value) is not int or not low <= value <= high:
        raise DomainError(f"integer out of bounds [{low}, {high}]")
    return value

def vector(value, min_len=2, max_len=6):
    if not isinstance(value, list) or not min_len <= len(value) <= max_len:
        raise DomainError("invalid vector length")
    return [rational(x) for x in value]

def encode(x):
    if isinstance(x, Fraction):
        return str(x)
    if isinstance(x, list):
        return [encode(y) for y in x]
    return x

def evaluate(op, data):
    flags = dict(student_step_verified=False, complete_theorem_certified=False,
                 teacher_approved=False, official_curriculum_atom_verified=False)
    if op not in SUPPORTED:
        return dict(status="UNSUPPORTED", explanation="No registered finite oracle", **flags)
    if not isinstance(data, dict) or len(data) > 12:
        return dict(status="CONDITIONS_NOT_ESTABLISHED", explanation="Expected bounded structured data", **flags)
    try:
        if op == "composition_reciprocal":
            # f(t)=1/t, g(x)=x+c, g(x) must lie in f's domain.
            x, c = rational(data["x"]), rational(data["shift"])
            inner = x + c
            if inner == 0:
                raise DomainError("inner result zero: original reciprocal undefined")
            witness = dict(inner=inner, output=1/inner)
        elif op == "parity_polynomial_at_point":
            # Only a pointwise parity observation; NOT a global parity certification.
            coeff = vector(data["coefficients"], 1, 6)
            x = rational(data["x"])
            f = lambda t: sum((a*t**i for i, a in enumerate(coeff)), Fraction(0))
            witness = dict(f_x=f(x), f_minus_x=f(-x),
                           even_at_point=(f(x) == f(-x)),
                           odd_at_point=(f(-x) == -f(x)),
                           global_parity_certified=False)
        elif op == "piecewise_endpoint":
            x, t = rational(data["x"]), rational(data["threshold"])
            # f(x)=x^2 for x<t, f(x)=2x for x>=t.
            witness = dict(branch="LEFT_LT" if x<t else "RIGHT_GE",
                           output=x*x if x<t else 2*x,
                           boundary_owned_by_right=(x==t))
        elif op == "ivt_polynomial_endpoints":
            # f(t)=t^2-k continuous; a sign change implies existence, not uniqueness.
            a,b,k=map(rational,(data["a"],data["b"],data["k"]))
            if a >= b: raise DomainError("interval requires a<b")
            fa,fb=a*a-k,b*b-k
            witness=dict(f_a=fa,f_b=fb,strict_opposite_sign=(fa*fb<0),
                         uniqueness_established=False,continuity_assumed_for_polynomial=True)
        elif op == "point_line_distance_squared":
            a,b,c,x,y=map(rational,(data["A"],data["B"],data["C"],data["x"],data["y"]))
            if a==0 and b==0: raise DomainError("zero normal vector: not a line")
            witness=dict(distance_squared=(a*x+b*y+c)**2/(a*a+b*b))
        elif op == "binomial_point_mass":
            n=integer(data["n"]); k=integer(data["k"]); p=rational(data["p"])
            if k>n or not 0<=p<=1: raise DomainError("invalid n,k,p")
            witness=dict(probability=Fraction(comb(n,k))*p**k*(1-p)**(n-k))
        elif op == "hypergeometric_point_mass":
            N=integer(data["N"],1); K=integer(data["K"]); n=integer(data["n"]); k=integer(data["k"])
            if K>N or n>N or not max(0,n-(N-K)) <= k <= min(n,K):
                raise DomainError("invalid population/sample or k outside support")
            witness=dict(probability=Fraction(comb(K,k)*comb(N-K,n-k),comb(N,n)))
        elif op == "regression_slope":
            xs=vector(data["xs"], 2, 6);ys=vector(data["ys"],2,6)
            if len(xs)!=len(ys):raise DomainError("paired sample lengths must agree")
            n=len(xs)
            sx=sum(xs);sy=sum(ys)
            sxx=n*sum(x*x for x in xs)-sx*sx
            if sxx==0:raise DomainError("zero x-variation: regression slope undefined")
            sxy=n*sum(x*y for x,y in zip(xs,ys))-sx*sy
            witness=dict(slope=sxy/sxx, intercept=(sy-(sxy/sxx)*sx)/n, causation_certified=False)
        elif op == "triangle_double_area":
            p=vector(data["P"],2,2);q=vector(data["Q"],2,2);r=vector(data["R"],2,2)
            det=(q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
            if det==0: raise DomainError("three collinear points: degenerate triangle")
            witness=dict(double_area=abs(det),orientation=1 if det>0 else -1)
        else:  # vector_linear_combination
            u=vector(data["u"]);v=vector(data["v"]);a=rational(data["a"]);b=rational(data["b"])
            if len(u)!=len(v):raise DomainError("vector dimensions differ")
            witness=dict(result=[a*x+b*y for x,y in zip(u,v)])
        return dict(status="VERIFIED_FINITE_INSTANCE", witness={k:encode(v) for k,v in witness.items()},
                    explanation="Only supplied exact operands/conditions checked; no whole-proof certification", **flags)
    except (DomainError, KeyError, ValueError, ZeroDivisionError, OverflowError) as exc:
        return dict(status="CONDITIONS_NOT_ESTABLISHED", explanation=str(exc)[:160], **flags)
