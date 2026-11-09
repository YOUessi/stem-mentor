"""Batch62 exact source-coordinate/privilege and independent competency gates."""
from copy import deepcopy
from pathlib import Path
import json
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch62_anchor_triage as A

TRIAGE=A.build()
ENTRIES=TRIAGE["rows"]
NONATOM=A.nonatom_matrix(TRIAGE)

def test_all_56_unlinked_anchors_have_original_mathematical_boundaries():
    assert TRIAGE["triaged_unlinked_anchors"]==56
    assert len({r["anchor_id"] for r in ENTRIES})==56
    assert TRIAGE["original_candidate_anchors"]==428
    assert TRIAGE["earlier_partial_leads"]==344
    assert TRIAGE["classification_counts"]=={
        "COMPETENCY_BLOCK":4,"CONTENT_BLOCK":5,"DIRECT_OBJECTIVE":4,
        "PEDAGOGY_BLOCK":5,"SUBSECTION_SCOPE":27,"TOPIC_CONTAINER":11}
    assert sum(TRIAGE["track_counts"].values())==56
    assert all(v is None for v in TRIAGE["official_atomic_denominator"].values())

@pytest.mark.parametrize("i",range(56))
def test_each_source_line_located_and_review_pending(i):
    row=ENTRIES[i]
    raw=A.rows()[i]
    assert row["anchor_id"]==raw["candidate_anchor_id"]
    assert row["source_line_sha256"]==raw["source_line_sha256"]
    assert row["teacher_review"]=="REVIEW_PENDING"
    assert row["teacher_signature"] is None
    assert row["mathematical_proof_certification"]=="NOT_CERTIFIED"
    assert row["educational_coverage"]=="NOT_ESTABLISHED"
    assert row["math_equivalence"]=="NOT_REVIEWED"
    assert row["source_lead_found"] is False
    assert row["student_publishable"] is False
    assert row["official_atomic_membership"]=="UNDETERMINED"
    assert row["proposed_child_atom_count"] is None
    assert row["full_source_context_verified"] is False
    assert len(row["math_or_coverage_boundary"])>=12
    assert len(row["original_topic_paraphrase"])>=2

@pytest.mark.parametrize("i",range(56))
def test_each_anchor_is_distinguished_from_parent_coverage_claim(i):
    row=ENTRIES[i]
    kind=row["marker_kind"]; cls=row["classification"]
    if kind=="SECTION_LABEL":
        assert cls in {"CONTENT_BLOCK","COMPETENCY_BLOCK","PEDAGOGY_BLOCK"}
    elif kind=="MAJOR_NUMBER":
        assert cls=="TOPIC_CONTAINER"
    elif kind=="CIRCLED_ITEM":
        assert cls=="DIRECT_OBJECTIVE"
    else:
        assert cls in {"SUBSECTION_SCOPE","DIRECT_OBJECTIVE"}
    assert row["next_action"] in {
      "SPLIT_AND_ATTEST_MATHEMATICAL_ATOMS_WITH_FULL_SOURCE_CONTEXT",
      "INSPECT_FULL_SECTION_AND_UNNUMBERED_OBJECTIVES",
      "REVIEW_CHILD_CLAUSES_NOT_STANDALONE_ATOM"}

@pytest.mark.parametrize("i",range(31))
def test_each_substantive_scope_holds_a_specific_math_boundary(i):
    rows=[r for r in ENTRIES if r["classification"] in ("SUBSECTION_SCOPE","DIRECT_OBJECTIVE")]
    assert len(rows)==31
    row=rows[i]
    assert row["review_area"]=="CONTENT_ATOMIZATION"
    assert row["mathematical_proof_certification"]=="NOT_CERTIFIED"
    assert "数学" not in row["math_or_coverage_boundary"] or len(row["math_or_coverage_boundary"])>12

def test_separate_sections_are_not_deleted_from_ability_coverage():
    assert NONATOM["total_sections"]==14
    assert NONATOM["counts_by_kind"]=={
        "COMPETENCY_BLOCK":4,"CONTENT_BLOCK":5,"PEDAGOGY_BLOCK":5}
    assert all(not r["unnumbered_requirements_checked"] for r in NONATOM["rows"])
    assert all(not r["teacher_approved"] for r in NONATOM["rows"])
    assert all(not r["ability_assessment_ids"] and not r["teaching_action_ids"] and
               not r["content_atom_ids"] for r in NONATOM["rows"])
    assert all(r["coverage_status"]=="UNMAPPED" for r in NONATOM["rows"])

