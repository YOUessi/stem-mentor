"""Batch66 teacher-side assessment, candidate deduplication and exact finite witness gates."""
import json
import sys
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch66_competency_evidence as B
from app import kb_batch66_competency_witnesses as W

CARDS=B.load(B.TASKS)
M,Q,I,A=B.build()

def test_replay_exact_outputs_and_unknown_denominators():
    assert B.load(B.OUT)==M and B.load(B.DUPS)==Q and B.load(B.INDEX)==I
    assert B.load(B.BACKLOG)==A
    assert B.REPORT.read_text(encoding="utf-8")==B.render(M,Q,I,A)
    assert M["official_atom_denominator"]=={t:None for t in B.TRACKS}
    assert M["source_pages_with_some_leads"]==61
    assert M["heuristic_clause_anchors"]==M["review_backlog_items"]==428
    assert len(A["rows"])==428
    assert M["internal_manuscript_anchor_links"]==31
    assert M["assessment_anchor_links"]==14
    assert M["unreviewed_provisional_atom_hypotheses"]==62
    assert M["internal_scope_manuscripts"]==31
    assert M["source_unnumbered_sections_still_unmapped"]==14
    assert M["independent_assessment_drafts"]==M["finite_exact_witnesses"]==14
    assert M["rubric_total_points"]==84
    assert M["teacher_full_page_reviews"]==M["teacher_approvals"]==M["student_published"]==0
    assert M["math_equivalence_certified_pairs"]==0
    assert all(not row["teacher_approved"] and not row["student_published"] for row in M["rubric_items"])

@pytest.mark.parametrize("index",range(14))
def test_independently_scored_original_assessment_not_official(index):
    card=CARDS[index]
    source=M["rubric_items"][index]
    idx=I["rows"][index]
    assert card["id"]==source["assessment_id"]==idx["id"]
    assert len(card["justification_steps"])==3
    assert len(card["three_stage_hints"])==3
    assert len(card["scoring_rubric"])==3
    assert sum(x["points"] for x in card["scoring_rubric"])==6
    assert card["near_transfer"]!=card["far_transfer"]
    assert card["teacher_expected_answer"]!=card["typical_wrong_answer"]
    assert len(card["counterexample_or_failure_boundary"])>=12
    assert card["teacher_review"]=="REVIEW_PENDING"
    assert card["answer_visibility"]=="TEACHER_ONLY"
    assert source["official_skill_alignment"]=="UNMAPPED"
    assert not idx["student_retrievable"]
    assert "teacher_expected_answer" not in idx

@pytest.mark.parametrize("key",list(W.GOLDEN))
def test_math_witness_independent_golden_per_domain(key):
    assert W.witnesses()[key]==W.GOLDEN[key]

@pytest.mark.parametrize("failure",[
    "fake_approve","publish","student_proof","fake_general_proof","fake_math_cert",
    "fake_section_match","fake_license","wrong_visibility","bad_id",
    "duplicate_id","duplicate_witness","blank_question","blank_solution",
    "delete_step","delete_hint","bad_rubric_points","bad_rubric_criterion",
    "blank_counterexample","blank_failure_boundary","bad_model_assumptions",
])
def test_fail_closed_on_forged_status_or_shallow_work(failure):
    cards=deepcopy(CARDS); r=cards[0]
    if failure=="fake_approve":r["teacher_review"]="APPROVED"
    elif failure=="publish":r["student_publishable"]=True
    elif failure=="student_proof":r["student_answer_verified"]=True
    elif failure=="fake_general_proof":r["general_theorem_certified"]=True
    elif failure=="fake_math_cert":r["math_verification"]="CERTIFIED"
    elif failure=="fake_section_match":r["section_alignment"]="CONFIRMED"
    elif failure=="fake_license":r["source_license"]="UNKNOWN"
    elif failure=="wrong_visibility":r["answer_visibility"]="STUDENT"
    elif failure=="bad_id":r["id"]="WRONG"
    elif failure=="duplicate_id":cards[1]["id"]=r["id"]
    elif failure=="duplicate_witness":cards[1]["witness_key"]=r["witness_key"]
    elif failure=="blank_question":r["question"]=""
    elif failure=="blank_solution":r["teacher_expected_answer"]=""
    elif failure=="delete_step":r["justification_steps"].pop()
    elif failure=="delete_hint":r["three_stage_hints"].pop()
    elif failure=="bad_rubric_points":r["scoring_rubric"][0]["points"]=0
    elif failure=="bad_rubric_criterion":r["scoring_rubric"][0]["criterion"]=""
    elif failure=="blank_counterexample":r["typical_wrong_answer"]=""
    elif failure=="blank_failure_boundary":r["counterexample_or_failure_boundary"]=""
    elif failure=="bad_model_assumptions":r["wrong_reason"]=""
    with pytest.raises((ValueError,KeyError)):
        B.build(cards=cards)

