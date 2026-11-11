"""Negative tests for the 300-label / 24-edited-candidate non-authority audit."""
from __future__ import annotations
import copy
import sys
from pathlib import Path
import pytest
HERE=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(HERE/"scripts"),str(HERE/"backend")]
from scripts import build_kb_batch93_candidate_triage as b
from scripts.kb_batch93_authoring import RECORDS
from app.kb_batch93_finite_oracles import CASES, finite_check

@pytest.fixture(scope="module")
def output():
    return b.build()

def test_all_project_labels_have_one_exclusive_state(output):
    assert len(output["provisional_candidate_ledger"]) == 300
    assert {r["candidate_id"] for r in output["provisional_candidate_ledger"]} == {
        r["candidate_id"] for r in b.read(b.SOURCES)["provisional_candidate_backlog"]}
    states={s:sum(r["scope_audit_state"]==s for r in output["provisional_candidate_ledger"]) for s in
        ("PAIR_RELATION_EDITORIAL_PENDING","SINGLE_CANDIDATE_EDITORIAL_PENDING",
        "NOT_YET_INDIVIDUALLY_AUDITED")}
    assert states=={"PAIR_RELATION_EDITORIAL_PENDING":166,
                    "SINGLE_CANDIDATE_EDITORIAL_PENDING":24,
                    "NOT_YET_INDIVIDUALLY_AUDITED":110}

def test_false_denominators_are_rejected_and_unknowns_preserved(output):
    assert output["official_atom_denominator"] is None
    assert set(output["official_atom_denominators_by_track"]) == set(b.TRACKS)
    assert all(v is None for v in output["official_atom_denominators_by_track"].values())
    assert output["fully_teacher_atomized_pages"]==0
    assert output["teacher_approved"]==0
    assert output["student_authoritative_release"]==0
    assert output["teacher_equivalence_adjudications"]==0
    assert output["historical_uncertified_proof_steps"]==538
    assert output["unresolved_math_conflicts"]==10
    assert output["remaining_without_pairwise_comparison"]==134

@pytest.mark.parametrize("track",b.TRACKS)
def test_every_track_uses_provisional_not_official_denominator(output,track):
    row=output["per_track"][track]
    assert row["official_atom_denominator"] is None
    assert row["teacher_approved"]==0
    assert row["provisional_labels"] == sum(row[k] for k in
        ("relation_compared_pending","individual_math_scope_pending","not_yet_individually_audited"))

@pytest.mark.parametrize("idx",range(24))
def test_every_math_review_is_source_locked_and_unapproved(output,idx):
    row=output["individual_math_review_notes"][idx]
    assert row["candidate_id"]==RECORDS[idx][0]
    assert len(row["source_line_sha256"])==64
    assert row["review_status"]=="REVIEW_PENDING"
    assert row["scope_classification"]=="SOURCE_CANDIDATE_MATH_EDITORIAL_ONLY"
    assert row["pairwise_semantic_adjudication"]=="NOT_PERFORMED"
    assert row["official_atom_id"] is None
    assert row["general_theorem_certified"] is False
    assert row["teacher_approved"] is False
    assert row["student_publishable"] is False
    assert all(len(row[k])>=25 for k in
        ("editorial_math_scope","necessary_conditions",
         "controlled_worked_witness","counterexample_or_invalid_boundary"))

@pytest.mark.parametrize("candidate_id",list(CASES))
def test_independent_finite_and_invalid_premise_examples(candidate_id):
    check=finite_check(candidate_id)
    assert check["finite_positive_case"] is True
    assert check["premise_or_boundary_rejection"] is True
    assert check["general_theorem_certified"] is False
    assert check["teacher_approved"] is False
    assert check["student_publishable"] is False

@pytest.mark.parametrize("idx",range(24))
def test_removing_any_counterexample_must_fail_closed(idx):
    copy_notes=copy.deepcopy(RECORDS)
    row=list(copy_notes[idx]);row[4]="";copy_notes[idx]=row
    with pytest.raises(ValueError, match="substance|counterexample"):
        b.build(notes=copy_notes)

