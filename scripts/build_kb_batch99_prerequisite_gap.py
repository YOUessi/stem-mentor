#!/usr/bin/env python3
"""Explicitly inventory unresolved textual prerequisites in 66 deep teacher drafts.

A natural-language prerequisite is not automatically a trusted, typed graph edge.
Do not auto-link, mark approved, or treat source topics as official syllabus atoms.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"scripts"),str(ROOT/"backend")]
from app.deep_knowledge import DeepLesson
import build_kb_batch99_seven_track_guard as T

OUT = ROOT/"docs/evaluation/KB_BATCH99_PREREQUISITE_GAP.json"
MD = ROOT/"docs/evaluation/KB_BATCH99_PREREQUISITE_GAP.md"

def checked_lesson(payload,known_ids):
    item = DeepLesson.model_validate(payload)
    deps = item.prerequisite_lesson_ids
    if len(set(deps)) != len(deps) or item.id in deps:
        raise ValueError("self or duplicate prerequisite")
    if any(dep not in known_ids for dep in deps):
        raise ValueError("unresolved referenced ID; do not invent graph edge")
    if item.review.status!="REVIEW_PENDING" or item.teacher_solution_visibility!="TEACHER_ONLY":
        raise ValueError("draft authority drift")
    if not item.prerequisites:
        raise ValueError("unresolved teaching prerequisite description")
    return {"lesson_id":item.id, "description_count":len(item.prerequisites),
            "resolved_id_count":len(deps),
            "editorial_status":"TEXT_ONLY_UNRESOLVED" if not deps else "IDS_PRESENT_NOT_TEACHER_APPROVED",
            "prerequisite_descriptions":list(item.prerequisites),
            "prerequisite_lesson_ids":list(deps),
            "teacher_review":"REVIEW_PENDING","student_authoritative":False}

def build():
    track=T.build()
    all_docs={}
    for n in range(94,99):
        path=next((ROOT/"knowledge/deep/v1").glob(f"batch{n}_deep_scope_*.json"))
        for payload in json.loads(path.read_text(encoding="utf8")):
            if payload["id"] in all_docs:raise ValueError("duplicate lesson ID")
            all_docs[payload["id"]]=payload
    if set(all_docs) != {r["lesson_id"] for r in track["lessons"]} or len(all_docs)!=66:
        raise ValueError("tracked lesson registry mismatch")
    rows=[checked_lesson(all_docs[k],all_docs) for k in sorted(all_docs)]
    by_track={r["lesson_id"]:r["source_track"] for r in track["lessons"]}
    for row in rows:row["source_provisional_track"]=by_track[row["lesson_id"]]
    counts=dict(sorted(Counter(x["editorial_status"] for x in rows).items()))
    return {
       "schema_version":"kb99-prerequisite-editorial-gap-v1",
       "scope":"TEXTUAL_PREREQUISITES_NOT_APPROVED_GRAPH_EDGES",
       "total_deep_draft_lessons":len(rows),
       "textual_prerequisite_descriptions":sum(x["description_count"] for x in rows),
       "resolved_prerequisite_id_references":sum(x["resolved_id_count"] for x in rows),
       "status_counts":counts,
       "official_atom_denominators_by_track":track["official_atom_denominators_by_track"],
       "teacher_approved":0,
       "student_authoritative_releases":0,
       "lessons":rows}
def markdown(x):
    out=["# Batch99｜先修图谱未解绑定台账","",
         "以下均为来源锁定深度草案的文本先修要求，不等于已验证的知识图谱边。未经教研审核全部保持 REVIEW_PENDING。","",
         f"讲义 {x['total_deep_draft_lessons']}；先修文字 {x['textual_prerequisite_descriptions']}；"
         f"解析成正式讲义ID的引用 {x['resolved_prerequisite_id_references']}。","",
         "| 讲义 | 来源轨道 | 文本先修数 | 已解析ID数 | 状态 |",
         "|---|---|---:|---:|---|"]
    for row in x["lessons"]:
        out.append(f"| {row['lesson_id']} | {row['source_provisional_track']} | "
                   f"{row['description_count']} | {row['resolved_id_count']} | {row['editorial_status']} |")
    out+=["","正式课标七轨原子分母仍 UNKNOWN。不得把文本条件静默升权为教学Agent可用的正式先修路径。",""]
    return "\n".join(out)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    report=build()
    for path,value in ((OUT,json.dumps(report,sort_keys=True,ensure_ascii=False,indent=2)+"\n"),
                       (MD,markdown(report))):
        if args.check:
            if path.read_text(encoding="utf8")!=value: raise ValueError("prerequisite artifact drift "+str(path))
        else: path.write_text(value,encoding="utf8")
    print("Batch99 prerequisite audit",report["total_deep_draft_lessons"],
          report["textual_prerequisite_descriptions"], "text notes;",
          report["resolved_prerequisite_id_references"],"typed edges; check",args.check)
if __name__=="__main__":main()
