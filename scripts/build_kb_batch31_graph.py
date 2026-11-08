#!/usr/bin/env python3
"""30+ math-specific editorial prerequisite proposals, isolated from student graph."""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import lessons
from app.kb_batch26_graph import SCOPE, validate_editorial_graph
SEED=ROOT/"knowledge/deep/prerequisite_editorial_candidates_batch31.tsv"
BASE=ROOT/"knowledge/deep/prerequisite_editorial_candidates_batch26.json"
OUT=ROOT/"docs/evaluation/KB_BATCH31_PREREQUISITE_EDITORIAL_REVIEW.json"

def parse(text):
    rows=[]
    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):continue
        data=raw.split("|")
        if len(data)!=3:raise ValueError("Expected lesson|prerequisite|math rationale")
        a,b,reason=map(str.strip,data)
        if len(reason)<28 or a==b or len(a)<10 or len(b)<10:raise ValueError("Incomplete editor edge")
        rows.append(dict(lesson_id=a,prerequisite_lesson_id=b,rationale=reason,
             teacher_review="PENDING",applied_to_authoritative_lesson_graph=False))
    if len(rows)!=len({(r["lesson_id"],r["prerequisite_lesson_id"]) for r in rows}):
        raise ValueError("Duplicate editorial graph edge")
    return rows

def build(seed=None,base=None,docs=None):
    docs=list(lessons() if docs is None else docs)
    payload=json.loads(BASE.read_text(encoding="utf-8")) if base is None else base
    if payload["scope"]!=SCOPE or len(payload["items"])!=31:raise ValueError("Old approved-unsafe editorial payload changed")
    new=parse(SEED.read_text(encoding="utf-8") if seed is None else seed)
    merged={**payload,"items":[*payload["items"],*new]}
    result=validate_editorial_graph(merged,docs)
    existing_unlinked={d.id for d in docs if not d.prerequisite_lesson_ids}
    all_proposed=set(result["by_lesson"])
    if len(all_proposed)!=len(payload["items"])+len(new) or len(all_proposed-existing_unlinked):
        raise ValueError("New graph must concern distinct previously unlinked lessons")
    if result["teacher_approved_edges"]!=0 or result["student_graph_changed"] is not False:
        raise ValueError("Illegally changed authoritative graph")
    summary=dict(total_draft_lessons=len(docs),missing_authoritative_graph_edges=len(existing_unlinked),
      preexisting_editorial_proposals=len(payload["items"]),new_editorial_proposals=len(new),
      editorial_proposals_total=len(all_proposed),
      still_no_editorial_candidate=len(existing_unlinked-all_proposed),
      combined_candidate_graph_acyclic=True,
      teacher_approved_proposals=0,authoritative_graph_modified=False,
      student_visible_proposals=0,official_atomic_denominator=None)
    return json.dumps(dict(schema_version="kb-batch31-prerequisite-expansion-v1",
       scope="LOCAL_EDITORIAL_PREREQUISITES_ONLY_NO_AGENT_EXPOSURE",
       summary=summary,
       new_proposals=new,
       combined_proposals_by_lesson=result["by_lesson"],
       reviewed_lesson_ids=[],
       warnings=["An editor's proposed prerequisite is NOT an authoritative graph edge or teacher-approved fact.",
                 "Foundational concept roots may appropriately have no prerequisites; absence does not prove a defect.",
                 "Proposal selection requires teacher review and graph-cycle revalidation before application."]),
       ensure_ascii=False,indent=2)+"\n"

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");args=p.parse_args()
    text=build()
    if args.check:
        if OUT.read_text(encoding="utf-8")!=text:raise SystemExit("Batch31 prerequisite graph review drift")
    else:OUT.write_text(text,encoding="utf-8")
    print("PASS graph",json.loads(text)["summary"])
if __name__=="__main__":main()
