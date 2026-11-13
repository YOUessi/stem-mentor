"""Batch135 source-locked manuscripts, exact witnesses and deny-by-default RAG."""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"backend"))
import build_kb_batch133_atomization as atoms
import build_kb_batch134_graph as graph
import build_kb_batch135_lessons as lessons
import check_kb_batch135_math as math
from app import kb_batch135_index as index
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="module")
def draft():return json.loads(lessons.OUT.read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def evidence():return json.loads(math.OUT.read_text(encoding="utf-8"))

def test_all_batch135_consistency(draft,evidence):
    assert lessons.validate(draft)
    assert math.validate(evidence)
    assert lessons.MD.read_text(encoding="utf-8")==lessons.render(draft)
    assert json.loads(lessons.SAFE.read_text(encoding="utf-8"))==lessons.safe_export(draft)

@pytest.mark.parametrize("i",range(8))
def test_each_lesson_full_editorial_scope(i,draft):
    x=draft[i]
    assert x["id"].startswith("kb135-deep-")
    assert len(x["reasoned_steps"])>=4
    assert len(x["teacher_examples"])==2
    assert len(x["student_hint_ladder"])==3
    assert x["teacher_review_status"]=="REVIEW_PENDING"
    assert x["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert not x["student_authoritative"] and not x["formal_proof_certified"]

@pytest.mark.parametrize("i",range(8))
def test_each_source_anchor_and_prerequisite(i,draft):
    records=json.loads(atoms.OUT.read_text(encoding="utf-8"))["records"]
    source={r["id"]:r for r in records}[draft[i]["source_candidate_id"]]
    assert source["source_lock"]["span_sha256"]==draft[i]["source_span_sha256"]
    assert source["source_pdf_sha256"]==draft[i]["source_pdf_sha256"]
    assert source["official_atom_id"] is None

@pytest.mark.parametrize("i",range(8))
@pytest.mark.parametrize("key,alter",[
    ("teacher_review_status","APPROVED"),("teacher_review_evidence",{"signed":"yes"}),
    ("teacher_solution_visibility","STUDENT"),("student_authoritative",True),
    ("formal_proof_certified",True),("free_student_step_verified",True),
])
def test_forged_approval_must_be_rejected(i,key,alter,draft):
    x=copy.deepcopy(draft);x[i][key]=alter
    with pytest.raises(ValueError,match="drift|forged"):
        lessons.validate(x)

@pytest.mark.parametrize("i",range(8))
def test_changed_answer_cannot_pass_frozen_authoring(i,draft):
    x=copy.deepcopy(draft);x[i]["teacher_examples"][0]["answer"]="unverified answer"
    with pytest.raises(ValueError):lessons.validate(x)

@pytest.mark.parametrize("i",range(8))
def test_removed_reasoning_cannot_pass(i,draft):
    x=copy.deepcopy(draft);x[i]["reasoned_steps"]=[]
    with pytest.raises(ValueError):lessons.validate(x)

@pytest.mark.parametrize("i",range(24))
def test_each_exact_case_independently_regenerated(i,evidence):
    assert evidence["cases"][i]==math.cases()[i]
    assert evidence["cases"][i]["result"]=="EXACT_PASS"
    assert not evidence["cases"][i]["teacher_approval"]

@pytest.mark.parametrize("i",range(4))
def test_each_symbolic_subclaim_regenerated(i,evidence):
    assert evidence["symbolic_checks"][i]==math.symbolic_subclaims()[i]
    assert not evidence["symbolic_checks"][i]["theorem_general_proof_certified"]

def test_oracle_does_not_claim_proof_or_student_verification(evidence):
    assert evidence["formal_general_proofs_certified"]==0
    assert evidence["teacher_approved_count"]==0
    assert not evidence["student_free_text_verified"]
    assert evidence["exact_finite_positive"]==16
    assert evidence["exact_finite_invalid_precondition"]==8

def test_oracle_tampering_rejected(evidence):
    x=copy.deepcopy(evidence);x["formal_general_proofs_certified"]=4
    with pytest.raises(ValueError):math.validate(x)

def test_proposal_counts_vs_official_unknown():
    a=json.loads(atoms.OUT.read_text(encoding="utf-8"))
    g=json.loads(graph.OUT.read_text(encoding="utf-8"))
    assert atoms.validate(a) and graph.validate(g)
    assert a["proposed_count"]==41
    assert a["official_atom_denominator"] is None
    assert all(x is None for x in g["official_atom_denominators"].values())

def test_22_teacher_review_index_and_denominator():
    x=index.public_coverage()
    assert x["candidate_manuscripts"]==22
    assert x["by_track"]=={"COMPULSORY":12,"SELECTIVE_COMPULSORY":6,"ELECTIVE_A":4}
    assert x["official_course_atom_denominator"] is None
    assert x["teacher_approved"]==x["student_authoritative"]==0
    assert not x["student_solution_or_teacher_manuscript_included"]

@pytest.mark.parametrize("query,expected",[
    ("投影","kb135-deep-sc_space_projection"),
    ("二次不等式","kb135-deep-c_quadratic_sign"),
    ("并集交集","kb135-deep-c_union_intersection"),
    ("正切","kb135-deep-c_tangent_domain"),
    ("等差","kb135-deep-sc_arith_progression"),
    ("最值","kb135-deep-sc_extreme_point"),
    ("商法则","kb135-deep-a_limits_quotient"),
    ("周期","kb135-deep-c_period"),
])
def test_editor_preview_search_real_fts(query,expected):
    hits=index.editor_preview_search(query,scope="EDITOR_LOCAL",limit=20)
    assert expected in {h["id"] for h in hits}
    assert all(h["review_status"]=="REVIEW_PENDING" and not h["student_publishable"] for h in hits)
    text=json.dumps(hits,ensure_ascii=False)
    assert "teacher_examples" not in text and "reasoned_steps" not in text

@pytest.mark.parametrize("wrong_scope",["","STUDENT","TEACHER","APPROVED"])
def test_editor_route_not_authorization(wrong_scope):
    with pytest.raises(index.LocalEditorOnlyError):
        index.editor_preview_search("投影",scope=wrong_scope)

@pytest.mark.parametrize("query",["投影","极值","商法则","证明","正切","<script>alert(1)</script>",""" " OR " """])
def test_student_lookups_default_denied(query):
    result=index.student_evidence_lookup(query)
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert result["candidates"]==[]
    assert not result["teacher_solution_exposed"]

@pytest.mark.parametrize("bad",["", "a"*161,"first\nsecond","\0"])
def test_invalid_query_denied(bad):
    with pytest.raises(ValueError):index.student_evidence_lookup(bad)

@pytest.mark.parametrize("limit",[-1,0,21,True,"5"])
def test_bad_limit_denied(limit):
    with pytest.raises(ValueError):index.editor_preview_search("正切",scope="EDITOR_LOCAL",limit=limit)

def test_unapproved_manuscripts_are_never_http_served():
    client=TestClient(app)
    response=client.get("/api/knowledge/kb135-review-coverage")
    assert response.status_code==200
    body=response.json()
    assert body["candidate_manuscripts"]==22
    assert not body["student_solution_or_teacher_manuscript_included"]
    assert "teacher_examples" not in response.text
    routes={r.path for r in app.routes}
    assert not any("/kb135" in r and ("full" in r or "editor" in r or "search" in r)
                   for r in routes)

def test_public_rag_does_not_leak_review_manuscripts():
    client=TestClient(app)
    response=client.post("/api/knowledge/search",
                         json={"query":"正交投影","include_excluded":True})
    assert response.status_code==200
    assert "kb135-deep-" not in response.text
    assert "kb134-deep-" not in response.text
    assert "kb133-deep-" not in response.text
    assert "teacher_examples" not in response.text
    assert "reasoned_steps" not in response.text

def test_source_hash_tamper_in_editor_index_rejected(tmp_path,monkeypatch):
    # Read only a temporary copy, NEVER mutate the actual original corpus.
    paths=[]
    for path in index.FILES:
        rows=json.loads(path.read_text(encoding="utf-8"))
        if path.name=="kb_batch135_eight_deep_lessons.json":
            rows[0]["teacher_review_status"]="APPROVED"
        dest=tmp_path/path.name
        dest.write_text(json.dumps(rows,ensure_ascii=False),encoding="utf-8")
        paths.append(dest)
    original=index.FILES
    index.load.cache_clear()
    monkeypatch.setattr(index,"FILES",tuple(paths))
    try:
        with pytest.raises(ValueError,match="Unattested approval"):
            index.load()
    finally:
        monkeypatch.setattr(index,"FILES",original)
        index.load.cache_clear()
