"""Batch44 independent frozen-source, schema, math premise, coverage and no-spoiler tests."""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
from fractions import Fraction

import pytest
from pydantic import ValidationError

from app.kb_batch42_coverage import GateError, Row, TRACKS
from app.kb_batch43_review import coverage_overlay as previous_overlay
from app.kb_batch44_review import (
    ROOT,SOURCE,SOURCE_SHA,AUDIT,MANUSCRIPT,COVERAGE,GAPS,OPS,
    validate,staged,audit,coverage_overlay,generate,student_retrieval_projection,
)
from app.kb_batch44_exact import KEYS,VALID,INVALID,EXPECTED,witness

DRAFTS=staged()
LEDGER=coverage_overlay()
LESSON_TEXT=MANUSCRIPT.read_text(encoding="utf-8")

def raw_records():
    return [json.loads(x) for x in SOURCE.read_text(encoding="utf-8").splitlines() if x.strip()]

def encode(records):
    return "\n".join(json.dumps(x,ensure_ascii=False) for x in records)+"\n"

def test_all_generated_files_and_source_are_reproducible():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    generate(check=True)
    assert len(DRAFTS)==20==len(OPS)==len(KEYS)
    assert set(OPS)==set(KEYS)==set(VALID)==set(INVALID)==set(EXPECTED)
    assert all(p.is_file() and p.stat().st_size>200 for p in (AUDIT,MANUSCRIPT,COVERAGE,GAPS))
    assert len({r[0] for r in DRAFTS})==20
    assert audit()["summary"]["teacher_approved"]==0

def test_coverage_numbers_and_legacy_not_recertified():
    previous=previous_overlay()
    assert previous["summary"]["direct_review_drafts"]==157
    assert previous["summary"]["missing_editorial_link"]==144
    assert LEDGER["summary"]==dict(project_candidates=313,direct_review_drafts=177,
        legacy_only=12,missing_editorial_link=124,batch44_new=20,
        teacher_approved=0,student_published=0,official_atom_denominator=None)
    assert sum(x["batch44_new_teacher_review_draft"] for x in LEDGER["rows"])==20
    assert set(LEDGER["tracks"])==set(TRACKS)
    assert [LEDGER["tracks"][t]["missing_direct_editorial_link"] for t in TRACKS]==[58,66,0,0,0,0,0]
    assert [LEDGER["tracks"][t]["with_direct_review_draft"] for t in TRACKS]==[67,26,22,27,17,15,3]
    assert all(t["official_atom_denominator"] is None and
               t["official_verified_coverage"] is None and
               t["teacher_approved"]==t["student_published"]==0
               for t in LEDGER["tracks"].values())

@pytest.mark.parametrize("i",range(313))
def test_every_coverage_record_has_immutable_source_and_no_fake_status(i):
    r=LEDGER["rows"][i]
    sanitized={k:v for k,v in r.items()
               if k not in ("batch43_new_teacher_review_draft",
                            "batch44_new_teacher_review_draft")}
    assert Row.model_validate(sanitized)
    assert r["teacher_approved"] is False and r["student_published"] is False
    assert r["math_certified"] is False and r["official_clause_verified"] is False
    if r["batch44_new_teacher_review_draft"]:
        assert r["editorial_status"]=="DRAFT_REVIEW_PENDING"
        assert r["direct_review_drafts"]==[f"kb44:{r['editorial_id']}"]
        assert r["track"]=="COMPULSORY"

@pytest.mark.parametrize("i",range(20))
def test_each_original_lesson_has_own_specific_evidence_and_teacher_gates(i):
    eid,u,src=DRAFTS[i]
    assert u.goal==src["goal"]
    assert src["editorial_status"]=="NO_DIRECT_LINK"
    assert src["track"]=="COMPULSORY"
    assert u.status=="REVIEW_PENDING" and u.student_publishable is False
    assert u.teacher_solution_visibility=="TEACHER_ONLY"
    assert u.proof_status=="NOT_FORMALLY_CERTIFIED"
    assert u.approved_reviewer is None and u.source_license=="PROJECT_AUTHORED"
    assert len(u.conditions)>=1 and len(u.derivation)==3
    assert len({s.reason for s in u.derivation})>=2
    assert len(u.examples)==2 and len({e.question for e in u.examples})==2
    assert len(u.hints)==3 and len(set(u.hints))==3
    assert len(u.error.counterexample)>=12 and len(u.error.why_invalid)>=8
    assert len(u.near)>=6 and len(u.far)>=6
    assert len(u.prerequisites)>=1
    assert eid in LESSON_TEXT and u.title in LESSON_TEXT
    record=audit()["items"][i]
    assert record["lesson_sha256"] and record["official_clause_verified"] is False
    assert record["general_theorem_certified"] is False
    assert record["student_freeform_step_verified"] is False

