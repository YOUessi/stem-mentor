#!/usr/bin/env python3
"""Versioned, loss-aware bridge for 26 pre-existing method/strategy cards.

These are NOT newly certified DeepLesson documents. They remain unreviewed and
cannot be automatically promoted to a theorem or teacher-approved content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "knowledge/corpus/methods.json"
TARGET = ROOT / "knowledge/deep/legacy_method_bridge_v1.json"


def build():
    raw = SOURCE.read_bytes()
    methods = json.loads(raw)
    if not isinstance(methods, list):
        raise TypeError("Expected list of existing method cards")
    ids = [x.get("id") for x in methods]
    if None in ids or len(set(ids)) != len(ids):
        raise ValueError("Missing or duplicated legacy source IDs")
    entries = []
    for m in methods:
        src = m.get("source", {})
        if src.get("permission") != "PROJECT_AUTHORED":
            raise ValueError(f"Source is not project authored: {m['id']}")
        if not m.get("boundary") or not m.get("hint"):
            raise ValueError(f"Missing source safety information: {m['id']}")
        entries.append({
            "legacy_id": m["id"], "kind": m["kind"], "title": m["title"],
            "source_version": m["version"], "source_path": "knowledge/corpus/methods.json",
            "requires": list(m.get("requires", [])),
            "structures": list(m.get("structures", [])),
            "prerequisites": list(m.get("prerequisites", [])),
            "boundary": m["boundary"], "hint": m["hint"],
            "source_reference": src.get("reference", ""),
            "content_coverage_status": "NEEDS_DEEP_AUTHORING",
            "expert_review": "PENDING",
            "candidate_deep_links": [],
            "teacher_solution_visibility": "TEACHER_ONLY",
        })
    kinds = Counter(x["kind"] for x in entries)
    return {
        "version": "1.0.0",
        "status": "UNREVIEWED_LEGACY_BRIDGE_ONLY",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_id_count": len(ids),
        "unconverted_ids": sorted(ids),
        "kinds": dict(sorted(kinds.items())),
        "entries": entries,
        "notice": "A bridge is only a loss-aware pointer to old summaries. Each card still "
                  "requires independent full authoring, case review, and verified pedagogy.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=TARGET)
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    text = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if a.check:
        if not a.output.exists() or a.output.read_text(encoding="utf-8") != text:
            raise SystemExit("Legacy bridge artifact drift: rebuild and commit the JSON")
        print("Bridge current:", len(build()["entries"]), "unreviewed legacy cards")
    else:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text, encoding="utf-8")
        print("Wrote", a.output)


if __name__ == "__main__":
    main()
