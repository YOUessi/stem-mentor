#!/usr/bin/env python3
"""Offline GitHub CI verification of committed Batch127-129 *editorial* source artifacts.

The licensed curriculum PDF/PDFKit cache stays on the authorised Mac. This
verifier checks committed records, hashes, negative publication gates and
rendered reports ONLY. It cannot re-open/re-interpret the original PDF.
Mac-only --check in each source builder remains the stronger source replay.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch118_source_atom_ledger as syllabus
import build_kb_batch127_source_review as b127
import build_kb_batch128_source_ledger as b128
import build_kb_batch129_scope_reviews as b129

BATCHES = (
    (127, b127, "KB_BATCH127_SOURCE_REVIEW.json", "k00_batch127_source_line_locks.json", "KB_BATCH127_SOURCE_REVIEW.md"),
    (128, b128, "KB_BATCH128_SEMANTIC_SPLIT_LEDGER.json", "k00_batch128_source_line_locks.json", "KB_BATCH128_SEMANTIC_SPLIT_LEDGER.md"),
    (129, b129, "KB_BATCH129_SCOPE_REVIEWS.json", "k00_batch129_source_line_locks.json", "KB_BATCH129_SCOPE_REVIEWS.md"),
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
TRACKS = set(syllabus.TRACKS)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def read(path: Path) -> dict:
    require(path.is_file(), "missing committed artifact: " + str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def check(root: Path = ROOT) -> dict:
    # These are hash commitments only, NOT regenerated source hashes from the PDF.
    manifest = read(root / "curriculum/highschool_math/k00_batch117_source_triage.json")
    pinned_pdf_sha = manifest["source_pdf_sha256"]
    require(pinned_pdf_sha == syllabus.PDF_SHA and HEX64.fullmatch(pinned_pdf_sha), "curriculum PDF manifest SHA drift")
    summary = {}
    all_ids = set()
    for batch, mod, json_name, locks_name, report_name in BATCHES:
        data = read(root / "docs/evaluation" / json_name)
        locks = read(root / "curriculum/highschool_math" / locks_name)
        # Built-in strict approval, draft count and per-track denominator gates.
        if batch == 127:
            mod.validate(data, locks, regen=False)
            report = mod.report(data)
        elif batch == 128:
            mod.validate(data, locks, compare=False)
            report = mod.render(data)
        else:
            mod.validate(data, locks, regen=False)
            report = mod.render(data)
        actual_report = root / "docs/evaluation" / report_name
        require(actual_report.is_file() and actual_report.read_text(encoding="utf-8") == report,
                f"Batch{batch}: report does not match committed records")
        require(len(locks) == len(data["records"]) == 28,
                f"Batch{batch}: unexpected lock or record count")
        seen = set()
        for r in data["records"]:
            uid = r.get("id", r.get("candidate_id"))
            require(uid and uid not in all_ids and uid not in seen,
                    f"Batch{batch}: duplicate source candidate across batches")
            seen.add(uid)
            all_ids.add(uid)
            require(r["course_track"] in TRACKS, f"Batch{batch}: invalid course track")
            require(r.get("source_pdf_sha256", r.get("curriculum_pdf_sha256")) == pinned_pdf_sha,
                    f"Batch{batch}: source PDF fingerprint mismatch")
            source = r["source"]
            require(source == locks[uid], f"Batch{batch}: source reference not locked")
            start, end = source["start_line"], source["end_line"]
            hashes = source["line_sha256"]
            require(isinstance(source["page"], int) and 13 <= source["page"] <= 73
                    and isinstance(start, int) and isinstance(end, int) and 1 <= start <= end
                    and len(hashes) == end - start + 1
                    and all(isinstance(h, str) and HEX64.fullmatch(h) for h in hashes)
                    and HEX64.fullmatch(source["span_sha256"]),
                    f"Batch{batch}: malformed source line/span hash commitment")
            require(r["teacher_status"] == "REVIEW_PENDING" and r["official_atom_id"] is None
                    and r["student_authoritative"] is False,
                    f"Batch{batch}: student publication or unapproved promotion")
        summary[f"batch_{batch}_committed_editorial_records"] = len(seen)
    require(len(all_ids) == 84, "cross-batch source ID census drift")
    summary["all_committed_source_records"] = len(all_ids)
    summary["source_pdf_recomputed_in_ci"] = False
    summary["source_hashes_recomputed_in_ci"] = False
    summary["teacher_approvals"] = 0
    summary["official_atoms_certified"] = 0
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", required=True)
    opt = ap.parse_args()
    print(json.dumps(check(), ensure_ascii=False, indent=2, sort_keys=True))
    print("PASS: committed-artifact-only gate. Source-PDF replay still REQUIRED on the authorised Mac.")
