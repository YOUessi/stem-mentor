"""Batch146 source-locked original deep content, finite guards, privacy and bounded census."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"backend"))
import build_kb_batch146_lessons as lessons
import build_kb_batch146_crosswalk as census
import check_kb_batch146_math as independent
from app import kb_batch146_index as index
from app.main import app

@pytest.fixture(scope="module")
def rows():return json.loads(lessons.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def cases():return json.loads(independent.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def tally():return json.loads(census.OUT.read_text(encoding="utf-8"))

def test_roundtrip_authored_lessons_math_crosswalk_safe_and_markdown(rows,cases,tally):
    assert rows==lessons.build()
    assert lessons.validate(rows)
    assert lessons.audit(rows)==json.loads(lessons.AUDIT.read_text(encoding="utf-8"))
    assert lessons.render(rows,lessons.audit(rows))==lessons.REPORT.read_text(encoding="utf-8")
    assert lessons.student_safe()==json.loads(lessons.SAFE.read_text(encoding="utf-8"))
    assert cases==independent.oracle()
    assert tally==census.build()
    assert census.render(tally)==census.REPORT.read_text(encoding="utf-8")

@pytest.mark.parametrize("i",range(10))
def test_complete_original_lesson_source_conditions_proofs_examples_hints(i,rows):
    r=rows[i]
    assert r["source_candidate_id"]==lessons.IDS[i]
    assert r["course_track"]==lessons.EXPECTED[lessons.IDS[i]]
    assert r["source_pdf_sha256"]==lessons.PDF
    assert r["official_atom_id"] is None
    assert not r["source_semantics_human_approved"]
    assert r["source_evidence_status"]=="PDFKIT_HASHED_NOT_HUMAN_SEMANTICALLY_APPROVED"
    assert r["teacher_review_status"]==r["prerequisite_math_review"]=="REVIEW_PENDING"
    assert r["teacher_review_evidence"] is None
    assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert not r["student_authoritative"] and not r["formal_proof_certified"]
    assert not r["free_student_step_verified"]
    assert len(r["reasoned_steps"])==4
    assert len(r["teacher_examples"])==2
    assert len(r["student_hint_ladder"])==3
    assert len(r["source_line_sha256"])==r["source_end_line"]-r["source_start_line"]+1
    assert r["near_transfer"] and r["far_transfer"] and r["typical_wrong_solution"]
    assert r["nonexample_or_failure"] and r["why_wrong_and_repair"]

FORGERIES=[
    ("teacher_review_status","APPROVED"),("teacher_review_evidence",{"fake":"teacher"}),
    ("teacher_solution_visibility","STUDENT"),("student_authoritative",True),
    ("source_semantics_human_approved",True),("official_atom_id","fake-official"),
    ("formal_proof_certified",True),("free_student_step_verified",True),
    ("source_evidence_status","APPROVED"),("prerequisite_math_review","APPROVED"),
    ("source_span_sha256","0"*64),("source_pdf_sha256","0"*64),
    ("source_start_line",999),("teacher_examples",[]),("reasoned_steps",[]),
    ("student_hint_ladder",[]),("nonexample_or_failure",""),("formal_definition_or_theorem","")
]
@pytest.mark.parametrize("i",range(10))
@pytest.mark.parametrize("field,forgery",FORGERIES)
def test_every_authority_source_content_mutation_is_rejected(i,field,forgery,rows):
    mutated=copy.deepcopy(rows)
    mutated[i][field]=forgery
    with pytest.raises(ValueError):
        lessons.validate(mutated)

@pytest.mark.parametrize("i",range(40))
def test_independent_exact_math_case_is_not_certified(i,cases):
    c=cases["cases"][i]
    assert c["candidate_id"]==lessons.IDS[i//4]
    assert c["passed"] is True
    assert c["outcome"]==("REJECT_INVALID_PRECONDITION" if i%4>=2 else "EXACT_FINITE_WITNESS")
    assert not c["teacher_approved"]
    assert not c["general_formal_proof_certified"]
    assert not c["student_free_step_verified"]

@pytest.mark.parametrize("track",lessons.TRACKS)
def test_by_track_provisional_denominator_is_not_official(track,tally):
    t=tally["by_track"][track]
    assert t["official_atom_denominator"] is None
    assert t["editorial_candidate_count"]==t["linked_teacher_only_drafts"]+t["missing_bounded_teacher_drafts"]
    assert t["editor_drafts_in_track"]>=t["linked_teacher_only_drafts"]
    assert t["teacher_approved"]==t["student_authoritative"]==0
    assert tally["official_atom_denominators"][track] is None

@pytest.mark.parametrize("field,value",[
    ("historical_editorial_candidates",113),("candidate_to_draft_matches",239),
    ("candidates_without_bounded_teacher_draft",0),("editor_draft_total",113),
    ("teacher_approved",85),("student_authoritative",85),
    ("official_syllabus_census_complete",True),("official_course_coverage_rate",1.0),
    ("official_atom_denominators",{"COMPULSORY":113}),
])
def test_cannot_pass_forged_coverage_or_approval(field,value,tally):
    altered=copy.deepcopy(tally); altered[field]=value
    assert altered!=census.build()

@pytest.mark.parametrize("q",["复数","二分法","弧度","数学归纳","排列组合",
                               "中值定理","概率密度","相容性","黄金分割","同余"])
def test_new_lessons_editor_only_and_student_deny(q):
    found=index.editor_preview_search(q,scope="EDITOR_LOCAL",limit=20)
    assert found
    for item in found:
        assert set(item)=={"id","course_track","source_candidate_id","review_status",
                          "condition_status","student_publishable","rank"}
        assert item["review_status"]=="REVIEW_PENDING"
        assert item["condition_status"]=="CONDITIONS_NOT_ESTABLISHED"
        assert not item["student_publishable"]
    denied=index.student_evidence_lookup(q)
    assert denied["status"]=="NO_APPROVED_EVIDENCE" and denied["candidates"]==[]
    assert not denied["teacher_solution_exposed"] and not denied["unverified_content_exposed"]

@pytest.mark.parametrize("bad",["","\x00x","x\nhello","x"*161])
def test_invalid_queries_rejected_in_both_paths(bad):
    with pytest.raises(ValueError):index.student_evidence_lookup(bad)
    with pytest.raises(ValueError):index.editor_preview_search(bad,scope="EDITOR_LOCAL")

@pytest.mark.parametrize("scope",["","STUDENT","APPROVED","TEACHER"])
def test_client_scope_does_not_authenticate_editor(scope):
    with pytest.raises(index.LocalEditorOnlyError):
        index.editor_preview_search("中值定理",scope=scope)

def test_public_api_aggregate_does_not_leak_draft_or_answer():
    r=TestClient(app).get("/api/knowledge/kb146-review-coverage")
    assert r.status_code==200
    doc=r.json()
    assert doc["editorial_review_manuscripts"]==85
    assert len(doc["by_track"])==7
    assert doc["teacher_approved"]==doc["student_authoritative"]==0
    assert all(v is None for v in doc["official_atom_denominators"].values())
    assert doc["teacher_solution_or_manuscript_included"] is False
    assert not any(key in doc for key in ("teacher_examples","reasoned_steps","formal_definition_or_theorem","student_hint_ladder"))
    assert not any("kb146" in route.path and any(term in route.path for term in ("search","draft","manuscript"))
                   for route in app.routes)
    assert len(index.load())==85
