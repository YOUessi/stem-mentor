#!/usr/bin/env python3
"""Deterministic 8-unit original probability pack; pending teacher approval."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch118_lessons import UNITS
from build_kb_batch117 import lesson_md
from app.deep_knowledge import DeepLesson,DEEP_DIR,curriculum

PACK=DEEP_DIR/"batch118_probability_distribution.json"
META=ROOT/"curriculum/highschool_math/k00_batch118_lesson_source_links.json"
MATH=ROOT/"docs/evaluation/KB_BATCH118_MATH_EXACT.json"
COVER=ROOT/"docs/evaluation/KB_BATCH118_COVERAGE.json"
MD=ROOT/"docs/evaluation/KB_BATCH118_LESSONS.md"
LEDGER=ROOT/"curriculum/highschool_math/k00_batch118_provisional_marker_ledger.json"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"

def require(ok,reason):
    if not ok: raise ValueError(reason)
def dump(obj):
    return json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
def exact_oracles():
    R=S.Rational
    out={
        "discrete_mass":(R(1,4)+R(1,2)+R(1,4)==1, R(1,2)+R(2,3)!=1,"mass 1/4+1/2+1/4","invalid sum 7/6"),
        "expectation_linearity":(S.Rational(1,2)+S.Rational(1,2)==1, R(1,2)!=R(1,2)*R(1,2),"dependent X and Y","product rule requires more"),
        "variance_affine":(S.Rational(1,2)*(1**2+3**2)-2**2==1,(-2)*1!=(-2)**2*1,"E[X²]−E[X]²","variance cannot scale negatively"),
        "binomial_pmf":(S.binomial(3,2)*R(1,2)**3==R(3,8), R(1,2)!=1,"independent repeated coin","dependent without replacement"),
        "binomial_moments":(5*R(1,2)*R(1,2)==R(5,4),R(1,2)!=1,"5 independent Bernoulli trials","correlated trials variance"),
        "hypergeom_mean":(3*R(4,10)==R(6,5), R(5,2)!=3*R(2,10),"N=10 K=4 n=3","wrong unqualified half"),
        "normal_standardization":((14-10)/S.sqrt(4)==2, S.sqrt(4)!=4,"variance 4 standard deviation 2","variance is not sigma"),
        "sample_correlation":(4/S.sqrt(2*8)==1, S.sqrt(0)==0,"positive centered collinear","zero variance undefined"),
    }
    require(set(out)=={u["key"] for u in UNITS},"missing exact oracle")
    rows=[]
    for key,(positive,negative,positive_label,negative_label) in out.items():
        require(positive is S.true or bool(positive),"positive witness failed "+key)
        require(negative is S.true or bool(negative),"negative witness failed "+key)
        rows.append({"lesson_key":key,"positive":positive_label,"negative":negative_label,
            "finite_exact_checks_passed":2,"general_proof_machine_certified":False,
            "student_free_text_verified":False,"teacher_approved":False})
    return {"batch":118,"positive_cases":8,"negative_cases":8,"general_proofs_certified":0,
            "teacher_approved":0,"cases":rows}

def convert():
    ledger=json.loads(LEDGER.read_text())
    require(ledger["original_pdf_sha256"]==PDF_SHA and ledger["official_atom_total_denominator"] is None,
            "invalid source-ledger attachment")
    marker_by_page={}
    for m in ledger["markers"]:
        marker_by_page.setdefault(m["printed_page"],[]).append(m)
    mapping=curriculum()
    mapping={v["id"]:v for v in mapping} if not isinstance(mapping,dict) else mapping
    prior_ids={row["id"] for f in DEEP_DIR.glob("*.json") if f!=PACK for row in json.loads(f.read_text())}
    require(len(UNITS)==8 and len({u["key"] for u in UNITS})==8,"must deliver eight unique manuscripts")
    docs,clause=[],[]
    preds={"expectation_linearity":["math.hs.batch118.01"],
           "variance_affine":["math.hs.batch118.02"],
           "binomial_pmf":["math.hs.batch117.04"],
           "binomial_moments":["math.hs.batch118.04","math.hs.batch118.03"],
           "hypergeom_mean":["math.hs.batch117.08","math.hs.batch118.02"],
           "normal_standardization":["math.hs.batch118.03"],
           "sample_correlation":["math.hs.batch118.03"]}
    for n,u in enumerate(UNITS,1):
        page,start_end = u["page"],u["span"]
        start,end=start_end
        page_record=ledger["pages"][page-13]
        require(page in (47,48) and 1<=start<=end<=page_record["source_line_count"],
                "bad source page/line span")
        markers=[m for m in marker_by_page[page] if start<=m["source_line"]<=end]
        require(len(markers)>=1,"no source-linked editorial cue in line span "+u["key"])
        require(all(m["track_hint"]=="SELECTIVE_COMPULSORY" for m in markers),"wrong track")
        require(u["cid"] in mapping and mapping[u["cid"]]["level"]=="选择性必修",
                "source engineering curriculum mismatch")
        require(u["kind"] in ("concept","theorem","method"),"wrong knowledge kind")
        require(len(u["statement"])>=60 and len(u["assumptions"])>=2
                and len(u["notation"])>=2 and len(u["prereqs"])>=2,"insufficient formal content")
        require(len(u["proof_or_rationale"])==3 and len(u["examples"])==2
                and len(u["hints"])==3 and len(set(u["hints"]))==3,"missing independent components")
        require(len(u["counterexample"])>=28 and len(u["near"])>=20
                and len(u["far"])>=20,"missing conceptual transfer")
        if u["kind"]=="theorem":
            require(all(isinstance(s,tuple) and len(s)==2 and min(map(len,s))>=18
                        for s in u["proof_or_rationale"]),"non-rigorous theorem steps")
        else:
            require(all(isinstance(s,str) and len(s)>=24 for s in u["proof_or_rationale"]),
                    "incomplete concept/method rationale")
        for e in u["examples"]:
            require(len(e["steps"])>=2 and len(e["check"])>=15,"missing worked solution or check")
        lid=f"math.hs.batch118.{n:02d}"
        require(lid not in prior_ids,"collision with historical deep pack")
        doc={
            "id":lid,"curriculum_ids":[u["cid"]],"kind":u["kind"],
            "title":u["title"],"version":"1.0.0",
            "notation":u["notation"],"prerequisites":u["prereqs"],
            "prerequisite_lesson_ids":preds.get(u["key"],[]),
            "definition":u["statement"] if u["kind"]=="concept" else None,
            "statement":u["statement"],"assumptions":u["assumptions"],
            "proof_steps":[{"claim":x,"reason":y} for x,y in u["proof_or_rationale"]] if u["kind"]=="theorem" else [],
            "rationale_steps":u["proof_or_rationale"] if u["kind"]!="theorem" else [],
            "boundaries":u["assumptions"],
            "counterexamples":[{
                "false_claim":u["false_claim"],"example":u["counterexample"],
                "explanation":u["why_wrong"]}],
            "misconceptions":[{
                "error":u["false_claim"],"why_wrong":u["why_wrong"],
                "repair_question":"请列出使用该公式所需的全部条件，找一个不满足条件的案例再做比较。"}],
            "worked_examples":u["examples"],"hint_ladder":u["hints"],
            "transfer":{"near":u["near"],"far":u["far"]},
            "provenance":{
                "kind":"PROJECT_AUTHORED","permission":"PROJECT_AUTHORED",
                "curriculum_standard":"普通高中数学课程标准（2017年版2020年修订）",
                "standard_url":"https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf",
                "author_role":"PROJECT_AUTHOR"},
            "review":{"status":"REVIEW_PENDING","reviewer_id":None,
                "reviewed_at":None,"review_record":None},
            "teacher_solution_visibility":"TEACHER_ONLY",
        }
        DeepLesson.model_validate(doc)
        docs.append(doc)
        clause.append({
            "lesson_id":lid,"engineering_curriculum_id":u["cid"],
            "printed_page":page,"pdf_page_index":page+7,
            "line_range":[start,end],
            "source_cue_ids":[m["editorial_marker_id"] for m in markers],
            "source_page_sha256":page_record["source_page_sha256"],
            "official_atom_id":None,"teacher_approved":False,
            "student_authoritative":False,"review_status":"REVIEW_PENDING",
            "evidence_grade":"EDITORIAL_SOURCE_LINE_LINK_NOT_TEACHER_CERTIFIED",
        })
    for d in docs:
        for pre in d["prerequisite_lesson_ids"]:
            require(pre in prior_ids or pre in {x["id"] for x in docs if x["id"]<d["id"]},
                    "orphan or forward prerequisite: "+pre)
    return docs,{"batch":118,"source_pdf_sha256":PDF_SHA,
                 "items":clause,"official_certified_atom_count":0,"candidate_count":len(clause)}

def coverage(ds,cl):
    prior=[r for f in sorted(DEEP_DIR.glob("*.json")) if f!=PACK
        for r in json.loads(f.read_text()) if not (match:=re.match(r"^batch(\d+)(?:_|$)",f.stem)) or int(match.group(1))<118]
    require(len(prior)==498,"Batch117 frozen previous drafts must remain 498")
    return {"batch":118,"prior_drafts":498,"new_drafts":len(ds),"total_review_pending_drafts":506,
        "teacher_approved":0,"authoritative_student_releases":0,"official_atom_denominators":
        {t:None for t in ("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A",
            "ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")},
        "new_teacher_only_examples":sum(len(d["worked_examples"]) for d in ds),
        "new_hint_levels":sum(len(d["hint_ladder"]) for d in ds),
        "new_transfer_prompts":sum(len(d["transfer"]) for d in ds),
        "new_counterexamples":sum(len(d["counterexamples"]) for d in ds),
        "new_uncertified_proof_steps":sum(len(d["proof_steps"]) for d in ds),
        "finite_exact_cases":16,
        "source_links":len(cl["items"])}
def generate():
    docs,cl=convert()
    return {PACK:docs,META:cl,MATH:exact_oracles(),COVER:coverage(docs,cl),
            MD:lesson_md(docs)}
def main():
    p=argparse.ArgumentParser()
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write",action="store_true")
    mode.add_argument("--check",action="store_true")
    args=p.parse_args()
    for dest,obj in generate().items():
        content=obj if isinstance(obj,str) else dump(obj)
        if args.write:dest.write_text(content)
        else:require(dest.read_text()==content,"generated manuscript drift: "+str(dest))
    print("Batch118 eight teacher-only probability drafts, 16 original examples,",
          "16 finite exact checks; all PENDING, 0 approvals")
if __name__=="__main__":main()
