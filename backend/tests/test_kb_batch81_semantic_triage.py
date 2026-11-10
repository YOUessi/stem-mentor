"""Batch81: source-specific 42/428 editorial proposals, not approved math atoms."""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch81_semantic_triage as SEM

@pytest.fixture(scope="module")
def result():
    return SEM.build()


def test_42_selected_real_anchor_proposals_not_official_coverage(result):
    assert result["selected_independently_paraphrased_anchors"] == 42
    assert result["source_review_anchor_count"] == 428
    assert result["remaining_without_manual_semantic_paraphrase"] == 386
    assert result["official_curriculum_atom_denominator"] is None
    assert result["teacher_full_page_atomizations"] == 0
    assert result["teacher_approved"] == result["student_published"] == 0
    assert result["by_track"] == dict(zip(
        ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A", "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E"),
        (7, 7, 7, 7, 7, 7, 0)))
    assert sum(result["by_provisional_role"].values()) == 42
    assert sum(r["semantic_role_provisional"] == "CURRICULUM_HEADING" for r in result["rows"]) == 11
    assert SEM.OUT.read_text(encoding="utf8") == SEM.dump(result)
    assert SEM.MD.read_text(encoding="utf8") == SEM.markdown(result)


@pytest.mark.parametrize("idx", range(42))
def test_row_preserves_frozen_real_source_and_draft_status(idx, result):
    item = result["rows"][idx]
    raw = json.loads(SEM.SOURCE.read_text(encoding="utf8"))
    origin = next(r for r in raw["anchor_review_queue"] if r["review_id"] == item["review_id"])
    for key in ("track", "printed_page", "pdfkit_line", "source_line_sha256", "source_page_pdfkit_sha256"):
        assert item[key] == origin[key]
    assert item["source_parent_segment"] == origin["parent_segment"]
    assert item["teacher_review"] == "REVIEW_PENDING"
    assert item["official_atom_count"] is None
    assert item["teacher_approved"] is item["student_publishable"] is False
    assert item["equivalence_review"] == "PENDING_INDEPENDENT_MATH_AND_SOURCE_REVIEW"


@pytest.mark.parametrize("idx", range(42))
@pytest.mark.parametrize("field,value", (
    ("teacher_confirmed", True), ("student_publishable", True),
    ("official_atom_count", 0), ("official_atom_count", 1),
    ("cross_track_equivalence", "MATHEMATICALLY_EQUIVALENT"),
    ("original_editorial_paraphrase", "too short")))
def test_proposals_cannot_forge_teacher_or_official_completion(idx, field, value):
    data = json.loads(SEM.AUTHOR.read_text(encoding="utf8"))
    data["records"][idx][field] = value
    with pytest.raises((ValueError, KeyError)):
        SEM.build(auth=data)


@pytest.mark.parametrize("idx", range(42))
def test_anchor_track_tamper_rejected(idx):
    data = json.loads(SEM.AUTHOR.read_text(encoding="utf8"))
    current = data["records"][idx]["track"]
    data["records"][idx]["track"] = "ELECTIVE_C" if current != "ELECTIVE_C" else "COMPULSORY"
    with pytest.raises(ValueError, match="Cross-track"):
        SEM.build(auth=data)


def test_application_heading_without_atom_is_valid_not_counted():
    result = SEM.build()
    row = next(x for x in result["rows"] if x["review_id"] == "KB80-A066-L007")
    assert row["semantic_role_provisional"] == "APPLICATION_CONTEXT"
    assert row["possible_math_units_for_teacher_split"] == []
    assert row["official_atom_count"] is None


def test_math_requirement_cannot_silently_erase_candidate():
    data = json.loads(SEM.AUTHOR.read_text(encoding="utf8"))
    row = next(x for x in data["records"] if x["semantic_role_provisional"] == "MATHEMATICAL_REQUIREMENT")
    row["possible_math_units_for_teacher_split"] = []
    with pytest.raises(ValueError, match="Mathematical clauses"):
        SEM.build(auth=data)


def test_heading_cannot_invent_math_atom():
    data = json.loads(SEM.AUTHOR.read_text(encoding="utf8"))
    row = next(x for x in data["records"] if x["semantic_role_provisional"] == "CURRICULUM_HEADING")
    row["possible_math_units_for_teacher_split"] = ["synthetic fake atom"]
    with pytest.raises(ValueError, match="Headings"):
        SEM.build(auth=data)


def test_source_line_sha_mutation_rejected_even_with_valid_pdf_sha():
    source = json.loads(SEM.SOURCE.read_text(encoding="utf8"))
    source["anchor_review_queue"][0]["source_line_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="Frozen 428-anchor"):
        SEM.build(upstream=source)


def test_source_row_line_mutation_rejected_even_with_valid_pdf_sha():
    source = json.loads(SEM.SOURCE.read_text(encoding="utf8"))
    source["anchor_review_queue"][0]["pdfkit_line"] += 1
    with pytest.raises(ValueError, match="Frozen 428-anchor"):
        SEM.build(upstream=source)


def test_duplicate_anchor_cannot_be_counted_twice():
    data = json.loads(SEM.AUTHOR.read_text(encoding="utf8"))
    data["records"][1]["review_id"] = data["records"][0]["review_id"]
    with pytest.raises(ValueError, match="unique"):
        SEM.build(auth=data)


def test_cross_track_topic_similarity_not_formally_equivalent(result):
    assert len(result["cross_track_links"]) == 3
    assert all(x["mathematical_equivalence_certified"] is False for x in result["cross_track_links"])
    assert len({(x["left"], x["right"]) for x in result["cross_track_links"]}) == 3
