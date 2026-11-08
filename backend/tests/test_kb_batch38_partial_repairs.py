"""Batch38: source-bound teacher manuscripts, independent math finite cases, negative security gates."""
import copy, hashlib, json, sys
from fractions import Fraction
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.kb_batch38_review import staged,validate_seed,student_retrieval_projection,SOURCE,AUDIT,BASE,PartialRepair
from app.kb_batch38_exact import FIELDS,VALID,INVALID,witness

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import author_kb_batch38_partial as author

DOCS=staged()
REPORT=json.loads(AUDIT.read_text(encoding="utf8"))
OLD=json.loads(BASE.read_text(encoding="utf8"))
PARTIAL={r["editorial_candidate_id"]:r for r in OLD["links"] if r["review_finding"]=="PARTIAL_SCOPE"}
INDEX={r["editorial_candidate_id"]:r for r in REPORT["records"]}

def test_frozen_historical_scope_and_reproducible_outputs():
    assert len(DOCS)==20 and len(PARTIAL)==27
    assert REPORT["summary"]["remaining_partial_links"]==7
    assert len(REPORT["partial_ids_remaining"])==7
    assert not set(REPORT["partial_ids_remaining"]) & set(INDEX)
    assert REPORT["source_audit_sha256"]==hashlib.sha256(BASE.read_bytes()).hexdigest()
    assert REPORT["seed_sha256"]==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    author.create(check=True)

@pytest.mark.parametrize("doc",DOCS,ids=lambda d:d.editorial_candidate_id)
def test_each_editorial_draft_has_provenance_and_no_student_authority(doc):
    assert doc.editorial_candidate_id in PARTIAL
    assert doc.editorial_candidate_id in INDEX
    original=PARTIAL[doc.editorial_candidate_id]
    assert original["review_finding"]=="PARTIAL_SCOPE"
    assert original["mathematical_equivalence_certified"] is False
    assert original["official_clause_alignment_verified"] is False
    assert doc.id=="math.hs.editorial.batch38."+doc.editorial_candidate_id.lower().replace("-",".")
    assert doc.review.status=="REVIEW_PENDING"
    assert doc.review.reviewer_id is None and doc.review.review_record is None
    assert doc.student_publishable is False and doc.teacher_solution_visibility=="TEACHER_ONLY"
    assert doc.proof_verification=="NOT_FORMALLY_CERTIFIED"
    assert doc.source_license=="PROJECT_AUTHORED"
    assert len(doc.notation)>=1 and len(doc.assumptions)>=1
    assert len(doc.reasoning_steps)==3 and all(s.reason for s in doc.reasoning_steps)
    assert len(doc.worked_examples)==2 and all(len(e.steps)==2 for e in doc.worked_examples)
    assert doc.counterexample.false_claim==doc.misconception.error
    assert doc.counterexample.explanation==doc.misconception.why_wrong
    assert len(doc.hint_ladder)==3 and len(set(doc.hint_ladder))==3
    assert doc.hint_ladder==author.HINTS[doc.editorial_candidate_id]
    assert all(len(hint)>=15 for hint in doc.hint_ladder)
    assert doc.transfer.near!=doc.transfer.far
    assert len(doc.boundaries)>=2

@pytest.mark.parametrize("doc",DOCS,ids=lambda d:d.editorial_candidate_id)
def test_each_record_has_correct_canonical_sha(doc):
    hashed=json.dumps(doc.model_dump(mode="json"),ensure_ascii=False,sort_keys=True,separators=(",",":"))
    assert INDEX[doc.editorial_candidate_id]["record_sha256"]==hashlib.sha256(hashed.encode()).hexdigest()
    assert INDEX[doc.editorial_candidate_id]["official_clause_verified"] is False
    assert INDEX[doc.editorial_candidate_id]["legacy_equivalence_certified"] is False

@pytest.mark.parametrize("doc",DOCS,ids=lambda d:d.editorial_candidate_id)
def test_each_unreviewed_draft_rejects_forged_authorization(doc):
    src=doc.model_dump(mode="json")
    edits=[("student_publishable",True),("teacher_solution_visibility","STUDENT"),
           ("proof_verification","FORMALLY_CERTIFIED"),("source_license","UNKNOWN")]
    for field,value in edits:
        tampered=copy.deepcopy(src);tampered[field]=value
        with pytest.raises(ValidationError):
            PartialRepair.model_validate(tampered)
    tampered=copy.deepcopy(src);tampered["review"]["status"]="APPROVED"
    with pytest.raises(ValidationError):
        PartialRepair.model_validate(tampered)
    tampered=copy.deepcopy(src);tampered["review"]["reviewer_id"]="fake-reviewer"
    with pytest.raises(ValidationError):
        PartialRepair.model_validate(tampered)

