#!/usr/bin/env python3
"""Auditable closure of 41 BOUNDED PDFKit proposal manuscripts, not full national syllabus."""
from __future__ import annotations
import argparse, copy, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch133_atomization as atoms
import build_kb_batch136_coverage as baseline
import build_kb_batch137_lessons as lessons
import check_kb_batch137_math as math
OUT=ROOT/"docs/evaluation/KB_BATCH137_BOUNDED_COMPLETENESS.json"
MD=ROOT/"docs/evaluation/KB_BATCH137_BOUNDED_COMPLETENESS.md"
def build():
    old=baseline.build()
    if old["full_teacher_draft_manuscripts"]!=34 or old["incomplete_proposal_drafts"]!=7:
        raise ValueError("baseline drift")
    new=lessons.build();lessons.validate(new)
    math.validate(math.build())
    rows=copy.deepcopy(old["rows"])
    lookup={r["candidate_id"]:r for r in rows}
    for r in new:
        item=lookup[r["source_candidate_id"]]
        if item["has_complete_teacher_manuscript"] or item["source_span_sha256"]!=r["source_span_sha256"]:
            raise ValueError("duplicate or source-mismatched reviewed item")
        item.update(has_complete_teacher_manuscript=True,manuscript_id=r["id"],missing_fields=[],
                    teacher_examples=2,student_hints=3)
    if len(new)!=7 or any(not r["has_complete_teacher_manuscript"] for r in rows):
        raise ValueError("bounded manuscript closure incomplete")
    by_track={}
    for track in atoms.TRACKS:
        sub=[r for r in rows if r["track"]==track]
        by_track[track]=dict(provisional_candidates=len(sub),
             complete_teacher_manuscript_drafts=len(sub),candidates_still_missing_full_draft=0,
             official_atom_denominator=None,official_coverage_rate=None,
             teacher_approved=0,student_published=0)
    total=old["finite_exact_oracle_cases"]+len(math.cases())
    assert total==123
    return dict(schema="kb137-bounded-quality-ledger/1",
        source="BOUNDED_41_EDITORIAL_PROPOSALS_NOT_FULL_NATIONAL_CENSUS",
        syllabus_version="2017-edition-2020-revision-editorial-only",
        all_seven_track_denominators_known=False,official_atom_denominators={t:None for t in atoms.TRACKS},
        national_course_coverage_percentage=None,scope_proposals=41,
        full_teacher_draft_manuscripts=41,incomplete_proposal_drafts=0,
        teacher_examples=82,hints=123,near_transfer_exercises=41,far_transfer_exercises=41,
        finite_exact_oracle_cases=total,certified_general_theorems=0,
        teacher_approvals=0,student_authoritative_releases=0,
        by_track=by_track,missing_full_manuscript_queue=[],rows=rows,
        reviewer_attestation="REVIEW_PENDING_NOT_SIGNED",
        source_semantics_certified=False)
def validate(obj):
    if obj!=build():raise ValueError("coverage ledger or approvals/denominators forged")
    return True
def render(d):
    lines=["# Batch137｜41条项目候选的完整教师讲义草案闭环（非全课标）","",
      "**本分母是41条尚待真实教师语义确认的项目拟议原子，绝不是全国课程标准知识原子总数。**",
      f"项目拟议原子{d['scope_proposals']}；完整教师候审讲义{d['full_teacher_draft_manuscripts']}；本有限子集缺稿{d['incomplete_proposal_drafts']}。",
      f"原创教师例题{d['teacher_examples']}；三级提示{d['hints']}；近远迁移各{d['near_transfer_exercises']}；精确有限检查{d['finite_exact_oracle_cases']}。",
      "一般定理认证0、教师批准0、学生权威发布0；有限检查不等于一般证明。",
      "## 七轨限定子集状态","",
      "| 七轨 | 项目拟议原子 | 完整候审稿 | 正式课程原子总数 | 教师批准 |",
      "|---|---:|---:|---|---:|"]
    for t in atoms.TRACKS:
        v=d["by_track"][t]
        lines.append(f"| {t} | {v['provisional_candidates']} | {v['complete_teacher_manuscript_drafts']} | UNKNOWN | 0 |")
    lines+=["","## 逐个候审原子的证据锁与内容对账",""]
    for r in d["rows"]:
        lines.append(f"- {r['candidate_id']} · {r['track']} · {r['knowledge_type']} · {r['manuscript_id']} · 例题{r['teacher_examples']} · 提示{r['student_hints']} · 原文片段SHA256 {r['source_span_sha256']} · REVIEW_PENDING")
    lines+=["","## 审查和下一批","",
      "选修B/C/D/E在这41条有限子集中没有拟议原子，绝不表示那些课程轨道完成或不存在；必须继续做七轨全量编号要求→原子语义映射。",
      "本闭环仅覆盖41个限定提案的结构化内容：证明每步还需独立认证，来源归属仍须教师逐条签字，学生自由解题步骤未经验证。",
      "下一批扩大范围到独立选修B–E与统计/解析几何/建模，冻结正式可审计课标分母；复核历史高风险证明和先修依赖。"]
    return "\n".join(lines)+"\n"
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    z=p.parse_args()
    if z.write:
        a=build();validate(a);OUT.write_text(atoms.stable_json(a),encoding="utf-8")
        MD.write_text(render(a),encoding="utf-8")
    else:
        a=json.loads(OUT.read_text(encoding="utf-8"));validate(a)
        if MD.read_text(encoding="utf-8")!=render(a):raise ValueError("Markdown drift")
    print("PASS 41/41 bounded review drafts; official seven-track denominator UNKNOWN")
if __name__=="__main__":main()
