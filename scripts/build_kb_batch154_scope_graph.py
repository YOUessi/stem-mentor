#!/usr/bin/env python3
"""Batch154 K00: source-line provenance graph and seven-track unresolved census ledger.

A source marker is neither an atom nor a lesson. Non-identical provenance is not
automatic semantic deduplication. No copyrighted text leaves the authorized Mac.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch148_official_clause_gate as old
import build_kb_batch154_crosswalk as latest

STD = old.OFFICIAL
ATOM = old.PROPOSALS
LEADS = old.ED_LEADS
CDE = ROOT / "docs/evaluation/KB_BATCH150_DE_SEMANTIC_BOUNDARY.json"
DRAFTS = ROOT / "docs/evaluation/KB_BATCH154_DEPTH_AUDIT.json"
CROSSWALK = latest.OUT
OUT = ROOT / "docs/evaluation/KB_BATCH154_SOURCE_GRAPH.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH154_SOURCE_GRAPH.md"
TRACKS = old.TRACKS
HASH = re.compile(r"[a-f0-9]{64}\Z")
LINE = re.compile(r"STD2020-SOURCELINE-P([0-9]+)-L([0-9]+)\Z")

def require(x, why):
    if not x:
        raise ValueError("KB154 source evidence graph: " + why)

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def encode(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"

def source_index():
    """Validate original signed positions, and construct independent line→source maps."""
    numbered, atom, leads, cde = load(STD), load(ATOM), load(LEADS), load(CDE)
    pdf_sha = old.validate_raw(numbered, atom, leads)
    require(cde["official_pdf_sha256"] == pdf_sha, "mismatched PDF revision (CDE)")
    require(cde["complete_official_course_census"] is False and
            all(v is None for v in cde["approved_atom_denominators"].values()), "false CDE completeness")
    require(len(cde["source_line_partition"]) == 122 and len(cde["proposals"]) == 32,
            "loss of unnumbered C/D/E source evidence")
    partition={}
    for line in cde["source_line_partition"]:
        match=LINE.fullmatch(line["line_id"])
        require(match is not None and
                (int(match[1]),int(match[2]))==(line["printed_page"],line["pdfkit_line"]),
                "source line identifier / position disagrees")
        require(line["classification"] in {"ELECTIVE_C","ELECTIVE_D","ELECTIVE_E","PARATEXT"} and
                bool(HASH.fullmatch(line["original_line_sha256"])) and
                line["teacher_review"] == "REVIEW_PENDING" and
                line["officially_certified"] is False and
                line["original_text_committed"] is False,
                "untrusted or counterfeit classified original line")
        require(line["line_id"] not in partition, "duplicated CDE source line")
        partition[line["line_id"]]=line
    require(set(z["printed_page"] for z in partition.values())=={69,70,71,72,73},
            "CDE 5-page source region incomplete")
    require(all(z["classification"]=="ELECTIVE_C" for z in partition.values() if
                z["printed_page"]==69 and z["pdfkit_line"]<=5), "page69 C boundary drift")
    require(all(z["classification"]=="ELECTIVE_D" for z in partition.values() if
                z["printed_page"]==73 and z["pdfkit_line"]<=12), "page73 D continuation drift")
    require(all(z["classification"]=="ELECTIVE_E" for z in partition.values() if
                z["printed_page"]==73 and 16<=z["pdfkit_line"]<=22), "page73 E optional examples drift")
    props={}
    for p in cde["proposals"]:
        require(p["id"] not in props and p["source_track"] in ("ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"),
                "duplicate or invalid CDE proposal")
        require(p["source_pdf_sha256"]==pdf_sha and
                p["teacher_review"]=="REVIEW_PENDING" and
                p["curriculum_scope_status"]=="EDITORIAL_PROPOSAL_NOT_APPROVED_ATOM" and
                p["official_knowledge_atom_id"] is None and
                p["student_authoritative"] is False and p["teacher_approved"] is False and
                p["lesson_complete"] is False, "false certified proposal")
        ids=p["source_line_ids"]; shas=p["source_line_sha256"]
        require(bool(ids) and len(ids)==len(shas)==len(set(ids)),
                "malformed CDE source-line list")
        for line_id,sha in zip(ids,shas):
            require(line_id in partition and partition[line_id]["classification"]==p["source_track"] and
                    partition[line_id]["original_line_sha256"]==sha, "CDE proposal source mismatch")
        require(p["is_school_elective_example"] == (p["source_track"]=="ELECTIVE_E"),
                "E is optional school elective, not nationwide required")
        props[p["id"]]=p
    counted=old.build()
    require(old.validate_report(counted), "upstream numbered source gate failed")
    source_markers={m["source_marker_id"]:m for m in counted["candidate_map"]}
    return numbered,atom,leads,cde,partition,props,counted,source_markers

def build():
    numbered,atom,leads,cde,partition,props,prior,source_markers=source_index()
    drafts=load(DRAFTS);cross=latest.build()
    require(cross==load(CROSSWALK), "latest manuscript gap report differs from source")
    require(drafts["total_teacher_only_drafts"]==145 and cross["total_pending_teacher_manuscripts"]==145,
            "source+draft revision drift")
    require(cross["matched_editorial_candidates"]==104 and
            cross["missing_editorial_candidates"]==135, "editorial source gap drift")
    # Build three different source populations; never sum them as a national denominator.
    marker_by_page=defaultdict(list); cde_by_page=defaultdict(list)
    for m in prior["candidate_map"]:
        marker_by_page[m["printed_page"]].append(m)
    for p in props.values():
        for line_id in p["source_line_ids"]:
            page=partition[line_id]["printed_page"]
            cde_by_page[page].append(p["id"])
    pages=[]
    for p in prior["source_pages"]:
        page=p["printed_page"]; mr=marker_by_page[page]
        require(p["numbered_source_markers"]==len(mr), "numbered source marker count drift")
        classed=[z for z in partition.values() if z["printed_page"]==page]
        class_counts=dict(sorted(Counter(z["classification"] for z in classed).items()))
        risk=set()
        if p["numbered_markers_without_line_overlap"]: risk.add("NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP")
        if page in {69,73}:risk.add("MIDPAGE_TRACK_TRANSITION")
        if page in {72,73}:risk.add("CROSSPAGE_ELECTIVE_D_CONTINUATION")
        if page>=69 and not cde_by_page[page]:risk.add("NO_UNNUMBERED_PROPOSAL_FOR_SOURCE_PAGE")
        if not p["numbered_source_markers"]:risk.add("ZERO_NUMBERED_MARKERS_NOT_ZERO_REQUIREMENTS")
        pages.append(dict(printed_page=page,pdf_page_index=p["pdf_page_index"],
            pdf_text_sha256=p["pdf_text_sha256"],
            numbered_source_markers=len(mr),
            numbered_without_existing_proposal_or_lead=p["numbered_markers_without_line_overlap"],
            numbered_marker_ids=[x["source_marker_id"] for x in mr],
            original_cde_lines=len(classed),
            cde_original_line_classifications=class_counts,
            cde_semantic_proposal_ids=sorted(set(cde_by_page[page])),
            content_requirements_in_unenumerated_lines="UNKNOWN",
            semantic_atom_count="UNKNOWN",
            teacher_scope_review="REVIEW_PENDING",
            risk_flags=sorted(risk)))
    # Provenance line mapping for unnumbered C/D/E proposals is deliberately NOT joined
    # to numbered markers by topic or line text similarity.
    junction=[]
    for p in sorted(props.values(),key=lambda x:x["id"]):
        ordered=[partition[i] for i in p["source_line_ids"]]
        junction.append(dict(proposal_id=p["id"],course_track=p["source_track"],
            original_paraphrase=p["original_paraphrase"],
            source_line_ids=list(p["source_line_ids"]),
            source_line_sha256=list(p["source_line_sha256"]),
            pages=sorted(set(x["printed_page"] for x in ordered)),
            kind=p["content_type"],
            is_school_elective_example=p["is_school_elective_example"],
            officially_certified=False,official_atom_id=None,
            semantic_duplicate_with_any_other_proposal="UNDETERMINED",
            teacher_review="REVIEW_PENDING",linked_approved_lesson_ids=[]))
    matched_draft_ids=set(cross["unmatched_candidate_ids"])
    by_track={}
    for t in TRACKS:
        marks=[m for m in prior["candidate_map"] if m["course_track"]==t]
        cde_props=[p for p in junction if p["course_track"]==t]
        track_gap=cross["by_track"][t]
        by_track[t]=dict(source_numbered_markers=len(marks),
            numbered_markers_without_existing_line_overlap=sum(
                not(m["provisional_atom_proposal_ids"] or m["editorial_lead_ids"]) for m in marks),
            provisional_41_atom_proposals=sum(r["track"]==t for r in atom["records"]),
            nonnumbered_cde_editorial_proposals=len(cde_props),
            historic_editorial_leads=track_gap["editorial_candidates"],
            draft_linked_editorial_leads=track_gap["linked_teacher_only_drafts"],
            draft_missing_editorial_leads=track_gap["missing_editorial_lead_draft"],
            unpublished_teacher_manuscripts=track_gap["total_teacher_only_drafts"],
            official_atomic_denominator=None,official_approved=0,
            student_authoritative=0)
    require(sum(x["source_numbered_markers"] for x in by_track.values())==315 and
            sum(x["nonnumbered_cde_editorial_proposals"] for x in by_track.values())==32 and
            sum(x["historic_editorial_leads"] for x in by_track.values())==239 and
            sum(x["draft_linked_editorial_leads"] for x in by_track.values())==104 and
            sum(x["draft_missing_editorial_leads"] for x in by_track.values())==135 and
            sum(x["unpublished_teacher_manuscripts"] for x in by_track.values())==145,
            "cross-track conservation law broken")
    todo=sorted((p for p in pages if p["risk_flags"]),
        key=lambda p:(-len(p["risk_flags"]),
            -p["numbered_without_existing_proposal_or_lead"],p["printed_page"]))
    return dict(schema="kb154-full-61-page-source-line-census-review-graph/1",
        official_standard="2017-edition-2020-revision",
        source_pdf_sha256=numbered["source"]["sha256"],source_pdf_total_pages=188,
        source_pages_scanned=61,source_numbered_markers=315,
        provisional_41_semantic_proposals=41,original_cde_lines_classified=122,
        cde_proposals_from_unnumbered_sources=32,
        historical_editorial_leads=239,pending_teacher_manuscripts=145,
        linked_editorial_leads=104,missing_editorial_leads=135,
        risk_pages=len(todo),by_track=by_track,
        pages=pages,cde_unnumbered_proposal_junction=junction,
        prioritized_review_pages=[dict(printed_page=p["printed_page"],risk_flags=p["risk_flags"],
            markers_unpaired=p["numbered_without_existing_proposal_or_lead"]) for p in todo],
        official_atom_denominators={t:None for t in TRACKS},
        seven_track_official_census_complete=False,
        unnumbered_source_requirements_human_split_complete=False,
        cross_page_semantic_dedup_human_review_complete=False,
        automatically_merged_source_clauses=0,
        real_teacher_approved=0,student_authoritative=0,
        warning="315 numbered source markers, 32 unnumbered CDE proposals, 41 proposals, 239 leads, and 145 drafts are NOT additive, not official knowledge atoms or coverage rates.")

def validate(v):
    require(len(v["pages"])==61 and {x["printed_page"] for x in v["pages"]}==set(range(13,74)),
            "incomplete 61-page source census")
    require(len(v["cde_unnumbered_proposal_junction"])==32 and
            len({x["proposal_id"] for x in v["cde_unnumbered_proposal_junction"]})==32, "lost CDE proposal")
    require(v["source_numbered_markers"]==315 and v["original_cde_lines_classified"]==122 and
            v["linked_editorial_leads"]+v["missing_editorial_leads"]==239 and
            v["pending_teacher_manuscripts"]==145 and
            len(v["prioritized_review_pages"])==v["risk_pages"],"conservation mismatch")
    require(all(v["official_atom_denominators"][t] is None and
           v["by_track"][t]["official_atomic_denominator"] is None and
           v["by_track"][t]["official_approved"]==0 and
           v["by_track"][t]["student_authoritative"]==0 for t in TRACKS),
           "forged official count/approval")
    require(not v["seven_track_official_census_complete"] and
            not v["unnumbered_source_requirements_human_split_complete"] and
            not v["cross_page_semantic_dedup_human_review_complete"] and
            v["automatically_merged_source_clauses"]==v["real_teacher_approved"]==
            v["student_authoritative"]==0,"false completed curriculum / release")
    for p in v["pages"]:
        require(p["content_requirements_in_unenumerated_lines"]=="UNKNOWN" and
                p["semantic_atom_count"]=="UNKNOWN" and
                p["teacher_scope_review"]=="REVIEW_PENDING","uncertified source page")
    for p in v["cde_unnumbered_proposal_junction"]:
        require(p["teacher_review"]=="REVIEW_PENDING" and
                p["official_atom_id"] is None and
                p["officially_certified"] is False and
                not p["linked_approved_lesson_ids"],"false CDE source certification")
    return True

def render(v):
    t=["# KB154｜61页正式来源索引×315编号锚×122条CDE分轨行×32个未编号提案",
       "","**范围事实层 != 已核定国家课标知识原子分母**。未经教师逐条确认，七轨分母均为UNKNOWN，学生可发布数0。",
       "",f"PDF来源SHA256：{v['source_pdf_sha256']}；61页已抽取来源索引，不代表语义内容已逐条完成。",
       f"新核对122条C/D/E非空分类来源行、32个编辑候审提案。{v['risk_pages']}页存在待审来源风险。","",
       "| 课程轨道 | 编号来源标记 | 41原子提案 | 额外CDE未编号提案 | 历史编辑线索 | 已关联候审稿线索 | 尚缺稿线索 | 课标原子分母 |",
       "|---|---:|---:|---:|---:|---:|---:|---|"]
    for track in TRACKS:
        r=v["by_track"][track]
        t.append(f"| {track} | {r['source_numbered_markers']} | {r['provisional_41_atom_proposals']} | {r['nonnumbered_cde_editorial_proposals']} | {r['historic_editorial_leads']} | {r['draft_linked_editorial_leads']} | {r['draft_missing_editorial_leads']} | UNKNOWN |")
    t+=["","## 多来源真实语义审校门槛","",
       "来源锚的页码/行号/哈希只证明定位；同页重叠不代表语义相同，不得自动合并。",
       "69页C转D、73页D续句转E、72→73体育例子跨页：源行逐条保存轨道，不按整页分轨。",
       "32个C/D/E候选仅是来源行的原创转述提案，E类是学校自选示例，不得强制作为全国统一必修要求。",
       "必须补齐未编号内容→明确数学对象/量词/条件→人工跨页语义去重→核定原子唯一ID→教师审核，才能计算正式课程分母。","",
       "## 优先逐页审校队列（源数据元信息，不含标准原文）","",
       "| 印刷页 | 未配对编号标记 | 风险原因 |","|---:|---:|---|"]
    for p in v["prioritized_review_pages"]:
        t.append(f"| {p['printed_page']} | {p['markers_unpaired']} | {', '.join(p['risk_flags'])} |")
    t+=["","完整61页明细、315项编号IDs与32条候审关联证据见同名JSON。未作课程原子已完成的虚假计数。",""]
    return "\n".join(t)

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    a=p.parse_args();v=build();validate(v)
    if a.write:
        OUT.write_text(encode(v),encoding="utf-8")
        REPORT.write_text(render(v),encoding="utf-8")
    else:
        require(load(OUT)==v and REPORT.read_text(encoding="utf-8")==render(v),
                "materialized evidence ledger drift")
    print(f"PASS KB154 source graph: 61 pages, 315 numbered markers, 122 CDE source lines, 32 unnumbered proposals, {v['risk_pages']} risk pages; 145 pending, 104 linked/135 missing, official denominator UNKNOWN")
if __name__=="__main__":
    main()
