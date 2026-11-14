#!/usr/bin/env python3
"""K00 source-boundary review graph, never automatic official curriculum dedup."""
from __future__ import annotations
import argparse,hashlib,json,sys
from collections import Counter,defaultdict
from itertools import combinations
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch147_lessons as lessons
import build_kb_batch147_crosswalk as cross
SOURCE=ROOT/"docs/evaluation/KB_BATCH125_PROVENANCE_GRADES.json"
OUT=ROOT/"docs/evaluation/KB_BATCH147_SOURCE_BOUNDARY_QUEUE.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH147_SOURCE_BOUNDARY_QUEUE.md"
def make():
    records=json.loads(SOURCE.read_text(encoding="utf-8"))["records"]
    contexts,_=lessons.prior.prior.prior.source.contexts()
    gap=cross.build()
    if len(records)!=239 or len({r["candidate_id"] for r in records})!=239:raise ValueError("239 source keys drift")
    linked=set(gap["unmatched_candidate_ids"])
    if len(linked)!=185 or gap["candidate_to_draft_matches"]!=54:raise ValueError("crosswalk drift")
    candidates=[]
    for r in records:
        ident=r["candidate_id"]
        c=contexts[ident];s=c["source"]
        if (s["source_span_sha256"]!=r["span_sha256"] or
            s["printed_page"]!=r["printed_page"] or
            c["course_track"]!=r["course_track"] or
            s["original_pdf_sha256"]!=lessons.PDF):
            raise ValueError("source anchor mismatch "+ident)
        if (r["official_atom_id"] is not None or r["teacher_approved"] or
             r["student_authoritative"] or not r["needs_human_semantic_check"]):
            raise ValueError("false approval "+ident)
        candidates.append(dict(id=ident,track=r["course_track"],
            proposed_objective=c["proposed_objective"],page=s["printed_page"],
            start=s["start_line"],end=s["end_line"],span_sha=s["source_span_sha256"],
            evidence_grade=r["evidence_grade"],matched_editor_draft=(ident not in linked),
            optional_school_example=bool(c["elective_e_optional_example"]),
            official_atom_id=None,teacher_approved=False,semantic_review="REVIEW_PENDING"))
    bypage=defaultdict(list)
    for c in candidates:bypage[c["page"]].append(c)
    edges=[];seen=set()
    def add(a,b,kind):
        x,y=sorted([a["id"],b["id"]]);key=(x,y,kind)
        if key in seen:return
        seen.add(key)
        edges.append(dict(a=x,b=y,relation=kind,source_page_pair=[a["page"],b["page"]],
             semantic_equivalence="UNDETERMINED",human_decision="REVIEW_PENDING",
             auto_merge_allowed=False))
    for page,items in bypage.items():
        for a,b in combinations(items,2):
            if a["start"]<=b["end"] and b["start"]<=a["end"]:
                add(a,b,"SAME_PAGE_OVERLAPPING_SOURCE_LINES_REVIEW")
            if a["span_sha"]==b["span_sha"]:
                add(a,b,"SAME_PAGE_IDENTICAL_SOURCE_SPAN_REVIEW")
    # Adjacent-page seam: review candidate at the last known source line and
    # candidate at the first known source line on the following printed page.
    # These are *possible* continuity cases, NOT dedup or semantic equivalence.
    for page,items in bypage.items():
        nxt=bypage.get(page+1,[])
        if not nxt:continue
        max_end=max(v["end"] for v in items)
        min_start=min(v["start"] for v in nxt)
        for a in items:
            if a["end"]!=max_end:continue
            for b in nxt:
                if b["start"]==min_start and a["track"]==b["track"]:
                    add(a,b,"ADJACENT_PAGE_SEAM_CANDIDATES_REVIEW")
    # A cross-page identical span digest, if it ever appears, is retained as
    # a review lead rather than being merged automatically.
    bysha=defaultdict(list)
    for c in candidates:bysha[c["span_sha"]].append(c)
    for items in bysha.values():
        for a,b in combinations(items,2):
            if a["page"]!=b["page"]:
                add(a,b,"CROSS_PAGE_IDENTICAL_SPAN_DIGEST_REVIEW")
    edges.sort(key=lambda r:(r["relation"],r["source_page_pair"],r["a"],r["b"]))
    touched={r["a"] for r in edges}|{r["b"] for r in edges}
    tracks={}
    for t in lessons.TRACKS:
        group=[r for r in candidates if r["track"]==t]
        tracks[t]=dict(source_leads=len(group),manuscript_linked=sum(r["matched_editor_draft"] for r in group),
            manuscript_missing=sum(not r["matched_editor_draft"] for r in group),
            possible_boundary_cases=sum(r["id"] in touched for r in group),
            optional_school_examples=sum(r["optional_school_example"] for r in group),
            official_atom_denominator=None,teacher_approved=0,student_authoritative=0)
    if sum(x["source_leads"] for x in tracks.values())!=239:raise ValueError("track partition incomplete")
    if sum(x["manuscript_missing"] for x in tracks.values())!=185:raise ValueError("missing drafts drift")
    if any(x["official_atom_denominator"] is not None for x in tracks.values()):raise ValueError("false official denominator")
    return dict(schema="kb147-k00-source-boundary-review-not-official-census/1",
        source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        source_pdf_sha256=lessons.PDF,historical_editorial_leads=239,teacher_pending_manuscripts=95,
        linked_leads=54,unmatched_leads=185,candidates=sorted(candidates,key=lambda r:r["id"]),
        candidate_relation_edges=edges,
        edge_counts=dict(sorted(Counter(r["relation"] for r in edges).items())),
        by_track=tracks,official_denominators={t:None for t in lessons.TRACKS},
        official_atom_census_completed=False,automatically_merged_atoms=0,
        teacher_approved_atoms=0,student_authoritative_atoms=0,
        interpretation="Metadata review queue only; page continuity is heuristic, not official semantic duplication")
