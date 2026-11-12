"""Batch117 regression: no false syllabus denominator, no approval, exact finite cases.

This suite does NOT certify theorems or free-form student solutions.
"""
from __future__ import annotations
import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest
import sympy as sp
from pydantic import ValidationError

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch117 as b
from kb_batch117_lessons import UNITS
from app.deep_knowledge import DeepLesson,lessons

SOURCE=json.loads(b.SOURCE.read_text())
CLAUSES=json.loads(b.CLAUSES.read_text())
DOCS=json.loads(b.PACK.read_text())
COVER=json.loads(b.COVER.read_text())

@pytest.mark.parametrize("row",SOURCE["pages"],ids=lambda v:f"page-{v['printed_page']}")
def test_61_page_source_fingerprint_locked(row):
    original=json.loads(b.MANIFEST.read_text())["pages"][row["pdf_page_index"]]
    assert row["page_text_sha256"]==original["pdfkit_utf8_sha256"]
    assert row["pdf_page_index"]==row["printed_page"]+7
    assert row["source_pdf_sha256"]==b.PDF_SHA
    assert row["nonempty_pdfkit_line_count"]>0
    assert row["official_atomic_denominator"] is None
    assert row["teacher_approved"] is False
    assert row["student_authoritative"] is False

@pytest.mark.parametrize("row",SOURCE["pages"],ids=lambda v:f"page-{v['printed_page']}")
def test_page_status_does_not_fake_review(row):
    if row["printed_page"] in SOURCE["review_pending_page_numbers"]:
        assert row["batch117_status"]=="PAGE_INDEXED_PENDING_HUMAN_REVIEW"
        assert row["prior_structure_review_status"]=="NOT_REVIEWED"
    else:
        assert row["batch117_status"]=="PRIOR_STRUCTURE_REVIEW_RETAINED"

@pytest.mark.parametrize("track",b.TRACKS)
def test_unknown_denominators_and_approval(track):
    assert SOURCE["seven_track_official_atom_denominators"][track] is None
    assert COVER["seven_track_denominators"][track] is None
    assert COVER["teacher_approvals"]==0
    assert COVER["student_authoritative_releases"]==0

@pytest.mark.parametrize("row",CLAUSES["items"],ids=lambda v:v["editorial_candidate_id"])
def test_source_anchor_and_track(row):
    page=SOURCE["pages"][row["printed_page"]-13]
    assert row["page_sha256"]==page["page_text_sha256"]
    assert 1<=row["line_range"][0]<=row["line_range"][1]<=page["nonempty_pdfkit_line_count"]
    assert row["track_hint"]=="SELECTIVE_COMPULSORY"
    assert row["official_atom_id"] is None
    assert row["teacher_approved"] is False

@pytest.mark.parametrize("doc",DOCS,ids=lambda v:v["id"])
def test_deep_lesson_educational_contract(doc):
    obj=DeepLesson.model_validate(doc)
    assert obj.review.status=="REVIEW_PENDING"
    assert obj.teacher_solution_visibility=="TEACHER_ONLY"
    assert obj.review.reviewer_id is None
    assert len(obj.assumptions)>=2
    assert len(obj.counterexamples)==1
    assert len(obj.misconceptions)==1
    assert len(obj.hint_ladder)==3
    assert len(obj.worked_examples)==2
    assert obj.transfer.near and obj.transfer.far
    assert obj.provenance.permission=="PROJECT_AUTHORED"
    assert len(obj.proof_steps)==3 if obj.kind=="theorem" else len(obj.proof_steps)==0

@pytest.mark.parametrize("doc",DOCS,ids=lambda v:v["id"])
def test_no_teacher_answer_in_hints(doc):
    hints=" ".join(doc["hint_ladder"])
    answers={ex["answer"] for ex in doc["worked_examples"]}
    assert all(a not in hints for a in answers)
    assert not any(t in hints for t in ("教师答案：","最终答案为","直接抄写"))

@pytest.mark.parametrize("doc",DOCS,ids=lambda v:v["id"])
def test_student_authority_is_not_structural_completeness(doc):
    forged=deepcopy(doc)
    forged["review"]["status"]="APPROVED"
    forged["review"]["reviewer_id"]="fake-teacher"
    forged["review"]["reviewed_at"]="2026-11-13"
    forged["review"]["review_record"]="editor-created"
    with pytest.raises(ValidationError):
        DeepLesson.model_validate(forged)

@pytest.mark.parametrize("doc",DOCS,ids=lambda v:v["id"])
def test_missing_teacher_approval_record_rejected(doc):
    forged=deepcopy(doc)
    forged["review"]["status"]="APPROVED"
    with pytest.raises(ValidationError):
        DeepLesson.model_validate(forged)

@pytest.mark.parametrize("key",list(b.PAGES))
def test_exact_positive_and_counterexample_both_required(key):
    rows={z["key"]:z for z in b.exact_witnesses()["cases"]}
    assert rows[key]["positive_exact"] is True
    assert rows[key]["negative_exact"] is True
    assert rows[key]["universal_proof_certified"] is False
    assert rows[key]["student_free_text_verified"] is False

