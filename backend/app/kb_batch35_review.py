"""Batch35 teacher-only editorial continuation for EXACT remaining 29 elective topics.

The 313 candidates are project-written page-level goals, not official atomic syllabus.
Finite checks and content schema tests are NOT theorem certificates or teacher approvals.
"""
from __future__ import annotations
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from .kb_batch34_review import Manuscript, known_source, review_only_manuscripts
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"knowledge/editorial_review/kb_batch35_seed.jsonl"
AUTHOR=ROOT/"scripts/author_kb_batch35_lessons.py"
PIN="6ed09a6db38380f6e5ace3bcf9b41819a1141a0e83ff96efb2ab34eed4a3e97a"
class Manuscript35(Manuscript):
    id:str=Field(pattern=r"^math\.hs\.editorial\.batch35\.kb33\.[a-d]\.p0[567]\d\.a\d{3}$")
def expected_candidates() -> set[str]:
    _,cross=known_source()
    return set(cross["unmatched_candidate_ids"])-{d.editorial_candidate_id for d in review_only_manuscripts()}
def validate_seed(text:str, *, check_pin:bool=True)->tuple[Manuscript35,...]:
    if check_pin and hashlib.sha256(text.encode("utf-8")).hexdigest()!=PIN:
        raise ValueError("Batch35 original seed SHA256 mismatch")
    audit,_=known_source()
    goals={r["editorial_id"]:r for r in audit["editorial_goals"]}
    rows=[Manuscript35.model_validate(json.loads(line)) for line in text.splitlines() if line.strip()]
    ids=[r.editorial_candidate_id for r in rows]
    expected=expected_candidates()
    if len(rows)!=29 or len(set(ids))!=29 or set(ids)!=expected:
        raise ValueError("Batch35 must contain exactly 29 remaining original elective candidates")
    if len({r.id for r in rows})!=29:
        raise ValueError("Duplicate manuscript identifier")
    for row in rows:
        source=goals[row.editorial_candidate_id]
        if source["teacher_review"]!="PENDING" or source["official_clause_alignment_verified"] or source["student_publishable"]:
            raise ValueError("Unverified source or forged approval")
        if f".{source['syllabus_track'][-1:].lower()}." not in row.id:
            raise ValueError("Wrong elective track in manuscript ID")
        if row.review.status!="REVIEW_PENDING" or row.student_publishable or row.teacher_solution_visibility!="TEACHER_ONLY":
            raise ValueError("Unsafe manuscript release")
    return tuple(rows)
@lru_cache(maxsize=1)
def review_only_manuscripts35():
    return validate_seed(SOURCE.read_text(encoding="utf-8"))
def student_retrieval_projection():
    return {"teacher_review_only_staged":len(review_only_manuscripts35()),
            "student_documents":[],"student_solutions":[],"publishable":0,
            "status":"NOT_RELEASED"}
def official_denominators():
    return {"COMPULSORY":None,"SELECTIVE_COMPULSORY":None,
            "ELECTIVE_A":None,"ELECTIVE_B":None,"ELECTIVE_C":None,
            "ELECTIVE_D":None,"ELECTIVE_E":None}
