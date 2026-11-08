"""Batch43 independent regression: source locks, lesson rigor, exact math and no-spoiler.
Does not turn finite witnesses into formal proof or teacher signatures.
"""
import copy
import hashlib
import json
from fractions import Fraction
from math import comb, perm
from pathlib import Path
import pytest
from pydantic import ValidationError

from app.kb_batch42_coverage import ROOT, TRACKS, GateError, Row
from app.kb_batch43_review import (
    SOURCE, SOURCE_SHA, AUDIT, MANUSCRIPT, COVERAGE, GAPS, OPS,
    staged, validate, audit, coverage_overlay, generate, student_retrieval_projection,
)
from app.kb_batch43_exact import KEYS, VALID, INVALID, EXPECTED, witness

DRAFTS=staged()
LEDGER=coverage_overlay()
def test_reproducible_author_source_and_all_outputs():
    import subprocess,sys
    subprocess.run([sys.executable,str(ROOT/"scripts/build_kb_batch43_seed.py"),"--check"],
                   cwd=ROOT,check=True,capture_output=True,text=True)
    generate(check=True)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    assert len(DRAFTS)==24==len(OPS)==len(KEYS)
    assert len(set(eid for eid,_,_ in DRAFTS))==24
    assert all(x.exists() and x.stat().st_size>200 for x in (AUDIT,MANUSCRIPT,COVERAGE,GAPS))

def test_non_official_coverage_overlay_exact_and_frozen_previous():
    assert LEDGER["summary"]==dict(project_candidates=313,direct_review_drafts=157,
        legacy_only=12,missing_editorial_link=144,batch43_new=24,
        teacher_approved=0,student_published=0,official_atom_denominator=None)
    assert len(LEDGER["rows"])==313
    assert set(LEDGER["tracks"])==set(TRACKS)
    assert [LEDGER["tracks"][k]["missing_direct_editorial_link"] for k in TRACKS]==[78,66,0,0,0,0,0]
    for t in LEDGER["tracks"].values():
        assert t["official_atom_denominator"] is None
        assert t["official_verified_coverage"] is None
        assert t["teacher_approved"]==t["student_published"]==0
    from app.kb_batch42_coverage import build
    assert build()["summary"]["direct_review_drafts"]==133
    assert build()["summary"]["missing_editorial_link"]==168

@pytest.mark.parametrize("i",range(313))
def test_every_overlay_row_has_correct_provenance_and_status(i):
    r=LEDGER["rows"][i]
    assert Row.model_validate({k:v for k,v in r.items() if k!="batch43_new_teacher_review_draft"})
    assert not any(r[k] for k in ("official_clause_verified","math_certified","teacher_approved","student_published"))
    assert r["editorial_status"] in ("NO_DIRECT_LINK","LEGACY_ONLY_NOT_EQUIVALENT","DRAFT_REVIEW_PENDING")
    if r["batch43_new_teacher_review_draft"]:
        assert r["direct_review_drafts"]==[f"kb43:{r['editorial_id']}"]
        assert r["track"] in TRACKS[:2]

@pytest.mark.parametrize("i",range(24))
def test_each_distinct_curated_manuscript_contains_specific_evidence(i):
    eid,unit,src=DRAFTS[i]
    assert unit.goal==src["goal"]
    assert src["editorial_status"]=="NO_DIRECT_LINK"
    assert src["printed_page"]>=15
    assert unit.status=="REVIEW_PENDING"
    assert unit.approved_reviewer is None and unit.student_publishable is False
    assert unit.teacher_solution_visibility=="TEACHER_ONLY"
    assert unit.proof_status=="NOT_FORMALLY_CERTIFIED"
    assert unit.source_license=="PROJECT_AUTHORED"
    assert len(unit.conditions)>=2 and len(unit.prerequisites)>=2
    assert len(unit.derivation)==3
    assert len(set(s.reason for s in unit.derivation))==3
    assert len(unit.examples)==2 and len({q.question for q in unit.examples})==2
    assert all(len(q.steps)==2 and len(q.check)>=3 for q in unit.examples)
    assert len(unit.error.counterexample)>=12 and len(unit.error.why_invalid)>=8
    assert len(set(unit.hints))==3 and len(unit.near)>=6 and len(unit.far)>=6
    assert unit.near!=unit.far
    a=audit()["items"][i]
    assert a["editorial_id"]==eid and a["exact_operator"]==OPS[i]
    assert not any(a[k] for k in ("general_theorem_certified","student_freeform_step_verified",
         "official_clause_equivalence_approved","teacher_approved","student_publishable"))

