#!/usr/bin/env python3
"""Source-marker-to-proposal audit. Markers, proposals and drafts are NOT official atoms."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "curriculum/highschool_math/official_numbered_clause_evidence_batch18.json"
PROPOSALS = ROOT / "curriculum/highschool_math/k00_batch133_atomic_proposals.json"
ED_LEADS = ROOT / "docs/evaluation/KB_BATCH147_SOURCE_BOUNDARY_QUEUE.json"
DRAFT_AUDIT = ROOT / "docs/evaluation/KB_BATCH147_DEPTH_AUDIT.json"
OUT = ROOT / "docs/evaluation/KB_BATCH148_NUMBERED_CLAUSE_RECONCILIATION.json"
MD = ROOT / "docs/evaluation/KB_BATCH148_NUMBERED_CLAUSE_RECONCILIATION.md"
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A", "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")
HASH = re.compile(r"^[0-9a-f]{64}$")

def require(condition, message):
    if not condition:
        raise ValueError("K00 official marker gate: " + message)

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"

def validate_raw(numbered, atom, leads):
    source = numbered["source"]
    sha = source["sha256"]
    require(bool(HASH.fullmatch(sha)) and sha == atom["source_pdf_sha256"] == leads["source_pdf_sha256"], "source PDF SHA drift")
    require(source["pdf_total_pages"] == 188 and source["printed_page_start"] == 13 and source["printed_page_end"] == 73, "wrong syllabus source/page range")
    pages = numbered["pages"]
    require(len(pages) == 61 and {p["printed_page"] for p in pages} == set(range(13, 74)), "missing curriculum source page")
    require(all(p["pdf_page_index"] == p["printed_page"] + 7 and HASH.fullmatch(p["pdf_text_sha256"]) for p in pages), "untrusted PDF page index or digest")
    anchors = numbered["enumerated_source_anchors"]
    require(len(anchors) == 315 and len({v["id"] for v in anchors}) == 315, "numbered source anchor loss/dup")
    require(all(v["id"] == f'STD2020-P{v["printed_page"]}-L{v["line_number"]:03d}' and
                v["pdf_page_index"] == v["printed_page"] + 7 and v["track"] in TRACKS and
                v["printed_page"] in range(13, 74) and v["line_number"] >= 1 and
                bool(HASH.fullmatch(v["line_sha256"])) and
                v["status"] == "SOURCE_ENUMERATION_UNREVIEWED_NOT_OFFICIAL_ATOM" and
                v["teacher_review"] == "PENDING" and not v["approved_lesson_ids"] for v in anchors),
            "counterfeit numbered marker or authority")
    require(sum(p["source_numbered_marker_count"] for p in pages) == len(anchors), "marker/page count drift")
    contract = numbered["denominator_contract"]
    require(contract["official_total_numbered_source_candidates"] == len(anchors) and
            contract["source_page_denominator"] == 61 and
            contract["by_track_source_numbered_candidates"] == {t:sum(v["track"]==t for v in anchors) for t in TRACKS} and
            contract["official_atomic_knowledge_denominator"] is None and
            contract["is_full_official_atomic_inventory"] is False and
            contract["teacher_approved_clauses"] == 0, "false syllabus denominator/approval")
    rows = atom["records"]
    require(len(rows) == 41 and atom["proposed_count"] == 41 and len({r["id"] for r in rows}) == 41, "bad 41 proposed requirements")
    require(atom["official_atom_denominator"] is None and not atom["full_source_census_complete"] and
            not atom["teacher_approved_count"] and not atom["student_authoritative_count"], "false 41 atom census")
    ids={r["id"] for r in rows}
    for r in rows:
        s=r["source_lock"]
        require(r["track"] in TRACKS and r["knowledge_type"] in ("Concept","Theorem","Method") and
                r["source_pdf_sha256"] == sha and r["atomization_review"] == "REVIEW_PENDING" and
                r["official_atom_id"] is None and r["teacher_approval"] is None and
                r["teacher_solution_visibility"] == "TEACHER_ONLY" and
                not r["formal_proof_certified"] and not r["student_authoritative"], "unreviewed proposal forged")
        require(s["printed_page"] in range(13,74) and 0<s["start_line"]<=s["end_line"] and
                len(s["line_sha256"]) == s["end_line"]-s["start_line"]+1 and
                all(HASH.fullmatch(v) for v in s["line_sha256"]+[s["span_sha256"]]), "bad proposal line chain")
        require(all(x in ids and x != r["id"] for x in r["prerequisite_proposals"]), "orphan/cyclic direct prerequisite")
    # Source/editorial proposals may overlap by design; never collapse by matching a line.
    candidates=leads["candidates"]
    require(len(candidates)==239 and len({v["id"] for v in candidates})==239 and
            leads["official_atom_census_completed"] is False and
            all(leads["official_denominators"].get(t) is None for t in TRACKS) and
            not leads["teacher_approved_atoms"] and not leads["student_authoritative_atoms"] and
            not leads["automatically_merged_atoms"], "false 239 official atom count")
    for c in candidates:
        require(c["track"] in TRACKS and c["page"] in range(13,74) and
                0 < c["start"] <= c["end"] and bool(HASH.fullmatch(c["span_sha"])) and
                c["semantic_review"] == "REVIEW_PENDING" and c["official_atom_id"] is None and
                not c["teacher_approved"], "invalid editorial candidate")
    return sha

def build():
    numbered,atom,leads = read(OFFICIAL),read(PROPOSALS),read(ED_LEADS)
    manuscript_audit = read(DRAFT_AUDIT)
    require(manuscript_audit["total_teacher_only_drafts"] == 95 and
            sum(manuscript_audit["by_track"].values()) == 95, "95 manuscript inventory drift")
    sha = validate_raw(numbered,atom,leads)
    candidates=leads["candidates"]
    proposal=atom["records"]
    by_page=defaultdict(list); by_page_prop=defaultdict(list); by_page_ed=defaultdict(list)
    for a in numbered["enumerated_source_anchors"]: by_page[a["printed_page"]].append(a)
    for v in proposal: by_page_prop[v["source_lock"]["printed_page"]].append(v)
    for v in candidates: by_page_ed[v["page"]].append(v)
    marker_rows=[]
    for a in sorted(numbered["enumerated_source_anchors"],key=lambda r:(r["printed_page"],r["line_number"])):
        page,ln,track=a["printed_page"],a["line_number"],a["track"]
        prop=sorted(v["id"] for v in by_page_prop[page] if v["track"]==track and
                    v["source_lock"]["start_line"]<=ln<=v["source_lock"]["end_line"])
        ed=sorted(v["id"] for v in by_page_ed[page] if v["track"]==track and
                  v["start"]<=ln<=v["end"])
        marker_rows.append(dict(source_marker_id=a["id"],printed_page=page,line=ln,
           course_track=track,source_line_sha256=a["line_sha256"],
           provisional_atom_proposal_ids=prop,editorial_lead_ids=ed,
           source_overlap_only=True,semantic_equivalence="UNDETERMINED",
           teacher_review="REVIEW_PENDING",official_atom_id=None,
           source_marker_is_official_atom=False,student_authoritative=False))
    by_track={}
    for track in TRACKS:
        marks=[m for m in marker_rows if m["course_track"]==track]
        by_track[track]=dict(numbered_source_markers=len(marks),
            marker_with_provisional_atom_line_overlap=sum(bool(m["provisional_atom_proposal_ids"]) for m in marks),
            marker_with_editorial_lead_line_overlap=sum(bool(m["editorial_lead_ids"]) for m in marks),
            marker_without_any_matched_line=sum(not(m["editorial_lead_ids"] or m["provisional_atom_proposal_ids"]) for m in marks),
            source_proposal_rows=sum(v["track"]==track for v in proposal),
            editorial_leads=sum(v["track"]==track for v in candidates),
            deep_teacher_pending_drafts=manuscript_audit["by_track"][track],
            official_knowledge_atom_denominator=None,teacher_approved=0)
    pages=[]
    for raw in numbered["pages"]:
        page=raw["printed_page"];marks=by_page[page]
        pages.append(dict(printed_page=page,pdf_page_index=raw["pdf_page_index"],
                          pdf_text_sha256=raw["pdf_text_sha256"],numbered_source_markers=len(marks),
                          provisional_atom_proposals=len(by_page_prop[page]),
                          historical_editorial_leads=len(by_page_ed[page]),
                          numbered_markers_without_line_overlap=sum(
                            not(m["provisional_atom_proposal_ids"] or m["editorial_lead_ids"])
                            for m in marker_rows if m["printed_page"]==page),
                          unnumbered_requirement_status="UNKNOWN_REQUIRES_HUMAN_SCOPE_SPLIT",
                          scope_review="REVIEW_PENDING",official_atoms_certified=0))
    return dict(schema="kb148-official-source-markers-not-knowledge-atom-denominator/1",
        source_pdf_sha256=sha,source_kind="2017_2020_REVISED_SYLLABUS_ORIGINAL",
        source_scan_pages=61,source_pdf_total_pages=188,
        source_numbered_marker_count=len(marker_rows),provisional_atom_proposal_count=len(proposal),
        historical_editorial_leads=len(candidates),teacher_pending_manuscripts=leads["teacher_pending_manuscripts"],
        relation_edges_pending=len(leads["candidate_relation_edges"]),
        candidate_map=marker_rows,source_pages=pages,by_track=by_track,
        official_atom_denominators={t:None for t in TRACKS},
        official_atomic_census_complete=False,
        unnumbered_clause_atomization_complete=False,
        crosspage_semantic_dedup_complete=False,
        human_semantic_merges_approved=0,
        teacher_approved=0,student_authoritative=0,
        warning="315 original numbered source markers, 41 proposed atoms, 239 editorial leads and 95 drafts are different non-equivalent populations; these are NOT official course coverage percentages")

def validate_report(v):
    require(set(v["by_track"]) == set(TRACKS) and set(v["official_atom_denominators"]) == set(TRACKS) and
            all(x is None for x in v["official_atom_denominators"].values()),"invented denominator")
    require(len(v["candidate_map"])==315 and len({r["source_marker_id"] for r in v["candidate_map"]})==315 and
            len(v["source_pages"])==61 and sum(r["numbered_source_markers"] for r in v["source_pages"])==315,
            "marker/page mapping lost")
    for m in v["candidate_map"]:
        require(m["course_track"] in TRACKS and m["teacher_review"]=="REVIEW_PENDING" and
                m["semantic_equivalence"]=="UNDETERMINED" and m["source_marker_is_official_atom"] is False and
                m["official_atom_id"] is None and m["source_overlap_only"] is True and
                m["student_authoritative"] is False, "forged semantic approval")
    require(not any(v[k] for k in ("official_atomic_census_complete","unnumbered_clause_atomization_complete",
              "crosspage_semantic_dedup_complete","human_semantic_merges_approved","teacher_approved","student_authoritative")),
            "false complete/approved claim")
    return True

def render(v):
    lines=["# K00 Batch148｜315个编号来源标记 × 41个原子提案 × 239个编辑线索审计","",
      "**只基于已哈希锁定的来源元数据定位，绝不把编号标记、行区间匹配、讲义计数等同于国家课标知识原子总数。**","",
      f"扫描范围：课标印刷页13–73（{v['source_scan_pages']}页，原始PDF {v['source_pdf_total_pages']}页）。",
      f"编号标记：{v['source_numbered_marker_count']}；原子编辑提案：{v['provisional_atom_proposal_count']}；旧线索：{v['historical_editorial_leads']}；教师候审讲义：{v['teacher_pending_manuscripts']}。","",
      "| 课程轨道 | 原始编号来源标记 | 与41提案同行交集 | 与239线索同行交集 | 无同行交集 | 正式原子分母 |",
      "|---|---:|---:|---:|---:|---|"]
    for t,a in v["by_track"].items():
        lines.append(f"| {t} | {a['numbered_source_markers']} | {a['marker_with_provisional_atom_line_overlap']} | {a['marker_with_editorial_lead_line_overlap']} | {a['marker_without_any_matched_line']} | UNKNOWN |")
    lines.extend(["","## 人工核定必要工作","",
      "1. 逐条读取编号要求及其前后文，逐句拆出概念、定理、方法、建模活动并审查跨页续句。",
      "2. 对同一数学思想在不同轨道的出现建立保留/合并裁决记录；当前同行仅是候选，不得自动归并。",
      "3. 特别补录所有未编号要求、选修D/E和非必选学校选修示例，最终把实际核定集合冻结才有分母。",
      "4. 真实教师签字并将版本/许可/数学条件审核证据纳入CI后才允许APPROVED。",
      "","## 61页逐页未完成范围","",
      "| 印刷页 | 标记 | 原子提案 | 编辑线索 | 没有同行交集的标记 |",
      "|---:|---:|---:|---:|---:|"])
    for p in v["source_pages"]:
        lines.append(f"| {p['printed_page']} | {p['numbered_source_markers']} | {p['provisional_atom_proposals']} | {p['historical_editorial_leads']} | {p['numbered_markers_without_line_overlap']} |")
    lines.extend(["","所有编号锚、同行映射与未审阅状态见同名JSON。文件不包含版权课标原文。",""])
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write",action="store_true");mode.add_argument("--check",action="store_true")
    args=p.parse_args()
    v=build();validate_report(v)
    if args.write:
        OUT.write_text(encode(v),encoding="utf-8")
        MD.write_text(render(v),encoding="utf-8")
    else:
        require(read(OUT)==v and MD.read_text(encoding="utf-8")==render(v),"materialized coverage report drift")
    print("PASS K00 Batch148: 315 numbered anchors/61 source pages; 41 proposals, 239 leads; seven official atom denominators UNKNOWN")

if __name__=="__main__":main()
