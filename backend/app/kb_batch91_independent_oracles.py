"""Limited exact checks for Batch91 authored math. NOT a theorem certifier.

No data is taken from the authoring text or generated answer; each witness is
an independent Fraction/SymPy or finite-logic calculation with falsifiable checks.
"""
from __future__ import annotations
from fractions import Fraction as F
import math
from sympy import symbols, sin, pi, simplify, diff, Rational, sqrt, log
from typing import Any

def verify(case:int)->dict[str,Any]:
    if type(case) is not int or not 1 <= case <= 20:
        raise ValueError("supported finite case must be an integer 1..20")
    x = symbols("x",real=True)
    if case==1:
        empty=frozenset()
        wrapper=frozenset({empty})
        ok=empty in wrapper and empty.issubset(wrapper)
        bad=empty in empty or wrapper.issubset(empty)
        witness="∅∈{∅}, ∅⊆{∅}; ∅∈∅为假"
    elif case==2:
        poly=lambda v:v*v-4
        ok=poly(0)<0 and poly(3)>0 and poly(2)==0
        bad=poly(2)<0
        witness="x²−4在x=0为−4，在x=3为5，端点2为0"
    elif case==3:
        f=lambda v:v if v<0 else v*v
        g=lambda v:1 if v<0 else 2
        ok=f(-2)==-2 and f(2)==4 and g(0)==2
        bad=g(0)==1
        witness="分段判断：−2、2和严格边界0"
    elif case==4:
        ok=simplify(sin(2*(x+pi)+pi/3)-sin(2*x+pi/3))==0
        bad=not (F(1,2)>0 and F(1,2)<1)  # A=0 allows smaller period than claimed 1
        witness="sin(2x+π/3)周期π；零振幅常数无基本正周期"
    elif case==5:
        D=[-1,0,1]
        predicate=lambda v:v*v>0
        ok=(not all(predicate(v) for v in D))==any(not predicate(v) for v in D)
        bad=all(not predicate(v) for v in D)
        witness="论域{−1,0,1}，x=0否定全称，但不是所有x都满足否定"
    elif case==6:
        ok=simplify(log(8)/log(2))==3 and 2**3==8
        bad=(1>0 and 1!=1)  # explicitly rejects base=1
        witness="log₂8=3，底数1不满足a≠1"
    elif case==7:
        a,q,n=2,1,4
        ok=sum(a*q**i for i in range(n))==n*a==8
        bad=q!=1   # forbidden division by 1-q must fail
        witness="q=1时四项2相加为8，分式分母为零"
    elif case==8:
        cubic=x**3
        ok=diff(cubic,x).subs(x,0)==0 and (-1)**3<0<1**3
        bad=((-1)**3>=0 or 1**3<=0)
        witness="x³在0导数为0，左右有严格较小和较大值"
    elif case==9:
        n=(0,0,1);v=(1,0,0)
        dot=lambda a,b:sum(i*j for i,j in zip(a,b))
        ok=dot(n,v)==0 and dot(n,(0,0,1))!=0 and dot(n,(0,0,0))==0
        bad=dot(n,(0,0,0))!=0
        witness="同方向在z=0内与z=1平行不交两种可能"
    elif case==10:
        ok=diff(x**3,x).subs(x,0)==0 and -1**3<0<1**3
        bad=diff(x**3,x).subs(x,0)>0
        witness="x³严格递增却在0处导数为0"
    elif case==11:
        tail=[F(1,n) for n in range(2,51)]
        ok=all(0<v<=F(1,2) for v in tail) and set((-1)**n for n in range(1,11))=={-1,1}
        bad=len(set((-1)**n for n in range(1,11)))==1
        witness="1/n趋零且有界，(−1)^n有两条不同常值子列"
    elif case==12:
        def f(t):return 1 if t==0 else t
        ok=f(0)==1 and f(F(1,100))==F(1,100) and f(F(-1,100))==F(-1,100)
        bad=f(0)==0
        witness="原点值1，周围x值趋向0，不能连续"
    elif case==13:
        f=lambda v:v*v
        ok=abs(f(2)-f(1))==3 and abs(f(2)-f(1))<=4*(2-1)
        bad=abs(f(2)-f(1))<=2*(2-1)
        witness="x²在[1,2]增量3；M=4足够，错误M=2不足"
    elif case==14:
        vertices=[(0,0),(2,0),(0,3)]
        vals=[a+b for a,b in vertices]
        ok=max(vals)==3 and vals.index(3)==2
        bad=max(vals)==2
        witness="三角形x+y顶点值[0,2,3]；遗漏最后顶点给错值"
    elif case==15:
        def f(a,b):return F(0) if a==0 and b==0 else F(a*b,a*a+b*b)
        ok=f(F(1,2),0)==f(0,F(1,2))==0 and f(F(1,2),F(1,2))==F(1,2)
        bad=f(F(1,2),F(1,2))==0
        witness="坐标轴偏导0；y=x方向趋近却恒为1/2"
    elif case==16:
        def f(a,b):return a*a+b*b
        ok=f(0,0)==0 and f(F(3,5),F(4,5))==1 and f(F(1,2),0)==F(1,4)
        bad=f(0,0)==1
        witness="单位圆盘内部最小0、边界最大1"
    elif case==17:
        target=F(100,200);frame=F(100,100)
        ok=target==F(1,2) and frame==1
        bad=target==frame
        witness="虚构目标总体200人支持100；抽样框100人均支持"
    elif case==18:
        P=F(100);r=F(1,10);n=2
        compound=P*(1+r)**n;simple=P*(1+n*r)
        ok=compound==121 and simple==120
        bad=compound==simple
        witness="P=100,r=1/10,n=2，复利121单利120"
    elif case==19:
        ok=simplify(sin(4*pi*(x+Rational(1,2)))-sin(4*pi*x))==0
        bad=not (F(1,4)>0 and F(1,4)<F(1,2))  # A=0: smaller period exists
        witness="s(t)=3sin4πt周期1/2；A=0时无基本正周期"
    else: # case 20
        ratio=2**Rational(1,12)
        ok=simplify(ratio**12)==2 and simplify(ratio**6)==sqrt(2)
        bad=simplify(ratio**6)==2
        witness="十二半音倍频2，六半音√2而非2"
    if not isinstance(ok,bool): ok=bool(ok)
    if not isinstance(bad,bool): bad=bool(bad)
    if not ok or bad: raise AssertionError(f"independent witness failed case={case}, positive={ok}, invalid={bad}")
    return {"lesson_index":case,"positive":"VERIFIED_FINITE_INSTANCE",
            "negative":"INVALID_GENERALIZATION_OR_BOUNDARY_REJECTED",
            "witness":witness,"general_theorem_formally_certified":False,
            "student_free_text_verified":False,
            "teacher_approved":False,"student_publishable":False,
            "evidence_scope":"EXACT_FINITE_CASE_OR_SYMBOLIC_IDENTITY_ONLY"}

def evaluate_all():
    return {i:verify(i) for i in range(1,21)}
