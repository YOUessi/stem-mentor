#!/usr/bin/env python3
"""Batch30: independently trace the final 44 historical P0 proof steps.

This report is an editorial *review queue*, not formal proof certification.
The finite exact oracles are separate bounded numerical witnesses.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from kb_frozen_batch24 import frozen_batch24_lessons
from app.kb_batch30_exact_witnesses import SUPPORTED,evaluate

HISTORY=ROOT/"docs/evaluation/KB_BATCH25_P0_PROOF_AND_CONFLICT_TRIAGE.json"
B28=ROOT/"docs/evaluation/KB_BATCH28_P0_CONDITION_REVIEW.json"
B29=ROOT/"docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json"
EDITORIAL=ROOT/"knowledge/proof/batch30_last44_editorial_reviews.json"
FIXTURES=ROOT/"knowledge/proof/batch30_finite_witness_fixtures.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json"

def load(p):return json.loads(p.read_text(encoding="utf8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def build(editorial=None,fixtures=None,history=None,prior28=None,prior29=None):
    h=history if history is not None else load(HISTORY)
    p28=prior28 if prior28 is not None else load(B28)
    p29=prior29 if prior29 is not None else load(B29)
    e=editorial if editorial is not None else load(EDITORIAL)
    fx=fixtures if fixtures is not None else load(FIXTURES)
    frozen=h["p0_review_queue"]
    risk={v["id"]:v for v in frozen}
    if len(frozen)!=127 or len(risk)!=127: raise ValueError("Frozen P0 source risk set not 127 unique")
    a={x["risk_step_id"] for x in p28["reviewed_step_proposals"]}
    b={x["risk_step_id"] for x in p29["new_editorial_step_proposals"]}
    if (len(a),len(b),len(a&b))!=(35,48,0):raise ValueError("Prior editorial partitions incomplete or overlapping")
    if set(p29["previous_step_ids"])!=a or set(p29["remaining_unreviewed_step_ids"])!=set(risk)-a-b:
        raise ValueError("Prior Batch29 unreviewed baseline tampered")
    remain=set(risk)-a-b
    if len(remain)!=44:raise ValueError("Expected final 44 P0 editorial steps")
    if (e.get("schema_version")!="kb-batch30-p0-last44-editorial-v1"
            or e.get("authority")!="NO_FORMAL_PROOF_OR_TEACHER_APPROVAL"
            or e.get("student_visibility")!="NEVER_STUDENT_EXPOSE"
            or e.get("review_state")!="REVIEW_PENDING"):
        raise ValueError("Editorial authority / student-visibility drift")
    entries=e.get("entries",[])
    if len(entries)!=44 or {x["risk_step_id"] for x in entries}!=remain:
        raise ValueError("Must explicitly author exactly the remaining 44 source-linked proof-step notes")
    if len({x["risk_step_id"] for x in entries})!=44:
        raise ValueError("Duplicate historical step review")
    if fx.get("schema_version")!="kb-batch30-finite-exact-cases-v1" or fx.get("authority")!="FINITE_RATIONAL_EXAMPLES_ONLY_NO_PROOF":
        raise ValueError("Finite fixture authority drift")
    items=fx.get("fixtures",[])
    if len(items)!=20 or {x["operation"] for x in items}!=SUPPORTED:
        raise ValueError("Must maintain 20 exact and invalid-domain witness families")
    if len({x["operation"] for x in items})!=20:raise ValueError("Duplicate exact fixture")
    witness_rows=[]
    for item in items:
        if item.get("teacher_review")!="PENDING" or item.get("status")!="BOUNDED_EXAMPLE_NOT_UNIVERSAL_PROOF":
            raise ValueError("Finite witness misrepresented as proof or approved")
        op=item["operation"]
        good=evaluate(op,item["valid_exact_fixture"])
        bad=evaluate(op,item["invalid_fixture"])
        if good["status"]!="VERIFIED_FINITE_INSTANCE" or bad["status"]!="CONDITIONS_NOT_ESTABLISHED":
            raise ValueError(f"Broken mathematical positive/negative fixtures: {op}")
        for v in (good,bad):
            if any(v[k] for k in ("student_step_verified","complete_theorem_certified","teacher_approved","official_curriculum_atom_verified")):
                raise ValueError("Unsupported proof/student/teacher promotion")
        witness_rows.append(dict(operation=op,good=good,bad=bad))
    index={x.id:x for x in frozen_batch24_lessons()}
    if len(index)!=287:raise ValueError("287 existing lessons changed: explicit rebaseline required")
    rows=[]
    for r in entries:
        id_=r["risk_step_id"]
        if r.get("math_status")!="EDITORIAL_CONDITIONS_WITH_EXPLICIT_COUNTEREXAMPLE_NOT_CERTIFIED" or r.get("human_math_review")!="PENDING" or r.get("teacher_review")!="PENDING" or r.get("student_publishable") is not False:
            raise ValueError("Proof audit status must stay pending and teacher-only")
        for k,length in (("necessary_hypotheses",50),("explanatory_counterexample",30),("next_review_action",15)):
            if not isinstance(r.get(k),str) or len(r[k])<length:
                raise ValueError(f"Substantive and case-specific editorial mathematical audit missing: {id_}/{k}")
        rec=risk[id_]
        lesson=index[rec["lesson_id"]]
        if lesson.review.status!="REVIEW_PENDING" or lesson.teacher_solution_visibility!="TEACHER_ONLY":
            raise ValueError("Existing lesson review/teacher visibility drift")
        step=lesson.proof_steps[rec["index"]-1]
        digest=hashlib.sha256((step.claim+"\0"+step.reason).encode("utf8")).hexdigest()
        if rec["verified_original_step_sha256"]!=digest or rec["proof_status"]!="NOT_FORMALLY_VERIFIED" or rec["teacher_review"]!="PENDING":
            raise ValueError(f"Source proof claim/reason/authority drift: {id_}")
        rows.append(dict(risk_step_id=id_,lesson_id=lesson.id,source_proof_step=rec["index"],
            exact_original_claim_reason_sha256=digest,original_claim=step.claim,original_reason=step.reason,
            necessary_hypotheses=r["necessary_hypotheses"],explanatory_counterexample=r["explanatory_counterexample"],
            next_review_action=r["next_review_action"],math_status=r["math_status"],
            proof_status="NOT_FORMALLY_VERIFIED",human_math_review="PENDING",teacher_review="PENDING",
            complete_proof_certified=False,student_step_verified=False,student_publishable=False))
    if len(rows)!=44:raise ValueError("44 editorial review audit missing")
    return json.dumps(dict(
        schema_version="kb-batch30-all-historical-p0-editorial-conditions-v1",
        evidence_boundary="SOURCE_HASH_PLUS_CASE_SPECIFIC_HUMAN_AUTHORED_MATH_HYPOTHESES_NOT_FORMAL_PROOF",
        source_sha256=dict(historical_p0=sha(HISTORY),batch28=sha(B28),batch29=sha(B29),
            batch30_editorial=sha(EDITORIAL),batch30_finite_witnesses=sha(FIXTURES)),
        summary=dict(historical_p0_count=127,previous_batch28_editorial=35,previous_batch29_editorial=48,
            batch30_new_editorial=44,total_with_explicit_editorial_math_condition_reviews=127,
            still_without_editorial_condition_review=0,formally_verified_historical_steps=0,
            formally_unverified_proof_steps_total=538,unresolved_historical_conflicts=10,
            batch30_new_exact_math_witness_families=20,batch30_valid_finite_examples=20,
            batch30_invalid_conditions_rejected=20,
            authentic_teacher_approvals=0,student_published_deep_lessons=0,
            official_compulsory_knowledge_atom_denominator=None,
            official_selective_knowledge_atom_denominator=None,
            official_elective_knowledge_atom_denominator=None),
        prior_editorial_ids=sorted(a|b),
        batch30_new_editorial_rows=sorted(rows,key=lambda x:x["risk_step_id"]),
        unresolved_editorial_ids=[],
        mathematical_finite_witness_examples=sorted(witness_rows,key=lambda x:x["operation"]),
        warnings=[
            "EDITORIAL REVIEW COVERAGE 127/127 IS NOT MATHEMATICAL PROOF CERTIFICATION.",
            "All 538 natural-language proof steps remain NOT_FORMALLY_VERIFIED; the finite exact witnesses do not prove general statements.",
            "No real human teacher review has been performed; no draft is publishable or approved.",
            "20 finite rational checks cannot validate student free-text proofs; source version and official curriculum atoms remain unverified."
        ]),ensure_ascii=False,indent=2)+"\n"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    result=build()
    if args.check:
        if REPORT.read_text(encoding="utf8")!=result:raise SystemExit("Batch30 frozen audit report drift")
    else:REPORT.write_text(result,encoding="utf8")
    print("PASS: 127/127 historical P0 steps have editorial condition reviews (35+48+44), 20 exact valid and 20 illegal-condition fixtures; formally certified=0, teacher-approved=0")

if __name__=="__main__":main()
