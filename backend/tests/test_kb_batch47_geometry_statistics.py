"""Batch47 auditable twenty-lesson math/source/permission tests, with negative cases."""
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from math import comb

import pytest
from pydantic import ValidationError

from app.kb_batch42_coverage import GateError, Row, TRACKS
from app.kb_batch46_review import coverage_overlay as previous_overlay
from app.kb_batch47_review import (SOURCE,SOURCE_SHA,AUDIT,MANUSCRIPT,COVERAGE,GAPS,
    staged,validate,audit,coverage_overlay,generate,student_retrieval_projection)
from app.kb_batch47_exact import OPS,SAMPLES,witness

DRAFTS=staged()
LEDGER=coverage_overlay()

def records():
    return [json.loads(x) for x in SOURCE.read_text(encoding="utf-8").splitlines() if x.strip()]
def encode(rows):
    return "".join(json.dumps(x,ensure_ascii=False,separators=(",",":"))+"\n" for x in rows)

def test_source_integrity_and_generated_artifacts():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    generate(check=True)
    assert len(DRAFTS)==len(OPS)==len(SAMPLES)==20
    assert len({x[0] for x in DRAFTS})==20
    assert all(p.exists() and p.stat().st_size>200 for p in (AUDIT,MANUSCRIPT,COVERAGE,GAPS))

def test_project_candidate_denominator_not_official():
    assert previous_overlay()["summary"]["missing_editorial_link"]==80
    assert LEDGER["summary"]==dict(project_candidates=313,direct_review_drafts=241,
        legacy_only=12,missing_editorial_link=60,batch47_new=20,
        teacher_approved=0,student_published=0,official_atom_denominator=None)
    assert len(LEDGER["rows"])==313
    assert [LEDGER["tracks"][t]["missing_direct_editorial_link"] for t in TRACKS]==[14,46,0,0,0,0,0]
    for tr in TRACKS:
        assert LEDGER["tracks"][tr]["official_atom_denominator"] is None
        assert LEDGER["tracks"][tr]["teacher_approved"]==0
        assert LEDGER["tracks"][tr]["student_published"]==0

@pytest.mark.parametrize("i",range(313))
def test_per_editorial_row_lineage_safe(i):
    row=LEDGER["rows"][i]
    raw={k:v for k,v in row.items() if not (k.startswith("batch") and k.endswith("_new_teacher_review_draft"))}
    assert Row.model_validate(raw)
    assert not any(row.get(k) for k in ("official_clause_verified","math_certified","teacher_approved","student_published"))
    if row["batch47_new_teacher_review_draft"]:
        assert row["track"]=="COMPULSORY" and row["editorial_status"]=="DRAFT_REVIEW_PENDING"
        assert row["direct_review_drafts"]==["kb47:"+row["editorial_id"]]

@pytest.mark.parametrize("i",range(20))
def test_all_twenty_individual_lessons(i):
    eid,u,src=DRAFTS[i]
    assert src["track"]=="COMPULSORY" and src["editorial_status"]=="NO_DIRECT_LINK"
    assert u.goal==src["goal"]
    assert u.status=="REVIEW_PENDING" and u.teacher_solution_visibility=="TEACHER_ONLY"
    assert u.source_license=="PROJECT_AUTHORED" and u.proof_status=="NOT_FORMALLY_CERTIFIED"
    assert u.student_publishable is False and u.approved_reviewer is None
    assert len(u.conditions)>=2 and len(u.prerequisites)>=2
    assert len(u.derivation)==3 and len({s.statement for s in u.derivation})==3
    assert len(u.examples)==2 and len({s.question for s in u.examples})==2
    assert len(u.hints)==3 and len(set(u.hints))==3
    assert eid in MANUSCRIPT.read_text(encoding="utf-8")
    row=audit()["items"][i]
    assert row["editorial_id"]==eid and len(row["content_sha256"])==64
    assert row["source_sha256"]==src["source_sha256"]
    assert not any(row[k] for k in ("official_clause_certified","formal_proof_certified",
        "teacher_approved","student_published","student_freeform_step_verified"))

@pytest.mark.parametrize("op",OPS)
def test_positive_and_invalid_premise_oracle(op):
    good,expected,bad=SAMPLES[op]
    result=witness(op,good)
    assert result["status"]=="FINITE_EXACT_CASE_ONLY" and result["exact_value"]==expected
    denied=witness(op,bad)
    assert denied["status"]=="CONDITIONS_NOT_ESTABLISHED" and denied["exact_value"] is None
    for r in (result,denied):
        assert not any(r[k] for k in ("general_theorem_certified","student_freeform_step_verified",
            "teacher_approved","student_publishable"))

@pytest.mark.parametrize("op",OPS)
def test_exact_math_strict_shape_and_injection_rejected(op):
    p=copy.deepcopy(SAMPLES[op][0])
    assert witness(op,{**p,"approved":True})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    key=next(iter(p))
    assert witness(op,{k:v for k,v in p.items() if k!=key})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    p[key]={"__proto__":"true"}
    assert witness(op,p)["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("payload",["model_asserted_true","sympify(\"x\")","APPROVE",123,None,{},[],True])
def test_unknown_proof_operation_unsupported(payload):
    r=witness(payload,{"proof":"AI claims it is true"})
    assert r["status"]=="UNSUPPORTED" and not r["general_theorem_certified"]

