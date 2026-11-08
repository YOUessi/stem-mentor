"""Seven remaining PARTIAL_SCOPE teacher-review manuscripts, strictly excluded from student knowledge."""
from __future__ import annotations
import hashlib, json
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from .kb_batch34_review import Manuscript
from .kb_batch38_review import staged as batch38_staged

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/"knowledge/editorial_review/kb_batch39_remaining.jsonl"
PRIOR = ROOT/"docs/evaluation/KB_BATCH38_PARTIAL_SCOPE_AUDIT.json"
HISTORICAL = ROOT/"docs/evaluation/KB_BATCH36_47_LEGACY_SCOPE_AUDIT.json"
AUDIT = ROOT/"docs/evaluation/KB_BATCH39_SEVEN_REPAIR_AUDIT.json"
PIN = "5a6073a9d4c13b370a344a290102bde0b7eef4c1abf5b53d24ecfdd1b864f78b"

class RemainingPartial(Manuscript):
    id: str = Field(pattern=r"^math\.hs\.editorial\.batch39\.kb33\.[c-d]\.p0[567]\d\.a\d{3}$")

def validate_seed(raw:str,*,check_pin:bool=True):
    if check_pin and hashlib.sha256(raw.encode()).hexdigest()!=PIN:
        raise ValueError("Batch39 original teacher manuscript SHA drift")
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    historical = json.loads(HISTORICAL.read_text(encoding="utf-8"))
    historical_partial = {r["editorial_candidate_id"]:r for r in historical["links"] if r["review_finding"]=="PARTIAL_SCOPE"}
    must = set(prior["partial_ids_remaining"])
    docs = tuple(RemainingPartial.model_validate(json.loads(s)) for s in raw.splitlines() if s.strip())
    ids = {d.editorial_candidate_id for d in docs}
    if len(must)!=7 or len(historical_partial)!=27 or len(docs)!=7 or len(ids)!=7 or ids!=must:
        raise ValueError("Batch39 must cover exactly 7 historically unresolved PARTIAL_SCOPE records")
    if len({d.id for d in docs})!=7:
        raise ValueError("Duplicate manuscript IDs")
    if ids & {d.editorial_candidate_id for d in batch38_staged()}:
        raise ValueError("Batch38/39 manuscript duplication")
    for d in docs:
        h = historical_partial[d.editorial_candidate_id]
        if d.id != "math.hs.editorial.batch39."+d.editorial_candidate_id.lower().replace("-","."):
            raise ValueError("Manuscript ID detached from source")
        if h["official_clause_alignment_verified"] or h["mathematical_equivalence_certified"]:
            raise ValueError("Historical association unexpectedly certified")
        if d.review.status!="REVIEW_PENDING" or d.review.reviewer_id is not None or d.student_publishable:
            raise ValueError("Reviewer forgery or illegal student publication")
        if d.teacher_solution_visibility!="TEACHER_ONLY" or d.proof_verification!="NOT_FORMALLY_CERTIFIED":
            raise ValueError("A finite example cannot certify a general theorem")
        if len(d.reasoning_steps)!=3 or len(d.worked_examples)!=2 or len(set(d.hint_ladder))!=3:
            raise ValueError("Incomplete reasoning/examples/hints")
    return docs

@lru_cache(maxsize=1)
def staged():
    return validate_seed(SOURCE.read_text(encoding="utf-8"))

def student_retrieval_projection():
    return {"review_drafts":len(staged()),"approved":0,"student_published":0,
            "student_documents":[],"teacher_solutions_exposed":[],
            "official_denominators":None,"status":"UNPUBLISHED_REVIEW_ONLY"}
