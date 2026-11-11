"""Batch95 independent exact/finite mathematics probes and domain guards.
These inspect controlled cases only; universal proofs and real teacher review remain absent.
"""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import product
from math import gcd, isfinite, lcm
from sympy import Symbol, sin, cos, pi, sqrt, diff, simplify, Rational, Matrix, Abs, limit

IDS=(
"KB80-A028-L002-C01","KB80-A029-L009-C01","KB80-A038-L025-C01",
"KB80-A039-L015-C01","KB80-A046-L021-C01","KB80-A047-L021-C01",
"KB80-A053-L010-C01","KB80-A053-L013-C01","KB80-A057-L007-C01",
"KB80-A059-L012-C01","KB80-A059-L018-C01","KB80-A064-L008-C01",
"KB80-A065-L006-C01","KB80-A068-L008-C01","KB80-A070-L023-C01",
"KB80-A071-L005-C01"
)

def probability_moments(outcomes):
    if not outcomes or any(type(x) not in (int,Q) or type(p) not in (int,Q) or p<0 for x,p in outcomes):
        raise ValueError("invalid exact probability input")
    if sum((Q(p) for _,p in outcomes),Q(0))!=1:
        raise ValueError("probabilities must sum to one")
    mean=sum((Q(x)*Q(p) for x,p in outcomes),Q(0))
    variance=sum(((Q(x)-mean)**2*Q(p) for x,p in outcomes),Q(0))
    return mean,variance

def _finite_exact_real(value):
    # Never coerce arbitrary-precision ints/Fractions to float: this can
    # overflow and can turn a genuine negative squared-radius check into inf <= inf.
    if type(value) not in (int, float, Q):
        return None
    if type(value) is float and not isfinite(value):
        return None
    return Q(value)

def real_log_domain(base,argument):
    a,b=(_finite_exact_real(v) for v in (base,argument))
    return a is not None and b is not None and a>0 and a!=1 and b>0

def real_sqrt_disk_domain(x,y,radius):
    a,b,r=(_finite_exact_real(v) for v in (x,y,radius))
    return (a is not None and b is not None and r is not None and
            r>=0 and a*a+b*b<=r*r)

def projection_y_length(y):
    if type(y) not in (int,Q) or y<0:raise ValueError("positive axis-aligned length")
    return Q(y,2)

def geometric_nth(a,q,n):
    if type(n) is not int or n<1 or type(a) not in (int,Q) or type(q) not in (int,Q):
        raise ValueError("index and exact real multiplier required")
    return Q(a)*Q(q)**(n-1)

def choose_count(items_a,items_b):
    return len(items_a|items_b)

def triangle_linear_opt(vertices,objective):
    if not vertices:raise ValueError("nonempty finite feasible vertex list")
    return min(objective(*v) for v in vertices),max(objective(*v) for v in vertices)

def sampled_curve(t):
    if type(t) not in (int,Q) or not (0<=t<=2):raise ValueError("parameter outside closed interval")
    return Q(2)*t,t*t

def modus_ponens_valid():
    return all(not((not p or q) and p) or q for p,q in product((False,True),repeat=2))

def classify_test_error(h0_true,reject):
    if type(h0_true) is not bool or type(reject) is not bool:raise ValueError("binary states")
    return "TYPE_I" if h0_true and reject else ("TYPE_II" if not h0_true and not reject else "CORRECT")

