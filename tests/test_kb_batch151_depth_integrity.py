"""KB151 deep-content, source integrity, math and teacher-only RAG regression tests."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"backend"))
import build_kb_batch151_lessons as lessons
import build_kb_batch151_crosswalk as crosswalk
import check_kb_batch151_math as math
from app import kb_batch151_index as index
from app.main import app

@pytest.fixture(scope="module")
def rows():
    return json.loads(lessons.OUT.read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def witnesses():
    return json.loads(math.OUT.read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def gap():
    return json.loads(crosswalk.OUT.read_text(encoding="utf-8"))

def test_all_ten_recomputed_from_original_authoring_are_immutable(rows,witnesses,gap):
    assert rows==lessons.build()
    assert lessons.validate(rows)
    inventory=lessons.audit(rows)
    assert inventory==json.loads(lessons.AUDIT.read_text(encoding="utf-8"))
    assert inventory["total_teacher_only_drafts"]==115
    assert inventory["teacher_approved"]==inventory["student_authoritative"]==0
    assert lessons.render(rows,inventory)==lessons.REPORT.read_text(encoding="utf-8")
    assert lessons.student_safe()==json.loads(lessons.SAFE.read_text(encoding="utf-8"))
    assert witnesses==math.oracle()
    assert gap==crosswalk.build()
    assert crosswalk.validate(gap)
    assert crosswalk.render(gap)==crosswalk.REPORT.read_text(encoding="utf-8")

@pytest.mark.parametrize("i",range(10))
def test_deep_content_and_source_chain(i,rows):
    r=rows[i]
    assert r["source_candidate_id"]==lessons.IDS[i]
    assert r["course_track"]==lessons.EXPECTED[lessons.IDS[i]]
    assert r["source_pdf_sha256"]==lessons.PDF
    assert r["source_evidence_status"]==lessons.EVIDENCE
    assert r["teacher_review_status"]==r["prerequisite_math_review"]=="REVIEW_PENDING"
    assert r["teacher_review_evidence"] is None and r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert r["official_atom_id"] is None and not r["source_semantics_human_approved"]
    assert not r["formal_proof_certified"] and not r["student_authoritative"]
    assert not r["free_student_step_verified"]
    assert len(r["reasoned_steps"])==4
    assert len(r["teacher_examples"])==2 and len(r["student_hint_ladder"])==3
    assert len(r["source_line_sha256"])==r["source_end_line"]-r["source_start_line"]+1
    assert r["elective_e_optional_example"]==(i==9)
    assert all(len(x["reasoned_solution"])>=3 for x in r["teacher_examples"])

FORGED=[
    ("teacher_review_status","APPROVED"),("teacher_review_evidence",{"teacher":"fabricated"}),
    ("teacher_solution_visibility","STUDENT"),("prerequisite_math_review","APPROVED"),
    ("student_authoritative",True),("source_semantics_human_approved",True),
    ("official_atom_id","nonexistent-official-atom"),("formal_proof_certified",True),
    ("free_student_step_verified",True),("source_evidence_status","APPROVED"),
    ("source_pdf_sha256","0"*64),("source_span_sha256","0"*64),
    ("source_start_line",999),("teacher_examples",[]),("reasoned_steps",[]),
    ("student_hint_ladder",[]),("nonexample_or_failure",""),
    ("formal_definition_or_theorem","")
]
@pytest.mark.parametrize("i",range(10))
@pytest.mark.parametrize("field,value",FORGED)
def test_tampered_schema_or_authority_fails(i,field,value,rows):
    bad=copy.deepcopy(rows);bad[i][field]=value
    with pytest.raises(ValueError):
        lessons.validate(bad)

@pytest.mark.parametrize("i",range(40))
def test_exact_math_outcomes_not_formal_proofs(i,witnesses):
    c=witnesses["cases"][i]
    assert c["candidate_id"]==lessons.IDS[i//4]
    assert c["outcome"]==("EXACT_FINITE_WITNESS" if i%4<2 else "REJECT_INVALID_PRECONDITION")
    assert c["passed"] and not c["teacher_approved"]
    assert not c["general_formal_proof_certified"]
    assert not c["student_free_step_verified"]

@pytest.mark.parametrize("i",range(7))
def test_seven_track_denominator_remains_unknown(i,gap):
    track=lessons.TRACKS[i]
    assert gap["official_atom_denominators"][track] is None
    assert gap["by_track"][track]["official_atom_denominator"] is None
    assert gap["by_track"][track]["teacher_approved"]==0
    assert gap["by_track"][track]["student_authoritative"]==0
    assert gap["official_course_coverage_rate"] is None
    assert not gap["official_atomic_census_complete"]

def test_source_crosswalk_not_official_denominator(gap):
    assert gap["editorial_source_candidate_total"]==239
    assert gap["matched_editorial_candidates"]==74
    assert gap["missing_editorial_candidates"]==165
    assert gap["total_pending_teacher_manuscripts"]==115
    assert gap["teacher_approved"]==gap["student_authoritative"]==0

@pytest.mark.parametrize("topic",["古典概型","数乘","余弦定理","等比数列","导数","介值定理","偏导数","充分条件","公倍数","通胀"])
def test_editor_fts_preview_is_only_metadata_and_student_denied(topic):
    hits=index.editor_preview_search(topic,scope="EDITOR_LOCAL",limit=20)
    assert hits,topic
    for hit in hits:
        assert set(hit)=={"id","course_track","source_candidate_id","review_status","condition_status","student_publishable","rank"}
        assert hit["review_status"]=="REVIEW_PENDING"
        assert hit["condition_status"]=="CONDITIONS_NOT_ESTABLISHED"
        assert not hit["student_publishable"]
    student=index.student_evidence_lookup(topic)
    assert student==dict(status="NO_APPROVED_EVIDENCE",candidates=[],
        teacher_solution_exposed=False,unverified_content_exposed=False)

@pytest.mark.parametrize("scope",["",None,"STUDENT","TEACHER","ADMIN","REVIEW_PENDING"])
def test_unauthorized_scope_cannot_access_local_draft_index(scope):
    with pytest.raises(index.LocalEditorOnlyError):
        index.editor_preview_search("等比数列",scope=scope)

def test_coverage_http_endpoint_no_teacher_text():
    body=TestClient(app).get("/api/knowledge/kb151-review-coverage")
    assert body.status_code==200
    obj=body.json()
    assert obj["editorial_review_manuscripts"]==115
    assert obj["editorial_source_candidates"]==239
    assert obj["editorial_candidates_linked"]==74
    assert obj["editorial_candidates_unlinked"]==165
    assert obj["teacher_approved"]==obj["student_authoritative"]==0
    assert obj["official_course_coverage_rate"] is None
    assert all(x is None for x in obj["official_atom_denominators"].values())
    assert not obj["teacher_solution_or_manuscript_included"]
    serialized=json.dumps(obj,ensure_ascii=False)
    for term in ("teacher_examples","reasoned_solution","student_hint_ladder","参考答案"):
        assert term not in serialized
