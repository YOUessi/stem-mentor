"""Batch122: source locks, 405 layout-cue disposition, exact mathematical cases,
teacher-only content isolation and rejection of forged completion."""
from __future__ import annotations
import copy, json, sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch122_semantic_census as s
import build_kb_batch122_depth as d
from app.deep_knowledge import public_summary
from kb_batch122_editorial_catalog import ROWS

CAND=json.loads(s.OUT.read_text(encoding="utf-8"))
QUEUE=json.loads(s.QUEUE.read_text(encoding="utf-8"))
COVER=json.loads(s.COVER.read_text(encoding="utf-8"))
DOCS=json.loads(d.OUT.read_text(encoding="utf-8"))
ORACLE=json.loads(d.MATH.read_text(encoding="utf-8"))
LOCKS=json.loads(s.LOCKS.read_text(encoding="utf-8"))

@pytest.mark.parametrize("row",CAND["candidates"],ids=lambda x:x["local_key"])
def test_source_pinned_candidate_with_valid_prerequisites_and_fail_closed_status(row):
    assert row["source"]["source_span_sha256"]==LOCKS[row["local_key"]]
    assert row["source"]["cue_kinds"]
    assert row["source"]["numbered_requirement_anchor"]==("NUMBERED_REQUIREMENT_CUE" in row["source"]["cue_kinds"])
    assert row["source"]["matching_layout_cues"]
    assert row["source"]["original_pdf_sha256"]==s.prior.evidence.PDF_SHA
    assert row["review_status"]=="REVIEW_PENDING" and row["teacher_evidence"] is None
    assert row["official_atom_id"] is None and row["official_atom_certified"] is False
    assert row["student_authoritative"] is False
    assert row["teacher_solution_visibility"]=="TEACHER_ONLY" and row["proof_verification"]=="UNVERIFIED"
    assert len(row["applicability"])>=22 and len(row["invalid_use"])>=20

@pytest.mark.parametrize("cue",QUEUE,ids=lambda x:x["cue_id"])
def test_every_source_layout_cue_has_auditable_disposition(cue):
    assert cue["course_track"] in set(s.prior.TRACKS)|{"ELECTIVE_UNASSIGNED"}
    assert cue["status"] in (
       "SOURCE_LINKED_EDITORIAL_CANDIDATE",
       "TOPIC_HEADING_NEEDS_CHILD_SCOPE_REVIEW",
       "SUBTOPIC_CUE_PENDING_CLAUSE_REVIEW",
       "NUMBERED_REQUIREMENT_AWAITING_EDITORIAL_ATOMIZATION")
    assert bool(cue["linked_candidate_ids"])==(cue["status"]=="SOURCE_LINKED_EDITORIAL_CANDIDATE")
    assert cue["official_atom_id"] is None and cue["teacher_approved"] is False
    assert cue["student_authoritative"] is False and len(cue["source_line_sha256"])==64

@pytest.mark.parametrize("track",sorted(COVER["per_track"]))
def test_official_atom_census_still_unknown_and_per_track_balanced(track):
    rec=COVER["per_track"][track]
    assert rec["official_atom_denominator"] is None and rec["official_coverage"] is None
    assert rec["layout_cues"]==rec["linked_cues"]+rec["unlinked_cues"]
    assert rec["teacher_approved"]==0

