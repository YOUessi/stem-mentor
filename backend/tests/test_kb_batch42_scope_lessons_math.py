"""Batch42 313 editorial goals + 20 full original review manuscripts + 20 finite oracle types."""
import copy
import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from app.kb_batch42_coverage import (
    Row, GateError, PINS, ROOT, TRACKS, candidates, read_pinned,
    build, write, editor_goal_lookup, student_goal_lookup)
from app.kb_batch42_review import staged, validate, audit, generate, SOURCE, SOURCE_SHA, student_retrieval_projection
from app.kb_batch42_exact import KEYS, VALID, INVALID, witness

DRAFTS=staged()
WITNESS_BY_SOURCE={
"KB31-C-P015-A001":"set_membership",
"KB31-C-P015-A007":"set_union",
"KB31-C-P015-A008":"set_intersection",
"KB31-C-P016-A004":"finite_forall",
"KB31-C-P016-A005":"finite_exists_square",
"KB31-C-P017-A002":"linear_zero",
"KB31-C-P017-A003":"quadratic_sign",
"KB31-C-P020-A005":"exponential_order",
"KB31-C-P021-A005":"unit_circle_quadrant",
"KB31-C-P022-A003":"tan_quadrant",
"KB32-S-P038-A001":"sequence_term",
"KB32-S-P038-A003":"arithmetic_differences",
"KB32-S-P038-A007":"geometric_ratios",
"KB32-S-P039-A003":"constant_derivative",
"KB32-S-P039-A004":"identity_derivative",
"KB32-S-P039-A009":"quadratic_finite_max",
"KB32-S-P042-A001":"spatial_vector_sum",
"KB32-S-P042-A010":"plane_normal_valid",
"KB32-S-P047-A002":"conditional_finite_uniform",
"KB32-S-P047-A009":"finite_probability_mass",
}
EXPECTED={
"set_membership":"true","set_union":"1,2,3","set_intersection":"2",
"finite_forall":"true","finite_exists_square":"true",
"linear_zero":"true","quadratic_sign":"POSITIVE","exponential_order":"LESS",
"unit_circle_quadrant":"0|1","tan_quadrant":"0","sequence_term":"9",
"arithmetic_differences":"3","geometric_ratios":"3",
"constant_derivative":"0","identity_derivative":"1",
"quadratic_finite_max":"1|0","spatial_vector_sum":"4,1,3",
"plane_normal_valid":"true","conditional_finite_uniform":"2/3",
"finite_probability_mass":"VALID",
}
def test_generated_reports_reproduce_exactly():
    write(check=True)
    generate(check=True)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    assert len(DRAFTS)==20 and len(set(WITNESS_BY_SOURCE))==20
    assert set(WITNESS_BY_SOURCE)=={eid for eid,_,_ in DRAFTS}

def test_313_project_denominator_not_official():
    a=build(); s=a["summary"]
    assert s==dict(project_candidates=313,direct_review_drafts=133,
        legacy_only=12,missing_editorial_link=168,
        teacher_approved=0,student_published=0,official_atom_denominator=None)
    assert len(a["rows"])==313
    assert sum(v["project_candidate_count"] for v in a["tracks"].values())==313
    assert all(v["official_atom_denominator"] is None and
        v["official_verified_coverage"] is None for v in a["tracks"].values())
    assert len({r["editorial_id"] for r in a["rows"]})==313
    assert not any(r["teacher_approved"] or r["official_clause_verified"] or
        r["math_certified"] or r["student_published"] for r in a["rows"])
    assert len([r for r in a["rows"] if r["editorial_status"]=="NO_DIRECT_LINK"])==168

def test_mixed_page_ids_do_not_restart_at_track_transitions():
    a={r["editorial_id"]:r for r in candidates()}
    assert a["KB33-C-P064-A004"]["track"]=="ELECTIVE_C"
    assert a["KB33-D-P069-A002"]["track"]=="ELECTIVE_D"
    assert a["KB33-E-P073-A005"]["track"]=="ELECTIVE_E"
    assert a["KB33-E-P073-A007"]["track"]=="ELECTIVE_E"
    # 47 manually curated historical link IDs refer to these exact rows.
    aa={r["editorial_id"]:r for r in build()["rows"]}
    assert aa["KB33-E-P073-A005"]["legacy_associations_unverified"]
    assert aa["KB33-E-P073-A007"]["legacy_associations_unverified"]

@pytest.mark.parametrize("label",list(PINS))
def test_corpus_source_pins_refuse_any_bit_drift(label):
    source, digest=PINS[label]
    raw=(ROOT/source).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==digest
    with pytest.raises(GateError,match="SHA drift"):
        read_pinned(label,raw+b" " if raw else b"x")

@pytest.mark.parametrize("index",range(20))
def test_each_core_review_unit_original_anchor_and_deep_pedagogy(index):
    eid,d,s=DRAFTS[index]
    assert d.goal==s["goal"]
    assert s["editorial_id"]==eid
    assert s["source_batch"] in ("kb31","kb32")
    assert len(d.derivation)==3 and len({x.statement for x in d.derivation})==3
    assert all(x.reason and x.statement for x in d.derivation)
    assert len(d.examples)==2 and all(len(x.steps)==2 and x.check for x in d.examples)
    assert d.error.counterexample and d.error.why_invalid
    assert len(set(d.hints))==3 and d.near!=d.far
    assert len(d.prerequisites)>0 and len(d.conditions)>0
    assert d.status=="REVIEW_PENDING"
    assert d.teacher_solution_visibility=="TEACHER_ONLY"
    assert d.proof_status=="NOT_FORMALLY_CERTIFIED"
    assert d.student_publishable is False and d.approved_reviewer is None

