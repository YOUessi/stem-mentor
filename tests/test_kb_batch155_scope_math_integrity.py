"""KB155: source census reconciles every discovered layout anchor, no false approval."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch155_review_matrix as m
import check_kb_batch155_exact_cases as oracle
from app import kb_batch155_review_status
from app.main import app

@pytest.fixture(scope="module")
def matrix():
    d=json.loads(m.OUT.read_text(encoding="utf-8"))
    assert d==m.build()
    assert m.validate(d)
    assert m.REPORT.read_text(encoding="utf-8")==m.render(d)
    return d

@pytest.fixture(scope="module")
def witnesses():
    w=json.loads(oracle.OUT.read_text(encoding="utf-8"))
    assert w==oracle.run()
    return w

def test_all_source_populations_are_reconciled_without_counterfeit_denominator(matrix):
    assert (matrix["printed_source_pages"],matrix["numbered_source_layout_markers"],
            matrix["provisional_atom_proposals"],matrix["independent_CDE_unnumbered_proposals"],
            matrix["classified_CDE_original_nonempty_lines"],matrix["historical_editorial_leads"],
            matrix["teacher_only_manuscripts"])==(61,315,41,32,122,239,145)
    assert (matrix["editorial_leads_with_teacher_only_drafts"],
            matrix["editorial_leads_missing_teacher_only_drafts"])==(104,135)
    assert set(matrix["by_track"])==set(m.TRACKS)
    assert all(v is None for v in matrix["official_atom_denominators"].values())
    assert matrix["current_official_completion_rate"] is None
    assert not matrix["official_source_scope_complete"]
    assert not matrix["crosspage_semantic_dedup_human_complete"]
    assert matrix["student_authoritative"]==matrix["real_teacher_approved"]==0
    assert sum(v["numbered_source_markers"] for v in matrix["by_track"].values())==315
    assert sum(v["unnumbered_CDE_editorial_proposals"] for v in matrix["by_track"].values())==32

@pytest.mark.parametrize("i",range(315))
def test_every_numbered_source_marker_is_mapped_to_exact_sha_not_certified(i,matrix):
    x=matrix["source_marker_obligations"][i]
    assert x["id"]==f'STD2020-P{x["printed_page"]}-L{x["pdfkit_line"]:03d}'
    assert x["pdf_page_index"]==x["printed_page"]+7
    assert len(x["source_line_sha256"])==64
    assert x["course_track"] in m.TRACKS
    assert x["review_state"]=="REVIEW_PENDING" and x["official_atom_id"] is None
    assert not x["student_publishable"] and not x["teacher_approved"]
    assert x["link_semantics"]=="LINE_OVERLAP_NOT_KNOWLEDGE_EQUIVALENCE"
    page=matrix["by_page"][x["printed_page"]-13]
    assert x["id"] in page["marker_ids"]
    if x["overlapping_teacher_only_draft_ids"]:
        assert x["overlapping_editorial_lead_ids"]
    if not (x["overlapping_editorial_lead_ids"] or x["overlapping_41_proposal_ids"]):
        assert x["id"] in page["unpaired_marker_ids"]
        assert x["next_action"]=="HUMAN_SPLIT_OR_VALIDATE_UNPAIRED_REQUIREMENT"

@pytest.mark.parametrize("i",range(32))
def test_each_unnumbered_elective_proposal_retains_exact_line_identity(i,matrix):
    x=matrix["unnumbered_CDE_editorial_obligations"][i]
    assert x["review_state"]=="REVIEW_PENDING" and x["official_atom_id"] is None
    assert not x["student_publishable"] and not x["teacher_approved"]
    assert x["course_track"] in ("ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
    assert x["is_school_elective_example"]==(x["course_track"]=="ELECTIVE_E")
    assert x["semantic_duplicate_with_other_proposals"]=="UNDETERMINED"
    assert len(x["source_line_ids"])==len(x["source_line_sha256"])>0
    assert all(len(h)==64 for h in x["source_line_sha256"])
    for p in x["printed_pages"]:
        assert x["id"] in matrix["by_page"][p-13]["CDE_unnumbered_proposal_ids"]

@pytest.mark.parametrize("i",range(61))
def test_each_page_has_machine_auditable_pending_source_obligations(i,matrix):
    p=matrix["by_page"][i]
    assert p["printed_page"]==i+13
    assert len(p["pdf_text_sha256"])==64
    assert p["scope_in_unnumbered_lines"]=="UNKNOWN"
    assert p["scope_review"]=="REVIEW_PENDING" and p["official_atom_count"] is None
    assert p["unpaired_layout_markers"]==len(p["unpaired_marker_ids"])
    assert p["source_markers"]==len(p["marker_ids"])
    assert len(p["editorial_leads_missing_deep_draft_ids"])>=0

@pytest.mark.parametrize("i",range(89))
def test_historical_source_relation_is_not_an_automatic_semantic_merge(i,matrix):
    e=matrix["source_relation_review_queue"][i]
    assert e["source_lead_a"]!=e["source_lead_b"]
    assert e["human_semantic_decision"]=="REVIEW_PENDING"
    assert e["automatic_merge_permitted"] is False

@pytest.mark.parametrize("i",range(145))
def test_all_drafts_still_require_teacher_review(i):
    draft=m.load(m.DEPTH)["rows"][i]
    assert draft["review"]=="REVIEW_PENDING"
    assert draft["track"] in m.TRACKS
    assert draft["source_sha"] is None or len(draft["source_sha"])==64

@pytest.mark.parametrize("i",range(30))
def test_independent_exact_boundary_and_false_premise_witness(i,witnesses):
    w=witnesses["witnesses"][i]
    assert w["condition_class"]==("EXACT_FINITE_WITNESS" if i%2==0 else
                                 "INVALID_PRECONDITION_REJECTED")
    assert w["exact_check"] and w["sample_limited"]
    assert not w["formal_general_proof_certified"] and not w["teacher_approved"]
    assert not w["arbitrary_student_step_verified"]

@pytest.mark.parametrize("field,bad",[
    ("official_source_scope_complete",True),
    ("crosspage_semantic_dedup_human_complete",True),
    ("human_semantic_merges",1),
    ("math_proof_certified_by_this_audit",1),
    ("real_teacher_approved",1),
    ("student_authoritative",1),
    ("current_official_completion_rate",0.9),
    ("numbered_source_layout_markers",314),
    ("historical_editorial_leads",238),
    ("editorial_leads_with_teacher_only_drafts",145),
    ("editorial_leads_missing_teacher_only_drafts",134),
    ("teacher_only_manuscripts",144),
    ("independent_CDE_unnumbered_proposals",31),
    ("historical_pending_source_relation_records",88),
])
def test_high_impact_false_completion_edits_fail_closed(field,bad,matrix):
    changed=copy.deepcopy(matrix);changed[field]=bad
    with pytest.raises(ValueError):m.validate(changed)

@pytest.mark.parametrize("field,bad",[
    ("official_atom_id","FAKE-OFFICIAL"),
    ("teacher_approved",True),
    ("student_publishable",True),
    ("review_state","APPROVED"),
    ("source_line_sha256","broken"),
    ("link_semantics","SEMANTICALLY_EQUAL"),
])
def test_all_numbered_source_row_forgeries_are_rejected(field,bad,matrix):
    changed=copy.deepcopy(matrix);changed["source_marker_obligations"][100][field]=bad
    with pytest.raises(ValueError):m.validate(changed)

@pytest.mark.parametrize("field,bad",[
    ("course_track","COMPULSORY"),
    ("is_school_elective_example",True),
    ("official_atom_id","FAKE"),
    ("teacher_approved",True),
    ("student_publishable",True),
    ("semantic_duplicate_with_other_proposals","CONFIRMED_EQUIVALENT"),
    ("source_line_sha256",[]),
])
def test_cde_optional_school_example_cannot_be_promoted(field,bad,matrix):
    changed=copy.deepcopy(matrix)
    changed["unnumbered_CDE_editorial_obligations"][0][field]=bad
    with pytest.raises(ValueError):m.validate(changed)

@pytest.mark.parametrize("field,bad",[
    ("scope_in_unnumbered_lines",0),
    ("scope_review","APPROVED"),
    ("official_atom_count",10),
])
def test_page_level_fake_scope_certification_rejected(field,bad,matrix):
    changed=copy.deepcopy(matrix);changed["by_page"][0][field]=bad
    with pytest.raises(ValueError):m.validate(changed)

def test_no_hidden_teacher_content_leaks_through_public_endpoint(matrix):
    result=TestClient(app).get("/api/knowledge/kb155-source-readiness")
    assert result.status_code==200
    v=result.json()
    assert v==kb_batch155_review_status.public_status()
    assert v["official_completion_rate"] is None
    assert all(vv is None for vv in v["official_atom_denominators"].values())
    assert v["student_authoritative"]==v["teacher_approved"]==0
    assert v["original_source_text_included"] is False
    assert v["teacher_solutions_included"] is False
    raw=json.dumps(v,ensure_ascii=False)
    for forbidden in ("teacher_examples","reasoned_solution","formal_definition_or_theorem",
                      "original_paraphrase","source_line_sha256","reference_answer",
                      "student_hint_ladder","source_marker_obligations"):
        assert forbidden not in raw

def test_student_evidence_still_fail_closed():
    from app import kb_batch154_index as prior
    assert prior.student_evidence_lookup("导数求极值")["status"]=="NO_APPROVED_EVIDENCE"
    assert prior.student_evidence_lookup("导数求极值")["teacher_solution_exposed"] is False


@pytest.mark.parametrize("i",range(41))
def test_missing_audit_source_sha_relinked_to_immutable_prior_proposal(i,matrix):
    r=matrix["old_draft_proposal_lineage_reconciliations"][i]
    assert r["draft_audit_source_sha_was_null"] is True
    assert r["reconciliation"]=="EXISTING_PROPOSAL_SOURCE_LOCK_NOT_NEW_PDF_REHASH"
    assert r["teacher_review"]=="REVIEW_PENDING"
    assert r["mathematical_verification"]=="NOT_CERTIFIED"
    assert r["official_atom_id"] is None
    src={p["id"]:p for p in m.load(m.PROP)["records"]}[r["candidate_id"]]
    assert src["source_lock"]["span_sha256"]==r["source_span_sha256"]
    assert src["source_lock"]["line_sha256"]==r["source_line_sha256"]
