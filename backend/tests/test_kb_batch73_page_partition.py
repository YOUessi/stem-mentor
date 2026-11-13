"""Batch73 source-line partition, anti-forgery, and candidate-link coverage tests."""
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
import build_kb_batch73_page_partition as M


@pytest.fixture(scope="module")
def witness():
    return M.load(M.WITNESS)


@pytest.fixture(scope="module")
def audit():
    return M.build()[0]


def test_mac_source_has_exact_pinned_pdfkit_page_hashes(witness):
    if os.getenv("KB73_VERIFY_LOCAL_SOURCE") != "1":
        pytest.skip("macOS-only original PDFKit source not mounted on Linux CI")
    assert M.validate_witness(witness, verify_mac_source=True)


def test_json_and_markdown_are_exactly_reproducible(audit):
    a, md = M.build()
    assert M.AUDIT.read_text(encoding="utf-8") == M.canonical(a)
    assert M.REPORT.read_text(encoding="utf-8") == md


def test_all_original_pages_are_partitioned_no_holes(witness, audit):
    assert witness["segment_count"] == 484
    assert audit["full_source_pages_line_partitioned"] == 61
    assert audit["heuristic_source_anchors"] == 428
    assert audit["internal_provisional_atom_splits"] == 62
    assert audit["independent_nonatom_requirements"] == 28
    assert sum(x["heuristic_segment_count"] for x in audit["tracks"].values()) == 484
    assert sum(x["pdfkit_lines_accounted_for"] for x in audit["tracks"].values()) == sum(
        M.load(M.REG)["page_line_counts"].values())
    assert M.validate_witness(witness)


def test_no_fake_official_denominator_approvals_or_copyright_text(audit, witness):
    assert all(x is None for x in audit["official_denominator_by_track"].values())
    assert all(x is None for x in witness["officially_certified_denominators"].values())
    assert not audit["curriculum_scope_complete"]
    assert audit["page_partition_is_not_full_clause_parse"]
    assert audit["source_text_embedded"] is False
    assert witness["includes_copyright_text"] is False
    assert audit["teacher_full_page_reviews"] == audit["approved_lessons"] == audit["student_published"] == 0
    assert all(not x["student_publishable"] and not x["counted_in_official_atom_denominator"]
               and x["official_clause_membership"] == "UNDETERMINED" for x in audit["segments"])
    assert "source_text" not in M.WITNESS.read_text()


@pytest.mark.parametrize("page", range(13, 74))
def test_each_page_contiguous_and_pinned(page, witness):
    rows = [x for x in witness["segments"] if x["printed_page"] == page]
    reg = M.load(M.REG)
    assert rows and rows[0]["first_line"] == 1
    assert rows[-1]["last_line"] == reg["page_line_counts"][str(page)]
    assert all(left["last_line"] + 1 == right["first_line"]
               for left, right in zip(rows, rows[1:]))
    assert all(M.B61.track_for(page, x["first_line"]) ==
               M.B61.track_for(page, x["last_line"]) == x["track_hint"] for x in rows)


@pytest.mark.parametrize("index", range(62))
def test_every_candidate_split_links_to_anchored_segment(index, audit):
    proposal = M.load(M.PROPOSALS)["proposals"][index]
    parent = proposal["parent_anchor_id"]
    p, n = int(parent[6:9]), int(parent[11:14])
    result = [x for x in audit["segments"] if x["printed_page"] == p and x["first_line"] == n]
    assert len(result) == 1 and result[0]["candidate_atom_splits"] == 2
    assert result[0]["evidence_kind"] == "ANCHOR_WINDOW"
    assert result[0]["official_clause_membership"] == "UNDETERMINED"


@pytest.mark.parametrize("index", range(28))
def test_nonatom_requirement_has_specific_source_overlap(index, audit):
    req = M.load(M.REQUIREMENTS)["records"][index]
    matched = [x for x in audit["segments"]
               if req["source_candidate_id"] in x["linked_nonatom_requirement_ids"]]
    assert matched and all(x["printed_page"] == req["printed_page"] for x in matched)
    assert all(not x["student_publishable"] for x in matched)


@pytest.mark.parametrize("track", (*M.TRACKS,"ELECTIVE_GENERAL"))
def test_tracks_are_only_candidate_evidence_not_certified_denominators(track, audit):
    item = audit["tracks"][track]
    assert item["official_atom_denominator"] is None
    assert item["confirmed_missing_atoms"] is None
    assert item["teacher_approved"] == item["student_published"] == 0


