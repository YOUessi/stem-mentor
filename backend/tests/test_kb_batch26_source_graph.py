"""Batch26: K00 original-PDF re-extraction + K01/K06 editorial graph negatives.

All checks are about source traceability and safe graph proposals, NOT
teacher approval, official atomization or complete theorem verification.
"""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path

import pytest

from app.deep_knowledge import lessons, curriculum
from app.deep_retrieval import editor_draft_full, student_evidence_lookup
from app.kb_batch26_graph import (
    MANIFEST, SCOPE, EditorGraphError, proposed_graph,
    validate_editorial_graph, editor_prerequisite_proposals,
)

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch26_source_reextract as audit
import build_kb_batch26_graph_progress as graph_progress


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


OLD=load(audit.ORIGINAL)
NEW=load(audit.REEXTRACTED)
REPORT=load(audit.OUTPUT)
GRAPH=load(MANIFEST)


def test_k00_reextraction_report_is_reproducible_and_conservative():
    assert json.loads(audit.build()) == REPORT
    audit.validate_source(OLD)
    audit.validate_source(NEW)
    summary=REPORT["summary"]
    assert summary["source_pages"]==61
    assert summary["original_pdf_byte_sha_verified"] is True
    assert summary["frozen_marker_occurrences"]==315
    assert summary["reextracted_marker_occurrences"]==317
    assert summary["delta_markers"]==2
    assert summary["changed_page_text_hashes"]==61
    assert summary["changed_page_marker_counts"]==[52]
    assert summary["human_visually_rechecked_pages"]==0
    assert summary["verified_official_atomic_denominator"] is None
    assert summary["official_coverage_rate"] is None
    assert not summary["teacher_approved_lessons"]
    assert not summary["student_published_lessons"]
    assert sum(x["occurrence_delta"] for x in REPORT["tracks"])==2
    assert {x["track"] for x in REPORT["tracks"]}=={
        "COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
        "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"}


@pytest.mark.parametrize("page",range(13,74))
def test_each_original_pdf_page_keeps_independent_extractors_uncertainty(page):
    row=REPORT["page_comparison"][page-13]
    assert row["printed_page"]==page
    assert row["pdf_page_index"]==page+7
    assert row["source_text_human_eyeball_review"]=="PENDING"
    assert row["frozen_marker_occurrences"] >= 0
    assert row["reextracted_marker_occurrences"] >= 0
    assert row["page_text_hash_matches"] is False
    assert row["delta"]==(2 if page==52 else 0)


@pytest.mark.parametrize("track",[
    "COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A",
    "ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"])
def test_track_marker_occurrences_are_not_official_atoms(track):
    row=next(x for x in REPORT["tracks"] if x["track"]==track)
    assert row["verified_official_atomic_denominator"] is None
    assert row["review"]=="PENDING"
    assert row["reextracted_markers"]-row["frozen_markers"]==row["occurrence_delta"]


@pytest.mark.parametrize("tamper",[
    "wrong_pdf", "page_removed", "page_offset", "new_track",
    "bad_page_hash", "duplicate_marker", "bad_marker_hash",
    "bad_marker_page", "approved_marker", "invented_atom_total", "changed_count",
])
def test_frozen_source_integrity_rejects_wrong_claims(tamper):
    d=copy.deepcopy(NEW)
    if tamper=="wrong_pdf":d["source"]["sha256"]="f"*64
    if tamper=="page_removed":d["pages"].pop()
    if tamper=="page_offset":d["pages"][0]["pdf_page_index"]+=1
    if tamper=="new_track":d["pages"][0]["tracks_present"]=["NOT_MATH"]
    if tamper=="bad_page_hash":d["pages"][0]["pdf_text_sha256"]="a"
    if tamper=="duplicate_marker":d["enumerated_source_anchors"].append(
        copy.deepcopy(d["enumerated_source_anchors"][0]))
    if tamper=="bad_marker_hash":d["enumerated_source_anchors"][0]["line_sha256"]="0"
    if tamper=="bad_marker_page":d["enumerated_source_anchors"][0]["pdf_page_index"]=20
    if tamper=="approved_marker":d["enumerated_source_anchors"][0]["teacher_review"]="APPROVED"
    if tamper=="invented_atom_total":d["denominator_contract"]["official_atomic_knowledge_denominator"]=317
    if tamper=="changed_count":d["pages"][0]["source_numbered_marker_count"]=8
    with pytest.raises(ValueError):audit.validate_source(d)


