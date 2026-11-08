"""Offline editorial prerequisite candidates (NOT an approved learning graph).

Rows are authored relationship hypotheses for teacher review. They do not change
knowledge/deep/v1 source lessons and never enter student API prompts.
"""
from __future__ import annotations
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from .deep_knowledge import lessons

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "knowledge/deep/prerequisite_editorial_candidates_batch26.json"
SCOPE = "EDITORIAL_CANDIDATES_NOT_TEACHER_REVIEWED_NOT_STUDENT_PUBLISHED"


class EditorGraphError(ValueError):
    pass


def validate_editorial_graph(payload: dict, docs=None) -> dict:
    docs = list(docs if docs is not None else lessons())
    lookup = {d.id: d for d in docs}
    if len(lookup)!=len(docs):
        raise EditorGraphError("Duplicate lesson IDs")
    if (payload.get("scope")!=SCOPE or
        payload.get("prerequisite_proposal_status")!="EDITORIAL_REVIEW_PENDING" or
        payload.get("teacher_signature") is not None or
        payload.get("mathematically_certified") is not False or
        payload.get("student_publishable") is not False):
        raise EditorGraphError("Unapproved links cannot assert authority")
    edges = {d.id:set(d.prerequisite_lesson_ids) for d in docs}
    seen=set()
    by_lesson=defaultdict(list)
    for r in payload.get("items",[]):
        a,b=r["lesson_id"],r["prerequisite_lesson_id"]
        if (a,b) in seen or a not in lookup or b not in lookup or a==b:
            raise EditorGraphError("Duplicate/orphan/self prerequisite")
        if b in edges[a]:
            raise EditorGraphError("Proposal already exists in authoritative graph")
        if (r.get("teacher_review")!="PENDING" or
            r.get("applied_to_authoritative_lesson_graph") is not False or
            not isinstance(r.get("rationale"),str) or len(r["rationale"])<20):
            raise EditorGraphError("Missing written rationale or fabricated review")
        # Must stay an editorial addition to an unlinked lesson.
        if lookup[a].prerequisite_lesson_ids:
            raise EditorGraphError("Existing graph edge requires a separate editor reconciliation")
        seen.add((a,b))
        edges[a].add(b)
        by_lesson[a].append({"knowledge_id":b, "title":lookup[b].title,
                             "rationale":r["rationale"],"status":"EDITORIAL_REVIEW_PENDING"})
    if not seen:
        raise EditorGraphError("Empty proposal batch")
    visiting,visited=set(),set()
    def walk(k):
        if k in visiting: raise EditorGraphError("Combined graph cycle")
        if k in visited: return
        visiting.add(k)
        for p in edges[k]:walk(p)
        visiting.remove(k);visited.add(k)
    for k in lookup:walk(k)
    return {"candidate_edges":len(seen), "lessons_with_candidate_edges":len(by_lesson),
            "missing_explicit_edges_in_authoritative_graph":sum(not x.prerequisite_lesson_ids for x in docs),
            "combined_candidate_graph_acyclic":True,
            "teacher_approved_edges":0,
            "student_graph_changed":False,
            "by_lesson":dict(sorted(by_lesson.items()))}


@lru_cache(maxsize=1)
def proposed_graph():
    return validate_editorial_graph(json.loads(MANIFEST.read_text(encoding="utf-8")))


def editor_prerequisite_proposals(knowledge_id: str, *, scope: str="") -> dict:
    # The scope check is accidental-misuse protection, NOT real authentication.
    # This must never be registered as an HTTP route or added to student prompts.
    if scope!="EDITOR_LOCAL":
        raise PermissionError("Prerequisite proposals require local editorial mode")
    docs={d.id for d in lessons()}
    if knowledge_id not in docs:raise KeyError("Unknown lesson")
    x=proposed_graph()
    return {"lesson_id":knowledge_id, "status":"EDITORIAL_REVIEW_PENDING",
            "teacher_signed":False,"student_publishable":False,
            "proposals":x["by_lesson"].get(knowledge_id,[])}