@pytest.mark.parametrize("page", [51,57,64,69,73])
def test_each_mixed_track_page_splits_without_leaking_track(page, witness):
    seq = [x for x in witness["segments"] if x["printed_page"] == page]
    assert len({x["track_hint"] for x in seq}) >= 2
    assert all(M.B61.track_for(page,x["first_line"]) ==
               M.B61.track_for(page,x["last_line"]) for x in seq)


@pytest.mark.parametrize("index", range(56))
def test_each_priority_review_risk_is_real_but_not_teacher_reviewed(index, audit):
    risk = audit["review_risks"][index]
    item = next(x for x in audit["segments"] if x["segment_id"] == risk["segment_id"])
    assert risk["lines"] == item["last_line"] - item["first_line"] + 1
    assert item["full_text_and_cross_page_teacher_review"] == "NOT_DONE"
    assert risk["reason"] in ("NOT_MARKER_ANCHORED","LONG_UNVERIFIED_WINDOW")


@pytest.mark.parametrize("page", range(13,74))
def test_fake_source_digest_is_rejected_for_every_page(page, witness):
    altered = deepcopy(witness)
    row = next(x for x in altered["segments"] if x["printed_page"] == page)
    row["span_sha256"] = "0"*64 if row["span_sha256"]!="0"*64 else "f"*64
    with pytest.raises(ValueError,match="source witness pin mismatch"):
        M.validate_witness(altered)


@pytest.mark.parametrize("index", range(20))
def test_fake_approval_and_student_publication_rejected(index, witness):
    for attr,value in (("teacher_approved",True),("student_publishable",True),
                       ("officially_certified_atom",True)):
        w = deepcopy(witness)
        w["segments"][index][attr] = value
        with pytest.raises(ValueError, match="source witness pin mismatch"):
            M.validate_witness(w)


@pytest.mark.parametrize("field,value", [
    ("full_page_teacher_reviews",1),
    ("student_published",1),
    ("teacher_approved",1),
    ("includes_copyright_text",True),
    ("scope","OFFICIAL_ATOM_DENOMINATOR"),
])
def test_top_level_forgery_rejected(field,value,witness):
    altered = deepcopy(witness)
    altered[field] = value
    with pytest.raises(ValueError):
        M.validate_witness(altered)


def test_misleading_elective_e_zero_is_rejected_as_completion(audit):
    assert audit["tracks"]["ELECTIVE_E"]["heuristic_anchor_count"] == 0
    assert audit["tracks"]["ELECTIVE_E"]["pdfkit_lines_accounted_for"] > 0
    assert audit["tracks"]["ELECTIVE_E"]["official_atom_denominator"] is None
    assert audit["tracks"]["ELECTIVE_GENERAL"]["pdfkit_lines_accounted_for"] > 0


def test_candidate_linkage_rejects_orphan_and_false_approval(monkeypatch):
    proposals = M.load(M.PROPOSALS)
    original = M.load
    for attr, val in (("parent_anchor_id","KB61-P999-L999"),
                      ("student_publishable",True),
                      ("official_atomic_membership","CERTIFIED")):
        mutated = deepcopy(proposals)
        mutated["proposals"][0][attr] = val
        monkeypatch.setattr(M, "load", lambda path, m=mutated: m if path == M.PROPOSALS else original(path))
        with pytest.raises(ValueError,match="unapproved atom or orphan"):
            M.build()
    monkeypatch.setattr(M, "load", original)


def test_nonatom_linkage_rejects_false_completion(monkeypatch):
    req = M.load(M.REQUIREMENTS)
    req["records"][0]["coverage_status"] = "CERTIFIED"
    original = M.load
    monkeypatch.setattr(M, "load", lambda path: req if path == M.REQUIREMENTS else original(path))
    with pytest.raises(ValueError,match="nonatom requirement scope"):
        M.build()


def test_underlying_partition_is_rechecked_even_if_attacker_repins_hash(witness,monkeypatch):
    altered = deepcopy(witness)
    altered["segments"][3]["first_line"] += 1
    altered["segments"][3]["line_count"] -= 1
    monkeypatch.setattr(M,"WITNESS_ROWS_SHA",M.rows_digest(altered["segments"]))
    with pytest.raises(ValueError,match="segment coordinate invalid|source partition gap"):
        M.validate_witness(altered)


def test_pinned_source_lineage_requires_all_428_original_anchors(witness,monkeypatch):
    altered = deepcopy(witness)
    altered["segments"][0]["section_kind"] = "ANCHOR_WINDOW"
    monkeypatch.setattr(M,"WITNESS_ROWS_SHA",M.rows_digest(altered["segments"]))
    with pytest.raises(ValueError,match="fabricated numbered clause|broken original anchor"):
        M.validate_witness(altered)
