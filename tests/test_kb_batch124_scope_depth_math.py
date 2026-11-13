"""Batch124: original line-locked concepts, rigorous teacher-only lessons,
non-atom review proposals and finite independent mathematics oracles.
All coverage/approval numbers remain fail-closed.
"""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch124_scope as k
import build_kb_batch124_depth as d
from kb_batch124_catalog import NONATOM,ROWS
from kb_batch124_deep_catalog import LESSONS
from app.deep_knowledge import public_summary

DATA=json.loads(k.OUT.read_text())
QUEUE=json.loads(k.QUEUE.read_text())
COV=json.loads(k.COVER.read_text())
DOC=json.loads(d.OUT.read_text())
ORACLE=json.loads(d.MATH.read_text())
LOCKS=json.loads(k.LOCKS.read_text())

@pytest.mark.parametrize("r",DATA["candidates"],ids=lambda a:a["local_key"])
def test_authored_atom_source_review_and_teacher_gate(r):
    assert r["local_key"] in LOCKS
    assert r["source"]["source_span_sha256"]==LOCKS[r["local_key"]]
    assert len(r["source"]["matching_layout_cues"])==1
    assert r["source"]["start_line"]==r["source"]["end_line"]
    assert r["official_atom_id"] is None and r["official_atom_certified"] is False
    assert r["review_status"]=="REVIEW_PENDING" and r["teacher_evidence"] is None
    assert r["student_authoritative"] is False and r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert r["proof_verification"]=="UNVERIFIED" and r["prerequisite_candidate_ids"]==[]
    assert len(r["applicability"])>=30 and len(r["invalid_use"])>=24

@pytest.mark.parametrize("q",QUEUE,ids=lambda a:a["cue_id"])
def test_each_cue_adjudication_is_visible_but_unapproved(q):
    assert q["official_atom_id"] is None and q["teacher_approved"] is False
    assert q["student_authoritative"] is False
    assert len(q["source_line_sha256"])==64
    assert q["status"] in {
        "SOURCE_LINKED_EDITORIAL_CANDIDATE",
        "NON_ATOM_ACTIVITY_EDITORIAL_PROPOSAL_PENDING_REVIEW",
        "TOPIC_HEADING_NEEDS_CHILD_SCOPE_REVIEW",
        "SUBTOPIC_CUE_PENDING_CLAUSE_REVIEW",
        "NUMBERED_REQUIREMENT_AWAITING_EDITORIAL_ATOMIZATION"}
    assert bool(q["linked_candidate_ids"])==(q["status"]=="SOURCE_LINKED_EDITORIAL_CANDIDATE")
    if q["status"]=="NON_ATOM_ACTIVITY_EDITORIAL_PROPOSAL_PENDING_REVIEW":
        assert q["cue_kind"]=="NUMBERED_REQUIREMENT_CUE"
        assert len(q["next_action"])>=20

@pytest.mark.parametrize("track",sorted(COV["per_track"]))
def test_seven_track_official_denominator_remains_unknown(track):
    r=COV["per_track"][track]
    assert r["official_atom_denominator"] is None and r["official_coverage"] is None
    assert r["layout_cues"]==r["linked_cues"]+r["unlinked_cues"]
    assert r["teacher_approved"]==0

