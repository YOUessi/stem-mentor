#!/usr/bin/env python3
"""Conservative project-topic semantic coverage and review-gap inventory.

A linked deep lesson is NOT by itself a full treatment of that engineering
topic, which itself is NOT an official atomic syllabus entry. This audit
never grants pedagogical approval or mathematical-proof certification.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.deep_knowledge import coverage_report, curriculum, lessons

GAPS = ROOT / "knowledge/deep/semantic_gaps_batch04.json"
DEFAULT_OUT = ROOT / "docs/evaluation/KB_SEMANTIC_COVERAGE_BATCH05.json"


def validate_gaps(raw, known_ids):
    if raw.get("scope") != "PROJECT_ENGINEERING_IDS_NOT_OFFICIAL_ATOMIC_SYLLABUS":
        raise ValueError("coverage denominator must not be misrepresented as official")
    if raw.get("review_status") != "PROJECT_EDITORIAL_CANDIDATES_NOT_TEACHER_CERTIFIED":
        raise ValueError("editorial gap flags cannot be passed off as teacher certification")
    ids = [row["curriculum_id"] for row in raw["gaps"]]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("missing or duplicated editorial gap IDs")
    if set(ids) - known_ids:
        raise ValueError("editorial gaps include unknown engineering topics")
    for row in raw["gaps"]:
        if row["status"] != "OPEN" or row["confidence"] != "PRELIMINARY_EDITORIAL_FLAG":
            raise ValueError("editorial gap cannot close without documented independent review")
        if len(row["missing_content"]) < 16 or not row["recommended_lesson_id"].startswith("math.hs."):
            raise ValueError("an editorial gap needs a concrete missing subskill and suggested lesson")
    return {g["curriculum_id"]:g for g in raw["gaps"]}


def build():
    all_rows = curriculum()
    records = lessons()
    links = defaultdict(list)
    for item in records:
        for topic_id in item.curriculum_ids:
            links[topic_id].append(item)
    raw = json.loads(GAPS.read_text(encoding="utf-8"))
    gaps = validate_gaps(raw, {r["id"] for r in all_rows})
    output_rows = []
    for row in all_rows:
        topic_id = row["id"]
        docs = links.get(topic_id, ())
        candidate_present = (topic_id in gaps and
                             gaps[topic_id]["recommended_lesson_id"] in {d.id for d in docs})
        if topic_id in gaps:
            state = "GAP_DRAFT_CANDIDATE_UNREVIEWED" if candidate_present else "KNOWN_PARTIAL_UNREVIEWED"
        elif docs:
            state = "LINKED_UNREVIEWED_NOT_CERTIFIED_COMPLETE"
        else:
            state = "NO_DEEP_CONTENT"
        output_rows.append({
            "engineering_topic_id":topic_id,
            "level":row["level"],
            "unit":row["unit"],
            "concept":row["concept"],
            "deep_lesson_ids":[d.id for d in docs],
            "teacher_approved_lesson_ids":[d.id for d in docs if d.review.status=="APPROVED"],
            "evidence_status":state,
            "explicit_missing_subskill":gaps[topic_id]["missing_content"] if topic_id in gaps else None,
            "recommended_next_lesson":gaps[topic_id]["recommended_lesson_id"] if topic_id in gaps else None,
            "gap_candidate_draft_present":candidate_present,
            "gap_review_status":"OPEN" if topic_id in gaps else None,
            "curriculum_atom_officially_verified":False
        })
    status=Counter(row["evidence_status"] for row in output_rows)
    by_level={}
    for level in ("必修","选择性必修","选修拓展"):
        select=[x for x in output_rows if x["level"]==level]
        by_level[level]={
            "engineering_topics":len(select),
            "with_any_draft_link":sum(bool(x["deep_lesson_ids"]) for x in select),
            "known_partial_topics":sum(x["gap_review_status"]=="OPEN" for x in select),
            "gap_draft_candidates":sum(x["gap_candidate_draft_present"] for x in select),
            "gap_without_candidate":sum(x["evidence_status"]=="KNOWN_PARTIAL_UNREVIEWED" for x in select),
            "teacher_reviewed_complete":0
        }
    old=coverage_report()
    if sum(v["engineering_topics"] for v in by_level.values()) != old["curriculum_topic_total"]:
        raise ValueError("denominator drift against the published engineering map")
    if len(records)!=old["deep_lesson_documents"]:
        raise ValueError("deep document count drift")
    # Deliberately never infer that a non-flagged topic is fully taught or safe.
    return {
        "scope":"CONSERVATIVE_PROJECT_ENGINEERING_MAP_ONLY",
        "unverified_official_syllabus_coverage": True,
        "generated_from":"curriculum/highschool_math/curriculum_map.json + knowledge/deep/v1/*.json + semantic_gaps_batch04.json",
        "summary":{
            "engineering_topic_denominator":len(output_rows),
            "deep_draft_documents":len(records),
            "linked_project_topics":sum(bool(x["deep_lesson_ids"]) for x in output_rows),
            "known_partial_topic_count":len(gaps),
            "gap_draft_candidate_count":status["GAP_DRAFT_CANDIDATE_UNREVIEWED"],
            "gap_without_candidate_count":status["KNOWN_PARTIAL_UNREVIEWED"],
            "other_linked_unreviewed_topic_count":status["LINKED_UNREVIEWED_NOT_CERTIFIED_COMPLETE"],
            "teacher_reviewed_complete":0,
            "fully_formally_proven_natural_language_lessons":0,
            "official_curriculum_atom_mapping_reviewed":0,
            "explicit_official_elective_tracks_completed":0,
            "student_draft_release_allowed":False,
            "per_level":by_level
        },
        "warnings":[
            "113 engineering IDs are NOT an official atomic syllabus denominator.",
            "113 linked draft topics do not mean 113 fully taught or mathematically proved topics.",
            "23 editorial gaps remain OPEN pending independent review even after draft candidates are added; other linked topics remain unreviewed.",
            "Review_PENDING drafts, teacher worked solutions, and their text are never approved student evidence.",
            "The 7 legacy extension topics do not constitute completion of official electives A–E."
        ],
        "topics":output_rows
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--summary",action="store_true")
    args=parser.parse_args()
    result=build()
    target=args.output or DEFAULT_OUT
    canonical=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8")!=canonical:
            print("FAIL: semantic coverage snapshot missing or out of date",file=sys.stderr)
            sys.exit(1)
        print("PASS: semantic coverage snapshot matches project drafts and 23 open, non-approved gaps")
    elif args.output:
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(canonical,encoding="utf-8")
        print("WROTE",target)
    elif args.summary:
        print(json.dumps(result["summary"],ensure_ascii=False,indent=2))
    else:
        print(canonical)


if __name__=="__main__":
    main()
