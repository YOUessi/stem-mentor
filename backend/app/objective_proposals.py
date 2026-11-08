"""Safe, draft-only curriculum-objective → lesson proposal review queue.

DO NOT expose this module through a student-facing API: a proposal is not an
independently certified coverage relationship and supplies no student evidence.
"""
from __future__ import annotations
import hashlib
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from .standard_scope import source_inventory
from .deep_knowledge import lessons

PATH=Path(__file__).resolve().parents[2]/"curriculum/highschool_math/objective_lesson_proposals_batch13.json"

def digest(value):
    raw=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def historical_batch13_deep():
    """Explicit frozen Batch21 editorial proposal scope (235), excluding later drafts.

    The new Batch22 index is separately audited and still unavailable to students.
    """
    later_path=PATH.parents[2]/"knowledge/deep/v1/elective_gap_batch22.json"
    later={x["id"] for x in json.loads(later_path.read_text(encoding="utf-8"))}
    later.update(x["id"] for x in json.loads((later_path.parent / "core_elective_batch23.json").read_text(encoding="utf-8")))
    later.update(x["id"] for x in json.loads((later_path.parent / "core_foundation_batch24.json").read_text(encoding="utf-8")))
    full={x.id:x.model_dump(mode="json") for x in lessons()}
    if len(later)!=52 or not later<=set(full) or len(full)-len(later)!=235:
        raise ValueError("Historical review snapshot is not reconcilable with live lessons")
    return {k:v for k,v in full.items() if k not in later}

def validate_proposals(data, original=None, deep=None):
    original=source_inventory() if original is None else original
    deep=historical_batch13_deep() if deep is None else deep
    if data.get("inventory_status")!="EDITORIAL_MATCH_QUEUE_NOT_APPROVED":
        raise ValueError("Proposed curriculum matches cannot be certified")
    if data.get("official_atomic_denominator") is not None or data.get("official_coverage_percent") is not None:
        raise ValueError("Official curriculum denominator or ratio was invented")
    if data.get("independent_teacher_approved_matches")!=0 or data.get("student_published_knowledge_count")!=0:
        raise ValueError("Editorial candidates cannot become student evidence")
    if data.get("base_source_digest_sha256")!=digest(original):
        raise ValueError("Source snapshot changed; regenerate and re-review")
    candidates={x["id"]:x for x in original["items"]}
    if data.get("total_source_objective_candidates")!=len(candidates):
        raise ValueError("Original source cardinality mismatch")
    if data.get("total_deep_draft_lessons")!=len(deep):
        raise ValueError("Deep lesson count drift")
    ids=set()
    by_track={track:Counter() for track in original["summary"]["by_track"]}
    for item in data["items"]:
        key=item["candidate_id"]
        if key in ids or key not in candidates:
            raise ValueError("Duplicated / unknown curriculum candidate")
        ids.add(key)
        cand=candidates[key]
        if item["candidate_track"]!=cand["track"] or item["candidate_source_page"]!=cand["source"]["printed_page"]:
            raise ValueError("Cross-track / page mismatch")
        if item["objective_snapshot_sha256"]!=digest(cand):
            raise ValueError("Tampered candidate learning objective")
        if item["review_state"]!="QUEUED_FOR_HUMAN_REVIEW":
            raise ValueError("Author cannot sign review")
        if not isinstance(item.get("review_questions"),list) or len(item["review_questions"])!=3:
            raise ValueError("Missing editorial audit questions")
        refs=item["proposed_deep_lessons"]
        if item["match_status"]!=("EDITORIAL_PROPOSAL_NOT_VERIFIED" if refs else "NO_PROPOSAL_NOT_A_COVERAGE_DECISION"):
            raise ValueError("Misleading proposal status")
        if len({x["lesson_id"] for x in refs})!=len(refs):
            raise ValueError("Duplicate lesson suggestion per objective")
        for ref in refs:
            lesson=deep.get(ref["lesson_id"])
            if not lesson:
                raise ValueError("Unknown proposed lesson")
            if ref["lesson_snapshot_sha256"]!=digest(lesson):
                raise ValueError("Deep knowledge changed; invalidate editorial link")
            if lesson["review"]["status"]!="REVIEW_PENDING":
                raise ValueError("This queue is only for pending deep drafts")
            if (ref["scope"],ref["source_grounding_review"],ref["math_proof_review"],ref["teacher_review"])!=(
                "TOPIC_OVERLAP_PARTIAL_UNKNOWN","NOT_CHECKED","NOT_CERTIFIED","PENDING"):
                raise ValueError("False claim of curriculum match certification")
        stat=by_track[item["candidate_track"]]
        stat["objective_candidates"]+=1
        stat["has_unreviewed_suggestion"]+=bool(refs)
        stat["without_suggestion"]+=not refs
        stat["suggestion_edges"]+=len(refs)
    if ids!=set(candidates):
        raise ValueError("Missing source candidate(s) from review queue")
    for track,stat in by_track.items():
        stat["independently_approved"]=0
        if data["by_track"].get(track)!=dict(stat):
            raise ValueError("Course track suggestion counts do not reconcile")
    if set(data["by_track"])!=set(by_track):
        raise ValueError("Unrecognized curriculum track")
    if data.get("proposed_objectives")!=sum(x["has_unreviewed_suggestion"] for x in by_track.values()):
        raise ValueError("Proposed objective count mismatch")
    if data.get("proposed_edges")!=sum(x["suggestion_edges"] for x in by_track.values()):
        raise ValueError("Proposed lesson count mismatch")
    if not data.get("warnings") or any(x["proposed_deep_lessons"] and x["review_state"]!="QUEUED_FOR_HUMAN_REVIEW" for x in data["items"]):
        raise ValueError("Editor-only warnings unavailable")
    return data

@lru_cache(maxsize=1)
def editorial_review_queue():
    return validate_proposals(json.loads(PATH.read_text(encoding="utf-8")))

def internal_review_counts():
    data=editorial_review_queue()
    return {k:data[k] for k in (
        "inventory_status","total_source_objective_candidates","total_deep_draft_lessons",
        "proposed_objectives","proposed_edges","by_track",
        "independent_teacher_approved_matches","official_atomic_denominator",
        "official_coverage_percent","student_published_knowledge_count")}
