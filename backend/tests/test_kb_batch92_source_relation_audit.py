"""Batch92 source audit: 48 topic IDs, 24 original mathematical comparisons.

All editorial mathematics is non-authoritative and may not be promoted by a
finite witness or by an untrusted request. Tests explicitly freeze this boundary.
"""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch92_relations as B
from app.kb_batch92_exact_witness import check_all, verify
from app.deep_retrieval import student_evidence_lookup, editor_draft_search, EditorOnlyError


@pytest.fixture(scope="module")
def scope():
    return B.build()


@pytest.fixture(scope="module")
def previous():
    return B.B90.build(), B.B89.build()[1]


def test_absolute_course_scope_distinctions(scope):
    assert scope["source_anchor_count"] == 428
    assert scope["provisional_topics"] == 300
    assert scope["previous_relation_pairs"] == 60
    assert scope["new_relation_pairs"] == 24
    assert scope["cumulative_relation_pairs"] == 84
    assert scope["previously_reviewed_provisional_topics"] == 118
    assert scope["newly_reviewed_provisional_topics"] == 48
    assert scope["cumulative_reviewed_provisional_topics"] == 166
    assert scope["remaining_unpaired_provisional_topics"] == 134
    assert len(scope["remaining_unpaired_candidate_ids"]) == 134
    assert scope["official_curriculum_atom_denominator"] is None
    assert set(scope["official_atom_denominators_by_track"]) == set(B.TRACKS)
    assert all(v is None for v in scope["official_atom_denominators_by_track"].values())
    assert scope["full_page_teacher_atomization_reviews"] == 0
    assert scope["teacher_adjudicated_atom_merges"] == 0
    assert scope["teacher_approved"] == scope["student_authoritative_release"] == 0
    assert scope["historical_uncertified_proof_steps"] == 538
    assert scope["historical_P0_unreviewed_proof_steps"] == 106
    assert scope["unresolved_math_conflicts"] == 10


def test_per_track_ledger_reconciles_to_frozen_scope(scope):
    tracks = scope["per_track"]
    assert sum(v["provisional_topics"] for v in tracks.values()) == 300
    assert sum(v["prior_reviewed"] for v in tracks.values()) == 118
    assert sum(v["newly_reviewed"] for v in tracks.values()) == 48
    assert sum(v["cumulative_reviewed"] for v in tracks.values()) == 166
    assert sum(v["still_without_relations"] for v in tracks.values()) == 134
    for track,v in tracks.items():
        assert v["provisional_topics"] == v["cumulative_reviewed"] + v["still_without_relations"]
        assert v["official_curriculum_atom_denominator"] is None
        assert v["teacher_approved"] == 0
    assert tracks["ELECTIVE_E"]["provisional_topics"] == 0
    assert tracks["ELECTIVE_E"]["official_curriculum_atom_denominator"] is None


@pytest.mark.parametrize("index", range(24))
def test_original_relation_provenance_scope_and_boundary(scope,index):
    item=scope["relation_reviews"][index]
    assert item["review_id"]==f"KB92-REL-{index+1:03d}"
    assert item["review_status"]=="REVIEW_PENDING"
    assert item["teacher_approved"] is False
    assert item["math_equivalence_certified"] is False
    assert item["student_publishable"] is False
    assert item["final_atom_id"] is None
    assert item["teacher_review"] is None
    assert item["official_atom_adjudication"]=="NOT_PERFORMED"
    assert item["student_authoritative_index_eligible"] is False
    for side in ("left_source","right_source"):
        source=item[side]
        assert len(source["source_line_sha256"])==64
        assert source["candidate_id"] and source["source_review_id"]
        assert source["track"] in B.TRACKS
        assert source["source_page"] is not None
    assert len(item["shared_maths"])>=25
    assert len(item["distinguishing_conditions"])>=34
    assert len(item["worked_witness"])>=25
    assert len(item["failure_or_boundary"])>=25
    assert "CERTIFIED" not in item["finite_verification"]["status"]


@pytest.mark.parametrize("index", range(1,17))
def test_independent_finite_exact_witnesses(index):
    data=verify(index)
    assert data["status"]=="VERIFIED_FINITE_INSTANCE_WITH_BOUNDARY_REJECTION"
    assert data["review_id"]==f"KB92-REL-{index:03d}"
    assert data["witness"]
    assert data["general_theorem_certified"] is False
    assert data["semantic_equivalence_certified"] is False
    assert data["teacher_approved"] is False
    assert data["student_publishable"] is False
    assert data["evidence_scope"]=="CONTROLLED_EXACT_OR_SYMBOLIC_CASE_ONLY"


@pytest.mark.parametrize("index",range(16,24))
def test_unverified_editorial_math_is_explicit_not_verified(scope,index):
    evidence=scope["relation_reviews"][index]["finite_verification"]
    assert evidence["status"]=="NOT_AUTOMATICALLY_VERIFIED"
    assert evidence["evidence_scope"]=="UNVERIFIED_EDITORIAL_WITNESS"


