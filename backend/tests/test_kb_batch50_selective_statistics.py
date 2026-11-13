"""Batch50 original selective courses: proof premises, no-spoiler, source pins, finite exact math."""
import copy
import hashlib
import itertools
import json
from fractions import Fraction as F
from math import comb
import pytest
from pydantic import ValidationError
from app.kb_batch42_coverage import GateError,Row,TRACKS
from app.kb_batch49_review import coverage_overlay as previous
from app.kb_batch50_review import (
 SOURCE,SOURCE_SHA,staged,validate,audit,coverage_overlay,generate,
 student_retrieval_projection,AUDIT,MANUSCRIPT,COVERAGE,GAPS)
from app.kb_batch50_exact import INDEX_OP,SAMPLES,witness

DRAFTS=staged()
OVERLAY=coverage_overlay()

def records():
    return [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line]
def pack(rows):
    return "".join(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n" for r in rows)

def test_authoring_pins_and_generated_drift():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    assert len(DRAFTS)==20 and len(INDEX_OP)==len(SAMPLES)==17
    generate(check=True)
    for x in (AUDIT,MANUSCRIPT,COVERAGE,GAPS):
        assert x.exists() and x.stat().st_size>100
    assert audit()["summary"]["research_method_drafts_without_numeric_proof"]==3

def test_project_editorial_count_not_official_denominator():
    assert previous()["summary"]["missing_editorial_link"]==20
    assert OVERLAY["summary"]==dict(project_candidates=313,direct_review_drafts=301,
      legacy_only=12,missing_editorial_link=0,batch50_new=20,compulsory_remaining=0,
      selective_compulsory_remaining=0,teacher_approved=0,student_published=0,
      official_atom_denominator=None)
    assert len(OVERLAY["rows"])==313
    assert [OVERLAY["tracks"][x]["with_direct_review_draft"] for x in TRACKS]==[125,92,22,27,17,15,3]
    assert [OVERLAY["tracks"][x]["legacy_association_only"] for x in TRACKS]==[0,0,6,2,2,1,1]
    assert all(x["official_atom_denominator"] is None and x["official_verified_coverage"] is None
               for x in OVERLAY["tracks"].values())
    assert all(not r["official_clause_verified"] for r in OVERLAY["rows"])
    assert all(not r["teacher_approved"] for r in OVERLAY["rows"])

@pytest.mark.parametrize("i",range(313))
def test_every_ledger_atom_is_valid_and_not_approved(i):
    r=OVERLAY["rows"][i]
    Row.model_validate({k:v for k,v in r.items()
                        if not(k.startswith("batch") and k.endswith("_new_teacher_review_draft"))})
    assert r["editorial_status"] in ("DRAFT_REVIEW_PENDING","LEGACY_ONLY_NOT_EQUIVALENT")
    if r["batch50_new_teacher_review_draft"]:
        assert r["track"]=="SELECTIVE_COMPULSORY"
        assert r["direct_review_drafts"]==["kb50:"+r["editorial_id"]]
        assert r["editorial_status"]=="DRAFT_REVIEW_PENDING"

@pytest.mark.parametrize("i",range(20))
def test_twenty_original_distinct_teacher_only_deep_lessons(i):
    eid,u,src=DRAFTS[i]
    assert u.goal==src["goal"]
    assert u.status=="REVIEW_PENDING" and u.student_publishable is False
    assert u.approved_reviewer is None and u.teacher_solution_visibility=="TEACHER_ONLY"
    assert u.source_license=="PROJECT_AUTHORED" and u.proof_status=="NOT_FORMALLY_CERTIFIED"
    assert len(u.conditions)>=2 and len(u.prerequisites)>=2
    assert len(u.derivation)==3 and len({p.statement for p in u.derivation})==3
    assert len(u.examples)==2 and len({x.question for x in u.examples})==2
    assert all(len(e.steps)==2 and len(e.check)>=3 for e in u.examples)
    assert len(u.hints)==3 and len(set(u.hints))==3
    assert len(u.error.counterexample)>=12 and len(u.error.why_invalid)>=8
    assert u.near and u.far and u.near!=u.far
    assert eid in MANUSCRIPT.read_text(encoding="utf-8")
    a=audit()["items"][i]
    assert a["editorial_id"]==eid and a["curriculum_source_sha256"]==src["source_sha256"]
    assert len(a["lesson_sha256"])==64
    assert a["finite_instance_checked"]==(i in INDEX_OP)
    for key in ("formal_general_proof_certified","official_clause_certified",
                "teacher_approved","student_published","student_freeform_step_verified"):
        assert a[key] is False

@pytest.mark.parametrize("op",SAMPLES)
def test_all_seventeen_finite_valid_bad_premise_pairs(op):
    good,expect,bad=SAMPLES[op]
    result=witness(op,good)
    assert result["status"]=="FINITE_EXACT_CASE_ONLY" and result["exact_value"]==expect
    invalid=witness(op,bad)
    assert invalid["status"]=="CONDITIONS_NOT_ESTABLISHED" and invalid["exact_value"] is None
    for k in ("general_theorem_certified","student_freeform_step_verified",
              "teacher_approved","student_publishable"):
        assert result[k] is False

@pytest.mark.parametrize("op",SAMPLES)
def test_seventeen_oracles_reject_extra_missing_and_payload_injection(op):
    d=copy.deepcopy(SAMPLES[op][0]);key=next(iter(d))
    assert witness(op,{**d,"student_publishable":True})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness(op,{k:v for k,v in d.items() if k!=key})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    d[key]={"__proto__":"teacher_approved"}
    assert witness(op,d)["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("payload",["freeform_proof","import os",None,1,False,{},["proof"],"cos(x)"])
def test_unsupported_student_freeform_cannot_be_certified(payload):
    r=witness(payload,{"model_claimed":True})
    assert r["status"]=="UNSUPPORTED" and not r["general_theorem_certified"]
    assert not r["student_freeform_step_verified"]

@pytest.mark.parametrize("key,value",[
 ("status","APPROVED"),("approved_reviewer","Teacher X"),("student_publishable",True),
 ("proof_status","FORMALLY_CERTIFIED"),("source_license","TEXTBOOK_FULL_COPY"),
 ("teacher_solution_visibility","PUBLIC"),("conditions",[]),("derivation",[]),
 ("examples",[]),("hints",["generic"]*3),("unverified",True)
])
def test_mutated_teacher_review_cannot_be_promoted_or_malformed(key,value):
    rec=records();rec[0][key]=value
    with pytest.raises((GateError,ValidationError)): validate(pack(rec),check_pin=False)

def test_modified_source_and_reuse_orphan_ids_denied():
    raw=SOURCE.read_text(encoding="utf-8")
    with pytest.raises(GateError): validate(raw+" ",check_pin=True)
    rec=records()
    with pytest.raises(GateError): validate(pack(rec+[rec[0]]),check_pin=False)
    for illegal in ("KB32-S-P038-A001","KB33-A-P052-A001","NOT-AN-ID"):
        mod=records();mod[0]["editorial_id"]=illegal
        with pytest.raises(GateError):validate(pack(mod),check_pin=False)

def test_exact_combinatorics_and_table_invariants_exhaustive():
    # independent calculation, not model self-assessment
    for n in range(0,9):
        for k in range(n+1):
            r=witness("binomial_probability",{"n":n,"k":k,"p_num":1,"p_den":2})
            assert F(r["exact_value"])==F(comb(n,k),2**n)
    for N in range(1,10):
        for K in range(N+1):
            for n in range(N+1):
                probs=[]
                for k in range(max(0,n-N+K),min(n,K)+1):
                    r=witness("hypergeometric_probability",{"N":N,"K":K,"n":n,"k":k})
                    target=F(comb(K,k)*comb(N-K,n-k),comb(N,n))
                    assert F(r["exact_value"])==target
                    probs.append(target)
                assert sum(probs,F(0))==1
    for a,b,c,d in itertools.product(range(3),repeat=4):
        if not (a+b+c+d):continue
        p=witness("empirical_2x2",{"a":a,"b":b,"c":c,"d":d})
        assert F(p["exact_value"])==F(a,a+b+c+d)
        if min(a+b,c+d,a+c,b+d)>0:
            e=witness("expected_2x2",{"a":a,"b":b,"c":c,"d":d})
            assert F(e["exact_value"])==F((a+b)*(a+c),a+b+c+d)
            z=witness("chi_square_2x2",{"a":a,"b":b,"c":c,"d":d})
            target=F((a+b+c+d)*(a*d-b*c)**2,(a+b)*(c+d)*(a+c)*(b+d))
            assert F(z["exact_value"])==target

def test_corner_cases_and_quantifiers_not_silently_added():
    assert witness("unsquared_root_filter",{"candidate":0})["exact_value"]=="INVALID_EXTRANEOUS"
    assert witness("unsquared_root_filter",{"candidate":3})["exact_value"]=="VALID"
    assert witness("normal_center_half",{"variance":0})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness("normal_z_score",{"mu":0,"variance":3,"x":3})["status"]=="UNSUPPORTED"  # not an invalid normal distribution
    assert witness("independence_2x2",{"a":1,"b":1,"c":1,"d":1})["exact_value"]=="EMPIRICAL_FACTORIZATION_ONLY"
    assert witness("pearson_perfect",{"x1":1,"x2":1,"x3":1,"slope":2})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness("in_range_or_extrapolation",{"low":0,"high":5,"x":3})["exact_value"]=="INTERPOLATION"
    assert [i for i in range(20) if i not in INDEX_OP]==[17,18,19]
    assert all("研究" in DRAFTS[i][1].title for i in (17,18,19))

def test_actual_student_retrieval_and_tutor_withhold_all_twenty_reviews():
    from app.deep_retrieval import student_evidence_lookup
    from app.model_tutor_draft import draft_next_question
    projection=student_retrieval_projection()
    assert projection["student_documents"]==[] and projection["teacher_solutions_exposed"]==[]
    for _,lesson,_ in DRAFTS:
        e=student_evidence_lookup(lesson.title,limit=3)
        assert e["status"]=="NO_APPROVED_EVIDENCE"
        assert e["candidates"]==[] and e["teacher_solution_exposed"] is False
        r=draft_next_question(lesson.title,mode="GUIDE",help_requested=True,
          consent_to_cloud=True,operator_scope="EDITOR_LOCAL",
          provider_url="https://api.openai.com/v1/chat/completions",
          provider_model="offline-test-do-not-call")
        assert r.status=="BLOCKED" and r.reason=="NO_APPROVED_MATH_EVIDENCE"
        assert not r.model_called and not r.student_visible and r.question_draft is None
