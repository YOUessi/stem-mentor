"""65 unapproved math editor manuscripts; versioned local-only FTS, public default-deny.

EDITOR_LOCAL is NOT a credential. Never attach editor_preview_search to HTTP.
"""
from __future__ import annotations
from functools import lru_cache
import json
from pathlib import Path
import re
import sqlite3
import sys
from . import kb_batch139_index as previous
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch143_lessons as authored
NEW=authored.OUT
CONTROLS=re.compile(r"[\x00-\x1f\x7f]")
LocalEditorOnlyError=previous.LocalEditorOnlyError

@lru_cache(maxsize=1)
def load():
    past=previous.load()
    added=json.loads(NEW.read_text(encoding="utf-8"))
    if added!=authored.build():raise ValueError("Batch143 unreviewed teaching manuscript drift")
    authored.validate(added)
    rows=past+added
    if len(rows)!=65 or len({x["id"] for x in rows})!=65:
        raise ValueError("65 unique editor-only manuscripts required")
    audit=authored.audit(added)
    if audit!=json.loads(authored.AUDIT.read_text(encoding="utf-8")):
        raise ValueError("7-track aggregate counts do not reconcile")
    return rows

@lru_cache(maxsize=1)
def _db():
    conn=sqlite3.connect(":memory:",check_same_thread=False)
    conn.execute('CREATE VIRTUAL TABLE drafts USING fts5(body,tokenize="unicode61")')
    tokenize=previous.previous.previous.tokenize
    for row in load():
        # This is a *private* ephemeral editor index. No worked answers/solutions/hints.
        title=row.get("title","")
        safe_text=" ".join([title,row["formal_definition_or_theorem"],
             row["notation_and_domain"],row["applicability_and_hypotheses"]])
        conn.execute("INSERT INTO drafts(body) VALUES (?)",(" ".join(tokenize(safe_text)),))
    conn.commit()
    return conn

def public_coverage():
    rows=load()
    return dict(scope="65_PROVISIONAL_EDITOR_DRAFTS_NOT_OFFICIAL_CURRICULUM",
                editorial_review_manuscripts=65,
                by_track={t:sum(x["course_track"]==t for x in rows) for t in authored.TRACKS},
                official_atom_denominators={t:None for t in authored.TRACKS},
                official_course_coverage_rate=None,teacher_approved=0,
                student_authoritative=0,teacher_solution_or_manuscript_included=False,
                general_proof_certified=0,student_free_text_steps_verified=0)

def _validate(query,limit):
    if not isinstance(query,str) or not 1<=len(query.strip())<=160 or CONTROLS.search(query):
        raise ValueError("invalid query")
    if type(limit) is not int or not 1<=limit<=20:
        raise ValueError("invalid limit")

def editor_preview_search(query: str, *, scope: str="", track: str|None=None, limit: int=8):
    if scope!="EDITOR_LOCAL":
        raise LocalEditorOnlyError("string-supplied scope is not authentication")
    _validate(query,limit)
    if track is not None and track not in authored.TRACKS:
        raise ValueError("invalid track")
    toks=previous.previous.previous.tokenize(query)
    if not toks:return []
    expr=" OR ".join('"'+t+'"' for t in toks)
    matches=_db().execute(
        "SELECT rowid,bm25(drafts) FROM drafts WHERE drafts MATCH ? ORDER BY bm25(drafts)",(expr,)).fetchall()
    rows=load()
    out=[]
    for rowid,score in matches:
        r=rows[rowid-1]
        if track is not None and r["course_track"]!=track:continue
        out.append(dict(id=r["id"],course_track=r["course_track"],
            source_candidate_id=r.get("source_candidate_id",r.get("candidate_id")),
            review_status="REVIEW_PENDING",condition_status="CONDITIONS_NOT_ESTABLISHED",
            student_publishable=False,rank=round(float(score),6)))
        if len(out)==limit:break
    return out

def student_evidence_lookup(query: str, *,limit:int=8):
    _validate(query,limit)
    return dict(status="NO_APPROVED_EVIDENCE",candidates=[],
                teacher_solution_exposed=False,unverified_content_exposed=False)
