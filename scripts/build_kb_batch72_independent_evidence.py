#!/usr/bin/env python3
"""Batch72 K00/K01/K06/K07: original non-atom teaching evidence, unapproved."""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"docs/evaluation/KB_BATCH58_COMPETENCY_COVERAGE.json"
OLD=ROOT/"curriculum/highschool_math/kb_batch58_competency_assessment_drafts.json"
COVER=ROOT/"docs/evaluation/KB_BATCH72_INDEPENDENT_REQUIREMENTS.json"
LESSONS=ROOT/"knowledge/editorial_review/kb_batch72_teaching_practices.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH72_INDEPENDENT_REQUIREMENTS.md"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
# Unique authored activities, NOT reproductions of the curriculum source text.
# title, classroom activity, exact example, wrong inference, mathematical boundary, observation, near, far
GUIDANCE=[
("二次不等式图数互证","比较y=x²−3x+2的零点和三段符号，然后写严格不等式解集。",
"(3/2)²−3(3/2)+2=−1/4；x=0时值2；x=1时值0。",
"有两个零点，所以严格正值的解集是[1,2]。",
"零点是符号变化边界，严格不等式不能把零点包含进去。",
"提交符号数轴、三个代入点及端点开闭说明。",
"把抛物线改为(x−2)(x−5)，复核端点。","反转开口并说明解集改变。"),
("三维交点与投影","比较不同高度空间直线的xy投影和真实交点。",
"L1=(t,0,0)，L2=(0,s,1)；投影相交但z恒不同。",
"只要在透视图出现交点，三维直线就一定相交。",
"投影丢失高度维度，必须检验三维坐标是否同时成立。",
"交付三维参数表达式、投影图及z坐标矛盾。",
"将第二条直线移至z=2再判断。","构造一组真正相交与一组异面直线。"),
("非正交平面基底","以u=(1,0)，v=(1,1)，w=(2,3)解释非正交分解。",
"w=−u+3v，而u·v=1并非零。",
"用正交投影系数直接展开任何一组非正交基。",
"非共线保证基底但不代表正交，投影公式不能无条件套用。",
"学生给出非共线判断、线性组合和系数核对。",
"换w=(4,5)继续表示。","分析共线向量为何不能生成平面。"),
("复数表征与模长","让学生在复平面定位3+4i并解释其几何模长。",
"|3+4i|²=9+16=25，模为5，不是实部。",
"复数模长5，所以这个复数的实部等于5。",
"复平面坐标、模长和拓展三角表示的教学层级不同。",
"交坐标图、模长平方计算及共轭几何解释。",
"将实部改成−3再比较模。","解释共轭复数在复平面中的反射。"),
("异面直线的严格区分","将空间两条不同高度且不平行直线作图后提出交点检验。",
"(t,0,0)与(0,s,1)无法同时满足z坐标相同。",
"由于这两条直线方向向量不平行，所以一定存在真实三维交点。",
"在三维空间还存在既不平行也不相交的异面直线。",
"写出方向向量和联立方程，说明无法相交。",
"第二条线改z=0重新判断。","自行构造平行而不重合的空间直线。"),
("几何直观与演绎前提","用纸模型先猜线面垂直，再核对两个方向判据。",
"(1,0,0)同时垂直(0,1,0)、(0,0,1)两独立方向。",
"图上直线垂直平面里一条线，必定垂直整个平面。",
"仅一条线不足以满足线面垂直判定的完整假设。",
"学生指出两条相交的平面内方向及垂直证据。",
"更换第二方向复核。","找出垂直一条线而不垂直平面的反例。"),
("样本描述不等于总体","用合成数据1、1、7讨论采集方式、均值及推断条件。",
"三个观测的均值为3；加入100后的总体均值为109/4。",
"样本均值3就说明总体均值也严格等于3。",
"抽样机制未知时不能从有限样本认证总体事实。",
"记录合成数据来源、样本计算、两种可行总体。",
"换成1、2、6讨论同均值不同分布。","比较便利抽样与随机抽样的推断条件。"),
("有限样本点与等可能","用权重1/4和3/4的二元随机试验区分数量与概率。",
"P(H)=1/4，P(T)=3/4，样本点虽只有2个但不等可能。",
"样本空间有两个元素，所以每个元素概率必为1/2。",
"古典概型必须另外证明等可能，有限性不足以推出。",
"列出样本点、权重及古典概率能否适用。",
"换成公平硬币重复计算。","设计一个不等权抽奖并解释概率。"),
("抽样框与代表性","比较只观察1、2、3和总体另含100的情境。",
"只观察1、2、3得到均值2；四数总体均值为53/2。",
"任何三个学生的分数平均都能代表全年级。",
"抽样框和机会机制影响代表性，便利样本不可无条件推广。",
"学生提交完整抽样方案、样本所覆盖的抽样框，以及反例总体的数值核验。",
"从四个数中均匀抽一项对比期望。","设计有两个层的加权抽样方案。"),
("频率波动不是概率证明","用四次合成试验H,H,H,T区分统计频率与概率参数。",
"H在4次记录中的频率为3/4，但这不证明下一次概率等于3/4。",
"四次得到三次H，便严格确定总体P(H)=3/4。",
"随机波动及模型独立性未定时不能把频率当作已认证概率。",
"保留试验次数、生成机制、频率和推断限度。",
"改用T,T,T,H比较频率。","讨论非独立试验的频率解释风险。"),
("建模闭环与现实约束","使用单价8、变动成本5、固定成本30的自编经营模型。",
"利润为3n−30，非负整数n时最小不亏销量10。",
"算出n=10就代表真实所有商店都有同一盈亏平衡点。",
"固定成本、单价、整数销量和时间范围是模型假设。",
"交变量与单位、假设、求解、n=9反例及现实解释。",
"把单位变动成本改成6再求解。","讨论价格随销量变化时模型失效。"),
("猜想与可复核反例","组织n²+n+41素数猜想，指导从试验转向反例检索。",
"n=41时得1763=41×43，因此为合数。",
"很多小n是素数，所以所有非负整数都成立。",
"有限正例不能认证全称命题；一个合法反例足以否定。",
"交猜想量词、反例分解、计算核对、反思过程。",
"核查n=0、1、2的数值。","设计一个量词范围明确的修正猜想。"),
("研究课题过程证据","组织合成速度数据的小课题，保留选题、计划、测量、解释和汇报。",
"12 km/h行驶20分钟对应4 km，需换算时间单位。",
"一次速度乘时间的计算就等于完整研究课题。",
"课题要求来源、假设、实施记录、反证与交流过程。",
"只用匿名合成表记录阶段目标、模型、局限和汇报。",
"改25分钟检查路程。","讨论带噪声观测的单位和误差来源。"),
("科研诚信与数字演示边界","为虚拟盈亏平衡模型设计不含真人数据的结题模板。",
"8n−(30+5n)=3n−30，n=10时模型收支相抵。",
"用模拟数据就可以声称真实商家已被实地验证。",
"可复现计算、真实来源、模型解释及教师签核是不同概念。",
"教师审查合成来源声明、假设、证据链和空白反馈表。",
"换n=11检查利润。","说明真实数据采集需额外知情同意与最小化。"),
]

