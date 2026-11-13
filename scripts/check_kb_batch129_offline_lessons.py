#!/usr/bin/env python3
"""CI replay of original mathematical lesson generation using locked *published* context.

Does NOT certify the source PDF: see check_kb_batch127_129_offline.py.
On the authorised Mac, build_kb_batch129_lessons.py --check independently
reconstructs the source from the private PDFKit line cache.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import build_kb_batch129_lessons as lessons
import check_kb_batch127_129_offline as evidence


def check() -> dict:
    evidence.check()
    snapshot = json.loads(evidence.b129.OUT.read_text(encoding="utf-8"))
    docs = lessons.build(source_snapshot=snapshot)
    exact = lessons.exact_checks()
    for path, expected in (
        (lessons.OUT, lessons.enc(docs)),
        (lessons.ORACLES, lessons.enc(exact)),
        (lessons.REPORT, lessons.render(docs, exact)),
    ):
        evidence.require(path.is_file() and path.read_text(encoding="utf-8") == expected,
                         "published lesson/math oracle drift: " + str(path))
    evidence.require(len(docs) == 9 and
                     exact["exact_worked_example_checks"] == 18 and
                     exact["invalid_condition_checks"] == 9 and
                     exact["cross_topic_independent_checks"] == 9 and
                     exact["all_finite_exact_cases_passed"] is True and
                     exact["general_theorem_proofs_formally_certified"] == 0,
                     "faked math oracle or certification")
    return {"pending_teacher_lessons": 9, "independent_examples": 18,
            "invalid_condition_tests": 9, "cross_topic_tests": 9,
            "source_pdf_revalidated": False, "teacher_approved": 0}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true", required=True)
    args = p.parse_args()
    print(json.dumps(check(), ensure_ascii=False, indent=2, sort_keys=True))
    print("PASS: offline math replay + negative gates; source PDF must be replayed separately on Mac.")
