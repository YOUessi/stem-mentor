"""Batch144 source provenance, 10 original lessons, math negatives, FTS/HTTP privacy."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"backend"))
import build_kb_batch144_lessons as author
import build_kb_batch144_crosswalk as gaps
import check_kb_batch144_math as math
from app import kb_batch144_index as index
from app.main import app

@pytest.fixture(scope="module")
def rows():return json.loads(author.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def cases():return json.loads(math.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def tally():return json.loads(gaps.OUT.read_text(encoding="utf-8"))

def test_exact_authoring_render_and_symbolic_oracle(rows,cases,tally):
    assert rows==author.build()
    assert author.validate(rows)
    assert author.audit(rows)==json.loads(author.AUDIT.read_text(encoding="utf-8"))
    assert author.render(rows,author.audit(rows))==author.REPORT.read_text(encoding="utf-8")
    assert author.student_safe()==json.loads(author.SAFE.read_text(encoding="utf-8"))
    assert cases==math.oracle()
    assert tally==gaps.build()
    assert gaps.render(tally)==gaps.REPORT.read_text(encoding="utf-8")

@pytest.mark.parametrize("i",range(10))
def test_every_original_lesson_has_rigorous_boundaries_examples_and_two_transfers(i,rows):
    r=rows[i]
    assert r["source_candidate_id"]==author.IDS[i]
    assert r["course_track"]==author.EXPECTED[author.IDS[i]]
    assert r["teacher_review_status"]=="REVIEW_PENDING"
    assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert r["teacher_review_evidence"] is None
    assert r["official_atom_id"] is None
    assert r["source_evidence_status"]=="PDFKIT_HASHED_NOT_HUMAN_SEMANTICALLY_APPROVED"
    assert not r["source_semantics_human_approved"]
    assert not r["formal_proof_certified"]
    assert not r["free_student_step_verified"]
    assert not r["student_authoritative"]
    assert len(r["source_line_sha256"])==r["source_end_line"]-r["source_start_line"]+1
    assert len(r["reasoned_steps"])==4 and len(r["teacher_examples"])==2
    assert len(r["student_hint_ladder"])==3
    assert all(len(e["reasoned_solution"])>=3 for e in r["teacher_examples"])
    for key in ("formal_definition_or_theorem","notation_and_domain",
                "applicability_and_hypotheses","why_method_is_legal",
                "nonexample_or_failure","typical_wrong_solution","why_wrong_and_repair",
                "near_transfer","far_transfer"):
        assert r[key]

@pytest.mark.parametrize("i",range(10))
@pytest.mark.parametrize("key,forged",[
    ("teacher_review_status","APPROVED"),("teacher_review_evidence",{"teacher":"forged"}),
    ("teacher_solution_visibility","STUDENT"),("student_authoritative",True),
    ("source_semantics_human_approved",True),("official_atom_id","fake-national-atom"),
    ("formal_proof_certified",True),("free_student_step_verified",True),
    ("source_evidence_status","APPROVED"),("prerequisite_math_review","APPROVED"),
    ("course_track","ELECTIVE_E"),("teacher_examples",[]),
    ("reasoned_steps",[]),("student_hint_ladder",[]),
])
def test_mutating_authority_or_structure_fails_review_gate(i,key,forged,rows):
    if key=="course_track" and rows[i]["course_track"]=="ELECTIVE_E":
        forged="COMPULSORY"
    x=copy.deepcopy(rows);x[i][key]=forged
    with pytest.raises(ValueError):author.validate(x)

@pytest.mark.parametrize("i",range(40))
def test_each_exact_math_case_is_independent_noncertifying(i,cases):
    c=cases["cases"][i]
    assert c["passed"] is True
    assert not c["formal_general_proof_certified"]
    assert not c["teacher_approved"] and not c["student_answer_verified"]
    assert c["candidate_id"]==author.IDS[i//4]
    assert c["outcome"]==("REJECT_INVALID_PRECONDITION" if i%4>=2 else "EXACT_FINITE_WITNESS")

@pytest.mark.parametrize("t",author.TRACKS)
def test_official_denominator_remains_unknown_and_all_tracks_accounted(t,tally):
    r=tally["by_track"][t]
    assert r["official_atom_denominator"] is None
    assert r["editorial_candidate_count"]==r["linked_teacher_only_drafts"]+r["missing_bounded_teacher_drafts"]
    assert not r["teacher_approved"] and not r["student_authoritative"]
    assert tally["official_atom_denominators"][t] is None

@pytest.mark.parametrize("key,forged",[
    ("historical_editorial_candidates",113),("editor_draft_total",113),
    ("candidate_to_draft_matches",239),("candidates_without_bounded_teacher_draft",0),
    ("teacher_approved",75),("student_authoritative",75),
    ("official_syllabus_census_complete",True),("official_course_coverage_rate",1),
    ("official_atom_denominators",{"COMPULSORY":113}),
])
def test_forged_course_completion_or_authority_cannot_pass_report(key,forged,tally):
    x=copy.deepcopy(tally);x[key]=forged
    assert x!=gaps.build()

@pytest.mark.parametrize("q",[
    "向量加法","集合的元素","周期函数","等差数列",
    "圆的方程","子空间","线性相关","复利","纯音","机器人坐标"
])
def test_local_editor_retrieval_and_public_deny_both_hold(q):
    found=index.editor_preview_search(q,scope="EDITOR_LOCAL",limit=20)
    assert found
    for r in found:
        assert set(r)=={"id","course_track","source_candidate_id","review_status",
                         "condition_status","student_publishable","rank"}
        assert r["review_status"]=="REVIEW_PENDING"
        assert r["condition_status"]=="CONDITIONS_NOT_ESTABLISHED"
        assert r["student_publishable"] is False
    deny=index.student_evidence_lookup(q)
    assert deny["status"]=="NO_APPROVED_EVIDENCE"
    assert deny["candidates"]==[]
    assert not deny["teacher_solution_exposed"]

@pytest.mark.parametrize("q",["", "\x00 DROP TABLE","hello\nworld","x"*161])
def test_search_and_student_query_reject_invalid_input(q):
    with pytest.raises(ValueError):index.student_evidence_lookup(q)
    with pytest.raises(ValueError):index.editor_preview_search(q,scope="EDITOR_LOCAL")

@pytest.mark.parametrize("scope",["","STUDENT","APPROVED","TEACHER"])
def test_no_authentication_from_client_supplied_scope(scope):
    with pytest.raises(index.LocalEditorOnlyError):
        index.editor_preview_search("圆的方程",scope=scope)

def test_public_http_only_aggregated_safe_coverage():
    client=TestClient(app)
    response=client.get("/api/knowledge/kb144-review-coverage")
    assert response.status_code==200
    doc=response.json()
    assert doc["editorial_review_manuscripts"]==75
    assert len(doc["by_track"])==7
    assert all(v is None for v in doc["official_atom_denominators"].values())
    assert doc["teacher_approved"]==0
    assert doc["student_authoritative"]==0
    assert doc["teacher_solution_or_manuscript_included"] is False
    leak_terms=("teacher_examples","reasoned_solution","teacher_solution","student_hint_ladder",
                "formal_definition_or_theorem","nonexample_or_failure")
    assert not any(x in doc for x in leak_terms)
    paths={r.path for r in app.routes}
    assert not any("kb144" in p and ("search" in p or "manuscript" in p or "draft" in p) for p in paths)

def test_75_editor_inventory_immutable_and_student_answer_not_leaked():
    rows=index.load()
    assert len(rows)==75 and len({r["id"] for r in rows})==75
    assert sum(1 for r in rows if r["id"].startswith("kb144-deep-"))==10
    assert all(r["teacher_review_status"]=="REVIEW_PENDING" for r in rows)
    assert index.public_coverage()["teacher_solution_or_manuscript_included"] is False
    assert index.student_evidence_lookup("full answer")["candidates"]==[]
