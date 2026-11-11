"""Independent exact/finite Batch96 witnesses, not universal theorem certification."""
from __future__ import annotations
from fractions import Fraction as Q
from math import comb
from sympy import Symbol, Abs, diff, limit, oo, pi, sin, cos, simplify, sqrt, Matrix

IDS=("KB80-A038-L018-C01","KB80-A039-L009-C02","KB80-A042-L019-C01",
     "KB80-A043-L024-C01","KB80-A047-L001-C01","KB80-A047-L028-C01",
     "KB80-A048-L018-C01","KB80-A048-L020-C01","KB80-A052-L022-C01",
     "KB80-A054-L018-C01","KB80-A065-L006-C03","KB80-A064-L007-C01")

def arithmetic_nth(a,d,n):
    if type(a) not in (int,Q) or type(d) not in (int,Q) or type(n) is not int or n<1:
        raise ValueError('arithmetic series requires exact scalars, positive index')
    return Q(a)+(n-1)*Q(d)

def normalize_vector(v):
    if type(v) is not tuple or len(v)!=3 or any(type(x) not in (int,Q) for x in v):
        raise ValueError('three exact vector components required')
    sq=sum((Q(x)*x for x in v),Q(0))
    if sq==0:raise ValueError('zero vector has no unit direction')
    return tuple(simplify(Q(x)/sqrt(sq)) for x in v)

def classify_lines(l1,l2):
    if any(type(v) not in (int,Q) for row in (l1,l2) for v in row) or any(len(row)!=3 for row in (l1,l2)):
        raise ValueError('exact three coefficients per line')
    a,b,c=map(Q,l1);u,v,w=map(Q,l2)
    if (a,b)==(0,0) or (u,v)==(0,0):raise ValueError('nonzero line normals required')
    if a*v-b*u==0:
        return 'COINCIDENT' if a*w-c*u==0 and b*w-c*v==0 else 'PARALLEL_DISTINCT'
    return 'PERPENDICULAR' if a*u+b*v==0 else 'INTERSECTING'

def binomial_coefficient(n,k):
    if type(n) is not int or type(k) is not int or n<0 or k<0 or k>n:
        raise ValueError('finite nonnegative integer binomial domain')
    return comb(n,k)

def normal_standardize(mu,variance,x):
    from sympy import sqrt
    if any(type(v) not in (int,Q) for v in (mu,variance,x)) or variance<=0:
        raise ValueError('positive exact variance required')
    return simplify((Q(x)-Q(mu))/sqrt(Q(variance)))

def regression_residual(intercept,slope,x,y):
    if any(type(v) not in (int,Q) for v in (intercept,slope,x,y)):
        raise ValueError('exact regression inputs required')
    return Q(y)-(Q(intercept)+Q(slope)*Q(x))

def table_row_proportion(a,b,c,d,which=0):
    if any(type(v) is not int or v<0 for v in (a,b,c,d)) or a+b+c+d==0 or type(which) is not int or which not in (0,1):
        raise ValueError('nonnegative integer table with positive total')
    numerator,denominator=((a,a+b) if which==0 else (c,c+d))
    if denominator==0:raise ValueError('empty conditioning row')
    return Q(numerator,denominator)

def dot_cross(u,v):
    # Dot and cross products are defined for zero vectors; only the direction,
    # angle cosine, or normalization requires nonzero vectors.
    if any(type(w) is not tuple or len(w)!=3 or
           any(type(x) not in (int,Q) for x in w) for w in (u,v)):
        raise ValueError('three exact vector components required')
    a,b=Matrix(u),Matrix(v)
    return Q(a.dot(b)),tuple(a.cross(b))

def helix_point(radius,rise,t):
    if type(radius) not in (int,Q) or radius<=0 or type(rise) not in (int,Q) or type(t) not in (int,Q):
        raise ValueError('positive radius and exact phase turns required')
    # t is number of complete turns, not radians.
    return simplify(Q(radius)*cos(2*pi*Q(t))),simplify(Q(radius)*sin(2*pi*Q(t))),simplify(2*pi*Q(rise)*Q(t))

