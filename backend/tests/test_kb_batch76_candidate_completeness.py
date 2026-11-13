"""Candidate denominators are distinct from official curricula and signed approvals."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json,sys,pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch76_progress as P

@pytest.fixture(scope="module")
def matrix():return P.build()

def test_progress_snapshots_are_deterministically_reproducible(matrix):
 assert P.OUT.read_text(encoding="utf8")==P.canon(matrix)
 assert P.MD.read_text(encoding="utf8")==P.report(matrix)

@pytest.mark.parametrize("i",range(26))
def test_all_26_candidate_source_and_draft_lineage(i,matrix):
 row=matrix["candidates"][i]
 assert row["source_sha256"] and len(row["source_sha256"])==64
 assert row["linked_review_only_teacher_draft_ids"]==sorted(row["linked_review_only_teacher_draft_ids"])
 assert row["linked_teacher_draft_count"]==len(row["linked_review_only_teacher_draft_ids"])
 assert row["official_knowledge_atom"] is None and row["source_certified"] is False
 assert row["teacher_approved"] is False and row["publishing_allowed"] is False

@pytest.mark.parametrize("i",range(8))
def test_all_new_8_lessons_have_full_draft_fields_but_no_proof_or_approval(i,matrix):
 item=matrix["lesson_completeness"][i]
 assert item["editorial_field_count"]==14 and item["editorial_field_presence_count"]==14
 assert item["number_of_worked_examples"]==2 and item["number_of_reasoned_steps"]>=4
 assert item["bounded_exact_case_verified"] is True
 assert item["teacher_review"]=="REVIEW_PENDING"
 assert not item["verified_universal_proof"]
 assert not item["teacher_approved"] and not item["student_publishable"]
 assert not item["prerequisites_linked_to_approved_ids"]

@pytest.mark.parametrize("field,value",[
 ("candidate_denominator",999),("teacher_approved",0),("approved_teacher_count",1),
 ("student_published_count",1),("formal_proof_certified_count",8),
 ("fully_teacher_atomized_pages",61),("comparison_sha256","f"*64),
 ("lesson_pack_sha256","f"*64),("candidate_without_draft",0)])
def test_false_coverage_claims_are_rejected(field,value,matrix):
 copied=deepcopy(matrix)
 if field=="teacher_approved":
  copied["candidates"][0]["teacher_approved"]=True
 else: copied[field]=value
 with pytest.raises((AssertionError,KeyError)):P.validate(copied)

@pytest.mark.parametrize("track",["COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"])
def test_tracks_preserve_unknown_official_denominator(track,matrix):
 assert matrix["official_full_denominators"][track] is None
 assert matrix["by_track"][track]["official_denominator"] is None

def test_unlinked_candidates_are_real_queue_not_fabricated_completed_coverage(matrix):
 pending=[x for x in matrix["candidates"] if not x["linked_teacher_draft_count"]]
 assert len(pending)==11
 assert all(not x["publishing_allowed"] for x in pending)