MATH_EXAMPLE_DIGESTS=('032b662ad59956464f212278e63889df677395434c04f707ee67813a92e1cb69', '5ce939423b6baa5495a7fce6871a26ec7c88f68fc636fd32f6c71e64efb905a9', 'ae62e1f55cdd815d4dabe639cb408bf68a9497dc71c4f5735ff6a803773cd2bc', '8bd87193643e203cf86124cc4af7c143e18c7fdab122ceec29db93c3758a9861', 'e93b1866b975c5e583b5c06157e3fc669b4abe65d7d08777597b8bb41a8ba10d', 'e21df2e81fc75e81719074db1e8616b7f0a0a32ff3219cc1909de49fc4e97d15', '7edc3bbcaae158d61329cfdb0ee2d255313226c4f116e93062071482d6fc3649', '1150332edbf15bf0af32a2290432b338785470c1cc209a39f13901b610e9ef8b', '1a2734629772c49f0d17912527777c2b139136cd5352a6dd3beb2bc178ea9d43', '0762a2b0dbd5543d3f665491ea83ca49a75ba4df1367df7040b8c4af706cecb5', 'b35bd35d461ea97b038aeb1253bfefbf56f726f543e1848c6d5532d4758fd199', 'c8e30bd969c5394d2e75043a861f03da065ef5bf3f3569f2bf145310e7eb1ce2', '0f55efc13a38ba93ac799faf09eb5d7d077da9f876d2a8f992272a19d58f33a8', '40084f1f114d441bef800a65f143150a5102237131ae23d7dd73fae205563aaa')

