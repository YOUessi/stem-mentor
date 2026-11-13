#!/usr/bin/env python3
"""Fail-closed K01/K07 corpus and proof-review queue audit for Batch24.

SHA256 tracks unverified proof text, not its truth. No teacher signatures, no
student free-text proof certification, no full curriculum claims are inferred.
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import DeepLesson, curriculum, lessons
from app.deep_retrieval import student_evidence_lookup
from app.official_clause_audit import TRACKS
from author_kb_batch24 import build as authored
from build_kb_batch24_scope import build as scope_build

OUT=ROOT/"docs/evaluation/KB_BATCH24_INTEGRITY_AND_PROOFS.json"
SOURCE=ROOT/"curriculum/highschool_math/author_seed_batch24.jsonl"
CORPUS=ROOT/"knowledge/deep/v1/core_foundation_batch24.json"
PRIOR=ROOT/"docs/evaluation/KB_BATCH23_INTEGRITY_AND_SCOPE.json"
SCOPE=ROOT/"docs/evaluation/KB_BATCH24_SOURCE_CROSSWALK.json"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
    if CORPUS.read_text(encoding="utf-8")!=authored():
        raise ValueError("Author-to-deep-corpus mismatch")
    if SCOPE.read_text(encoding="utf-8")!=scope_build():
        raise ValueError("Unverified source crosswalk not current")
    corpus=read(CORPUS);old=read(PRIOR);scope=read(SCOPE)
    # Historical Batch24 checks must stay reproducible after later batches
    # add legitimate drafts to the live corpus. The exact Batch24 snapshot
    # remains frozen at 287; the live registry is allowed to grow, not shrink.
    if len(corpus)!=20 or len(curriculum())!=178 or len(lessons())<287:
        raise ValueError("Historical corpus or engineering map totals mismatched")
    if old["current_unverified_proof_steps"]!=519 or old["summary"]["deep_lesson_drafts_expected"]!=267:
        raise ValueError("Previously frozen proof obligations not preserved")
    if old["certified_whole_proofs"] or old["teacher_approved"]:
        raise ValueError("Historical unverified content cannot be approved")
    if scope["summary"]["verified_official_atomic_denominator"] is not None:
        raise ValueError("K00 scope is still unverified")
    known={c["id"]:c for c in curriculum()}
    new_proofs=[];types=Counter();by_track=Counter();all_lessons={d.id:d for d in lessons()}
    for d in corpus:
        m=DeepLesson.model_validate(d)
        if d!=m.model_dump(mode="json") or all_lessons[m.id].model_dump(mode="json")!=d:
            raise ValueError("Schema or live retrieval mismatch")
        if m.review.status!="REVIEW_PENDING" or m.teacher_solution_visibility!="TEACHER_ONLY":
            raise ValueError("Unapproved lesson disclosed")
        if len(m.curriculum_ids)!=1 or len(m.worked_examples)!=2 or len(m.hint_ladder)!=3:
            raise ValueError("Lesson requires distinct problems and safe hints")
        cid=m.curriculum_ids[0]
        if cid not in known or known[cid]["level"] not in ("必修","选择性必修"):
            raise ValueError("Batch24 must deepen required-track content")
        if known[cid]["source"]["teacher_review"]!="PENDING":
            raise ValueError("Engineering course map was falsely approved")
        types[m.kind]+=1
        by_track["COMPULSORY" if known[cid]["level"]=="必修" else "SELECTIVE_COMPULSORY"]+=1
        for i,step in enumerate(m.proof_steps,1):
            proof_sha=hashlib.sha256((step.claim+"\x00"+step.reason).encode("utf-8")).hexdigest()
            new_proofs.append(dict(id=m.id+"#"+str(i),claim_reason_sha256=proof_sha,
                priority="P0_UNVERIFIED_STEP_REQUIRES_DOMAIN_CHECK",
                status="NOT_FORMALLY_VERIFIED",whole_theorem_certified=False,
                teacher_review="PENDING",student_publishable=False))
    if len({x["id"] for x in new_proofs})!=len(new_proofs):
        raise ValueError("Duplicate proof obligations")
    if student_evidence_lookup("高中数学 求根 三角函数 正弦定理")["status"]!="NO_APPROVED_EVIDENCE":
        raise ValueError("Student retrieval release leaked unapproved draft")
    if any(x["verified_official_atomic_denominator"] is not None for x in scope["by_track"]):
        raise ValueError("Unofficial denominator masquerading as official")
    info=dict(schema_version="batch24-k01-k07-audit-v1",
         scope="MACHINE_SCHEMA_AND_FINITE_PROOF_TEXT_INTEGRITY_NOT_TEACHER_MATH_CERTIFICATION",
         frozen_sha256=dict(batch23_proofs=sha(PRIOR),source_crosswalk=sha(SCOPE),
             authored_source=sha(SOURCE),materialized_lesson_corpus=sha(CORPUS)),
         # The frozen historical snapshot is not a live total.
         summary=dict(current_draft_lessons=287,new_required_core_lessons=len(corpus),
             new_teacher_side_examples=sum(len(x["worked_examples"]) for x in corpus),
             new_by_kind=dict(sorted(types.items())),new_required_by_track=dict(sorted(by_track.items())),
             frozen_history_unverified_proof_steps=519,new_unverified_proof_steps=len(new_proofs),
             all_unverified_proof_steps=519+len(new_proofs),historical_p0_pending=127,
             historical_conflict_pairs_pending=10,unresolved_official_k00_review_tasks=427,
             verified_official_atomic_denominator=None,verified_official_coverage_rate=None,
             approved_teacher_lessons=0,student_published_deep_lessons=0,
             whole_proofs_certified=0,student_freetext_steps_verified=0),
         new_unverified_proof_review_queue=new_proofs,
         official_tracks=[dict(track=x["track"],
             source_numbered_marker_candidates=x["numbered_pdf_marker_candidates"],
             editorial_objective_candidates=x["project_authored_editorial_objectives"],
             official_verified_atom_denominator=None,official_coverage_rate=None)
             for x in scope["by_track"]],
         warnings=[
             "Added proof text hashes only prove no drift of claim and reason, never soundness of a proof.",
             "The 315 marker and 132 editorial ledgers overlap; page proximity cannot certify clause correspondence.",
             "All 20 teacher-only problem answers are excluded from student RAG; unapproved lessons remain REVIEW_PENDING.",
             "Historical P0 proof review and ten conflicts remain unresolved; full teacher audit is mandatory."])
    return json.dumps(info,ensure_ascii=False,indent=2)+"\n"
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    args=p.parse_args();body=build()
    if args.check:
        if OUT.read_text(encoding="utf-8")!=body:raise SystemExit("Batch24 integrity snapshot drift")
    else:OUT.write_text(body,encoding="utf-8")
    summary=json.loads(body)["summary"]
    print("PASS: Batch24",summary["new_required_core_lessons"],"lesson drafts,",summary["new_unverified_proof_steps"],"unverified proof steps,",summary["all_unverified_proof_steps"],"in all; official denominator NULL")
if __name__=="__main__":main()
