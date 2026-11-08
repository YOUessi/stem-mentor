#!/usr/bin/env python3
"""Validated five editorially linked finite exact math instances; not certification."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"backend"),str(ROOT/"scripts")]
from app.kb_batch33_elective_finite_math import OPS,guarded_evaluate
import build_kb_batch33_elective_scope as scope

SOURCE=ROOT/"knowledge/proof/kb_batch33_elective_finite_fixtures.json"
OUT=ROOT/"docs/evaluation/KB_BATCH33_FINITE_MATH_AUDIT.json"
SOURCE_SHA="bae1b1198311ef00266f9ad56e05559ec204ae10133a8401510c4ab5d8d5b088"
def build(fixtures=None):
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError("Pinned finite-fixture content modified")
    official=json.loads(scope.build())
    got=fixtures if fixtures is not None else json.loads(SOURCE.read_text(encoding="utf-8"))
    if set(got)!={"schema_version","teacher_approved","student_publishable","exact_official_clause_coverage","fixtures"}:
        raise ValueError("Fixture schema mismatch")
    if any(got[k] for k in ("teacher_approved","student_publishable","exact_official_clause_coverage")):
        raise ValueError("Forged release, certification or syllabus mapping")
    cands={x["editorial_id"]:x for x in official["editorial_goals"]}
    if len(got["fixtures"])!=len(OPS) or {x.get("op") for x in got["fixtures"]}!=set(OPS):
        raise ValueError("Missing, duplicated or invented finite oracle")
    evidence=[]
    for row in got["fixtures"]:
        if set(row)!={"op","editorial_id","valid","invalid","math_justification"}:
            raise ValueError("Unexpected fixture fields")
        atom=row["editorial_id"]
        if atom not in cands or len(row["math_justification"])<60:
            raise ValueError("Unanchored or weakly justified finite witness")
        good=guarded_evaluate(row["op"],row["valid"])
        bad=guarded_evaluate(row["op"],row["invalid"])
        if good["status"]!="VERIFIED_FINITE_INSTANCE" or bad["status"]!="CONDITIONS_NOT_ESTABLISHED":
            raise ValueError("Finite witness failed or out-of-domain instance was accepted")
        forbidden=("whole_theorem_certified","teacher_approved","student_freeform_step_verified",
                   "official_atomic_goal_certified","student_solution_release_authorized")
        if any(good[x] or bad[x] for x in forbidden):
            raise ValueError("False certification")
        evidence.append(dict(op=row["op"],editorial_id=atom,track=cands[atom]["syllabus_track"],
            scope="EXACT_FINITE_INPUT_ONLY",positive=good["status"],
            negative=bad["status"],witness=good["witness"],
            formal_general_proof_certificate=None,student_step_verification=None))
    result=dict(schema_version="kb-batch33-finite-math-editorial-v1",
        mathematical_evidence=evidence,
        summary=dict(operators=len(OPS),valid_instances=len(OPS),invalid_premises_rejected=len(OPS),
            universal_theorems_formally_certified=0,teacher_approved_lessons=0,
            verified_freeform_student_steps=0,official_atomic_goals_verified=0),
        safety=dict(student_index_unchanged=True,teacher_solution_not_exposed=True,
            finite_instance_does_not_imply_general_theorem=True))
    return json.dumps(result,ensure_ascii=False,indent=2)+"\n"
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    doc=build()
    if a.check:
        if OUT.read_text(encoding="utf-8")!=doc:raise SystemExit("Batch33 finite math audit drift")
    else: OUT.write_text(doc,encoding="utf-8")
    print("PASS Batch33 5 valid finite cases + 5 invalid-premise refusals, no general proof")
if __name__=="__main__":main()
