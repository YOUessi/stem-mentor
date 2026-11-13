"""Batch41: independent mathematical boundary tests, source guard and student privacy."""
from __future__ import annotations
import copy
import hashlib
import json
import pytest
from pydantic import ValidationError
from app.kb_batch41_core_review import (
    staged,source_goals,validate_seed,student_retrieval_projection,Lesson,
    build,audit,SOURCE,SEED_SHA,EDITORIAL_FILES,MANUSCRIPT,REPORT)
from app.kb_batch41_exact import FIELDS,VALID,INVALID,witness

DOCS=staged()
EXPECTED_EXACT={
"set_complement_mask":"2","amgm_square_gap":"25","inequality_scale":">",
"quadratic_roots_count":"2","radical_fraction_domain":"DEFINED",
"log_product_powers":"5","classical_probability":"1/2","event_union":"2/3",
"event_independent":"true","weighted_population_mean":"5",
"sample_variance_unbiased_2":"2","arithmetic_term":"-1","arithmetic_sum":"24",
"geometric_sum":"20","complex_division":"0|1","plane_normal_dot":"true",
"square_increase":"8",
}
def test_full_authored_batch_is_frozen_and_reproducible():
    assert len(DOCS)==29
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SEED_SHA
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in EDITORIAL_FILES.values())
    build(check=True)
    assert MANUSCRIPT.is_file() and REPORT.is_file()
    assert len({d.goal for d,_ in DOCS})==29
    assert {s["source"] for _,s in DOCS}=={"kb31","kb32"}

def test_counts_are_editorial_only_and_never_official_denominators():
    report=audit()
    summary=report["summary"]
    assert summary["by_track"]=={"COMPULSORY":25,"SELECTIVE_COMPULSORY":4}
    assert summary["draft_manuscripts"]==29
    assert summary["teacher_examples"]==58 and summary["counterexamples"]==29
    assert summary["hint_levels"]==87 and summary["near_far_transfers"]==58
    assert summary["teacher_approved"]==summary["student_published"]==0
    assert all(v is None for v in summary["official_atomic_denominators"].values())
    assert len(report["records"])==29
    assert all(not r["official_clause_alignment_verified"] and not r["math_certified"] for r in report["records"])

@pytest.mark.parametrize("number",range(29))
def test_each_lesson_has_real_anchor_assumptions_reasoned_steps_and_two_checked_exercises(number):
    d,src=DOCS[number]
    assert d.goal==src["original_goal"]
    assert src["printed_page"] in set(range(15,29))|set(range(29,51))
    assert src["kind"] in ("concept","theorem","method")
    assert src["track"] in ("COMPULSORY","SELECTIVE_COMPULSORY")
    assert src["optional"]=="N"
    assert d.conditions and d.prerequisites and len(d.derivation)==3
    assert all(x.statement and x.reason for x in d.derivation)
    assert len(d.examples)==2 and all(len(x.steps)==2 and x.check for x in d.examples)
    assert len(set(d.hints))==3
    assert d.near!=d.far and d.error.counterexample and d.error.why_invalid
    assert d.status=="REVIEW_PENDING" and d.approved_reviewer is None
    assert d.teacher_solution_visibility=="TEACHER_ONLY"
    assert d.proof_status=="NOT_FORMALLY_CERTIFIED"
    assert d.source_license=="PROJECT_AUTHORED" and d.student_publishable is False

@pytest.mark.parametrize("number",range(29))
def test_each_draft_rejects_forged_teacher_approval_student_release_and_proof_certification(number):
    d,_=DOCS[number];original=d.model_dump(mode="json")
    for field,value in (("status","APPROVED"),("approved_reviewer","fake-reviewer"),
                        ("teacher_solution_visibility","STUDENT"),("student_publishable",True),
                        ("proof_status","FORMALLY_CERTIFIED"),("source_license","UNKNOWN")):
        tampered=copy.deepcopy(original);tampered[field]=value
        with pytest.raises(ValidationError):
            Lesson.model_validate(tampered)
    tampered=copy.deepcopy(original);tampered["examples"][0]["steps"]=["spoiled"]
    with pytest.raises(ValidationError):
        Lesson.model_validate(tampered)
    tampered=copy.deepcopy(original);tampered["made_up_official_id"]=True
    with pytest.raises(ValidationError):
        Lesson.model_validate(tampered)

