"""Batch45 independently executable source/schema/finite math/Tutor negative regression."""
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from math import comb

import pytest
from pydantic import ValidationError
from sympy import cos, sin, pi

from app.kb_batch42_coverage import GateError, Row, TRACKS
from app.kb_batch44_review import coverage_overlay as previous_overlay
from app.kb_batch45_review import (
    SOURCE,SOURCE_SHA,AUDIT,MANUSCRIPT,COVERAGE,GAPS,OPS,
    staged,validate,audit,coverage_overlay,generate,student_retrieval_projection,
)
from app.kb_batch45_exact import KEYS,VALID,INVALID,EXPECTED,witness

DRAFTS=staged()
LEDGER=coverage_overlay()
TEXT=MANUSCRIPT.read_text(encoding="utf-8")

def records():
    return [json.loads(s) for s in SOURCE.read_text(encoding="utf-8").splitlines() if s.strip()]
def encode(rows):
    return "".join(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n" for r in rows)

def test_source_pin_and_generated_evidence_are_reproducible():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    generate(check=True)
    assert len(DRAFTS)==len(OPS)==len(KEYS)==len(VALID)==len(INVALID)==len(EXPECTED)==24
    assert len({eid for eid,_,_ in DRAFTS})==24
    assert all(p.is_file() and p.stat().st_size>200 for p in (AUDIT,MANUSCRIPT,COVERAGE,GAPS))

def test_project_candidate_counts_are_not_official_denominators():
    prev=previous_overlay()["summary"]
    assert prev["direct_review_drafts"]==177
    assert prev["missing_editorial_link"]==124
    assert LEDGER["summary"]==dict(project_candidates=313,direct_review_drafts=201,
        legacy_only=12,missing_editorial_link=100,batch45_new=24,
        teacher_approved=0,student_published=0,official_atom_denominator=None)
    assert len(LEDGER["rows"])==313
    assert sum(r["batch45_new_teacher_review_draft"] for r in LEDGER["rows"])==24
    assert [LEDGER["tracks"][x]["missing_direct_editorial_link"] for x in TRACKS]==[34,66,0,0,0,0,0]
    assert [LEDGER["tracks"][x]["with_direct_review_draft"] for x in TRACKS]==[91,26,22,27,17,15,3]
    assert all(LEDGER["tracks"][x]["official_atom_denominator"] is None and
        LEDGER["tracks"][x]["official_verified_coverage"] is None for x in TRACKS)

@pytest.mark.parametrize("i",range(313))
def test_source_lineage_and_full_unapproved_ledger(i):
    r=LEDGER["rows"][i]
    clean={k:v for k,v in r.items() if k not in
           ("batch43_new_teacher_review_draft","batch44_new_teacher_review_draft",
            "batch45_new_teacher_review_draft")}
    assert Row.model_validate(clean)
    assert not any(r[k] for k in
        ("official_clause_verified","math_certified","teacher_approved","student_published"))
    if r["batch45_new_teacher_review_draft"]:
        assert r["editorial_status"]=="DRAFT_REVIEW_PENDING"
        assert r["direct_review_drafts"]==[f"kb45:{r['editorial_id']}"]
        assert r["track"]=="COMPULSORY"

@pytest.mark.parametrize("i",range(24))
def test_individual_original_lesson_schema_math_boundary_and_visibility(i):
    eid,lesson,src=DRAFTS[i]
    assert eid==audit()["items"][i]["editorial_id"]
    assert src["editorial_status"]=="NO_DIRECT_LINK" and src["track"]=="COMPULSORY"
    assert lesson.goal==src["goal"]
    assert lesson.status=="REVIEW_PENDING" and lesson.source_license=="PROJECT_AUTHORED"
    assert lesson.teacher_solution_visibility=="TEACHER_ONLY"
    assert lesson.student_publishable is False and lesson.approved_reviewer is None
    assert lesson.proof_status=="NOT_FORMALLY_CERTIFIED"
    assert len(lesson.statement)>30 and len(lesson.conditions)>=2
    assert len(lesson.derivation)==3 and len({x.reason for x in lesson.derivation})>=2
    assert len(lesson.examples)==2 and len({x.question for x in lesson.examples})==2
    assert len(lesson.hints)==3 and len(set(lesson.hints))==3
    assert len(lesson.error.counterexample)>=20
    assert len(lesson.error.why_invalid)>=9
    assert len(lesson.near)>=8 and len(lesson.far)>=8 and lesson.prerequisites
    assert lesson.title in TEXT and eid in TEXT
    witness_record=audit()["items"][i]
    assert witness_record["content_sha256"]
    assert witness_record["source_project_sha256"]==src["source_sha256"]
    assert not any(witness_record[k] for k in (
        "teacher_approved","math_certified","student_freeform_step_verified",
        "general_theorem_certified","official_clause_verified","student_publishable"))

@pytest.mark.parametrize("op",sorted(KEYS))
def test_24_bounded_exact_math_witness_and_invalid_premise_cases(op):
    good=witness(op,VALID[op]);bad=witness(op,INVALID[op])
    assert good["status"]=="FINITE_EXACT_CASE_ONLY" and good["exact_value"]==EXPECTED[op]
    assert bad["status"]=="CONDITIONS_NOT_ESTABLISHED" and bad["exact_value"] is None
    for record in (good,bad):
        assert record["general_theorem_certified"] is False
        assert record["student_freeform_step_verified"] is False
        assert record["student_publishable"] is False
        assert record["teacher_approved"] is False

@pytest.mark.parametrize("op",sorted(KEYS))
def test_math_validator_never_accepts_missing_or_unsafe_extra_fields(op):
    sample=copy.deepcopy(VALID[op])
    assert witness(op,{**sample,"student_approved":True})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    first=next(iter(sample))
    assert witness(op,{k:v for k,v in sample.items() if k!=first})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    sample[first]={"__proto__":"forged approval"}
    assert witness(op,sample)["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("bad",["natural_language_proof","eval","sympify","approve","unknown",None,True,42])
def test_freeform_claims_and_unknown_math_operations_are_not_certified(bad):
    result=witness(bad,{"x":"LLM says valid"})
    assert result["status"]=="UNSUPPORTED"
    assert result["general_theorem_certified"] is False

def test_frozen_source_drift_duplicate_orphan_and_existing_lesson_rejected():
    raw=SOURCE.read_text(encoding="utf-8")
    with pytest.raises(GateError):validate(raw+" ",check_pin=True)
    rows=records()
    with pytest.raises(GateError):validate(encode(rows+[copy.deepcopy(rows[0])]),check_pin=False)
    rows=records(); rows[0]["editorial_id"]="NONEXISTENT"
    with pytest.raises(GateError):validate(encode(rows),check_pin=False)
    rows=records(); rows[0]["editorial_id"]="KB31-C-P015-A002"
    with pytest.raises(GateError):validate(encode(rows),check_pin=False)

@pytest.mark.parametrize("field,value",[
    ("status","APPROVED"),("approved_reviewer","Fake Teacher"),
    ("student_publishable",True),("teacher_solution_visibility","STUDENT_VISIBLE"),
    ("proof_status","FORMALLY_CERTIFIED"),("source_license","TEXTBOOK_COPY"),
    ("extra_permission","publish"),("derivation",[]),("examples",[]),("hints",["generic"]*3)
])
def test_forged_review_mathematics_or_student_release_rejected(field,value):
    rows=records();rows[0][field]=value
    with pytest.raises((ValidationError,GateError)):validate(encode(rows),check_pin=False)

def test_exact_trigonometric_oracles_independent_sympy():
    for a,b in itertools.product(range(-360,361,90),repeat=2):
        r=witness("cos_difference",{"alpha":a,"beta":b})
        s=witness("sin_sum",{"alpha":a,"beta":b})
        assert r["status"]=="FINITE_EXACT_CASE_ONLY"
        assert s["status"]=="FINITE_EXACT_CASE_ONLY"
        assert Fraction(r["exact_value"])==int(cos((a-b)*pi/180))
        assert Fraction(s["exact_value"])==int(sin((a+b)*pi/180))
    assert witness("tan_identity",{"angle":90})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness("tan_identity",{"angle":180})["exact_value"]=="1"

def test_zero_brackets_sign_and_nonuniqueness_are_respected():
    assert witness("continuous_sign_bracket",dict(coefficients=[0,-1,0,1],lo=-1,hi=1))["status"]=="CONDITIONS_NOT_ESTABLISHED"
    # The cubic f=x(x²-1) has THREE roots and still satisfies strict opposite endpoint sign.
    yes=witness("continuous_sign_bracket",dict(coefficients=[0,-1,0,1],lo=-2,hi=3))
    assert yes["exact_value"]=="ROOT_EXISTS_UNIQUENESS_UNDETERMINED"
    monotone=witness("continuous_sign_bracket",dict(coefficients=[-1,1],lo=0,hi=2))
    assert monotone["exact_value"]=="ROOT_EXISTS_UNIQUENESS_UNDETERMINED"  # does NOT imply multiple roots
    assert witness("continuous_sign_bracket",dict(coefficients=[1,0,1],lo=-2,hi=3))["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_binary_sample_space_requires_full_cartesian_support_not_only_binary_marginals():
    # Correlated repeated coin outcomes can each be H/T while joint possibilities are only HH and TT.
    failed=witness("sample_space_coins",dict(flips=2,two_outcomes_each=True,all_sequences_possible=False))
    assert failed["status"]=="CONDITIONS_NOT_ESTABLISHED"
    supported=witness("sample_space_coins",dict(flips=2,two_outcomes_each=True,all_sequences_possible=True))
    assert supported["exact_value"]=="4"

def test_bisection_bound_respects_true_sign_bracket_and_exact_shrinkage():
    for n in range(12):
        a=witness("bisection_error",dict(coefficients=[-2,0,1],lo=1,hi=2,steps=n))
        assert a["exact_value"]==str(Fraction(1,2**(n+1)))
    assert witness("bisection_error",dict(coefficients=[2,0,1],lo=1,hi=2,steps=3))["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_vector_basis_and_plane_cross_product_against_independent_formula():
    for a,b,c,d in itertools.product(range(-2,3),repeat=4):
        w=witness("vector_basis",{"u":[a,b],"v":[c,d]})
        det=a*d-b*c
        if det:
            assert int(w["exact_value"])==det
        else:
            assert w["status"]=="CONDITIONS_NOT_ESTABLISHED"
    for x,y in itertools.product(range(-2,3),repeat=2):
        p=[0,0,0];q=[1,0,x];r=[0,1,y]
        v=witness("three_point_plane",dict(a=p,b=q,c=r))
        assert v["status"]=="FINITE_EXACT_CASE_ONLY"
        nx,ny,nz=(int(z) for z in v["exact_value"].split(","))
        assert nx+ nz*x == 0 and ny+nz*y == 0 and nz!=0

def test_complex_division_exact_multiplicative_inverse():
    for ar,ai,br,bi in itertools.product(range(-2,3),repeat=4):
        got=witness("complex_division",dict(ar=ar,ai=ai,br=br,bi=bi))
        if br==bi==0:
            assert got["status"]=="CONDITIONS_NOT_ESTABLISHED"
            continue
        x,y=(Fraction(t) for t in got["exact_value"].split(","))
        assert x*br-y*bi==ar and x*bi+y*br==ai

def test_event_truth_table_and_classical_probability_conditions():
    U=[1,2,3,4]
    for mask1,mask2 in itertools.product(range(16),repeat=2):
        a=[x for idx,x in enumerate(U) if mask1>>idx & 1]
        b=[x for idx,x in enumerate(U) if mask2>>idx & 1]
        w=witness("mutually_exclusive",dict(universe=U,a=a,b=b))
        assert w["exact_value"]==("true" if not set(a)&set(b) else "false")
    for n in range(1,10):
        for k in range(n+1):
            r=witness("classical_probability",dict(outcomes=n,favorable=k,equally_likely=1))
            assert r["exact_value"]==str(Fraction(k,n))
    assert witness("classical_probability",dict(outcomes=6,favorable=3,equally_likely=0))["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_sample_combination_probability_and_strata_integrality():
    for N in range(1,15):
        for n in range(1,N+1):
            v=witness("simple_random_sample",dict(population=N,sample=n,uniform=True))
            assert Fraction(v["exact_value"])*comb(N,n)==1
    assert witness("simple_random_sample",dict(population=4,sample=2,uniform=False))["status"]=="CONDITIONS_NOT_ESTABLISHED"
    for a,b,n in itertools.product(range(1,7),range(1,7),range(1,8)):
        p=dict(first=a,second=b,sample=n)
        w=witness("stratified_proportion",p)
        if n<=a+b and n*a%(a+b)==0:
            x,y=(int(t) for t in w["exact_value"].split(","))
            assert x+y==n and x<=a and y<=b
        else:
            assert w["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_descriptive_variance_translation_and_repeated_constant():
    for a,b in itertools.product(range(-4,5),repeat=2):
        v=witness("descriptive_variance",dict(values=[a,b]))
        expected=Fraction((a-b)**2,4)
        assert v["exact_value"]==f"{abs(a-b)},{expected}"
        shifted=witness("descriptive_variance",dict(values=[a+2,b+2]))
        assert shifted["exact_value"]==v["exact_value"]
    assert witness("descriptive_variance",dict(values=[3,3,3]))["exact_value"]=="0,0"

def test_no_student_evidence_no_teacher_solution_and_actual_adapter_block():
    from app.deep_retrieval import student_evidence_lookup
    from app.model_tutor_draft import draft_next_question
    view=student_retrieval_projection()
    assert view["status"]=="NO_APPROVED_GOAL_EVIDENCE"
    assert view["student_documents"]==view["teacher_solutions_exposed"]==[]
    for eid,u,_ in DRAFTS:
        result=student_evidence_lookup(u.title,limit=3)
        assert result["status"]=="NO_APPROVED_EVIDENCE"
        assert result["candidates"]==[]
        assert result["teacher_solution_exposed"] is False
        request=draft_next_question(u.title,mode="GUIDE",help_requested=True,
            consent_to_cloud=True,operator_scope="EDITOR_LOCAL",
            provider_url="https://api.openai.com/v1/chat/completions",
            provider_model="test-offline-do-not-call")
        assert request.status=="BLOCKED" and request.reason=="NO_APPROVED_MATH_EVIDENCE"
        assert request.model_called is False and request.student_visible is False
        assert request.question_draft is None
