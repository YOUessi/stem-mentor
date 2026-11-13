#!/usr/bin/env python3
"""K00 page/marker/editorial crosswalk; NEVER an official atomic denominator.

Materializes all 315 machine-extracted numbered markers, 23 optional D/E
unnumbered topic headings, 132 prior editorial samples, and 28 gap decisions.
A same-page association is NOT a semantic match or curricular equivalence.
"""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"curriculum/highschool_math/official_numbered_clause_evidence_batch18.json"
OBJECTIVES=ROOT/"curriculum/highschool_math/source_anchored_skill_candidates_batch12.json"
UNNUMBERED=ROOT/"curriculum/highschool_math/official_unnumbered_de_outline_batch18.json"
TICKETS=ROOT/"curriculum/highschool_math/k00_gap_tickets_batch18.json"
OLD=ROOT/"docs/evaluation/KB_BATCH20_K00_REVIEW_QUEUE.json"
COURSE=ROOT/"curriculum/highschool_math/curriculum_map.json"
OUT=ROOT/"docs/evaluation/KB_BATCH24_SOURCE_CROSSWALK.json"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
def load(path):return json.loads(path.read_text(encoding="utf-8"))
# Versioned source-extraction ledgers are frozen separately from the PDF SHA label.
# A forged 64-hex marker hash or altered candidate text is NOT authentic evidence.
# These pins preserve the reviewed extraction baseline; they do not prove the
# completeness or fidelity of OCR/text extraction against the original PDF.
PINNED_LEDGER_DIGESTS = {'numbered_evidence': '26abbb442d8ebf4c7866af11475a139235efb004d452fe1080c4238996dac53b', 'editorial_sample': '08a13a2ace447b89f630a9135fd3b656b57b5b5db0f16480b814a79a04a699dc', 'unnumbered_de_outline': 'ed44052ad7b2c585a368ace855f7fee9bd0536c8eb379f71df40d57534e77da6', 'editorial_tickets': '5babafd6e7f71ad0b08eba05c88044b39b26ef5f529a8c76e3a890701bf2ecc8', 'frozen_427_task_queue': 'd565148b08a944f34863eb62c6d32967e1dfc7a8d0941fd827f98ee8e0d8668c'}
def canonical_digest(payload):
    return hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def hashfile(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def reconcile(source, objectives, unnumbered, gaps, original, course):
    supplied={"numbered_evidence":source,"editorial_sample":objectives,
              "unnumbered_de_outline":unnumbered,"editorial_tickets":gaps,
              "frozen_427_task_queue":original}
    for name,data in supplied.items():
        if canonical_digest(data)!=PINNED_LEDGER_DIGESTS[name]:
            raise ValueError(f"Frozen source extraction ledger modified: {name}; independent re-review required")
    pages=source["pages"]
    markers=source["enumerated_source_anchors"]
    objs=objectives["items"]; headings=unnumbered["items"];tickets=gaps["tickets"]
    if (source["source"]["sha256"]!=PDF_SHA or
       unnumbered["source_pdf_sha256"]!=PDF_SHA or
       gaps["source_pdf_sha256"]!=PDF_SHA or
       original["source_pdf_sha256"]!=PDF_SHA):
        raise ValueError("Untrusted or inconsistent source PDF SHA")
    if (len(pages),len(markers),len(objs),len(headings),len(tickets),len(original["review_queue"]))!=(61,315,132,23,28,427):
        raise ValueError("Source candidate inventory changed: independent review required")
    if len(set(x["printed_page"] for x in pages))!=61:
        raise ValueError("Missing or duplicate source page")
    page_lookup={p["printed_page"]:p for p in pages}
    def check_item(item,page_field,hash_field):
        page=page_lookup.get(item[page_field])
        if page is None or item[hash_field]!=page["pdf_text_sha256"]:
            raise ValueError("Source-page text hash mismatch")
        if item["track"] not in TRACKS:return False
        return True
    for x in markers:
        if not x["id"].startswith("STD2020-P") or x["status"]!="SOURCE_ENUMERATION_UNREVIEWED_NOT_OFFICIAL_ATOM":
            raise ValueError("Marker asserted false curricular authority")
        if x["printed_page"] not in page_lookup or x["pdf_page_index"]!=page_lookup[x["printed_page"]]["pdf_page_index"]:
            raise ValueError("Marker page/index mismatch")
        if x["track"] not in TRACKS or len(x["line_sha256"])!=64:
            raise ValueError("Invalid track or source-line digest")
        if x["teacher_review"]!="PENDING" or x["approved_lesson_ids"]:
            raise ValueError("False marker teacher approval")
    if not all(check_item(x,"printed_page","page_text_sha256") for x in headings):
        raise ValueError("Bad unnumbered topic track")
    if not all(check_item(x,"printed_page","source_page_text_sha256") for x in tickets):
        raise ValueError("Bad editorial gap source page")
    for obj in objs:
        if obj["track"] not in TRACKS or obj["source"]["printed_page"] not in page_lookup:
            raise ValueError("Unknown objective source page or track")
        if obj["teacher_review"]!="PENDING" or obj["verified_official_atom_id"] is not None or obj["linked_deep_lesson_ids"]:
            raise ValueError("An unreviewed objective was treated as approved/linked")
    if len({x["id"] for x in markers})!=315 or len({x["id"] for x in objs})!=132 or len({x["id"] for x in headings})!=23 or len({x["id"] for x in tickets})!=28:
        raise ValueError("Duplicated marker / objective / heading / gap ID")
    if original["summary"]["official_atomic_denominator"] is not None or any(x["teacher_approved"] for x in original["review_queue"]):
        raise ValueError("Historical K00 approval claim not substantiated")
    # Original PDF markers can coexist on the same physical PDF text line.
    line_groups=defaultdict(list);global_line_groups=defaultdict(list);page_track=defaultdict(list); objectives_page_track=defaultdict(list)
    for x in markers:
        line_groups[(x["printed_page"],x["line_sha256"])].append(x["id"])
        global_line_groups[x["line_sha256"]].append((x["printed_page"],x["id"]))
        page_track[(x["track"],x["printed_page"])].append(x["id"])
    for x in objs:
        objectives_page_track[(x["track"],x["source"]["printed_page"])].append(x["id"])
    same_line_collisions=[
      dict(printed_page=p,line_sha256=d,marker_ids=sorted(ids),marker_count=len(ids),
           status="MULTIPLE_MARKERS_SAME_PDF_TEXT_LINE_REQUIRES_MANUAL_SPLIT")
      for (p,d),ids in sorted(line_groups.items()) if len(ids)>1
    ]
    objectives_rows=[]
    for x in objs:
        candidates=sorted(page_track[(x["track"],x["source"]["printed_page"])])
        objectives_rows.append(dict(
            editorial_objective_id=x["id"],track=x["track"],printed_page=x["source"]["printed_page"],
            section=x["section"],project_editorial_objective=x["editorial_learning_objective"],
            same_page_track_marker_ids=candidates,
            association_status="COLOCATED_ONLY_NOT_SEMANTIC_EQUIVALENCE" if candidates else "UNNUMBERED_OR_UNMATCHED_REVIEW",
            verified_official_atom_id=None,teacher_review="PENDING",student_publishable=False))
    marker_rows=[
      dict(marker_id=x["id"],track=x["track"],printed_page=x["printed_page"],
           pdf_page_index=x["pdf_page_index"],source_line_sha256=x["line_sha256"],
           same_line_marker_ids=sorted(line_groups[(x["printed_page"],x["line_sha256"])]),
           co_page_objective_ids=sorted(objectives_page_track[(x["track"],x["printed_page"])]),
           split_status="REQUIRE_INDEPENDENT_CLAUSE_AND_UNNUMBERED_ATOMIZATION",
           counts_as_official_atom=False,teacher_review="PENDING",student_publishable=False)
      for x in markers
    ]
    level_to_track={"必修":"COMPULSORY","选择性必修":"SELECTIVE_COMPULSORY"}
    counts=Counter()
    for r in course["coverage"]:
        t=level_to_track.get(r["level"],r.get("elective_track","ELECTIVE_UNASSIGNED"))
        counts[t]+=1
    if len(course["coverage"])!=178:raise ValueError("Engineering map unexpectedly changed")
    rows=[]
    for track in TRACKS:
        rows.append(dict(
            track=track,numbered_pdf_marker_candidates=sum(x["track"]==track for x in markers),
            project_authored_editorial_objectives=sum(x["track"]==track for x in objs),
            unnumbered_de_heading_candidates=sum(x["track"]==track for x in headings),
            unresolved_editorial_gap_tickets=sum(x["track"]==track for x in tickets),
            project_engineering_map_rows=counts[track],
            verified_official_atomic_denominator=None,official_coverage_rate=None,
            teacher_approved=0,official_inventory_complete=False))
    if sum(x["numbered_pdf_marker_candidates"] for x in rows)!=315:
        raise ValueError("Suspicious marker audit totals")
    return dict(
        schema_version="batch24-k00-source-crosswalk-v1",scope="PAGE_PROXIMITY_AND_LINE_HASH_ONLY_NOT_OFFICIAL_ATOMIZATION",
        source_pdf_sha256=PDF_SHA,source_provenance={n:hashfile(p) for n,p in [
          ("numbered_evidence",SRC),("editorial_sample",OBJECTIVES),("unnumbered_de_outline",UNNUMBERED),
          ("editorial_tickets",TICKETS),("frozen_427_task_queue",OLD),("engineering_map",COURSE)]},
        summary=dict(source_pdf_pages=61,numbered_marker_occurrences=315,
          distinct_pdf_text_lines_with_markers=len(line_groups),
          multi_marker_same_line_groups=len(same_line_collisions),
          repeated_text_hash_across_pages_groups=sum(len(v)>1 for v in global_line_groups.values()),
          distinct_marker_text_hashes=len(global_line_groups),
          editorial_sample_objectives=132,unnumbered_de_headings=23,
          open_editorial_gap_tickets=28,source_review_tasks_preserved=427,
          engineering_map_rows=178,undocumented_historical_248_marker_claim="NOT_REPRODUCED_FROM_THIS_SOURCE",
          complete_official_atomic_inventory=False,verified_official_atomic_denominator=None,
          official_coverage_rate=None,teacher_approved=0),
        by_track=rows,source_markers=marker_rows,
        project_objective_page_proximities=objectives_rows,
        same_text_line_collisions=same_line_collisions,
        repeated_marker_text_hashes_across_pages=[dict(source_line_sha256=d,
             page_and_marker_ids=sorted((dict(printed_page=p,marker_id=i) for p,i in rows),key=lambda x:(x["printed_page"],x["marker_id"])),
             review_status="REUSED_TEXT_NOT_DUPLICATE_REQUIREMENT")
             for d,rows in sorted(global_line_groups.items()) if len(rows)>1],
        unnumbered_de_headings=[dict(id=x["id"],track=x["track"],printed_page=x["printed_page"],
            source_page_text_sha256=x["page_text_sha256"],split_status="UNNUMBERED_REVIEW_PENDING",
            teacher_review="PENDING",counts_as_verified_atom=False) for x in headings],
        editorial_gap_tickets=[dict(id=x["id"],track=x["track"],printed_page=x["printed_page"],
            status="OPEN_EDITORIAL_CANDIDATE_NOT_PROVEN_MISSING",counts_as_verified_atom=False)
            for x in tickets],
        warnings=[
          "Markers on one physical PDF line may be distinct enumerations; duplicate line hashes are not automatically duplicate curricular requirements.",
          "Same-page and same-track objective associations are NOT textual equivalence and cannot certify any knowledge atom.",
          "Historical 248 marker claim has no primary 248-record ledger in this audit; do not replace 315 with 248 or assert reconciliation.",
          "PDF text extraction may omit non-numbered prose, tables, mathematics, optional E examples and regional requirements.",
          "These machine totals are auditable candidate inventories, never the official atom denominator; all seven verified denominators remain null.",
          "Teacher review remains pending; nobody may turn page proximity, finite examples or AI summaries into APPROVED."])
def build():
    return json.dumps(reconcile(load(SRC),load(OBJECTIVES),load(UNNUMBERED),
       load(TICKETS),load(OLD),load(COURSE)),ensure_ascii=False,indent=2)+"\n"
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    args=p.parse_args();body=build()
    if args.check:
        if OUT.read_text(encoding="utf-8")!=body:raise SystemExit("K00 Batch24 source crosswalk drift")
    else:OUT.write_text(body,encoding="utf-8")
    report=json.loads(body)
    print("PASS: 315 source markers, 132 editorial objectives, 23 D/E headings, 28 open gaps; official atomic denominator NULL; repeated text hash groups",report["summary"]["repeated_text_hash_across_pages_groups"])
if __name__=="__main__":main()
