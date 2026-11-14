"""85 unpublished manuscripts in ephemeral editor-only FTS5. No HTTP search endpoint."""
from __future__ import annotations
from functools import lru_cache
import json,re,sqlite3,sys
from pathlib import Path
from . import kb_batch144_index as previous
from .kb_batch137_index import tokenize
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch146_lessons as new
LocalEditorOnlyError=previous.LocalEditorOnlyError
BAD=re.compile(r"[\x00-\x1f\x7f]")
@lru_cache(maxsize=1)
def load():
    past=previous.load()
    more=json.loads(new.OUT.read_text(encoding="utf-8"))
    if more!=new.build():raise ValueError("unreviewed manuscript source drift")
    new.validate(more)
    rows=past+more
    if len(rows)!=85 or len({r["id"] for r in rows})!=85:
        raise ValueError("85 unique manuscript inventory required")
    if json.loads(new.AUDIT.read_text(encoding="utf-8"))!=new.audit(more):
        raise ValueError("seven-track aggregate drift")
    return rows
@lru_cache(maxsize=1)
def _db():
    db=sqlite3.connect(":memory:",check_same_thread=False)
    db.execute('CREATE VIRTUAL TABLE draft_index USING fts5(body,tokenize="unicode61")')
    for r in load():
        # Do not index any full teacher solution, example answer, or unsafe hint.
        brief=" ".join([r.get("title",""),r["formal_definition_or_theorem"],
                        r["notation_and_domain"],r["applicability_and_hypotheses"]])
        db.execute("INSERT INTO draft_index(body) VALUES (?)",(" ".join(tokenize(brief)),))
    db.commit()
    return db
def public_coverage():
    rows=load()
    return dict(scope="85_PROVISIONAL_UNPUBLISHED_EDITOR_DRAFTS_NOT_OFFICIAL_SYLLABUS",
         editorial_review_manuscripts=85,
         by_track={t:sum(r["course_track"]==t for r in rows) for t in new.TRACKS},
         official_atom_denominators={t:None for t in new.TRACKS},
         official_course_coverage_rate=None,teacher_approved=0,student_authoritative=0,
         general_proof_certified=0,student_free_text_steps_verified=0,
         teacher_solution_or_manuscript_included=False)
def validate_query(query,limit):
    if not isinstance(query,str) or not 1<=len(query.strip())<=160 or BAD.search(query):
        raise ValueError("invalid search input")
    if type(limit) is not int or not 1<=limit<=20:
        raise ValueError("invalid search limit")
def editor_preview_search(query,*,scope="",track=None,limit=8):
    # EDITOR_LOCAL is an internal scope marker, not a credential; this method is NOT routed.
    if scope!="EDITOR_LOCAL":
        raise LocalEditorOnlyError("unpublished editor previews are not student evidence")
    validate_query(query,limit)
    if track is not None and track not in new.TRACKS:raise ValueError("unknown track")
    ts=tokenize(query)
    if not ts:return []
    expr=" OR ".join('"'+t+'"' for t in ts)
    hits=_db().execute(
       "SELECT rowid,bm25(draft_index) FROM draft_index WHERE draft_index MATCH ? ORDER BY bm25(draft_index)",
       (expr,)).fetchall()
    rows=load();out=[]
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
    validate_query(query,limit)
    return dict(status="NO_APPROVED_EVIDENCE",candidates=[],
         teacher_solution_exposed=False,unverified_content_exposed=False)
