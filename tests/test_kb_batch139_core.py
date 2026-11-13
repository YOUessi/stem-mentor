"""Batch139 eight source-backed provisional manuscripts / exact math / leak guards."""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"backend"))
import build_kb_batch139_core as authors
import check_kb_batch139_math as oracle
from app import kb_batch139_index as index
from app.main import app

@pytest.fixture(scope="module")
def rows():
    return json.loads(authors.OUT.read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def exact():
    return json.loads(oracle.OUT.read_text(encoding="utf-8"))

def test_rebuild_all_content_and_ledger(rows, exact):
    assert authors.build()==rows
    assert authors.full_inventory(rows)==json.loads(authors.AUDIT.read_text(encoding="utf-8"))
    assert authors.render(rows,authors.full_inventory(rows))==authors.REPORT.read_text(encoding="utf-8")
    assert json.loads(authors.SAFE.read_text(encoding="utf-8"))==authors.safe()
    assert exact==oracle.build()

@pytest.mark.parametrize("i",range(8))
def test_complete_original_proof_conditions_and_student_guard(i,rows):
    r=rows[i]
    assert r["source_candidate_id"]==authors.IDS[i]
    assert r["course_track"]==authors.EXPECTED[r["source_candidate_id"]]
    assert len(r["reasoned_steps"])==4
    assert len(r["student_hint_ladder"])==3
    assert len(r["teacher_examples"])==2
    assert all(len(x["reasoned_solution"])>=3 for x in r["teacher_examples"])
    assert r["teacher_review_status"]=="REVIEW_PENDING"
    assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert r["teacher_review_evidence"] is None
    assert r["official_atom_id"] is None
    assert not r["formal_proof_certified"]
    assert not r["free_student_step_verified"]
    assert not r["student_authoritative"]
    assert r["source_pdf_sha256"]==authors.PDF
    assert r["prerequisite_math_review"]=="REVIEW_PENDING"
    assert r["missing_prerequisite_gap"]

@pytest.mark.parametrize("i",range(8))
@pytest.mark.parametrize("field,forgery",[
    ("teacher_review_status","APPROVED"),
    ("teacher_review_evidence",{"teacher":"synthetic","signed":True}),
    ("teacher_solution_visibility","STUDENT"),
    ("official_atom_id","fake-national-standard-atom"),
    ("student_authoritative",True),
    ("formal_proof_certified",True),
    ("free_student_step_verified",True),
    ("prerequisite_math_review","APPROVED"),
    ("source_span_sha256","f"*64),
    ("source_pdf_sha256","f"*64),
    ("source_line_sha256",[]),
    ("source_evidence_status","TEACHER_APPROVED"),
    ("course_track","ELECTIVE_E"),
    ("formal_definition_or_theorem","changed mathematical conclusion"),
    ("reasoned_steps",[]),
    ("teacher_examples",[]),
    ("student_hint_ladder",[]),
    ("prerequisite_proposals",["nonexistent-prerequisite"])
])
def test_mutated_approval_proof_source_or_math_is_rejected(i,field,forgery,rows):
    altered=copy.deepcopy(rows)
    altered[i][field]=forgery
    assert altered!=authors.build()
    if field in {"teacher_review_status","teacher_review_evidence",
                 "teacher_solution_visibility","official_atom_id","student_authoritative",
                 "formal_proof_certified","free_student_step_verified",
                 "prerequisite_math_review","course_track","source_pdf_sha256",
                 "source_evidence_status","reasoned_steps","teacher_examples",
                 "student_hint_ladder","prerequisite_proposals"}:
        with pytest.raises((ValueError,AssertionError,KeyError)):
            authors.validate(altered)

@pytest.mark.parametrize("i",range(32))
def test_all_independent_sympy_finite_oracles(i,exact):
    item=oracle.build()["cases"][i]
    assert item==exact["cases"][i]
    assert item["passed"] is True
    assert not item["general_proof_certified"]
    assert not item["teacher_approved"]
    assert not item["student_free_text_verified"]

@pytest.mark.parametrize("key,value",[
    ("teacher_approved",1),("general_proofs_certified",1),
    ("student_free_text_verified",1),("exact_cases",3200),
    ("negative_condition_rejections",0)
])
def test_cannot_promote_exact_witness_count_to_proof_or_teacher_approval(exact,key,value):
    poisoned=copy.deepcopy(exact)
    poisoned[key]=value
    assert poisoned!=oracle.build()

@pytest.mark.parametrize("track,expected",[
 ("COMPULSORY",27),("SELECTIVE_COMPULSORY",13),("ELECTIVE_A",9),
 ("ELECTIVE_B",2),("ELECTIVE_C",2),("ELECTIVE_D",2),("ELECTIVE_E",2),
])
def test_bounded_seven_track_matrix_never_claims_official_coverage(track,expected,rows):
    ledger=authors.full_inventory(rows)
    assert ledger["total_manuscripts"]==57
    assert ledger["by_track"][track]==expected
    assert ledger["official_atom_denominators"][track] is None
    assert ledger["official_coverage_rate"] is None
    assert ledger["teacher_approved"]==0 and ledger["student_authoritative"]==0

@pytest.mark.parametrize("query,track,key",[
    ("向量数量积","COMPULSORY","120-c103"),
    ("不共线向量","COMPULSORY","120-c105"),
    ("简单随机抽样","COMPULSORY","120-c111"),
    ("样本方差","COMPULSORY","124-c524"),
    ("两点确定直线","SELECTIVE_COMPULSORY","121-s203"),
    ("分布列概率","SELECTIVE_COMPULSORY","121-s206"),
    ("微积分基本定理","ELECTIVE_A","122-a302"),
    ("最小二乘回归","ELECTIVE_A","123-a405"),
])
def test_local_editor_fts_can_locate_each_new_draft_without_teacher_answer(query,track,key):
    records=index.editor_preview_search(query,scope="EDITOR_LOCAL",track=track,limit=20)
    assert any(item["id"].endswith(key) for item in records)
    assert all(set(item)<={"id","course_track","source_candidate_id","review_status",
                             "condition_status","student_publishable","rank"} for item in records)
    assert all(item["student_publishable"] is False for item in records)

@pytest.mark.parametrize("scope",["","PUBLIC","STUDENT","TEACHER","ADMIN","EDITOR","EDITOR_LOCAL "])
def test_local_editor_scope_default_denies_untrusted_roles(scope):
    with pytest.raises(index.LocalEditorOnlyError):
        index.editor_preview_search("数量积",scope=scope)

@pytest.mark.parametrize("query",[""," ","\n","a"*161,"x\x00y"])
def test_bad_student_and_editor_queries_are_rejected(query):
    with pytest.raises(ValueError):
        index.student_evidence_lookup(query)
    with pytest.raises(ValueError):
        index.editor_preview_search(query,scope="EDITOR_LOCAL")

@pytest.mark.parametrize("limit",[-1,0,21,True,1.5])
def test_bad_query_limits_rejected(limit):
    with pytest.raises(ValueError):
        index.student_evidence_lookup("概率",limit=limit)
    with pytest.raises(ValueError):
        index.editor_preview_search("概率",scope="EDITOR_LOCAL",limit=limit)

def test_student_entire_57_manuscript_collection_is_default_deny():
    for q in ("数量积","极值","最小二乘","样本方差","模型","几何"):
        out=index.student_evidence_lookup(q)
        assert out["status"]=="NO_APPROVED_EVIDENCE"
        assert out["candidates"]==[]
        assert out["teacher_solution_exposed"] is False
        assert out["unverified_content_exposed"] is False

def test_http_aggregate_only_no_teacher_solution_or_text_and_no_editor_route(rows):
    response=TestClient(app).get("/api/knowledge/kb139-review-coverage")
    assert response.status_code==200
    info=response.json()
    assert info["editorial_review_manuscripts"]==57
    assert info["official_course_coverage_rate"] is None
    assert all(v is None for v in info["official_atom_denominators"].values())
    assert info["teacher_solution_or_manuscript_included"] is False
    for r in rows:
        assert r["formal_definition_or_theorem"] not in response.text
        assert r["teacher_examples"][0]["answer"] not in response.text
    assert all(not ("/kb139" in route.path and any(w in route.path for w in ("search","editor","draft","solution")))
               for route in app.routes)

@pytest.mark.parametrize("field,value",[
    ("student_authoritative",True),("teacher_review_status","APPROVED"),
    ("source_span_sha256","0"*64),("course_track","ELECTIVE_E"),
    ("prerequisite_proposals",["invented"]),("teacher_review_evidence",{"signature":"fake"})
])
def test_index_throws_on_tampered_manuscript_file(tmp_path,monkeypatch,field,value):
    contents=json.loads(index.NEW.read_text(encoding="utf-8"))
    contents[0][field]=value
    tmp=tmp_path/"malicious.json"
    tmp.write_text(json.dumps(contents,ensure_ascii=False),encoding="utf-8")
    original=index.NEW
    index.load.cache_clear();index.index.cache_clear()
    monkeypatch.setattr(index,"NEW",tmp)
    try:
        with pytest.raises((ValueError,AssertionError)):index.load()
    finally:
        monkeypatch.setattr(index,"NEW",original)
        index.load.cache_clear();index.index.cache_clear()
