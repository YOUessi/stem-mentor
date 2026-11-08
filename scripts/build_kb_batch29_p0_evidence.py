#!/usr/bin/env python3
"""Batch29: independently trace another 48 historical P0 steps to curated conditions.
Never treat bounded arithmetic as a mathematical proof, teacher signoff or student solution.
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import lessons
from app.kb_batch29_exact_witnesses import SUPPORTED,evaluate

MANIFEST=ROOT/"knowledge/proof/batch29_p0_condition_profiles.json"
HISTORY=ROOT/"docs/evaluation/KB_BATCH25_P0_PROOF_AND_CONFLICT_TRIAGE.json"
PREVIOUS=ROOT/"docs/evaluation/KB_BATCH28_P0_CONDITION_REVIEW.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json"

def load(path):return json.loads(path.read_text(encoding="utf8"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def build(manifest=None,history=None,previous=None):
    m=load(MANIFEST) if manifest is None else manifest
    h=load(HISTORY) if history is None else history
    prev=load(PREVIOUS) if previous is None else previous
    if m.get("schema_version")!="kb-batch29-p0-conditions-v1" or m.get("student_visibility")!="NEVER_STUDENT_EXPOSE" or m.get("teacher_review")!="PENDING" or m.get("complete_proof_certificates")!=0:
        raise ValueError("Manifest integrity / teacher authority drift")
    if h.get("p0_review_queue") is None or len(h["p0_review_queue"])!=127:
        raise ValueError("Frozen historical P0 risk set drift")
    risk={x["id"]:x for x in h["p0_review_queue"]}
    if len(risk)!=127:raise ValueError("Repeated historical P0 id")
    older={x["risk_step_id"] for x in prev["reviewed_step_proposals"]}
    if len(older)!=35 or len(prev["unresolved_p0_step_ids"])!=92 or older & set(prev["unresolved_p0_step_ids"]) or (older|set(prev["unresolved_p0_step_ids"]))!=set(risk):
        raise ValueError("Prior 35-step editorial review baseline drift")
    if len(m.get("profiles",[]))!=20:raise ValueError("Require 20 independently curated mathematical boundary families")
    indexed={x.id:x for x in lessons()}
    if len(indexed)!=287:raise ValueError("287-draft frozen base changed: explicit rebaseline required")
    seen=set();families=Counter();rows=[]
    for p in m["profiles"]:
        op=p["operation"]
        if op not in SUPPORTED or families[op] or p.get("status")!="EDITORIAL_CONDITION_PROPOSAL_NOT_PROOF" or p.get("teacher_review")!="PENDING":
            raise ValueError("Duplicate or unsupported operation / forged authority")
        if len(p.get("necessary_hypotheses",""))<45 or len(p.get("explanatory_counterexample",""))<35:
            raise ValueError("Missing substantive conditions or counterexamples")
        if not 1<=len(p.get("risk_step_ids",[]))<=6:raise ValueError("Risk family mapping suspicious or empty")
        good=evaluate(op,p["valid_exact_fixture"])
        bad=evaluate(op,p["invalid_fixture"])
        if good["status"]!="VERIFIED_FINITE_INSTANCE" or bad["status"]!="CONDITIONS_NOT_ESTABLISHED":
            raise ValueError(f"Broken exact-positive / negative-condition witnesses: {op}, {good}, {bad}")
        for outcome in (good,bad):
            if any(outcome[k] for k in ("student_step_verified","complete_theorem_certified","teacher_approved","official_curriculum_atom_verified")):
                raise ValueError("Finite arithmetic falsely promoted to proof/review")
        for id_ in p["risk_step_ids"]:
            if id_ in seen or id_ in older or id_ not in risk:
                raise ValueError(f"Overlap, duplicate or absent original P0 step: {id_}")
            seen.add(id_)
            rec=risk[id_]
            doc=indexed.get(rec["lesson_id"])
            if doc is None or doc.review.status!="REVIEW_PENDING" or doc.teacher_solution_visibility!="TEACHER_ONLY":
                raise ValueError("Lesson not pending/teacher-only")
            n=rec["index"]
            if not 1<=n<=len(doc.proof_steps):
                raise ValueError("Incorrect original proof step index")
            step=doc.proof_steps[n-1]
            actual=hashlib.sha256((step.claim+"\0"+step.reason).encode("utf8")).hexdigest()
            if rec.get("verified_original_step_sha256")!=actual or rec.get("proof_status")!="NOT_FORMALLY_VERIFIED" or rec.get("teacher_review")!="PENDING":
                raise ValueError("Original P0 claim/reason hash or proof status drift")
            rows.append(dict(risk_step_id=id_,lesson_id=doc.id,original_step_index=n,claim_reason_sha256=actual,
                source_claim=step.claim,source_reason=step.reason,
                operation=op,necessary_hypotheses=p["necessary_hypotheses"],
                counterexample_or_failure_mode=p["explanatory_counterexample"],
                bounded_valid_instance=good,bounded_invalid_case=bad,
                math_status="BOUNDED_EXACT_WITNESSES_ONLY_NOT_PROOF",proof_status="NOT_FORMALLY_VERIFIED",
                complete_proof_certified=False,human_math_review="PENDING",teacher_review="PENDING",
                student_publishable=False,student_step_verified=False))
            families[op]+=1
    if len(seen)!=48 or sum(families.values())!=48 or set(families)!=SUPPORTED:
        raise ValueError("Expected exactly 48 new non-overlapping original P0 steps in 20 curated families")
    covered=seen|older
    if len(covered)!=83 or len(set(risk)-covered)!=44:raise ValueError("Unresolved P0 count mismatch")
    report=dict(schema_version="kb-batch29-p0-review-v1",
        evidence_boundary="SOURCE_SHA_PLUS_EDITORIAL_MATH_CONDITIONS_AND_FINITE_EXACT_WITNESSES_NOT_UNIVERSAL_PROOFS",
        source_sha256=dict(historical_p0_queue=sha(HISTORY),batch28_review=sha(PREVIOUS),batch29_authored_profiles=sha(MANIFEST)),
        summary=dict(total_historical_p0=127,previously_curated_p0=35,newly_curated_p0=48,
            total_with_editorial_condition_proposals=83,still_missing_curated_conditions=44,
            batch29_distinct_finite_math_oracles=20,valid_exact_fixtures=20,invalid_condition_fixtures=20,
            formally_certified_historical_steps=0,unverified_proof_steps_total=538,
            teacher_approvals=0,student_published_lessons=0,unresolved_historical_conflicts=10,
            official_compulsory_atom_denominator=None,official_selective_atom_denominator=None,
            official_elective_atom_denominator=None),
        operation_distribution=dict(sorted(families.items())),
        new_editorial_step_proposals=sorted(rows,key=lambda x:x["risk_step_id"]),
        previous_step_ids=sorted(older),
        remaining_unreviewed_step_ids=sorted(set(risk)-covered),
        audit_warnings=[
          "Original source claim/reason SHA protects text integrity; it does not certify its mathematical correctness.",
          "20 exact fixture checks and independent tests cover bounded instances only; all 538 proof steps remain NOT_FORMALLY_VERIFIED.",
          "48 new reviews are editor-only condition proposals; no teacher signoff, no student retrieval and no official syllabus atom count."
        ])
    return json.dumps(report,ensure_ascii=False,indent=2)+"\n"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    txt=build()
    if args.check:
        if REPORT.read_text(encoding="utf8")!=txt:raise SystemExit("Batch29 P0 report drift")
    else:REPORT.write_text(txt,encoding="utf8")
    print("PASS: 48 new P0 step condition profiles + 35 previous = 83/127, 44 remain, 20 exact and 20 negative fixtures, 0 proofs certified")

if __name__=="__main__":main()
