"""Batch95 source-locked 16 deep drafts; independent math, negative and access tests."""
from __future__ import annotations
from copy import deepcopy
import json
import sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch95_depth as B
from kb_batch95_authoring import RECORDS
from app.deep_knowledge import DeepLesson,lessons,coverage_report
from app.deep_retrieval import editor_draft_search,editor_draft_full,student_evidence_lookup,EditorOnlyError
from app.kb_batch95_math_oracles import (IDS,check,verify_all,probability_moments,
    real_log_domain,real_sqrt_disk_domain,geometric_nth,projection_y_length,
    triangle_linear_opt,sampled_curve,next_sync,classify_test_error)
from fractions import Fraction as Q

@pytest.fixture(scope="module")
def product():return B.build()
@pytest.fixture(scope="module")
def prior():return B.B94.build()[1]

def test_16_new_full_lessons_are_not_official_atoms(product):
    docs,report=product
    assert len(docs)==len(IDS)==16
    assert report["prior_full_deep_drafts"]==14
    assert report["new_individual_full_deep_drafts"]==16
    assert report["cumulative_new_deep_drafts_since_batch94"]==30
    assert report["still_without_any_individual_review"]==80
    assert report["remaining_without_pairwise_comparison"]==134
    assert report["official_atom_denominator"] is None
    assert all(v is None for v in report["official_atom_denominators_by_track"].values())
    assert report["fully_teacher_atomized_pages"]==0
    assert report["teacher_approved"]==report["student_authoritative_release"]==0
    assert report["unresolved_math_conflicts"]==10
    assert report["historical_uncertified_proof_steps"]==538
    assert report["P0_historical_steps_without_teacher_cards"]==106
    assert report["general_theorem_certificates"]==0

def test_track_counts_and_no_duplicate_source_links(product,prior):
    r=product[1]
    assert set(r["per_track"])==set(B.B93.TRACKS)
    assert sum(v["batch95_deep_drafts"] for v in r["per_track"].values())==16
    assert r["per_track"]["ELECTIVE_E"]["batch95_deep_drafts"]==0
    src={e["source_candidate_id"] for e in r["canonical_lesson_source_links"]}
    old={e["source_candidate_id"] for e in prior["canonical_lesson_source_links"]}
    assert src.isdisjoint(old)
    assert len(src)==16
    assert all(v["official_curriculum_atom_denominator"] is None for v in r["per_track"].values())

@pytest.mark.parametrize("i",range(16))
def test_structured_lesson_and_source_fingerprint(i,product):
    docs,report=product
    row=DeepLesson.model_validate(docs[i])
    link=report["canonical_lesson_source_links"][i]
    assert row.id==f"math.hs.batch95.{i+1:02d}"
    assert link["source_candidate_id"]==RECORDS[i]["anchor"]==IDS[i]
    assert link["source_line_sha256"] and len(link["source_line_sha256"])==64
    assert row.review.status=="REVIEW_PENDING" and row.review.reviewer_id is None
    assert row.teacher_solution_visibility=="TEACHER_ONLY"
    assert len(row.worked_examples)==2 and len(row.hint_ladder)==3
    assert len(row.counterexamples)==len(row.misconceptions)==1
    assert row.transfer.near!=row.transfer.far
    assert len(row.proof_steps)>=3 if row.kind=="theorem" else len(row.rationale_steps)>=3
    assert link["finite_evidence"]["general_theorem_certified"] is False
    assert link["teacher_approved"] is link["student_publishable"] is False

@pytest.mark.parametrize("i",range(1,17))
def test_exact_controlled_valid_and_invalid_cases(i):
    r=check(i)
    assert r["finite_positive_case"] is True
    assert r["invalid_premise_or_overgeneralization"] is True
    assert r["general_theorem_certified"] is r["teacher_approved"] is r["student_publishable"] is False

@pytest.mark.parametrize("invalid",[0,17,-1,True,1.0,None,"1"])
def test_unrecognized_math_oracle_rejected(invalid):
    with pytest.raises(ValueError):check(invalid)

@pytest.mark.parametrize("i",range(16))
def test_no_student_authority_and_teacher_solution_leak(i,product):
    doc=product[0][i]
    assert any(d.id==doc["id"] for d in lessons())
    hits=editor_draft_search(doc["title"],scope="EDITOR_LOCAL",limit=20)
    assert any(x["knowledge_id"]==doc["id"] for x in hits)
    with pytest.raises(EditorOnlyError):editor_draft_full(doc["id"])
    with pytest.raises(EditorOnlyError):editor_draft_search(doc["title"])
    student=student_evidence_lookup(doc["title"])
    assert student["status"]=="NO_APPROVED_EVIDENCE"
    assert student["teacher_solution_exposed"] is False
    assert student["unverified_content_exposed"] is False
    for example in doc["worked_examples"]:
        assert example["answer"] not in json.dumps(student,ensure_ascii=False)

@pytest.mark.parametrize("i",range(16))
def test_fake_unknown_or_prior_used_source_rejected(i,prior):
    modified=deepcopy(RECORDS)
    modified[i]["anchor"]="FAKE-CANDIDATE-2026"
    with pytest.raises(ValueError,match="source"):
        B.build(records=modified,prior=prior)

@pytest.mark.parametrize("i",range(16))
def test_missing_proof_conditions_rejected(i,prior):
    modified=deepcopy(RECORDS)
    modified[i]["assumptions"]=[]
    with pytest.raises(ValueError,match="assumptions"):
        B.build(records=modified,prior=prior)

