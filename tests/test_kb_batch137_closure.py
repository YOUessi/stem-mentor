"""Exact lesson closure, forged approval rejection, 41-item editor index and student privacy."""
from __future__ import annotations
import copy, json, sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"));sys.path.insert(0,str(ROOT/"backend"))
import build_kb_batch137_lessons as lessons
import check_kb_batch137_math as math
import build_kb_batch137_coverage as matrix
from app import kb_batch137_index as idx
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="module")
def rows():return json.loads(lessons.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def oracle():return json.loads(math.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def coverage():return json.loads(matrix.OUT.read_text(encoding="utf-8"))

def test_all_generated_artifacts_rebuild_exactly(rows,oracle,coverage):
    assert lessons.validate(rows) and math.validate(oracle) and matrix.validate(coverage)
    assert lessons.MD.read_text(encoding="utf-8")==lessons.render(rows)
    assert matrix.MD.read_text(encoding="utf-8")==matrix.render(coverage)
    assert json.loads(lessons.SAFE.read_text(encoding="utf-8"))==lessons.safe_export(rows)

@pytest.mark.parametrize("i",range(7))
def test_complete_teacher_only_lessons(i,rows):
    r=rows[i]
    assert len(r["reasoned_steps"])==4
    assert len(r["teacher_examples"])==2
    assert len(r["student_hint_ladder"])==3
    assert r["student_authoritative"] is False
    assert r["teacher_review_status"]=="REVIEW_PENDING"
    assert r["teacher_review_evidence"] is None
    assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert r["formal_proof_certified"] is False

@pytest.mark.parametrize("i",range(7))
@pytest.mark.parametrize("key,forgery",[
 ("teacher_review_status","APPROVED"),
 ("teacher_review_evidence",{"signed":"fake"}),
 ("teacher_solution_visibility","STUDENT"),
 ("student_authoritative",True),
 ("formal_proof_certified",True),
 ("free_student_step_verified",True),
 ("source_span_sha256","a"*64),
 ("source_pdf_sha256","a"*64),
 ("course_track","ELECTIVE_E"),
 ("formal_definition_or_theorem","bogus"),
 ("reasoned_steps",[]),
 ("student_hint_ladder",[]),
])
def test_tampered_math_source_or_approval_rejected(i,key,forgery,rows):
    changed=copy.deepcopy(rows);changed[i][key]=forgery
    with pytest.raises(ValueError):lessons.validate(changed)

@pytest.mark.parametrize("i",range(21))
def test_each_exact_math_case_independently_recomputed(i,oracle):
    case=math.cases()[i]
    assert case==oracle["cases"][i]
    assert case["status"]=="EXACT_INSTANCE_PASS"
    assert case["formal_proof_certified"] is False

@pytest.mark.parametrize("key,value",[
 ("general_theorem_proofs_certified",7),("teacher_approvals",7),
 ("student_free_step_verified",True),("student_authoritative_releases",7),
])
def test_oracle_cannot_self_certify(key,value,oracle):
    bad=copy.deepcopy(oracle);bad[key]=value
    with pytest.raises(ValueError):math.validate(bad)

@pytest.mark.parametrize("i",range(41))
def test_all_41_bounded_proposals_have_review_manuscripts(i,coverage):
    r=coverage["rows"][i]
    assert r["has_complete_teacher_manuscript"]
    assert r["teacher_examples"]==2 and r["student_hints"]==3
    assert r["teacher_review"]=="REVIEW_PENDING"
    assert r["official_atom_id"] is None
    assert r["student_authoritative"] is False
    assert not r["missing_fields"]

@pytest.mark.parametrize("track",["COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"])
def test_cannot_invent_official_denominator(track,coverage):
    bad=copy.deepcopy(coverage);bad["official_atom_denominators"][track]=41
    with pytest.raises(ValueError):matrix.validate(bad)

def test_no_approved_evidence_ever_in_bounded_ledger(coverage):
    assert coverage["scope_proposals"]==41
    assert coverage["full_teacher_draft_manuscripts"]==41
    assert coverage["incomplete_proposal_drafts"]==0
    assert coverage["finite_exact_oracle_cases"]==123
    assert coverage["teacher_examples"]==82
    assert coverage["hints"]==123
    assert coverage["teacher_approvals"]==coverage["student_authoritative_releases"]==0
    assert coverage["national_course_coverage_percentage"] is None
    assert all(v is None for v in coverage["official_atom_denominators"].values())

@pytest.mark.parametrize("query,expected",[
 ("数列递推","kb137-deep-sc_sequence_model"),
 ("数学归纳法","kb137-deep-sc_induction_optional"),
 ("求导商法则","kb137-deep-sc_derivative_rules"),
 ("空间基底","kb137-deep-sc_space_basis"),
 ("单调有界","kb137-deep-a_monotone_convergence"),
 ("函数极限","kb137-deep-a_function_limit"),
 ("连续性","kb137-deep-a_continuity"),
])
def test_editor_only_retrieves_all_seven_without_answers(query,expected):
    hits=idx.editor_preview_search(query,scope="EDITOR_LOCAL",limit=20)
    assert expected in {h["id"] for h in hits}
    assert all(not h["student_publishable"] for h in hits)
    serialized=json.dumps(hits,ensure_ascii=False)
    assert "teacher_examples" not in serialized and "reasoned_steps" not in serialized

@pytest.mark.parametrize("scope",["","ADMIN","STUDENT","APPROVED","TEACHER"])
def test_editor_search_does_not_accept_fake_scope(scope):
    with pytest.raises(idx.LocalEditorOnlyError):idx.editor_preview_search("数学归纳法",scope=scope)

@pytest.mark.parametrize("query",["函数极限","数学归纳法","空间基底","导数","<script>alert(1)</script>"])
def test_student_evidence_is_default_deny(query):
    result=idx.student_evidence_lookup(query)
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert result["candidates"]==[]
    assert result["teacher_solution_exposed"] is False

def test_http_exposes_only_aggregate_41_no_teacher_manuscripts():
    client=TestClient(app)
    response=client.get("/api/knowledge/kb137-review-coverage")
    assert response.status_code==200
    data=response.json()
    assert data["candidate_manuscripts"]==41
    assert data["by_track"]=={"COMPULSORY":23,"SELECTIVE_COMPULSORY":11,"ELECTIVE_A":7}
    assert data["official_course_atom_denominator"] is None
    assert data["student_authoritative"]==0
    assert not data["student_solution_or_teacher_manuscript_included"]
    assert "teacher_examples" not in response.text
    assert "reasoned_steps" not in response.text
    routes=[route.path for route in app.routes]
    assert not any("/kb137" in p and ("editor" in p or "search" in p or "solution" in p)
                   for p in routes)

@pytest.mark.parametrize("tamper",["source_span_sha256","source_pdf_sha256","course_track","teacher_review_status"])
def test_local_index_rechecks_source_approval_locks(tamper,tmp_path,monkeypatch):
    paths=[]
    for f in idx.FILES:
        x=json.loads(f.read_text(encoding="utf-8"))
        if f.name=="kb_batch137_seven_deep_lessons.json":
            x[0][tamper]="APPROVED" if tamper=="teacher_review_status" else (
                "ELECTIVE_E" if tamper=="course_track" else "f"*64)
        target=tmp_path/f.name;target.write_text(json.dumps(x,ensure_ascii=False),encoding="utf-8")
        paths.append(target)
    original=idx.FILES
    idx.load.cache_clear();idx._index.cache_clear()
    monkeypatch.setattr(idx,"FILES",tuple(paths))
    try:
        with pytest.raises(ValueError):idx.load()
    finally:
        monkeypatch.setattr(idx,"FILES",original)
        idx.load.cache_clear();idx._index.cache_clear()
