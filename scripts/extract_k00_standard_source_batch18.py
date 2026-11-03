#!/usr/bin/env python3
"""Extract an audit ledger from the official 2020 high-school mathematics PDF.

This tool is run on the authorized Mac, against a separately downloaded PDF.
It records only page/marker positions and hashes, not copyrighted lesson text.
PDF enumeration is NOT an official count of atomic mathematical skills.
Requires pypdf for extraction; CI validates the frozen ledger without a PDF.
"""
import argparse
import hashlib
import json
import logging
import re
from collections import Counter
from pathlib import Path

PDF_URL = "https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf"
DOCUMENT = "普通高中数学课程标准（2017年版2020年修订）"
CIRCLES = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
NUMBERED = re.compile(r"^\s*([" + CIRCLES + r"]|[（(]\s*[0-9０-９]+\s*[)）])")
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A",
          "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")
TRACK_SPLITS = {
    57: ("犅类课程", "ELECTIVE_B"), 64: ("犆类课程", "ELECTIVE_C"),
    69: ("犇类课程", "ELECTIVE_D"), 73: ("犈类课程", "ELECTIVE_E"),
}

def page_track(printed, line, current):
    if printed <= 35: return "COMPULSORY"
    if printed <= 50: return "SELECTIVE_COMPULSORY"
    if printed <= 56: return "ELECTIVE_A"
    for boundary, (heading, new_track) in TRACK_SPLITS.items():
        if printed == boundary and heading in line: return new_track
    if printed == 57: return current or "ELECTIVE_A"
    if printed <= 63: return "ELECTIVE_B"
    if printed == 64: return current or "ELECTIVE_B"
    if printed <= 68: return "ELECTIVE_C"
    if printed == 69: return current or "ELECTIVE_C"
    if printed <= 72: return "ELECTIVE_D"
    if printed == 73: return current or "ELECTIVE_D"
    raise ValueError(printed)

def extract(pdf_path):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Install pypdf into a temporary Mac environment for extraction") from exc
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    raw = Path(pdf_path).read_bytes()
    pdf_sha = hashlib.sha256(raw).hexdigest()
    reader = PdfReader(pdf_path)
    if len(reader.pages) < 81:
        raise ValueError("Wrong PDF: too few pages")
    clauses, pages = [], []
    phase, current = "NON_CONTENT", None
    for pdf_page in range(20, 81):
        printed = pdf_page - 7  # Verified by visual comparison with printed footers.
        t = reader.pages[pdf_page].extract_text()
        page_hash = hashlib.sha256(t.encode("utf-8")).hexdigest()
        page_counts = Counter()
        touched_tracks = set()
        for line_number, line in enumerate(t.splitlines(), 1):
            current = page_track(printed, line, current)
            touched_tracks.add(current)
            if "【内容要求】" in line: phase = "CONTENT"
            if "【教学提示】" in line or "【学业要求】" in line: phase = "NON_CONTENT"
            # In the elective section, the standard uses topic itemizations without
            # the compulsory-course content/pedagogy heading structure.
            eligible = (printed <= 50 and phase == "CONTENT") or printed >= 52
            match = NUMBERED.match(line) if eligible else None
            if not match:
                continue
            marker = re.sub(r"\s+", "", match.group(1))
            identifier = f"STD2020-P{printed:02d}-L{line_number:03d}"
            # Deliberately retain no text beyond an enumeration marker.
            clauses.append({
                "id": identifier, "printed_page": printed, "pdf_page_index": pdf_page,
                "line_number": line_number, "track": current, "marker": marker,
                "line_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
                "status": "SOURCE_ENUMERATION_UNREVIEWED_NOT_OFFICIAL_ATOM",
                "teacher_review": "PENDING", "approved_lesson_ids": [],
            })
            page_counts[current] += 1
        pages.append({
            "printed_page": printed, "pdf_page_index": pdf_page,
            "pdf_text_sha256": page_hash,
            "source_numbered_marker_count": sum(page_counts.values()),
            "tracks_present": sorted(touched_tracks),
            "source_scan_status": "COMPLETE_PAGE_SCAN_EXTRACTION_NOT_HUMAN_CERTIFIED",
            "unnumbered_requirement_completeness": "UNKNOWN_NEEDS_HUMAN_SPLIT",
        })
    counts = {k: sum(c["track"] == k for c in clauses) for k in TRACKS}
    return {
        "schema_version": "1.0", "status": "SOURCE_ENUMERATION_AUDIT_NOT_COMPLETE_ATOMIC_INVENTORY",
        "source": {"title": DOCUMENT, "url": PDF_URL, "sha256": pdf_sha,
                   "pdf_total_pages": len(reader.pages), "printed_page_start": 13,
                   "printed_page_end": 73, "printed_to_pdf_index_offset": 7},
        "denominator_contract": {
            "official_total_numbered_source_candidates": len(clauses),
            "source_page_denominator": len(pages),
            "by_track_source_numbered_candidates": counts,
            "official_atomic_knowledge_denominator": None,
            "is_full_official_atomic_inventory": False,
            "reason": "The standard contains unnumbered content and school-selected electives E; enumerated source markers are not one-to-one knowledge atoms.",
            "teacher_approved_clauses": 0,
        }, "pages": pages, "enumerated_source_anchors": clauses,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    result = extract(a.pdf)
    Path(a.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["denominator_contract"], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
