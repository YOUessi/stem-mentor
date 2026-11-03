#!/usr/bin/env python3
"""Fail-closed scope proposal audit; counts are editorial and never official coverage."""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.objective_proposals import internal_review_counts
from app.standard_scope import source_inventory
from app.deep_knowledge import coverage_report
from app.deep_retrieval import student_evidence_lookup

OUT=ROOT/"docs/evaluation/KB_BATCH13_EDITORIAL_REVIEW_QUEUE.json"

def audit():
    counts=internal_review_counts()
    assert counts["total_source_objective_candidates"]==132
    assert counts["total_deep_draft_lessons"]>=176
    assert sum(x["objective_candidates"] for x in counts["by_track"].values())==132
    assert counts["independent_teacher_approved_matches"]==0
    assert counts["student_published_knowledge_count"]==0
    assert counts["official_atomic_denominator"] is None
    assert counts["official_coverage_percent"] is None
    assert source_inventory()["is_complete_official_atomic_inventory"] is False
    assert coverage_report()["review_statuses"]=={"REVIEW_PENDING":176}
    assert student_evidence_lookup("数列极限的 epsilon N 定义")["status"]=="NO_APPROVED_EVIDENCE"
    return {
        "scope":"EDITORIAL_OBJECTIVE_LESSON_PROPOSALS_ONLY",
        **counts,
        "unmapped_candidates":sum(x["without_suggestion"] for x in counts["by_track"].values()),
        "full_standard_review_completed":False,
        "all_math_proofs_certified":False,
        "notes":[
            "Proposed links mean possible topic overlap, not content completeness.",
            "A candidate with no suggestion is an open review queue item, not evidence it is outside the standard.",
            "No official curriculum denominator or official coverage percentage is available.",
            "Human teacher approval and student-release count remain zero."
        ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    val=json.dumps(audit(),ensure_ascii=False,indent=2)+"\n"
    if args.check:
        if OUT.read_text(encoding="utf-8")!=val:
            raise AssertionError("Batch13 scope editorial queue snapshot drift")
        print("PASS Batch13 review queue is draft-only and source-anchored")
    else:
        OUT.write_text(val,encoding="utf-8")
        print("WROTE",OUT)

if __name__=="__main__":
    main()
