"""Batch48 Mac-only source, finite-math, permission and negative regression tests."""
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from math import comb, factorial

import pytest
from pydantic import ValidationError

from app.kb_batch42_coverage import GateError, Row, TRACKS
from app.kb_batch47_review import coverage_overlay as previous_overlay
from app.kb_batch48_review import (SOURCE,SOURCE_SHA,AUDIT,MANUSCRIPT,COVERAGE,GAPS,
                                  staged,validate,audit,coverage_overlay,generate,
                                  student_retrieval_projection)
from app.kb_batch48_exact import OPS,SAMPLES,witness

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
    assert len(set(x[0] for x in DRAFTS))==20
    assert all(x.exists() and x.stat().st_size>200 for x in (AUDIT,MANUSCRIPT,COVERAGE,GAPS))

def test_project_editorial_not_official_denominator():
    assert previous_overlay()["summary"]["missing_editorial_link"]==60
    assert LEDGER["summary"]==dict(project_candidates=313,direct_review_drafts=261,
        legacy_only=12,missing_editorial_link=40,batch48_new=20,
        teacher_approved=0,student_published=0,official_atom_denominator=None)
    assert len(LEDGER["rows"])==313
    assert [LEDGER["tracks"][t]["missing_direct_editorial_link"] for t in TRACKS]==[14,26,0,0,0,0,0]
    for t in TRACKS:
        assert LEDGER["tracks"][t]["official_atom_denominator"] is None
        assert LEDGER["tracks"][t]["official_verified_coverage"] is None
        assert LEDGER["tracks"][t]["teacher_approved"]==0
        assert LEDGER["tracks"][t]["student_published"]==0

@pytest.mark.parametrize("i",range(313))
def test_row_lineage_is_never_published(i):
    row=LEDGER["rows"][i]
    original={k:v for k,v in row.items() if not (k.startswith("batch") and k.endswith("_new_teacher_review_draft"))}
    assert Row.model_validate(original)
    assert not any(row.get(k) for k in ("official_clause_verified","math_certified",
                                        "teacher_approved","student_published"))
    if row["batch48_new_teacher_review_draft"]:
        assert row["track"]=="SELECTIVE_COMPULSORY"
        assert row["editorial_status"]=="DRAFT_REVIEW_PENDING"
        assert row["direct_review_drafts"]==["kb48:"+row["editorial_id"]]

@pytest.mark.parametrize("i",range(20))
def test_twenty_distinct_full_technical_reviews(i):
    eid,u,src=DRAFTS[i]
    assert src["track"]=="SELECTIVE_COMPULSORY"
    assert src["editorial_status"]=="NO_DIRECT_LINK"
    assert u.goal==src["goal"]
    assert u.status=="REVIEW_PENDING" and u.teacher_solution_visibility=="TEACHER_ONLY"
    assert u.source_license=="PROJECT_AUTHORED" and u.proof_status=="NOT_FORMALLY_CERTIFIED"
    assert u.student_publishable is False and u.approved_reviewer is None
    assert len(u.conditions)>=2 and len(u.prerequisites)>=2
    assert len(u.derivation)==3 and len({s.statement for s in u.derivation})==3
    assert len(u.examples)==2 and len({e.question for e in u.examples})==2
    assert len(u.hints)==3 and len(set(u.hints))==3
    assert len(u.error.counterexample)>12 and len(u.error.why_invalid)>8
    assert eid in MANUSCRIPT.read_text(encoding="utf-8")
    item=audit()["items"][i]
    assert item["editorial_id"]==eid and len(item["content_sha256"])==64
    assert item["source_sha256"]==src["source_sha256"]
    assert not any(item[k] for k in ("official_clause_certified","formal_proof_certified",
        "teacher_approved","student_published","student_freeform_step_verified"))

@pytest.mark.parametrize("op",OPS)
def test_exact_math_good_and_bad_premise(op):
    good,expected,bad=SAMPLES[op]
    result=witness(op,good)
    assert result["status"]=="FINITE_EXACT_CASE_ONLY"
    assert result["exact_value"]==expected
    denied=witness(op,bad)
    assert denied["status"]=="CONDITIONS_NOT_ESTABLISHED" and denied["exact_value"] is None
    for r in (result,denied):
        assert not any(r[k] for k in ("general_theorem_certified","student_freeform_step_verified",
                                      "teacher_approved","student_publishable"))