def test_crosspage_dedup_queue_is_risk_review_not_merge():
    assert Q["total_unordered_candidate_pairs"]==1891
    assert Q["same_parent_pairs_excluded"]==31
    assert Q["cross_page_overlap_candidates"]==len(Q["rows"])
    assert Q["math_equivalence_certified"]==0
    assert not Q["auto_merge_permitted"]
    assert all(not x["merge_permitted"] and x["requires_full_clauses"] for x in Q["rows"])
    assert all(x["left_page"]!=x["right_page"] for x in Q["rows"])
    assert not I["student_index_write_permitted"]
    assert not I["contains_teacher_answers"]

@pytest.mark.parametrize("bad", [True,False,1.2,"2",object()])
def test_exact_rejects_untrusted_scalars(bad):
    with pytest.raises(W.UnsafePremise): W.exact(bad)

@pytest.mark.parametrize("bad", [1,F(1),True,1.0])
def test_composed_domain_singularity_and_nonexact_input(bad):
    with pytest.raises(W.UnsafePremise): W.composed_reciprocal(bad)
    assert W.composed_reciprocal(2)==1

def test_implication_direction_and_predicate_type():
    assert W.finite_implication((0,1,3),lambda x:x>2,lambda x:x>0)
    assert not W.finite_implication((0,1,3),lambda x:x>0,lambda x:x>2)
    with pytest.raises(W.UnsafePremise):W.finite_implication((),lambda x:True,lambda x:True)
    with pytest.raises(W.UnsafePremise):W.finite_implication((1,2),lambda x:1,lambda x:True)
    with pytest.raises(W.UnsafePremise):W.finite_implication((1,1.5),lambda x:True,lambda x:True)

def test_weighted_probability_without_unsafe_uniform_assumption():
    assert W.weighted_probability((1,2,3),(F(1,2),F(1,3),F(1,6)),(2,3))==F(1,2)
    for outcomes,weights,event in [
        ((1,2), (1,1), (1,)),
        ((1,2), (F(1,2),F(1,2)), (3,)),
        ((1,1), (F(1,2),F(1,2)), (1,)),
        ((1,2), (True,0), (1,)),
        ((1,2), (F(-1,2),F(3,2)), (1,)),
    ]:
        with pytest.raises(W.UnsafePremise):W.weighted_probability(outcomes,weights,event)

def test_residuals_mean_and_empty_sample_refusal():
    assert W.residuals((0,1,2),(1,3,6),2,1)==[0,0,1]
    assert W.finite_mean((1,2,3,100))==F(53,2)
    with pytest.raises(W.UnsafePremise):W.finite_mean(())
    with pytest.raises(W.UnsafePremise):W.finite_mean((1.1,2))
    with pytest.raises(W.UnsafePremise):W.residuals((1,2),(2,),1,0)
    with pytest.raises(W.UnsafePremise):W.residuals((1,),(2,),True,0)

def test_student_knowledge_store_not_polluted_by_teacher_assessment_ids():
    from app.deep_knowledge import lessons
    ids={x.id for x in lessons()}
    assert set(c["id"] for c in CARDS).isdisjoint(ids)
    assert not any(c["teacher_expected_answer"] in json.dumps(I,ensure_ascii=False) for c in CARDS)

from test_attested_release_batch08 import offline_reviewer_fixture

@pytest.mark.parametrize("card_index",range(14))
def test_approved_mixed_index_does_not_leak_teacher_rubric(card_index,offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    card=CARDS[card_index]
    result=student_evidence_lookup(card["domain"])
    assert {x["knowledge_id"] for x in result["candidates"]}<={doc.id}
    payload=json.dumps(result,ensure_ascii=False)
    assert card["id"] not in payload
    assert card["teacher_expected_answer"] not in payload
    assert not result["teacher_solution_exposed"]
    assert not result["unverified_content_exposed"]


@pytest.mark.parametrize("row_index",range(428))
def test_every_official_source_anchor_is_auditable_but_not_approved(row_index):
    row=A["rows"][row_index]
    assert row["anchor_id"].startswith("KB61-P")
    assert len(row["source_line_sha256"])==64
    assert row["official_atomic_membership"]=="UNDETERMINED"
    assert row["full_source_clause_teacher_review"]=="NOT_DONE"
    assert row["math_equivalence_review"]=="NOT_REVIEWED"
    assert not row["teacher_approved"] and not row["student_published"]
