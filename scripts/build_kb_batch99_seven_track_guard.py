#!/usr/bin/env python3
"""Audit all 66 Batch94-98 deep drafts against the seven engineering tracks.

The source and engineering curriculum are provisional editor mappings, NOT official atoms.
Unknown elective subtracks are unresolved, never silently reported as exact matches.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "backend")]
from app.deep_knowledge import DeepLesson, curriculum
import build_kb_batch93_candidate_triage as B93
import build_kb_batch99_scope_matrix as B99

OUT = ROOT / "docs/evaluation/KB_BATCH99_SEVEN_TRACK_AUDIT.json"
MD = ROOT / "docs/evaluation/KB_BATCH99_SEVEN_TRACK_AUDIT.md"
TRACKS = tuple(B93.TRACKS)
BATCHES = range(94, 99)

def ensure(ok, why):
    if not ok:
        raise ValueError(why)

def map_engineering_track(engineering):
    """Declare only explicit A-E unit labels; generic electives remain unresolved."""
    level = engineering["level"]
    if level == "必修":
        return "COMPULSORY"
    if level == "选择性必修":
        return "SELECTIVE_COMPULSORY"
    ensure(level == "选修拓展", f"invalid curriculum engineering level {level}")
    m = re.fullmatch(r"选修([ABCDE])课程深度内容", engineering["unit"])
    return f"ELECTIVE_{m.group(1)}" if m else None

def classify(source_track, mapped):
    ensure(source_track in TRACKS, f"unknown source track {source_track}")
    if mapped is None:
        return "TRACK_UNRESOLVED"
    return "MATCH_EDITORIAL_ONLY" if source_track == mapped else "CROSS_TRACK_EDITORIAL_ONLY"

def build():
    b99, scopes = B99.build()
    ensure(len(scopes) == 32 and b99["official_atom_denominator"] is None and
           b99["teacher_approved"] == 0, "Batch99 curriculum authority drift")
    known = {x["id"]: x for x in curriculum()}
    source = {x["candidate_id"]: x for x in B93.read(B93.SOURCES)["provisional_candidate_backlog"]}
    rows, seen = [], set()
    for batch in BATCHES:
        audit = ROOT / f"docs/evaluation/KB_BATCH{batch}_SOURCE_LESSON_MATRIX.json"
        pack = next((ROOT / "knowledge/deep/v1").glob(f"batch{batch}_deep_scope_*.json"))
        records = json.loads(audit.read_text(encoding="utf8"))["canonical_lesson_source_links"]
        documents = {x["id"]: x for x in json.loads(pack.read_text(encoding="utf8"))}
        ensure(len(records) == len(documents), "lesson/lineage missing")
        for link in records:
            lesson_id, key = link["lesson_id"], link["source_candidate_id"]
            ensure(key in source and key not in seen, "duplicate or alien source anchor")
            seen.add(key)
            src = source[key]
            doc = DeepLesson.model_validate(documents[lesson_id])
            ensure(link["source_track"] == src["track"] and
                   link["source_line_sha256"] == src["source_line_sha256"] and
                   doc.review.status == "REVIEW_PENDING" and
                   doc.teacher_solution_visibility == "TEACHER_ONLY" and
                   link["student_publishable"] is False and
                   link["official_atom_id"] is None and
                   link["teacher_approved"] is False, "lesson source / authority mismatch")
            mapping = known[link["engineering_curriculum_id"]]
            ensure(link["engineering_level"] == mapping["level"], "engineering level drift")
            inferred = map_engineering_track(mapping)
            status = classify(src["track"], inferred)
            rows.append({
                "lesson_id": lesson_id,
                "source_candidate_id": key,
                "source_track": src["track"],
                "engineering_id": mapping["id"],
                "engineering_level": mapping["level"],
                "engineering_unit": mapping["unit"],
                "declared_engineering_track": inferred,
                "classification": status,
                "legacy_cross_track_flag": link["cross_track_mapping_editorial_only"],
                "legacy_false_negative": status == "CROSS_TRACK_EDITORIAL_ONLY" and
                                         not link["cross_track_mapping_editorial_only"],
                "source_line_sha256": src["source_line_sha256"],
                "teacher_review_status": "REVIEW_PENDING",
                "official_atom_id": None,
                "student_authoritative_index_eligible": False
            })
    ensure(len(rows) == 66, "expected all 66 Batch94-98 deep lessons")
    counts = dict(sorted(Counter(x["classification"] for x in rows).items()))
    unresolved = [x for x in rows if x["classification"] == "TRACK_UNRESOLVED"]
    mismatches = [x for x in rows if x["classification"] == "CROSS_TRACK_EDITORIAL_ONLY"]
    false_negatives = [x for x in rows if x["legacy_false_negative"]]
    return {
        "schema_version": "kb99-seven-track-engineering-editorial-v1",
        "scope": "PROJECT_PROVISIONAL_TRACKS_NOT_OFFICIAL_CURRICULUM_ATOMS",
        "source_snapshot_sha256": B93.FROZEN_BATCH89_CANDIDATES_SHA256,
        "batch99_matrix_sha256": sha256(B99.OUTPUT.read_bytes()).hexdigest(),
        "total_deep_drafts_audited": len(rows),
        "classification_counts": counts,
        "unresolved_engineering_subtrack": len(unresolved),
        "cross_track_editorial_only": len(mismatches),
        "legacy_missed_cross_track": len(false_negatives),
        "unresolved_lesson_ids": [x["lesson_id"] for x in unresolved],
        "mismatched_lesson_ids": [x["lesson_id"] for x in mismatches],
        "legacy_missed_lesson_ids": [x["lesson_id"] for x in false_negatives],
        "by_source_track": {t: dict(sorted(Counter(x["classification"] for x in rows
                                     if x["source_track"] == t).items())) for t in TRACKS},
        "official_atom_denominators_by_track": {t: None for t in TRACKS},
        "teacher_approved": 0,
        "student_authoritative_releases": 0,
        "lessons": rows
    }

def markdown(x):
    out = ["# Batch99 七轨工程归属交叉审计", "",
           "**非官方课程映射，未获教师审核，不得据此宣称正式课程原子完成。**", "",
           "| 类别 | 深度草案数 |", "|---|---:|"]
    out += [f"| {k} | {v} |" for k,v in x["classification_counts"].items()]
    out += ["", f"旧版标志漏报的跨轨：**{x['legacy_missed_cross_track']}**；"
            f"选修工程子轨道未知：**{x['unresolved_engineering_subtrack']}**。", "",
            "| 讲义ID | 来源轨道 | 工程轨道 | 状态 |",
            "|---|---|---|---|"]
    for row in x["lessons"]:
        out += [f"| {row['lesson_id']} | {row['source_track']} | "
                f"{row['declared_engineering_track'] or 'UNKNOWN'} | {row['classification']} |"]
    out += ["", "七轨正式原子分母均 UNKNOWN，所有记录保持 REVIEW_PENDING。", ""]
    return "\n".join(out)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    x = build()
    for path,body in ((OUT,json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n"),
                      (MD,markdown(x))):
        if args.check:
            ensure(path.read_text(encoding="utf8") == body, "artifact drift " + str(path))
        else:
            path.write_text(body, encoding="utf8")
    print("BATCH99 seven track",x["total_deep_drafts_audited"],
          x["classification_counts"],"legacy_missed",x["legacy_missed_cross_track"],
          "check",args.check)

if __name__ == "__main__":
    main()
