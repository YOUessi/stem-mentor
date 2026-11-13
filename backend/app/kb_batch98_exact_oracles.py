"""Batch98 independently callable, bounded exact-instance checks. Not a proof assistant."""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import product
from math import floor
from sympy import Matrix, sqrt

IDS=(
"KB80-A042-L016-C01","KB80-A043-L006-C01","KB80-A048-L003-C01",
"KB80-A048-L021-C01","KB80-A052-L010-C01","KB80-A053-L003-C01",
"KB80-A055-L017-C01","KB80-A060-L011-C01","KB80-A062-L003-C01",
"KB80-A063-L012-C01","KB80-A067-L008-C01","KB80-A069-L017-C01")

def q(x):
    if type(x) not in (int,Q): raise ValueError("exact rational required; floats and booleans rejected")
    return Q(x)

def vec(v,dim=3):
    if type(v) is not tuple or len(v)!=dim: raise ValueError("vector dimensionality mismatch")
    return Matrix([q(a) for a in v])

def cuboid_vertices(a,b,c):
    a,b,c=map(q,(a,b,c))
    if min(a,b,c)<=0:raise ValueError("positive orthogonal edge lengths")
    return {tuple((i*a,j*b,k*c)) for i,j,k in product((0,1),repeat=3)}

def point_line_sq(p,a,d):
    p,a,d=map(vec,(p,a,d))
    if d.dot(d)==0:raise ValueError("nonzero line direction")
    z=p-a
    return z.dot(z)-z.dot(d)**2/d.dot(d)

def point_plane_sq(p,a,n):
    p,a,n=map(vec,(p,a,n))
    if n.dot(n)==0:raise ValueError("nonzero plane normal")
    return (p-a).dot(n)**2/n.dot(n)

def normal_standardized(mu,variance,x):
    mu,v,x=map(q,(mu,variance,x))
    if v<=0:raise ValueError("strictly positive normal variance")
    return (x-mu)/sqrt(v)

def pearson_2x2(table):
    if type(table) is not tuple or len(table)!=2 or any(type(row) is not tuple or len(row)!=2 for row in table):raise ValueError("2x2 frequency table")
    a,b,c,d=(q(z) for row in table for z in row)
    if any(z<0 or z.denominator!=1 for z in (a,b,c,d)):raise ValueError("nonnegative integer frequencies")
    n=a+b+c+d
    if not n:raise ValueError("positive total frequency")
    exp=tuple(r*t/n for r in (a+b,c+d) for t in (a+c,b+d))
    if any(e<=0 for e in exp):raise ValueError("nonzero expectation required")
    observed=(a,b,c,d)
    return (sum(((o-e)**2/e for o,e in zip(observed,exp)),Q(0)), exp,
            all(e>=5 for e in exp)) # a heuristic approximation guard, NOT an automatic p-value

def reciprocal_epsilon_N(eps):
    eps=q(eps)
    if eps<=0: raise ValueError("epsilon must be positive")
    return floor(1/eps)+1 # strict n>1/epsilon bound

def squared_poly_on_closed_interval(lo,hi):
    lo,hi=map(q,(lo,hi))
    if lo>hi:raise ValueError("ordered nonempty closed interval")
    closest=max(lo,min(Q(0),hi))
    return (closest**2,max(lo**2,hi**2))

def apply_isometry(Qmat,p,b=(0,0)):
    if type(Qmat) is not tuple or len(Qmat)!=2 or any(type(r) is not tuple or len(r)!=2 for r in Qmat): raise ValueError("2x2 matrix")
    m=Matrix([[q(z) for z in r] for r in Qmat])
    if m.T*m!=Matrix.eye(2):raise ValueError("orthogonal matrix required")
    return tuple(m*vec(p,2)+vec(b,2))

def spatial_line_distance_sq(a,u,b,v):
    a,u,b,v=map(vec,(a,u,b,v))
    n=u.cross(v)
    if u.dot(u)==0 or v.dot(v)==0 or n.dot(n)==0:raise ValueError("distinct nonparallel directions required")
    return ((b-a).dot(n))**2/n.dot(n)

