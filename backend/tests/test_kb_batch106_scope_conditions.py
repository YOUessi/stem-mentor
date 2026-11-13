"""Fail-closed regression for source-grounded candidate atomization (no teacher approval)."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch106_scope_authoring import CANDIDATES as ATOM_CANDIDATES, PARTITIONS as PAGE_PARTITIONS, BRIDGES as CROSS_PAGE_BRIDGES
from build_kb_batch106_scope_conditions import build,REPORT
from app.kb_batch106_math import witness

@pytest.fixture(scope="module")
def report():
    return build()

def test_candidate_counts_are_not_official_denominators(report):
    assert report["provisional_requirement_candidate_count"]==25
    assert report["provisional_requirement_count_by_track"]["COMPULSORY"]==10
    assert report["provisional_requirement_count_by_track"]["ELECTIVE_A"]==15
    assert len(report["official_seven_track_denominators"])==7
    assert set(report["official_seven_track_denominators"].values())=={None}
    assert report["teacher_full_page_atomizations"]==0
    assert report["student_authoritative_releases"]==0
    assert report["teacher_approvals"]==0

def test_two_full_page_structural_partitions(report):
    assert report["line_count_by_page"]=={"16":29,"53":28}
    assert report["structural_partition_count"]==14
    for page in (16,53):
        covered=[i for x in report["structural_partitions"] if x["page"]==page
                 for i in range(x["start"],x["end"]+1)]
        assert covered==list(range(1,report["line_count_by_page"][str(page)]+1))

def test_two_bridge_ranges_and_source_shas(report):
    assert [(r["from_page"],r["to_page"]) for r in report["cross_page_bridges"]]==[(15,16),(52,53)]
    assert all(len(r["from_page_sha256"])==64 and len(r["to_page_sha256"])==64
               for r in report["cross_page_bridges"])

def test_frozen_generated_artifact(report):
    assert json.loads(REPORT.read_text(encoding="utf8"))==report

@pytest.mark.parametrize("index",range(25))
def test_each_candidate_math_precise_and_non_authoritative(report,index):
    r=report["candidates"][index]
    x=ATOM_CANDIDATES[index]
    assert r["title"]==x["title"]
    assert r["source_line_start"]==x["start"]
    assert r["source_line_end"]==x["end"]
    assert r["printed_page"]==x["page"]
    assert len(r["source_page_text_sha256"])==64
    assert r["teacher_review_status"]=="REVIEW_PENDING"
    assert r["official_atom_id"] is None
    assert r["publishable_for_student"] is False
    assert r["formally_certified"] is False
    oracle=witness(x["finite_oracle_key"])
    assert oracle==r["independently_computed_witness"]
    assert oracle["general_proof_certified"] is False
    assert oracle["student_step_verified"] is False

@pytest.mark.parametrize("index",range(25))
def test_reject_cross_track_for_every_candidate(index):
    atoms=deepcopy(ATOM_CANDIDATES)
    atoms[index]["track"]="ELECTIVE_A" if atoms[index]["page"]==16 else "COMPULSORY"
    with pytest.raises(ValueError,match="cross-track"):build(atoms=atoms)

@pytest.mark.parametrize("index",range(25))
def test_reject_invalid_source_line(index):
    atoms=deepcopy(ATOM_CANDIDATES)
    atoms[index]["start"]=0
    with pytest.raises(ValueError,match="source line range"):build(atoms=atoms)

@pytest.mark.parametrize("index",range(25))
def test_reject_orphan_existing_draft_reference(index):
    atoms=deepcopy(ATOM_CANDIDATES)
    atoms[index]["related_draft_ids"]=["math.hs.nonexistent.approved"]
    with pytest.raises(ValueError,match="orphan draft"):build(atoms=atoms)

@pytest.mark.parametrize("index",range(25))
def test_reject_forged_human_approval_or_official_id(index):
    atoms=deepcopy(ATOM_CANDIDATES)
    atoms[index]["review_status"]="APPROVED"
    with pytest.raises(ValueError,match="forged author fields"):build(atoms=atoms)

@pytest.mark.parametrize("name",["official_atom_id","teacher_signature","student_publishable","student_answer_verified"])
def test_reject_forged_authority_metadata(name):
    atoms=deepcopy(ATOM_CANDIDATES)
    atoms[0][name]=True
    with pytest.raises(ValueError,match="forged author fields"):build(atoms=atoms)

@pytest.mark.parametrize("bad",["none","overlap","out_of_order","unknown_page"])
def test_reject_incorrect_structural_page_coverage(bad):
    parts=deepcopy(PAGE_PARTITIONS)
    if bad=="none":parts[16]=parts[16][1:]
    elif bad=="overlap":parts[16].insert(1,(1,3,"DUPLICATE_SCOPE"))
    elif bad=="out_of_order":parts[16][0],parts[16][1]=parts[16][1],parts[16][0]
    else:parts[54]=[(1,2,"FORGED_PAGE")]
    with pytest.raises(ValueError):build(parts=parts)

@pytest.mark.parametrize("bad",["missing","wrong_page","wrong_track","truncated"])
def test_reject_broken_cross_page_provenance(bad):
    bridges=deepcopy(CROSS_PAGE_BRIDGES)
    if bad=="missing":bridges.pop()
    elif bad=="wrong_page":bridges[0]["to_page"]=53
    elif bad=="wrong_track":bridges[1]["track"]="COMPULSORY"
    else:bridges[1]["to_lines"]=[1,3]
    with pytest.raises(ValueError):build(bridges=bridges)

def test_reject_repeated_candidate_title():
    atoms=deepcopy(ATOM_CANDIDATES)
    atoms[1]["title"]=atoms[0]["title"]
    with pytest.raises(ValueError,match="duplicate mathematical requirement"):build(atoms=atoms)

@pytest.mark.parametrize("field",["editorial_interpretation","mathematical_preconditions","misleading_generalization"])
def test_reject_empty_mathematical_context(field):
    atoms=deepcopy(ATOM_CANDIDATES)
    atoms[4][field]=""
    with pytest.raises(ValueError,match="incomplete math editorial evidence"):build(atoms=atoms)

def test_reject_unrecognized_math_witness():
    with pytest.raises(ValueError,match="unknown"):witness("arbitrary_llm_assertion")

@pytest.mark.parametrize("page",[16,53])
def test_original_pinned_source_page_sha_stored(report,page):
    rows=[r for r in report["candidates"] if r["printed_page"]==page]
    assert rows
    assert len(set(r["source_page_text_sha256"] for r in rows))==1
    assert all(r["source_pdf_sha256"]==report["source_pdf_sha256"] for r in rows)

def test_original_editorial_reason_not_official_text(report):
    assert report["not_new_complete_deep_lessons"] is True
    assert report["general_formal_proof_certificates"]==0
    assert all(r["provenance_class"]=="OFFICIAL_SOURCE_RANGE_EDITORIAL_PROPOSAL"
               for r in report["candidates"])

@pytest.mark.parametrize("index",range(25))
def test_reject_legal_but_wrong_source_clause_range(index):
    rows=deepcopy(ATOM_CANDIDATES)
    r=rows[index]
    r["start"]=r["end"]  # still within page; must match the clause lock
    if r["start"]==ATOM_CANDIDATES[index]["start"]:
        r["end"]=r["end"]+1  # still in page bounds for these 1-line cases
    with pytest.raises(ValueError,match="clause lock mismatch"):
        build(atoms=rows)
