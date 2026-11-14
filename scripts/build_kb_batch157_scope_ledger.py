#!/usr/bin/env python3
"""K00 deterministic traceability ledger: NOT a national official curriculum denominator.

Every numbered layout marker is one auditable review obligation, not a knowledge atom.
Unnumbered CDE are distinct overlapping editorial proposals. No auto semantic merges.
"""
from __future__ import annotations
import argparse,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch155_review_matrix as source
import build_kb_batch157_lessons as content
OUT=ROOT/"docs/evaluation/KB_BATCH157_REVIEW_OBLIGATIONS.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH157_REVIEW_OBLIGATIONS.md"
TRACKS=source.TRACKS
def encode(d):return json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
def must(ok,msg):
    if not ok:raise ValueError("KB157 syllabus ledger: "+msg)
def build():
    old=source.build();drafts=content.audit(content.build())
    authored={x["candidate"]:x for x in drafts["rows"]}
    must(len(authored)==165,"165 unique draft source candidates required")
    must(len(old["source_marker_obligations"])==315 and
         len(old["unnumbered_CDE_editorial_obligations"])==32 and
         len(old["source_relation_review_queue"])==89,"source review populations drift")
    out=[];classes=Counter()
    for s in old["source_marker_obligations"]:
        leads=s["overlapping_editorial_lead_ids"]
        matched=sorted(set(leads)&authored.keys())
        not_written=sorted(set(leads)-authored.keys())
        # Source line equality is not knowledge equivalence.
        if not leads and not s["overlapping_41_proposal_ids"]:
            priority="P0_UNMAPPED_LAYOUT_LINE"
        elif len(leads)>1 or len(s["overlapping_41_proposal_ids"])>1:
            priority="P0_MULTIPLE_POSSIBLE_SEMANTIC_UNITS"
        elif not matched and not s["overlapping_teacher_only_draft_ids"]:
            priority="P1_NO_LINKED_COMPLETE_DRAFT"
        else:
            priority="P2_DRAFT_EXISTS_NEEDS_TEACHER_SEMANTIC_REVIEW"
        classes[priority]+=1
        out.append(dict(id=s["id"],course_track=s["course_track"],
             printed_page=s["printed_page"],pdfkit_line=s["pdfkit_line"],
             pdf_page_index=s["pdf_page_index"],source_line_sha256=s["source_line_sha256"],
             overlapping_historical_leads=leads,linked_pending_draft_candidate_ids=matched,
             historical_leads_without_manuscripts=not_written,
             existing_proposal_ids=s["overlapping_41_proposal_ids"],
             priority=priority,human_semantic_equivalence="UNDETERMINED",
             human_split_decision="REVIEW_PENDING",official_atom_id=None,
             official_atom_count_contribution=None,review_state="REVIEW_PENDING",
             teacher_approved=False,student_authoritative=False))
    by_track={}
    for t in TRACKS:
        rows=[r for r in out if r["course_track"]==t]
        drafted=[r for r in authored.values() if r["track"]==t]
        cde=[r for r in old["unnumbered_CDE_editorial_obligations"] if r["course_track"]==t]
        source_track=old["by_track"][t]
        must(len(rows)==source_track["numbered_source_markers"],"marker/track mismatch "+t)
        by_track[t]=dict(numbered_layout_review_obligations=len(rows),
            drafted_marker_overlaps=sum(bool(r["linked_pending_draft_candidate_ids"]) for r in rows),
            unmatched_orphan_markers=sum(r["priority"]=="P0_UNMAPPED_LAYOUT_LINE" for r in rows),
            historical_leads=source_track["historical_editorial_leads"],
            historical_leads_with_pending_draft=sum(r["track"]==t for r in authored.values() if r["candidate"].startswith("hs-semantic-pilot-")),
            unpublished_drafts=len(drafted),
            unnumbered_cde_editorial_obligations=len(cde),
            official_semantic_atoms=None,teacher_approved=0,student_authoritative=0)
    must(sum(v["numbered_layout_review_obligations"] for v in by_track.values())==315,"marker conservation")
    must(sum(v["unnumbered_cde_editorial_obligations"] for v in by_track.values())==32,"CDE conservation")
    must(sum(v["unpublished_drafts"] for v in by_track.values())==165,"draft conservation")
    return dict(schema="kb157-deterministic-source-obligations-not-official-atoms/1",
      standard_version="2017-edition-2020-revision",
      source_pdf_sha256=old["source_pdf_sha256"],
      printed_source_pages=61,
      numbered_layout_review_obligations=315,
      unnumbered_CDE_pending_proposals=32,
      historical_editorial_leads=239,
      historical_editorial_leads_with_unpublished_draft=124,
      historical_editorial_leads_without_unpublished_draft=115,
      pending_manuscripts=165,
      cross_page_and_same_page_source_relation_records_pending=89,
      source_risk_pages=53,
      line_overlap_not_semantic_equivalence=True,
      official_syllabus_scope_complete=False,
      crosspage_semantic_dedup_human_complete=False,
      official_atom_denominators={t:None for t in TRACKS},
      official_coverage_rate=None,teacher_approved=0,student_authoritative=0,
      triage_priority_counts=dict(classes),
      by_track=by_track,numbered_marker_review_rows=out,
      cde_unnumbered_review_ids=[r["id"] for r in old["unnumbered_CDE_editorial_obligations"]],
      interpretation="315 and 32 are nonadditive source-review obligations, never nationwide official knowledge atom denominators.")