@pytest.mark.parametrize("i",range(24))
def test_each_teacher_approval_or_content_safety_spoof_refused(i):
    _,unit,_=DRAFTS[i]
    raw=unit.model_dump(mode="json")
    for field,malicious in (
        ("status","APPROVED"),("approved_reviewer","someone"),
        ("student_publishable",True),("teacher_solution_visibility","STUDENT"),
        ("proof_status","FORMALLY_CERTIFIED"),("source_license","COPYRIGHTED_TEXT")):
        patch=copy.deepcopy(raw);patch[field]=malicious
        with pytest.raises(ValidationError):unit.__class__.model_validate(patch)
    patch=copy.deepcopy(raw);patch["examples"][0]["steps"]=[]
    with pytest.raises(ValidationError):unit.__class__.model_validate(patch)

def test_source_pin_duplicate_orphan_and_hidden_extra_refused():
    raw=SOURCE.read_text(encoding="utf-8")
    with pytest.raises(GateError,match="SHA drift"):validate(raw+" ")
    with pytest.raises(GateError,match="Duplicate"):
        validate(raw+raw.splitlines()[0]+"\n",check_pin=False)
    with pytest.raises(GateError,match="Orphan"):
        validate(raw.replace("KB31-C-P015-A005","KB00-FAKE-999",1),check_pin=False)
    first=json.loads(raw.splitlines()[0]);first["student_publishable"]=True
    corrupted="\n".join([json.dumps(first,ensure_ascii=False),*raw.splitlines()[1:]])+"\n"
    with pytest.raises(ValidationError):validate(corrupted,check_pin=False)
    first=json.loads(raw.splitlines()[0]);first["new_trust_flag"]=True
    corrupted="\n".join([json.dumps(first,ensure_ascii=False),*raw.splitlines()[1:]])+"\n"
    with pytest.raises(ValidationError):validate(corrupted,check_pin=False)

