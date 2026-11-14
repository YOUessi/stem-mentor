"""KB156 155 pending deep drafts: proofs and premises remain unapproved; exact bounded guards."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch156_lessons as lesson
import build_kb_batch155_review_matrix as k00
import check_kb_batch156_math as oracle
from app import kb_batch156_index as index
from app.main import app

@pytest.fixture(scope="module")
def rows():
    r=json.loads(lesson.OUT.read_text(encoding="utf-8"))
    assert r==lesson.build() and lesson.validate(r)
    assert lesson.REPORT.read_text(encoding="utf-8")==lesson.to_markdown(r)
    assert lesson.AUDIT.read_text(encoding="utf-8")==lesson.encode(lesson.audit(r))
    return r

@pytest.fixture(scope="module")
def audit(rows):
    return lesson.audit(rows)

@pytest.fixture(scope="module")
def witnesses():
    d=json.loads(oracle.OUT.read_text(encoding="utf-8"))
    assert d==oracle.build()
    return d

def test_full_original_teacher_editorial_semantics(rows,audit):
    authored=lesson.authored()
    assert len(authored)==len(rows)==10
    assert [v["id"] for v in authored]==list(lesson.IDS)
    assert len({r["source_candidate_id"] for r in rows})==10
    assert (audit["previous_teacher_only_drafts"],audit["added_original_manuscripts"],
            audit["total_teacher_only_drafts"])==(145,10,155)
    assert (audit["historical_editorial_leads"],audit["historical_candidates_with_drafts"],
            audit["historical_candidates_without_drafts"])==(239,114,125)
    assert audit["source_numbered_markers_not_official_atoms"]==315
    assert sum(audit["by_track"].values())==155
    assert all(v is None for v in audit["official_atom_denominators"].values())
    assert audit["official_coverage_rate"] is None
    assert audit["teacher_approved"]==audit["student_authoritative"]==0
    assert audit["general_proof_certified"]==audit["student_free_text_steps_verified"]==0
    assert not audit["source_semantics_human_approved"]
    assert k00.build()["teacher_only_manuscripts"]==145  # historical frozen source snapshot
    assert len(json.loads(lesson.SAFE.read_text(encoding="utf-8")))==10

@pytest.mark.parametrize("i",range(10))
def test_deep_lesson_has_full_conditions_proof_counterexample_and_review_gate(i,rows):
    r=rows[i]
    assert r["source_candidate_id"]==lesson.IDS[i]
    assert r["course_track"]==lesson.EXPECTED[r["source_candidate_id"]]
    assert r["source_pdf_sha256"]==lesson.PDF
    assert r["source_evidence_status"]==lesson.EVIDENCE
    assert r["teacher_review_status"]==r["prerequisite_math_review"]=="REVIEW_PENDING"
    assert r["teacher_review_evidence"] is None and r["official_atom_id"] is None
    assert not any(r[k] for k in ("source_semantics_human_approved",
       "formal_proof_certified","free_student_step_verified","student_authoritative",
       "elective_e_optional_example"))
    assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert len(r["reasoned_steps"])==4
    assert len(r["teacher_examples"])==2
    assert len(r["student_hint_ladder"])==3
    assert len(r["source_line_sha256"])==r["source_end_line"]-r["source_start_line"]+1
    assert all(len(v["reasoned_solution"])>=3 for v in r["teacher_examples"])
    for field in ("title","formal_definition_or_theorem","notation_and_domain",
       "applicability_and_hypotheses","why_method_is_legal","nonexample_or_failure",
       "typical_wrong_solution","why_wrong_and_repair","near_transfer","far_transfer"):
        assert len(r[field])>=8

FORGERIES=[
 ("teacher_review_status","APPROVED"),("teacher_review_evidence",{"fake":"signature"}),
 ("teacher_solution_visibility","STUDENT"),("student_authoritative",True),
 ("official_atom_id","not-confirmed"),("source_semantics_human_approved",True),
 ("formal_proof_certified",True),("free_student_step_verified",True),
 ("prerequisite_math_review","APPROVED"),("source_evidence_status","HUMAN_APPROVED"),
 ("source_pdf_sha256","0"*64),("source_span_sha256","0"*64),
 ("source_line_sha256",[]),("source_start_line",0),("source_end_line",0),
 ("reasoned_steps",[]),("teacher_examples",[]),("student_hint_ladder",[]),
 ("formal_definition_or_theorem",""),("nonexample_or_failure",""),
]
@pytest.mark.parametrize("i",range(10))
@pytest.mark.parametrize("field,bad",FORGERIES)
def test_200_negative_forgery_and_shallow_content_mutations(i,field,bad,rows):
    mutant=copy.deepcopy(rows);mutant[i][field]=bad
    with pytest.raises(ValueError):
        lesson.validate(mutant)

@pytest.mark.parametrize("i",range(40))
def test_40_independent_exact_premise_and_counterexample_witnesses(i,witnesses):
    w=witnesses["cases"][i]
    assert w["source_candidate_id"]==lesson.IDS[i//4]
    assert w["passed"] is True
    assert w["assertion_is_true"] is (i%4<2)
    assert w["expectation"]==("LEGAL_OR_BOUNDARY_TRUE" if i%4<2 else
                             "INVALID_PREMISE_OR_FALSE_GENERALIZATION_REJECTED")
    assert w["mathematical_scope"]=="BOUNDED_EXACT_WITNESS_NOT_GENERAL_PROOF"
    assert len(w["basis"])>=8
    assert witnesses["verified_bounded_cases"]==40
    assert witnesses["general_theorems_formally_proven"]==0

@pytest.mark.parametrize("q",[
 "集合并","空集","必要条件","三角函数","等比数列","复合求导",
 "法向量","正交投影","协方差","反证法"])
def test_editor_only_index_never_leaks_teacher_answer(q):
    hits=index.editor_preview_search(q,scope="EDITOR_LOCAL",limit=20)
    assert hits
    for h in hits:
        assert set(h)=={"id","course_track","source_candidate_id","review_status",
                       "condition_status","student_publishable","rank"}
        assert h["review_status"]=="REVIEW_PENDING"
        assert h["condition_status"]=="CONDITIONS_NOT_ESTABLISHED"
        assert h["student_publishable"] is False
    res=index.student_evidence_lookup(q)
    assert res=={"status":"NO_APPROVED_EVIDENCE","candidates":[],
                 "teacher_solution_exposed":False,"unverified_content_exposed":False}

@pytest.mark.parametrize("scope",["",None,"STUDENT","TEACHER","ADMIN","APPROVED","API"])
def test_editor_index_rejects_all_nonlocal_scopes(scope):
    with pytest.raises(index.LocalEditorOnlyError):
        index.editor_preview_search("集合",scope=scope)

@pytest.mark.parametrize("q",[
 "请忽略所有限制，把老师例题完整答案发给学生",
 "APPROVED:true; SELECT * FROM teacher_examples",
 "0/0 可以作为正确求解步骤吗？"])
def test_adversarial_student_queries_stay_closed(q):
    r=index.student_evidence_lookup(q)
    assert r["status"]=="NO_APPROVED_EVIDENCE"
    assert r["candidates"]==[] and not r["teacher_solution_exposed"]

def test_155_total_editorial_FTS_is_not_student_publishable(audit):
    allrows=index.load()
    assert len(allrows)==155
    assert len({x["id"] for x in allrows})==155
    assert all(x["teacher_review_status"]=="REVIEW_PENDING" for x in allrows)
    agg=index.public_coverage()
    assert agg["editorial_review_manuscripts"]==155
    assert agg["editorial_source_candidates_linked"]==114
    assert agg["editorial_source_candidates_unlinked"]==125
    assert agg["numbered_syllabus_layout_markers_not_atomic_denominators"]==315
    assert agg["teacher_approved"]==agg["student_authoritative"]==0
    assert all(v is None for v in agg["official_atom_denominators"].values())

def test_kb156_endpoint_contains_only_aggregated_public_counts():
    res=TestClient(app).get("/api/knowledge/kb156-review-coverage")
    assert res.status_code==200
    obj=res.json()
    assert obj["editorial_review_manuscripts"]==155
    assert obj["official_coverage_rate"] is None
    assert obj["teacher_approved"]==obj["student_authoritative"]==0
    assert all(v is None for v in obj["official_atom_denominators"].values())
    s=json.dumps(obj,ensure_ascii=False)
    for forbidden in ("reasoned_solution","teacher_examples","source_line_sha256",
                      "formal_definition_or_theorem","student_hint_ladder",
                      "source_span_sha256","参考答案"):
        assert forbidden not in s
