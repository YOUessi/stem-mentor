"""Batch138: source-locked elective maths, authoring fields, FTS default-deny boundaries."""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"backend"))
import build_kb_batch138_electives as lessons
import check_kb_batch138_math as oracle
from app import kb_batch138_index as index
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="module")
def rows():
    return json.loads(lessons.OUT.read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def math():
    return json.loads(oracle.OUT.read_text(encoding="utf-8"))

def test_both_builder_and_oracle_independently_reconstruct(rows,math):
    assert rows==lessons.build()
    assert math==oracle.build()
    assert json.loads(lessons.AUDIT.read_text(encoding="utf-8"))==lessons.audit(rows)
    assert json.loads(lessons.SAFE.read_text(encoding="utf-8"))==lessons.safe()
    assert lessons.REPORT.read_text(encoding="utf-8")==lessons.render(rows,lessons.audit(rows))

@pytest.mark.parametrize("i",range(8))
def test_complete_math_and_source_provenance(i,rows):
    r=rows[i]
    assert len(r["reasoned_steps"])==4
    assert len(r["student_hint_ladder"])==3
    assert len(r["teacher_examples"])==2
    assert all(len(e["reasoned_solution"])>=3 for e in r["teacher_examples"])
    assert r["teacher_review_status"]=="REVIEW_PENDING"
    assert r["teacher_review_evidence"] is None and r["official_atom_id"] is None
    assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert not r["formal_proof_certified"] and not r["free_student_step_verified"]
    assert not r["student_authoritative"]
    assert r["course_track"] in {"ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"}

@pytest.mark.parametrize("i",range(8))
@pytest.mark.parametrize("key,forgery",[
    ("teacher_review_status","APPROVED"),
    ("teacher_review_evidence",{"signed":"fake teacher"}),
    ("teacher_solution_visibility","STUDENT"),
    ("student_authoritative",True),
    ("formal_proof_certified",True),
    ("free_student_step_verified",True),
    ("official_atom_id","official-1"),
    ("source_span_sha256","f"*64),
    ("source_pdf_sha256","f"*64),
    ("course_track","COMPULSORY"),
    ("formal_definition_or_theorem","wrong statement"),
    ("reasoned_steps",[]),
    ("teacher_examples",[]),
    ("student_hint_ladder",[]),
    ("prerequisite_proposals",["not-real"])
])
def test_forged_status_math_source_or_prerequisite_rejected(i,key,forgery,rows):
    tampered=copy.deepcopy(rows)
    tampered[i][key]=forgery
    assert tampered!=lessons.build()

@pytest.mark.parametrize("i",range(32))
def test_every_exact_witness_is_recomputed(i,math):
    item=oracle.build()["cases"][i]
    assert item==math["cases"][i] and item["passed"]
    assert not item["general_proof_certified"]
    assert not item["teacher_approved"] and not item["student_step_verified"]

@pytest.mark.parametrize("key,value",[
    ("teacher_approved",1),
    ("general_theorem_certificates",1),
    ("student_authoritative_releases",2),
    ("student_free_text_steps_verified",4),
    ("finite_exact_checks",1000),
])
def test_oracle_must_not_promote_finite_examples_to_proofs(key,value,math):
    changed=copy.deepcopy(math)
    changed[key]=value
    assert changed!=oracle.build()

@pytest.mark.parametrize("track,expected",[
    ("COMPULSORY",23),("SELECTIVE_COMPULSORY",11),("ELECTIVE_A",7),
    ("ELECTIVE_B",2),("ELECTIVE_C",2),("ELECTIVE_D",2),("ELECTIVE_E",2)])
def test_bounded_seven_track_counts_not_official_denominators(track,expected):
    audit=lessons.audit(lessons.build())
    assert audit["by_track_new_manuscripts"].get(track,0)==(0 if track in ("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A") else 2)
    assert index.public_coverage()["by_track"][track]==expected
    assert audit["official_atom_denominators"][track] is None
    assert index.public_coverage()["official_atom_denominator"] is None

@pytest.mark.parametrize("query,track,expected",[
    ("非齐次线性方程组","ELECTIVE_B","kb138-deep-121-b205"),
    ("二次函数闭圆盘","ELECTIVE_B","kb138-deep-121-b203"),
    ("Logistic概率模型","ELECTIVE_C","kb138-deep-121-ec202"),
    ("调查选项","ELECTIVE_C","kb138-deep-121-ec204"),
    ("音频频率","ELECTIVE_D","kb138-deep-121-ed201"),
    ("平面旋转 平移 缩放","ELECTIVE_D","kb138-deep-121-ed202"),
    ("最大公因数","ELECTIVE_E","kb138-deep-120-ee104"),
    ("建筑测量 比例尺","ELECTIVE_E","kb138-deep-120-ee106"),
])
def test_local_editor_only_retrieval_finds_each_elective(query,track,expected):
    result=index.editor_preview_search(query,scope="EDITOR_LOCAL",track=track,limit=20)
    assert expected in {r["id"] for r in result}
    flat=json.dumps(result,ensure_ascii=False)
    assert all(r["student_publishable"] is False for r in result)
    assert all(r["condition_status"]=="CONDITIONS_NOT_ESTABLISHED" for r in result)
    assert "teacher_examples" not in flat and "reasoned_solution" not in flat
    assert "student_hint_ladder" not in flat and "reasoned_steps" not in flat

@pytest.mark.parametrize("scope",["","ADMIN","STUDENT","TEACHER","APPROVED"])
def test_editor_preview_requires_local_scope_and_is_not_http(scope):
    with pytest.raises(index.LocalEditorOnlyError):
        index.editor_preview_search("欧几里得算法",scope=scope)

@pytest.mark.parametrize("query",["复利","Logistic","欧几里得算法","平面旋转","声波频率","<script>alert(1)</script>"])
def test_all_student_lookups_reject_unapproved_evidence(query):
    response=index.student_evidence_lookup(query)
    assert response=={
        "status":"NO_APPROVED_EVIDENCE","candidates":[],
        "teacher_solution_exposed":False,"unverified_content_exposed":False}

@pytest.mark.parametrize("bad",[""," ","\n","a"*161])
def test_invalid_student_queries_fail_closed(bad):
    with pytest.raises(ValueError):index.student_evidence_lookup(bad)

def test_http_only_aggregate_and_no_teacher_draft_route():
    client=TestClient(app)
    response=client.get("/api/knowledge/kb138-review-coverage")
    assert response.status_code==200
    assert response.json()["editorial_review_manuscripts"]==49
    assert response.json()["student_authoritative"]==0
    assert response.json()["official_course_coverage_rate"] is None
    assert response.json()["teacher_solution_or_manuscript_included"] is False
    assert "teacher_examples" not in response.text
    assert "reasoned_steps" not in response.text
    assert all(not ("/kb138" in route.path and any(x in route.path for x in ("search","editor","draft","solution")))
               for route in app.routes)

@pytest.mark.parametrize("key,value",[
    ("student_authoritative",True),
    ("teacher_review_status","APPROVED"),
    ("source_span_sha256","0"*64),
    ("teacher_review_evidence",{"signature":"forged"}),
])
def test_local_index_rejects_mutated_source_files(tmp_path,monkeypatch,key,value):
    original=index.NEW
    broken=json.loads(original.read_text(encoding="utf-8"))
    broken[0][key]=value
    fake=tmp_path/"poison.json"
    fake.write_text(json.dumps(broken,ensure_ascii=False),encoding="utf-8")
    index.load.cache_clear();index.index.cache_clear()
    monkeypatch.setattr(index,"NEW",fake)
    try:
        with pytest.raises(ValueError):index.load()
    finally:
        monkeypatch.setattr(index,"NEW",original)
        index.load.cache_clear();index.index.cache_clear()
