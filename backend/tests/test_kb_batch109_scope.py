"""Batch109 page 18/55 source integrity, negative authority and exact witness regression."""
from __future__ import annotations
import json,sys
from copy import deepcopy
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch109_scope as B
from kb_batch109_scope_authoring import CANDIDATES,PARTITIONS

@pytest.fixture(scope="module")
def artifact():return B.build()

def test_full_source_partition_conservation(artifact):
    assert artifact["pages"]==[19,56]
    assert artifact["line_counts"]=={"19":27,"56":27}
    assert artifact["source_lines_total"]==54
    assert len(artifact["structural_partitions"])==28
    for page,limit in ((19,27),(56,27)):
        lines=[n for seg in artifact["structural_partitions"] if seg["page"]==page
               for n in range(seg["start"],seg["end"]+1)]
        assert lines==list(range(1,limit+1))

def test_candidate_math_scope_not_official_atom(artifact):
    assert artifact["new_editorial_candidates"]==20
    assert artifact["track_hint_counts"]["COMPULSORY"]==9
    assert artifact["track_hint_counts"]["ELECTIVE_A"]==11
    assert set(artifact["official_seven_track_atom_denominators"].values())=={None}
    assert artifact["teacher_full_page_atomizations"]==0
    assert artifact["teacher_approvals"]==0
    assert artifact["student_authoritative_releases"]==0
    assert artifact["bounded_exact_witnesses"]==15
    assert artifact["pedagogy_items_not_math_proofs"]==5

@pytest.mark.parametrize("idx",range(20))
def test_each_editorial_record_source_and_math(idx,artifact):
    a=CANDIDATES[idx];r=artifact["candidates"][idx]
    assert r["key"]==a["key"] and r["title"]==a["title"]
    assert r["page"]==a["page"]
    assert r["source_pdf_sha256"]==artifact["source_pdf_sha256"]
    assert len(r["source_page_pdfkit_sha256"])==64
    assert r["track_hint"]==("COMPULSORY" if r["page"]==19 else "ELECTIVE_A")
    assert r["official_atom_id"] is None
    assert r["teacher_review_status"]=="REVIEW_PENDING"
    assert not r["student_authoritative_release"]
    assert not r["math_witness"]["general_proof_certified"]
    witness=B.exact_witness(a["key"])
    assert r["math_witness"]==witness
    if a["kind"]=="PEDAGOGY":
        assert witness["status"]=="PEDAGOGY_NOT_AUTOMATICALLY_CHECKABLE"
        assert not witness["finite_exact_positive_passed"]
    else:
        assert witness["status"]=="FINITE_EXACT_INSTANCE_ONLY"
        assert witness["finite_exact_positive_passed"]
        assert witness["invalid_generalization_rejected"]

@pytest.mark.parametrize("idx",range(20))
def test_reject_duplicate_candidate_key(idx):
    rows=deepcopy(CANDIDATES)
    rows[idx]["key"]=rows[(idx+1)%20]["key"]
    with pytest.raises(ValueError):B.build(candidates=rows)

@pytest.mark.parametrize("idx",range(20))
def test_reject_source_line_tampering(idx):
    rows=deepcopy(CANDIDATES)
    rows[idx]["start"]=99
    with pytest.raises(ValueError):B.build(candidates=rows)

@pytest.mark.parametrize("idx",range(20))
def test_reject_fake_approval(idx):
    rows=deepcopy(CANDIDATES)
    rows[idx]["teacher_review_status"]="APPROVED"
    with pytest.raises(ValueError,match="schema drift"):B.build(candidates=rows)

@pytest.mark.parametrize("idx",range(20))
def test_reject_math_precondition_erasure(idx):
    rows=deepcopy(CANDIDATES)
    rows[idx]["mathematical_preconditions"]="none"
    with pytest.raises(ValueError):B.build(candidates=rows)

@pytest.mark.parametrize("page", [19,56])
def test_reject_missing_source_lines(page):
    copies=deepcopy(PARTITIONS)
    copies[page][0]=(2,3,"CORRUPTED")
    with pytest.raises(ValueError,match="page missing"):B.build(partitions=copies)

@pytest.mark.parametrize("key",["nonexistent","fake_oracle","teacher_certified"])
def test_unknown_math_witness_rejected(key):
    with pytest.raises(ValueError,match="unknown finite math witness"):B.exact_witness(key)

def test_artifact_can_be_rebuilt_without_drift(artifact):
    assert B.OUT.read_text(encoding="utf8")==B.serialize(artifact)
    assert B.MD.read_text(encoding="utf8")==B.markdown(artifact)
