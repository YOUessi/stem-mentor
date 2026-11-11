#!/usr/bin/env python3
"""Batch99 source-locked editorial triage of the last 32 provisional labels.

Editorial scope review is NOT full official curriculum atomization or teacher certification.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "backend")]
import build_kb_batch93_candidate_triage as B93
import build_kb_batch98_scope_matrix as B98
from kb_batch99_scope_authoring import ROWS

OUTPUT = ROOT / "docs/evaluation/KB_BATCH99_300_PROVISIONAL_STATUS.json"
SCOPES = ROOT / "docs/evaluation/KB_BATCH99_32_SCOPE_INTERPRETATIONS.json"
MARKDOWN = ROOT / "docs/evaluation/KB_BATCH99_300_PROVISIONAL_STATUS.md"
REQUIRED = {"anchor", "scope", "assumptions", "positive", "nonexample", "relation"}

def require(test, message):
    if not test:
        raise ValueError(message)

def stable(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"

def build(rows=None, previous=None):
    rows = ROWS if rows is None else rows
    previous = B98.build()[0] if previous is None else previous
    source_rows = B93.read(B93.SOURCES)["provisional_candidate_backlog"]
    require(len(source_rows) == 300 and
            B93.candidate_snapshot_sha256(source_rows) == B93.FROZEN_BATCH89_CANDIDATES_SHA256,
            "original source snapshot changed")
    sources = {r["candidate_id"]: r for r in source_rows}
    require(len(sources) == 300, "source candidate ids are not unique")
    prev = previous["candidates"]
    require(len(prev) == len({v["candidate_id"] for v in prev}) == 300,
            "previous-stage registry invalid")
    require(previous["stage_counts"] == {
        "PAIR_COMPARISON_NOT_ATOMIZED": 166,
        "INDIVIDUAL_SCOPE_NOT_ATOMIZED": 24,
        "INDIVIDUAL_SCOPE_EDITORIAL_PENDING": 12,
        "NO_INDIVIDUAL_EDITORIAL": 32,
        "FULL_DEEP_DRAFT_PENDING_TEACHER": 66,
    } and previous["teacher_approved"] == 0 and
            previous["official_atom_denominator"] is None and
            all(x is None for x in previous["official_atom_denominators_by_track"].values()),
            "prior 300-item denominator / authority drift")
    needed = {v["candidate_id"] for v in prev
              if v["editorial_stage"] == "NO_INDIVIDUAL_EDITORIAL"}
    require(type(rows) is list and len(rows) == len(needed) == 32,
            "exactly 32 remaining editorial interpretations required")
    authored = {}
    for r in rows:
        require(type(r) is dict and set(r) == REQUIRED,
                "strict editor scope schema expected")
        key = r["anchor"]
        require(type(key) is str and key in needed and key not in authored,
                "only distinct remaining source labels can be interpreted")
        require(all(type(r[f]) is str and len(r[f].strip()) >= 28
                    for f in REQUIRED - {"anchor"}),
                "mathematical scope/assumption/positive/nonexample/relation missing")
        src = sources[key]
        require(src["review_status"] == "REVIEW_PENDING"
                and src["teacher_approval"] is None
                and src["official_math_atom_id"] is None
                and src["student_authoritative_index_eligible"] is False,
                "source authority was elevated")
        authored[key] = {
            **r,
            "source_track": src["track"],
            "source_review_id": src["source_review_id"],
            "source_page": src["source_page"],
            "source_line_sha256": src["source_line_sha256"],
            "source_snapshot_sha256": B93.FROZEN_BATCH89_CANDIDATES_SHA256,
            "status": "INDIVIDUAL_SCOPE_EDITORIAL_PENDING",
            "teacher_review_status": "REVIEW_PENDING",
            "teacher_approval": None,
            "official_atom_id": None,
            "student_publishable": False,
            "mathematically_universally_certified": False,
        }
    require(set(authored) == needed, "not all 32 remaining sources independently interpreted")
    updated = []
    for old in prev:
        r = dict(old)
        key = r["candidate_id"]
        require(key in sources and r["source_line_sha256"] == sources[key]["source_line_sha256"]
                and r["teacher_approval"] is None
                and r["official_atom_id"] is None
                and r["student_authoritative_index_eligible"] is False,
                "provenance / authority drift in inherited record")
        if key in authored:
            r["editorial_stage"] = "INDIVIDUAL_SCOPE_EDITORIAL_PENDING"
            r["batch99_editorial_scope_id"] = key
        updated.append(r)
    counts = Counter(r["editorial_stage"] for r in updated)
    expected = {
        "PAIR_COMPARISON_NOT_ATOMIZED": 166,
        "INDIVIDUAL_SCOPE_NOT_ATOMIZED": 24,
        "INDIVIDUAL_SCOPE_EDITORIAL_PENDING": 44,
        "FULL_DEEP_DRAFT_PENDING_TEACHER": 66,
    }
    require(dict(counts) == expected and sum(counts.values()) == 300,
            "candidate-stage loss, double counting, or premature certification")
    tracks = {
        track: {
            "provisional_source_labels": sum(r["track"] == track for r in updated),
            "stages": dict(sorted(Counter(r["editorial_stage"] for r in updated
                                          if r["track"] == track).items())),
            "official_curriculum_atom_denominator": None,
            "teacher_approved": 0,
        } for track in B93.TRACKS
    }
    require(sum(v["provisional_source_labels"] for v in tracks.values()) == 300,
            "track disaggregation does not conserve 300 provisional labels")
    report = {
        "schema_version": "kb99-32-provisional-editorial-audit-v1",
        "source_scope": "PROJECT_PROVISIONAL_LABELS_NOT_OFFICIAL_SYLLABUS_ATOMS",
        "source_sha256": sha256(B93.SOURCES.read_bytes()).hexdigest(),
        "prior_report_sha256": sha256(B98.OUTPUT.read_bytes()).hexdigest(),
        "authoring_sha256": sha256((ROOT / "scripts/kb_batch99_scope_authoring.py").read_bytes()).hexdigest(),
        "provisional_source_labels": 300,
        "source_page_line_anchors": 428,
        "batch99_editorial_scope_interpretations": 32,
        "remaining_without_individual_editorial": 0,
        "remaining_without_pairwise_semantic_comparison": 134,
        "completed_full_depth_drafts_pending_teacher": 66,
        "stage_counts": dict(sorted(counts.items())),
        "track_matrix": tracks,
        "official_atom_denominator": None,
        "official_atom_denominators_by_track": {t: None for t in B93.TRACKS},
        "fully_human_atomized_source_pages": "0/61",
        "teacher_approved": 0,
        "student_authoritative_releases": 0,
        "historical_uncertified_proof_steps": 538,
        "historical_P0_without_teacher_cards": 106,
        "unresolved_mathematical_conflicts": 10,
        "editorial_scopes_are_official_atoms": False,
        "candidates": updated,
    }
    return report, [authored[r["anchor"]] for r in rows]

def markdown(report, scopes):
    lines = [
        "# Batch99｜32项剩余临时主题范围草案与300行机器可审计状态",
        "",
        "**非官方分母。** 32项为原有临时标签的编辑解释，不是完整讲义、教师批准或官方知识原子。",
        "**课程缺口仍存在：** 正式七轨分母全部 UNKNOWN；原始61页完整教师原子化 0/61；",
        "134个临时主题尚未成对语义辨析，166个已比较但仍未完成正式原子化。",
        "",
        "| 编辑阶段 | 临时主题 |", "|---|---:|",
    ]
    lines += [f"| {key} | {value} |" for key, value in report["stage_counts"].items()]
    lines += ["", "| 轨道 | 临时主题数 | 官方原子总数 |",
              "|---|---:|---|"]
    lines += [f"| {key} | {value['provisional_source_labels']} | UNKNOWN |"
              for key, value in report["track_matrix"].items()]
    for r in scopes:
        lines += [
            "", "## " + r["anchor"] + "｜" + r["source_track"], "",
            "来源页："+str(r["source_page"])+"；源行SHA256："+r["source_line_sha256"], "",
            "**数学范围：** " + r["scope"], "",
            "**成立前提：** " + r["assumptions"], "",
            "**合法实例：** " + r["positive"], "",
            "**反例 / 不适用：** " + r["nonexample"], "",
            "**相邻概念：** " + r["relation"], "",
        ]
    lines += ["**审核：** REVIEW_PENDING；全体均无正式教师审核；不可向学生作为权威知识发布。", ""]
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report, scopes = build()
    for p, content in {
        OUTPUT: stable(report), SCOPES: stable(scopes),
        MARKDOWN: markdown(report, scopes)
    }.items():
        if args.check:
            require(p.exists() and p.read_text(encoding="utf8") == content,
                    "source audit artifact drift: " + str(p))
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf8")
    print("BATCH99 source-locked", len(scopes), "scope interpretations,",
          report["remaining_without_individual_editorial"], "remaining; check:", args.check)

if __name__ == "__main__":
    main()
