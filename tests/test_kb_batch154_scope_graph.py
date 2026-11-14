"""Batch154 independent provenance integrity, C/D/E boundary and student denial regressions."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch154_scope_graph as g
from app.kb_batch154_scope_status import public_status
from app import kb_batch154_index as index
from app.main import app

@pytest.fixture(scope="module")
def value():
    return g.load(g.OUT)

def test_graph_rebuild_and_materialized_md_are_identical(value):
    assert g.build()==value
    assert g.validate(value)
    assert g.REPORT.read_text(encoding="utf-8")==g.render(value)

def test_distinct_provenance_populations_are_conserved(value):
    assert (value["source_pages_scanned"],value["source_numbered_markers"],
            value["original_cde_lines_classified"],value["cde_proposals_from_unnumbered_sources"])==(61,315,122,32)
    assert (value["historical_editorial_leads"],value["pending_teacher_manuscripts"],
            value["linked_editorial_leads"],value["missing_editorial_leads"])==(239,145,104,135)
    assert sum(z["source_numbered_markers"] for z in value["by_track"].values())==315
    assert sum(z["nonnumbered_cde_editorial_proposals"] for z in value["by_track"].values())==32
    assert value["by_track"]["ELECTIVE_D"]["source_numbered_markers"]==0
    assert value["by_track"]["ELECTIVE_E"]["source_numbered_markers"]==0
    assert (value["by_track"]["ELECTIVE_D"]["nonnumbered_cde_editorial_proposals"],
            value["by_track"]["ELECTIVE_E"]["nonnumbered_cde_editorial_proposals"])==(17,13)

@pytest.mark.parametrize("page",range(13,74))
def test_each_of_61_pages_retains_distinct_unknown_semantics(page,value):
    row=value["pages"][page-13]
    assert row["printed_page"]==page
    assert row["pdf_page_index"]==page+7
    assert row["semantic_atom_count"]=="UNKNOWN"
    assert row["content_requirements_in_unenumerated_lines"]=="UNKNOWN"
    assert row["teacher_scope_review"]=="REVIEW_PENDING"
    assert len(row["pdf_text_sha256"])==64
    assert len(row["numbered_marker_ids"])==row["numbered_source_markers"]

@pytest.mark.parametrize("i",range(315))
def test_each_numbered_source_marker_is_located_but_not_deemed_atom(i,value):
    source=g.load(g.STD)["enumerated_source_anchors"][i]
    page=value["pages"][source["printed_page"]-13]
    assert source["id"] in page["numbered_marker_ids"]
    assert source["teacher_review"]=="PENDING"
    assert source["status"]=="SOURCE_ENUMERATION_UNREVIEWED_NOT_OFFICIAL_ATOM"
    assert not source["approved_lesson_ids"]

@pytest.mark.parametrize("i",range(122))
def test_cde_line_is_immutable_unapproved_original_sha(i):
    line=g.load(g.CDE)["source_line_partition"][i]
    assert line["teacher_review"]=="REVIEW_PENDING"
    assert not line["original_text_committed"]
    assert not line["officially_certified"]
    assert line["classification"] in {"ELECTIVE_C","ELECTIVE_D","ELECTIVE_E","PARATEXT"}
    assert len(line["original_line_sha256"])==64

@pytest.mark.parametrize("i",range(32))
def test_each_cde_proposal_preserves_original_line_and_elective_scope(i,value):
    proposal=value["cde_unnumbered_proposal_junction"][i]
    original=next(p for p in g.load(g.CDE)["proposals"] if p["id"]==proposal["proposal_id"])
    assert proposal["teacher_review"]=="REVIEW_PENDING"
    assert proposal["official_atom_id"] is None and not proposal["officially_certified"]
    assert proposal["source_line_ids"]==original["source_line_ids"]
    assert proposal["source_line_sha256"]==original["source_line_sha256"]
    assert proposal["is_school_elective_example"]==(proposal["course_track"]=="ELECTIVE_E")

@pytest.mark.parametrize("field,bad",[
    ("seven_track_official_census_complete",True),
    ("unnumbered_source_requirements_human_split_complete",True),
    ("cross_page_semantic_dedup_human_review_complete",True),
    ("automatically_merged_source_clauses",1),
    ("real_teacher_approved",1),("student_authoritative",1),
    ("source_numbered_markers",314),("pending_teacher_manuscripts",134),
    ("original_cde_lines_classified",121),
])
def test_source_ledger_forgeries_are_rejected(field,bad,value):
    tampered=copy.deepcopy(value);tampered[field]=bad
    with pytest.raises(ValueError):
        g.validate(tampered)

@pytest.mark.parametrize("track",g.TRACKS)
def test_each_track_count_rejects_counterfeit_official_approval(track,value):
    tampered=copy.deepcopy(value)
    tampered["official_atom_denominators"][track]=5
    with pytest.raises(ValueError):
        g.validate(tampered)
    tampered=copy.deepcopy(value)
    tampered["by_track"][track]["official_approved"]=1
    with pytest.raises(ValueError):
        g.validate(tampered)

@pytest.mark.parametrize("mutation",["line_sha","track","optional","approval"])
def test_false_cde_original_provenance_is_detected(tmp_path,monkeypatch,mutation):
    original=g.load(g.CDE)
    p=original["proposals"][0]
    if mutation=="line_sha":p["source_line_sha256"][0]="0"*64
    elif mutation=="track":p["source_track"]="ELECTIVE_D"
    elif mutation=="optional":p["is_school_elective_example"]=True
    else:p["teacher_approved"]=True
    clone=tmp_path/"mutated.json";clone.write_text(g.encode(original),encoding="utf-8")
    monkeypatch.setattr(g,"CDE",clone)
    with pytest.raises(ValueError):
        g.source_index()

@pytest.mark.parametrize("query",["函数定义域","跨页课标","概率","导数","二项分布","体育赛程"])
def test_unapproved_content_never_reaches_student(query):
    assert index.student_evidence_lookup(query)["status"]=="NO_APPROVED_EVIDENCE"

def test_public_endpoint_never_leaks_teacher_solution_or_raw_standard():
    r=TestClient(app).get("/api/knowledge/kb154-source-scope-status")
    assert r.status_code==200
    body=r.json()
    assert body==public_status()
    assert body["source_pages_indexed"]==61
    assert body["numbered_source_markers_not_atoms"]==315
    assert body["cde_unnumbered_editorial_proposals_not_atoms"]==32
    assert body["pending_teacher_manuscripts"]==145
    assert body["student_authoritative"]==body["teacher_approved"]==0
    assert not body["official_atomic_census_complete"]
    assert all(x is None for x in body["official_atom_denominators"].values())
    assert body["teacher_solution_or_copyright_source_included"] is False
    text=json.dumps(body,ensure_ascii=False)
    for banned in ("reasoned_solution","teacher_examples","source_line_sha256","source_span_sha256","原始课标","正式参考答案"):
        assert banned not in text
