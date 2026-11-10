"""Batch83: 60 distinct source-anchor editorial reviews and math boundaries.

No teacher approval, no general theorem proof certification or student publication.
"""
import json
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import sys
import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "backend"))
import build_kb_batch83_semantic_coverage as B83
from app.kb_batch83_math_relations import finite_witnesses, RELATIONS


@pytest.fixture(scope="module")
def report():
    return B83.build()


def author():
    return json.loads(B83.AUTHOR.read_text(encoding="utf8"))


def test_source_coverage_not_false_official_denominator(report):
    assert report["source_anchor_denominator"] == 428
    assert report["previous_editorial_reviews"] == 42
    assert report["new_editorial_reviews"] == 60
    assert report["cumulative_editorial_reviews"] == 102
    assert report["not_editorially_reviewed"] == 326
    assert report["official_curriculum_atom_denominator"] is None
    assert report["teacher_full_page_atomizations"] == 0
    assert report["teacher_approved"] == 0
    assert report["student_deep_content_published"] == 0
    assert report["by_track"]["ELECTIVE_E"]["source_review_anchor_denominator"] == 0
    assert report["by_track"]["ELECTIVE_E"]["official_mathematical_atom_denominator"] is None
    assert B83.OUT.read_text(encoding="utf8") == B83.dump(report)
    assert B83.MD.read_text(encoding="utf8") == B83.markdown(report)


def test_source_track_and_role_conservation(report):
    totals = report["by_track"]
    assert sum(x["source_review_anchor_denominator"] for x in totals.values()) == 428
    assert sum(x["editorially_paraphrased_source_anchors"] for x in totals.values()) == 102
    assert sum(x["without_original_semantic_paraphrase"] for x in totals.values()) == 326
    assert all(x["editorially_paraphrased_source_anchors"] == 17 for k, x in totals.items()
               if k != "ELECTIVE_E")
    assert sum(report["new_by_role"].values()) == 60
    assert Counter(x["track"] for x in report["new_rows"]) == {
        "COMPULSORY": 10, "SELECTIVE_COMPULSORY": 10, "ELECTIVE_A": 10,
        "ELECTIVE_B": 10, "ELECTIVE_C": 10, "ELECTIVE_D": 10,
    }


@pytest.mark.parametrize("ix", range(60))
def test_each_row_matches_provenance_and_never_promotes_status(ix, report):
    x = report["new_rows"][ix]
    upstream = B83.load(B83.B81.SOURCE)
    orig = next(r for r in upstream["anchor_review_queue"]
                if r["review_id"] == x["review_id"])
    for key in ("track", "printed_page", "pdfkit_line",
                "source_line_sha256", "source_page_pdfkit_sha256"):
        assert x[key] == orig[key]
    assert x["review_status"] == "REVIEW_PENDING"
    assert x["editorial_paraphrase_completed"] is True
    assert x["teacher_approved"] is False
    assert x["student_publishable"] is False
    assert x["student_authoritative_index_eligible"] is False
    assert x["official_atom_count"] is None
    assert x["math_certification"] == "NOT_FORMALLY_VERIFIED"
    assert not {"teacher_solution", "proof_certification", "teacher_approval_evidence"} & x.keys()


@pytest.mark.parametrize("ix", range(60))
@pytest.mark.parametrize("field,bad", (
    ("teacher_confirmed", True),
    ("student_publishable", True),
    ("official_atom_count", 0),
    ("official_atom_count", 1),
    ("cross_track_equivalence", "MATHEMATICALLY_EQUIVALENT"),
    ("original_editorial_paraphrase", "未审"),
    ("condition_or_scope_caution", ""),
))
def test_forbidden_status_or_degraded_editorial_evidence_rejected(ix, field, bad):
    x = author()
    x["records"][ix][field] = bad
    with pytest.raises(ValueError):
        B83.build(auth=x)


@pytest.mark.parametrize("ix", range(60))
def test_cross_track_spoofing_rejected(ix):
    x = author()
    t = x["records"][ix]["track"]
    x["records"][ix]["track"] = "ELECTIVE_A" if t != "ELECTIVE_A" else "ELECTIVE_D"
    with pytest.raises(ValueError, match="cross-track"):
        B83.build(auth=x)


@pytest.mark.parametrize("ix", range(60))
def test_reviewer_cannot_hide_extra_approval_field(ix):
    x = author()
    x["records"][ix]["teacher_approval_evidence"] = {"claimed": "yes"}
    with pytest.raises(ValueError, match="authoring fields"):
        B83.build(auth=x)


