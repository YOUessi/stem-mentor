"""115 editor-only deep manuscripts in volatile FTS5. Never offer unapproved student evidence."""
from __future__ import annotations
import json,sqlite3,sys
from functools import lru_cache
from pathlib import Path
from . import kb_batch149_index as previous
from .kb_batch137_index import tokenize
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch151_lessons as new
import build_kb_batch151_crosswalk as crosswalk
LocalEditorOnlyError=previous.LocalEditorOnlyError

@lru_cache(maxsize=1)
def load():
    past=previous.load()
    more=json.loads(new.OUT.read_text(encoding="utf-8"))
    if more!=new.build():raise ValueError("KB151 draft content source drift")
    new.validate(more)
    rows=past+more
    if len(rows)!=115 or len({v["id"] for v in rows})!=115:
        raise ValueError("KB151 requires 115 unique unpublished manuscripts")
    audit=json.loads(new.AUDIT.read_text(encoding="utf-8"))
    if new.audit(more)!=audit:raise ValueError("KB151 unapproved seven-track tally drift")
    return rows

@lru_cache(maxsize=1)
def _db():
    db=sqlite3.connect(":memory:",check_same_thread=False)
    db.execute('CREATE VIRTUAL TABLE draft_index USING fts5(body,tokenize="unicode61")')
    for r in load():
        # Neither answer nor full teacher solution enters the index at any point.
        brief=" ".join([r.get("title",""),r["formal_definition_or_theorem"],
                        r["notation_and_domain"],r["applicability_and_hypotheses"]])
        db.execute("INSERT INTO draft_index(body) VALUES (?)",(" ".join(tokenize(brief)),))
    db.commit()
    return db

def editor_preview_search(query,*,scope="",track=None,limit=8):
    if scope!="EDITOR_LOCAL":
        raise LocalEditorOnlyError("editor preview scope is internal only, never routed")
    previous.previous.validate_query(query,limit)
    if track is not None and track not in new.TRACKS:raise ValueError("unknown course track")
    ts=tokenize(query)
    if not ts:return []
    expr=" OR ".join('"'+t+'"' for t in ts)
    hits=_db().execute("SELECT rowid,bm25(draft_index) FROM draft_index WHERE draft_index MATCH ? ORDER BY bm25(draft_index)",
                       (expr,)).fetchall()
    out=[];rows=load()
    for rowid,rank in hits:
        r=rows[rowid-1]
        if track is not None and r["course_track"]!=track:continue
        out.append(dict(id=r["id"],course_track=r["course_track"],
            source_candidate_id=r.get("source_candidate_id",r.get("candidate_id")),
            review_status="REVIEW_PENDING",condition_status="CONDITIONS_NOT_ESTABLISHED",
            student_publishable=False,rank=round(float(rank),6)))
        if len(out)>=limit:break
    return out

def student_evidence_lookup(query,*,limit=8):
    previous.previous.validate_query(query,limit)
    return dict(status="NO_APPROVED_EVIDENCE",candidates=[],
                teacher_solution_exposed=False,unverified_content_exposed=False)

def public_coverage():
    rows=load()
    gaps=crosswalk.build()
    assert crosswalk.validate(gaps)
    return dict(scope="115_EDITOR_ONLY_PENDING_DRAFTS_NOT_OFFICIAL_SYLLABUS",
        editorial_review_manuscripts=115,
        by_track={t:sum(r["course_track"]==t for r in rows) for t in new.TRACKS},
        editorial_source_candidates=239,editorial_candidates_linked=gaps["matched_editorial_candidates"],
        editorial_candidates_unlinked=gaps["missing_editorial_candidates"],
        source_elective_de_page_review_queue=5,
        official_atom_denominators={t:None for t in new.TRACKS},
        official_course_coverage_rate=None,teacher_approved=0,student_authoritative=0,
        general_proof_certified=0,student_free_text_steps_verified=0,
        teacher_solution_or_manuscript_included=False)