@pytest.mark.parametrize("op",OPS)
def test_reject_unknown_fields_missing_fields_and_object_injection(op):
    original=copy.deepcopy(SAMPLES[op][0])
    assert witness(op,{**original,"teacher_approved":True})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    key=next(iter(original))
    assert witness(op,{k:v for k,v in original.items() if k!=key})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    original[key]={"__proto__":"true"}
    assert witness(op,original)["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("value",["APPROVE","sympify('x')","model_asserted_true",1,[],{},None,True])
def test_unsupported_proof_operation_not_accepted(value):
    r=witness(value,{"proof":"AI proved this"})
    assert r["status"]=="UNSUPPORTED" and r["exact_value"] is None
    assert r["general_theorem_certified"] is False

def test_duplicate_cross_track_pin_drift_and_fake_approval_rejected():
    raw=SOURCE.read_text(encoding="utf-8")
    with pytest.raises(GateError):validate(raw+" ",check_pin=True)
    items=records()
    with pytest.raises(GateError):validate(encode(items+[items[0]]),check_pin=False)
    for eid in ("KB31-C-P021-A003","KB32-S-P038-A001","UNKNOWN"):
        clone=records();clone[0]["editorial_id"]=eid
        with pytest.raises(GateError):validate(encode(clone),check_pin=False)

@pytest.mark.parametrize("field,value",[
 ("status","APPROVED"),("student_publishable",True),("approved_reviewer","Fake Teacher"),
 ("proof_status","FORMALLY_CERTIFIED"),("source_license","TEXTBOOK_COPY"),
 ("teacher_solution_visibility","PUBLIC"),("conditions",[]),("derivation",[]),
 ("examples",[]),("hints",["same hint"]*3),("ignore_safety",True)
])
def test_draft_invalid_mutation_rejected(field,value):
    items=records();items[0][field]=value
    with pytest.raises((ValidationError,GateError)):validate(encode(items),check_pin=False)

def test_independent_projection_pythagorean_oracle():
    for x,y,z in itertools.product(range(-3,4),repeat=3):
        r=witness("space_point_line_distance_sq",
                  {"q":[x,y,z],"p":[0,0,0],"u":[1,0,0]})
        assert r["status"]=="FINITE_EXACT_CASE_ONLY"
        assert Fraction(r["exact_value"])==y*y+z*z
    assert witness("space_point_line_distance_sq",
                   {"q":[1,1,0],"p":[0,0,0],"u":[1,1,0]})["exact_value"]=="0"

def test_independent_parallel_perpendicular_and_relabeling():
    for a,b in itertools.product(range(-4,5),repeat=2):
        if a==b==0:continue
        n1=[a,b];n2=[2*a,2*b]
        v=witness("general_line_relation",{"A":n1[0],"B":n1[1],"D":n2[0],"E":n2[1]})
        assert v["exact_value"]=="PARALLEL_DIRECTIONS_ONLY"
        p=witness("general_line_relation",{"A":a,"B":b,"D":-b,"E":a})
        assert p["exact_value"]=="PERPENDICULAR"

def test_line_intersection_substitution_and_rank_cases():
    for c,f in itertools.product(range(-3,4),repeat=2):
        r=witness("linear_line_intersection",
                  {"A":1,"B":1,"C":c,"D":1,"E":-1,"F":f})
        x,y=[Fraction(v) for v in r["exact_value"][1:-1].split(",")]
        assert x+y==c and x-y==f
    assert witness("linear_line_intersection",
          {"A":1,"B":1,"C":2,"D":2,"E":2,"F":4})["exact_value"]=="COINCIDENT"
    assert witness("linear_line_intersection",
          {"A":1,"B":1,"C":2,"D":2,"E":2,"F":5})["exact_value"]=="PARALLEL_DISTINCT"

def test_circle_position_equal_centres_and_internal_external_tangency():
    def pair(x,r1,r2):
        return witness("two_circle_position",{"x1":0,"y1":0,"r1":r1,
                        "x2":x,"y2":0,"r2":r2})["exact_value"]
    assert pair(0,2,2)=="COINCIDENT"
    assert pair(0,2,3)=="INTERNAL_DISJOINT"
    assert pair(1,2,3)=="INTERNAL_TANGENT"
    assert pair(4,2,3)=="TWO_INTERSECTIONS"
    assert pair(5,2,3)=="EXTERNAL_TANGENT"
    assert pair(6,2,3)=="EXTERNAL_DISJOINT"

def test_ellipse_hyperbola_different_parameter_relations():
    for a in range(2,10):
        for c in range(1,a):
            e=witness("ellipse_focal_sum",{"a":a,"c":c})
            h=witness("hyperbola_focal_difference",{"a":c,"c":a})
            assert Fraction(e["exact_value"])==a*a-c*c
            assert Fraction(h["exact_value"])==a*a-c*c

def test_arrangement_factorial_combination_reconciliation():
    for n in range(21):
        for k in range(n+1):
            a=witness("arrangements_combinations",{"n":n,"k":k,"ordered":1})
            c=witness("arrangements_combinations",{"n":n,"k":k,"ordered":0})
            assert int(a["exact_value"])==int(c["exact_value"])*factorial(k)
            assert int(c["exact_value"])==comb(n,k)

def test_conditional_restriction_of_equally_likely_space():
    for N in range(1,14):
        for b in range(1,N+1):
            for intersection in range(b+1):
                r=witness("finite_conditional_probability",
                          {"N":N,"B":b,"intersection":intersection})
                assert Fraction(r["exact_value"])==Fraction(intersection,b)

def test_teacher_only_adapter_blocks_20_titles_without_provider():
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
