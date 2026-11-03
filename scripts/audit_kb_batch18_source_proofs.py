#!/usr/bin/env python3
"""Frozen Batch18 checks: page/marker evidence, 28 open gaps, 451 risk steps."""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.official_clause_audit import source_clause_ledger, page_progress
from app.k00_gap_audit import gap_tickets
from app.official_topic_outline import de_outline
from build_kb_batch18_unnumbered_outline import build as build_outline
from build_kb_batch18_gap_inventory import build as build_gap_tickets
from build_kb_batch18_proof_risks import build as build_proof_risks

def check():
    source_clause_ledger()  # count and trust boundary, not external text certification
    if de_outline() != build_outline():
        raise AssertionError("D/E source outline data drift")
    if page_progress()["official_atomic_knowledge_denominator"] is not None:
        raise AssertionError("Editorial clause count treated as official atom count")
    frozen_gap=gap_tickets()
    generated_gap=build_gap_tickets()
    if frozen_gap!=generated_gap:
        raise AssertionError("Batch18 gap tickets do not match frozen source data")
    proof_path=ROOT/"docs/evaluation/KB_BATCH18_SOURCE_AND_PROOF_RISK_AUDIT.json"
    frozen_proof=json.loads(proof_path.read_text(encoding="utf-8"))
    generated_proof=build_proof_risks()
    if generated_proof!=frozen_proof:
        raise AssertionError("Batch18 proof and conflict risk audit drift")
    if (frozen_proof["summary"]["whole_proofs_certified"]!=0 or
            frozen_proof["summary"]["versions_resolved"]!=0 or
            frozen_proof["summary"]["teacher_approved_lessons"]!=0):
        raise AssertionError("Unreviewed evidence falsely claimed approved")
    return frozen_proof["summary"]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    summary=check()
    print("Batch18 source/proof audit PASS:",json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()
