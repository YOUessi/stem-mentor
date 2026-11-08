"""Batch39 substantive teacher-review records, exact finite cases, rejection and indexing gates."""
import copy, hashlib, json, sys
from fractions import Fraction
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.kb_batch39_review import (
    SOURCE, PRIOR, HISTORICAL, AUDIT, staged, validate_seed, RemainingPartial,
    student_retrieval_projection,
)
from app.kb_batch39_exact import FIELDS,VALID,INVALID,witness,_schedule
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import author_kb_batch39_remaining as author

DOCS=staged()
REPORT=json.loads(AUDIT.read_text(encoding="utf-8"))
PRIOR_DATA=json.loads(PRIOR.read_text(encoding="utf-8"))
HISTORY=json.loads(HISTORICAL.read_text(encoding="utf-8"))
HIST_IDS={r["editorial_candidate_id"]:r for r in HISTORY["links"] if r["review_finding"]=="PARTIAL_SCOPE"}
DOC_IDS={d.editorial_candidate_id for d in DOCS}

def test_full_partial_scope_coverage_and_outputs_reproducible():
    assert len(HIST_IDS)==27 and PRIOR_DATA["summary"]["remaining_partial_links"]==7
    assert DOC_IDS==set(PRIOR_DATA["partial_ids_remaining"])
    assert REPORT["summary"]["remaining_unaddressed"]==0
    assert REPORT["summary"]["prior_repaired"]==20 and REPORT["summary"]["new_repaired"]==7
    assert REPORT["summary"]["teacher_examples_new"]==14
    assert REPORT["summary"]["review_only_manuscripts_total"]==84
    assert REPORT["summary"]["legacy_deep_drafts"]==287
    assert REPORT["summary"]["unverified_official_clause_links"]==12
    assert REPORT["summary"]["historical_proof_steps_uncertified"]==538
    assert REPORT["summary"]["historical_conflicts_unresolved"]==10
    assert REPORT["summary"]["teacher_approved"]==REPORT["summary"]["student_published"]==0
    assert all(v is None for v in REPORT["summary"]["official_denominators"].values())
    assert REPORT["source_47_audit_sha256"]==hashlib.sha256(HISTORICAL.read_bytes()).hexdigest()
    assert REPORT["batch38_partial_audit_sha256"]==hashlib.sha256(PRIOR.read_bytes()).hexdigest()
    assert REPORT["seed_sha256"]==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    author.create(check=True)

@pytest.mark.parametrize("doc",DOCS,ids=lambda d:d.editorial_candidate_id)
def test_original_source_bound_curriculum_draft_not_certified(doc):
    original=HIST_IDS[doc.editorial_candidate_id]
    report=next(r for r in REPORT["records"] if r["editorial_candidate_id"]==doc.editorial_candidate_id)
    assert doc.id=="math.hs.editorial.batch39."+doc.editorial_candidate_id.lower().replace("-",".")
    assert original["review_finding"]=="PARTIAL_SCOPE" and not original["official_clause_alignment_verified"]
    assert not original["mathematical_equivalence_certified"]
    assert report["legacy_content_sha256"]==original["legacy_lesson_content_sha256"]
    assert report["legacy_lesson_id"]==original["legacy_lesson_id"]
    assert report["candidate_track"]==original["candidate_track"]
    assert report["official_clause_alignment_verified"] is False
    assert report["mathematical_equivalence_certified"] is False
    assert report["teacher_review"]=="REVIEW_PENDING"
    assert doc.review.status=="REVIEW_PENDING" and doc.review.reviewer_id is None
    assert doc.review.review_record is None and doc.review.reviewed_at is None
    assert doc.student_publishable is False and doc.teacher_solution_visibility=="TEACHER_ONLY"
    assert doc.proof_verification=="NOT_FORMALLY_CERTIFIED"
    assert doc.source_license=="PROJECT_AUTHORED"
    assert len(doc.reasoning_steps)==3 and all(s.reason for s in doc.reasoning_steps)
    assert len(doc.worked_examples)==2 and all(len(e.steps)==2 for e in doc.worked_examples)
    assert len(doc.hint_ladder)==len(set(doc.hint_ladder))==3
    assert all(len(h)>20 for h in doc.hint_ladder)
    assert doc.counterexample.false_claim==doc.misconception.error
    assert doc.counterexample.explanation==doc.misconception.why_wrong
    assert doc.transfer.near!=doc.transfer.far
    data=doc.model_dump(mode="json")
    digest=hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    assert report["manuscript_sha256"]==digest

@pytest.mark.parametrize("doc",DOCS,ids=lambda d:d.editorial_candidate_id)
def test_reject_forged_approval_and_solution_publication(doc):
    raw=doc.model_dump(mode="json")
    for field,value in (("student_publishable",True),("teacher_solution_visibility","STUDENT"),
                        ("proof_verification","FORMALLY_CERTIFIED"),("source_license","UNKNOWN")):
        edited=copy.deepcopy(raw);edited[field]=value
        with pytest.raises(ValidationError):RemainingPartial.model_validate(edited)
    edited=copy.deepcopy(raw);edited["review"]["status"]="APPROVED"
    with pytest.raises(ValidationError):RemainingPartial.model_validate(edited)
    edited=copy.deepcopy(raw);edited["review"]["reviewer_id"]="fake"
    with pytest.raises(ValidationError):RemainingPartial.model_validate(edited)