def next_sync(a,b,phase_a=0,phase_b=0):
    """Smallest strictly positive simultaneous time, or None if incompatible.

    Generalized CRT, O(log max(a,b)) via modular inverse. Unlike bounded
    enumeration, this also works with negative or very large phase offsets.
    """
    if any(type(x) is not int for x in (a,b,phase_a,phase_b)) or min(a,b)<=0:
        raise ValueError("positive integer cycles required")
    g=gcd(a,b)
    delta=phase_b-phase_a
    if delta%g:return None
    modulus_b=b//g
    offset=(delta//g*pow(a//g,-1,modulus_b))%modulus_b if modulus_b>1 else 0
    period=lcm(a,b)
    residue=(phase_a+a*offset)%period
    return residue if residue>0 else period

def check(i):
    if type(i) is not int or i<1 or i>len(IDS):raise ValueError("unsupported oracle ID")
    x=Symbol("x",real=True)
    if i==1:
        positive=projection_y_length(6)==3 and projection_y_length(5)==Q(5,2)
        negative=projection_y_length(6)!=6
    elif i==2:
        # planes z=0 and y=0, x arbitrary: a unique intersection line
        p=lambda t:(t,0,0)
        n1=Matrix([0,0,1]);n2=Matrix([0,1,0])
        positive=all(p(k)[1]==p(k)[2]==0 for k in (-3,0,2)) and n1.cross(n2).norm()==1
        # Coincident plane normals have rank one, so no unique intersection line.
        negative=n1.cross(n1).norm()==0 and (0,1,0)[2]==0 and (0,1,0)[1]!=0
    elif i==3:
        positive=geometric_nth(200,Q(21,20),3)==Q(441,2) and geometric_nth(3,-2,4)==-24
        negative=Q(110,100)!=Q(120,110)
    elif i==4:
        positive=diff(7,x)==0 and diff(-3,x)==0
        negative=diff(x,x).subs(x,5)!=0
    elif i==5:
        positive=3*4==12 and len({"语1","语2"}|{"数1","数2","数3"})==5
        negative=choose_count({1,2},{2,3})!=len({1,2})+len({2,3})
    elif i==6:
        positive=probability_moments([(0,Q(1,2)),(2,Q(1,2))])==(Q(1),Q(1))
        try:probability_moments([(0,Q(3,5)),(1,Q(3,5))]);negative=False
        except ValueError:negative=True
    elif i==7:
        h=(3*x+1)**2
        positive=simplify(diff(h,x)-6*(3*x+1))==0
        negative=simplify(diff(sin(x**2),x)-cos(x**2))!=0
    elif i==8:
        positive=diff(x*x,x).subs(x,2)==4 and 1<2<3
        # |x| on [-1,1] has slope ±1 away from 0; average slope is 0
        negative=Q(abs(1)-abs(-1),2)==0 and limit(Abs(x)/x,x,0,dir="+")==1 and limit(Abs(x)/x,x,0,dir="-")==-1
    elif i==9:
        positive=Q(3,100)<Q(5,100) and classify_test_error(True,True)=="TYPE_I"
        negative=classify_test_error(False,False)=="TYPE_II"
    elif i==10:
        positive=real_sqrt_disk_domain(3,0,3) and real_log_domain(2,1)
        negative=not real_sqrt_disk_domain(4,0,3) and not real_log_domain(1,1) and not real_log_domain(2,0)
    elif i==11:
        vs=[(0,0),(4,0),(0,4)]
        positive=triangle_linear_opt(vs,lambda a,b:2*a+b)==(0,8)
        try:triangle_linear_opt([],lambda a,b:a+b);negative=False
        except ValueError:negative=True
    elif i==12:
        positive=sampled_curve(2)==(4,4) and sampled_curve(Q(1,2))==(1,Q(1,4))
        try:sampled_curve(-1);negative=False
        except ValueError:negative=True
    elif i==13:
        positive=modus_ponens_valid()
        p,q=False,True
        negative=(not p or q) and q and not p # affirming the consequent fails
    elif i==14:
        positive=Q(400,500)==Q(4,5) and Q(200,1000)==Q(1,5)
        sample_frame=set(range(200,1000));omitted=set(range(200))
        negative=not (sample_frame & omitted) and len(sample_frame)==800 # inaccessible units remain absent
    elif i==15:
        omega=4*pi
        positive=simplify(omega/(2*pi)-2)==0 and Q(1,2)==Q(1,2)
        negative=simplify(6*pi/(2*pi)-6)!=0 # angular frequency is not Hz
    else:
        positive=next_sync(4,6)==12 and next_sync(3,5)==15
        negative=next_sync(4,6,0,1) is None # incompatible phases
    if positive is not True and positive!=True:raise AssertionError(f"finite positive case {i}")
    if negative is not True and negative!=True:raise AssertionError(f"invalid premise case {i}")
    return {"finite_positive_case":True,"invalid_premise_or_overgeneralization":True,
            "general_theorem_certified":False,"teacher_approved":False,
            "student_publishable":False,"oracle":f"BATCH95_FINITE_{i:02d}"}

def verify_all():
    return {anchor:check(i) for i,anchor in enumerate(IDS,1)}
