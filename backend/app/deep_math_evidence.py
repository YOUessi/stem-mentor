"""K07: narrow, reproducible math evidence for unpublished knowledge drafts.

This is NOT a general proof checker and never approves content or student steps.
Only project-authored, frozen rational/trigonometric claims are evaluated.
Expression parsing deliberately uses a restricted AST, not eval or sympify
on raw input. Outputs must not be exposed through student-facing HTTP routes.
"""
from __future__ import annotations

import ast
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sympy import (
    Integer, Rational, Symbol, cancel, cos, diff, factor_list, fraction,
    pi, simplify, sin, together, trigsimp,
)

from .deep_knowledge import ROOT, lessons

FIXTURE_FILE = ROOT / "knowledge/deep/math_evidence_v1.json"
NAMES = {name: Symbol(name, real=True) for name in ("x", "y", "a", "b", "c", "d", "q", "n")}
FUNCTIONS = {"sin": sin, "cos": cos}
CONSTANTS = {"pi": pi}


class EvidenceError(ValueError):
    """Malformed, unsafe or underspecified formal evidence."""


class MathExpr:
    def __init__(self, value, divisors=()):
        self.value = value
        self.divisors = tuple(divisors)


def parse_expression(source: str) -> MathExpr:
    """Safely parse a limited arithmetic/trigonometric expression.

    No general function calls, comparisons, attributes, comprehensions,
    negative powers, unbounded exponents, or arbitrary Python evaluation.
    """
    if not isinstance(source, str) or not 1 <= len(source) <= 180:
        raise EvidenceError("expression length outside 1-180 characters")
    try:
        tree = ast.parse(source, mode="eval")
    except (SyntaxError, ValueError) as exc:
        raise EvidenceError("invalid expression syntax") from exc
    if len(list(ast.walk(tree))) > 90:
        raise EvidenceError("expression AST too complex")

    def visit(node) -> MathExpr:
        if isinstance(node, ast.Constant) and type(node.value) is int:
            if abs(node.value) > 100000:
                raise EvidenceError("integer literal too large")
            return MathExpr(Integer(node.value))
        if isinstance(node, ast.Name):
            if node.id in NAMES:
                return MathExpr(NAMES[node.id])
            if node.id in CONSTANTS:
                return MathExpr(CONSTANTS[node.id])
            raise EvidenceError("unknown variable or constant")
        if isinstance(node, ast.UnaryOp) and type(node.op) in (ast.USub, ast.UAdd):
            item = visit(node.operand)
            return MathExpr(-item.value if isinstance(node.op, ast.USub) else item.value, item.divisors)
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in FUNCTIONS:
                raise EvidenceError("function is not explicitly permitted")
            if node.keywords or len(node.args) != 1:
                raise EvidenceError("unexpected function arguments")
            arg = visit(node.args[0])
            return MathExpr(FUNCTIONS[node.func.id](arg.value), arg.divisors)
        if isinstance(node, ast.BinOp):
            left = visit(node.left)
            if isinstance(node.op, ast.Pow):
                # Only nonnegative literal integer powers, including zero.
                if not (isinstance(node.right, ast.Constant)
                        and type(node.right.value) is int
                        and 0 <= node.right.value <= 8):
                    raise EvidenceError("only literal integer powers from 0 to 8")
                return MathExpr(left.value ** node.right.value, left.divisors)
            right = visit(node.right)
            divs = left.divisors + right.divisors
            if isinstance(node.op, ast.Add):
                return MathExpr(left.value + right.value, divs)
            if isinstance(node.op, ast.Sub):
                return MathExpr(left.value - right.value, divs)
            if isinstance(node.op, ast.Mult):
                return MathExpr(left.value * right.value, divs)
            if isinstance(node.op, ast.Div):
                if right.value == 0:
                    raise EvidenceError("division by zero is never allowed")
                # Capture original divisors before SymPy can cancel away holes.
                return MathExpr(left.value / right.value, divs + (right.value,))
        raise EvidenceError("unsupported Python expression syntax")

    return visit(tree.body)


