"""Batch58 teacher-only assessment proposals and bounded exact math witnesses.

Finite enumeration checks only the explicit 14 worked examples, not a theorem's
general validity, real teacher approval, or students' freely typed proofs.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import sys

import pytest
from sympy import symbols, expand, simplify

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch58_competency_coverage as C

DRAFTS = C.read(C.DRAFTS)["items"]
DRAFT_IDS = {x["draft_id"] for x in DRAFTS}
MAPPING = {x["source_candidate_id"]: x for x in DRAFTS}


def test_fourteen_drafts_cover_achievement_and_activities_not_pedagogy():
    source = C.build()
    expected = {r["source_candidate_id"] for r in source["rows"]
                if r["source_kind"] in ("ACHIEVEMENT_REQUIREMENT", "ACTIVITY_REQUIREMENT")}
    assert len(DRAFTS) == 14 and set(MAPPING) == expected
    assert len(DRAFT_IDS) == 14
    assert source["teacher_only_draft_assessment_proposals"] == 14
    assert source["assessment_verified"] == 0
    assert source["assessment_unmapped"] == 28


@pytest.mark.parametrize("idx", range(14))
def test_each_teacher_proposal_is_full_scoped_unapproved(idx):
    d = DRAFTS[idx]
    assert len(d["original_problem"]) >= 18
    assert len(d["worked_solution_steps"]) >= 3
    assert len(d["hint_ladder"]) == 3
    assert len(d["scoring_rubric"]) >= 3
    assert d["nonexample_or_boundary"] != d["common_wrong_method"]
    assert d["review_status"] == "REVIEW_PENDING"
    assert d["teacher_solution_visibility"] == "TEACHER_ONLY"
    assert d["formal_general_proof_certified"] is False
    assert d["student_published"] is False
    assert d["math_verification_status"] == "FINITE_WITNESS_ONLY_NOT_GENERAL_CERTIFICATION"
    assert d["draft_id"] in C.OUT_DRAFT_MD.read_text(encoding="utf8")
    row = next(r for r in C.build()["rows"] if r["source_candidate_id"] == d["source_candidate_id"])
    assert row["teacher_only_assessment_draft_ids_not_verified"] == [d["draft_id"]]
    assert row["assessment_artifact_ids"] == row["rubric_evidence_ids"] == []


@pytest.mark.parametrize("mut", ["approved", "publish", "verify", "leak", "missing-rubric",
                                  "orphan", "duplicate", "missing-draft", "short-question"])
def test_fake_release_and_incomplete_proposals_rejected(mut):
    d = C.read(C.DRAFTS)
    a = d["items"]
    if mut == "approved":
        a[0]["review_status"] = "APPROVED"
    elif mut == "publish":
        a[0]["student_published"] = True
    elif mut == "verify":
        a[0]["formal_general_proof_certified"] = True
    elif mut == "leak":
        a[0]["teacher_solution_visibility"] = "PUBLIC"
    elif mut == "missing-rubric":
        a[0]["scoring_rubric"] = []
    elif mut == "orphan":
        a[0]["source_candidate_id"] = "KB56-C-P999-S999"
    elif mut == "duplicate":
        a[1]["source_candidate_id"] = a[0]["source_candidate_id"]
    elif mut == "missing-draft":
        a.pop()
    elif mut == "short-question":
        a[0]["original_problem"] = "求解"
    with pytest.raises(ValueError):
        C.build(drafts=d)


def test_manuscripts_reproduce_and_are_editor_only():
    source = C.build()
    md = C.OUT_DRAFT_MD.read_text(encoding="utf8")
    assert md == C.render_assessment_manuscripts(source, C.read(C.DRAFTS))
    assert md.count("## KB58-ASSESS-") == 14
    assert md.count("教师侧解题或论证步骤") == 14
    assert "REVIEW_PENDING" in md and "TEACHER_ONLY" in md
    assert "不接入学生挑战模式" in md


@pytest.mark.parametrize("n", range(1, 33))
def test_odd_sum_induction_finite_witness(n):
    assert sum(2 * k - 1 for k in range(1, n + 1)) == n * n
    assert (n + 1)**2 - n*n == 2*n + 1


@pytest.mark.parametrize("q", (F(-2), F(-1), F(0), F(1), F(2), F(3)))
def test_rational_domain_hole_is_not_promoted(q):
    if q != 1:
        lhs = (q*q - 1) / (q - 1)
        assert lhs == q + 1
        assert (lhs >= 0) == (q >= -1)
    else:
        with pytest.raises(ZeroDivisionError):
            _ = (q*q - 1) / (q - 1)


@pytest.mark.parametrize("n", range(1, 10))
def test_finite_square_perimeter_max_bound(n):
    width = F(n)
    area = width * (10 - width)
    assert area <= 25
    assert area == 25 if n == 5 else area < 25


@pytest.mark.parametrize("a,b", list(product(range(1, 7), repeat=2)))
def test_fair_dice_favorable_results(a, b):
    expect = (a + b == 7)
    assert expect == (b == 7-a)


def test_sets_functions_exponents_and_complex_exact():
    u = {-2,-1,0,1,2}
    a = {x for x in u if x >= 0}
    assert a == {0,1,2} and u-a == {-2,-1}
    values = {x: x*x for x in range(-2,3)}
    assert values[-2] == values[2] == 4
    assert 2**0 == 1 and 2**3 == 8
    assert (1+2j)*(1-1j) == 3+1j
    u2, v2 = (1,2),(2,-1)
    assert sum(x*y for x,y in zip(u2,v2)) == 0


def test_bisection_two_iterations_exact_endpoint_signs():
    def f(x): return x**3-x-1
    lo, hi = F(1), F(2)
    assert f(lo) == -1 and f(hi) == 5
    mid = (lo+hi)/2
    assert mid == F(3,2) and f(mid) == F(7,8)
    hi = mid
    mid = (lo+hi)/2
    assert mid == F(5,4) and f(mid) == F(-19,64)
    lo = mid
    assert hi-lo == F(1,4)
    assert (hi-lo)/2 == F(1,8)


def test_noncollinearity_and_degenerate_counterexample():
    p = (0,0,0); q=(1,0,0); r=(0,1,0); r2=(2,0,0)
    pq = [q[i]-p[i] for i in range(3)]
    pr = [r[i]-p[i] for i in range(3)]
    pr2 = [r2[i]-p[i] for i in range(3)]
    assert pq[0]*pr[1]-pq[1]*pr[0] == 1
    assert pq[0]*pr2[1]-pq[1]*pr2[0] == 0


def test_dice_weighted_sample_coin_and_plan_exact():
    assert len(list(product(range(1,7), repeat=2))) == 36
    assert sum(x+y==7 for x,y in product(range(1,7), repeat=2)) == 6
    assert F(6,36) == F(1,6)
    assert F(40*5+60*10,100) == 8
    assert F(5+10,2) != 8
    assert F(1,2)**10 == F(1,1024)
    assert F(20)+F(1,10)*600 == F(50)+F(1,20)*600
    assert F(50)+F(1,20)*1000 == 100
    assert F(20)+F(1,10)*1000 == 120


def test_finite_model_fits_do_not_prove_unique_extrapolation():
    x = symbols("x")
    line = 2*x+1
    alternative = line+x*(x-1)*(x-2)
    for t, value in ((0,1),(1,3),(2,5)):
        assert line.subs(x,t) == alternative.subs(x,t) == value
    assert line.subs(x,10) == 21
    assert alternative.subs(x,10) != line.subs(x,10)
    assert simplify(alternative-line) == x*(x-1)*(x-2)
