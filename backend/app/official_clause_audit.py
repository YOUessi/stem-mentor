"""Fail-closed audit of source page and numbered-clause coverage.

A physical page and a source enumeration marker are measurable denominators.
Neither constitutes a formally defined count of official atomic knowledge units.
"""
import json
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "curriculum/highschool_math/official_numbered_clause_evidence_batch18.json"
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A",
          "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")
SOURCE_URL = "https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf"

def validate_ledger(data):
    if data.get("status") != "SOURCE_ENUMERATION_AUDIT_NOT_COMPLETE_ATOMIC_INVENTORY":
        raise ValueError("Unreviewed enumeration cannot be approved")
    src = data.get("source", {})
    if src.get("url") != SOURCE_URL or not re.fullmatch(r"[0-9a-f]{64}", src.get("sha256", "")):
        raise ValueError("Incorrect official standard source or missing PDF SHA")
    if (src.get("printed_page_start"), src.get("printed_page_end"), src.get("printed_to_pdf_index_offset")) != (13, 73, 7):
        raise ValueError("Unexpected physical syllabus page span")
    pages = data.get("pages", [])
    if [p["printed_page"] for p in pages] != list(range(13, 74)):
        raise ValueError("Missing/repeated syllabus page")
    for p in pages:
        if p["pdf_page_index"] != p["printed_page"] + 7:
            raise ValueError("PDF/printed page mismatch")
        if not re.fullmatch(r"[0-9a-f]{64}", p["pdf_text_sha256"]):
            raise ValueError("Missing source page hash")
        if p["source_scan_status"] != "COMPLETE_PAGE_SCAN_EXTRACTION_NOT_HUMAN_CERTIFIED":
            raise ValueError("Uncertified page asserted human verified")
        if p["unnumbered_requirement_completeness"] != "UNKNOWN_NEEDS_HUMAN_SPLIT":
            raise ValueError("Unnumbered requirements cannot be assumed complete")
    ids, page_counts, track_counts = set(), Counter(), Counter()
    for c in data.get("enumerated_source_anchors", []):
        if c["id"] in ids or not re.fullmatch(r"STD2020-P\d{2}-L\d{3}", c["id"]):
            raise ValueError("Invalid/duplicate source enumeration anchor")
        ids.add(c["id"])
        p = c["printed_page"]
        if not 13 <= p <= 73 or c["pdf_page_index"] != p + 7:
            raise ValueError("Anchor page outside syllabus content")
        if c["id"] != f"STD2020-P{p:02d}-L{c['line_number']:03d}":
            raise ValueError("Anchor ID cannot drift from source")
        if c["track"] not in TRACKS or c["track"] not in pages[p-13]["tracks_present"]:
            raise ValueError("Anchor track not in source page")
        if not re.fullmatch(r"[0-9a-f]{64}", c.get("line_sha256", "")):
            raise ValueError("Missing source line hash")
        if c["status"] != "SOURCE_ENUMERATION_UNREVIEWED_NOT_OFFICIAL_ATOM":
            raise ValueError("Cannot certify enumerations as official atoms")
        if c["teacher_review"] != "PENDING" or c["approved_lesson_ids"]:
            raise ValueError("Unreviewed source cannot release lesson")
        page_counts[p] += 1
        track_counts[c["track"]] += 1
    for p in pages:
        if p["source_numbered_marker_count"] != page_counts[p["printed_page"]]:
            raise ValueError("Source marker count mismatch")
    contract = data["denominator_contract"]
    if contract["official_total_numbered_source_candidates"] != len(ids):
        raise ValueError("Source enumeration denominator drift")
    if contract["source_page_denominator"] != len(pages):
        raise ValueError("Source page denominator drift")
    if contract["by_track_source_numbered_candidates"] != {t:track_counts[t] for t in TRACKS}:
        raise ValueError("Per-track enumeration denominator drift")
    if (contract["official_atomic_knowledge_denominator"] is not None or
            contract["is_full_official_atomic_inventory"] is not False or
            contract["teacher_approved_clauses"] != 0):
        raise ValueError("Unreviewed source enumeration falsely claims complete syllabus")
    return data

@lru_cache(maxsize=1)
def source_clause_ledger():
    return validate_ledger(json.loads(SOURCE.read_text(encoding="utf-8")))

def page_progress():
    from .official_topic_outline import de_outline
    c = source_clause_ledger()["denominator_contract"]
    return {
        "source_pages_scanned": c["source_page_denominator"],
        "numbered_source_clause_candidates": c["official_total_numbered_source_candidates"],
        "numbered_by_track": c["by_track_source_numbered_candidates"],
        "unnumbered_d_e_outline":de_outline()["summary"],
        "official_atomic_knowledge_denominator": None,
        "official_total_coverage_rate": None,
        "teacher_approved": 0,
        "note": "Numerated source requirements are only a partial reference ledger; unnumbered requirements and elective choices still require reviewed atomic decomposition.",
    }