def _irreducible_nonzero(expression) -> set[str]:
    """Nonzero factors; ignore nonzero numeric units and signs.

    The grammar is an authored-claim subset, not arbitrary SymPy expressions.
    A rational divisor is nonzero only if its numerator is nonzero; any
    denominator in that divisor was already captured by parse_expression.
    """
    num, _ = fraction(together(expression))
    if num == 0:
        raise EvidenceError("zero cannot satisfy a nonzero obligation")
    try:
        _, factors = factor_list(num)
    except (TypeError, ValueError, NotImplementedError) as exc:
        raise EvidenceError("cannot factor symbolic nonzero obligation") from exc
    result = set()
    for factor, _power in factors:
        if factor.is_number:
            if factor == 0:
                raise EvidenceError("zero guard")
            continue
        key = str(factor if not factor.could_extract_minus_sign() else -factor)
        result.add(key)
    return result


def missing_domain_guards(items: tuple[MathExpr, ...], declared_guards: list[str]) -> list[str]:
    required = set()
    for item in items:
        for denominator in item.divisors:
            required.update(_irreducible_nonzero(denominator))
    declared = set()
    for raw in declared_guards:
        expr = parse_expression(raw)
        if expr.divisors:
            raise EvidenceError("nonzero guards must not contain divisions")
        declared.update(_irreducible_nonzero(expr.value))
    return sorted(required - declared)


class FrozenClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^ev\.[a-z0-9.-]+$")
    lesson_id: str = Field(pattern=r"^math\.hs\.[a-z0-9._-]+$")
    kind: str = Field(pattern=r"^(identity|derivative|counterexample|domain_gap)$")
    lhs: str = Field(min_length=1, max_length=180)
    rhs: str = Field(min_length=1, max_length=180)
    nonzero: list[str] = Field(default_factory=list)
    assignments: dict[str, str] = Field(default_factory=dict)
    relation: str = Field(default="eq", pattern=r"^(eq|le|ge)$")
    differentiate_by: str | None = None
    expected_status: str
    explanation: str = Field(min_length=12)
    proof_scope: str = Field(pattern=r"^(SUPPORTING_ALGEBRA|SUPPORTING_TRIG|FINITE_WITNESS)$")
    provenance: str = Field(pattern=r"^PROJECT_AUTHORED$")
    review_status: str = Field(pattern=r"^REVIEW_PENDING$")

    @model_validator(mode="after")
    def validate_kind(self):
        outcomes = {
            "identity": "IDENTITY_ON_DECLARED_DOMAIN",
            "derivative": "DERIVATIVE_IDENTITY",
            "counterexample": "VALID_COUNTEREXAMPLE",
            "domain_gap": "DOMAIN_NOT_ESTABLISHED",
        }
        if self.expected_status != outcomes[self.kind]:
            raise ValueError("unexpected fixed evidence expectation")
        if self.kind != "counterexample" and self.assignments:
            raise ValueError("assignments only for counterexamples")
        if self.kind == "counterexample" and not self.assignments:
            raise ValueError("counterexample needs a concrete witness")
        if self.kind == "derivative" and self.differentiate_by not in NAMES:
            raise ValueError("derivative needs a whitelisted variable")
        if self.kind != "derivative" and self.differentiate_by is not None:
            raise ValueError("differentiate_by only for derivatives")
        if self.kind == "counterexample" and self.proof_scope != "FINITE_WITNESS":
            raise ValueError("a finite witness cannot claim a theorem")
        if self.kind == "domain_gap" and self.proof_scope == "FINITE_WITNESS":
            raise ValueError("domain gap is not a counterexample")
        return self


def _equal(lhs, rhs) -> bool:
    # Rational identities and trig identities, not inequalities or geometry.
    return simplify(trigsimp(cancel(together(lhs - rhs)))) == 0


def _rational_assignments(raw: dict[str, str]):
    values = {}
    for key, value in raw.items():
        if key not in NAMES:
            raise EvidenceError("unknown witness variable")
        if not isinstance(value, str) or len(value) > 16:
            raise EvidenceError("invalid rational witness")
        try:
            if "/" in value:
                parts = value.split("/")
                if len(parts) != 2 or not all(part.lstrip("-").isdigit() for part in parts):
                    raise ValueError("not a rational literal")
                num, den = (int(p) for p in parts)
                if not den or abs(num) > 10000 or abs(den) > 10000:
                    raise ValueError("rational witness out of bounds")
                values[NAMES[key]] = Rational(num, den)
            elif value.lstrip("-").isdigit() and abs(int(value)) <= 10000:
                values[NAMES[key]] = Integer(int(value))
            else:
                raise ValueError("not a bounded rational literal")
        except (TypeError, ValueError, ZeroDivisionError) as exc:
            raise EvidenceError("bad or unsafe rational witness") from exc
    return values


