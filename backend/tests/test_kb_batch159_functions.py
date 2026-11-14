"""Batch159: source-locked ten-lesson module, math boundary and student privacy tests."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch159_functions as lesson
import check_kb_batch159_math as math
from app import kb_batch159_index as index
from app.main import app

ROWS=lesson.build()
IDS=lesson.IDS

def test_10_unique_source_locked_deep_chapter_drafts():
    assert len(ROWS)==len(IDS)==10
    assert tuple(r["source_candidate_id"] for r in ROWS)==IDS
    assert len({r["id"] for r in ROWS})==10
    assert lesson.validate(ROWS)

@pytest.mark.parametrize("i",range(10))
def test_each_lesson_has_full_original_depth_and_source(i):
    r=ROWS[i]
    assert r["course_track"]=="COMPULSORY"
    assert r["source_pdf_sha256"]==lesson.PDF
    assert r["source_evidence_status"]==lesson.EVIDENCE
    assert r["source_line_sha256"] and len(r["source_span_sha256"])==64
    assert all(len(r[k])>=25 for k in ("formal_definition_or_theorem",
        "notation_and_domain","applicability_and_hypotheses",
        "why_method_is_legal","nonexample_or_failure","typical_wrong_solution",
        "why_wrong_and_repair","near_transfer","far_transfer"))
    assert len(r["reasoned_steps"])==4
    assert len(r["teacher_examples"])==2
    assert all(len(e["reasoned_solution"])>=3 for e in r["teacher_examples"])
    assert len(r["student_hint_ladder"])==3
    assert r["official_atom_id"] is None and not r["source_semantics_human_approved"]
    assert r["teacher_review_status"]=="REVIEW_PENDING"
    assert r["teacher_review_evidence"] is None
    assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert not r["student_authoritative"] and not r["formal_proof_certified"]
    assert not r["free_student_step_verified"]

@pytest.mark.parametrize("i",range(10))
def test_source_line_locks_are_reproducible_without_licensed_text(i):
    r=ROWS[i]
    lock=json.loads(lesson.LOCKS.read_text())[r["source_candidate_id"]]
    assert lock["span_sha256"]==r["source_span_sha256"]
    assert lock["line_sha256"]==r["source_line_sha256"]
    assert len(lock["line_sha256"])==lock["end_line"]-lock["start_line"]+1
    assert all(len(x)==64 for x in lock["line_sha256"])
    assert not any(k in lock for k in ("text","full_text","pdf_body"))

@pytest.mark.parametrize("i",range(10))
def test_source_falsification_rejected(i):
    rows=copy.deepcopy(ROWS)
    rows[i]["source_span_sha256"]="0"*64
    with pytest.raises(ValueError,match="forged source provenance"):
        lesson.validate(rows)

@pytest.mark.parametrize("i",range(10))
def test_untrusted_teacher_approval_rejected(i):
    rows=copy.deepcopy(ROWS)
    rows[i]["teacher_review_status"]="APPROVED"
    with pytest.raises(ValueError,match="forged approval"):
        lesson.validate(rows)

@pytest.mark.parametrize("i",range(10))
def test_teacher_solution_visibility_cannot_be_promoted(i):
    rows=copy.deepcopy(ROWS)
    rows[i]["teacher_solution_visibility"]="STUDENT_VISIBLE"
    with pytest.raises(ValueError,match="forged approval"):
        lesson.validate(rows)

@pytest.mark.parametrize("i",range(10))
def test_unverified_student_steps_cannot_be_promoted(i):
    rows=copy.deepcopy(ROWS)
    rows[i]["free_student_step_verified"]=True
    with pytest.raises(ValueError,match="forged approval"):
        lesson.validate(rows)

@pytest.mark.parametrize("i",range(10))
def test_general_proof_cannot_be_falsely_certified(i):
    rows=copy.deepcopy(ROWS)
    rows[i]["formal_proof_certified"]=True
    with pytest.raises(ValueError,match="forged approval"):
        lesson.validate(rows)

@pytest.mark.parametrize("i",range(10))
def test_structured_hint_ladder_and_teacher_examples_not_in_student_safe_index(i):
    rows=json.loads(lesson.SAFE.read_text())
    assert len(rows)==10
    row=rows[i]
    assert not row["student_authoritative"] and not row["teacher_solution_exposed"]
    assert "teacher_examples" not in row and "student_hint_ladder" not in row
    assert "formal_definition_or_theorem" not in row

@pytest.mark.parametrize("i",range(10))
def test_oracle_exact_example_and_invalid_premise_witnesses(i):
    o=math.build()
    assert o["teacher_example_checks"]==20 and o["invalid_premise_checks"]==20
    assert o["general_proof_certified"] is False
    assert o["teacher_approved"]==0 and o["student_authoritative"]==0
    assert all(x["source_candidate_id"]==IDS[i] and not x["teacher_solution_exposed"]
               for x in o["positive_cases"][2*i:2*i+2])
    assert all(x["source_candidate_id"]==IDS[i]
               for x in o["negative_cases"][2*i:2*i+2])

@pytest.mark.parametrize("i",range(10))
def test_oracle_detects_wrong_teacher_answers(i):
    bad=copy.deepcopy(ROWS)
    bad[i]["teacher_examples"][0]["answer"]="错误答案"
    with pytest.raises(ValueError,match="teacher answer text drift"):
        math.build(bad)

@pytest.mark.parametrize("bad",["APPROVED","STUDENT_VISIBLE","VERIFIED_GENERAL"])
def test_publication_status_not_allowed(bad):
    rows=copy.deepcopy(ROWS);rows[0]["teacher_review_status"]=bad
    with pytest.raises(ValueError):
        lesson.validate(rows)

@pytest.mark.parametrize("scope",["","STUDENT","PARENT","TEACHER","ADMIN"])
def test_editor_search_denied_without_explicit_editor_scope(scope):
    with pytest.raises(index.LocalEditorOnlyError):
        index.editor_preview_search("指数函数",scope=scope)

@pytest.mark.parametrize("q",["指数函数","正弦模型","cos 差角","对数定义域"])
def test_students_never_receive_pending_evidence(q):
    d=index.student_evidence_lookup(q)
    assert d==dict(status="NO_APPROVED_EVIDENCE",candidates=[],
       teacher_solution_exposed=False,unverified_content_exposed=False)

def test_editor_fts_returns_metadata_only_and_no_teacher_answer():
    hits=index.editor_preview_search("指数函数",scope="EDITOR_LOCAL",track="COMPULSORY")
    assert hits and len(hits)<=8
    for hit in hits:
        assert set(hit)=={"id","course_track","review_status","condition_status",
                          "source_candidate_id","student_publishable","rank"}
        assert hit["review_status"]=="REVIEW_PENDING"
        assert hit["condition_status"]=="CONDITIONS_NOT_ESTABLISHED"
        assert not hit["student_publishable"]

@pytest.mark.parametrize("limit",[-1,0,21,100,True])
def test_search_limit_cannot_be_bypassed(limit):
    with pytest.raises(ValueError):
        index.editor_preview_search("对数",scope="EDITOR_LOCAL",limit=limit)

@pytest.mark.parametrize("filter",["ELECTIVE_Z","UNKNOWN","UNSAFE"])
def test_invalid_track_filter_rejected(filter):
    with pytest.raises(ValueError):
        index.editor_preview_search("对数",scope="EDITOR_LOCAL",track=filter)

def test_aggregate_api_has_no_manuscript_or_teacher_solution():
    response=TestClient(app).get("/api/knowledge/kb159-review-coverage")
    assert response.status_code==200
    data=response.json()
    assert data["editorial_review_manuscripts"]==185
    assert data["editorial_source_candidates_linked"]==144
    assert data["editorial_source_candidates_unlinked"]==95
    assert data["numbered_syllabus_layout_markers_not_atomic_denominators"]==315
    assert all(v is None for v in data["official_atom_denominators"].values())
    assert data["official_coverage_rate"] is None
    assert data["teacher_approved"]==data["student_authoritative"]==0
    assert not data["teacher_solution_or_manuscript_included"]
    payload=response.text
    assert "teacher_examples" not in payload
    assert "reasoned_solution" not in payload
    assert "formal_definition_or_theorem" not in payload

def test_module_prerequisite_dag_and_provisional_atom_review():
    assert len(lesson.MODULE_PREREQS)==8
    assert sum(map(len,lesson.MODULE_PREREQS.values()))==10
    for node,parents in lesson.MODULE_PREREQS.items():
        assert all(p in IDS and IDS.index(p)<IDS.index(node) for p in parents)
    d=lesson.provisional_atom_dossiers(ROWS)
    assert d["candidate_dossiers"]==10 and d["unique_official_atoms"] is None
    assert all(r["official_atom_count_contribution"] is None and r["official_atom_id"] is None
               and r["source_requirement_human_approval"]=="PENDING" for r in d["dossiers"])
    assert d==json.loads(lesson.ATOMS.read_text())

def test_cumulative_coverage_recomputes_five_year_source_without_count_inflation():
    a=lesson.audit(ROWS)
    assert a["total_teacher_only_drafts"]==185 and a["added_original_manuscripts"]==10
    assert a["historical_leads_with_pending_drafts"]==144
    assert a["historical_leads_without_drafts"]==95
    assert a["teacher_approved"]==a["student_authoritative"]==0
    assert a["official_coverage_rate"] is None
    assert all(v is None for v in a["official_atom_denominators"].values())
    assert sum(a["by_track"].values())==185