@pytest.mark.parametrize("manuscript",DOC,ids=lambda a:a["id"])
def test_complete_teacher_only_reasoning_with_examples_hints_transfer(manuscript):
    assert manuscript["teacher_review_status"]=="REVIEW_PENDING"
    assert manuscript["teacher_evidence"] is None and manuscript["student_authoritative"] is False
    assert manuscript["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert manuscript["proof_step_machine_certified"] is False
    assert len(manuscript["reasoned_steps"])==3
    assert len(manuscript["teacher_examples"])==2
    assert len(manuscript["student_hint_ladder"])==3
    assert manuscript["why_it_works"] and manuscript["formal_definition_or_statement"]
    assert manuscript["boundary_and_counterexample"] and manuscript["why_wrong"]
    assert manuscript["near_transfer"] and manuscript["far_transfer"]
    assert len(manuscript["symbols"])>20

@pytest.mark.parametrize("bad",[
 lambda x:x.update(official_atom_total_denominator=405),
 lambda x:x.update(official_atom_census_complete=True),
 lambda x:x.update(teacher_approved_count=1),
 lambda x:x.update(student_authoritative_count=1),
 lambda x:x.update(source_text_committed=True),
 lambda x:x.update(new_candidate_count=33),
 lambda x:x.update(cumulative_editorial_candidate_count=405),
 lambda x:x["candidates"][0].update(review_status="APPROVED"),
 lambda x:x["candidates"][0].update(official_atom_id="FAKE"),
 lambda x:x["candidates"][0].update(official_atom_certified=True),
 lambda x:x["candidates"][0].update(student_authoritative=True),
 lambda x:x["candidates"][0].update(teacher_evidence={"signed_by":"model"}),
 lambda x:x["candidates"][0].update(proof_verification="PROVED"),
 lambda x:x["candidates"][0].update(teacher_solution_visibility="PUBLIC"),
 lambda x:x["candidates"][0].update(course_track="ELECTIVE_D"),
 lambda x:x["candidates"][0]["source"].update(source_span_sha256="bogus"),
 lambda x:x["candidates"][0]["source"].update(matching_layout_cues=[]),
 lambda x:x["candidates"][0]["source"].update(printed_page=74),
 lambda x:x["candidates"][0].update(prerequisite_candidate_ids=["NO-SUCH-KNOWLEDGE"]),
 lambda x:x["candidates"][0].update(invalid_use=""),
 lambda x:x["candidates"].append(copy.deepcopy(x["candidates"][0])),
])
def test_forge_official_census_scope_or_teacher_approval_is_rejected(bad):
    x=copy.deepcopy(DATA);bad(x)
    with pytest.raises(ValueError):k.validate(x)

@pytest.mark.parametrize("bad",[
 lambda x:x.pop(),
 lambda x:x[0].update(status="SOURCE_LINKED_EDITORIAL_CANDIDATE"),
 lambda x:x[0].update(teacher_approved=True),
 lambda x:x[0].update(student_authoritative=True),
 lambda x:x[0].update(official_atom_id="APPROVED"),
 lambda x:x[0].update(source_line_sha256="forged"),
 lambda x:x[0].update(linked_candidate_ids=["fabricated"]),
])
def test_queue_tampering_is_rejected(bad):
    x=copy.deepcopy(QUEUE);bad(x)
    with pytest.raises(ValueError):k.validate_queue(DATA,x,COV)

@pytest.mark.parametrize("bad",[
 lambda x:x[0].update(teacher_review_status="APPROVED"),
 lambda x:x[0].update(student_authoritative=True),
 lambda x:x[0].update(teacher_solution_visibility="STUDENT"),
 lambda x:x[0].update(proof_step_machine_certified=True),
 lambda x:x[0].update(teacher_evidence={"fake_teacher":"llm"}),
 lambda x:x[0].update(math_example_exact_checks_passed=100),
 lambda x:x[0].update(teacher_examples=[]),
 lambda x:x[0].update(student_hint_ladder=[]),
 lambda x:x[0].update(reasoned_steps=[]),
 lambda x:x[0].update(formal_definition_or_statement=""),
 lambda x:x[0].update(boundary_and_counterexample=""),
 lambda x:x[0].update(candidate_id="unrelated"),
])
def test_deep_lesson_proof_or_access_spoof_is_rejected(bad):
    x=copy.deepcopy(DOC);bad(x)
    with pytest.raises(ValueError):d.validate(x)

@pytest.mark.parametrize("key",sorted(ORACLE["per_lesson"]))
def test_independent_exact_math_witness_per_domain(key):
    assert ORACLE["per_lesson"][key]=={"worked_examples":2,"negative_cases":1,"cross_topic":1}
    assert d.exact_witnesses()["per_lesson"][key]==ORACLE["per_lesson"][key]

def test_complete_scope_dispositions_and_original_source_consistency():
    assert len(DATA["candidates"])==len(ROWS)==32
    assert len(QUEUE)==COV["total_layout_cues"]==405
    assert COV["cues_linked"]==270 and COV["cues_unlinked"]==135
    assert COV["new_editorial_candidates"]==32 and COV["cumulative_editorial_candidates"]==239
    assert COV["editorial_nonatom_proposals_pending"]==len(NONATOM)==3
    assert COV["official_atom_total_denominator"] is None and COV["official_atom_census_complete"] is False
    assert k.validate(DATA) and k.validate_queue(DATA,QUEUE,COV)
    assert d.validate(DOC)
    assert ORACLE["exact_worked_cases_passed"]==16 and ORACLE["independent_negative_checks_passed"]==8
    assert ORACLE["cross_topic_exact_checks_passed"]==8
    assert ORACLE["general_formal_theorems_proven"]==0 and ORACLE["student_free_text_steps_certified"]==0
    assert ORACLE["teacher_approved"]==ORACLE["student_authoritative"]==0

def test_student_cannot_retrieve_unreviewed_teacher_manuscripts():
    public=json.dumps(public_summary(),ensure_ascii=False)
    assert "hs-semantic-pilot-124" not in public
    assert "kb_batch124_eight_depth_lessons" not in public
    assert "teacher_examples" not in public
    assert "teacher_solution" not in public

def test_local_sha_locks_only_when_authorized_original_is_present():
    # CI contains no proprietary PDF; pin checks still enforce committed source
    # hash, page digest and cue mapping. Mac can additionally check local original.
    if k.previous.base_scope.evidence.CACHE.exists():
        assert k.pinned()==k.anchored()

def test_actual_reasoned_proof_uses_nonzero_conditions():
    by={r["candidate_id"].split("-")[-1]:r for r in DOC}
    assert by["c507"]["proof_required"] is True
    assert by["c521"]["proof_required"] is True
    assert by["b501"]["proof_required"] is True
    assert by["s502"]["proof_required"] is False
    for key in ("c507","c521","b501"):
        assert len(by[key]["reasoned_steps"])>=3
        assert by[key]["proof_step_machine_certified"] is False