@pytest.mark.parametrize("i",range(16))
def test_missing_worked_examples_rejected(i,prior):
    modified=deepcopy(RECORDS)
    modified[i]["examples"]=modified[i]["examples"][:1]
    with pytest.raises(ValueError,match="examples"):
        B.build(records=modified,prior=prior)

@pytest.mark.parametrize("i",range(16))
def test_missing_counterexample_rejected(i,prior):
    modified=deepcopy(RECORDS)
    modified[i]["negative"]=("","", "")
    with pytest.raises(ValueError,match="counterexample"):
        B.build(records=modified,prior=prior)

@pytest.mark.parametrize("i",range(16))
def test_missing_hint_hierarchy_rejected(i,prior):
    modified=deepcopy(RECORDS)
    modified[i]["hints"]=modified[i]["hints"][:2]
    with pytest.raises(ValueError,match="hints"):
        B.build(records=modified,prior=prior)

@pytest.mark.parametrize("i",range(16))
def test_forged_teacher_approval_cannot_be_accepted(i,product):
    doc=deepcopy(product[0][i])
    doc["review"]={"status":"APPROVED","reviewer_id":"fake_teacher",
        "reviewed_at":"2026-11-11","review_record":"self_signed"}
    with pytest.raises(ValueError):DeepLesson.model_validate(doc)

@pytest.mark.parametrize("field,value",[
    ("official_atom_denominator",300),("teacher_approved",16),
    ("student_authoritative_release",16),("fully_teacher_atomized_pages",61),
    ("historical_uncertified_proof_steps",0),("unresolved_math_conflicts",0),
    ("still_without_any_individual_review",0),("remaining_without_pairwise_comparison",0)
])
def test_fake_historical_progress_rejected(field,value,prior):
    modified=deepcopy(prior);modified[field]=value
    with pytest.raises(ValueError,match="drift"):
        B.build(prior=modified)

def test_real_domain_and_probability_rejection():
    assert probability_moments([(0,Q(1,2)),(2,Q(1,2))])==(1,1)
    for cases in ([(0,Q(3,5)),(1,Q(3,5))],[(0,Q(-1,2)),(1,Q(3,2))]):
        with pytest.raises(ValueError):probability_moments(cases)
    assert real_log_domain(2,1)
    for a,b in ((0,1),(1,1),(-1,1),(2,0),(2,-5),(float("nan"),1),(2,float("inf")),(True,3)):
        assert real_log_domain(a,b) is False
    assert real_sqrt_disk_domain(3,0,3)
    assert not real_sqrt_disk_domain(4,0,3)

def test_parameter_time_and_beat_phase_fail_closed():
    assert sampled_curve(Q(1,2))==(1,Q(1,4))
    with pytest.raises(ValueError):sampled_curve(-1)
    with pytest.raises(ValueError):sampled_curve(3)
    assert next_sync(4,6)==12
    assert next_sync(4,6,0,1) is None
    with pytest.raises(ValueError):next_sync(0,4)
    with pytest.raises(ValueError):next_sync(True,4)

@pytest.mark.parametrize("v",[
    10**450, Q(10**550,3), 1e308,
])
def test_exact_domains_no_float_overflow_or_infinite_squared_radius(v):
    assert real_log_domain(v,2)
    assert real_sqrt_disk_domain(v,0,v)
    assert not real_sqrt_disk_domain(v,v,v)

@pytest.mark.parametrize("a,b,phase_a,phase_b",[
    (2,3,-100,-100),(4,6,-20,-20),(7,11,100_000_003,-9_000_000_001),
    (12,18,8,14),(1,37,-77,8),(1,1,-50,-50),
])
def test_generalized_crt_offsets_and_minimality(a,b,phase_a,phase_b):
    actual=next_sync(a,b,phase_a,phase_b)
    from math import gcd,lcm
    compatible=(phase_b-phase_a)%gcd(a,b)==0
    if not compatible:
        assert actual is None
    else:
        assert isinstance(actual,int) and actual>=1
        assert (actual-phase_a)%a==0
        assert (actual-phase_b)%b==0
        assert actual<=lcm(a,b)
        assert not any((t-phase_a)%a==0 and (t-phase_b)%b==0
                       for t in range(1,min(actual,1000)))

def test_historical_batch94_real_guards_are_callable_and_fail_closed():
    from app.kb_batch94_math_oracles import valid_line_normal,induction_base_valid
    assert valid_line_normal(3,4) and valid_line_normal(Q(1,10),0)
    for a,b in ((0,0),(False,1),(float("nan"),1),(float("inf"),2)):
        assert not valid_line_normal(a,b)
    assert induction_base_valid(1,1) and induction_base_valid(3,6)
    for n,s in ((0,0),(1,2),(3,7),(True,1)):
        assert not induction_base_valid(n,s)

def test_reasoned_theorem_traces_and_editor_content_coverage(product):
    assert sum(d["kind"]=="theorem" for d in product[0])>=4
    for doc in product[0]:
        for e in doc["worked_examples"]:
            assert e["question"] and e["check"] and e["answer"]
    report=coverage_report()
    assert report["deep_lesson_documents"]>=337
    assert report["review_statuses"]["REVIEW_PENDING"]>=337
    assert report["human_teacher_review_complete"] is False
    assert report["direct_student_teaching_enabled"] is False
