#!/usr/bin/env python3
"""Fail-closed unapproved default release audit: no teacher secrets in CI."""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"backend"))
from app.attested_releases import approved_lesson_ids
from app.deep_knowledge import lessons

def report():
    docs=lessons()
    approved=approved_lesson_ids()
    return {
        "scope":"EXTERNAL_SIGNED_CONTENT_RELEASE_NOT_REAL_TEACHER_IDENTITY_VERIFICATION",
        "draft_count":len(docs),
        "review_pending_count":sum(x.review.status=="REVIEW_PENDING" for x in docs),
        "externally_attested_count":len(approved),
        "student_release_available":bool(approved),
        "formal_math_proof_review_complete":False,
        "real_teacher_identities_authenticated_by_this_software":False,
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args=p.parse_args()
    data=report()
    print(json.dumps(data,ensure_ascii=False,indent=2))
    if args.check:
        assert data["draft_count"] >= 146
        assert data["review_pending_count"] == data["draft_count"]
        for k in ("STEM_MENTOR_ENABLE_APPROVED_RAG",
                  "STEM_MENTOR_TRUSTED_REVIEWERS_PATH",
                  "STEM_MENTOR_REVIEW_ATTESTATIONS_PATH"):
            assert not os.environ.get(k), "CI cannot access external reviewer credentials"
        assert data["externally_attested_count"] == 0