@pytest.mark.parametrize("op",list(KEYS))
def test_24_exact_positive_and_negative_boundary_fixtures(op):
    positive=witness(op,VALID[op]);negative=witness(op,INVALID[op])
    assert positive==dict(status="FINITE_EXACT_CASE_ONLY",exact_value=EXPECTED[op],
        general_theorem_certified=False,student_freeform_step_verified=False,
        teacher_approved=False,student_publishable=False)
    assert negative["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert negative["exact_value"] is None and negative["general_theorem_certified"] is False
    assert witness(op+"-not-supported",VALID[op])["status"]=="UNSUPPORTED"

@pytest.mark.parametrize("op",list(KEYS))
def test_24_exact_operators_refuse_injected_and_missing_fields(op):
    base=VALID[op]
    assert witness(op,{**base,"teacher_approved":True})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness(op,{**base,"student_publishable":True})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness(op,{})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    missing=copy.deepcopy(base);missing.pop(next(iter(missing)))
    assert witness(op,missing)["status"]=="CONDITIONS_NOT_ESTABLISHED"
    for malformed in (None,True,[],42,"hi"):
        assert witness(op,malformed)["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("op",list(KEYS))
def test_24_exact_operators_reject_wrong_types_large_inputs(op):
    field=next(iter(VALID[op]))
    for value in (True,False,None,1.5,"2",10**30,{},[True],[False],[10**40]):
        args=copy.deepcopy(VALID[op]);args[field]=value
        assert witness(op,args)["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_math_counterexamples_and_independent_arithmetic_properties():
    assert witness("sufficient",dict(p=[0,1],q=[0,0]))["exact_value"]=="false"
    assert witness("equivalent",dict(p=[0,1],q=[1,1]))["exact_value"]=="false"
    assert witness("unit_identity",dict(cos_num=3,sin_num=3,den=5))["exact_value"]=="false"
    assert witness("ssa_acute",dict(a=3,b=8,sin_num=1,sin_den=2))["exact_value"]=="NONE"
    assert witness("ssa_acute",dict(a=4,b=8,sin_num=1,sin_den=2))["exact_value"]=="ONE"
    assert witness("ssa_acute",dict(a=8,b=8,sin_num=1,sin_den=2))["exact_value"]=="ONE"
    assert witness("line_slope",dict(p=[3,-1],q=[3,7]))["exact_value"]=="UNDEFINED"
    assert witness("circle_line",dict(cx=0,cy=0,radius=3,a=1,b=0,c=-3))["exact_value"]=="TANGENT"
    assert witness("circle_line",dict(cx=0,cy=0,radius=1,a=1,b=0,c=-3))["exact_value"]=="NONE"
    assert witness("bayes_posterior",dict(weights=[1,99],likelihoods=[9,1],total=100,trials=10,target=0))["exact_value"]=="1/12"
    assert witness("discrete_moments",dict(values=[5],weights=[1],total=1))["exact_value"]=="5|0"
    for n in range(0,10):
        assert int(witness("combination",dict(n=n,r=0))["exact_value"])==1
        assert int(witness("permutation",dict(n=n,r=0))["exact_value"])==1
        for r in range(n+1):
            actual=int(witness("combination",dict(n=n,r=r))["exact_value"])
            assert actual==comb(n,r)==comb(n,n-r)
            p=int(witness("permutation",dict(n=n,r=r))["exact_value"])
            assert p==perm(n,r)
            assert p==actual*__import__("math").factorial(r)
    for n in range(1,40):
        assert int(witness("induction_sum",dict(n=n))["exact_value"])==sum(range(1,n+1))
    for x in range(-4,5):
        w=witness("quadratic_derivative",dict(a=2,b=3,c=-1,x=x,h=1))
        assert w["exact_value"]==f"{4*x+3}|{4*x+5}"
    for n in range(0,10):
        b=witness("binomial_coefficients",dict(n=n))["exact_value"]
        assert sum(map(int,b.split(",")))==2**n

def test_approval_is_not_granted_by_explicit_student_metadata_api():
    from app.kb_batch42_coverage import student_goal_lookup,editor_goal_lookup
    projection=student_retrieval_projection()
    assert projection["student_documents"]==projection["teacher_solutions_exposed"]==[]
    assert projection["teacher_approved"]==projection["student_published"]==0
    assert projection["official_atomic_denominator"] is None
    for eid,_,_ in DRAFTS:
        assert student_goal_lookup(eid)["status"]=="NO_APPROVED_GOAL_EVIDENCE"
        with pytest.raises(PermissionError):editor_goal_lookup(eid)
        meta=editor_goal_lookup(eid,scope="EDITOR_LOCAL")
        assert "teacher_solution" not in meta and "examples" not in meta

def test_independent_sympy_algebraic_cross_checks_not_general_proof_certification():
    import sympy as s
    x,y,a,b,c,h,t=s.symbols("x y a b c h t",real=True)
    q=lambda v:a*v*v+b*v+c
    # Identity on punctured neighborhood h != 0; plugging h=0 into the quotient is invalid.
    assert s.cancel((q(x+h)-q(x))/h-(2*a*x+b+a*h))==0
    assert s.diff(q(x),x)==2*a*x+b
    for n in range(0,10):
        polynomial=s.expand((x+y)**n)
        independently=sum(s.binomial(n,k)*x**(n-k)*y**k for k in range(n+1))
        assert s.expand(polynomial-independently)==0
    # A two-point normalized finite distribution, p+(1-p)=1.
    p=s.symbols("p",real=True)
    mu=s.expand(p*x+(1-p)*y)
    direct_variance=s.expand(p*(x-mu)**2+(1-p)*(y-mu)**2)
    second_moment=s.expand(p*x*x+(1-p)*y*y-mu*mu)
    assert s.simplify(direct_variance-second_moment)==0
    # For nonzero evidence denominator, posterior terms sum to one.
    w1,w2,l1,l2=s.symbols("w1 w2 l1 l2",positive=True)
    evidence=w1*l1+w2*l2
    assert s.simplify(w1*l1/evidence+w2*l2/evidence-1)==0
    # Positive denominator is essential; zero normal vector cannot define a plane.
    assert witness("plane_distance_squared",dict(point=[1,2,3],
        plane_point=[0,0,0],normal=[0,0,0]))["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert all(v["general_theorem_certified"] is False
        for v in (witness(op,VALID[op]) for op in KEYS))


def test_quadratic_extremum_witness_tracks_vertex_and_value_not_origin():
    # f(x)=a(x-center)^2+shift: extremum is at center, value is shift.
    positive=witness("fermat_quadratic",dict(a=2,center=7,shift=-5))
    negative=witness("fermat_quadratic",dict(a=-3,center=-4,shift=6))
    assert positive["exact_value"]=="MINIMUM|7|-5"
    assert negative["exact_value"]=="MAXIMUM|-4|6"
    assert witness("fermat_quadratic",dict(a=0,center=7,shift=-5))["status"]=="CONDITIONS_NOT_ESTABLISHED"
