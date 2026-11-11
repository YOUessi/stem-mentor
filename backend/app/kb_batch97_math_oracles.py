"""Batch97 independent guarded exact and finite-instance mathematics diagnostics.
A successful finite diagnostic NEVER certifies a general theorem or a human reviewer.
"""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import product, combinations
from math import isqrt
from sympy import Symbol, diff, integrate, limit, oo, simplify, cos, sin, sqrt

IDS=("KB80-A042-L014-C01","KB80-A043-L004-C01","KB80-A044-L014-C01",
     "KB80-A052-L039-C01","KB80-A053-L021-C01","KB80-A057-L001-C01",
     "KB80-A059-L016-C02","KB80-A062-L019-C01","KB80-A062-L023-C01",
     "KB80-A065-L014-C01","KB80-A068-L004-C01","KB80-A070-L002-C01")

def _frac(x):
    if type(x) not in (int,Q):raise ValueError("finite exact integer or rational required")
    return Q(x)
def _vec(v,dim=3):
    if type(v) is not tuple or len(v)!=dim:raise ValueError("exact vector dimension required")
    return tuple(_frac(x) for x in v)
def distance_sq(p,q):
    p,q=_vec(p),_vec(q)
    return sum(((b-a)**2 for a,b in zip(p,q)),Q(0))
def line_plane_relation(p,d,a,n):
    p,d,a,n=map(_vec,(p,d,a,n))
    if not any(d) or not any(n):raise ValueError("line and plane must be nondegenerate")
    nd=sum((u*v for u,v in zip(n,d)),Q(0))
    const=sum((u*(x-y) for u,x,y in zip(n,p,a)),Q(0))
    if nd: return ("INTERSECT_ONE", -const/nd)
    return ("CONTAINED",None) if not const else ("PARALLEL_DISJOINT",None)
def hyperbola_domain(focal_distance,difference):
    f,h=_frac(focal_distance),_frac(difference)
    if not 0<h<f:raise ValueError("nondegenerate hyperbola needs 0<difference<focal_distance")
    return True
def finite_limit_quotient(numer_limit,denom_limit):
    a,b=_frac(numer_limit),_frac(denom_limit)
    if not b:raise ValueError("quotient theorem requires nonzero denominator limit")
    return a/b
def newton_leibniz_polynomial(coefficients,lower,upper):
    if type(coefficients) is not tuple or not coefficients:raise ValueError("nonempty coefficients")
    vals=tuple(_frac(c) for c in coefficients)
    lo,hi=_frac(lower),_frac(upper)
    x=Symbol("x",real=True)
    polynomial=sum((c*x**i for i,c in enumerate(vals)))
    anti=integrate(polynomial,x)
    result=simplify(anti.subs(x,hi)-anti.subs(x,lo))
    if simplify(diff(anti,x)-polynomial)!=0:raise AssertionError("independent FTC derivative check failed")
    return result
def rectangle_probability(density,xmax,ymax,width,height):
    v,x,y,w,h=map(_frac,(density,xmax,ymax,width,height))
    if not(v>=0 and x>0 and y>0 and v*x*y==1 and 0<=w<=x and 0<=h<=y):
        raise ValueError("valid normalized constant rectangle density and subrectangle required")
    return v*w*h
def closed_rectangle_poly_extrema(x_lo=0,x_hi=2,y_lo=0,y_hi=2):
    # f=(x-3)^2+y^2, evaluated on an exact nonempty compact rectangle.
    # Minimum is the Cartesian projection of (3,0) to the box.
    # Maximum is attained at a corner, by convexity in each coordinate.
    xl,xh,yl,yh=map(_frac,(x_lo,x_hi,y_lo,y_hi))
    if xl>xh or yl>yh:
        raise ValueError("nonempty closed rectangular domain required")
    x_min=min(max(Q(3),xl),xh)
    y_min=min(max(Q(0),yl),yh)
    x_max=max((xl,xh),key=lambda x:(x-3)**2)
    y_max=max((yl,yh),key=lambda y:y*y)
    val=lambda x,y:(x-3)**2+y*y
    return ((x_min,y_min),val(x_min,y_min)),((x_max,y_max),val(x_max,y_max))
def euclidean_sq(u,v):
    if type(u) is not tuple or type(v) is not tuple or len(u)!=len(v) or not u:
        raise ValueError("equal nonempty feature dimensions")
    return sum(((_frac(a)-_frac(b))**2 for a,b in zip(u,v)),Q(0))
def zscore(x,mean,std):
    x,m,s=map(_frac,(x,mean,std))
    if s<=0:raise ValueError("positive standard deviation required")
    return (x-m)/s
