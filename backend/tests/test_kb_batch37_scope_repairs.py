"""Independent Batch37 teacher-only source, original maths and finite-domain checks."""
from __future__ import annotations
import copy, hashlib, json, sys
from fractions import Fraction
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.kb_batch37_review import staged_repairs, validate_seed, student_retrieval_projection, SOURCE, BASE
from app.kb_batch37_exact import FIELDS, VALID, INVALID, witness

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import author_kb_batch37_scope as author

DOCS=staged_repairs()
AUDIT=json.loads((ROOT/"docs/evaluation/KB_BATCH37_SCOPE_REPAIR_AUDIT.json").read_text(encoding="utf8"))
RECORDS={r["editorial_candidate_id"]:r for r in AUDIT["records"]}
ORIGINAL=json.loads(BASE.read_text(encoding="utf8"))
MIS={r["editorial_candidate_id"]:r for r in ORIGINAL["links"] if r["review_finding"]=="CLAIM_MISMATCH"}

def test_exact_historical_eight_and_all_three_build_artifacts():
    assert len(DOCS)==len(MIS)==8
    assert set(RECORDS)==set(MIS)
    for path,expected in author.build().items():
        assert path.read_text(encoding="utf8")==expected

@pytest.mark.parametrize("doc",DOCS,ids=lambda d:d.editorial_candidate_id)
def test_real_mathematical_scope_not_recycled_old_lesson(doc):
    r=RECORDS[doc.editorial_candidate_id]
    assert r["historic_mismatched_lesson"]==MIS[doc.editorial_candidate_id]["legacy_lesson_id"]
    assert r["new_staged_manuscript"]==doc.id
    assert r["original_scope_mismatch_still_recorded"] is True
    assert r["source_anchor"]=="PAGE_ONLY_NOT_CLAUSE_ATTESTED"
    assert r["official_clause_alignment_verified"] is False
    assert r["mathematical_equivalence_certified"] is False
    assert r["student_publishable"] is False
    assert len(doc.assumptions)>=1 and len(doc.reasoning_steps)>=3
    assert len(doc.worked_examples)==2
    assert len(doc.hint_ladder)==3 and len(set(doc.hint_ladder))==3
    assert doc.transfer.near != doc.transfer.far
    assert doc.review.status=="REVIEW_PENDING"
    assert doc.teacher_solution_visibility=="TEACHER_ONLY"
    assert doc.proof_verification=="NOT_FORMALLY_CERTIFIED"

@pytest.mark.parametrize("doc",DOCS,ids=lambda d:d.editorial_candidate_id)
def test_manuscript_content_sha_is_exact(doc):
    record=RECORDS[doc.editorial_candidate_id]
    payload=doc.model_dump(mode="json")
    actual=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
    assert record["manuscript_sha256"]==actual

@pytest.mark.parametrize("doc",DOCS,ids=lambda d:d.editorial_candidate_id)
def test_forged_teacher_approval_and_student_visibility_are_rejected(doc):
    src=doc.model_dump(mode="json")
    for wrong in ("APPROVED","REJECTED"):
        tampered=copy.deepcopy(src);tampered["review"]["status"]=wrong
        with pytest.raises(ValidationError):type(doc).model_validate(tampered)
    tampered=copy.deepcopy(src);tampered["student_publishable"]=True
    with pytest.raises(ValidationError):type(doc).model_validate(tampered)
    tampered=copy.deepcopy(src);tampered["teacher_solution_visibility"]="STUDENT"
    with pytest.raises(ValidationError):type(doc).model_validate(tampered)

@pytest.mark.parametrize("doc",DOCS,ids=lambda d:d.editorial_candidate_id)
def test_specific_counterexample_is_bound_to_misconception(doc):
    assert doc.counterexample.false_claim==doc.misconception.error
    assert doc.counterexample.explanation==doc.misconception.why_wrong
    assert len(doc.counterexample.example)>=12
    assert doc.worked_examples[0].answer != "" and doc.worked_examples[1].answer != ""

