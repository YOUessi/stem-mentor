"""Real K00 source replay and math/content/schema/privacy regressions for KB149."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"backend"))
import build_kb_batch149_lessons as lessons
import build_kb_batch149_unnumbered_elective_queue as source
import build_kb_batch149_crosswalk as crosswalk
import check_kb_batch149_math as independent
from app import kb_batch149_index as index
from app.main import app

@pytest.fixture(scope="module")
def rows():return json.loads(lessons.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def k00():return json.loads(source.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def oracle():return json.loads(independent.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def ledger():return json.loads(crosswalk.OUT.read_text(encoding="utf-8"))

def test_recomputed_ten_deep_originals_matches_release_artifacts(rows,oracle,ledger,k00):
    assert rows==lessons.build() and lessons.validate(rows)
    audit=lessons.audit(rows)
    assert audit==json.loads(lessons.AUDIT.read_text(encoding="utf-8"))
    assert audit["total_teacher_only_drafts"]==105
    assert lessons.render(rows,audit)==lessons.REPORT.read_text(encoding="utf-8")
    assert lessons.student_safe()==json.loads(lessons.SAFE.read_text(encoding="utf-8"))
    assert oracle==independent.oracle()
    assert ledger==crosswalk.build()
    assert crosswalk.validate(ledger) and crosswalk.render(ledger)==crosswalk.REPORT.read_text(encoding="utf-8")
    assert source.validate(k00)
    assert source.render(k00)==source.REPORT.read_text(encoding="utf-8")

@pytest.mark.parametrize("i",range(10))
def test_deep_manuscripts_rigorous_scope_and_teacher_only(i,rows):
    r=rows[i]
    assert r["source_candidate_id"]==lessons.IDS[i]
    assert r["course_track"]==lessons.EXPECTED[lessons.IDS[i]]
    assert r["source_evidence_status"]==lessons.EVIDENCE
    assert r["teacher_review_status"]==r["prerequisite_math_review"]=="REVIEW_PENDING"
    assert r["teacher_solution_visibility"]=="TEACHER_ONLY" and r["teacher_review_evidence"] is None
    assert not r["source_semantics_human_approved"] and r["official_atom_id"] is None
    assert not r["formal_proof_certified"] and not r["free_student_step_verified"] and not r["student_authoritative"]
    assert len(r["reasoned_steps"])==4 and len(r["teacher_examples"])==2 and len(r["student_hint_ladder"])==3
    assert all(len(e["reasoned_solution"])>=3 for e in r["teacher_examples"])
    assert r["nonexample_or_failure"] and r["typical_wrong_solution"] and r["why_wrong_and_repair"]
    assert len(r["source_line_sha256"])==r["source_end_line"]-r["source_start_line"]+1
    assert r["elective_e_optional_example"]==(i==9)

FORGERIES=[
    ("teacher_review_status","APPROVED"),("teacher_review_evidence",{"teacher":"fake"}),
    ("teacher_solution_visibility","STUDENT"),("prerequisite_math_review","APPROVED"),
    ("student_authoritative",True),("source_semantics_human_approved",True),
    ("official_atom_id","fake-official-atom"),("formal_proof_certified",True),
    ("free_student_step_verified",True),("source_evidence_status","APPROVED"),
    ("source_pdf_sha256","0"*64),("source_span_sha256","0"*64),
    ("source_start_line",999),("teacher_examples",[]),
    ("reasoned_steps",[]),("student_hint_ladder",[]),
    ("nonexample_or_failure",""),("formal_definition_or_theorem",""),
]
@pytest.mark.parametrize("i",range(10))
@pytest.mark.parametrize("field,forge",FORGERIES)
def test_each_source_content_authority_manipulation_fails_closed(i,field,forge,rows):
    changed=copy.deepcopy(rows);changed[i][field]=forge
    with pytest.raises(ValueError):lessons.validate(changed)

@pytest.mark.parametrize("i",range(40))
def test_independent_exact_witness_status_not_formal_proof(i,oracle):
    c=oracle["cases"][i]
    assert c["passed"] is True
    assert c["candidate_id"]==lessons.IDS[i//4]
    assert c["outcome"]==("EXACT_FINITE_WITNESS" if i%4<2 else "REJECT_INVALID_PRECONDITION")
    assert not c["teacher_approved"] and not c["general_formal_proof_certified"] and not c["student_free_step_verified"]

@pytest.mark.parametrize("i",range(122))
def test_every_unnumbered_source_line_is_only_sha_review_candidate(i,k00):
    r=k00["line_rows"][i]
    assert r["line_id"].startswith("STD2020-SOURCELINE-P")
    assert len(r["line_sha256"])==64
    assert r["teacher_review"]=="REVIEW_PENDING"
    assert r["curriculum_semantic_classification"]=="UNDETERMINED"
    assert not r["line_is_knowledge_atom"] and r["official_atom_id"] is None
    assert not r["student_authoritative"]

@pytest.mark.parametrize("i",range(5))
def test_de_page_lineage_and_boundary_state(i,k00):
    r=k00["page_rows"][i]
    assert r["printed_page"]==i+69 and r["source_numbered_markers"]==0
    assert r["nonempty_lines"]>0 and r["official_atoms_certified"]==0
    assert r["semantic_review"]=="REVIEW_PENDING"
    assert len(r["original_pdfkit_page_sha256"])==64

@pytest.mark.parametrize("i",range(4))
def test_crosspage_edges_never_auto_adjudicated(i,k00):
    seam=k00["crosspage_seams"][i]
    assert seam["continuation"]=="UNDETERMINED"
    assert seam["semantic_duplicate"]=="UNDETERMINED"
    assert seam["teacher_review"]=="REVIEW_PENDING"

@pytest.mark.parametrize("i",range(7))
def test_seven_track_denominator_not_invented(i,k00,ledger):
    track=lessons.TRACKS[i]
    assert k00["all_seven_official_atom_denominators"][track] is None
    assert ledger["official_atom_denominators"][track] is None
    assert ledger["by_track"][track]["official_atom_denominator"] is None
    assert ledger["by_track"][track]["teacher_approved"]==0
    assert ledger["by_track"][track]["student_authoritative"]==0

@pytest.mark.parametrize("field,value",[
    ("human_approved_clauses",1),("unnumbered_atomization_complete",True),
    ("crosspage_semantic_dedup_complete",True),("teacher_approved",1),
    ("student_authoritative",1),("all_seven_official_atom_denominators",{"ELECTIVE_D":122}),
])
def test_k00_false_global_completion_rejected(field,value,k00):
    changed=copy.deepcopy(k00);changed[field]=value
    with pytest.raises((ValueError,KeyError)):source.validate(changed)

@pytest.mark.parametrize("field,value",[
    ("teacher_review","APPROVED"),("official_atom_id","fake"),
    ("line_is_knowledge_atom",True),("student_authoritative",True),
    ("curriculum_semantic_classification","APPROVED_ATOM"),("line_sha256","0"),
])
def test_k00_per_line_forgery_rejected(field,value,k00):
    changed=copy.deepcopy(k00);changed["line_rows"][0][field]=value
    with pytest.raises(ValueError):source.validate(changed)

@pytest.mark.parametrize("field,value",[
    ("semantic_duplicate","SAME_ATOM"),("continuation","SAME_CLAUSE"),
    ("teacher_review","APPROVED"),
])
def test_k00_crosspage_forgery_rejected(field,value,k00):
    changed=copy.deepcopy(k00);changed["crosspage_seams"][0][field]=value
    with pytest.raises(ValueError):source.validate(changed)

def test_crosswalk_64_175_105_not_official_census(ledger):
    assert ledger["matched_editorial_candidates"]==64
    assert ledger["missing_editorial_candidates"]==175
    assert ledger["total_pending_teacher_manuscripts"]==105
    assert ledger["official_course_coverage_rate"] is None
    assert not ledger["official_atomic_census_complete"]
    assert ledger["teacher_approved"]==ledger["student_authoritative"]==0

@pytest.mark.parametrize("q",[
    "古典概型","分层抽样","不等式","条件概率","贝叶斯",
    "收敛数列","二元函数","反证法","轴对称","球面"])
def test_editor_preview_scoped_and_student_denied(q):
    result=index.editor_preview_search(q,scope="EDITOR_LOCAL",limit=20)
    assert result, q
    for item in result:
        assert set(item)=={"id","course_track","source_candidate_id",
                           "review_status","condition_status","student_publishable","rank"}
        assert item["review_status"]=="REVIEW_PENDING"
        assert item["condition_status"]=="CONDITIONS_NOT_ESTABLISHED"
        assert not item["student_publishable"]
    denial=index.student_evidence_lookup(q)
    assert denial["status"]=="NO_APPROVED_EVIDENCE" and denial["candidates"]==[]
    assert not denial["teacher_solution_exposed"] and not denial["unverified_content_exposed"]

@pytest.mark.parametrize("scope",["","STUDENT","TEACHER","APPROVED",None])
def test_non_internal_scopes_cannot_read_draft_index(scope):
    with pytest.raises(index.LocalEditorOnlyError):
        index.editor_preview_search("贝叶斯",scope=scope)

@pytest.mark.parametrize("q",["","\x00","newline\nx","x"*161])
def test_query_invalid_rejected(q):
    with pytest.raises(ValueError):index.student_evidence_lookup(q)
    with pytest.raises(ValueError):index.editor_preview_search(q,scope="EDITOR_LOCAL")

def test_public_coverage_api_does_not_serve_teacher_content():
    r=TestClient(app).get("/api/knowledge/kb149-review-coverage")
    assert r.status_code==200
    d=r.json()
    assert d["editorial_review_manuscripts"]==105
    assert d["editorial_source_candidates"]==239
    assert d["editorial_candidates_linked"]==64 and d["editorial_candidates_unlinked"]==175
    assert sum(d["by_track"].values())==105
    assert len(d["official_atom_denominators"])==7
    assert all(x is None for x in d["official_atom_denominators"].values())
    assert d["teacher_approved"]==d["student_authoritative"]==0
    assert d["teacher_solution_or_manuscript_included"] is False
    assert len(index.load())==105
    assert not any(key in d for key in ("teacher_examples","reasoned_steps",
        "formal_definition_or_theorem","student_hint_ladder","teacher_solution"))
    assert not any("kb149" in route.path and
        any(fragment in route.path for fragment in ("search","manuscript","draft","teacher"))
        for route in app.routes)