def validate(d):
    expected=build()
    must(d==expected,"unexpected status, provenance, count or row mutation")
    must(len({r["id"] for r in d["numbered_marker_review_rows"]})==315,"duplicate source marker")
    for r in d["numbered_marker_review_rows"]:
        must(r["official_atom_id"] is None and r["official_atom_count_contribution"] is None and
         r["review_state"]=="REVIEW_PENDING" and not r["teacher_approved"] and
         not r["student_authoritative"] and r["human_semantic_equivalence"]=="UNDETERMINED",
         "forged curriculum freeze or approval")
    return True
def markdown(x):
    lines=["# KB157 K00｜七轨来源审查义务（不是官方课程原子分母）","",
    "版本：2017年版2020年修订；原始PDF仅在授权Mac验源，仓库仅保存SHA及元信息。",
    "315条编号排版标记、32条未编号CDE提案、239个历史编辑候选以及89条边界关系均有重叠，**绝不相加作为知识原子总数**。",
    "目前165份原创教师候审讲义，其中124条历史候选有对应稿、115条缺完整稿；官方七轨分母全部UNKNOWN，教师批准0。",
    "全部编号标记均是待语义拆分、去重的人工任务；未获审校不得给学生权威检索。","",
    "## 编号标记分流统计",""]
    for k,n in sorted(x["triage_priority_counts"].items()):
        lines.append(f"- {k}: {n}")
    lines+=["","## 七轨明细","",
          "| Track | 排版标记 | 带候审稿重叠的标记 | 候审稿 | CDE未编号候审提案 | 官方原子分母 |",
          "|---|---:|---:|---:|---:|---|"]
    for k in TRACKS:
        v=x["by_track"][k]
        lines.append(f'| {k} | {v["numbered_layout_review_obligations"]} | {v["drafted_marker_overlaps"]} | {v["unpublished_drafts"]} | {v["unnumbered_cde_editorial_obligations"]} | UNKNOWN |')
    lines+=["","## 下批人工与机器审查","",
    "优先核对未匹配和多义条款，按印刷页和PDFKit行SHA核验候选前提；跨页关系需要真人裁决等价/包含/无关，不能自动合并。",
    "进一步按官方原始课程要求逐条拆分语义并覆盖非编号课程要求，再为正式原子维护完整的内容、题族、条件校验和审核证据。",""]
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    a=p.parse_args();obj=build();validate(obj)
    targets=((OUT,encode(obj)),(REPORT,markdown(obj)))
    if a.write:
        for f,s in targets:f.write_text(s,encoding="utf-8")
    else:
        for f,s in targets:must(f.read_text(encoding="utf-8")==s,"artifact drift "+str(f))
    print("PASS KB157 315 numbered obligations + 32 CDE; 165 teacher drafts; official denominators UNKNOWN")
if __name__=="__main__":main()
