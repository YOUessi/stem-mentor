"""Finite exact witnesses for historical P0 proof conditions.

These typed, bounded computations are NOT full theorem proofs, lesson approval
or checks of arbitrary student free-text reasoning. No expression evaluation.
"""
from __future__ import annotations

import re
from fractions import Fraction
from math import comb, isqrt

LIMIT = 10**6

class InvalidDomain(ValueError):
    pass

def rat(x):
    if type(x) not in (str, int):
        raise InvalidDomain("Expected bounded exact integer or rational literal")
    s = str(x)
    if not re.fullmatch(r"-?(?:0|[1-9][0-9]{0,5})(?:/[1-9][0-9]{0,5})?", s):
        raise InvalidDomain("Noncanonical or oversized rational literal")
    q = Fraction(s)
    if max(abs(q.numerator), q.denominator) > LIMIT:
        raise InvalidDomain("Exact operand out of bounds")
    return q

def vec(x, min_len=2, max_len=5):
    if type(x) is not list or not min_len <= len(x) <= max_len:
        raise InvalidDomain("Invalid vector dimensions")
    return [rat(i) for i in x]

def integer(x, low=0, high=100):
    if type(x) is not int or not low <= x <= high:
        raise InvalidDomain("Invalid integer parameter")
    return x

def positive(x, desc):
    y=rat(x)
    if y <= 0: raise InvalidDomain(desc + " must be positive")
    return y

def poly(c, x):
    return sum((v*x**k for k,v in enumerate(c)), Fraction(0))

def sqroot(q):
    if q < 0: raise InvalidDomain("Negative square root")
    p, d = isqrt(q.numerator), isqrt(q.denominator)
    if p*p != q.numerator or d*d != q.denominator:
        raise InvalidDomain("Irrational root outside rational-only witness")
    return Fraction(p,d)

