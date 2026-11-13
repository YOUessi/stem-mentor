"""Teacher-only, hash-bound and source-anchored staged repairs; no authority granted."""
from __future__ import annotations
import hashlib, json
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from .kb_batch34_review import Manuscript

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"knowledge/editorial_review/kb_batch37_scope_repairs.jsonl"
BASE=ROOT/"docs/evaluation/KB_BATCH36_47_LEGACY_SCOPE_AUDIT.json"
PIN="7cf991096365c704e859173187c72469c49ede251b865ed01ebef196c31283af"

class ScopeRepair(Manuscript):
    id: str=Field(pattern=r"^math\.hs\.editorial\.batch37\.kb33\.[a-e]\.p0[567][0-9]\.a\d{3}$")

def validate_seed(raw:str, *, check_pin:bool=True)->tuple[ScopeRepair,...]:
    if check_pin and hashlib.sha256(raw.encode("utf8")).hexdigest()!=PIN:
        raise ValueError("Original teacher-only scope repair seed drifted")
    original=json.loads(BASE.read_text(encoding="utf8"))
    mismatch={x["editorial_candidate_id"]:x for x in original["links"] if x["review_finding"]=="CLAIM_MISMATCH"}
    if len(mismatch)!=8:raise ValueError("Historical mismatch baseline drifted")
    docs=tuple(ScopeRepair.model_validate(json.loads(line)) for line in raw.splitlines() if line.strip())
    ids=[d.editorial_candidate_id for d in docs]
    if len(docs)!=8 or len(set(ids))!=8 or set(ids)!=set(mismatch):
        raise ValueError("Must repair exactly 8 original mismatches, without duplicating IDs")
    if len({d.id for d in docs})!=8:raise ValueError("Duplicate staged manuscript ID")
    for doc in docs:
        old=mismatch[doc.editorial_candidate_id]
        if old["official_clause_alignment_verified"] or old["mathematical_equivalence_certified"]:
            raise ValueError("Cannot claim original source was attested")
        if not doc.id.endswith(doc.editorial_candidate_id.lower().replace("-",".")):
            raise ValueError("Teacher-only manuscript target and ID do not match")
        if doc.review.status!="REVIEW_PENDING" or doc.teacher_solution_visibility!="TEACHER_ONLY":
            raise ValueError("Not eligible for student release")
        if doc.proof_verification!="NOT_FORMALLY_CERTIFIED" or doc.student_publishable:
            raise ValueError("Unproven mathematics cannot be published")
        if len(doc.reasoning_steps)<3 or not doc.assumptions or not doc.counterexample.example:
            raise ValueError("Missing detailed mathematical review")
        if any(len(ex.steps)!=2 or len(ex.check)<8 for ex in doc.worked_examples):
            raise ValueError("Incomplete teacher worked example")
    return docs

@lru_cache(maxsize=1)
def staged_repairs()->tuple[ScopeRepair,...]:
    return validate_seed(SOURCE.read_text(encoding="utf8"))

def student_retrieval_projection()->dict:
    """Never insert these drafts (especially full teacher solutions) in student RAG."""
    return dict(staged=len(staged_repairs()),student_documents=[],student_solutions=[],
                authenticated_teacher_approvals=0,student_published=0,
                status="NOT_PUBLISHED",official_curriculum_denominators=None)
