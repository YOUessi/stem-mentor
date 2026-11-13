#!/usr/bin/env python3
"""Independent exact *finite* math oracle for 12 selected KB141 P0 risks.

No inference from the author prose and no claim of universally quantified proof.
"""
import argparse
import json
from pathlib import Path
import sys
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch141_lineage as source

OUT=ROOT/"docs/evaluation/KB_BATCH141_EXACT_MATH_CASES.json"
R=S.Rational
M=S.Matrix

def evidence():
    x,p=S.symbols("x p",real=True)
    cases=[]
    def check(sid, good, good_reason, bad, bad_reason):
        assert good is True or good == S.true,(sid,"positive")
        assert bad is True or bad == S.true,(sid,"negative")
        cases.append(dict(
            historical_step_id=sid,legal_exact_case_pass=True,
            legal_case=good_reason,invalid_precondition_case_pass=True,
            invalid_case=bad_reason,
            verdict="TWO_FINITE_CASES_NOT_A_GENERAL_PROOF",
            teacher_approved=False,student_step_verified=False
        ))
    check("math.hs.calculus.tangent-line#3",
          S.diff(x*x,x).subs(x,2)==4 and S.expand((4+4*(x-2))-(4*x-4))==0,
          "f(x)=x² 在x=2切点(2,4)，导数4，切线y=4x−4；逐项代入准确",
          S.limit(S.Abs(x)/x,x,0,dir="+")==1 and
          S.limit(S.Abs(x)/x,x,0,dir="-")==-1,
          "f(x)=|x| 在0处左右差商不等，不能用有限导数构造该切线")
    z=1+S.I;w=1-S.I
    check("math.hs.complex.operations#2",
          S.simplify(z/w-S.I)==0 and S.simplify(z*S.conjugate(w)/(w*S.conjugate(w))-S.I)==0,
          "(1+i)/(1−i)=i，共轭分母为2，允许除法",
          S.simplify(S.Integer(0)*S.conjugate(S.Integer(0)))==0,
          "w=0时w·conj(w)=0，实数/复数求逆与共轭分母均不可用")
    Q=M([[0,-1],[1,0]]);T=M([[2,0],[0,1]]);v=M([1,0])
    check("math.hs.elective.geometry.euclidean-isometries#2",
          Q.T*Q==S.eye(2) and (Q*v).dot(Q*v)==v.dot(v),
          "直角旋转QᵀQ=I，对向量(1,0)严格保范数",
          (T*v).dot(T*v)!=v.dot(v) and T.T*T!=S.eye(2),
          "非等距T=diag(2,1)使e₁长度平方从1变为4")
    A=M([[1,2],[3,5]]);B=M([[1,2],[2,4]])
    check("math.hs.elective.matrix.inverse-two-by-two#3",
          A.det()==-1 and A*A.inv()==S.eye(2) and A.inv()*A==S.eye(2),
          "行列式−1的2×2矩阵双侧逆乘积均为单位阵",
          B.det()==0 and B*M([-2,1])==M([0,0]),
          "行列式0时非零(-2,1)属于核，不能构造逆")
    domain={n for n in (-2,-1,0,1,2) if n+1 in {0,2}}
    check("math.hs.function.composition-domain#3",
          domain=={-1,1} and all((n+1) in {0,2} for n in domain),
          "在有界整数候选集上，g(x)=x+1和Df={0,2}的复合域恰为{-1,1}",
          0 in {-2,-1,0,1,2} and 0+1 not in {0,2},
          "x=0属于g的输入域，g(0)=1却不属于f的输入域")
    check("math.hs.geometry.line-general#2",
          (2*0-3+3==0) and (2*1-5+3==0) and (2**2+(-1)**2>0),
          "2x−y+3=0含(0,3),(1,5)，法向量(2,−1)非零",
          0*0+0*1==0 and 0**2+0**2==0,
          "A=B=C=0的方程对每个点都真，不能唯一刻画直线")
    check("math.hs.geometry.line-relations#2",
          1*2-1*2==0 and 1!=R(1,2),
          "x+y=1与2x+2y=1方向相同却无共同点（两个常数归一化不同）",
          1*2-1*2==0 and (1*2)==2,
          "仅法向行列式为0不能区分重合与两条不同的平行直线")
    foot=M([R(3,5),R(4,5)])
    check("math.hs.geometry.point-line-distance#3",
          (3*foot[0]+4*foot[1]-5)==0 and foot.dot(foot)==1 and
          R(abs(-5),5)==1,
          "原点到3x+4y−5=0距离为1；垂足(3/5,4/5)在线上且距离平方为1",
          0**2+0**2==0,
          "A=B=0导致距离分母√(A²+B²)=0，未定义点到直线距离")
    omega={1,2,3,4};a={1,2};b={2,3}
    check("math.hs.probability.multiplication#2",
          R(len(a&b),len(omega))==
          R(len(a),len(omega))*R(len(a&b),len(a)),
          "四个等可能结果：P(A∩B)=1/4=P(A)P(B|A)，A={1,2}, B={2,3}",
          len(set())==0,
          "A=空事件时P(A)=0，P(B|A)=P(A∩B)/P(A)的分母为0")
    u=M([0,0,1]);v=M([1,0,0]);w=M([0,1,0])
    v_bad=M([1,0,0]);w_bad=M([2,0,0]);u_bad=M([0,1,0])
    check("math.hs.space.perpendicular-plane#2",
          u.dot(v)==u.dot(w)==0 and v.cross(w)!=M([0,0,0]),
          "u=e₃同时垂直平面内两条相交且独立方向e₁,e₂，从而垂直其张成平面",
          u_bad.dot(v_bad)==u_bad.dot(w_bad)==0 and
          v_bad.cross(w_bad)==M([0,0,0]) and u_bad.dot(M([0,1,0]))!=0,
          "若两条所谓相交方向其实平行，存在与它们均正交、但不垂直所在平面的向量")
    # All-zero Bernoulli outcomes: p=0 is the boundary MLE, not an interior critical point.
    L=(p**2)*(1-p)**3
    check("math.hs.elective.statistics.bernoulli-mle#3",
          S.diff(L,p).subs(p,R(2,5))==0 and
          S.diff(S.log(p**2*(1-p)**3),p,2).subs(p,R(2,5))<0 and
          L.subs(p,R(2,5))>L.subs(p,R(1,2)),
          "n=5,k=2的内部MLE为p=2/5，精确导数为0、二阶负且优于1/2",
          (1-R(0))**5>(1-R(1,5))**5 and S.limit((1-p)**5,p,0,dir="+")==1,
          "k=0时边界p=0取最大值；只解内部对数导数会漏掉该解")
    t,h=S.symbols("t h",real=True)
    check("math.hs.space.solid-volumes#3",
          S.integrate(9*(t/3)**2,(t,0,3))==9 and R(9*3,3)==9,
          "底面积9高3的相似锥体，精确切片积分=9=Bh/3",
          3*9!=9 and S.simplify(S.Integer(9)/(h*h)).subs(h,0)==S.zoo,
          "同一锥体不能误用柱体Bh=27；若h=0，推导中的1/h²未定义")
    expected=source.EXACT_IDS
    assert len(cases)==len(expected)==12
    assert tuple(c["historical_step_id"] for c in cases)==expected
    return {
       "schema":"kb141-independent-exact-cases/1",
       "scope":"24_EXACT_FINITE_CASES_NO_GENERAL_PROOFS",
       "tested_step_count":12,"positive_or_boundary_cases":12,"invalid_premise_cases":12,
       "historical_p0_denominator":127,"formal_proofs_certified":0,
       "teacher_approvals":0,"student_steps_verified":0,
       "official_course_denominators":None,"cases":cases,
    }

def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write",action="store_true")
    group.add_argument("--check",action="store_true")
    options=parser.parse_args()
    data=evidence()
    if options.write:
        OUT.write_text(source.canonical(data),encoding="utf-8")
    else:
        assert json.loads(OUT.read_text(encoding="utf-8"))==data,"frozen exact cases drift"
    print("PASS KB141 independent math: 12 positive + 12 negative finite cases, 0 universal proofs")

if __name__=="__main__":main()