def render(v):
    lines=["# K00 Batch147｜来源边界、跨页衔接与未审查原子候选队列","",
        "本表只展示项目原创编辑候选与来源元数据，不复刻课标正文。",
        "**239不是官方分母；95为教师候审稿；54/239等关联数不是正式课程覆盖率。**",
        "同页相交、跨页首尾相邻都只是待裁决风险，不意味着课程知识是同一个原子。","",
        "| 轨道 | 编辑来源候选 | 已联候审稿 | 缺稿 | 待裁决边界候选 | 学校选修示例 | 官方原子分母 |",
        "|---|---:|---:|---:|---:|---:|---|"]
    for t,x in v["by_track"].items():
        lines.append(f'| {t} | {x["source_leads"]} | {x["manuscript_linked"]} | {x["manuscript_missing"]} | {x["possible_boundary_cases"]} | {x["optional_school_examples"]} | UNKNOWN |')
    lines.extend(["", "## 元数据边界审查关系（不自动归并）"])
    for k,n in v["edge_counts"].items():lines.append(f"- {k}: {n} pairs")
    lines.extend(["", "## 对每个候选必须完成的人工步骤",
        "1. 在授权Mac根据原始印刷页、行号和SHA重放来源，确认完整编号条款及跨页句子连贯性。",
        "2. 把单个条款中多项独立数学要求拆成候选原子，并检查是否跨页重复或仅为示例。",
        "3. 对每个原子验证知识分型、课程轨道、先修、证明前提、题族链接；记录保留/拆分/合并的理由。",
        "4. 经过真实教师审核后方可冻结七轨分母，候审稿不能作为学生权威知识。",
        "", "## 全量待裁决关系索引"])
    for row in v["candidate_relation_edges"]:
        lines.append(f'- {row["relation"]}: {row["a"]} ↔ {row["b"]}; {row["source_page_pair"]}; REVIEW_PENDING')
    return "\n".join(lines)+"\n"
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    a=p.parse_args();v=make()
    if a.write:
        OUT.write_text(lessons.encode(v),encoding="utf-8")
        REPORT.write_text(render(v),encoding="utf-8")
    elif json.loads(OUT.read_text(encoding="utf-8"))!=v or REPORT.read_text(encoding="utf-8")!=render(v):
        raise ValueError("K00 metadata audit drift")
    print("PASS Batch147 K00: 239 provisional leads; 54 draft-linked /185 unmatched; no official denominators; "+str(len(v["candidate_relation_edges"]))+" source review edges")
if __name__=="__main__":main()
