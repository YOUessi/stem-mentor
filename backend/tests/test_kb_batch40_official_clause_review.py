"""Negative and positive Batch40 source-scope / bounded-math regressions."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import sys
import pytest
from app.kb_batch40_exact_scope import FIELDS, VALID, INVALID, witness

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch40_official_clauses as audit40

SOURCE = audit40.load(audit40.SOURCE)
OLD = audit40.load(audit40.OLD)
PINS = audit40.load(audit40.FINGERPRINTS)
REPORT = audit40.audit()
ROWS = REPORT["rows"]

@pytest.mark.parametrize("row", ROWS, ids=lambda r: r["editorial_candidate_id"])
def test_all_twelve_editorial_candidates_have_real_original_page_and_legacy_provenance(row):
    x = next(r for r in OLD["links"] if r["editorial_candidate_id"] == row["editorial_candidate_id"])
    assert x["review_finding"] == "CLAUSE_UNVERIFIED"
    assert row["legacy_lesson_id"] == x["legacy_lesson_id"]
    assert row["legacy_lesson_content_sha256"] == x["legacy_lesson_content_sha256"]
    assert row["track"] == x["candidate_track"]
    assert row["printed_page"] == x["source_printed_page"]
    assert row["pdf_page_index_zero_based"] == row["printed_page"] + 7
    assert row["source_scope_class"] == audit40.CLASS[row["editorial_candidate_id"]]
    assert row["pdfkit_page_text_sha256"] in {
        p["pdfkit_page_text_sha256"] for p in PINS["page_fingerprints"]
    }
    assert row["source_short_probe_sha256"] == hashlib.sha256(
        row["short_source_probe_chinese"].encode()).hexdigest()

@pytest.mark.parametrize("row", ROWS, ids=lambda r: r["editorial_candidate_id"])
def test_no_source_alignment_or_legacy_link_can_auto_approve_a_math_lesson(row):
    assert row["teacher_review"] == "REVIEW_PENDING"
    assert row["official_atomic_equivalence_certified"] is False
    assert row["legacy_lesson_certified"] is False
    assert row["student_publishable"] is False
    assert row["teacher_solution"] is None
    assert row["review_action"] and row["mathematical_scope_note"]

@pytest.mark.parametrize("row", ROWS, ids=lambda r: r["editorial_candidate_id"])
def test_each_row_rejects_false_teacher_and_official_certification(row):
    for name, val in [
        ("teacher_review", "APPROVED"),
        ("official_atomic_equivalence_certified", True),
        ("legacy_lesson_certified", True),
        ("student_publishable", True),
    ]:
        other = copy.deepcopy(SOURCE)
        target = next(x for x in other["entries"] if x["editorial_candidate_id"] == row["editorial_candidate_id"])
        target[name] = val
        with pytest.raises(ValueError):
            audit40.audit(source=other)

@pytest.mark.parametrize("row", ROWS, ids=lambda r: r["editorial_candidate_id"])
def test_tampering_topic_scope_classification_is_rejected(row):
    other = copy.deepcopy(SOURCE)
    target = next(x for x in other["entries"] if x["editorial_candidate_id"] == row["editorial_candidate_id"])
    target["source_scope_class"] = "OFFICIALLY_CERTIFIED"
    with pytest.raises(ValueError):
        audit40.audit(source=other)

@pytest.mark.parametrize("field", [
    "short_source_probe_chinese", "section_anchor", "mathematical_scope_note",
    "review_action", "track", "printed_page"
])
def test_missing_evidence_or_wrong_track_page_rejected(field):
    other = copy.deepcopy(SOURCE)
    other["entries"][0][field] = 0 if field == "printed_page" else "x"
    with pytest.raises((ValueError, TypeError)):
        audit40.audit(source=other)

@pytest.mark.parametrize("case", ["duplicate", "missing", "extra", "false_pdf_sha", "altered_offset"])
def test_source_scope_frozen_12_and_pdf_sha_guard(case):
    other = copy.deepcopy(SOURCE)
    if case == "duplicate":
        other["entries"][-1] = other["entries"][0]
    elif case == "missing":
        other["entries"].pop()
    elif case == "extra":
        other["entries"].append(other["entries"][0])
    elif case == "false_pdf_sha":
        other["source"]["sha256"] = "1"*64
    else:
        other["source"]["printed_to_pdf_index_offset"] = 0
    with pytest.raises(ValueError):
        audit40.audit(source=other)

@pytest.mark.parametrize("case", ["missing_page", "changed_index", "teacher_forgery", "bad_pdf_sha", "pdf_committed"])
def test_source_page_fingerprint_guard(case):
    pins = copy.deepcopy(PINS)
    if case == "missing_page":
        pins["page_fingerprints"].pop()
    elif case == "changed_index":
        pins["page_fingerprints"][0]["pdf_page_index"] += 1
    elif case == "teacher_forgery":
        pins["page_fingerprints"][0]["teacher_verified"] = True
    elif case == "bad_pdf_sha":
        pins["pdf_sha256"] = "x"*64
    else:
        pins["pdf_committed"] = True
    with pytest.raises(ValueError):
        audit40.audit(fingerprints=pins)

def test_generated_audit_and_md_are_reproducible_and_no_false_denominator():
    assert audit40.OUT.read_text(encoding="utf-8") == json.dumps(
        REPORT, ensure_ascii=False, indent=2) + "\n"
    assert audit40.MARKDOWN.read_text(encoding="utf-8") == audit40.markdown(REPORT)
    assert len(ROWS) == 12 and len(PINS["page_fingerprints"]) == 9
    assert REPORT["summary"]["class_count"] == {
        "CONTEXTUAL_APPLICATION": 1, "DIRECT_SCOPE": 6,
        "LOCAL_ELECTIVE_OPTION": 1, "PARTIAL_DERIVATION": 1,
        "TOPIC_ONLY_NOT_EXPLICIT": 3
    }
    assert set(REPORT["summary"]["official_atomic_denominator"]) == set(audit40.TRACKS)
    assert all(x is None for x in REPORT["summary"]["official_atomic_denominator"].values())
    assert REPORT["summary"]["teacher_approved"] == 0
    assert REPORT["summary"]["student_published"] == 0
    assert REPORT["student_retrieval"] == {"documents": [], "teacher_solutions": []}

@pytest.mark.parametrize("op", sorted(FIELDS))
def test_exact_guard_valid_and_invalid_conditions(op):
    good = witness(op, VALID[op])
    assert good["status"] == "FINITE_EXACT_CASE_ONLY" and good["value"]
    assert all(good[x] is False for x in
        ("proof_certified", "teacher_approved", "student_step_verified", "student_publishable"))
    assert witness(op, INVALID[op])["status"] == "CONDITIONS_NOT_ESTABLISHED"
    assert witness(op+"___LLM_APPROVED", VALID[op])["status"] == "UNSUPPORTED"

@pytest.mark.parametrize("op", sorted(FIELDS))
def test_all_math_inputs_reject_undeclared_or_missing_fields(op):
    v = VALID[op]
    assert witness(op, {})["status"] == "CONDITIONS_NOT_ESTABLISHED"
    assert witness(op, dict(v, llm_certified=True))["status"] == "CONDITIONS_NOT_ESTABLISHED"
    o = dict(v)
    o.pop(next(iter(o)))
    assert witness(op, o)["status"] == "CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("op", sorted(FIELDS))
def test_exact_guard_all_values_reject_bad_types_and_size(op):
    for key in FIELDS[op]:
        for poison in (True, "1", 1.2, 10**55, None):
            v = dict(VALID[op])
            v[key] = poison
            assert witness(op, v)["status"] == "CONDITIONS_NOT_ESTABLISHED"

def test_math_counterexamples_independent_frozen_values():
    expected = {
        "reciprocal_epsilon_n": "N=13;1/N=1/13;epsilon=1/12",
        "quadratic_increment_vs_differential": "delta=5;dy=4;error=1",
        "tail_probability_vs_posterior": "P(E|H0)=1/20;P(H0|E)=1/91",
        "cobb_douglas_positive_example": "Q=30;log_inputs_positive=true",
        "integer_rhythm_lcm": "discrete_lcm=12",
        "affine_first_order_difference": "x_n=14;branch=a=1",
        "polynomial_upper_limit_integral": "integral_0_x_t2=9;derivative_at_x=9"
    }
    assert {key: witness(key, VALID[key])["value"] for key in expected} == expected
    assert witness("affine_first_order_difference",
                   {"a":2,"b":1,"x0":1,"n":3})["value"] == "x_n=15;branch=a!=1"

def test_no_students_freeform_approval_escape():
    for bad in ("", "__proto__", "teacher_approved", "FORMAL_THEOREM", "student_answer"):
        assert witness(bad, {"expr":"x=x"})["status"] == "UNSUPPORTED"
