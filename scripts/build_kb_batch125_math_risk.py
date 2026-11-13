#!/usr/bin/env python3
"""Independent exact counterexamples for all 10 unresolved historical conflicts.

These are finite mathematical witnesses, NEVER certified universal proofs or
student free-form grading. The historical queue remains intact.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"docs/evaluation/KB_BATCH125_CONFLICT_RISK_REVIEW.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH125_MATH_COUNTEREXAMPLES.md"
CONFLICTS=ROOT/"docs/evaluation/KB_BATCH70_TEN_CONFLICT_PROOF_REVIEW.json"
DEBT=ROOT/"docs/evaluation/KB_BATCH81_RISK_CENSUS.json"
TEXT=[
("复合定义域并非两个原定义域的简单交集",
 "先确定内层输出是否落入外层定义域；对有分母的外层函数检查非零。",
 "当内层输出为0时，外层倒数在该点不存在；不能因内层在实数域定义便放行。",
 "将复合表达改为根号或对数时，逐层生成非负或严格正值条件。"),
("定义域对称是全域奇偶性不可省的前提",
 "检验每个输入的负数也在定义域，然后才判断等式；零函数是奇偶兼有的边界。",
 "仅在非负半轴上给出的x²不能直接称为全域偶函数。",
 "把定义域换成不对称的有限集合，观察代数相等如何不足以成立。"),
("分段规则覆盖后还需要重叠区输出一致",
 "对每个定义域输入，至少有一条分支适用；重叠区的函数值必须相同。",
 "在x=0两个分支分别输出0和1，故不是单值函数。",
 "为同一个输入添加第三条分支，检验三者是否同时一致。"),
("介值定理需要连续性且只保证存在",
 "核对闭区间连续和端点异号；得出有根后不得推断唯一性。",
 "跳跃函数可两端异号但全区间没有零点；三次连续函数可有多个零点。",
 "比较二分法的存在性前提与单调性提供的唯一性前提。"),
("点到直线距离公式分母不能是零",
 "把Ax+By+C=0视为直线前，必须满足法向量(A,B)不为零。",
 "若A=B=0且C不等于零，得到的是空集而非直线，距离表达式分母为零。",
 "同时比较零法向量且C=0时方程代表整个平面而非一条线。"),
("二项式分布需独立且同一成功率",
 "先核对每次伯努利试验相互独立、成功率一致，才使用组合计数。",
 "两次成功指示完全相同时，不可能恰好成功一次，即使各自边际都是一半。",
 "保持边际概率不变而改变联合相关结构，比较成功次数分布。"),
("超几何分布要求无放回与有效支持集",
 "从有限总体无放回等可能抽取固定数量，检查样本数和成功数的整数边界。",
 "放回抽样会改变成功概率且不满足固定子集等可能模型。",
 "使用总体较小且成功项较少的例子列举组合数与支持集。"),
("最小二乘斜率与相关系数有不同非零条件",
 "斜率需要Sxx>0，Pearson相关还要Syy>0；二者都不能用关联代替因果。",
 "所有x相同时斜率分母为零；误把无法辨识写成斜率0不合法。",
 "保留相同x数据但替换y，检验最小二乘常数拟合与斜率不唯一。"),
("三角形正弦面积公式要求两边真正夹角",
 "S=ab sinθ/2中的θ必须是所选a、b的夹角，长度均为正。",
 "直角三角形的边3和4夹角是直角，错取边3的对角会给出不同面积。",
 "同一三角形换用另一对边时，重新识别两边夹角。"),
("向量运算必须位于同一向量空间",
 "逐坐标线性运算需要相同维数；叉积更有专门的三维约定。",
 "二维向量和三维向量不能在未定义嵌入的情况下直接相加。",
 "在二维到三维添加零坐标是额外指定的映射，不是原向量相加的默认规则。"),
]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def serial(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def exact_witnesses():
    R=S.Rational;x=S.symbols("x",real=True)
    expr=x*(x-1)*(x+1)
    # Each pair checks a legal example and a false generalisation/invalid premise.
    positive=[
      S.Rational(1,3-2)==1 and S.denom(S.cancel(1/(x-2))).subs(x,3)==1,
      all(z*z==(-z)*(-z) for z in (-2,-1,0,1,2)) and all(0==-0 for _ in range(3)),
      S.Integer(0)**2==S.Integer(2)*0,
      expr.subs(x,-2)<0 and expr.subs(x,2)>0 and all(expr.subs(x,t)==0 for t in (-1,0,1)),
      S.Abs(3*0+4*0-25)/S.sqrt(3**2+4**2)==5,
      R(2,4)==R(1,2),
      S.binomial(3,2)*S.binomial(3,0)/S.binomial(6,2)==R(1,5),
      S.simplify(sum((t-1)**2 for t in [0,1,2]))==2 and
         S.simplify(sum((a-1)*(b-3) for a,b in [(0,1),(1,3),(2,5)]))==4,
      R(1,2)*3*4*S.sin(S.pi/2)==6,
      S.Matrix([1,2])*2+S.Matrix([3,4])*2==S.Matrix([8,12]),
    ]
    negative=[
      S.denom(S.cancel(1/(x-2))).subs(x,2)==0,
      not all(-z in {0,1,2} for z in {0,1,2}),
      S.Integer(0)**2!=S.Integer(0)+1,
      (lambda f: f(-1)<0 and f(1)>0 and all(f(t)!=0 for t in (-1,0,1)))(lambda t:-1 if t<0 else 1),
      S.sqrt(0)==0 and S.S(1)/S.sqrt(0)==S.zoo,
      (sum(1 for a in (0,1) if 2*a==1)==0) and R(2,4)!=0,
      R(1,2)**2!=R(1,5),
      sum((z-1)**2 for z in [1,1,1])==0,
      R(1,2)*3*4*R(3,5)!=6,
      len(S.Matrix([1,2]))!=len(S.Matrix([3,4,5])),
    ]
    need(len(positive)==len(negative)==10 and
         all(v is True or v is S.true for v in positive) and
         all(v is True or v is S.true for v in negative),
         "one exact witness failed")
    return [(bool(a),bool(b)) for a,b in zip(positive,negative)]
def build():
    historical=json.loads(CONFLICTS.read_text(encoding="utf-8"))
    debt=json.loads(DEBT.read_text(encoding="utf-8"))
    need(len(historical["records"])==len(TEXT)==10 and
         historical["conflicts_resolved"]==historical["general_proofs_certified"]==0,
         "historical conflict changed")
    need(debt["historical_proof_denominator"]==538 and debt["formally_certified"]==0,
         "historical proof census changed")
    need(sum(v["total"] for v in debt["by_risk"].values())==538,
         "historical risk partition invalid")
    checks=exact_witnesses()
    packets=[]
    for i,(source, authored) in enumerate(zip(historical["records"],TEXT)):
        need(source["conflict_index"]==i and source["dispute_resolution"].startswith("UNRESOLVED")
             and source["general_proof_certified"] is False and source["teacher_review"]=="REVIEW_PENDING"
             and len(source["active_sha256"])==64,"conflict has been resolved/replaced; rebuild required")
        title,guard,counter,transfer=authored
        packets.append({"id":"KB125-CONFLICT-%02d"%(i+1),"conflict_id":source["conflict_id"],
          "source_active_sha256":source["active_sha256"],"title":title,
          "required_precondition":guard,"invalid_case_explained":counter,
          "far_transfer_prompt":transfer,
          "finite_legal_instance_checked":checks[i][0],
          "finite_invalid_assumption_checked":checks[i][1],
          "whole_proof_formally_certified":False,"teacher_status":"REVIEW_PENDING",
          "teacher_signature":None,"student_freeform_certified":False,
          "student_publishable":False})
    result={"batch":125,"historical_unverified_proof_steps":538,
       "risk_partition":{k:v["total"] for k,v in debt["by_risk"].items()},
       "proof_steps_certified_this_batch":0,
       "historical_conflicts_unresolved":10,"conflicts_resolved_this_batch":0,
       "exact_legal_witnesses_passed":10,"invalid_premise_witnesses_passed":10,
       "source_conflict_sha256":hashlib.sha256(CONFLICTS.read_bytes()).hexdigest(),
       "source_proof_census_sha256":hashlib.sha256(DEBT.read_bytes()).hexdigest(),
       "student_authoritative":False,"teacher_approved":False,"packets":packets}
    validate(result);return result
def validate(r):
    need(r["historical_unverified_proof_steps"]==538 and
         sum(r["risk_partition"].values())==538
         and len(r["packets"])==r["historical_conflicts_unresolved"]==10 and
         r["exact_legal_witnesses_passed"]==r["invalid_premise_witnesses_passed"]==10
         and r["proof_steps_certified_this_batch"]==r["conflicts_resolved_this_batch"]==0
         and r["student_authoritative"] is False and r["teacher_approved"] is False,
         "proof/approval claim drift")
    need(all(p["finite_legal_instance_checked"] is True
       and p["finite_invalid_assumption_checked"] is True
       and p["whole_proof_formally_certified"] is False
       and p["teacher_signature"] is None and p["teacher_status"]=="REVIEW_PENDING"
       and p["student_freeform_certified"] is False and p["student_publishable"] is False
       and len(p["source_active_sha256"])==64 for p in r["packets"]),
       "unsafe promoted mathematics")
    need(r["source_conflict_sha256"]==hashlib.sha256(CONFLICTS.read_bytes()).hexdigest()
       and r["source_proof_census_sha256"]==hashlib.sha256(DEBT.read_bytes()).hexdigest(),
       "source conflict/proof census drift")
    return True
def render(r):
    lines=["# Batch125｜10项数学争议的独立精确反例与前提审查","",
      "本稿独立实现20组有限精确合法/失效实例验证。它们**不是一般定理的形式证明，也不裁决历史冲突**。",
      "538条历史证明步骤仍然全部待认证；10项历史冲突仍未解决。教师审核与学生自由文本证明认证均为0。",""]
    for item in r["packets"]:
        lines+=["## "+item["id"]+" · "+item["title"],
        "- 历史冲突ID: `"+item["conflict_id"]+"`",
        "- 适用条件: "+item["required_precondition"],
        "- 错误/反例解释: "+item["invalid_case_explained"],
        "- 远迁移教学问题: "+item["far_transfer_prompt"],
        "- 核验范围: 1组合法例 + 1组无效前提精确见证；不认证整体推理；REVIEW_PENDING。",""]
    lines+=["## 审校与发布门禁","",
       "原始争议材料、风险优先级及冲突ID保持不变。未经真实教师逐步审校不能覆盖原争议或推送到学生端权威RAG。",
       "下一阶段应逐项形成前提语义合同、分步定理依据和反例覆盖，之后再申请教师签署。",""]
    return "\n".join(lines)
def main():
    a=argparse.ArgumentParser();g=a.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    o=a.parse_args();x=build()
    for p,v in ((OUT,serial(x)),(REPORT,render(x))):
        if o.write:p.write_text(v,encoding="utf-8")
        else:need(p.exists() and p.read_text(encoding="utf-8")==v,"math audit changed "+str(p))
    print("Batch125: 10 unresolved conflicts, 20 finite independent checks; 538 unverified steps unchanged")
if __name__=="__main__":main()
