#!/usr/bin/env python3
"""Reproducible partial K00 atom *editorial candidates*; not official syllabus coverage.

Source annotations are locally authored after inspection of the original, pinned
2017/2020 curriculum PDF on Mac. No copyrighted passage is stored in this repo.
Never treat a numbered heading, proposed atom, draft lesson or schema pass as an
official atom denominator, teacher signoff or student-publishable artifact.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"curriculum/highschool_math/k00_batch31_core_atomic_drafts.tsv"
LEDGER=ROOT/"curriculum/highschool_math/official_pypdf59_reextract_batch26.json"
FROZEN=ROOT/"curriculum/highschool_math/official_numbered_clause_evidence_batch18.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH31_K00_PARTIAL_ATOM_AUDIT.json"
SOURCE_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
REEXTRACT_SHA="c0747fd67bba8261cd332ce76f130e014deb529efa999762f07aadb33dbda65f"
FROZEN_SHA="427ae60de66a528b73f44a16f5892fd07f7136621cf7f1dbc6ffd1685b8672da"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
PDFKIT_TEXT_EXAMINED=tuple(range(15,29))
ASSISTANT_VISUALLY_INSPECTED=(15,16,19,20,25,26,27,28,52)
VISUAL_BATCH31=(15,16,19,20,25,26,27,28)
VISUAL_RENDER_SHA={
    15:"eee18cb120b80e97c067b631a2802a0c230a81d9acdf31b5071141c92251fa1d",
    16:"ec85df524fb0c3f80b81543a97cb459207d293cd4eda323823ec7beca068ff71",
    19:"7409e56fcb069805f4a855bb56107a2f0963e2c3f9c9363a9003565ed34f73a5",
    20:"bc4dddd21d176ad4932a26e0d6a779242ae7f95b7f7695ef5d45b1b28b0f353f",
    25:"089ec0ad49ed257c29daa3ff88837c7909e64c99715ba2c1e7a88c2b7930687c",
    26:"5ae71127a5861219ed96e48f240712bea1bdb5a652d474547c14a453e0f4a37d",
    27:"54db1108b66d24f6b0b323709953b71b843555a3682401236d68fc21eaf0988e",
    28:"d8251b613256d2804c2d066662f3eccdabc4a6bfa3d6df4497b6e5c2d8f98326",
}
KINDS={"concept","theorem","method"}

def digest(path:Path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read_ledger():
    if digest(LEDGER)!=REEXTRACT_SHA or digest(FROZEN)!=FROZEN_SHA:
        raise ValueError("Immutable curriculum source ledger differs from reviewed baseline")
    d=json.loads(LEDGER.read_text(encoding="utf-8"))
    if (d["source"]["sha256"]!=SOURCE_SHA or d["source"]["pdf_total_pages"]!=188 or
        len(d["pages"])!=61 or len(d["enumerated_source_anchors"])!=317):
        raise ValueError("Source is not the pinned 2017/2020 official PDF ledger")
    if [p["printed_page"] for p in d["pages"]]!=list(range(13,74)):
        raise ValueError("Incomplete 61-page source")
    return d

def parse_seed(text):
    rows=[]
    seen=set()
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):continue
        parts=raw.split("|")
        if len(parts)!=5:raise ValueError("Seed must have exactly five fields")
        pg,section,kind,optional,goal=map(str.strip,parts)
        if not pg.isdecimal() or int(pg) not in PDFKIT_TEXT_EXAMINED:
            raise ValueError("Candidate outside inspected compulsory original text pages")
        pg=int(pg)
        if (not 2<=len(section)<=40 or kind not in KINDS or optional not in ("N","Y") or
            not 12<=len(goal)<=125 or "普通高中数学课程标准" in goal or "\u0000" in goal):
            raise ValueError("Incomplete/unsafe original atomic candidate")
        if goal in seen:raise ValueError("Repeated atom editorial description")
        seen.add(goal)
        rows.append((pg,section,kind,optional=="Y",goal))
    if not rows:raise ValueError("Empty candidate audit")
    if [x[0] for x in rows]!=sorted(x[0] for x in rows):
        raise ValueError("Source page ordering is needed for stable IDs")
    return rows

def build(seed=None,ledger=None):
    if ledger is not None and ledger != read_ledger():
        raise ValueError("Injected source ledger differs from immutable original")
    ledger=read_ledger() if ledger is None else ledger
    if (ledger["source"]["sha256"]!=SOURCE_SHA or len(ledger["pages"])!=61 or
        len(ledger["enumerated_source_anchors"])!=317):
        raise ValueError("Source substitution not permitted")
    pages={r["printed_page"]:r for r in ledger["pages"]}
    if any(p["pdf_page_index"]!=p["printed_page"]+7 for p in pages.values()):
        raise ValueError("Printed-to-PDF page offset drift")
    rows=parse_seed(SEED.read_text(encoding="utf-8") if seed is None else seed)
    counters=defaultdict(int);items=[]
    for page,section,kind,starred,original_goal in rows:
        src=pages[page]
        if "COMPULSORY" not in src["tracks_present"]:
            raise ValueError("Curriculum track cannot be inferred from a page with other track")
        counters[page]+=1
        id=f"KB31-CORE-P{page:03d}-A{counters[page]:03d}"
        items.append(dict(id=id,track="COMPULSORY",source_printed_page=page,
            source_pdf_index_zero_based=page+7,
            source_pdf_sha256=SOURCE_SHA,
            source_page_extracted_sha256=src["pdf_text_sha256"],
            section_project_label=section,kind_candidate=kind,
            original_project_authored_outcome=original_goal,
            optional_starred_non_exam=starred,
            official_clause_anchor_status="PAGE_LEVEL_ONLY_NOT_INDEPENDENTLY_MAPPED",
            official_atomic_id=None,
            matched_teacher_approved_lesson_ids=[],
            provisional_lesson_associations=[],
            teacher_review="PENDING",math_content_verification="NOT_CHECKED",
            review_status="EDITORIAL_ATOM_CANDIDATE_REVIEW_PENDING",
            student_publishable=False))
    candidate_ids={x["id"] for x in items}
    if len(candidate_ids)!=len(items):raise ValueError("Duplicate generated IDs")
    for x in items:
        if (x["official_atomic_id"] is not None or x["teacher_review"]!="PENDING" or
            x["student_publishable"] or x["matched_teacher_approved_lesson_ids"]):
            raise ValueError("Unreviewed atoms cannot masquerade as approved syllabus coverage")
    n_by_page=Counter(x["source_printed_page"] for x in items)
    page_rows=[]
    for p in ledger["pages"]:
        pg=p["printed_page"]
        status=("ASSISTANT_RENDERED_ORIGINAL_IMAGE_EXAMINED" if pg in ASSISTANT_VISUALLY_INSPECTED
                else "ASSISTANT_PDFKIT_TEXT_EXAMINED" if pg in PDFKIT_TEXT_EXAMINED
                else "AWAITING_ORIGINAL_CONTENT_INSPECTION")
        page_rows.append(dict(printed_page=pg,pdf_index_zero_based=pg+7,
             source_pypdf_page_sha256=p["pdf_text_sha256"],
             extraction_marker_occurrences=p["source_numbered_marker_count"],
             candidate_atom_count=n_by_page[pg],
             content_inspection=status,
             assistant_render_sha256=VISUAL_RENDER_SHA.get(pg),
             original_page_teacher_review="PENDING",
             unnumbered_requirements_completeness="UNKNOWN",
             official_atom_denominator=None))
    status_counts=Counter(p["content_inspection"] for p in page_rows)
    unexamined=[p["printed_page"] for p in page_rows if p["content_inspection"]=="AWAITING_ORIGINAL_CONTENT_INSPECTION"]
    content_pages=sorted(n_by_page)
    summary=dict(official_source_pages=61,original_pdf_sha256=SOURCE_SHA,
        entire_original_pdf_byte_verified_at_authoring=True,
        independent_pypdf_marker_occurrences=317,
        original_editorial_atomic_candidate_count=len(items),
        original_candidates_compulsory=len(items),
        new_atomic_candidate_pages=len(content_pages),
        first_pass_pdfkit_text_pages=len(PDFKIT_TEXT_EXAMINED),
        assistant_rendered_page_total=len(ASSISTANT_VISUALLY_INSPECTED),
        batch31_visual_page_sha_count=len(VISUAL_RENDER_SHA),
        assistant_rendered_pages_new=len(VISUAL_BATCH31),
        remaining_pages_uninspected=len(unexamined),
        teacher_verified_atomic_items=0,teacher_approved_lessons=0,
        full_official_atomic_denominator=None, official_content_coverage_rate=None,
        student_published_lessons=0)
    return json.dumps(dict(schema_version="kb-batch31-provisional-atoms-v1",
        status="PARTIAL_EDITORIAL_SOURCE_DECOMPOSITION_NOT_OFFICIAL_DENOMINATOR",
        source=dict(document="普通高中数学课程标准（2017年版2020年修订）",
          pinned_original_pdf_sha256=SOURCE_SHA,pypdf59_evidence_sha256=digest(LEDGER),
          original_pdf_committed_to_git=False,original_pdf_text_committed_to_git=False),
        summary=summary,
        by_track_official_denominators={t:None for t in TRACKS},
        by_track_editorial_candidate_counts={t:len(items) if t=="COMPULSORY" else 0 for t in TRACKS},
        page_inspection_status_counts=dict(sorted(status_counts.items())),
        pages=page_rows,items=items,
        warnings=["These are 87 ORIGINAL project-authored editorial proposals, not official numbered atoms or teaching lesson approvals.",
                  "Printed pages 15–28 were inspected through Mac PDFKit text; 8 were independently inspected as rendered images; previous printed page 52 remains image-inspected.",
                  "Source heading counts and machine source candidate totals are not authoritative denominators; cross-page statements and unnumbered requirements remain unatomized.",
                  "Starred optional content within compulsory chapter is flagged separately, not falsely promoted to elective A–E.",
                  "Any teacher status or student-visible answer based on these draft outcomes remains forbidden."]),
        ensure_ascii=False,indent=2)+"\n"

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--check",action="store_true")
    a.add_argument("--pdf",type=Path)
    a.add_argument("--image-dir",type=Path)
    args=a.parse_args()
    if args.pdf and digest(args.pdf)!=SOURCE_SHA:
        raise ValueError("Not the pinned official PDF; refuse source inspection")
    if args.image_dir:
        for pg,expected in VISUAL_RENDER_SHA.items():
            if digest(args.image_dir/f"stem_kb31_print_{pg}.png") != expected:
                raise ValueError(f"Rendered page {pg} does not match audited Mac evidence")
    v=build()
    if args.check:
        if REPORT.read_text(encoding="utf-8")!=v:raise SystemExit("K00 Batch31 source audit drift")
    else:REPORT.write_text(v,encoding="utf-8")
    d=json.loads(v)
    print("PASS K00",d["summary"]["original_editorial_atomic_candidate_count"],
          "original editor candidates on",d["summary"]["new_atomic_candidate_pages"],
          "pages; official denominators NULL")
if __name__=="__main__":main()
