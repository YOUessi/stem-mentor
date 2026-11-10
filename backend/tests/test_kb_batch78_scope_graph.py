"""Seven-track machine-auditable K00 candidate lineage and false-coverage gates."""
from copy import deepcopy
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch78_scope_graph as B

@pytest.fixture(scope="module")
def graph():return B.build()

def test_reproducible_scope_graph_and_full_source_conservation(graph):
    assert B.OUT.read_text(encoding="utf8")==B.dump(graph)
    assert B.MD.read_text(encoding="utf8")==B.markdown(graph)
    assert len(graph["nodes"])==484+56+60+26
    assert len(graph["edges"])==56+60+26
    assert graph["total_page_line_partitions"]==484
    assert graph["total_unanchored_editorial_triage"]==56
    assert graph["total_subspan_editorial_components"]==60
    assert graph["total_local_math_topic_candidates"]==26
    assert graph["local_candidate_topics_with_review_only_drafts"]==26
    assert graph["general_elective_source_segment_count"]==1
    assert graph["general_elective_scope_triage"]==1
    assert graph["official_full_curriculum_atom_denominator"] is None
    assert graph["teacher_full_page_reviews"]==graph["officially_certified_atom_count"]==graph["student_publishable_count"]==0
    assert graph["source_pdf_sha256"] and len(graph["source_pdf_sha256"])==64
    assert len(graph["sources_sha256"])==4

@pytest.mark.parametrize("t",B.TRACKS)
def test_track_local_candidate_counts_and_review_only_status(t,graph):
    r=graph["by_track"][t]
    assert r["status"]=="CANDIDATE_INVENTORY_NOT_OFFICIAL_COVERAGE"
    assert r["official_atom_denominator"] is None and r["official_coverage"] is None
    assert r["teacher_approved"]==0
    assert r["local_candidate_topics"]==r["local_candidate_topics_with_review_only_drafts"]

@pytest.mark.parametrize("idx",range(484+56+60+26))
def test_every_lineage_node_well_formed_not_certified(idx,graph):
    node=graph["nodes"][idx]
    assert node["id"].split(":",1)[0] in {"SOURCE","TRIAGE","SUBSPAN","CANDIDATE"}
    assert node["track_hint"] in B.TRACKS+("ELECTIVE_GENERAL",)
    assert not any(k in node for k in ("teacher_signature","certified_official_atom_count","approved"))
    if node["id"].startswith("CANDIDATE:"):
        assert node["review_status"]=="REVIEW_PENDING" and node["teacher_draft_ids"]

@pytest.mark.parametrize("idx",range(56+60+26))
def test_every_lineage_edge_has_existing_source_node(idx,graph):
    edge=graph["edges"][idx]
    node_index={r["id"] for r in graph["nodes"]}
    assert edge["source"] in node_index and edge["parent"] in node_index
    assert edge["source"]!=edge["parent"]
    assert edge["relation"] in ("SOURCE_LINES","EDITORIAL_SPLIT","NOT_OFFICIAL_ATOM")

@pytest.mark.parametrize("which",["partition","triage","subspan","draft"])
def test_source_missing_count_rejected(which):
    data=B.read(B.SOURCES[which])
    field={"partition":"segments","triage":"records","subspan":"records","draft":"candidates"}[which]
    data[field].pop()
    with pytest.raises(ValueError):B.build(input_override={which:data})

@pytest.mark.parametrize("which,field,bad",[
 ("partition","source_pdf_sha256","0"*64),
 ("triage","source_pdf_sha256","0"*64),
 ("subspan","source_pdf_sha256","0"*64),
 ("draft","source_pdf_sha256","0"*64),
 ])
def test_cross_stage_wrong_official_pdf_rejected(which,field,bad):
    data=B.read(B.SOURCES[which]);data[field]=bad
    with pytest.raises(ValueError):B.build(input_override={which:data})

@pytest.mark.parametrize("op",[
 "wrong_subspan_parent_sha","out_of_parent_extent","cross_track_reassignment",
 "fake_subspan_official_count","fake_candidate_source_sha","fake_teacher_approval",
 "fake_official_denominator","fake_student_release","orphan_source_segment"])
def test_syllabus_and_release_falsification_rejected(op):
    data={k:B.read(p) for k,p in B.SOURCES.items()}
    if op=="wrong_subspan_parent_sha":data["subspan"]["records"][0]["parent_span_sha256"]="0"*64
    elif op=="out_of_parent_extent":data["subspan"]["records"][0]["last_line"]=999999
    elif op=="cross_track_reassignment":data["subspan"]["records"][0]["track_hint"]="ELECTIVE_E"
    elif op=="fake_subspan_official_count":data["subspan"]["records"][0]["official_atom_contribution"]=1
    elif op=="fake_candidate_source_sha":data["draft"]["candidates"][0]["source_sha256"]="0"*64
    elif op=="fake_teacher_approval":data["draft"]["candidates"][0]["teacher_approved"]=True
    elif op=="fake_official_denominator":data["draft"]["official_denominators"]["ELECTIVE_B"]=11
    elif op=="fake_student_release":data["triage"]["records"][0]["student_publishable"]=True
    else:data["triage"]["records"][0]["segment_id"]="FAKE-SEGMENT"
    with pytest.raises(ValueError):B.build(input_override=data)
