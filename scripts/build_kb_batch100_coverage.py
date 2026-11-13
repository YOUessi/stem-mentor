#!/usr/bin/env python3
"""Strict editorial coverage ledger for 20 additional source-locked math teacher drafts.

No promotion of draft content, unofficial track census or prerequisite text.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"backend"),str(ROOT/"scripts")]
import build_kb_batch99_prerequisite_gap as G
import build_kb_batch100_depth as D
from app.deep_knowledge import DeepLesson,lessons
from app.deep_retrieval import student_evidence_lookup

OUT=ROOT/"docs/evaluation/KB_BATCH100_COVERAGE_AND_GATES.json"
MD=ROOT/"docs/evaluation/KB_BATCH100_COVERAGE_AND_GATES.md"

def require(ok,message):
    if not ok:raise ValueError(message)

def verify(payloads=None, links=None):
    authored,audit=D.build()
    payloads=authored if payloads is None else payloads
    links=audit["canonical_lesson_source_links"] if links is None else links
    require(len(payloads)==len(links)==20,"new lesson/lineage counts changed")
    ids=[x["id"] for x in payloads]
    require(len(set(ids))==20,"duplicate lesson ID")
    require(set(ids)=={x["lesson_id"] for x in links},"lesson-to-source mismatch")
    all_docs={x.id:x for x in lessons()}
    require(len(all_docs)>=20 and all(x in all_docs for x in ids),
            "new lessons must be discovered by live teacher-side deep lesson loader")
    require(len({x["source_candidate_id"] for x in links})==20,
            "duplicate source anchors")
    for payload in payloads:
        item=DeepLesson.model_validate(payload)
        require(item.review.status=="REVIEW_PENDING" and
                item.teacher_solution_visibility=="TEACHER_ONLY" and
                not item.prerequisite_lesson_ids,
                "unreviewed concept was promoted or prerequisite silently resolved")
        require(len(item.worked_examples)==2 and len(item.hint_ladder)==3,
                "worked examples and hint ladder incomplete")
        for ex in item.worked_examples:
            require(len(ex.steps)>=2 and ex.answer and ex.check,
                    "teacher example proof or independent check missing")
        lookup=student_evidence_lookup(item.title)
        require(lookup["status"]=="NO_APPROVED_EVIDENCE"
                and lookup["teacher_solution_exposed"] is False,
                "student lookup leaked an unreviewed teacher solution")
        # Tests keep teacher examples entirely in teacher data; never include them in response.
        resp=json.dumps(lookup,ensure_ascii=False)
        require(all(ex.answer not in resp for ex in item.worked_examples
                    if len(ex.answer)>2),"student response leaks teacher answer")
    old=G.build()
    require(old["total_deep_draft_lessons"]==66
            and old["textual_prerequisite_descriptions"]==132
            and old["resolved_prerequisite_id_references"]==0,"historical graph audit drift")
    new_text=sum(len(r["prerequisites"]) for r in payloads)
    require(new_text==40,"batch100 unresolved prerequisites changed")
    require(all(v is None for v in audit["official_atom_denominators_by_track"].values()),
            "fabricated official atom denominator")
    per_track={}
    for track,vals in audit["track_counts"].items():
        per_track[track]={
          "project_provisional_labels_not_official_atoms":vals["provisional_label_count"],
          "teacher_pending_deep_drafts":vals["full_drafts_pending_teacher"],
          "official_verified_atom_denominator":None,
          "teacher_approved":0,"student_authoritative_release":0
        }
    by_kind=dict(sorted(Counter(x["kind"] for x in payloads).items()))
    status=dict(sorted(Counter(x["engineering_track_status"] for x in links).items()))
    return {
      "schema_version":"kb100-coverage-and-fail-closed-v1",
      "source_scope":"PROVISIONAL_EDITORIAL_PROJECT_REGISTRY",
      "total_provisional_labels":300,
      "provisional_stage_counts":audit["stage_counts"],
      "new_teacher_pending_deep_drafts":20,
      "total_teacher_pending_source_locked_deep_drafts":86,
      "new_teacher_worked_examples":40,
      "new_hint_ladder_prompts":60,
      "new_theorem_proof_drafts":audit["proof_bearing_theorem_drafts"],
      "new_bounded_exact_oracles":20,
      "new_lesson_kinds":by_kind,
      "new_lesson_engineering_track_alignment":status,
      "new_source_locked_ids":ids,
      "tracks":per_track,
      "official_atom_denominator":None,
      "human_atomized_pages":"0/61",
      "uncompared_provisional_labels":134,
      "preexisting_unresolved_textual_prerequisites":132,
      "new_unresolved_textual_prerequisites":new_text,
      "total_unresolved_textual_prerequisites":132+new_text,
      "promoted_teacher_approved_prerequisite_edges":0,
      "teacher_approved":0,
      "student_authoritative_releases":0,
      "authoritative_student_retrieval":"FAIL_CLOSED_NO_APPROVED_EVIDENCE",
      "formal_general_math_theorem_certificates":0,
      "unresolved_historical_proof_steps":538,
      "P0_steps_without_teacher_review":106,
      "unresolved_math_conflicts":10
    }
def md(x):
    lines=["# Batch100｜七轨编辑覆盖及学生端安全门禁", "",
      "**注意：** 源数据仅为项目临时标签和作者编辑对应。正式知识原子分母尚未逐页核实，任何深度讲义均不属于正式已审核课程。","",
      "| 指标 | 计数 |","|---|---:|",
      f"| 来源临时标签 | {x['total_provisional_labels']} |",
      f"| 本批完整原创教师草案 | {x['new_teacher_pending_deep_drafts']} |",
      f"| 累计来源锁定深度草案 | {x['total_teacher_pending_source_locked_deep_drafts']} |",
      f"| 本批教师例题 | {x['new_teacher_worked_examples']} |",
      f"| 本批三级提示 | {x['new_hint_ladder_prompts']} |",
      f"| 未成对比较的临时主题 | {x['uncompared_provisional_labels']} |",
      f"| 未解析文字先修 (累计) | {x['total_unresolved_textual_prerequisites']} |",
      "| 教师审核批准 | 0 |","| 面向学生的权威发布 | 0 |","",
      "| 临时编辑轨道 | 临时源标签 | 本轨深度草案 | 正式原子分母 |",
      "|---|---:|---:|---|"]
    for k,v in x["tracks"].items():
        lines.append(f"| {k} | {v['project_provisional_labels_not_official_atoms']} | {v['teacher_pending_deep_drafts']} | UNKNOWN |")
    lines+=["","**新增20项工程轨道匹配（编辑状态）：** "+
       str(x["new_lesson_engineering_track_alignment"])+
       "。不将来源轨道相同误作主题语义审核通过。","",
       "**安全：** 未批准检索一律 NO_APPROVED_EVIDENCE；教师完整解答不对独立挑战泄漏。","",
       "下一批优先：134对未比对主题、七轨正式来源原子、172段先修依赖的人工审核候选、教师签审及未见题评测。",""]
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");args=p.parse_args()
    x=verify()
    output={OUT:json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n",MD:md(x)}
    for path,data in output.items():
        if args.check:
            require(path.read_text(encoding="utf8")==data,"coverage drift: "+str(path))
        else:path.write_text(data,encoding="utf8")
    print("BATCH100 COVERAGE 20 new/86 cumulative; 172 unresolved prerequisite notes; teacher 0; check",args.check)
if __name__=="__main__":main()
