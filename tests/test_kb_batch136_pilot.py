"""Bounded 34/41 deep manuscript pilot: conditional math, safe RAG and source gates."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"backend"))
import build_kb_batch133_atomization as atoms
import build_kb_batch136_lessons as lessons
import check_kb_batch136_math as oracle
import build_kb_batch136_coverage as coverage
from app import kb_batch136_index as index
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="module")
def drafts():return json.loads(lessons.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def math():return json.loads(oracle.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def matrix():return json.loads(coverage.OUT.read_text(encoding="utf-8"))

def test_new_artefacts_are_frozen_and_readable(drafts,math,matrix):
    assert lessons.validate(drafts)
    assert oracle.validate(math)
    assert coverage.validate(matrix)
    assert lessons.MD.read_text(encoding="utf-8")==lessons.render(drafts)
    assert coverage.MD.read_text(encoding="utf-8")==coverage.render(matrix)
    assert json.loads(lessons.SAFE.read_text(encoding="utf-8"))==lessons.safe_export(drafts)

@pytest.mark.parametrize("i",range(12))
def test_each_manuscript_complete(i,drafts):
    r=drafts[i]
    assert len(r["reasoned_steps"])>=4
    assert len(r["teacher_examples"])==2
    assert all(len(ex["reasoned_solution"])>=3 for ex in r["teacher_examples"])
    assert len(r["student_hint_ladder"])==3
    assert r["near_transfer"] and r["far_transfer"]
    assert r["teacher_review_status"]=="REVIEW_PENDING"
    assert r["teacher_review_evidence"] is None
    assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert r["student_authoritative"] is False
    assert r["formal_proof_certified"] is False
    assert r["free_student_step_verified"] is False

@pytest.mark.parametrize("i",range(12))
def test_source_lock_matches_authoring_inventory(i,drafts):
    source=json.loads(atoms.OUT.read_text(encoding="utf-8"))
    cand={r["id"]:r for r in source["records"]}[drafts[i]["source_candidate_id"]]
    assert drafts[i]["source_pdf_sha256"]==cand["source_pdf_sha256"]
    assert drafts[i]["source_span_sha256"]==cand["source_lock"]["span_sha256"]
    assert cand["official_atom_id"] is None

@pytest.mark.parametrize("i",range(12))
@pytest.mark.parametrize("key,forged",[
    ("teacher_review_status","APPROVED"),
    ("teacher_review_evidence",{"fake_signature":"admin"}),
    ("teacher_solution_visibility","STUDENT"),
    ("student_authoritative",True),
    ("formal_proof_certified",True),
    ("free_student_step_verified",True),
])
def test_forged_approval_and_authority_denied(i,key,forged,drafts):
    mutated=copy.deepcopy(drafts)
    mutated[i][key]=forged
    with pytest.raises(ValueError):
        lessons.validate(mutated)

@pytest.mark.parametrize("i",range(12))
def test_changed_source_hash_denied(i,drafts):
    mutated=copy.deepcopy(drafts)
    mutated[i]["source_span_sha256"]="0"*64
    with pytest.raises(ValueError):lessons.validate(mutated)

@pytest.mark.parametrize("i",range(12))
def test_missing_reasoned_steps_denied(i,drafts):
    mutated=copy.deepcopy(drafts)
    mutated[i]["reasoned_steps"]=[]
    with pytest.raises(ValueError):lessons.validate(mutated)

@pytest.mark.parametrize("i",range(12))
def test_teacher_solution_tampering_denied(i,drafts):
    mutated=copy.deepcopy(drafts)
    mutated[i]["teacher_examples"][1]["answer"]="0=1"
    with pytest.raises(ValueError):lessons.validate(mutated)

@pytest.mark.parametrize("i",range(36))
def test_math_case_independently_recomputed(i,math):
    rebuilt=oracle.cases()[i]
    assert math["cases"][i]==rebuilt
    assert rebuilt["status"]=="EXACT_INSTANCE_PASS"
    assert not rebuilt["general_proof_certified"]
    assert not rebuilt["teacher_approved"]
    assert not rebuilt["student_free_step_verified"]

@pytest.mark.parametrize("key,forgery",[
    ("general_theorem_proofs_certified",12),
    ("teacher_approvals",12),
    ("student_free_step_verified",True),
    ("student_authoritative_releases",12),
])
def test_math_cannot_self_certify(key,forgery,math):
    mutated=copy.deepcopy(math)
    mutated[key]=forgery
    with pytest.raises(ValueError):oracle.validate(mutated)

def test_exact_positive_and_invalid_cases_are_distinguished(math):
    assert math["positive_exact_instance_count"]==24
    assert math["invalid_hypothesis_instance_count"]==12
    assert sum(x["kind"]=="NEG" for x in math["cases"])==12
    assert math["general_theorem_proofs_certified"]==0

def test_bounded_matrix_and_seven_track_denominators_not_forged(matrix):
    assert matrix["scope_proposals"]==41
    assert matrix["full_teacher_draft_manuscripts"]==34
    assert matrix["incomplete_proposal_drafts"]==7
    assert matrix["teacher_examples"]==68
    assert matrix["hints"]==102
    assert matrix["finite_exact_oracle_cases"]==102
    assert len(matrix["rows"])==41
    assert len(matrix["missing_full_manuscript_queue"])==7
    assert all(v is None for v in matrix["official_atom_denominators"].values())
    assert matrix["national_course_coverage_percentage"] is None
    assert matrix["teacher_approvals"]==matrix["student_authoritative_releases"]==0

@pytest.mark.parametrize("i",range(41))
def test_each_pilot_atom_has_a_frozen_completion_record(i,matrix):
    r=matrix["rows"][i]
    assert r["teacher_review"]=="REVIEW_PENDING"
    assert r["official_atom_id"] is None
    assert not r["student_authoritative"]
    if r["has_complete_teacher_manuscript"]:
        assert r["teacher_examples"]==2 and r["student_hints"]==3
    else:
        assert r["teacher_examples"]==0 and r["missing_fields"]

@pytest.mark.parametrize("t",atoms.TRACKS)
def test_cannot_forge_official_denominator(t,matrix):
    altered=copy.deepcopy(matrix)
    altered["official_atom_denominators"][t]=41
    with pytest.raises(ValueError):coverage.validate(altered)

def test_cannot_forge_teacher_approval_in_matrix(matrix):
    altered=copy.deepcopy(matrix)
    altered["teacher_approvals"]=34
    with pytest.raises(ValueError):coverage.validate(altered)

def test_review_only_fts_34_matches_coverage():
    result=index.public_coverage()
    assert result["candidate_manuscripts"]==34
    assert result["by_track"]=={"COMPULSORY":23,"SELECTIVE_COMPULSORY":7,"ELECTIVE_A":4}
    assert result["official_course_atom_denominator"] is None
    assert result["teacher_approved"]==0
    assert result["student_authoritative"]==0
    assert result["student_solution_or_teacher_manuscript_included"] is False

@pytest.mark.parametrize("query,expected",[
    ("子集","kb136-deep-c_set_subset"),
    ("充分条件","kb136-deep-c_sufficiency"),
    ("量词","kb136-deep-c_quantifier"),
    ("分段函数","kb136-deep-c_piecewise"),
    ("单调递增","kb136-deep-c_monotonicity"),
    ("指数函数","kb136-deep-c_exponential_exp"),
    ("对数","kb136-deep-c_logarithm_law"),
    ("导数","kb136-deep-sc_derivative_def"),
    ("正切","kb135-deep-c_tangent_domain"),
])
def test_editor_fts_recalls_manuscripts_without_answers(query,expected):
    hits=index.editor_preview_search(query,scope="EDITOR_LOCAL",limit=20)
    assert expected in {r["id"] for r in hits}
    assert all(not r["student_publishable"] for r in hits)
    assert all(r["condition_status"]=="CONDITIONS_NOT_ESTABLISHED" for r in hits)
    serialized=json.dumps(hits,ensure_ascii=False)
    assert "teacher_examples" not in serialized
    assert "reasoned_steps" not in serialized

@pytest.mark.parametrize("scope",["","STUDENT","ADMIN","TEACHER","APPROVED"])
def test_editor_scope_is_not_authentication(scope):
    with pytest.raises(index.LocalEditorOnlyError):
        index.editor_preview_search("量词",scope=scope)

@pytest.mark.parametrize("query",["导数","集合","对数","证明","<script>sample</script>"])
def test_student_evidence_default_denied(query):
    body=index.student_evidence_lookup(query)
    assert body["status"]=="NO_APPROVED_EVIDENCE"
    assert body["candidates"]==[]
    assert body["teacher_solution_exposed"] is False
    assert body["unverified_content_exposed"] is False

@pytest.mark.parametrize("query",["","a"*161,"hi\nall","\0"])
def test_untrusted_query_rejected(query):
    with pytest.raises(ValueError):index.student_evidence_lookup(query)

@pytest.mark.parametrize("limit",[True,0,-1,21,"8"])
def test_invalid_editor_query_limit_rejected(limit):
    with pytest.raises(ValueError):
        index.editor_preview_search("导数",scope="EDITOR_LOCAL",limit=limit)

def test_public_http_only_aggregate_no_new_teacher_manuscript():
    client=TestClient(app)
    response=client.get("/api/knowledge/kb136-review-coverage")
    assert response.status_code==200
    body=response.json()
    assert body["candidate_manuscripts"]==34
    assert body["official_course_atom_denominator"] is None
    assert not body["student_solution_or_teacher_manuscript_included"]
    assert "teacher_examples" not in response.text
    assert "reasoned_steps" not in response.text
    routes={r.path for r in app.routes}
    assert not any("/kb136" in p and ("editor" in p or "search" in p or "full" in p)
                   for p in routes)
    public=client.post("/api/knowledge/search",
                json={"query":"一元二次不等式","include_excluded":True})
    assert public.status_code==200
    assert "kb136-deep-" not in public.text
    assert "teacher_examples" not in public.text

@pytest.mark.parametrize("tamper",["source_span_sha256","source_pdf_sha256","course_track"])
def test_local_editor_index_rejects_well_formed_forgery(tamper,tmp_path,monkeypatch):
    paths=[]
    for p in index.FILES:
        rows=json.loads(p.read_text(encoding="utf-8"))
        if p.name=="kb_batch136_twelve_deep_lessons.json":
            if tamper=="course_track":rows[0][tamper]="ELECTIVE_E"
            else:rows[0][tamper]="f"*64
        target=tmp_path/p.name
        target.write_text(json.dumps(rows,ensure_ascii=False),encoding="utf-8")
        paths.append(target)
    original=index.FILES
    index.load.cache_clear();index._index.cache_clear()
    monkeypatch.setattr(index,"FILES",tuple(paths))
    try:
        with pytest.raises(ValueError,match="Source hash|Course track"):
            index.load()
    finally:
        monkeypatch.setattr(index,"FILES",original)
        index.load.cache_clear();index._index.cache_clear()

def test_tampered_file_editor_index_cannot_forge_approval(tmp_path,monkeypatch):
    files=[]
    for p in index.FILES:
        rows=json.loads(p.read_text(encoding="utf-8"))
        if p.name=="kb_batch136_twelve_deep_lessons.json":
            rows[0]["teacher_review_status"]="APPROVED"
        target=tmp_path/p.name
        target.write_text(json.dumps(rows,ensure_ascii=False),encoding="utf-8")
        files.append(target)
    original=index.FILES
    index.load.cache_clear();index._index.cache_clear()
    monkeypatch.setattr(index,"FILES",tuple(files))
    try:
        with pytest.raises(ValueError,match="Unattested approval"):
            index.load()
    finally:
        monkeypatch.setattr(index,"FILES",original)
        index.load.cache_clear();index._index.cache_clear()
