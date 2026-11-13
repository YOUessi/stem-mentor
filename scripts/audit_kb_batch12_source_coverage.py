#!/usr/bin/env python3
"""Audit incomplete official-standard scope sampling without inflating content claims."""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
sys.path.insert(0,str(ROOT))
from app.standard_scope import source_inventory,public_progress
from app.deep_knowledge import coverage_report
from scripts.kb_frozen_batch24 import frozen_batch24_lessons
from app.deep_retrieval import student_evidence_lookup
from app.main import app
OUT=ROOT/"docs/evaluation/KB_BATCH12_STANDARD_SOURCE_COVERAGE.json"

def audit():
    inventory=source_inventory()
    summary=coverage_report()
    progress=public_progress()
    assert summary["deep_lesson_documents"]>=287  # live index grows, frozen snapshot does not
    assert len(frozen_batch24_lessons())==287
    assert progress["official_atomic_denominator"] is None
    assert progress["complete_curriculum"] is False
    assert all(row["teacher_review"]=="PENDING" for row in inventory["items"])
    assert student_evidence_lookup("函数极限的严格定义")["status"]=="NO_APPROVED_EVIDENCE"
    assert any(r.path=="/api/knowledge/standard-progress" for r in app.routes)
    return {
      "status":"SOURCE_ANCHORED_EDITORIAL_SAMPLE_UNDER_REVIEW",
      "sampled_objectives":len(inventory["items"]),
      "by_track":progress["by_track"],
      "source_page_anchored_candidates":len(inventory["items"]),
      "official_atomic_denominator":None,
      "full_course_coverage_percent":None,
      "deep_draft_lessons":len(frozen_batch24_lessons()) - 52,  # frozen Batch21 snapshot

      "independent_teacher_approved":0,
      "student_deep_lesson_release_count":0,
      "verified_official_atom_links":0,
      "reference_standard":inventory["source_url"],
      "warnings":[
        "These objectives are project-authored paraphrases anchored to printed standard pages, not all official curriculum atoms.",
        "Some elective E topics are school-selected examples, not nationally uniform mandatory lessons.",
        "Existing 113 engineering topics and 176 draft lesson files cannot certify full course coverage.",
        "Neither page provenance nor math test oracles constitute a real independent teacher review."
      ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    expected=json.dumps(audit(),ensure_ascii=False,indent=2)+"\n"
    if args.check:
        if OUT.read_text(encoding="utf-8")!=expected:
            raise AssertionError("Batch12 curriculum snapshot drift")
        print("PASS Batch12: sampled curriculum remains non-certified")
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(expected,encoding="utf-8")
        print("WROTE",OUT)

if __name__=="__main__":
    main()
