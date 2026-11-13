"""Batch120 source-locked seven-track editorial candidates, negative review gates and exact witnesses."""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
import pytest
import sympy as S

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "backend")]
import build_kb_batch120_semantic_expansion as b
import build_kb_batch120_math_oracles as oracle
import build_kb_batch119_semantic_pilot as previous
from kb_batch120_semantic_catalog import ROWS, FROZEN_SOURCE_SHA256
from app.deep_knowledge import public_summary

DATA = json.loads(b.OUT.read_text(encoding="utf-8"))
COVER = json.loads(b.COVER.read_text(encoding="utf-8"))
MATH = json.loads(oracle.OUT.read_text(encoding="utf-8"))
PREVIOUS = json.loads(previous.OUT.read_text(encoding="utf-8"))

@pytest.mark.parametrize("row", DATA["candidates"], ids=lambda r:r["local_key"])
def test_editorial_candidate_is_source_locked_not_teacher_authority(row):
    key = row["local_key"]
    assert row["source"]["source_span_sha256"] == FROZEN_SOURCE_SHA256[key]
    assert row["review_status"] == "REVIEW_PENDING"
    assert row["teacher_evidence"] is None and row["official_atom_id"] is None
    assert row["official_atom_certified"] is False
    assert row["proof_verification"] == "UNVERIFIED"
    assert row["teacher_solution_visibility"] == "TEACHER_ONLY"
    assert row["student_authoritative"] is False
    assert row["elective_e_optional_example"] == (row["course_track"] == "ELECTIVE_E")
    assert row["source"]["original_pdf_sha256"] == b.evidence.PDF_SHA
    assert row["source"]["physical_page_index"] == row["source"]["printed_page"]+7
    assert len(row["applicability"]) >= 12 and len(row["invalid_use"]) >= 13
    assert key in {raw[0] for raw in ROWS}

@pytest.mark.parametrize("track", b.TRACKS)
def test_per_track_denominator_never_inferred_from_cues_or_candidates(track):
    candidate_count = sum(r["course_track"] == track for r in DATA["candidates"])
    prior_count = sum(r["course_track"] == track for r in PREVIOUS["candidates"])
    t = COVER["per_track"][track]
    assert t["new"] == candidate_count
    assert t["previous"] == prior_count
    assert t["cumulative_editorial_candidates"] == candidate_count + prior_count
    assert t["official_atom_denominator"] is None and t["whole_track_complete"] is False
    assert t["teacher_approved"] == 0
    assert COVER["official_atom_denominator"][track] is None

@pytest.mark.parametrize("case", MATH["cases"], ids=lambda c:c["candidate"])
def test_independently_recomputed_exact_math_witnesses_not_proofs(case):
    live = oracle.build()
    actual = next(item for item in live["cases"] if item["candidate"] == case["candidate"])
    assert actual == case
    assert case["exact_positive_passed"] is True
    assert case["exact_negative_passed"] is True
    assert case["general_proof_certified"] is False
    assert MATH["formal_general_proofs_certified"] == 0
    assert MATH["student_free_text_verified"] is False