def test_seed_tampering_duplicate_or_wrong_target_fail_closed():
    raw=SOURCE.read_text(encoding="utf8")
    with pytest.raises(ValueError,match="SHA drift"):
        validate_seed(raw.replace("矩阵乘法","矩阵运算",1))
    with pytest.raises(ValueError,match="20 unique"):
        validate_seed(raw+raw.splitlines()[0]+"\n",check_pin=False)
    with pytest.raises(ValueError,match="20 unique"):
        validate_seed(raw.replace("KB33-A-P052-A005","KB33-A-P052-A004",1),check_pin=False)
    malformed=json.loads(raw.splitlines()[0]);malformed["proof_verification"]="FORMALLY_CERTIFIED"
    tampered=json.dumps(malformed,ensure_ascii=False)+"\n"+"\n".join(raw.splitlines()[1:])+"\n"
    with pytest.raises(ValidationError):
        validate_seed(tampered,check_pin=False)

def test_student_projection_is_empty_despite_20_rich_teacher_drafts():
    p=student_retrieval_projection()
    assert p["review_drafts"]==20 and p["student_documents"]==[]
    assert p["teacher_solutions_exposed"]==[]
    assert p["approved"]==p["student_published"]==0
    assert p["official_denominators"] is None
    summary=REPORT["summary"]
    assert summary["teacher_worked_examples"]==40 and summary["new_counterexamples"]==20
    assert summary["deep_drafts_unchanged"]==287
    assert summary["teacher_approved"]==summary["student_published"]==0
    assert summary["unverified_historical_proof_steps"]==538
    assert all(x is None for x in summary["official_denominators"].values())

@pytest.mark.parametrize("op",sorted(FIELDS))
def test_each_bounded_math_witness_has_valid_and_invalid_premise(op):
    valid=witness(op,VALID[op])
    invalid=witness(op,INVALID[op])
    assert valid["status"]=="FINITE_EXACT_CASE_ONLY" and valid["exact_value"]
    assert invalid["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert valid["teacher_approved"]=="false" and valid["general_theorem_certified"]=="false"
    assert valid["student_freeform_step_verified"]=="false"

@pytest.mark.parametrize("op",sorted(FIELDS))
def test_each_witness_rejects_llm_hallucinated_fields_and_missing_data(op):
    assert witness(op+"__APPROVED",VALID[op])["status"]=="UNSUPPORTED"
    assert witness(op,{})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness(op,dict(VALID[op],llm_certified=True))["status"]=="CONDITIONS_NOT_ESTABLISHED"
    missing=dict(VALID[op]);missing.pop(next(iter(missing)))
    assert witness(op,missing)["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("op",sorted(FIELDS))
def test_reject_bool_float_string_large_integer_for_every_operand(op):
    for key in FIELDS[op]:
        for evil in (True,1.0,"1",10**50):
            p=dict(VALID[op]);p[key]=evil
            assert witness(op,p)["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_independent_expected_math_finite_values():
    exact_values={"factorial_sum":"8/3","matrix2_product":"3,2;1,1","row_scale_equation":"2x=6",
      "cramer_2x2":"2,1","density_linear":"1/4","chi_square_2":"4/5","quadratic_convex":"2",
      "linear_mvt":"3","square_affine_max":"3","kmeans_two":"1|2","leontief_scalar":"20",
      "fixed_compound_rate":"41/400","isometry2":"1","annuity":"2100/11"}
    assert set(exact_values)==set(FIELDS)
    for op,expected in exact_values.items():
        assert witness(op,VALID[op])["exact_value"]==expected

def test_kmeans_local_minimum_counterexample_exact_rational():
    data=(0,1,2,3,5)
    def cost(clusters):
        result=Fraction()
        for cluster in clusters:
            mu=Fraction(sum(cluster),len(cluster))
            result+=sum(((Fraction(x)-mu)**2 for x in cluster),Fraction())
        return result
    local=cost((data[:2],data[2:]))
    better=cost((data[:3],data[3:]))
    assert local==Fraction(31,6)>better==Fraction(4,1)
    # centers 1/2,10/3 make each point closer to its assigned center
    left,right=Fraction(1,2),Fraction(10,3)
    assert all(abs(Fraction(x)-left)<=abs(Fraction(x)-right) for x in data[:2])
    assert all(abs(Fraction(x)-right)<=abs(Fraction(x)-left) for x in data[2:])

def test_core_mathematics_special_cases_and_opposite_orientation():
    assert witness("annuity",dict(VALID["annuity"],inum=0))["exact_value"]=="220"
    assert witness("fixed_compound_rate",dict(VALID["fixed_compound_rate"],m=1))["exact_value"]=="1/10"
    assert witness("isometry2",{"a":-1,"b":0,"c":0,"d":1})["exact_value"]=="-1"
    assert witness("cramer_2x2",{"a":1,"b":1,"c":2,"d":2,"u":3,"v":6})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness("annuity",{"amount":5,"inum":-1,"iden":1,"periods":2})["status"]=="CONDITIONS_NOT_ESTABLISHED"
