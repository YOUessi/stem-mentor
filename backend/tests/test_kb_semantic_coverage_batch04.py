"""Negative gates for open Batch04 gaps and new Batch05 draft candidates."""
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts"))
from audit_kb_semantic_coverage import GAPS, build, validate_gaps


def test_113_links_do_not_falsely_equal_full_curriculum():
    matrix=build()
    summary=matrix["summary"]
    assert summary["engineering_topic_denominator"]==113
    assert summary["deep_draft_documents"]>=86
    assert summary["linked_project_topics"]==113
    assert summary["known_partial_topic_count"]>=23
    assert summary["gap_draft_candidate_count"] + summary["gap_without_candidate_count"] == summary["known_partial_topic_count"]
    assert summary["other_linked_unreviewed_topic_count"]+summary["known_partial_topic_count"]==113
    assert summary["official_curriculum_atom_mapping_reviewed"]==0
    assert summary["explicit_official_elective_tracks_completed"]==0
    assert summary["student_draft_release_allowed"] is False
    assert summary["teacher_reviewed_complete"]==0
    assert summary["fully_formally_proven_natural_language_lessons"]==0


@pytest.mark.parametrize("topic",[
 "HS-MATH-001","HS-MATH-025","HS-MATH-026","HS-MATH-041","HS-MATH-042",
 "HS-MATH-045","HS-MATH-048","HS-MATH-056","HS-MATH-066","HS-MATH-067",
 "HS-MATH-069","HS-MATH-089","HS-MATH-091","HS-MATH-096"])
def test_semantic_gaps_are_open_and_have_specific_next_lesson(topic):
    rows={r["engineering_topic_id"]:r for r in build()["topics"]}
    assert rows[topic]["evidence_status"]=="GAP_DRAFT_CANDIDATE_UNREVIEWED"
    assert rows[topic]["gap_candidate_draft_present"] is True
    assert rows[topic]["gap_review_status"] == "OPEN"
    assert rows[topic]["recommended_next_lesson"].startswith("math.hs.")
    assert rows[topic]["curriculum_atom_officially_verified"] is False
    assert rows[topic]["teacher_approved_lesson_ids"]==[]


def test_semantic_report_does_not_make_unflagged_topics_auto_approved():
    data=build()
    for r in data["topics"]:
        assert r["curriculum_atom_officially_verified"] is False
        assert "APPROVED" not in r["evidence_status"]
        assert r["teacher_approved_lesson_ids"]==[]


@pytest.mark.parametrize("mutation",[
 lambda raw:raw["gaps"].append(copy.deepcopy(raw["gaps"][0])),
 lambda raw:raw["gaps"][0].update({"curriculum_id":"HS-MATH-999"}),
 lambda raw:raw["gaps"][0].update({"status":"CLOSED"}),
 lambda raw:raw.update({"scope":"OFFICIAL_COMPLETE"}),
 lambda raw:raw["gaps"][0].update({"recommended_lesson_id":"unknown"}),
])
def test_gap_catalog_fails_closed_on_forgery(mutation):
    raw=json.loads(GAPS.read_text(encoding="utf-8"))
    known={row["engineering_topic_id"] for row in build()["topics"]}
    mutation(raw)
    with pytest.raises(ValueError):
        validate_gaps(raw,known)


def test_coverage_snapshot_is_stable_and_remains_editorial():
    snapshot=json.loads((ROOT/"docs/evaluation/KB_SEMANTIC_COVERAGE_BATCH07.json").read_text(encoding="utf-8"))
    result=build()
    assert result==snapshot
    assert "CONSERVATIVE" in snapshot["scope"]