def bivariate_cov_determinant(sx,sy,rho):
    sx,sy,rho=map(q,(sx,sy,rho))
    if not (sx>0 and sy>0 and -1<rho<1):raise ValueError("positive marginal scales and |rho|<1")
    return sx*sx*sy*sy*(1-rho*rho)

def diagonal_input_output(a,b,d1,d2):
    a,b,d1,d2=map(q,(a,b,d1,d2))
    if min(a,b,d1,d2)<0 or a==1 or b==1:raise ValueError("nonnegative nondegenerate model")
    x=(d1/(1-a),d2/(1-b))
    if any(z<0 for z in x):raise ValueError("algebraic solution violates nonnegative output")
    return x

def discrete_growth(p0,r,n):
    p0,r=q(p0),q(r)
    if type(n) is not int or n<0 or p0<=0 or r<=-1:raise ValueError("positive initial state, positive factor, integer step")
    return p0*(1+r)**n

def circle_rotation(p,center,r):
    p,center=vec(p,2),vec(center,2)
    r=q(r)
    if r<=0 or (p-center).dot(p-center)!=r*r:raise ValueError("point must lie on positive radius circle")
    rot=Matrix([[0,-1],[1,0]])
    z=center+rot*(p-center)
    return (tuple(z),(z-center).dot(z-center))

def check(i):
    if type(i) is not int or i<1 or i>12:raise ValueError("unknown finite check")
    if i==1:
        positive=(len(cuboid_vertices(2,3,4))==8 and (2,3,4) in cuboid_vertices(2,3,4))
        invalid=lambda: cuboid_vertices(2,0,4)
    elif i==2:
        positive=point_line_sq((0,2,0),(0,0,0),(1,0,0))==4 and point_plane_sq((1,2,5),(0,0,1),(0,0,1))==16
        invalid=lambda:point_plane_sq((0,0,0),(0,0,0),(0,0,0))
    elif i==3:
        positive=normal_standardized(10,9,16)==2 and normal_standardized(-2,4,-4)==-1
        invalid=lambda:normal_standardized(0,0,1)
    elif i==4:
        val,exp,adequate=pearson_2x2(((10,20),(20,10)))
        positive=val==Q(20,3) and exp==(15,15,15,15) and adequate
        invalid=lambda:pearson_2x2(((2,0),(0,0)))
    elif i==5:
        positive=reciprocal_epsilon_N(Q(1,10))==11 and all(Q(1,n)<Q(1,10) for n in range(11,111))
        invalid=lambda:reciprocal_epsilon_N(0)
    elif i==6:
        positive=squared_poly_on_closed_interval(-2,1)==(0,4)
        invalid=lambda:squared_poly_on_closed_interval(2,1)
    elif i==7:
        positive=apply_isometry(((0,-1),(1,0)),(1,2))==(-2,1)
        invalid=lambda:apply_isometry(((2,0),(0,1)),(1,2))
    elif i==8:
        positive=spatial_line_distance_sq((0,0,0),(1,0,0),(0,0,2),(0,1,0))==4
        invalid=lambda:spatial_line_distance_sq((0,0,0),(1,0,0),(0,1,0),(2,0,0))
    elif i==9:
        positive=bivariate_cov_determinant(2,3,Q(1,2))==27
        invalid=lambda:bivariate_cov_determinant(1,1,1)
    elif i==10:
        positive=diagonal_input_output(Q(1,2),Q(1,4),4,3)==(8,4)
        invalid=lambda:diagonal_input_output(2,0,1,1)
    elif i==11:
        positive=discrete_growth(100,Q(1,10),2)==121
        invalid=lambda:discrete_growth(100,-1,2)
    else:
        positive=circle_rotation((1,0),(0,0),1)==((0,1),1)
        invalid=lambda:circle_rotation((2,0),(0,0),1)
    try: invalid();negative=False
    except ValueError:negative=True
    if not positive or not negative:raise AssertionError("positive / invalid-premise finite case failed")
    return dict(source_candidate_id=IDS[i-1],finite_positive_case=True,
                invalid_premise_rejected=True,general_theorem_certified=False,
                teacher_approved=False,student_publishable=False)

def verify_all():
    return {key:check(i) for i,key in enumerate(IDS,1)}
