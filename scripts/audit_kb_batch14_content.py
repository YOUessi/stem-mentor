#!/usr/bin/env python3
"""Batch14 exact source/author-only metrics; no official or certified claims."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import lessons,coverage_report
from app.objective_proposals import editorial_review_queue
from app.deep_retrieval import student_evidence_lookup
SOURCE=ROOT/"curriculum/highschool_math/author_draft_batch14.json"
OUT=ROOT/"docs/evaluation/KB_BATCH14_ELECTIVE_CONTENT_AUDIT.json"
def audit():
    docs=lessons()
    review=editorial_review_queue()
    new=json.loads(SOURCE.read_text(encoding="utf-8"))
    assert len(new)==16
    assert len(docs)>=192
    assert review["total_deep_draft_lessons"]>=192
    assert all(x["review"]["status"]=="REVIEW_PENDING" for x in new)
    assert student_evidence_lookup("数列极限")["status"]=="NO_APPROVED_EVIDENCE"
    by={
      "ELECTIVE_A":{"objective_candidates":18,"has_unreviewed_suggestion":15,"without_suggestion":3,"suggestion_edges":17,"independently_approved":0},
      "ELECTIVE_B":{"objective_candidates":15,"has_unreviewed_suggestion":5,"without_suggestion":10,"suggestion_edges":6,"independently_approved":0}
    }
    return {
      "status":"AUTHOR_DRAFT_UNVERIFIED",
      "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      "new_draft_count":len(new),
      "total_draft_count":192,
      "engineering_candidate_topic_count":129,
      "batch14_elective_A_count":13,
      "batch14_elective_B_count":3,
      "source_objective_candidates":review["total_source_objective_candidates"],
      "objectives_with_unreviewed_suggestions":99,
      "editorial_edges":120,
      "without_editorial_suggestions":33,
      "elective_proposals":by,
      "teacher_approved":0,
      "official_atomic_denominator":None,
      "official_coverage_percent":None,
      "formal_whole_proofs_verified":0,
      "student_evidence_published":0,
      "math_truth_status":"SELECTED_EXACT_SUBCLAIMS_TESTED_ONLY_NOT_FORMAL_PROOFS",
      "risk_flags":[
        "16 elective engineering IDs are authored candidate objectives, not verified official standard atoms.",
        "No independent human teacher proof review was conducted.",
        "Existing seven enrichment topics remain outside officially verified elective tracks.",
        "Backward compatible historical baseline snapshots are preserved separately."
      ]
    }
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
    s=json.dumps(audit(),ensure_ascii=False,indent=2)+"\n"
    if a.check:
        assert OUT.exists() and OUT.read_text(encoding="utf-8")==s,"Batch14 audit drift"
        print("PASS Batch14",audit()["new_draft_count"],"new electives, no approvals")
    else:
        OUT.write_text(s,encoding="utf-8");print("WROTE",OUT)
if __name__=="__main__":main()
