#!/usr/bin/env python3
"""Editorial-only, version-pinned Batch17 audit. Never outputs an official coverage rate."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import lessons,curriculum
from app.objective_proposals import editorial_review_queue,validate_proposals
from app.deep_retrieval import student_evidence_lookup

SRC=ROOT/"curriculum/highschool_math/author_draft_batch17.json"
COURSE=ROOT/"curriculum/highschool_math/cross_track_atomic_candidates_batch17.json"
RENDER=ROOT/"knowledge/deep/v1/cross_track_batch17.json"
PROPOSALS=ROOT/"curriculum/highschool_math/objective_lesson_proposals_batch13.json"
OUT=ROOT/"docs/evaluation/KB_BATCH17_EDITORIAL_AUDIT.json"
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def audit():
    authored=json.loads(SRC.read_text(encoding="utf8"))
    mapping=json.loads(COURSE.read_text(encoding="utf8"))
    proposals=editorial_review_queue()
    all_docs=lessons()
    assert len(authored)==11 and len(mapping)==11
    assert len(all_docs)>=224 and len(curriculum())==161
    assert len({r["id"] for r in authored})==11
    assert {r["curriculum_ids"][0] for r in authored}=={m["id"] for m in mapping}
    assert {r["curriculum_ids"][0] for r in authored}=={f"HS-MATH-{i}" for i in range(151,162)}
    assert Counter(r["kind"] for r in authored)=={"theorem":3,"concept":4,"method":4}
    assert sum(len(r["proof_steps"]) for r in authored)==12
    assert sum(len(r["worked_examples"]) for r in authored)==22
    assert all(r["review"]["status"]=="REVIEW_PENDING" and
               r["teacher_solution_visibility"]=="TEACHER_ONLY" and
               not any(r["review"][k] for k in ("reviewer_id","review_record","reviewed_at"))
               for r in authored)
    assert json.loads(RENDER.read_text(encoding="utf8"))==authored
    assert validate_proposals(proposals)
    assert proposals["proposed_objectives"]==132 and proposals["proposed_edges"]==154
    assert proposals["official_atomic_denominator"] is None
    assert proposals["official_coverage_percent"] is None
    assert all(x["without_suggestion"]==0 for x in proposals["by_track"].values())
    assert all(x.review.status=="REVIEW_PENDING" for x in all_docs)
    assert proposals["independent_teacher_approved_matches"]==0
    assert proposals["student_published_knowledge_count"]==0
    assert student_evidence_lookup("循环群空集节拍与微积分")["status"]=="NO_APPROVED_EVIDENCE"
    return {
        "status":"BATCH17_11_AUTHOR_DRAFTS_NOT_TEACHER_CERTIFIED",
        "authored_source_sha256":sha(SRC),
        "editorial_engineering_map_sha256":sha(COURSE),
        "rendered_lessons_sha256":sha(RENDER),
        "editorial_review_queue_sha256":sha(PROPOSALS),
        "new_deep_drafts":11,
        "new_by_kind":dict(sorted(Counter(r["kind"] for r in authored).items())),
        "new_pending_theorem_steps":12,
        "new_teacher_only_worked_examples":22,
        "new_engineering_nodes":11,
        "deep_drafts_total":len(all_docs),
        "deep_drafts_total_at_batch17":224,
        "engineering_nodes_total":161,
        "curriculum_objective_candidate_sample":132,
        "candidate_objectives_with_unreviewed_proposals":132,
        "candidate_proposed_links":154,
        "candidate_unmatched":0,
        "editorial_target_track_counts":dict(sorted(Counter(m["level"] for m in mapping).items())),
        "official_atomic_denominator":None,
        "official_coverage_percent":None,
        "teacher_approved_lessons":0,
        "student_published_lessons":0,
        "whole_natural_language_proofs_certified":0,
        "proof_step_verification_scope":"BOUNDED_ORACLES_ONLY_NOT_PROOF_CERTIFICATION",
        "warnings":[
            "132/132 only means the project's incomplete editorial candidate sample has suggested links; official curricular coverage is unknown.",
            "Two links reuse existing MVT/FTC draft explanations. A candidate overlap is not a signed review decision.",
            "Independent finite/parameterized checks do not certify complete proof chains, pedagogy, copyright, or standard paragraph alignment.",
            "All draft content is TEACHER_ONLY and REVIEW_PENDING; student approved-only retrieval remains fail-closed."
        ]
    }
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
    report=json.dumps(audit(),ensure_ascii=False,indent=2)+"\n"
    if a.check:
        if not OUT.exists() or OUT.read_text(encoding="utf8")!=report:
            raise AssertionError("Batch17 pinned editorial coverage report drift")
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(report,encoding="utf8")
    print("PASS Batch17 historical 224 draft snapshot; current=",len(lessons()),"132/132 author-proposed; teacher=0")
if __name__=="__main__":main()
