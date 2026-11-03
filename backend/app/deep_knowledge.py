"""Structured, project-authored draft math knowledge. No student-solution exposure.

This module is a content validation and coverage component, NOT a proof checker,
teacher review system, or generic model-based mathematical tutor.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parents[2]
COURSE_MAP = ROOT / "curriculum/highschool_math/curriculum_map.json"
DEEP_DIR = ROOT / "knowledge/deep/v1"
VALID_LEVELS = ("必修", "选择性必修", "选修拓展")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ProofStep(StrictModel):
    claim: str = Field(min_length=12)
    reason: str = Field(min_length=12)


class NegativeExample(StrictModel):
    false_claim: str = Field(min_length=12)
    example: str = Field(min_length=12)
    explanation: str = Field(min_length=12)


class WorkedExample(StrictModel):
    question: str = Field(min_length=10)
    steps: list[str] = Field(min_length=2)
    answer: str = Field(min_length=1)
    check: str = Field(min_length=10)


class Misconception(StrictModel):
    error: str = Field(min_length=10)
    why_wrong: str = Field(min_length=12)
    repair_question: str = Field(min_length=10)


class Transfer(StrictModel):
    near: str = Field(min_length=12)
    far: str = Field(min_length=12)


class Provenance(StrictModel):
    kind: Literal["PROJECT_AUTHORED"]
    permission: Literal["PROJECT_AUTHORED"]
    curriculum_standard: str = Field(min_length=10)
    standard_url: str = Field(pattern=r"^https://")
    author_role: Literal["PROJECT_AUTHOR"]


class Review(StrictModel):
    status: Literal["DRAFT", "REVIEW_PENDING", "APPROVED", "REJECTED"]
    reviewer_id: str | None = None
    reviewed_at: str | None = None
    review_record: str | None = None

    @model_validator(mode="after")
    def enforce_review_evidence(self):
        provided = (self.reviewer_id, self.reviewed_at, self.review_record)
        if self.status == "APPROVED":
            if not all(provided):
                raise ValueError("APPROVED requires real reviewer, date and evidence")
            # Never trust author-editable JSON as evidence of independent human review.
            # Add an authenticated, signed teacher-review registry in a later batch.
            raise ValueError("APPROVED disabled until independently authenticated teacher review is integrated")
        if any(provided):
            raise ValueError("draft/rejected content cannot invent review evidence")
        return self


class DeepLesson(StrictModel):
    id: str = Field(pattern=r"^math\.hs\.[a-z0-9._-]+$")
    curriculum_ids: list[str] = Field(min_length=1)
    kind: Literal["concept", "theorem", "method"]
    title: str = Field(min_length=4)
    version: str = Field(pattern=r"^[1-9]\d*\.\d+\.\d+$")
    notation: list[str] = Field(min_length=1)
    prerequisites: list[str] = Field(min_length=1)
    prerequisite_lesson_ids: list[str] = Field(default_factory=list)
    definition: str | None = None
    statement: str | None = None
    assumptions: list[str] = Field(min_length=1)
    proof_steps: list[ProofStep] = Field(default_factory=list)
    rationale_steps: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(min_length=1)
    counterexamples: list[NegativeExample] = Field(min_length=1)
    worked_examples: list[WorkedExample] = Field(min_length=2)
    misconceptions: list[Misconception] = Field(min_length=1)
    hint_ladder: list[str] = Field(min_length=3)
    transfer: Transfer
    provenance: Provenance
    review: Review
    teacher_solution_visibility: Literal["TEACHER_ONLY"]

    @model_validator(mode="after")
    def validate_pedagogical_kind(self):
        if self.kind == "theorem":
            if not self.statement or len(self.statement) < 24:
                raise ValueError("theorem needs an explicit full statement")
            if len(self.proof_steps) < 3:
                raise ValueError("theorem needs >=3 proof steps with reasons")
        elif self.kind == "concept":
            if not self.definition or len(self.definition) < 24:
                raise ValueError("concept needs a real mathematical definition")
            if len(self.rationale_steps) < 2:
                raise ValueError("concept needs >=2 explanations/derivations")
        elif self.kind == "method":
            if not self.statement or len(self.statement) < 24:
                raise ValueError("method needs a precise usable statement")
            if len(self.rationale_steps) < 3:
                raise ValueError("method requires rationale and validity checks")
        if len(set(self.curriculum_ids)) != len(self.curriculum_ids):
            raise ValueError("duplicate curriculum ID in one lesson")
        if len(self.hint_ladder) > 6:
            raise ValueError("hint leakage risk: too many progressive steps")
        return self


@lru_cache(maxsize=1)
def curriculum():
    items = json.loads(COURSE_MAP.read_text(encoding="utf-8"))["coverage"]
    ids = [x["id"] for x in items]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate curriculum mapping IDs")
    if any(x["level"] not in VALID_LEVELS for x in items):
        raise ValueError("unknown curriculum track")
    return tuple(items)


@lru_cache(maxsize=1)
def lessons():
    known = {c["id"] for c in curriculum()}
    seen: set[str] = set()
    content = []
    for path in sorted(DEEP_DIR.glob("*.json")):
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, list):
            raise ValueError(f"{path}: expected list of deep lessons")
        for payload in loaded:
            item = DeepLesson.model_validate(payload)
            if item.id in seen:
                raise ValueError(f"duplicate deep knowledge ID {item.id}")
            seen.add(item.id)
            unknown = set(item.curriculum_ids) - known
            if unknown:
                raise ValueError(f"{item.id}: unknown curriculum ID {sorted(unknown)}")
            content.append(item)
    lookup = {x.id: x for x in content}
    for item in content:
        deps = item.prerequisite_lesson_ids
        if len(deps) != len(set(deps)):
            raise ValueError(f"{item.id}: duplicated prerequisites")
        if item.id in deps:
            raise ValueError(f"{item.id}: self prerequisite")
        if any(v not in lookup for v in deps):
            raise ValueError(f"{item.id}: orphan prerequisite")
    visited, visiting = set(), set()
    def walk(key):
        if key in visiting:
            raise ValueError(f"cyclic prerequisite graph at {key}")
        if key in visited:
            return
        visiting.add(key)
        for dep in lookup[key].prerequisite_lesson_ids:
            walk(dep)
        visiting.remove(key)
        visited.add(key)
    for key in lookup:
        walk(key)
    return tuple(content)


def coverage_report():
    entries = curriculum()
    docs = lessons()
    indexed = defaultdict(list)
    by_level = defaultdict(list)
    for doc in docs:
        for key in doc.curriculum_ids:
            indexed[key].append(doc)
    for row in entries:
        by_level[row["level"]].append(row)
    levels = {}
    for level in VALID_LEVELS:
        topic_ids = [row["id"] for row in by_level[level]]
        drafted = [key for key in topic_ids if key in indexed]
        approved = [key for key in topic_ids if any(
            v.review.status == "APPROVED" for v in indexed.get(key, ()))]
        levels[level] = {
            "engineering_topics": len(topic_ids),
            "with_deep_draft": len(drafted),
            "without_deep_draft": len(topic_ids) - len(drafted),
            "teacher_approved": len(approved),
            "missing_topic_ids": [key for key in topic_ids if key not in indexed]
        }
    return {
        "scope": "PROJECT_ENGINEERING_MAP_NOT_OFFICIAL_ATOMIC_SYLLABUS",
        "curriculum_topic_total": len(entries),
        "deep_lesson_documents": len(docs),
        "mapped_curriculum_ids": len(indexed),
        "review_statuses": dict(Counter(x.review.status for x in docs)),
        "kinds": dict(Counter(x.kind for x in docs)),
        "by_level": levels,
        "human_teacher_review_complete": False,
        "student_math_proofs_verified": False,
        "direct_student_teaching_enabled": False,
        "notes": [
            "Existing topic IDs are project granularity and must be audited against the official curriculum.",
            "Schema validation cannot prove mathematical truth; a draft is never a teacher-reviewed fact.",
            "Draft worked examples and proof steps remain TEACHER_ONLY until genuine review."
        ]
    }


def public_summary():
    """Safe to publish on an unauthenticated diagnostics endpoint: counts only."""
    r = coverage_report()
    return {
        "scope": r["scope"], "curriculum_topic_total": r["curriculum_topic_total"],
        "deep_lesson_documents": r["deep_lesson_documents"],
        "mapped_curriculum_ids": r["mapped_curriculum_ids"],
        "by_level": {
            level: {
                key: row[key] for key in (
                    "engineering_topics", "with_deep_draft",
                    "without_deep_draft", "teacher_approved"
                )
            }
            for level, row in r["by_level"].items()
        },
        "review_statuses": r["review_statuses"],
        "human_teacher_review_complete": False,
        "direct_student_teaching_enabled": False,
    }


def unpublished_teacher_preview(query: str):
    """LOCAL TEST/EDITOR TOOL ONLY. Never register as a web API without auth."""
    words = [w.lower() for w in re.findall(r"[\u3400-\u9fff]{2,}|[A-Za-z0-9_.]+", query)]
    if not words or len(query) > 160:
        return []
    return [
        doc.model_dump(mode="json") for doc in lessons()
        if any(w in (doc.title + " " + doc.statement.__str__() + " " + (doc.definition or "")).lower()
               for w in words)
    ][:8]
