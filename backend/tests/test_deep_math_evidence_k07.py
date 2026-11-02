"""K07 safety and mathematical evidence regression for deep draft material.

The checks certify only frozen subclaims, never whole proofs, approval, or
student free-text mathematics.
"""
import copy
import importlib.util
import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from sympy import Integer, Rational, simplify

from app.deep_knowledge import lessons
from app.deep_math_evidence import (
    FIXTURE_FILE, EvidenceError, FrozenClaim, NAMES, claims, evaluate,
    evidence_audit, missing_domain_guards, parse_expression,
)


@pytest.mark.parametrize("claim", claims(), ids=lambda c: c.id)
def test_every_authored_claim_has_expected_independent_result(claim):
    result = evaluate(claim)
    assert result["status"] == claim.expected_status
    assert result["lesson_id"] == claim.lesson_id
    assert result["whole_theorem_verified"] is False
    assert result["student_step_verified"] is False
    assert result["teacher_review"] == "PENDING"


def test_certificates_are_only_subclaims_and_keep_teacher_review_pending():
    report = evidence_audit()
    assert report["claims"] == 48
    assert report["linked_lesson_count"] >= 12
    assert report["total_draft_lessons"] == 28
    assert report["failures"] == []
    assert report["math_subclaims_checked"] == 48
    assert report["whole_theorems_verified"] == 0
    assert report["student_free_text_steps_verified"] == 0
    assert report["teacher_approved"] == 0
    assert all(item.review.status == "REVIEW_PENDING" for item in lessons())


