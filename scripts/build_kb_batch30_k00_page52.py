#!/usr/bin/env python3
"""K00: rendered-source visual audit of *one* original syllabus page (52).

Assistant inspected Mac PDFKit-rendered page 60 (0-based PDF index 59) from
pinned official PDF. This only settles the 315/317 *marker occurrences* drift,
not clause atomization or a teacher-approved curriculum denominator.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"curriculum/highschool_math/official_numbered_clause_evidence_batch18.json"
REEXTRACT=ROOT/"curriculum/highschool_math/official_pypdf59_reextract_batch26.json"
OUT=ROOT/"docs/evaluation/KB_BATCH30_K00_PAGE52_VISUAL_MARKER_AUDIT.json"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
RENDER_SHA="50de0f8c0bbfb53484b5e31b0aebc38e8bb80e3ae1c9f957cf305c1134fb9076"

def load(p):return json.loads(p.read_text(encoding="utf8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def build(old=None,new=None):
    old=load(ORIGINAL) if old is None else old
    new=load(REEXTRACT) if new is None else new
    for x in (old,new):
        if x["source"]["sha256"]!=PDF_SHA or x["source"]["pdf_total_pages"]!=188:
            raise ValueError("Pinned official source PDF changed")
        if len(x["pages"])!=61:raise ValueError("Expected full 61-page machine ledger")
        if [v["printed_page"] for v in x["pages"]]!=list(range(13,74)):
            raise ValueError("Missing source scope page")
    if len(old["enumerated_source_anchors"])!=315 or len(new["enumerated_source_anchors"])!=317:
        raise ValueError("Historical 315/317 counts changed")
    byold=[r for r in old["enumerated_source_anchors"] if r["printed_page"]==52]
    bynew=[r for r in new["enumerated_source_anchors"] if r["printed_page"]==52]
    # Mac PDFKit rendered source image independently inspected. Two independent
    # visual groups: Sequence limits are not counts of educational atoms.
    expected=["（１）","（２）","（３）","（４）","（５）","（１）","（２）","（３）"]
    expected_old=["（１）","（３）","（５）","（１）","（２）","（３）"]
    if [r["marker"] for r in bynew]!=expected or [r["marker"] for r in byold]!=expected_old:
        raise ValueError("Frozen page52 visual-check anchor sequence drift")
    if any(r["track"]!="ELECTIVE_A" or r["pdf_page_index"]!=59 for r in bynew+byold):
        raise ValueError("Page52 track or PDF index drift")
    extras=[
        dict(marker="（２）",section="1. 数列极限",historical_ledger="OMITTED",
             rendered_original="VISUALLY_PRESENT",normalized_reextract="PRESENT",
             anchor_id=bynew[1]["id"],source_line_sha256=bynew[1]["line_sha256"]),
        dict(marker="（４）",section="1. 数列极限",historical_ledger="OMITTED",
             rendered_original="VISUALLY_PRESENT",normalized_reextract="PRESENT",
             anchor_id=bynew[3]["id"],source_line_sha256=bynew[3]["line_sha256"])
    ]
    return json.dumps(dict(
        schema_version="kb-batch30-p52-original-visual-evidence-v1",
        source=dict(description="Ordinary high-school mathematics curriculum standard (2017 edition, 2020 revision)",
            original_pdf_sha256=PDF_SHA,original_pdf_total_pages=188,
            printed_page=52,pdf_page_index_zero_based=59,render="macOS PDFKit at 2x resolution",
            original_page_png_sha256=RENDER_SHA,image_committed_to_git=False,
            visual_verification_method="ASSISTANT_VISUAL_INSPECTION_OF_RENDERED_ORIGINAL_NOT_HUMAN_TEACHER_REVIEW",
            original_pdf_embedded_in_git=False,original_paragraphs_copied=False),
        source_ledger_sha256=dict(historical=sha(ORIGINAL),reextracted=sha(REEXTRACT)),
        marker_audit=dict(historical_page52_count=6,rendered_original_page52_count=8,
            reextracted_page52_count=8,section_1_sequence=expected[:5],
            section_2_sequence=expected[5:],two_historically_omitted_numbered_markers=extras,
            resolved_issue="NUMBERED_MARKER_OCCURRENCE_EXTRACTION_OMISSION_IN_HISTORICAL_LEDGER",
            numbered_markers_are_atomic_knowledge_units=False),
        global_scope=dict(source_pages=61,assistant_visually_rechecked_pages=1,
            remaining_without_assistant_visual_recheck=60,teacher_visually_rechecked_pages=0,
            frozen_extractor_marker_count=315,source_reextract_marker_count=317,
            new_count_for_marker_occurrence_audit=317,
            verified_official_atom_denominators={
                t:None for t in ("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")},
            official_knowledge_atom_coverage_rate=None,teacher_approved_lessons=0),
        warnings=["The original page visibly has five subsection markers under sequence limits and three under function limits: eight occurrences, not eight atomic learning outcomes.",
            "Batch18 missed the (2) and (4) markers in the first group on printed page 52; the pinned 317 re-extraction matches the render.",
            "One page is visually reviewed by an assistant only; 60 printed pages and all unnumbered requirements still lack corresponding visual review.",
            "This is not certification of official syllabus atoms, formal proofs, source licensing or teacher review."]),ensure_ascii=False,indent=2)+"\n"

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
    result=build()
    if a.check:
        if OUT.read_text(encoding="utf8")!=result:raise SystemExit("Batch30 page52 K00 audit drift")
    else:OUT.write_text(result,encoding="utf8")
    print("PASS K00 page52 visually checked: rendered 5+3=8 markers, historical 6 omitted 2; 1/61 assistant-viewed, official atoms NULL")

if __name__=="__main__":main()
