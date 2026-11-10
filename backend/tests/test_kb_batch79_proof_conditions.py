"""Batch79 high-risk proof-source and mathematical assumption regression (Mac/CI)."""
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts"))
import build_kb_batch79_proof_conditions as B
from app.kb_batch79_math import OPS, GOOD, BAD, KEYS, check

@pytest.fixture(scope="module")
def package():
    return B.build()

def test_reproducible_original_review_source_and_no_false_math_certification(package):
    assert B.OUT.read_text(encoding="utf8")==B.dump(package)
    assert B.MD.read_text(encoding="utf8")==B.markdown(package)
    assert package["historical_step_count"]==538
    assert package["existing_batch78_guard_cards"]==16
    assert package["new_batch79_guard_cards"]==12
    assert package["total_distinct_high_risk_review_card_links"]==28
    assert package["official_atom_denominator"] is None
    assert package["teacher_approvals"]==package["formally_certified_proofs"]==package["student_published"]==0

@pytest.mark.parametrize("idx",range(12))
def test_proof_card_contains_guarded_original_three_step_reasoning(idx,package):
    c=package["review_cards"][idx]
    assert len(c["proof_steps"])==3 and [r["index"] for r in c["proof_steps"]]==[1,2,3]
    assert all(r["claim_and_reason"].strip() and "。" in r["claim_and_reason"] for r in c["proof_steps"])
    assert len(c["worked_examples"])==2 and len(c["hint_ladder"])==3
    assert tuple(c["hint_ladder"])==B.HINTS[idx]
    assert len(c["assumptions"])>=2 and c["invalid_boundary"] and c["common_wrong_method"]
    assert c["near_transfer"] and c["far_transfer"]
    assert c["teacher_solution_visibility"]=="TEACHER_ONLY" and c["review_status"]=="REVIEW_PENDING"
    assert c["formal_math_certification"]=="NOT_FORMALLY_VERIFIED" and c["finite_instance_status"]=="VERIFIED_FINITE_INSTANCE_ONLY"
    assert c["official_curriculum_atom_id"] is None and c["reviewer_id"] is None
    assert not c["student_publishable"] and not c["student_free_text_verified"]

@pytest.mark.parametrize("idx",range(12))
@pytest.mark.parametrize("key,value",[
    ("review_status","APPROVED"),
    ("teacher_solution_visibility","STUDENT"),
    ("reviewer_id","forged_teacher"),
    ("formal_math_certification","FORMALLY_VERIFIED"),
    ("student_publishable",True),
    ("student_free_text_verified",True),
    ("official_curriculum_atom_id","OFFICIAL-FAKE"),
    ("original_step_sha256","0"*64),
    ("invalid_boundary",""),
    ("far_transfer",""),
    ("source_kind","OFFICIAL_CERTIFIED_ATOM"),
    ("original_ledger_sha256","0"*64),
    ("curriculum_track_hint","ELECTIVE_A_CERTIFIED"),
    ("copyright_origin","UNKNOWN_LICENSE"),
    ("curriculum_standard_version","2017年版2020年修订-FAKE"),
    ("assumptions",["",""]),
    ("hint_ladder",["", "", ""]),
])
def test_forged_math_or_release_or_removed_counterexample_rejected(idx,key,value,package):
    cards=deepcopy(package["review_cards"])
    cards[idx][key]=value
    with pytest.raises(ValueError):
        B.validate(cards,B.read(B.PARENT))

@pytest.mark.parametrize("idx",range(12))
def test_invalid_positive_math_witness_swaps_rejected(idx,package):
    cards=deepcopy(package["review_cards"])
    cards[idx]["finite_valid"]=deepcopy(BAD[OPS[idx]])
    with pytest.raises(ValueError):
        B.validate(cards,B.read(B.PARENT))
    cards=deepcopy(package["review_cards"])
    cards[idx]["finite_invalid"]=deepcopy(GOOD[OPS[idx]])
    with pytest.raises(ValueError):
        B.validate(cards,B.read(B.PARENT))

