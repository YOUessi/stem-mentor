"""155 unpublished editorial drafts: local editor FTS only, students have zero authoritative hits."""
from __future__ import annotations
import json,sqlite3,sys
from functools import lru_cache
from pathlib import Path
from . import kb_batch154_index as previous
from .kb_batch137_index import tokenize
from .kb_batch147_index import validate_query
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch156_lessons as new
LocalEditorOnlyError=previous.LocalEditorOnlyError

@lru_cache(maxsize=1)
def load():
    past=previous.load()
    more=json.loads(new.OUT.read_text(encoding="utf-8"))
    if more!=new.build():raise ValueError("KB156 draft source drift")
    new.validate(more)
    rows=past+more
    if len(rows)!=155 or len({v["id"] for v in rows})!=155:
        raise ValueError("KB156 155 unique unapproved manuscripts required")
    if new.audit(more)!=json.loads(new.AUDIT.read_text(encoding="utf-8")):
        raise ValueError("KB156 seven-track K00 ledger drift")
    if any(r["teacher_review_status"]!="REVIEW_PENDING" or
           r["teacher_solution_visibility"]!="TEACHER_ONLY" or
           r["student_authoritative"] for r in rows):
        raise ValueError("KB156 rejects forged teacher approval")
    return rows

@lru_cache(maxsize=1)
def _db():
    db=sqlite3.connect(":memory:",check_same_thread=False)
    db.execute('CREATE VIRTUAL TABLE draft_index USING fts5(body,tokenize="unicode61")')
    for r in load():
        # No teacher answer, solution, hint ladder, counterexample or proof in the index.
        brief=" ".join([r.get("title",""),r["formal_definition_or_theorem"],
                        r["notation_and_domain"],r["applicability_and_hypotheses"]])
        db.execute("INSERT INTO draft_index(body) VALUES (?)",(" ".join(tokenize(brief)),))
    db.commit()
    return db

def editor_preview_search(query,*,scope="",track=None,limit=8):
    if scope!="EDITOR_LOCAL":
        raise LocalEditorOnlyError("unapproved KB156 local search is editor-only")
    validate_query(query,limit)
    if track is not None and track not in new.TRACKS:raise ValueError("invalid track")
    ts=tokenize(query)
    if not ts:return []
    expr=" OR ".join('"'+t+'"' for t in ts)
    hits=_db().execute("SELECT rowid,bm25(draft_index) FROM draft_index WHERE draft_index MATCH ? ORDER BY bm25(draft_index)",(expr,)).fetchall()
    rows=load(); out=[]
    for rowid,rank in hits:
        r=rows[rowid-1]
        if track is not None and r["course_track"]!=track:continue
        out.append(dict(id=r["id"],course_track=r["course_track"],
             review_status="REVIEW_PENDING",condition_status="CONDITIONS_NOT_ESTABLISHED",
             source_candidate_id=r.get("source_candidate_id",r.get("candidate_id")),
             student_publishable=False,rank=round(float(rank),6)))
        if len(out)>=limit:break
    return out

def student_evidence_lookup(query,*,limit=8):
    validate_query(query,limit)
    return dict(status="NO_APPROVED_EVIDENCE",candidates=[],
          teacher_solution_exposed=False,unverified_content_exposed=False)

def public_coverage():
    rows=load();audit=new.audit(new.build())
    return dict(scope="155_EDITOR_ONLY_PENDING_DRAFTS_NOT_OFFICIAL_SYLLABUS",
       editorial_review_manuscripts=len(rows),
       by_track=audit["by_track"],historical_editorial_source_candidates=239,
       editorial_source_candidates_linked=114,editorial_source_candidates_unlinked=125,
       numbered_syllabus_layout_markers_not_atomic_denominators=315,
       official_atom_denominators={t:None for t in new.TRACKS},
       official_coverage_rate=None,teacher_approved=0,student_authoritative=0,
       general_proof_certified=0,student_free_text_steps_verified=0,
       teacher_solution_or_manuscript_included=False)