@pytest.mark.parametrize("number",range(29))
def test_every_editorial_anchor_has_unique_source_fingerprint(number):
    d,src=DOCS[number]
    report=audit()["records"][number]
    assert report["source"]==src
    serialized=json.dumps(d.model_dump(mode="json"),sort_keys=True,ensure_ascii=False,separators=(",",":"))
    assert report["lesson_sha256"]==hashlib.sha256(serialized.encode()).hexdigest()
    assert report["teacher_approved"] is False and report["student_publishable"] is False

def test_source_drift_duplicates_and_unanchored_goals_fail_closed():
    raw=SOURCE.read_text(encoding="utf-8")
    with pytest.raises(ValueError,match="SHA drift"):
        validate_seed(raw.replace("空集与单元素集合","空集与单元素集",1))
    with pytest.raises(ValueError,match="Duplicate editorial goal"):
        validate_seed(raw+raw.splitlines()[0]+"\n",check_pin=False)
    entries=[json.loads(x) for x in raw.splitlines()]
    entries[0]["goal"]="这是一个未锚定到课标编辑候选的伪造学习目标"
    changed="\n".join(json.dumps(x,ensure_ascii=False) for x in entries)
    with pytest.raises(ValueError,match="Unanchored editorial goal"):
        validate_seed(changed,check_pin=False)

def test_no_teacher_explanations_in_student_projection():
    p=student_retrieval_projection()
    assert p["review_pending"]==29
    assert p["student_documents"]==[] and p["teacher_solutions_exposed"]==[]
    assert p["approved"]==p["student_published"]==0
    assert p["status"]=="UNPUBLISHED_REVIEW_ONLY"
    assert len(p["official_atomic_denominators"])==7
    assert all(v is None for v in p["official_atomic_denominators"].values())

@pytest.mark.parametrize("operator",sorted(FIELDS))
def test_bounded_exact_math_and_invalid_premises(operator):
    assert witness(operator,VALID[operator])=={
        "status":"FINITE_EXACT_CASE_ONLY","exact_value":EXPECTED_EXACT[operator],
        "general_theorem_certified":False,"student_freeform_step_verified":False,
        "teacher_approved":False,"student_publishable":False}
    bad=witness(operator,INVALID[operator])
    assert bad["status"]=="CONDITIONS_NOT_ESTABLISHED" and bad["exact_value"] is None

@pytest.mark.parametrize("operator",sorted(FIELDS))
def test_bounded_exact_math_rejects_hallucinated_unknown_missing_inputs(operator):
    assert witness(operator+"__approved",VALID[operator])["status"]=="UNSUPPORTED"
    assert witness(operator,{})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness(operator,{**VALID[operator],"teacher_approved":True})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    data=VALID[operator].copy();data.pop(next(iter(data)))
    assert witness(operator,data)["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness(operator,[])["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("operator",sorted(FIELDS))
def test_bounded_exact_math_fails_closed_on_bool_float_str_extreme(operator):
    for field in FIELDS[operator]:
        for value in [True,False,1.1,"2",None,10**50]:
            data=VALID[operator].copy();data[field]=value
            assert witness(operator,data)["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_specific_mathematical_regressions_and_counterexamples():
    # Positive-derivative sufficiency does not make x^3 derivative strictly positive at 0.
    assert 3*0**2==0
    assert all((b**3 > a**3) for a,b in ((-2,-1),(-1,0),(0,1),(1,2)))
    # Intersections cannot exceed individual events.
    assert witness("event_union",{"total":6,"a":1,"b":1,"intersection":2})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    # Geometric q=1 cannot use the rational nonzero-denominator formula.
    assert witness("geometric_sum",{"a1":9,"q":1,"n":4})["exact_value"]=="36"
    # Equal-probability hypothesis is *not* derived from finite sample count.
    assert witness("classical_probability",{"good":1,"total":2})["general_theorem_certified"] is False
    # With noncollinear plane directions, w in plane is not perpendicular.
    wrong=VALID["plane_normal_dot"].copy(); wrong.update(wx=1,wy=0,wz=0)
    assert witness("plane_normal_dot",wrong)["exact_value"]=="false"
    # Different probability models may have P(A∩B)=0 but A∩B nonempty (null event).
    # The implementation does not try to infer empty intersection from probability.
    assert witness("event_independent",{"total":4,"a":0,"b":2,"intersection":0})["exact_value"]=="true"
