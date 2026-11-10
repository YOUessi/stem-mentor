#!/usr/bin/env python3
"""Batch81: reproducible K00 anchor review lanes and COMPLETE K07 P0 risk census.

The 127 P0_GUARD_AND_COUNTEREXAMPLE entries are one of FOUR P0 classes.
This script explicitly counts all 182 P0 obligations and preserves 428
source-review anchors without claiming that either is an official atom count.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROOFS=ROOT/"docs/evaluation/KB_BATCH80_PROOF_QUEUE.json"
ANCHORS=ROOT/"curriculum/highschool_math/kb_batch80_review_queue.json"
CARDS81=ROOT/"knowledge/editorial_review/kb_batch81_twelve_math_cards.json"
OUT=ROOT/"docs/evaluation/KB_BATCH81_RISK_CENSUS.json"
OUT_ANCHORS=ROOT/"curriculum/highschool_math/kb_batch81_anchor_triage.json"
OUT_MD=ROOT/"docs/evaluation/KB_BATCH81_RISK_CENSUS.md"
EXPECTED_SHA={
 "proofs":"339ceb2ecb0b60116f38093f5a7a52a3e60c7b738fe5a4fc2021a06695232c01",
 "anchors":"f9c2f95a7cd6a49383769b88762eee79f6366ff744a19d865f6be3674e28653e",
}
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
KINDS={
 "SECTION_LABEL":"REVIEW_HEADING_NOT_AN_ATOM_BY_ITSELF",
 "MAJOR_NUMBER":"REVIEW_MIXED_CLAUSE_AND_CHILDREN",
 "SUBCLAUSE_NUMBER":"REVIEW_ATOMIC_SPLIT_AND_DEPENDENCIES",
 "CIRCLED_ITEM":"REVIEW_REQUIREMENT_VERSUS_ACTIVITY",
}
RISK_CLASSES=("P0_GUARD_AND_COUNTEREXAMPLE","P0_HUMAN_ATTENTION",
 "P0_REVIEW_IF_DOMAIN_OR_EQUIVALENCE_MISSING","P0_UNVERIFIED_STEP_REQUIRES_DOMAIN_CHECK",
 "P1_HUMAN_ATTENTION","P1_THEOREM_PROOF","P1_UNVERIFIED","P2_REVIEW")

def reject(ok,message):
 if not ok: raise ValueError(message)

def get_inputs():
 for key,location in (("proofs",PROOFS),("anchors",ANCHORS)):
  reject(hashlib.sha256(location.read_bytes()).hexdigest()==EXPECTED_SHA[key],
         "Frozen Batch80 "+key+" input changed")
 return json.loads(PROOFS.read_text()),json.loads(ANCHORS.read_text())

def build(proofs=None,anchors=None,newcards=None):
 if proofs is None or anchors is None:
  p,a=get_inputs();proofs=p if proofs is None else proofs;anchors=a if anchors is None else anchors
 if newcards is None:newcards=json.loads(CARDS81.read_text())
 rows=proofs["step_review_queue"]
 src=anchors["anchor_review_queue"]
 reject(len(rows)==538 and len({r["id"] for r in rows})==538,"Proof queue not conserved")
 reject(all(r["review_status"]=="REVIEW_PENDING" and r["formal_certification"]=="NOT_FORMALLY_VERIFIED"
   and r["student_publishable"] is False for r in rows),
   "Any historical proof step has illegal review/certification state")
 reject(len(src)==428 and len({r["review_id"] for r in src})==428,"Anchor queue not conserved")
 reject(proofs["unresolved_conflicts"]==10 and proofs["formally_certified_steps"]==0,
        "Proofs illegally certified or conflicts removed")
 reject(anchors["official_atom_denominator"] is None and anchors["full_page_teacher_atomizations"]==0,
        "Official scope prematurely certified")
 risk=Counter(r["risk_priority"] for r in rows)
 reject(set(risk)==set(RISK_CLASSES),"Unexpected risk taxonomy")
 extra=newcards["review_cards"]
 reject(len(extra)==12 and newcards["teacher_approvals"]==0 and newcards["formal_certifications"]==0,
        "Independent Batch81 card evidence changed")
 prior_ids={r["id"] for r in rows if r["review_card_id"] is not None}
 newlinks={}
 for c in extra:
  k=c["linked_historical_step_id"]
  original=next((r for r in rows if r["id"]==k),None)
  reject(original is not None and original["review_card_id"] is None and k not in newlinks,
         "Duplicate or missing new review source")
  reject(c["original_step_sha256"]==original["source_sha256"]
    and original["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE",
         "New review card must point to SHA-attested P0")
  reject(c["review_status"]=="REVIEW_PENDING" and c["student_publishable"] is False
    and c["formal_math_certification"]=="NOT_FORMALLY_VERIFIED"
    and c["teacher_solution_visibility"]=="TEACHER_ONLY",
         "Unauthorized teacher card release")
  newlinks[k]=c["id"]
 linked=[r for r in rows if r["review_card_id"] is not None]
 reject(len(linked)==36 and all(r["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE" for r in linked),
        "Teacher draft ledger links mutated")
 p0=[r for r in rows if r["risk_priority"].startswith("P0_")]
 reject(len(p0)==182 and risk["P0_GUARD_AND_COUNTEREXAMPLE"]==127,
        "High-risk debt population changed")
 reject(len([r for r in p0 if not r["review_card_id"]])==146 and len(newlinks)==12,
        "High-risk review gap changed")
 by_risk={}
 for k in RISK_CLASSES:
  segment=[r for r in rows if r["risk_priority"]==k]
  by_risk[k]={"total":len(segment),"teacher_drafts_linked":sum(r["review_card_id"] is not None or r["id"] in newlinks for r in segment),
    "without_teacher_drafts":sum(r["review_card_id"] is None and r["id"] not in newlinks for r in segment),
    "teacher_approved":0,"formally_certified":0}
 queue=[]
 for r in p0:
  reject(r["review_status"]=="REVIEW_PENDING" and r["formal_certification"]=="NOT_FORMALLY_VERIFIED"
    and r["student_publishable"] is False,"Invalid P0 release status")
  queue.append({"id":r["id"],"risk_priority":r["risk_priority"],
   "risk_groups":r["risk_groups"],"historical_step_sha256":r["source_sha256"],
   "review_card_id":r["review_card_id"] or newlinks.get(r["id"]),"conflict_id":r["conflict_id"],
   "next_action":"INDEPENDENT_CONFLICT_ADJUDICATION" if r["conflict_id"]
     else "DRAFT_CONDITION_GUARD_AND_COUNTEREXAMPLE" if r["review_card_id"] is None and r["id"] not in newlinks
     else "TEACHER_REVIEW_OF_EXISTING_DRAFT",
   "teacher_approved":False,"formal_math_verification":False,"student_publishable":False})
 result={
  "schema_version":"kb81-complete-p0-risk-population-v1",
  "source_input_sha256":EXPECTED_SHA["proofs"],
  "historical_proof_denominator":538,"all_p0_steps":182,
  "guard_subclass_p0_steps":127,"other_p0_steps":55,
  "all_p0_unlinked":134,"guard_subclass_p0_unlinked":79,
  "prior_batch80_all_p0_unlinked":146,"new_p0_teacher_drafts":12,
  "linked_teacher_drafts":48,"unresolved_conflicts":10,
  "teacher_approved":0,"formally_certified":0,"student_published":0,
  "by_risk":by_risk,"p0_review_queue":queue,
 }
 track=Counter(a["track"] for a in src)
 kind=Counter(a["kind"] for a in src)
 reject(set(track)<=set(TRACKS) and set(kind)==set(KINDS),"Unexpected scope classification")
 out=[]
 for s in src:
  reject(s["status"]=="REVIEW_PENDING" and s["official_atom_count"] is None
   and s["student_publishable"] is False,"Illegal K00 source promotion")
  out.append({"review_id":s["review_id"],"track":s["track"],"kind":s["kind"],
     "page":s["printed_page"],"pdfkit_line":s["pdfkit_line"],
     "source_line_sha256":s["source_line_sha256"],"parent_segment":s["parent_segment"],
     "review_lane":KINDS[s["kind"]],"semantic_role":"NOT_YET_EVIDENCE_ADJUDICATED",
     "deduplicated_official_atom_count":None,
     "human_approved":False,"student_publishable":False})
 doc={
  "schema_version":"kb81-anchor-work-routing-not-atomic-curriculum-v1",
  "source_input_sha256":EXPECTED_SHA["anchors"],"review_obligations":428,
  "by_track":{k:track[k] for k in TRACKS},"by_kind":dict(sorted(kind.items())),
  "candidate_work_items":out,"curriculum_official_denominator":None,
  "full_page_teacher_reviews":0,"teacher_approved":0,"student_published":0,
  "teacher_review_needed":True,"source_pdf_sha256":anchors["source_pdf_sha256"],
 }
 reject(sum(track.values())==428 and sum(kind.values())==428,"K00 reconciliation failed")
 return result,doc

def dump(x):
 return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n"

def markdown(p,a):
 return "\n".join([
  "# Batch81 | Complete P0 risk census and K00 review lanes","",
  "Every risk counted below comes from the SHA-pinned Batch80 ledger. No synthetic teacher approval.",
  "Crucial correction: **127 is only the P0_GUARD_AND_COUNTEREXAMPLE subclass, not all P0 risks**.",
  f"True P0 population **{p['all_p0_steps']}/538**, unlinked **{p['all_p0_unlinked']}**; "
  f"the guard subclass backlog is now {p['guard_subclass_p0_unlinked']}/127.",
  "",
  "| Historical risk class | All steps | Teacher draft only | No draft |",
  "|---|---:|---:|---:|",
  *[f"| {k} | {v['total']} | {v['teacher_drafts_linked']} | {v['without_teacher_drafts']} |"
     for k,v in p["by_risk"].items()],
  "",
  f"K00: **{a['review_obligations']}** source anchor work items routed by structural kind; "
  "**zero** human-completed semantic atomizations, **unknown** official curriculum atom denominator.",
  "Heading, numbered clause, nested item, and source mathematical atom are different concepts.",
  "Seven tracks include an empty ELECTIVE_E anchor queue, **not** an empty official syllabus.",
  "All existing teacher drafts are REVIEW_PENDING and must never be surfaced to students as approved evidence.",
  "",
  "## Next steps",
  "1. Independently review all four P0 risk classes; especially the 55 previously missing from the 127-subclass dashboard.",
  "2. Read the actual original PDF page text for K00 semantic adjudication; this work-routing output does not replace it.",
  "3. Resolve 10 independent conflicts and get real teacher signatures before approval or release.",
  ""])

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");v=ap.parse_args()
 p,a=build()
 for dest,s in ((OUT,dump(p)),(OUT_ANCHORS,dump(a)),(OUT_MD,markdown(p,a))):
  if v.check:
   reject(dest.exists() and dest.read_text()==s,"Generated artifact out of sync: "+str(dest))
  else:dest.write_text(s)
 print("Batch81: 182 all-P0, 48 draft links, 134 unlinked; 428 source obligations; no official atom certification")
if __name__=="__main__":main()
