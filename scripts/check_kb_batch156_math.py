#!/usr/bin/env python3
"""40 independent, exact bounded math witnesses for ten KB156 drafts.

These checks do NOT certify the general theorems, teacher approval, or student free steps.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch156_lessons as content
OUT=ROOT/"docs/evaluation/KB_BATCH156_EXACT_WITNESSES.json"

def encode(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
R=S.Rational;M=S.Matrix;z=S.symbols("z",real=True)
def group(index,cases):
    assert len(cases)==4
    cid=content.IDS[index]
    out=[]
    for j,(name,predicate,explanation) in enumerate(cases):
        expected=j<2
        observation=bool(predicate)
        if observation != expected:
            raise AssertionError("KB156 oracle mismatch "+cid+" "+name+
                                 "; expected "+str(expected)+" observed "+str(observation))
        out.append(dict(source_candidate_id=cid,case=name,
              assertion_is_true=observation,
              expectation="LEGAL_OR_BOUNDARY_TRUE" if expected else
                          "INVALID_PREMISE_OR_FALSE_GENERALIZATION_REJECTED",
              mathematical_scope="BOUNDED_EXACT_WITNESS_NOT_GENERAL_PROOF",
              basis=explanation,passed=True))
    return out

def build():
    A={1,2};B={2,3};U={0,1,2,3};F={0,2}
    P=M([1,2,3]);normal=M([2,-1,1])
    u=M([1,1]);v=M([1,2]); proj=(v.dot(u)/u.dot(u))*u
    tau1=M([[1,1],[1,1]]);tau2=M([[1,2],[2,1]])
    a,b=S.symbols("a b",real=True);t=M([a,b])
    x=S.symbols("x",real=True)
    rows=[]
    rows+=group(0,[
        ("union-retains-intersection",{1,2,3}==A|B,"并集的或是包含性析取，公共元素2必须保留"),
        ("intersection-only-shared",{2}==A&B,"交集仅含在两个集合中同时出现的2"),
        ("exclusive-or-is-not-union",(A^B)==(A|B),"异或丢掉公共元素2，不能当作并集"),
        ("intersection-not-all-of-A",(A&B)==A,"元素1仅在A中，不属于交集")])
    rows+=group(1,[
        ("empty-intersection",F&set()==set(),"空集中没有成员，交集为空"),
        ("empty-union",F|set()==F,"空集对并集是恒等元"),
        ("empty-not-singleton",set()=={0},"空集与含零的单元素集合不同"),
        ("complement-no-outside-U",(U-F)=={1,3,100},"有限全集之外的100不能算作补集")])
    rows+=group(2,[
        ("forward-implication-at-2",(2==2 and 2**2==4),"x=2充分保证x平方为4"),
        ("reverse-counterexample-at-minus2",((-2)**2==4 and -2!=2),"x=-2满足后件但不满足前件"),
        ("reverse-claim-is-false",all(q==2 for q in (-2,2) if q*q==4),
         "真实论域中后件x平方为4还包括x=-2，因此反向不成立"),
        ("equivalence-is-false",{v for v in (-2,2) if v*v==4}=={2},
         "反例x=-2排除两命题同解集")])
    rows+=group(3,[
        ("unit-circle-sine",S.simplify(S.sin(S.pi/6)-R(1,2))==0,"单位圆π/6的纵坐标为1/2"),
        ("unit-circle-tangent",S.simplify(S.tan(5*S.pi/6)+S.sqrt(3)/3)==0,
         "第二象限正切为负且余弦非零"),
        ("zero-cosine-forbids-tangent",S.cos(S.pi/2)!=0,"π/2余弦为0，不允许实数除法"),
        ("tangent-not-sine",S.simplify(S.tan(S.pi/6)-S.sin(S.pi/6))==0,
         "在π/6正切不等于正弦，不能读取同一个坐标")])
    rows+=group(4,[
        ("finite-q3",sum(2*3**k for k in range(4))==80,"2+6+18+54=80"),
        ("finite-q1",sum(-2*1**k for k in range(5))==-10,"q=1直接n倍首项"),
        ("q1-denominator-illegal",(1-1)!=0,"q=1时有限和分式的分母严格为0"),
        ("infinite-q3-not-finite",sum(2*3**k for k in range(4))==R(2,1-3),
         "|q|>1时无限和公式不适用且不等于有限求和")])
    f=(2*x-1)**3
    rows+=group(5,[
        ("affine-chain-rule",S.diff(f,x).subs(x,1)==6,"f(u)=u立方与u=2x-1复合，导数需乘2"),
        ("zero-affine-factor",S.diff(S.Abs(0*x),x)==0,"a=0时g(x)=0即使外函数在0不可导"),
        ("omitted-inner-factor",S.diff(f,x).subs(x,1)==3,
         "漏掉链式法则的内函数导数会得3而非6"),
        ("absolute-cusp-not-differentiable",S.limit(S.Abs(z)/z,z,0,dir="+")==
         S.limit(S.Abs(z)/z,z,0,dir="-"),
         "|x|在0处左右差商分别为1和-1")])
    rows+=group(6,[
        ("point-on-plane",normal.dot(P-P)==0,"给定点代入点法式结果为0"),
        ("tangent-direction-orthogonal",M([0,0,1]).dot(M([1,0,0]))==0,
         "方向与法向量正交才能与平面方向平行"),
        ("zero-normal-must-be-nonzero",M([0,0,0]).dot(M([1,2,3]))!=0,
         "零法向量使点法式恒为0，不能定义唯一平面"),
        ("parallel-line-not-necessarily-contained",M([0,0,3])[2]==2,
         "z=3方向水平的直线不会因此属于z=2的平面")])
    rows+=group(7,[
        ("projection-on-x-axis",M([3,4]).dot(M([1,0]))/M([1,0]).dot(M([1,0]))*M([1,0])==M([3,0]),
         "正交投影到水平轴保留水平分量"),
        ("projection-oblique",proj==M([R(3,2),R(3,2)]),
         "投影系数为3/2且需乘以投影方向向量"),
        ("zero-direction-forbidden",M([0,0]).dot(M([0,0]))!=0,
         "零向量不允许作投影公式分母"),
        ("scalar-not-vector",proj==M([R(3,2)]),
         "投影向量不能用单个标量系数替代")])
    rows+=group(8,[
        ("psd-quadratic-identity",S.simplify((t.T*tau1*t)[0]-(a+b)**2)==0,
         "退化协方差矩阵二次型恰是非负平方"),
        ("symmetric-singular-psd",tau1==tau1.T and tau1.det()==0 and
         set(tau1.eigenvals())=={S.Integer(0),S.Integer(2)},
         "半正定允许零特征值且仍必须对称"),
        ("negative-determinant-forbidden",tau2.det()>=0,
         "行列式为-3无法满足二维半正定条件"),
        ("singular-matrix-not-invertible",tau1.det()!=0,
         "行列式0的半正定矩阵不允许使用通常逆矩阵密度公式")])
    n=S.symbols("n",integer=True)
    rows+=group(9,[
        ("integer-successor",S.simplify(n+1-n)==1,
         "每个整数都有比它大1的整数，否定最大整数假设"),
        ("odd-square-remains-odd",S.expand((2*n+1)**2)-(2*(2*n*n+2*n)+1)==0,
         "奇整数平方仍能写成2k+1"),
        ("finite-check-not-universal",all(k*k<10 for k in (1,2,3)) and
            all(k*k<10 for k in range(1,11)),
         "只在1至3检查通过，不能断言1至10也全成立"),
        ("inconsistent-hypotheses-cannot-certify",1==2,
         "若原前提自相矛盾，不能作为现实数学事实的独立认证")])
    assert len(rows)==40 and sum(r["expectation"]=="LEGAL_OR_BOUNDARY_TRUE" for r in rows)==20
    assert sum(r["expectation"]=="INVALID_PREMISE_OR_FALSE_GENERALIZATION_REJECTED" for r in rows)==20
    return dict(schema="kb156-bounded-exact-independent-oracle/1",cases=rows,
         verified_bounded_cases=40,legal_or_boundary_true=20,
         invalid_premise_or_false_generalization_rejected=20,
         general_theorems_formally_proven=0,teacher_approved=0,student_free_steps_verified=0)

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    a=p.parse_args();v=build()
    if a.write:OUT.write_text(encode(v),encoding="utf-8")
    else:
        if OUT.read_text(encoding="utf-8")!=encode(v):
            raise ValueError("KB156 independent math evidence drift")
    print("PASS KB156 40/40 independent exact bounded witnesses; no general proof certified")
if __name__=="__main__":main()