@pytest.mark.parametrize("ix", range(60))
def test_edited_source_id_cannot_slip_into_source_census(ix):
    x = author()
    x["records"][ix]["review_id"] = f"KB83-UNSOURCED-{ix:02}"
    with pytest.raises(ValueError):
        B83.build(auth=x)


@pytest.mark.parametrize("ix", range(60))
def test_invalid_heading_candidate_or_missing_math_candidate_rejected(ix):
    x = author()
    r = x["records"][ix]
    if r["semantic_role_provisional"] == "CURRICULUM_HEADING":
        r["possible_math_units_for_teacher_split"] = ["伪造的数学定义知识原子"]
    elif r["semantic_role_provisional"] in ("MIXED_CLAUSE", "MATHEMATICAL_REQUIREMENT"):
        r["possible_math_units_for_teacher_split"] = []
    else:
        r["possible_math_units_for_teacher_split"] = ["重复候选内容", "重复候选内容"]
    with pytest.raises(ValueError):
        B83.build(auth=x)


def test_prior_42_not_double_counted():
    x = author()
    previous_id = B83.B81.build()["rows"][0]["review_id"]
    x["records"][0]["review_id"] = previous_id
    with pytest.raises(ValueError):
        B83.build(auth=x)


def test_tampered_source_queue_line_sha_rejected():
    raw = B83.load(B83.B81.SOURCE)
    raw["anchor_review_queue"][25]["source_line_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="frozen 428"):
        B83.build(source=raw)


def test_forged_previous_review_completeness_rejected():
    prior = B83.B81.build()
    prior["teacher_approved"] = 42
    with pytest.raises(ValueError, match="previous editorial"):
        B83.build(previous=prior)


def test_actual_mac_pdf_line_sha_for_all_new_records():
    # The copyrighted original is deliberately absent from GitHub Actions.
    # Never silently turn an unavailable source into a verified source.
    if not B83.B81.LOCAL_PDF.is_file():
        pytest.skip("original source PDF only available on authorized Mac; frozen hashes checked in CI")
    result = B83.build(verify_local_source=True)
    assert len(result["new_rows"]) == 60


def test_explicit_local_pdf_verification_rejects_missing_source(monkeypatch, tmp_path):
    missing = tmp_path / "unavailable-official-curriculum.pdf"
    monkeypatch.setattr(B83.B81, "LOCAL_PDF", missing)
    with pytest.raises(ValueError, match="official source PDF unavailable"):
        B83.build(verify_local_source=True)


def test_exact_finite_witness_count_and_status(report):
    out = report["mathematics_finite_non_equivalence_witnesses"]
    assert len(out) == len(RELATIONS) == 5
    assert {w["op"] for w in out} == {r[0] for r in RELATIONS}
    assert all(w["general_equivalence_certified"] is False
               and w["teacher_approved"] is False
               and w["evidence_scope"] == "FINITE_EXACT_COUNTEREXAMPLE_ONLY" for w in out)
    assert out == finite_witnesses()


def test_sympy_independent_checks_of_five_math_boundary_witnesses():
    x = sp.symbols("x", real=True)
    # x^3 stationary derivative at x=0, but increasing on both sides.
    f = x**3
    assert sp.diff(f, x).subs(x, 0) == 0
    assert f.subs(x, -1) < f.subs(x, 0) < f.subs(x, 1)
    # One affine triple is not geometric.
    ys = (sp.Integer(1), sp.Integer(3), sp.Integer(5))
    assert ys[1] - ys[0] == ys[2] - ys[1]
    assert ys[1]**2 != ys[0] * ys[2]
    # Absolute value continuous at 0, not differentiable there.
    assert sp.limit(sp.Abs(x), x, 0) == 0
    assert sp.limit(sp.Abs(x)/x, x, 0, dir="-") == -1
    assert sp.limit(sp.Abs(x)/x, x, 0, dir="+") == 1
    # Finite increment differs from the linear differential.
    h = sp.Rational(1, 2)
    delta = (1+h)**2 - 1
    assert delta == sp.Rational(5, 4)
    assert sp.diff(x**2, x).subs(x, 1) * h == 1
    # Geometric area is nonnegative, signed integral may be negative.
    assert sp.integrate(-1, (x, 0, 1)) == -1
    assert sp.integrate(sp.Abs(-sp.Integer(1)), (x, 0, 1)) == 1
