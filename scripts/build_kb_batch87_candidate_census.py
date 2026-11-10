#!/usr/bin/env python3
"""Preliminary 7-track curriculum candidate census, NOT an official atom denominator.

Across 428 PDFKit source anchors, 300 proposed teacher-split labels exist;
exact-string uniqueness never certifies mathematical non-equivalence.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_kb_batch87_semantic_review as S
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"docs/evaluation/KB_BATCH87_PROVISIONAL_ATOM_CENSUS.json"
MD=ROOT/"docs/evaluation/KB_BATCH87_PROVISIONAL_ATOM_CENSUS.md"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A",
        "ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
def require(ok,msg):
    if not ok:raise ValueError(msg)
def dump(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2)+"\n"
def build(editorial=None,teacher=None,allrows=None):
    import build_kb_batch87_math_lessons as M
    editorial=S.build() if editorial is None else editorial
    teacher=M.build() if teacher is None else teacher
    require(editorial["source_review_denominator"]==428
        and editorial["cumulative_editorial_count"]==428
        and editorial["pending_editorial_count"]==0
        and editorial["official_curriculum_atom_denominator"] is None
        and editorial["teacher_approved"]==0
        and teacher["teacher_approvals"]==0 and teacher["student_releases"]==0,
        "coverage or teacher authority spoof")
    if allrows is None:
        b=S.B86
        allrows=b.B85.B84.B83.B81.build()["rows"]+[
            r for module in (b.B85.B84.B83,b.B85.B84,b.B85,b,S)
            for r in module.build()["new_rows"]]
    require(len(allrows)==428
        and len({r["review_id"] for r in allrows})==428,
        "missing/duplicated source anchors across batches")
    queue=S.load(S.B86.B85.B84.B83.B81.SOURCE)["anchor_review_queue"]
    origin={r["review_id"]:r for r in queue}
    require({r["review_id"] for r in allrows}==set(origin),"source identity drift")
    topics=[];exact=defaultdict(list);by_track=Counter();by_role=Counter()
    for r in allrows:
        rid,tr=r["review_id"],r["track"]
        require(tr in TRACKS and tr==origin[rid]["track"]
                and r["source_line_sha256"]==origin[rid]["source_line_sha256"]
                and r["official_atom_count"] is None
                and r.get("teacher_approved") is False
                and r.get("student_publishable") is False,
                "source SHA or fake official teacher approval")
        by_role[r["semantic_role_provisional"]]+=1
        units=r["possible_math_units_for_teacher_split"]
        require(type(units) is list and len(units)<=5,"not a valid candidate list")
        if r["semantic_role_provisional"]=="CURRICULUM_HEADING":
            require(units==[],"heading promoted to official topic")
        for idx,title in enumerate(units,1):
            require(type(title) is str and len(title)>=3,"invalid math topic")
            key=(tr,title)
            exact[key].append(rid)
            topics.append({"candidate_id":f"{rid}-C{idx:02}",
                "track":tr,"source_review_id":rid,
                "printed_page":origin[rid]["printed_page"],
                "source_line_sha256":origin[rid]["source_line_sha256"],
                "provisional_topic":title,
                "cross_track_equivalence":"NOT_ADJUDICATED",
                "cross_page_equivalence":"NOT_ADJUDICATED",
                "official_math_atom_id":None,
                "prerequisite_graph_review":"NOT_EVALUATED",
                "complete_teacher_lesson_approved":False,
                "student_publishable":False})
            by_track[tr]+=1
    require(len(topics)==300 and len(exact)==300
        and len({t["candidate_id"] for t in topics})==300
        and dict(by_track)=={
            "COMPULSORY":75,"SELECTIVE_COMPULSORY":66,
            "ELECTIVE_A":60,"ELECTIVE_B":60,
            "ELECTIVE_C":31,"ELECTIVE_D":8},
        "provisional math labels drift; do not inflate official denominator")
    require(dict(by_role)=={
        "MATHEMATICAL_REQUIREMENT":187,"CURRICULUM_HEADING":155,
        "APPLICATION_CONTEXT":33,"MIXED_CLAUSE":30,
        "COMPETENCY_REQUIREMENT":23}, "source roles changed")
    teacherids={c["source_review_id"] for c in teacher["cards"]}
    require(len(teacherids)==7 and teacherids<={t["source_review_id"] for t in topics},
            "guarded lessons lack source mathematical candidate")
    per={}
    for tr in TRACKS:
        per[tr]={"source_anchor_denominator":editorial["by_track"][tr]["source_anchor_denominator"],
                "source_anchor_editorials":editorial["by_track"][tr]["original_editorial_coverage"],
                "provisional_label_occurrences":by_track[tr],
                "exact_string_unique_labels":sum(x[0]==tr for x in exact),
                "mathematically_adjudicated_unique_atom_denominator":None,
                "approved_complete_deep_lessons":0,
                "teacher_reviewed_full_pages":0,
                "student_published_atoms":0}
    return {"schema_version":"kb87-full-source-provisional-seven-track-census-v1",
      "standard_version":editorial["standard_version"],
      "source_pdf_sha256":editorial["source_pdf_sha256"],
      "source_queue_sha256":editorial["source_queue_sha256"],
      "source_review_anchors":428,"source_editorials_completed":428,
      "source_editorials_missing":0,"source_role_counts":dict(by_role),
      "provisional_topic_label_occurrences":len(topics),
      "exact_string_distinct_label_count":len(exact),
      "semantic_equivalence_adjudicated_count":0,
      "official_curriculum_atom_denominator":None,
      "total_full_page_teacher_atomizations":0,
      "teacher_approved_complete_lessons":0,
      "student_published_deep_lessons":0,
      "new_source_linked_teacher_drafts":len(teacherids),
      "new_source_linked_teacher_draft_ids":sorted(teacherids),
      "not_an_official_atom_count":True,
      "by_track":per,"provisional_candidates":topics}
def markdown(d):
    lines=["# Batch87｜七轨课程候选分母预审：来源锚点≠数学知识原子","",
      "已完成428/428条PDFKit来源锚点的项目原创解释；**不等于正式课程全覆盖**。",
      "初步从这些条目得到300个待去重的数学教学主题标签：恰好300个文字唯一标签，",
      "但**跨页/跨轨的数学同义、适用域差异、上下位关系尚未判定**，所以不能宣布300个正式知识原子。",
      "不同能力/活动要求不是数学定理；155个课程标题并非独立数学原子。",
      "所有轨道的官方数学知识原子分母均为null；教师完整逐页审核0/61；批准/正式学生发布0。","",
      "| 轨道 | 来源锚点 | 原创释义 | 暂定数学主题标签 | 数学审核后原子分母 | 已批准完整讲义 |",
      "|---|---:|---:|---:|---|---:|"]
    for tr,v in d["by_track"].items():
        lines.append(f'| {tr} | {v["source_anchor_denominator"]} | {v["source_anchor_editorials"]} | {v["provisional_label_occurrences"]} | 未知 | 0 |')
    lines+=["",f'本批7份新增教师审稿讲义均挂接于来源锚点：{", ".join(d["new_source_linked_teacher_draft_ids"])}。',
            "该数量不是已有全项目讲义的正式覆盖率，需独立教师审核和来源等价裁决。","",
            "## 待教师裁决事项","",
            "1. 每个数学主题在必修、选择性必修、选修A–E中是否语义重复、进阶还是额外范围。",
            "2. 将混合型条款按概念/定理/方法/题族拆分；确定先修图并审计遗漏。",
            "3. 对每个正式原子审核定义、完整条件、逐步证明、反例、解题与提示及版权来源。",
            "4. 教师审定分母并签字之前保留null，学生端仅可访问真正已审定内容。",""]
    return "\n".join(lines).rstrip("\n")+"\n"
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    args=p.parse_args();x=build()
    for path,value in ((OUT,dump(x)),(MD,markdown(x))):
        if args.check:require(path.is_file() and path.read_text(encoding="utf8")==value,"candidate census output drift")
        else:path.write_text(value,encoding="utf8")
    print("Batch87 provisional curriculum census: 428 source anchors; 300 UNADJUDICATED topic labels; official math atoms UNKNOWN; approved=0")
if __name__=="__main__":main()
