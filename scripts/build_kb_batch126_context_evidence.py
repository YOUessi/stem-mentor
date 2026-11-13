#!/usr/bin/env python3
"""Batch126: 26 manually interpreted, source-locked syllabus *context* dossiers.

Reviewing a passage is not verifying the mathematical theorem, assigning an
official atom or obtaining a teacher signature. Original PDF text stays on Mac.
The public JSON contains author-written summaries and SHA-256 attestations.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch125_provenance as previous

DEST = ROOT / "docs/evaluation"
OUT = DEST / "KB_BATCH126_CONTEXT_EVIDENCE.json"
REPORT = DEST / "KB_BATCH126_CONTEXT_REVIEW.md"
LOCKS = ROOT / "curriculum/highschool_math/k00_batch126_source_line_locks.json"
TRACKS = {"COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A", "ELECTIVE_B",
          "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E"}
RELATIONS = {
    "NUMBERED_NEIGHBOR_PARTIAL", "OPTIONAL_NUMBERED_ACTIVITY", "DIRECT_TEXT_AXIOM",
    "DIRECT_TEXT_THEOREM", "GENERAL_PARAGRAPH_PARTIAL", "TEACHING_GUIDANCE_ONLY",
    "CROSS_PAGE_CONTINUATION", "TEXT_INSUFFICIENT_VISUAL_REQUIRED",
    "RESEARCH_ACTIVITY_NOT_ATOMIZED", "NUMBERED_COMPETENCY_NOT_ATOMIZED",
    "NUMBERED_APPLICATION_NOT_ATOMIZED",
}
# (candidate/cue, page, first source line, last source line,
#  provenance class, project-authored source interpretation, remaining semantic gap)
# These annotations were composed after reading the local authorized original,
# NOT machine-certified paraphrases or one-to-one official atom declarations.
SPECS = [
 ("hs-semantic-pilot-119-c02",27,9,10,"NUMBERED_NEIGHBOR_PARTIAL",
  "相邻要求涉及复数代数表示的四则运算及加减运算的几何意义。",
  "小节标题本身不能证明具体除法分母条件已被逐条教研确认。"),
 ("hs-semantic-pilot-119-s01",38,12,13,"NUMBERED_NEIGHBOR_PARTIAL",
  "数列章节的正文说明数列属于特殊函数，并列举数列表示方式。",
  "将数列定义域一律写作全部正整数会忽略有限数列及不同起始下标。"),
 ("hs-semantic-pilot-119-s06",38,29,30,"OPTIONAL_NUMBERED_ACTIVITY",
  "带星号的归纳法方向要求理解原理并处理简单的数列命题。",
  "标星内容不应无条件混入全国选择性必修最低门槛；证明起点与归纳步仍待教师检查。"),
 ("hs-semantic-pilot-120-s112",46,22,26,"NUMBERED_NEIGHBOR_PARTIAL",
  "相邻计数要求包括分类分步计数、排列组合及其计数公式推导。",
  "该区间含多项要求，不能合并认作一个知识原子，也不能代替条件完整推导。"),
 ("hs-semantic-pilot-123-c408",21,19,20,"NUMBERED_NEIGHBOR_PARTIAL",
  "相邻三角函数要求包括弧度制及角度弧度的互相换算。",
  "弧长与物理量纲属于展开讲解，不能仅用小节名证明其全部细节。"),
 ("hs-semantic-pilot-123-c410",22,28,30,"NUMBERED_NEIGHBOR_PARTIAL",
  "相邻要求涵盖零点存在判断与二分法的求解思路。",
  "二分法算法收敛须额外验证连续性与异号端点，源行未授权遗漏前提。"),
 ("hs-semantic-pilot-123-s401",42,22,23,"NUMBERED_NEIGHBOR_PARTIAL",
  "相邻要求含空间向量基本定理、正交分解及坐标表示。",
  "唯一性证明需要基向量线性无关；不能用小节标题代替该假设。"),
 ("hs-semantic-pilot-123-s403",47,21,22,"NUMBERED_NEIGHBOR_PARTIAL",
  "相邻要求涉及离散型随机变量、分布列及数字特征。",
  "非负与归一条件须独立核查；一段要求往往对应多个概念。"),
 ("hs-semantic-pilot-123-s405",48,11,13,"NUMBERED_NEIGHBOR_PARTIAL",
  "相邻要求涉及样本相关系数、标准化数据夹角及多组数据比较。",
  "异常值敏感性没有从这几行得到完整直接结论，必须另标作者扩展。"),
 ("hs-semantic-pilot-123-s406",47,28,28,"NUMBERED_NEIGHBOR_PARTIAL",
  "相邻要求介绍正态分布及其误差背景。",
  "标准化必须假设标准差严格为正；不能将相关公式直接视作已通过来源审查。"),
 ("hs-semantic-pilot-119-c03",28,8,8,"DIRECT_TEXT_AXIOM",
  "基本事实陈述三个非共线点确定唯一平面。",
  "直接数学陈述已找到，但独立公理与定理证明不能混淆，教师尚未审核。"),
 ("hs-semantic-pilot-119-c04",28,9,10,"DIRECT_TEXT_AXIOM",
  "基本事实讨论直线上两点在同一平面时整条直线的包含关系。",
  "需明确讨论的是该直线上全部点；数学事实不是数值见证可证明的。"),
 ("hs-semantic-pilot-119-c05",28,11,12,"DIRECT_TEXT_AXIOM",
  "基本事实限定两个不重合平面有共同点时的公共直线。",
  "忽略平面不重合会产生无数公共直线的反例。"),
 ("hs-semantic-pilot-119-c07",31,6,8,"GENERAL_PARAGRAPH_PARTIAL",
  "概率章节概述有限样本空间、随机事件及古典概率。",
  "概述不自动证明等可能前提；需结合后文条件和事件定义审查。"),
 ("hs-semantic-pilot-119-c08",33,6,10,"TEACHING_GUIDANCE_ONLY",
  "教学提示强调古典概型的有限性、等可能性与列表树图。",
  "教学提示不等于独立编号课程原子，且不能用有限性替代等可能性。"),
 ("hs-semantic-pilot-119-c09",35,9,13,"TEXT_INSUFFICIENT_VISUAL_REQUIRED",
  "文本片段描述数学探究活动，不足以证实建模验证失败后的回退循环。",
  "回退循环需要第35页原始流程图视觉复核，不能靠PDFKit控制字符或探究段落伪证。"),
 ("hs-semantic-pilot-119-ec02",65,1,1,"CROSS_PAGE_CONTINUATION",
  "本页首行承接前页充分必要条件段落，必须跨页阅读。",
  "不核查前一页第64页末段就不能认定完整命题及其选修C归属。"),
 ("hs-semantic-pilot-119-ec06",65,19,23,"GENERAL_PARAGRAPH_PARTIAL",
  "选修C的数学模型专题讨论经济社会模型及参数背景。",
  "课程示例不证明某个现实经济模型有效，仍需变量单位和适用域的单独验证。"),
 ("hs-semantic-pilot-120-c109",28,19,20,"DIRECT_TEXT_THEOREM",
  "教学范围给出线面平行与辅助平面交线平行的空间性质。",
  "使用时必须保证辅助平面确实相交、所给直线不落在原平面。"),
 ("hs-semantic-pilot-120-c110",28,21,22,"DIRECT_TEXT_THEOREM",
  "教学范围给出两平行平面被第三平面截得平行交线的性质。",
  "两个截线必须存在，不能省略第三平面分别与二平面相交的前提。"),
 ("syllabus-cue-fa79a32fcccf7f814533",21,6,7,"RESEARCH_ACTIVITY_NOT_ATOMIZED",
  "带星号的对数史资料阅读与写作任务，属于可选研学活动。",
  "待教师决定是否登记教学活动，不能自动计算为必修数学定理。"),
 ("syllabus-cue-e26ca752fcfbb29bdebf",23,9,11,"RESEARCH_ACTIVITY_NOT_ATOMIZED",
  "真实函数模型材料收集与参数意义讨论，属于应用探究活动。",
  "可产生建模任务但未对应独立固定数学命题，原先非原子判断仍待教师裁决。"),
 ("syllabus-cue-3042834dd2faa78d959c",29,9,9,"NUMBERED_COMPETENCY_NOT_ATOMIZED",
  "编号要求强调使用已有结论证明简单空间位置关系命题。",
  "它是证明能力范围而不是唯一的特定定理；需要映射多个题族。"),
 ("syllabus-cue-afc6ea0759e9a1f4ea48",32,18,20,"NUMBERED_APPLICATION_NOT_ATOMIZED",
  "抽样方法选择要求学生根据简单现实情境设计合适抽样。",
  "对应抽样方法决策题族而非单独固定公式，需要先修与任务拆分。"),
 ("syllabus-cue-f16fb54272cc33b9200f",32,29,29,"NUMBERED_APPLICATION_NOT_ATOMIZED",
  "统计要求强调用样本估计总体取值规律。",
  "应用能力范围较广，需拆成方法和具体条件，不可直接作为一个原子分母。"),
 ("syllabus-cue-7836cdcac3c80b03c51a",44,16,16,"NUMBERED_COMPETENCY_NOT_ATOMIZED",
  "编号要求是学习圆锥曲线后体会数形结合思想。",
  "属于横贯主题的数学思维目标，不能冒充具完整假设结论的定理。"),
]
def require(value,why):
    if not value: raise ValueError(why)
def serial(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def source_pages():
    from build_kb_batch118_source_atom_ledger import source_pages as load
    return {r["printed_page"]:r["lines"] for r in load()}
def source_locks():
    require(LOCKS.is_file(),"missing locked source attestations")
    return json.loads(LOCKS.read_text(encoding="utf-8"))
def freeze_locks():
    pages=source_pages()
    result={}
    for key,page,lo,hi,_,_,_ in SPECS:
        lines=pages[page]
        require(1<=lo<=hi<=len(lines),"invalid source excerpt")
        result[key]={
          "printed_page":page,"from_line":lo,"to_line":hi,
          "source_line_sha256":[hashlib.sha256(s.encode("utf-8")).hexdigest()
                                 for s in lines[lo-1:hi]],
          "source_span_sha256":hashlib.sha256("\n".join(lines[lo-1:hi]).encode("utf-8")).hexdigest(),
        }
    return result
def audit(*,verify_local_source=False):
    old,residual=previous.audit()
    original,queue,base=previous.originals()
    cand={r["id"]:r for r in original}
    gaps={r["cue_id"]:r for r in queue if not r["linked_candidate_ids"]}
    locks=source_locks()
    require(set(locks)=={r[0] for r in SPECS} and len(SPECS)==26,"26-case lock mismatch")
    if verify_local_source:require(locks==freeze_locks(),"Mac PDFKit source passages changed")
    all_markers={m["editorial_marker_id"]:m for m in base["markers"]}
    grade={r["candidate_id"]:r["evidence_grade"] for r in old["records"]}
    result=[]
    for key,page,lo,hi,relation,interpretation,concern in SPECS:
        require(relation in RELATIONS and len(interpretation)>=16 and len(concern)>=20,
                "missing substantive human editorial judgement")
        require(key in cand or key in gaps,"unknown source candidate/cue")
        reference=cand.get(key,gaps.get(key))
        track=reference["course_track"]
        require(track in TRACKS and previous.old.previous.base_scope.evidence.track_at(page,lo)==track,
                "source track was changed")
        require(all(previous.old.previous.base_scope.evidence.track_at(page,i)==track
                    for i in range(lo,hi+1)),"context crosses course boundary")
        att=locks[key]
        require(att["printed_page"]==page and att["from_line"]==lo and att["to_line"]==hi
                and len(att["source_line_sha256"])==hi-lo+1
                and all(len(h)==64 for h in att["source_line_sha256"])
                and len(att["source_span_sha256"])==64,"source lock invalid")
        marker=all_markers.get(key)
        if key in cand:
            src=cand[key]["source"]
            require(page==src["printed_page"],"candidate context from different printed page")
            require(grade[key] in {"HEADING_OR_SUBTOPIC_ONLY_REQUIRES_CLAUSE",
                    "NO_LAYOUT_MARKER_ALTERNATE_EVIDENCE_REVIEW"},"inappropriate evidence upgrade")
            kind="EDITORIAL_CANDIDATE"
            original_grade=grade[key]
        else:
            require(gaps[key]["cue_kind"]=="NUMBERED_REQUIREMENT_CUE",
                    "residual is not a numbered requirement")
            kind="UNLINKED_NUMBERED_CUE"
            original_grade="UNLINKED_NUMBERED_REQUIREMENT"
            require(marker is not None and marker["printed_page"]==page
                    and lo<=marker["source_line"]<=hi,"cue source mismatch")
        result.append({"id":key,"entry_kind":kind,"track":track,"page":page,
          "line_range":[lo,hi],"source_attestation":att,
          "previous_grade":original_grade,"context_relation":relation,
          "editorial_interpretation":interpretation,"unresolved_risk":concern,
          "original_pdf_sha256":previous.old.previous.base_scope.evidence.PDF_SHA,
          "human_semantic_check":"EDITORIAL_ONLY_NOT_TEACHER_CERTIFIED",
          "math_proof_certified":False,"official_atom_id":None,
          "teacher_status":"REVIEW_PENDING","student_authoritative":False,
          "teacher_signature":None})
    counts=collections.Counter(r["context_relation"] for r in result)
    proposed={
      "batch":126,"source_reviewed_entries":26,
      "source_reviewed_editorial_proposals":20,"source_reviewed_residual_numbered_cues":6,
      "source_pdf_sha256":previous.old.previous.base_scope.evidence.PDF_SHA,
      "previous_239_candidates":239,"previous_135_residual_cues":135,
      "remaining_untouched_candidate_count":219,
      "full_official_atomic_denominator":None,
      "per_track_official_atomic_denominator":{t:None for t in sorted(TRACKS)},
      "teacher_approved":0,"student_authoritative":0,
      "provenance_not_formal_proof":True,"source_text_embedded":False,
      "case_classes":dict(sorted(counts.items())),
      "records":result,
    }
    validate(proposed)
    return proposed

def validate(data):
    require(data["batch"]==126 and data["source_reviewed_entries"]==26 and
            data["source_reviewed_editorial_proposals"]==20 and
            data["source_reviewed_residual_numbered_cues"]==6 and
            data["remaining_untouched_candidate_count"]==219 and
            data["previous_239_candidates"]==239 and data["previous_135_residual_cues"]==135,
            "coverage inflation")
    require(data["full_official_atomic_denominator"] is None and
            data["per_track_official_atomic_denominator"]=={t:None for t in sorted(TRACKS)}
            and data["teacher_approved"]==data["student_authoritative"]==0 and
            data["provenance_not_formal_proof"] is True
            and data["source_text_embedded"] is False,"authority or denominator forged")
    require(len(data["records"])==26 and len({x["id"] for x in data["records"]})==26,
            "missing or duplicated review")
    for r in data["records"]:
        require(r["context_relation"] in RELATIONS and
                r["human_semantic_check"]=="EDITORIAL_ONLY_NOT_TEACHER_CERTIFIED"
                and r["teacher_status"]=="REVIEW_PENDING"
                and r["math_proof_certified"] is False and
                r["student_authoritative"] is False and
                r["teacher_signature"] is None and r["official_atom_id"] is None,
                "unapproved source evidence was promoted")
    require(dict(collections.Counter(r["context_relation"] for r in data["records"]))==
            data["case_classes"],"review classification count forged")
    # Audit annotations and hashes must not be editable without explicit source
    # refreezing and a new review. This is an editorial lock, not teacher approval.
    expectations={row[0]:row for row in SPECS}
    pinned=source_locks()
    sources,residual,_=previous.originals()
    track_by_id={x["id"]:x["course_track"] for x in sources}
    track_by_id.update({x["cue_id"]:x["course_track"] for x in residual
                        if not x["linked_candidate_ids"]})
    grade_by_id={x["candidate_id"]:x["evidence_grade"]
                 for x in previous.audit()[0]["records"]}
    require(set(pinned)==set(expectations),"source evidence lock set altered")
    for record in data["records"]:
        key=record["id"]
        require(key in expectations,"unknown editorial case")
        _,page,lo,hi,relation,interpretation,concern=expectations[key]
        require(record["page"]==page and record["line_range"]==[lo,hi]
                and record["context_relation"]==relation
                and record["editorial_interpretation"]==interpretation
                and record["unresolved_risk"]==concern
                and record["source_attestation"]==pinned[key]
                and record["original_pdf_sha256"]==previous.old.previous.base_scope.evidence.PDF_SHA,
                "authored evidence or source hash changed")
        require(record["entry_kind"]==("UNLINKED_NUMBERED_CUE" if key.startswith("syllabus-cue-")
                else "EDITORIAL_CANDIDATE"),"review ID type changed")
        require(record["track"]==track_by_id[key] and
                record["previous_grade"]==grade_by_id.get(key,"UNLINKED_NUMBERED_REQUIREMENT"),
                "candidate/track source lineage changed")
    require(sum(r["entry_kind"]=="EDITORIAL_CANDIDATE" for r in data["records"])==20,
            "candidate count changed")
    return True

def report(data):
    out=["# Batch126｜26项课标上下文语义审查（非教师批准）","",
       "在Mac授权原件中逐条查看对应源码行；仅将原创语义判断、页行号与SHA-256写入仓库，不转载课标段落。",
       "**这是一份人工编写的项目候审记录，不是教师审查或形式数学证明。**",
       "上一批239候选仅分来源强度；本批核对20个候选（其中10个此前无布局marker）及6个仍未关联编号要求。",
       "其余219项候选未在本批逐行解释，不得把26/26写成全部课程覆盖率。",
       "正式课程原子分母仍UNKNOWN，正式教师批准0，学生权威发布0。","",
       "## 已审的来源上下文与数学边界","",
       "|ID|课标范围及页行|证据类型|仍需核查|",
       "|---|---|---|---|"]
    for r in data["records"]:
        out.append("|"+r["id"]+"|"+r["track"]+f" p{r['page']} L{r['line_range'][0]}–{r['line_range'][1]}"+
                   "|"+r["context_relation"]+"|"+r["unresolved_risk"]+"|")
    out+=["","## 验收边界","",
       "- source-line 哈希证明使用了锁定的PDFKit抽取文本；不能取代公式、跨页、流程图的原始图片审查。",
       "- 对第35页回退循环、选修C跨页条件、可选星号归纳法保留明确的未完成证据标签。",
       "- 6项未关联编号要求尚未删除或变成官方知识原子，活动/能力/应用的拆分等待教师审核。",
       "- 这些候审内容继续TEACHER_ONLY/REVIEW_PENDING，不进入学生权威RAG或直接公开完整答案。",""]
    return "\n".join(out)

def main():
    cli=argparse.ArgumentParser();m=cli.add_mutually_exclusive_group(required=True)
    m.add_argument("--write",action="store_true");m.add_argument("--check",action="store_true")
    cli.add_argument("--freeze-source",action="store_true")
    cli.add_argument("--verify-local-source",action="store_true")
    args=cli.parse_args()
    if args.freeze_source:
        require(args.write and args.verify_local_source,
                "source freeze requires explicit Mac full-source verification")
        LOCKS.write_text(serial(freeze_locks()),encoding="utf-8")
    obj=audit(verify_local_source=args.verify_local_source)
    for p,s in ((OUT,serial(obj)),(REPORT,report(obj))):
        if args.write:p.write_text(s,encoding="utf-8")
        else:require(p.is_file() and p.read_text(encoding="utf-8")==s,
                     "context evidence output drift: "+str(p))
    print("Batch126",len(obj["records"]),"source-locked editorial reviews;",
          "official atomic denominators UNKNOWN; approvals zero")

if __name__=="__main__": main()
