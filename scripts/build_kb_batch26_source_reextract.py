#!/usr/bin/env python3
"""Batch26 K00: explicit extractor-drift audit, never a syllabus atom counter.

The pinned source PDF is NOT committed. A machine re-extracts a legally
retrieved original on the Mac with pypdf 5.9.0; only page/line hashes and
marker positions may enter Git.  A different extractor may legitimately
split lines differently.  Neither ledger is an authoritative atomization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "curriculum/highschool_math/official_numbered_clause_evidence_batch18.json"
REEXTRACTED = ROOT / "curriculum/highschool_math/official_pypdf59_reextract_batch26.json"
OUTPUT = ROOT / "docs/evaluation/KB_BATCH26_K00_PDF_REEXTRACTION_AUDIT.json"
EXPECTED_PDF_SHA = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
FROZEN_LEDGER_SHA = "427ae60de66a528b73f44a16f5892fd07f7136621cf7f1dbc6ffd1685b8672da"
REEXTRACT_LEDGER_SHA = "c0747fd67bba8261cd332ce76f130e014deb529efa999762f07aadb33dbda65f"
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A", "ELECTIVE_B",
          "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_source(ledger: dict):
    if ledger["source"]["sha256"] != EXPECTED_PDF_SHA:
        raise ValueError("Wrong original PDF SHA; do not silently replace source")
    if ledger["source"]["pdf_total_pages"] != 188:
        raise ValueError("Wrong original PDF page count")
    pages = ledger["pages"]
    if len(pages) != 61 or [r["printed_page"] for r in pages] != list(range(13, 74)):
        raise ValueError("Incomplete or duplicated official content pages")
    seen = set()
    for row in pages:
        if row["pdf_page_index"] != row["printed_page"] + 7:
            raise ValueError("Printed page -> PDF index drift")
        if set(row["tracks_present"]) - set(TRACKS):
            raise ValueError("Unknown source track")
        if len(row["pdf_text_sha256"]) != 64:
            raise ValueError("Bad page hash")
    by_page = Counter()
    for m in ledger["enumerated_source_anchors"]:
        if m["id"] in seen:
            raise ValueError("Repeated numbered marker ID")
        seen.add(m["id"])
        if not 13 <= m["printed_page"] <= 73 or m["track"] not in TRACKS:
            raise ValueError("Bad source marker scope")
        if m["pdf_page_index"] != m["printed_page"] + 7:
            raise ValueError("Marker PDF index invalid")
        if not 1 <= m["line_number"] <= 1000 or len(m["line_sha256"]) != 64:
            raise ValueError("Marker hash or position invalid")
        if m["teacher_review"] != "PENDING" or m["approved_lesson_ids"]:
            raise ValueError("Fabricated source authority")
        by_page[m["printed_page"]] += 1
    if any(by_page[p["printed_page"]] != p["source_numbered_marker_count"] for p in pages):
        raise ValueError("Page marker counts do not reconcile")
    if sum(ledger["denominator_contract"]["by_track_source_numbered_candidates"].values()) != len(seen):
        raise ValueError("Track candidate ledger mismatch")
    if ledger["denominator_contract"]["official_atomic_knowledge_denominator"] is not None:
        raise ValueError("Unreviewed marker count falsely promoted to official atomic denominator")
    return ledger


def build(old=None, new=None):
    if hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() != FROZEN_LEDGER_SHA:
        raise ValueError("Frozen 315-marker ledger SHA changed; explicit rebaseline needed")
    if hashlib.sha256(REEXTRACTED.read_bytes()).hexdigest() != REEXTRACT_LEDGER_SHA:
        raise ValueError("Pinned 317-marker re-extraction SHA changed; explicit rebaseline needed")
    old = validate_source(old if old is not None else load(ORIGINAL))
    new = validate_source(new if new is not None else load(REEXTRACTED))
    if old["source"]["sha256"] != new["source"]["sha256"]:
        raise ValueError("Compared different documents")
    old_page = {r["printed_page"]: r for r in old["pages"]}
    new_page = {r["printed_page"]: r for r in new["pages"]}
    rows = []
    for p in range(13, 74):
        a, b = old_page[p], new_page[p]
        am = [x for x in old["enumerated_source_anchors"] if x["printed_page"] == p]
        bm = [x for x in new["enumerated_source_anchors"] if x["printed_page"] == p]
        old_lines = {(x["marker"], x["line_sha256"]) for x in am}
        new_lines = {(x["marker"], x["line_sha256"]) for x in bm}
        rows.append(dict(printed_page=p, pdf_page_index=p+7,
            frozen_marker_occurrences=len(am), reextracted_marker_occurrences=len(bm),
            delta=len(bm)-len(am), frozen_page_text_sha256=a["pdf_text_sha256"],
            reextracted_page_text_sha256=b["pdf_text_sha256"],
            page_text_hash_matches=a["pdf_text_sha256"]==b["pdf_text_sha256"],
            equal_marker_line_hash_pairs=len(old_lines & new_lines),
            frozen_unique_marker_line_hash_pairs=len(old_lines),
            reextracted_unique_marker_line_hash_pairs=len(new_lines),
            source_text_human_eyeball_review="PENDING",
            reason="Extractor line flow/hash drift requires source visual check; counts are not official knowledge atoms."))
    old_c=Counter(x["track"] for x in old["enumerated_source_anchors"])
    new_c=Counter(x["track"] for x in new["enumerated_source_anchors"])
    result=dict(
        schema_version="kb-batch26-k00-reextract-v1",
        scope="EXTRACTOR_REPRODUCIBILITY_DIAGNOSTIC_NOT_OFFICIAL_ATOM_COUNT",
        official_pdf_sha256=EXPECTED_PDF_SHA,
        extraction_provenance=dict(
            frozen_ledger_sha256=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),
            pypdf59_ledger_sha256=hashlib.sha256(REEXTRACTED.read_bytes()).hexdigest(),
            pinned_reextraction="pypdf==5.9.0",
            independent_second_extractor="pypdf==6.5.0 gave identical page-hash and 317-marker results on Mac, checked during Batch26",
            source_pdf_embedded_in_git=False,
            source_text_embedded_in_git=False),
        summary=dict(source_pages=61,
            original_pdf_byte_sha_verified=True,
            frozen_marker_occurrences=len(old["enumerated_source_anchors"]),
            reextracted_marker_occurrences=len(new["enumerated_source_anchors"]),
            delta_markers=len(new["enumerated_source_anchors"])-len(old["enumerated_source_anchors"]),
            changed_page_text_hashes=sum(not r["page_text_hash_matches"] for r in rows),
            changed_page_marker_counts=[r["printed_page"] for r in rows if r["delta"]],
            machine_reextracted_pages=61,
            human_visually_rechecked_pages=0,
            official_verified_atoms=0,
            verified_official_atomic_denominator=None, official_coverage_rate=None,
            teacher_approved_lessons=0, student_published_lessons=0),
        tracks=[dict(track=t, frozen_markers=old_c[t], reextracted_markers=new_c[t],
                     occurrence_delta=new_c[t]-old_c[t],
                     verified_official_atomic_denominator=None, review="PENDING")
                for t in TRACKS],
        page_comparison=rows,
        warnings=[
           "pypdf text flow and Unicode output are version-dependent; do not trust raw lines as curriculum atoms.",
           "Two additional numbered-marker occurrences at printed page 52 must be visually investigated; do not overwrite the historical 315 ledger.",
           "No human full-page/unnumbered-clause audit has been completed. All 7 official atom denominators remain null.",
           "Original PDF is stored outside the repository; no copyrighted paragraphs are committed."
        ])
    if not any(r["delta"] for r in rows):
        raise ValueError("Expected version drift not present; requires explicit rebaseline")
    return json.dumps(result, ensure_ascii=False, indent=2)+"\n"


def verify_live_pdf(pdf_path: Path):
    if hashlib.sha256(pdf_path.read_bytes()).hexdigest() != EXPECTED_PDF_SHA:
        raise ValueError("Live PDF SHA mismatch")
    try:
        from pypdf import __version__ as version
    except ImportError as e:
        raise RuntimeError("Install pinned pypdf==5.9.0 on authorized Mac") from e
    if version != "5.9.0":
        raise ValueError(f"Pin pypdf==5.9.0, not {version}")
    from extract_k00_standard_source_batch18 import extract
    fresh=extract(str(pdf_path))
    if fresh!=load(REEXTRACTED):
        raise ValueError("Pinned re-extraction differs from committed evidence; review required")
    return fresh


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--pdf",type=Path)
    a=p.parse_args()
    if a.pdf:
        verify_live_pdf(a.pdf)
    result=build()
    if a.check:
        if OUTPUT.read_text(encoding="utf-8")!=result:
            raise SystemExit("Batch26 K00 report drift")
    else:
        OUTPUT.write_text(result, encoding="utf-8")
    print("PASS source 61 PDF pages / frozen 315 vs pypdf59 317 candidates; official atomic denominator NULL")


if __name__=="__main__":
    main()
