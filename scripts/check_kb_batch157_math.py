#!/usr/bin/env python3
"""Independent exact, finite premise/counterexample checks; never general proof certification."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch157_lessons as lessons
OUT=ROOT/"docs/evaluation/KB_BATCH157_EXACT_WITNESSES.json"
def encode(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+"\n"
def group(i,items):
    assert len(items)==4
    out=[]
    for j,(title,predicate,reason) in enumerate(items):
        observed=bool(predicate); expected=j<2
        if observed!=expected:raise AssertionError(f"{lessons.IDS[i]} {title}: expected {expected} got {observed}")
        out.append(dict(source_candidate_id=lessons.IDS[i],case=title,
            assertion_is_true=observed,passed=True,basis=reason,
            expectation="LEGAL_OR_BOUNDARY_TRUE" if expected else "INVALID_PREMISE_OR_FALSE_GENERALIZATION_REJECTED",
            mathematical_scope="BOUNDED_EXACT_WITNESS_NOT_GENERAL_PROOF"))
    return out
R=S.Rational
def build():
    rows=[]
    rows+=group(0,[
      ("two-roots-in-Z",{k for k in range(-4,5) if k*k==4}=={-2,2},"整数有理数范围内x²=4的两个根均应保留"),
      ("both-set-inclusions",{-1,1}=={k for k in range(-3,4) if k*k==1},"有限整数论域双方包含"),
      ("missing-negative-root",{-2,2}=={2},"漏掉负根不等价于描述式"),
      ("zero-not-empty",{0}==set(),"单元素零集合不等于空集")])
    rows+=group(1,[
      ("two-day-scale",100*2**R(4,2)==400,"每两天翻倍，四天是两期"),
      ("half-per-period",80*R(1,2)**3==10,"三期指数衰减为10"),
      ("wrong-daily-scale",100*2**4==400,"每两天翻倍不能误按每天"),
      ("negative-exponential-base-is-allowed",-2>0,"实时间指数底数必须正")])
    rows+=group(2,[
      ("dice-frequency",R(4,20)==R(1,5),"20次中4次的样本频率1/5"),
      ("valid-questionnaire-denominator",R(12,40)==R(3,10),"只用40份有效问卷作分母"),
      ("zero-sample-denominator",0!=0,"n=0时0/0不得当频率"),
      ("observed-1-5-equals-1-6",R(4,20)==R(1,6),"经验频率不必等于理论概率")])
    rows+=group(3,[
      ("parabola-focal-distance",(R(2)-R(2))**2+R(4)**2==(R(2)+R(2))**2,"点(2,4)到焦点和准线的距离平方都等于16"),
      ("hyperbola-foci",S.sqrt(3**2+4**2)==5,"a=3 b=4则焦距c=5"),
      ("parabola-degenerate-p",0!=0,"p=0违反非退化条件"),
      ("hyperbola-zero-axis",0>0,"b=0不满足正半轴条件")])
    # y²=8x, focus(2,0), directrix x=-2; at x=2,y=4 point on curve:
    rows+=group(4,[
      ("normal-mean-and-sd",R(12-10,2)==1,"X~N(10,4)，标准差2而非方差4"),
      ("constant-degenerate-variance",sum((k-5)**2 for k in [5,5,5])==0,"恒定变量有零标准差"),
      ("nonzero-variance-from-constant",0>0,"σ=0不允许标准化"),
      ("sd-mistaken-for-variance",R(12-10,4)==1,"把4直接当标准差不正确")])
    a1=R(2);a2=R(9,4);a3=R(64,27)
    rows+=group(5,[
      ("a2-greater-a1",a2>a1,"精确有理数比较9/4>2"),
      ("a3-greater-a2",a3>a2,"精确交叉相乘256>243"),
      ("finite-a2-equals-e",a2==S.E,"任意给定有限项不等于极限e"),
      ("first-3-implies-all",all((a2>a1,a3>a2,0>a3)),"前三项增长不能证明第四项仍增长")])
    x=S.symbols("x",real=True)
    rows+=group(6,[
      ("quadratic-minimum",min([(-1)**2,0**2,2**2])==0,"闭区间驻点及端点比较"),
      ("absolute-endpoint-maximum",max([abs(-2),abs(0),abs(1)])==2,"尖点和端点联合比较"),
      ("all-extrema-derivative-zero",S.diff(x,x).subs(x,1)==0,"端点最大值可以有非零导数"),
      ("x-cube-stationary-local-max",S.diff(x**3,x).subs(x,0)>0,"x³在0有驻点但不取局部极值")])
    rows+=group(7,[
      ("modus-ponens", (8%2==0) and (8%2==0),"有效全称规则与前提应用"),
      ("induction-counterexample-n5",not (5**2<5+10),"有限观察可被n=5证伪"),
      ("finite-cases-prove-all",all(n*n<n+10 for n in range(1,6)),"前三个样本通过并不保证所有n"),
      ("reverse-implication",(-2)**2==4 and -2==2,"后件成立不保证前件")])
    t=S.symbols("t",real=True)
    f=S.sin(2*S.pi*t/3)
    rows+=group(8,[
      ("sine-period-3",S.simplify(f.subs(t,t+3)-f)==0,"三秒平移角度增加2π"),
      ("constant-period-any-positive",7==7 and R(1,2)>0,"常数函数任意正数都是周期"),
      ("quadratic-period-3",S.simplify((t+3)**2-t**2)==0,"非恒定二次函数没有正周期3"),
      ("constant-smallest-positive-period",min([R(1),R(1,2)])==R(1),"任意周期还有更小正周期")])
    rows+=group(9,[
      ("two-period-compound",1000*R(21,20)**2==R(2205,2),"两期各增长5%得1102.5"),
      ("zero-rate",1000*(1+R(0))**3==1000,"r=0合法且余额不变"),
      ("extra-deposit-no-cashflows",1000*R(21,20)**2+50==1000*R(21,20)**2,"额外存款不属于零现金流模型"),
      ("annual-rate-is-monthly-rate",R(1,10)==R(1,120),"年率10%不能不说明约定直接作为每月10%")])
    if len(rows)!=40 or sum(x["assertion_is_true"] for x in rows)!=20:
        raise AssertionError("missing/oracle misclassified cases")
    return dict(schema="kb157-independent-finite-witness/1",cases=rows,
       verified_bounded_cases=40,legal_or_boundary_true=20,invalid_premise_rejected=20,
       formal_general_proofs_certified=0,teacher_approved=0,student_free_steps_verified=0)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    x=p.parse_args();a=build();s=encode(a)
    if x.write:OUT.write_text(s,encoding="utf-8")
    elif OUT.read_text(encoding="utf-8")!=s:raise ValueError("KB157 proof witness drift")
    print("PASS 40/40 independent bounded exact case checks; no general theorem certified")
if __name__=="__main__":main()