def need(condition,reason):
    if not condition:raise ValueError(reason)
def hash_bytes(data):return hashlib.sha256(data).hexdigest()
def digest(path):return hash_bytes(path.read_bytes())
def encode(obj):return json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+"\n"

def exact_case(i):
    if i==0:
        q=lambda x:x*x-3*x+2
        return q(F(3,2))==F(-1,4) and q(F(0))==2 and q(F(1))==0
    if i in (1,4):return F(0)!=F(1) and (1,0)!=(0,1)
    if i==2:return -1+3==2 and 3==3 and 1*1+0*1==1
    if i==3:return 3**2+4**2==25
    if i==5:return sum(a*b for a,b in zip((1,0,0),(0,1,0)))==0 and sum(a*b for a,b in zip((1,0,0),(0,0,1)))==0
    if i==6:return (F(1)+F(1)+F(7))/3==3 and (F(1)+F(1)+F(7)+F(100))/4==F(109,4)
    if i==7:return F(1,4)+F(3,4)==1 and F(1,4)!=F(1,2)
    if i==8:return (F(1)+F(2)+F(3))/3==2 and (F(1)+F(2)+F(3)+F(100))/4==F(53,2)
    if i==9:return F(3,4)!=F(1,2)
    if i in (10,13):return 8*10-(30+5*10)==0 and 8*9-(30+5*9)<0
    if i==11:return 41**2+41+41==41*43
    if i==12:return F(12)*F(20,60)==4
    raise ValueError("unsupported case")

def mac_verify_source(rows,source_dir=Path("/private/tmp")):
    """Verify 10 raw local PDFKit page SHA and 28 source-span SHA; do not export text."""
    checked=set()
    for r in rows:
        p=source_dir/f"kb56_page_{r['printed_page']}.txt"
        need(p.is_file(),"source page unavailable")
        need(digest(p)==r["source_page_pdfkit_sha256"],"source page digest mismatch")
        lines=p.read_text(encoding="utf-8").splitlines()
        m=re.fullmatch(r"P\d+-L(\d+)-(\d+)",r["source_span_id"])
        need(m is not None,"invalid line interval")
        lo,hi=map(int,m.groups())
        need(0<lo<=hi<=len(lines),"invalid source line interval")
        src="\n".join(lines[lo-1:hi]).encode()
        need(hash_bytes(src)==r["source_span_pdfkit_sha256"],"source span digest mismatch")
        checked.add(r["printed_page"])
    return len(checked)

