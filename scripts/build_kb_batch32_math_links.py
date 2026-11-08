#!/usr/bin/env python3
"""Auditable manually selected finite-oracle links to editorial K00 candidates."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.kb_batch32_selective_finite_math import OPS,guarded_evaluate
LINKS=ROOT/"knowledge/proof/kb_batch32_selective_finite_fixture_links.json"
ATOMS=ROOT/"docs/evaluation/KB_BATCH32_K00_CORE_SELECTIVE_ATOM_AUDIT.json"
OUT=ROOT/"docs/evaluation/KB_BATCH32_MATH_FINITE_LINK_AUDIT.json"
EXPECTED={
 "arithmetic_series":"KB32-SELE-P038-A005",
 "conditional_probability_finite":"KB32-SELE-P047-A003",
 "hypergeometric_mass":"KB32-SELE-P047-A012",
 "point_line_distance_squared":"KB32-SELE-P044-A001",
 "binomial_choice":"KB32-SELE-P046-A005",
 "least_squares_line":"KB32-SELE-P048-A005"
}
def build(links=None):
    from build_kb_batch32_source_atoms import build as atom_build
    atoms=json.loads(atom_build())["new_items"]
    lookup={x["editorial_id"]:x for x in atoms}
    d=json.loads(LINKS.read_text(encoding="utf8")) if links is None else links
    if (d["scope"]!="EDITORIAL_CANDIDATE_TO_FINITE_INSTANCE_ONLY_NOT_OFFICIAL_OR_TEACHER_VERIFIED"
        or d["official_atomic_denominator"] is not None
        or d["teacher_approved"] is not False or d["student_publishable"] is not False):
        raise ValueError("Forged source/release boundary")
    fixtures=d["fixtures"]
    if type(fixtures) is not list or len(fixtures)!=len(OPS):
        raise ValueError("Every bounded exact witness must have one fixture")
    if {x["op"]:x["editorial_id"] for x in fixtures}!=EXPECTED or len(fixtures)!=len(OPS):
        raise ValueError("Math witness mapped to wrong editorial source candidate")
    records=[]
    for f in fixtures:
        if f["editorial_id"] not in lookup or f["op"] not in OPS or len(f["math_justification"])<44:
            raise ValueError("Unreviewed math-atom link")
        good=guarded_evaluate(f["op"],f["valid"])
        bad=guarded_evaluate(f["op"],f["invalid"])
        if good["status"]!="VERIFIED_FINITE_INSTANCE" or bad["status"]!="CONDITIONS_NOT_ESTABLISHED":
            raise ValueError("Invalid fixture did not refuse or valid fixture failed")
        for r in (good,bad):
            if any(r[k] for k in ("whole_theorem_certified","student_freeform_step_verified",
                                  "teacher_approved","official_curriculum_atom_verified",
                                  "student_solution_release_authorized")):
                raise ValueError("Finite test forged full mathematical/teaching approval")
        records.append(dict(
          op=f["op"],editorial_id=f["editorial_id"],
          track=lookup[f["editorial_id"]]["syllabus_track"],
          page=lookup[f["editorial_id"]]["source_printed_page"],
          math_justification=f["math_justification"],
          legal_status=good["status"],legal_witness={k:str(v) for k,v in good["witness"].items()},
          invalid_condition_status=bad["status"],invalid_rejection_reason=bad["reason"],
          entire_statement_proven=False,student_freeform_solution_verified=False,
          teacher_reviewer_id=None,student_publishable=False))
    return json.dumps(dict(schema_version="kb-batch32-finite-math-source-links-v1",
       scope="SIX_FINITE_INSTANCE_GUARDS_NOT_THEOREM_CERTIFICATES",
       source_atoms_sha256=hashlib.sha256(ATOMS.read_bytes()).hexdigest(),
       summary=dict(checked_editorial_links=len(records),legal_finite_fixtures_passed=len(records),
                    invalid_fixtures_refused=len(records),formal_general_proof_certificates=0,
                    student_freetext_steps_verified=0,teacher_approved=0),
       items=records,teacher_release_unchanged=True),ensure_ascii=False,indent=2)+"\n"

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
    v=build()
    if a.check:
        if OUT.read_text(encoding="utf8")!=v:raise SystemExit("Batch32 finite math audit drift")
    else:OUT.write_text(v,encoding="utf8")
    print("PASS K07 Batch32 6 legal exact cases, 6 invalid refusals, zero teacher/theorem certifications")
if __name__=="__main__":main()