@pytest.mark.parametrize("idx",range(12))
def test_historical_step_sha_tampering_rejected(idx,package):
    history=deepcopy(B.read(B.PARENT))
    chosen=package["review_cards"][idx]["linked_historical_step_id"]
    for row in history["proof_obligations"]:
        if row["id"]==chosen:
            row["original_step_sha256"]="0"*64
            break
    with pytest.raises(ValueError):
        B.build(ledger_override=history)

@pytest.mark.parametrize("op",OPS)
def test_exact_positive_math_case_and_invalid_assumption(op):
    state,e=check(op,GOOD[op])
    assert state=="VERIFIED_FINITE_INSTANCE" and e
    state,e=check(op,BAD[op])
    assert state=="CONDITIONS_NOT_ESTABLISHED" and e["failed_condition"]

@pytest.mark.parametrize("op",OPS)
def test_unknown_key_bools_floats_oversized_or_string_inputs_rejected(op):
    fixture=deepcopy(GOOD[op])
    mutated=deepcopy(fixture);mutated["extraneous"]=7
    with pytest.raises(ValueError):check(op,mutated)
    for garbage in (False,3.0,"7",100000):
        mutated=deepcopy(fixture)
        mutated[next(iter(KEYS[op]))]=garbage
        with pytest.raises(ValueError):check(op,mutated)
    with pytest.raises(ValueError):check(op,None)
    with pytest.raises(ValueError):check("unknown_"+op,fixture)

@pytest.mark.parametrize("x,y",list(product(range(-2,8),repeat=2)))
def test_amgm_conditions_and_exact_square_gap(x,y):
    status,evidence=check("amgm",{"a":x,"b":y})
    assert (status=="VERIFIED_FINITE_INSTANCE")== (x>0 and y>0)
    if x>0 and y>0:
        assert evidence["square_gap"]==(x-y)**2

@pytest.mark.parametrize("u,v",list(product(
    [[0,0],[1,2],[2,-1],[-2,3],[4,4]],repeat=2)))
def test_cauchy2_independent_lagrange_identity(u,v):
    status,ev=check("cauchy2",{"a":u,"b":v})
    assert status=="VERIFIED_FINITE_INSTANCE"
    assert ev["lagrange_identity_gap"] == (u[0]*v[1]-u[1]*v[0])**2

@pytest.mark.parametrize("a,q,n",list(product(range(-3,4),range(-3,4),range(1,9))))
def test_geometric_series_branch_never_divides_by_zero(a,q,n):
    status,ev=check("geometric_sum",{"a":a,"q":q,"n":n})
    assert (status=="VERIFIED_FINITE_INSTANCE")== (q!=1)
    if q!=1:assert ev["sum"]==sum(a*q**k for k in range(n))

@pytest.mark.parametrize("x",range(-8,9))
def test_composition_outer_domain_not_just_inner(x):
    status,ev=check("composition",{"x":x})
    assert (status=="VERIFIED_FINITE_INSTANCE")== (x!=2)
    if x!=2:assert ev["f_of_g"]==str(Q(1,x-2))

@pytest.mark.parametrize("A,B",list(product(
    [list(i for i in range(1,5) if mask&(1<<(i-1))) for mask in range(16)],repeat=2)))
def test_bayes_exhaustive_events_and_conditioning_denominator(A,B):
    status,ev=check("bayes",{"N":4,"A":A,"B":B})
    assert (status=="VERIFIED_FINITE_INSTANCE")==bool(A and B)
    if A and B:
        assert Q(ev["bayes_probability"])==Q(len(set(A)&set(B)),len(B))

@pytest.mark.parametrize("a,b,c",list(product(range(-3,5),range(-3,5),range(1,5))))
def test_bisection_opposite_sign_only(a,b,c):
    state,ev=check("bisection",{"a":a,"b":b,"c":c})
    expected=a<b and (a*a-c)*(b*b-c)<0
    assert (state=="VERIFIED_FINITE_INSTANCE")==expected
    if expected:assert ev["f_left"]*ev["f_right"]<0

