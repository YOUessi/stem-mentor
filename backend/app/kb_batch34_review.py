"""Batch34 ORIGINAL editorial manuscripts: teacher-review staging, never student RAG.

No official atomic denominator, verified whole proofs, or teacher approval is inferred.
Data is anchored only to Batch33 page-level editorial goals, not to individual
official syllabus clauses. This module exposes no student full-answer endpoint.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "knowledge/editorial_review/kb_batch34_seed.jsonl"
PIN = "de5d3c5f1f3635682398beb44a33aab590c92b944449bba3aa50c4450952cd8e"
EDITORIAL = ROOT / "docs/evaluation/KB_BATCH33_ELECTIVE_SCOPE_AUDIT.json"
CROSSWALK = ROOT / "docs/evaluation/KB_BATCH33_DRAFT_CROSSWALK_AUDIT.json"

class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class Step(Strict):
    claim: str = Field(min_length=8)
    reason: str = Field(min_length=8)

class Counterexample(Strict):
    false_claim: str = Field(min_length=6)
    example: str = Field(min_length=12)
    explanation: str = Field(min_length=8)

class WorkedExample(Strict):
    question: str = Field(min_length=6)
    steps: list[str] = Field(min_length=2, max_length=5)
    answer: str = Field(min_length=1)
    check: str = Field(min_length=6)

class Misconception(Strict):
    error: str = Field(min_length=6)
    why_wrong: str = Field(min_length=8)
    repair_question: str = Field(min_length=6)

class Transfer(Strict):
    near: str = Field(min_length=12)
    far: str = Field(min_length=12)

class Review(Strict):
    status: Literal["REVIEW_PENDING"]
    reviewer_id: None = None
    reviewed_at: None = None
    review_record: None = None

class Manuscript(Strict):
    editorial_candidate_id: str = Field(pattern=r"^KB33-[ABCDE]-P0[567][0-9]-A\d{3}$")
    id: str = Field(pattern=r"^math\.hs\.editorial\.batch34\.[a-z0-9.]+$")
    kind: Literal["concept","theorem","method"]
    title: str = Field(min_length=7)
    claim: str = Field(min_length=25)
    notation: list[str] = Field(min_length=1)
    assumptions: list[str] = Field(min_length=1)
    reasoning_steps: list[Step] = Field(min_length=3)
    counterexample: Counterexample
    worked_examples: list[WorkedExample] = Field(min_length=2, max_length=2)
    boundaries: list[str] = Field(min_length=1)
    misconception: Misconception
    hint_ladder: list[str] = Field(min_length=3, max_length=3)
    transfer: Transfer
    review: Review
    teacher_solution_visibility: Literal["TEACHER_ONLY"]
    source_license: Literal["PROJECT_AUTHORED"]
    proof_verification: Literal["NOT_FORMALLY_CERTIFIED"]
    student_publishable: Literal[False]

    @model_validator(mode="after")
    def validate_rich_review_content(self):
        if len(set(self.hint_ladder)) != 3:
            raise ValueError("Repeated hints are not a graduated hint ladder")
        if len({x.question for x in self.worked_examples}) != 2:
            raise ValueError("Each draft needs two distinct controlled examples")
        if any(len(x.steps) != 2 for x in self.worked_examples):
            raise ValueError("Explicit two-stage reasoning required for each example")
        if any(len(x.claim) < 8 or len(x.reason) < 8 for x in self.reasoning_steps):
            raise ValueError("Reasoned and auditable step claims needed")
        if self.counterexample.false_claim != self.misconception.error:
            raise ValueError("Wrong-method misconception must link to actual counterexample")
        if self.counterexample.explanation != self.misconception.why_wrong:
            raise ValueError("Error explanation and worked counterexample drift")
        return self

def known_source():
    audit = json.loads(EDITORIAL.read_text(encoding="utf-8"))
    crosswalk = json.loads(CROSSWALK.read_text(encoding="utf-8"))
    if audit["summary"]["all_provisional_editorial_candidates"] != 313:
        raise ValueError("Previous page-level scope baseline changed")
    if crosswalk["summary"]["no_suggested_related_draft"] != 49:
        raise ValueError("Previous 49 editorial unmatched candidates baseline changed")
    return audit, crosswalk

def validate_seed(text: str, *, check_pin: bool = True) -> list[Manuscript]:
    if check_pin and hashlib.sha256(text.encode("utf-8")).hexdigest() != PIN:
        raise ValueError("Original manually authored seed SHA256 changed")
    audit, crosswalk = known_source()
    candidates = {r["editorial_id"]:r for r in audit["editorial_goals"]}
    unmatched = set(crosswalk["unmatched_candidate_ids"])
    rows=[]
    ids=set()
    for raw in text.splitlines():
        if not raw.strip():
            continue
        doc=Manuscript.model_validate(json.loads(raw))
        if doc.editorial_candidate_id not in unmatched:
            raise ValueError("Only previously unassociated editorial candidates may be newly staged")
        if doc.editorial_candidate_id in ids:
            raise ValueError("Duplicate editorial candidate")
        source=candidates[doc.editorial_candidate_id]
        if source["teacher_review"]!="PENDING" or source["official_clause_alignment_verified"]:
            raise ValueError("Invalid or falsely approved source reference")
        if source["student_publishable"] or doc.student_publishable:
            raise ValueError("No unauthorized publication")
        ids.add(doc.editorial_candidate_id)
        rows.append(doc)
    if len(rows) != 20 or len(ids) != 20:
        raise ValueError("The curated batch requires 20 distinct original manuscripts")
    if len({x.id for x in rows}) != 20:
        raise ValueError("Duplicate review manuscript ID")
    return rows

@lru_cache(maxsize=1)
def review_only_manuscripts() -> tuple[Manuscript,...]:
    return tuple(validate_seed(SOURCE.read_text(encoding="utf-8")))

def student_retrieval_projection() -> dict:
    # No full-answer or even preview payload leaves this isolated review corpus.
    return {"staged_count": len(review_only_manuscripts()),"publishable_count":0,
            "student_documents":[],"student_solutions":[],"status":"NOT_RELEASED"}

def curriculum_denominator() -> None:
    # Page-level source candidate count != officially verified atomic syllabus count.
    return None
