#!/usr/bin/env python3
"""Read-only mapping for the *engineering* curriculum, not syllabus certification."""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.deep_knowledge import coverage_report, lessons, curriculum


def build():
    official = json.loads((ROOT / "curriculum/highschool_math/official_scope_v1.json").read_text())
    deep = coverage_report()
    mapped = defaultdict(list)
    for item in lessons():
        for key in item.curriculum_ids:
            mapped[key].append({"id": item.id, "review": item.review.status, "kind": item.kind})
    rows = []
    for topic in curriculum():
        tr = official["legacy_level_normalization"][topic["level"]]
        th = official["legacy_theme_normalization"].get(topic["theme"], topic["theme"])
        tracks = next((x for x in official["tracks"] if x["id"] == tr), None)
        # Batch17 introduced project-authored editorial candidates in *all*
        # legacy levels. Their deliberately unverified theme is NOT an official
        # curriculum theme. Retain them as pending instead of silently making
        # a fabricated official scope match (or crashing CI).
        is_editorial_candidate = topic["theme"] == "高中数学课标样本候选（未经教研认证）"
        if is_editorial_candidate:
            source = topic.get("source") or {}
            if (source.get("mapping_type") != "ENGINEERING_INTERPRETATION"
                    or source.get("teacher_review") != "PENDING"
                    or not topic.get("editorial_objective_id")
                    or topic.get("status") != "PLANNED"):
                raise ValueError(f"untrusted editorial curriculum candidate: {topic['id']}")
            th = "UNVERIFIED_EDITORIAL_CANDIDATE"
        elif tr != "ELECTIVE_UNASSIGNED" and (not tracks or th not in tracks["themes"]):
            raise ValueError(f"unknown legacy level/theme: {topic['id']}")
        rows.append({
            "curriculum_id": topic["id"],
            "engineering_concept": topic["concept"],
            "engineering_unit": topic["unit"],
            "official_track_candidate": tr,
            "theme_high_level_match": th,
            "editorial_theme_uncertified": is_editorial_candidate,
            "existing_tool_status": topic["status"],
            "deep_docs": mapped[topic["id"]],
            "teacher_review": topic.get("source",{}).get("teacher_review", "MISSING"),
            "official_atom_mapping_review": "PENDING",
            "not_officially_verified_atom": True,
        })
    totals = {
        "legacy_engineering_topics": len(rows),
        "per_track": {k:sum(r["official_track_candidate"]==k for r in rows)
                      for k in (*[t["id"] for t in official["tracks"]], "ELECTIVE_UNASSIGNED")},
        "engineering_topic_levels": dict(Counter(x["level"] for x in curriculum())),
        "unassigned_elective_atoms": [x["curriculum_id"] for x in rows
            if x["official_track_candidate"] == "ELECTIVE_UNASSIGNED"],
        "official_explicit_elective_tracks_with_atom_mapping": 0,
        "official_elective_track_count": 5,
        "unreviewed_legacy_atoms": sum(x["official_atom_mapping_review"]=="PENDING" for x in rows),
        "deep_knowledge": deep,
    }
    assert len({r["curriculum_id"] for r in rows}) == len(rows)
    assert sum(totals["per_track"].values()) == len(rows)
    return {
        "warning": "NOT THE OFFICIAL ATOMIC SYLLABUS; HUMAN MAPPING REVIEW REQUIRED",
        "source": {"document":official["basis"],"url":official["url"],"status":official["status"]},
        "totals": totals, "curriculum": rows, "official_tracks": official["tracks"]
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=None, help="Write generated JSON for CI/review")
    parser.add_argument("--summary",action="store_true",help="Only high-level counts")
    a = parser.parse_args()
    result = build()
    obj = result["totals"] if a.summary else result
    text = json.dumps(obj, ensure_ascii=False, indent=2)
    if a.output:
        Path(a.output).write_text(text+"\n",encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
