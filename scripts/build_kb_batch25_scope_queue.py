#!/usr/bin/env python3
"""K00: source-page work queue across ALL 61 pages, without fake official counts.

Known numbered occurrences, unnumbered themes, project objectives and open
editorial tickets are DIFFERENT, potentially overlapping source categories.
"""
import argparse
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path
from build_kb_batch24_scope import build as old_build, TRACKS

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"curriculum/highschool_math/official_numbered_clause_evidence_batch18.json"
HEADINGS=ROOT/"curriculum/highschool_math/official_unnumbered_de_outline_batch18.json"
OBJECTIVES=ROOT/"curriculum/highschool_math/source_anchored_skill_candidates_batch12.json"
GAPS=ROOT/"curriculum/highschool_math/k00_gap_tickets_batch18.json"
PRIOR=ROOT/"docs/evaluation/KB_BATCH24_SOURCE_CROSSWALK.json"
OUT=ROOT/"docs/evaluation/KB_BATCH25_K00_PAGE_REVIEW_MATRIX.json"
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
    scope=json.loads(old_build())
    if scope!=load(PRIOR):raise ValueError("Source crosswalk changed without baseline review")
    raw=load(SOURCE);head=load(HEADINGS)["items"]; objectives=load(OBJECTIVES)["items"];tickets=load(GAPS)["tickets"]
    markers=raw["enumerated_source_anchors"]
    if (len(markers),len(head),len(objectives),len(tickets))!=(315,23,132,28):
        raise ValueError("Source review candidates changed")
    per_page=defaultdict(lambda:dict(markers=[],headings=[],objectives=[],gaps=[]))
    for m in markers:per_page[m["printed_page"]]["markers"].append(m["id"])
    for h in head:per_page[h["printed_page"]]["headings"].append(h["id"])
    for o in objectives:per_page[o["source"]["printed_page"]]["objectives"].append(o["id"])
    for t in tickets:per_page[t["printed_page"]]["gaps"].append(t["id"])
    pages=[];by_track=Counter()
    page_ids={p["printed_page"] for p in raw["pages"]}
    if set(per_page)-page_ids:raise ValueError("Orphan page references")
    for p in raw["pages"]:
        n=p["printed_page"]; group=per_page[n]
        if len(group["markers"])!=p["source_numbered_marker_count"]:
            raise ValueError("Source page marker count mismatch")
        if any(x not in TRACKS for x in p["tracks_present"]):
            raise ValueError("Unknown official page track")
        for track in p["tracks_present"]:by_track[track]+=1
        pages.append(dict(printed_page=n,pdf_page_index=p["pdf_page_index"],
          source_page_sha256=p["pdf_text_sha256"],candidate_track_labels=p["tracks_present"],
          numbered_marker_ids=sorted(group["markers"]),
          editorial_objective_ids=sorted(group["objectives"]),
          unnumbered_de_heading_ids=sorted(group["headings"]),
          open_editorial_gap_ids=sorted(group["gaps"]),
          numbered_occurrences=len(group["markers"]),
          candidate_count_sum_with_overlap=sum(len(group[k]) for k in group),
          review_priority="P0_NO_NUMBERED_MARKERS_CHECK_UNNUMBERED" if not group["markers"]
             else "P0_MANY_MARKERS_SPLIT_INTO_ATOMS" if len(group["markers"])>=8
             else "P1_EXTRACT_NUMBERED_AND_UNNUMBERED_CLAUSES",
          original_pdf_page_rechecked=False,all_unnumbered_requirements_verified=False,
          teacher_signed_atomic_review=False,review_state="REVIEW_PENDING",
          official_atoms_verified=None,official_page_complete=False))
    if len(pages)!=61 or len({x["printed_page"] for x in pages})!=61:
        raise ValueError("Page denominator mismatch")
    if sum(x["numbered_occurrences"] for x in pages)!=315:
        raise ValueError("Lost numbered marker occurrences")
    if sorted(x["printed_page"] for x in pages)!=list(range(13,74)):
        raise ValueError("PDF printed page coverage [13,73] incomplete")
    return json.dumps(dict(schema_version="kb-batch25-k00-pages-v1",
       scope="ALL_61_SOURCE_PAGES_REVIEW_TASKS_NOT_VERIFIED_OFFICIAL_ATOMS",
       source_sha256={"official_pdf_label":raw["source"]["sha256"],
                      "numbered_ledger":digest(SOURCE),
                      "project_objectives":digest(OBJECTIVES),
                      "unnumbered_de_headings":digest(HEADINGS),
                      "editorial_gaps":digest(GAPS),
                      "prior_crosswalk":digest(PRIOR)},
       summary=dict(pages_queued=61,pages_rechecked_against_original_pdf=0,
         numbered_marker_occurrences=315,project_objective_candidates=132,
         unnumbered_d_e_heading_candidates=23,open_editorial_gap_candidates=28,
         pages_with_no_numbered_markers=sum(not p["numbered_occurrences"] for p in pages),
         pages_with_eight_plus_markers=sum(p["numbered_occurrences"]>=8 for p in pages),
         source_page_labels_per_track=dict(sorted(by_track.items())),
         official_atoms_human_verified=0,verified_official_atomic_denominator=None,
         official_coverage_rate=None),
       pages=pages,tracks=[dict(track=t,numbered_source_marker_candidates=sum(m["track"]==t for m in markers),
            verified_official_atomic_denominator=None,verified_coverage=None,
            full_unnumbered_scan_complete=False,teacher_review="PENDING")
            for t in TRACKS],
       warnings=["Counts from disjoint *data collections* are not disjoint mathematical knowledge atoms.",
                 "The 61 pages come from earlier extraction, NOT a fresh visual review of the original PDF.",
                 "All pages still require independent clause/subclause and prose/table atomization."]),
       ensure_ascii=False,indent=2)+"\n"
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");a=ap.parse_args();v=build()
    if a.check:
        if OUT.read_text(encoding="utf-8")!=v:raise SystemExit("Batch25 page review matrix drift")
    else:OUT.write_text(v,encoding="utf-8")
    print("PASS 61 K00 pages queued, 315 markers, 23 D/E headings; official atoms remain NULL")
if __name__=="__main__":main()