def build(source=None,assessments=None,scenarios=None):
    source=source if source is not None else json.loads(SRC.read_text(encoding="utf-8"))
    assessments=assessments if assessments is not None else json.loads(OLD.read_text(encoding="utf-8"))
    scenarios=scenarios if scenarios is not None else GUIDANCE
    need(source["source_pdf_sha256"]=="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195","unexpected curriculum source PDF version")
    rows=source["rows"]
    need(len(rows)==28 and len({x["source_candidate_id"] for x in rows})==28,"28 unique spans required")
    kinds=Counter(x["source_kind"] for x in rows)
    need(kinds=={"TEACHING_GUIDANCE":14,"ACHIEVEMENT_REQUIREMENT":11,"ACTIVITY_REQUIREMENT":3},"incorrect source category distribution")
    need(len(scenarios)==14,"14 distinct pedagogical designs required")
    existing={x["draft_id"]:x for x in assessments["items"]}
    need(len(existing)==14,"legacy 14 achievement/activity drafts missing")
    result=[];lesson_rows=[];index=0
    for row in rows:
        for key in ("source_page_pdfkit_sha256","source_span_pdfkit_sha256"):
            s=row[key]
            need(isinstance(s,str) and len(s)==64 and all(ch in "0123456789abcdef" for ch in s),"malformed source SHA")
        need(row["curriculum_track"]=="COMPULSORY" and row["review"]=="REVIEW_PENDING" and row["teacher_approved"] is False and row["student_publishable"] is False,"source track/review tamper")
        entry={k:row[k] for k in ("source_candidate_id","source_kind","printed_page","source_span_id","source_page_pdfkit_sha256","source_span_pdfkit_sha256","original_scope_paraphrase")}
        entry.update(source_pdf_sha256=source["source_pdf_sha256"],track_hint_not_authoritative="COMPULSORY",coverage_status="UNMAPPED",
                     candidate_alignment="UNVERIFIED",full_clause_teacher_review="NOT_DONE",
                     official_atom_membership="NONATOM_SOURCE_SPAN",teacher_review="REVIEW_PENDING",
                     teacher_signature=None,student_publishable=False,formal_proof_certified=False,
                     verified_student_steps=0)
        if row["source_kind"]=="TEACHING_GUIDANCE":
            title,activity,example,wrong,boundary,observed,near,far=scenarios[index]
            need(all(isinstance(x,str) and len(x)>=5 for x in (title,activity,example,wrong,boundary,observed,near,far)) and all(len(x)>=18 for x in (activity,example,wrong,boundary,observed)),"incomplete teacher protocol")
            need(hash_bytes(example.encode())==MATH_EXAMPLE_DIGESTS[index],"math case text changed without independent revalidation")
            need(exact_case(index),"finite rational witness false")
            pid=f"KB72-TEACH-{index+1:02}"
            item={"id":pid,"type":"TEACHING_ACTION","source_candidate_id":row["source_candidate_id"],
                  "title":title,"student_task_proposal":activity,
                  "bounded_math_example":example,
                  "teacher_procedure":[
                    "提问、对象与已知条件辨识："+activity,
                    "让学生独立记录推测及所用数学条件。",
                    "结合精确有限实例核验条件："+example,
                    "反思错误推断及适用边界："+boundary],
                  "typical_wrong_claim":wrong,"error_reason":boundary,
                  "observable_anonymized_evidence":observed,
                  "three_stage_hints":[
                    "先识别问题目标和给定对象，不直接揭晓结果。",
                    "列出需要满足的定义域、结构和模型前提。",
                    "尝试边界反例，教师侧再进行完整解析。"],
                  "near_transfer":near,"far_transfer":far,
                  "rubric":[{"criterion":"识别任务对象、条件和证据来源","points":2},
                           {"criterion":"使用数学条件和反例核查推理","points":2},
                           {"criterion":"明确适用边界并提供可复核观察","points":2}],
                  "score_total":6,"source_license":"PROJECT_AUTHORED",
                  "math_verification":"FINITE_EXACT_CASE_ONLY",
                  "teacher_solution_visibility":"TEACHER_ONLY",
                  "teacher_review":"REVIEW_PENDING","teacher_signature":None,
                  "student_publishable":False,"general_proof_certified":False,
                  "observation_form":{"synthetic_only":True,"student_identifier":None,
                                     "student_response":None,"teacher_observation":None,
                                     "teacher_signoff":None}}
            entry.update(candidate_evidence_id=pid,evidence_kind="UNVERIFIED_TEACHER_OBSERVATION_PROTOCOL")
            lesson_rows.append(item);index+=1
        else:
            ids=row["teacher_only_assessment_draft_ids_not_verified"]
            need(len(ids)==1 and ids[0] in existing,"missing independent assessment draft")
            a=existing[ids[0]]
            need(a["source_candidate_id"]==row["source_candidate_id"] and a["review_status"]=="REVIEW_PENDING" and a["teacher_solution_visibility"]=="TEACHER_ONLY" and not a["student_published"],"legacy assessment source/status mismatch")
            entry.update(candidate_evidence_id=ids[0],evidence_kind="EXISTING_UNVERIFIED_ASSESSMENT_PROPOSAL")
        result.append(entry)
    need(index==14 and len(lesson_rows)==14,"missing original guidance items")
    coverage={"schema_version":"kb72-independent-nonatom-source-proposals-v1",
      "source_ledger_sha256":digest(SRC),"legacy_assessments_sha256":digest(OLD),
      "source_span_count":28,"source_kind_counts":dict(kinds),
      "linked_assessment_proposals":14,"new_teaching_protocol_drafts":14,
      "candidate_evidence_links":28,"verified_requirement_coverage":0,
      "official_atom_denominator":{t:None for t in TRACKS},
      "source_text_not_embedded":True,"teacher_approved":0,"student_published":0,
      "general_proof_certified":0,"records":result}
    lesson_data={"schema_version":"kb72-teacher-guidance-v1","source_license":"PROJECT_AUTHORED",
      "student_data_included":False,"items":lesson_rows}
    lines=["# Batch72｜独立课程学业/活动/教学要求证据草案","",
      "课标局部来源：印刷页18–36的28个已有来源跨度，均为必修课标的非知识原子类要求。",
      "14项学业或活动要求链接已有教师侧测评提案；14项教学建议新增原创可观察教学方案。",
      "28/28表示待教师审核的独立证据提案可追溯，不代表能力覆盖认证：**认证数为0**。",
      "10页Mac PDFKit页面及28个来源跨度可按SHA重算；整页和教师全文审核仍为0。未提交版权原文或真实学生数据。",
      "十四项教学设计各含4步教学活动、数学有限实例、错误推断与反例、3级提示、近远迁移、6分评价量规。",
      "七轨官方知识原子分母全为null，数学一般证明认证0，教师批准0，学生发布0。",
      "","| 来源片段 | 类型 | 证据候选 | 认证状态 |","|---|---|---|---|"]
    lines += [f"| {r['source_candidate_id']} | {r['source_kind']} | {r['candidate_evidence_id']} | UNMAPPED |" for r in result]
    lines += ["","## 安全与下批审查","",
      "不能把候选对应、局部SHA一致、CI通过、有限实例，宣称为真实课程能力已覆盖。",
      "候选教学方案是供真实教师观察及签核的空白计划，完整解析仍为TEACHER_ONLY。",
      "下一批优先校核完整连续条款、跨页等价去重并扩展至选择性必修和选修A–E；538未认证步骤和10项冲突保持开放。",""]
    return coverage,lesson_data,"\n".join(lines)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local-source",action="store_true")
    p.add_argument("--source-dir",type=Path,default=Path("/private/tmp"))
    opt=p.parse_args()
    cov,lesson,doc=build()
    if opt.verify_local_source:
        n=mac_verify_source(json.loads(SRC.read_text(encoding="utf-8"))["rows"],opt.source_dir)
        print("MAC_SOURCE_PAGES_VERIFIED=",n,"SOURCE_SPANS_VERIFIED=28")
    for dest,text in ((COVER,encode(cov)),(LESSONS,encode(lesson)),(REPORT,doc)):
        if opt.check:
            need(dest.exists() and dest.read_text(encoding="utf-8")==text,"generated artifact drift: "+str(dest))
        else:
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding="utf-8")
    print("KB72 PASS: 28 tentative source-evidence links, 14 teaching drafts; coverage verified=0")
if __name__=="__main__":main()
