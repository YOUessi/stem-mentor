#!/usr/bin/env python3
"""Explicit human-editable elective candidate -> deep draft *review suggestions*.

No fuzzy lexical matching, no promotion to syllabus coverage or student RAG.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"backend"))
from kb_frozen_batch24 import frozen_batch24_lessons
import build_kb_batch33_elective_scope as scope
TSV=ROOT/"curriculum/highschool_math/k00_batch33_draft_associations.tsv"
REPORT=ROOT/"docs/evaluation/KB_BATCH33_DRAFT_CROSSWALK_AUDIT.json"
PIN="6dddfc4f5d8e92b5302ca05c456fc9a6bed9b834f47d66f0429ba1091c6c02a4"
LESSONS_DIR=ROOT/"knowledge/deep/v1"

def lessons():
    frozen_ids={d.id for d in frozen_batch24_lessons()}
    rows={}
    for f in sorted(LESSONS_DIR.glob("*.json")):
        doc=json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(doc,list):continue
        for lesson in doc:
            ident=lesson["id"]
            if ident not in frozen_ids: continue  # exclude post-Batch24 drafts
            if ident in rows:raise ValueError("Duplicate deep lesson id")
            if lesson["review"]["status"]!="REVIEW_PENDING" or lesson["teacher_solution_visibility"]!="TEACHER_ONLY":
                raise ValueError("Draft review/visibility contract changed")
            rows[ident]=dict(title=lesson["title"],kind=lesson["kind"],path=str(f.relative_to(ROOT)))
    if len(rows)!=287:
        raise ValueError("Expected frozen 287 review-pending deep lessons; rebaseline explicitly")
    return rows

def build(seed:str|None=None,scope_audit:dict|None=None):
    if seed is None:
        if hashlib.sha256(TSV.read_bytes()).hexdigest()!=PIN:
            raise ValueError("Curated crosswalk SHA drift")
        seed=TSV.read_text(encoding="utf-8")
    expected=json.loads(scope.build())
    if scope_audit is not None and scope_audit!=expected:
        raise ValueError("Source audit substituted")
    saved=json.loads(scope.REPORT.read_text(encoding="utf-8"))
    if saved!=expected:raise ValueError("Source audit report drift")
    candidates={x["editorial_id"]:x for x in saved["editorial_goals"]}
    drafts=lessons()
    seen=set()
    pairs=[]
    for line in seed.splitlines():
        if not line.strip() or line.startswith("#"):continue
        parts=[p.strip() for p in line.split("|")]
        if len(parts)!=3:raise ValueError("Crosswalk requires exactly 3 source fields")
        atom,lesson,reason=parts
        if atom in seen or atom not in candidates or lesson not in drafts:
            raise ValueError("Duplicate candidate or unknown draft/atom")
        if len(reason)<14 or len(reason)>180 or "已审核" in reason or "完全覆盖" in reason:
            raise ValueError("Misleading or weak math relation annotation")
        seen.add(atom)
        c=candidates[atom];d=drafts[lesson]
        pairs.append(dict(editorial_candidate_id=atom,original_editorial_goal=c["original_project_authored_goal"],
            candidate_track=c["syllabus_track"],candidate_source_page=c["source_printed_page"],
            related_draft_lesson_id=lesson,related_draft_title=d["title"],
            draft_source_path=d["path"],math_relation_editorial_reason=reason,
            association_status="HUMAN_REVIEW_REQUIRED_NOT_CLAUSE_COVERAGE",
            exact_official_clause_alignment_verified=False,
            mathematically_equivalent_content_certified=False,
            curriculum_atom_covered=False,teacher_review="PENDING",
            draft_solution_visible_to_student=False))
    if len(pairs)<30:raise ValueError("Crosswalk too small for this batch")
    summary=dict(total_deep_lessons_existing=len(drafts),
        source_editorial_elective_candidates=len(candidates),
        suggested_related_draft_pairs=len(pairs),
        no_suggested_related_draft=len(candidates)-len(pairs),
        editorial_suggestions_by_track=dict(Counter(p["candidate_track"] for p in pairs)),
        authentic_teacher_review_count=0,approved_lessons=0,
        official_atom_denominator=None,official_coverage_rate=None,
        student_released_answers=0)
    report=dict(schema_version="kb-batch33-curated-related-drafts-v1",
        purpose="EXPLICIT_MATH_EDITORIAL_REVIEW_SUGGESTIONS_NOT_OFFICIAL_ATOM_COVERAGE",
        input_editorial_seed_sha256=scope.SEED_SHA,curated_pair_seed_sha256=PIN,
        summary=summary,links=pairs,
        unmatched_candidate_ids=sorted(set(candidates)-seen),
        policy=dict(search_index_modified=False,student_exposed=False,
            automatic_lexical_equalization_used=False,teacher_approved=False,
            no_full_solution_copied=True,
            required_followup="Check exact official clause, detailed math equivalence, proofs, counterexamples, and teacher signoff"))
    return json.dumps(report,ensure_ascii=False,indent=2)+"\n"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    doc=build()
    if args.check:
        if REPORT.read_text(encoding="utf-8")!=doc:raise SystemExit("Crosswalk audit drift")
    else:REPORT.write_text(doc,encoding="utf-8")
    print("PASS Batch33",len(json.loads(doc)["links"]),"curated related-draft review pairs; 0 certified equivalences")
if __name__=="__main__":main()
