#!/usr/bin/env python3
"""Batch127: 8 authored REVIEW_PENDING teacher lessons + independent finite exact oracles."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from kb_batch127_deep_catalog import LESSONS
import build_kb_batch125_provenance as provenance
OUT=ROOT/"knowledge/editorial_review/kb_batch127_eight_deep_lessons.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH127_EIGHT_DEEP_LESSONS.md"
CHECKS=ROOT/"docs/evaluation/KB_BATCH127_MATH_WITNESSES.json"
def req(ok,msg):
 if not ok:raise ValueError(msg)
def dump(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def build():
 raw,_,_=provenance.originals();cm={r["id"]:r for r in raw}
 docs=[]
 for l in LESSONS:
  key="hs-semantic-pilot-"+l["key"];s=cm[key]
  req(all(len(l[k])>=24 for k in ("formal","symbols","premises","why","edge","wrong","whywrong","near","far")),"short manuscript "+key)
  req(len(l["steps"])==3 and all(len(a)>=4 and len(b)>=20 for a,b in l["steps"]),"missing justified steps")
  req(len(l["examples"])==2 and all(len(ex["steps"])==2 and len(ex["question"])>=12 and len(ex["answer"])>=2 and len(ex["verification"])>=8 for ex in l["examples"]),"missing worked examples")
  req(len(l["hints"])==3 and all(len(h)>=10 for h in l["hints"]),"missing hint ladder")
  req(s["review_status"]=="REVIEW_PENDING" and s["teacher_evidence"] is None and s["student_authoritative"] is False and s["official_atom_id"] is None,"source not pending")
  docs.append({"id":"kb127-deep-"+l["key"],"candidate_id":key,"course_track":s["course_track"],"kind":s["kind"],
   "title":s["proposed_objective"],"source":s["source"],
   "formal_definition_or_statement":l["formal"],"symbols":l["symbols"],
   "applicability":l["premises"],"reasoning":l["why"],
   "reasoned_steps":[{"step":a,"justification":b} for a,b in l["steps"]],
   "invalid_case":l["edge"],"typical_wrong_solution":l["wrong"],"why_wrong":l["whywrong"],
   "teacher_examples":l["examples"],"student_hint_ladder":l["hints"],
   "near_transfer":l["near"],"far_transfer":l["far"],
   "version":"2020-revision-editorial-batch127",
   "review_status":"REVIEW_PENDING","teacher_evidence":None,
   "proof_machine_certified":False,"student_authoritative":False,
   "teacher_solution_visibility":"TEACHER_ONLY"})
 validate(docs,regen=False)
 return docs
def validate(docs,regen=True):
 req(len(docs)==8 and len({d["candidate_id"] for d in docs})==8,"8 distinct lessons required")
 for d in docs:
  req(d["review_status"]=="REVIEW_PENDING" and d["teacher_evidence"] is None
   and d["proof_machine_certified"] is False and d["student_authoritative"] is False
   and d["teacher_solution_visibility"]=="TEACHER_ONLY" and len(d["teacher_examples"])==2
   and len(d["student_hint_ladder"])==3,"unreviewed content promoted or truncated")
 if regen:req(docs==build(),"teacher manuscript or citation edited")
 return True
def exact_checks():
 R=S.Rational
 x,y=S.symbols("x y",real=True)
 cases={
 "119-c01":[S.solve([2*x-1-5,y+3+2],[x,y])=={x:3,y:-5},
              (1+2*S.I)!=(1-2*S.I) and S.Abs(1+2*S.I)==S.sqrt(5)],
 "119-c06":[len({2,4,6}&{4,5,6})==2 and len({2,4,6}|{4,5,6})==4,
              ({1,3,5}&{2,3})=={3} and len({1,3,5}|{2,3})==4],
 "119-s02":[3+(5-1)*2==11, 10+(6-1)*(-3)==-5 and 10+3*(-3)==1],
 "119-s04":[2*3**(4-1)==54, 81*R(1,3)**3==3],
 "119-a01":[R(1,5)<R(1,4) and all(R(1,n)<=R(1,5) for n in range(5,100)),
             R(2,11)<R(1,5) and all(R(2,n)<=R(2,11) for n in range(11,100))],
 "119-b04":[S.diff(x*x*y+3*y*y,x).subs({x:2,y:1})==4 and S.diff(x*x*y+3*y*y,y).subs({x:2,y:1})==10,
              S.diff(x**3+2*x*y,x).subs({x:1,y:2})==7 and S.diff(x**3+2*x*y,y).subs({x:1,y:2})==2],
 "119-ec03":[all((p or not p) and not(p and not p) for p in [False,True]),
               all(not((p or not p) is False) for p in [False,True])],
 "119-ed03":[S.simplify(2*S.sin(S.pi*(x+4)/2)-2*S.sin(S.pi*x/2))==0,
              S.simplify(S.cos(2*S.pi*(x+3)/3)-S.cos(2*S.pi*x/3))==0]
 }
 negative={
 "119-c01":S.Abs(1+S.I)==S.Abs(1-S.I) and (1+S.I)!=(1-S.I),
 "119-c06":len({2,4,6}|{4,5,6})!=len({2,4,6})+len({4,5,6}),
 "119-s02":3+5*2!=11,
 "119-s04":2*3**4!=54,
 "119-a01":R(1,4)==R(1,4) and not(R(1,4)<R(1,4)),
 "119-b04":S.limit(S.Symbol("t", real=True)**2/(2*S.Symbol("t", real=True)**2),S.Symbol("t", real=True),0)==S.Rational(1,2),
 "119-ec03":any(not p for p in [False,True]) and not all(p for p in [False,True]),
 "119-ed03":S.sin(0)==S.sin(2*S.pi) and 2*S.pi!=0
 }
 # Narrowly check invalid assumptions; no theorem claim from these finite cases.
 cross={
 "119-c01":S.re(2+3*S.I)==2 and S.im(2+3*S.I)==3,
 "119-c06":R(3+3-2,6)==R(2,3),
 "119-s02":sum(3+2*j for j in range(5))==35,
 "119-s04":sum(2*3**j for j in range(4))==80,
 "119-a01":all(R(3,n+2)<R(1,4) for n in range(11,50)),
 "119-b04":S.diff(x*x*y+3*y*y,x,y)==2*x,
 "119-ec03":all(((p or not p)==(not(p and not p))) for p in [False,True]),
 "119-ed03":S.simplify(S.sin(4*x+S.pi/7)-S.sin(4*(x+S.pi/2)+S.pi/7))==0
 }
 req(set(cases)==set(negative)==set(cross)=={l["key"] for l in LESSONS},"oracle coverage")
 req(all(len(v)==2 and all(bool(z) for z in v) for v in cases.values()),"worked math verification failed")
 req(all(bool(z) for z in negative.values()),"boundary math case failed")
 req(all(bool(z) for z in cross.values()),"cross topic math witness failed")
 return {"batch":127,"teacher_review_status":"REVIEW_PENDING","mathematical_witnesses_not_general_proofs":True,
   "exact_worked_examples":16,"independent_negative_cases":8,"cross_topic_checks":8,
   "general_theorems_formally_certified":0,"student_free_steps_certified":0,
   "teacher_approved":0,"student_authoritative":0,
   "per_lesson":{k:{"worked_exact":2,"negative":1,"cross":1} for k in sorted(cases)}}
def render(docs,checks):
 lines=["# Batch127 — 8 original, teacher-review mathematics lessons","",
 "All materials are author-created and REVIEW_PENDING. Formula witnesses are limited exact instances, not formal theorem certification.",""]
 for d in docs:
  lines += ["## "+d["title"],"","Track: "+d["course_track"]+" · "+d["candidate_id"],
   "**Formal statement:** "+d["formal_definition_or_statement"],
   "**Symbols:** "+d["symbols"],"**Scope and premises:** "+d["applicability"],
   "**Why the method/theorem works:** "+d["reasoning"],""]
  for i,s in enumerate(d["reasoned_steps"],1):
   lines.append(f"{i}. **{s['step']}** — {s['justification']}")
  lines += ["","**Boundary / counterexample:** "+d["invalid_case"],
   "**Typical wrong solution:** "+d["typical_wrong_solution"],
   "**Why wrong:** "+d["why_wrong"],""]
  for j,ex in enumerate(d["teacher_examples"],1):
   lines += [f"**Teacher-only example {j}:** "+ex["question"]]
   lines += ["- "+step for step in ex["steps"]]
   lines += ["- Teacher answer: "+ex["answer"],"- Independent exact check: "+ex["verification"],""]
  lines+= ["**Student-only hint ladder:**"]
  lines+= [f"{i}. {hint}" for i,hint in enumerate(d["student_hint_ladder"],1)]
  lines+= ["**Near transfer:** "+d["near_transfer"],"**Far transfer:** "+d["far_transfer"],""]
 lines+= ["## Exact finite test accounting","",dump(checks)]
 return "\n".join(lines)
def main():
 a=argparse.ArgumentParser();g=a.add_mutually_exclusive_group(required=True)
 g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
 opt=a.parse_args();docs=build();math=exact_checks()
 for path,data in ((OUT,dump(docs)),(CHECKS,dump(math)),(REPORT,render(docs,math))):
  if opt.write:path.write_text(data,encoding="utf-8")
  else:req(path.is_file() and path.read_text(encoding="utf-8")==data,"derived content drift "+str(path))
 print("Batch127 8 deep lessons; 16 exact examples + 8 negative + 8 cross checks")
if __name__=="__main__":main()
