"""Batch35 provenance, mathematical exact fixtures, unapproved teacher-only manuscripts."""
from __future__ import annotations
import copy,hashlib,json,subprocess,sys
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.kb_batch35_review import (SOURCE,PIN,Manuscript35,review_only_manuscripts35,
    validate_seed,expected_candidates,student_retrieval_projection,official_denominators,known_source)
from app.kb_batch34_review import review_only_manuscripts
from app.kb_batch35_exact_witness import finite_evidence,guard,guard_pairs
from app.deep_knowledge import lessons as original_deep_lessons
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"docs/evaluation/KB_BATCH35_EDITORIAL_COVERAGE_AUDIT.json"
MD=ROOT/"docs/evaluation/KB_BATCH35_REMAINING_29_ELECTIVE_MANUSCRIPTS.md"
RAW=SOURCE.read_text(encoding="utf-8")
ROWS=[json.loads(l) for l in RAW.splitlines() if l.strip()]
DOCS=review_only_manuscripts35()
EVIDENCE=finite_evidence()
GUARDS=guard_pairs()
@pytest.mark.parametrize("doc",DOCS,ids=lambda d:d.editorial_candidate_id)
def test_each_editorial_goal_has_complete_unapproved_math_manuscript(doc):
    assert doc.review.status=="REVIEW_PENDING"
    assert doc.review.reviewer_id is None and doc.review.reviewed_at is None
    assert doc.review.review_record is None
    assert doc.proof_verification=="NOT_FORMALLY_CERTIFIED"
    assert doc.teacher_solution_visibility=="TEACHER_ONLY"
    assert doc.student_publishable is False
    assert doc.source_license=="PROJECT_AUTHORED"
    assert len(doc.reasoning_steps)==3
    assert len(doc.worked_examples)==2
    assert len(doc.hint_ladder)==len(set(doc.hint_ladder))==3
    assert doc.transfer.near!=doc.transfer.far
    assert doc.counterexample.false_claim==doc.misconception.error
    assert doc.counterexample.explanation==doc.misconception.why_wrong
@pytest.mark.parametrize("doc",DOCS,ids=lambda d:d.editorial_candidate_id)
def test_each_candidate_is_exact_previous_page_level_gap_and_not_official_clause(doc):
    audit,cross=known_source()
    goal=next(g for g in audit["editorial_goals"] if g["editorial_id"]==doc.editorial_candidate_id)
    assert doc.editorial_candidate_id in cross["unmatched_candidate_ids"]
    assert goal["official_atom_id"] is None
    assert not goal["official_clause_alignment_verified"]
    assert goal["source_anchor_level"]=="PAGE_SECTION_ONLY_NOT_INDIVIDUAL_CLAUSE_VERIFIED"
    assert goal["teacher_review"]=="PENDING"
@pytest.mark.parametrize("doc",DOCS,ids=lambda d:d.editorial_candidate_id)
def test_each_example_stays_teacher_side_with_specific_checks(doc):
    assert len({e.question for e in doc.worked_examples})==2
    assert all(len(e.steps)==2 and e.check for e in doc.worked_examples)
    assert all(e.answer for e in doc.worked_examples)
    assert not doc.student_publishable
@pytest.mark.parametrize("doc",DOCS,ids=lambda d:d.editorial_candidate_id)
def test_exact_math_fixtures_are_bounded_only_for_audited_topics(doc):
    evidence=EVIDENCE[doc.editorial_candidate_id]
    assert evidence["finite_examples"]==2
    assert evidence["status"]=="EXACT_BOUNDED_NUMERIC_CASES_ONLY"
    assert not evidence["universal_theorem_certified"]
    assert not evidence["teacher_approved"]
    assert not evidence["student_step_verified"]
    assert not evidence["causal_historical_or_empirical_interpretation_verified"]
@pytest.mark.parametrize("unsafe,value",[
    ("student_publishable",True),("teacher_solution_visibility","PUBLIC"),
    ("source_license","COPYRIGHTED_TEXTBOOK"),("proof_verification","VERIFIED"),
])
@pytest.mark.parametrize("row",ROWS,ids=lambda r:r["editorial_candidate_id"])
def test_fake_approval_or_student_release_fails_per_topic(row,unsafe,value):
    r=copy.deepcopy(row);r[unsafe]=value
    with pytest.raises(ValidationError):Manuscript35.model_validate(r)
@pytest.mark.parametrize("mutation",[
    "duplicate","missing","wrong_id","outside_goal","fake_approval",
    "fake_reviewer","no_proof","no_counterexample","no_exercises","missing_hint",
    "different_error_reason","same_questions","student_publish",
])
def test_bad_batch_seed_fails_closed(mutation):
    rows=copy.deepcopy(ROWS)
    if mutation=="duplicate":rows[-1]=rows[0]
    elif mutation=="missing":rows.pop()
    elif mutation=="wrong_id":rows[0]["id"]="math.hs.editorial.batch34.kb33.a.p054.a001"
    elif mutation=="outside_goal":rows[0]["editorial_candidate_id"]="KB33-A-P054-A999"
    elif mutation=="fake_approval":rows[0]["review"]["status"]="APPROVED"
    elif mutation=="fake_reviewer":rows[0]["review"]["reviewer_id"]="not-a-teacher"
    elif mutation=="no_proof":rows[0]["reasoning_steps"]=[]
    elif mutation=="no_counterexample":rows[0]["counterexample"]={}
    elif mutation=="no_exercises":rows[0]["worked_examples"]=[]
    elif mutation=="missing_hint":rows[0]["hint_ladder"].pop()
    elif mutation=="different_error_reason":rows[0]["misconception"]["why_wrong"]="捏造原因与反例不匹配"
    elif mutation=="same_questions":rows[0]["worked_examples"][1]["question"]=rows[0]["worked_examples"][0]["question"]
    elif mutation=="student_publish":rows[0]["student_publishable"]=True
    raw="\n".join(json.dumps(x,ensure_ascii=False) for x in rows)+"\n"
    with pytest.raises((ValidationError,ValueError)):
        validate_seed(raw,check_pin=False)
