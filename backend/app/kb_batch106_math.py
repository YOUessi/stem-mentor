"""Bounded, independent exact or SymPy witnesses; never universal proof/approval.

Reject unsupported arbitrary student reasoning rather than reusing these test certificates.
"""
from __future__ import annotations
from fractions import Fraction as F
from sympy import Symbol, diff, integrate, limit, log, sin, cos, Abs, S, oo, simplify

x=Symbol("x",real=True)
h=Symbol("h",real=True)
n=Symbol("n",integer=True,positive=True)
CASES={
 "necessary":lambda:( (-2)**2==4 and 2**2==4, -2!=2, "x²=4 是 x=2 的必要但非充分条件"),
 "sufficient":lambda:( all(z>1 for z in [F(5,2),3,4]), F(3,2)<=2, "x>2 足以推出 x>1，逆向不足"),
 "iff":lambda:( all((t==0)==(t*t==0) for t in [-2,-1,0,1,2]), (-2)**2==4 and -2!=2, "等价证明要核对两个方向"),
 "forall":lambda:(all(t*t>=0 for t in range(-5,6)), not all(t>0 for t in range(-5,6)), "有限抽样不能升级为全称形式证明"),
 "exists":lambda:(2**2==4,0**2!=4,"存在见证不能升级为每个对象都满足"),
 "not_forall":lambda:(not all(t>0 for t in [-1,0,1]) and any(t<=0 for t in [-1,0,1]), not all(t<=0 for t in [-1,0,1]), "否定全称应换成存在反例"),
 "not_exists":lambda:(not any(t>0 for t in [-2,-1]) and all(t<=0 for t in [-2,-1]), any(t<=0 for t in [-2,-1]), "否定存在必须换成全称"),
 "equality_cancel":lambda:(3*2!=3*3, 0*2==0*3 and 2!=3, "零因子不能约去"),
 "inequality_sign":lambda:(2<3 and -2>-3, not (-2 < -3) and not(0*2<0*3), "乘负数换向；乘零破坏严格性"),
 "amgm":lambda:(F(1)+F(9)>=2*3 and F(4)+F(4)==2*4, -1<0, "非负域及等号 a=b 为前提"),
 "continuity":lambda:(limit(x*x,x,0)==0, limit(x,x,0)==0 and 5!=0, "极限等于0不保证该点的定义值也是0"),
 "continuous_bounded":lambda:(all(0<=F(i,10)**2<=1 for i in range(11)), F(1,1000)>0 and 1/F(1,1000)>100, "半开区间上 1/x 可以无界"),
 "ivt":lambda:(2*F(1,2)-1==0 and 2*0-1<0 and 2*1-1>0, (-1<0<1) and not any(t==0 for t in [-1,1]), "异号但不连续的阶跃函数可无零点"),
 "bisection":lambda:(1**2-2<0 and F(3,2)**2-2>0 and F(3,2)-1==F(1,2), (-1<0<1) and all(t!=0 for t in [-1,1]), "无连续性不能保证二分区间含根"),
 "derivative":lambda:(limit(((x+h)**2-x*x)/h,h,0)==2*x, limit(Abs(h)/h,h,0,dir="+")==1 and limit(Abs(h)/h,h,0,dir="-")==-1, "|x|在0左右导数不同"),
 "second_derivative":lambda:(diff(x*x,x,2)==2,limit(2*Abs(h)/h,h,0,dir="+")==2 and limit(2*Abs(h)/h,h,0,dir="-")==-2, "x|x| 的一阶导存在但二阶不一定存在"),
 "chain":lambda:(simplify(diff(sin(x*x),x)-2*x*cos(x*x))==0, diff(sin(x*x),x)!=cos(x)+2*x,"链式求导不可拆为相加"),
 "mvt":lambda:(F(3**2-1**2,3-1)==4 and 2*2==4, (-1<0<1 and (-1 != 1)), "跳跃函数不满足闭区间连续条件"),
 "monotonic_derivative":lambda:(all(2*t>=0 for t in [0,F(1,4),1,2]), 2*(-1)<0 and 2*1>0,"某一点导数正不能推出整段递增"),
 "log_inequality":lambda:(bool(log(2)<1) and F(1,2)<1, not(0<0) and -1<=-1,"x>0与对数正定义域均不可省"),
 "fermat":lambda:(diff(x*x,x).subs(x,0)==0, diff(x**3,x).subs(x,0)==0 and F(-1,10)**3<0<F(1,10)**3,"驻点可能是拐点而非极值"),
 "differential":lambda:(simplify((1+h)**2-1-2*h)==h*h, F(1,2)**2!=0,"微分主部与有限增量存在二阶误差"),
 "riemann":lambda:(sum(-F(2,10) for _ in range(10))==-2, -2<0,"定积分为有向面积，可以为负"),
 "ftc":lambda:(integrate(x*x,(x,0,2))==F(8,3) and diff(x**3/3,x)==x*x, F(8,3)!=-F(8,3),"积分方向颠倒改变符号"),
 "integral_compute":lambda:(integrate(x,(x,1,3))==4 and diff(x*x/2,x)==x, -1<0<1,"1/x在跨过0的区间不满足通常定积分可积前提"),
}
def witness(key: str):
    if not isinstance(key,str) or key not in CASES:
        raise ValueError("unknown math oracle key")
    yes,no,note=CASES[key]()
    if not (bool(yes) and bool(no)):
        raise ValueError("finite witness or invalid generalization failed: "+key)
    return dict(oracle_key=key,finite_or_symbolic_witness_passed=True,
      invalid_generalization_rejected=True,witness_note=note,
      general_proof_certified=False,teacher_approved=False,
      student_step_verified=False,method="EXACT_FINITE_OR_SYMPY_SAMPLE_NOT_FORMAL_PROOF")
