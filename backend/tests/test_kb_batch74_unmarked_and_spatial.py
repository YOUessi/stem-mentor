"""Batch74 project editorial triage, mathematical prerequisites, and no-spoiler tests."""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from pathlib import Path
import json
import os
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch74_unmarked_review as U
import build_kb_batch74_geometry_theorems as G
import build_kb_batch74_page35_visual as V

@pytest.fixture(scope="module")
def triage():
    return U.build()[0]

@pytest.fixture(scope="module")
def packet():
    return G.build()

def test_reproducibility_and_no_copyright_source(triage,packet):
    data,markdown=U.build()
    assert U.OUTPUT.read_text(encoding="utf8")==U.canonical(data)
    assert U.REPORT.read_text(encoding="utf8")==markdown
    assert G.TARGET.read_text(encoding="utf8")==json.dumps(packet,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    assert triage["no_copyright_source_text"]
    assert triage["parent_witness_sha256"]

def test_local_pdfkit_source_hashes_on_mac():
    if os.getenv("KB74_VERIFY_LOCAL_SOURCE")!="1":
        pytest.skip("Original macOS PDFKit hashes require authorized Mac-only source")
    assert U.B73.validate_witness(U.B73.load(U.B73.WITNESS),verify_mac_source=True)

@pytest.mark.parametrize("index", range(56))
def test_every_unmarked_source_span_traced_with_action(index,triage):
    r=triage["records"][index]
    source=U.B73.load(U.AUDIT)
    witness={x["segment_id"]:x for x in U.B73.load(U.B73.WITNESS)["segments"]}
    risk=source["review_risks"][index]
    assert r["segment_id"]==risk["segment_id"]
    assert r["span_sha256"]==witness[r["segment_id"]]["span_sha256"]
    assert r["source_pdf_sha256"]==U.PDF_SHA
    assert r["priority"]==U.PRIORITY[r["classification"]]
    assert r["next_action"]==U.NEXT[r["classification"]]
    assert r["review_status"]=="PROJECT_EDITORIAL_TRIAGE"
    assert r["teacher_review"]=="REVIEW_PENDING"
    assert r["official_atom_count"] is None
    assert r["student_publishable"] is False

@pytest.mark.parametrize("track", U.B73.TRACKS)
def test_no_fabricated_official_track_denominators(track,triage):
    assert triage["complete_official_denominators"][track] is None
    assert triage["teacher_approved_count"]==0
    assert triage["student_published_count"]==0
    assert triage["teacher_full_page_reviews"]==0

@pytest.mark.parametrize("index",range(4))
def test_four_unmarked_geometry_proof_packets_have_full_conditions(index,packet):
    p=packet["proof_packets"][index]
    assert p["id"]==f"KB74-SP-{index+1:02d}"
    assert len(p["assumptions"])>=2
    assert len(p["proof_steps"])>=3
    assert p["boundary"] and p["counterexample"] and p["common_error"]
    assert len(p["examples"])>=2 and len(p["hints"])==3
    assert p["near_transfer"] and p["far_transfer"]
    assert "分" not in packet["mathematical_certification"] or packet["mathematical_certification"]=="NOT_FORMALLY_CERTIFIED"

@pytest.mark.parametrize("index",range(4))
def test_valid_exact_integer_coordinate_witness(index):
    f=G.FIXTURES[index]
    assert G.evaluates(f["rule"],f) is True

@pytest.mark.parametrize("index",range(4))
def test_invalid_exact_coordinate_premise_is_rejected(index):
    f=G.FIXTURES[index]
    assert G.evaluates(f["rule"],f,invalid=True) is False

@pytest.mark.parametrize("rule",("LINE_PLANE","PLANES","LINE_PERP","PLANES_PERP"))
def test_nonzero_direction_and_independence_essential(rule):
    f=deepcopy(next(f for f in G.FIXTURES if f["rule"]==rule))
    if rule in ("LINE_PLANE","LINE_PERP"):
        f["line"]=([0,0,0],[0,0,0])
    elif rule=="PLANES":
        f["refs"][1]=f["refs"][0]
    else:
        f["other_normal"]=[0,0,0]
    assert not G.evaluates(rule,f)

@pytest.mark.parametrize("rule", ("LINE_PLANE", "PLANES", "LINE_PERP", "PLANES_PERP"))
@pytest.mark.parametrize("invalid_plane", [
    ([0, 0, 0], 0),           # No valid plane
    ([0, 0], 0),              # 2D vector instead of 3D
    ([0, 0, 1, 0], 0),        # 4D vector
    ([0, 0, 1], 0.0),         # Binary float, not exact source
    ([0, True, 1], 0),        # Bool is not a coordinate
])
def test_exact_witness_rejects_malformed_plane_in_all_rules(rule, invalid_plane):
    f=deepcopy(next(f for f in G.FIXTURES if f["rule"]==rule))
    f["plane"]=invalid_plane
    assert G.evaluates(rule,f) is False


@pytest.mark.parametrize("rule", ("LINE_PLANE", "PLANES", "LINE_PERP", "PLANES_PERP"))
@pytest.mark.parametrize("bad_vector", [[1, 0], [1, 0, 0, 0], [1, 0.0, 0], [1, False, 0]])
def test_exact_witness_rejects_bad_reference_or_line_vectors(rule,bad_vector):
    f=deepcopy(next(f for f in G.FIXTURES if f["rule"]==rule))
    if rule=="PLANES_PERP":
        f["other_normal"]=bad_vector
    elif rule=="LINE_PERP":
        f["refs"][0]=(f["refs"][0][0],bad_vector)
    else:
        f["refs"][0]=(f["refs"][0][0],bad_vector)
    assert G.evaluates(rule,f) is False


def test_line_plane_reference_direction_must_lie_in_plane():
    # A reference line passing through the plane is NOT a line in the plane.
    # Without testing the reference direction, a perpendicular direction could
    # incorrectly be accepted as a witness of strict line-plane parallelism.
    f=deepcopy(next(f for f in G.FIXTURES if f["rule"]=="LINE_PLANE"))
    f["refs"]=[([0,0,0],[0,0,1])]
    f["line"]=([1,0,2],[0,0,1])
    assert G.evaluates("LINE_PLANE",f) is False


def test_enforced_56_risk_inventory_and_lineage(triage):
    source=U.B73.load(U.AUDIT)
    assert len(triage["records"])==len(source["review_risks"])==56
    assert sum(triage["classifications"].values())==56
    assert triage["classifications"]["SUBSTANTIVE_UNNUMBERED"]>=10
    assert triage["classifications"]["MIXED_REQUIRES_SPLIT"]>=10
    assert triage["classifications"]["GRAPHIC_VISUAL_INSPECTED_PENDING_TEACHER"]==1
    assert triage["classifications"]["SCHOOL_DEFINED_ELECTIVE"]==1
    U.verify(triage["records"], source)
    missing=deepcopy(triage["records"])
    missing.pop()
    with pytest.raises(AssertionError):
        U.verify(missing,source)

def test_teacher_approval_and_source_sha_tampering_rejected(triage):
    source=U.B73.load(U.AUDIT)
    altered=deepcopy(triage["records"])
    altered[0]["student_publishable"]=True
    with pytest.raises(AssertionError):
        U.verify(altered,source)
    altered=deepcopy(triage["records"])
    altered[0]["span_sha256"]="0"*64
    with pytest.raises(AssertionError):
        U.verify(altered,source)
    altered=deepcopy(triage["records"])
    altered[0]["teacher_review"]="APPROVED"
    with pytest.raises(AssertionError):
        U.verify(altered,source)

def test_source29_not_student_solution_or_certified_proof(packet):
    assert packet["source_segment_id"]=="KB73-P029-L001-008"
    assert packet["distribution"]=="TEACHER_ONLY"
    assert packet["teacher_review"]=="REVIEW_PENDING"
    assert packet["mathematical_certification"]=="NOT_FORMALLY_CERTIFIED"
    assert not packet["student_publishable"]
    assert packet["official_curriculum_atom_count"] is None
    assert packet["exact_valid_fixtures"]==packet["exact_invalid_fixtures"]==4

def test_all_critical_tracks_have_nonempty_review_actions(triage):
    counts=Counter(x["track_hint"] for x in triage["records"])
    assert len(counts)>=7
    e=next(x for x in triage["records"] if x["segment_id"]=="KB73-P073-L013-023")
    assert e["classification"]=="SCHOOL_DEFINED_ELECTIVE"
    assert e["next_action"]=="REQUIRE_SCHOOL_OFFERING_LIST"
    graph=next(x for x in triage["records"] if x["segment_id"]=="KB73-P035-L001-021")
    assert graph["classification"]=="GRAPHIC_VISUAL_INSPECTED_PENDING_TEACHER"
    assert graph["priority"]=="HIGH"


def test_page35_original_image_attestation_and_loop(tmp_path):
    x=V.build()
    assert V.TARGET.read_text(encoding="utf8")==json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    assert x["source_pdf_sha256"]==U.PDF_SHA
    assert x["source_segment_id"]=="KB73-P035-L001-021"
    assert x["evidence_type"]=="AGENT_VISUAL_OBSERVATION_OF_MAC_PDF_RENDER"
    assert x["teacher_review"]=="REVIEW_PENDING"
    assert x["official_atom_count"] is None
    assert x["image_not_committed"] and x["extract_text_corrupted"]
    e={(v["source"],v["target"],v["condition"]) for v in x["edges"]}
    assert ("VALIDATE","CONSTRUCT","INVALID_REALITY_REVISE_MODEL") in e
    assert ("VALIDATE","RESULT","CONSISTENT_WITH_REALITY") in e
    assert len(x["nodes"])==6 and len(x["edges"])==6
    assert not x["student_publishable"]

def test_mac_original_page35_png_hash_if_available():
    if os.getenv("KB74_VERIFY_LOCAL_SOURCE")!="1":
        pytest.skip("PDFKit page image is only on the authorized Mac")
    assert V.digest(V.PDF)==U.PDF_SHA
    assert V.digest(V.IMAGE)==V.PNG_SHA

def test_skew_lines_must_not_support_plane_parallel_proof():
    f=deepcopy(G.FIXTURES[1])
    f["refs"][1]=([0,0,3],[0,1,0])
    assert not G.evaluates("PLANES",f)

def test_line_plane_perpendicular_cannot_use_off_plane_refs():
    f=deepcopy(G.FIXTURES[2])
    f["refs"][0]=([0,0,2],[1,0,0])
    assert not G.evaluates("LINE_PERP",f)

def test_plane_normal_and_contained_line_must_be_nonzero():
    for f in G.FIXTURES:
        x=deepcopy(f)
        x["plane"]=([0,0,0],x["plane"][1])
        assert not G.evaluates(x["rule"],x)
    f=deepcopy(G.FIXTURES[3])
    f["line"]=([0,0,0],[0,0,0])
    assert not G.evaluates("PLANES_PERP",f)

from test_attested_release_batch08 import offline_reviewer_fixture

@pytest.mark.parametrize("index",range(4))
def test_teacher_only_geometry_packets_cannot_leak_into_mixed_student_rag(index,offline_reviewer_fixture,packet):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    p=packet["proof_packets"][index]
    response=student_evidence_lookup(p["name"])
    raw=json.dumps(response,ensure_ascii=False)
    assert {r["knowledge_id"] for r in response["candidates"]}<={doc.id}
    assert p["id"] not in raw
    assert p["proof_steps"][-1] not in raw
    assert p["examples"][-1] not in raw
    assert response["teacher_solution_exposed"] is False
    assert response["unverified_content_exposed"] is False
