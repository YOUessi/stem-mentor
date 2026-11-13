"""Regression/anti-forgery for ten legacy conflict teacher-only proof packets."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch70_conflict_review as B

@pytest.fixture(scope="module")
def packet():
    return B.build()

def test_generated_snapshots_and_baseline(packet):
    B.write(check=True)
    assert packet["new_packets"]==10
    assert packet["new_draft_claim_reason_steps"]==40
    assert packet["bounded_checks"]==10
    assert packet["conflicts_resolved"]==0
    assert packet["historical_unverified_proof_steps_remaining"]==538
    assert packet["teacher_approved"]==packet["general_proofs_certified"]==packet["student_published"]==0
    assert all(v is None for v in packet["official_atomic_denominator"].values())
    assert len({x["packet_id"] for x in packet["records"]})==10
    assert len({x["conflict_id"] for x in packet["records"]})==10

@pytest.mark.parametrize("i",range(10))
def test_mathematical_statement_has_auditable_assumptions_and_proof(packet,i):
    row=packet["records"][i]
    assert row["conflict_id"]==B.IDS[i]
    assert len(row["assumptions"])>=2
    assert len(row["proof_steps"])==4
    assert [s["step"] for s in row["proof_steps"]]==[1,2,3,4]
    assert all(s["claim"] and s["justification"] for s in row["proof_steps"])
    assert row["knowledge_kind"] in ("THEOREM","CONCEPT","METHOD")
    assert row["bounded_math_check"]=="FINITE_EXACT_INSTANCE_ONLY"
    assert row["general_proof_certified"] is False
    assert row["dispute_resolution"].startswith("UNRESOLVED")
    assert row["version_winner"] is None
    assert row["candidate_sha256"]!=row["active_sha256"]
    assert row["teacher_signature"] is None and row["teacher_review"]=="REVIEW_PENDING"
    assert row["official_atomic_membership"]=="UNDETERMINED"

@pytest.mark.parametrize("i",range(10))
def test_hints_errors_transfers_teacher_only(packet,i):
    v=packet["records"][i]
    assert len(v["hints"])==3 and len(set(v["hints"]))==3
    assert v["worked_example"]["question"] and v["worked_example"]["teacher_solution"]
    assert v["invalid_case"]["false_claim"] and v["invalid_case"]["counterexample_explanation"]
    assert v["near_transfer"]!=v["far_transfer"]
    assert v["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert v["student_publishable"] is False
    assert v["student_freeform_steps_verified"] is False

@pytest.mark.parametrize("i",range(10))
def test_finite_cases_are_exact_but_never_universal_proofs(i):
    assert B.exact_case(i) is True

@pytest.mark.parametrize("i",range(10))
def test_teacher_signature_forgery_is_rejected(i):
    copy=deepcopy(B.load(B.AUTHORING))
    copy["items"][i]["teacher_review"]="APPROVED"
    copy["items"][i]["teacher_signature"]="fake-teacher"
    with pytest.raises(ValueError,match="Forged teacher"):
        B.build(custom_authoring=copy)

@pytest.mark.parametrize("i",range(10))
def test_proof_certification_forgery_is_rejected(i):
    copy=deepcopy(B.load(B.AUTHORING))
    copy["items"][i]["proof_certification"]="FORMALLY_CERTIFIED"
    with pytest.raises(ValueError,match="Forged proof"):
        B.build(custom_authoring=copy)

@pytest.mark.parametrize("i",range(10))
def test_student_visibility_forgery_is_rejected(i):
    copy=deepcopy(B.load(B.AUTHORING))
    copy["items"][i]["student_publishable"]=True
    with pytest.raises(ValueError,match="Teacher answer exposure"):
        B.build(custom_authoring=copy)

@pytest.mark.parametrize("i",range(10))
def test_source_sha_forgery_is_rejected(i):
    copy=deepcopy(B.load(B.SOURCE))
    copy["conflicts"][i]["candidate_sha256"]="0"*64
    with pytest.raises(ValueError,match="Forged frozen source"):
        B.build(custom_source=copy)

@pytest.mark.parametrize("i",range(10))
def test_missing_step_is_rejected(i):
    copy=deepcopy(B.load(B.AUTHORING))
    copy["items"][i]["proof_steps"].pop()
    with pytest.raises(ValueError,match="Missing/incorrectly ordered proof"):
        B.build(custom_authoring=copy)

@pytest.mark.parametrize("i",range(10))
def test_empty_justification_is_rejected(i):
    copy=deepcopy(B.load(B.AUTHORING))
    copy["items"][i]["proof_steps"][0]["justification"]=""
    with pytest.raises(ValueError,match="Unsupported claim-reason"):
        B.build(custom_authoring=copy)

def test_duplicate_conflict_entry_and_unsupported_math_index_denied():
    copy=deepcopy(B.load(B.AUTHORING))
    copy["items"][1]["conflict_id"]=copy["items"][0]["conflict_id"]
    with pytest.raises(ValueError,match="Missing/duplicate"):
        B.build(custom_authoring=copy)
    with pytest.raises(ValueError,match="Unknown finite check"):
        B.exact_case(999)

from test_attested_release_batch08 import offline_reviewer_fixture

@pytest.mark.parametrize("i",range(10))
def test_mixed_student_index_does_not_leak_new_teacher_answers(i,offline_reviewer_fixture,packet):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    row=packet["records"][i]
    response=student_evidence_lookup(row["title"])
    serialized=json.dumps(response,ensure_ascii=False)
    assert {x["knowledge_id"] for x in response["candidates"]}<={doc.id}
    assert row["packet_id"] not in serialized
    assert row["worked_example"]["teacher_solution"] not in serialized
    assert response["teacher_solution_exposed"] is False
    assert response["unverified_content_exposed"] is False
