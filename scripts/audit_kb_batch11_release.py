#!/usr/bin/env python3
"""Batch11 cumulative draft inventory and fail-closed teaching controls.
Evidence produced here does not certify proofs or real human approvals.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import lessons,coverage_report
from app.deep_retrieval import student_evidence_lookup
from app.model_tutor_draft import draft_next_question
from app.main import app

DOC=ROOT/"knowledge/deep/v1/algebra_count_geometry_probability_batch11.json"
PROOFS=ROOT/"docs/evaluation/KB_PROOF_OBLIGATIONS_BATCH07.json"
UNION=ROOT/"docs/evaluation/KB_BATCH21_PROOF_REVIEW_UNION.json"
OUT=ROOT/"docs/evaluation/KB_BATCH11_RELEASE_AUDIT.json"
def audit():
    rows=json.loads(DOC.read_text(encoding="utf8"))
    # Freeze this historical release audit at the Batch21 lesson set.
    # The new Batch22 drafts are reviewed by their separate source audit.
    later={x['id'] for x in json.loads((ROOT/'knowledge/deep/v1/elective_gap_batch22.json').read_text(encoding='utf8'))}
    later.update(x['id'] for x in json.loads((ROOT/'knowledge/deep/v1/core_elective_batch23.json').read_text(encoding='utf8')))
    contents=tuple(x for x in lessons() if x.id not in later)
    assert len(later)==32 and len(contents)==235
    proof=json.loads(PROOFS.read_text(encoding="utf8"))
    union=json.loads(UNION.read_text(encoding="utf8"))["summary"]
    assert len(rows)==12 and len({x["id"] for x in rows})==12
    assert len(contents)>=176 and all(x.review.status=="REVIEW_PENDING" for x in contents)
    assert all(x["kind"]=="theorem" and x["review"]["status"]=="REVIEW_PENDING" and
               x["teacher_solution_visibility"]=="TEACHER_ONLY" and
               len(x["worked_examples"])>=2 and len(x["proof_steps"])>=3 for x in rows)
    from collections import Counter
    historical_kinds=Counter(x.kind for x in contents)
    assert proof["summary"]["deep_draft_lessons"]==union["existing_historical_draft_lessons"]
    assert union["current_draft_lessons"]==len(contents)
    assert proof["summary"]["theorems"] + sum(x.kind=="theorem" for x in contents if x.id in {r["lesson_id"] for r in json.loads(UNION.read_text(encoding="utf8"))["new_proof_review_queue"]})==historical_kinds["theorem"]
    assert union["total_current_unverified_proof_steps"]==sum(len(x.proof_steps) for x in contents)
    assert proof["summary"]["theorems_with_whole_proof_certification"]==0
    assert proof["summary"]["teacher_approved"]==0
    assert len({x.id for x in contents})==len(contents)
    assert all(key not in os.environ for key in (
       "STEM_MENTOR_ENABLE_MODEL_DRAFT","STEM_TUTOR_API_KEY",
       "STEM_MENTOR_ENABLE_APPROVED_RAG","STEM_MENTOR_TRUSTED_REVIEWERS_PATH",
       "STEM_MENTOR_REVIEW_ATTESTATIONS_PATH"))
    assert not any(("editor" in route.path or "draft" in route.path) for route in app.routes)
    lookup=student_evidence_lookup("对数商法则")
    assert lookup["status"]=="NO_APPROVED_EVIDENCE" and not lookup["candidates"]
    attempt=draft_next_question("对数商法则",operator_scope="EDITOR_LOCAL",
                  help_requested=True,consent_to_cloud=True)
    assert attempt.status=="BLOCKED" and not attempt.model_called and not attempt.student_visible
    cov=dict(coverage_report(),kinds=dict(historical_kinds))
    return {
        "scope":"AUTHOR_DRAFT_MATH_ORACLES_NOT_FORMAL_PROOF_OR_TEACHER_RELEASE",
        "prior_drafts":164,
        "new_theorem_drafts":12,
        "total_drafts":len(contents),
        "theorem_drafts":cov["kinds"]["theorem"],
        "concept_drafts":cov["kinds"]["concept"],
        "method_drafts":cov["kinds"]["method"],
        "source_sha256":hashlib.sha256(DOC.read_bytes()).hexdigest(),
        "new_ids":[v["id"] for v in rows],
        "uncertified_proof_step_obligations":union["total_current_unverified_proof_steps"],
        "full_formal_proofs_verified":0,
        "teacher_approved":0,
        "student_deep_knowledge_released":0,
        "live_model_api_requests":0,
        "official_electives_A_E_atomic_verification":0,
        "unresolved_legacy_conflicts":10,
        "unresolved_semantic_gaps":23,
        "warnings":[
          "Finite exact independent oracles and 24 authored worked-example answer checks cannot certify all 12 complete proofs.",
          "Existing 113 engineering topics are not an official atomic curricular denominator.",
          "Student-only knowledge access is fail-closed without genuine independent teacher approval."
        ]
    }
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    a=parser.parse_args()
    text=json.dumps(audit(),indent=2,ensure_ascii=False)+"\n"
    if a.check:
        assert OUT.read_text(encoding="utf8")==text,"Batch11 release audit drift"
        print("PASS Batch11 baseline retained, 0 teacher approvals or student model calls")
    else:
        OUT.write_text(text,encoding="utf8")
        print("WROTE",OUT)
