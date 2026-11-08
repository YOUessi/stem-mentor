#!/usr/bin/env python3
"""K09 per-course editorial completeness ledger, not official syllabus atomization.

All 178 engineering IDs are provisional; a source-located page or validated JSON
does NOT count as official coverage, teacher review, or mathematical certification.
"""
import argparse
import json
import sys
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import curriculum,lessons

OUT=ROOT/"docs/evaluation/KB_BATCH24_COURSE_PROGRESS_MATRIX.json"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
        "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E","ELECTIVE_UNASSIGNED")
def build():
    rows=curriculum();corpus=lessons()
    links=defaultdict(list)
    for d in corpus:
        for cid in d.curriculum_ids:links[cid].append(d)
    if len(rows)!=178 or len(corpus)!=287:raise ValueError("Unexpected live baseline")
    course=[];trackmap=defaultdict(list)
    for r in rows:
        track=("COMPULSORY" if r["level"]=="必修" else
            "SELECTIVE_COMPULSORY" if r["level"]=="选择性必修" else
            r.get("elective_track","ELECTIVE_UNASSIGNED"))
        if track not in TRACKS:raise ValueError("Unknown course category")
        l=sorted(links[r["id"]],key=lambda d:d.id)
        counts=Counter(d.kind for d in l)
        if not l or any(d.review.status!="REVIEW_PENDING" or
                         d.teacher_solution_visibility!="TEACHER_ONLY" for d in l):
            if not l:
                status="NO_STRUCTURED_LESSON_DRAFT"
            else:raise ValueError("Unapproved content attempted release")
        else:status="SCHEMA_VALID_UNREVIEWED_DRAFTS"
        item=dict(
            engineering_id=r["id"],track=track,project_theme=r["theme"],
            project_unit=r["unit"],project_topic=r["concept"],
            source_mapping_type=r["source"]["mapping_type"],
            source_teacher_review=r["source"]["teacher_review"],
            editorial_gap_id=r.get("editorial_objective_id"),
            structured_draft_ids=[d.id for d in l],structured_draft_count=len(l),
            draft_kinds=dict(sorted(counts.items())),
            draft_unverified_proof_steps=sum(len(d.proof_steps) for d in l),
            teacher_side_worked_examples=sum(len(d.worked_examples) for d in l),
            required_schema_status=status,
            official_knowledge_atoms_in_topic=None,
            official_unit_coverage=None,approved_lesson_count=0,
            mathematical_full_proofs_certified=0,student_visible_teacher_solutions=0)
        trackmap[track].append(item);course.append(item)
    all_ids={d.id for d in corpus}
    assert len(all_ids)==287
    assert sum(x["structured_draft_count"] for x in course)==sum(len(d.curriculum_ids) for d in corpus)
    assert all(d.review.status=="REVIEW_PENDING" for d in corpus)
    tracks=[]
    for track in TRACKS:
        assigned=trackmap[track]
        tracks.append(dict(track=track,
            provisional_engineering_topics=len(assigned),
            engineering_topics_with_draft=sum(bool(x["structured_draft_count"]) for x in assigned),
            draft_links=sum(x["structured_draft_count"] for x in assigned),
            curriculum_official_atom_denominator=None,
            officially_covered_atoms=None,official_coverage_rate=None,
            verified_math_lessons=0,teacher_approved_lessons=0,
            student_published_lessons=0))
    report=dict(schema_version="batch24-course-completeness-v1",
        scope="ALL_ENGINEERING_TOPICS_DRAFT_ONLY_NOT_OFFICIAL_ATOMIC_CURRICULUM",
        summary=dict(engineering_topics=len(course),linked_draft_documents=len(corpus),
            draft_course_associations=sum(x["structured_draft_count"] for x in course),
            engineering_topics_with_drafts=sum(bool(x["structured_draft_count"]) for x in course),
            unlinked_project_topics=sum(not x["structured_draft_count"] for x in course),
            unverified_proof_steps=sum(len(x.proof_steps) for x in corpus),
            worked_example_count=sum(len(x.worked_examples) for x in corpus),
            officially_verified_atomic_denominator=None,
            teacher_approved_lessons=0,student_published_lessons=0),
        tracks=tracks,courses=course,
        warnings=[
            "A coarse engineering topic can link many partially overlapping drafts; linked is NOT complete.",
            "Prerequisites, theorem assumptions and example correctness still require independent auditing.",
            "A valid schema is not a mathematical proof and cannot grant real teacher approval.",
            "Course official atom denominator and coverage remain null until source clauses are independently decomposed and teacher verified."])
    return json.dumps(report,ensure_ascii=False,indent=2)+"\n"
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");args=p.parse_args()
    body=build()
    if args.check:
        if OUT.read_text(encoding="utf-8")!=body:raise SystemExit("Course progress matrix drift")
    else:OUT.write_text(body,encoding="utf-8")
    r=json.loads(body)["summary"]
    print("PASS: 178 engineering topics, 287 REVIEW_PENDING drafts; official knowledge denominator NULL;",r["unlinked_project_topics"],"engineering rows with no lesson")
if __name__=="__main__":main()
