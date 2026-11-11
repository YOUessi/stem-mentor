"""Batch36 47 legacy-scope reviews and 12 strictly bounded mathematics operators."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import sys
import pytest
from pydantic import ValidationError
from app.kb_batch36_finite_review import SPECS, VALID, INVALID, witness
from scripts.kb_frozen_batch24 import frozen_batch24_lessons as original_deep_lessons

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts"))
import build_kb_batch36_legacy_scope_review as review
ROWS = review.load_seed()
AUDIT = review.audit()
LINKS = AUDIT["links"]
REVIEW_MAP = {r.editorial_candidate_id: r for r in ROWS}
EXPECTED = json.loads(review.PRIOR.read_text(encoding="utf-8"))["links"]

@pytest.mark.parametrize("row", LINKS, ids=lambda x:x["editorial_candidate_id"])
def test_link_has_actual_mathematics_and_no_false_certification(row):
    assert row["legacy_lesson_assumptions"]
    assert row["legacy_lesson_counterexample_count"] >= 1
    assert row["review_finding"] in review.KINDS
    assert len(row["mathematical_assumption_to_check"]) >= 14
    assert len(row["specific_coverage_gap_or_counterexample"]) >= 18
    assert row["official_clause_alignment_verified"] is False
    assert row["mathematical_equivalence_certified"] is False
    assert row["student_publishable"] is False
    assert row["student_full_solution_exposed"] is False
    assert row["teacher_review"] == "PENDING"

@pytest.mark.parametrize("row", LINKS, ids=lambda x:x["editorial_candidate_id"])
def test_review_links_are_exactly_the_previously_curated_links(row):
    original = next(x for x in EXPECTED if x["editorial_candidate_id"]==row["editorial_candidate_id"])
    assert row["legacy_lesson_id"] == original["related_draft_lesson_id"]
    assert row["original_editorial_goal"] == original["original_editorial_goal"]
    assert row["source_printed_page"] == original["candidate_source_page"]
    assert row["candidate_track"] == original["candidate_track"]

@pytest.mark.parametrize("row", LINKS, ids=lambda x:x["editorial_candidate_id"])
def test_actual_legacy_lesson_sha256_and_no_teacher_answer_leak(row):
    path = ROOT / row["legacy_lesson_path"]
    docs = json.loads(path.read_text(encoding="utf-8"))
    source = next(x for x in docs if x["id"]==row["legacy_lesson_id"])
    canonical = json.dumps(source, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    assert row["legacy_lesson_content_sha256"] == hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert source["review"]["status"] == "REVIEW_PENDING"
    assert source["teacher_solution_visibility"] == "TEACHER_ONLY"
    assert row.get("worked_examples") is None
    assert row.get("teacher_solution") is None

@pytest.mark.parametrize("row", LINKS, ids=lambda x:x["editorial_candidate_id"])
def test_review_provenance_rejects_fake_pair_or_missing_conditions(row):
    current = REVIEW_MAP[row["editorial_candidate_id"]]
    source = review.SEED.read_text(encoding="utf-8")
    bad = source.replace(current.editorial_candidate_id, "KB33-A-P099-A999", 1)
    with pytest.raises(ValueError):
        review.audit(bad, enforce_pin=False)

@pytest.mark.parametrize("op", sorted(SPECS))
def test_specific_finite_exact_case(op):
    r = witness(op,VALID[op])
    assert r["status"] == "FINITE_EXACT_CASE_ONLY"
    assert r["teacher_approved"] == "false"
    assert r["general_theorem_certified"] == "false"
    assert r["student_freeform_step_verified"] == "false"
    assert r["exact_value"] and "nan" not in r["exact_value"].lower()

@pytest.mark.parametrize("op", sorted(SPECS))
def test_invalid_real_premise_is_rejected(op):
    assert witness(op,INVALID[op])["status"] == "CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("op", sorted(SPECS))
def test_empty_extra_and_unrecognized_fields_are_rejected(op):
    assert witness(op,{})["status"] == "CONDITIONS_NOT_ESTABLISHED"
    p=copy.deepcopy(VALID[op]);p["LLM_SAYS_VALID"]=True
    assert witness(op,p)["status"] == "CONDITIONS_NOT_ESTABLISHED"
    assert witness(op+"_VERIFIED",VALID[op])["status"] == "UNSUPPORTED"

@pytest.mark.parametrize("op", sorted(SPECS))
def test_each_parameter_rejects_boolean_invalid_type_and_oversized_integer(op):
    for key in SPECS[op]:
        bad = copy.deepcopy(VALID[op]);bad[key]=True
        assert witness(op,bad)["status"] == "CONDITIONS_NOT_ESTABLISHED"
        bad=copy.deepcopy(VALID[op]);bad[key]="1"
        assert witness(op,bad)["status"] == "CONDITIONS_NOT_ESTABLISHED"
        bad=copy.deepcopy(VALID[op]);bad[key]=10**100
        assert witness(op,bad)["status"] == "CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("mutation", ["duplicate","removed","unknown","missing_assumption","fake_review_kind"])
def test_bad_editorial_seed_rejected(mutation):
    text = review.SEED.read_text(encoding="utf-8")
    rows = [x for x in text.splitlines() if x and not x.startswith("#")]
    if mutation == "duplicate": rows[-1]=rows[0]
    elif mutation == "removed": rows.pop()
    elif mutation == "unknown": rows[0]=rows[0].replace("KB33-A-P052-A001","KB33-A-P099-A999")
    elif mutation == "missing_assumption":
        a=rows[0].split("|");a[2]="无";rows[0]="|".join(a)
    else:
        a=rows[0].split("|");a[1]="FULLY_APPROVED";rows[0]="|".join(a)
    altered = "# editable-review\n" + "\n".join(rows) + "\n"
    with pytest.raises((ValueError,ValidationError)):
        review.audit(altered,enforce_pin=False)

def test_generator_stable_full_47_and_denominators_remain_unknown():
    assert review.OUT.read_text(encoding="utf-8") == review.render()
    assert len(ROWS) == len(LINKS) == len(EXPECTED) == 47
    assert len({x["editorial_candidate_id"] for x in LINKS}) == 47
    assert sum(AUDIT["summary"]["findings_by_class"].values()) == 47
    assert AUDIT["summary"]["verified_syllabus_atom_equivalences"] == 0
    assert AUDIT["summary"]["teacher_approved"] == AUDIT["summary"]["student_published"] == 0
    assert all(v is None for v in AUDIT["summary"]["official_curriculum_denominator"].values())
    assert len(original_deep_lessons()) == 287

def test_original_seed_pin_and_old_crosswalk_pin():
    assert hashlib.sha256(review.SEED.read_bytes()).hexdigest() == review.PIN
    assert hashlib.sha256(review.PRIOR.read_bytes()).hexdigest() == review.PRIOR_PIN

def test_numeric_regressions_selected():
    assert witness("binomial_upper_tail",VALID["binomial_upper_tail"])["exact_value"] == "5/16"
    assert witness("mvt_square",VALID["mvt_square"])["exact_value"] == "2"
    assert witness("two_point_regression",VALID["two_point_regression"])["exact_value"] == "2"
    assert witness("rhythm_lcm",VALID["rhythm_lcm"])["exact_value"] == "12"
    assert witness("cramer_2x2",VALID["cramer_2x2"])["exact_value"] == "-2"
    assert witness("annuity_present_value",VALID["annuity_present_value"])["exact_value"] == "21000/121"

def test_no_llm_or_freeform_proof_is_accepted():
    for expr in ("", "__proto__", "PROOF_VERIFIED", "APPROVED_BY_LLM"):
        assert witness(expr,{})["status"] == "UNSUPPORTED"
