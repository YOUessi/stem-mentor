#!/usr/bin/env python3
"""Machine-auditable provisional curriculum source-to-draft crosswalk.

The 239 editorial candidate IDs are NOT the nationwide official atom denominator;
the 65 private teacher manuscripts are NOT official coverage. Does not promote either.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch143_lessons as latest
SOURCE=ROOT/"docs/evaluation/KB_BATCH125_PROVENANCE_GRADES.json"
OUT=ROOT/"docs/evaluation/KB_BATCH143_SOURCE_TO_DRAFT_GAPS.json"
MD=ROOT/"docs/evaluation/KB_BATCH143_SOURCE_TO_DRAFT_GAPS.md"
EVIDENCE=[
"NUMBERED_ANCHOR_PRESENT_NOT_CERTIFIED",
"HEADING_OR_SUBTOPIC_ONLY_REQUIRES_CLAUSE",
"OPTIONAL_EXAMPLE_NOT_REQUIRED_ATOM",
"NO_LAYOUT_MARKER_ALTERNATE_EVIDENCE_REVIEW",
]
def encode(x): return json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
def build():
    src=json.loads(SOURCE.read_text(encoding="utf-8"))
    records=src["records"]
    draft=json.loads(latest.AUDIT.read_text(encoding="utf-8"))
    latest_rows=json.loads(latest.OUT.read_text(encoding="utf-8"))
    assert draft==latest.audit(latest_rows)
    assert len(records)==239 and len({r["candidate_id"] for r in records})==239
    assert len(draft["rows"])==65 and len({r["candidate"] for r in draft["rows"]})==65
    assert {r["evidence_grade"] for r in records}==set(EVIDENCE)
    assert all(r["official_atom_id"] is None and not r["teacher_approved"] and
        not r["student_authoritative"] for r in records)
    assert all(r["review"]=="REVIEW_PENDING" for r in draft["rows"])
    index={r["candidate_id"]:r for r in records}
    match={r["candidate"] for r in draft["rows"] if r["candidate"] in index}
    out_of_125=sorted({r["candidate"] for r in draft["rows"]}-set(index))
    by_track={}
    all_tracks=set(latest.TRACKS)
    assert {r["course_track"] for r in records}<=all_tracks
    for t in latest.TRACKS:
        per=[r for r in records if r["course_track"]==t]
        covered=[r for r in per if r["candidate_id"] in match]
        incomplete=[r for r in per if r["candidate_id"] not in match]
        counts=Counter(r["evidence_grade"] for r in per)
        by_track[t]=dict(
           historical_editorial_candidates=len(per),
           author_drafts_total=draft["by_track"][t],
           candidate_to_draft_crosswalk_count=len(covered),
           candidate_without_draft=len(incomplete),
           candidate_without_draft_ids=sorted(r["candidate_id"] for r in incomplete),
           evidence_grade_counts={g:counts[g] for g in EVIDENCE},
           official_atom_denominator=None,official_coverage_fraction=None,
           human_approved_atoms=0,student_authoritative=0)
    candidate_rows=[]
    for r in records:
        candidate_rows.append(dict(candidate_id=r["candidate_id"],
          course_track=r["course_track"],grade=r["evidence_grade"],
          printed_page=r["printed_page"],source_span_sha256=r["span_sha256"],
          bounded_editor_draft_exists=r["candidate_id"] in match,
          official_atom_id=None,teacher_review="REVIEW_PENDING",
          proof_certified=False,student_authoritative=False))
    missing=sorted(r["candidate_id"] for r in records if r["candidate_id"] not in match)
    assert sum(v["candidate_without_draft"] for v in by_track.values())==len(missing)
    assert sum(v["candidate_to_draft_crosswalk_count"] for v in by_track.values())==len(match)
    assert len(match)+len(out_of_125)==65
    return dict(schema="kb143-source-to-draft-provisional-gap/1",
       official_standard_version="2017-edition-2020-revision",
       candidate_source_version=125,
       candidate_editorial_denominator=239,
       teacher_only_manuscript_total=65,
       crosswalked_historical_candidates=len(match),
       older_draft_candidates_without_this_239_ledger=out_of_125,
       historical_candidates_without_bounded_full_draft=len(missing),
       historical_unmatched_candidate_ids=missing,
       by_track=by_track, records=candidate_rows,
       official_atom_denominators={t:None for t in latest.TRACKS},
       official_coverage_fraction=None,teacher_approved=0,student_authoritative=0,
       teacher_review_pending=True,official_census_complete=False,
       warning="239 editorial candidates != official atoms; 65 teacher manuscripts != 65 validated curriculum lessons")
def validate(value):
    if value!=build(): raise ValueError("source-to-draft crosswalk changed or official status was forged")
    return True
def render(data):
    rows=["# Batch143｜七轨来源候选→教师候审讲义交叉缺口（K00/K01/K09）","",
     "**239是历史编辑候选数，绝非国家课程知识原子分母。65份是教师候审原创稿，不能作为全国课程完成率分子。**","",
     "| 课程轨道 | 历史编辑候选 | 匹配候审稿 | 未匹配候选 | 现存候审稿总数 | 官方原子分母 |",
     "|---|---:|---:|---:|---:|---|"]
    for t in latest.TRACKS:
        r=data["by_track"][t]
        rows.append(f'| {t} | {r["historical_editorial_candidates"]} | {r["candidate_to_draft_crosswalk_count"]} | {r["candidate_without_draft"]} | {r["author_drafts_total"]} | UNKNOWN |')
    rows+=["","## 证据等级与合法推断","",
     "- NUMBERED_ANCHOR_PRESENT_NOT_CERTIFIED：只能证明版面存在编号线索；不能证明具体数学结论为课标原文要求。",
     "- HEADING_OR_SUBTOPIC_ONLY_REQUIRES_CLAUSE：只有标题或小节线索，不得算作官方完整原子。",
     "- OPTIONAL_EXAMPLE_NOT_REQUIRED_ATOM：选学示例，不得自动并入必修。",
     "- NO_LAYOUT_MARKER_ALTERNATE_EVIDENCE_REVIEW：仍需补充真实课程条款证据。","",
     "## 未闭环内容","",
     f'- 239个历史编辑候选中有 {data["historical_candidates_without_bounded_full_draft"]} 个未与现有65份完整候审稿一一匹配。',
     f'- 65份候审稿中有 {len(data["older_draft_candidates_without_this_239_ledger"])} 个沿用其他历史编辑来源路径，不能强行映射为此239候选。',
     "- 官方分母、跨页语义去重和审校状态一律仍为UNKNOWN/REVIEW_PENDING；教师批准0、学生权威发布0。","",
     "## 接下来","",
     "按每条真实编号要求进行逐段语义拆分、跨页去重，随后标记CONCEPT/THEOREM/METHOD等类别；再将尚未匹配的编辑候选扩成真正原创讲义并由教师审核。",""]
    return "\n".join(rows)
def main():
    p=argparse.ArgumentParser()
    x=p.add_mutually_exclusive_group(required=True)
    x.add_argument("--write",action="store_true")
    x.add_argument("--check",action="store_true")
    arg=p.parse_args()
    d=build()
    if arg.write:
        OUT.write_text(encode(d),encoding="utf-8")
        MD.write_text(render(d),encoding="utf-8")
    else:
        validate(json.loads(OUT.read_text(encoding="utf-8")))
        if MD.read_text(encoding="utf-8")!=render(d):raise ValueError("Markdown gap report differs")
    print("PASS candidate-to-draft crosswalk: 239 editorial candidates; 65 teacher drafts; 7 official atom denominators UNKNOWN")
if __name__=="__main__":main()
