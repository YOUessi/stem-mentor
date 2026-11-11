"""Batch101: source-locked queue integrity, explicit non-approval, refusal cases."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "backend")]
import build_kb_batch101_review_queue as Q
from app.deep_retrieval import student_evidence_lookup

@pytest.fixture(scope="module")
def report():
    return Q.build()

def test_evidence_census_and_non_authoritative_coverage(report):
    assert report["page_census"] == 61
    assert report["source_anchor_census"] == 428
    assert len(report["page_evidence"]) == 61
    assert sum(r["project_anchor_count"] for r in report["page_evidence"]) == 428
    assert all(not r["student_publishable"] for r in report["page_evidence"])
    assert all(r["official_atom_count"] is None for r in report["page_evidence"])
    assert report["official_curriculum_atom_denominator"] is None
    assert len(report["official_atom_denominators_by_track"]) == 7
    assert all(x is None for x in report["official_atom_denominators_by_track"].values())
    assert report["human_atomized_pages"] == 0
    assert report["teacher_approved"] == report["student_published"] == 0
    Q.validate_report(report)

@pytest.mark.parametrize("position",range(61))
def test_every_source_page_has_unambiguous_nonapproved_state(report,position):
    row=report["page_evidence"][position]
    assert row["printed_page"] > 0
    assert row["full_page_human_atomization"] == "NOT_PERFORMED"
    assert row["missing_coverage_reason"] == "NO_COMPLETE_HUMAN_PAGE_REVIEW"
    assert row["teacher_approved"] == 0

@pytest.mark.parametrize("position",range(134))
def test_every_unpaired_theme_has_three_unapproved_candidates(report,position):
    row=report["semantic_pair_reviewer_queue"][position]
    assert row["pairwise_semantic_review"] == "NOT_PERFORMED"
    assert not row["math_equivalence_certified"]
    assert not row["teacher_approved"]
    assert row["official_atom_id"] is None
    assert not row["student_publishable"]
    assert len(row["source_line_sha256"]) == 64
    assert len(row["suggestions"]) <= 3
    assert len({s["candidate_id"] for s in row["suggestions"]}) == len(row["suggestions"])
    assert all(0 <= x["lexical_overlap_score"] <= 1 for x in row["suggestions"])
    assert all(x["lexical_overlap_score"] >= 0.12 for x in row["suggestions"])
    assert all(x["equivalence_status"] == "UNREVIEWED_NOT_CERTIFIED"
               for x in row["suggestions"])

@pytest.mark.parametrize("position",range(172))
def test_each_textual_prerequisite_is_unresolved_not_in_student_graph(report,position):
    row=report["text_prerequisite_reviewer_queue"][position]
    assert row["queue_id"].startswith(row["lesson_id"]+"#pre")
    assert row["approved_edge_id"] is None
    assert not row["teacher_approved"] and not row["student_graph_eligible"]
    assert len(row["suggestions"]) <= 3
    assert row["resolution"] in {"EDITORIAL_CANDIDATES_ONLY","MANUAL_DISCOVERY_REQUIRED"}
    for option in row["suggestions"]:
        assert option["lesson_id"] != row["lesson_id"]
        assert option["lexical_overlap_score"] >= 0.16
        assert not option["mathematical_implication_verified"]
        assert option["edge_type"] == "SUGGESTION_NOT_RESOLVED"

@pytest.mark.parametrize("word",[
    "课堂", "答案", "正态分布", "分母", "先修","相关系数",
])
def test_lexical_overlap_is_bounded_symmetric_and_only_heuristic(word):
    assert Q.lexical(word,word)==1.0
    assert Q.lexical(word,"不同的代数对象")==Q.lexical("不同的代数对象",word)
    assert 0 <= Q.lexical(word,"非空域下的代数") <= 1

@pytest.mark.parametrize("attack",[
    "fake_teacher_approval","fake_approved_prerequisite",
    "self_prerequisite","duplicate_prerequisite",
    "fake_pairwise_review","fake_equivalence","fake_official_denominator",
    "missing_unpaired","fake_page_completion","duplicate_semantic_id",
    "fake_student_release","fake_certified_suggestion",
])
def test_mutation_rejected_fail_closed(report,attack):
    x=deepcopy(report)
    t=x["text_prerequisite_reviewer_queue"]
    s=x["semantic_pair_reviewer_queue"]
    if attack=="fake_teacher_approval": x["teacher_approved"]=1
    elif attack=="fake_approved_prerequisite": t[0]["approved_edge_id"]="math.hs.fake"
    elif attack=="self_prerequisite": t[0]["suggestions"][0]["lesson_id"]=t[0]["lesson_id"]
    elif attack=="duplicate_prerequisite": t[1]["queue_id"]=t[0]["queue_id"]
    elif attack=="fake_pairwise_review": s[0]["pairwise_semantic_review"]="APPROVED"
    elif attack=="fake_equivalence": s[0]["math_equivalence_certified"]=True
    elif attack=="fake_official_denominator": x["official_atom_denominators_by_track"]["COMPULSORY"]=75
    elif attack=="missing_unpaired": x["remaining_unpaired_provisional_topics"]=0
    elif attack=="fake_page_completion": x["human_atomized_pages"]=61
    elif attack=="duplicate_semantic_id": s[1]["source_candidate_id"]=s[0]["source_candidate_id"]
    elif attack=="fake_student_release": x["student_published"]=1
    elif attack=="fake_certified_suggestion": s[0]["suggestions"][0]["equivalence_status"]="CERTIFIED"
    with pytest.raises(ValueError):
        Q.validate_report(x)

@pytest.mark.parametrize("attack",[
    "missing_anchor","duplicate_anchor","same_size_duplicate_coordinate",
    "out_of_census_page","out_of_range_line","conflicting_page_digest",
    "fake_approval","bad_source_sha",
])
def test_source_registry_mutations_are_rejected(attack):
    reg=Q.source_read(Q.REGISTRY)
    reg=deepcopy(reg)
    if attack=="missing_anchor": reg["rows"].pop()
    elif attack=="duplicate_anchor": reg["rows"].append(deepcopy(reg["rows"][0]))
    elif attack=="same_size_duplicate_coordinate": reg["rows"][1]=deepcopy(reg["rows"][0])
    elif attack=="out_of_census_page": reg["rows"][0]["printed_page"]=999
    elif attack=="out_of_range_line": reg["rows"][0]["pdfkit_line"]=-1
    elif attack=="conflicting_page_digest": reg["rows"][1]["source_page_pdfkit_sha256"]="f"*64
    elif attack=="fake_approval": reg["rows"][0]["teacher_review"]="APPROVED"
    elif attack=="bad_source_sha": reg["rows"][0]["source_line_sha256"]="oops"
    with pytest.raises(ValueError):
        Q.audit_source_pages(reg)

@pytest.mark.parametrize("attack",["remove_theme","duplicate_theme","fake_snapshot","fake_topic_approval","remove_unpaired"])
def test_historical_semantic_source_mutations_are_rejected(attack):
    source=deepcopy(Q.source_read(Q.SOURCE))
    previous=deepcopy(Q.source_read(Q.PREV))
    if attack=="remove_theme": source["provisional_candidate_backlog"].pop()
    elif attack=="duplicate_theme": source["provisional_candidate_backlog"][1]=deepcopy(source["provisional_candidate_backlog"][0])
    elif attack=="fake_snapshot": source["provisional_candidate_backlog"][0]["provisional_topic"]="篡改"
    elif attack=="fake_topic_approval": source["provisional_candidate_backlog"][0]["teacher_approval"]="FAKE"
    elif attack=="remove_unpaired": previous["remaining_unpaired_candidate_ids"].pop()
    with pytest.raises(ValueError):
        Q.semantic_queue(source,previous)

def test_authored_queue_files_are_reproducible_and_source_locked(report):
    Q.validate_report(report)
    assert Q.OUT.exists() and Q.MD.exists()
    assert json.loads(Q.OUT.read_text(encoding="utf8"))==report
    assert Q.MD.read_text(encoding="utf8")==Q.markdown(report)
    for path,expected in report["source_snapshots_sha256"].items():
        assert Q.digest(ROOT/path)==expected

@pytest.mark.parametrize("number",range(1,21))
def test_latest_teacher_draft_still_fails_closed_to_student(number):
    from app.deep_knowledge import lessons
    lesson=next(d for d in lessons() if d.id==f"math.hs.batch100.{number:02d}")
    assert lesson.review.status=="REVIEW_PENDING"
    result=student_evidence_lookup(lesson.title)
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert not result["teacher_solution_exposed"]
    blob=json.dumps(result,ensure_ascii=False)
    assert all(ex.answer not in blob for ex in lesson.worked_examples if len(ex.answer)>2)
