#!/usr/bin/env python3
"""Batch21: 11 independently authored gap-adjacent elective DRAFT lessons.

This writes EDITOR-ONLY content. Topic adjacency is not source-clause
alignment, formal proof checking, teacher review or curriculum completion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.deep_knowledge import DeepLesson, curriculum  # noqa: E402

AUTHOR = ROOT / "curriculum/highschool_math/author_draft_batch21.json"
GAPS = ROOT / "curriculum/highschool_math/k00_gap_tickets_batch18.json"
OUTPUT = ROOT / "knowledge/deep/v1/elective_gap_batch21.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH21_EDITORIAL_GAP_OVERLAPS.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[str, str]:
    author = json.loads(AUTHOR.read_text(encoding="utf-8"))
    gaps = json.loads(GAPS.read_text(encoding="utf-8"))
    inventory = {i["id"]: i for i in gaps["tickets"]}
    course_map = {i["id"]: i for i in curriculum()}
    if len(inventory) != 28 or len(author) != 11:
        raise ValueError("Frozen Batch18 28 gap candidates / Batch21 11 authors expected")
    if len({x["gap"] for x in author}) != 11:
        raise ValueError("Duplicate gap association")
    if len({x["lesson"]["id"] for x in author}) != 11:
        raise ValueError("Duplicate lesson ID")
    proposed = {}
    lessons = []
    by_track = Counter()
    for row in author:
        gap_key = f"STD2020-EDITORIAL-GAP-{row['gap']:03d}"
        ticket = inventory[gap_key]
        if ticket["gap_status"] != "OPEN_EDITORIAL_CANDIDATE_NOT_PROVEN_MISSING":
            raise ValueError("Do not silently close editorial gap tickets")
        model = DeepLesson.model_validate(row["lesson"])
        if model.review.status != "REVIEW_PENDING" or model.teacher_solution_visibility != "TEACHER_ONLY":
            raise ValueError("Unreviewed content cannot enter student publication")
        if model.review.reviewer_id or model.review.review_record or model.review.reviewed_at:
            raise ValueError("No invented teachers or signatures")
        if len(model.curriculum_ids) != 1:
            raise ValueError("No speculative multiple curriculum claims")
        course = course_map[model.curriculum_ids[0]]
        if course["level"] != "选修拓展" or course.get("elective_track") != ticket["track"]:
            raise ValueError(f"{model.id}: elective course track mismatch")
        if len(model.worked_examples) != 2 or len(model.hint_ladder) != 3:
            raise ValueError("Teacher-only examples and three-tier scaffolding required")
        lessons.append(model.model_dump(mode="json"))
        proposed[gap_key] = (model.id, course["id"])
        by_track[ticket["track"]] += 1
    rows = []
    for ticket in gaps["tickets"]:
        gap_key = ticket["id"]
        matched = proposed.get(gap_key)
        rows.append({
            "gap_ticket": gap_key,
            "track": ticket["track"],
            "printed_source_page": ticket["printed_page"],
            "source_page_text_sha256": ticket["source_page_text_sha256"],
            "gap_remains_open": True,
            "editorial_draft_lesson_id": matched[0] if matched else None,
            "existing_engineering_map_id": matched[1] if matched else None,
            "topic_overlap_status": ("PROJECT_AUTHORED_ADJACENCY_NOT_CURRICULUM_EQUIVALENCE"
                                     if matched else "NO_BATCH21_ADJACENCY"),
            "official_clause_verified": False,
            "formal_proof_certified": False,
            "teacher_review": "PENDING",
            "student_publishable": False,
        })
    report = {
        "schema_version": "batch21-editorial-overlap-v1",
        "frozen_gap_tickets_sha256": sha(GAPS),
        "author_drafts_sha256": sha(AUTHOR),
        "source_document_sha256": gaps["source_pdf_sha256"],
        "scope": "EDITORIAL_SUGGESTIONS_NOT_OFFICIAL_SYLLABUS_ATOMS",
        "summary": {
            "open_editorial_gap_candidates": len(inventory),
            "new_draft_lessons": len(lessons),
            "editorial_gap_tickets_with_new_draft_overlap": len(proposed),
            "gap_tickets_still_open": len(inventory),
            "no_new_draft_overlap": len(inventory) - len(proposed),
            "by_elective_track": dict(sorted(by_track.items())),
            "official_atomic_denominator": None,
            "official_coverage_rate": None,
            "formal_proof_certified": 0,
            "teacher_approved": 0,
            "student_released": 0
        },
        "ticket_status": rows,
        "caveats": [
            "A lesson sharing an engineering topic with a gap ticket does not prove source clause equivalence.",
            "Exact finite mathematical oracles do not certify an entire natural-language proof.",
            "All 28 gap tickets remain OPEN until human curriculum review, and all new lessons remain REVIEW_PENDING.",
            "Core/selected-compulsory/each elective-track official atomic denominator is still null."
        ]
    }
    return (json.dumps(lessons, ensure_ascii=False, indent=2) + "\n",
            json.dumps(report, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    lesson_text, report_text = build()
    outputs = [(OUTPUT, lesson_text), (REPORT, report_text)]
    if args.check:
        for path, rendered in outputs:
            if not path.exists() or path.read_text(encoding="utf-8") != rendered:
                raise AssertionError(f"Batch21 reproducibility/drift violation: {path}")
    else:
        for path, rendered in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8")
    print("PASS Batch21: 11 REVIEW_PENDING lessons; 11 editorial overlaps; 28/28 gaps still OPEN")


if __name__ == "__main__":
    main()
