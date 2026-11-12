"""Ten complete, unapproved lessons: schemas, math limits, refusals, no leaks."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json,sys
import pytest
from pydantic import ValidationError
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch107_lessons as B
from kb_batch107_lesson_authoring import UNITS
from app.kb_batch107_math import check
from app.deep_knowledge import DeepLesson,lessons,curriculum
from app.deep_retrieval import student_evidence_lookup


@pytest.fixture(scope="module")
def output():
    return B.build()


@pytest.mark.parametrize("index",range(10))
def test_complete_distinct_math_lesson(index,output):
    docs,audit=output
    x=DeepLesson.model_validate(docs[index])
    authored=UNITS[index]
    assert x.id==f"math.hs.batch107.{index+1:02d}"
    assert x.title==authored["title"]
    assert x.statement==authored["statement"]
    assert x.curriculum_ids==[authored["curriculum_id"]]
    assert x.review.status=="REVIEW_PENDING"
    assert x.review.reviewer_id is None
    assert x.review.reviewed_at is None
    assert x.review.review_record is None
    assert x.teacher_solution_visibility=="TEACHER_ONLY"
    assert x.provenance.permission=="PROJECT_AUTHORED"
    assert len(x.notation)>=2 and len(x.assumptions)>=2
    assert len(x.worked_examples)==2
    assert x.worked_examples[0].question!=x.worked_examples[1].question
    assert all(len(e.steps)>=2 and len(e.check)>=15 for e in x.worked_examples)
    assert len(x.hint_ladder)==3
    assert len(set(x.hint_ladder))==3
    assert x.transfer.near and x.transfer.far
    assert x.counterexamples[0].false_claim and x.counterexamples[0].example
    if x.kind=="theorem":
        assert len(x.proof_steps)>=3
        assert all(p.claim and p.reason for p in x.proof_steps)
    else:
        assert len(x.rationale_steps)>=3
        assert x.definition if x.kind=="concept" else x.statement
    src=audit["source_to_engineering_crosswalk"][index]
    assert src["lesson_id"]==x.id
    assert src["source_key"]==B.SOURCE_KEYS[index]
    assert src["approved_official_atom_id"] is None
    assert src["teacher_approved"] is False
    assert src["general_proof_certified"] is False


@pytest.mark.parametrize("index",range(10))
def test_bounded_oracle_and_failure_witness(index,output):
    x=output[1]["source_to_engineering_crosswalk"][index]
    w=check(B.SOURCE_KEYS[index])
    assert x["bounded_math_evidence"]==w
    assert w["invalid_generalization_rejected"] is True
    assert w["finite_exact_positive_passed"] is True
    assert w["universal_proof_certified"] is False
    assert w["arbitrary_student_step_verified"] is False


@pytest.mark.parametrize("index",range(10))
def test_student_api_rejects_teacher_only_lesson(index,output):
    d=output[0][index]
    response=student_evidence_lookup(d["title"])
    assert response["status"]=="NO_APPROVED_EVIDENCE"
    assert response["teacher_solution_exposed"] is False
    serialized=json.dumps(response,ensure_ascii=False)
    for e in d["worked_examples"]:
        assert e["answer"] not in serialized
        assert e["check"] not in serialized


@pytest.mark.parametrize("index",range(10))
def test_forbid_fake_teacher_review(index,output):
    altered=deepcopy(output[0][index])
    altered["review"]={"status":"APPROVED","reviewer_id":"fabricated",
                       "reviewed_at":"2026-11-12","review_record":"fabricated proof"}
    with pytest.raises(ValidationError):
        DeepLesson.model_validate(altered)


@pytest.mark.parametrize("index",range(10))
def test_forbid_student_solution_visibility(index,output):
    altered=deepcopy(output[0][index])
    altered["teacher_solution_visibility"]="STUDENT_VISIBLE"
    with pytest.raises(ValidationError):
        DeepLesson.model_validate(altered)


@pytest.mark.parametrize("index",range(10))
def test_forbid_untrusted_lesson_provenance(index,output):
    altered=deepcopy(output[0][index])
    altered["provenance"]["permission"]="COPYRIGHT_UNKNOWN"
    with pytest.raises(ValidationError):
        DeepLesson.model_validate(altered)


@pytest.mark.parametrize("kind",["missing","duplicate","unknown_curriculum","unknown_kind",
                                  "missing_examples","duplicate_hints","short_statement",
                                  "empty_counterexample","thin_proof","forward_link"])
def test_builder_rejects_bad_authoring_input(kind):
    rows=deepcopy(UNITS)
    keys=list(B.SOURCE_KEYS)
    if kind=="missing":rows.pop()
    elif kind=="duplicate":rows.append(deepcopy(rows[0]))
    elif kind=="unknown_curriculum":rows[0]["curriculum_id"]="HS-MATH-NOT-REAL"
    elif kind=="unknown_kind":rows[0]["kind"]="LLM_CERTIFIED"
    elif kind=="missing_examples":rows[0]["examples"].pop()
    elif kind=="duplicate_hints":rows[0]["hints"][0]=rows[0]["hints"][1]
    elif kind=="short_statement":rows[0]["statement"]="true"
    elif kind=="empty_counterexample":rows[0]["negative"]=("a","b","c")
    elif kind=="thin_proof":rows[0]["reasoning"][0]["reason"]="guess"
    elif kind=="forward_link":keys[0]="arbitrary_claim"
    with pytest.raises((ValueError,ValidationError)):
        B.build(units=rows,source_keys=keys)


def test_complete_artifacts_and_approved_count_zero(output):
    docs,audit=output
    assert audit["number_of_new_deep_drafts"]==10
    assert audit["new_teacher_worked_examples"]==20
    assert audit["new_nonleaking_hint_levels"]==30
    assert audit["new_counterexamples"]==10
    assert audit["new_near_and_far_transfers"]==20
    assert audit["new_bounded_exact_witnesses"]==10
    assert audit["new_invalid_generalization_rejections"]==10
    assert audit["teacher_approvals"]==0
    assert audit["student_authoritative_releases"]==0
    assert set(audit["official_seven_track_denominators"].values())=={None}
    assert audit["unreviewed_prior_prerequisite_labels"]==172
    assert audit["uncertified_prior_proof_steps"]==538
    assert audit["unresolved_prior_conflicts"]==10
    assert B.PACK.read_text(encoding="utf8")==B.canonical(docs)
    assert B.AUDIT.read_text(encoding="utf8")==B.canonical(audit)
    assert B.MD.read_text(encoding="utf8")==B.markdown(docs,audit)
    assert len({x["id"] for x in docs})==10
    assert len({x.id for x in lessons()})==audit["with_new_drafts"]


def test_valid_teacher_only_prerequisite_graph(output):
    docs,audit=output
    known={x.id for x in lessons()}
    for x in docs:
        assert x["id"] not in x["prerequisite_lesson_ids"]
        assert len(x["prerequisite_lesson_ids"])==len(set(x["prerequisite_lesson_ids"]))
        assert all(p in known for p in x["prerequisite_lesson_ids"])


def test_provisional_source_never_claims_official_track_crosswalk(output):
    docs,audit=output
    assert len({x["source_key"] for x in audit["source_to_engineering_crosswalk"]})==10
    assert all(x["approved_official_atom_id"] is None for x in audit["source_to_engineering_crosswalk"])
    assert all(x["engineering_curriculum_id"] in {c["id"] for c in curriculum()}
               for x in audit["source_to_engineering_crosswalk"])


def test_zero_first_vector_does_not_require_false_scalar_multiple(output):
    from sympy import Matrix
    zero=Matrix([0,0,0]); nonzero=Matrix([1,2,3])
    assert zero.cross(nonzero)==Matrix([0,0,0])
    proof=output[0][4]["proof_steps"][-1]
    assert "先处理u=0情形" in proof["claim"]
    assert "当u=0时不需要将非零v表示为ku" in proof["reason"]
    assert check("cross_product")["finite_exact_positive_passed"] is True
