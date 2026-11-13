"""49 bounded REVIEW_PENDING manuscripts, local editorial FTS only; fail closed.

A caller-supplied scope is NOT authentication. Do not mount editor search on
unauthenticated HTTP. Public API must only expose aggregate coverage counts.
"""
from __future__ import annotations
from collections import Counter
from functools import lru_cache
from pathlib import Path
import json
import sqlite3
import sys

from . import kb_batch137_index as previous

ROOT = Path(__file__).resolve().parents[2]
NEW = ROOT / "knowledge/editorial_review/kb_batch138_eight_elective_lessons.json"
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch138_electives as current


class LocalEditorOnlyError(PermissionError):
    pass


@lru_cache(maxsize=1)
def load():
    old = previous.load()
    new = json.loads(NEW.read_text(encoding="utf-8"))
    if new != current.build():
        raise ValueError("New draft source/status/mathematics drift")
    current.validate_rows_structure(new)
    items = old + new
    if len(items) != 49 or len({r["id"] for r in items}) != 49:
        raise ValueError("Incomplete or duplicate 49 manuscripts")
    return items


@lru_cache(maxsize=1)
def index():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.execute('CREATE VIRTUAL TABLE manuscripts USING fts5(body, tokenize="unicode61")')
    for r in load():
        body = " ".join((
            r.get("title", ""), r["formal_definition_or_theorem"],
            r["notation_and_domain"], r["applicability_and_hypotheses"],
            r["typical_wrong_solution"]))
        slug = r["id"].split("-deep-")[-1]
        body = previous.ALIASES.get(slug, "") + " " + body
        # Worked examples, answers, proof steps and teacher solutions are NEVER indexed.
        conn.execute("INSERT INTO manuscripts(body) VALUES (?)",
                     (" ".join(previous.tokenize(body)),))
    conn.commit()
    return conn


def public_coverage():
    records = load()
    return {
        "scope": "49_BOUNDED_TEACHER_DRAFTS_NOT_NATIONAL_SYLLABUS",
        "editorial_review_manuscripts": len(records),
        "by_track": dict(sorted(Counter(r["course_track"] for r in records).items())),
        "official_atom_denominator": None,
        "official_course_coverage_rate": None,
        "teacher_approved": 0,
        "student_authoritative": 0,
        "general_proof_certified": 0,
        "student_free_text_steps_verified": 0,
        "teacher_solution_or_manuscript_included": False,
    }


def editor_preview_search(query: str, *, scope: str = "", track: str | None = None,
                          limit: int = 8):
    if scope != "EDITOR_LOCAL":
        raise LocalEditorOnlyError("Caller-supplied scope is not authentication")
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 160 or previous._CONTROLS.search(query):
        raise ValueError("Invalid editor query")
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("Invalid limit")
    rows = load()
    if track is not None and track not in {r["course_track"] for r in rows}:
        raise ValueError("Invalid track")
    tokens = previous.tokenize(query)
    if not tokens:
        return []
    expression = " OR ".join('"' + token + '"' for token in tokens)
    matches = index().execute(
        "SELECT rowid, bm25(manuscripts) FROM manuscripts WHERE manuscripts MATCH ? "
        "ORDER BY bm25(manuscripts)", (expression,)).fetchall()
    found = []
    for rowid, score in matches:
        item = rows[rowid-1]
        if track is not None and item["course_track"] != track:
            continue
        found.append({
            "id": item["id"],
            "source_candidate_id": item.get("source_candidate_id", item.get("candidate_id")),
            "course_track": item["course_track"],
            "review_status": "REVIEW_PENDING",
            "condition_status": "CONDITIONS_NOT_ESTABLISHED",
            "student_publishable": False,
            "rank": round(float(score), 6),
        })
        if len(found) >= limit:
            break
    return found


def student_evidence_lookup(query: str, *, limit: int = 8):
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 160 or previous._CONTROLS.search(query):
        raise ValueError("Invalid student query")
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("Invalid limit")
    return {
        "status": "NO_APPROVED_EVIDENCE",
        "candidates": [],
        "teacher_solution_exposed": False,
        "unverified_content_exposed": False,
    }
