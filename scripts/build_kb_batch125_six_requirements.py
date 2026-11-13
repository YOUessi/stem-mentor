#!/usr/bin/env python3
"""Six historically unmatched numbered requirements: true editorial triage.
No normative standard excerpt is committed. All six outcomes need a teacher.
"""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch125_provenance as base
OUT=ROOT/"docs/evaluation/KB_BATCH125_SIX_NUMBERED_REQUIREMENT_REVIEWS.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH125_SIX_REQUIREMENTS.md"
# Curated from local source with adjacent context, not just marker-heading guesses.
# Printed page, line, type, substantive mathematical decomposition, constraints,
# invalid simplification, and one concrete next-step review.
ROWS=[
(21,6,"COMPULSORY","HISTORY_AND_INQUIRY_ACTIVITY_CANDIDATE",
 "对数发展史研究是学习活动；需要讲解指数与对数互逆、对数化乘为加，但历史研究本身不宜自动新增同名定理原子。",
 "应引用已学的实对数合法底数与正真数条件，历史材料须有合法授权来源。",
 "不能将撰写历史报告误记为学生已证明换底公式；不能复刻版权书中史料全文。",
 "请教师核对是否归入探究活动清单，并给出可被教学Agent检索的原创历史探究题。"),
(23,9,"COMPULSORY","MODEL_EXPLORATION_ACTIVITY_CANDIDATE",
 "实际模型资料搜集与参数意义讨论属于跨领域建模任务；可链接函数拟合、单位、残差、数据范围，而不是单一数学定理。",
 "应标注变量、参数单位、训练数据覆盖区间与可检验的预测目标。",
 "若仅给指数或线性拟合曲线，不得暗示模型对未来外推准确或有因果效应。",
 "请教师判定建模任务与函数知识之间的多对多映射，保留真实案例的授权证据。"),
(29,9,"COMPULSORY","GEOMETRY_PROOF_COMPETENCY_CANDIDATE",
 "空间点线面位置关系的综合证明能力；不应把抽象‘会证明’直接等同另一条新定理，可链接线面平行、垂直及两面垂直判定。",
 "每道证明须明确线不在平面内、空间线面垂直的全部方向条件，给出依赖的原命题。",
 "由投影图的直角、平行线外观直接认定三维垂直是无效推理；缺条件的判定不能替代证明。",
 "请教师分拆为可命名的题族和逐步证明能力要求，逐条映射既有空间定理原子。"),
(32,18,"COMPULSORY","SAMPLING_METHOD_BUNDLE_CANDIDATE",
 "选取抽样方法要求先确定总体与抽样框，再按场景比较简单随机抽样与分层随机抽样的适用性及成本。",
 "每个备选方法要说明抽中概率、分层比例、样本量与非应答风险，设计应服务既定推断目标。",
 "便利抽样不会因为样本数大就自动变成随机样本；分层抽样也无法修复错误的总体定义。",
 "请教师拆解简单随机/分层/抽样偏差的独立方法目标，核对课程范围后绑定原创题族。"),
(32,29,"COMPULSORY","POPULATION_ESTIMATION_COMPETENCY_CANDIDATE",
 "使用样本描述总体取值规律是一种统计推断能力；应联系经验分布、抽样变异、样本代表性与不确定性。",
 "需区分描述性样本分布与对总体分布的推断，声明抽样机制和有限数据的有效范围。",
 "不能把样本直方图高度当总体真实概率，也不能忽略分箱、测量误差和选择偏差。",
 "请教师核对是否拆为经验分布估计、误差来源与统计解释三个方法目标。"),
(44,16,"SELECTIVE_COMPULSORY","CROSS_TOPIC_GEOMETRIC_REASONING_CANDIDATE",
 "数形结合是贯穿圆锥曲线和方程的学习策略，不宜凭一句思想目标新造一条可形式证明的定理。",
 "图形结论必须由圆锥曲线的严格定义、标准方程及其参数范围支持，必要时核对退化边界。",
 "将草图的相切、相交或轨迹形状视作已证代数结果属于错误；单凭画板不能给出数学认证。",
 "请教师把这项思想能力链接椭圆、双曲线、抛物线定义与变式，而非直接计数为新知识原子。"),
]
def need(b,s):
    if not b:raise ValueError(s)
