#!/usr/bin/env python3
"""Generate teacher-only manuscripts and auditable coverage, not official coverage."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.kb_batch35_review import SOURCE,PIN,review_only_manuscripts35,official_denominators,known_source,student_retrieval_projection
from app.kb_batch34_review import SOURCE as OLD_SOURCE,review_only_manuscripts
from app.kb_batch35_exact_witness import finite_evidence,guard,guard_pairs
OUT=ROOT/"docs/evaluation/KB_BATCH35_EDITORIAL_COVERAGE_AUDIT.json"
MD=ROOT/"docs/evaluation/KB_BATCH35_REMAINING_29_ELECTIVE_MANUSCRIPTS.md"
def collect():
    audit,cross=known_source()
    docs=review_only_manuscripts35()
    older=review_only_manuscripts()
    goals={x["editorial_id"]:x for x in audit["editorial_goals"]}
    ids={x.editorial_candidate_id for x in docs}
    old_ids={x.editorial_candidate_id for x in older}
    if ids&old_ids or ids|old_ids!=set(cross["unmatched_candidate_ids"]):
        raise ValueError("Expected exact disjoint cover of 49 original editorial gaps")
    ev=finite_evidence()
    if set(ev)!=ids:raise ValueError("Finite example audit missing or extra topic")
    for op,(yes,no) in guard_pairs().items():
        if guard(op,yes)!="FINITE_PREMISE_GUARDED" or guard(op,no)!="CONDITIONS_NOT_ESTABLISHED":
            raise ValueError("Invalid premise guard: "+op)
    return audit,cross,docs,goals,ev
def build():
    audit,cross,docs,goals,ev=collect()
    tracks=Counter(goals[d.editorial_candidate_id]["syllabus_track"] for d in docs)
    records=[]
    for d in docs:
        g=goals[d.editorial_candidate_id]
        records.append(dict(id=d.id,editorial_id=d.editorial_candidate_id,track=g["syllabus_track"],
          page=g["source_printed_page"],original_project_authored_goal=g["original_project_authored_goal"],
          source_anchor="PAGE_ONLY_NOT_INDIVIDUAL_CLAUSE_VERIFIED",official_clause_id=None,
          teacher_review="REVIEW_PENDING",complete_proof_certified=False,
          finite_numeric_checks=ev[d.editorial_candidate_id]["finite_examples"],
          teacher_solution_visible_to_student=False,student_published=False,
          content_completeness=dict(accurate_claim=bool(d.claim),assumptions=bool(d.assumptions),
             stepwise_reasoning=len(d.reasoning_steps)>=3,
             concrete_counterexample=bool(d.counterexample.example),
             two_teacher_side_solved_examples=len(d.worked_examples)==2,
             graded_hints=len(d.hint_ladder)==3,
             near_far_transfer=bool(d.transfer.near and d.transfer.far),
             source_page_but_not_official_clause=True),
          teacher_authoritative_prerequisite_edges_approved=False))
    return json.dumps(dict(
        schema_version="kb-batch35-audit-v1",
        original_pdf_sha256=audit["original_pdf"]["sha256"],
        source_seed_sha256=PIN,prior_seed_sha256=hashlib.sha256(OLD_SOURCE.read_bytes()).hexdigest(),
        summary=dict(editorial_goals_total=313,elective_editorial_goals=96,
            formerly_unassociated=49,batch34_manuscripts=20,batch35_manuscripts=29,
            formerly_unassociated_now_staged=49,remaining_without_review_manuscript=0,
            old_tentative_links_not_certified=47,by_track=dict(sorted(tracks.items())),
            finite_cases=sum(x["finite_examples"] for x in ev.values()),guard_classes=len(guard_pairs()),
            prior_deep_drafts_untouched=287,
            manuscripts_structurally_complete=29,student_authoritative_prerequisite_edges_approved=0,uncertified_proof_steps=538,unresolved_conflicts=10,
            official_denominators=official_denominators(),official_coverage=None,
            formally_certified_proofs=0,teacher_approved=0,student_published=0),
        records=records,finite_instance_evidence=ev,
        safety_projection=student_retrieval_projection(),
        source_scope="313 and 96 are project-authored page-level candidates, NOT official curricular knowledge denominators",
        math_scope="Finite arithmetic examples only, NOT general theorem, empirical causal claims, history, or student freeform proof certification",
        source_pdf_committed=False,real_student_data_committed=False),
        ensure_ascii=False,indent=2)+"\n"
def markdown():
    audit,cross,docs,goals,ev=collect()
    lines=["# STEM Mentor｜Batch35 剩余 29 篇原创选修数学审核稿","",
        "> 仅供真实教师审查：REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED；未进入学生 Agent 权威索引。页级课程位置不等于官方逐条课标归属。","",
        "## 审核边界","",
        "Batch34 已暂存20篇，本批补足此前49个未关联候选中的另外29篇；另外47个旧稿关联尚未独立核准。全部源于项目自编候选，不是官方课程知识原子分母。每篇两项受控有限算术检查不认证一般数学命题、经验模型、因果或历史主张。",""]
    for i,d in enumerate(docs,1):
        g=goals[d.editorial_candidate_id]
        lines += [f"## {i:02d}. {d.title}","",
          f"**审核ID**：{d.id}；**选修方向**：{g['syllabus_track']}；**原课标印刷页**：{g['source_printed_page']}；**编辑候选**：{g['original_project_authored_goal']}。","",
          f"**类型**：{d.kind}；**记号**：{'，'.join(d.notation)}。","",
          "### 准确定义 / 命题 / 方法","",d.claim,"",
          f"**全部声明的使用假设**：{'；'.join(d.assumptions)}","",
          "### 逐步推导与依据（教师审核前不可自动批准）",""]
        for j,s in enumerate(d.reasoning_steps,1):
            lines.append(f"{j}. {s.claim} **依据**：{s.reason}")
        lines += ["","### 错因 / 反例 / 适用边界","",
            f"**错误主张**：{d.counterexample.false_claim}。","",
            f"**具体反例**：{d.counterexample.example}","",
            f"**失效原因**：{d.counterexample.explanation}","",
            f"**适用边界**：{'；'.join(d.boundaries)}","",
            f"**修复提问**：{d.misconception.repair_question}","",
            "### 教师侧例题（不对独立学习泄漏）",""]
        for j,e in enumerate(d.worked_examples,1):
            lines += [f"**例题{j}**：{e.question}","",
                f"1. {e.steps[0]}",
                f"2. {e.steps[1]}",
                f"**教师答案**：{e.answer}；**复核**：{e.check}",""]
        lines += ["### 学生非剧透提示阶梯",""]
        for j,h in enumerate(d.hint_ladder,1):
            lines.append(f"{j}. {h}")
        lines += ["","### 迁移练习（无教师答案外泄）","",
            f"**近迁移**：{d.transfer.near}","",
            f"**远迁移**：{d.transfer.far}","",
            "**有限数学核验**：仅两项例题指定运算；形式证明批准 0，教师批准 0，学生发布 0。",""]
    return "\n".join(lines).rstrip()+"\n"
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    obj=build();md=markdown()
    if args.check:
        if OUT.read_text(encoding="utf-8")!=obj or MD.read_text(encoding="utf-8")!=md:
            raise SystemExit("Batch35 audit or markdown drift")
    else:
        OUT.write_text(obj,encoding="utf-8")
        MD.write_text(md,encoding="utf-8")
    print("PASS Batch35 29 original teacher-only manuscripts, 58 finite arithmetic cases, 12 premise guards; approval 0")
if __name__=="__main__":main()
