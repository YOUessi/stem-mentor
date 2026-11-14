#!/usr/bin/env python3
"""Seven-track candidate-to-teacher-draft coverage, NEVER national official syllabus completeness."""
from __future__ import annotations
import argparse,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch144_lessons as lessons
import build_kb_batch143_source_gap as old
SOURCE=ROOT/"docs/evaluation/KB_BATCH125_PROVENANCE_GRADES.json"
OUT=ROOT/"docs/evaluation/KB_BATCH144_SOURCE_TO_DRAFT_GAPS.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH144_SOURCE_TO_DRAFT_GAPS.md"
def build():
    source=json.loads(SOURCE.read_text(encoding="utf-8"))["records"]
    audit=lessons.audit(lessons.build())
    prior=old.build()
    assert len(source)==239 and len({x["candidate_id"] for x in source})==239
    assert len(audit["rows"])==75
    rows={r["candidate"]:r for r in audit["rows"]}
    matched=[r for r in source if r["candidate_id"] in rows]
    missing=[r for r in source if r["candidate_id"] not in rows]
    outsider=sorted(set(rows)-{r["candidate_id"] for r in source})
    assert len(matched)>=prior["crosswalked_historical_candidates"] and len(outsider)<=75
    tracks={}
    for t in lessons.TRACKS:
        entries=[r for r in source if r["course_track"]==t]
        known=[r for r in entries if r["candidate_id"] in rows]
        tracks[t]=dict(editorial_candidate_count=len(entries),linked_teacher_only_drafts=len(known),
         missing_bounded_teacher_drafts=len(entries)-len(known),
         editor_drafts_in_track=audit["by_track"][t],official_atom_denominator=None,
         teacher_approved=0,student_authoritative=0,
         source_grades=dict(Counter(r["evidence_grade"] for r in entries)))
    assert sum(x["editorial_candidate_count"] for x in tracks.values())==239
    assert sum(x["linked_teacher_only_drafts"] for x in tracks.values())==len(matched)
    return dict(schema="kb144-seven-track-provisional-source-to-draft/1",
       standard_version="2017-edition-2020-revision",historical_editorial_candidates=239,
       candidate_to_draft_matches=len(matched),candidates_without_bounded_teacher_draft=len(missing),
       editor_draft_total=75,drafts_from_other_lineage=len(outsider),
       unmatched_candidate_ids=sorted(r["candidate_id"] for r in missing),
       other_lineage_draft_candidates=outsider,by_track=tracks,
       official_atom_denominators={t:None for t in lessons.TRACKS},
       official_syllabus_census_complete=False,official_course_coverage_rate=None,
       human_approved_official_atoms=0,teacher_approved=0,student_authoritative=0,
       warning="239 editorial leads != national syllabus denominator; 75 unapproved drafts != official coverage")
def render(v):
    lines=["# Batch144｜历史课程来源候选→候审讲义缺口核对","",
      "**分母239只是历史编辑候选。国家课标七轨的正式知识原子分母仍然UNKNOWN。**","",
      "| 轨道 | 历史候选 | 匹配完整候审稿 | 尚缺对应稿 | 现存稿 | 官方原子分母 |",
      "|---|---:|---:|---:|---:|---|"]
    for t in lessons.TRACKS:
        r=v["by_track"][t]
        lines.append(f'| {t} | {r["editorial_candidate_count"]} | {r["linked_teacher_only_drafts"]} | {r["missing_bounded_teacher_drafts"]} | {r["editor_drafts_in_track"]} | UNKNOWN |')
    lines+=["",f'- 239个编辑候选中有{v["candidate_to_draft_matches"]}条关联到独立候审稿，有{v["candidates_without_bounded_teacher_draft"]}条没有关联。',f'- 另有{v["drafts_from_other_lineage"]}份草案来自不同历史来源路径，不能自动转成239条候选。',"- 所有草案REVIEW_PENDING/TEACHER_ONLY，官方认定、正式教师审核和学生发布均为0。","",
     "## 优先处置","逐条校对源要求的语义原子、跨页重复及必修/选学界线；真实教师审核前不能冻结国家课程分母。","","## 数学验证与Agent","本批新稿应通过独立数学Oracle及学生端零证据默认拒绝测试；有限见证不等于普适证明。",""]
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser();a=p.add_mutually_exclusive_group(required=True)
    a.add_argument("--write",action="store_true");a.add_argument("--check",action="store_true")
    args=p.parse_args();v=build()
    if args.write:
        OUT.write_text(lessons.encode(v),encoding="utf-8")
        REPORT.write_text(render(v),encoding="utf-8")
    else:
        assert json.loads(OUT.read_text(encoding="utf-8"))==v,"crosswalk drift"
        assert REPORT.read_text(encoding="utf-8")==render(v),"crosswalk report drift"
    print("PASS Batch144 source crosswalk: 239 provisional; "+str(v["candidate_to_draft_matches"])+" matched; "+str(v["candidates_without_bounded_teacher_draft"])+" still missing; official denominators UNKNOWN")
if __name__=="__main__":main()