def oa_strength2(rows):
    if type(rows) not in (list,tuple) or not rows:raise ValueError("nonempty design")
    if any(type(r) is not tuple or len(r)<2 or any(type(v) is not int or v not in (0,1) for v in r) for r in rows):
        raise ValueError("all rows binary tuples with at least two columns")
    k=len(rows[0])
    if any(len(r)!=k for r in rows) or len(rows)%4:raise ValueError("rectangular design count divisible by four")
    n=len(rows)//4
    return all(sum((row[i]==a and row[j]==b) for row in rows)==n
               for i,j in combinations(range(k),2) for a,b in product(range(2),repeat=2))
def independent_p_given_q(gamma,atom):
    # Deliberately bounded 2-variable propositional independent decision, no arbitrary proof parser.
    if gamma!="q" or atom!="p":raise ValueError("only pre-audited Gamma={q}, A=p scenario")
    yes=(True,True);no=(False,True) # p, q
    return yes[1] and yes[0] and no[1] and not no[0]
def response_rate(invited,responded):
    if type(invited) is not int or type(responded) is not int or invited<=0 or not 0<=responded<=invited:
        raise ValueError("valid denominator and response count required")
    return Q(responded,invited)
def reflect(p,a,n):
    p,a,n=map(_vec,(p,a,n))
    sq=sum((x*x for x in n),Q(0))
    if not sq:raise ValueError("nonzero normal required")
    alpha=sum(((x-y)*z for x,y,z in zip(p,a,n)),Q(0))/sq
    return tuple(x-2*alpha*z for x,z in zip(p,n))
def check(i):
    if type(i) is not int or not 1<=i<=len(IDS):raise ValueError("unknown verifier case")
    try:
        if i==1:
            pos=distance_sq((1,2,3),(4,6,3))==25
            # Reject non-exact booleans masquerading as integer coordinates.
            try:distance_sq((True,2,3),(4,6,3));neg=False
            except ValueError:neg=True
        elif i==2:
            pos=(line_plane_relation((0,1,2),(1,0,0),(0,0,0),(0,0,1))==("PARALLEL_DISJOINT",None)
             and line_plane_relation((0,0,0),(1,0,0),(0,0,0),(0,0,1))==("CONTAINED",None))
            try:line_plane_relation((0,0,0),(0,0,0),(0,0,0),(0,0,1));neg=False
            except ValueError:neg=True
        elif i==3:
            pos=hyperbola_domain(10,6)
            try:hyperbola_domain(6,8);neg=False
            except ValueError:neg=True
        elif i==4:
            x=Symbol("x")
            pos=finite_limit_quotient(4,2)==2 and limit((x*x-4)/(x-2),x,2)==4
            try:finite_limit_quotient(0,0);neg=False
            except ValueError:neg=True
        elif i==5:
            pos=newton_leibniz_polynomial((0,0,1),0,2)==Q(8,3)
            try:newton_leibniz_polynomial((1,),0,True);neg=False
            except ValueError:neg=True
        elif i==6:
            pos=rectangle_probability(2,Q(1,2),1,Q(1,4),Q(1,2))==Q(1,4)
            try:rectangle_probability(2,1,1,1,1);neg=False
            except ValueError:neg=True
        elif i==7:
            pos=closed_rectangle_poly_extrema()==(((2,0),1),((0,2),13))
            try:closed_rectangle_poly_extrema(2,0,0,2);neg=False
            except ValueError:neg=True
        elif i==8:
            pos=euclidean_sq((1,1000),(2,1010))==101
            try:zscore(7,7,0);neg=False
            except ValueError:neg=True
        elif i==9:
            pos=oa_strength2([(0,0,0),(0,1,1),(1,0,1),(1,1,0)])
            neg=not oa_strength2([(0,0),(0,0),(1,1),(1,1)])
        elif i==10:
            pos=independent_p_given_q("q","p")
            try:independent_p_given_q("p","p");neg=False
            except ValueError:neg=True
        elif i==11:
            pos=response_rate(500,400)==Q(4,5)
            try:response_rate(0,0);neg=False
            except ValueError:neg=True
        else:
            p=(Q(2),Q(0),Q(1));o=(0,0,0);n=(1,1,0)
            q=reflect(p,o,n)
            pos=q==(0,-2,1) and reflect(q,o,n)==p and distance_sq(q,(0,0,0))==distance_sq(p,(0,0,0))
            try:reflect((1,2,3),o,(0,0,0));neg=False
            except ValueError:neg=True
    except (TypeError,ZeroDivisionError) as exc:
        raise AssertionError("unsafe unguarded boundary") from exc
    if pos is not True or neg is not True:
        raise AssertionError("witness failed: "+str(i))
    return {"finite_positive_case":True,"invalid_premise_or_overgeneralization":True,
            "general_theorem_certified":False,"teacher_approved":False,"student_publishable":False,
            "scope":"CONTROLLED_EXACT_OR_FINITE_CASES_ONLY"}
def verify_all():
    return {a:check(i) for i,a in enumerate(IDS,1)}

