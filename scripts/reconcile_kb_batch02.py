#!/usr/bin/env python3
"""Safely reconcile pre-existing Batch02 drafts against published Batch05 IDs.

Candidate originals are immutable editorial evidence; duplicate-ID alternatives
MUST NOT enter the active lesson index. Regeneration is deterministic and CI-gated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "knowledge/deep/candidates/batch02"
ACTIVE = ROOT / "knowledge/deep/v1"
REPORT = ROOT / "docs/evaluation/KB_BATCH02_RECONCILIATION.json"
RECONCILED_SUFFIX = "_batch06_import.json"
# Exactly the ten existing collections that participated in the historical
# Batch02 -> Batch06 reconciliation. Appending Batch07...Batch91 lessons must
# not change this frozen decision ledger. All ten must continue to exist.
FROZEN_ACTIVE_BASE_FILENAMES = (
    "advanced_space_prob_model_batch04.json",
    "core_foundations_v1.json",
    "elective_a_b_advanced_batch15.json",
    "elective_b_c_d_e_batch16.json",
    "extension_topics_batch04.json",
    "functional_trig_vector_batch04.json",
    "geometry_probability_sequences_v1.json",
    "geometry_stats_foundations_batch04.json",
    "semantic_gap_subskills_batch05.json",
    "spatial_fundamentals_batch04.json",
)
EXCLUDED_FIELDS = {"version"}  # Version differences alone do not settle mathematical meaning.


def canonical(item):
    return json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(item):
    return hashlib.sha256(canonical(item)).hexdigest()


def read_rows(path):
    values = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(values, list):
        raise ValueError(f"{path}: expected list")
    return values


def build():
    paths = sorted(SOURCE.glob("*batch02.json"))
    if not paths:
        raise ValueError("Missing original Batch02 candidate files; refuse empty import")

    existing = {}
    for filename in FROZEN_ACTIVE_BASE_FILENAMES:
        path = ACTIVE / filename
        if not path.is_file():
            raise ValueError(f"Missing frozen reconciliation source: {filename}")
        for item in read_rows(path):
            key = item["id"]
            if key in existing:
                raise ValueError(f"Ambiguous existing published lesson ID: {key}")
            existing[key] = (path.name, item)

    if len(existing) != 130:
        raise ValueError("Historical reconciliation base must have exactly 130 distinct lessons")

    imported = {}
    conflicts = []
    candidate_ids = set()
    for path in paths:
        selected = []
        for item in read_rows(path):
            key = item["id"]
            if key in candidate_ids:
                raise ValueError(f"Duplicate candidate lesson: {key}")
            candidate_ids.add(key)
            if key in existing:
                old_path, current = existing[key]
                differing = sorted(k for k in (item.keys() | current.keys())
                                   if item.get(k) != current.get(k) and k not in EXCLUDED_FIELDS)
                conflicts.append({
                    "id": key,
                    "candidate_title": item["title"],
                    "existing_title": current["title"],
                    "candidate_source": str(path.relative_to(ROOT)),
                    "existing_source": "knowledge/deep/v1/" + old_path,
                    "candidate_sha256": digest(item),
                    "existing_sha256": digest(current),
                    "differing_fields": differing,
                    "status": "OPEN_EDITORIAL_CONFLICT_NOT_PROMOTED",
                })
                continue
            selected.append(item)
            imported[key] = str(path.relative_to(ROOT))
        yield_name = path.name.replace("_batch02.json", RECONCILED_SUFFIX)
        yield_path = ACTIVE / yield_name
        yield_data = json.dumps(selected, ensure_ascii=False, indent=2) + "\n"
        imported[yield_name] = yield_data

    summaries = sorted(k for k in imported if k.endswith(RECONCILED_SUFFIX))
    outputs = {ACTIVE / k: imported[k] for k in summaries}
    introduced = {k: v for k, v in imported.items() if not k.endswith(RECONCILED_SUFFIX)}
    if len(candidate_ids) != len(introduced) + len(conflicts):
        raise ValueError("Candidate import lost or silently duplicated lessons")
    if set(introduced) & set(existing):
        raise ValueError("Conflict entered active lesson index")
    expected = {"source_candidates": 39, "nonconflicting_imports": 29, "held_for_review": 10}
    actual = {"source_candidates": len(candidate_ids),
              "nonconflicting_imports": len(introduced),
              "held_for_review": len(conflicts)}
    if expected != actual:
        raise ValueError(f"Unexpected candidate baseline drift: {actual} != {expected}")
    report = {
        "scope": "EDITORIAL_CANDIDATE_MERGE_NOT_MATH_CERTIFICATION",
        "source": "Retained, unmodified Batch02 candidate texts",
        "summary": {
            **actual,
            "published_active_lessons_after_import": len(existing) + len(introduced),
            "still_teacher_approved": 0,
            "candidate_conflicts_automatically_resolved": 0,
        },
        "new_lesson_ids": sorted(introduced),
        "unresolved_conflicts": sorted(conflicts, key=lambda x: x["id"]),
        "warnings": [
            "Never convert an ID conflict into a new approved theorem automatically.",
            "All imported drafts remain REVIEW_PENDING and TEACHER_ONLY.",
            "The 113 engineering-topic map is not the official full syllabus.",
            "Mathematical truth and complete proofs need independent checks and real reviewers."
        ],
    }
    outputs[REPORT] = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    return outputs, report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    outputs, report = build()
    if args.check:
        for path, expected in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Reconciliation drift: {path.relative_to(ROOT)}")
        print("PASS: 39 candidates => 29 imported drafts, 10 held, 0 auto-overwrites")
    else:
        for path, value in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8")
        print("WROTE:", report["summary"])


if __name__ == "__main__":
    main()
