#!/usr/bin/env python3
"""Batch36: 47 legacy elective links are *review tasks*, never syllabus coverage.

Every record explicitly identifies the missing mathematical assumption/scope.
The original 287 deep drafts and 49 separate review manuscripts remain untouched.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "curriculum/highschool_math/k00_batch36_47_legacy_scope_reviews.tsv"
PRIOR = ROOT / "docs/evaluation/KB_BATCH33_DRAFT_CROSSWALK_AUDIT.json"
OUT = ROOT / "docs/evaluation/KB_BATCH36_47_LEGACY_SCOPE_AUDIT.json"
PIN = "df10fe2a0689b2880b2593bf60d9ef9ae26b6a29d0c71b7560a01c1567328534"
PRIOR_PIN = "194c82bd9e4e4a40a71bb77dd665489006041a351b9cf14e9651cf3b076f2bd9"
KINDS = ("CLAUSE_UNVERIFIED", "PARTIAL_SCOPE", "CLAIM_MISMATCH")

class ReviewedPair(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    editorial_candidate_id: str = Field(pattern=r"^KB33-[A-E]-P0[567]\d-A\d{3}$")
    finding: Literal["CLAUSE_UNVERIFIED", "PARTIAL_SCOPE", "CLAIM_MISMATCH"]
    mathematical_assumption_to_check: str = Field(min_length=14, max_length=220)
    specific_coverage_gap_or_counterexample: str = Field(min_length=18, max_length=260)

def load_seed(text: str | None = None, *, enforce_pin: bool = True) -> tuple[ReviewedPair, ...]:
    if text is None:
        text = SEED.read_text(encoding="utf-8")
    if enforce_pin and hashlib.sha256(text.encode("utf-8")).hexdigest() != PIN:
        raise ValueError("Manual 47-link review TSV SHA256 mismatch")
    rows = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 4:
            raise ValueError("Every link review must contain exactly four fields")
        rows.append(ReviewedPair.model_validate(dict(zip(
            ("editorial_candidate_id", "finding", "mathematical_assumption_to_check",
             "specific_coverage_gap_or_counterexample"), parts))))
    if len(rows) != 47 or len({r.editorial_candidate_id for r in rows}) != 47:
        raise ValueError("Expected exactly 47 distinct legacy pair review tasks")
    return tuple(rows)

def deep_index() -> dict:
    out = {}
    for file in sorted((ROOT / "knowledge/deep/v1").glob("*.json")):
        parsed = json.loads(file.read_text(encoding="utf-8"))
        if not isinstance(parsed, list):
            raise ValueError(f"Unexpected lesson collection: {file}")
        for x in parsed:
            ident = x["id"]
            if ident in out:
                raise ValueError("Duplicate pre-existing deep lesson ID")
            if x["review"]["status"] != "REVIEW_PENDING" or x["teacher_solution_visibility"] != "TEACHER_ONLY":
                raise ValueError("Existing draft approval/visibility drift")
            if not (x.get("assumptions") and x.get("counterexamples") and
                    len(x.get("worked_examples", [])) >= 2):
                raise ValueError(f"Missing mathematical assumptions or review evidence: {ident}")
            out[ident] = (x, file)
    if len(out) != 287:
        raise ValueError("287 frozen legacy deep drafts changed; rebaseline explicitly")
    return out

def audit(review_text: str | None = None, *, enforce_pin: bool = True) -> dict:
    if hashlib.sha256(PRIOR.read_bytes()).hexdigest() != PRIOR_PIN:
        raise ValueError("The original curated 47-link audit is no longer pinned")
    old = json.loads(PRIOR.read_text(encoding="utf-8"))
    originals = old["links"]
    reviews = load_seed(review_text, enforce_pin=enforce_pin)
    if len(originals) != 47:
        raise ValueError("Unexpected legacy crosswalk size")
    byid = {r.editorial_candidate_id: r for r in reviews}
    old_ids = {r["editorial_candidate_id"] for r in originals}
    if old_ids != set(byid):
        raise ValueError("Manual review misses or forges candidate association")
    lessons = deep_index()
    links = []
    for old_row in originals:
        ident = old_row["editorial_candidate_id"]
        note = byid[ident]
        doc, file = lessons[old_row["related_draft_lesson_id"]]
        # SHA freezes the *actual* old mathematics, not just a manually claimed title.
        canonical = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if old_row["related_draft_title"] != doc["title"]:
            raise ValueError("Frozen relation title differs from actual deep draft")
        links.append({
            "editorial_candidate_id": ident,
            "candidate_track": old_row["candidate_track"],
            "source_printed_page": old_row["candidate_source_page"],
            "original_editorial_goal": old_row["original_editorial_goal"],
            "legacy_lesson_id": doc["id"],
            "legacy_lesson_title": doc["title"],
            "legacy_lesson_version": doc["version"],
            "legacy_lesson_path": str(file.relative_to(ROOT)),
            "legacy_lesson_content_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "legacy_lesson_assumptions": doc["assumptions"],
            "legacy_lesson_counterexample_count": len(doc["counterexamples"]),
            "review_finding": note.finding,
            "mathematical_assumption_to_check": note.mathematical_assumption_to_check,
            "specific_coverage_gap_or_counterexample": note.specific_coverage_gap_or_counterexample,
            "official_clause_alignment_verified": False,
            "mathematical_equivalence_certified": False,
            "teacher_review": "PENDING",
            "student_publishable": False,
            "student_full_solution_exposed": False,
            "followup": "逐句官方课标核对 + 针对限制条件反例及教师人工核准"
        })
    count = Counter(x["review_finding"] for x in links)
    return {
        "schema_version": "kb-batch36-legacy-pair-conditions-v1",
        "purpose": "47_MATHEMATICAL_SCOPE_REVIEWS_NOT_VERIFIED_SYLLABUS_COVERAGE",
        "source_audit_sha256": PRIOR_PIN,
        "manual_review_seed_sha256": PIN,
        "summary": {
            "historical_association_count": len(links),
            "explicit_mathematical_scope_reviews": len(links),
            "findings_by_class": {k: count[k] for k in KINDS},
            "legacy_deep_drafts": len(lessons),
            "separate_batch34_and_35_review_manuscripts": 49,
            "candidate_electives_total": 96,
            "verified_syllabus_atom_equivalences": 0,
            "teacher_approved": 0,
            "student_published": 0,
            "official_curriculum_denominator": {
                "COMPULSORY": None, "SELECTIVE_COMPULSORY": None,
                "ELECTIVE_A": None, "ELECTIVE_B": None, "ELECTIVE_C": None,
                "ELECTIVE_D": None, "ELECTIVE_E": None
            },
            "uncertified_proof_steps_from_frozen_baseline": 538,
            "unresolved_historical_content_conflicts": 10
        },
        "links": links,
        "policy": {
            "review_only": True,
            "teacher_solutions_excluded_from_output": True,
            "student_index_modified": False,
            "no_automatic_clause_equivalence": True,
            "mathematics_witnesses_not_formal_proofs": True
        }
    }

def render() -> str:
    return json.dumps(audit(), ensure_ascii=False, indent=2) + "\n"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    data = render()
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != data:
            raise SystemExit("Batch36 legacy pair review output drift")
    else:
        OUT.write_text(data, encoding="utf-8")
    print("PASS 47/47 distinct scoped legacy-link reviews; 0 syllabus equivalence certifications")

if __name__ == "__main__":
    main()
