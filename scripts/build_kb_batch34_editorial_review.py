#!/usr/bin/env python3
"""Versioned 20-item original authoring & reviewer-only K00 crosswalk.

The known 49 unassociated Batch33 page-level editorial candidates are NOT
official atoms. This batch stages manuscripts for 20, leaving 29 with no
draft association; none is published or counted toward official coverage.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.kb_batch34_review import SOURCE,PIN,EDITORIAL,CROSSWALK,review_only_manuscripts,known_source
from app.kb_batch34_exact_witness import evidence,rejected_bad_conditions
OUT=ROOT/"docs/evaluation/KB_BATCH34_EDITORIAL_REVIEW_AUDIT.json"
MARKDOWN=ROOT/"docs/evaluation/KB_BATCH34_TWENTY_ORIGINAL_MATH_MANUSCRIPTS.md"

def build():
    goal_audit,linked=known_source()
    docs=review_only_manuscripts()
    verified=evidence()
    negatives=rejected_bad_conditions()
    goals={x["editorial_id"]:x for x in goal_audit["editorial_goals"]}
    review_items=[]
    for d in docs:
        goal=goals[d.editorial_candidate_id]
        review_items.append(dict(
          manuscript_id=d.id,editorial_candidate_id=d.editorial_candidate_id,
          project_authored_goal=goal["original_project_authored_goal"],
          source_printed_page=goal["source_printed_page"],track=goal["syllabus_track"],
          kind=d.kind,title=d.title,manuscript_status=d.review.status,
          evidence_scope="PROJECT_AUTHORED_PAGE_ANCHORED_NOT_CLAUSE_VERIFIED",
          official_clause_id=None,official_clause_verified=False,
          independently_verified_example_pairs=verified.get(d.editorial_candidate_id,{}).get("valid_numeric_instances",0),
          proof_status="NOT_FORMALLY_CERTIFIED",teacher_approved=False,
          student_released=False,student_solution_visible=False))
    n=len(review_items)
    track=Counter(r["track"] for r in review_items)
    summary=dict(editorial_scope_candidates=313,prior_elective_unassociated_candidates=49,
      new_review_manuscripts=n,prior_existing_deep_lessons_untouched=287,
      elective_editorial_candidates_with_new_manuscripts=n,
      remaining_elective_unassociated_candidates=49-n,
      math_topics_with_exact_bounded_example_witness=len(verified),
      finite_instance_checks=sum(x["valid_numeric_instances"] for x in verified.values()),
      topics_still_without_independent_finite_instance_check=n-len(verified),
      explicit_invalid_premise_classes_rejected=len(negatives),
      manuscript_kinds=dict(Counter(d.kind for d in docs)),
      manuscripts_by_track=dict(sorted(track.items())),
      official_atomic_denominator=None,official_coverage_rate=None,
      teacher_approved_lessons=0,student_published_lessons=0,formally_certified_proofs=0)
    result=dict(schema_version="kb-batch34-editorial-review-v1",
      source_seed_sha256=PIN,
      source_batch33_elective_audit_sha256=hashlib.sha256(EDITORIAL.read_bytes()).hexdigest(),
      source_batch33_crosswalk_audit_sha256=hashlib.sha256(CROSSWALK.read_bytes()).hexdigest(),
      source_pdf_sha256=goal_audit["original_pdf"]["sha256"],
      source_pdf_borrowed_text_committed=False,
      summary=summary,items=review_items,
      finite_checks=verified,
      explicit_negative_premise_classes=list(negatives),
      still_without_review_manuscript=sorted(
          set(linked["unmatched_candidate_ids"])-{d.editorial_candidate_id for d in docs}),
      policy=dict(
          student_agent_index_untouched=True,student_full_solution_released=False,
          teacher_review_registry_unchanged=True,
          original_teacher_review_required=True,
          official_syllabus_clause_mapping_complete=False,
          real_student_data_uploaded=False,
          no_textbook_fulltext_copied=True,
          future_integration="After exact official clause review, topic alignment, proof verification and authenticated teacher approval"),
      evidence_boundary="Schema acceptance and finite examples are not complete mathematical proof certificates or teacher signoff")
    if summary["remaining_elective_unassociated_candidates"]!=29 or len(result["still_without_review_manuscript"])!=29:
        raise ValueError("Expected 29 unmatched elective candidates after this review batch")
    return json.dumps(result,ensure_ascii=False,indent=2)+"\n"

def markdown():
    goal_audit,_=known_source()
    goals={x["editorial_id"]:x for x in goal_audit["editorial_goals"]}
    finite=evidence()
    lines=["# STEM Mentor｜Batch34：20 篇数学原创完整审核稿（教师审核区）","",
      "> 所有稿件均为项目原创，**REVIEW_PENDING / TEACHER_ONLY**；页级来源并非官方逐句条款归属。此文件不是学生教材正式发布，不得直接用作权威 Agent 回答。","",
      "## 审核口径","","20 篇为独立可审稿件，不属于当前学生索引的原有 287 篇深度草案。来源分母及正式覆盖率仍未知；16 篇有两组有界精确例题检查，其余 4 篇待独立有限数值检验；没有任何完整证明获得形式认证或教师批准。",""]
    for ix,d in enumerate(review_only_manuscripts(),1):
        g=goals[d.editorial_candidate_id]
        lines += [f"## {ix:02d}. {d.title}","",f"**审核编号**：{d.id}；**选修轨道**：{g['syllabus_track']}；**原始来源印刷页**：{g['source_printed_page']}；**项目原创候选目标**：{g['original_project_authored_goal']}。","",f"**类型**：{d.kind}；**符号**：{', '.join(d.notation)}。","",f"### 定义或准确陈述","",d.claim,"",f"**全部明确前提**：{'；'.join(d.assumptions)}","",
                 "### 分步论证（待形式与教师复核）",""]
        for j,s in enumerate(d.reasoning_steps,1):
            lines += [f"{j}. {s.claim} **数学依据**：{s.reason}"]
        lines += ["","### 失效边界、反例与错因","",f"**错误说法**：{d.counterexample.false_claim}。","",f"**具体反例**：{d.counterexample.example}","",f"**失败原因**：{d.counterexample.explanation}","",f"**适用边界**：{'；'.join(d.boundaries)}","",f"**修复追问**：{d.misconception.repair_question}","",
                  "### 典型例题及教师侧完整过程",""]
        for j,e in enumerate(d.worked_examples,1):
            lines += [f"**例题 {j}**：{e.question}","",*([f"{k}. {s}" for k,s in enumerate(e.steps,1)]),
                       f"**教师答案**：{e.answer}。 **交叉检查提示**：{e.check}",""]
        lines += ["### 学生提示梯度（不含完整答案）","",*([f"{j}. {h}" for j,h in enumerate(d.hint_ladder,1)]),"",
                 "### 近迁移与远迁移","",f"**近迁移**：{d.transfer.near}","",f"**远迁移**：{d.transfer.far}","",
                 f"**独立有限实例验证**：{'2 个定值实例通过，但不证明一般定理' if d.editorial_candidate_id in finite else '本批无独立数值证据，继续 REVIEW_PENDING'}；**正式证明认证**：0；**教师审签**：0；**学生端发布**：0。",""]
    return "\n".join(lines).rstrip()+"\n"

def main():
    a=argparse.ArgumentParser();a.add_argument("--check",action="store_true");args=a.parse_args()
    expected=build();m=markdown()
    if args.check:
        if OUT.read_text(encoding="utf-8")!=expected or MARKDOWN.read_text(encoding="utf-8")!=m:
            raise SystemExit("Batch34 report or manuscript markdown drift")
    else:
        OUT.write_text(expected,encoding="utf-8")
        MARKDOWN.write_text(m,encoding="utf-8")
    s=json.loads(expected)["summary"]
    print("PASS Batch34",s["new_review_manuscripts"],"original REVIEW_PENDING manuscripts;",
          s["finite_instance_checks"],"finite checks;",s["remaining_elective_unassociated_candidates"],"editorial gaps; APPROVED=0")
if __name__=="__main__":main()
