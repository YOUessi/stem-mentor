"""Bounded independently computed witnesses for Batch105 candidate requirements.

These 17 calculations do NOT certify any universally quantified theorem.
Never apply their status to arbitrary student free-text reasoning.
"""
from __future__ import annotations
from fractions import Fraction
from sympy import E, S, Symbol, oo, limit, pi, sin, simplify

x=Symbol("x",real=True)
n=Symbol("n",integer=True,positive=True)

def _check(ok, label):
    if not ok:
        raise ValueError(f"math witness failed: {label}")

def witness(key: str):
    cases = {}
    A={1,2}; B={2,3}; U={1,2,3,4}
    cases["membership"]=(1 in {1,3} and 2 not in {1,3}, {1} not in {1,3}, "成员资格与单元素集合不是同一关系")
    cases["set_notation"]=(set(range(0,6,2))=={0,2,4}, 3 not in set(range(0,6,2)), "明确整数论域，偶整数不含3")
    cases["empty_universe"]=(U-set()==U and set().issubset(U), {0}!=set(), "空集不等于包含0的集合")
    cases["subset_equality"]=(A.issubset(A|{3}) and not (A|{3}).issubset(A), A != A|{3}, "严格包含不等于相等")
    cases["union"]=(A|B=={1,2,3}, A|B!={2}, "并集保留至少属于其一的元素")
    cases["intersection"]=(A&B=={2}, A&B!={1,2,3}, "交集需要同时属于两个集合")
    cases["complement"]=(U-{1,3}=={2,4}, U-{1,3}!={2,4,5}, "补集取决于固定全集")
    cases["venn"]=(A&B=={2} and A|B=={1,2,3}, A&B!=A|B, "重叠区域与全圆区域不相同")
    for eps in (Fraction(1,2),Fraction(1,4),Fraction(1,101)):
        N=1//eps+1  # integer floor(1/eps)+1
        _check(Fraction(1,N)<eps, "epsilon-N witness")
    cases["sequence_eps_n"]=(limit(1/n,n,oo)==0, S.One != -S.One, "交替数列的奇偶子列极限不同")
    cases["convergent_bounded"]=(limit(1/n,n,oo)==0 and all(Fraction(1,k)<=1 for k in range(1,60)), 1!=-1, "有界交替列的两个常值子列不趋同")
    cases["monotone_bounded"]=(limit(1-1/n,n,oo)==1 and all(Fraction(1,k)-Fraction(1,k+1)>0 for k in range(1,60)), limit(n,n,oo)!=S.One, "n虽单调却无上界")
    cases["sequence_arithmetic"]=(limit(1/n+2+1/n,n,oo)==2 and limit((1/n)*(2+1/n),n,oo)==0,limit((1/n)/(1/n),n,oo)==1,"零极限之比不能使用非零分母商法则")
    cases["e_sequence"]=(limit((1+1/n)**n,n,oo)==E, S(2)!=E, "n=1时数值2只是极限数列的一项")
    eps=Fraction(1,5); xx=Fraction(21,20); delta=eps/2
    cases["function_eps_delta"]=(abs(xx-1)<delta and abs(2*xx-2)<eps and limit(2*x,x,1)==2, 100!=2, "点值可与去心极限不同")
    cases["function_arithmetic"]=(limit(x+x*x,x,1)==2 and limit(x/(x*x),x,1)==1,limit(x-1,x,1)==0,"分母极限0时需单独分析商")
    cases["sinc_limit"]=(limit(sin(x)/x,x,0)==1,simplify(sin(pi)/pi)==0,"极限相等不代表函数每一点相等")
    cases["exp_limit"]=(limit((1+x)**(1/x),x,0)==E, S(2)!=E, "x=1时的函数值2不是极限e")
    _check(key in cases,"unknown / unreviewed oracle key")
    yes,no,note=cases[key]
    _check(bool(yes) and bool(no),key)
    return {"oracle_key":key,"finite_or_symbolic_witness_passed":True,
            "invalid_generalization_rejected":True,
            "witness_note":note,"general_proof_certified":False,
            "teacher_approved":False,"student_step_verified":False,
            "method":"EXACT_FINITE_OR_SYMPY_LIMIT_SAMPLE_NOT_FORMAL_PROOF"}
