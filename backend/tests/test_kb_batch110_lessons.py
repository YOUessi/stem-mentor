"""Full teacher-only lesson guard, curriculum source link, and retrieval non-disclosure."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest
from pydantic import ValidationError
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch110_lessons as B
from kb_batch110_lesson_authoring import UNITS
from app.deep_knowledge import DeepLesson,lessons
from app.deep_retrieval import student_evidence_lookup

@pytest.fixture(scope="module")
def batch():
    return B.build()

@pytest.mark.parametrize("i",range(8))
def test_teacher_only_full_lesson(i,batch):
    x=DeepLesson.model_validate(batch[0][i]);a=UNITS[i]
    assert x.id==f"math.hs.batch110.{i+1:02d}"
    assert x.kind==a["kind"] and x.title==a["title"]
    assert x.review.status=="REVIEW_PENDING"
    assert x.review.reviewer_id is None and x.review.review_record is None
    assert x.teacher_solution_visibility=="TEACHER_ONLY"
    assert x.provenance.permission=="PROJECT_AUTHORED"
    assert len(x.assumptions)>=2 and len(x.notation)>=2 and len(x.prerequisites)>=2
    assert len(x.worked_examples)==2 and len(x.hint_ladder)==3
    assert x.worked_examples[0].question!=x.worked_examples[1].question
    assert x.transfer.near and x.transfer.far
    assert len(x.counterexamples)==1 and x.counterexamples[0].explanation
    if x.kind=="theorem":assert len(x.proof_steps)>=3
    else:assert len(x.rationale_steps)>=3
    if x.kind=="concept":assert x.definition==x.statement
    link=batch[1]["editorial_source_crosswalk"][i]
    assert link["lesson_id"]==x.id
    assert link["source_key"]==a["source_key"]
    assert link["source_track_hint"]==("COMPULSORY" if i<4 else "ELECTIVE_A")
    assert link["official_math_atom_id"] is None
    assert not link["teacher_approved"] and not link["general_proof_certified"]

@pytest.mark.parametrize("i",range(8))
def test_student_evidence_no_teacher_solution_leak(i,batch):
    d=batch[0][i]
    x=student_evidence_lookup(d["title"])
    assert x["status"]=="NO_APPROVED_EVIDENCE"
    assert x["teacher_solution_exposed"] is False
    payload=json.dumps(x,ensure_ascii=False)
    for e in d["worked_examples"]:
        assert e["answer"] not in payload
        assert e["check"] not in payload

@pytest.mark.parametrize("i",range(8))
def test_forged_approval_rejected(i,batch):
    d=deepcopy(batch[0][i])
    d["review"]={"status":"APPROVED","reviewer_id":"fake",
                 "reviewed_at":"2026-11-12","review_record":"fake"}
    with pytest.raises(ValidationError):DeepLesson.model_validate(d)

@pytest.mark.parametrize("i",range(8))
def test_student_solution_escalation_rejected(i,batch):
    d=deepcopy(batch[0][i]);d["teacher_solution_visibility"]="STUDENT_VISIBLE"
    with pytest.raises(ValidationError):DeepLesson.model_validate(d)

@pytest.mark.parametrize("i",range(8))
def test_unlicensed_source_rejected(i,batch):
    d=deepcopy(batch[0][i]);d["provenance"]["permission"]="UNKNOWN"
    with pytest.raises(ValidationError):DeepLesson.model_validate(d)

@pytest.mark.parametrize("kind",["missing","unknown_mapping","fake_source","short_statement",
    "no_reasoning","fake_proof","no_counterexample","no_examples","fake_type","hint_repeated",
    "no_far_transfer","duplicate_source","mixed_tracks"])
def test_builder_negative_authoring_guards(kind):
    a=deepcopy(UNITS)
    if kind=="missing":a.pop()
    elif kind=="unknown_mapping":a[0]["curriculum_id"]="NO-SUCH-CURRICULUM"
    elif kind=="fake_source":a[0]["source_key"]="invented"
    elif kind=="short_statement":a[0]["statement"]="too thin"
    elif kind=="no_reasoning":a[2]["reasoning"]=[]
    elif kind=="fake_proof":a[2]["reasoning"][0]=("claim","no reason")
    elif kind=="no_counterexample":a[0]["negative"]=("tiny","tiny","tiny")
    elif kind=="no_examples":a[0]["examples"].pop()
    elif kind=="fake_type":a[0]["kind"]="external-verifier"
    elif kind=="hint_repeated":a[1]["hints"][1]=a[1]["hints"][0]
    elif kind=="no_far_transfer":a[0]["far"]="far"
    elif kind=="duplicate_source":a[0]["source_key"]=a[1]["source_key"]
    elif kind=="mixed_tracks":a[0]["source_key"]=a[4]["source_key"]
    with pytest.raises((ValueError,ValidationError)):
        B.build(units=a)

def test_full_pack_outputs_and_audit_consistency(batch):
    docs,audit=batch
    assert len(docs)==8 and len({x["id"] for x in docs})==8
    assert audit["number_of_new_deep_drafts"]==8
    assert audit["new_teacher_worked_examples"]==16
    assert audit["new_no_answer_hint_levels"]==24
    assert audit["new_near_and_far_transfer_tasks"]==16
    assert audit["new_counterexamples"]==8
    assert audit["new_proof_step_candidates"]==12
    assert audit["teacher_approvals"]==0
    assert audit["student_authoritative_releases"]==0
    assert audit["general_proof_certificates"]==0
    assert set(audit["official_seven_track_atom_denominators"].values())=={None}
    assert B.PACK.read_text(encoding="utf8")==B.serialize(docs)
    assert B.AUDIT.read_text(encoding="utf8")==B.serialize(audit)
    assert B.MD.read_text(encoding="utf8")==B.markdown(docs,audit)
    assert {x["id"] for x in docs}<={x.id for x in lessons()}

def test_no_forward_prerequisite_edges(batch):
    index={x["id"]:i for i,x in enumerate(batch[0])}
    for i,d in enumerate(batch[0]):
        for p in d["prerequisite_lesson_ids"]:
            assert p in index and index[p]<i
