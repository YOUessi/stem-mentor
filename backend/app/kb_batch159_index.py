"""KB159 185 unpublished drafts: editor-only retrieval and aggregate status.

The service may only expose metadata for authorized editor work. No learner may
retrieve pending manuscripts, their worked answers or any certified statement.
"""
from __future__ import annotations
import json,sqlite3,sys
from functools import lru_cache
from pathlib import Path
from . import kb_batch158_index as previous
from .kb_batch137_index import tokenize
from .kb_batch147_index import validate_query

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch159_functions as module
LocalEditorOnlyError=previous.LocalEditorOnlyError

@lru_cache(maxsize=1)
def load():
    prior=previous.load()
    current=json.loads(module.OUT.read_text(encoding="utf-8"))
    if current!=module.build():
        raise ValueError("KB159 source or chapter content drift")
    module.validate(current)
    audit=json.loads(module.AUDIT.read_text(encoding="utf-8"))
    if audit!=module.audit(current):
        raise ValueError("KB159 source review audit drift")
    dossiers=json.loads(module.ATOMS.read_text(encoding="utf-8"))
    if dossiers!=module.provisional_atom_dossiers(current):
        raise ValueError("KB159 atom dossier drift")
    rows=prior+current
    if len(rows)!=185 or len({r["id"] for r in rows})!=185:
        raise ValueError("KB159 185 unique unpublished manuscripts expected")
    if any(r["teacher_review_status"]!="REVIEW_PENDING" or
           r["teacher_solution_visibility"]!="TEACHER_ONLY" or
           r["student_authoritative"] or
           r["teacher_review_evidence"] is not None for r in rows):
        raise ValueError("KB159 forbids invented teacher approvals")
    return rows

@lru_cache(maxsize=1)
def _db():
    db=sqlite3.connect(":memory:",check_same_thread=False)
    db.execute('CREATE VIRTUAL TABLE draft_index USING fts5(body,tokenize="unicode61")')
    for r in load():
        brief=" ".join([r.get("title",""),r["formal_definition_or_theorem"],
                        r["notation_and_domain"],r["applicability_and_hypotheses"]])
        # Never include worked examples, teacher answer, proofs, counterexamples
        # or hint ladder in the persisted local FTS field.
        db.execute("INSERT INTO draft_index(body) VALUES(?)",(" ".join(tokenize(brief)),))
    db.commit()
    return db

def editor_preview_search(query,*,scope="",track=None,limit=8):
    if scope!="EDITOR_LOCAL":
        raise LocalEditorOnlyError("unapproved KB159 content is editor-only")
    validate_query(query,limit)
    if track is not None and track not in module.TRACKS:
        raise ValueError("invalid curriculum track")
    ts=tokenize(query)
    if not ts:return []
    expr=" OR ".join('"'+term+'"' for term in ts)
    hits=_db().execute(
        "SELECT rowid,bm25(draft_index) FROM draft_index WHERE draft_index MATCH ? ORDER BY bm25(draft_index)",
        (expr,)).fetchall()
    rows=load();out=[]
    for index,rank in hits:
        r=rows[index-1]
        if track is not None and track!=r["course_track"]:continue
        out.append(dict(id=r["id"],course_track=r["course_track"],
            review_status="REVIEW_PENDING",condition_status="CONDITIONS_NOT_ESTABLISHED",
            source_candidate_id=r.get("source_candidate_id",r.get("candidate_id")),
            student_publishable=False,rank=round(float(rank),6)))
        if len(out)==limit:break
    return out

def student_evidence_lookup(query,*,limit=8):
    validate_query(query,limit)
    return dict(status="NO_APPROVED_EVIDENCE",candidates=[],
        teacher_solution_exposed=False,unverified_content_exposed=False)

def public_coverage():
    rows=load();audit=module.audit(module.build())
    return dict(scope="185_EDITOR_ONLY_PENDING_DRAFTS_NOT_OFFICIAL_SYLLABUS",
        editorial_review_manuscripts=len(rows),by_track=audit["by_track"],
        historical_editorial_source_candidates=239,
        editorial_source_candidates_linked=144,
        editorial_source_candidates_unlinked=95,
        numbered_syllabus_layout_markers_not_atomic_denominators=315,
        official_atom_denominators=audit["official_atom_denominators"],
        official_coverage_rate=None,
        teacher_approved=0,student_authoritative=0,
        general_proof_certified=0,student_free_text_steps_verified=0,
        provisional_atom_dossiers=10,
        provisional_semantic_overlap_pairs=len(audit["possible_semantic_overlap_pairs"]),
        teacher_solution_or_manuscript_included=False)
