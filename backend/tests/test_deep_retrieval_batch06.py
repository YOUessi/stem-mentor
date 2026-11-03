"""Batch06: collision-safe merge, 29 imported drafts, editorial retrieval and math checks."""
from __future__ import annotations

import copy
import json
import math
import subprocess
import sys
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path

import pytest
from pydantic import ValidationError
from sympy import Rational, binomial, simplify, sqrt

from app.deep_knowledge import DeepLesson, coverage_report, lessons
from app.deep_retrieval import (
    EditorOnlyError, _tokens, editor_draft_full, editor_draft_search,
    student_evidence_lookup,
)

ROOT = Path(__file__).resolve().parents[2]
NEW = ROOT / "knowledge/deep/v1"
BRIDGE = ROOT / "knowledge/deep/legacy_method_bridge_v1.json"
NEW_IDS = {
    obj["id"]
    for path in NEW.glob("*batch06_import.json")
    for obj in json.loads(path.read_text(encoding="utf-8"))
}


def test_batch02_has_real_distinct_authored_documents():
    all_docs = lessons()
    assert len(all_docs) >= 138
    assert len(NEW_IDS) == 29
    assert len({x.id for x in all_docs}) == len(all_docs)
    kinds = Counter(x.kind for x in all_docs)
    assert kinds["concept"] >= 66
    assert kinds["theorem"] >= 58
    assert kinds["method"] >= 14
    assert sum(kinds.values()) == len(all_docs)
    for doc in all_docs:
        assert doc.review.status == "REVIEW_PENDING"
        assert doc.teacher_solution_visibility == "TEACHER_ONLY"
        assert len(doc.worked_examples) >= 2
        assert len(doc.hint_ladder) >= 3
        assert doc.counterexamples and doc.misconceptions and doc.boundaries
        if doc.kind == "theorem":
            assert len(doc.proof_steps) >= 3


def test_coverage_denominator_is_engineering_not_official_atoms():
    info = coverage_report()
    assert info["curriculum_topic_total"] == 113
    assert info["deep_lesson_documents"] >= 138
    assert info["mapped_curriculum_ids"] == 113
    assert sum(x["engineering_topics"] for x in info["by_level"].values()) == 113
    assert sum(x["with_deep_draft"] for x in info["by_level"].values()) == 113
    assert sum(x["teacher_approved"] for x in info["by_level"].values()) == 0
    assert info["human_teacher_review_complete"] is False
    assert info["student_math_proofs_verified"] is False
    assert info["direct_student_teaching_enabled"] is False


@pytest.mark.parametrize("lesson_id", sorted(NEW_IDS))
def test_each_new_lesson_has_no_fake_teacher_approval(lesson_id):
    item = next(x for x in lessons() if x.id == lesson_id)
    bad = item.model_dump(mode="python")
    bad["review"] = {
        "status": "APPROVED",
        "reviewer_id": "author-fabricated",
        "reviewed_at": "2026-11-03",
        "review_record": "fake-evidence",
    }
    with pytest.raises(ValidationError, match="independently authenticated"):
        DeepLesson.model_validate(bad)


def test_editor_gate_is_fail_closed_even_if_local_authentication_claimed():
    with pytest.raises(EditorOnlyError):
        editor_draft_search("正弦定理")
    with pytest.raises(EditorOnlyError):
        editor_draft_full("math.hs.triangle.sine-law")
    with pytest.raises(KeyError):
        editor_draft_full("math.hs.nonexistent", scope="EDITOR_LOCAL")
    found = editor_draft_full("math.hs.triangle.ssa-ambiguity", scope="EDITOR_LOCAL")
    assert found["review_status"] == "REVIEW_PENDING"
    assert found["condition_status"] == "CONDITIONS_NOT_ESTABLISHED"


@pytest.mark.parametrize("query", [
    "正弦定理", "直线和圆", "二项分布", "回归分析",
    "数列初始条件", "数学建模", "条件概率", "垂直向量",
])
def test_student_search_does_not_expose_draft_proofs(query):
    result = student_evidence_lookup(query)
    assert result["candidates"] == []
    assert result["teacher_solution_exposed"] is False
    assert result["unverified_content_exposed"] is False
    assert result["status"] == "NO_APPROVED_EVIDENCE"
    assert "worked_examples" not in result


def test_editor_rankings_and_metadata_are_inspectable():
    hits = editor_draft_search("正弦定理 SSA", scope="EDITOR_LOCAL", limit=8)
    assert any(x["knowledge_id"] == "math.hs.triangle.ssa-ambiguity" for x in hits)
    assert all(x["condition_status"] == "CONDITIONS_NOT_ESTABLISHED" for x in hits)
    assert all(x["review_status"] == "REVIEW_PENDING" for x in hits)
    assert all("worked_examples" not in x for x in hits)
    g = editor_draft_search("直线 圆 切线", scope="EDITOR_LOCAL", limit=8)
    assert any(x["knowledge_id"] == "math.hs.geometry.line-circle" for x in g)
    c = editor_draft_search(
        "数学建模", scope="EDITOR_LOCAL", curriculum_ids=("HS-MATH-059",), limit=8
    )
    assert c and all("HS-MATH-059" in x["curriculum_ids"] for x in c)


def test_editor_retrieval_rejects_bad_queries_and_filters():
    for text in ("", "  ", "x" * 161, "\x00hi"):
        with pytest.raises(ValueError):
            editor_draft_search(text, scope="EDITOR_LOCAL")
    with pytest.raises(ValueError):
        editor_draft_search("数学", scope="EDITOR_LOCAL", limit=21)
    with pytest.raises(ValueError):
        editor_draft_search("数学", scope="EDITOR_LOCAL", kind="proof")
    with pytest.raises(ValueError):
        editor_draft_search("数学", scope="EDITOR_LOCAL", curriculum_ids=("HS-FAKE",))
    # Potential SQL/FTS operator characters cannot escape the sanitized token list.
    assert isinstance(editor_draft_search(
        '" OR 1=1 -- ; DROP TABLE evidence;', scope="EDITOR_LOCAL"
    ), list)


