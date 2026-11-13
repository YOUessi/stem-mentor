#!/usr/bin/env python3
"""30 original semantic drafts + *all* 405 source-cue review dispositions.

Cues and editorial candidates are not the official course atomic denominator.
This file never exports the licensed source text from the Mac.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch118_source_atom_ledger as evidence
import build_kb_batch119_semantic_pilot as b119
import build_kb_batch120_semantic_expansion as b120
from kb_batch121_editorial_catalog import ROWS
OUT=ROOT/"curriculum/highschool_math/k00_batch121_semantic_editorials.json"
LOCKS=ROOT/"curriculum/highschool_math/k00_batch121_source_locks.json"
QUEUE=ROOT/"docs/evaluation/KB_BATCH121_SOURCE_CUE_DISPOSITIONS.json"
COVER=ROOT/"docs/evaluation/KB_BATCH121_SEVEN_TRACK_COVERAGE.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH121_EDITORIAL_SCOPE.md"
TRACKS=evidence.TRACKS
def demand(v,msg):
    if not v: raise ValueError(msg)
def hash_text(t):return hashlib.sha256(t.encode("utf-8")).hexdigest()
def serial(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def base():
    z=json.loads(evidence.OUT.read_text(encoding="utf-8"))
    demand(evidence.validate(z),"invalid source marker ledger")
    return z
def previous():
    a=json.loads(b119.OUT.read_text(encoding="utf-8"))
    b=json.loads(b120.OUT.read_text(encoding="utf-8"))
    demand(b119.validate(a) and b120.validate(b),"invalid prior semantic candidates")
    return a["candidates"]+b["candidates"]
def local_locks():
    pages={p["printed_page"]:p["lines"] for p in evidence.source_pages()}
    return {row[0]:hash_text(pages[row[2]][row[3]-1]) for row in ROWS}
def locks():
    demand(LOCKS.exists(),"missing separately frozen Mac source line digest manifest")
    x=json.loads(LOCKS.read_text(encoding="utf-8"))
    demand(set(x)=={r[0] for r in ROWS} and all(len(v)==64 for v in x.values()),"bad frozen source locks")
    return x
def build():
    raw=base();prior=previous();sealed=locks()
    pages={x["printed_page"]:x for x in raw["pages"]}
    cues=raw["markers"]
    seen={r["id"] for r in prior}
    titles={(r["course_track"],r["proposed_objective"]) for r in prior}
    draft=[]
    for row in ROWS:
        key,track,p,l,kind,title,domain,invalid,prereq,visual=row
        rid="hs-semantic-pilot-121-"+key.lower()
        demand(rid not in seen and (track,title) not in titles,"duplicate identity/objective "+key)
        demand(track in TRACKS and kind in ("concept","theorem","method"),"bad taxonomy")
        demand(1<=l<=pages[p]["source_line_count"] and evidence.track_at(p,l)==track,"cross-track source "+key)
        demand(len(title)>9 and len(domain)>=22 and len(invalid)>=20,"incomplete math boundary "+key)
        deps=[] if prereq is None else ["hs-semantic-pilot-121-"+prereq.lower()]
        demand(all(dep in seen for dep in deps),"orphan/forward prerequisite "+key)
        matching=[m["editorial_marker_id"] for m in cues
                  if m["printed_page"]==p and m["source_line"]==l and m["track_hint"]==track]
        demand(matching,"no exact source cue "+key)
        item={"id":rid,"local_key":key,"course_track":track,"kind":kind,
              "proposed_objective":title,"applicability":domain,"invalid_use":invalid,
              "prerequisite_candidate_ids":deps,
              "source":{"printed_page":p,"physical_page_index":p+7,"start_line":l,"end_line":l,
                        "original_pdf_sha256":evidence.PDF_SHA,
                        "frozen_page_sha256":pages[p]["source_page_sha256"],
                        "source_span_sha256":sealed[key],
                        "matching_layout_cues":matching,
                        "visual_formula_recheck":"REQUIRED" if visual or pages[p]["mathematics_image_risk"] else "NOT_FLAGGED"},
              "review_status":"REVIEW_PENDING","teacher_evidence":None,
              "proof_verification":"UNVERIFIED","teacher_solution_visibility":"TEACHER_ONLY",
              "student_authoritative":False,"official_atom_id":None,"official_atom_certified":False,
              "elective_e_optional_example":track=="ELECTIVE_E"}
        draft.append(item);seen.add(rid);titles.add((track,title))
    data={"schema_version":"kb121-editorial-proposal-v1",
          "curriculum_standard":raw["curriculum_standard"],"original_pdf_sha256":evidence.PDF_SHA,
          "source_text_committed":False,"semantic_candidates_not_official_atoms":True,
          "official_atom_census_complete":False,"official_atom_total_denominator":None,
          "new_candidate_count":len(draft),"cumulative_editorial_candidate_count":len(prior)+len(draft),
          "teacher_approved_count":0,"student_authoritative_count":0,"candidates":draft}
    validate(data)
    return data

def validate(data):
    raw=base(); prior=previous(); sealed=locks()
    page={p["printed_page"]:p for p in raw["pages"]}
    cue={x["editorial_marker_id"]:x for x in raw["markers"]}
    demand(data["schema_version"]=="kb121-editorial-proposal-v1"
           and data["curriculum_standard"]==raw["curriculum_standard"]
           and data["original_pdf_sha256"]==evidence.PDF_SHA
           and data["source_text_committed"] is False
           and data["semantic_candidates_not_official_atoms"] is True,"source provenance")
    demand(data["official_atom_census_complete"] is False and
           data["official_atom_total_denominator"] is None and
           data["teacher_approved_count"]==data["student_authoritative_count"]==0,"forged authority")
    demand(data["new_candidate_count"]==len(data["candidates"])==len(ROWS)==30
           and data["cumulative_editorial_candidate_count"]==len(prior)+len(ROWS),"inflated census")
    seen={r["id"] for r in prior}
    objectives={(r["course_track"],r["proposed_objective"]) for r in prior}
    for item, spec in zip(data["candidates"],ROWS):
        key,track,p,l,kind,title,domain,invalid,prereq,visual=spec
        rid="hs-semantic-pilot-121-"+key.lower()
        expect_dep=[] if prereq is None else ["hs-semantic-pilot-121-"+prereq.lower()]
        src=item["source"]
        match=[m["editorial_marker_id"] for m in raw["markers"]
               if m["printed_page"]==p and m["source_line"]==l and m["track_hint"]==track]
        demand(item["id"]==rid and rid not in seen and item["local_key"]==key and
               item["course_track"]==track and item["kind"]==kind and
               item["proposed_objective"]==title and item["applicability"]==domain and
               item["invalid_use"]==invalid and item["prerequisite_candidate_ids"]==expect_dep and
               all(x in seen for x in expect_dep),"catalog identity/condition/prerequisite mismatch "+key)
        demand((track,title) not in objectives,"duplicated course objective")
        demand(item["review_status"]=="REVIEW_PENDING" and item["teacher_evidence"] is None and
               item["proof_verification"]=="UNVERIFIED" and item["teacher_solution_visibility"]=="TEACHER_ONLY" and
               item["student_authoritative"] is False and item["official_atom_id"] is None and
               item["official_atom_certified"] is False,"false review certification")
        demand(item["elective_e_optional_example"]==(track=="ELECTIVE_E"),"elective E mislabel")
        demand(src["printed_page"]==p and src["physical_page_index"]==p+7 and
               src["start_line"]==src["end_line"]==l and
               src["original_pdf_sha256"]==evidence.PDF_SHA and
               src["frozen_page_sha256"]==page[p]["source_page_sha256"] and
               src["source_span_sha256"]==sealed[key] and
               src["matching_layout_cues"]==match and len(match)>0 and
               src["visual_formula_recheck"]==("REQUIRED" if visual or page[p]["mathematics_image_risk"] else "NOT_FLAGGED"),"tampered source "+key)
        demand(1<=l<=page[p]["source_line_count"] and evidence.track_at(p,l)==track and
               all(id_ in cue for id_ in match),"cross-track or missing cue")
        seen.add(rid);objectives.add((track,title))
    return True

def review_queue(data):
    raw=base();prev=previous()
    links=defaultdict(set)
    for item in prev+data["candidates"]:
        for cue in item["source"]["matching_layout_cues"]:
            links[cue].add(item["id"])
    entries=[]
    for m in raw["markers"]:
        ids=sorted(links[m["editorial_marker_id"]])
        entries.append({"cue_id":m["editorial_marker_id"],"printed_page":m["printed_page"],
              "source_line":m["source_line"],"source_line_sha256":m["source_line_sha256"],
              "course_track":m["track_hint"],"cue_kind":m["cue_kind"],
              "linked_editorial_candidate_ids":ids,
              "disposition":"EDITORIAL_CANDIDATE_LINKED" if ids else "UNRESOLVED_EDITORIAL_SPLIT_OR_NON_ATOM",
              "remaining_action":"TEACHER_REVIEW_PLUS_OFFICIAL_CENSUS" if ids else "HUMAN_SEMANTIC_TRIAGE_REQUIRED",
              "visual_review_required":m["needs_formula_visual_recheck"],
              "official_atom_id":None,"teacher_approved":False,"student_authoritative":False})
    return entries

def coverage(data,queue):
    total=Counter(x["course_track"] for x in queue)
    linked=Counter(x["course_track"] for x in queue if x["linked_editorial_candidate_ids"])
    review=Counter(x["course_track"] for x in data["candidates"])
    prior=Counter(x["course_track"] for x in previous())
    tracks=sorted(set(TRACKS)|{"ELECTIVE_UNASSIGNED"})
    result={"batch":121,"scope":"61 printed syllabus pages / seven national tracks and elective preamble",
      "total_layout_cues":len(queue),"cues_linked":sum(bool(x["linked_editorial_candidate_ids"]) for x in queue),
      "cues_unresolved":sum(not x["linked_editorial_candidate_ids"] for x in queue),
      "new_editorial_candidates":len(data["candidates"]),
      "cumulative_editorial_candidates":len(previous())+len(data["candidates"]),
      "formal_official_atom_denominators_known":False,"teacher_approved":0,
      "student_authoritative_releases":0,"official_atom_census_complete":False,
      "per_track":{tr:{"source_layout_cues":total[tr],"source_cues_linked":linked[tr],
                       "source_cues_unresolved":total[tr]-linked[tr],
                       "new_editorial_candidates":review[tr],
                       "cumulative_editorial_candidates":review[tr]+prior[tr],
                       "official_atom_denominator":None,"official_coverage_fraction":None,
                       "teacher_approved":0,"student_authoritative":0}
                   for tr in tracks}}
    demand(result["total_layout_cues"]==405 and len(queue)==405,"source denominator drift")
    demand(result["cues_linked"]+result["cues_unresolved"]==405,"unbalanced source cue review")
    demand(sum(z["source_layout_cues"] for z in result["per_track"].values())==405,"unbalanced track assignment")
    demand(sum(z["new_editorial_candidates"] for z in result["per_track"].values())==30,"inflated authored count")
    return result

def validate_queue(data, queue, cov):
    expected=review_queue(data)
    demand(queue==expected,"cue dispositions / source locks tampered")
    demand(cov==coverage(data,queue),"coverage denominator drift")
    demand(len({x["cue_id"] for x in queue})==405,"duplicate source cue")
    for row in queue:
        demand(row["official_atom_id"] is None and row["teacher_approved"] is False and
               row["student_authoritative"] is False,"unreviewed cue promoted to authority")
    return True

def render(data,queue,cov):
    lines=["# Batch121｜七轨课程线索：30条源锚语义草案 + 405条机器可审计处置台账","",
      "本批所有内容为**原创人工候审提案**；未建立正式官方知识原子总分母。405条排版线索、143条候审语义提案均不能视为官方知识点总数。","",
      f"来源线索总数 {cov['total_layout_cues']}；已关联 {cov['cues_linked']}；仍待语义判断 {cov['cues_unresolved']}；本批新增 {cov['new_editorial_candidates']}；累计 {cov['cumulative_editorial_candidates']}。","",
      "|课程轨道|排版线索|已有语义提案关联|待判别线索|新增语义提案|累计语义提案|正式原子分母|",
      "|---|---:|---:|---:|---:|---:|---|"]
    for k,v in cov["per_track"].items():
        lines.append(f"|{k}|{v['source_layout_cues']}|{v['source_cues_linked']}|{v['source_cues_unresolved']}|{v['new_editorial_candidates']}|{v['cumulative_editorial_candidates']}|UNKNOWN|")
    lines+=["","无语义候选关联的排版线索**不是已经判定缺少某个知识点**；标题、重复、跨页续行与真正知识原子必须由编辑/教师区分。E轨当前排版线索已全部关联，但不证明全轨完整。","",
           "## 本批原创提案及失效情形"]
    for r in data["candidates"]:
        lines+=["",f"### {r['id']} · {r['proposed_objective']}",
                f"- 分类：{r['course_track']} / {r['kind']}；课标印刷第{r['source']['printed_page']}页，第{r['source']['start_line']}行；review: REVIEW_PENDING。",
                f"- 适用前提：{r['applicability']}",
                f"- 反例/不可用条件：{r['invalid_use']}"]
    lines+=["","## 审核和发布边界","","- 定义/定理/方法正式采用前仍需人工语义原子化、完整内容、独立数学审校和教师签字。",
            "- 所有正式分母保留 null/UNKNOWN，不将405行线索或143条草案变成课程完成率。",
            "- 来源文本只在已授权Mac私有缓存保留；版本库仅保存页行、哈希、可检查的提案和失败条件。"]
    return "\n".join(lines)+"\n"

def main():
    ap=argparse.ArgumentParser()
    mx=ap.add_mutually_exclusive_group(required=True)
    mx.add_argument("--write",action="store_true");mx.add_argument("--check",action="store_true")
    ap.add_argument("--verify-local-source",action="store_true")
    ap.add_argument("--freeze-source",action="store_true")
    args=ap.parse_args()
    if args.freeze_source:
        demand(args.write,"freeze requires write")
        LOCKS.write_text(serial(local_locks()),encoding="utf-8")
    x=build()
    if args.verify_local_source:
        demand(local_locks()==locks(),"Mac source line SHA drift")
    q=review_queue(x);c=coverage(x,q);validate_queue(x,q,c)
    files={OUT:serial(x),QUEUE:serial(q),COVER:serial(c),REPORT:render(x,q,c)}
    for path,value in files.items():
        if args.write:path.write_text(value,encoding="utf-8")
        else:demand(path.exists() and path.read_text(encoding="utf-8")==value,
                    "output tamper/build drift "+str(path))
    print(f"Batch121: {len(x['candidates'])} review proposals, {c['cues_linked']}/405 cues linked, {c['cues_unresolved']} unresolved, official denominators UNKNOWN")

if __name__=="__main__":main()
