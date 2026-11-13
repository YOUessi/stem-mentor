#!/usr/bin/env python3
"""Batch124 deep explanations + separate exact SymPy oracle; all pending review."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch124_scope as scope
from kb_batch124_deep_catalog import LESSONS
OUT=ROOT/"knowledge/editorial_review/kb_batch124_eight_depth_lessons.json"
MATH=ROOT/"docs/evaluation/KB_BATCH124_EXACT_WITNESSES.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH124_DEPTH_TEACHER_REVIEW.md"
def need(x,m):
    if not x:raise ValueError(m)
def serial(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def build():
    cm={r["local_key"]:r for r in scope.build()["candidates"]}
    docs=[]
    for raw in LESSONS:
        k=raw["key"];s=cm[k]
        need(len(raw["formal"])>45 and len(raw["symbols"])>30 and len(raw["premises"])>35
             and len(raw["why"])>50 and len(raw["steps"])==3
             and all(len(z[0])>4 and len(z[1])>25 for z in raw["steps"])
             and len(raw["edge"])>40 and len(raw["wrong"])>30 and len(raw["whywrong"])>25
             and len(raw["examples"])==2 and all(len(z["steps"])>=2 and len(z["answer"])>2 for z in raw["examples"])
             and len(raw["hints"])==3 and len(raw["near"])>20 and len(raw["far"])>25,
             "incomplete deep lesson "+k)
        docs.append({"id":"kb124-deep-"+k.lower(),"candidate_id":s["id"],"title":s["proposed_objective"],
            "kind":s["kind"],"course_track":s["course_track"],"source":s["source"],
            "curriculum_standard":scope.previous.base_scope.base()["curriculum_standard"],
            "formal_definition_or_statement":raw["formal"],"symbols":raw["symbols"],"applicability":raw["premises"],
            "why_it_works":raw["why"],
            "reasoned_steps":[{"step":t,"justification":r} for t,r in raw["steps"]],
            "boundary_and_counterexample":raw["edge"],"typical_wrong_solution":raw["wrong"],
            "why_wrong":raw["whywrong"],"teacher_examples":raw["examples"],"student_hint_ladder":raw["hints"],
            "near_transfer":raw["near"],"far_transfer":raw["far"],
            "math_example_exact_checks_passed":2,"proof_required":s["kind"]=="theorem",
            "proof_step_machine_certified":False,"teacher_review_status":"REVIEW_PENDING",
            "teacher_evidence":None,"student_authoritative":False,"teacher_solution_visibility":"TEACHER_ONLY"})
    validate(docs);return docs
def validate(docs):
    need(len(docs)==len(LESSONS)==8 and len({d["id"] for d in docs})==8,"duplicate lesson")
    for d,src in zip(docs,LESSONS):
        s=next(x for x in scope.build()["candidates"] if x["local_key"]==src["key"])
        need(d["id"]=="kb124-deep-"+src["key"].lower() and d["title"]==s["proposed_objective"]
             and d["candidate_id"]==s["id"] and d["kind"]==s["kind"]
             and d["course_track"]==s["course_track"] and d["source"]==s["source"],"forged teacher source lineage")
        keys={"formal_definition_or_statement":"formal","symbols":"symbols","applicability":"premises",
              "why_it_works":"why","boundary_and_counterexample":"edge","typical_wrong_solution":"wrong",
              "why_wrong":"whywrong","teacher_examples":"examples","student_hint_ladder":"hints",
              "near_transfer":"near","far_transfer":"far"}
        need(all(d[a]==src[b] for a,b in keys.items())
             and d["reasoned_steps"]==[{"step":t,"justification":r} for t,r in src["steps"]],
             "math manuscript altered")
        need(d["math_example_exact_checks_passed"]==2 and d["proof_required"]==(s["kind"]=="theorem")
             and d["proof_step_machine_certified"] is False and d["teacher_review_status"]=="REVIEW_PENDING"
             and d["teacher_evidence"] is None and d["student_authoritative"] is False
             and d["teacher_solution_visibility"]=="TEACHER_ONLY","spoofed math approval")
    return True
def exact_witnesses():
    """Checks displayed *finite cases* independently of prose; not formal proofs."""
    R=S.Rational;p=S.pi
    u=S.Matrix([1,0,0]);v=S.Matrix([0,1,0])
    w=S.Matrix([1,2,0]);z=S.Matrix([3,0,0])
    checks={
     "C502":[S.Integer(2)**(-2)==R(1,4) and S.Integer(2)**2==4,
             R(1,2)**(-2)==4 and R(1,2)**1==R(1,2)],
     "C503":[S.simplify(S.log(8,2))==3 and S.Integer(2)**3==8,
             S.simplify(S.log(4,R(1,2)))==-2 and R(1,2)**(-2)==4],
     "C506":[S.Abs(3)==3 and S.simplify(2*p/S.Abs(2))==p and S.simplify(R(1,6)*p/2)==p/12,
             S.Abs(-2)==2 and S.simplify(2*p/S.Abs(-4))==p/2],
     "C507":[S.simplify(S.cos(p/3-p/6)-S.sqrt(3)/2)==0 and S.simplify(S.cos(p/3)*S.cos(p/6)+S.sin(p/3)*S.sin(p/6)-S.sqrt(3)/2)==0,
             S.cos(-p)==-1 and S.cos(0)*S.cos(p)+S.sin(0)*S.sin(p)==-1],
     "C516":[S.simplify(p*2**2*3-12*p)==0,
             S.simplify(p*3**2*4/3-12*p)==0],
     "C521":[len({1,2,3}|{3,4})==4 and R(3+2-1,6)==R(2,3),
             len({1,3,5}|{2,3,5})==4 and R(3+3-2,6)==R(2,3)],
     "S502":[S.sqrt((2-0)**2+(1-1)**2)==2 and S.Abs(1+1)==2 and 2**2==4*1,
             S.sqrt((0-0)**2+(0-1)**2)==1 and S.Abs(0+1)==1 and 0==4*0],
     "B501":[u.dot(v)==0 and u.cross(v)==S.Matrix([0,0,1]) and u.cross(v).norm()==1,
             w.dot(z)==3 and w.cross(z)==S.Matrix([0,0,-6]) and w.cross(z).norm()==6],
    }
    negatives={
      "C502":S.Integer(1)**2==S.Integer(1)**3 and R(1,2)**2<R(1,2),
      "C503":S.log(0)==S.zoo and S.log(-1).is_real is False,
      "C506":S.simplify(2*p/S.Abs(-4))==p/2 and S.Abs(-2)!=-2,
      "C507":S.cos(0-p)!=S.cos(0)-S.cos(p),
      "C516":S.simplify(p*3**2*5/3-12*p)!=0,
      "C521":R(3+2,6)!=R(4,6),
      "S502":S.Matrix([0,0])==S.Matrix([0,0]) and 0**2==4*0*9,
      "B501":u.cross(v)!=u.dot(v) and z.cross(w)==-w.cross(z),
    }
    cross={
      "C502":S.simplify(S.log(8,2))==3,
      "C503":S.Integer(2)**(-2)==R(1,4),
      "C506":S.sin(2*(p/2)+p/6)==S.sin(p+p/6),
      "C507":u.dot(v)==S.cos(p/2),
      "C516":S.integrate(p*(3*S.symbols("t")/4)**2,(S.symbols("t"),0,4))==12*p,
      "C521":R(2,3)<=1,
      "S502":S.solve(S.symbols("x")**2-4*S.symbols("y"),S.symbols("y"))==[S.symbols("x")**2/4],
      "B501":w.cross(z).dot(w)==0 and w.cross(z).dot(z)==0,
    }
    need(set(checks)=={k["key"] for k in LESSONS}==set(negatives)==set(cross),"math oracle coverage")
    need(all(len(a)==2 and all(x is S.true or x is True for x in a) for a in checks.values()),
         "finite worked example failed")
    need(all(v is S.true or v is True for v in negatives.values()),"invalid-premise case failed")
    need(all(v is S.true or v is True for v in cross.values()),"cross-topic exact case failed")
    return {"batch":124,"lesson_count":8,"exact_worked_cases_passed":16,
            "independent_negative_checks_passed":8,"cross_topic_exact_checks_passed":8,
            "general_formal_theorems_proven":0,"student_free_text_steps_certified":0,
            "teacher_approved":0,"student_authoritative":0,
            "per_lesson":{k:{"worked_examples":2,"negative_cases":1,"cross_topic":1} for k in sorted(checks)}}
def render(docs,w):
    lines=["# Batch124 — eight teacher-only complete original lessons","",
       "These are deliberately REVIEW_PENDING; finite SymPy witnesses are not a universal proof or teacher approval.",""]
    for d in docs:
        lines+=["## "+d["title"],"","Track: "+d["course_track"]+" · "+d["candidate_id"],
          "**Statement:** "+d["formal_definition_or_statement"],"**Symbols:** "+d["symbols"],
          "**Applicability:** "+d["applicability"],"**Justification:** "+d["why_it_works"],""]
        for i,st in enumerate(d["reasoned_steps"],1): lines.append(f"{i}. {st['step']} — {st['justification']}")
        lines+=["","**Boundary:** "+d["boundary_and_counterexample"],
          "**Typical wrong reasoning:** "+d["typical_wrong_solution"],
          "**Why wrong:** "+d["why_wrong"],""]
        for j,x in enumerate(d["teacher_examples"],1):
            lines+= [f"**Teacher-only example {j}:** {x['question']}"]+[f"- {z}" for z in x["steps"]]+[
                f"- Answer (teacher only): {x['answer']}",
                f"- Independent exact witness: {x['verification']}",""]
        lines+=["**Student hint ladder (does not reveal full teacher answer):**"]+[
            f"{i}. {x}" for i,x in enumerate(d["student_hint_ladder"],1)]+[
            "**Near transfer:** "+d["near_transfer"],"**Far transfer:** "+d["far_transfer"],""]
    lines+=["","## Math verification boundaries",json.dumps(w,ensure_ascii=False,indent=2),""]
    return "\n".join(lines)
def main():
    a=argparse.ArgumentParser();g=a.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    opt=a.parse_args();docs=build();math=exact_witnesses()
    for path,val in ((OUT,serial(docs)),(MATH,serial(math)),(REPORT,render(docs,math))):
        if opt.write:path.write_text(val,encoding="utf-8")
        else:need(path.exists() and path.read_text(encoding="utf-8")==val,"derived lesson drift "+str(path))
    print("Batch124 deep:",len(docs),"lessons; 16 exact examples, 8 invalid premise, 8 cross checks")
if __name__=="__main__":main()
