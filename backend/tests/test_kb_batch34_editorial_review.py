"""Batch34 20 original review-only mathematical manuscripts and controlled witnesses."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.kb_batch34_review import (
    SOURCE,PIN,Manuscript,review_only_manuscripts,validate_seed,
    student_retrieval_projection,curriculum_denominator,known_source,
)
from app.kb_batch34_exact_witness import (
    evidence,rejected_bad_conditions,guarded_premise,guarded_fixture_pairs,
)
from app.deep_knowledge import lessons as student_authoritative_corpus

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/"docs/evaluation/KB_BATCH34_EDITORIAL_REVIEW_AUDIT.json"
DOC=ROOT/"docs/evaluation/KB_BATCH34_TWENTY_ORIGINAL_MATH_MANUSCRIPTS.md"
RAW=SOURCE.read_text(encoding="utf-8")
ROWS=[json.loads(x) for x in RAW.splitlines() if x.strip()]
EVIDENCE=evidence()
GUARDS=guarded_fixture_pairs()
MANUSCRIPTS=review_only_manuscripts()

def test_exactly_twenty_original_anchored_and_hash_pinned():
    assert len(MANUSCRIPTS)==20
    assert len(ROWS)==20
    assert len({r["editorial_candidate_id"] for r in ROWS})==20
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==PIN
    assert curriculum_denominator() is None
    audit,crosswalk=known_source()
    assert len(crosswalk["unmatched_candidate_ids"])==49
    assert audit["summary"]["all_provisional_editorial_candidates"]==313
    assert [x["editorial_candidate_id"] for x in ROWS] == [x.editorial_candidate_id for x in MANUSCRIPTS]

@pytest.mark.parametrize("item",MANUSCRIPTS,ids=lambda r:r.editorial_candidate_id)
def test_complete_distinct_math_manuscript_with_locked_human_review(item):
    audit,crosswalk=known_source()
    goal=next(g for g in audit["editorial_goals"] if g["editorial_id"]==item.editorial_candidate_id)
    assert item.editorial_candidate_id in crosswalk["unmatched_candidate_ids"]
    assert goal["official_clause_alignment_verified"] is False
    assert goal["student_publishable"] is False
    assert item.review.status=="REVIEW_PENDING"
    assert item.review.reviewer_id is None and item.review.reviewed_at is None
    assert item.review.review_record is None
    assert item.proof_verification=="NOT_FORMALLY_CERTIFIED"
    assert item.teacher_solution_visibility=="TEACHER_ONLY"
    assert item.student_publishable is False
    assert item.source_license=="PROJECT_AUTHORED"
    assert len(item.reasoning_steps)>=3
    assert len(item.worked_examples)==2
    assert all(len(e.steps)==2 and e.check for e in item.worked_examples)
    assert len(item.counterexample.explanation)>=8
    assert len(item.hint_ladder)==3
    assert item.transfer.near and item.transfer.far
    assert item.kind in {"concept","theorem","method"}

@pytest.mark.parametrize("item",MANUSCRIPTS,ids=lambda r:r.editorial_candidate_id)
def test_no_auto_promotion_to_official_clause_or_student_content(item):
    audit,_=known_source()
    anchor=next(g for g in audit["editorial_goals"] if g["editorial_id"]==item.editorial_candidate_id)
    assert anchor["source_anchor_level"]=="PAGE_SECTION_ONLY_NOT_INDIVIDUAL_CLAUSE_VERIFIED"
    assert anchor["official_atom_id"] is None
    assert not anchor["official_clause_alignment_verified"]
    assert item.id.startswith("math.hs.editorial.batch34.")
    assert "teacher" not in item.review.model_dump(exclude_none=True)

@pytest.mark.parametrize("item",MANUSCRIPTS,ids=lambda r:r.editorial_candidate_id)
def test_all_20_drafts_have_independent_near_far_hints_and_wrong_case(item):
    assert len(set(item.hint_ladder))==3
    assert item.counterexample.false_claim==item.misconception.error
    assert item.counterexample.explanation==item.misconception.why_wrong
    assert item.transfer.near!=item.transfer.far
    assert all(s.claim and s.reason for s in item.reasoning_steps)
    assert item.worked_examples[0].question != item.worked_examples[1].question

@pytest.mark.parametrize("item",MANUSCRIPTS,ids=lambda r:r.editorial_candidate_id)
def test_two_teacher_side_examples_are_not_released(item):
    assert all(x.answer for x in item.worked_examples)
    assert len(item.worked_examples)==2
    assert item.teacher_solution_visibility=="TEACHER_ONLY"
    projection=student_retrieval_projection()
    assert projection["student_solutions"]==[]
    assert projection["student_documents"]==[]

def test_live_287_deep_lessons_remain_unchanged_and_student_projection_empty():
    assert len(student_authoritative_corpus())==287
    assert all(x.review.status=="REVIEW_PENDING" for x in student_authoritative_corpus())
    assert all(x.teacher_solution_visibility=="TEACHER_ONLY" for x in student_authoritative_corpus())
    assert student_retrieval_projection()==dict(
        staged_count=20,publishable_count=0,student_documents=[],
        student_solutions=[],status="NOT_RELEASED")

@pytest.mark.parametrize("key,value",[
    ("teacher_solution_visibility","PUBLIC"),
    ("proof_verification","VERIFIED"),
    ("source_license","COPIED_TEXTBOOK"),
    ("student_publishable",True),
])
def test_unsafe_content_flags_are_rejected_by_schema(key,value):
    row=copy.deepcopy(ROWS[0]);row[key]=value
    with pytest.raises(ValidationError):
        Manuscript.model_validate(row)

@pytest.mark.parametrize("key,value",[
    ("status","APPROVED"),("reviewer_id","fake-teacher"),
    ("reviewed_at","2026-11-08"),("review_record","fabricated-signature"),
])
def test_fabricated_review_data_rejected(key,value):
    row=copy.deepcopy(ROWS[0]);row["review"][key]=value
    with pytest.raises(ValidationError):
        Manuscript.model_validate(row)

@pytest.mark.parametrize("mutation",[
    "duplicate", "missing", "source_wrong", "existing_related", "empty_proof",
    "no_examples", "no_counterexample", "same_hints", "wrong_semantics", "fake_approval",
])
def test_corrupt_or_forged_author_seeds_fail(mutation):
    rows=copy.deepcopy(ROWS)
    if mutation=="duplicate":rows[-1]=copy.deepcopy(rows[0])
    if mutation=="missing":rows.pop()
    if mutation=="source_wrong":rows[0]["editorial_candidate_id"]="KB33-A-P053-A999"
    if mutation=="existing_related":rows[0]["editorial_candidate_id"]="KB33-A-P052-A001"
    if mutation=="empty_proof":rows[0]["reasoning_steps"]=[]
    if mutation=="no_examples":rows[0]["worked_examples"]=[]
    if mutation=="no_counterexample":rows[0]["counterexample"]={}
    if mutation=="same_hints":rows[0]["hint_ladder"]=["检查条件。"]*3
    if mutation=="wrong_semantics":rows[0]["misconception"]["why_wrong"]="错误归因文本完全不一致"
    if mutation=="fake_approval":rows[0]["review"]["status"]="APPROVED"
    text="\n".join(json.dumps(x,ensure_ascii=False) for x in rows)+"\n"
    with pytest.raises((ValueError,ValidationError)):
        validate_seed(text,check_pin=False)

def test_pinned_original_author_content_byte_mutations_are_rejected():
    with pytest.raises(ValueError,match="SHA256"):
        validate_seed(RAW+"\n# Forged extra draft\n")

def test_audit_json_and_human_readable_report_are_reproducible():
    import sys
    sys.path.insert(0,str(ROOT/"scripts"))
    import build_kb_batch34_editorial_review as build
    assert AUDIT.read_text(encoding="utf-8")==build.build()
    assert DOC.read_text(encoding="utf-8")==build.markdown()
    r=json.loads(AUDIT.read_text(encoding="utf-8"))
    s=r["summary"]
    assert s["new_review_manuscripts"]==20
    assert s["remaining_elective_unassociated_candidates"]==29
    assert s["prior_existing_deep_lessons_untouched"]==287
    assert s["finite_instance_checks"]==40
    assert s["topics_still_without_independent_finite_instance_check"]==0
    assert s["teacher_approved_lessons"]==s["student_published_lessons"]==0
    assert s["official_atomic_denominator"] is None
    assert s["official_coverage_rate"] is None
    assert not r["policy"]["teacher_review_registry_unchanged"] is False
    assert r["policy"]["student_agent_index_untouched"]
    assert r["policy"]["student_full_solution_released"] is False

@pytest.mark.parametrize("candidate_id",sorted(EVIDENCE))
def test_each_20_mathematical_topics_has_two_exact_evidence_cases(candidate_id):
    evidence_for=EVIDENCE[candidate_id]
    assert candidate_id in {x.editorial_candidate_id for x in MANUSCRIPTS}
    assert evidence_for["valid_numeric_instances"]==2
    assert evidence_for["invalid_premises_exercised"]==0
    assert evidence_for["check_class"]=="EXACT_BOUNDED_EXAMPLE_NOT_WHOLE_PROOF"
    assert not evidence_for["whole_theorem_formally_certified"]
    assert not evidence_for["teacher_approved"]
    assert not evidence_for["student_answer_automatically_verified"]

@pytest.mark.parametrize("kind",sorted(GUARDS))
def test_eight_exact_domain_guarded_fixtures(kind):
    yes,no=GUARDS[kind]
    assert guarded_premise(kind,yes)=="FINITE_GUARD_PASSED"
    assert guarded_premise(kind,no)=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("kind",sorted(GUARDS))
def test_domain_guards_reject_type_forgery_and_missing_params(kind):
    yes,_=GUARDS[kind]
    bad=copy.deepcopy(yes)
    first=next(iter(bad));bad.pop(first)
    assert guarded_premise(kind,bad)=="CONDITIONS_NOT_ESTABLISHED"
    bad=copy.deepcopy(yes);bad["unexpected"]="forged"
    assert guarded_premise(kind,bad)=="CONDITIONS_NOT_ESTABLISHED"
    bad=copy.deepcopy(yes);bad[next(iter(bad))]=object()
    assert guarded_premise(kind,bad)=="CONDITIONS_NOT_ESTABLISHED"

def test_finite_evidence_does_not_claim_proof_certification():
    assert len(EVIDENCE)==20
    assert sum(x["valid_numeric_instances"] for x in EVIDENCE.values())==40
    assert len(rejected_bad_conditions())==8
    assert guarded_premise("unsupported_llm_judge",{})=="CONDITIONS_NOT_ESTABLISHED"


def test_valid_modus_ponens_example_does_not_assert_false_universal_implication():
    row=next(r for r in ROWS if r["editorial_candidate_id"]=="KB33-C-P065-A002")
    assert all((not (x > 3)) or (x > 0) for x in range(-9, 15))
    assert not all((not (x > 3)) or (x == 4) for x in range(-9, 15))
    assert "x=4" in row["worked_examples"][1]["question"]
    assert "x>3⇒x>0" in row["worked_examples"][1]["question"]
    assert "x>0且x=4" not in row["worked_examples"][1]["question"]


@pytest.mark.parametrize("op", sorted(GUARDS))
def test_exact_premise_guards_do_not_confuse_boolean_with_numeric(op):
    good,_=GUARDS[op]
    keys=[k for k,v in good.items() if type(v) in (int,str) and k not in {"distribution"}]
    for k in keys:
        forged=copy.deepcopy(good)
        forged[k]=True
        assert guarded_premise(op, forged)=="CONDITIONS_NOT_ESTABLISHED"


@pytest.mark.parametrize("op", sorted(GUARDS))
def test_exact_premise_guards_bound_input_size_and_type(op):
    good,_=GUARDS[op]
    keys=[k for k,v in good.items() if type(v) in (int,str) and k not in {"distribution"}]
    for key in keys:
        for invalid in ("9"*90, 10**20, "not_a_number"):
            forged=copy.deepcopy(good)
            forged[key]=invalid
            assert guarded_premise(op,forged)=="CONDITIONS_NOT_ESTABLISHED"
    for k in ("defined","theta2_is_relative"):
        if k in good:
            forged=copy.deepcopy(good)
            forged[k]=1
            assert guarded_premise(op,forged)=="CONDITIONS_NOT_ESTABLISHED"


def test_classical_modus_ponens_complete_truth_table_and_invalid_converse():
    values=[(p,q) for p in (False,True) for q in (False,True)]
    assert all(not ((((not p) or q) and p)) or q for p,q in values)
    # Q true does NOT force P true even if P=>Q.
    assert any((not p) and q and ((not p) or q) for p,q in values)


@pytest.mark.parametrize("bad_num", ["1/0", "0/0", "12/0", "inf"])
def test_fraction_guard_validates_numerator_as_well_as_denominator(bad_num):
    assert guarded_premise("fraction", {"num":bad_num,"den":2})=="CONDITIONS_NOT_ESTABLISHED"
    assert guarded_premise("fraction", {"num":1,"den":2})=="FINITE_GUARD_PASSED"