def _compute(op, d):
    if op in ("log_product_domain", "log_quotient_domain", "log_change_base_domain"):
        a=positive(d["base"], "log base")
        if a==1: raise InvalidDomain("Log base cannot be one")
        x=positive(d["x"], "first logarithm argument")
        if op=="log_change_base_domain":
            b=positive(d["other_base"], "change-of-base denominator")
            if b==1: raise InvalidDomain("Other log base cannot be one")
            return dict(base=a, argument=x, other_base=b, legal_domain=True,
                        equality_formula_not_independently_proved=True)
        y=positive(d["y"], "second logarithm argument")
        return dict(base=a, x=x, y=y,
                    combined_argument=x*y if op=="log_product_domain" else x/y,
                    legal_domain=True, identity_not_independently_proved=True)
    if op=="quadratic_discriminant":
        a,b,c=(rat(d[k]) for k in ("a","b","c"))
        if a==0: raise InvalidDomain("Quadratic leading coefficient must be nonzero")
        delta=b*b-4*a*c
        return dict(delta=delta, real_root_count=(0 if delta<0 else 1 if delta==0 else 2),
                    vertex_x=-b/(2*a), vertex_value=(4*a*c-b*b)/(4*a))
    if op=="amgm_rational_roots":
        a,b=(rat(d[k]) for k in ("a","b"))
        if a<0 or b<0: raise InvalidDomain("AM-GM requires nonnegative real operands")
        ra,rb=sqroot(a),sqroot(b)
        return dict(arithmetic_mean=(a+b)/2, geometric_mean=ra*rb,
                    exact_gap=(ra-rb)**2/2, equal_iff_a_eq_b=(ra==rb)==(a==b))
    if op=="line_circle":
        A,B,C,cx,cy,r=(rat(d[k]) for k in ("A","B","C","cx","cy","r"))
        if A==B==0: raise InvalidDomain("Not a line: zero normal")
        if r<=0: raise InvalidDomain("Circle radius must be positive")
        dist2=(A*cx+B*cy+C)**2/(A*A+B*B)
        return dict(distance_squared=dist2, radius_squared=r*r,
                    intersection_count=0 if dist2>r*r else 1 if dist2==r*r else 2)
    if op=="circle_circle":
        x1,y1,r1,x2,y2,r2=(rat(d[k]) for k in ("x1","y1","r1","x2","y2","r2"))
        if r1<=0 or r2<=0: raise InvalidDomain("Both radii must be positive")
        D=(x1-x2)**2+(y1-y2)**2
        if D==0: return dict(center_distance_squared=D, intersection_count="INFINITE" if r1==r2 else 0)
        count=0 if D>(r1+r2)**2 or D<(r1-r2)**2 else 1 if D in ((r1+r2)**2,(r1-r2)**2) else 2
        return dict(center_distance_squared=D, intersection_count=count)
    if op=="parabola_focus":
        p,x,y=(rat(d[k]) for k in ("p","x","y"))
        if p==0: raise InvalidDomain("p=0 collapses distinct focus/directrix")
        focus2=(x-p)**2+y*y
        directrix2=(x+p)**2
        return dict(focus_distance_squared=focus2, directrix_distance_squared=directrix2,
                    equal_distances=(focus2==directrix2), standard_equation_holds=y*y==4*p*x)
    if op=="ellipse_tangent":
        a,b,x0,y0,x,y=(rat(d[k]) for k in ("a","b","x0","y0","x","y"))
        if a<=0 or b<=0: raise InvalidDomain("Semiaxes must be strictly positive")
        if x0*x0/(a*a)+y0*y0/(b*b)!=1:
            raise InvalidDomain("Proposed tangent point not on ellipse")
        return dict(normal_x=2*x0/(a*a),normal_y=2*y0/(b*b),
                    tangent_point_is_regular=(x0!=0 or y0!=0),
                    query_on_tangent=(x*x0/(a*a)+y*y0/(b*b)==1))
    if op=="cauchy_schwarz":
        u,v=vec(d["u"]),vec(d["v"])
        if len(u)!=len(v): raise InvalidDomain("Vector dimensions differ")
        dot=sum((a*b for a,b in zip(u,v)),Fraction(0))
        nu=sum((a*a for a in u),Fraction(0));nv=sum((b*b for b in v),Fraction(0))
        lagrange=sum(((u[i]*v[j]-u[j]*v[i])**2 for i in range(len(u)) for j in range(i+1,len(u))),Fraction(0))
        gap=nu*nv-dot*dot
        if gap!=lagrange: raise AssertionError("Lagrange identity failed")
        return dict(gap=gap,sum_minor_squares=lagrange,equality=(gap==0),zero_vector_allowed=True)
    if op=="quotient_polynomial_derivative":
        u,v=vec(d["u"],1,5),vec(d["v"],1,5)
        x=rat(d["x"]); U=poly(u,x);V=poly(v,x)
        if V==0: raise InvalidDomain("Denominator polynomial zero at point")
        du=poly([j*val for j,val in enumerate(u)][1:],x)
        dv=poly([j*val for j,val in enumerate(v)][1:],x)
        return dict(numerator_value=U,denominator_value=V,
                    derivative=(du*V-U*dv)/(V*V),pointwise_only=True)
    if op=="union_probability":
        n=integer(d["n"],1,12)
        A,B=d["A"],d["B"]
        if type(A) is not list or type(B) is not list or any(type(x) is not int or x<0 or x>=n for x in A+B):
            raise InvalidDomain("Invalid outcome indices")
        if len(set(A))!=len(A) or len(set(B))!=len(B):raise InvalidDomain("Duplicate outcome index")
        w=d.get("weights")
        if w is None: w=[Fraction(1,n)]*n
        else:
            if type(w) is not list or len(w)!=n: raise InvalidDomain("Invalid probability weights")
            w=[rat(z) for z in w]
            if any(z<0 for z in w) or sum(w)!=1: raise InvalidDomain("Probabilities nonnegative, sum one")
        a,b=set(A),set(B)
        prob=lambda S:sum((w[z] for z in S),Fraction(0))
        return dict(p_a=prob(a),p_b=prob(b),p_intersection=prob(a&b),p_union=prob(a|b),
                    zero_probability_does_not_imply_empty=(prob(a&b)==0 and bool(a&b)))
    if op=="hypergeometric":
        N,K,n,k=(integer(d[p],1 if p=="N" else 0,100) for p in ("N","K","n","k"))
        if K>N or n>N or not max(0,n-(N-K))<=k<=min(n,K):
            raise InvalidDomain("k outside valid hypergeometric support")
        return dict(total_subsets=comb(N,n),point_probability=Fraction(comb(K,k)*comb(N-K,n-k),comb(N,n)))
    if op=="vector_angle":
        u,v=vec(d["u"]),vec(d["v"])
        if len(u)!=len(v):raise InvalidDomain("Mismatched vector dimension")
        if all(z==0 for z in u) or all(z==0 for z in v):
            raise InvalidDomain("Angle undefined for zero vector")
        return dict(dot=sum(a*b for a,b in zip(u,v)),perpendicular=(sum(a*b for a,b in zip(u,v))==0))
    if op=="odd_square_induction":
        n=integer(d["n"],1,1000)
        return dict(previous_sum=n*n,next_term=2*n+1,next_sum=n*n+2*n+1,expected_next=(n+1)**2)
    if op=="fermat_difference":
        h=rat(d["h"])
        if h==0:raise InvalidDomain("Difference quotient requires h != 0")
        return dict(h=h, difference_quotient=-h, side="RIGHT" if h>0 else "LEFT",
                    required_sign_holds=(-h<=0 if h>0 else -h>=0))
    if op=="point_plane_distance":
        p,q,v=vec(d["P"],3,3),vec(d["Q"],3,3),vec(d["normal"],3,3)
        if all(z==0 for z in v):
            raise InvalidDomain("Plane requires nonzero normal vector")
        top=sum((a-b)*z for a,b,z in zip(p,q,v))
        norm2=sum(z*z for z in v)
        return dict(distance_squared=top*top/norm2)
    raise KeyError("unsupported operation")

SUPPORTED=frozenset(("log_product_domain","log_quotient_domain","log_change_base_domain",
    "quadratic_discriminant","amgm_rational_roots","line_circle","circle_circle",
    "parabola_focus","ellipse_tangent","cauchy_schwarz",
    "quotient_polynomial_derivative","union_probability","hypergeometric",
    "vector_angle","odd_square_induction","fermat_difference","point_plane_distance"))

def evaluate(op, data):
    flags=dict(student_step_verified=False,complete_theorem_certified=False,
               teacher_approved=False,official_curriculum_atom_verified=False)
    if op not in SUPPORTED:
        return dict(status="UNSUPPORTED",reason="Unknown bounded operation",**flags)
    if type(data) is not dict or len(data)>15:
        return dict(status="CONDITIONS_NOT_ESTABLISHED",reason="Expected bounded structured inputs",**flags)
    try:
        result=_compute(op,data)
        def encode(x):
            if isinstance(x,Fraction):return str(x)
            if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
            return x
        return dict(status="VERIFIED_FINITE_INSTANCE",witness=encode(result),
                    reason="Exact bounded operands only; no general proof certification",**flags)
    except (InvalidDomain,KeyError,ZeroDivisionError,OverflowError) as e:
        return dict(status="CONDITIONS_NOT_ESTABLISHED",reason=str(e)[:180],**flags)