@pytest.mark.parametrize("value",[0,17,-1,True,1.5,"1",None])
def test_math_guard_rejects_unsupported_claims(value):
    with pytest.raises(ValueError):
        verify(value)


def test_all_witness_keys_are_subset_of_authored_source_relations(scope):
    all_cards=check_all()
    assert len(all_cards)==scope["independently_checked_finite_witnesses"]==16
    assert set(all_cards)<=set(r["review_id"] for r in scope["relation_reviews"])
    assert scope["original_editorial_only_witnesses"]==8


def test_previous_covered_ids_never_counted_twice(scope,previous):
    already=set(previous[0]["remaining_unpaired_candidate_ids"])
    now=set(scope["remaining_unpaired_candidate_ids"])
    touched={x for r in scope["relation_reviews"] for x in
             (r["left_candidate_id"],r["right_candidate_id"])}
    assert len(touched)==48
    assert touched<=already
    assert len(touched & now)==0
    assert already==now|touched
    assert len(touched)==len(set(touched))


@pytest.mark.parametrize("index",range(24))
def test_no_editorial_relation_is_student_authoritative(scope,index):
    r=scope["relation_reviews"][index]
    assert r["student_authoritative_index_eligible"] is False
    assert r["final_atom_id"] is None
    assert r["review_status"]=="REVIEW_PENDING"
    # Plain public student retrieval must never see unapproved editorial evidence.
    result=student_evidence_lookup(r["left_source"]["provisional_topic"])
    assert result["teacher_solution_exposed"] is False
    assert result["unverified_content_exposed"] is False


@pytest.mark.parametrize("poison",[
    "teacher_root","student_root","semantic_root","wrong_version",
    "short_math","wrong_edge","duplicate_edge","reuse_endpoint",
    "fake_teacher","fake_math_cert","fake_student_release","invented_atom",
    "missing_record","extra_record","invalid_source_fingerprint",
    "fabricated_prior_denominator","fabricated_prior_approval",
])
def test_forged_scope_duplicate_authority_and_math_rejected(scope,previous,poison):
    raw=deepcopy(B.read(B.AUTHOR))
    old=deepcopy(previous[0])
    hist=deepcopy(previous[1])
    first=raw["relations"][0]
    if poison=="teacher_root":raw["teacher_approved"]=True
    elif poison=="student_root":raw["student_publishable"]=True
    elif poison=="semantic_root":raw["semantic_equivalence_certified"]=True
    elif poison=="wrong_version":raw["standard_version"]="fake"
    elif poison=="short_math":first["worked_witness"]="a"
    elif poison=="wrong_edge":first["left_candidate_id"]="FAKE-CANDIDATE"
    elif poison=="duplicate_edge":raw["relations"][1]["left_candidate_id"]=first["right_candidate_id"]
    elif poison=="reuse_endpoint":raw["relations"][2]["right_candidate_id"]=first["left_candidate_id"]
    elif poison=="fake_teacher":first["teacher_approved"]=True
    elif poison=="fake_math_cert":first["math_equivalence_certified"]=True
    elif poison=="fake_student_release":first["student_publishable"]=True
    elif poison=="invented_atom":first["final_atom_id"]="OFFICIAL-MATH-0001"
    elif poison=="missing_record":raw["relations"].pop()
    elif poison=="extra_record":raw["relations"].append(deepcopy(first))
    elif poison=="invalid_source_fingerprint":
        hist["provisional_candidate_backlog"][0]["source_line_sha256"]="xxx"
        # target actual first source for tampering; no checksum must be forged
        target=first["left_candidate_id"]
        next(r for r in hist["provisional_candidate_backlog"]
             if r["candidate_id"]==target)["source_line_sha256"]="000"
    elif poison=="fabricated_prior_denominator":old["official_curriculum_atom_denominator"]=300
    elif poison=="fabricated_prior_approval":old["teacher_approved"]=1
    with pytest.raises((ValueError, KeyError)):
        B.build(raw=raw, earlier=old, historical=hist)


def test_no_trusting_unapproved_relation_for_student_explanation():
    with pytest.raises(EditorOnlyError):
        editor_draft_search("向量数乘与共线",scope="")
    # Existing fully-structured editor-only drafts stay guarded too.
    result=student_evidence_lookup("正弦型函数基本周期的非退化条件")
    assert result["teacher_solution_exposed"] is False
    assert result["unverified_content_exposed"] is False


def test_generated_artifacts_are_frozen_and_in_sync(scope):
    assert B.OUT.read_text(encoding="utf-8")==B.dump(scope)
    assert B.DOC.read_text(encoding="utf-8")==B.markdown(scope)
    doc=json.loads(B.OUT.read_text(encoding="utf-8"))
    assert doc["teacher_approved"]==0
    assert doc["official_curriculum_atom_denominator"] is None