@pytest.mark.parametrize("u",UNITS,ids=lambda v:v["key"])
def test_authored_source_and_examples_are_distinct(u):
    assert u["key"] in b.PAGES
    assert len(u["examples"])==2
    assert u["examples"][0]["question"]!=u["examples"][1]["question"]
    assert u["near"]!=u["far"]
    assert len(u["reasoning"])==3
    assert u["counterexample"]!=u["statement"]

@pytest.mark.parametrize("doc",DOCS,ids=lambda v:v["id"])
def test_prerequisite_graph_acyclic_and_resolvable(doc):
    current=int(doc["id"].rsplit(".",1)[1])
    ids={d["id"] for d in DOCS}
    assert len(doc["prerequisite_lesson_ids"])==len(set(doc["prerequisite_lesson_ids"]))
    assert all(p in ids and int(p.rsplit(".",1)[1])<current
               for p in doc["prerequisite_lesson_ids"])

def test_source_p35_refuses_text_only_certification():
    row=SOURCE["pages"][35-13]
    assert row["manual_visual_risk"]=="PDFKIT_CONTROL_TEXT_MANUAL_IMAGE_REQUIRED"
    assert row["official_atomic_denominator"] is None
    assert row["batch117_status"]=="PAGE_INDEXED_PENDING_HUMAN_REVIEW"

def test_source_cross_track_boundary_has_no_automatic_classification():
    for page in (51,69,73):
        p=SOURCE["pages"][page-13]
        assert p["editorial_track_hint"]=="MULTI_TRACK_TRANSITION"
        assert p["manual_visual_risk"]
        assert p["official_atomic_denominator"] is None

def test_no_fake_all_pages_certified():
    assert SOURCE["page_count"]==61
    assert SOURCE["retained_prior_structure_review_count"]==18
    assert SOURCE["new_page_line_indices_without_human_structure_review"]==43
    assert len(SOURCE["review_pending_page_numbers"])==43
    assert SOURCE["complete_teacher_atomization_pages"]==0
    assert SOURCE["physical_pages_sha_locked"]==188
    assert not SOURCE["copyright_source_text_embedded"]

def test_machine_verified_bookkeeping_not_formal_proof():
    assert COVER["new_deep_drafts"]==8
    assert COVER["prior_deep_drafts"]==490
    assert COVER["total_deep_drafts"]==498
    assert COVER["new_teacher_examples"]==16
    assert COVER["new_hint_levels"]==24
    assert COVER["new_transfer_prompts"]==16
    assert b.exact_witnesses()["proof_certificates"]==0

def test_critical_finite_counterexamples_independent():
    R=sp.Rational
    x=sp.symbols("x")
    assert sp.expand((x+2)**3-(x**3+6*x**2+12*x+8))==0
    assert sp.binomial(5,2)==10
    assert sp.binomial(5,2)!=5*4
    assert R(2,6)/R(3,6)==R(2,3)
    assert sp.binomial(1,2)==0
    assert sp.binomial(2,2)==1
    assert sp.binomial(1,2)/sp.binomial(2,2)!=R(1,4)
    assert sum(sp.binomial(2,k)*sp.binomial(3,2-k) for k in range(3))==sp.binomial(5,2)

def test_build_check_no_drift():
    output=b.generate()
    for f,object_value in output.items():
        expected=object_value if isinstance(object_value,str) else b.dump(object_value)
        assert f.read_text()==expected

def test_student_layer_public_data_does_not_contain_teacher_solution():
    from app.deep_knowledge import public_summary,unpublished_teacher_preview
    text=json.dumps(public_summary(),ensure_ascii=False)
    assert "teacher_solution" not in text
    assert "batch117_selective_counting" not in text
    assert all(d["teacher_solution_visibility"]=="TEACHER_ONLY" for d in DOCS)
    # Unpublished teacher previews are explicitly separate, never treated as student evidence.
    assert len(unpublished_teacher_preview("组合数"))>=0


def test_prior_batch115_snapshot_is_immutable_across_future_pack():
    import build_kb_batch115 as baseline
    _, audit = baseline.lessons()
    assert audit["prior_deep_drafts"] == 482
    assert audit["total_deep_drafts"] == 490
    recorded = json.loads((ROOT / "docs/evaluation/KB_BATCH115_AUDIT.json").read_text())
    assert recorded["prior_deep_drafts"] == 482
    assert recorded["total_deep_drafts"] == 490


def test_future_batch_pack_cannot_retroactively_inflate_batch117_denominator():
    # Regression: historical Batch115 drift had failed a complete Mac suite.
    assert b.is_frozen_prior_pack(ROOT/"knowledge/deep/v1/batch116_dummy.json")
    assert b.is_frozen_prior_pack(ROOT/"knowledge/deep/v1/custom_historical_pack.json")
    assert not b.is_frozen_prior_pack(ROOT/"knowledge/deep/v1/batch117_selective_counting.json")
    assert not b.is_frozen_prior_pack(ROOT/"knowledge/deep/v1/batch118_future.json")
    assert not b.is_frozen_prior_pack(ROOT/"knowledge/deep/v1/batch120_future.json")
