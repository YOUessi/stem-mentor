#!/usr/bin/env python3
"""Batch26 reproducible editorial graph coverage matrix (not student curriculum)."""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import curriculum
from app.kb_batch26_graph import validate_editorial_graph, MANIFEST
from kb_frozen_batch24 import frozen_batch24_lessons

OUT=ROOT/"docs/evaluation/KB_BATCH26_PREREQUISITE_EDITORIAL_REVIEW.json"
def build():
    docs=frozen_batch24_lessons()
    c={r["id"]:r for r in curriculum()}
    graph=validate_editorial_graph(json.loads(MANIFEST.read_text(encoding="utf-8")),docs=docs)
    no_edges={d.id for d in docs if not d.prerequisite_lesson_ids}
    proposed=set(graph["by_lesson"])
    if not proposed<=no_edges:raise ValueError("Proposal must refer to currently unlinked lesson")
    missing=no_edges-proposed
    associations=Counter()
    items=[]
    for d in sorted(docs,key=lambda d:d.id):
        if d.id not in no_edges:continue
        tracks=sorted({("COMPULSORY" if c[x]["level"]=="必修" else
                       "SELECTIVE_COMPULSORY" if c[x]["level"]=="选择性必修"
                       else c[x].get("elective_track","ELECTIVE_UNASSIGNED")) for x in d.curriculum_ids})
        state="EDITORIAL_CANDIDATE_PENDING" if d.id in proposed else "NO_PROPOSAL_YET"
        for tr in tracks:associations[(tr,state)]+=1
        items.append(dict(id=d.id,tracks=tracks,status=state,
                          prerequisites_currently_linked=0,
                          proposed=[x["knowledge_id"] for x in graph["by_lesson"].get(d.id,[])],
                          teacher_verified=False,student_visible=False))
    matrix={}
    for (tr,state),n in sorted(associations.items()):matrix.setdefault(tr,{})[state]=n
    result=dict(schema_version="kb-batch26-prereq-review-v1",
      scope="EDITORIAL_REVIEW_QUEUE_NOT_STUDENT_READY_PREREQUISITE_GRAPH",
      summary=dict(draft_lessons=len(docs),authoritative_unlinked_lessons=len(no_edges),
        lessons_with_new_editorial_proposals=len(proposed),
        still_without_editorial_proposals=len(missing),
        proposed_edges=graph["candidate_edges"],candidate_merged_graph_acyclic=True,
        approved_edges=0, student_published=0,teacher_approved=0,
        officially_verified_atomic_denominator=None),
      by_track_candidate_associations=matrix,
      items=items,warnings=[
        "31 editorial links are NOT inserted into authoritative DeepLesson.prerequisite_lesson_ids.",
        "Human confirmation and source lesson semantics remain required.",
        "Missing explicit prerequisite edges need not be errors for mathematically foundational root concepts.",
        "Future importer must separately verify teacher signature and recheck all graph cycles."
      ])
    return json.dumps(result,ensure_ascii=False,indent=2)+"\n"
def main():
    a=argparse.ArgumentParser();a.add_argument("--check",action="store_true");args=a.parse_args()
    result=build()
    if args.check:
        if OUT.read_text(encoding="utf-8")!=result:raise SystemExit("Batch26 graph review matrix drift")
    else:OUT.write_text(result,encoding="utf-8")
    s=json.loads(result)["summary"]
    print("PASS",s["proposed_edges"],"editor candidates,",s["still_without_editorial_proposals"],"unlinked without proposal; 0 teacher-approved")
if __name__=="__main__":main()
