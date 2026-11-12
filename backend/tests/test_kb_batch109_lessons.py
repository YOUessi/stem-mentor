"""Batch109 independent teacher-only DeepLesson regression and negative gates."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json,sys
import pytest
from pydantic import ValidationError
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch109_lesson_authoring import UNITS
import build_kb_batch109_lessons as B
from app.deep_knowledge import DeepLesson,lessons
from app.deep_retrieval import student_evidence_lookup

@pytest.fixture(scope="module")
def batch():
    return B.build()

@pytest.mark.parametrize("idx",range(10))
def test_actual_complete_teacher_lesson(idx,batch):
    x=DeepLesson.model_validate(batch[0][idx]);a=UNITS[idx]
    assert x.id==f"math.hs.batch109.{idx+1:02d}"
    assert x.title==a["title"] and x.statement==a["statement"]
    assert x.review.status=="REVIEW_PENDING"
    assert x.review.reviewer_id is None
    assert x.review.review_record is None
    assert x.provenance.permission=="PROJECT_AUTHORED"
    assert x.teacher_solution_visibility=="TEACHER_ONLY"
    assert len(x.assumptions)>=2 and len(x.notation)>=2
    assert len(x.worked_examples)==2 and x.worked_examples[0].question!=x.worked_examples[1].question
    assert len(x.hint_ladder)==3 and len(set(x.hint_ladder))==3
    assert x.transfer.near and x.transfer.far
    assert x.counterexamples[0].false_claim and x.counterexamples[0].explanation
    if x.kind=="theorem":
        assert len(x.proof_steps)>=3
        assert all(p.claim and p.reason for p in x.proof_steps)
    else:
        assert len(x.rationale_steps)>=3
        if x.kind=="concept":assert x.definition==x.statement
    link=batch[1]["editorial_source_crosswalk"][idx]
    assert link["lesson_id"]==x.id and link["source_key"]==a["source_key"]
    assert link["source_track_hint"]==("COMPULSORY" if idx<6 else "ELECTIVE_A")
    assert link["official_math_atom_id"] is None
    assert link["teacher_approved"] is False
    assert link["general_proof_certified"] is False

@pytest.mark.parametrize("idx",range(10))
def test_student_not_exposed_to_unapproved_teacher_answers(idx,batch):
    d=batch[0][idx]
    result=student_evidence_lookup(d["title"])
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert result["teacher_solution_exposed"] is False
    raw=json.dumps(result,ensure_ascii=False)
    for e in d["worked_examples"]:
        assert e["answer"] not in raw
        assert e["check"] not in raw

@pytest.mark.parametrize("idx",range(10))
def test_forged_review_still_rejected(idx,batch):
    d=deepcopy(batch[0][idx])
    d["review"]={"status":"APPROVED","reviewer_id":"fake",
                 "reviewed_at":"2026-11-12","review_record":"fake"}
    with pytest.raises(ValidationError):DeepLesson.model_validate(d)

@pytest.mark.parametrize("idx",range(10))
def test_teacher_solution_visibility_cannot_be_escalated(idx,batch):
    d=deepcopy(batch[0][idx]);d["teacher_solution_visibility"]="STUDENT_VISIBLE"
    with pytest.raises(ValidationError):DeepLesson.model_validate(d)

@pytest.mark.parametrize("idx",range(10))
def test_provenance_rejects_unlicensed_content(idx,batch):
    d=deepcopy(batch[0][idx]);d["provenance"]["permission"]="UNKNOWN"
    with pytest.raises(ValidationError):DeepLesson.model_validate(d)

@pytest.mark.parametrize("kind",["missing","unknown_mapping","fake_source",
     "too_short","empty_proof","missing_counterexample","missing_example",
     "fake_kind","fake_hint","broken_transfer","duplicate_source"])
def test_builder_rejects_invalid_authoring(kind):
    units=deepcopy(UNITS)
    if kind=="missing":units.pop()
    elif kind=="unknown_mapping":units[0]["curriculum_id"]="HS-NOPE"
    elif kind=="fake_source":units[0]["source_key"]="fabricated"
    elif kind=="too_short":units[0]["statement"]="unverified"
    elif kind=="empty_proof":units[0]["reasoning"]=[]
    elif kind=="missing_counterexample":units[0]["negative"]=["thin","tiny","wrong"]
    elif kind=="missing_example":units[0]["examples"].pop()
    elif kind=="fake_kind":units[0]["kind"]="arbitrary_verifier"
    elif kind=="fake_hint":units[0]["hints"][1]=units[0]["hints"][0]
    elif kind=="broken_transfer":units[0]["far"]="a"
    elif kind=="duplicate_source":units[0]["source_key"]=units[1]["source_key"]
    with pytest.raises((ValueError,ValidationError)):
        B.build(units=units)

def test_real_artifact_and_audit_consistency(batch):
    docs,audit=batch
    assert len(docs)==10 and len({x["id"] for x in docs})==10
    assert audit["number_of_new_deep_drafts"]==10
    assert audit["new_teacher_worked_examples"]==20
    assert audit["new_no_answer_hint_levels"]==30
    assert audit["new_near_and_far_transfer_tasks"]==20
    assert audit["new_counterexamples"]==10
    assert audit["new_finite_math_witnesses"]==10
    assert audit["teacher_approvals"]==0
    assert audit["proof_certificates"]==0
    assert audit["student_authoritative_releases"]==0
    assert set(audit["official_seven_track_atom_denominators"].values())=={None}
    assert audit["unreviewed_prior_prerequisite_labels"]==172
    assert audit["uncertified_prior_proof_steps"]==538
    assert audit["unresolved_prior_conflicts"]==10
    assert B.PACK.read_text(encoding="utf8")==B.serialize(docs)
    assert B.AUDIT.read_text(encoding="utf8")==B.serialize(audit)
    assert B.MD.read_text(encoding="utf8")==B.markdown(docs,audit)
    assert len(lessons())>=audit["all_deep_lessons"]
    assert {x["id"] for x in docs}<={x.id for x in lessons()}

def test_teacher_prerequisite_edges_are_backward_only(batch):
    ids={x["id"]:i for i,x in enumerate(batch[0])}
    for i,x in enumerate(batch[0]):
        for dep in x["prerequisite_lesson_ids"]:
            assert dep in ids and ids[dep]<i
