"""Batch21: independent exact bounded examples, scope integrity and tutor leakage regressions.

These oracles sample stated algebraic subclaims; they do NOT mechanically
certify complete proof_steps, source-clause equivalence or a student answer.
"""
import copy
import importlib.util
import json
from fractions import Fraction as Q
from itertools import product
from math import factorial, gcd
from pathlib import Path

import pytest
import sympy as sp
from pydantic import ValidationError
from app.deep_knowledge import DeepLesson, coverage_report, lessons
from app.deep_retrieval import EditorOnlyError, editor_draft_search, student_evidence_lookup

ROOT = Path(__file__).resolve().parents[2]
AUTHOR = ROOT / "curriculum/highschool_math/author_draft_batch21.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH21_EDITORIAL_GAP_OVERLAPS.json"
ROWS = json.loads(AUTHOR.read_text(encoding="utf-8"))
GAPS = json.loads(REPORT.read_text(encoding="utf-8"))

spec = importlib.util.spec_from_file_location(
    "batch21_builder", ROOT / "scripts/build_kb_batch21_lessons.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def test_batch21_11_units_integrated_and_28_open_gaps():
    lesson_text, report_text = builder.build()
    assert json.loads(lesson_text) == [r["lesson"] for r in ROWS]
    assert json.loads(report_text) == GAPS
    assert len(ROWS) == 11
    assert len({r["lesson"]["id"] for r in ROWS}) == 11
    assert {r["gap"] for r in ROWS} == {1, 2, 3, 6, 10, 11, 12, 14, 17, 20, 27}
    assert len(lessons()) == 267  # Includes independent Batch22; Batch21 snapshot itself remains 235
    assert coverage_report()["deep_lesson_documents"] == 267
    assert set(GAPS["summary"]["by_elective_track"]) == {
        "ELECTIVE_A", "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E"}
    assert GAPS["summary"]["open_editorial_gap_candidates"] == 28
    assert GAPS["summary"]["gap_tickets_still_open"] == 28
    assert GAPS["summary"]["editorial_gap_tickets_with_new_draft_overlap"] == 11
    assert GAPS["summary"]["no_new_draft_overlap"] == 17
    assert GAPS["summary"]["official_atomic_denominator"] is None
    assert GAPS["summary"]["official_coverage_rate"] is None
    assert GAPS["summary"]["teacher_approved"] == 0
    assert GAPS["summary"]["student_released"] == 0
    assert all(t["gap_remains_open"] and not t["student_publishable"]
               and t["teacher_review"] == "PENDING" for t in GAPS["ticket_status"])
    for row in ROWS:
        lesson = DeepLesson.model_validate(row["lesson"])
        assert lesson.review.status == "REVIEW_PENDING"
        assert lesson.teacher_solution_visibility == "TEACHER_ONLY"
        assert len(lesson.worked_examples) == 2
        assert len(lesson.counterexamples) == 1
        assert len(lesson.hint_ladder) == 3
    assert student_evidence_lookup("正交矩阵 最短距离 泛音 差分方程")["status"] == "NO_APPROVED_EVIDENCE"
    with pytest.raises(EditorOnlyError):
        editor_draft_search("最短距离")


@pytest.mark.parametrize("field,value", [
    ("teacher_solution_visibility", "STUDENT_VISIBLE"),
    ("review", {"status":"APPROVED", "reviewer_id":"fake",
                "reviewed_at":"2026-11-08", "review_record":"fake"}),
    ("kind", "theorem"),
])
def test_batch21_rejects_fake_teacher_or_student_content(field, value):
    bad = copy.deepcopy(ROWS[1]["lesson"])  # method
    bad[field] = value
    with pytest.raises(ValidationError):
        DeepLesson.model_validate(bad)


@pytest.mark.parametrize("mutation", ["duplicate_gap", "wrong_track", "approved", "one_example",
                                       "wrong_course", "fake_reviewer", "missing_gap"])
def test_batch21_generator_fails_closed_on_mutation(tmp_path, monkeypatch, mutation):
    raw = copy.deepcopy(ROWS)
    if mutation == "duplicate_gap":
        raw[1]["gap"] = raw[0]["gap"]
    elif mutation == "wrong_track":
        raw[0]["gap"] = 20
    elif mutation == "approved":
        raw[1]["lesson"]["review"]["status"] = "APPROVED"
    elif mutation == "one_example":
        raw[1]["lesson"]["worked_examples"].pop()
    elif mutation == "wrong_course":
        raw[0]["lesson"]["curriculum_ids"] = ["HS-MATH-002"]
    elif mutation == "fake_reviewer":
        raw[1]["lesson"]["review"]["reviewer_id"] = "fabricated"
    else:
        raw.pop()
    p = tmp_path / "mutated.json"
    p.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(builder, "AUTHOR", p)
    with pytest.raises((ValueError, ValidationError)):
        builder.build()


@pytest.mark.parametrize("n", range(1, 70))
def test_e_series_increasing_and_uniform_bound(n):
    s = sum((Q(1, factorial(k)) for k in range(n + 1)), Q(0))
    nxt = s + Q(1, factorial(n + 1))
    assert s < nxt
    assert 2 <= s < 3
    assert s <= Q(17, 6)  # independent tail bound, not an equality for e
    assert nxt < 3


@pytest.mark.parametrize("x,h", product(range(-9, 10), range(-11, 12)))
def test_differential_exact_quadratic_remainder(x, h):
    x, h = Q(x), Q(h, 10)
    delta = (x+h)**2-x**2
    dy = 2*x*h
    assert delta-dy == h*h
    if h != 0:
        assert (delta-dy)/h == h


@pytest.mark.parametrize("x,y", product(range(-12, 13), repeat=2))
def test_orthogonal_rotation_reflection_and_shear_counterexample(x, y):
    # Q=[0,-1;1,0] or R=[1,0;0,-1], both preserve squared length.
    original = x*x+y*y
    assert (-y)*(-y)+x*x == original
    assert x*x+(-y)*(-y) == original
    if x != 0:
        assert (2*x)**2 != x*x  # Q=diag(2,1/2) is not orthogonal


@pytest.mark.parametrize("x,y,z", product(range(-3, 4), repeat=3))
def test_three_unknown_rank_vs_augmented_rank(x, y, z):
    A = sp.diag(1,1,0)
    b = sp.Matrix([x,y,z])
    assert A.rank() == 2
    assert A.row_join(b).rank() == (2 if z == 0 else 3)
    assert (z == 0) == (A.row_join(b).rank() == A.rank())
    if z == 0:
        for t in (-9,0,9):
            assert A*sp.Matrix([x,y,t]) == b
    else:
        assert not (A*sp.Matrix([x,y,0]) == b)


@pytest.mark.parametrize("cx,cy", product(range(-5, 6), repeat=2))
def test_polytope_affine_extrema_by_exact_grid_and_tie(cx, cy):
    vertices = ((0,0),(2,0),(0,3),(2,3))
    values = [cx*x+cy*y for x,y in vertices]
    lo, hi = min(values), max(values)
    for x,y in product((Q(0),Q(1,2),Q(1),Q(3,2),Q(2)),
                       (Q(0),Q(3,4),Q(3,2),Q(9,4),Q(3))):
        assert lo <= cx*x+cy*y <= hi
    assert (cx == 0) == (values[0] == values[1])
    assert (cy == 0) == (values[0] == values[2])


@pytest.mark.parametrize("h,t,s", product(range(-7, 8),(-5,0,5),(-4,0,4)))
def test_skew_lines_exact_shortest_distance(h,t,s):
    # L1=(t,0,0), L2=(0,s,h); squared distance=t^2+s^2+h^2.
    assert t*t+s*s+h*h >= h*h
    assert abs(h) == abs(Q(h,1))
    assert 0*0+0*0+h*h == h*h


@pytest.mark.parametrize("a,b", product(range(-12,13), repeat=2))
def test_kmeans_centroid_sse_pair(a,b):
    center = Q(a+b,2)
    loss = (Q(a)-center)**2+(Q(b)-center)**2
    for delta in (-3,-1,0,2):
        candidate = center+delta
        cost = (Q(a)-candidate)**2+(Q(b)-candidate)**2
        assert cost == loss+2*delta*delta
    assert loss >= 0


@pytest.mark.parametrize("speed,minutes", product(range(-11, 12),range(0,41)))
def test_units_seconds_minutes_consistency(speed,minutes):
    # v in metres per second, t in minutes.
    assert speed*(60*minutes) == (60*speed)*minutes
    if speed and minutes:
        assert speed*minutes != (60*speed)*minutes


@pytest.mark.parametrize("ratings", product((1,2,3,4,5),repeat=3))
def test_ordinal_median_under_strictly_increasing_recode(ratings):
    x = sorted(ratings)
    encoded = sorted(z**3 for z in ratings)
    assert encoded[1] == x[1]**3
    assert [a<b for a,b in zip(x,x[1:])] == [a<b for a,b in zip(encoded,encoded[1:])]
    if x == [1,2,4]: assert Q(sum(encoded),3) != Q(sum(x),3)


@pytest.mark.parametrize("k,l", product(range(1,20),repeat=2))
def test_harmonic_gcd_smallest_common_period_of_individual_components(k,l):
    g = gcd(k,l)
    period = Q(1,g)  # f0=1 Hz, in seconds
    assert (k*period).denominator == 1
    assert (l*period).denominator == 1
    for n in range(1,g):
        shorter = Q(n,k*l)
        # Any shorter positive common period would contradict gcd minimality:
        if shorter < period:
            assert (k*shorter).denominator != 1 or (l*shorter).denominator != 1


@pytest.mark.parametrize("a,b,x0", product((Q(-2),Q(-1),Q(-1,2),Q(0),
                                              Q(1,2),Q(3,4),Q(1),Q(2)),
                                             range(-4,5),range(-4,5)))
def test_affine_recurrence_closed_form_and_edge_case(a,b,x0):
    x = Q(x0)
    fixed = Q(b)/(1-a) if a!=1 else None
    for n in range(10):
        predicted = x0+n*b if a==1 else fixed+a**n*(Q(x0)-fixed)
        assert x == predicted
        x = a*x+b
    if a==1 and b==0:
        assert x == x0
    if abs(a)>1 and x0==fixed:
        assert x == fixed


def test_noncertification_exceptions_are_explicit():
    # Parallel lines invalidate cross-product denominator.
    u = sp.Matrix([1,0,0])
    v = sp.Matrix([2,0,0])
    assert u.cross(v) == sp.zeros(3,1)
    # Singular coefficient matrix: det zero does not imply inconsistency.
    A = sp.diag(1,1,0)
    assert A.det() == 0
    assert A.row_join(sp.Matrix([2,3,0])).rank() == 2
    assert A.row_join(sp.Matrix([2,3,1])).rank() == 3
    # Mathematical domain: first-order approximation does not imply exact equality.
    assert (Q(201,100)**2-Q(2)**2) != Q(4,100)


@pytest.mark.parametrize("tamper", ["alter_step_reason", "fake_signed_teacher", "delete_proof_step"])
def test_batch21_proof_union_rejects_unverified_source_mutation(tmp_path, monkeypatch, tamper):
    """A review queue cannot silently diverge from the actual lesson index."""
    from scripts import build_kb_batch21_proof_union as proof_union
    raw = json.loads((ROOT / "knowledge/deep/v1/elective_gap_batch21.json").read_text(encoding="utf-8"))
    if tamper == "alter_step_reason":
        raw[0]["proof_steps"][0]["reason"] += " (unreviewed tamper)"
    elif tamper == "fake_signed_teacher":
        raw[0]["review"].update(status="APPROVED", reviewer_id="invented", reviewed_at="2026-11-08", review_record="invented")
    else:
        raw[0]["proof_steps"].pop()
    candidate = tmp_path / "tampered-review-source.json"
    candidate.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(proof_union, "NEW", candidate)
    with pytest.raises(ValueError):
        proof_union.build()
