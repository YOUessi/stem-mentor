"""Validate editorial gap tickets without converting suggestions to official demands."""
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from .official_clause_audit import source_clause_ledger, TRACKS
from .standard_scope import source_inventory

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "curriculum/highschool_math/k00_gap_tickets_batch18.json"

def validate_gap_tickets(data):
    ledger=source_clause_ledger()
    if data["scope"]!="ORIGINAL_EDITORIAL_GAP_TRIAGE_NOT_OFFICIAL_ATOMIC_DENOMINATOR":
        raise ValueError("Wrong gap scope")
    if data["source_pdf_sha256"]!=ledger["source"]["sha256"] or data["source_url"]!=ledger["source"]["url"]:
        raise ValueError("Untrusted source for editorial gaps")
    candidates={x["id"] for x in source_inventory()["items"]}
    pages={p["printed_page"]:p for p in ledger["pages"]}
    ids=set()
    counts=Counter()
    for r in data["tickets"]:
        if r["id"] in ids: raise ValueError("Duplicate editorial gap")
        ids.add(r["id"])
        p=r["printed_page"]
        if p not in pages or r["pdf_page_index"]!=p+7:
            raise ValueError("Gap source page outside document")
        if r["source_page_text_sha256"]!=pages[p]["pdf_text_sha256"]:
            raise ValueError("Page source text hash mismatch")
        if r["track"] not in TRACKS or r["track"] not in pages[p]["tracks_present"]:
            raise ValueError("Wrong official track for source page")
        if (r["nearest_existing_editorial_objective"] is not None and
                r["nearest_existing_editorial_objective"] not in candidates):
            raise ValueError("Unknown editorial objective")
        if not r["original_project_paraphrase"] or not r["why_not_equivalent"]:
            raise ValueError("Missing independent gap reasoning")
        if r["track"]=="ELECTIVE_E":
            if r["standard_status"]!="OPTIONAL_LOCAL_CHOICE_EXAMPLE":
                raise ValueError("School-elective examples cannot be declared universal")
        elif r["standard_status"]!="SOURCE_TOPIC_LOCATED_REQUIREMENT_SPLIT_PENDING":
            raise ValueError("Non-elective source topic not properly labeled")
        if (r["review_status"]!="HUMAN_CURRICULUM_REVIEW_PENDING"
            or r["gap_status"]!="OPEN_EDITORIAL_CANDIDATE_NOT_PROVEN_MISSING"
            or r["lesson_depth_check"]!="NOT_ASSESSED" or r["student_publishable"] is not False):
            raise ValueError("Unreviewed gap must remain open and non-authoritative")
        counts[r["track"]]+=1
    summary=data["summary"]
    if summary["tickets"]!=len(ids) or summary["not_verified_missing"]!=len(ids):
        raise ValueError("Gap count mismatch")
    if summary["by_track"]!={t:counts[t] for t in TRACKS if t.startswith("ELECTIVE_")}:
        raise ValueError("Gap count by track mismatch")
    if summary["teacher_resolved"]!=0 or summary["official_complete_denominator"] is not None:
        raise ValueError("Gap count cannot imply teacher approval or full official coverage")
    return data

@lru_cache(maxsize=1)
def gap_tickets():
    return validate_gap_tickets(json.loads(PATH.read_text(encoding="utf-8")))
