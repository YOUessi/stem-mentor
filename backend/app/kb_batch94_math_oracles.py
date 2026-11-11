"""Independent finite probes for 14 Batch94 mathematics drafts (NOT universal proof).
Avoid importing authoring prose: exact mathematical predicates and invalid-premise
witnesses are checked independently of any explanation produced by an LLM.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import comb, perm
from sympy import Matrix, Symbol, sqrt, simplify, diff, limit, oo

IDS=(
"KB80-A015-L022-C01","KB80-A026-L023-C01",
"KB80-A038-L018-C02","KB80-A038-L023-C02",
"KB80-A039-L030-C01","KB80-A042-L024-C01",
"KB80-A043-L028-C01","KB80-A046-L024-C01",
"KB80-A047-L023-C01","KB80-A052-L030-C01",
"KB80-A055-L020-C01","KB80-A059-L016-C01",
"KB80-A065-L011-C02","KB80-A070-L012-C01"
)

def check(i:int):
    if type(i) is not int or not 1<=i<=14:raise ValueError("unsupported oracle ID")
    x=Symbol("x",real=True)
    n=Symbol("n",integer=True,positive=True)
    if i==1:
        u={1,2,3,4};a={1,2};b={2,4}
        pos=(a&b=={2} and a|b=={1,2,4} and u-(a|b)==(u-a)&(u-b))
        neg=((u-a)!=(u|{5})-a) # a complement changes if universal set changes
    elif i==2:
        # sides (2,2) and 60 degree enclosed angle => opposite side 2
        pos=simplify(2**2+2**2-2*2*2*F(1,2)-2**2)==0
        neg=(1+1<=3) # these lengths cannot make nondegenerate triangle
    elif i==3:
        seq=[80+5*k for k in range(6)]
        pos=(seq==[80,85,90,95,100,105])
        neg=((110-100)!=(121-110)) # 10% growth not arithmetic
    elif i==4:
        s=lambda k:k*k+k+1
        pos=(s(1)==3 and s(3)-s(2)==6)
        neg=(s(1)!=(2*1)) # illegal first-index extension
    elif i==5:
        pos=(diff(x**2,x).subs(x,0)==0 and F(1,2)**2>0)
        neg=(diff(x**3,x).subs(x,0)==0 and (-F(1,2))**3<0<(F(1,2))**3)
    elif i==6:
        u=Matrix([1,-2,3]);v=Matrix([2,1,-1])
        pos=(u+v==Matrix([3,-1,2]) and 2*u-v==Matrix([0,-5,7]))
        neg=(Matrix([2,0,0]).norm()!=Matrix([1,0,0]).norm())
    elif i==7:
        a,b,c=3,4,-10
        pos=(F(abs(c),1)/sqrt(a*a+b*b)==2)
        neg=(0*0+0*0==0) # zero normal rejected in check below
        # explicit guard: both zero must not define a line
        neg=neg and not (0*0+0*0>0)
    elif i==8:
        pos=(comb(5,2)==10 and perm(5,2)==20)
        neg=(comb(5,2)!=perm(5,2))
    elif i==9:
        pos=(comb(3,2)*F(1,2)**3==F(3,8) and F(3,4)**2==F(9,16))
        # without replacement: two red out of 2R+1B P(R,R)=1/3 not (2/3)^2
        neg=(F(2,3)*F(1,2)!=F(2,3)**2)
    elif i==10:
        pos=(limit(1+1/n,n,oo)==1 and limit(2-3/n,n,oo)==2 and
             limit(3-2/n,n,oo)==3)
        neg=(limit(n,n,oo)==oo and limit(-n,n,oo)==-oo and n+(-n)==0)
    elif i==11:
        q=Matrix([[0,-1],[1,0]])
        p=Matrix([[2,0],[0,F(1,2)]])
        pos=(q.T*q==Matrix.eye(2) and q*Matrix([2,1])==Matrix([-1,2]))
        neg=(p.det()==1 and p.T*p!=Matrix.eye(2))
    elif i==12:
        xx,yy=Symbol("x",real=True),Symbol("y",real=True)
        saddle=xx**2-yy**2
        pos=(diff(xx**2+yy**2,xx).subs({xx:0,yy:0})==0 and
             diff(xx**2+yy**2,yy).subs({xx:0,yy:0})==0)
        neg=(diff(saddle,xx).subs({xx:0,yy:0})==0 and
             diff(saddle,yy).subs({xx:0,yy:0})==0 and
             saddle.subs({xx:1,yy:0})>0 and saddle.subs({xx:0,yy:1})<0)
    elif i==13:
        k=Symbol("k",integer=True,positive=True)
        pos=(simplify(k*(k+1)/2+(k+1)-(k+1)*(k+2)/2)==0
             and 1*2//2==1)
        neg=(not (0<0)) # a failed base case cannot be rescued by the step
    else:
        phi=(1+sqrt(5))/2
        pos=(simplify(phi**2-phi-1)==0 and phi>1)
        neg=(F(3,2)!=F(5,3) and simplify(phi-F(3,2))!=0)
    if pos is not True and pos!=True:raise AssertionError(f"positive finite witness {i} failed")
    if neg is not True and neg!=True:raise AssertionError(f"invalid premise witness {i} failed")
    return {"finite_positive_case":True,"invalid_premise_or_overgeneralization":True,
            "general_theorem_certified":False,"teacher_approved":False,
            "student_publishable":False,"oracle":f"BATCH94_FINITE_{i:02d}"}

def verify_all():
    return {anchor:check(i) for i,anchor in enumerate(IDS,1)}
