"""Batch81 true P0 census, K00 review queues, 12 exact condition guards and no teacher-solution leak."""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from itertools import product
from pathlib import Path
import json
import sys
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch81_risk_census as CENSUS
import build_kb_batch81_twelve_cards as CARDS
from app.kb_batch81_math import OPERATIONS, check as math_check

@pytest.fixture(scope="module")
def census():
    return CENSUS.build()

@pytest.fixture(scope="module")
def cards():
    return CARDS.build()

def test_three_generated_evidence_documents_are_reproducible(census):
    proof,anchor=census
    assert CENSUS.OUT.read_text()==CENSUS.dump(proof)
    assert CENSUS.OUT_ANCHORS.read_text()==CENSUS.dump(anchor)
    assert CENSUS.OUT_MD.read_text()==CENSUS.markdown(proof,anchor)

def test_twelve_card_generation_is_reproducible(cards):
    assert CARDS.OUT.read_text()==CARDS.dump(cards)
    assert CARDS.MD.read_text()==CARDS.markdown(cards)

def test_complete_p0_census_not_guard_subclass_only(census):
    proof,anchors=census
    assert proof["historical_proof_denominator"]==538
    assert sum(x["total"] for x in proof["by_risk"].values())==538
    assert proof["all_p0_steps"]==182
    assert sum(v["total"] for k,v in proof["by_risk"].items() if k.startswith("P0_"))==182
    assert proof["guard_subclass_p0_steps"]==127
    assert proof["other_p0_steps"]==55
    assert proof["linked_teacher_drafts"]==48
    assert proof["all_p0_unlinked"]==134
    assert proof["guard_subclass_p0_unlinked"]==79
    assert proof["prior_batch80_all_p0_unlinked"]==146
    assert proof["unresolved_conflicts"]==10
    assert proof["teacher_approved"]==proof["formally_certified"]==0
    assert anchors["curriculum_official_denominator"] is None
    assert anchors["full_page_teacher_reviews"]==anchors["student_published"]==0
    assert anchors["by_track"]["ELECTIVE_E"]==0

@pytest.mark.parametrize("idx",range(428))
def test_428_anchor_routing_preserves_exact_coordinates_without_promotion(idx,census):
    _,scope=census
    source=json.loads(CENSUS.ANCHORS.read_text())["anchor_review_queue"][idx]
    row=scope["candidate_work_items"][idx]
    assert row["review_id"]==source["review_id"]
    assert row["source_line_sha256"]==source["source_line_sha256"]
    assert row["track"]==source["track"]
    assert row["parent_segment"]==source["parent_segment"]
    assert row["review_lane"]==CENSUS.KINDS[row["kind"]]
    assert row["semantic_role"]=="NOT_YET_EVIDENCE_ADJUDICATED"
    assert row["deduplicated_official_atom_count"] is None
    assert row["human_approved"] is row["student_publishable"] is False

@pytest.mark.parametrize("idx",range(182))
def test_all_p0_step_id_sha_and_review_status_conserved(idx,census):
    proof,_=census
    row=proof["p0_review_queue"][idx]
    origin=next(r for r in json.loads(CENSUS.PROOFS.read_text())["step_review_queue"] if r["id"]==row["id"])
    assert row["risk_priority"]==origin["risk_priority"]
    assert row["historical_step_sha256"]==origin["source_sha256"]
    assert row["risk_priority"].startswith("P0_")
    assert row["teacher_approved"] is row["formal_math_verification"] is row["student_publishable"] is False
    if row["conflict_id"] is not None:
        assert row["next_action"]=="INDEPENDENT_CONFLICT_ADJUDICATION"
    elif row["review_card_id"] is not None:
        assert row["next_action"]=="TEACHER_REVIEW_OF_EXISTING_DRAFT"
    else:
        assert row["next_action"]=="DRAFT_CONDITION_GUARD_AND_COUNTEREXAMPLE"