def test_seed_mutations_fail_closed():
    raw=SOURCE.read_text(encoding="utf-8")
    with pytest.raises(ValueError,match="SHA drift"):
        validate_seed(raw.replace("有限命题", "无限命题", 1))
    with pytest.raises(ValueError,match="exactly 7"):
        validate_seed(raw+raw.splitlines()[0]+"\n",check_pin=False)
    with pytest.raises(ValueError,match="exactly 7"):
        validate_seed(raw.replace("KB33-C-P065-A005","KB33-C-P065-A004",1),check_pin=False)
    bad=json.loads(raw.splitlines()[0]);bad["student_publishable"]=True
    poisoned=json.dumps(bad,ensure_ascii=False)+"\n"+"\n".join(raw.splitlines()[1:])+"\n"
    with pytest.raises(ValidationError):validate_seed(poisoned,check_pin=False)

def test_unpublished_projection_no_full_solution_or_false_curriculum_denominator():
    p=student_retrieval_projection()
    assert p["review_drafts"]==7 and p["student_documents"]==p["teacher_solutions_exposed"]==[]
    assert p["approved"]==p["student_published"]==0
    assert p["official_denominators"] is None
    assert REPORT["student_retrieval"]["student_documents"]==[]

@pytest.mark.parametrize("op",sorted(FIELDS))
def test_every_exact_case_has_boundary_and_provenance(op):
    good=witness(op,VALID[op]);bad=witness(op,INVALID[op])
    assert good["status"]=="FINITE_EXACT_CASE_ONLY" and good["exact_value"]
    assert good["citation_id"]=="kb-batch39-"+op
    assert bad["status"]=="CONDITIONS_NOT_ESTABLISHED"
    for k in ("teacher_approved","student_freeform_step_verified","general_theorem_certified","inference_certified"):
        assert good[k]=="false"
    assert witness(op+"___LLM_APPROVED",VALID[op])["status"]=="UNSUPPORTED"

@pytest.mark.parametrize("op",sorted(FIELDS))
def test_extra_unknown_missing_wrong_types_bounded_finite_inputs_rejected(op):
    sample=VALID[op]
    assert witness(op,{})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert witness(op,dict(sample,model_approved=True))["status"]=="CONDITIONS_NOT_ESTABLISHED"
    missing=dict(sample);missing.pop(next(iter(missing)))
    assert witness(op,missing)["status"]=="CONDITIONS_NOT_ESTABLISHED"
    for key in FIELDS[op]:
        for value in (True,1.5,"1",10**50):
            poison=dict(sample);poison[key]=value
            assert witness(op,poison)["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_frozen_independent_exact_values():
    expected={"finite_propositional":"1|1","response_mean_gap":"-10",
              "conditional_group_weight":"20","equal_temperament_octaves":"1760",
              "reflection_translation_order":"-1,3|-3,3",
              "pinhole_project":"3,6","round_robin_schedule":"5|10"}
    assert set(FIELDS)==set(expected)
    for op,value in expected.items():
        assert witness(op,VALID[op])["exact_value"]==value

@pytest.mark.parametrize("n",range(2,31))
def test_round_robin_edge_cover_every_pair_once_no_same_round_duplicate(n):
    schedule=_schedule(n)
    assert len(schedule)==(n-1 if n%2==0 else n)
    edges=[x for round_ in schedule for x in round_]
    assert set(edges)=={(a,b) for a in range(n) for b in range(a+1,n)}
    assert len(edges)==len(set(edges))==n*(n-1)//2
    for round_ in schedule:
        players=[p for edge in round_ for p in edge]
        assert len(players)==len(set(players))
        assert len(round_)==n//2
    assert witness("round_robin_schedule",{"teams":n})["exact_value"]==f"{len(schedule)}|{len(edges)}"

def test_mathematical_counterexamples_are_independently_checkable():
    # finite logic: p alone has models with both values of q, hence cannot entail q or not-q.
    assert witness("finite_propositional",{"include_p":1,"include_imp":0})["exact_value"]=="2|0"
    # one extra known response from the four-person finite population changes the conditional arithmetic.
    assert witness("response_mean_gap",dict(VALID["response_mean_gap"],responded=4))["exact_value"]=="0"
    # missing-response inference ambiguity: same observed [10,10], totals change if missing [0,0] vs [100,100].
    assert Fraction(10+10+0+0,4)==5
    assert Fraction(10+10+100+100,4)==55
    assert witness("equal_temperament_octaves",{"f0":440,"steps":12})["exact_value"]=="880"
    assert witness("equal_temperament_octaves",{"f0":440,"steps":-12})["exact_value"]=="220"
    assert witness("reflection_translation_order",dict(VALID["reflection_translation_order"],dx=0))["exact_value"]=="-2,3|-2,3"
    assert witness("pinhole_project",{"f":2,"x":1,"y":0,"z":2})["exact_value"]=="1,0"
    assert witness("pinhole_project",{"f":2,"x":1,"y":0,"z":4})["exact_value"]=="1/2,0"
    assert witness("pinhole_project",{"f":2,"x":1,"y":0,"z":0})["status"]=="CONDITIONS_NOT_ESTABLISHED"
