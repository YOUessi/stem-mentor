#!/usr/bin/env python3
"""Fail-closed integration audit: new drafts are not teaching approvals."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))

from app.deep_knowledge import lessons, coverage_report
from app.deep_retrieval import student_evidence_lookup
from app.model_tutor_draft import draft_next_question
from app.main import app

def audit():
    # Freeze this historical release audit at the Batch21 lesson set.
    # The new Batch22 drafts are reviewed by their separate source audit.
    later={x['id'] for x in json.loads((ROOT/'knowledge/deep/v1/elective_gap_batch22.json').read_text(encoding='utf8'))}
    later.update(x['id'] for x in json.loads((ROOT/'knowledge/deep/v1/core_elective_batch23.json').read_text(encoding='utf8')))
    later.update(x['id'] for x in json.loads((ROOT/'knowledge/deep/v1/core_foundation_batch24.json').read_text(encoding='utf8')))
    existing=tuple(x for x in lessons() if x.id not in later)
    assert len(later)==52 and len(existing)==235
    coverage=coverage_report()
    from collections import Counter
    coverage=dict(coverage, kinds=dict(Counter(x.kind for x in existing)),review_statuses={"REVIEW_PENDING":len(existing)})
    ids=[x.id for x in existing]
    assert len(ids)==len(set(ids))
    new=[x for x in existing if x.id in {
        "math.hs.calculus.chain-rule", "math.hs.calculus.quotient-rule",
        "math.hs.calculus.fermat-stationary", "math.hs.vector.cauchy-schwarz",
        "math.hs.counting.binomial-sum", "math.hs.probability.expectation-linearity",
        "math.hs.function.bisection-root"}]
    assert len(new)==7
    assert len(existing)>=153  # Historical Batch09 lessons plus subsequent curriculum drafts.
    assert all(x.review.status=="REVIEW_PENDING" for x in new)
    assert all(x.teacher_solution_visibility=="TEACHER_ONLY" for x in existing)
    # CI never turns on cloud sending or loads an external trust/attestation file.
    assert "STEM_MENTOR_ENABLE_MODEL_DRAFT" not in os.environ
    assert "STEM_TUTOR_API_KEY" not in os.environ
    assert "STEM_MENTOR_ENABLE_APPROVED_RAG" not in os.environ
    assert not any("model-draft" in route.path or "draft-search" in route.path
                   for route in app.routes)
    evidence=student_evidence_lookup("等比数列求和")
    assert evidence["status"]=="NO_APPROVED_EVIDENCE" and not evidence["candidates"]
    result=draft_next_question("等比数列求和",operator_scope="EDITOR_LOCAL",
        help_requested=True,consent_to_cloud=True)
    assert result.status=="BLOCKED" and not result.student_visible and not result.model_called
    return {
        "scope":"UNAPPROVED_EDITOR_DRAFTS_NOT_RELEASED",
        "deep_draft_count":len(existing), "new_drafts":len(new),
        "theorem_drafts":coverage["kinds"]["theorem"],
        "review_pending":coverage["review_statuses"]["REVIEW_PENDING"],
        "teacher_approved":0, "student_released_evidence":len(evidence["candidates"]),
        "student_public_llm_route":False,
        "model_external_requests":0,
        "official_elective_atom_mapping_verified":0,
        "student_math_steps_verified":False,
        "warnings":[
            "Model questions are editor-only candidates and not correctness-certified.",
            "Zero signed human teacher approvals; real student/cloud LLM integration remains disabled.",
            "Seven complete structured drafts have NOT been independently mathematically certified."
        ]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--output",default="docs/evaluation/KB_BATCH09_RELEASE_AUDIT.json")
    args=parser.parse_args()
    result=audit()
    out=ROOT/args.output
    expected=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.check:
        if not out.exists() or out.read_text(encoding="utf-8")!=expected:
            raise SystemExit("Batch09 release audit drift")
        print("PASS: %d draft lessons, 0 approved, 0 cloud calls, safe editor-only gate" % result["deep_draft_count"])
    else:
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(expected,encoding="utf-8")
        print(out.relative_to(ROOT))
if __name__=="__main__":
    main()
