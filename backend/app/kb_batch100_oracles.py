"""Independent bounded exact-instance witnesses for Batch100 source-linked drafts.

Not a general theorem prover. Each witness checks a real positive numerical
instance and a deliberate invalid/degenerate premise separately.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import isfinite
from sympy import Matrix, Symbol, S, Rational, integrate, diff, linsolve, symbols

IDS=(0,2,3,4,5,6,7,9,10,11,12,13,15,16,17,18,19,21,30,31)

def nonzero(v):
    if len(v) == 0 or all(x==0 for x in v):
        raise ValueError("zero vector cannot define a line direction or angle")
    return v

def class_line_plane(normal, base, direction, c):
    # zip() silently truncates mismatched dimensions; that is not a valid 3D test.
    if not all(isinstance(v, (tuple, list)) and len(v) == 3
               for v in (normal, base, direction)):
        raise ValueError("normal, base and direction must all be 3D vectors")
    nonzero(normal);nonzero(direction)
    dot=sum(a*b for a,b in zip(normal,direction))
    off=sum(a*b for a,b in zip(normal,base))-c
    return "contained" if dot==off==0 else ("disjoint" if dot==0 else "unique")

def vector_add(a,b):
    if not a or len(a)!=len(b):raise ValueError("vector dimensions do not match")
    return tuple(x+y for x,y in zip(a,b))

def linear_delta(slope,epsilon):
    if epsilon<=0:raise ValueError("epsilon must be positive")
    return epsilon/abs(slope) if slope else F(1)

def projectile_curve(vx,vy,g):
    if vx==0 or g<=0:raise ValueError("horizontal speed nonzero and g positive required")
    X=Symbol("x",real=True)
    return (vy*(X/vx)-g*(X/vx)**2/2).expand()

def bin_assignment(x,bins):
    indices=[i for i,(lo,hi) in enumerate(bins) if lo<=x<=hi]
    if len(indices)!=1:raise ValueError("bins overlap or omit a sample")
    return indices[0]

def pair_balanced(a,b):
    if len(a)!=len(b) or not a or set(a+b) != {0,1}:raise ValueError("binary equal columns required")
    from collections import Counter
    counts=Counter(zip(a,b))
    return all(counts[(i,j)]==len(a)/4 for i in (0,1) for j in (0,1))

def quadratic_interval(a,b,c,left,right):
    if left>right:raise ValueError("reversed interval")
    candidates=[left,right]
    if a!=0:
        v=-F(b,2*a)
        if left<=v<=right:candidates.append(v)
    ys=[a*x*x+b*x+c for x in candidates]
    return min(ys),max(ys)

def matrix_prediction(x,y):
    X=Matrix(x);Y=Matrix(y)
    if (X.rows == 0 or X.cols == 0 or Y.cols != 1 or
            X.rows != Y.rows or X.rank() != X.cols):
        raise ValueError("nonempty design matrix needs one target column and full column rank")
    return (X.T*X).inv()*X.T*Y

def evaluate(i):
    if type(i) is not int or i not in IDS:raise ValueError("unknown witness id")
    x=Symbol("x",real=True); t=Symbol("t",real=True)
    good=bad=False
    if i==0:
        A=Matrix([1,2]);B=Matrix([3,6]);d=B-A
        good=(d!=Matrix([0,0]) and A+d==B and (A+2*d)==Matrix([5,10]))
        try:nonzero([0,0])
        except ValueError:bad=True
    elif i==2:
        u=Matrix([2,-1,3]);v=Matrix([-1,4,0])
        good=(vector_add(tuple(u),tuple(v))==(1,3,3) and u-v==Matrix([3,-5,3]))
        try:vector_add([1,2,3],[1,2])
        except ValueError:bad=True
    elif i==3:
        tp,sp=symbols("tp sp")
        good=list(linsolve([tp,-sp,S.Zero],(tp,sp)))==[(0,0)]
        bad=not bool(linsolve([tp,-sp,-1],(tp,sp)))
    elif i==4:
        good=(class_line_plane([0,0,1],[1,2,0],[1,0,0],0)=="contained" and
              class_line_plane([1,1,1],[1,0,1],[1,0,1],0)=="unique")
        bad=(class_line_plane([0,0,1],[1,2,1],[1,0,0],0)=="disjoint")
    elif i==5:
        Q=Matrix.diag(-1,1,1);v=Matrix([1,2,3])
        good=(Q.T*Q==Matrix.eye(3) and (Q*v).dot(Q*v)==v.dot(v))
        bad=(Matrix.diag(2,1,1).T*Matrix.diag(2,1,1)!=Matrix.eye(3))
    elif i==6:
        Q=Matrix([[0,-1,0],[1,0,0],[0,0,1]])
        good=(Q.T*Q==Matrix.eye(3) and Q.det()==1 and
              (Q*Matrix([1,2,3])).norm()**2==14)
        D=Matrix.diag(2,Rational(1,2),1)
        bad=(D.det()==1 and D.T*D!=Matrix.eye(3))
    elif i==7:
        eps=F(1,20);N=61
        good=(F(3,N)<eps and all(F(3,n)<eps for n in (N,N+1,1000)))
        bad=(F(3,60)==eps and not F(3,60)<eps)
    elif i==9:
        eps=F(1,10);delta=linear_delta(3,eps)
        good=(abs(3*(F(2,1)+delta/2)+1-7)<eps)
        try:linear_delta(3,F(0))
        except ValueError:bad=True
    elif i==10:
        good=(quadratic_interval(1,-4,0,F(0),F(5))==(F(-4),F(5)))
        try:quadratic_interval(1,-4,0,F(5),F(0))
        except ValueError:bad=True
    elif i==11:
        good=(integrate(x,(x,-2,2))==0 and integrate(abs(x),(x,-2,2))==4)
        bad=(integrate(1-x,(x,0,2))==0 and integrate(abs(1-x),(x,0,2))==1)
    elif i==12:
        verts=[(0,0),(2,0),(0,3),(2,3)]
        good=(max(3*a+b for a,b in verts)==9)
        bad=(all(-a*a-b*b<0 for a,b in ((-1,-1),(-1,1),(1,-1),(1,1)))
             and 0>max(-a*a-b*b for a,b in ((-1,-1),(-1,1),(1,-1),(1,1))))
    elif i==13:
        good=(min(a*a+b*b for a in (-1,0,1) for b in (-1,0,1))==0 and
              max(a*a+b*b for a in (-1,0,1) for b in (-1,0,1))==2)
        bad=(all(diff(x+Symbol('y'),v)!=0 for v in (x,Symbol('y'))))
    elif i==15:
        u=Matrix([2,1,0]);v=Matrix([-1,2,0])
        good=(u.dot(v)==0 and u.norm()!=0 and v.norm()!=0)
        try:nonzero([0,0,0])
        except ValueError:bad=True
    elif i==16:
        good=pair_balanced([0,0,1,1],[0,1,0,1])
        bad=not pair_balanced([0,0,1,1],[0,0,1,1])
    elif i==17:
        A=Matrix.diag(S.Half,0,S(1)/4);d=Matrix([2,3,3])
        result=(Matrix.eye(3)-A).inv()*d
        good=(result==Matrix([4,3,4]) and A*result+d==result)
        bad=((Matrix.eye(3)-Matrix.diag(2,0,0)).inv()*Matrix([1,1,1])==
             Matrix([-1,1,1]))
    elif i==18:
        good=(projectile_curve(2,3,2)==3*x/2-x*x/4)
        try:projectile_curve(0,3,2)
        except ValueError:bad=True
    elif i==19:
        domain=(-2,-1,0,1,2)
        good=all(n*n>=0 for n in domain)
        bad=not any(n*n<0 for n in domain)
    elif i==21:
        good=all((n*n+n)%2==0 for n in range(-20,21))
        bad=((41*41-41+41)==41**2 and 41**2%41==0)
    elif i==30:
        freqs=[3,5,4];relative=[F(a,sum(freqs)) for a in freqs]
        good=(sum(relative)==1 and relative==[F(1,4),F(5,12),F(1,3)])
        try:bin_assignment(10,[(0,10),(10,20)])
        except ValueError:bad=True
    elif i==31:
        good=(matrix_prediction([[1,0],[1,1],[1,2]],[1,3,5])==
              Matrix([1,2]))
        try:matrix_prediction([[1,1],[1,1],[1,1]],[2,3,4])
        except ValueError:bad=True
    if not (bool(good) and bool(bad)):
        raise ValueError(f"Batch100 exact witness {i} failed: positive={good}, invalid={bad}")
    return {"id":i,"exact_positive":True,"invalid_case_rejected":True,
            "scope":"BOUNDED_EXACT_INSTANCES_ONLY",
            "general_theorem_certified":False,"teacher_approved":False,
            "student_publishable":False}
def check_all():
    result={i:evaluate(i) for i in IDS}
    assert len(result)==20
    return result
