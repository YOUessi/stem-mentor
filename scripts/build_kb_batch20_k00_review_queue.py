#!/usr/bin/env python3
"""K00: reproducible *source-review tasks*, NEVER an official atom denominator.

A page-review, numbered-marker, D/E heading and editorial gap may describe
overlapping mathematics. Counts across these types MUST NOT be added as
curriculum atom counts. This is a machine-auditable queue of things to check.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.official_clause_audit import TRACKS, source_clause_ledger
from app.official_topic_outline import de_outline
from app.k00_gap_audit import gap_tickets
from app.standard_scope import source_inventory

OUTPUT = ROOT / "docs/evaluation/KB_BATCH20_K00_REVIEW_QUEUE.json"
SCOPE = "UNVERIFIED_SOURCE_REVIEW_TASKS_NOT_OFFICIAL_ATOMIC_DENOMINATOR"
PENDING = "HUMAN_CURRICULUM_AND_MATH_REVIEW_PENDING"
KINDS = (
    "SOURCE_PAGE_SPLIT",
    "NUMBERED_MARKER_SPLIT",
    "UNNUMBERED_DE_HEADING_SPLIT",
    "EDITORIAL_GAP_DECISION",
)


def build():
    ledger = source_clause_ledger()  # trusted frozen extraction SHA, NOT reviewed atomic truth
    outline = de_outline()
    gaps = gap_tickets()
    editorial = source_inventory()
    pages = {p["printed_page"]: p for p in ledger["pages"]}
    tasks = []

    def task(identifier, kind, track, printed, linked_id, line_hash=None):
        if kind not in KINDS:
            raise ValueError("Unrecognized task type")
        if printed not in pages:
            raise ValueError("Unknown source page")
        if track is not None and track not in pages[printed]["tracks_present"]:
            raise ValueError("Task is assigned to an absent course track")
        x = {
            "id": identifier, "kind": kind, "track": track,
            "printed_page": printed, "source_id": linked_id,
            "source_page_sha256": pages[printed]["pdf_text_sha256"],
            "review_status": PENDING, "teacher_approved": False,
            "counts_as_verified_atomic_skill": False, "student_publishable": False,
        }
        if line_hash is not None:
            x["source_line_sha256"] = line_hash
        tasks.append(x)

    for p in ledger["pages"]:
        task(f"K00-PAGE-{p['printed_page']:02d}", KINDS[0], None,
             p["printed_page"], f"STD2020-PAGE-{p['printed_page']:02d}")
    for a in ledger["enumerated_source_anchors"]:
        task("K00-MARKER-"+a["id"], KINDS[1], a["track"],
             a["printed_page"], a["id"], a["line_sha256"])
    for row in outline["items"]:
        task("K00-OUTLINE-"+row["id"], KINDS[2], row["track"],
             row["printed_page"], row["id"])
    for row in gaps["tickets"]:
        task("K00-GAP-"+row["id"], KINDS[3], row["track"],
             row["printed_page"], row["id"])

    if len(tasks) != len({x["id"] for x in tasks}):
        raise ValueError("Duplicate review-task ID")
    by_kind = Counter(x["kind"] for x in tasks)
    by_track = Counter(x["track"] for x in ledger["enumerated_source_anchors"])
    de_counts = Counter(x["track"] for x in outline["items"])
    gap_counts = Counter(x["track"] for x in gaps["tickets"])
    edit_counts = Counter(x["track"] for x in editorial["items"])
    matrix = []
    for track in TRACKS:
        matrix.append({
            "track": track,
            "source_pages_with_track": [
                p["printed_page"] for p in ledger["pages"]
                if track in p["tracks_present"]
            ],
            "numbered_source_marker_candidates": by_track[track],
            "d_e_unnumbered_heading_candidates": de_counts[track],
            "editorial_learning_objective_candidates": edit_counts[track],
            "editorial_gap_tickets_open": gap_counts[track],
            "verified_official_atomic_denominator": None,
            "teacher_verified_knowledge_atoms": 0,
            "approved_lessons": 0,
            "student_publishable_lessons": 0,
            "official_coverage_rate": None,
            "needs_full_human_atomization": True,
        })

    return {
        "schema_version": "1.0",
        "scope": SCOPE,
        "source_pdf_sha256": ledger["source"]["sha256"],
        "summary": {
            "source_review_tasks": len(tasks),
            "task_counts_by_kind": {kind: by_kind[kind] for kind in KINDS},
            "official_atomic_denominator": None,
            "complete_syllabus_inventory": False,
            "teacher_verified_atoms": 0,
            "student_publishable_deep_lessons": 0,
            "warning": "Task categories overlap mathematically. Do not sum them into knowledge atoms or claim course coverage.",
        },
        "tracks": matrix,
        "review_queue": tasks,
    }


def validate_queue(data):
    expected = build()
    if data != expected:
        raise ValueError("K00 review queue drift/forged status/source/count; regenerate from pinned ledger")
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    output = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != output:
            raise AssertionError("K00 review queue is not in sync with source evidence")
        validate_queue(json.loads(output))
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(output, encoding="utf-8")
    print("K00 source-review queue PASS:", build()["summary"]["task_counts_by_kind"])


if __name__ == "__main__":
    main()
