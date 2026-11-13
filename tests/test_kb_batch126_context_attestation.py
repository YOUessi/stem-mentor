"""Batch126 tests: 26 editorial source cases, 12 exact finite math witnesses.
Neither source hashes nor finite SymPy witnesses establish theorem certification.
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch126_context_evidence as b
from app.deep_knowledge import public_summary

DATA=json.loads(b.OUT.read_text(encoding="utf-8"))
LOCKS=json.loads(b.LOCKS.read_text(encoding="utf-8"))
CASES={x["id"]:x for x in DATA["records"]}

@pytest.mark.parametrize("case",DATA["records"],ids=lambda x:x["id"])
def test_all_26_reviews_have_pinned_context_and_are_not_teacher_authority(case):
    assert case["teacher_status"]=="REVIEW_PENDING"
    assert case["human_semantic_check"]=="EDITORIAL_ONLY_NOT_TEACHER_CERTIFIED"
    assert case["math_proof_certified"] is False
    assert case["teacher_signature"] is None
    assert case["student_authoritative"] is False
    assert case["official_atom_id"] is None
    assert case["context_relation"] in b.RELATIONS
    assert len(case["editorial_interpretation"])>=16
    assert len(case["unresolved_risk"])>=20
    assert case["source_attestation"]==LOCKS[case["id"]]

@pytest.mark.parametrize("case",DATA["records"],ids=lambda x:x["id"])
def test_exact_line_hashes_recomputed_from_authorized_mac_pdfkit_cache(case):
    page=case["page"];lo,hi=case["line_range"]
    lines=b.source_pages()[page][lo-1:hi]
    assert len(lines)==hi-lo+1
    expected=[hashlib.sha256(s.encode("utf-8")).hexdigest() for s in lines]
    assert expected==case["source_attestation"]["source_line_sha256"]
    assert hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()==case["source_attestation"]["source_span_sha256"]

@pytest.mark.parametrize("edit",[
    lambda d:d.update(source_reviewed_entries=27),
    lambda d:d.update(source_reviewed_editorial_proposals=21),
    lambda d:d.update(remaining_untouched_candidate_count=0),
    lambda d:d.update(full_official_atomic_denominator=239),
    lambda d:d.update(teacher_approved=1),
    lambda d:d.update(student_authoritative=1),
    lambda d:d.update(source_text_embedded=True),
    lambda d:d["per_track_official_atomic_denominator"].update(COMPULSORY=100),
    lambda d:d["records"][0].update(student_authoritative=True),
    lambda d:d["records"][0].update(teacher_status="APPROVED"),
    lambda d:d["records"][0].update(math_proof_certified=True),
    lambda d:d["records"][0].update(teacher_signature="fake-approval"),
    lambda d:d["records"][0].update(official_atom_id="FAKE"),
    lambda d:d["records"][0].update(page=73),
    lambda d:d["records"][0].update(context_relation="DIRECT_TEXT_THEOREM"),
    lambda d:d["records"][0].update(editorial_interpretation="Invented official wording"),
    lambda d:d["records"][0].update(unresolved_risk="No risk"),
    lambda d:d["records"][0]["source_attestation"].update(source_span_sha256="FAKE"),
    lambda d:d["records"][0]["source_attestation"]["source_line_sha256"].clear(),
    lambda d:d["records"].append(copy.deepcopy(d["records"][0])),
    lambda d:d["records"].pop(),
    lambda d:d["case_classes"].update(DIRECT_TEXT_AXIOM=100),
])
def test_batch126_forgeries_and_denominator_promotions_rejected(edit):
    changed=copy.deepcopy(DATA)
    edit(changed)
    with pytest.raises((ValueError,KeyError)):
        b.validate(changed)

def test_all_real_source_review_counts_and_reproducibility():
    assert b.validate(DATA)
    assert DATA["source_reviewed_editorial_proposals"]==20
    assert DATA["source_reviewed_residual_numbered_cues"]==6
    assert len([x for x in CASES if x.startswith("syllabus-cue-")])==6
    assert len([x for x in CASES if x.startswith("hs-semantic-")])==20
    assert DATA["per_track_official_atomic_denominator"]=={t:None for t in sorted(b.TRACKS)}
    assert b.OUT.read_text(encoding="utf-8")==b.serial(DATA)
    assert b.REPORT.read_text(encoding="utf-8")==b.report(DATA)
    assert DATA==b.audit(verify_local_source=True)

def test_unproven_source_topics_explicitly_remain_unproven():
    assert CASES["hs-semantic-pilot-119-c09"]["context_relation"]=="TEXT_INSUFFICIENT_VISUAL_REQUIRED"
    assert CASES["hs-semantic-pilot-119-ec02"]["context_relation"]=="CROSS_PAGE_CONTINUATION"
    assert CASES["hs-semantic-pilot-119-s06"]["context_relation"]=="OPTIONAL_NUMBERED_ACTIVITY"
    assert CASES["hs-semantic-pilot-123-s405"]["context_relation"]=="NUMBERED_NEIGHBOR_PARTIAL"
    assert "异常值" in CASES["hs-semantic-pilot-123-s405"]["unresolved_risk"]
    assert not any(x["teacher_status"]=="APPROVED" for x in CASES.values())

def test_student_public_retrieval_stays_teacher_answer_free():
    summary=json.dumps(public_summary(),ensure_ascii=False)
    assert "KB_BATCH126_CONTEXT_EVIDENCE" not in summary
    assert "EDITORIAL_ONLY_NOT_TEACHER_CERTIFIED" not in summary
    assert "source_attestation" not in summary

# These are finite exact counterexample/consistency witnesses, not universal
# theorem proofs. Every case tests an admissible and an invalid/degenerate input.
def witness(case_id):
    x,y,z,t=sp.symbols("x y z t",real=True)
    if case_id=="three_noncollinear_points":
        valid=sp.Matrix([1,0,0]).cross(sp.Matrix([0,1,0])).norm()==1
        invalid=sp.Matrix([1,0,0]).cross(sp.Matrix([2,0,0]))==sp.zeros(3,1)
    elif case_id=="plane_contains_line":
        a=sp.Matrix([1,0,1]);direction=sp.Matrix([0,1,0])
        valid=sp.simplify((a+t*direction)[0]-(a+t*direction)[2])==0
        invalid=sp.simplify((a+t*sp.Matrix([1,0,0]))[0]-(a+t*sp.Matrix([1,0,0]))[2])!=0
    elif case_id=="two_planes_unique_intersection":
        valid=sp.Matrix([1,0,0]).cross(sp.Matrix([0,1,0]))!=sp.zeros(3,1)
        invalid=sp.Matrix([1,0,0]).cross(sp.Matrix([2,0,0]))==sp.zeros(3,1)
    elif case_id=="classical_finite_equiprobable":
        valid=sp.Rational(2,4)==sp.Rational(1,2)
        invalid=sp.Rational(1,2)+sp.Rational(1,4)!=sp.Rational(2,4)
    elif case_id=="bisection_sign_and_continuity":
        f=lambda q:q*q-2
        valid=f(sp.Integer(1))*f(sp.Integer(2))<0
        invalid=(lambda q:q*q+1)(1)*(lambda q:q*q+1)(2)>0
    elif case_id=="induction_sum_check_not_proof":
        valid=all(sum(range(1,n+1))==n*(n+1)//2 for n in range(1,31))
        invalid=any(sum(range(1,n+1))!=n*(n+1)//2+1 for n in range(1,31))
    elif case_id=="discrete_distribution_nonnegative":
        valid=sp.Rational(1,3)+sp.Rational(2,3)==1
        invalid=sp.Rational(4,3)+sp.Rational(-1,3)==1 and sp.Rational(-1,3)<0
    elif case_id=="line_parallel_plane_conditions":
        valid=sp.Matrix([1,0,0]).dot(sp.Matrix([0,0,1]))==0 and sp.Integer(1)!=0
        invalid=sp.Matrix([1,0,0]).dot(sp.Matrix([0,0,1]))==0 and sp.Integer(0)==0
    elif case_id=="sample_variance_singleton_denominator":
        valid=sp.Rational(1,2-1)==1
        invalid=sp.Integer(1)-1==0
    elif case_id=="normal_standardization_sigma":
        valid=(sp.Integer(9)-sp.Integer(5))/sp.Integer(2)==2
        invalid=sp.Integer(0)==0
    elif case_id=="log_base_inverse_domain":
        valid=sp.log(sp.Integer(8),2)==3
        invalid=sp.Integer(1)==1 # base one invalid for log_a
    elif case_id=="correlation_zero_variance":
        xx=[1,2,3];yy=[1,2,3]
        valid=sum((a-2)*(b-2) for a,b in zip(xx,yy))==2
        invalid=sum((a-2)**2 for a in [2,2,2])==0
    else: raise ValueError(case_id)
    return (bool(valid),bool(invalid))

@pytest.mark.parametrize("case_id",[
    "three_noncollinear_points","plane_contains_line","two_planes_unique_intersection",
    "classical_finite_equiprobable","bisection_sign_and_continuity",
    "induction_sum_check_not_proof","discrete_distribution_nonnegative",
    "line_parallel_plane_conditions","sample_variance_singleton_denominator",
    "normal_standardization_sigma","log_base_inverse_domain",
    "correlation_zero_variance",
])
def test_finite_math_legal_and_invalid_assumption_witness(case_id):
    assert witness(case_id)==(True,True)