def check(i):
    if type(i) is not int or not 1<=i<=len(IDS):raise ValueError('unknown witness')
    x=Symbol('x',real=True)
    if i==1:
        pos=(arithmetic_nth(80,6,5)==104 and arithmetic_nth(3,4,5)==19)
        neg=arithmetic_nth(100,10,3)!=121
    elif i==2:
        q=Abs(x)/x
        pos=(limit(x**2/x,x,0,dir='+')==limit(x**2/x,x,0,dir='-')==0)
        neg=(limit(q,x,0,dir='+')==1 and limit(q,x,0,dir='-')==-1)
    elif i==3:
        pos=(normalize_vector((3,4,0))==(Q(3,5),Q(4,5),0))
        try:normalize_vector((0,0,0));neg=False
        except ValueError:neg=True
    elif i==4:
        pos=(classify_lines((1,2,-3),(2,4,-5))=='PARALLEL_DISTINCT' and
             classify_lines((1,2,0),(2,-1,-1))=='PERPENDICULAR')
        try:classify_lines((0,0,1),(1,2,3));neg=False
        except ValueError:neg=True
    elif i==5:
        pos=binomial_coefficient(4,1)*2**3*(-1)==-32 and sum(comb(3,k) for k in range(4))==8
        try:binomial_coefficient(-1,2);neg=False
        except ValueError:neg=True
    elif i==6:
        pos=normal_standardize(10,4,12)==1 and normal_standardize(0,9,-3)==-1
        try:normal_standardize(0,0,1);neg=False
        except ValueError:neg=True
    elif i==7:
        pos=(regression_residual(1,2,3,10)==3 and regression_residual(2,1,0,1)==-1)
        neg=(regression_residual(2,1,2,5)==1 and (-1+1)==0 and ((-1)**2+1**2)>0)
    elif i==8:
        pos=(table_row_proportion(20,80,30,20)==Q(1,5) and table_row_proportion(20,80,30,20,1)==Q(3,5))
        try:table_row_proportion(0,0,3,4);neg=False
        except ValueError:neg=True
    elif i==9:
        # A finite diagnostic only: rational n/(n+2) increases and is <1 for n≥1.
        vals=[Q(n,n+2) for n in range(1,60)]
        pos=all(a<b<1 for a,b in zip(vals,vals[1:]))
        neg=(((-1)**2)!=((-1)**3) and abs((-1)**2)<=1 and abs((-1)**3)<=1)
    elif i==10:
        pos=(dot_cross((1,0,0),(0,2,0))==(0,(0,0,2)) and
             dot_cross((0,0,0),(1,0,0))==(0,(0,0,0)))
        # Undefined is a *direction/normalization* of a zero vector, not its
        # valid dot or cross product.
        try:normalize_vector((0,0,0));neg=False
        except ValueError:neg=True
    elif i==11:
        pos=all(n*n>=0 for n in range(-50,51))
        neg=(40*40+40+41==41*41)
    else:
        p0=helix_point(2,1,0);p1=helix_point(2,1,1)
        pos=(p0==(2,0,0) and simplify(p1[2]-p0[2])==2*pi)
        neg=(p0!=p1 and helix_point(3,0,0)==helix_point(3,0,1))
    if type(pos) is not bool or type(neg) is not bool or not (pos and neg):
        raise AssertionError('finite witness invalid, id='+str(i))
    return {'finite_positive_case':True,'invalid_premise_or_overgeneralization':True,
            'general_theorem_certified':False,'teacher_approved':False,'student_publishable':False,
            'scope':'CONTROLLED_EXACT_OR_FINITE_CASES_ONLY'}

def verify_all():
    return {a:check(i) for i,a in enumerate(IDS,1)}
