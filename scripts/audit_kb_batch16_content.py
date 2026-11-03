#!/usr/bin/env python3
"""Machine-reconcilable, deliberately NON-CERTIFYING Batch16 editorial coverage."""
from __future__ import annotations
import sys,json,hashlib,argparse
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import lessons,curriculum
from app.objective_proposals import editorial_review_queue,validate_proposals
from app.deep_retrieval import student_evidence_lookup

SRC=ROOT/"curriculum/highschool_math/author_draft_batch16.json"
MAPPING=ROOT/"curriculum/highschool_math/elective_b_c_d_e_atomic_candidates_batch16.json"
OUT=ROOT/"docs/evaluation/KB_BATCH16_EDITORIAL_AUDIT.json"

def audit():
    new=json.loads(SRC.read_text(encoding="utf8"))
    mapping=json.loads(MAPPING.read_text(encoding="utf8"))
    docs=lessons(); course=curriculum()
    proposed=editorial_review_queue()
    assert len(new)==len(mapping)==12
    assert len(docs)==213 and len(course)==150
    assert {x["curriculum_ids"][0] for x in new}=={x["id"] for x in mapping}
    assert proposed["total_source_objective_candidates"]==132
    assert proposed["total_deep_draft_lessons"]==213
    assert proposed["proposed_objectives"]==119 and proposed["proposed_edges"]==141
    assert validate_proposals(proposed)
    assert proposed["official_atomic_denominator"] is None
    assert student_evidence_lookup("十二平均律黄金分割逻辑斯蒂模型")["status"]=="NO_APPROVED_EVIDENCE"
    assert all(x["review"]["status"]=="REVIEW_PENDING"
               and x["teacher_solution_visibility"]=="TEACHER_ONLY"
               and x["review"]["reviewer_id"] is None for x in new)
    return {
        "status":"BATCH16_EDITORIAL_DRAFT_NOT_OFFICIALLY_CERTIFIED",
        "authored_source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
        "mapping_sha256":hashlib.sha256(MAPPING.read_bytes()).hexdigest(),
        "new_deep_lessons":len(new),
        "by_elective_track":dict(sorted(Counter(m["elective_track"] for m in mapping).items())),
        "deep_lessons_total":len(docs),"engineering_topics_total":len(course),
        "source_objective_candidates":proposed["total_source_objective_candidates"],
        "objectives_with_editorial_proposals":proposed["proposed_objectives"],
        "editorial_proposal_edges":proposed["proposed_edges"],
        "unmatched_source_candidates":proposed["total_source_objective_candidates"]-proposed["proposed_objectives"],
        "by_track":proposed["by_track"],
        "official_atomic_denominator":None,"official_atomic_coverage_percent":None,
        "teacher_approved_lessons":0,"formal_whole_proofs_verified":0,"student_published_lessons":0,
        "claims_warning":[
            "The 132 source-page candidates are an incomplete project-authored sample; official atom denominator remains unknown.",
            "A lesson-objective association is an editorial review proposal, NOT a teacher-certified curricular coverage claim.",
            "Bounded arithmetic/symbolic oracles do not certify full natural-language mathematical proofs.",
            "Unreviewed teacher examples remain TEACHER_ONLY; actual external API calls not executed."
        ]
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
    report=json.dumps(audit(),ensure_ascii=False,indent=2)+"\n"
    if a.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf8")!=report:
            raise AssertionError("Batch16 audit drift")
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(report,encoding="utf8")
    print("PASS Batch16 editorial audit",audit()["deep_lessons_total"],"draft lessons")
if __name__=="__main__":main()
