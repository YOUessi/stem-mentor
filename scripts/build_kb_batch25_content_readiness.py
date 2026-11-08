#!/usr/bin/env python3
"""K01/K09 review worklist for all 287 in-repository drafts.

This is NOT a theorem checker. Field presence, lesson links and candidate
coverage must never masquerade as teacher signatures or official atom coverage.
"""
import argparse
import json
import sys
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import curriculum,lessons

OUT=ROOT/"docs/evaluation/KB_BATCH25_LESSON_REVIEW_READINESS.json"
def build():
    corpus=lessons();rows=curriculum()
    if len(corpus)!=287 or len(rows)!=178:raise ValueError("Unexpected batch24 corpus baseline")
    maps={x["id"]:x for x in rows}
    tracks=Counter();kindcounts=Counter();reasons=Counter();action=defaultdict(list)
    items=[]
    for d in sorted(corpus,key=lambda t:t.id):
        record=d.model_dump(mode="json")
        if record["review"]!={"status":"REVIEW_PENDING","reviewer_id":None,
                              "reviewed_at":None,"review_record":None}:
            raise ValueError("Illegal reviewer evidence or released draft")
        if d.teacher_solution_visibility!="TEACHER_ONLY":
            raise ValueError("Unapproved solution leak")
        assert all(cid in maps for cid in d.curriculum_ids)
        tr=[("COMPULSORY" if maps[cid]["level"]=="必修" else
             "SELECTIVE_COMPULSORY" if maps[cid]["level"]=="选择性必修" else
             maps[cid].get("elective_track","ELECTIVE_UNASSIGNED"))
            for cid in d.curriculum_ids]
        track=sorted(set(tr))
        if not track:raise ValueError("No course context")
        for t in track:tracks[t]+=1
        kindcounts[d.kind]+=1
        # Mandatory type-specific structural fields, NOT content truth.
        required={
            "notation":bool(d.notation),"assumptions":bool(d.assumptions),
            "boundaries":bool(d.boundaries),"counterexamples":bool(d.counterexamples),
            "misconceptions":bool(d.misconceptions),"worked_examples":len(d.worked_examples)>=2,
            "hint_ladder":len(d.hint_ladder)>=3,
            "prerequisites":bool(d.prerequisites),
            "near_transfer":bool(d.transfer.near),"far_transfer":bool(d.transfer.far),
            "definition" if d.kind=="concept" else "statement":bool(
                d.definition if d.kind=="concept" else d.statement),
            "proof_steps" if d.kind=="theorem" else "rationale_steps":
                len(d.proof_steps)>=3 if d.kind=="theorem" else len(d.rationale_steps)>=2
        }
        if not all(required.values()):raise ValueError("Schema depth fields missing for "+d.id)
        # A natural-language prerequisite is not a graph edge.
        needs_graph=not d.prerequisite_lesson_ids
        if needs_graph:reasons["no_explicit_prerequisite_lesson_graph_edge"]+=1
        if d.kind=="theorem":reasons["proof_whole_not_certified"]+=1
        if not d.proof_steps and d.kind=="concept":reasons["concept_no_proof_required"]+=1
        reasons["teacher_review_missing"]+=1
        reasons["official_atom_mapping_unverified"]+=1
        for t in track:action[t].append(d.id)
        items.append(dict(id=d.id,kind=d.kind,version=d.version,
          project_curriculum_ids=d.curriculum_ids,track_candidates=track,
          required_field_presence=required,structurally_valid_unreviewed=True,
          prerequisite_text_count=len(d.prerequisites),
          explicit_prerequisite_graph_edges=len(d.prerequisite_lesson_ids),
          proof_step_count=len(d.proof_steps),
          teacher_side_worked_examples=len(d.worked_examples),
          staged_hint_count=len(d.hint_ladder),
          official_atomic_ids_verified=[],
          independent_mathematical_proof_certificate=None,
          independent_example_math_certification=None,
          teacher_approval_evidence=None,
          student_challenge_teacher_solution_visible=False,
          review_state="REVIEW_PENDING",
          pending_work=["K00 source clause independent split/mapping",
             "K07 independent premise + counterexample verification",
             "K09 authenticated teacher review"]+
             (["K01 explicit prerequisite graph link audit"] if needs_graph else [])))
    if len(items)!=len({x["id"] for x in items}):raise ValueError("Duplicated lesson")
    summary=dict(draft_lessons=len(corpus),provisional_engineering_topics=len(rows),
          with_required_type_specific_fields=sum(all(x["required_field_presence"].values()) for x in items),
          with_explicit_graph_edges=sum(x["explicit_prerequisite_graph_edges"]>0 for x in items),
          total_unverified_proof_steps=sum(x["proof_step_count"] for x in items),
          teacher_side_examples=sum(x["teacher_side_worked_examples"] for x in items),
          by_kind=dict(sorted(kindcounts.items())),by_track_draft_associations=dict(sorted(tracks.items())),
          pending_reasons=dict(sorted(reasons.items())),
          teacher_approved=0,mathematically_certified_whole_proofs=0,
          verified_official_atomic_denominator=None,official_atom_coverage_rate=None,
          student_published_lessons=0)
    if summary["total_unverified_proof_steps"]!=538 or summary["teacher_side_examples"]!=574:
        raise ValueError("Historical proof/example count mismatch")
    return json.dumps(dict(schema_version="kb-batch25-content-readiness-v1",
         scope="STRUCTURAL_CONTENT_AND_EDITORIAL_WORKLIST_ONLY_NOT_MATHEMATICAL_TRUTH",
         summary=summary,items=items,
         by_track_unreviewed_lesson_ids=dict(sorted((k,sorted(v)) for k,v in action.items())),
         warnings=["Type-specific schema completeness is not quality of proof or source equivalence.",
                   "Absent explicit prerequisite links flag an editorial work item, not a mathematical error.",
                   "All 287 items need independently reviewed standards anchors and real teacher signature."]),
         ensure_ascii=False,indent=2)+"\n"
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");a=ap.parse_args()
    v=build()
    if a.check:
        if OUT.read_text(encoding="utf-8")!=v:raise SystemExit("Batch25 readiness matrix drift")
    else:OUT.write_text(v,encoding="utf-8")
    x=json.loads(v)["summary"]
    print("PASS",x["draft_lessons"],"draft audit, 538 unverified steps, 0 approved")
if __name__=="__main__":main()