@pytest.mark.parametrize("op",sorted(GUARDS))
def test_guard_rejects_invalid_condition_and_accepts_valid_control(op):
    yes,no=GUARDS[op]
    assert guard(op,yes)=="FINITE_PREMISE_GUARDED"
    assert guard(op,no)=="CONDITIONS_NOT_ESTABLISHED"
@pytest.mark.parametrize("op",sorted(GUARDS))
def test_guard_rejects_missing_extra_boolean_and_poisoned_values(op):
    good,_=GUARDS[op]
    for key in good:
        candidate=copy.deepcopy(good)
        candidate.pop(key)
        assert guard(op,candidate)=="CONDITIONS_NOT_ESTABLISHED"
        candidate=copy.deepcopy(good)
        candidate[key]=object()
        assert guard(op,candidate)=="CONDITIONS_NOT_ESTABLISHED"
        candidate=copy.deepcopy(good)
        candidate[key]=True if type(good[key]) is int else "UNVERIFIED"
        assert guard(op,candidate)=="CONDITIONS_NOT_ESTABLISHED"
    extra=copy.deepcopy(good);extra["unsafe"]=True
    assert guard(op,extra)=="CONDITIONS_NOT_ESTABLISHED"
@pytest.mark.parametrize("op",sorted(GUARDS))
def test_guard_rejects_oversized_input_and_unknown_operator(op):
    good,_=GUARDS[op]
    for key,value in good.items():
        if type(value) is int:
            bad=copy.deepcopy(good);bad[key]=10**100
            assert guard(op,bad)=="CONDITIONS_NOT_ESTABLISHED"
    assert guard(op+"__LLM_VERIFIED",good)=="CONDITIONS_NOT_ESTABLISHED"
def test_29_exact_disjoint_remaining_ids_and_original_drafts_not_mutated():
    assert len(DOCS)==29 and len(set(d.id for d in DOCS))==29
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==PIN
    assert len(review_only_manuscripts())==20
    assert len(expected_candidates())==29
    old={d.editorial_candidate_id for d in review_only_manuscripts()}
    new={d.editorial_candidate_id for d in DOCS}
    _,cross=known_source()
    assert not old&new
    assert old|new==set(cross["unmatched_candidate_ids"])
    assert len(original_deep_lessons())==287
    assert all(d.review.status=="REVIEW_PENDING" for d in original_deep_lessons())
    assert all(x is None for x in official_denominators().values())
    assert student_retrieval_projection()["student_documents"]==[]
    assert student_retrieval_projection()["student_solutions"]==[]
def test_seed_hash_pin_catches_normal_looking_tampering():
    with pytest.raises(ValueError,match="SHA256"):
        validate_seed(RAW.replace("定积分","积分定值",1),check_pin=True)
def test_math_witnesses_and_quality_scope_not_conflated_with_certification():
    assert len(EVIDENCE)==29
    assert sum(x["finite_examples"] for x in EVIDENCE.values())==58
    assert len(GUARDS)==12
    assert not any(x["teacher_approved"] for x in EVIDENCE.values())
def test_source_generator_stable_and_pinned():
    from runpy import run_path
    module=run_path(str(ROOT/"scripts/author_kb_batch35_lessons.py"),run_name="not_main")
    emitted="\n".join(json.dumps(r,ensure_ascii=False,separators=(",",":")) for r in module["build_rows"]())+"\n"
    assert emitted==SOURCE.read_text(encoding="utf-8")
def test_audit_and_human_teacher_draft_markdown_reproducible():
    sys.path.insert(0,str(ROOT/"scripts"))
    import build_kb_batch35_editorial_review as builder
    assert OUT.read_text(encoding="utf-8")==builder.build()
    assert MD.read_text(encoding="utf-8")==builder.markdown()
    s=json.loads(OUT.read_text(encoding="utf-8"))["summary"]
    assert s["formerly_unassociated_now_staged"]==49
    assert s["remaining_without_review_manuscript"]==0
    assert s["old_tentative_links_not_certified"]==47
    assert s["batch35_manuscripts"]==29
    assert s["finite_cases"]==58
    assert s["teacher_approved"]==s["student_published"]==0
    assert all(x is None for x in s["official_denominators"].values())


def test_unknown_guard_operator_empty_payload_is_rejected():
    assert guard("LLM_SAYS_VALID",{})=="CONDITIONS_NOT_ESTABLISHED"
    assert guard("__proto__",{})=="CONDITIONS_NOT_ESTABLISHED"
    assert guard("",{})=="CONDITIONS_NOT_ESTABLISHED"
    assert guard("fraction",{})=="CONDITIONS_NOT_ESTABLISHED"