@pytest.mark.parametrize("op",sorted(KEYS))
def test_each_operator_exact_positive_and_premise_rejection(op):
    result=witness(op,VALID[op])
    assert result["status"]=="FINITE_EXACT_CASE_ONLY"
    assert result["exact_value"]==EXPECTED[op]
    invalid=witness(op,INVALID[op])
    assert invalid["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert invalid["exact_value"] is None
    for actual in (result,invalid):
        assert actual["general_theorem_certified"] is False
        assert actual["student_freeform_step_verified"] is False
        assert actual["teacher_approved"] is False
        assert actual["student_publishable"] is False

@pytest.mark.parametrize("op",sorted(KEYS))
def test_each_operator_rejects_extra_fields_missing_fields_and_mutated_types(op):
    sample=copy.deepcopy(VALID[op])
    assert witness(op,{**sample,"approved":True})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    k=next(iter(sample))
    assert witness(op,{field:val for field,val in sample.items() if field!=k})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    bad=dict(sample)
    bad[k]={"__proto__":"teacher_approved"}
    assert witness(op,bad)["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness(op,[])["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("bad",["open_text","student free-text","evaluate","system:approve",None,42,True])
def test_unknown_or_untrusted_operator_never_returns_verification(bad):
    result=witness(bad,{"x":1})
    assert result["status"]=="UNSUPPORTED"
    assert result["general_theorem_certified"] is False
    assert result["student_publishable"] is False

def test_source_pin_drift_and_duplicate_and_orphan_ids():
    raw=SOURCE.read_text(encoding="utf-8")
    with pytest.raises(GateError):
        validate(raw+" ",check_pin=True)
    entries=raw_records()
    with pytest.raises(GateError):
        validate(encode(entries+[copy.deepcopy(entries[0])]),check_pin=False)
    tampered=copy.deepcopy(entries)
    tampered[0]["editorial_id"]="UNRECOGNIZED"
    with pytest.raises(GateError):
        validate(encode(tampered),check_pin=False)
    tampered=copy.deepcopy(entries)
    tampered[0]["editorial_id"]=DRAFTS[1][0]
    with pytest.raises(GateError):
        validate(encode(tampered),check_pin=False)

@pytest.mark.parametrize("field,val",[
    ("status","APPROVED"),("student_publishable",True),
    ("teacher_solution_visibility","STUDENT_VISIBLE"),
    ("proof_status","FORMALLY_CERTIFIED"),
    ("approved_reviewer","Synthetic Teacher"),
    ("source_license","COPYRIGHTED_TEXTBOOK"),
    ("unexpected_field","forgery"),
])
def test_no_forged_review_publication_or_unsafe_schema(field,val):
    rows=raw_records()
    rows[0][field]=val
    with pytest.raises((ValidationError,GateError)):
        validate(encode(rows),check_pin=False)

def test_no_student_teacher_solution_leakage():
    result=student_retrieval_projection()
    assert result["status"]=="NO_APPROVED_GOAL_EVIDENCE"
    assert result["student_documents"]==[]
    assert result["teacher_solutions_exposed"]==[]
    assert result["teacher_approved"]==result["student_published"]==0
    assert result["official_atom_denominator"] is None

def test_set_builder_matches_independent_comprehension():
    domain=list(range(-10,11))
    for d in (1,2,3,4):
        for t in (-2,0,4):
            expected=",".join(str(x) for x in domain if x>t and x%d==0)
            assert witness("set_predicate",dict(domain=domain,divisor=d,threshold=t))["exact_value"]==expected

def test_finite_set_symmetric_difference_matches_membership_xor():
    universe=[1,2,3,4]
    for mask_a in range(16):
        for mask_b in range(16):
            left=[x for j,x in enumerate(universe) if (mask_a>>j)&1]
            right=[x for j,x in enumerate(universe) if (mask_b>>j)&1]
            expected=",".join(str(x) for x in universe if (x in left)!=(x in right))
            assert witness("set_symdiff",dict(universe=universe,left=left,right=right))["exact_value"]==expected

def test_open_endpoint_has_supremum_but_no_maximum():
    for lo,hi in [(-5,5),(0,1),(1,2)]:
        a=witness("maximum_on_interval",dict(lo=lo,hi=hi,right_closed=0))
        b=witness("maximum_on_interval",dict(lo=lo,hi=hi,right_closed=1))
        assert a["exact_value"]==f"NO_MAX|{hi}"
        assert b["exact_value"]==f"MAX|{hi}"

def test_rational_power_domain_and_negative_base_odd_denominator():
    assert witness("rational_power",dict(base=-8,numerator=2,denominator=3))["exact_value"]=="4"
    assert witness("real_power_domain",dict(x=0,numerator=0,denominator=1))["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness("real_power_domain",dict(x=0,numerator=-1,denominator=1))["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness("rational_power",dict(base=0,numerator=-1,denominator=1))["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_vector_projection_residual_orthogonality_many_cases():
    for x,y,a,b in itertools.product(range(-2,3),repeat=4):
        if not (a or b):
            continue
        v=[a,b];u=[x,y]
        result=witness("vector_projection",dict(u=u,v=v))
        assert result["status"]=="FINITE_EXACT_CASE_ONLY"
        s,t=(Fraction(k) for k in result["exact_value"].split(","))
        assert (x-s)*a+(y-t)*b==0

def test_vector_triangle_telescopes_for_all_small_triples():
    for x,y,z in itertools.product(range(-2,3),repeat=3):
        a,b,c=[x,0],[y,0],[z,0]
        assert witness("triangle_vector",dict(a=a,b=b,c=c))["exact_value"]==f"{z-x},0"

def test_exponential_monotonicity_and_integer_laws_boundaries():
    for a in (2,3,5):
        for p,q in itertools.product(range(-3,4),repeat=2):
            result=witness("positive_exp_law",dict(base=a,p=p,q=q))
            assert result["exact_value"]==str(Fraction(a)**(p+q))
    for bn,bd in [(1,2),(1,3),(2,1),(3,2)]:
        result=witness("positive_exp_monotonic",dict(base_num=bn,base_den=bd,x=-2,y=2))
        assert result["exact_value"]==("INCREASING" if bn>bd else "DECREASING")

def test_angle_conversion_and_projection_degenerate_examples():
    assert witness("angle_degree_to_radian",dict(degrees=-210))["exact_value"]=="-7/6*pi"
    assert witness("angle_degree_to_radian",dict(degrees=720))["exact_value"]=="4*pi"
    assert witness("angle_degree_to_radian",dict(degrees=721))["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness("vector_projection",dict(u=[0,0],v=[0,0]))["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_real_existing_student_deep_rag_and_llm_adapter_refuse_unapproved_batch44():
    """Actual application components, not merely the synthetic student projection."""
    from app.deep_retrieval import student_evidence_lookup
    from app.model_tutor_draft import draft_next_question
    for eid,lesson,_src in DRAFTS:
        found=student_evidence_lookup(lesson.title,limit=3)
        assert found["status"]=="NO_APPROVED_EVIDENCE"
        assert found["candidates"]==[]
        assert found["teacher_solution_exposed"] is False
        assert found["unverified_content_exposed"] is False
        result=draft_next_question(lesson.title,mode="GUIDE",
            help_requested=True,consent_to_cloud=True,
            operator_scope="EDITOR_LOCAL",
            provider_url="https://api.openai.com/v1/chat/completions",
            provider_model="offline-no-call")
        assert result.status=="BLOCKED"
        assert result.reason=="NO_APPROVED_MATH_EVIDENCE"
        assert result.model_called is False
        assert result.student_visible is False
        assert result.question_draft is None