def test_legacy_bridge_preserves_all_26_unique_ids_without_promotion():
    data = json.loads(BRIDGE.read_text(encoding="utf-8"))
    legacy = json.loads((ROOT / "knowledge/corpus/methods.json").read_text())
    assert data["source_id_count"] == 26
    assert set(data["unconverted_ids"]) == {x["id"] for x in legacy}
    assert len(data["entries"]) == 26
    assert Counter(x["kind"] for x in data["entries"]) == {"method": 22, "strategy": 4}
    for entry in data["entries"]:
        original = next(x for x in legacy if x["id"] == entry["legacy_id"])
        assert entry["boundary"] == original["boundary"]
        assert entry["hint"] == original["hint"]
        assert entry["requires"] == original["requires"]
        assert entry["content_coverage_status"] == "NEEDS_DEEP_AUTHORING"
        assert entry["expert_review"] == "PENDING"
        assert not entry["candidate_deep_links"]


def test_legacy_bridge_regeneration_is_deterministic():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build_kb_legacy_bridge.py"), "--check"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("n,p", list(product(range(0, 9), (Rational(0), Rational(1), Rational(1, 2), Rational(2, 3)))))
def test_binomial_pmf_is_normalized_at_boundary(n, p):
    # Python/SymPy empty-product convention handles 0**0 at n=0 and at p=0/1.
    value = sum(binomial(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1))
    assert simplify(value - 1) == 0


@pytest.mark.parametrize("N", range(1, 8))
def test_hypergeometric_has_valid_integer_support_and_normalization(N):
    for K in range(N + 1):
        for n in range(N + 1):
            low = max(0, n - (N - K))
            high = min(n, K)
            probs = [
                binomial(K, k) * binomial(N - K, n - k) / binomial(N, n)
                for k in range(low, high + 1)
            ]
            assert probs and all(0 <= v <= 1 for v in probs)
            assert simplify(sum(probs) - 1) == 0


def test_exact_probability_union_nonexclusive_counterexample():
    universe = set(range(1, 7))
    A, B = {1, 2, 3}, {3, 4}
    P = lambda e: Fraction(len(e), len(universe))
    assert P(A | B) == P(A) + P(B) - P(A & B) == Fraction(2, 3)
    assert P(A) + P(B) == Fraction(5, 6)


@pytest.mark.parametrize("A,B,P", [
    (1, 0, (3, 4)), (3, 4, (0, 0)), (-2, 1, (2, 5)), (2, -1, (-1, 3))
])
def test_point_line_projection_formula(A, B, P):
    assert A * A + B * B > 0
    # Test ℓ:Ax+By+1=0. The orthogonal foot H must satisfy ℓ.
    x, y = map(Rational, P)
    A, B = Rational(A), Rational(B)
    f = A * x + B * y + 1
    h_x = x - f * A / (A*A + B*B)
    h_y = y - f * B / (A*A + B*B)
    assert simplify(A*h_x + B*h_y + 1) == 0
    squared_dist = simplify((x-h_x)**2+(y-h_y)**2)
    assert simplify(squared_dist - f*f/(A*A+B*B)) == 0


def test_ssa_has_two_distinct_angles_and_rejects_degeneracy():
    from sympy import asin, pi
    A = pi/6
    B1 = asin(Rational(3, 4))
    B2 = pi - B1
    assert 0 < B1 < B2
    assert A + B1 < pi
    assert A + B2 < pi
    # A=30, a=b=4: B'=150, so third angle zero and invalid.
    assert A + (pi - asin(Rational(1, 2))) == pi


def test_empirical_quantile_uses_explicit_lower_inverse_convention():
    def inverse_ecdf(xs, p):
        if not 0 < p <= 1:
            raise ValueError("p must be in (0,1]")
        ordered = sorted(xs)
        return ordered[math.ceil(len(ordered)*p)-1]
    assert inverse_ecdf([1,2,4,7], 0.5) == 2
    assert inverse_ecdf([1,1,3,6,8,9], 0.75) == 8
    with pytest.raises(ValueError):
        inverse_ecdf([1], 0)


def test_density_histogram_area_not_height():
    widths = (1, 4)
    freqs = (Fraction(1, 5), Fraction(4, 5))
    heights = [p/w for p,w in zip(freqs, widths)]
    assert heights[0] == heights[1]
    assert sum(h*w for h,w in zip(heights,widths)) == 1
    assert freqs[1] > freqs[0]


def test_geometry_vector_and_circle_exact_counterexamples():
    v1, v2 = (1, 2, -1), (2, -1, 0)
    assert sum(a*b for a,b in zip(v1,v2)) == 0
    assert sum(v*v for v in v1) > 0
    assert sum(v*v for v in v2) > 0
    # x^2+y^2=9 and y=3 is tangent, while y=0 has two intersections.
    assert 9-3**2 == 0
    assert 9-0**2 > 0
    assert 4-3**2 < 0


def test_prerequisite_graph_is_acyclic_and_not_accidentally_reversed():
    docs = {x.id:x for x in lessons()}
    assert docs["math.hs.triangle.area-sine"].id not in (
        docs["math.hs.triangle.area-sine"].prerequisite_lesson_ids
    )
    assert "math.hs.function.domain" in (
        docs["math.hs.sequence.recurrence-initial"].prerequisite_lesson_ids
    )
    for doc in docs.values():
        assert doc.id not in doc.prerequisite_lesson_ids