@pytest.mark.parametrize("index",range(20))
def test_every_review_approval_fake_is_refused(index):
    _,d,_=DRAFTS[index]
    source=d.model_dump(mode="json")
    for k,v in (("status","APPROVED"),("approved_reviewer","fake"),
                ("student_publishable",True),("teacher_solution_visibility","STUDENT"),
                ("proof_status","FORMALLY_CERTIFIED"),("source_license","UNKNOWN")):
        bad=copy.deepcopy(source);bad[k]=v
        with pytest.raises(ValidationError):d.__class__.model_validate(bad)
    bad=copy.deepcopy(source);bad["examples"][0]["steps"]=["answer spoiled"]
    with pytest.raises(ValidationError):d.__class__.model_validate(bad)

def test_invalid_course_source_and_duplicate_are_rejected():
    raw=SOURCE.read_text(encoding="utf-8")
    with pytest.raises(GateError,match="SHA drift"):
        validate(raw+" ")
    with pytest.raises(GateError,match="Duplicate"):
        validate(raw+raw.splitlines()[0]+"\n",check_pin=False)
    altered=raw.replace("KB31-C-P015-A001","KB00-NOT-A-REAL-SOURCE",1)
    with pytest.raises(GateError,match="Orphan"):
        validate(altered,check_pin=False)

@pytest.mark.parametrize("index",range(313))
def test_one_to_one_machine_ledger_all_tracks_all_rows(index):
    item=build()["rows"][index]
    parsed=Row.model_validate(item)
    assert parsed.source_sha256==PINS[item["source_batch"]][1]
    assert item["official_clause_verified"] is False
    assert item["student_published"] is False
    assert item["teacher_approved"] is False
    assert item["math_certified"] is False
    assert item["track"] in TRACKS
    assert item["editorial_status"] in ("DRAFT_REVIEW_PENDING","LEGACY_ONLY_NOT_EQUIVALENT","NO_DIRECT_LINK")

@pytest.mark.parametrize("source",range(3))
def test_source_rows_reject_incorrect_metadata_or_fake_source(source):
    label=("kb31","kb32","kb33")[source]
    raw=(ROOT/PINS[label][0]).read_bytes()
    with pytest.raises(GateError,match="SHA drift"):
        candidates(overrides={label:raw+b"\n"})

@pytest.mark.parametrize("index",range(20))
def test_exact_fixture_and_invalid_math_boundary_for_each_lesson(index):
    eid,_,_=DRAFTS[index]
    op=WITNESS_BY_SOURCE[eid]
    good=witness(op,VALID[op])
    bad=witness(op,INVALID[op])
    assert good==dict(status="FINITE_EXACT_CASE_ONLY",exact_value=EXPECTED[op],
        general_theorem_certified=False,student_freeform_step_verified=False,
        teacher_approved=False,student_publishable=False)
    assert bad["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert bad["exact_value"] is None and not bad["general_theorem_certified"]
    assert not bad["student_freeform_step_verified"]

@pytest.mark.parametrize("operator",list(KEYS))
def test_each_math_witness_rejects_unknown_missing_extra_false_approval(operator):
    assert witness(operator+"_LLM_APPROVED",VALID[operator])["status"]=="UNSUPPORTED"
    assert witness(operator,{})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness(operator,{**VALID[operator],"teacher_approved":True})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    bad=copy.deepcopy(VALID[operator]);bad.pop(next(iter(bad)))
    assert witness(operator,bad)["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("operator",list(KEYS))
def test_each_math_witness_denies_type_injection_and_extreme_numbers(operator):
    original=VALID[operator]
    field=next(iter(original))
    for invalid in (True,False,None,1.25,"3",10**100):
        data=copy.deepcopy(original)
        data[field]=invalid
        assert witness(operator,data)["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_premises_and_no_overclaim_math():
    assert witness("tan_quadrant",{"quarter_turn":1})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness("linear_zero",{"slope":0,"intercept":0,"candidate":0})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness("conditional_finite_uniform",{"total":5,"event_a":[1],"event_b":[]})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness("plane_normal_valid",{"normal":[0,0,1],"direction1":[1,0,0],"direction2":[2,0,0]})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness("finite_probability_mass",{"weights":[2,3],"denominator":4})["exact_value"]=="NOT_NORMALIZED"
    assert witness("geometric_ratios",{"terms":[3,0,0]})["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_no_solution_leaks_in_student_projection_or_local_unreviewed_goal_lookup():
    p=student_retrieval_projection()
    assert p["student_documents"]==[] and p["teacher_solutions_exposed"]==[]
    assert p["approved"]==p["student_published"]==0
    assert p["review_pending"]==20
    for eid in WITNESS_BY_SOURCE:
        with pytest.raises(PermissionError):editor_goal_lookup(eid)
        e=student_goal_lookup(eid)
        assert e["candidates"]==[]
        assert e["status"]=="NO_APPROVED_GOAL_EVIDENCE"
        assert e["teacher_solution_exposed"] is False
        info=editor_goal_lookup(eid,scope="EDITOR_LOCAL")
        assert "examples" not in info and "teacher_solution" not in info
        assert info["editorial_id"]==eid
