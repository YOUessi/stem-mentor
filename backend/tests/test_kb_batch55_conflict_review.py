"""Independent exact math witnesses, unsafe-premise rejection and old-proof release gate."""
from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

import pytest

from app.kb_batch55_conflict_witnesses import (
    checked_conflict_witness as witness, ConditionsNotEstablished, OPS
)

ROOT = Path(__file__).resolve().parents[2]
S = importlib.util.spec_from_file_location("kb55_author", ROOT/"scripts/build_kb_batch55_conflict_review.py")
G = importlib.util.module_from_spec(S)
S.loader.exec_module(G)
AUDIT=G.build()


def test_frozen_inventory_and_nonapproval():
    assert AUDIT["conflict_count"] == 10 and AUDIT["conflicts_resolved"] == 0
    assert AUDIT["frozen_unverified_proof_steps"] == 538
    assert AUDIT["historical_proof_steps"] == 451
    assert AUDIT["p0_historical_steps_source_attested_not_math_certified"] == 127
    assert len(AUDIT["p0_priority_ids"]) == len(set(AUDIT["p0_priority_ids"])) == 127
    assert AUDIT["teacher_approved"] == AUDIT["student_published"] == 0
    assert len(AUDIT["official_atomic_denominator"]) == 7
    assert set(AUDIT["official_atomic_denominator"].values()) == {None}
    assert set(p["id"] for p in AUDIT["packets"]) == set(OPS)
    assert G.render_md(AUDIT).count("## math.hs.") == 10


@pytest.mark.parametrize("i",range(10))
def test_each_mathematical_conflict_kept_open_and_evidence_hashed(i):
    r=AUDIT["packets"][i]
    assert r["version_resolution"]=="UNRESOLVED"
    assert r["general_proof_status"]=="NOT_FORMALLY_CERTIFIED"
    assert r["teacher_review"]=="REVIEW_PENDING"
    assert r["student_publishable"] is False
    assert len(r["candidate_sha256"])==len(r["active_sha256"])==64
    assert r["human_review_question"]
    assert len(r["bounded_exact_cases"])==2
    assert all(x["status"] in ("FINITE_EXACT_CASE_ONLY","CONDITIONS_NOT_ESTABLISHED") for x in r["bounded_exact_cases"])
    assert all(x["result"]["status"]==x["status"] for x in r["bounded_exact_cases"])


@pytest.mark.parametrize("key",sorted(OPS))
def test_each_conflict_rejects_spurious_or_missing_fields(key):
    seed=G.FIXTURES[key][0]
    with pytest.raises(ConditionsNotEstablished):
        witness(key,**(seed|{"fabricated_teacher_approval":True}))
    for field in OPS[key]:
        omitted=dict(seed)
        omitted.pop(field)
        with pytest.raises(ConditionsNotEstablished):
            witness(key,**omitted)


@pytest.mark.parametrize("key",sorted(OPS))
def test_undetermined_student_correctness_never_certified(key):
    for case in G.FIXTURES[key]:
        try:
            r=witness(key,**case)
        except ConditionsNotEstablished:
            continue
        assert r["status"]=="FINITE_EXACT_CASE_ONLY"
        assert r["conflict_decision"]=="OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW"
        assert r["universal_proof_certified"] is False
        assert r["student_solution_verified"] is False
        assert r["teacher_approved"] is False


def test_composition_domain_zero_denominator():
    key="math.hs.function.composition-domain"
    assert witness(key,x=3,shift=-2)["composition"]==1
    assert witness(key,x=Fraction(1,2),shift=-2)["composition"]==Fraction(-2,3)
    with pytest.raises(ConditionsNotEstablished):witness(key,x=2,shift=-2)


def test_parity_polynomial_zero_both_and_mixed_neither():
    key="math.hs.function.parity"
    assert all(witness(key,coefficients=[0],domain="ALL_REAL")[k] for k in ("is_even","is_odd","zero_polynomial"))
    assert witness(key,coefficients=[0,1],domain="ALL_REAL")["is_odd"]
    assert witness(key,coefficients=[1,0,1],domain="ALL_REAL")["is_even"]
    assert not witness(key,coefficients=[1,1],domain="ALL_REAL")["is_even"]
    assert not witness(key,coefficients=[1,1],domain="ALL_REAL")["is_odd"]
    with pytest.raises(ConditionsNotEstablished):witness(key,coefficients=[0],domain="POSITIVE_REAL")


def test_piecewise_endpoint_double_branch_gap_and_matching():
    key="math.hs.function.piecewise"
    bad=witness(key,left_inclusive=True,right_inclusive=True,left_value=1,right_value=2)
    assert bad["ambiguous_if_different"] and bad["boundary_value"] is None
    okay=witness(key,left_inclusive=True,right_inclusive=True,left_value=2,right_value=2)
    assert okay["overlap"] and okay["boundary_value"]==2
    gap=witness(key,left_inclusive=False,right_inclusive=False,left_value=1,right_value=2)
    assert gap["gap"] and gap["boundary_defined"] is False
    with pytest.raises(ConditionsNotEstablished):witness(key,left_inclusive=1,right_inclusive=True,left_value=1,right_value=2)


