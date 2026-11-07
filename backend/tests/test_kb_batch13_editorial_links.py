import copy
import json
from pathlib import Path
import pytest
from app.objective_proposals import (
    PATH, validate_proposals, editorial_review_queue, internal_review_counts
)
from app.standard_scope import source_inventory
from app.deep_knowledge import lessons

def raw():
    return json.loads(PATH.read_text(encoding="utf-8"))

def test_all_source_candidates_have_a_review_queue_row():
    data=editorial_review_queue()
    assert len(data["items"])==len(source_inventory()["items"])==132
    assert data["total_deep_draft_lessons"] == 235  # frozen Batch13 review scope
    assert len(lessons()) == 247  # Batch22 separately audited
    assert data["proposed_objectives"]>60
    assert data["proposed_edges"]>=data["proposed_objectives"]
    assert all(r["review_state"]=="QUEUED_FOR_HUMAN_REVIEW" for r in data["items"])

def test_no_human_teacher_or_student_evidence():
    stats=internal_review_counts()
    assert stats["official_atomic_denominator"] is None
    assert stats["official_coverage_percent"] is None
    assert stats["independent_teacher_approved_matches"]==0
    assert stats["student_published_knowledge_count"]==0
    assert sum(x["without_suggestion"] for x in stats["by_track"].values())==0

def test_source_rows_keep_link_field_empty():
    assert all(not row["linked_deep_lesson_ids"] for row in source_inventory()["items"])

def first_linked(payload):
    return next(x for x in payload["items"] if x["proposed_deep_lessons"])

@pytest.mark.parametrize("change", [
 "fake_approved","fake_student","fake_denominator","fake_coverage",
 "wrong_base_digest","remove_candidate","duplicate_candidate",
 "wrong_track","wrong_page","wrong_objective_digest",
 "fake_review","fake_scope","fake_proof","fake_grounding",
 "unknown_lesson","stale_lesson_hash","duplicate_lesson",
 "fabricated_total","fabricated_track_stat","fabricated_edges",
 "wrong_match_status","missing_review_questions"
])
def test_reject_integrity_violations(change):
    data=raw()
    row=first_linked(data)
    link=row["proposed_deep_lessons"][0]
    if change=="fake_approved":data["independent_teacher_approved_matches"]=1
    elif change=="fake_student":data["student_published_knowledge_count"]=1
    elif change=="fake_denominator":data["official_atomic_denominator"]=132
    elif change=="fake_coverage":data["official_coverage_percent"]=100
    elif change=="wrong_base_digest":data["base_source_digest_sha256"]="0"*64
    elif change=="remove_candidate":data["items"].pop()
    elif change=="duplicate_candidate":data["items"].append(copy.deepcopy(row))
    elif change=="wrong_track":row["candidate_track"]="ELECTIVE_E"
    elif change=="wrong_page":row["candidate_source_page"]=1
    elif change=="wrong_objective_digest":row["objective_snapshot_sha256"]="z"*64
    elif change=="fake_review":row["review_state"]="APPROVED"
    elif change=="fake_scope":link["scope"]="FULLY_COVERED"
    elif change=="fake_proof":link["math_proof_review"]="CERTIFIED"
    elif change=="fake_grounding":link["source_grounding_review"]="VERIFIED"
    elif change=="unknown_lesson":link["lesson_id"]="math.hs.invalid"
    elif change=="stale_lesson_hash":link["lesson_snapshot_sha256"]="f"*64
    elif change=="duplicate_lesson":row["proposed_deep_lessons"].append(copy.deepcopy(link))
    elif change=="fabricated_total":data["total_source_objective_candidates"]=1
    elif change=="fabricated_track_stat":data["by_track"][row["candidate_track"]]["suggestion_edges"]+=1
    elif change=="fabricated_edges":data["proposed_edges"]+=1
    elif change=="wrong_match_status":row["match_status"]="CERTIFIED"
    elif change=="missing_review_questions":row["review_questions"]=[]
    with pytest.raises((ValueError,KeyError)):
        validate_proposals(data)

def test_writes_are_not_exposed_through_student_api():
    from app.main import app
    paths=[r.path for r in app.routes]
    assert "/api/knowledge/standard-progress" in paths
    assert "/api/knowledge/editorial-proposals" not in paths
    assert not any("candidate-proposal" in x for x in paths)

def test_one_track_can_remain_without_lesson_suggestions():
    data=raw()
    assert len(data["by_track"])==7
    assert all(track["independently_approved"]==0 for track in data["by_track"].values())