@pytest.mark.parametrize("p,x,y",list(product(range(1,5),range(0,7),range(-8,9))))
def test_parabola_focus_directrix_squared_distance_identity(p,x,y):
    state,ev=check("parabola",{"p":p,"x":x,"y":y})
    expected=y*y==4*p*x
    assert (state=="VERIFIED_FINITE_INSTANCE")==expected
    if expected:
        assert ev["squared_distance_to_focus_and_directrix"] == (x-p)**2+y*y

@pytest.mark.parametrize("a,d,n",list(product(range(-3,4),range(-3,4),range(1,8))))
def test_arithmetic_sum_symmetrical_pairing(a,d,n):
    state,ev=check("arithmetic_sum",{"a":a,"d":d,"n":n})
    assert state=="VERIFIED_FINITE_INSTANCE"
    assert ev["sum"]==sum(a+d*k for k in range(n))

@pytest.mark.parametrize("D,E,F",list(product(range(-2,3),repeat=3)))
def test_circle_complete_square_proper_real_radius(D,E,F):
    state,ev=check("circle_square",{"D":D,"E":E,"F":F})
    expected=Q(D*D+E*E,4)-F>0
    assert (state=="VERIFIED_FINITE_INSTANCE")==expected
    if expected:assert Q(ev["radius_squared"])==Q(D*D+E*E,4)-F

@pytest.mark.parametrize("xs,ys",[
    ([0,1,2],[1,3,5]),([-1,0,1],[0,0,0]),([0,2,3],[3,2,1]),
    ([1,1,1],[1,3,5]),([0,1],[1,1]),([0,1],[1,2]),([1,2,3],[-2,3,8]),
])
def test_ols_normal_equations_and_constant_x_rejection(xs,ys):
    status,ev=check("ols",{"xs":xs,"ys":ys})
    assert (status=="VERIFIED_FINITE_INSTANCE")== (len(set(xs))>1)
    if len(set(xs))>1:
        beta=Q(ev["slope"]);alpha=Q(ev["intercept"])
        residual=[y-alpha-beta*x for x,y in zip(xs,ys)]
        assert sum(residual)==sum(x*r for x,r in zip(xs,residual))==0

@pytest.mark.parametrize("scale,shift",list(product(range(-3,4),range(-3,4))))
def test_variance_affine_scaling_independent_population_variance(scale,shift):
    xs=[-2,0,5]
    status,ev=check("variance_affine",{"xs":xs,"a":scale,"b":shift})
    assert status=="VERIFIED_FINITE_INSTANCE"
    assert Q(ev["transformed_variance"])==scale*scale*Q(ev["population_variance"])

@pytest.mark.parametrize("a,b,c",list(product(range(1,6),repeat=3)))
def test_cosine_law_rejects_degenerate_or_nonexistent_triangles(a,b,c):
    status,ev=check("cosine_law",{"a":a,"b":b,"c":c})
    good=(a+b>c and a+c>b and b+c>a)
    assert (status=="VERIFIED_FINITE_INSTANCE")==good
    if good:assert -1<Q(ev["cosine_of_included_angle"])<1

from test_attested_release_batch08 import offline_reviewer_fixture
@pytest.mark.parametrize("idx",range(12))
def test_review_cards_and_teacher_answers_do_not_leak_into_approved_student_index(idx,package,offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    c=package["review_cards"][idx]
    response=student_evidence_lookup(c["title"])
    text=json.dumps(response,ensure_ascii=False)
    assert {r["knowledge_id"] for r in response["candidates"]}<={doc.id}
    assert c["id"] not in text
    assert all(example["teacher_solution"] not in text for example in c["worked_examples"])
    assert response["teacher_solution_exposed"] is False
    assert response["unverified_content_exposed"] is False