def test_ivt_bracket_guarantees_existence_not_uniqueness_and_same_sign_is_inconclusive():
    key="math.hs.function.zero-ivt"
    yes=witness(key,coefficients=[-1,0,1],left=-2,right=0)
    assert yes["existence_guaranteed_by_bracket"] is True and yes["uniqueness"]=="UNDETERMINED"
    no=witness(key,coefficients=[-1,0,1],left=-2,right=2)
    assert no["existence_guaranteed_by_bracket"] is False
    assert no["same_sign_does_not_imply_no_roots"] is True


def test_point_line_distance_squared_and_irrational_rejection():
    key="math.hs.geometry.point-line-distance"
    p=witness(key,A=3,B=4,C=0,x=1,y=2)
    assert p["squared_distance"]==Fraction(121,25)
    assert p["exact_distance"]==Fraction(11,5)
    q=witness(key,A=1,B=1,C=0,x=1,y=0)
    assert q["squared_distance"]==Fraction(1,2) and q["exact_distance"] is None
    with pytest.raises(ConditionsNotEstablished):witness(key,A=0,B=0,C=1,x=1,y=2)


@pytest.mark.parametrize("n,p",[(0,0),(0,1),(2,0),(2,1),(3,Fraction(1,2)),(4,Fraction(1,3))])
def test_binomial_pmf_sum_one_for_valid_iid(n,p):
    key="math.hs.probability.binomial-distribution"
    probs=[witness(key,n=n,k=k,p=p,independent_identical=True)["probability"] for k in range(n+1)]
    assert sum(probs)==1


def test_hypergeometric_support_and_normalization():
    key="math.hs.probability.hypergeometric"
    p=witness(key,N=5,K=2,n=2,k=1,equal_likelihood_without_replacement=True)
    assert p["probability"]==Fraction(3,5)
    for N in range(2,9):
        for K in range(N+1):
            for n in range(N+1):
                assert sum(witness(key,N=N,K=K,n=n,k=k,equal_likelihood_without_replacement=True)["probability"] for k in range(n+1))==1


def test_regression_zero_slope_does_not_imply_no_nonlinear_pattern():
    key="math.hs.statistics.correlation-regression"
    r=witness(key,xs=[-1,0,1],ys=[1,0,1])
    assert r["slope"]==0 and r["correlation_squared"]==0
    assert r["nonlinear_relationship_excluded"] is False and r["causality"]=="NOT_ESTABLISHED"
    q=witness(key,xs=[1,2,3],ys=[7,7,7])
    assert q["slope"]==0 and q["correlation_defined"] is False
    with pytest.raises(ConditionsNotEstablished):witness(key,xs=[1,1,1],ys=[1,2,3])


def test_triangle_area_included_angle_and_degeneracy():
    key="math.hs.triangle.area-sine"
    p=witness(key,a=3,b=4,cos_included_angle=0,is_included_angle=True)
    assert p["area_squared"]==36
    for angle in (-1,1):
        with pytest.raises(ConditionsNotEstablished):
            witness(key,a=3,b=4,cos_included_angle=angle,is_included_angle=True)
    with pytest.raises(ConditionsNotEstablished):
        witness(key,a=3,b=4,cos_included_angle=0,is_included_angle=False)


def test_vector_norm_is_not_component_sum_norm():
    key="math.hs.vector.linear-operations"
    p=witness(key,u=[1,0],v=[0,1])
    assert p["sum_components"]==(1,1)
    assert p["norm_sum_squared"]==2 and p["norm_u_squared"]==p["norm_v_squared"]==1
    with pytest.raises(ConditionsNotEstablished):witness(key,u=[1,0],v=[1,2,3])


