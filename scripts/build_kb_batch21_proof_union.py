#!/usr/bin/env python3
"""Historical 451 proof obligations + Batch21 unverified proof obligations.

This deterministic *review queue* does not certify any natural-language proof,
mathematics, teacher identity, syllabus equivalence, or student response.
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
sys.path.insert(0,str(ROOT))
from app.deep_knowledge import lessons
from scripts.kb_frozen_batch24 import frozen_batch24_lessons

BASE = ROOT / "docs/evaluation/KB_PROOF_OBLIGATIONS_BATCH07.json"
NEW = ROOT / "knowledge/deep/v1/elective_gap_batch21.json"
OUT = ROOT / "docs/evaluation/KB_BATCH21_PROOF_REVIEW_UNION.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    base = json.loads(BASE.read_text(encoding="utf-8"))
    new = json.loads(NEW.read_text(encoding="utf-8"))
    old_rows = {x["id"]: x for x in base["lessons"]}
    current = {x.id: x for x in frozen_batch24_lessons() if not x.id.startswith("math.hs.batch24.")}
    fresh_ids = {x["id"] for x in new}
    if (len(old_rows) != 224 or len(new) != 11
            or set(old_rows) & fresh_ids or not (set(old_rows) | fresh_ids <= set(current))
            or len(set(current) - set(old_rows) - fresh_ids) != 32):
        raise ValueError("Old + new proof queue must exactly cover current independent draft IDs")
    for key, prior in old_rows.items():
        doc = current[key]
        if prior["review_status"] != "REVIEW_PENDING" or doc.review.status != "REVIEW_PENDING":
            raise ValueError("No implicit teacher approval of historical lessons")
        steps = doc.model_dump(mode="json")["proof_steps"]
        if [r["claim"] for r in prior["proof_step_obligations"]] != [r["claim"] for r in steps]:
            raise ValueError("Historical proof-step claims no longer match frozen source")
        if [r["reason"] for r in prior["proof_step_obligations"]] != [r["reason"] for r in steps]:
            raise ValueError("Historical proof-step reasons no longer match frozen source")
        if any(r["status"] != "NOT_FORMALLY_VERIFIED" for r in prior["proof_step_obligations"]):
            raise ValueError("Historical proof falsely certified")
    items = []
    for raw in new:
        doc = current[raw["id"]]
        if raw != doc.model_dump(mode="json"):
            raise ValueError("Proof review source must match strictly validated live lesson")
        if doc.review.status != "REVIEW_PENDING" or doc.teacher_solution_visibility != "TEACHER_ONLY":
            raise ValueError("Unsafe new draft")
        for i, step in enumerate(raw["proof_steps"], 1):
            items.append({
                "id": raw["id"] + "#" + str(i), "lesson_id": raw["id"], "step_index": i,
                "claim_reason_sha256": hashlib.sha256(
                    (step["claim"] + "\x00" + step["reason"]).encode("utf-8")).hexdigest(),
                "proof_status": "NOT_FORMALLY_VERIFIED", "teacher_review": "PENDING",
                "student_publishable": False
            })
    prior_count = base["summary"]["proof_step_obligations_not_formally_verified"]
    if prior_count != 451 or sum(len(x["proof_step_obligations"]) for x in old_rows.values()) != 451:
        raise ValueError("Batch20 frozen proof obligation baseline has changed")
    if len(items) != 23:
        raise ValueError("Batch21 expected exactly 23 new unverified theorem proof steps")
    summary = {
        "existing_historical_draft_lessons": 224, "batch21_new_deep_drafts": 11,
        "current_draft_lessons": len(old_rows) + len(new),  # Frozen Batch21 snapshot, not live Batch22.
        "historical_unverified_proof_steps": prior_count,
        "batch21_unverified_proof_steps": len(items),
        "total_current_unverified_proof_steps": prior_count + len(items),
        "formal_proof_certifications": 0, "teacher_approved": 0,
        "student_publication": 0,
        "official_atomic_denominator": None, "official_coverage_rate": None
    }
    return {
        "schema_version": "batch21-proof-union-v1",
        "frozen_batch20_baseline_sha256": sha(BASE),
        "new_batch21_lesson_blob_sha256": sha(NEW),
        "scope": "EDITORIAL_PROOF_OBLIGATIONS_UNVERIFIED",
        "summary": summary, "new_proof_review_queue": items,
        "warnings": [
            "23 new natural-language proof steps remain unverified; finite exact pytest checks do not formally certify them.",
            "Old 451-step risk priorities are frozen; new steps require separate independent human proof risk triage.",
            "This worklist is editor-only; student challenge and teacher signing are unavailable."
        ]
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != rendered:
            raise ValueError("Batch21 451+23 proof review union drift")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(rendered, encoding="utf-8")
    print("PASS Batch21 proof review: 451 historical + 23 new = 474 unverified, 0 certified")


if __name__ == "__main__":
    main()