def test_freeze_generator_matches_checked_in_fixtures_without_mutating_files():
    source = Path(__file__).resolve().parents[2] / "scripts/build_deep_math_evidence.py"
    spec = importlib.util.spec_from_file_location("authored_k07_cases", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert json.loads(FIXTURE_FILE.read_text(encoding="utf-8")) == module.ROWS
    assert len({item["id"] for item in module.ROWS}) == len(module.ROWS)


@pytest.mark.parametrize("source", [
    "__import__('os').system('echo broken')",
    "open('/tmp/nope')",
    "eval('2+2')",
    "sin(x,y)",
    "sin(x, y=3)",
    "x.real",
    "x.__class__",
    "(x for x in (1,2))",
    "x if 1 else y",
    "[x, y]",
    "x[0]",
    "1.2",
    "True",
    "x**-1",
    "x**9",
    "x**y",
    "x//2",
    "x%2",
    "x<y",
    "x and y",
    "1/(x-x)",
    "5**100",
    "1000000000",
])
def test_untrusted_python_syntax_and_unsafe_operations_are_rejected(source):
    with pytest.raises(EvidenceError):
        parse_expression(source)


@pytest.mark.parametrize("left,right,guards,expected", [
    ("x/x", "1", [], ["x"]),
    ("(x**2-1)/(x-1)", "x+1", [], ["x - 1"]),
    ("1/x+1/y", "(x+y)/(x*y)", ["x"], ["y"]),
    ("1/(x*y)", "1", ["x*y"], []),
    ("(a*b)/b", "a", ["b"], []),
    ("(x**2-1)/(x-1)", "x+1", ["1-x"], []),
    ("1/(x*x)", "1", ["x"], []),
    ("1/(x**2-y**2)", "1", ["x-y", "x+y"], []),
    ("(x/y)/x", "1/y", ["x","y"], []),
    ("a*x**2+b*x+c", "a*(x+b/(2*a))**2+(4*a*c-b**2)/(4*a)", [], ["a"]),
])
def test_exact_nonzero_obligations_survive_simplification(left,right,guards,expected):
    got = missing_domain_guards(
        (parse_expression(left), parse_expression(right)), guards)
    assert got == expected


def test_cannot_forge_approval_on_a_mathematical_fixture():
    item = claims()[0].model_dump()
    item["review_status"] = "APPROVED"
    with pytest.raises(ValidationError):
        FrozenClaim.model_validate(item)


@pytest.mark.parametrize("key,value", [
    ("expected_status", "FULL_THEOREM_VERIFIED"),
    ("provenance", "COPYRIGHT_UNKNOWN"),
    ("kind", "arbitrary_python"),
    ("proof_scope", "FULL_FORMAL_PROOF"),
    ("differentiate_by", "os"),
])
def test_frozen_claim_contract_rejects_overclaiming_or_unauthorized_values(key,value):
    base = claims()[0].model_dump()
    base[key] = value
    with pytest.raises(ValidationError):
        FrozenClaim.model_validate(base)


def test_explicit_counterexample_witness_is_not_a_heuristic_or_guess():
    source = next(c for c in claims() if c.id == "ev.wrong-square-sum")
    answer = evaluate(source)
    assert answer["status"] == "VALID_COUNTEREXAMPLE"
    assert answer["left_value"] == "4"
    assert answer["right_value"] == "2"
    assert answer["witness_values"] == {"x": "1", "y": "1"}


def test_fake_witness_where_claim_is_true_does_not_validate_counterexample():
    source = next(c for c in claims() if c.id == "ev.wrong-square-sum")
    changed = source.model_copy(update={"assignments": {"x":"0", "y":"2"}})
    answer = evaluate(changed)
    assert answer["status"] == "COUNTEREXAMPLE_FAILED"


def test_counterexample_at_undefined_input_does_not_validate_claim():
    source = next(c for c in claims() if c.id == "ev.wrong-ratio-symmetry")
    changed = source.model_copy(update={"assignments": {"x":"0","y":"3"}})
    answer = evaluate(changed)
    assert answer["status"] == "WITNESS_OUTSIDE_DOMAIN"


@pytest.mark.parametrize("values", [
    {"x":"99999999999","y":"1"}, {"x":"1/0","y":"1"},
    {"x":"1/100000000","y":"1"}, {"z":"2","y":"3"},
    {"x":"__import__('os')","y":"1"},
])
def test_untrusted_rational_witnesses_are_rejected(values):
    source = next(c for c in claims() if c.id == "ev.wrong-ratio-symmetry")
    altered = source.model_copy(update={"assignments": values})
    with pytest.raises(EvidenceError):
        evaluate(altered)


def test_all_authored_proof_subclaims_are_general_not_single_point_matches():
    # These are exact symbolic identities, not random numeric equality tests.
    ids = [
        "ev.vertex-parametric", "ev.geometric-finite-six", "ev.arithmetic-six",
        "ev.binomial-five", "ev.sine-add", "ev.cosine-sub",
    ]
    for claim_id in ids:
        entry = next(c for c in claims() if c.id == claim_id)
        assert evaluate(entry)["status"] == "IDENTITY_ON_DECLARED_DOMAIN"
        assert entry.proof_scope in {"SUPPORTING_ALGEBRA","SUPPORTING_TRIG"}


def test_cancelled_expression_excludes_the_original_zero_denominator():
    raw = parse_expression("(x**2-1)/(x-1)")
    assert simplify(raw.value).subs(NAMES["x"], Integer(1)) == 2
    assert str(raw.value.subs(NAMES["x"], Integer(1))) == "nan"
    # Algebraic cancellation is not permission to silently include x=1.
    assert missing_domain_guards((raw,), []) == ["x - 1"]


def test_existing_student_api_has_no_raw_unreviewed_math_evidence_endpoint():
    from app.main import app
    paths = [route.path for route in app.routes]
    assert not any("math_evidence" in path or "/certificates" in path for path in paths)
    assert not any("teacher-preview" in path for path in paths)


def test_algebraically_false_claim_is_not_certified_by_same_schema():
    good = next(c for c in claims() if c.id == "ev.square-sum")
    altered = good.model_copy(update={"rhs": "x**2+y**2"})
    assert evaluate(altered)["status"] == "IDENTITY_MISMATCH"


def test_wrong_derivative_coefficient_is_detected():
    good = next(c for c in claims() if c.id == "ev.differentiate-cubic")
    altered = good.model_copy(update={"rhs": "2*x**2"})
    assert evaluate(altered)["status"] == "DERIVATIVE_MISMATCH"


def test_malicious_zero_nonzero_assumption_is_rejected():
    with pytest.raises(EvidenceError):
        missing_domain_guards((parse_expression("x/x"),), ["0"])


def test_claim_does_not_auto_prove_a_different_lesson():
    good = next(c for c in claims() if c.id == "ev.binomial-five")
    assert evaluate(good)["whole_theorem_verified"] is False
    assert good.lesson_id == "math.hs.counting.binomial"
    assert len({c.lesson_id for c in claims()}) < len(lessons())
