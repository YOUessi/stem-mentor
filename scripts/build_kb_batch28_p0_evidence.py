#!/usr/bin/env python3
"""Author-curated P0 condition review, bound to original step hash + exact fixtures.

This does NOT verify entire theorem proofs, approve lessons or certify free-form
student answers; even a mathematically valid fixture is evidence for its instance.
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from kb_frozen_batch24 import frozen_batch24_lessons
from app.kb_batch28_condition_oracles import SUPPORTED, evaluate

MANIFEST=ROOT/"knowledge/proof/batch28_p0_condition_profiles.json"
HISTORY=ROOT/"docs/evaluation/KB_BATCH25_P0_PROOF_AND_CONFLICT_TRIAGE.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH28_P0_CONDITION_REVIEW.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build(manifest=None, history=None):
    manifest=load(MANIFEST) if manifest is None else manifest
    history=load(HISTORY) if history is None else history
    if manifest["schema_version"]!="kb-batch28-p0-conditions-v1" or manifest["teacher_review"]!="PENDING" or manifest["student_visibility"]!="NEVER_STUDENT_EXPOSE" or manifest["complete_proof_certificates"]!=0:
        raise ValueError("Manifest authority or format drift")
    risk={x["id"]:x for x in history["p0_review_queue"]}
    if len(risk)!=127 or len(history["p0_review_queue"])!=127:
        raise ValueError("Historical 127 P0 baseline changed")
    indexed={doc.id:doc for doc in frozen_batch24_lessons()}
    if len(indexed)!=287:
        raise ValueError("Base Batch26 corpus changed; explicit rebaseline required")
    if len(manifest["profiles"])!=17:
        raise ValueError("Expected 17 hand-authored condition profiles")
    records=[]
    used=set()
    families=Counter()
    for p in manifest["profiles"]:
        op=p["operation"]
        if op not in SUPPORTED or p["teacher_review"]!="PENDING" or p["status"]!="EDITORIAL_CONDITION_PROPOSAL_NOT_PROOF":
            raise ValueError("Unsupported operation or forged reviewer status")
        if len(p["necessary_hypotheses"])<28 or len(p["explanatory_counterexample"])<25:
            raise ValueError("Shallow or missing original mathematical conditions/counterexample")
        if not p["risk_step_ids"]:
            raise ValueError("Profile without P0 obligations")
        good=evaluate(op,p["valid_exact_fixture"])
        bad=evaluate(op,p["invalid_fixture"])
        if good["status"]!="VERIFIED_FINITE_INSTANCE" or bad["status"]!="CONDITIONS_NOT_ESTABLISHED":
            raise ValueError(f"Incorrect valid/invalid fixture: {op} {good['status']} {bad['status']}")
        for outcome in (good,bad):
            if any(outcome[k] for k in ("student_step_verified","complete_theorem_certified","teacher_approved","official_curriculum_atom_verified")):
                raise ValueError("Improper promotion of finite check to authoritative proof/approval")
        for id_ in p["risk_step_ids"]:
            if id_ in used or id_ not in risk:
                raise ValueError("Duplicate, missing or untracked P0 step: "+id_)
            used.add(id_)
            rec=risk[id_]
            doc=indexed.get(rec["lesson_id"])
            if doc is None or doc.review.status!="REVIEW_PENDING" or doc.teacher_solution_visibility!="TEACHER_ONLY":
                raise ValueError("Missing or publicly visible original lesson")
            n=rec["index"]
            if not 1<=n<=len(doc.proof_steps):
                raise ValueError("Out-of-range original step index")
            step=doc.proof_steps[n-1]
            actual=hashlib.sha256((step.claim+"\0"+step.reason).encode()).hexdigest()
            if rec["verified_original_step_sha256"]!=actual or rec["proof_status"]!="NOT_FORMALLY_VERIFIED" or rec["teacher_review"]!="PENDING":
                raise ValueError("Original P0 proof claim/reason changed or falsely certified")
            records.append(dict(
                risk_step_id=id_,lesson_id=rec["lesson_id"],step_index=n,claim_reason_sha256=actual,
                operation=op,necessary_hypotheses=p["necessary_hypotheses"],
                counterexample_or_failure_mode=p["explanatory_counterexample"],
                bounded_valid_instance=good,bounded_invalid_case=bad,
                risk_groups=rec["risk_groups"],math_status="CONDITION_WITNESSES_ONLY_NOT_PROOF",
                complete_proof_certified=False,human_mathematical_review="PENDING",
                teacher_review="PENDING",student_step_verified=False,student_publishable=False))
            families[op]+=1
    if len(records)!=35 or sum(families.values())!=35:
        raise ValueError("Expected 35 independently selected P0 source steps")
    data=dict(schema_version="kb-batch28-p0-conditions-reviewed-as-proposals-v1",
        purpose="TRACEABLE_EDITORIAL_HYPOTHESES_AND_BOUNDED_EXACT_CASES_NOT_UNIVERSAL_PROOFS",
        sources=dict(p0_triage_sha256=sha(HISTORY),author_profiles_sha256=sha(MANIFEST)),
        summary=dict(total_historical_p0=127,p0_with_curated_hypotheses_and_counterexamples=35,
                     p0_not_yet_curated=92, distinct_guarded_exact_oracles=17,
                     exact_valid_fixtures_passed=17,negative_condition_fixtures_rejected=17,
                     full_formal_proofs_certified=0,teacher_approvals=0,
                     resolved_historical_conflicts=0,all_unverified_proof_steps=538,
                     official_verified_atomic_denominator=None,student_published_lessons=0),
        oracle_distribution=dict(sorted(families.items())),
        reviewed_step_proposals=sorted(records,key=lambda x:x["risk_step_id"]),
        unresolved_p0_step_ids=sorted(set(risk)-used),
        warnings=[
          "Only 35 of 127 frozen P0 natural-language steps have curated condition review proposals.",
          "Each exact oracle checks specific bounded operands, not its theorem for all admissible inputs.",
          "P0 source SHA is integrity evidence only; no natural-language proof step was formally certified.",
          "All 287 deep lessons remain REVIEW_PENDING/TEACHER_ONLY; no student disclosure."
        ])
    return json.dumps(data,ensure_ascii=False,indent=2)+"\n"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    s=build()
    if args.check:
        if not REPORT.exists() or REPORT.read_text(encoding="utf-8")!=s:
            raise SystemExit("Batch28 K07 condition-review report differs from source")
    else: REPORT.write_text(s,encoding="utf-8")
    print("PASS 35/127 P0 condition proposals; 17 exact-positive+17 negative guards; 0 formal proofs, 0 approvals")

if __name__=="__main__":main()