def test_committed_reports_deterministic():
    assert A.OUT.read_text(encoding="utf-8")==A.canonical(TRIAGE)
    assert A.REPORT.read_text(encoding="utf-8")==A.render(TRIAGE)
    assert A.NONATOM.read_text(encoding="utf-8")==A.canonical(NONATOM)
    A.validate(TRIAGE)

@pytest.mark.parametrize("tamper",[
    "approve","signature","publish","certified","equivalent","claim_coverage",
    "claim_overlap","wrong_line","wrong_track","wrong_page","wrong_label",
    "empty_scope","fake_atoms","claim_source_context","delete_row","duplicate_row",
    "wrong_global_denominator","claim_teacher_pages","claim_teacher_total",
    "claim_students","claim_56_resolved","alter_queue_sha","alter_registry_sha"
])
def test_forged_status_scope_and_provenance_rejected(tamper):
    t=deepcopy(TRIAGE); r=t["rows"][0]
    if tamper=="approve":r["teacher_review"]="APPROVED"
    elif tamper=="signature":r["teacher_signature"]="fake"
    elif tamper=="publish":r["student_publishable"]=True
    elif tamper=="certified":r["mathematical_proof_certification"]="PROVED"
    elif tamper=="equivalent":r["math_equivalence"]="MATCH"
    elif tamper=="claim_coverage":r["educational_coverage"]="COMPLETE"
    elif tamper=="claim_overlap":r["source_lead_found"]=True
    elif tamper=="wrong_line":r["source_line_sha256"]="a"*64
    elif tamper=="wrong_track":r["track_hint"]="ELECTIVE_E"
    elif tamper=="wrong_page":r["printed_page"]=-4
    elif tamper=="wrong_label":r["classification"]="DIRECT_OBJECTIVE"
    elif tamper=="empty_scope":r["math_or_coverage_boundary"]=""
    elif tamper=="fake_atoms":r["proposed_child_atom_count"]=900
    elif tamper=="claim_source_context":r["full_source_context_verified"]=True
    elif tamper=="delete_row":t["rows"].pop()
    elif tamper=="duplicate_row":t["rows"][1]=deepcopy(r)
    elif tamper=="wrong_global_denominator":t["official_atomic_denominator"]["COMPULSORY"]=100
    elif tamper=="claim_teacher_pages":t["teacher_full_page_reviews"]=61
    elif tamper=="claim_teacher_total":t["teacher_approved"]=14
    elif tamper=="claim_students":t["student_published"]=56
    elif tamper=="claim_56_resolved":t["source_lead_overlap_still_missing"]=False
    elif tamper=="alter_queue_sha":t["parent_unlinked_queue_sha256"]="b"*64
    elif tamper=="alter_registry_sha":t["parent_registry_sha256"]="b"*64
    with pytest.raises(ValueError):
        A.validate(t)

def test_nonatom_topic_counts_are_not_official_denominators():
    assert TRIAGE["machine_triage_cannot_certify_math_or_source_completeness"] is True
    assert TRIAGE["teacher_full_page_reviews"]==0
    assert TRIAGE["teacher_approved"]==0
    assert TRIAGE["student_published"]==0
    assert NONATOM["no_section_is_atom"] is True
    assert NONATOM["no_section_approved"] is True

@pytest.mark.parametrize("i",[0,3,8,12,20,30,40,55])
def test_student_lookup_and_tutor_fail_closed_for_unreviewed_anchors(i):
    from app.deep_retrieval import student_evidence_lookup
    from app.model_tutor_draft import draft_next_question
    anchor=ENTRIES[i]["anchor_id"]
    result=student_evidence_lookup(anchor,limit=3)
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert result["candidates"]==[]
    assert result["teacher_solution_exposed"] is False
    attempt=draft_next_question(anchor,mode="GUIDE",help_requested=True,
       consent_to_cloud=True,operator_scope="EDITOR_LOCAL",
       provider_url="https://api.openai.com/v1/chat/completions",
       provider_model="offline-test-no-network")
    assert attempt.status=="BLOCKED" and attempt.reason=="NO_APPROVED_MATH_EVIDENCE"
    assert attempt.model_called is False and attempt.student_visible is False