def test_prerequisite_candidates_are_valid_and_teacher_only():
    out=validate_editorial_graph(GRAPH)
    assert out["candidate_edges"]==31
    assert out["lessons_with_candidate_edges"]==31
    assert out["missing_explicit_edges_in_authoritative_graph"]==133
    assert out["combined_candidate_graph_acyclic"]
    assert not out["student_graph_changed"]
    assert out["teacher_approved_edges"]==0
    assert out==proposed_graph()
    assert GRAPH["scope"]==SCOPE
    assert not GRAPH["student_publishable"]
    assert GRAPH["teacher_signature"] is None
    assert all(not x["applied_to_authoritative_lesson_graph"]
               and x["teacher_review"]=="PENDING" for x in GRAPH["items"])
    assert len(lessons())==287


@pytest.mark.parametrize("index",range(31))
def test_each_editorial_edge_links_two_real_lessons_and_requires_review(index):
    row=GRAPH["items"][index]
    ids={x.id for x in lessons()}
    assert row["lesson_id"] in ids
    assert row["prerequisite_lesson_id"] in ids
    assert row["lesson_id"] != row["prerequisite_lesson_id"]
    assert len(row["rationale"])>=20
    local=editor_prerequisite_proposals(row["lesson_id"],scope="EDITOR_LOCAL")
    assert local["status"]=="EDITORIAL_REVIEW_PENDING"
    assert not local["teacher_signed"]
    assert not local["student_publishable"]
    assert row["prerequisite_lesson_id"] in {x["knowledge_id"] for x in local["proposals"]}


@pytest.mark.parametrize("tamper",[
    "fake_teacher", "fake_approved", "student_open", "missing_rationale",
    "orphan", "self_edge", "duplicate_edge", "already_applied", "cycle"
])
def test_graph_mutations_fail_closed(tamper):
    d=copy.deepcopy(GRAPH)
    if tamper=="fake_teacher":d["teacher_signature"]={"id":"fake"}
    if tamper=="fake_approved":d["items"][0]["teacher_review"]="APPROVED"
    if tamper=="student_open":d["student_publishable"]=True
    if tamper=="missing_rationale":d["items"][0]["rationale"]=""
    if tamper=="orphan":d["items"][0]["prerequisite_lesson_id"]="math.hs.nonexistent"
    if tamper=="self_edge":d["items"][0]["prerequisite_lesson_id"]=d["items"][0]["lesson_id"]
    if tamper=="duplicate_edge":d["items"].append(copy.deepcopy(d["items"][0]))
    if tamper=="already_applied":d["items"][0]["applied_to_authoritative_lesson_graph"]=True
    if tamper=="cycle":
        # The first candidate points into an existing prerequisite chain:
        # provoke cycle by adding reverse dependency as an editor proposal.
        a,b=d["items"][0]["lesson_id"],d["items"][0]["prerequisite_lesson_id"]
        # a source with preexisting graph links cannot be treated as unlinked.
        d["items"][0]["lesson_id"]=b
        d["items"][0]["prerequisite_lesson_id"]=a
    with pytest.raises(EditorGraphError):validate_editorial_graph(d)


def test_editor_preview_is_editor_only_student_lookup_stays_closed():
    target=GRAPH["items"][0]["lesson_id"]
    with pytest.raises(PermissionError):editor_prerequisite_proposals(target)
    with pytest.raises(PermissionError):editor_draft_full(target)
    with pytest.raises(KeyError):editor_prerequisite_proposals("math.hs.absent",scope="EDITOR_LOCAL")
    full=editor_draft_full(target,scope="EDITOR_LOCAL")
    assert full["review_status"]=="REVIEW_PENDING"
    assert full["condition_status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert full["prerequisite_editorial_candidates"]["status"]=="EDITORIAL_REVIEW_PENDING"
    assert full["content"]["teacher_solution_visibility"]=="TEACHER_ONLY"
    for question in ("正弦定理", "条件概率", "方程平方后增根", "问卷无应答偏差"):
        answer=student_evidence_lookup(question)
        assert answer["status"]=="NO_APPROVED_EVIDENCE"
        assert answer["candidates"]==[]
        assert not answer["teacher_solution_exposed"]
        assert not answer["unverified_content_exposed"]
        assert "prerequisite_editorial_candidates" not in answer


def test_versioned_graph_progress_is_reproducible_and_never_fake_verified():
    actual=json.loads(graph_progress.build())
    assert actual==load(graph_progress.OUT)
    s=actual["summary"]
    assert s["draft_lessons"]==287
    assert s["authoritative_unlinked_lessons"]==133
    assert s["lessons_with_new_editorial_proposals"]==31
    assert s["still_without_editorial_proposals"]==102
    assert s["teacher_approved"]==0
    assert s["officially_verified_atomic_denominator"] is None
    assert all(not x["student_visible"] and not x["teacher_verified"]
               for x in actual["items"])
