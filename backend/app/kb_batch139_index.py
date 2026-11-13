"""57 provisional teacher manuscripts: local editorial FTS; student evidence default-deny.

Caller-supplied EDITOR_LOCAL scope is NOT authentication: do not publish
editor_preview_search as an HTTP endpoint; only aggregate count may be public.
"""
from __future__ import annotations
from collections import Counter
from functools import lru_cache
from pathlib import Path
import json
import re
import sqlite3
import sys
from . import kb_batch138_index as previous
ROOT=Path(__file__).resolve().parents[2]
NEW=ROOT/"knowledge/editorial_review/kb_batch139_eight_core_lessons.json"
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch139_core as author

class LocalEditorOnlyError(PermissionError):
    pass

@lru_cache(maxsize=1)
def load():
    old=previous.load()
    new=json.loads(NEW.read_text(encoding="utf-8"))
    if new!=author.build():
        raise ValueError("Batch139 teacher manuscript/verification drift")
    author.validate(new)
    rows=old+new
    if len(rows)!=57 or len({r["id"] for r in rows})!=57:
        raise ValueError("incorrect or duplicate bounded 57 manuscripts")
    return rows

@lru_cache(maxsize=1)
def index():
    db=sqlite3.connect(":memory:",check_same_thread=False)
    db.execute('CREATE VIRTUAL TABLE drafts USING fts5(body,tokenize="unicode61")')
    for r in load():
        # Do NOT index answers, proof steps, teacher example questions, or hints.
        text=" ".join([r.get("title",""),r["formal_definition_or_theorem"],
                       r["notation_and_domain"],r["applicability_and_hypotheses"],
                       r["typical_wrong_solution"]])
        aliases=previous.previous.ALIASES.get(r["id"].split("-deep-")[-1],"")
        db.execute("INSERT INTO drafts(body) VALUES (?)",
                   (" ".join(previous.previous.tokenize(aliases+" "+text)),))
    db.commit()
    return db

def public_coverage():
    rows=load()
    return dict(scope="57_BOUNDED_REVIEW_PENDING_TEACHER_MANUSCRIPTS_NOT_NATIONAL_SYLLABUS",
        editorial_review_manuscripts=len(rows),
        by_track={k:sum(r["course_track"]==k for r in rows) for k in author.TRACKS},
        official_atom_denominators={k:None for k in author.TRACKS},
        official_course_coverage_rate=None,
        teacher_approved=0,student_authoritative=0,
        general_proof_certified=0,student_free_text_steps_verified=0,
        teacher_solution_or_manuscript_included=False)

def editor_preview_search(query: str, *, scope: str="", track: str|None=None, limit: int=8):
    if scope!="EDITOR_LOCAL":
        raise LocalEditorOnlyError("scope string is not a proof of authentication")
    if not isinstance(query,str) or not 1<=len(query.strip())<=160 or previous.previous._CONTROLS.search(query):
        raise ValueError("invalid editorial query")
    if type(limit) is not int or not 1<=limit<=20:
        raise ValueError("invalid limit")
    rows=load()
    if track is not None and track not in author.TRACKS: raise ValueError("invalid track")
    tokens=previous.previous.tokenize(query)
    if not tokens: return []
    expression=" OR ".join('"'+t+'"' for t in tokens)
    matches=index().execute("SELECT rowid,bm25(drafts) FROM drafts WHERE drafts MATCH ? ORDER BY bm25(drafts)",
                           (expression,)).fetchall()
    found=[]
    for rowid,score in matches:
        r=rows[rowid-1]
        if track is not None and r["course_track"]!=track: continue
        found.append(dict(id=r["id"],course_track=r["course_track"],
              source_candidate_id=r.get("source_candidate_id",r.get("candidate_id")),
              review_status="REVIEW_PENDING",condition_status="CONDITIONS_NOT_ESTABLISHED",
              student_publishable=False,rank=round(float(score),6)))
        if len(found)==limit: break
    return found

def student_evidence_lookup(query: str, *,limit:int=8):
    if not isinstance(query,str) or not 1<=len(query.strip())<=160 or previous.previous._CONTROLS.search(query):
        raise ValueError("invalid student query")
    if type(limit) is not int or not 1<=limit<=20:
        raise ValueError("invalid limit")
    return dict(status="NO_APPROVED_EVIDENCE",candidates=[],
                teacher_solution_exposed=False,unverified_content_exposed=False)