@pytest.mark.parametrize("idx",range(12))
def test_each_new_review_card_has_source_sha_and_requires_teacher(cards,idx,census):
    c=cards["review_cards"][idx]
    proof,_=census
    matching=[q for q in proof["p0_review_queue"] if q["id"]==c["linked_historical_step_id"]]
    assert len(matching)==1
    assert matching[0]["review_card_id"]==c["id"]
    assert matching[0]["historical_step_sha256"]==c["original_step_sha256"]
    assert c["review_status"]=="REVIEW_PENDING"
    assert c["formal_math_certification"]=="NOT_FORMALLY_VERIFIED"
    assert c["finite_instance_check"]=="EXACT_WITNESS_NOT_GENERAL_THEOREM_PROOF"
    assert c["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert c["student_publishable"] is c["student_free_text_verified"] is False
    assert c["reviewer_id"] is None
    assert c["official_curriculum_atom_id"] is None
    assert len(c["proof_steps"])==3 and len(c["hints"])==3
    assert len(c["worked_examples"])==2
    assert all(x["visibility"]=="TEACHER_ONLY" for x in c["worked_examples"])

@pytest.mark.parametrize("idx",range(12))
def test_exact_positive_and_negative_math_cases(idx,cards):
    c=cards["review_cards"][idx]
    good,ev=math_check(c["finite_op"],c["valid"])
    bad,why=math_check(c["finite_op"],c["invalid"])
    assert good=="FINITE_EXACT_WITNESS_ONLY" and ev
    assert bad=="CONDITIONS_NOT_ESTABLISHED" and why["reason"]

@pytest.mark.parametrize("idx",range(12))
@pytest.mark.parametrize("mutation",("missing_proof","missing_assumption","missing_solution",
 "replace_good_with_bad","replace_bad_with_good","forge_source","double_source","release_marker"))
def test_tampered_12_card_authoring_fails_closed(idx,mutation):
    data=json.loads(CARDS.AUTHOR.read_text())
    item=data["cards"][idx]
    if mutation=="missing_proof":item["proof_steps"].pop()
    elif mutation=="missing_assumption":item["assumptions"]=[]
    elif mutation=="missing_solution":item["worked_examples"][0]["teacher_solution"]=""
    elif mutation=="replace_good_with_bad":item["valid"]=deepcopy(item["invalid"])
    elif mutation=="replace_bad_with_good":item["invalid"]=deepcopy(item["valid"])
    elif mutation=="forge_source":item["source_step"]="math.hs.nonexistent#1"
    elif mutation=="double_source":item["source_step"]=data["cards"][1 if idx==0 else 0]["source_step"]
    else:item["kind"]="APPROVED_WITHOUT_REVIEW"
    with pytest.raises((ValueError,KeyError)):
        CARDS.build(author=data)

@pytest.mark.parametrize("op",OPERATIONS)
@pytest.mark.parametrize("bad",(True,False,1.5,"2",None))
def test_inexact_or_bool_values_never_become_verified_numeric_examples(op,bad,cards):
    item=next(x for x in cards["review_cards"] if x["finite_op"]==op)
    witness=deepcopy(item["valid"])
    first=next(iter(witness))
    val=witness[first]
    if isinstance(val,list) and val:val[0]=bad
    else:witness[first]=bad
    status,_=math_check(op,witness)
    assert status=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("idx",range(12))
def test_each_finite_guard_rejects_missing_parameter(idx,cards):
    c=cards["review_cards"][idx]
    instance=deepcopy(c["valid"])
    del instance[next(iter(instance))]
    st,_=math_check(c["finite_op"],instance)
    assert st=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("op",OPERATIONS)
def test_zero_denominator_exact_rational_input_is_rejected(op,cards):
    case=deepcopy(next(x["valid"] for x in cards["review_cards"] if x["finite_op"]==op))
    key=next(iter(case))
    if isinstance(case[key],list) and case[key]:case[key][0]={"num":1,"den":0}
    else:case[key]={"num":1,"den":0}
    assert math_check(op,case)[0]=="CONDITIONS_NOT_ESTABLISHED"

def test_parent_teacher_draft_cannot_be_promoted_by_census():
    p,a=CENSUS.get_inputs()
    q=deepcopy(p);q["step_review_queue"][0]["formal_certification"]="FORMALLY_VERIFIED"
    # Even non-P0 steps must be fail-closed on forged certification.
    with pytest.raises(ValueError):
        CENSUS.build(proofs=q,anchors=a)
    other=deepcopy(a);other["anchor_review_queue"][0]["status"]="APPROVED"
    with pytest.raises(ValueError):
        CENSUS.build(proofs=p,anchors=other)

def test_generated_card_approval_forgery_rejected():
    p,a=CENSUS.get_inputs()
    x=json.loads(CARDS.OUT.read_text())
    x["review_cards"][0]["student_publishable"]=True
    with pytest.raises(ValueError,match="Unauthorized"):
        CENSUS.build(proofs=p,anchors=a,newcards=x)

def test_student_evidence_lookup_cannot_leak_any_of_twelve(cards,offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    for c in cards["review_cards"]:
        response=student_evidence_lookup(c["title"])
        serialized=json.dumps(response,ensure_ascii=False)
        assert {v["knowledge_id"] for v in response["candidates"]}<={doc.id}
        assert c["id"] not in serialized
        assert all(e["teacher_solution"] not in serialized for e in c["worked_examples"])
        assert response["teacher_solution_exposed"] is False
        assert response["unverified_content_exposed"] is False

from test_attested_release_batch08 import offline_reviewer_fixture
