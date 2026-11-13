"""Batch49 regression: original math content, source pins, finite exact premises and student isolation."""
import copy
import hashlib
import itertools
import json
from fractions import Fraction
import pytest
from pydantic import ValidationError
from app.kb_batch42_coverage import GateError,Row,TRACKS
from app.kb_batch48_review import coverage_overlay as previous
from app.kb_batch49_review import (SOURCE,SOURCE_SHA,staged,validate,audit,coverage_overlay,
    generate,student_retrieval_projection,AUDIT,MANUSCRIPT,COVERAGE,GAPS)
from app.kb_batch49_exact import INDEX_OP,SAMPLES,witness

DRAFTS=staged()
OVERLAY=coverage_overlay()

def records():
    return [json.loads(s) for s in SOURCE.read_text(encoding="utf-8").splitlines() if s.strip()]
def encode(rows):
    return "".join(json.dumps(x,ensure_ascii=False,separators=(",",":"))+"\n" for x in rows)

def test_pins_generation_and_batch_counts():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    generate(check=True)
    assert len(DRAFTS)==20 and len(INDEX_OP)==17 and len(SAMPLES)==17
    assert len({eid for eid,_,_ in DRAFTS})==20
    assert all(p.exists() and p.stat().st_size>100 for p in (AUDIT,MANUSCRIPT,COVERAGE,GAPS))
    assert audit()["summary"]["nonnumeric_source_methods"]==3

def test_project_editorial_denominators_do_not_claim_official_coverage():
    assert previous()["summary"]["missing_editorial_link"]==40
    assert OVERLAY["summary"]==dict(project_candidates=313,direct_review_drafts=281,
        legacy_only=12,missing_editorial_link=20,batch49_new=20,
        compulsory_remaining=0,selective_compulsory_remaining=20,
        teacher_approved=0,student_published=0,official_atom_denominator=None)
    assert len(OVERLAY["rows"])==313
    assert [OVERLAY["tracks"][t]["missing_direct_editorial_link"] for t in TRACKS]==[0,20,0,0,0,0,0]
    assert all(OVERLAY["tracks"][t]["official_atom_denominator"] is None for t in TRACKS)
    assert all(OVERLAY["tracks"][t]["official_verified_coverage"] is None for t in TRACKS)

@pytest.mark.parametrize("i",range(313))
def test_each_ledger_row_valid_and_unapproved(i):
    r=OVERLAY["rows"][i]
    core={k:v for k,v in r.items() if not(k.startswith("batch") and k.endswith("_new_teacher_review_draft"))}
    Row.model_validate(core)
    assert not any(r.get(k) for k in ("official_clause_verified","math_certified","teacher_approved","student_published"))
    if r["batch49_new_teacher_review_draft"]:
        assert r["editorial_status"]=="DRAFT_REVIEW_PENDING"
        assert r["direct_review_drafts"]==["kb49:"+r["editorial_id"]]

@pytest.mark.parametrize("i",range(20))
def test_twenty_independent_detailed_original_teacher_reviews(i):
    eid,u,src=DRAFTS[i]
    assert u.goal==src["goal"] and src["editorial_status"]=="NO_DIRECT_LINK"
    assert src["track"]==("COMPULSORY" if i<14 else "SELECTIVE_COMPULSORY")
    assert u.status=="REVIEW_PENDING" and u.teacher_solution_visibility=="TEACHER_ONLY"
    assert u.source_license=="PROJECT_AUTHORED" and u.proof_status=="NOT_FORMALLY_CERTIFIED"
    assert u.student_publishable is False and u.approved_reviewer is None
    assert len(u.conditions)>=2 and len(u.prerequisites)>=2
    assert len(u.derivation)==3 and len({d.statement for d in u.derivation})==3
    assert len(u.examples)==2 and len({x.question for x in u.examples})==2
    assert all(len(e.steps)==2 and len(e.check)>=3 for e in u.examples)
    assert len(u.hints)==3 and len(set(u.hints))==3
    assert len(u.error.counterexample)>12 and len(u.error.why_invalid)>8
    assert eid in MANUSCRIPT.read_text(encoding="utf-8")
    item=audit()["items"][i]
    assert item["editorial_id"]==eid and item["curriculum_source_sha256"]==src["source_sha256"]
    assert len(item["authored_content_sha256"])==64
    assert not any(item[k] for k in ("source_clause_certified","math_general_proof_certified",
                                     "teacher_approved","student_published","student_freeform_step_verified"))
    assert item["mathematical_finite_case_available"]==(i in INDEX_OP)

@pytest.mark.parametrize("op",SAMPLES)
def test_valid_and_invalid_mathematical_premises(op):
    good,expected,bad=SAMPLES[op]
    assert witness(op,good)["exact_value"]==expected
    assert witness(op,good)["status"]=="FINITE_EXACT_CASE_ONLY"
    invalid=witness(op,bad)
    assert invalid["status"]=="CONDITIONS_NOT_ESTABLISHED" and invalid["exact_value"] is None
    assert all(not witness(op,good)[k] for k in ("general_theorem_certified",
             "student_freeform_step_verified","teacher_approved","student_publishable"))

