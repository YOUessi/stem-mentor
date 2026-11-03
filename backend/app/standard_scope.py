"""Project-authored curriculum checklist, not a source of approved teaching evidence."""
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "curriculum/highschool_math/source_anchored_skill_candidates_batch12.json"
TRACK_PAGES = {"COMPULSORY":(13,35),"SELECTIVE_COMPULSORY":(36,50),
               "ELECTIVE_A":(51,57),"ELECTIVE_B":(58,63),
               "ELECTIVE_C":(64,68),"ELECTIVE_D":(69,72),"ELECTIVE_E":(73,73)}

def validate_source_inventory(data):
    if data.get("status") != "SOURCE_ANCHORED_EDITORIAL_SAMPLE_REVIEW_PENDING":
        raise ValueError("Invalid source inventory status")
    if data.get("is_complete_official_atomic_inventory") is not False:
        raise ValueError("Editorial sample cannot claim complete official coverage")
    if data.get("verified_official_atomic_denominator") is not None:
        raise ValueError("Unknown official denominator must remain null")
    if not data.get("source_url","").startswith("https://"):
        raise ValueError("Missing standard source")
    ids=set()
    by_track=Counter()
    for row in data["items"]:
        key=row["id"]
        if key in ids or row["track"] not in TRACK_PAGES:
            raise ValueError("Duplicate ID or invalid track")
        ids.add(key)
        track=row["track"]
        if not key.startswith("HS-STD2020-"+track+"-"):
            raise ValueError("Source atom ID/track mismatch")
        source=row["source"]
        page=source["printed_page"]
        if type(page) is not int or not TRACK_PAGES[track][0] <= page <= TRACK_PAGES[track][1]:
            raise ValueError("Page outside section of official standard")
        if source["url"]!=data["source_url"] or source["passage_review"]!="SOURCE_SECTION_LOCATED_NOT_TEACHER_SIGNED":
            raise ValueError("Unverified source location")
        if row["teacher_review"]!="PENDING" or row["verified_official_atom_id"] is not None:
            raise ValueError("Unreviewed curriculum falsely certified")
        if row["linked_deep_lesson_ids"]!=[]:
            raise ValueError("Provisional candidate cannot release student knowledge")
        if row["content_status"]!="CURRICULUM_CANDIDATE_NOT_DEEP_LESSON":
            raise ValueError("Editorial objective cannot be labeled complete")
        if not row["section"] or not row["editorial_learning_objective"]:
            raise ValueError("Empty course unit or learning objective")
        by_track[track]+=1
    summary=data["summary"]
    if summary["candidate_learning_objectives"]!=len(ids):
        raise ValueError("Count mismatch")
    if summary["by_track"]!={track:by_track[track] for track in TRACK_PAGES}:
        raise ValueError("Track count mismatch")
    if summary["teacher_approved"]!=0 or summary["active_deep_lesson_links"]!=0:
        raise ValueError("Provisional curriculum cannot assert approvals")
    if summary["remaining_official_coverage_unknown"] is not True:
        raise ValueError("Cannot claim missing content is zero")
    return data

@lru_cache(maxsize=1)
def source_inventory():
    return validate_source_inventory(json.loads(SOURCE.read_text(encoding="utf-8")))

def public_progress():
    from .official_clause_audit import page_progress
    from .k00_gap_audit import gap_tickets
    inventory=source_inventory()
    return {
        "scope":"SOURCE_ANCHORED_EDITORIAL_SAMPLE_NOT_FULL_COURSE",
        "candidate_learning_objectives":inventory["summary"]["candidate_learning_objectives"],
        "by_track":inventory["summary"]["by_track"],
        "official_atomic_denominator":None,
        "teacher_approved":0,
        "student_knowledge_released":0,
        "complete_curriculum":False,
        "official_source_page_evidence":page_progress(),
        "unreviewed_source_gap_candidates":gap_tickets()["summary"],
        "notice":"来源页码核对样本，不是全国课标官方原子全集或经教师审核的课程完成比例。"
    }
