#!/usr/bin/env python3
"""Batch124 K00/K01: pinned 2020 curriculum lines, 32 real editorial concepts,
three NON-ATOM review candidates, 405-cue full ledger, fail-closed gates.
No teacher approvals, no official atom denominator, no source text committed.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch123_semantic_census as previous
from kb_batch124_catalog import ROWS, NONATOM
D=ROOT/"curriculum/highschool_math";E=ROOT/"docs/evaluation"
OUT=D/"k00_batch124_editorial_atoms.json"; LOCKS=D/"k00_batch124_source_locks.json"
QUEUE=E/"KB_BATCH124_CUE_ADJUDICATION.json"; COVER=E/"KB_BATCH124_COVERAGE.json"
REPORT=E/"KB_BATCH124_SCOPE_REVIEW.md"
def require(ok,msg):
    if not ok:raise ValueError(msg)
def h(t):return hashlib.sha256(t.encode("utf-8")).hexdigest()
def serialize(t):return json.dumps(t,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def anchored():
    pages={r["printed_page"]:r["lines"] for r in previous.base_scope.evidence.source_pages()}
    return {row[0]:h(pages[row[2]][row[3]-1]) for row in ROWS}
def pinned():
    require(LOCKS.exists(),"independent Mac original-source hash locks missing")
    data=json.loads(LOCKS.read_text())
    require(set(data)=={r[0] for r in ROWS} and all(len(v)==64 for v in data.values()),"source hash locks invalid")
    return data
def prior():
    return previous.prev()+previous.build()["candidates"]
def build():
    b=previous.base_scope.base(); page={r["printed_page"]:r for r in b["pages"]}
    source=previous.base_scope.evidence
    cue=defaultdict(list)
    for r in b["markers"]:cue[(r["printed_page"],r["source_line"],r["track_hint"])].append(r)
    locks=pinned(); old=prior()
    known_ids={r["id"] for r in old}
    names={(r["course_track"],r["proposed_objective"]) for r in old}
    drafts=[]
    for key,track,p,l,kind,title,applicability,invalid in ROWS:
        ident="hs-semantic-pilot-124-"+key.lower()
        require(ident not in known_ids and (track,title) not in names, "duplicate proposal "+key)
        require(kind in ("concept","theorem","method") and track in source.TRACKS,"invalid candidate type/track")
        require(len(title)>=10 and len(applicability)>=30 and len(invalid)>=24,"insufficient source interpretation "+key)
        require(source.track_at(p,l)==track and 1<=l<=page[p]["source_line_count"],"line crosses curriculum track")
        markers=cue[(p,l,track)]
        require(len(markers)==1 and markers[0]["editorial_marker_id"] not in
            {j for r in old for j in r["source"]["matching_layout_cues"]},"no new distinct source cue "+key)
        markers=markers[0]
        src={"printed_page":p,"physical_page_index":p+7,"start_line":l,"end_line":l,
             "original_pdf_sha256":source.PDF_SHA,"frozen_page_sha256":page[p]["source_page_sha256"],
             "source_span_sha256":locks[key],"matching_layout_cues":[markers["editorial_marker_id"]],
             "cue_kinds":[markers["cue_kind"]],
             "numbered_requirement_anchor":markers["cue_kind"]=="NUMBERED_REQUIREMENT_CUE",
             "visual_formula_recheck":"REQUIRED" if page[p]["mathematics_image_risk"] else "NOT_FLAGGED"}
        drafts.append({"id":ident,"local_key":key,"course_track":track,"kind":kind,
            "proposed_objective":title,"applicability":applicability,"invalid_use":invalid,
            "prerequisite_candidate_ids":[],"source":src,"review_status":"REVIEW_PENDING",
            "teacher_evidence":None,"proof_verification":"UNVERIFIED",
            "teacher_solution_visibility":"TEACHER_ONLY","student_authoritative":False,
            "official_atom_id":None,"official_atom_certified":False,
            "elective_e_optional_example":track=="ELECTIVE_E"})
        known_ids.add(ident);names.add((track,title))
    result={"schema_version":"kb124-original-editorial-v1","curriculum_standard":b["curriculum_standard"],
            "original_pdf_sha256":source.PDF_SHA,"source_text_committed":False,
            "official_atom_census_complete":False,"official_atom_total_denominator":None,
            "semantic_candidates_not_official_atoms":True,
            "new_candidate_count":len(drafts),"cumulative_editorial_candidate_count":len(old)+len(drafts),
            "teacher_approved_count":0,"student_authoritative_count":0,"candidates":drafts}
    validate(result);return result
def validate(data):
    b=previous.base_scope.base()
    source=previous.base_scope.evidence
    require(data["schema_version"]=="kb124-original-editorial-v1"
        and data["curriculum_standard"]==b["curriculum_standard"]
        and data["original_pdf_sha256"]==source.PDF_SHA and data["source_text_committed"] is False
        and data["official_atom_census_complete"] is False
        and data["official_atom_total_denominator"] is None
        and data["semantic_candidates_not_official_atoms"] is True
        and data["teacher_approved_count"]==data["student_authoritative_count"]==0,
        "forged census or authority")
    require(data["new_candidate_count"]==len(ROWS)==len(data["candidates"])==32
        and data["cumulative_editorial_candidate_count"]==len(prior())+32,"candidate denominator drift")
    old={r["id"] for r in prior()}; locks=pinned()
    pages={r["printed_page"]:r for r in b["pages"]}
    for r, row in zip(data["candidates"],ROWS):
        key,track,p,l,kind,title,domain,invalid=row
        marker=[m for m in b["markers"] if m["printed_page"]==p and m["source_line"]==l
                and m["track_hint"]==track]
        src=r["source"]; require(len(marker)==1,"ambiguous line marker")
        expected={"printed_page":p,"physical_page_index":p+7,"start_line":l,"end_line":l,
            "original_pdf_sha256":source.PDF_SHA,"frozen_page_sha256":pages[p]["source_page_sha256"],
            "source_span_sha256":locks[key],"matching_layout_cues":[marker[0]["editorial_marker_id"]],
            "cue_kinds":[marker[0]["cue_kind"]],
            "numbered_requirement_anchor":marker[0]["cue_kind"]=="NUMBERED_REQUIREMENT_CUE",
            "visual_formula_recheck":"REQUIRED" if pages[p]["mathematics_image_risk"] else "NOT_FLAGGED"}
        require(r["id"]=="hs-semantic-pilot-124-"+key.lower() and r["id"] not in old
            and r["local_key"]==key and r["course_track"]==track and r["kind"]==kind
            and r["proposed_objective"]==title and r["applicability"]==domain and r["invalid_use"]==invalid
            and r["prerequisite_candidate_ids"]==[] and src==expected,"manuscript/source identity drift "+key)
        require(r["review_status"]=="REVIEW_PENDING" and r["teacher_evidence"] is None
           and r["proof_verification"]=="UNVERIFIED" and r["student_authoritative"] is False
           and r["teacher_solution_visibility"]=="TEACHER_ONLY"
           and r["official_atom_id"] is None and r["official_atom_certified"] is False
           and r["elective_e_optional_example"]==(track=="ELECTIVE_E"),"draft promoted "+key)
        require(source.track_at(p,l)==track,"source track altered")
    return True
def triage(data):
    b=previous.base_scope.base();links=defaultdict(list)
    for z in prior()+data["candidates"]:
        for key in z["source"]["matching_layout_cues"]: links[key].append(z["id"])
    nonatom={(p,l,track):reason for track,p,l,reason in NONATOM}
    require(len(nonatom)==len(NONATOM)==3,"duplicate non-atom review")
    result=[]
    for m in b["markers"]:
        cid=m["editorial_marker_id"];k=(m["printed_page"],m["source_line"],m["track_hint"]);ids=sorted(links[cid])
        if ids: state="SOURCE_LINKED_EDITORIAL_CANDIDATE";action="Human and teacher review; official atom count unknown"
        elif k in nonatom:
            require(m["cue_kind"]=="NUMBERED_REQUIREMENT_CUE","non-atom is not a numbered activity")
            state="NON_ATOM_ACTIVITY_EDITORIAL_PROPOSAL_PENDING_REVIEW";action=nonatom[k]
        else:
            state,action={
            "TOPIC_CUE":("TOPIC_HEADING_NEEDS_CHILD_SCOPE_REVIEW","Heading only; review its child objectives"),
            "SUBTOPIC_CUE":("SUBTOPIC_CUE_PENDING_CLAUSE_REVIEW","Inspect requirements across neighboring lines"),
            "NUMBERED_REQUIREMENT_CUE":("NUMBERED_REQUIREMENT_AWAITING_EDITORIAL_ATOMIZATION","Inspect full clause and possible atomic splitting")}[m["cue_kind"]]
        result.append({"cue_id":cid,"cue_kind":m["cue_kind"],"course_track":m["track_hint"],
          "printed_page":m["printed_page"],"source_line":m["source_line"],
          "source_line_sha256":m["source_line_sha256"],"status":state,"next_action":action,
          "linked_candidate_ids":ids,"needs_formula_visual_recheck":m["needs_formula_visual_recheck"],
          "official_atom_id":None,"teacher_approved":False,"student_authoritative":False})
    require(len(result)==405,"source cue loss")
    return result
def coverage(data,queue):
    group=sorted(set(previous.base_scope.TRACKS)|{"ELECTIVE_UNASSIGNED"})
    n=Counter(r["course_track"] for r in queue)
    linked=Counter(r["course_track"] for r in queue if r["linked_candidate_ids"])
    pending=Counter(r["course_track"] for r in queue if r["status"]=="NON_ATOM_ACTIVITY_EDITORIAL_PROPOSAL_PENDING_REVIEW")
    prevcount=Counter(r["course_track"] for r in prior())
    batch=Counter(r["course_track"] for r in data["candidates"])
    count=Counter(r["status"] for r in queue)
    return {"batch":124,"total_layout_cues":405,"total_source_pages":61,
      "cues_linked":sum(bool(q["linked_candidate_ids"]) for q in queue),
      "cues_unlinked":sum(not q["linked_candidate_ids"] for q in queue),
      "editorial_nonatom_proposals_pending":sum(pending.values()),
      "source_cue_dispositions":dict(sorted(count.items())),
      "new_editorial_candidates":len(data["candidates"]),
      "cumulative_editorial_candidates":len(prior())+len(data["candidates"]),
      "official_atom_census_complete":False,"official_atom_total_denominator":None,
      "student_authoritative_count":0,"teacher_approved_count":0,
      "per_track":{k:{"layout_cues":n[k],"linked_cues":linked[k],"unlinked_cues":n[k]-linked[k],
        "nonatom_editorial_pending":pending[k],"new_editorial_candidates":batch[k],
        "cumulative_editorial_candidates":prevcount[k]+batch[k],
        "official_atom_denominator":None,"official_coverage":None,"teacher_approved":0} for k in group}}
def validate_queue(data,queue,cover):
    require(queue==triage(data) and cover==coverage(data,queue),"source queue or denominator altered")
    require(len({q["cue_id"] for q in queue})==405,"repeated source cue")
    require(all(q["official_atom_id"] is None and q["teacher_approved"] is False and
      q["student_authoritative"] is False for q in queue),"forged authority")
    return True
def render(data,queue,c):
    lines=["# Batch124 — mathematics curriculum clauses: editorial atomization and exclusions","",
      "Source: 2017 curriculum, 2020 revision; Mac-held original PDF only. No copyrighted source lines checked in.",
      "All items are **editorial proposals** pending expert review. Official seven-track atom denominators remain UNKNOWN.",
      f"New proposed concepts/methods/theorems: {len(ROWS)}; cumulative {c['cumulative_editorial_candidates']}.",
      f"Source cues linked {c['cues_linked']}/405; unlinked {c['cues_unlinked']}.",
      "Separately: 3 research/activity/competency clauses have proposed NON-ATOM dispositions awaiting human adjudication.",
      "Do not subtract those 3 to invent any official atom denominator.","",
      "|Track|Cues|Linked|Unlinked|Draft atoms|Nonatom proposals|Official denominator|",
      "|---|---:|---:|---:|---:|---:|---|"]
    for k,v in c["per_track"].items():
        lines.append(f"|{k}|{v['layout_cues']}|{v['linked_cues']}|{v['unlinked_cues']}|{v['cumulative_editorial_candidates']}|{v['nonatom_editorial_pending']}|UNKNOWN|")
    lines+=["","## Numbered requirement review proposals"]
    for track,p,l,reason in NONATOM:
        lines.append(f"- {track} printed p{p}, line {l}: {reason}; REVIEW_PENDING (not certified).")
    lines+=["","## Source-locked original mathematical objectives"]
    for row in data["candidates"]:
        lines += [f"### {row['local_key']} — {row['proposed_objective']}",
                  f"{row['course_track']} · printed p{row['source']['printed_page']} line {row['source']['start_line']} · {row['kind']}",
                  f"Premises: {row['applicability']}",f"Failure/false use: {row['invalid_use']}",""]
    lines+=["","## Limits","- Finite mathematical witnesses are not universal proofs.",
      "- No teacher approval, official completion, or student-authoritative release.",
      "- All remaining source cues require targeted human line/context/visual review, not just string matching.",""]
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    p.add_argument("--freeze-source",action="store_true");p.add_argument("--verify-local-source",action="store_true")
    a=p.parse_args()
    if a.freeze_source:
        require(a.write,"freeze must be explicit write")
        LOCKS.write_text(serialize(anchored()),encoding="utf-8")
    data=build();queue=triage(data);cv=coverage(data,queue);validate_queue(data,queue,cv)
    if a.verify_local_source: require(pinned()==anchored(),"local source SHA changed")
    for path,value in ((OUT,serialize(data)),(QUEUE,serialize(queue)),(COVER,serialize(cv)),(REPORT,render(data,queue,cv))):
        if a.write:path.write_text(value,encoding="utf-8")
        else:require(path.exists() and path.read_text(encoding="utf-8")==value,"derived file drift "+str(path))
    print("Batch124",len(ROWS),"new",len(prior())+len(ROWS),"total",cv["cues_linked"],"linked",cv["cues_unlinked"],"unlinked; official atoms UNKNOWN")
if __name__=="__main__":main()
