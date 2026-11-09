"""Batch58 independent competency coverage: source, crosswalk, review and mutation gates."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch58_competency_coverage as C

AUDIT = C.build()
ROWS = AUDIT["rows"]


def test_independent_audit_counts_and_unmapped_denominators():
    assert AUDIT["source_span_count_inherited_not_unique_atoms"] == 130
    assert AUDIT["review_queue_items"] == 28
    assert AUDIT["counts_by_kind"] == {
        "ACHIEVEMENT_REQUIREMENT": 11, "ACTIVITY_REQUIREMENT": 3,
        "TEACHING_GUIDANCE": 14,
    }
    assert AUDIT["assessment_verified"] == AUDIT["teacher_approved"] == 0
    assert AUDIT["assessment_unmapped"] == len(ROWS) == 28
    assert AUDIT["student_published"] == 0
    assert set(AUDIT["official_atomic_denominator"]) == set(C.TRACKS)
    assert all(v is None for v in AUDIT["official_atomic_denominator"].values())
    assert AUDIT["not_included_as_knowledge_atoms"] is True


@pytest.mark.parametrize("idx", range(28))
def test_each_competency_has_source_and_open_assessment_gap(idx):
    row = ROWS[idx]
    assert row["source_candidate_id"].startswith(("KB56-C", "KB57-C"))
    assert row["source_kind"] in C.CATEGORIES
    assert row["source_span_pdfkit_sha256"]
    assert row["pdf_sha256"] == C.SOURCE_SHA
    assert row["assessment_artifact_ids"] == []
    assert row["rubric_evidence_ids"] == []
    assert row["student_activity_ids"] == []
    assert row["mathematical_equivalence"] == "NOT_CERTIFIED"
    assert row["assessment_coverage"] == "UNMAPPED"
    assert row["review"] == "REVIEW_PENDING"
    assert row["teacher_approved"] is row["student_publishable"] is row["official_atom"] is False


@pytest.mark.parametrize("idx", range(52))
def test_batch56_source_inventory_and_state(idx):
    source = C.read(C.SOURCE_PATHS[0])
    row = source["rows"][idx]
    assert row["source_pdf_sha256"] == C.SOURCE_SHA
    assert row["teacher_review"] == "REVIEW_PENDING"
    assert row["student_publishable"] is False
    assert row["official_atom_certified"] is False


@pytest.mark.parametrize("idx", range(78))
def test_batch57_source_inventory_and_state(idx):
    source = C.read(C.SOURCE_PATHS[1])
    row = source["rows"][idx]
    assert row["source_pdf_sha256"] == C.SOURCE_SHA
    assert row["teacher_review"] == "REVIEW_PENDING"
    assert row["student_publishable"] is False
    assert row["official_atom_certified"] is False


@pytest.mark.parametrize("mutation,part", [
    ("page", 56), ("pdf", 56), ("hash", 56), ("review", 56),
    ("approved", 56), ("student", 56), ("official", 56),
    ("page", 57), ("pdf", 57), ("hash", 57), ("review", 57),
    ("approved", 57), ("student", 57), ("official", 57),
    ("fake-denominator", 56), ("fake-denominator", 57),
    ("id", 56), ("id", 57),
])
def test_source_drift_and_fake_approval_fail_closed(mutation, part):
    a = C.read(C.SOURCE_PATHS[0])
    b = C.read(C.SOURCE_PATHS[1])
    source = a if part == 56 else b
    row = source["rows"][0]
    if mutation == "page":
        row["pdf_page_index"] += 1
    elif mutation == "pdf":
        row["source_pdf_sha256"] = "0" * 64
    elif mutation == "hash":
        row["source_span_pdfkit_sha256"] = "00" * 32
        row["source_span_pdfkit_sha256"] = "bad"
    elif mutation == "review":
        row["teacher_review"] = "APPROVED"
    elif mutation == "approved":
        source["teacher_approved"] = 1
    elif mutation == "student":
        row["student_publishable"] = True
    elif mutation == "official":
        row["official_atom_certified"] = True
    elif mutation == "fake-denominator":
        source["official_atomic_denominator"]["COMPULSORY"] = 100
    elif mutation == "id":
        row["candidate_id"] = "forged"
    with pytest.raises(ValueError):
        C.build(source56=a, source57=b)


@pytest.mark.parametrize("batch", (56, 57))
def test_duplicate_competency_and_forged_equivalence_rejected(batch):
    a = C.read(C.SOURCE_PATHS[0])
    b = C.read(C.SOURCE_PATHS[1])
    src = a if batch == 56 else b
    first, second = src["rows"][0:2]
    second["candidate_id"] = first["candidate_id"]
    with pytest.raises(ValueError, match="duplicate / forged"):
        C.build(source56=a, source57=b)
    src["rows"][1]["candidate_id"] = ("KB56" if batch == 56 else "KB57") + "-C-P999-S999"
    item = next(r for r in src["rows"] if r["source_kind"] in C.CATEGORIES)
    k = "related_lesson_math_equivalence_certified" if batch == 56 else "mathematical_scope_equivalence_certified"
    item[k] = True
    with pytest.raises(ValueError, match="thematic match"):
        C.build(source56=a, source57=b)


def test_reproducibility_and_reports_do_not_claim_teaching_release():
    assert C.OUT_JSON.read_text(encoding="utf8") == json.dumps(
        AUDIT, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    md = C.OUT_MD.read_text(encoding="utf8")
    assert md == C.render(AUDIT)
    assert "未证等价" in md and "分母仍为null" in md
    assert "无独立题族/量规/活动验收证据" in md
    assert "APPROVED" not in md
