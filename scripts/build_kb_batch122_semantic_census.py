#!/usr/bin/env python3
"""Batch122: source-hash-locked proposals + auditable 405-cue semantic triage.

405 layout cues are *not* a denominator of official course atoms. No track is
marked complete and no teacher approval is generated.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch121_editorial_scope as prior
from kb_batch122_editorial_catalog import ROWS

BASE=ROOT/"curriculum/highschool_math"
OUT=BASE/"k00_batch122_semantic_proposals.json"
LOCKS=BASE/"k00_batch122_local_source_locks.json"
QUEUE=ROOT/"docs/evaluation/KB_BATCH122_CUE_TRIAGE.json"
COVER=ROOT/"docs/evaluation/KB_BATCH122_COVERAGE.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH122_SOURCE_AND_SEMANTIC_AUDIT.md"

def demand(ok,what):
    if not ok: raise ValueError(what)
def serial(x): return json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()

def source_locks_from_mac():
    pages={p["printed_page"]:p["lines"] for p in prior.evidence.source_pages()}
    return {r[0]:sha(pages[r[2]][r[3]-1]) for r in ROWS}

def locks():
    demand(LOCKS.exists(),"missing independently frozen Mac source hash manifest")
    m=json.loads(LOCKS.read_text(encoding="utf-8"))
    demand(set(m)=={r[0] for r in ROWS} and all(len(v)==64 for v in m.values()),"bad Mac source locks")
    return m

def prev():
    return prior.previous()+prior.build()["candidates"]

def build():
    original=prior.base(); pinned=locks()
    pages={p["printed_page"]:p for p in original["pages"]}
    markers=original["markers"]
    taken={x["id"] for x in prev()}
    names={(x["course_track"],x["proposed_objective"]) for x in prev()}
    result=[]
    for key,track,p,l,kind,title,domain,invalid,dependency,visual in ROWS:
        ident="hs-semantic-pilot-122-"+key.lower()
        demand(ident not in taken and (track,title) not in names,"duplicate identity or objective "+key)
        demand(track in prior.TRACKS and kind in ("method","concept","theorem"),"invalid taxonomy "+key)
        demand(prior.evidence.track_at(p,l)==track and 1<=l<=pages[p]["source_line_count"],"cross-track anchor "+key)
        demand(len(title)>9 and len(domain)>=22 and len(invalid)>=20,"incomplete editorial math boundaries "+key)
        if dependency:
            dep="hs-semantic-pilot-122-"+dependency.lower()
            demand(dep in taken,"orphan or forward prerequisite "+key)
            deps=[dep]
        else: deps=[]
        linked=[m["editorial_marker_id"] for m in markers if m["printed_page"]==p and m["source_line"]==l and m["track_hint"]==track]
        demand(linked,"no matching source layout cue "+key)
        result.append({
            "id":ident,"local_key":key,"course_track":track,"kind":kind,
            "proposed_objective":title,"applicability":domain,"invalid_use":invalid,
            "prerequisite_candidate_ids":deps,
            "source":{"printed_page":p,"physical_page_index":p+7,"start_line":l,"end_line":l,
                "original_pdf_sha256":prior.evidence.PDF_SHA,
                "frozen_page_sha256":pages[p]["source_page_sha256"],
                "source_span_sha256":pinned[key],"matching_layout_cues":linked,
                "visual_formula_recheck":"REQUIRED" if visual or pages[p]["mathematics_image_risk"] else "NOT_FLAGGED",
                "cue_kinds":sorted({m["cue_kind"] for m in markers if m["editorial_marker_id"] in linked}),
                "numbered_requirement_anchor":any(m["cue_kind"]=="NUMBERED_REQUIREMENT_CUE" for m in markers if m["editorial_marker_id"] in linked)},
            "review_status":"REVIEW_PENDING","teacher_evidence":None,"proof_verification":"UNVERIFIED",
            "teacher_solution_visibility":"TEACHER_ONLY","student_authoritative":False,
            "official_atom_id":None,"official_atom_certified":False,
            "elective_e_optional_example":track=="ELECTIVE_E",
        })
        taken.add(ident); names.add((track,title))
    obj={
        "schema_version":"kb122-source-anchored-editorials-v1",
        "curriculum_standard":original["curriculum_standard"],
        "original_pdf_sha256":prior.evidence.PDF_SHA,
        "source_text_committed":False,"official_atom_census_complete":False,
        "official_atom_total_denominator":None,"semantic_candidates_not_official_atoms":True,
        "new_candidate_count":len(result),
        "cumulative_editorial_candidate_count":len(prev())+len(result),
        "student_authoritative_count":0,"teacher_approved_count":0,
        "candidates":result}
    validate(obj)
    return obj

def validate(x):
    base=prior.base();pages={p["printed_page"]:p for p in base["pages"]}
    pinned=locks();known={p["id"] for p in prev()}
    demand(x["schema_version"]=="kb122-source-anchored-editorials-v1"
           and x["curriculum_standard"]==base["curriculum_standard"]
           and x["original_pdf_sha256"]==prior.evidence.PDF_SHA
           and x["source_text_committed"] is False
           and x["official_atom_census_complete"] is False
           and x["official_atom_total_denominator"] is None
           and x["semantic_candidates_not_official_atoms"] is True,"forged official census/source")
    demand(x["teacher_approved_count"]==x["student_authoritative_count"]==0,"forged approval")
    demand(x["new_candidate_count"]==len(ROWS)==len(x["candidates"])==32
           and x["cumulative_editorial_candidate_count"]==len(prev())+len(ROWS),"inflated proposal count")
    for r,spec in zip(x["candidates"],ROWS):
        key,track,p,l,kind,title,domain,invalid,dependency,visual=spec
        ident="hs-semantic-pilot-122-"+key.lower()
        deps=[] if dependency is None else ["hs-semantic-pilot-122-"+dependency.lower()]
        expected=[m["editorial_marker_id"] for m in base["markers"] if m["printed_page"]==p and m["source_line"]==l and m["track_hint"]==track]
        src=r["source"]
        kinds=sorted({m["cue_kind"] for m in base["markers"] if m["editorial_marker_id"] in expected})
        demand(r["id"]==ident and ident not in known and r["local_key"]==key
               and r["course_track"]==track and r["kind"]==kind
               and r["proposed_objective"]==title and r["applicability"]==domain
               and r["invalid_use"]==invalid and r["prerequisite_candidate_ids"]==deps
               and all(d in known for d in deps),"editorial identity or math boundary modified "+key)
        demand(r["review_status"]=="REVIEW_PENDING" and r["teacher_evidence"] is None
               and r["proof_verification"]=="UNVERIFIED" and r["teacher_solution_visibility"]=="TEACHER_ONLY"
               and r["student_authoritative"] is False and r["official_atom_id"] is None
               and r["official_atom_certified"] is False,"unreviewed candidate promoted "+key)
        demand(r["elective_e_optional_example"]==(track=="ELECTIVE_E"),"incorrect elective E labelling")
        demand(src["printed_page"]==p and src["physical_page_index"]==p+7
               and src["start_line"]==src["end_line"]==l
               and src["original_pdf_sha256"]==prior.evidence.PDF_SHA
               and src["frozen_page_sha256"]==pages[p]["source_page_sha256"]
               and src["source_span_sha256"]==pinned[key]
               and src["matching_layout_cues"]==expected and bool(expected)
               and src["cue_kinds"]==kinds
               and src["numbered_requirement_anchor"]==("NUMBERED_REQUIREMENT_CUE" in kinds)
               and src["visual_formula_recheck"]==("REQUIRED" if visual or pages[p]["mathematics_image_risk"] else "NOT_FLAGGED"),
               "source/line/hash mismatch "+key)
        demand(prior.evidence.track_at(p,l)==track,"cross-track source "+key)
        known.add(ident)
    return True

def triage(x):
    base=prior.base()
    links=defaultdict(set)
    for c in prev()+x["candidates"]:
        for cue in c["source"]["matching_layout_cues"]:
            links[cue].add(c["id"])
    # Distinguish heading-only evidence from numbered requirement cues.
    unresolved={
        "TOPIC_CUE":("TOPIC_HEADING_NEEDS_CHILD_SCOPE_REVIEW","Review all numbered children; a heading is not an atom"),
        "SUBTOPIC_CUE":("SUBTOPIC_CUE_PENDING_CLAUSE_REVIEW","Inspect clause text: some elective numbered requirements are tagged SUBTOPIC_CUE; split or dedup appropriately"),
        "NUMBERED_REQUIREMENT_CUE":("NUMBERED_REQUIREMENT_AWAITING_EDITORIAL_ATOMIZATION","Human source-text and formula review required"),
    }
    queue=[]
    for m in base["markers"]:
        ids=sorted(links[m["editorial_marker_id"]])
        if ids: status,action="SOURCE_LINKED_EDITORIAL_CANDIDATE","Teacher review; census still incomplete"
        else: status,action=unresolved[m["cue_kind"]]
        queue.append({"cue_id":m["editorial_marker_id"],"cue_kind":m["cue_kind"],
            "printed_page":m["printed_page"],"source_line":m["source_line"],
            "source_line_sha256":m["source_line_sha256"],"course_track":m["track_hint"],
            "status":status,"next_action":action,"linked_candidate_ids":ids,
            "needs_formula_visual_recheck":m["needs_formula_visual_recheck"],
            "official_atom_id":None,"teacher_approved":False,"student_authoritative":False})
    return queue

def coverage(x,q):
    alltracks=sorted(set(prior.TRACKS)|{"ELECTIVE_UNASSIGNED"})
    t=Counter(r["course_track"] for r in q)
    a=Counter(r["course_track"] for r in q if r["linked_candidate_ids"])
    types=Counter(r["status"] for r in q)
    prev_count=Counter(r["course_track"] for r in prev())
    new=Counter(r["course_track"] for r in x["candidates"])
    res={
       "batch":122,"total_layout_cues":405,"total_source_pages":61,
       "cues_linked":sum(bool(r["linked_candidate_ids"]) for r in q),
       "cues_unlinked":sum(not r["linked_candidate_ids"] for r in q),
       "source_cue_dispositions":dict(sorted(types.items())),
       "new_editorial_candidates":len(x["candidates"]),
       "cumulative_editorial_candidates":len(prev())+len(x["candidates"]),
       "official_atom_census_complete":False,"official_atom_total_denominator":None,
       "teacher_approved_count":0,"student_authoritative_count":0,
       "per_track":{k:{"layout_cues":t[k],"linked_cues":a[k],"unlinked_cues":t[k]-a[k],
           "new_editorial_candidates":new[k],"cumulative_editorial_candidates":new[k]+prev_count[k],
           "official_atom_denominator":None,"official_coverage":None,"teacher_approved":0}
           for k in alltracks}}
    demand(len(q)==405 and res["cues_linked"]+res["cues_unlinked"]==405
           and sum(k["layout_cues"] for k in res["per_track"].values())==405,
           "source cue count changed")
    return res

def validate_queue(x,q,c):
    demand(q==triage(x) and c==coverage(x,q),"untracked cue disposition or denominator drift")
    demand(len({r["cue_id"] for r in q})==405,"duplicate source cue")
    for item in q:
        demand(item["official_atom_id"] is None and item["teacher_approved"] is False
               and item["student_authoritative"] is False,"forged cue approval")
    return True

def render(x,q,c):
    lines=["# Batch122: source-locked semantic curriculum proposals + full 405-cue audit","",
           "All proposals are original, teacher-only REVIEW_PENDING. **The seven-track official atom denominator is still UNKNOWN.**",
           "Automated TOPIC/SUBTOPIC/NUMBERED cue kinds are extraction labels, not official knowledge-atom classifications. Some elective numbered clauses are tagged SUBTOPIC_CUE.","",
           f"Linked {c['cues_linked']}/405 layout cues; {c['cues_unlinked']} unlinked; +{x['new_candidate_count']} editorial proposals; {c['cumulative_editorial_candidates']} cumulative proposals.","",
           "|Track|Layout cues|Linked|Unlinked|New proposals|All proposals|Official atom denominator|",
           "|---|---:|---:|---:|---:|---:|---|"]
    for k,v in c["per_track"].items():
        lines.append(f"|{k}|{v['layout_cues']}|{v['linked_cues']}|{v['unlinked_cues']}|{v['new_editorial_candidates']}|{v['cumulative_editorial_candidates']}|UNKNOWN|")
    lines.extend(["","## Cue dispositions (not mathematical atom certification)",""])
    for kind,n in c["source_cue_dispositions"].items(): lines.append(f"- {kind}: {n}")
    lines+=["","## Authored original candidate objectives and failure conditions",""]
    for r in x["candidates"]:
        lines.extend([f"### {r['local_key']} {r['proposed_objective']}",
          f"Track: {r['course_track']}; kind: {r['kind']}; printed page {r['source']['printed_page']} line {r['source']['start_line']}.",
          f"Applicability: {r['applicability']}",
          f"Invalid use: {r['invalid_use']}",""])
    lines+=["",f"Parser source-tag audit: {sum(bool(z['source']['numbered_requirement_anchor']) for z in x['candidates'])} NUMBERED_REQUIREMENT_CUE; {sum(not z['source']['numbered_requirement_anchor'] for z in x['candidates'])} SUBTOPIC_CUE/TOPIC_CUE. This is a regex extraction tag, NOT a human judgment that these are mere headings.","", "## Verification boundaries","",
            "- Local legal-source text stays only on the Mac, digest/source span is frozen, each candidate links an exact source cue, explicitly distinguishing headings from numbered requirements.",
            "- The line-level source witness is not a semantic correctness certification; visual/formula flags remain review requirements.",
            "- No machine generated teaching approvals, no authoritative student indexing, no unsupported general proof claims.",""]
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser()
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write",action="store_true");mode.add_argument("--check",action="store_true")
    ap.add_argument("--freeze-source",action="store_true")
    ap.add_argument("--verify-local-source",action="store_true")
    args=ap.parse_args()
    if args.freeze_source:
        demand(args.write,"freezing requires writing")
        LOCKS.write_text(serial(source_locks_from_mac()),encoding="utf-8")
    x=build()
    if args.verify_local_source: demand(locks()==source_locks_from_mac(),"Mac frozen source line mismatch")
    q=triage(x);c=coverage(x,q);validate_queue(x,q,c)
    for p,v in ((OUT,serial(x)),(QUEUE,serial(q)),(COVER,serial(c)),(REPORT,render(x,q,c))):
        if args.write:p.write_text(v,encoding="utf-8")
        else:demand(p.exists() and p.read_text(encoding="utf-8")==v,"build output drift "+str(p))
    print(f"Batch122: {x['new_candidate_count']} authored, {c['cumulative_editorial_candidates']} cumulative, {c['cues_linked']}/405 linked, {c['cues_unlinked']} unlinked, official denominator UNKNOWN")

if __name__=="__main__":main()
