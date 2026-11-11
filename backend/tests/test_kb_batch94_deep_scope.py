"""Batch94 curriculum provenance, 14 substantive draft lessons, exact finite checks,
student privacy, review gate and malicious-input regressions. All Mac tests.
"""
from __future__ import annotations
from copy import deepcopy
import json
import pytest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch94_deep_scope as B
from kb_batch94_authoring import RECORDS
from app.kb_batch94_math_oracles import IDS,check,verify_all
from app.deep_knowledge import DeepLesson,lessons,coverage_report
from app.deep_retrieval import student_evidence_lookup,editor_draft_full,editor_draft_search,EditorOnlyError

@pytest.fixture(scope="module")
def pack():return B.build()

@pytest.fixture(scope="module")
def upstream():return B.B93.build()

def test_fourteen_complete_original_editor_drafts(pack):
    docs,scope=pack
    assert len(docs)==len(IDS)==14
    assert scope["new_individual_full_deep_drafts"]==14
    assert scope["still_without_any_individual_review"]==96
    assert scope["prior_individual_scope_pending"]==24
    assert scope["relation_compared_pending"]==166
    assert scope["remaining_without_pairwise_comparison"]==134
    assert scope["official_atom_denominator"] is None
    assert scope["fully_teacher_atomized_pages"]==0
    assert scope["teacher_approved"]==scope["student_authoritative_release"]==0
    assert scope["general_theorem_certificates"]==0
    assert scope["historical_uncertified_proof_steps"]==538
    assert scope["P0_historical_steps_without_teacher_cards"]==106
    assert scope["unresolved_math_conflicts"]==10

def test_seven_track_unknown_official_denominators(pack):
    scope=pack[1];rows=scope["per_track"]
    assert set(rows)==set(B.B93.TRACKS)
    assert sum(r["batch94_editor_deep_draft"] for r in rows.values())==14
    assert all(r["official_curriculum_atom_denominator"] is None for r in rows.values())
    assert rows["ELECTIVE_E"]["project_provisional_labels"]==0
    assert rows["ELECTIVE_E"]["official_curriculum_atom_denominator"] is None
    assert all(r["teacher_approved"]==0 for r in rows.values())

@pytest.mark.parametrize("i",range(14))
def test_full_schema_and_source_linkage(pack,upstream,i):
    d,scope=pack; lesson=DeepLesson.model_validate(d[i])
    link=scope["canonical_lesson_source_links"][i]
    source={x["candidate_id"]:x for x in upstream["provisional_candidate_ledger"]}
    assert lesson.id==f"math.hs.batch94.{i+1:02d}"
    assert len(lesson.worked_examples)==2
    assert len(lesson.hint_ladder)==3
    assert lesson.transfer.near!=lesson.transfer.far
    assert len(lesson.counterexamples)==1 and len(lesson.misconceptions)==1
    assert len(lesson.assumptions)>=2 and len(lesson.notation)>=3
    assert len(lesson.proof_steps)>=3 if lesson.kind=="theorem" else len(lesson.rationale_steps)>=3
    assert lesson.review.status=="REVIEW_PENDING" and lesson.review.reviewer_id is None
    assert lesson.teacher_solution_visibility=="TEACHER_ONLY"
    assert link["lesson_id"]==lesson.id
    assert link["source_candidate_id"]==RECORDS[i]["anchor"]
    assert source[link["source_candidate_id"]]["scope_audit_state"]=="NOT_YET_INDIVIDUALLY_AUDITED"
    assert link["source_line_sha256"]==source[link["source_candidate_id"]]["source_line_sha256"]
    assert link["official_atom_id"] is None
    assert link["general_theorem_certified"] is False and link["student_publishable"] is False
    assert link["finite_evidence"]["general_theorem_certified"] is False

@pytest.mark.parametrize("i",range(1,15))
def test_independent_finite_positive_and_invalid_witnesses(i):
    assert check(i)["finite_positive_case"] is True
    assert check(i)["invalid_premise_or_overgeneralization"] is True
    assert check(i)["general_theorem_certified"] is False

