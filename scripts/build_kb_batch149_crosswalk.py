#!/usr/bin/env python3
"""Truthful, seven-track crosswalk of 239 EDITORIAL candidates to 105 pending manuscripts."""
from __future__ import annotations
import argparse,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch149_lessons as lesson
import build_kb_batch147_crosswalk as prior
SOURCE=prior.SOURCE
OUT=ROOT/"docs/evaluation/KB_BATCH149_SOURCE_TO_DRAFT_GAPS.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH149_SOURCE_TO_DRAFT_GAPS.md"
def build():
    entries=json.loads(SOURCE.read_text(encoding="utf-8"))["records"]
    audit=lesson.audit(lesson.build())
    assert len(entries)==239 and len({v["candidate_id"] for v in entries})==239
    rows={r["candidate"]:r for r in audit["rows"]}
    assert len(rows)==105
    matched={s["candidate_id"] for s in entries if s["candidate_id"] in rows}
    missing={s["candidate_id"] for s in entries if s["candidate_id"] not in rows}
    outsider=sorted(set(rows)-{e["candidate_id"] for e in entries})
    by_track={}
    for tr in lesson.TRACKS:
        sub=[e for e in entries if e["course_track"]==tr]
        included=[e for e in sub if e["candidate_id"] in rows]
        by_track[tr]=dict(editorial_candidates=len(sub),linked_teacher_only_drafts=len(included),
                          missing_editorial_lead_draft=len(sub)-len(included),
                          total_teacher_only_drafts=audit["by_track"][tr],
                          evidence_grades=dict(Counter(e["evidence_grade"] for e in sub)),
                          official_atom_denominator=None,teacher_approved=0,student_authoritative=0)
    assert sum(r["editorial_candidates"] for r in by_track.values())==239
    assert sum(r["linked_teacher_only_drafts"] for r in by_track.values())==len(matched)
    assert len(matched)+len(missing)==239 and sum(audit["by_track"].values())==105
    baseline=prior.build()
    assert len(matched)==baseline["candidate_to_draft_matches"]+10
    return dict(schema="kb149-unapproved-editorial-candidates-to-draft-gap/1",
      editorial_source_candidate_total=239,matched_editorial_candidates=len(matched),
      missing_editorial_candidates=len(missing),total_pending_teacher_manuscripts=105,
      drafts_from_other_lineages=len(outsider),other_lineage_draft_candidates=outsider,
      unmatched_candidate_ids=sorted(missing),by_track=by_track,
      official_atom_denominators={t:None for t in lesson.TRACKS},
      official_course_coverage_rate=None,official_atomic_census_complete=False,
      teacher_approved=0,student_authoritative=0,
      warning="239 editorial leads and 105 drafts are NOT the official syllabus atomic denominator.")
def validate(v):
    assert set(v["by_track"])==set(lesson.TRACKS)
    assert v["editorial_source_candidate_total"]==239 and v["total_pending_teacher_manuscripts"]==105
    assert v["matched_editorial_candidates"]+v["missing_editorial_candidates"]==239
    assert len(v["unmatched_candidate_ids"])==v["missing_editorial_candidates"]
    assert all(v["official_atom_denominators"][t] is None and
        v["by_track"][t]["official_atom_denominator"] is None and
        v["by_track"][t]["teacher_approved"]==0 and
        v["by_track"][t]["student_authoritative"]==0 for t in lesson.TRACKS)
    assert v["official_atomic_census_complete"] is False and v["official_course_coverage_rate"] is None
    assert v["teacher_approved"]==v["student_authoritative"]==0
    return True
def render(v):
    rows=["# KB149｜239条来源编辑候选与105篇教师候审深度稿的真实关联缺口","",
      "**编辑来源候选不能作为正式课标课程原子分母；教师尚未审校，学生不可获取教师解答。**","",
      "| 轨道 | 来源编辑候选 | 已关联候审稿 | 尚未关联 | 当前候审稿总数 | 官方原子分母 |",
      "|---|---:|---:|---:|---:|---|"]
    for tr in lesson.TRACKS:
        r=v["by_track"][tr]
        rows.append(f'| {tr} | {r["editorial_candidates"]} | {r["linked_teacher_only_drafts"]} | {r["missing_editorial_lead_draft"]} | {r["total_teacher_only_drafts"]} | UNKNOWN |')
    rows.extend(["",f'编辑来源关联{v["matched_editorial_candidates"]}/239，尚缺{v["missing_editorial_candidates"]}；另有{v["drafts_from_other_lineages"]}篇候审稿来自不同历史路径。',
      "这是课程编辑覆盖的进展，不是官方课标的完成率。七轨分母全部UNKNOWN，教师正式批准0。","",
      "机器可审查的完整未关联来源候选ID位于同名JSON。下一批依据真实课标语义、跨页续句和优先级分批编写，再由教师核对。",""])
    return "\n".join(rows)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    a=p.parse_args();v=build();validate(v)
    if a.write:
        OUT.write_text(lesson.encode(v),encoding="utf-8")
        REPORT.write_text(render(v),encoding="utf-8")
    else:
        assert json.loads(OUT.read_text(encoding="utf-8"))==v,"crosswalk hash/source drift"
        assert REPORT.read_text(encoding="utf-8")==render(v),"report drift"
    print(f'PASS Batch149 source→draft crosswalk: {v["matched_editorial_candidates"]} matched, {v["missing_editorial_candidates"]} unmatched (editorial only), official unknown')
if __name__=="__main__":main()