@pytest.mark.parametrize("op",SAMPLES)
def test_nonwhitelisted_shapes_injections_and_missing_field(op):
    data=copy.deepcopy(SAMPLES[op][0]);key=next(iter(data))
    assert witness(op,{**data,"teacher_approved":True})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness(op,{k:v for k,v in data.items() if k!=key})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    data[key]={"__proto__":"approved"}
    assert witness(op,data)["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("illegal",["freeform_proof",None,{},False,1,["cos(x)"],"__import__('os')"])
def test_unsupported_freeform_never_certified(illegal):
    result=witness(illegal,{"model_claimed":True})
    assert result["status"]=="UNSUPPORTED" and result["exact_value"] is None
    assert result["general_theorem_certified"] is False

def test_duplicate_unregistered_old_link_and_approval_forgery_denied():
    raw=SOURCE.read_text(encoding="utf-8")
    with pytest.raises(GateError):validate(raw+" ",check_pin=True)
    rows=records()
    with pytest.raises(GateError):validate(encode(rows+[rows[0]]),check_pin=False)
    for eid in ("KB32-S-P038-A001","KB33-A-P052-A001","BAD-ID"):
        modified=records();modified[0]["editorial_id"]=eid
        with pytest.raises(GateError):validate(encode(modified),check_pin=False)

@pytest.mark.parametrize("key,value",[
 ("status","APPROVED"),("approved_reviewer","Fake Person"),("student_publishable",True),
 ("proof_status","FORMALLY_CERTIFIED"),("teacher_solution_visibility","PUBLIC"),
 ("source_license","TEXTBOOK_FULL_COPY"),("conditions",[]),("derivation",[]),
 ("examples",[]),("hints",["same"]*3),("inject",True)
])
def test_schema_blocks_illegal_review_mutations(key,value):
    rows=records();rows[0][key]=value
    with pytest.raises((GateError,ValidationError)):validate(encode(rows),check_pin=False)

def test_small_integer_oracles_crosscheck_many_cases():
    for x,y in itertools.product(range(-4,5),repeat=2):
        v=witness("displacement_length_sq",{"x1":0,"y1":0,"x2":x,"y2":y})
        assert v["exact_value"]==str(x*x+y*y)
        c=witness("complex_modulus_sq_nonzero",{"x":x,"y":y})
        if x==y==0:assert c["status"]=="CONDITIONS_NOT_ESTABLISHED"
        else:assert c["exact_value"]==str(x*x+y*y)
    for initial in range(1,20):
        for d in range(1,10):
            assert Fraction(witness("nonnegative_linear_horizon",
                  {"initial":initial,"decrement":d})["exact_value"])==Fraction(initial,d)
    for n in range(15):
        r=witness("additive_recurrence_term",{"x0":2,"d":3,"n":n})
        assert int(r["exact_value"])==2+3*n
    for z in (-3,-1,0,1,2,4):
        r=witness("line_plane_z_relation",{"base_z":z,"slope_z":0,"plane_z":0,"normal_z":1})
        assert r["exact_value"]==("CONTAINED" if z==0 else "PARALLEL_DISJOINT")
    assert witness("skew_lines_projected_crossing",{"height":1})["exact_value"]=="SKEW_PROJECTION_CROSS"

def test_disallow_suspect_model_inference_and_nonmath_history_certification():
    assert witness("three_equal_step_linear_fit",{"y0":0,"y1":2,"y2":0,"step":1})["exact_value"]=="NOT_LINEAR"
    assert witness("three_equal_step_linear_fit",{"y0":1,"y1":3,"y2":5,"step":1})["exact_value"]=="LINEAR"
    assert [i for i in range(20) if i not in INDEX_OP]==[0,14,18]
    assert all(audit()["items"][i]["finite_op"] is None for i in (0,14,18))
    assert all("历史" in DRAFTS[i][1].title or "史" in DRAFTS[i][1].title for i in (0,14,18))

def test_actual_student_retrieval_and_tutor_block_unauthorized_20_titles():
    from app.deep_retrieval import student_evidence_lookup
    from app.model_tutor_draft import draft_next_question
    p=student_retrieval_projection()
    assert p["student_documents"]==[] and p["teacher_solutions_exposed"]==[]
    for _,lesson,_ in DRAFTS:
        evidence=student_evidence_lookup(lesson.title,limit=3)
        assert evidence["status"]=="NO_APPROVED_EVIDENCE"
        assert evidence["candidates"]==[] and evidence["teacher_solution_exposed"] is False
        result=draft_next_question(lesson.title,mode="GUIDE",help_requested=True,
              consent_to_cloud=True,operator_scope="EDITOR_LOCAL",
              provider_url="https://api.openai.com/v1/chat/completions",
              provider_model="offline-test-do-not-call")
        assert result.status=="BLOCKED" and result.reason=="NO_APPROVED_MATH_EVIDENCE"
        assert not result.model_called and not result.student_visible
        assert result.question_draft is None