@pytest.mark.parametrize("bad",[0,15,-1,True,1.0,None,"1"])
def test_oracle_fail_closed_unknown_input(bad):
    with pytest.raises(ValueError):check(bad)

@pytest.mark.parametrize("i",range(14))
def test_student_deep_solution_never_retrievable(pack,i):
    doc=pack[0][i]
    live=next(x for x in lessons() if x.id==doc["id"])
    assert live.title==doc["title"]
    hits=editor_draft_search(doc["title"],scope="EDITOR_LOCAL",limit=20)
    assert any(h["knowledge_id"]==doc["id"] for h in hits)
    teacher_answer=doc["worked_examples"][0]["answer"]
    with pytest.raises(EditorOnlyError):editor_draft_full(doc["id"])
    with pytest.raises(EditorOnlyError):editor_draft_search(doc["title"])
    result=student_evidence_lookup(doc["title"])
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert result["teacher_solution_exposed"] is False
    assert result["unverified_content_exposed"] is False
    assert teacher_answer not in json.dumps(result,ensure_ascii=False)

@pytest.mark.parametrize("i",range(14))
def test_invalid_source_membership_or_duplicates_rejected(upstream,i):
    records=deepcopy(RECORDS)
    records[i]["anchor"]="NOT-A-CANONICAL-SOURCE"
    with pytest.raises(ValueError,match="canonical source"):
        B.build(records=records,baseline=upstream)

@pytest.mark.parametrize("i",range(14))
def test_missing_worked_example_rejected(upstream,i):
    records=deepcopy(RECORDS)
    records[i]["examples"]=records[i]["examples"][:1]
    with pytest.raises(ValueError,match="two original"):
        B.build(records=records,baseline=upstream)

@pytest.mark.parametrize("i",range(14))
def test_missing_counterexample_rejected(upstream,i):
    records=deepcopy(RECORDS)
    records[i]["negative"]=("","","")
    with pytest.raises(ValueError,match="counterexample"):
        B.build(records=records,baseline=upstream)

@pytest.mark.parametrize("i",range(14))
def test_missing_conditions_rejected(upstream,i):
    records=deepcopy(RECORDS)
    records[i]["assumptions"]=[]
    with pytest.raises(ValueError,match="assumptions"):
        B.build(records=records,baseline=upstream)

@pytest.mark.parametrize("i",range(14))
def test_forged_teacher_and_provenance_rejected(upstream,i):
    baseline=deepcopy(upstream)
    ident=RECORDS[i]["anchor"]
    row=next(r for r in baseline["provisional_candidate_ledger"] if r["candidate_id"]==ident)
    row["source_line_sha256"]="f"*64
    with pytest.raises(ValueError,match="SHA mismatch"):
        B.build(baseline=baseline)

@pytest.mark.parametrize("field,value",[
 ("official_atom_denominator",300),("teacher_approved",1),
 ("student_authoritative_release",14),("fully_teacher_atomized_pages",61),
 ("historical_uncertified_proof_steps",0),("unresolved_math_conflicts",0),
 ("still_without_any_individual_review",0),("remaining_without_pairwise_comparison",0)])
def test_historical_false_progress_rejected(upstream,field,value):
    baseline=deepcopy(upstream)
    baseline[field]=value
    with pytest.raises(ValueError,match="drift"):
        B.build(baseline=baseline)

def test_teacher_approval_cannot_be_self_declared(pack):
    for d in pack[0]:
        forged=deepcopy(d)
        forged["review"]={"status":"APPROVED","reviewer_id":"fake",
          "reviewed_at":"2026-11-11","review_record":"fabricated"}
        with pytest.raises(ValueError):DeepLesson.model_validate(forged)

def test_all_deep_drafts_unapproved_and_corpus_coverage(pack):
    report=coverage_report()
    assert report["deep_lesson_documents"]>=321
    assert report["review_statuses"]["REVIEW_PENDING"]>=321
    assert report["human_teacher_review_complete"] is False
    assert report["direct_student_teaching_enabled"] is False
    for link in pack[1]["canonical_lesson_source_links"]:
        assert link["teacher_approved"] is False
        assert link["student_publishable"] is False