@pytest.mark.parametrize("lesson",DOCS,ids=lambda x:x["id"])
def test_eight_complete_original_lessons_are_teacher_only(lesson):
    assert lesson["teacher_review_status"]=="REVIEW_PENDING" and lesson["teacher_evidence"] is None
    assert lesson["student_authoritative"] is False and lesson["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert lesson["proof_step_machine_certified"] is False
    assert len(lesson["teacher_examples"])==2 and len(lesson["student_hint_ladder"])==3
    assert len(lesson["reasoned_steps"])>=3
    assert lesson["formal_definition_or_statement"] and lesson["symbols"] and lesson["applicability"]
    assert lesson["boundary_and_counterexample"] and lesson["typical_wrong_solution"] and lesson["why_wrong"]
    assert lesson["near_transfer"] and lesson["far_transfer"]

@pytest.mark.parametrize("tamper",[
 lambda z:z.update(official_atom_census_complete=True),
 lambda z:z.update(official_atom_total_denominator=175),
 lambda z:z.update(teacher_approved_count=1),
 lambda z:z.update(student_authoritative_count=1),
 lambda z:z.update(source_text_committed=True),
 lambda z:z.update(new_candidate_count=33),
 lambda z:z.update(cumulative_editorial_candidate_count=405),
 lambda z:z["candidates"][0].update(review_status="APPROVED"),
 lambda z:z["candidates"][0].update(teacher_evidence={"name":"spoof"}),
 lambda z:z["candidates"][0].update(student_authoritative=True),
 lambda z:z["candidates"][0].update(proof_verification="PROVED"),
 lambda z:z["candidates"][0].update(official_atom_certified=True),
 lambda z:z["candidates"][0].update(teacher_solution_visibility="PUBLIC"),
 lambda z:z["candidates"][0].update(course_track="ELECTIVE_A"),
 lambda z:z["candidates"][0].update(prerequisite_candidate_ids=["bogus"]),
 lambda z:z["candidates"][0].update(applicability="anything"),
 lambda z:z["candidates"][0].update(invalid_use="anything"),
 lambda z:z["candidates"][0]["source"].update(printed_page=99),
 lambda z:z["candidates"][0]["source"].update(source_span_sha256="bad"),
 lambda z:z["candidates"][0]["source"].update(matching_layout_cues=[]),
 lambda z:z["candidates"][0]["source"].update(numbered_requirement_anchor=False),
 lambda z:z["candidates"].append(copy.deepcopy(z["candidates"][0])),
 ])
def test_reject_fake_census_and_authority(tamper):
    data=copy.deepcopy(CAND);tamper(data)
    with pytest.raises(ValueError):s.validate(data)

@pytest.mark.parametrize("tamper",[
 lambda q:q[0].update(teacher_approved=True),
 lambda q:q[0].update(student_authoritative=True),
 lambda q:q[0].update(official_atom_id="FAKE-001"),
 lambda q:q[0].update(status="SOURCE_LINKED_EDITORIAL_CANDIDATE"),
 lambda q:q[0].update(cue_id="FAKE"),
 lambda q:q[0].update(source_line_sha256="bad"),
 lambda q:q[0].update(linked_candidate_ids=["fake"]),
 lambda q:q.pop(),
 ])
def test_reject_cue_queue_tampering(tamper):
    data=copy.deepcopy(QUEUE);tamper(data)
    with pytest.raises(ValueError):s.validate_queue(CAND,data,COVER)

@pytest.mark.parametrize("tamper",[
 lambda docs:docs[0].update(teacher_review_status="APPROVED"),
 lambda docs:docs[0].update(teacher_evidence={"teacher":"fake"}),
 lambda docs:docs[0].update(student_authoritative=True),
 lambda docs:docs[0].update(teacher_solution_visibility="STUDENT"),
 lambda docs:docs[0].update(proof_step_machine_certified=True),
 lambda docs:docs[0].update(math_example_exact_checks_passed=99),
 lambda docs:docs[0].update(teacher_examples=[]),
 lambda docs:docs[0].update(reasoned_steps=[]),
 lambda docs:docs[0].update(boundary_and_counterexample=""),
 lambda docs:docs[0].update(candidate_id="unknown"),
 ])
def test_reject_lesson_content_and_math_proof_spoofing(tamper):
    data=copy.deepcopy(DOCS);tamper(data)
    with pytest.raises(ValueError):d.validate(data)

@pytest.mark.parametrize("key",sorted(ORACLE["details_by_lesson"]))
def test_independent_exact_oracle_per_lesson(key):
    assert ORACLE["details_by_lesson"][key]=={"exact_worked_examples":2,"independent_negative_cases":1}
    assert d.exact_witnesses()["details_by_lesson"][key]==ORACLE["details_by_lesson"][key]

def test_no_invented_official_denominator_or_student_public_authority():
    assert COVER["total_layout_cues"]==405
    assert COVER["cues_linked"]==206 and COVER["cues_unlinked"]==199
    assert COVER["new_editorial_candidates"]==32
    assert COVER["cumulative_editorial_candidates"]==175
    assert COVER["official_atom_census_complete"] is False and COVER["official_atom_total_denominator"] is None
    assert ORACLE["exact_worked_cases_passed"]==16
    assert ORACLE["lesson_boundary_negative_checks_passed"]==8
    assert ORACLE["cross_topic_exact_boundary_checks_passed"]==8
    assert ORACLE["general_formal_theorems_proven"]==0 and ORACLE["teacher_approved"]==0
    assert s.validate(CAND) and s.validate_queue(CAND,QUEUE,COVER) and d.validate(DOCS)

def test_student_authoritative_retrieval_has_no_batch122_teacher_examples():
    public=json.dumps(public_summary(),ensure_ascii=False)
    assert "hs-semantic-pilot-122" not in public
    assert "kb_batch122_eight_depth_lessons" not in public
    assert "kb_batch122_semantic_proposals" not in public
    assert "teacher_examples" not in public
    assert "teacher_solution" not in public
