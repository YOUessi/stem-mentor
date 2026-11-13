"""Batch71: page35 modelling depth, exact numeric evidence, K00 honesty, safe retrieval."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch71_modelling as M


@pytest.fixture(scope="module")
def built():
    return M.build()


def changed_author(i,field,value):
    copy=deepcopy(M.load(M.AUTHOR))
    copy["items"][i][field]=value
    return copy


def test_artifacts_are_byte_reproducible_and_not_official(built):
    M.write(check=True)
    report,links,coverage=built
    assert report["model_drafts"]==7
    assert report["worked_examples"]==14
    assert report["reasoning_steps"]==28
    assert report["bounded_exact_checks"]==7
    assert report["teacher_approved"]==report["student_published"]==0
    assert report["formally_certified_math_proofs"]==0
    assert links["complete_editorial_drafts"]==7
    assert links["official_clause_certified"]==0
    assert links["official_denominator"] is None
    assert all(v is None for v in report["official_atomic_denominator"].values())
    assert all(v is None for v in coverage["official_atom_denominator"].values())
    assert coverage["official_missing_atom_count"] is None
    assert coverage["unmapped_unnumbered_objectives"]==14
    assert coverage["historical_unverified_proof_steps"]==538
    assert coverage["unresolved_math_conflicts"]==10
    assert coverage["teacher_full_page_reviews"]==0


@pytest.mark.parametrize("i",range(7))
def test_source_lineage_uses_distinct_original_page35_split(i,built):
    report,links,coverage=built
    row=report["records"][i]; link=links["records"][i]
    assert row["source_anchor"]==f"KB51-C-P035-V{i+1:03d}"
    assert row["manuscript_id"]==link["lesson_id"]
    assert row["knowledge_kind"]==M.KINDS[i]
    assert row["source_printed_page"]==35
    assert row["source_pdf_sha256"]==links["source_pdf_sha256"]
    assert row["source_full_page_review"]=="NOT_COMPLETED"
    assert row["official_atomic_membership"]=="UNDETERMINED"
    assert link["official_clause_review"]=="NOT_DONE"
    assert link["official_atomic_membership"]=="UNDETERMINED"


@pytest.mark.parametrize("i",range(7))
def test_each_editorial_type_has_fully_auditable_depth(i,built):
    row=built[0]["records"][i]
    assert len(row["assumptions"])>=2
    assert len(row["prerequisites"])>=2
    assert len(row["symbols"])>=2
    assert len(row["steps"])==4
    assert len(row["worked_examples"])>=2
    assert row["definition"] and row["validity_why"] and row["boundary"]
    assert row["invalid_case"]["false_claim"] and row["invalid_case"]["counterexample_explanation"]
    assert len(row["hints"])==3
    assert row["near_transfer"]!=row["far_transfer"]
    assert sum(pts for _,pts in row["scoring_rubric"])==6


@pytest.mark.parametrize("i",range(7))
def test_independent_exact_math_matches_one_named_case_only(i,built):
    row=built[0]["records"][i]
    note=M.finite_witness(i,row["finite_case"])
    assert note==row["finite_validation_note"]
    assert row["finite_validation_level"]=="EXACT_NUMERIC_CASE_ONLY"
    assert row["formal_certification"]=="NOT_FORMALLY_CERTIFIED"
    assert row["student_freeform_proof_steps_verified"] is False


@pytest.mark.parametrize("i",range(7))
def test_teacher_approval_is_not_self_issued(i):
    copy=changed_author(i,"status","APPROVED")
    copy["items"][i]["teacher_signature"]="Self"
    with pytest.raises(ValueError,match="Forged teacher approval"):
        M.build(custom_author=copy)


@pytest.mark.parametrize("i",range(7))
def test_rejects_formal_proof_claim_without_proof_checker(i):
    copy=changed_author(i,"formal_certification","FORMALLY_CERTIFIED")
    with pytest.raises(ValueError,match="Forged mathematical proof certification"):
        M.build(custom_author=copy)


@pytest.mark.parametrize("i",range(7))
def test_student_teacher_solution_leak_blocked(i):
    copy=changed_author(i,"student_publishable",True)
    with pytest.raises(ValueError,match="Teacher-only answer exposure"):
        M.build(custom_author=copy)


@pytest.mark.parametrize("i",range(7))
def test_bad_authoring_source_license_is_rejected(i):
    copy=changed_author(i,"source_license","UNKNOWN_COPYRIGHT")
    with pytest.raises(ValueError,match="Invalid source"):
        M.build(custom_author=copy)


@pytest.mark.parametrize("i",range(7))
def test_wrong_type_is_rejected_not_forced_into_theorem(i):
    copy=changed_author(i,"knowledge_kind","THEOREM")
    with pytest.raises(ValueError,match="Knowledge-type mismatch"):
        M.build(custom_author=copy)


@pytest.mark.parametrize("i",range(7))
def test_wrong_page35_source_anchor_is_rejected(i):
    copy=changed_author(i,"anchor","KB51-C-P999-V001")
    with pytest.raises(ValueError,match="Page35 candidate id/order mismatch"):
        M.build(custom_author=copy)


@pytest.mark.parametrize("i",range(7))
def test_missing_reasoning_step_is_rejected(i):
    copy=deepcopy(M.load(M.AUTHOR))
    copy["items"][i]["steps"].pop()
    with pytest.raises(ValueError,match="Four auditable reasoning steps"):
        M.build(custom_author=copy)


@pytest.mark.parametrize("i",range(7))
def test_missing_second_example_is_rejected(i):
    copy=deepcopy(M.load(M.AUTHOR))
    copy["items"][i]["worked_examples"].pop()
    with pytest.raises(ValueError,match="At least two complete"):
        M.build(custom_author=copy)


@pytest.mark.parametrize("i",range(7))
def test_score_must_be_a_six_point_domain_rubric(i):
    copy=deepcopy(M.load(M.AUTHOR))
    copy["items"][i]["scoring_rubric"][0][1]=7
    with pytest.raises(ValueError,match="Six-point criterion"):
        M.build(custom_author=copy)


@pytest.mark.parametrize("i",range(7))
def test_extrapolation_or_wrong_math_target_is_rejected(i):
    copy=deepcopy(M.load(M.AUTHOR))
    key=("expected","expected_km","minimum_units","expected_residual",
         "expected_solution","expected","algebraic_forecast")[i]
    copy["items"][i]["finite_case"][key]+=1
    with pytest.raises(ValueError,match="Incorrect|Not the minimum|Wrong|Failed|factorization"):
        M.build(custom_author=copy)


@pytest.mark.parametrize("i",range(7))
def test_float_is_not_a_rigorous_numeric_math_witness(i):
    copy=deepcopy(M.load(M.AUTHOR))
    key=("rate","minutes","fixed","slope","fixed","n","rate")[i]
    copy["items"][i]["finite_case"][key]=1.125
    with pytest.raises(ValueError,match="exact integers"):
        M.build(custom_author=copy)


@pytest.mark.parametrize("i",range(7))
def test_retrieval_excludes_unapproved_modelling_teacher_solution(i,built,offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    row=built[0]["records"][i]
    response=student_evidence_lookup(row["title"])
    raw=json.dumps(response,ensure_ascii=False)
    assert {x["knowledge_id"] for x in response["candidates"]}<={doc.id}
    assert row["manuscript_id"] not in raw
    assert row["worked_examples"][0]["teacher_solution"] not in raw
    assert response["teacher_solution_exposed"] is False
    assert response["unverified_content_exposed"] is False


from test_attested_release_batch08 import offline_reviewer_fixture


def test_14_unnumbered_objectives_not_spuriously_mapped():
    objectives=M.load(M.OBJECTIVES)
    assert len(objectives["rows"])==14
    assert all(row["coverage_status"]=="UNMAPPED" for row in objectives["rows"])


def test_fake_objective_promotion_is_rejected():
    copy=deepcopy(M.load(M.OBJECTIVES))
    copy["rows"][0]["coverage_status"]="APPROVED"
    with pytest.raises(ValueError,match="Forged 14 competencies"):
        M.build(custom_objectives=copy)


def test_fake_modelling_source_promotion_is_rejected():
    copy=deepcopy(M.load(M.SOURCE))
    copy["teacher_review"]="APPROVED"
    with pytest.raises(ValueError,match="Forged page35 candidate source"):
        M.build(custom_source=copy)


def test_no_false_student_export_or_official_denominator():
    report,links,coverage=M.build()
    assert {r["teacher_solution_visibility"] for r in report["records"]}=={"TEACHER_ONLY"}
    assert not any(r["student_publishable"] for r in report["records"])
    assert coverage["unknown_not_zero"] is True
    assert coverage["page35_teacher_approved"]==0