def evaluate(claim: FrozenClaim) -> dict[str, Any]:
    """Check only the stated, narrow formal claim (never the full lesson proof)."""
    left, right = parse_expression(claim.lhs), parse_expression(claim.rhs)
    missing = missing_domain_guards((left, right), claim.nonzero)
    base = {"id": claim.id, "lesson_id": claim.lesson_id,
            "evidence_scope": claim.proof_scope,
            "whole_theorem_verified": False,
            "student_step_verified": False,
            "teacher_review": "PENDING"}
    if missing:
        return {**base, "status": "DOMAIN_NOT_ESTABLISHED", "missing_nonzero": missing}
    if claim.kind == "counterexample":
        values = _rational_assignments(claim.assignments)
        all_symbols = left.value.free_symbols | right.value.free_symbols
        if not all_symbols.issubset(values):
            return {**base, "status": "WITNESS_INCOMPLETE"}
        if any(simplify(den.subs(values)) == 0 for item in (left, right) for den in item.divisors):
            return {**base, "status": "WITNESS_OUTSIDE_DOMAIN"}
        a = simplify(left.value.subs(values))
        b = simplify(right.value.subs(values))
        if a.is_number is not True or b.is_number is not True or not a.is_real or not b.is_real:
            return {**base, "status": "WITNESS_INDETERMINATE"}
        holds = {"eq": a == b, "le": a <= b, "ge": a >= b}[claim.relation]
        return {**base, "status": "COUNTEREXAMPLE_FAILED" if holds else "VALID_COUNTEREXAMPLE",
                "witness_values": {str(k): str(v) for k, v in values.items()},
                "left_value": str(a), "right_value": str(b)}
    if claim.kind == "derivative":
        variable = NAMES[claim.differentiate_by]
        ok = _equal(diff(left.value, variable), right.value)
        return {**base, "status": "DERIVATIVE_IDENTITY" if ok else "DERIVATIVE_MISMATCH"}
    ok = _equal(left.value, right.value)
    return {**base, "status": "IDENTITY_ON_DECLARED_DOMAIN" if ok else "IDENTITY_MISMATCH"}


@lru_cache(maxsize=1)
def claims() -> tuple[FrozenClaim, ...]:
    data = json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise EvidenceError("expected list of frozen authored claims")
    known = {doc.id for doc in lessons()}
    entries = tuple(FrozenClaim.model_validate(item) for item in data)
    keys = [item.id for item in entries]
    if len(keys) != len(set(keys)):
        raise EvidenceError("duplicate evidence IDs")
    for claim in entries:
        if claim.lesson_id not in known:
            raise EvidenceError(f"unknown lesson: {claim.lesson_id}")
    return entries


def evidence_audit() -> dict[str, Any]:
    results = [evaluate(entry) for entry in claims()]
    issues = [
        {"id": claim.id, "expected": claim.expected_status,
         "actual": result["status"], "reason": result.get("missing_nonzero")}
        for claim, result in zip(claims(), results)
        if claim.expected_status != result["status"]
    ]
    return {
        "scope": "LIMITED_AUTHORED_EXPRESSION_EVIDENCE_NOT_FULL_PROOF",
        "claims": len(results),
        "expected_status_counts": dict(Counter(c.expected_status for c in claims())),
        "actual_status_counts": dict(Counter(r["status"] for r in results)),
        "linked_lesson_count": len({c.lesson_id for c in claims()}),
        "total_draft_lessons": len(lessons()),
        "math_subclaims_checked": len(results) - len(issues),
        "whole_theorems_verified": 0,
        "student_free_text_steps_verified": 0,
        "teacher_approved": 0,
        "failures": issues,
        "review_state": "REVIEW_PENDING",
        "notes": [
            "Each result applies to one explicitly authored rational or trig statement only.",
            "Domain guards are declared assumptions, not premises independently established.",
            "Finite witnesses disprove only the particular stated false universal claim.",
            "No derived result may be marked as a reviewed proof of a course theorem."
        ],
    }
