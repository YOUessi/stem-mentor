"""Batch72: separate 28 non-atom source requirements, 14 teaching protocols and safety."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch72_independent_evidence as M

@pytest.fixture(scope="module")
def build():
    return M.build()

def source_copy():
    return deepcopy(json.loads(M.SRC.read_text(encoding="utf-8")))

def old_copy():
    return deepcopy(json.loads(M.OLD.read_text(encoding="utf-8")))

def test_generated_artifacts_reproduce(build):
    c,l,d=build
    assert M.COVER.read_text(encoding="utf-8")==M.encode(c)
    assert M.LESSONS.read_text(encoding="utf-8")==M.encode(l)
    assert M.REPORT.read_text(encoding="utf-8")==d

def test_counts_and_legal_classification(build):
    c,l,_=build
    assert len(c["records"])==28
    assert len(l["items"])==14
    assert c["source_kind_counts"]=={"TEACHING_GUIDANCE":14,"ACHIEVEMENT_REQUIREMENT":11,"ACTIVITY_REQUIREMENT":3}
    assert c["candidate_evidence_links"]==28
    assert c["linked_assessment_proposals"]==14
    assert c["new_teaching_protocol_drafts"]==14

def test_no_official_claims_or_student_data(build):
    c,l,_=build
    assert all(v is None for v in c["official_atom_denominator"].values())
    assert c["verified_requirement_coverage"]==0
    assert c["teacher_approved"]==c["student_published"]==c["general_proof_certified"]==0
    assert l["student_data_included"] is False
    assert all(x["teacher_review"]=="REVIEW_PENDING" and x["student_publishable"] is False for x in c["records"])

@pytest.mark.parametrize("i",range(28))
def test_source_linkage_and_nonatom_honesty(i,build):
    c,_,_=build
    src=source_copy()["rows"][i]
    r=c["records"][i]
    assert src["source_candidate_id"]==r["source_candidate_id"]
    assert src["source_span_pdfkit_sha256"]==r["source_span_pdfkit_sha256"]
    assert src["source_page_pdfkit_sha256"]==r["source_page_pdfkit_sha256"]
    assert r["teacher_signature"] is None and r["student_publishable"] is False
    assert r["coverage_status"]=="UNMAPPED"
    assert r["full_clause_teacher_review"]=="NOT_DONE"
    assert r["candidate_alignment"]=="UNVERIFIED"
    assert r["verified_student_steps"]==0
    assert r["official_atom_membership"]=="NONATOM_SOURCE_SPAN"

@pytest.mark.parametrize("i",range(14))
def test_teaching_material_is_substantive_and_restricted(i,build):
    _,l,_=build
    t=l["items"][i]
    assert t["type"]=="TEACHING_ACTION"
    assert t["source_license"]=="PROJECT_AUTHORED"
    assert len(t["teacher_procedure"])==4
    assert len(t["three_stage_hints"])==3
    assert t["near_transfer"] != t["far_transfer"]
    assert sum(x["points"] for x in t["rubric"])==t["score_total"]==6
    assert t["observable_anonymized_evidence"]
    assert t["typical_wrong_claim"] != t["error_reason"]
    assert t["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert t["math_verification"]=="FINITE_EXACT_CASE_ONLY"
    assert t["general_proof_certified"] is False
    assert t["teacher_signature"] is None
    assert all(v is None for k,v in t["observation_form"].items() if k!="synthetic_only")
    assert t["student_publishable"] is False

@pytest.mark.parametrize("i",range(14))
def test_exact_finite_case_not_general_proof(i):
    assert M.exact_case(i) is True
    assert M.hash_bytes(M.GUIDANCE[i][2].encode())==M.MATH_EXAMPLE_DIGESTS[i]

@pytest.mark.parametrize("i",range(28))
def test_source_review_forgery_rejected(i):
    s=source_copy();s["rows"][i]["teacher_approved"]=True
    with pytest.raises(ValueError,match="source track/review tamper"): M.build(source=s)

@pytest.mark.parametrize("i",range(28))
def test_source_sha_forgery_rejected(i):
    s=source_copy();s["rows"][i]["source_span_pdfkit_sha256"]="x"*64
    with pytest.raises(ValueError,match="malformed source SHA"): M.build(source=s)

@pytest.mark.parametrize("i",range(14))
def test_wrong_assessment_alignment_rejected(i):
    o=old_copy();o["items"][i]["source_candidate_id"]="UNKNOWN"
    with pytest.raises(ValueError,match="legacy assessment source/status mismatch"): M.build(assessments=o)

@pytest.mark.parametrize("i",range(14))
def test_teacher_only_assessment_policy_rejected(i):
    o=old_copy();o["items"][i]["student_published"]=True
    with pytest.raises(ValueError,match="legacy assessment source/status mismatch"): M.build(assessments=o)

@pytest.mark.parametrize("i",range(14))
def test_missing_teaching_math_or_explanation_rejected(i):
    scenarios=deepcopy(M.GUIDANCE);item=list(scenarios[i]);item[2]="假";scenarios[i]=tuple(item)
    with pytest.raises(ValueError,match="incomplete teacher protocol"): M.build(scenarios=scenarios)

@pytest.mark.parametrize("i",range(14))
def test_fake_math_case_with_valid_length_rejected(i):
    scenarios=deepcopy(M.GUIDANCE);item=list(scenarios[i]);item[2]="我们可以不检查前提，任何参数和任何取值都会完全相同。";scenarios[i]=tuple(item)
    with pytest.raises(ValueError,match="math case text changed"): M.build(scenarios=scenarios)

def test_empty_duplicate_missing_category_are_rejected():
    s=source_copy();s["rows"].pop()
    with pytest.raises(ValueError,match="28 unique spans"): M.build(source=s)
    s=source_copy();s["rows"][1]["source_candidate_id"]=s["rows"][0]["source_candidate_id"]
    with pytest.raises(ValueError,match="28 unique spans"): M.build(source=s)
    s=source_copy();s["rows"][0]["source_kind"]="THEOREM"
    with pytest.raises(ValueError,match="incorrect source category"): M.build(source=s)

def test_mac_pdfkit_all_exact_page_and_span_digests():
    from os import environ
    if environ.get("KB72_VERIFY_LOCAL_SOURCE")!="1":
        pytest.skip("Local Mac-only frozen PDFKit extracts not distributed on CI")
    records=source_copy()["rows"]
    assert M.mac_verify_source(records)==10

from test_attested_release_batch08 import offline_reviewer_fixture

@pytest.mark.parametrize("i",range(14))
def test_student_retrieval_does_not_expose_teacher_drafts(i,build,offline_reviewer_fixture):
    sys.path.insert(0,str(ROOT/"backend"))
    from app import deep_retrieval as R
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert R.approved_lesson_ids()=={doc.id}
    t=build[1]["items"][i]
    response=R.student_evidence_lookup(t["title"],limit=8)
    assert response["teacher_solution_exposed"] is False
    assert response["unverified_content_exposed"] is False
    assert {x["knowledge_id"] for x in response["candidates"]}<={doc.id}
    payload=json.dumps(response,ensure_ascii=False)
    assert t["id"] not in payload
    assert t["bounded_math_example"] not in payload
    assert t["typical_wrong_claim"] not in payload
