#!/usr/bin/env python3
"""Batch07: conservative release-blocking elective, editorial-conflict and proof audit.

A source file's spelling is NOT an official syllabus atom; supporting SymPy cases
cannot certify a mathematical proof, nor can untrusted JSON grant teacher approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "curriculum/highschool_math/official_scope_v1.json"
CURRICULUM = ROOT / "curriculum/highschool_math/curriculum_map.json"
RECONCILE = ROOT / "docs/evaluation/KB_BATCH02_RECONCILIATION.json"
EVIDENCE = ROOT / "knowledge/deep/math_evidence_v1.json"
LESSON_DIR = ROOT / "knowledge/deep/v1"
CROSSWALK_OUT = ROOT / "curriculum/highschool_math/elective_track_crosswalk_batch07.json"
CONFLICT_OUT = ROOT / "docs/evaluation/KB_CONFLICT_RISK_BATCH07.json"
PROOF_OUT = ROOT / "docs/evaluation/KB_PROOF_OBLIGATIONS_BATCH07.json"

REVIEW_HINTS = {
    "math.hs.function.composition-domain": "验证先 g 后 f，联合 g 的定义域和 g(x) 属于 f 定义域；逐项检查根式/分母。",
    "math.hs.function.parity": "先确认定义域关于零对称，再验证 f(-x)=±f(x)，并检查零函数的双重情况。",
    "math.hs.function.piecewise": "检查分段条件交并是否恰好覆盖定义域，边界点仅属于一个分支。",
    "math.hs.function.zero-ivt": "闭区间连续且端点异号保证至少一个零点；无条件保证唯一性，端点同号也不能推断无零点。",
    "math.hs.geometry.point-line-distance": "检查 A,B 不同时为零，点到直线的法向量及平方根分母。",
    "math.hs.probability.binomial-distribution": "独立同分布伯努利试验，边界 p=0,1 和整数 0<=k<=n。",
    "math.hs.probability.hypergeometric": "有限总体无放回，参数满足 0<=K<=N、0<=n<=N、合法 k 支撑。",
    "math.hs.statistics.correlation-regression": "回归系数分母非零；相关不是因果；常量自变量时斜率未定义。",
    "math.hs.triangle.area-sine": "两边夹角的正弦，非夹角不得直接套用；退化零角不构成非退化三角形。",
    "math.hs.vector.linear-operations": "确保向量维度相同、分量逐一计算；两版 kind 不同须分别审查定义与命题。",
}

def as_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()

def lookup(path, key):
    values = as_json(path)
    found = [x for x in values if x["id"] == key]
    if len(found) != 1:
        raise ValueError(f"Not exactly one source {key} in {path}")
    return found[0]

def build():
    official = as_json(OFFICIAL)
    course = as_json(CURRICULUM)["coverage"]
    reconciled = as_json(RECONCILE)
    evidence = as_json(EVIDENCE)
    sys.path.insert(0, str(ROOT))
    from backend.app.deep_knowledge import lessons  # full strict validation
    docs = list(lessons())

    tracks = [t for t in official["tracks"] if t["id"].startswith("ELECTIVE_")]
    if [t["id"] for t in tracks] != ["ELECTIVE_A", "ELECTIVE_B", "ELECTIVE_C",
                                     "ELECTIVE_D", "ELECTIVE_E"]:
        raise ValueError("Missing elective track from official high-level scope")
    legacy = [x for x in course if x["level"] == "选修拓展" and not x.get("elective_track")]
    new_editorial = [x for x in course if x.get("elective_track") in {t["id"] for t in tracks}]
    matrix = []
    for track in tracks:
        for order, theme in enumerate(track["themes"], 1):
            matrix.append({
                "key": f'{track["id"]}:THEME:{order:02d}',
                "track": track["id"], "theme": theme,
                "mapping_status": "HIGH_LEVEL_THEME_ONLY_NOT_ATOMIC",
                "verified_official_atom_ids": [],
                "assigned_legacy_engineering_topic_ids": [],
                "approved_deep_lesson_ids": [],
                "human_review": "PENDING",
                "note": "Official high-level curriculum theme transcription is not an itemized teaching syllabus.",
            })
    crosswalk = {
        "status": "CANDIDATE_CROSSWALK_UNVERIFIED",
        "scope": "ELECTIVES_A_E_HIGH_LEVEL_THEMES_NOT_OFFICIAL_ATOMS",
        "standard": official["basis"], "standard_url": official["url"],
        "tracks": [t["id"] for t in tracks],
        "summary": {
            "elective_tracks": len(tracks), "high_level_theme_slots": len(matrix),
            "atomic_subtopics_verified": 0,
            "legacy_extension_topics_without_explicit_track": len(legacy),
            "teacher_approved_elective_lessons": 0,
            "mapped_draft_links": 0,
        },
        "theme_candidates": matrix,
        "new_unreviewed_elective_engineering_candidates": len(new_editorial),
        "unassigned_legacy_extension_topics": [
            {"id": x["id"], "concept": x["concept"], "status": "ELECTIVE_TRACK_NOT_ASSIGNED"}
            for x in legacy
        ],
        "warnings": [
            "A-E themes were copied from the existing internal high-level scope; no page-level atomic crosswalk has been independently verified.",
            "A high-level theme does not represent a complete approved lesson or track curriculum.",
            "Seven old engineering extension topics have no verified A-E allocation; none may be silently assigned.",
        ],
    }
    if len(matrix) != sum(len(t["themes"]) for t in tracks):
        raise ValueError("Lost elective themes")
    if len({x["key"] for x in matrix}) != len(matrix):
        raise ValueError("Duplicated elective theme slot")

    conflicts = []
    for x in reconciled["unresolved_conflicts"]:
        id_ = x["id"]
        old = lookup(ROOT / x["existing_source"], id_)
        candidate = lookup(ROOT / x["candidate_source"], id_)
        if sha(old) != x["existing_sha256"] or sha(candidate) != x["candidate_sha256"]:
            raise ValueError(f"Conflict evidence changed without review: {id_}")
        if id_ not in REVIEW_HINTS:
            raise ValueError(f"No subject-specific review hint: {id_}")
        if any(z["review"]["status"] == "APPROVED" for z in (old, candidate)):
            raise ValueError(f"Fake conflict approval: {id_}")
        high_risk = sorted(set(x["differing_fields"]) &
            {"assumptions", "proof_steps", "counterexamples", "boundaries", "kind", "definition", "statement"})
        conflicts.append({
            "id": id_,
            "candidate_sha256": x["candidate_sha256"], "active_sha256": x["existing_sha256"],
            "candidate_kind": candidate["kind"], "active_kind": old["kind"],
            "mathematical_risk_fields": high_risk,
            "review_hint": REVIEW_HINTS[id_],
            "candidate_assumptions": candidate["assumptions"],
            "active_assumptions": old["assumptions"],
            "candidate_boundaries": candidate["boundaries"],
            "active_boundaries": old["boundaries"],
            "candidate_counterexamples": candidate["counterexamples"],
            "active_counterexamples": old["counterexamples"],
            "decision": "HOLD_BOTH_SOURCE_VERSIONS",
            "evidence_status": "MATH_NOT_INDEPENDENTLY_ADJUDICATED",
        })
    if len(conflicts) != 10 or set(REVIEW_HINTS) != {x["id"] for x in conflicts}:
        raise ValueError("Unexpected Batch02 conflict count or IDs")
    conflict_report = {
        "scope": "PRIORITIZED_HUMAN_EDITORIAL_TRIAGE_NOT_AUTOMATIC_MERGE",
        "summary": {
            "conflict_count": len(conflicts),
            "unresolved_conflicts": len(conflicts),
            "automatically_resolved": 0,
            "conflicts_with_changed_math_risk_fields": sum(bool(c["mathematical_risk_fields"]) for c in conflicts),
        },
        "conflicts": conflicts,
        "warning": "Both originals remain unchanged; subject-specific hints are not verification or teacher approval.",
    }

    bylesson = defaultdict(list)
    for row in evidence:
        bylesson[row["lesson_id"]].append(row["id"])
    proof_rows = []
    for doc in docs:
        data = doc.model_dump(mode="json")
        is_theorem = doc.kind == "theorem"
        obligations = [
            {"index": i + 1, "claim": step["claim"], "reason": step["reason"],
             "status": "NOT_FORMALLY_VERIFIED"}
            for i, step in enumerate(data["proof_steps"])
        ]
        proof_rows.append({
            "id": doc.id, "kind": doc.kind,
            "curriculum_ids": list(doc.curriculum_ids),
            "review_status": doc.review.status,
            "teacher_solution_visibility": doc.teacher_solution_visibility,
            "math_truth_status": "NOT_CERTIFIED",
            "formal_natural_language_proof_verified": False,
            "theorem_assumptions": list(doc.assumptions) if is_theorem else [],
            "proof_step_obligations": obligations,
            "counterexample_count": len(doc.counterexamples),
            "worked_example_count": len(doc.worked_examples),
            "linked_existing_supporting_oracle_ids": sorted(bylesson[doc.id]),
            "oracle_scope": "LIMITED_SUPPORTING_SUBCLAIMS_NOT_WHOLE_PROOF",
            "human_review": "PENDING",
            "needs_editorial_reconciliation": doc.id in REVIEW_HINTS,
        })
    proof_summary = {
        "deep_draft_lessons": len(docs), "theorems": sum(x["kind"] == "theorem" for x in proof_rows),
        "proof_step_obligations_not_formally_verified": sum(len(x["proof_step_obligations"]) for x in proof_rows),
        "existing_supporting_oracles_linked": sum(len(x["linked_existing_supporting_oracle_ids"]) for x in proof_rows),
        "theorems_with_whole_proof_certification": 0,
        "teacher_approved": 0,
        "student_solution_steps_verified": 0,
    }
    if any(x.review.status == "APPROVED" for x in docs):
        raise ValueError("Unexpected teacher approval without independent registry")
    if len({x.id for x in docs}) != len(docs):
        raise ValueError("Duplicate active lesson IDs")
    proof_report = {
        "scope": "HUMAN_PROOF_OBLIGATION_QUEUE_NOT_MATHEMATICAL_CERTIFICATION",
        "summary": proof_summary,
        "lessons": proof_rows,
        "warnings": [
            "Neither complete Pydantic content nor 48 supporting K07 identities proves every theorem.",
            "Even the independent Batch07 exact arithmetic regressions support only explicitly tested examples.",
            "Every lesson remains REVIEW_PENDING until independent signed real human review is available.",
            "These records are editor-only: never send teacher proof text to student or cloud model.",
        ],
    }

    return {
        CROSSWALK_OUT: crosswalk, CONFLICT_OUT: conflict_report, PROOF_OUT: proof_report,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    artifacts = build()
    for path, object_ in artifacts.items():
        expected = json.dumps(object_, indent=2, ensure_ascii=False) + "\n"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Batch07 report drift: {path.relative_to(ROOT)}")
        elif not args.summary:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    for path, obj in artifacts.items():
        print(("CHECKED" if args.check else "SUMMARY" if args.summary else "WROTE"),
              path.relative_to(ROOT), obj["summary"])

if __name__ == "__main__":
    main()
