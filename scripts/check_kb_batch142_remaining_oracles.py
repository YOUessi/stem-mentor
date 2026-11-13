#!/usr/bin/env python3
"""Batch142 independent exact *finite* witnesses for all 35 KB141 P0 cards not in its oracle.

The oracle checks mathematical objects, rather than reading an LLM justification as truth.
A positive example and a counterexample / invalid-premise example are not universal
proofs, and no authority is granted to student free-form steps or teacher approval.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

import sympy as S

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "backend")]
import build_kb_batch141_lineage as previous

OUT = ROOT / "docs/evaluation/KB_BATCH142_REMAINING_EXACT_CASES.json"
R = S.Rational
M = S.Matrix


def oracle():
    prior = previous.build()
    remaining = {r["historical_proof_step_id"]: r for r in prior["records"]
                 if r["independent_exact_case_status"] == "NOT_IN_THIS_BATCH_ORACLE"}
    assert len(remaining) == 35
    cases = []

    def add(suffix, legal, invalid, legal_explanation, invalid_explanation):
        sid = suffix
        assert sid in remaining, "not a previously untested KB141 step: " + sid
        assert type(legal) in (bool, S.logic.boolalg.BooleanTrue), (sid, "legal type", type(legal))
        assert type(invalid) in (bool, S.logic.boolalg.BooleanTrue), (sid, "invalid type", type(invalid))
        assert legal is True or legal == S.true, (sid, "positive failed")
        assert invalid is True or invalid == S.true, (sid, "negative failed")
        assert len(legal_explanation) >= 18 and len(invalid_explanation) >= 18
        cases.append(dict(historical_step_id=sid,
                          historical_step_sha256=remaining[sid]["historical_step_sha256"],
                          legal_exact_case_pass=True,
                          invalid_precondition_case_pass=True,
                          legal_case=legal_explanation, invalid_case=invalid_explanation,
                          scope="TWO_EXACT_FINITE_WITNESSES_NOT_UNIVERSAL_PROOF",
                          teacher_approved=False, formal_proof_certified=False,
                          student_step_verified=False, student_publishable=False))

    u, v, h = S.symbols("u v h", real=True)
    # Complex division: second step, separate from KB141's previously checked earlier step.
    w = 2 + 3*S.I
    z = 1 - S.I
    add("math.hs.complex.operations#3",
        S.simplify(z/w-z*S.conjugate(w)/13)==0 and S.expand_complex(w*S.conjugate(w))==13,
        S.expand_complex(S.Integer(0)*S.conjugate(S.Integer(0)))==0,
        "w=2+3i满足|w|²=13>0；z/w与同乘共轭得到的z·conj(w)/13严格相同",
        "w=0时w·conj(w)=0，原分母与有理化后的分母均为零，绝不可约分")

    a = S.Integer(2)
    add("math.hs.elective.calculus.differentiable-continuous#1",
        S.expand((a+h)**2-a**2-h*(2*a+h))==0 and S.limit(h*(2*a+h),h,0)==0,
        S.limit(S.Abs(h)/h,h,0,dir="+") != S.limit(S.Abs(h)/h,h,0,dir="-"),
        "在a=2，f(x)=x²的函数值差严格等于h(4+h)，差商有极限4且函数值差趋零",
        "f(x)=|x|在a=0函数连续但左右差商分别为1和−1；不能由连续反推可导")

    add("math.hs.elective.calculus.second-derivative-convexity#3",
        S.diff(u*u,u,2)>0 and R(1) <= R(1,2)*(0**2+2**2),
        -1 > R(1,2)*(0+(-4)),
        "f(x)=x²的f′在实轴严格递增，x=0,z=1,y=2时1≤(0+4)/2",
        "f(x)=−x²在同样三个点中f(1)=−1>−2，f′递减时弦线凸性不等式失败")

    i=R(1,10); n=3; q=1/(1+i)
    annuity = S.Add(*[q**k for k in range(1,n+1)])
    add("math.hs.elective.finance.annuity-present-value#3",
        S.simplify(annuity - (1-(1+i)**(-n))/i)==0,
        S.limit((1-(1+u)**(-n))/u,u,0)==n,
        "三期期末支付的每期利率1/10，三项精确贴现和等于[1−(1+i)^−3]/i",
        "i=0时分式分母为零，必须切换到三项各为1、总额3的无息分支")

    aa=R(2); eps=R(1,2); delta=min(R(1),eps/(1+2*abs(aa)))
    xx=aa+delta/2
    add("math.hs.elective.function.epsilon-delta-square#2",
        delta>0 and abs(xx-aa)<delta and abs(xx**2-aa**2)<eps,
        abs((aa+R(1,2))**2-aa**2)>eps and R(1,2)<1,
        "a=2、ε=1/2，取δ=1/10，x=41/20时0<|x−a|<δ且|x²−a²|<ε",
        "若粗心固定δ=1，x=5/2满足|x−2|<1却有|x²−4|=9/4>1/2")

    Q=M([[0,-1],[1,0]]); T=M([[2,0],[0,1]])
    p=M([1,0]); r=M([1,1])
    dotcos=lambda x,y: S.simplify(x.dot(y)/(S.sqrt(x.dot(x))*S.sqrt(y.dot(y))))
    add("math.hs.elective.geometry.euclidean-isometries#3",
        Q.T*Q==S.eye(2) and S.simplify(dotcos(Q*p,Q*r)-dotcos(p,r))==0,
        S.simplify(dotcos(T*p,T*r)-dotcos(p,r))!=0,
        "直角旋转Q满足QᵀQ=I；非零向量(1,0),(1,1)变换前后余弦同为1/√2",
        "T=diag(2,1)非等距，原余弦1/√2，变换后的余弦2/√5，角度不保持")

    add("math.hs.elective.matrix.gaussian-row-equivalence#2",
        3*(2*0+3*2-6)==0 and (2*1+3*0-6)!=0 and 3*(2*1+3*0-6)!=0,
        0*(2*1+3*0-6)==0 and (2*1+3*0-6)!=0,
        "对2x+3y=6整行乘3，(0,2)仍是解、(1,0)仍不是解，非零倍可逆",
        "错误地把整行乘0后，原方程非解(1,0)也满足0=0，解集被扩大")

    b=R(1,4); d2=3; x2=d2/(1-b)
    add("math.hs.elective.model.input-output-triangular#2",
        x2==4 and S.simplify((1-b)*x2-d2)==0 and x2>=0,
        1-R(1)==0 and d2>0,
        "三角形投入产出式b=1/4、d₂=3时x₂=4≥0并严格满足(1−b)x₂=d₂",
        "若b=1、d₂=3，则方程变为0·x₂=3根本无解，不能除以1−b")

    f=lambda t: 3*t*t+2*t+1
    add("math.hs.elective.model.time-rescaling#4",
        S.expand(f(2*u)-(12*u*u+4*u+1))==0 and S.solve(S.Eq(2*u,6),u)==[3],
        S.simplify(f(0*u)-1)==0 and S.solve(S.Eq(0*u,1),u)==[],
        "a=3、b=2、s=2时f(2u)=12u²+4u+1且u=t/2可唯一反求",
        "s=0时t=0对所有u相同，t=1无对应u；代数代入仍成立但非可逆变量替换")

    x,y=S.symbols("x y",real=True); poly=x*x*y+3*y*y
    add("math.hs.elective.multivariable.partial-polynomial#3",
        S.simplify((poly.subs(y,y+h)-poly)/h-(x*x+6*y+3*h))==0 and
        S.limit((poly.subs(y,y+h)-poly)/h,h,0)==x*x+6*y,
        S.diff(poly,x)!=S.diff(poly,y),
        "固定x，对y增量h≠0，精确差商=x²+6y+3h，极限为x²+6y",
        "若错误地把固定x改成对x求偏导，则得到2xy而非x²+6y，变量保持条件不可漏")

    phi=(1+S.sqrt(5))/2; psi=(1-S.sqrt(5))/2; k=4
    Fibonacci=lambda t: S.simplify((phi**t-psi**t)/S.sqrt(5))
    ratio=S.simplify(phi*(1-(psi/phi)**(k+1))/(1-(psi/phi)**k))
    add("math.hs.elective.sequence.fibonacci-golden-ratio#3",
        Fibonacci(k)==3 and Fibonacci(k+1)==5 and S.simplify(ratio-R(5,3))==0,
        Fibonacci(0)==0 and S.simplify(1-(psi/phi)**0)==0,
        "F₀=0、F₁=1的第4、5项为3、5，Binet比值表达式在n=4严格给出5/3",
        "若擅自取n=0，则F₀=0且公式分母1−(ψ/φ)^0=0，不能取F₁/F₀")

    p=S.symbols("p",positive=True); L=p**2*(1-p)**3
    add("math.hs.elective.statistics.bernoulli-mle#2",
        S.diff(S.log(L),p).subs(p,R(2,5))==0 and
        S.diff(S.log(L),p,2).subs(p,R(2,5))<0,
        S.diff(S.log((1-p)**5),p).subs(p,R(1,2))<0 and
        (1-R(0))**5>(1-R(1,2))**5,
        "n=5,k=2时p=2/5是开区间内对数似然的严格局部极大点",
        "k=0时log L的内部导数严格为负，真实最大值在边界p=0，不能硬套内部零点条件")

    RADIUS=5; circle_pt=M([3,4])
    add("math.hs.extension.circle-polar#1",
        circle_pt.dot(circle_pt)==RADIUS**2 and circle_pt.dot(M([3,4]))==RADIUS**2,
        M([0,0]).dot(M([0,0]))!=RADIUS**2,
        "半径5圆上T=(3,4)满足|T|²=25；以T为法向量的切线为3x+4y=25",
        "若错误取T=(0,0)，该点不在半径5圆上且所谓法向量为零，无法定义切线")

    polar_pt=M([10,0]); inner_pt=M([2,0])
    add("math.hs.extension.circle-polar#3",
        R(25,10)<5 and 2**2+0**2<5**2 and S.simplify(R(25)-10*R(5,2))==0,
        R(25,2)>5 and R(25,2)**2>RADIUS**2,
        "极点P=(10,0)、R=5的极线x=5/2，距离2.5<5，和圆有两交点",
        "极点P=(2,0)位于圆内时极线x=25/2，距原点12.5>5，不与圆相交")

    cr_u=M([1,2,3]); cr_v=M([2,-1,1])
    add("math.hs.extension.cross-product#3",
        S.simplify(cr_u.cross(cr_v).dot(cr_u.cross(cr_v)) -
                   (cr_u.dot(cr_u)*cr_v.dot(cr_v)-cr_u.dot(cr_v)**2))==0,
        M([0,0,0]).dot(M([0,0,0]))==0,
        "u=(1,2,3),v=(2,−1,1)，外积模平方与Gram行列式用整数精确一致",
        "当u=0时恒等式仍成立但|u||v|=0，不能用除法定义夹角余弦或正弦")

    add("math.hs.geometry.line-circle#3",
        RADIUS**2-5**2==0 and RADIUS**2-6**2<0,
        (0**2+(6**2)!=RADIUS**2) and (RADIUS**2-6**2<0),
        "半径5圆与y=5相切仅有(0,5)一交点，方程x²=0只有一个实解",
        "同一圆与y=6满足x²=25−36=−11，无实交点，不能误判成相切")

    nvec=M([2,3]); base=M([1,-1]); point=M([4,-3])
    add("math.hs.geometry.line-equation#2",
        nvec!=M([0,0]) and nvec.dot(point-base)==0 and
        2*(4-1)+3*(-3+1)==0,
        M([0,0]).dot(M([7,9])-base)==0,
        "法向(2,3)非零，P₀=(1,−1)，P=(4,−3)位移(3,−2)点积为零",
        "若法向(0,0)，对任意P均有零点积，方程0=0不能表示唯一直线")

    add("math.hs.geometry.line-equation#3",
        nvec.dot(point-base)==0 and nvec.dot(M([1,-1])-base)==0,
        M([0,0]).dot(M([100,200])-base)==0,
        "满足2(x−1)+3(y+1)=0的点(4,−3)与P₀确在同一法向为(2,3)的直线上",
        "如果法向量为零，任意点(100,200)都满足方程，逆向不能声称唯一确定一条线")

    n2=M([1,-2]); p0=M([3,4]); p1=M([5,5])
    add("math.hs.geometry.line-general#1",
        n2.dot(p1-p0)==0 and n2!=M([0,0]),
        n2.dot(M([5,4])-p0)!=0,
        "法向n=(1,−2)与直线上位移(2,1)的点积为0，确属对应直线",
        "点(5,4)相对P₀=(3,4)位移(2,0)不与n正交，不能直接当作线上点")

    add("math.hs.geometry.line-general#3",
        M([3,4]).dot(M([4,-3]))==0 and M([3,4])!=M([0,0]),
        M([0,0]).dot(M([100,-100]))==0,
        "法向(3,4)的齐次方程3x+4y=0有非零线上向量(4,−3)，解集是一维子空间",
        "法向(0,0)得到所有平面点的解集，不再是一维直线，也不能谈法向唯一")

    direction=M([-3,2]); normal=M([2,3])
    add("math.hs.geometry.line-relations#1",
        normal.dot(direction)==0 and direction!=M([0,0]),
        M([0,0]).dot(M([0,0]))==0,
        "对非零法向(2,3)，方向(−3,2)非零且点积严格为零",
        "若所谓法向(0,0)，给出的方向(0,0)亦为零向量，不是直线方向")

    d1=M([0,1]); d2=M([-1,0])
    add("math.hs.geometry.line-relations#3",
        d1.dot(d2)==0 and d1!=M([0,0]) and d2!=M([0,0]),
        M([0,1]).dot(M([0,2]))!=0,
        "x=0与y=0方向分别为(0,1),(−1,0)，严格正交",
        "x=0与x=1的方向分别(0,1),(0,2)，点积为2，不是垂直线")

    uu=M([1,2,3]); vv=M([3,0,1])
    add("math.hs.geometry.space-dot#1",
        (uu-vv).dot(uu-vv)==uu.dot(uu)+vv.dot(vv)-2*uu.dot(vv),
        uu.dot(vv)!=0 and (uu-vv).dot(uu-vv)!=uu.dot(uu)+vv.dot(vv),
        "同一三维正交坐标下u=(1,2,3),v=(3,0,1)，范数展开保留−2u·v项严格正确",
        "当u·v≠0，删去交叉项会得错误的勾股式，不能冒称任何两向量都垂直")

    uu=M([1,0,0]); vv=M([1,1,0])
    add("math.hs.geometry.space-dot#2",
        S.simplify((uu-vv).dot(uu-vv) -
                   (uu.dot(uu)+vv.dot(vv)-2*S.sqrt(uu.dot(uu))*S.sqrt(vv.dot(vv))*dotcos(uu,vv)))==0,
        M([0,0,0]).dot(M([0,0,0]))==0,
        "非零u=e₁与v=(1,1,0)，余弦为1/√2，余弦定理给出的差向量模平方等于1",
        "若u=0，代数距离公式仍可算，但cosθ=(u·v)/(|u||v|)的分母为0，夹角无定义")

    add("math.hs.geometry.space-dot#3",
        M([1,0,0]).dot(M([0,1,0]))==0 and dotcos(M([1,0,0]),M([0,1,0]))==0,
        M([0,0,0]).dot(M([0,1,0]))==0,
        "非零单位向量e₁,e₂点积与夹角余弦均为0，符合垂直判据",
        "零向量与任意向量也点积为0，但零向量无方向，不可推出夹角为90°")

    e1=M([1,0,0]);e2=M([0,1,0]);e3=M([0,0,1])
    add("math.hs.space.parallel-perpendicular-criteria#3",
        e1.dot(e2)==0 and e1!=M([0,0,0]) and e2!=M([0,0,0]),
        e1.dot(2*e1)!=0,
        "x=0与y=0两平面分别有法向e₁、e₂，法向正交，平面垂直",
        "若法向是e₁与2e₁则点积2不为0，对应平面可以平行或重合而非垂直")

    add("math.hs.space.perpendicular-plane#1",
        e1.cross(e2)!=M([0,0,0]) and e3.dot(e1)==e3.dot(e2)==0,
        e1.cross(2*e1)==M([0,0,0]),
        "e₁,e₂在xy平面内相交且非平行，构成基底；非零e₃正交二者",
        "若拿e₁与2e₁作为所谓两相交方向，叉积为零，无法张成完整平面")

    add("math.hs.space.perpendicular-plane#3",
        e3.dot(2*e1+3*e2)==0 and e1.cross(e2)!=M([0,0,0]),
        e2.dot(e1)==0 and e2.dot(e2)!=0,
        "对xy平面基底e₁,e₂及w=2e₁+3e₂，法向e₃与w点积仍为零",
        "仅证明u=e₂与e₁垂直，不足以推出垂直于xy平面：u·e₂=1")

    P=M([1,2,3]); Q0=M([0,0,0]); D=M([1,0,0]); W=P-Q0
    t0=W.dot(D)/D.dot(D); residual=W-t0*D
    add("math.hs.space.point-line-distance#3",
        residual.dot(D)==0 and residual.dot(residual)==13 and
        W.dot(W)-W.dot(D)**2/D.dot(D)==13,
        M([0,0,0]).dot(M([0,0,0]))==0,
        "P=(1,2,3)到过原点沿e₁的直线最近点为(1,0,0)，距离平方为13",
        "若把直线方向u取零，投影参数(w·u)/|u|²分母为零，不能定义该直线")

    t=S.symbols("t",nonnegative=True)
    add("math.hs.space.solid-volumes#1",
        S.integrate(S.Integer(6),(t,0,5))==30,
        S.integrate(6*(t/5)**2,(t,0,5))!=30,
        "横截面积恒B=6、高h=5的柱体，切片积分严格为30=Bh",
        "横截面积随高度二次变化的锥体并非柱体，其积分为10而非Bh=30")

    add("math.hs.space.solid-volumes#2",
        S.simplify(9*(R(1,3))**2)==1 and S.integrate(9*(t/3)**2,(t,0,3))==9,
        S.simplify(9/(h*h)).subs(h,0)==S.zoo,
        "锥体B=9,h=3时距顶点t=1的截面面积为1，沿高度精确积分9",
        "h=0时相似比t/h未定义，不能直接套用以顶点切片的平方比例式")

    # 3-4-5 triangle: sin A=3/5, sin B=4/5, sin C=1.
    add("math.hs.triangle.sine-law#3",
        R(3,5)/3==R(4,5)/4==R(1,5),
        S.Integer(1)/S.Integer(0)==S.zoo,
        "三边为3,4,5的非退化直角三角形，sin A/a=sin B/b=sin C/c=1/5",
        "若一边长度为0则已非三角形，除以该边非法，不能直接套用正弦定理的商式")

    angle=S.pi/6
    add("math.hs.trig.double-angle-reduction#3",
        S.simplify(S.cos(2*angle)-(1-2*S.sin(angle)**2))==0 and
        S.simplify(S.cos(2*angle)-(2*S.cos(angle)**2-1))==0,
        S.simplify(S.cos(2*angle)-(1-2*S.sin(S.pi/3)**2))!=0,
        "x=π/6时cos(2x)=1/2，两种降幂替换经三角精确化简都等于1/2",
        "若错把sin²x换成另一个角y=π/3的sin²y，1−2sin²y=−1/2≠cos2x")

    ua=M([1,0]); vb=M([1,0]); rotate=M([[0,-1],[1,0]])
    add("math.hs.vector.linear-operations#1",
        M([1,2])+M([3,-1])==M([4,1]),
        ua+vb!=ua+rotate*vb,
        "同一坐标系下有向位移(1,2)+(3,−1)的分量和严格为(4,1)",
        "若第二个坐标系旋转90°，局部位移(1,0)在全局是(0,1)，误加得到(2,0)而非(1,1)")

    ax=M([2,3]); bx=M([1,1]); coefficient=ax.dot(bx)/bx.dot(bx)
    add("math.hs.vector.projection#2",
        coefficient==R(5,2) and (ax-coefficient*bx).dot(bx)==0,
        M([0,0]).dot(M([0,0]))==0,
        "a=(2,3),b=(1,1)给t=5/2，残差(−1/2,1/2)与b严格正交",
        "若b=0，则b·b=0，投影系数出现0/0，不存在唯一的沿b投影参数")

    got={c["historical_step_id"] for c in cases}
    assert len(cases)==len(got)==35
    assert got==set(remaining), f"not all previously unaudited 35 P0 rows covered: {set(remaining)-got}"
    return {
      "schema":"kb142-all-remaining-kb141-p0-exact-witnesses/1",
      "method":"INDEPENDENT_SYMPY_EXACT_FINITE_CASES_WITH_PRECONDITION_FAILURES",
      "original_kb141_lineage_count":47,
      "previously_oracled_in_kb141":12,
      "newly_oracled_in_this_batch":35,
      "new_legal_cases":35,
      "new_invalid_precondition_cases":35,
      "all_kb141_lineage_rows_with_finite_witnesses":47,
      "historical_p0_denominator":127,
      "p0_universally_proven_from_this_batch":0,
      "historical_formally_unverified_steps":538,
      "unresolved_math_conflicts":10,
      "official_course_atom_denominators":{t:None for t in previous.TRACKS},
      "teacher_approvals":0, "student_authoritative_releases":0,
      "student_free_form_step_verified":0,
      "cases":cases
    }


def verify_report(data):
    expected=oracle()
    if data!=expected:
        raise ValueError("finite witness, source SHA, negative case or review status differs from computed oracle")
    return True


def main():
    ap=argparse.ArgumentParser()
    gr=ap.add_mutually_exclusive_group(required=True)
    gr.add_argument("--write",action="store_true")
    gr.add_argument("--check",action="store_true")
    args=ap.parse_args()
    result=oracle()
    if args.write: OUT.write_text(previous.canonical(result),encoding="utf-8")
    else: verify_report(json.loads(OUT.read_text(encoding="utf-8")))
    print("PASS Batch142: 35 exact legal + 35 exact invalid-premise witnesses; no general certification")


if __name__=="__main__":main()
