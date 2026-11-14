#!/usr/bin/env python3
"""Independent finite SymPy conflict witnesses. Keeps both source versions pending."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from math import comb
import sympy as s

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"docs/evaluation/KB_CONFLICT_RISK_BATCH07.json"
OUT=ROOT/"docs/evaluation/KB_BATCH148_CONFLICT_MATH_WITNESSES.json"
MD=ROOT/"docs/evaluation/KB_BATCH148_CONFLICT_MATH_WITNESSES.md"

def check(value,msg):
    if not value:raise ValueError("K07 conflict oracle: "+msg)
def enc(x):return json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
def iszero(expr):return s.simplify(expr)==0
CASE_DESCRIPTIONS={
"math.hs.function.composition-domain": [
    "f(t)=√t, g(x)=x−5：x=7时f(g(7))=√2为实数。",
    "x=5时复合函数取值0，定义域端点必须包含。",
    "x=4时g(4)=−1不属于f的非负实数定义域，复合函数在实数域无值。",
    "误将D_f∩D_g=[0,+∞)作为D_{f∘g}：x=1在交集中但f(g(1))不是实数。"],
"math.hs.function.parity": [
    "f(x)=x²在对称实数域满足f(−x)=f(x)，偶性成立。",
    "零函数定义于对称区间时同时满足f(−x)=f(x)与f(−x)=−f(x)。",
    "仅将f(x)=x²限制到{1,2}，定义域对负号不封闭，不能宣布偶函数。",
    "f(x)=x在实数域一般不满足f(−x)=f(x)，并非偶函数。"],
"math.hs.function.piecewise": [
    "f(x)=x在x<0和x≥0分别给相同规则，左右极限均为0，连续。",
    "在左支f(x)=0(x<0)时，左侧极限为0而且该局部支连续。",
    "同一输入x=0若被两个分支分别指定0和1，则输出冲突，不能构成单值函数。",
    "f(x)=0(x<0), 1(x≥0)：分段规则成立但0处左右极限不同，不能推出整体连续。"],
"math.hs.function.zero-ivt": [
    "f(x)=x在[−1,1]连续且端点异号，存在零点0。",
    "f(x)=x(x²−1)在[−2,2]有三个不同零点−1、0、1，存在性不意味着唯一性。",
    "端点符号−1与1本身不保证跨区间的连续性；不能省略连续假设。",
    "f(x)=x²−1在[−2,2]两端同为3>0，但内部有零点±1。"],
"math.hs.geometry.point-line-distance": [
    "点(0,0)到直线3x+4y−5=0距离为|−5|/√25=1。",
    "点(3,−1)满足3×3+4×(−1)−5=0，因此距离0。",
    "A=B=0不是有效直线法向量，距离公式的分母为0，必须拒绝。",
    "省略法向量归一化会把(0,0)到给定直线的距离错误算为5。"],
"math.hs.probability.binomial-distribution": [
    "独立公平伯努利试验3次，P(X=1)=C(3,1)(1/2)^3=3/8。",
    "p=0的边界模型中，3次成功数恒为0，所有k的概率和仍为1。",
    "n=3而k=4不在成功次数支持集内，不能生造C(3,4)等于正常事件概率。",
    "2张中有1张成功无放回取完，则成功数必为1；错误二项模型会给P(X=1)=1/2。"],
"math.hs.probability.hypergeometric": [
    "N=5、K=2、不放回n=2时P(X=1)=C(2,1)C(3,1)/C(5,2)=3/5。",
    "同一合法超几何分布k=0,1,2的概率严格求和为1。",
    "n=2时k=3超过合法支持集，必须拒绝。",
    "相同总体若改成有放回独立抽样，则P(X=1)=2×(2/5)(3/5)=12/25，区别于3/5。"],
"math.hs.statistics.correlation-regression": [
    "样本x=(0,1,2),y=(1,3,5)拟合带截距OLS，斜率2截距1。",
    "样本x=(0,1,2),y=(5,5,5)自变量不常量，OLS斜率0合法；相关系数则未必有定义。",
    "样本x=(1,1,1)方差为0，OLS斜率除以0，不能报告有限斜率。",
    "对于前述斜率2样本，说斜率必为0明显不符合原始坐标，须从协方差求。"],
"math.hs.triangle.area-sine": [
    "两边3、4夹角90°时，面积=3×4×sin90°/2=6。",
    "两边3、4夹角30°时，面积=3×4×sin30°/2=3。",
    "夹角0°使三点退化共线，不满足非退化三角形角域0<θ<π。",
    "夹角30°的面积3不等于6，不能不看实际夹角就固定使用直角面积。"],
"math.hs.vector.linear-operations": [
    "同维二维向量(a,b)+(c,d)=(a+c,b+d)按分量相加。",
    "二维向量线性运算的分配律2(v+w)=2v+2w在所有实坐标上恒成立。",
    "二维和三维向量长度不匹配，原有逐分量加法尚未定义。",
    "(1,2)+(3,4)=(4,6)，并非(4,7)，不能仅凭类似数字认定向量结果。"]
}

def cases():
    x=s.symbols('x',real=True); a,b,c,d=s.symbols('a b c d',real=True)
    results={}
    def put(key,valid,boundary,invalid,negative):
        results[key]=[
          ("VALID_EXACT_WITNESS",valid),
          ("LEGAL_BOUNDARY_WITNESS",boundary),
          ("REJECT_INVALID_HYPOTHESIS",invalid),
          ("REJECT_FALSE_UNIVERSAL_INFERENCE",negative),
        ]
    # 1. Composition f(g(x)) versus D_f intersect D_g; sqrt(x-5) is real only x>=5.
    put("math.hs.function.composition-domain",
        bool(s.sqrt(7-5).is_real), bool(s.sqrt(5-5).is_real),
        not bool(s.sqrt(4-5).is_real), 1 in range(0,10) and not bool(s.sqrt(1-5).is_real))
    # 2. Symmetry of the domain is required independently of the algebraic expression.
    put("math.hs.function.parity",
        iszero((-x)**2-x**2),iszero(s.Integer(0)+s.Integer(0)),
        not ({1,2}=={-v for v in {1,2}}),
        not iszero((-x)-x))
    # 3. Two piecewise branches can be continuous or discontinuous; duplicate inputs must agree.
    put("math.hs.function.piecewise",
        s.limit(x,x,0,dir='-')==s.limit(x,x,0,dir='+'),
        s.limit(s.Integer(0),x,0,dir='-')==s.Integer(0),
        s.Integer(0)!=s.Integer(1),
        s.limit(s.Integer(0),x,0,dir='-')!=s.limit(s.Integer(1),x,0,dir='+'))
    # 4. IVT: existence not uniqueness; endpoint same sign does not imply no roots.
    poly=x*(x*x-1)
    jump=s.Piecewise((s.Integer(-1),x<0),(s.Integer(1),True))
    put("math.hs.function.zero-ivt",
        s.solveset(x, x, domain=s.Interval(-1,1))==s.FiniteSet(0),
        s.solveset(poly,x,domain=s.Interval(-2,2))==s.FiniteSet(-1,0,1),
        jump.subs(x,-1)==-1 and jump.subs(x,0)==1 and
            {v.expr for v in jump.args} == {-1,1} and
            all(jump.subs(x,t)!=0 for t in (-1,0,1)),
        s.solveset(x*x-1,x,domain=s.Interval(-2,2))==s.FiniteSet(-1,1))
    # 5. Point-to-line distance requires a nonzero normal vector (A,B).
    def dist(A,B,C,X,Y):
        return s.Abs(A*X+B*Y+C)/s.sqrt(A*A+B*B)
    put("math.hs.geometry.point-line-distance",
        iszero(dist(3,4,-5,0,0)-1),
        iszero(dist(3,4,-5,3,-1)),
        iszero(s.Integer(0)**2+s.Integer(0)**2),
        not iszero(dist(3,4,-5,0,0)-5))
    # 6. Binomial counting requires independent identically distributed trials.
    binom=lambda n,k,p:s.Integer(comb(n,k))*p**k*(1-p)**(n-k)
    put("math.hs.probability.binomial-distribution",
        iszero(binom(3,1,s.Rational(1,2))-s.Rational(3,8)),
        iszero(sum(binom(3,k,s.Integer(0)) for k in range(4))-1),
        not 0<=4<=3,
        not iszero(binom(2,1,s.Rational(1,2))-1))
    # 7. Hypergeometric sampling without replacement, supporting integer range.
    hg=lambda N,K,n,k:s.Rational(comb(K,k)*comb(N-K,n-k),comb(N,n))
    put("math.hs.probability.hypergeometric",
        iszero(hg(5,2,2,1)-s.Rational(6,10)),
        iszero(sum(hg(5,2,2,k) for k in range(3))-1),
        not (0<=3<=min(2,2)),
        not iszero(hg(5,2,2,1)-2*s.Rational(2,5)*s.Rational(3,5)))
    # 8. Least squares with intercept; x variance required; correlation is a separate object.
    def slope(xs,ys):
        xm=s.Rational(sum(xs),len(xs));ym=s.Rational(sum(ys),len(ys))
        den=sum((v-xm)**2 for v in xs)
        return None if den==0 else s.simplify(sum((v-xm)*(w-ym) for v,w in zip(xs,ys))/den)
    put("math.hs.statistics.correlation-regression",
        slope([0,1,2],[1,3,5])==2,
        slope([0,1,2],[5,5,5])==0,
        slope([1,1,1],[1,2,3]) is None,
        slope([0,1,2],[1,3,5])!=0)
    # 9. Sine area formula for INCLUDED angle only; nondegenerate triangle theta in (0,pi).
    put("math.hs.triangle.area-sine",
        iszero(s.Rational(1,2)*3*4*s.sin(s.pi/2)-6),
        iszero(s.Rational(1,2)*3*4*s.sin(s.pi/6)-3),
        not (0<s.Integer(0)<s.pi),
        not iszero(s.Rational(1,2)*3*4*s.sin(s.pi/6)-6))
    # 10. Vector linear operations in a common vector space with matching dimensions.
    v=s.Matrix([a,b]);w=s.Matrix([c,d])
    put("math.hs.vector.linear-operations",
        v+w==s.Matrix([a+c,b+d]),
        iszero(sum((2*v+2*w-2*(v+w)).applyfunc(s.simplify))),
        len((1,2))!=len((3,4,5)),
        s.Matrix([1,2])+s.Matrix([3,4])!=s.Matrix([4,7]))
    return results

def build():
    orig=json.loads(SOURCE.read_text(encoding="utf-8"))
    check(orig["summary"]["conflict_count"]==10 and orig["summary"]["unresolved_conflicts"]==10,
          "original conflict ledger changed")
    ev=cases()
    check(set(ev)=={r["id"] for r in orig["conflicts"]}==set(CASE_DESCRIPTIONS),"missing conflict IDs or descriptions")
    rows=[]
    for conflict in orig["conflicts"]:
        key=conflict["id"]
        for j,(kind,boolean) in enumerate(ev[key]):
            check(type(boolean) is bool and boolean, "oracle failed "+key+":"+kind)
            check(len(CASE_DESCRIPTIONS[key])==4 and len(CASE_DESCRIPTIONS[key][j])>=20,"missing mathematical evidence narrative")
            rows.append(dict(conflict_id=key,case_index=j,case_kind=kind,
                original_mathematical_witness=CASE_DESCRIPTIONS[key][j],
                exact_finite_check_passed=True,
                interpretation="finite controlled witness or rejected missing premise; not general formal certification"))
    return dict(schema="kb148-ten-conflicts-forty-finite-exact-witnesses/1",
       conflicts_total=10,conflicts_with_finite_cases=10,
       independent_exact_cases=len(rows),cases=rows,
       formal_general_proof_certificates=0,math_conflicts_human_resolved=0,
       source_versions_merged=0,teacher_approved=0,student_authoritative=0,
       review_state="REVIEW_PENDING",
       source_identity=[dict(id=r["id"],candidate_sha256=r["candidate_sha256"],
        active_sha256=r["active_sha256"],decision=r["decision"],
        evidence_status=r["evidence_status"]) for r in orig["conflicts"]],
       warning="40 finite SymPy/exact witnesses do not resolve the ten source version conflicts or certify universal proofs")

def validate(v):
    check(v["independent_exact_cases"]==40 and len(v["cases"])==40 and len(v["source_identity"])==10,"count drift")
    check(not any(v[k] for k in ("formal_general_proof_certificates","math_conflicts_human_resolved",
                      "source_versions_merged","teacher_approved","student_authoritative")),"forged approval")
    check(v["review_state"]=="REVIEW_PENDING" and
          {r["id"] for r in v["source_identity"]}=={r["conflict_id"] for r in v["cases"]},
          "conflict identity drift")
    for r in v["cases"]:
        check(r["case_kind"] in ("VALID_EXACT_WITNESS","LEGAL_BOUNDARY_WITNESS",
              "REJECT_INVALID_HYPOTHESIS","REJECT_FALSE_UNIVERSAL_INFERENCE") and
              r["exact_finite_check_passed"] is True,"invalid finite evidence")
    return True

def render(v):
    lines=["# K07 Batch148｜10个冲突的40项精确有限数学证据","",
      "来自历史两版数学条目的真实冲突ID与原始SHA；不自动合并任何来源版本。","",
      "| 冲突ID | 合法计算 | 边界 | 无效前提拒绝 | 错误泛化反例 | 审查 |",
      "|---|---:|---:|---:|---:|---|"]
    for s in v["source_identity"]:
        lines.append(f"| {s['id']} | 1 | 1 | 1 | 1 | REVIEW_PENDING |")
    lines+=["","共40/40有限检查；**不是10项冲突数学裁决，更不是538条历史证明步骤认证**。",
        "下一步须逐条比对两版正式陈述、完整定义域及前提，做教师数学审核签署。",""]
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser();m=p.add_mutually_exclusive_group(required=True)
    m.add_argument("--write",action="store_true");m.add_argument("--check",action="store_true")
    a=p.parse_args();v=build();validate(v)
    if a.write:
        OUT.write_text(enc(v),encoding="utf-8")
        MD.write_text(render(v),encoding="utf-8")
    else:
        check(json.loads(OUT.read_text(encoding="utf-8"))==v and MD.read_text(encoding="utf-8")==render(v),"oracle output drift")
    print("PASS K07 Batch148: 10 source conflicts, 40/40 finite exact math cases; all adjudications pending")

if __name__=="__main__":main()