def test_reject_tampered_duplicated_wrong_track_and_unauthorized_evidence():
    raw=SOURCE.read_text(encoding="utf-8")
    with pytest.raises(GateError):validate(raw+" ",check_pin=True)
    r=records()
    with pytest.raises(GateError):validate(encode(r+[r[0]]),check_pin=False)
    for eid in ("KB31-C-P021-A006","KB32-S-P047-A013","NO-GOAL"):
        q=records();q[0]["editorial_id"]=eid
        with pytest.raises(GateError):validate(encode(q),check_pin=False)

@pytest.mark.parametrize("field,value",[
 ("status","APPROVED"),("student_publishable",True),("approved_reviewer","Fake Teacher"),
 ("proof_status","FORMALLY_CERTIFIED"),("source_license","TEXTBOOK_COPY"),
 ("teacher_solution_visibility","PUBLIC"),("conditions",[]),("derivation",[]),
 ("examples",[]),("hints",["identical"]*3),("user_override",True)
])
def test_mutated_published_and_unverified_content_rejected(field,value):
    r=records();r[0][field]=value
    with pytest.raises((ValidationError,GateError)):validate(encode(r),check_pin=False)

def test_independent_vector_parallel_and_plane_geometry():
    # Parametric check of parallel planes, directions, and perpendicular planes.
    for x,y,z in itertools.product(range(-3,4),repeat=3):
        if x==y==z==0:continue
        u=[x,y,z];v=[2*x,2*y,2*z]
        res=witness("parallel_directions",{"u":u,"v":v})
        assert res["exact_value"]=="PARALLEL_DIRECTIONS"
    for k in range(-5,6):
        if k==0:continue
        r=witness("normal_line_directions",{"n":[0,0,1],"d1":[0,0,k],"d2":[0,0,1]})
        assert r["exact_value"]=="PARALLEL_DIRECTIONS"
    for z in range(-5,6):
        if z==0:continue
        r=witness("separate_line_plane",{"p":[0,0,z],"d":[1,0,0],"n":[0,0,1],"off":0})
        assert r["exact_value"]=="PARALLEL_DISTINCT"
    assert witness("separate_line_plane",{"p":[0,0,0],"d":[1,0,0],"n":[0,0,1],"off":0})["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_independent_percentile_fraction_oracle():
    for a,b,c,d in itertools.combinations(range(-4,7),4):
        vals=[d,b,a,c] # intentionally unsorted
        for p in (0,25,50,75,100):
            r=witness("percentile_linear",{"values":vals,"p":p})
            x=Fraction(3*p,100);idx=x.numerator//x.denominator;t=x-idx
            sorted_vals=sorted(vals)
            expected=sorted_vals[-1] if idx==3 else (1-t)*sorted_vals[idx]+t*sorted_vals[idx+1]
            assert r["status"]=="FINITE_EXACT_CASE_ONLY"
            assert Fraction(r["exact_value"])==expected
        assert witness("percentile_nearest_rank",{"values":vals,"p":50})["exact_value"]==str(sorted(vals)[1])

def test_binomial_independent_closed_form_positive_likelihood():
    for n in range(1,11):
        for k in range(n+1):
            for p in (0,1,2,3):
                q=3
                r=witness("binomial_likelihood",{"n":n,"k":k,"p_num":p,"p_den":q})
                expected=comb(n,k)*Fraction(p,q)**k*(1-Fraction(p,q))**(n-k)
                assert r["status"]=="FINITE_EXACT_CASE_ONLY" and Fraction(r["exact_value"])==expected

def test_random_drawing_no_replacement_and_stratification():
    for n in range(1,12):
        nums=list(range(1,n+1))
        res=witness("no_replacement_draws",{"N":n,"draws":nums+[1],"n":n})
        assert res["exact_value"]==",".join(map(str,nums))
        assert len(set(res["exact_value"].split(",")))==n
    for n1,n2,m1,m2 in itertools.product((1,2,5),(1,3,9),(-3,5),(-10,7)):
        r=witness("stratified_mean",{"n1":n1,"n2":n2,"m1":m1,"m2":m2})
        assert Fraction(r["exact_value"])==Fraction(n1*m1+n2*m2,n1+n2)

def test_real_tutor_refuses_all_pending_without_cloud():
    from app.deep_retrieval import student_evidence_lookup
    from app.model_tutor_draft import draft_next_question
    assert student_retrieval_projection()["student_documents"]==[]
    for _,unit,_ in DRAFTS:
        evidence=student_evidence_lookup(unit.title,limit=3)
        assert evidence["status"]=="NO_APPROVED_EVIDENCE"
        assert evidence["candidates"]==[] and evidence["teacher_solution_exposed"] is False
        result=draft_next_question(unit.title,mode="GUIDE",help_requested=True,
            consent_to_cloud=True,operator_scope="EDITOR_LOCAL",
            provider_url="https://api.openai.com/v1/chat/completions",
            provider_model="test-offline-do-not-call")
        assert result.status=="BLOCKED" and result.reason=="NO_APPROVED_MATH_EVIDENCE"
        assert not result.model_called and not result.student_visible and result.question_draft is None


def test_equal_counts_do_not_certify_census_or_unique_person_identity():
    r=witness("census_coverage",{"N":30,"observed":30})
    assert r["status"]=="FINITE_EXACT_CASE_ONLY"
    assert r["exact_value"]=="COUNT_EQUAL_ONLY_NOT_FRAME_VERIFIED"
    assert not r["general_theorem_certified"] and not r["teacher_approved"]
