#!/usr/bin/env python3
"""Auditable duplicate-source *triage* for 239 historical leads, not official atomization.

A shared source span or cue is NOT enough to collapse two educational concepts.
This stage emits human adjudication queues, never silently deduplicates an atom.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch146_crosswalk as cross
import build_kb_batch146_lessons as lessons
SOURCE=ROOT/"docs/evaluation/KB_BATCH125_PROVENANCE_GRADES.json"
OUT=ROOT/"docs/evaluation/KB_BATCH146_SOURCE_ALIAS_REVIEW.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH146_SOURCE_ALIAS_REVIEW.md"
EXPECTED_GRADES={
  "NUMBERED_ANCHOR_PRESENT_NOT_CERTIFIED",
  "HEADING_OR_SUBTOPIC_ONLY_REQUIRES_CLAUSE",
  "OPTIONAL_EXAMPLE_NOT_REQUIRED_ATOM",
  "NO_LAYOUT_MARKER_ALTERNATE_EVIDENCE_REVIEW"
}
def audit():
    data=json.loads(SOURCE.read_text(encoding="utf-8"))
    entries=data["records"]
    if len(entries)!=239 or len({r["candidate_id"] for r in entries})!=239:
        raise ValueError("historical source candidates have drifted")
    if not all(r["official_atom_id"] is None and not r["teacher_approved"] and
               not r["student_authoritative"] and r["needs_human_semantic_check"] for r in entries):
        raise ValueError("unreviewed historical evidence falsified approval")
    if any(r["evidence_grade"] not in EXPECTED_GRADES for r in entries):
        raise ValueError("unknown source evidence grading")
    src_map=defaultdict(list)
    cue_map=defaultdict(set)
    for r in entries:
        key=(r["printed_page"],r["span_sha256"])
        src_map[key].append(r)
        for marker in r["marker_ids"]:
            cue_map[marker].add(r["candidate_id"])
    groups=[]
    for (page,sha),members in sorted(src_map.items()):
        if len(members)<2:continue
        tracks=sorted({r["course_track"] for r in members})
        groups.append(dict(source_page=page,source_span_sha256=sha,
              candidate_ids=sorted(r["candidate_id"] for r in members),
              tracks=tracks,human_review_status="REVIEW_PENDING",
              semantic_merge_decision="UNDECIDED",
              warning="shared span can legitimately contain multiple objectives"))
    cue_groups=[]
    for marker,members in sorted(cue_map.items()):
        if len(members)<2:continue
        cue_pages=sorted({r["printed_page"] for r in entries if r["candidate_id"] in members})
        cue_groups.append(dict(marker_id=marker,candidate_ids=sorted(members),
             printed_pages=cue_pages,cross_page_evidence=(len(cue_pages)>1),
             semantic_merge_decision="UNDECIDED"))
    by_track={}
    for track in lessons.TRACKS:
        subset=[r for r in entries if r["course_track"]==track]
        by_track[track]=dict(historical_candidate_count=len(subset),
            provisional_evidence_grades=dict(sorted(Counter(r["evidence_grade"] for r in subset).items())),
            candidate_ids_in_shared_source_span=sum(any(r["candidate_id"] in g["candidate_ids"] for g in groups) for r in subset),
            official_atom_denominator=None,
            missing_official_review=True,
            teacher_approved=0)
    draft_cross=cross.build()
    assert draft_cross["candidate_to_draft_matches"]==44
    assert sum(x["historical_candidate_count"] for x in by_track.values())==239
    assert len(groups)==7 and sum(len(g["candidate_ids"]) for g in groups)==19
    assert len(cue_groups)==17 and sum(len(g["candidate_ids"]) for g in cue_groups)==40
    return dict(schema="kb146-source-shared-span-human-adjudication/1",
        source="KB_BATCH125_PROVENANCE_GRADES.json",
        source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        historical_editorial_candidate_count=239,
        evidence_grade_counts=dict(sorted(Counter(r["evidence_grade"] for r in entries).items())),
        shared_source_span_group_count=len(groups),
        candidate_count_in_shared_source_span_groups=sum(len(g["candidate_ids"]) for g in groups),
        shared_cue_group_count=len(cue_groups),
        cross_page_shared_cue_group_count=sum(bool(g["cross_page_evidence"]) for g in cue_groups),
        source_cue_memberships_with_shared_marker=sum(len(g["candidate_ids"]) for g in cue_groups),
        exact_span_review_groups=groups,shared_cue_review_groups=cue_groups,
        by_track=by_track,linked_existing_draft_count=44,
        missing_bounded_teacher_draft_count=195,
        official_seven_track_atom_denominators={t:None for t in lessons.TRACKS},
        official_census_complete=False,source_aliases_auto_merged=0,
        human_approved_semantic_merges=0,
        teacher_approved=0,student_authoritative=0,
        disclosure="Source hashes are text evidence anchors, NOT nationally approved unique curriculum atoms")
def render(data):
    lines=["# Batch146｜历史课程线索重复来源与跨页语义人工裁决队列","",
       "依据旧版239条来源候选，识别**共享同页同源文本指纹**与**共享版式提示**，不自动合并数学知识。",
       "同一页码与span SHA碰撞只能说明来自相同来源片段；可能是一个要求拆分的多个不同概念。",
       "同一 cue 被复用也是证据线索，不等于相同的教育目标。此处没有完成跨页语义去重，也没有冻结官方分母。","",
       f"- 历史编辑候选：{data['historical_editorial_candidate_count']}；关联完整候审稿：{data['linked_existing_draft_count']}；缺稿：{data['missing_bounded_teacher_draft_count']}。",
       f"- 同页同段来源共享：{data['shared_source_span_group_count']}组／{data['candidate_count_in_shared_source_span_groups']}个候选，需要人工逐条核对。",
       f"- 相同版式 cue 复用：{data['shared_cue_group_count']}组／{data['source_cue_memberships_with_shared_marker']}次候选-线索关系，需要语义而非哈希判断。",
       f"- 这些共享cue中跨页复用：{data['cross_page_shared_cue_group_count']}组。**零不表示已完成跨页语义去重**，因为不同cue也可能描述相同课程目标。","",
       "## 按七轨分组（官方课程原子分母均 UNKNOWN）",
       "| 轨道 | 编辑线索 | 共用原文段候选 | 已确认官方原子分母 |",
       "|---|---:|---:|---|"]
    for track in lessons.TRACKS:
        v=data["by_track"][track]
        lines.append(f'| {track} | {v["historical_candidate_count"]} | {v["candidate_ids_in_shared_source_span"]} | UNKNOWN |')
    lines += ["","## 同源段人工裁决队列（不自动合并）"]
    for j,g in enumerate(data["exact_span_review_groups"],1):
        lines.append(f'{j}. 印刷页{g["source_page"]}，来源SHA `{g["source_span_sha256"]}`：'+", ".join(g["candidate_ids"])+
            "；**REVIEW_PENDING**，拆并理由及教师签字缺失。")
    lines += ["","## 跨页/跨主题处理门槛",
        "- 对每组取得原始许可课标上下文，在Mac上审查编号要求的全句、上下段与页面连续关系。",
        "- 人工裁定同源是同一目标、多目标拆分，或只是教学活动举例；冲突归属须保留来源证据。",
        "- 只有完整覆盖全部官方内容要求且逐条审核完成，才能计算必修、选择性必修及A–E真正分母。",
        "- 机器不得将239减去重复片段数直接当作官方总知识原子数；候审稿也不得自动APPROVED。",""]
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--write",action="store_true")
    group.add_argument("--check",action="store_true")
    a=p.parse_args();r=audit()
    if a.write:
        OUT.write_text(lessons.encode(r),encoding="utf-8")
        REPORT.write_text(render(r),encoding="utf-8")
    else:
        if json.loads(OUT.read_text(encoding="utf-8"))!=r or REPORT.read_text(encoding="utf-8")!=render(r):
            raise ValueError("source alias adjudication report drift")
    print("PASS K00: 239 leads; 7 shared-span groups (19 candidates); 17 cue reuse groups; official denominators UNKNOWN")
if __name__=="__main__":main()