def dump(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def build():
    summary,_=base.audit()
    cue={ (r["printed_page"],r["source_line"]):r for r in
      json.loads(base.QUE.read_text(encoding="utf-8")) if r["cue_kind"]=="NUMBERED_REQUIREMENT_CUE"}
    prior=json.loads(base.old.QUEUE.read_text(encoding="utf-8"))
    old={r["cue_id"]:r for r in prior}
    records=[]
    for p,l,track,kind,scope,premises,invalid,action in ROWS:
        orig=cue[(p,l)]
        need(orig["course_track"]==track and orig["is_official_atom"] is None,
           "numbered requirement not in current track")
        original=old[orig["cue_id"]]
        need(orig["source_line_sha256"]==original["source_line_sha256"],
           "reviewed clause source digest changed")
        records.append({"cue_id":orig["cue_id"],"course_track":track,
           "printed_page":p,"source_line":l,"source_line_sha256":orig["source_line_sha256"],
           "proposed_disposition":kind,"interpretation":scope,
           "prerequisites_or_boundaries":premises,"typical_invalid_inference":invalid,
           "human_next_action":action,"official_atom_count_effect":None,
           "teacher_review_status":"REVIEW_PENDING","teacher_signature":None,
           "student_authoritative":False})
    result={"batch":125,"numbered_requirements_reviewed_for_triage":6,
       "proposed_activities_or_competencies":len(records),
       "official_atoms_certified":0,"teacher_approved":0,
       "official_atom_denominator":None,"source_only_not_teacher_approval":True,
       "records":records}
    validate(result);return result
def validate(x):
    need(x["numbered_requirements_reviewed_for_triage"]==6
       and len(x["records"])==6 and x["official_atoms_certified"]==0
       and x["teacher_approved"]==0 and x["official_atom_denominator"] is None
       and x["source_only_not_teacher_approval"] is True,"false six-clause signoff")
    need(len({r["cue_id"] for r in x["records"]})==6,"duplicated numbered requirement")
    for rec,row in zip(x["records"],ROWS):
        p,l,track,kind,scope,premises,invalid,action=row
        need(rec["printed_page"]==p and rec["source_line"]==l and
             rec["course_track"]==track and rec["proposed_disposition"]==kind and
             rec["interpretation"]==scope and rec["prerequisites_or_boundaries"]==premises and
             rec["typical_invalid_inference"]==invalid and rec["human_next_action"]==action and
             rec["official_atom_count_effect"] is None and rec["teacher_signature"] is None and
             rec["teacher_review_status"]=="REVIEW_PENDING" and
             rec["student_authoritative"] is False,"unreviewed clause changed")
    return True
def render(x):
    s=["# Batch125｜全部6条残余编号课程要求的语义审校方案","",
       "本稿核对编号要求所在页的前后语境并原创编写教学归属建议。**六条均须真实教师确认**，没有正式排除或新增知识原子。",""]
    for r in x["records"]:
        s+=[f"## 印刷页{r['printed_page']} 行{r['source_line']} · {r['proposed_disposition']}",
          "- 解释与拆分建议："+r["interpretation"],
          "- 数学前提："+r["prerequisites_or_boundaries"],
          "- 反例/不能直接推出："+r["typical_invalid_inference"],
          "- 人工审核任务："+r["human_next_action"],""]
    s+=["## 剩余验收","", "校验标识只证明来源线索可追踪。与正式原子分母、教师审定、发布权限无关。",
        "所有6条都需要单独的专家决策和可追溯审核记录，不能机器自动关闭。",""]
    return "\n".join(s)
def main():
    ap=argparse.ArgumentParser();mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write",action="store_true");mode.add_argument("--check",action="store_true")
    a=ap.parse_args();x=build()
    for p,v in ((OUT,dump(x)),(REPORT,render(x))):
        if a.write:p.write_text(v,encoding="utf-8")
        else:need(p.exists() and p.read_text(encoding="utf-8")==v,"six requirement audit drift")
    print("Batch125 six numbered requirement packets ready: 6 pending human review, zero certified")
if __name__=="__main__":main()
