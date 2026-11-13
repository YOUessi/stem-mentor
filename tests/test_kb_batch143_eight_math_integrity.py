"""Batch143 cross-track original math depth, exact finite oracle, seven-track coverage and RAG deny gates."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import pytest
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"backend"))
import build_kb_batch143_lessons as author
import check_kb_batch143_math as oracle
from app import kb_batch143_index as index
from app.main import app

@pytest.fixture(scope="module")
def rows():
    return json.loads(author.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def cases():
    return json.loads(oracle.OUT.read_text(encoding="utf-8"))

def test_source_authoring_rebuild_and_all_output_consistency(rows,cases):
    assert rows==author.build()
    assert json.loads(author.AUDIT.read_text(encoding="utf-8"))==author.audit(rows)
    assert author.REPORT.read_text(encoding="utf-8")==author.render(rows,author.audit(rows))
    assert json.loads(author.SAFE.read_text(encoding="utf-8"))==author.safe()
    assert cases==oracle.oracle()

@pytest.mark.parametrize("i",range(8))
def test_each_manuscript_original_full_teacher_review_content(i,rows):
    r=rows[i]
    assert r["source_candidate_id"]==author.IDS[i]
    assert r["teacher_review_status"]=="REVIEW_PENDING"
    assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert r["teacher_review_evidence"] is None
    assert r["official_atom_id"] is None
    assert r["source_semantics_human_approved"] is False
    assert r["source_evidence_status"]==author.EVIDENCE
    assert r["source_pdf_sha256"]==author.old.PDF
    assert len(r["source_line_sha256"])==1+r["source_end_line"]-r["source_start_line"]
    assert len(r["reasoned_steps"])==4
    assert len(r["teacher_examples"])==2
    assert len(r["student_hint_ladder"])==3
    assert all(len(e["reasoned_solution"])>=3 for e in r["teacher_examples"])
    assert all(r[k] for k in ["formal_definition_or_theorem","notation_and_domain",
        "applicability_and_hypotheses","why_method_is_legal","nonexample_or_failure",
        "typical_wrong_solution","why_wrong_and_repair","near_transfer","far_transfer"])
    assert not r["formal_proof_certified"]
    assert not r["free_student_step_verified"]
    assert not r["student_authoritative"]

@pytest.mark.parametrize("i",range(8))
@pytest.mark.parametrize("field,forged",[
    ("teacher_review_status","APPROVED"),("teacher_review_evidence",{"name":"invented","approved":True}),
    ("teacher_solution_visibility","STUDENT"),("official_atom_id","invented-standard-id"),
    ("source_semantics_human_approved",True),("student_authoritative",True),
    ("formal_proof_certified",True),("free_student_step_verified",True),
    ("prerequisite_math_review","APPROVED"),("source_evidence_status","APPROVED"),
    ("source_pdf_sha256","0"*64),("course_track","ELECTIVE_E"),
    ("reasoned_steps",[]),("teacher_examples",[]),("student_hint_ladder",[])
])
def test_forged_approval_source_steps_or_leak_rejected(i,field,forged,rows):
    tampered=copy.deepcopy(rows)
    tampered[i][field]=forged
    assert tampered!=author.build()
    with pytest.raises((ValueError,AssertionError,KeyError)):
        author.validate(tampered)

@pytest.mark.parametrize("i",range(8))
@pytest.mark.parametrize("field,newval",[
    ("formal_definition_or_theorem","2+2=7 forged"),
    ("why_method_is_legal","math premise removed"),
    ("typical_wrong_solution","no typical error"),
    ("source_span_sha256","1"*64),
    ("source_line_sha256",[]),
    ("teacher_examples",[]),
])
def test_author_reconstruction_detects_math_and_source_changes(i,field,newval,rows):
    poisoned=copy.deepcopy(rows)
    poisoned[i][field]=newval
    assert poisoned!=author.build()

@pytest.mark.parametrize("i",range(32))
def test_independent_exact_finite_math_oracles(i,cases):
    x=oracle.oracle()["cases"][i]
    assert x==cases["cases"][i]
    assert x["passed"] is True
    assert not x["formal_proof_certified"]
    assert not x["teacher_approved"]
    assert not x["free_student_text_verified"]

@pytest.mark.parametrize("key,value",[
    ("proof_certifications",1),("teacher_approvals",1),("student_step_verifications",1),
    ("total_cases",3200),("negative_precondition_rejections",0),
    ("official_atom_denominators",{"COMPULSORY":100}),
])
def test_exact_witnesses_cannot_forge_formal_proof_or_scope(cases,key,value):
    data=copy.deepcopy(cases)
    data[key]=value
    assert data!=oracle.oracle()

@pytest.mark.parametrize("track,count",[
    ("COMPULSORY",31),("SELECTIVE_COMPULSORY",15),("ELECTIVE_A",10),
    ("ELECTIVE_B",2),("ELECTIVE_C",2),("ELECTIVE_D",3),("ELECTIVE_E",2),
])
def test_seven_track_bounded_coverage_never_fakes_denominator(track,count,rows):
    ledger=author.audit(rows)
    assert ledger["total_teacher_only_drafts"]==65
    assert ledger["by_track"][track]==count
    assert ledger["official_atom_denominators"][track] is None
    assert ledger["official_coverage_rate"] is None
    assert ledger["teacher_approved"]==0
    assert ledger["student_authoritative"]==0

@pytest.mark.parametrize("query,expected,track",[
    ("全称命题","121-c203","COMPULSORY"),("奇偶性","123-c404","COMPULSORY"),
    ("正弦定理","120-c108","COMPULSORY"),("事件并集","124-c521","COMPULSORY"),
    ("斜率","120-s107","SELECTIVE_COMPULSORY"),("超几何","122-s305","SELECTIVE_COMPULSORY"),
    ("克拉默","120-a108","ELECTIVE_A"),("十二平均律","120-ed105","ELECTIVE_D"),
])
def test_private_fts_indexes_each_new_draft_but_never_teacher_answers(query,expected,track):
    hits=index.editor_preview_search(query,scope="EDITOR_LOCAL",track=track,limit=20)
    assert any(x["id"].endswith(expected) for x in hits)
    assert all(set(x)<={"id","course_track","source_candidate_id","review_status",
                       "condition_status","student_publishable","rank"} for x in hits)
    assert all(x["student_publishable"] is False for x in hits)

@pytest.mark.parametrize("scope",["","EDITOR","TEACHER","STUDENT","PUBLIC","ADMIN","editor_local","EDITOR_LOCAL "])
def test_raw_scope_strings_never_grant_local_editor_search(scope):
    with pytest.raises(index.LocalEditorOnlyError):
        index.editor_preview_search("正弦定理",scope=scope)

@pytest.mark.parametrize("query",[""," ","\n","a"*161,"x\x00y"])
def test_query_validation_both_interfaces(query):
    with pytest.raises(ValueError):
        index.student_evidence_lookup(query)
    with pytest.raises(ValueError):
        index.editor_preview_search(query,scope="EDITOR_LOCAL")

@pytest.mark.parametrize("limit",[-1,0,21,True,2.1])
def test_limit_validation_both_interfaces(limit):
    with pytest.raises(ValueError):
        index.student_evidence_lookup("概率",limit=limit)
    with pytest.raises(ValueError):
        index.editor_preview_search("概率",scope="EDITOR_LOCAL",limit=limit)

def test_student_all_65_editor_drafts_default_deny_and_no_answer_leak():
    for q in ("正弦定理","超几何分布","函数","集合","行列式","十二平均律","高斯消元"):
        data=index.student_evidence_lookup(q)
        assert data["status"]=="NO_APPROVED_EVIDENCE"
        assert data["candidates"]==[]
        assert data["teacher_solution_exposed"] is False
        assert data["unverified_content_exposed"] is False

def test_http_public_aggregate_only_and_no_editor_search_routes(rows):
    response=TestClient(app).get("/api/knowledge/kb143-review-coverage")
    assert response.status_code==200
    d=response.json()
    assert d["editorial_review_manuscripts"]==65
    assert d["official_course_coverage_rate"] is None
    assert all(x is None for x in d["official_atom_denominators"].values())
    assert d["teacher_approved"]==0 and d["student_authoritative"]==0
    assert d["teacher_solution_or_manuscript_included"] is False
    for r in rows:
        assert r["formal_definition_or_theorem"] not in response.text
        assert r["teacher_examples"][0]["answer"] not in response.text
    assert not any("/kb143" in route.path and any(w in route.path for w in
          ("search","draft","teacher","solution","editor","manuscript")) for route in app.routes)
