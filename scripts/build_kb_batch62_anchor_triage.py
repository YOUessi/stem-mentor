#!/usr/bin/env python3
"""Curated, source-hash-locked triage for all 56 previously unlinked anchors.

The manual editorial notes are ORIGINAL paraphrases, NOT copied syllabus text.
The classification is *not* an official atom denominator or teacher approval.
CLI --verify-local-source accepts local Mac PDFKit text files, never commits them.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import build_kb_batch61_requirement_anchors as B61

ROOT = Path(__file__).resolve().parents[1]
CUR = ROOT / "curriculum/highschool_math"
DOC = ROOT / "docs/evaluation"
SOURCE = DOC / "KB_BATCH61_UNLINKED_ANCHOR_REVIEW_QUEUE.csv"
OUT = CUR / "k00_batch62_unlinked_anchor_triage.json"
REPORT = DOC / "KB_BATCH62_ANCHOR_TRIAGE.md"
NONATOM = DOC / "KB_BATCH62_NONATOM_REQUIREMENTS.json"

# Key = (printed page, PDFKit line).
# The first item describes a possible future source unit; the second is a
# condition/boundary requiring mathematical inspection, not a certified proof.
OBJECTIVES = {
 (15,10): ("集合及元素属于关系", "区分对象属于集合与集合包含关系；定义集合时必须给出判定范围"),
 (15,15): ("子集与集合相等", "包含允许等号；真子集才要求两集合不相等"),
 (15,17): ("并集、交集与补集", "补集依赖明确的全集；空集与全集需作边界测试"),
 (16,7): ("必要、充分及充要条件", "区分命题方向，逆命题不自动成立"),
 (16,14): ("全称量词与存在量词", "量词必须有论域；改变论域可改变真值"),
 (16,16): ("量词命题的否定", "否定全称要换存在且否定谓词，不能只改谓词"),
 (16,24): ("等式与不等式的合法变形", "不等式同乘负数必须反向；同除量先证明非零"),
 (16,26): ("基本不等式", "仅适用非负实数；等号一般要求两数相等"),
 (17,9): ("二次方程实根与函数零点", "最高次系数非零；判别式区分无实根与重根"),
 (17,12): ("一元二次不等式求解", "开口方向、根重数和严格/非严格不等号都影响解集"),
 (19,13): ("函数定义与表示", "同一对应关系必须有明确非空定义域及每个输入的唯一输出"),
 (19,21): ("函数单调性与极值", "单调区间不可跨越定义域间隙；端点与极值判定要分开"),
 (20,13): ("幂函数及其定义域", "分数指数的实数定义域依指数而异，不可默认全体实数"),
 (20,19): ("指数与指数函数", "指数函数底数须大于零且不等于一，单调方向随底数变化"),
 (20,31): ("对数与换底公式", "对数真数为正、底数正且不等于一，换底分母不可为零"),
 (20,34): ("对数函数图像性质", "自变量严格为正，底数大于一时递增，介于零一时递减"),
 (21,21): ("单位圆及三角函数", "正切在余弦为零时无定义；角度与弧度不可混用"),
 (22,12): ("三角恒等变换", "平方恒等式会丢符号；同除正余弦必须检查零点"),
 (22,18): ("三角函数实际建模", "周期、相位、量纲需要场景依据，不可由少数观测点过拟合"),
 (22,27): ("函数零点的二分法", "连续性与端点异号是存在保证，不代表唯一性"),
 (23,2): ("函数模型的条件与检验", "参数、定义域及数据适用区间必须说明，外推不是定理"),
 (26,13): ("平面向量基本定理", "作为基底的两个向量必须非共线；零向量不能构成基底"),
 (26,20): ("向量应用与解三角形", "余弦定理仅用于真实三角形，SSA可出现多解"),
 (27,4): ("复数概念及表示", "纯虚数的实部为零且虚部非零；虚数单位平方为负一"),
 (27,8): ("复数四则运算", "除数复数不可为零；复共轭运算须明确分母模平方"),
 (28,4): ("空间点线面位置关系", "空间直线异面不等于相交；几何图像不能代替公理"),
 (28,5): ("空间关系的定义", "异面直线既不平行也不相交；图上投影重叠不构成相交"),
 (28,16): ("空间线面平行垂直判定", "证明需满足相应充分条件，单看图形倾斜不可判断"),
 (31,10): ("随机试验、样本点及事件", "有限样本空间不自动等可能；事件为样本点集合"),
 (32,9): ("抽样与样本代表性", "简单随机抽样的等机会原则不能混同于实际样本必然代表总体"),
 (58,35): ("微分与局部线性近似（选修B）", "微分是导数乘自变量增量；有限增量一般不等于微分"),
}
# For heading-only anchors: topic containers are not the missing knowledge
# units. Section labels can hold *unnumbered* competencies or teaching actions.
SECTION_KIND = {
  "内容要求":"CONTENT_BLOCK",
  "学业要求":"COMPETENCY_BLOCK",
  "教学提示":"PEDAGOGY_BLOCK",
  "教学建议":"PEDAGOGY_BLOCK",
  "内容与要求":"CONTENT_BLOCK",
}
SECTION_COORDS = {
 (15,1):"CONTENT_BLOCK",(17,18):"PEDAGOGY_BLOCK",(18,16):"COMPETENCY_BLOCK",
 (19,3):"CONTENT_BLOCK",(23,12):"PEDAGOGY_BLOCK",(25,8):"CONTENT_BLOCK",
 (29,14):"PEDAGOGY_BLOCK",(30,16):"COMPETENCY_BLOCK",(31,3):"CONTENT_BLOCK",
 (33,3):"PEDAGOGY_BLOCK",(34,2):"COMPETENCY_BLOCK",(34,14):"CONTENT_BLOCK",
 (35,22):"PEDAGOGY_BLOCK",(36,6):"COMPETENCY_BLOCK",
}
HEADING_COORDS = {
 (15,4):"集合",(15,24):"常用逻辑用语",(16,19):"等式及不等式",
 (17,2):"二次函数和不等式",(19,6):"函数的概念与性质",
 (20,6):"幂指数对数函数",(21,8):"三角函数",
 (22,21):"函数应用",(26,26):"复数",
 (27,15):"空间几何",(31,5):"概率",
}
EXPECTED_TOTAL = 56
TRACKS = (*B61.TRACKS,"ELECTIVE_GENERAL")
VALID_CLASSES = {"CONTENT_BLOCK","COMPETENCY_BLOCK","PEDAGOGY_BLOCK",
                 "TOPIC_CONTAINER","SUBSECTION_SCOPE","DIRECT_OBJECTIVE"}

def sha_bytes(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def canonical(v):
    return json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n"

def require(cond, text):
    if not cond: raise ValueError(text)

def rows():
    with SOURCE.open(encoding="utf-8",newline="") as f:
        data=list(csv.DictReader(f))
    require(len(data)==EXPECTED_TOTAL, "unlinked review queue unexpectedly changed")
    return data

def validate_notes():
    source=rows()
    coords={(int(r["printed_page"]),int(r["pdfkit_line"])) for r in source}
    require(len(coords)==EXPECTED_TOTAL,"duplicate anchor coordinate in queue")
    require(set(OBJECTIVES)|set(SECTION_COORDS)|set(HEADING_COORDS)==coords,
            "curation does not cover all 56 anchor locations")
    require(not(set(OBJECTIVES)&set(SECTION_COORDS)) and
            not(set(OBJECTIVES)&set(HEADING_COORDS)) and
            not(set(SECTION_COORDS)&set(HEADING_COORDS)),
            "overlapping triage classifications")
    for coord,(title,boundary) in OBJECTIVES.items():
        require(len(title)>=4 and len(boundary)>=12, "placeholder objective/boundary")
    for label in SECTION_COORDS.values():
        require(label in {"CONTENT_BLOCK","COMPETENCY_BLOCK","PEDAGOGY_BLOCK"},
                "unrecognized section")

def make_record(r, base):
    p,n=int(r["printed_page"]),int(r["pdfkit_line"])
    coord=p,n
    source=next((a for a in base["anchors"] if
                a["printed_page"]==p and a["pdfkit_line"]==n),None)
    require(source is not None and not source["has_partially_located_source_lead"],
            "must point to a genuinely unlinked, source-attested anchor")
    require(source["source_line_sha256"]==r["source_line_sha256"] and
            source["kind"]==r["marker_kind"] and source["track_hint"]==r["track_hint"],
            "source-anchor evidence drift")
    if coord in OBJECTIVES:
        topic,boundary=OBJECTIVES[coord]
        cls="DIRECT_OBJECTIVE" if r["marker_kind"]=="CIRCLED_ITEM" or coord==(58,35) else "SUBSECTION_SCOPE"
        next_action="SPLIT_AND_ATTEST_MATHEMATICAL_ATOMS_WITH_FULL_SOURCE_CONTEXT"
        assessor="CONTENT_ATOMIZATION"
    elif coord in SECTION_COORDS:
        cls=SECTION_COORDS[coord]
        topic=f"{cls}：独立审查未编号要求（不将栏目标题误计为知识点）"
        boundary="必须检查本栏所有连续段落；仅有栏目标题不能证明学业能力、教学要求或知识覆盖"
        assessor="COMPETENCY_COVERAGE" if cls=="COMPETENCY_BLOCK" else "SOURCE_CONTEXT_REVIEW"
        next_action="INSPECT_FULL_SECTION_AND_UNNUMBERED_OBJECTIVES"
    else:
        require(coord in HEADING_COORDS, "unclassified coordinate")
        require(r["marker_kind"]=="MAJOR_NUMBER","expected topic heading")
        cls="TOPIC_CONTAINER"
        topic=HEADING_COORDS[coord]
        boundary="章标题不是独立知识原子；须核对其下各个子要求及跨页连续内容"
        assessor="HEADING_STRUCTURE"
        next_action="REVIEW_CHILD_CLAUSES_NOT_STANDALONE_ATOM"
    if coord in OBJECTIVES:
        require(r["marker_kind"] in {"SUBCLAUSE_NUMBER","CIRCLED_ITEM"},
                "subsection/direct source marker mismatch")
    if coord in SECTION_COORDS:
        require(r["marker_kind"]=="SECTION_LABEL","section marker mismatch")
    return dict(anchor_id=r["candidate_anchor_id"],printed_page=p,pdfkit_line=n,
         source_line_sha256=r["source_line_sha256"],source_page_pdfkit_sha256=source["source_page_pdfkit_sha256"],
         track_hint=r["track_hint"],marker_kind=r["marker_kind"],classification=cls,
         original_topic_paraphrase=topic,math_or_coverage_boundary=boundary,
         next_action=next_action,review_area=assessor,
         source_lead_found=False,full_source_context_verified=False,
         official_atomic_membership="UNDETERMINED",math_equivalence="NOT_REVIEWED",
         teacher_review="REVIEW_PENDING",teacher_signature=None,student_publishable=False,
         mathematical_proof_certification="NOT_CERTIFIED",
         educational_coverage="NOT_ESTABLISHED",
         authoring_method="MAC_EDITORIAL_TRIAGE_NON_TEACHER",
         proposed_child_atom_count=None)

def build():
    validate_notes()
    original=B61.build()
    out=[make_record(r, original) for r in rows()]
    require(len({x["anchor_id"] for x in out})==len(out)==EXPECTED_TOTAL,
            "queue duplicates")
    classes=Counter(x["classification"] for x in out)
    tracks=Counter(x["track_hint"] for x in out)
    for t in TRACKS:tracks.setdefault(t,0)
    require(sum(classes.values())==EXPECTED_TOTAL, "classification loss")
    return dict(schema_version="kb62-curated-source-triage-v1",
      parent_registry_sha256=sha_bytes(B61.REGISTRY.read_bytes()),
      parent_unlinked_queue_sha256=sha_bytes(SOURCE.read_bytes()),
      source_pdf_sha256=B61.PDF_SHA,
      original_candidate_anchors=original["candidate_anchor_count"],
      earlier_partial_leads=original["earlier_partial_source_leads"],
      triaged_unlinked_anchors=EXPECTED_TOTAL,
      classification_counts=dict(sorted(classes.items())),
      track_counts=dict(sorted(tracks.items())),
      official_atomic_denominator={t:None for t in B61.TRACKS},
      teacher_full_page_reviews=0,teacher_approved=0,student_published=0,
      rows=out,
      machine_triage_cannot_certify_math_or_source_completeness=True,
      source_lead_overlap_still_missing=True)

def nonatom_matrix(report):
    blocks=[]
    for row in report["rows"]:
        if row["classification"] in ("CONTENT_BLOCK","COMPETENCY_BLOCK","PEDAGOGY_BLOCK"):
            blocks.append(dict(anchor_id=row["anchor_id"],category=row["classification"],
              track_hint=row["track_hint"],printed_page=row["printed_page"],
              source_line_sha256=row["source_line_sha256"],
              numbered_atom_membership="NOT_A_STANDALONE_ATOM",
              unnumbered_requirements_checked=False,
              ability_assessment_ids=[],teaching_action_ids=[],content_atom_ids=[],
              coverage_status="UNMAPPED",review_status="REVIEW_PENDING",
              teacher_approved=False))
    return dict(schema_version="kb62-section-competency-ledger-v1",
      total_sections=len(blocks),counts_by_kind=dict(sorted(Counter(r["category"] for r in blocks).items())),
      no_section_is_atom=True,no_section_approved=True,rows=blocks)

def validate(report):
    require(report["schema_version"]=="kb62-curated-source-triage-v1" and
            report["source_pdf_sha256"]==B61.PDF_SHA,"schema/source mismatch")
    require(report["parent_registry_sha256"]==sha_bytes(B61.REGISTRY.read_bytes()) and
            report["parent_unlinked_queue_sha256"]==sha_bytes(SOURCE.read_bytes()),
            "upstream provenance drift")
    require(len(report["rows"])==EXPECTED_TOTAL and
            report["triaged_unlinked_anchors"]==EXPECTED_TOTAL,"lost review case")
    require(report["official_atomic_denominator"]=={t:None for t in B61.TRACKS},
            "forged official denominator")
    require(report["teacher_approved"]==report["student_published"]==
            report["teacher_full_page_reviews"]==0,"forged teacher review")
    require(report["machine_triage_cannot_certify_math_or_source_completeness"] is True and
            report["source_lead_overlap_still_missing"] is True,"misleading coverage claim")
    expected=build()
    require(report==expected,"triage differs from locked original annotation")
    for row in report["rows"]:
        require(row["classification"] in VALID_CLASSES and
                row["teacher_review"]=="REVIEW_PENDING" and
                row["teacher_signature"] is None and row["student_publishable"] is False and
                row["official_atomic_membership"]=="UNDETERMINED" and
                row["math_equivalence"]=="NOT_REVIEWED" and
                row["source_lead_found"] is False and
                row["full_source_context_verified"] is False and
                row["mathematical_proof_certification"]=="NOT_CERTIFIED" and
                row["educational_coverage"]=="NOT_ESTABLISHED" and
                row["proposed_child_atom_count"] is None,"unearned approval or coverage")

def verify_local_source(source_dir:Path):
    base=B61.load(B61.PAGES)
    hashes={p["printed_page"]:p["pdfkit_text_sha256"] for p in base["pages"]}
    for page in sorted({int(x["printed_page"]) for x in rows()}):
        raw=(source_dir/f"kb56_page_{page}.txt").read_bytes()
        require(sha_bytes(raw)==hashes[page],"Mac PDFKit page source drift")
        lines=raw.decode("utf-8").splitlines()
        for r in rows():
            if int(r["printed_page"])==page:
                line=lines[int(r["pdfkit_line"])-1]
                require(sha_bytes(line.encode())==r["source_line_sha256"],"source line SHA mismatch")
    return True

def render(report):
    kinds=report["classification_counts"]
    lines=["# Batch62｜56处未关联条款起点的原创内容层级审查（待教师确认）","",
      f"候选起点：{report['original_candidate_anchors']}；历史局部来源线索：{report['earlier_partial_leads']}；本批实际分类：{len(report['rows'])}/56。","",
      "**仅确认行首类型、主题及数学前提审核任务，不认证课标原子分母，也不宣称已解决56个缺漏来源。**","",
      "## 逐类审核队列","",
      "| 类型 | 件数 | 审核动作 |","|---|---:|---|"]
    for cls,n in sorted(kinds.items()):
        lines.append(f"| {cls} | {n} | {'提炼潜在学习目标并核验数学前提' if cls in ('SUBSECTION_SCOPE','DIRECT_OBJECTIVE') else '检查跨行/未编号要求，不计为单独知识原子'} |")
    lines+=["","## 31个实质性主题/子条的独立数学边界","",
            "| 位置 | 主题（原创释义） | 不可跳过的数学/适用边界 |",
            "|---|---|---|"]
    for row in report["rows"]:
        if row["classification"] in ("SUBSECTION_SCOPE","DIRECT_OBJECTIVE"):
            lines.append(f"| {row['anchor_id']} | {row['original_topic_paraphrase']} | {row['math_or_coverage_boundary']} |")
    lines+=["","## 审核红线","",
      "- 14个栏目标签、11个主题标题不是单独的数学知识原子；学业要求和教学提示仍须单独覆盖，不得从统计中消失。",
      "- 28个子条框架和3个直接目标只得到候选数学边界；完整条款、跨页重叠、图示和不编号内容尚未人工审完。",
      "- 所有条目均为 REVIEW_PENDING / NOT_CERTIFIED / NOT_ESTABLISHED；不向学生发布完整教师解答。",
      "- 七轨官方知识原子分母全部 null，完整教师页审核 0；不得用本审计类目替代正式覆盖率。",
      "- 不含课标版权原文：仅记录原创主题释义、原始页/行哈希、前提和审查任务。",""]
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    ap.add_argument("--verify-local-source",type=Path)
    ap.add_argument("--source-dir",type=Path,default=Path("/private/tmp"))
    args=ap.parse_args()
    if args.verify_local_source:
        require(args.verify_local_source.exists() and
                sha_bytes(args.verify_local_source.read_bytes())==B61.PDF_SHA,
                "official original PDF SHA mismatch")
        verify_local_source(args.source_dir)
    report=build()
    validate(report)
    sections=nonatom_matrix(report)
    require(sections["total_sections"]==14 and sections["counts_by_kind"]=={"COMPETENCY_BLOCK":4,"CONTENT_BLOCK":5,"PEDAGOGY_BLOCK":5}, "expected separate ability/pedagogy sections")
    if args.check:
        require(NONATOM.read_text(encoding="utf-8")==canonical(sections),"section competency ledger stale")
        require(OUT.read_text(encoding="utf-8")==canonical(report),"generated triage JSON stale")
        require(REPORT.read_text(encoding="utf-8")==render(report),"generated report stale")
    else:
        NONATOM.write_text(canonical(sections),encoding="utf-8")
        OUT.write_text(canonical(report),encoding="utf-8")
        REPORT.write_text(render(report),encoding="utf-8")
    print("Batch62 triage",report["classification_counts"],"teacher approvals: 0")

if __name__=="__main__":
    main()
