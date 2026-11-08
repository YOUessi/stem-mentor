"""Batch46 strictly independent selective-math content, source and safety regression."""
from __future__ import annotations
import copy
import hashlib
import itertools
import json
from fractions import Fraction

import pytest
from pydantic import ValidationError

from app.kb_batch42_coverage import GateError,Row,TRACKS
from app.kb_batch45_review import coverage_overlay as previous_overlay
from app.kb_batch46_review import (
    SOURCE,SOURCE_SHA,AUDIT,MANUSCRIPT,COVERAGE,GAPS,
    staged,validate,audit,coverage_overlay,generate,student_retrieval_projection,
)
from app.kb_batch46_exact import OPS,SAMPLES,witness,calculate

DRAFTS=staged()
LEDGER=coverage_overlay()
def records():
    return [json.loads(s) for s in SOURCE.read_text(encoding="utf-8").splitlines() if s.strip()]
def encode(rows):
    return "".join(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n" for r in rows)

def test_pinned_source_schema_and_generated_evidence():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    generate(check=True)
    assert len(DRAFTS)==len(OPS)==len(SAMPLES)==20
    assert len({eid for eid,_,_ in DRAFTS})==20
    assert all(p.is_file() and p.stat().st_size>100 for p in (AUDIT,MANUSCRIPT,COVERAGE,GAPS))

def test_project_editorial_counts_never_masquerade_as_official_denominator():
    before=previous_overlay()["summary"]
    assert before["direct_review_drafts"]==201 and before["missing_editorial_link"]==100
    assert LEDGER["summary"]==dict(project_candidates=313,direct_review_drafts=221,
        legacy_only=12,missing_editorial_link=80,batch46_new=20,
        teacher_approved=0,student_published=0,official_atom_denominator=None)
    assert len(LEDGER["rows"])==313
    assert [LEDGER["tracks"][t]["missing_direct_editorial_link"] for t in TRACKS]==[34,46,0,0,0,0,0]
    assert [LEDGER["tracks"][t]["with_direct_review_draft"] for t in TRACKS]==[91,46,22,27,17,15,3]
    for track in TRACKS:
        assert LEDGER["tracks"][track]["official_atom_denominator"] is None
        assert LEDGER["tracks"][track]["official_verified_coverage"] is None

@pytest.mark.parametrize("i",range(313))
def test_each_candidate_frozen_lineage_and_unapproved_status(i):
    row=LEDGER["rows"][i]
    clean={k:v for k,v in row.items() if k not in (
        "batch43_new_teacher_review_draft","batch44_new_teacher_review_draft",
        "batch45_new_teacher_review_draft","batch46_new_teacher_review_draft")}
    assert Row.model_validate(clean)
    assert not any(row.get(k) for k in (
        "official_clause_verified","math_certified","teacher_approved","student_published"))
    if row["batch46_new_teacher_review_draft"]:
        assert row["track"]=="SELECTIVE_COMPULSORY"
        assert row["editorial_status"]=="DRAFT_REVIEW_PENDING"
        assert row["direct_review_drafts"]==["kb46:"+row["editorial_id"]]

@pytest.mark.parametrize("i",range(20))
def test_each_full_original_lesson_and_typed_safety(i):
    eid,lesson,src=DRAFTS[i]
    assert eid==audit()["items"][i]["editorial_id"]
    assert src["track"]=="SELECTIVE_COMPULSORY" and src["editorial_status"]=="NO_DIRECT_LINK"
    assert lesson.goal==src["goal"]
    assert lesson.status=="REVIEW_PENDING" and lesson.teacher_solution_visibility=="TEACHER_ONLY"
    assert lesson.source_license=="PROJECT_AUTHORED"
    assert lesson.proof_status=="NOT_FORMALLY_CERTIFIED"
    assert not lesson.student_publishable and lesson.approved_reviewer is None
    assert len(lesson.derivation)==3 and len(set(x.statement for x in lesson.derivation))==3
    assert len(lesson.examples)==2 and len(set(x.question for x in lesson.examples))==2
    assert len(lesson.hints)==3 and len(set(lesson.hints))==3
    assert len(lesson.conditions)>=2 and len(lesson.prerequisites)>=2
    assert len(lesson.error.counterexample)>20
    assert eid in MANUSCRIPT.read_text(encoding="utf-8")
    item=audit()["items"][i]
    assert item["content_sha256"] and item["source_sha256"]==src["source_sha256"]
    assert not any(item[k] for k in ("official_clause_certified","formal_proof_certified",
        "teacher_approved","student_published","student_freeform_step_verified"))

@pytest.mark.parametrize("op",OPS)
def test_each_exact_math_op_and_counterexample(op):
    valid,expected,invalid=SAMPLES[op]
    v=witness(op,valid);bad=witness(op,invalid)
    assert v["status"]=="FINITE_EXACT_CASE_ONLY"
    assert v["exact_value"]==expected
    assert bad["status"]=="CONDITIONS_NOT_ESTABLISHED" and bad["exact_value"] is None
    for r in (v,bad):
        assert r["general_theorem_certified"] is False
        assert r["student_freeform_step_verified"] is False
        assert r["student_publishable"] is False
        assert r["teacher_approved"] is False

@pytest.mark.parametrize("op",OPS)
def test_math_op_rejects_extra_missing_wrong_type(op):
    good=copy.deepcopy(SAMPLES[op][0])
    assert witness(op,{**good,"approved":True})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    first=next(iter(good))
    assert witness(op,{k:v for k,v in good.items() if k!=first})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    good[first]={"__proto__":"override"}
    assert witness(op,good)["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("untrusted",["eval","sympify","freeform-proof","APPROVE",None,123,[],{},True])
def test_unsupported_formula_or_student_freeform_never_certified(untrusted):
    assert witness(untrusted,{"proof":"LLM asserts valid"})["status"]=="UNSUPPORTED"

def test_duplicate_drift_existing_id_cross_track_and_orphan_blocked():
    raw=SOURCE.read_text(encoding="utf-8")
    with pytest.raises(GateError):validate(raw+" ",check_pin=True)
    r=records()
    with pytest.raises(GateError):validate(encode(r+[copy.deepcopy(r[0])]),check_pin=False)
    for bad_id in ("DOES-NOT-EXIST","KB31-C-P015-A001","KB32-S-P038-A001"):
        r=records();r[0]["editorial_id"]=bad_id
        with pytest.raises(GateError):validate(encode(r),check_pin=False)

@pytest.mark.parametrize("field,value",[
    ("status","APPROVED"),("approved_reviewer","Synthetic Teacher"),
    ("student_publishable",True),("teacher_solution_visibility","PUBLIC"),
    ("proof_status","FORMALLY_CERTIFIED"),("source_license","UNLICENSED_TEXTBOOK"),
    ("unknown_permission","leak"),("conditions",[]),("derivation",[]),
    ("examples",[]),("hints",["same"]*3)
])
def test_forged_reviewer_proof_or_published_status_rejected(field,value):
    r=records();r[0][field]=value
    with pytest.raises((GateError,ValidationError)):validate(encode(r),check_pin=False)

def test_independent_polynomial_derivatives_and_affine_chain_against_sympy():
    from sympy import Symbol,diff,expand
    x=Symbol("x")
    for a,b,c in itertools.product(range(-3,4),repeat=3):
        for at in (-2,-1,0,1,2):
            p={"coeffs":[a,b,c],"x0":at}
            res=witness("polynomial_derivative_limit",p)
            assert res["exact_value"]==str(diff(a+b*x+c*x*x,x).subs(x,at))
            t=witness("polynomial_product_derivative",{"f":[a,b,c],"g":[2,1],"x0":at})
            assert t["exact_value"]==str(diff((a+b*x+c*x*x)*(2+x),x).subs(x,at))
    for a in range(-3,4):
        for p in range(1,6):
            res=witness("affine_power_chain",{"a":a,"b":2,"power":p,"x0":1})
            assert res["exact_value"]==str(diff((a*x+2)**p,x).subs(x,1))

def test_exact_progressions_and_math_degeneracies():
    for a1 in range(-5,6):
        for q in (-3,-2,-1,0,1,2,3):
            for n in range(1,8):
                got=witness("geometric_n",{"a1":a1,"q":q,"n":n})
                assert got["exact_value"]==str(a1*q**(n-1))
    assert witness("positive_exponential_sample",{"a1":3,"q":0,"n":4})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness("arithmetic_n",{"a1":5,"d":0,"n":6})["exact_value"]=="5"

def test_projection_residual_exact_orthogonal_and_nonzero_condition():
    for u in itertools.product(range(-2,3),repeat=3):
        for v in ((1,0,0),(1,1,0),(2,-1,1),(0,0,-2)):
            got=witness("vector_projection",{"u":list(u),"v":list(v)})
            assert got["status"]=="FINITE_EXACT_CASE_ONLY"
            projected=[Fraction(z) for z in got["exact_value"].split(",")]
            assert sum((Fraction(u[i])-projected[i])*v[i] for i in range(3))==0
    assert witness("vector_projection",{"u":[1,1,1],"v":[0,0,0]})["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_plane_direction_classification_and_degenerate_vectors():
    assert witness("line_plane_class",{"p":[0,0,0],"d":[1,0,0],"n":[0,0,1],"offset":0})["exact_value"]=="CONTAINED"
    assert witness("line_plane_class",{"p":[0,0,1],"d":[0,0,1],"n":[0,0,1],"offset":0})["exact_value"]=="INTERSECT_ONE_POINT"
    assert witness("line_plane_class",{"p":[0,0,1],"d":[1,0,0],"n":[0,0,1],"offset":0})["exact_value"]=="PARALLEL_DISTINCT"
    assert witness("line_direction_span",{"d":[0,0,0],"scale":1})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness("orthogonality_3d",{"u":[0,0,0],"v":[1,0,0]})["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_real_tutor_refuses_unapproved_evidence_without_model_call():
    from app.deep_retrieval import student_evidence_lookup
    from app.model_tutor_draft import draft_next_question
    assert student_retrieval_projection()["student_documents"]==[]
    for _,unit,_ in DRAFTS:
        evidence=student_evidence_lookup(unit.title,limit=3)
        assert evidence["status"]=="NO_APPROVED_EVIDENCE"
        assert evidence["candidates"]==[]
        assert evidence["teacher_solution_exposed"] is False
        result=draft_next_question(unit.title,mode="GUIDE",help_requested=True,
            consent_to_cloud=True,operator_scope="EDITOR_LOCAL",
            provider_url="https://api.openai.com/v1/chat/completions",
            provider_model="test-offline-do-not-call")
        assert result.status=="BLOCKED" and result.reason=="NO_APPROVED_MATH_EVIDENCE"
        assert not result.model_called and not result.student_visible and result.question_draft is None
