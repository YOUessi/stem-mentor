#!/usr/bin/env python3
"""Conservative current-state audit: editorial matches never equal official coverage."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import lessons,curriculum
from app.objective_proposals import editorial_review_queue
from app.deep_retrieval import student_evidence_lookup
SRC=ROOT/"curriculum/highschool_math/author_draft_batch15.json"
OUT=ROOT/"docs/evaluation/KB_BATCH15_ADVANCED_DRAFT_AUDIT.json"
def audit():
    own=json.loads(SRC.read_text(encoding="utf8")); docs=lessons()
    review=editorial_review_queue()
    # Later batches must NOT rewrite the historical Batch15 snapshot. Reconfirm
    # original authored bytes and immutable snapshot SHA, then use its archived
    # metrics; current-state metrics belong to subsequent batch audits.
    if len(docs)>201:
        frozen=OUT.read_bytes()
        assert hashlib.sha256(frozen).hexdigest()=="c428b13ba052df7f860b126cb6e3d2fc28a7ac73571bf7e2a0c89443205457cb"
        assert hashlib.sha256(SRC.read_bytes()).hexdigest()=="f0532c1f781d1d308073bfe4d9014cc80433d65b71b3736639459224152f5a89"
        assert len(own)==9 and len(curriculum())>=138
        assert review["total_deep_draft_lessons"]==len(docs)
        assert all(x["review"]["status"]=="REVIEW_PENDING"
                   and x["teacher_solution_visibility"]=="TEACHER_ONLY" for x in own)
        return json.loads(frozen)
    assert len(own)==9 and len(docs)==201 and len(curriculum())==138
    assert review["total_deep_draft_lessons"]==201
    assert student_evidence_lookup("线性回归求斜率")["status"]=="NO_APPROVED_EVIDENCE"
    assert all(x["review"]["status"]=="REVIEW_PENDING" and x["teacher_solution_visibility"]=="TEACHER_ONLY" for x in own)
    return {
        "status":"AUTHOR_DRAFT_UNVERIFIED",
        "source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
        "batch15_lessons":len(own),
        "deep_drafts_total":len(docs),
        "engineering_topics":len(curriculum()),
        "editorial_source_candidate_objectives":review["total_source_objective_candidates"],
        "objectives_with_unreviewed_suggestions":review["proposed_objectives"],
        "editorial_suggestion_edges":review["proposed_edges"],
        "no_suggestion_count":sum(x["without_suggestion"] for x in review["by_track"].values()),
        "by_track":review["by_track"],
        "teacher_approved":0,"formal_whole_proofs_verified":0,"student_evidence_published":0,
        "official_atomic_denominator":None,"official_coverage_percent":None,
        "math_truth_status":"BOUNDED_EXACT_SUBCLAIMS_ONLY",
        "warnings":["All authored content requires independent mathematical review and real teacher signatures.",
                    "Matching editorial objectives is NOT proof of official curriculum coverage.",
                    "Current 10 legacy content conflicts and pre-existing proof obligations remain unresolved."]
    }
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
    s=json.dumps(audit(),ensure_ascii=False,indent=2)+"\n"
    if a.check:
        assert OUT.exists() and OUT.read_text(encoding="utf8")==s, "Batch15 snapshot drift"
    else: OUT.write_text(s,encoding="utf8")
    print("PASS Batch15 audit",audit()["batch15_lessons"],"drafts")
if __name__=="__main__":main()
