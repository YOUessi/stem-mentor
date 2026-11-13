#!/usr/bin/env python3
"""Original teacher-only full-depth explanations with exact finite math witnesses."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch123_semantic_census as scope
from kb_batch123_deep_catalog import LESSONS
OUT=ROOT/"knowledge/editorial_review/kb_batch123_eight_depth_lessons.json"
MATH=ROOT/"docs/evaluation/KB_BATCH123_EXACT_MATH_WITNESSES.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH123_EIGHT_DEPTH_LESSONS.md"

def demand(cond,msg):
    if not cond: raise ValueError(msg)
def build():
    candidates={r["local_key"]:r for r in scope.build()["candidates"]}
    docs=[]
    for raw in LESSONS:
        key=raw["key"]; source=candidates[key]
        demand(len(raw["formal"])>=38 and len(raw["symbols"])>=25 and len(raw["applicability"])>=38
               and len(raw["explanation"])>=40 and len(raw["steps"])>=3
               and len(raw["boundary"])>=25 and len(raw["wrong"])>=25
               and len(raw["why_wrong"])>=25 and len(raw["examples"])==2
               and all(len(x["steps"])>=2 and len(x["answer"])>1 for x in raw["examples"])
               and len(raw["hints"])==3 and len(raw["near"])>=18 and len(raw["far"])>=25,
               "incomplete lesson "+key)
        docs.append({
           "id":"kb123-deep-"+key.lower(),"candidate_id":source["id"],"course_track":source["course_track"],
           "curriculum_standard":scope.base_scope.base()["curriculum_standard"],
           "source":source["source"],"kind":source["kind"],"title":source["proposed_objective"],
           "formal_definition_or_statement":raw["formal"],"symbols":raw["symbols"],
           "applicability":raw["applicability"],"why_it_works":raw["explanation"],
           "reasoned_steps":[{"step":step,"justification":why} for step,why in raw["steps"]],
           "boundary_and_counterexample":raw["boundary"],"typical_wrong_solution":raw["wrong"],
           "why_wrong":raw["why_wrong"],"teacher_examples":raw["examples"],
           "student_hint_ladder":raw["hints"],"near_transfer":raw["near"],"far_transfer":raw["far"],
           "proof_required":source["kind"]=="theorem","proof_step_machine_certified":False,
           "math_example_exact_checks_passed":2,"teacher_review_status":"REVIEW_PENDING",
           "teacher_evidence":None,"student_authoritative":False,"teacher_solution_visibility":"TEACHER_ONLY"})
    validate(docs)
    return docs

def validate(rows):
    demand(len(rows)==len(LESSONS)==8 and len({r["candidate_id"] for r in rows})==8,"lesson count/identity")
    candidates={r["local_key"]:r for r in scope.build()["candidates"]}
    for doc,raw in zip(rows,LESSONS):
        source=candidates[raw["key"]]
        demand(doc["id"]=="kb123-deep-"+raw["key"].lower()
               and doc["candidate_id"]==source["id"] and doc["course_track"]==source["course_track"]
               and doc["kind"]==source["kind"] and doc["source"]==source["source"]
               and doc["title"]==source["proposed_objective"],"forged lineage")
        for generated,authored in [
             ("formal_definition_or_statement","formal"),("symbols","symbols"),
             ("applicability","applicability"),("why_it_works","explanation"),
             ("boundary_and_counterexample","boundary"),("typical_wrong_solution","wrong"),
             ("why_wrong","why_wrong"),("teacher_examples","examples"),
             ("student_hint_ladder","hints"),("near_transfer","near"),("far_transfer","far")]:
            demand(doc[generated]==raw[authored],"manuscript tampering "+generated)
        demand(doc["reasoned_steps"]==[{"step":s,"justification":why} for s,why in raw["steps"]],
               "reasoning steps modified")
        demand(doc["teacher_review_status"]=="REVIEW_PENDING" and doc["teacher_evidence"] is None
               and doc["student_authoritative"] is False and doc["teacher_solution_visibility"]=="TEACHER_ONLY"
               and doc["proof_required"]==(source["kind"]=="theorem")
               and doc["proof_step_machine_certified"] is False and doc["math_example_exact_checks_passed"]==2,
               "forged proof/exam authority")
    return True

def exact_witnesses():
    """Independent SymPy exact examples and distinct invalid-premise cases; NOT universal proofs."""
    x=S.symbols("x",real=True); R=S.Rational; M=S.Matrix
    f=x**4-3*x**2;g=x**3-x
    def d_line(A,B,C,cx,cy):return S.Abs(A*cx+B*cy+C)/S.sqrt(A*A+B*B)
    def d_skew(P,u,Q,v):
        w=u.cross(v); demand(w.dot(w)!=0,"parallel direction supplied to skew oracle")
        return S.simplify(S.Abs((Q-P).dot(w))/S.sqrt(w.dot(w)))
    checks={
      "C404":[S.expand(f.subs(x,-x)-f)==0 and f.subs(x,2)==4,
              S.expand(g.subs(x,-x)+g)==0 and g.subs(x,-2)==-6 and g.subs(x,2)==6],
      "C407":[S.simplify(S.log(8,4))==R(3,2) and S.Integer(4)**R(3,2)==8,
              S.simplify(S.log(3,9))==R(1,2) and S.Integer(9)**R(1,2)==3],
      "C410":[R(3,2)**2-2==R(1,4) and R(5,4)**2-2==-R(7,16),
              R(3,2)**3-R(3,2)-1==R(7,8) and R(5,4)**3-R(5,4)-1==-R(19,64)],
      "S402":[d_line(3,4,-25,0,0)==5 and S.simplify(3*3+4*4-25)==0 and 3**2+4**2==25,
              d_line(1,0,-5,1,-2)==4 and 4>2],
      "A401":[S.limit(x*x+3*x,x,2)==10, S.limit((x*x+1)/(x+1),x,1)==1],
      "A403":[M([0,0,1]).dot(M([1,0,-1]))==-1 and M([0,0,1]).dot(M([1,0,0]))==0,
              all(M([0,0,1]).dot(M([1,2,3])+t*M([1,0,0])-M([0,0,3]))==0 for t in (0,1,-9))],
      "B403":[d_skew(M([0,0,0]),M([1,0,0]),M([0,2,3]),M([0,1,0]))==3,
              d_skew(M([0,0,0]),M([1,0,0]),M([0,0,2]),M([0,1,0]))==2],
      "B404":[M.diag(1,2,3).det()==6 and M.diag(1,2,3).rank()==3,
              M.diag(1,1,0).det()==0 and M.diag(1,1,0).rank()==2 and M.diag(1,1,0).nullspace()==[M([0,0,1])]],
    }
    negative={
      "C404":not ((-1) in set(range(0,4))) and S.expand((x*x+x).subs(x,-x)-(x*x+x))!=0,
      "C407":S.log(0) == S.zoo and S.log(1,2)==0,
      "C410": (lambda h: h(-1)<0 and h(1)>0 and all(h(z)!=0 for z in (-1,0,1)))(lambda z: -1 if z<0 else 1),
      "S402": (0**2+0**2)==0,
      "A401": S.limit(x/x,x,0)==1 and S.limit(x,x,0)==0,
      "A403": M([0,0,1]).dot(M([1,0,0]))==0 and M([0,0,1]).dot(M([1,2,3])-M([0,0,0]))!=0,
      "B403": M([1,0,0]).cross(M([2,0,0]))==M([0,0,0]),
      "B404": M.diag(1,1,0)*M([1,2,8])==M([1,2,0]) and M.diag(1,1,0)*M([1,2,0])==M([1,2,0]),
    }
    boundaries={
      "ZERO_VECTOR_INVALID_ANGLE":M([0,0,0]).dot(M([1,0,0]))==0 and M([0,0,0]).norm()==0,
      "ODD_ZERO_NOT_SUFFICIENT":(x*x).subs(x,0)==0 and S.expand((x*x).subs(x,-x)+(x*x))!=0,
      "LOG_BASE_NOT_ONE":S.log(1,2)==0,
      "CIRCLE_B_ZERO_STILL_LINE":d_line(1,0,-5,1,-2)==4,
      "BISECTION_INTERVAL_LENGTH":R(2-1,2**2)==R(1,4),
      "LIMIT_DENOM_ZERO_REQUIRES_OTHER_METHOD":S.limit((x*x-4)/(x-2),x,2)==4,
      "LINE_PLANE_UNIQUE_T":M([0,0,1]).dot(M([1,0,-1]))==-1,
      "SINGULAR_NONHOMOGENOUS_INCONSISTENT":M.diag(1,1,0).rank()==2 and M.diag(1,1,0).row_join(M([1,2,1])).rank()==3,
    }
    demand(set(checks)=={r["key"] for r in LESSONS},"missing math example family")
    demand(all(len(v)==2 and all(bool(z) for z in v) for v in checks.values()),
           "one or more worked examples failed exact SymPy check")
    demand(all(bool(z) for z in negative.values()) and all(bool(z) for z in boundaries.values()),
           "negative/cross-topic exact math witness failed")
    return {"batch":123,"exact_worked_cases_passed":16,"lesson_boundary_negative_checks_passed":8,
       "cross_topic_exact_boundary_checks_passed":8,
       "general_formal_theorems_proven":0,"free_text_student_steps_verified":False,
       "teacher_approved":0,"details_by_lesson":{k:{"exact_worked_examples":2,
       "independent_negative_cases":1} for k in checks},
       "boundary_case_names":list(boundaries)}

def render(docs):
    out=["# Batch123｜八份原创数学讲义 · 全部教师候审","",
         "注意：全部为 REVIEW_PENDING / TEACHER_ONLY。16组SymPy精确示例、8项失败条件和8项跨题边界仅为有限数学核验，不构成一般命题的形式证明或教师认可。",""]
    for r in docs:
        out += [f"## {r['title']}（{r['course_track']}）","",
                "**定义／定理表述**："+r["formal_definition_or_statement"],"",
                "**符号**："+r["symbols"],"",
                "**使用前提**："+r["applicability"],"",
                "**为什么成立**："+r["why_it_works"],""]
        for j,step in enumerate(r["reasoned_steps"],1):
            out += [f"{j}. **{step['step']}**：{step['justification']}"]
        out += ["","**边界条件与反例**："+r["boundary_and_counterexample"],"",
                "**典型错误解法**："+r["typical_wrong_solution"],"",
                "**错误原因**："+r["why_wrong"],"","### 教师示范解答（学生挑战不可直接检索）",""]
        for j,ex in enumerate(r["teacher_examples"],1):
            out += [f"{j}. {ex['question']}","   - 推理："+"；".join(ex["steps"]),
                    "   - 结果："+ex["answer"],"   - 精确检查："+ex["verification"]]
        out+=["","**三级提示**："+" → ".join(r["student_hint_ladder"]),"",
              "**近迁移**："+r["near_transfer"],"",
              "**远迁移**："+r["far_transfer"],""]
    return "\n".join(out).rstrip()+"\n"

def main():
    ap=argparse.ArgumentParser(); mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write",action="store_true");mode.add_argument("--check",action="store_true")
    a=ap.parse_args(); lessons=build(); oracle=exact_witnesses()
    for path,value in ((OUT,scope.serial(lessons)),(MATH,scope.serial(oracle)),(REPORT,render(lessons))):
        if a.write:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(value,encoding="utf-8")
        else:demand(path.exists() and path.read_text(encoding="utf-8")==value,"lesson build drift "+str(path))
    print("Batch123 depth: 8 original lessons, 16 exact examples, 8 invalid use, 8 other boundaries, 0 approved")
if __name__=="__main__": main()
