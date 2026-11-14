"""Executable K00 official-marker coverage truth and K07 10-conflict finite witnesses."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"backend"))
import build_kb_batch148_official_clause_gate as k00
import review_kb_batch148_conflicts as k07
from app import kb_batch148_audit
from app.main import app

@pytest.fixture(scope="module")
def census():return k00.build()
@pytest.fixture(scope="module")
def conflicts():return k07.build()

def test_source_315_61_41_239_and_report_replay(census):
    assert k00.validate_report(census)
    assert census==json.loads(k00.OUT.read_text(encoding="utf-8"))
    assert k00.render(census)==k00.MD.read_text(encoding="utf-8")
    assert census["source_numbered_marker_count"]==315
    assert census["source_scan_pages"]==61
    assert census["provisional_atom_proposal_count"]==41
    assert census["historical_editorial_leads"]==239
    assert census["teacher_pending_manuscripts"]==95
    assert census["relation_edges_pending"]==89
    assert sum(t["numbered_source_markers"] for t in census["by_track"].values())==315
    assert sum(t["deep_teacher_pending_drafts"] for t in census["by_track"].values())==95
    assert not census["official_atomic_census_complete"]
    assert not census["crosspage_semantic_dedup_complete"]
    assert not census["unnumbered_clause_atomization_complete"]

@pytest.mark.parametrize("i",range(315))
def test_each_numbered_source_marker_is_not_an_official_atom(i,census):
    row=census["candidate_map"][i]
    assert row["source_marker_id"].startswith("STD2020-")
    assert len(row["source_line_sha256"])==64
    assert row["official_atom_id"] is None
    assert row["teacher_review"]=="REVIEW_PENDING"
    assert row["semantic_equivalence"]=="UNDETERMINED"
    assert row["source_marker_is_official_atom"] is False
    assert row["source_overlap_only"] is True
    assert not row["student_authoritative"]
    assert all(item.startswith("kb133-proposal-") for item in row["provisional_atom_proposal_ids"])
    assert all(item.startswith("hs-semantic-pilot-") for item in row["editorial_lead_ids"])

@pytest.mark.parametrize("i",range(61))
def test_every_source_page_has_explicit_not_complete_state(i,census):
    row=census["source_pages"][i]
    assert row["printed_page"]==i+13
    assert row["pdf_page_index"]==i+20
    assert row["unnumbered_requirement_status"]=="UNKNOWN_REQUIRES_HUMAN_SCOPE_SPLIT"
    assert row["scope_review"]=="REVIEW_PENDING"
    assert row["official_atoms_certified"]==0
    assert len(row["pdf_text_sha256"])==64

@pytest.mark.parametrize("track",k00.TRACKS)
def test_seven_track_denominators_remain_unknown(track,census):
    assert census["official_atom_denominators"][track] is None
    row=census["by_track"][track]
    assert row["official_knowledge_atom_denominator"] is None
    assert row["teacher_approved"]==0
    assert row["marker_without_any_matched_line"]<=row["numbered_source_markers"]

@pytest.mark.parametrize("field,value",[
    ("official_atomic_census_complete",True),
    ("unnumbered_clause_atomization_complete",True),
    ("crosspage_semantic_dedup_complete",True),
    ("human_semantic_merges_approved",1),
    ("teacher_approved",1),
    ("student_authoritative",1)])
def test_reject_false_global_completion_mutations(census,field,value):
    altered=copy.deepcopy(census);altered[field]=value
    with pytest.raises(ValueError):k00.validate_report(altered)

@pytest.mark.parametrize("field,value",[
    ("teacher_review","APPROVED"),
    ("semantic_equivalence","SAME_ATOM"),
    ("official_atom_id","fake-atom"),
    ("source_marker_is_official_atom",True),
    ("source_overlap_only",False),
    ("student_authoritative",True)])
def test_reject_false_per_anchor_authority_mutations(census,field,value):
    altered=copy.deepcopy(census);altered["candidate_map"][0][field]=value
    with pytest.raises(ValueError):k00.validate_report(altered)

@pytest.mark.parametrize("kind",["source_hash","marker_id","source_track","proposal_approval","missing_anchor","orphan_prerequisite"])
def test_reject_raw_source_or_curriculum_forgery(kind):
    numbered=k00.read(k00.OFFICIAL);proposals=k00.read(k00.PROPOSALS); leads=k00.read(k00.ED_LEADS)
    if kind=="source_hash":numbered["source"]["sha256"]="0"*64
    elif kind=="marker_id":numbered["enumerated_source_anchors"][0]["id"]="FAKE"
    elif kind=="source_track":numbered["enumerated_source_anchors"][0]["track"]="ELECTIVE_Z"
    elif kind=="proposal_approval":proposals["records"][0]["atomization_review"]="APPROVED"
    elif kind=="missing_anchor":numbered["enumerated_source_anchors"].pop()
    elif kind=="orphan_prerequisite":proposals["records"][0]["prerequisite_proposals"]=["fake-id"]
    with pytest.raises(ValueError):k00.validate_raw(numbered,proposals,leads)

@pytest.mark.parametrize("i",range(41))
def test_each_proposal_is_still_unapproved_and_source_locked(i):
    r=k00.read(k00.PROPOSALS)["records"][i]
    assert r["knowledge_type"] in ("Concept","Theorem","Method")
    assert r["official_atom_id"] is None and r["teacher_approval"] is None
    assert r["atomization_review"]=="REVIEW_PENDING"
    assert r["source_evidence_status"]=="PDFKIT_LINE_REHASHED_SEMANTIC_PENDING"
    assert len(r["source_lock"]["span_sha256"])==64
    assert not r["student_authoritative"]

@pytest.mark.parametrize("i",range(239))
def test_every_editorial_lead_pending_does_not_turn_into_an_atom(i):
    r=k00.read(k00.ED_LEADS)["candidates"][i]
    assert r["official_atom_id"] is None
    assert r["semantic_review"]=="REVIEW_PENDING"
    assert not r["teacher_approved"]

def test_ten_conflict_versions_and_40_exact_cases_recompute(conflicts):
    assert k07.validate(conflicts)
    assert conflicts==json.loads(k07.OUT.read_text(encoding="utf-8"))
    assert k07.render(conflicts)==k07.MD.read_text(encoding="utf-8")
    assert len({x["id"] for x in conflicts["source_identity"]})==10
    assert all(v["decision"]=="HOLD_BOTH_SOURCE_VERSIONS" for v in conflicts["source_identity"])
    assert all(len(v["candidate_sha256"])==len(v["active_sha256"])==64 for v in conflicts["source_identity"])
    assert conflicts["formal_general_proof_certificates"]==0
    assert conflicts["math_conflicts_human_resolved"]==0
    assert conflicts["teacher_approved"]==0

@pytest.mark.parametrize("i",range(40))
def test_each_independent_finite_witness_and_invalid_premise(i,conflicts):
    row=conflicts["cases"][i]
    # Re-execute the pure symbolic/numeric oracle rather than just trusting archive booleans.
    assert k07.cases()[row["conflict_id"]][row["case_index"]][1] is True
    assert row["exact_finite_check_passed"] is True
    assert row["case_kind"]==k07.cases()[row["conflict_id"]][row["case_index"]][0]
    assert row["interpretation"].startswith("finite controlled witness")

@pytest.mark.parametrize("field,value",[
    ("teacher_approved",1),("student_authoritative",1),
    ("source_versions_merged",1),("math_conflicts_human_resolved",1),
    ("formal_general_proof_certificates",1),("review_state","APPROVED")])
def test_k07_reject_fake_teacher_or_proof_approval(conflicts,field,value):
    modified=copy.deepcopy(conflicts);modified[field]=value
    with pytest.raises(ValueError):k07.validate(modified)

def test_public_api_is_aggregate_not_retrieval_or_answer():
    r=TestClient(app).get("/api/knowledge/kb148-curriculum-evidence-status")
    assert r.status_code==200
    payload=r.json()
    assert payload["source_numbered_markers"]==315
    assert payload["provisional_atom_proposals"]==41
    assert payload["historical_editorial_leads"]==239
    assert payload["unpublished_teacher_review_manuscripts"]==95
    assert payload["unresolved_math_conflicts"]==10
    assert payload["bounded_conflict_math_witnesses"]==40
    assert payload["teacher_approved"]==payload["student_authoritative"]==payload["general_proof_certificates"]==0
    assert len(payload["by_track"])==7
    assert all(t["official_atom_denominator"] is None for t in payload["by_track"].values())
    assert not payload["student_solution_exposed"] and not payload["draft_content_exposed"] and not payload["syllabus_text_exposed"]
    assert not any(key in payload for key in ("reasoned_steps","teacher_examples","teacher_solution","source_text","proof"))
    assert kb_batch148_audit.student_evidence_lookup("函数图像")["status"]=="NO_APPROVED_EVIDENCE"
    assert not any("kb148" in route.path and "search" in route.path for route in app.routes)
