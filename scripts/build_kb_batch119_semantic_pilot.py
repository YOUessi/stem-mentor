#!/usr/bin/env python3
"""Manually authored semantic candidates; not an official curriculum denominator."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from kb_batch119_semantic_catalog import ROWS
import build_kb_batch118_source_atom_ledger as old
BASE=ROOT/"curriculum/highschool_math/k00_batch118_provisional_marker_ledger.json"
OUT=ROOT/"curriculum/highschool_math/k00_batch119_semantic_atom_pilot.json"
MD=ROOT/"docs/evaluation/KB_BATCH119_SEMANTIC_ATOM_PILOT.md"
MATH=ROOT/"docs/evaluation/KB_BATCH119_MATH_GUARDS.json"
COVER=ROOT/"docs/evaluation/KB_BATCH119_COVERAGE.json"
TRACKS=old.TRACKS
def demand(ok,why):
    if not ok: raise ValueError(why)
def digest(v):return hashlib.sha256(v.encode()).hexdigest()
def formatted(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def source():
    # This is only available on the authorized Mac; never commit its text.
    return {p["printed_page"]:p["lines"] for p in old.source_pages()}
def census():
    data=json.loads(BASE.read_text())
    old.validate(data)
    return data
def build(use_local=False):
    base=census()
    page={p["printed_page"]:p for p in base["pages"]}
    marks=base["markers"]
    old_hash={}
    if OUT.exists():
        old_hash={r["local_key"]:r["source"]["source_span_sha256"]
                  for r in json.loads(OUT.read_text()).get("candidates",[])}
    private=source() if use_local else None
    candidates=[]; seen=set()
    for key,track,p,lo,hi,kind,title,condition,nonexample,visual,prereq in ROWS:
        demand(key not in seen,"duplicate candidate "+key)
        seen.add(key)
        demand(track in TRACKS and kind in ("concept","theorem","method"),"invalid category")
        demand(p in page and 1<=lo<=hi<=page[p]["source_line_count"],"bad source range "+key)
        demand(all(old.track_at(p,l)==track for l in range(lo,hi+1)),"cross-track "+key)
        demand(len(title)>=6 and len(condition)>=7 and len(nonexample)>=10,"incomplete objective "+key)
        if prereq:demand(prereq in seen and prereq!=key,"orphan/forward prerequisite "+key)
        span_hash=digest("\n".join(private[p][lo-1:hi])) if private else old_hash.get(key)
        demand(isinstance(span_hash,str) and bool(re.fullmatch("[0-9a-f]{64}",span_hash)),
               "missing trusted span digest; create with --write --verify-local-source")
        marker_ids=[m["editorial_marker_id"] for m in marks
                    if m["printed_page"]==p and lo<=m["source_line"]<=hi
                    and m["track_hint"]==track]
        candidates.append({
           "id":"hs-semantic-pilot-119-"+key.lower(),"local_key":key,
           "course_track":track,"kind":kind,"proposed_objective":title,
           "applicability":condition,"invalid_use":nonexample,
           "prerequisite_candidate_ids":[("hs-semantic-pilot-119-"+prereq.lower())] if prereq else [],
           "source":{"printed_page":p,"physical_page_index":p+7,"start_line":lo,"end_line":hi,
                     "original_pdf_sha256":old.PDF_SHA,"frozen_page_sha256":page[p]["source_page_sha256"],
                     "source_span_sha256":span_hash,"matching_layout_cues":marker_ids,
                     "visual_formula_recheck":"REQUIRED" if visual else "NOT_FLAGGED"},
           "review_status":"REVIEW_PENDING","teacher_evidence":None,"proof_verification":"UNVERIFIED",
           "teacher_solution_visibility":"TEACHER_ONLY","student_authoritative":False,
           "official_atom_id":None,"official_atom_certified":False,
           "elective_e_optional_example":track=="ELECTIVE_E",
        })
    count=Counter(x["course_track"] for x in candidates)
    used={i for x in candidates for i in x["source"]["matching_layout_cues"]}
    data={"schema_version":"kb119-semantic-pilot-v1",
          "curriculum_standard":base["curriculum_standard"],
          "original_pdf_sha256":old.PDF_SHA,
          "source_text_committed":False,"semantic_editorial_pilot_not_official_census":True,
          "source_cue_total":len(marks),"source_cues_linked":len(used),
          "source_cues_not_linked":len(marks)-len(used),
          "total_semantic_candidates":len(candidates),
          "official_atom_total_denominator":None,"official_atom_census_complete":False,
          "teacher_approved_count":0,"student_authoritative_count":0,
          "by_track":{t:{"pilot_count":count[t],"official_atom_denominator":None,
                         "teacher_approved":0,"whole_track_complete":False} for t in TRACKS},
          "candidates":candidates}
    validate(data)
    return data
def validate(data):
    base=census()
    page={p["printed_page"]:p for p in base["pages"]}
    cues={m["editorial_marker_id"]:m for m in base["markers"]}
    demand(data["schema_version"]=="kb119-semantic-pilot-v1","schema version")
    demand(data["source_text_committed"] is False and
           data["original_pdf_sha256"]==old.PDF_SHA and
           data["semantic_editorial_pilot_not_official_census"] is True,"source/census provenance")
    demand(data["official_atom_total_denominator"] is None and
           data["official_atom_census_complete"] is False,"forged official denominator")
    demand(data["teacher_approved_count"]==data["student_authoritative_count"]==0,
           "forged authority")
    demand(set(data["by_track"])==set(TRACKS),"missing track")
    demand(data["source_cue_total"]==len(cues) and
           data["total_semantic_candidates"]==len(data["candidates"]),"bad census")
    seen=set();linked=set();count=Counter()
    for row in data["candidates"]:
        rid=row["id"]; track=row["course_track"]; src=row["source"]; p=src["printed_page"]
        demand(re.fullmatch(r"hs-semantic-pilot-119-[a-z0-9]+",rid) is not None and rid not in seen,
               "duplicate or illegal ID")
        seen.add(rid)
        demand(track in TRACKS and row["kind"] in ("concept","theorem","method"),"bad type")
        demand(row["review_status"]=="REVIEW_PENDING" and row["teacher_evidence"] is None
               and row["proof_verification"]=="UNVERIFIED"
               and row["teacher_solution_visibility"]=="TEACHER_ONLY"
               and row["student_authoritative"] is False and row["official_atom_id"] is None
               and row["official_atom_certified"] is False,"forged candidate approval")
        demand(len(row["applicability"])>=7 and len(row["invalid_use"])>=10,
               "missing mathematical boundaries")
        demand(p in page and src["original_pdf_sha256"]==old.PDF_SHA and
               src["physical_page_index"]==p+7 and
               src["frozen_page_sha256"]==page[p]["source_page_sha256"],"source identity")
        demand(1<=src["start_line"]<=src["end_line"]<=page[p]["source_line_count"],"source range")
        demand(re.fullmatch("[0-9a-f]{64}",src["source_span_sha256"]) is not None,"source digest")
        demand(src["visual_formula_recheck"] in ("REQUIRED","NOT_FLAGGED"),"visual status")
        demand(all(old.track_at(p,n)==track for n in range(src["start_line"],src["end_line"]+1)),
               "cross-track source line")
        for cid in src["matching_layout_cues"]:
            demand(cid in cues and cues[cid]["printed_page"]==p and
                   src["start_line"]<=cues[cid]["source_line"]<=src["end_line"] and
                   cues[cid]["track_hint"]==track,"invalid cue relation")
            linked.add(cid)
        for dep in row["prerequisite_candidate_ids"]:
            demand(dep in seen and dep!=rid,"orphan/forward prerequisite")
        demand(row["elective_e_optional_example"]==(track=="ELECTIVE_E"),"elective E misclassified")
        count[track]+=1
    demand(data["source_cues_linked"]==len(linked)
           and data["source_cues_not_linked"]==len(cues)-len(linked),"source coverage inflated")
    for t in TRACKS:
        d=data["by_track"][t]
        demand(d["pilot_count"]==count[t] and d["official_atom_denominator"] is None
               and d["teacher_approved"]==0 and d["whole_track_complete"] is False,
               "false official coverage")
    return True
def verify_local(data):
    raw=source()
    for row in data["candidates"]:
        s=row["source"]
        actual=digest("\n".join(raw[s["printed_page"]][s["start_line"]-1:s["end_line"]]))
        demand(actual==s["source_span_sha256"],"private source drift "+row["id"])
def math_checks():
    import sympy as s
    x=s.symbols("x",real=True)
    R=s.Rational
    checks=[
        ("q1_sum",sum([2]*5)==10),
        ("geometric_sum",sum(3*2**k for k in range(4))==45),
        ("cubic_stationary_not_extremum",s.diff(x**3,x).subs(x,0)==0 and (-1)**3<0<1**3),
        ("closed_interval_endpoint",s.maximum(x**2,x,s.Interval(-1,2))==4),
        ("nonindependent_conditional_p0",R(0)==0),
        ("least_squares_sxx_zero",sum((v-3)**2 for v in (3,3,3))==0),
        ("alternating_subsequences",(-1)**10==1 and (-1)**11==-1),
        ("point_value_vs_limit",s.limit(x*x,x,0)==0),
        ("log_domain",s.diff(s.log(1+x),x)==1/(x+1)),
        ("hypergeom_mean",3*R(4,10)==R(6,5)),
        ("total_probability",R(1,3)*R(3,4)+R(2,3)*R(1,4)==R(5,12)),
        ("periodic_sine",s.simplify(s.sin(x+2*s.pi)-s.sin(x))==0),
        ("compound_nominal_vs_effective",(1+R(12,100)/12)**12!=1+R(12,100)),
        ("partial_not_differentiable_diagonal",
         s.limit((x*x)/s.sqrt(2*x*x)/s.sqrt(2*x*x),x,0,dir="+")==R(1,2)),
        ("equal_probability_required",R(1,4)+R(3,4)==1),
    ]
    for name,ok in checks:demand(bool(ok),"exact math witness failed "+name)
    return {"finite_exact_case_count":len(checks),"case_names":[name for name,_ in checks],
            "formal_general_proofs_certified":0,"teacher_approved":0,
            "student_free_text_verified":False,
            "scope":"SELECTED_FINITE_EXACT_CHECKS_NOT_GENERAL_PROOFS"}
def markdown(data,math):
    lines=["# Batch119｜课程语义候选原子先导（不是官方完整分母）","",
      "仅保存自编数学教学目标、数学条件、反例与本机合法来源的行级SHA；不上传课标原文。",
      f"本批 {len(data['candidates'])} 个语义编辑候选，{math['finite_exact_case_count']} 组有限精确核验。",
      f"源排版线索405条，候选绑定{data['source_cues_linked']}条，尚有{data['source_cues_not_linked']}条未关联。",
      "同一来源可以分拆为多个知识类型；跨轨重用知识不得当作不同官方总分母。","",
      "| 轨道 | 本批人工语义候选 | 官方完整原子分母 | 教师审核 |",
      "| --- | ---: | --- | ---: |"]
    for t in TRACKS:lines.append(f"| {t} | {data['by_track'][t]['pilot_count']} | UNKNOWN | 0 |")
    lines+=["","| ID | 轨道 | 源页/行 | 类型 | 目标及前提 | 非例/风险 | 图像风险 |",
      "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in data["candidates"]:
        v=r["source"]
        lines.append(f"| {r['local_key']} | {r['course_track']} | {v['printed_page']}:{v['start_line']}-{v['end_line']} | {r['kind']} | {r['proposed_objective']}：{r['applicability']} | {r['invalid_use']} | {v['visual_formula_recheck']} |")
    lines+=["","## 有效性边界","",
       "- 全部 REVIEW_PENDING / TEACHER_ONLY，未有真实教师验收，不会进入学生端权威检索。",
       "- 证据行哈希只保证可追踪，不保证OCR公式与原图等价。",
       "- E轨只是学校可选择的示例方向，不当作全国必修知识。",
       "- 实际 61 页完整知识拆分、跨页去重、数学一般证明和先修审查仍待继续。",
       ""]
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check",action="store_true")
    p.add_argument("--verify-local-source",action="store_true")
    args=p.parse_args()
    data=build(use_local=args.write or args.verify_local_source)
    math=math_checks()
    cover={"batch":119,"source_cues":405,
           "semantic_pilot_candidates":len(data["candidates"]),
           "per_track_pilot":{t:data["by_track"][t]["pilot_count"] for t in TRACKS},
           "official_atom_denominators":{t:None for t in TRACKS},
           "teacher_approved":0,"student_authoritative_releases":0,
           "whole_curriculum_completed":False,"finite_exact_cases":math["finite_exact_case_count"]}
    files={OUT:formatted(data),MD:markdown(data,math),MATH:formatted(math),COVER:formatted(cover)}
    for path,expected in files.items():
        if args.write:path.write_text(expected)
        else:demand(path.exists() and path.read_text()==expected,"generated artifact drift "+str(path))
    if args.verify_local_source:verify_local(data)
    print(f"Batch119: {len(data['candidates'])} project-authored semantic proposals, {math['finite_exact_case_count']} exact finite checks, all PENDING, official denominator UNKNOWN")
if __name__=="__main__":main()