@pytest.mark.parametrize("idx",range(24))
def test_duplicate_source_candidate_must_fail_closed(idx):
    copy_notes=copy.deepcopy(RECORDS)
    row=list(copy_notes[idx]);row[0]="KB80-A015-L011-C01";copy_notes[idx]=row
    with pytest.raises(ValueError, match="source not in unpaired"):
        b.build(notes=copy_notes)

@pytest.mark.parametrize("idx",range(24))
def test_short_unjustified_claim_must_fail_closed(idx):
    copy_notes=copy.deepcopy(RECORDS)
    row=list(copy_notes[idx]);row[2]="任何输入都能用";copy_notes[idx]=row
    with pytest.raises(ValueError, match="substance|counterexample"):
        b.build(notes=copy_notes)

@pytest.mark.parametrize("field,value",[
    ("official_math_atom_id","OFFICIAL-FAKE"),
    ("teacher_approval","someone"),
    ("student_authoritative_index_eligible",True),
    ("review_status","APPROVED"),
    ("official_atom_count_contribution",1),
    ("source_line_sha256","tampered"),
])
def test_forged_history_authority_or_source_fails_anywhere(field,value):
    source=b.read(b.SOURCES)
    source["provisional_candidate_backlog"][-1][field]=value
    with pytest.raises(ValueError,match="forged prior source"):
        b.build(source=source)

@pytest.mark.parametrize("field,value",[
    ("official_atom_denominator",300),
    ("teacher_approved",1),
    ("student_published",1),
])
def test_forged_historical_summary_fails(field,value):
    source=b.read(b.SOURCES)
    source[field]=value
    with pytest.raises(ValueError,match="historical provisional"):
        b.build(source=source)

@pytest.mark.parametrize("field,value",[
    ("official_curriculum_atom_denominator",300),
    ("teacher_approved",1),
    ("student_authoritative_release",1),
    ("teacher_adjudicated_atom_merges",1),
    ("general_theorem_proof_certificates",1),
])
def test_forged_pairwise_upstream_authority_fails(field,value):
    prev=b.read(b.PREVIOUS)
    prev[field]=value
    with pytest.raises(ValueError,match="drift|certification"):
        b.build(previous=prev)

def test_swapped_pair_sources_are_rejected():
    prev=b.read(b.PREVIOUS)
    prev["relation_reviews"][0]["left_source"]["source_line_sha256"]="a"*64
    with pytest.raises(ValueError,match="stale source lineage"):
        b.build(previous=prev)

def test_no_student_leak_or_proof_in_ledger(output):
    for row in output["provisional_candidate_ledger"]:
        assert row["official_atom_id"] is None
        assert row["teacher_approved"] is False
        assert row["student_authoritative_index_eligible"] is False
        assert row["source_line_not_official_atom"] is True
        assert "teacher_solution" not in row
        assert "approved_proof" not in row

def test_reproducible_generated_artifacts_are_frozen():
    check=b.run(check=True)
    assert check["new_individual_math_scope_reviews"]==24
    assert check["finite_math_checks"]==14


# Regression: a forged 64-hex digest used to pass length-only provenance checks.
@pytest.mark.parametrize("candidate_index", [0, 35, 75, 141, 201, 261, 291, 299])
def test_valid_length_forged_source_line_sha_is_rejected(candidate_index):
    source = b.read(b.SOURCES)
    current = source["provisional_candidate_backlog"][candidate_index]["source_line_sha256"]
    source["provisional_candidate_backlog"][candidate_index]["source_line_sha256"] = (
        "a" * 64 if current != "a" * 64 else "b" * 64
    )
    with pytest.raises(ValueError, match="frozen Batch89"):
        b.build(source=source)


@pytest.mark.parametrize("field, replacement", [
    ("source_page", 999),
    ("source_review_id", "FORGED-SOURCE"),
    ("provisional_topic", "伪造知识单元"),
    ("track", "ELECTIVE_E"),
])
def test_source_identity_change_without_new_review_is_rejected(field,replacement):
    source = b.read(b.SOURCES)
    source["provisional_candidate_backlog"][0][field] = replacement
    with pytest.raises(ValueError, match="frozen Batch89"):
        b.build(source=source)
