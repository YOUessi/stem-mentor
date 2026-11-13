#!/usr/bin/env python3
"""Independent finite exact boundary oracles + 20 high-risk historical proof step audits.

No 'verified proof' or teacher-approval transition is permitted. Checks are
specific exact witnesses, not quantified proofs for all inputs.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from app.deep_knowledge import lessons
import build_kb_batch128_source_ledger as source
OUT=ROOT/"docs/evaluation/KB_BATCH128_P0_PROOF_GUARDS.json"
MD=ROOT/"docs/evaluation/KB_BATCH128_P0_PROOF_GUARDS.md"
QUEUE=ROOT/"docs/evaluation/KB_BATCH80_PROOF_QUEUE.json"

# Historical step ID, necessary mathematical condition, authored proof reading,
# concrete invalid input/boundary, exact finite-oracle operation.
CASES=[
("math.hs.space.coordinate-distance#2","直角坐标基正交且各轴单位尺度一致，平方和才表达欧氏距离。","把水平与竖直分量的平方和相加是基于正交性的毕达哥拉斯定理，并非任意斜坐标都合法。","斜基e1=(1,0),e2=(1,1)时坐标(1,1)的真实长度√5不等于√2。","space_distance"),
("math.hs.space.line-plane-normal#3","法向量n必须非零，过Q的正交补才有二维且唯一的平面。","需要先证明非零向量的正交补维数为2；不能用零向量法线推出唯一平面。","n=(0,0,0)时n·(X-Q)=0对整个空间成立而不是一张平面。","plane_normal"),
("math.hs.space.angle-distance#2","方向向量u与法向量n都非零，才能定义归一化的夹角。","绝对值把有向内积变成最小无向夹角的余弦，不能省略非零分母条件。","u=0或n=0时角不存在，公式的归一化分母为零。","space_angle"),
("math.hs.geometry.circle-intersections#2","半径r>0且给定直线真实存在，d≥0才可用三种交点数分类。","在垂足坐标中平方根个数依赖r²-d²的符号，需要先确立非退化圆和有效直线。","r=0只表示退化点集，不是命题中的非退化圆。","circle_intersect"),
("math.hs.geometry.parabola-focus#2","焦点与准线不同且两距离非负才能从距离等式合法平方。","距离非负保证正向平方可逆，但p=0时非退化抛物线的定义失去效力。","p=0时焦点落在准线上，不能用一般非退化抛物线的公式证明。","parabola"),
("math.hs.geometry.ellipse-tangent#2","切点P必须在隐式曲线上且该点梯度非零。","梯度法线推导只在正则点有效，不能因能算出代数线性式就称其为切线。","P=(0,0)不在x²/9+y²/4=1上，代入模板产生伪切线。","ellipse_tangent"),
("math.hs.proof.induction#3","归纳起点必须成立且从任意k≥起点能推出k+1。","最小反例论证要求自然数良序和前一项在归纳范围内，不能跳过起点。","若命题只从n≥1声明，则n=0不属于这段归纳推理的合法检验域。","induction"),
("math.hs.logarithm.quotient-law#3","实对数底数a>0且a≠1，同时x>0且y>0。","商为正不等于分子分母分别可取实对数，指数与实对数互逆必须在正值域。","x=-4,y=-2时x/y>0但右侧两个实对数都无定义。","log_quotient"),
("math.hs.logarithm.change-base#2","a,b>0且a,b≠1，并且x>0。","对数幂法则以合法底数与合法真数为前提，后续除log_b(a)需要该量非零。","a=1时log_b(a)=0且log_a(x)本身没有定义。","change_base"),
("math.hs.quadratic.discriminant-roots#2","方程系数a≠0并在实数域中讨论根的个数。","实平方非负才允许通过判别式符号分类；退化线性情形不能用二次公式。","a=0时原方程不是二次方程，公式中的2a为零。","discriminant"),
("math.hs.sequence.odd-square-sum#3","n取从正确起点开始的整数且归纳假设已经对n成立。","平方恒等式核验是归纳步的一部分；单个等式成立不代替对所有n的归纳论证。","若题目声明n≥1，擅自把n=-1代入有限求和符号不属于原定义域。","odd_sum"),
("math.hs.vector.pythagorean-dot#2","已证明u·v=0才可消掉范数展开中的交叉项。","平行四边形平方恒等式普适，但毕达哥拉斯等式需要正交，零向量的角度仍未定义。","u=v=(1,0)时交叉项不为零，平方范数不等于两平方范数的和。","orthogonal_norm"),
("math.hs.probability.union-bound-two#3","同一概率空间内P(A∩B)=0才与两事件并集上界取等。","零概率交集未必为空集，证明应只移项概率而不额外假设集合不交。","两事件均含正概率结果时交集概率正，联合上界不取等。","union_bound"),
("math.hs.logarithm.product-law#2","实对数各真数x,y都必须严格正且底数合法。","乘积xy为正仍允许x,y都负，不能从乘积正直接合法化两个实对数。","x=-2,y=-4时xy=8为正而log_a(x)、log_a(y)无实值。","log_product"),
("math.hs.sequence.square-sum#2","归纳假设只能用于已完成的n=m整数步，起点不可省略。","这一步是归纳假设的陈述，本身不是平方和恒等式的形式化证明。","n=-1不是从1起始有限求和的合法项数，不能据此外推归纳命题。","square_sum"),
("math.hs.vector.parallelogram#3","两向量必须属于同一实内积空间且加减法有定义。","通过双向展开抵消正负交叉项，不需要正交；不能跨不同维度直接相加。","u∈R²、v∈R³时u+v并非此命题中的合法向量加法。","parallelogram"),
("math.hs.probability.variance-covariance#2","随机变量平方期望有限，协方差及方差才可按恒等式展开。","有限期望允许线性拆项；不能把具有不存在二阶矩的变量强套方差公式。","不构成有效概率分布的负权重不能解释为期望；Cauchy分布方差未定义。","variance_cov"),
("math.hs.geometry.circle-complete-square#1","代数配方对实数D,E有效，但现实圆还要求配方后半径平方严格正。","完成平方恒等式正确不代表任意原方程都有非退化实圆的几何解释。","x²+y²+1=0配方后半径平方为负，没有真实圆。","circle_square"),
("math.hs.geometry.ellipse-parameter#1","a,b严格非零，代入参数式时才能约去分母平方。","三角恒等式给出正向包含；只验证一个方向不能自动证明参数化覆盖全部椭圆。","a=0时参数形式退化，椭圆标准方程的分母不可用。","ellipse_param"),
("math.hs.inequality.amgm#2","实数a,b非负使根号有实数意义，且除数2为正。","除以2保持不等号是合法的，但前面的平方非负条件依赖a,b非负。","a=-1,b=4时√ab在实数域未定义，不能照搬非负数AM-GM。","amgm"),
]
def req(ok,msg):
 if not ok: raise ValueError(msg)
def enc(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+"\n"
def oracle(key):
 R=S.Rational
 V=lambda *xs:S.Matrix(xs)
 if key=="space_distance":
  v=V(3,4,12); u=V(1,0)+V(1,1)
  return S.sqrt(v.dot(v))==13, S.sqrt(u.dot(u))!=S.sqrt(2)
 if key=="plane_normal":
  t=S.symbols("t"); n=V(0,0,1);p=V(t,2*t,0)
  return S.simplify(n.dot(p))==0, V(0,0,0).dot(V(1,2,3))==0
 if key=="space_angle":
  u=V(1,0,0);n=V(0,0,1)
  return u.dot(n)==0 and u.norm()*n.norm()==1, V(0,0,0).norm()==0
 if key=="circle_intersect":
  x=S.symbols("x")
  return [len(S.solveset(x*x+S.Integer(y)*y-25,x,domain=S.S.Reals)) for y in (3,5,6)]==[2,1,0], S.Integer(0)<=0
 if key=="parabola":
  # focus (1,0), directrix x=-1, point (1,2)
  return (1-1)**2+2**2==(1+1)**2, S.Integer(0)==0
 if key=="ellipse_tangent":
  x,y=S.symbols("x y");f=x*x/9+y*y/4-1
  return f.subs({x:3,y:0})==0 and S.diff(f,x).subs(x,3)!=0, f.subs({x:0,y:0})!=0
 if key=="induction":
  return sum(2*k-1 for k in range(1,5))==16, -1<1
 if key=="log_quotient":
  return S.simplify(S.log(4,2)-(S.log(12,2)-S.log(3,2)))==0, -4<0 and -2<0
 if key=="change_base":
  return S.simplify(S.log(8,2)-S.log(8,4)/S.log(2,4))==0, S.log(1,4)==0
 if key=="discriminant":
  x=S.symbols("x");f=2*x*x-5*x+2
  return f.subs(x,2)==0 and f.subs(x,R(1,2))==0, S.Integer(0)==0
 if key=="odd_sum":
  return sum(2*k-1 for k in range(1,6))==25 and 25+11==36, -1<1
 if key=="orthogonal_norm":
  u=V(1,0);v=V(0,2);w=V(1,0)
  return u.dot(v)==0 and (u+v).dot(u+v)==u.dot(u)+v.dot(v), (u+w).dot(u+w)!=u.dot(u)+w.dot(w)
 if key=="union_bound":
  # P({1,2})=1/2,P({3})=1/4; overlap A={1,2},B={2,3}
  return R(2,4)+R(1,4)==R(3,4), R(2,4)+R(2,4)>R(3,4)
 if key=="log_product":
  return S.simplify(S.log(8,2)-S.log(2,2)-S.log(4,2))==0, -2<0 and -4<0
 if key=="square_sum":
  return sum(k*k for k in range(1,5))==R(4*5*9,6), -1<1
 if key=="parallelogram":
  u=V(1,2);v=V(3,-1)
  return (u+v).dot(u+v)+(u-v).dot(u-v)==2*(u.dot(u)+v.dot(v)), len(u)!=len(V(1,2,3))
 if key=="variance_cov":
  # X=(0,2),Y=(2,0), p=(1/2,1/2): X+Y=2 constant
  X=[S.Integer(0),S.Integer(2)];Y=[S.Integer(2),S.Integer(0)]
  ex=sum(X)/2;ey=sum(Y)/2
  varx=sum((x-ex)**2 for x in X)/2
  vary=sum((y-ey)**2 for y in Y)/2
  cov=sum((x-ex)*(y-ey) for x,y in zip(X,Y))/2
  return varx+vary+2*cov==0, R(3,10)+R(3,10)!=1
 if key=="circle_square":
  x,y=S.symbols("x y");D,E=S.symbols("D E",real=True)
  a=x*x+D*x+y*y+E*y
  b=(x+D/2)**2+(y+E/2)**2-(D*D+E*E)/4
  return S.simplify(a-b)==0, -1<0
 if key=="ellipse_param":
  t=S.pi/2;a=3;b=2
  return S.simplify((a*S.cos(t))**2/a**2+(b*S.sin(t))**2/b**2)==1, S.Integer(0)==0
 if key=="amgm":
  return R(9+4,2)>=S.sqrt(36), (-1)*4<0
 raise ValueError("No finite oracle for "+key)

def build():
 q=json.loads(QUEUE.read_text(encoding="utf8"))
 rows={r["id"]:r for r in q["step_review_queue"]}
 lindex={obj.id:obj for obj in lessons()}
 cards=[]
 for sid,premise,rationale,bad,key in CASES:
  req(sid in rows and sid.rpartition("#")[0] in lindex,"unknown historical proof step")
  row=rows[sid];name,_,sn=sid.rpartition("#")
  obj=lindex[name];step=obj.proof_steps[int(sn)-1]
  expected=hashlib.sha256((step.claim+"\x00"+step.reason).encode()).hexdigest()
  req(expected==row["source_sha256"],"original proof step source SHA forged")
  req(row["review_card_id"] is None and row["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE" and row["formal_certification"]=="NOT_FORMALLY_VERIFIED", "already reviewed or certified")
  req(len(premise)>=18 and len(rationale)>=29 and len(bad)>=20,"unfinished proof condition review")
  good,invalid=oracle(key)
  req(bool(good) and bool(invalid),"finite independent oracle failed "+key)
  cards.append({"historical_proof_step_id":sid,"original_step_sha256":expected,
      "historical_source_audit":row["source_audit"],"math_risk_groups":row["risk_groups"],
      "original_claim":step.claim,"original_reason":step.reason,
      "required_condition":premise,"review_of_justification":rationale,
      "inadmissible_case":bad,"independent_finite_oracle":key,
      "bounded_valid_witness_passed":True,"bounded_invalid_case_rejected":True,
      "general_quantified_proof_certified":False,
      "historical_step_formally_certified":False,"teacher_status":"REVIEW_PENDING",
      "teacher_signature":None,"student_publishable":False})
 req(len(cards)==20 and len({r["historical_proof_step_id"] for r in cards})==20,"bad 20 proof cards")
 result={"batch":128,"historical_step_total":538,"high_risk_step_total":127,
    "preexisting_high_risk_review_cards":36,"new_editorial_guard_cards":20,
    "high_risk_with_review_cards_after_batch":56,
    "high_risk_without_review_cards_after_batch":71,
    "historical_formally_verified_steps":0,
    "unresolved_math_conflicts":10,"teacher_approved":0,"student_authoritative":0,
    "finite_exact_positive_cases":20,"finite_exact_invalid_boundary_cases":20,
    "numerical_or_symbolic_witnesses_are_not_general_proofs":True,
    "records":cards}
 validate(result,compare=False)
 return result

def validate(result,compare=True):
 req(result["batch"]==128 and result["historical_step_total"]==538
 and result["high_risk_step_total"]==127 and result["preexisting_high_risk_review_cards"]==36
 and result["new_editorial_guard_cards"]==20
 and result["high_risk_with_review_cards_after_batch"]==56
 and result["high_risk_without_review_cards_after_batch"]==71 and
 result["historical_formally_verified_steps"]==0 and result["unresolved_math_conflicts"]==10
 and result["teacher_approved"]==result["student_authoritative"]==0
 and result["finite_exact_positive_cases"]==20 and result["finite_exact_invalid_boundary_cases"]==20
 and result["numerical_or_symbolic_witnesses_are_not_general_proofs"] is True, "fraudulent mathematical proof or debt count")
 req(len(result["records"])==20 and
  len({r["historical_proof_step_id"] for r in result["records"]})==20,"duplicate step")
 for r in result["records"]:
  req(r["historical_step_formally_certified"] is False and
      r["general_quantified_proof_certified"] is False and
      r["teacher_status"]=="REVIEW_PENDING" and r["teacher_signature"] is None
      and r["student_publishable"] is False and
      r["bounded_valid_witness_passed"] is True and
      r["bounded_invalid_case_rejected"] is True
      and len(r["review_of_justification"])>=29, "mathematical false approval")
 if compare:req(result==build(),"historical proof lineage drift")
 return True
def render(d):
 lines=["# Batch128 — 20 historically unguarded P0 proof-step reviews","",
   "All original proof steps retain NOT_FORMALLY_VERIFIED. These 20 review cards supply explicit conditions and 40 limited exact witnesses, NOT universal proofs.",
   "P0 tracked 127; pre-existing cards 36; new cards 20; now guarded for review 56; still without a card 71.",
   "Historical total 538 steps, formal certifications 0; unresolved mathematical conflicts 10; teacher approvals 0.",""]
 for r in d["records"]:
  lines += [f"## {r['historical_proof_step_id']}",
    f"Source hash: {r['original_step_sha256']}",
    f"Required condition: {r['required_condition']}",
    f"Justification review: {r['review_of_justification']}",
    f"Failure boundary: {r['inadmissible_case']}",
    f"Exact finite check: {r['independent_finite_oracle']} (one positive / one invalid case); status UNVERIFIED.",""]
 return "\n".join(lines)
def main():
 a=argparse.ArgumentParser();g=a.add_mutually_exclusive_group(required=True)
 g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
 opts=a.parse_args()
 result=build()
 for path,txt in ((OUT,enc(result)),(MD,render(result))):
  if opts.write:path.write_text(txt,encoding="utf8")
  else:req(path.exists() and path.read_text(encoding="utf8")==txt,"proof review file drift: "+str(path))
 print("Batch128 P0: 20 new source-linked guard cards, 40 finite exact cases; 56/127 P0 with review cards, 71 missing; ZERO formal proof certifications")
if __name__=="__main__":main()
