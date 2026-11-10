"""Batch80: all 428 K00 source anchors and 538 K07 proof obligations remain traceable.

Covers exact limited mathematical guards and non-leaking student retrieval.
These tests do not automatically approve any theorem, proof or teacher document.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch80_review_queue as REVIEW
import build_kb_batch80_eight_cards as CARDS
from app.kb_batch80_math import OPS, KEYS, check as math_check

@pytest.fixture(scope="module")
def artifacts():
    return REVIEW.build()

@pytest.fixture(scope="module")
def cards():
    return CARDS.build()

def test_regenerated_artifacts_are_byte_for_byte_deterministic(artifacts,cards):
    curriculum,proofs,markdown=artifacts
    assert REVIEW.OUT_CURR.read_text()==REVIEW.json.dumps(curriculum,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    assert REVIEW.OUT_PROOFS.read_text()==REVIEW.json.dumps(proofs,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    assert REVIEW.OUT_MD.read_text()==markdown
    assert CARDS.OUTPUT.read_text()==CARDS.dump(cards)
    assert CARDS.SUMMARY.read_text()==CARDS.markdown(cards)

def test_all_tracks_are_explicit_and_nonofficial(artifacts):
    curriculum,proofs,_=artifacts
    assert set(curriculum["by_track"])==set(REVIEW.TRACKS)
    assert curriculum["candidate_review_denominator"]==428
    assert curriculum["source_line_partition_count"]==484
    assert curriculum["nonanchor_triage_count"]==56
    assert curriculum["editorial_subspan_count"]==60
    assert curriculum["all_source_pages"]==61
    assert curriculum["official_atom_denominator"] is None
    assert sum(v["anchor_review_obligations"] for v in curriculum["by_track"].values())==428
    assert all(v["teacher_approved"]==0 and v["official_atom_denominator"] is None for v in curriculum["by_track"].values())
    assert curriculum["student_publishable_count"]==0
    assert proofs["historical_step_denominator"]==538
    assert proofs["p0_historical_steps"]==127
    assert proofs["review_only_p0_card_links"]==36
    assert proofs["p0_without_review_card"]==91
    assert proofs["unresolved_conflicts"]==10
    assert proofs["formally_certified_steps"]==proofs["teacher_approved_steps"]==0

@pytest.mark.parametrize("idx",range(428))
def test_every_anchor_has_exactly_one_source_segment_and_unreviewed_flag(idx,artifacts):
    curr,_,_=artifacts
    row=curr["anchor_review_queue"][idx]
    original=REVIEW.load_inputs()["anchors"]["anchors"][idx]
    assert row["source_line_sha256"]==original["source_line_sha256"]
    assert row["track"]==original["track_hint"]
    assert row["printed_page"]==original["printed_page"]
    assert row["pdfkit_line"]==original["pdfkit_line"]
    assert row["source_segment_range"][0]<=row["pdfkit_line"]<=row["source_segment_range"][1]
    assert row["parent_segment"] and row["status"]=="REVIEW_PENDING"
    assert row["official_atom_count"] is None
    assert row["student_publishable"] is False

@pytest.mark.parametrize("idx",range(538))
def test_every_proof_step_preserves_source_sha_and_noncertification(idx,artifacts):
    _,package,_=artifacts
    row=package["step_review_queue"][idx]
    old=REVIEW.load_inputs()["proofs"]["proof_obligations"][idx]
    assert row["id"]==old["id"]
    assert row["source_sha256"]==old["original_step_sha256"]
    assert row["formal_certification"]=="NOT_FORMALLY_VERIFIED"
    assert row["review_status"]=="REVIEW_PENDING"
    assert row["student_publishable"] is False
    if row["review_card_id"]:
        assert old["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE"

@pytest.mark.parametrize("key",tuple(REVIEW.FILES))
def test_mutation_of_any_frozen_upstream_artifact_fails_closed(key):
    originals=REVIEW.load_inputs()
    altered=deepcopy(originals)
    altered[key]["batch80_tampered"]=True
    with pytest.raises(ValueError,match="Frozen independent input altered"):
        REVIEW.build(altered)

@pytest.mark.parametrize("idx",range(10))
def test_historical_conflicts_remain_unresolved_and_source_fingerprinted(idx,artifacts):
    _,proofs,_=artifacts
    record=proofs["conflicts"][idx]
    assert record["status"]=="UNRESOLVED_NEEDS_INDEPENDENT_TEACHER"
    assert len(record["candidate_sha256"])==len(record["active_sha256"])==64
    assert record["id"] and record["math_risk_fields"]

@pytest.mark.parametrize("idx",range(8))
def test_eight_original_math_guard_cards_have_complete_teacher_review_fields(idx,cards):
    c=cards["review_cards"][idx]
    assert c["id"]==f"KB80-P{idx+1:02}"
    assert c["kind"] in ("THEOREM","METHOD")
    assert len(c["assumptions"])>=2 and len(c["proof_steps"])==3
    assert len(c["worked_examples"])==2 and len(c["hints"])==3
    assert c["near"] and c["far"] and c["wrong_method"] and c["boundary"]
    assert all(r["visibility"]=="TEACHER_ONLY" for r in c["worked_examples"])
    assert c["review_status"]=="REVIEW_PENDING"
    assert c["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert c["student_publishable"] is False
    assert c["student_free_text_verified"] is False
    assert c["official_curriculum_atom_id"] is None
    assert c["reviewer_id"] is None
    assert c["formal_math_certification"]=="NOT_FORMALLY_VERIFIED"
    assert c["finite_instance_check"]=="CONDITIONS_ONLY_NOT_GENERAL_PROOF"

@pytest.mark.parametrize("idx",range(8))
def test_teacher_guard_positive_case_and_invalid_case_are_independent(idx,cards):
    card=cards["review_cards"][idx]
    op=card["finite_op"]
    good,ev=math_check(op,card["valid"])
    bad,why=math_check(op,card["invalid"])
    assert good=="GUARD_PASSED_FINITE_CASE_ONLY" and ev
    assert bad=="CONDITIONS_NOT_ESTABLISHED" and why["failed_condition"]

@pytest.mark.parametrize("idx",range(8))
@pytest.mark.parametrize("corruption",("remove_assumption","remove_proof","remove_solution","replace_good_with_bad","replace_bad_with_good","forge_step_id"))
def test_teacher_card_tampering_is_rejected(idx,corruption):
    obj=deepcopy(CARDS.read(CARDS.AUTHOR))
    c=obj["cards"][idx]
    if corruption=="remove_assumption":
        c["assumptions"]=["unjustified"]
    elif corruption=="remove_proof":
        c["proof_steps"]=c["proof_steps"][:-1]
    elif corruption=="remove_solution":
        c["worked_examples"][0]["teacher_solution"]=""
    elif corruption=="replace_good_with_bad":
        c["valid"]=deepcopy(c["invalid"])
    elif corruption=="replace_bad_with_good":
        c["invalid"]=deepcopy(c["valid"])
    else:
        c["source_step"]="math.hs.fake#1"
    with pytest.raises(ValueError):
        CARDS.build(author=obj)

@pytest.mark.parametrize("op",OPS)
@pytest.mark.parametrize("bad", (False,3.14,"4",257))
def test_unsafe_or_inexact_parameter_types_are_rejected(op,bad,cards):
    witness=deepcopy(next(c["valid"] for c in cards["review_cards"] if c["finite_op"]==op))
    witness[next(iter(KEYS[op]))]=bad
    with pytest.raises(ValueError):
        math_check(op,witness)

@pytest.mark.parametrize("op",OPS)
def test_extra_and_missing_keys_rejected(op,cards):
    base=deepcopy(next(c["valid"] for c in cards["review_cards"] if c["finite_op"]==op))
    base["extra"]=1
    with pytest.raises(ValueError):math_check(op,base)
    del base["extra"]
    del base[next(iter(base))]
    with pytest.raises(ValueError):math_check(op,base)

@pytest.mark.parametrize("x,y",list(product(range(-4,5),repeat=2)))
def test_real_log_product_requires_both_individual_positive(x,y):
    st,_=math_check("log_product",{"a":2,"x":x,"y":y})
    assert (st=="GUARD_PASSED_FINITE_CASE_ONLY")==(x>0 and y>0)

@pytest.mark.parametrize("a,b,c,x",list(product(range(-2,3),repeat=4)))
def test_quadratic_completed_square_exactly_matches_original(a,b,c,x):
    st,out=math_check("quadratic_sign",{"a":a,"b":b,"c":c,"x":x})
    assert (st=="GUARD_PASSED_FINITE_CASE_ONLY")==(a!=0)
    if a:assert Q(out["completed_square_value"])==a*x*x+b*x+c

@pytest.mark.parametrize("u,v",list(product(range(-5,6),repeat=2)))
def test_absolute_value_triangle_equality_iff_same_sign(u,v):
    st,_=math_check("absolute_equality",{"u":u,"v":v})
    assert (st=="GUARD_PASSED_FINITE_CASE_ONLY")==(u*v>=0)

@pytest.mark.parametrize("counts",list(product(range(4),repeat=3)))
def test_counting_rule_applies_iff_all_branches_same_size(counts):
    st,ev=math_check("uniform_stage_count",{"counts":list(counts)})
    assert (st=="GUARD_PASSED_FINITE_CASE_ONLY")==(len(set(counts))==1)
    if len(set(counts))==1:assert ev["count_by_product"]==sum(counts)

@pytest.mark.parametrize("x,h",list(product(range(-5,6),range(-3,4))))
def test_parabola_tangent_has_exact_second_order_remainder(x,h):
    st,out=math_check("parabola_tangent",{"kind":0,"x0":x,"h":h})
    assert (st=="GUARD_PASSED_FINITE_CASE_ONLY")==(h!=0)
    if h:assert out["second_order_residual"]==h*h

@pytest.mark.parametrize("u,v",list(product(
    ([0,0],[1,0],[0,2],[2,-1],[-2,3]),repeat=2)))
def test_vector_angle_rejects_zero_and_satisfies_lagrange_identity(u,v):
    st,out=math_check("vector_angle",{"u":u,"v":v})
    assert (st=="GUARD_PASSED_FINITE_CASE_ONLY")==(u!=[0,0] and v!=[0,0])
    if u!=[0,0] and v!=[0,0]:
        assert out["cauchy_gap"]==(u[0]*v[1]-u[1]*v[0])**2

@pytest.mark.parametrize("subset",range(16))
@pytest.mark.parametrize("blocks",(
    [[1,2],[3,4]], [[1,3],[2,4]], [[1],[2],[3],[4]], [[1,2],[2,3,4]]))
def test_total_probability_counts_only_disjoint_exhaustive_partitions(subset,blocks):
    A=[i+1 for i in range(4) if subset>>i & 1]
    st,out=math_check("total_partition",{"N":4,"A":A,"blocks":blocks})
    valid=(blocks!=[[1,2],[2,3,4]])
    assert (st=="GUARD_PASSED_FINITE_CASE_ONLY")==valid
    if valid:assert Q(out["event_probability"])==Q(len(A),4)

@pytest.mark.parametrize("p,q,r",list(product(range(-3,4),range(-3,4),range(1,6))))
def test_double_angle_finite_unit_circle_identity(p,q,r):
    st,ev=math_check("double_angle_unit_circle",{"p":p,"q":q,"r":r})
    valid=p*p+q*q==r*r
    assert (st=="GUARD_PASSED_FINITE_CASE_ONLY")==valid
    if valid:
        assert Q(ev["sin_double"])**2+Q(ev["cos_double"])**2==1

from test_attested_release_batch08 import offline_reviewer_fixture

@pytest.mark.parametrize("idx",range(8))
def test_student_retrieval_blocks_unapproved_batch80_teacher_answers(idx,cards,offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    c=cards["review_cards"][idx]
    response=student_evidence_lookup(c["title"])
    serialized=json.dumps(response,ensure_ascii=False)
    assert {r["knowledge_id"] for r in response["candidates"]}<={doc.id}
    assert c["id"] not in serialized
    assert all(ex["teacher_solution"] not in serialized for ex in c["worked_examples"])
    assert response["teacher_solution_exposed"] is False
    assert response["unverified_content_exposed"] is False
