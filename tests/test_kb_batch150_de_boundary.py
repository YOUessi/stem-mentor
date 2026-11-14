"""Negative regressions: source boundary, illegal official atom counts, privacy and license."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch150_de_boundary as scope

@pytest.fixture(scope="module")
def clean():
    v=scope.build()
    assert scope.validate(v)
    return v

def test_licensed_line_count_and_exact_editorial_track_boundaries(clean):
    assert len(clean["source_line_partition"])==122
    assert clean["source_line_counts"]=={
        "ELECTIVE_C":5,"ELECTIVE_D":100,"ELECTIVE_E":10,"PARATEXT":7}
    assert scope.owner(69,1)=="ELECTIVE_C"
    assert scope.owner(69,5)=="ELECTIVE_C"
    assert scope.owner(69,6)=="ELECTIVE_D"
    assert scope.owner(73,12)=="ELECTIVE_D"
    assert scope.owner(73,13)=="ELECTIVE_E"
    assert scope.owner(73,22)=="ELECTIVE_E"
    assert scope.owner(73,23)=="PARATEXT"
    assert scope.owner(72,25)=="PARATEXT"

def test_proposals_original_and_not_approved(clean):
    proposals=clean["proposals"]
    assert len(proposals)==32
    assert dict(Counter(p["source_track"] for p in proposals))=={
        "ELECTIVE_C":2,"ELECTIVE_D":17,"ELECTIVE_E":13}
    assert all(p["teacher_review"]=="REVIEW_PENDING" for p in proposals)
    assert all(p["curriculum_scope_status"]=="EDITORIAL_PROPOSAL_NOT_APPROVED_ATOM" for p in proposals)
    assert all(p["teacher_approved"] is False for p in proposals)
    assert all(p["official_knowledge_atom_id"] is None for p in proposals)
    assert all(p["lesson_complete"] is False for p in proposals)
    assert all(p["theorem_proof_required"] is False for p in proposals)
    assert all(p["student_authoritative"] is False for p in proposals)
    assert all(p["is_school_elective_example"] is (p["source_track"]=="ELECTIVE_E") for p in proposals)

def test_original_32_semantic_topics_not_forged_coverage(clean):
    assert clean["approved_atom_denominators"]=={t:None for t in scope.TRACKS}
    assert not clean["complete_official_course_census"]
    assert clean["valid_teacher_manuscripts_new"]==0
    assert clean["teacher_approved"]==0
    assert clean["student_authoritative"]==0
    assert "not" in clean["warning"].lower()
    assert scope.render(clean).count("STD2020-EDITORIAL-PROP150-")==32

def test_sport_crosspage_continuation_does_not_change_track(clean):
    p=next(x for x in clean["proposals"] if x["original_paraphrase"].startswith("投掷跳跃"))
    assert p["source_line_ids"][0]==scope.source_id(72,22)
    assert p["source_line_ids"][-1]==scope.source_id(73,1)
    assert all(scope.owner(int(i.split("-P")[1][:2]),int(i.split("-L")[1]))=="ELECTIVE_D"
               for i in p["source_line_ids"])

def test_no_licensed_source_text_or_student_answers_in_committed_index(clean):
    s=json.dumps(clean,ensure_ascii=False)
    assert "普通高中数学课程标准" not in s
    assert "体育运动中的数学四个专题" not in s
    assert "教师完整解答" not in s
    assert "teacher_solution" not in s
    assert "original_text" not in s or "original_text_committed" in s
    assert all(len(p["original_paraphrase"])<36 for p in clean["proposals"])

def test_committed_json_markdown_exactly_generated(clean):
    assert scope.OUT.read_text(encoding="utf-8") == json.dumps(
        clean,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
    assert scope.REPORT.read_text(encoding="utf-8")==scope.render(clean)

@pytest.mark.parametrize("page,line,forged",[
    (69,1,"ELECTIVE_D"),(69,6,"ELECTIVE_C"),(73,13,"ELECTIVE_D"),
    (73,12,"ELECTIVE_E"),(72,25,"ELECTIVE_D"),(73,23,"ELECTIVE_E"),
])
def test_wrong_source_course_or_page_furniture_rejected(clean,page,line,forged):
    m=copy.deepcopy(clean)
    r=next(x for x in m["source_line_partition"]
           if x["printed_page"]==page and x["pdfkit_line"]==line)
    r["classification"]=forged
    with pytest.raises(ValueError):
        scope.validate(m)

@pytest.mark.parametrize("field,forged",[
    ("source_line_counts",{"ELECTIVE_C":0,"ELECTIVE_D":122,"ELECTIVE_E":0,"PARATEXT":0}),
    ("approved_atom_denominators",{"ELECTIVE_D":100}),
    ("complete_official_course_census",True),
    ("teacher_approved",1),("student_authoritative",1),
    ("valid_teacher_manuscripts_new",32),("proposed_count",33),
])
def test_false_census_release_and_completion_claims_rejected(clean,field,forged):
    m=copy.deepcopy(clean)
    m[field]=forged
    with pytest.raises(ValueError):
        scope.validate(m)

@pytest.mark.parametrize("field,forged",[
    ("source_track","ELECTIVE_D"),("teacher_review","APPROVED"),
    ("teacher_approved",True),("student_authoritative",True),
    ("lesson_complete",True),("source_pdf_sha256","bad"),
    ("source_line_sha256",["bad"]),("is_school_elective_example",False),
])
def test_forged_proposal_source_scope_or_authority_rejected(clean,field,forged):
    m=copy.deepcopy(clean)
    m["proposals"][-1][field]=forged
    with pytest.raises(ValueError):
        scope.validate(m)

@pytest.mark.parametrize("kind",["line_sha","duplicate_line","missing_proposal",
                                "false_boundary","wrong_span","wrong_id"])
def test_provenance_tampering_rejected(clean,kind):
    m=copy.deepcopy(clean)
    if kind=="line_sha":
        m["source_line_partition"][4]["original_line_sha256"]="f"*64
    elif kind=="duplicate_line":
        m["source_line_partition"][1]["line_id"]=m["source_line_partition"][0]["line_id"]
    elif kind=="missing_proposal":
        m["proposals"].pop()
    elif kind=="false_boundary":
        m["source_boundary_evidence"][1]["line"]=12
    elif kind=="wrong_span":
        m["proposals"][17]["source_line_ids"].append(scope.source_id(73,13))
    elif kind=="wrong_id":
        m["proposals"][17]["id"]="APPROVED-0001"
    with pytest.raises(ValueError):
        scope.validate(m)

def test_original_boundary_line_hashes_are_proper_sha256(clean):
    assert all(len(x["original_line_sha256"])==64 and
               all(c in "0123456789abcdef" for c in x["original_line_sha256"])
               for x in clean["source_line_partition"])

def test_public_api_aggregates_no_source_content_or_solutions():
    from backend.app.kb_batch150_scope import public_status
    data=public_status()
    assert data["source_line_counts"]=={
        "ELECTIVE_C":5,"ELECTIVE_D":100,"ELECTIVE_E":10,"PARATEXT":7}
    assert data["preliminary_semantic_topic_proposals"]==32
    assert data["source_c_to_d_boundary"]["source_line"]==6
    assert data["source_d_to_e_boundary"]["source_line"]==13
    assert data["student_evidence_status"]=="NO_APPROVED_EVIDENCE"
    assert data["teacher_approved"]==data["student_authoritative"]==0
    assert not data["licensed_syllabus_text_included"]
    assert not data["teacher_solution_or_manuscript_included"]
    assert all(n is None for n in data["approved_atom_denominators"].values())
    for prohibited in ["proposals","teacher_solution","original_source_lines","source_line_sha256"]:
        assert prohibited not in data

def test_actual_fastapi_route_registration_is_aggregate_only():
    from backend.app.main import app
    matches=[route for route in app.routes
             if getattr(route,"path",None)=="/api/knowledge/kb150-source-boundary-status"]
    assert len(matches)==1
    assert "GET" in matches[0].methods
    result=matches[0].endpoint()
    assert result["student_evidence_status"]=="NO_APPROVED_EVIDENCE"
    assert result["official_course_coverage_rate"] is None
    assert result["teacher_approved"]==0
    assert "proposals" not in result
