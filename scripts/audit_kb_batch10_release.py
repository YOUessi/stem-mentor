#!/usr/bin/env python3
"""Batch10 release gate: original authoring does not equal teacher review or proof certification."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"backend"))

from backend.app.deep_knowledge import lessons, coverage_report
from backend.app.deep_retrieval import student_evidence_lookup
from backend.app.model_tutor_draft import draft_next_question
from backend.app.main import app

CONTENT=ROOT/"knowledge/deep/v1/algebra_geometry_probability_batch10.json"
OUTPUT=ROOT/"docs/evaluation/KB_BATCH10_RELEASE_AUDIT.json"
PROOF=ROOT/"docs/evaluation/KB_PROOF_OBLIGATIONS_BATCH07.json"
UNION=ROOT/"docs/evaluation/KB_BATCH21_PROOF_REVIEW_UNION.json"

def audit():
    # Freeze this historical release audit at the Batch21 lesson set.
    # The new Batch22 drafts are reviewed by their separate source audit.
    later={x['id'] for x in json.loads((ROOT/'knowledge/deep/v1/elective_gap_batch22.json').read_text(encoding='utf8'))}
    current=tuple(x for x in lessons() if x.id not in later)
    assert len(later)==12 and len(current)==235
    coverage=coverage_report()
    from collections import Counter
    coverage=dict(coverage,kinds=dict(Counter(x.kind for x in current)))
    source=CONTENT.read_bytes()
    new=json.loads(source)
    proof=json.loads(PROOF.read_text(encoding="utf8"))
    union=json.loads(UNION.read_text(encoding="utf8"))["summary"]
    old_count=153
    assert len(new)==11
    assert len(current)>=old_count+len(new)  # Preserve Batch10 baseline; permit subsequent batches
    assert set(x["id"] for x in new).issubset({d.id for d in current})
    assert all(x["review"]["status"]=="REVIEW_PENDING" and x["teacher_solution_visibility"]=="TEACHER_ONLY" for x in new)
    assert all(x["provenance"]["permission"]=="PROJECT_AUTHORED" for x in new)
    assert all(x["kind"]=="theorem" and len(x["proof_steps"])>=3 and len(x["worked_examples"])>=2 for x in new)
    assert sum(x.review.status=="APPROVED" for x in current)==0
    assert proof["summary"]["deep_draft_lessons"]==union["existing_historical_draft_lessons"]
    assert union["current_draft_lessons"]==len(current)
    assert proof["summary"]["theorems"] + sum(x.kind=="theorem" for x in current if x.id in {r["lesson_id"] for r in json.loads(UNION.read_text(encoding="utf8"))["new_proof_review_queue"]})==coverage["kinds"]["theorem"]
    assert union["total_current_unverified_proof_steps"]==sum(len(x.proof_steps) for x in current)
    assert proof["summary"]["theorems_with_whole_proof_certification"]==0
    assert not any("draft" in route.path or "editor" in route.path for route in app.routes)
    # Never use external credentials or enable model egress during CI audit.
    for key in ("STEM_MENTOR_ENABLE_MODEL_DRAFT","STEM_TUTOR_API_KEY",
                "STEM_MENTOR_ENABLE_APPROVED_RAG","STEM_MENTOR_TRUSTED_REVIEWERS_PATH",
                "STEM_MENTOR_REVIEW_ATTESTATIONS_PATH"):
        assert not os.environ.get(key),f"unexpected CI environment secret/config: {key}"
    evidence=student_evidence_lookup("等比数列数学证明",limit=2)
    assert evidence["status"]=="NO_APPROVED_EVIDENCE" and not evidence["candidates"]
    draft=draft_next_question("为什么等比数列求和须分情况",operator_scope="EDITOR_LOCAL",
                          help_requested=True,consent_to_cloud=True)
    assert draft.status=="BLOCKED" and not draft.model_called and not draft.student_visible
    return {
        "scope":"PROJECT_AUTHORED_DRAFTS_NOT_CERTIFIED_CURRICULUM",
        "base_drafts":old_count,
        "batch10_added_theorems":len(new),
        "batch10_lesson_ids":[x["id"] for x in new],
        "source_sha256":hashlib.sha256(source).hexdigest(),
        "current_total_drafts":len(current),
        "current_theorem_drafts":coverage["kinds"]["theorem"],
        "current_concept_drafts":coverage["kinds"]["concept"],
        "current_method_drafts":coverage["kinds"]["method"],
        "uncertified_proof_steps":union["total_current_unverified_proof_steps"],
        "full_proofs_formally_certified":0,
        "teacher_approved":0,
        "student_released_evidence":len(evidence["candidates"]),
        "student_model_api_requests":0,
        "verified_official_elective_atoms":0,
        "review_required":True,
        "warnings":[
          "Finite exact oracle checks support sampled statements; they are not formal proofs of entire authored lesson.",
          "Project engineering IDs remain an incomplete proxy for full ministry curriculum coverage.",
          "Student-facing cloud teaching is disabled without external human approval and consent.",
        ],
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    report=audit()
    text=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if args.check:
        assert OUTPUT.exists() and OUTPUT.read_text(encoding="utf8")==text, "Batch10 release audit drift"
        print("PASS",report["current_total_drafts"],"drafts, 0 approvals, 0 student/cloud requests")
    else:
        OUTPUT.write_text(text,encoding="utf8")
        print("WROTE",OUTPUT)
