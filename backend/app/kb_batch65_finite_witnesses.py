"""Batch65 exact finite witnesses. These do NOT certify general theorems or student prose.

Only integers/Fraction exact arithmetic. No float, booleans, symbolic assumptions or
natural-language freeform proofs accepted. Out-of-scope input raises FailedPremise.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import gcd

class FailedPremise(ValueError): pass

def rational(x):
    if type(x) is int: return F(x)
    if type(x) is F: return x
    raise FailedPremise("exact integer/Fraction only; no float/bool")

def finite_quantifier(values, predicate):
    if type(values) not in (tuple,list) or not values or len(values)>128:
        raise FailedPremise("nonempty finite bounded domain needed")
    results=[predicate(rational(v)) for v in values]
    if any(type(v) is not bool for v in results):
        raise FailedPremise("predicate must return actual bool")
    return (all(results),any(results),any(not x for x in results),all(not x for x in results))

def inequality_scaled(a,b,c):
    a,b,c=map(rational,(a,b,c))
    if a>=b or c==0: raise FailedPremise("strict premise a<b and nonzero factor")
    return ("<" if c>0 else ">", a*c,b*c)

def quadratic_discriminant(a,b,c):
    a,b,c=map(rational,(a,b,c))
    if a==0: raise FailedPremise("nonzero quadratic coefficient required")
    d=b*b-4*a*c
    return (d,2 if d>0 else (1 if d==0 else 0))

def quadratic_sign(a,b,c,x):
    a,b,c,x=map(rational,(a,b,c,x))
    if a==0: raise FailedPremise("must be quadratic")
    v=a*x*x+b*x+c
    return -1 if v<0 else (1 if v>0 else 0)

def real_rational_power_domain(base,m,n):
    base=rational(base)
    if type(m) is not int or type(n) is not int or n<=0 or gcd(abs(m),n)!=1:
        raise FailedPremise("reduced rational exponent m/n with n>0 required")
    if n%2==0 and base<0: return False
    if m<0 and base==0: return False
    if m==0 and base==0: raise FailedPremise("0**0 not defined by this contract")
    return True

def log_monotone_orientation(base,x,y):
    base,x,y=map(rational,(base,x,y))
    if base<=0 or base==1 or x<=0 or y<=0 or x==y:
        raise FailedPremise("log base and positive distinct arguments required")
    return ("<" if (x<y)==(base>1) else ">")

def unit_circle_rational_pair(c,s):
    c,s=map(rational,(c,s))
    if c*c+s*s!=1:
        raise FailedPremise("pair not an attested rational point of unit circle")
    return (c*c+s*s,c!=0)

def polynomial_value(coeffs,x):
    if type(coeffs) not in (list,tuple) or not 1<=len(coeffs)<=6:
        raise FailedPremise("bounded polynomial degree 0..5 only")
    x=rational(x)
    total=F(0)
    for c in coeffs: total=total*x+rational(c)
    return total

def polynomial_bisect(coeffs,lo,hi,steps):
    lo,hi=map(rational,(lo,hi))
    if len(coeffs)<2 or lo>=hi or type(steps) is not int or not 1<=steps<=24:
        raise FailedPremise("strict bracket and bounded steps required")
    a=polynomial_value(coeffs,lo)
    b=polynomial_value(coeffs,hi)
    if a*b>=0: raise FailedPremise("endpoint signs must be strictly opposite")
    initial=hi-lo
    for _ in range(steps):
        m=(lo+hi)/2
        v=polynomial_value(coeffs,m)
        if v==0: return (m,m,True)
        if a*v<0: hi=m;b=v
        else: lo=m;a=v
    assert hi-lo==initial/F(2**steps)
    return (lo,hi,False) # existence only; never uniqueness

def vector_basis_coefficients(u,v,w):
    if any(type(t) not in (tuple,list) or len(t)!=2 for t in (u,v,w)):
        raise FailedPremise("2D coordinates expected")
    ax,ay=map(rational,u);bx,by=map(rational,v);wx,wy=map(rational,w)
    determinant=ax*by-ay*bx
    if determinant==0: raise FailedPremise("basis cannot be collinear")
    a=(wx*by-wy*bx)/determinant
    b=(ax*wy-ay*wx)/determinant
    assert (a*ax+b*bx,a*ay+b*by)==(wx,wy)
    return (a,b,determinant)

def complex_quotient(a,b,c,d):
    a,b,c,d=map(rational,(a,b,c,d))
    norm=c*c+d*d
    if norm==0: raise FailedPremise("complex divisor zero")
    return ((a*c+b*d)/norm,(b*c-a*d)/norm)

def line_intersection_3d(origin_a,dir_a,origin_b,dir_b):
    values=(origin_a,dir_a,origin_b,dir_b)
    if any(type(t) not in (tuple,list) or len(t)!=3 for t in values):
        raise FailedPremise("3D line data required")
    p,u,q,v=([rational(x) for x in t] for t in values)
    if all(x==0 for x in u) or all(x==0 for x in v):
        raise FailedPremise("line direction cannot be zero")
    pairs=((0,1),(0,2),(1,2))
    for i,j in pairs:
        det=u[j]*v[i]-u[i]*v[j]
        if det!=0:
            d1=q[i]-p[i];d2=q[j]-p[j]
            t=(-d1*v[j]+d2*v[i])/det
            s=(u[i]*d2-u[j]*d1)/det
            point=[p[k]+t*u[k] for k in range(3)]
            if all(point[k]==q[k]+s*v[k] for k in range(3)):
                return tuple(point)
            return None # skew, the projected crossing is not a real 3D intersection
    if all((q[i]-p[i])*u[j]==(q[j]-p[j])*u[i] for i,j in pairs):
        return tuple(p) # coincident; caller must separately distinguish
    return None # parallel non-coincident

def equiprobable_event_probability(outcomes,positive,event):
    if type(positive) is not bool or positive is not True:
        raise FailedPremise("explicit uniform elementary outcomes attestation required")
    if type(outcomes) not in (list,tuple) or type(event) not in (list,tuple):
        raise FailedPremise("finite outcomes required")
    if len(outcomes)==0 or len(outcomes)>128 or len(set(outcomes))!=len(outcomes):
        raise FailedPremise("nonempty unique elementary outcomes required")
    if len(set(event))!=len(event) or not set(event).issubset(set(outcomes)):
        raise FailedPremise("event must be subset, no duplicate counting")
    return F(len(event),len(outcomes))

def polynomial_differential(coeffs,x0,dx):
    x0,dx=map(rational,(x0,dx))
    if dx==0: raise FailedPremise("nonzero increment needed to compare finite difference")
    derivative=[c*(len(coeffs)-i-1) for i,c in enumerate(map(rational,coeffs[:-1]))]
    linear=polynomial_value(derivative,x0)*dx if derivative else F(0)
    finite=polynomial_value(coeffs,x0+dx)-polynomial_value(coeffs,x0)
    return (linear,finite,finite-linear) # exact witness, not asymptotic general proof