def test_seed_tamper_duplicate_and_wrong_target_rejected():
    seed=SOURCE.read_text(encoding="utf8")
    with pytest.raises(ValueError,match="drifted"):
        validate_seed(seed.replace("黄金分割","黄金比例",1))
    with pytest.raises(ValueError,match="exactly 8"):
        validate_seed(seed+seed.splitlines()[0]+"\n",check_pin=False)
    with pytest.raises(ValueError,match="exactly 8"):
        validate_seed(seed.replace("KB33-A-P052-A004","KB33-A-P052-A003",1),check_pin=False)

def test_student_retrieval_remains_empty_and_official_denominators_unknown():
    proj=student_retrieval_projection()
    assert proj["staged"]==8 and proj["student_documents"]==[] and proj["student_solutions"]==[]
    assert proj["student_published"]==0
    summary=AUDIT["summary"]
    assert summary["mismatch_goals_with_new_staged_manuscript"]==8
    assert summary["approved_by_teacher"]==summary["published_to_student"]==0
    assert all(value is None for value in summary["official_denominators"].values())

@pytest.mark.parametrize("operator",sorted(FIELDS))
def test_exact_guard_positive_and_negative_cases(operator):
    ok=witness(operator,VALID[operator])
    bad=witness(operator,INVALID[operator])
    assert ok["status"]=="FINITE_EXACT_CASE_ONLY" and ok["exact_value"]!=""
    assert ok["teacher_approved"]=="false" and ok["general_theorem_certified"]=="false"
    assert ok["student_freeform_step_verified"]=="false"
    assert bad["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("operator",sorted(FIELDS))
def test_exact_guard_rejects_unknown_missing_extra_and_llm_assertions(operator):
    assert witness(operator+"__LLM_APPROVED",VALID[operator])["status"]=="UNSUPPORTED"
    assert witness(operator,{})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    extra=dict(VALID[operator],llm_says_true=True)
    assert witness(operator,extra)["status"]=="CONDITIONS_NOT_ESTABLISHED"
    short=dict(VALID[operator]);short.pop(next(iter(short)))
    assert witness(operator,short)["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("operator",sorted(FIELDS))
def test_exact_guard_rejects_boolean_string_float_and_huge_int(operator):
    for key in FIELDS[operator]:
        for val in (True,"1",1.0,10**100):
            p=copy.deepcopy(VALID[operator]);p[key]=val
            assert witness(operator,p)["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_independent_exact_math_expected_values():
    assert witness("limit_ratio",VALID["limit_ratio"])["exact_value"]=="5/3"
    assert witness("project3",VALID["project3"])["exact_value"]=="3,0,0"
    assert witness("orthogonal_diag3",VALID["orthogonal_diag3"])["exact_value"]=="14"
    assert witness("lines3",VALID["lines3"])["exact_value"]=="NONPARALLEL:1"
    parallel=dict(VALID["lines3"],vx=1,vy=0,vz=0,qy=3,qz=4)
    assert witness("lines3",parallel)["exact_value"]=="PARALLEL:25"
    assert witness("weighted_means",VALID["weighted_means"])["exact_value"]=="40|30"
    assert witness("fixed_growth",VALID["fixed_growth"])["exact_value"]=="729"
    assert witness("golden_integer_residual",VALID["golden_integer_residual"])["exact_value"]=="1"
    assert witness("sphere_axes",VALID["sphere_axes"])["exact_value"]=="RIGHT_ANGLE:1*pi/2"
    antipodal=dict(VALID["sphere_axes"],qx=-1,qy=0,qz=0)
    assert witness("sphere_axes",antipodal)["exact_value"]=="ANTIPODAL:1*pi"
    # This only shows finite numbers; it is NOT a proof of any general theorem.
    assert Fraction(2,1)/(Fraction(1,20)+Fraction(1,60))==30