ATTACKS = [
    lambda d: d.update(official_atom_census_complete=True),
    lambda d: d.update(official_atom_total_denominator=113),
    lambda d: d.update(source_text_committed=True),
    lambda d: d.update(teacher_approved_count=1),
    lambda d: d.update(student_authoritative_count=1),
    lambda d: d.update(source_cues_linked_cumulative=405),
    lambda d: d.update(source_cues_not_linked_cumulative=0),
    lambda d: d.update(new_candidate_count=65),
    lambda d: d.update(cumulative_editorial_candidate_count=405),
    lambda d: d["by_track"]["COMPULSORY"].update(official_atom_denominator=21),
    lambda d: d["by_track"]["ELECTIVE_E"].update(whole_track_complete=True),
    lambda d: d["candidates"][0].update(review_status="APPROVED"),
    lambda d: d["candidates"][0].update(teacher_evidence={"reviewer":"fake"}),
    lambda d: d["candidates"][0].update(student_authoritative=True),
    lambda d: d["candidates"][0].update(official_atom_id="invented-official-id"),
    lambda d: d["candidates"][0].update(official_atom_certified=True),
    lambda d: d["candidates"][0].update(proof_verification="CERTIFIED"),
    lambda d: d["candidates"][0].update(teacher_solution_visibility="STUDENT"),
    lambda d: d["candidates"][0].update(course_track="ELECTIVE_A"),
    lambda d: d["candidates"][0].update(kind="theorem"),
    lambda d: d["candidates"][0].update(proposed_objective="伪造的目标"),
    lambda d: d["candidates"][0].update(applicability="被删除"),
    lambda d: d["candidates"][0].update(invalid_use="被删除"),
    lambda d: d["candidates"][0].update(local_key="C999"),
    lambda d: d["candidates"][0].update(prerequisite_candidate_ids=["fake"]),
    lambda d: d["candidates"][0]["source"].update(printed_page=73),
    lambda d: d["candidates"][0]["source"].update(start_line=2),
    lambda d: d["candidates"][0]["source"].update(frozen_page_sha256="1"*64),
    lambda d: d["candidates"][0]["source"].update(source_span_sha256="1"*64),
    lambda d: d["candidates"][0]["source"].update(matching_layout_cues=[]),
    lambda d: d["candidates"][0]["source"].update(visual_formula_recheck="REQUIRED"),
    lambda d: d["candidates"][0].update(elective_e_optional_example=True),
    lambda d: d["candidates"].append(copy.deepcopy(d["candidates"][0])),
]
@pytest.mark.parametrize("attack", ATTACKS, ids=[f"malicious-edit-{i:02d}" for i in range(len(ATTACKS))])
def test_forged_semantic_scope_certification_and_references_are_rejected(attack):
    clone = copy.deepcopy(DATA)
    attack(clone)
    with pytest.raises(ValueError):
        b.validate(clone)

@pytest.mark.parametrize("a,q,n,want", [
    (S.Integer(2),S.Integer(0),1,S.Integer(2)),
    (S.Integer(2),S.Integer(0),5,S.Integer(2)),
    (S.Integer(3),S.Integer(1),5,S.Integer(15)),
    (S.Integer(4),S.Rational(1,2),4,S.Rational(15,2)),
    (S.Integer(0),S.Integer(0),3,S.Integer(0)),
])
def test_geometric_power_sum_convention_does_not_certify_q_zero_ratio(a,q,n,want):
    finite_sum = a * sum(q**k for k in range(n))
    assert S.simplify(finite_sum-want) == 0
    adjudication = json.loads(b.ADJUDICATION.read_text(encoding="utf-8"))
    assert adjudication["status"] == "REVIEW_PENDING"
    assert adjudication["general_proof_machine_certified"] is False
    assert adjudication["student_authoritative"] is False
    if q == 0 and n >= 3:
        assert a*q**2 == 0
        assert a*q**2 == 0 and a*q**3 == 0  # later adjacent ratio = 0/0, not a valid nonzero ratio

def test_build_reproducibility_count_correctness_and_student_retrieval_isolation():
    assert DATA == b.build(use_local=False)
    assert b.validate(DATA)
    assert MATH == oracle.build()
    assert COVER["source_layout_cues"] == 405
    assert COVER["source_cues_linked_cumulative"] == 144
    assert COVER["source_cues_unlinked"] == 261
    assert COVER["previous_editorial_candidates"] == 49
    assert COVER["new_editorial_candidates"] == 64
    assert COVER["cumulative_editorial_candidates"] == 113
    assert COVER["all_official_atom_denominators_known"] is False
    assert COVER["teacher_approved"] == COVER["student_authoritative_releases"] == 0
    assert b.REPORT.read_text(encoding="utf-8") == b.render(DATA)
    assert MATH["exact_witness_pairs"] == 32 and MATH["exact_cases_passed"] == 64
    assert len(FROZEN_SOURCE_SHA256) == len(ROWS) == 64
    student_index = json.dumps(public_summary(), ensure_ascii=False)
    assert "hs-semantic-pilot-120" not in student_index
    assert "k00_batch120_semantic_expansion" not in student_index