@pytest.mark.parametrize("key,fields",[
    ("math.hs.function.composition-domain",{"x":True,"shift":0}),
    ("math.hs.function.composition-domain",{"x":1.0,"shift":0}),
    ("math.hs.geometry.point-line-distance",{"A":0,"B":0,"C":0,"x":0,"y":0}),
    ("math.hs.geometry.point-line-distance",{"A":1.0,"B":1,"C":0,"x":0,"y":0}),
    ("math.hs.probability.binomial-distribution",{"n":2,"k":1,"p":-1,"independent_identical":True}),
    ("math.hs.probability.binomial-distribution",{"n":2,"k":1,"p":2,"independent_identical":True}),
    ("math.hs.probability.binomial-distribution",{"n":2,"k":1,"p":Fraction(1,2),"independent_identical":False}),
    ("math.hs.probability.hypergeometric",{"N":5,"K":2,"n":6,"k":1,"equal_likelihood_without_replacement":True}),
    ("math.hs.probability.hypergeometric",{"N":5,"K":2,"n":2,"k":1,"equal_likelihood_without_replacement":False}),
    ("math.hs.statistics.correlation-regression",{"xs":[0,1,2],"ys":[1,2]}),
    ("math.hs.statistics.correlation-regression",{"xs":[0,1,2],"ys":[1,2,True]}),
    ("math.hs.triangle.area-sine",{"a":0,"b":2,"cos_included_angle":0,"is_included_angle":True}),
    ("math.hs.triangle.area-sine",{"a":3,"b":4,"cos_included_angle":2,"is_included_angle":True}),
    ("math.hs.vector.linear-operations",{"u":[0,0],"v":[0,False]}),
    ("math.hs.function.zero-ivt",{"coefficients":[1,1],"left":1,"right":1}),
    ("math.hs.function.piecewise",{"left_inclusive":False,"right_inclusive":1,"left_value":2,"right_value":3}),
])
def test_refusal_on_unestablished_premises(key,fields):
    with pytest.raises(ConditionsNotEstablished):witness(key,**fields)


@pytest.mark.parametrize("mutation",[
    "remove_conflict","copy_conflict_id","fake_resolved","fake_teacher",
    "fake_step_certification","fake_student_step","fake_official_denominator",
    "missing_page","approved_page","remove_p0","duplicate_p0","alter_hash",
    "fake_p0_teacher","fake_p0_proof","fake_p0_publish","fake_p0_student_step",
    "fake_p0_finite_certificate","fake_conflict_evidence",
])
def test_frozen_source_mutation_rejected(mutation):
    risk=json.loads(G.RISK.read_text())
    proof=json.loads(G.PROOF.read_text())
    scope=json.loads(G.SCOPE.read_text())
    if mutation=="remove_conflict":risk["conflicts"].pop()
    elif mutation=="copy_conflict_id":risk["conflicts"][1]["id"]=risk["conflicts"][0]["id"]
    elif mutation=="fake_resolved":risk["summary"]["unresolved_conflicts"]=9
    elif mutation=="fake_teacher":proof["summary"]["teacher_approved"]=1
    elif mutation=="fake_step_certification":proof["summary"]["mathematical_proofs_formally_certified"]=1
    elif mutation=="fake_student_step":proof["summary"]["student_steps_verified"]=1
    elif mutation=="fake_official_denominator":scope["official_atomic_denominator"]["COMPULSORY"]=5
    elif mutation=="missing_page":scope["source_pages"].pop()
    elif mutation=="approved_page":scope["source_pages"][0]["full_page_manual_atomization"]="APPROVED"
    elif mutation=="remove_p0":proof["p0_review_queue"].pop()
    elif mutation=="duplicate_p0":proof["p0_review_queue"][1]["id"]=proof["p0_review_queue"][0]["id"]
    elif mutation=="alter_hash":risk["conflicts"][0]["candidate_sha256"]="no_sha"
    elif mutation=="fake_p0_teacher":proof["p0_review_queue"][0]["teacher_review"]="APPROVED"
    elif mutation=="fake_p0_proof":proof["p0_review_queue"][0]["proof_status"]="VERIFIED"
    elif mutation=="fake_p0_publish":proof["p0_review_queue"][0]["student_publishable"]=True
    elif mutation=="fake_p0_student_step":proof["p0_review_queue"][0]["student_step_verified"]=True
    elif mutation=="fake_p0_finite_certificate":proof["p0_review_queue"][0]["finite_instance_certificate"]=True
    elif mutation=="fake_conflict_evidence":risk["conflicts"][0]["evidence_status"]="MATH_CERTIFIED"
    with pytest.raises(ValueError):G.build(risk=risk,proof=proof,scope=scope)


@pytest.mark.parametrize("i",range(10))
def test_student_tutor_blocks_unapproved_conflict(i):
    from app.deep_retrieval import student_evidence_lookup
    from app.model_tutor_draft import draft_next_question
    row=AUDIT["packets"][i]
    query=row["human_review_question"]
    res=student_evidence_lookup(query,limit=3)
    assert res["status"]=="NO_APPROVED_EVIDENCE"
    assert res["candidates"]==[] and res["teacher_solution_exposed"] is False
    draft=draft_next_question(query,mode="GUIDE",help_requested=True,
        consent_to_cloud=True,operator_scope="EDITOR_LOCAL",
        provider_url="https://api.openai.com/v1/chat/completions",
        provider_model="offline-test-do-not-call")
    assert draft.status=="BLOCKED" and draft.reason=="NO_APPROVED_MATH_EVIDENCE"
    assert draft.model_called is False and draft.student_visible is False
    assert draft.question_draft is None


def test_generated_artifacts_are_replayable():
    data=json.dumps(AUDIT,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    assert G.OUTPUT_JSON.read_text()==data
    assert G.OUTPUT_MD.read_text()==G.render_md(AUDIT)
