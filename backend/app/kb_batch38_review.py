"""Batch38 original teacher manuscripts, never approved or student retrievable."""
from __future__ import annotations
from pathlib import Path
import hashlib,json
from functools import lru_cache
from pydantic import Field
from .kb_batch34_review import Manuscript

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"knowledge/editorial_review/kb_batch38_partial.jsonl"
BASE=ROOT/"docs/evaluation/KB_BATCH36_47_LEGACY_SCOPE_AUDIT.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH38_PARTIAL_SCOPE_AUDIT.json"
PIN="d28e04b16511017119c3560568d9d22f46af6f8eebc57185ee8bf7773f7e2be1"

class PartialRepair(Manuscript):
    id:str=Field(pattern=r"^math\.hs\.editorial\.batch38\.kb33\.[a-e]\.p0[567]\d\.a\d{3}$")

def validate_seed(raw:str,*,check_pin:bool=True):
    if check_pin and hashlib.sha256(raw.encode()).hexdigest()!=PIN:
        raise ValueError("Teacher manuscript seed SHA drift")
    previous=json.loads(BASE.read_text(encoding="utf8"))
    partial={x["editorial_candidate_id"]:x for x in previous["links"] if x["review_finding"]=="PARTIAL_SCOPE"}
    docs=[PartialRepair.model_validate(json.loads(line)) for line in raw.splitlines() if line.strip()]
    ids={d.editorial_candidate_id for d in docs}
    if len(partial)!=27 or len(docs)!=20 or len(ids)!=20 or not ids.issubset(partial):
        raise ValueError("Expected 20 unique original PARTIAL_SCOPE target IDs")
    if len({d.id for d in docs})!=20:
        raise ValueError("Duplicate staged manuscript ID")
    for d in docs:
        if d.id!="math.hs.editorial.batch38."+d.editorial_candidate_id.lower().replace("-","."):
            raise ValueError("Manuscript ID cannot detach from editorial target")
        if d.review.status!="REVIEW_PENDING" or d.student_publishable or d.teacher_solution_visibility!="TEACHER_ONLY":
            raise ValueError("Unapproved student disclosure")
        if d.proof_verification!="NOT_FORMALLY_CERTIFIED" or not d.assumptions or len(d.reasoning_steps)!=3:
            raise ValueError("Invalid proof boundary")
        if any(len(ex.steps)!=2 for ex in d.worked_examples):
            raise ValueError("Missing two-stage worked example")
        if partial[d.editorial_candidate_id]["official_clause_alignment_verified"] or partial[d.editorial_candidate_id]["mathematical_equivalence_certified"]:
            raise ValueError("Prior source claims are unexpectedly certified")
    return tuple(docs)

@lru_cache(maxsize=1)
def staged():return validate_seed(SOURCE.read_text(encoding="utf8"))

def student_retrieval_projection():
    return {"status":"UNPUBLISHED_REVIEW_ONLY","review_drafts":len(staged()),
            "student_documents":[],"teacher_solutions_exposed":[],
            "approved":0,"student_published":0,"official_denominators":None}
