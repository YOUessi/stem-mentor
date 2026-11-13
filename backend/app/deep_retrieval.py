"""Offline-only evidence retrieval over unapproved teaching drafts.

No HTTP routes or LLM calls. This is a *curation* search surface: results cannot
establish theorem applicability, proof validity, student correctness, or review.
Only audited content may ever leave editor-only tooling into student teaching.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from .deep_knowledge import lessons
from .attested_releases import approved_lesson_ids

_UNSAFE = re.compile(r"[\u0000-\u001f]")
_WORDS = re.compile(r"[\u3400-\u9fff]+|[a-z0-9_]+")
_MAX_WORDS = 40
_MAX_LIMIT = 20


class EditorOnlyError(PermissionError):
    pass


@dataclass(frozen=True)
class EvidenceHit:
    knowledge_id: str
    title: str
    kind: str
    curriculum_ids: tuple[str, ...]
    review_status: str
    score: float
    condition_status: Literal["CONDITIONS_NOT_ESTABLISHED"] = "CONDITIONS_NOT_ESTABLISHED"


def _tokens(query: str, *, max_tokens: int = _MAX_WORDS) -> list[str]:
    normalized = query.lower().replace("−", "-").replace("²", "2")
    output: list[str] = []
    for match in _WORDS.findall(normalized):
        if re.fullmatch(r"[\u3400-\u9fff]+", match):
            output.extend(match[i:i + 2] for i in range(len(match) - 1))
            if len(match) == 1:
                output.append(match)
        elif len(match) <= 35:
            output.append(match)
    return list(dict.fromkeys(output))[:max_tokens]


def _document_tokens(doc) -> tuple[str, str]:
    title_terms = _tokens(doc.title)
    body = " ".join(
        [doc.title, doc.statement or "", doc.definition or "", *doc.assumptions,
         *doc.boundaries, *doc.notation, *doc.prerequisites,
         *(x.claim + " " + x.reason for x in doc.proof_steps),
         *doc.rationale_steps,
         *(x.error + " " + x.why_wrong for x in doc.misconceptions)]
    )
    return " ".join(title_terms), " ".join(_tokens(body, max_tokens=512))


@lru_cache(maxsize=1)
def _index():
    """An in-memory FTS5 index without leaking any worked example into APIs."""
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.execute('CREATE VIRTUAL TABLE evidence USING fts5(title, body, tokenize="unicode61")')
    all_docs = lessons()
    for doc in all_docs:
        db.execute("INSERT INTO evidence(title,body) VALUES(?,?)", _document_tokens(doc))
    db.commit()
    return db


def _validate_query(query: str, limit: int):
    if not isinstance(query, str) or not (1 <= len(query.strip()) <= 160):
        raise ValueError("Search query must be 1–160 chars")
    if _UNSAFE.search(query):
        raise ValueError("Control characters not accepted")
    if not isinstance(limit, int) or isinstance(limit, bool) or not (1 <= limit <= _MAX_LIMIT):
        raise ValueError("limit out of supported range")


def _search_metadata(query: str, *, curriculum_ids: tuple[str, ...] | None = None,
                     kind: str | None = None, limit: int = 8,
                     allowed_ids: frozenset[str] | None = None):
    _validate_query(query, limit)
    if kind not in (None, "concept", "method", "theorem"):
        raise ValueError("Unknown mathematical knowledge kind")
    known_ids = {v for d in lessons() for v in d.curriculum_ids}
    if curriculum_ids is not None:
        if not curriculum_ids or set(curriculum_ids) - known_ids:
            raise ValueError("Unknown or empty curriculum filters")
    terms = _tokens(query)
    if not terms:
        return []
    # The only FTS query syntax is constructed from internally generated tokens.
    expression = " OR ".join('"' + term + '"' for term in terms)
    db = _index()
    # Filter on curriculum/kind AFTER retrieval, so a global top-100 cut
    # would silently drop a valid lower-ranked matching lesson. The current
    # curated corpus is small and local; keep every FTS hit before filtering.
    candidates = db.execute(
        "SELECT rowid, bm25(evidence, 4.0, 1.0) AS rank "
        "FROM evidence WHERE evidence MATCH ? ORDER BY rank",
        (expression,),
    ).fetchall()
    found: list[EvidenceHit] = []
    all_docs = lessons()
    for row_id, rank in candidates:
        doc = all_docs[row_id - 1]
        if allowed_ids is not None and doc.id not in allowed_ids:
            continue
        if curriculum_ids and not (set(curriculum_ids) & set(doc.curriculum_ids)):
            continue
        if kind and doc.kind != kind:
            continue
        found.append(EvidenceHit(
            knowledge_id=doc.id,
            title=doc.title,
            kind=doc.kind,
            curriculum_ids=tuple(doc.curriculum_ids),
            review_status=doc.review.status,
            score=round(-float(rank), 5),
        ))
        if len(found) == limit:
            break
    return found


def editor_draft_search(query: str, *, scope: str = "", curriculum_ids: tuple[str, ...] | None = None,
                        kind: str | None = None, limit: int = 8):
    """Explicit local editor use only; DO NOT register this method as an API route.

    'scope' is just an accidental misuse guard, not an authentication system.
    All output remains unreviewed and not mathematically certified.
    """
    if scope != "EDITOR_LOCAL":
        raise EditorOnlyError("Draft lesson access restricted to local editor tools")
    return [hit.__dict__ for hit in _search_metadata(
        query, curriculum_ids=curriculum_ids, kind=kind, limit=limit)]


def editor_draft_full(knowledge_id: str, *, scope: str = ""):
    """Full text for local editors only. Full solutions must not reach student LLM prompts."""
    if scope != "EDITOR_LOCAL":
        raise EditorOnlyError("Full lesson content restricted to local editor tools")
    doc = next((d for d in lessons() if d.id == knowledge_id), None)
    if doc is None:
        raise KeyError("Unknown draft ID")
    # Separate editorial hypotheses from the authoritative lesson graph.
    # These IDs are not evidence and never reach student_evidence_lookup.
    from .kb_batch26_graph import editor_prerequisite_proposals
    return {
        "content": doc.model_dump(mode="json"),
        "review_status": doc.review.status,
        "condition_status": "CONDITIONS_NOT_ESTABLISHED",
        "prerequisite_editorial_candidates": editor_prerequisite_proposals(doc.id, scope=scope),
        "note": "Unreviewed authored draft; not proof-checked or safe for student answers.",
    }


def student_evidence_lookup(query: str, *, limit: int = 8):
    """Only return minimum hint metadata for independently attested lessons.

    Returning a hint is not a proof check or automatic applicability judgment.
    No full worked examples, proof steps, theorem statements or teacher plans
    enter student payloads or external LLM prompts.
    """
    _validate_query(query, limit)
    approved = approved_lesson_ids()
    if not approved:
        return {
            "status": "NO_APPROVED_EVIDENCE",
            "candidates": [],
            "teacher_solution_exposed": False,
            "unverified_content_exposed": False,
            "note": "No externally doubly attested lesson versions are available.",
        }
    docs = {doc.id: doc for doc in lessons()}
    hits = _search_metadata(query, limit=limit, allowed_ids=approved)
    safe = []
    for hit in hits:
        if hit.knowledge_id not in approved:
            continue
        doc = docs[hit.knowledge_id]
        safe.append({
            "knowledge_id": doc.id,
            "curriculum_ids": list(doc.curriculum_ids),
            "title": doc.title,
            "version": doc.version,
            "hint": doc.hint_ladder[0],
            "condition_status": "CONDITIONS_NOT_ESTABLISHED",
            "approval_evidence": "TWO_EXTERNAL_SIGNATURES",
        })
        if len(safe) >= limit:
            break
    return {
        "status": "APPROVED_HINTS_ONLY" if safe else "NO_MATCHING_APPROVED_EVIDENCE",
        "candidates": safe,
        "teacher_solution_exposed": False,
        "unverified_content_exposed": False,
        "note": "Signed human review is a publication gate, not mathematical applicability proof.",
    }
