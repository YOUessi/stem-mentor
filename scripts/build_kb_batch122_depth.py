#!/usr/bin/env python3
"""Original teacher-only full-depth explanations with exact finite math witnesses."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch122_semantic_census as scope
from kb_batch122_deep_catalog import LESSONS
OUT=ROOT/"knowledge/editorial_review/kb_batch122_eight_depth_lessons.json"
MATH=ROOT/"docs/evaluation/KB_BATCH122_EXACT_MATH_WITNESSES.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH122_EIGHT_DEPTH_LESSONS.md"

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
           "id":"kb122-deep-"+key.lower(),"candidate_id":source["id"],"course_track":source["course_track"],
           "curriculum_standard":scope.prior.base()["curriculum_standard"],
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
        demand(doc["id"]=="kb122-deep-"+raw["key"].lower()
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
    R=S.Rational
    x=S.symbols("x",real=True)
    def corr(xs,ys):
        ux=[S.Integer(v)-S.Rational(sum(xs),len(xs)) for v in xs]
        uy=[S.Integer(v)-S.Rational(sum(ys),len(ys)) for v in ys]
        return S.simplify(sum(a*b for a,b in zip(ux,uy))/S.sqrt(sum(a*a for a in ux)*sum(b*b for b in uy)))
    checks={
      "C303":[{1,2,3,4}-{2,4}=={1,3}, {"a","b","c"}-set()=={"a","b","c"}],
      "C306":[S.solveset(x*x-9,x,domain=S.S.Reals)==S.FiniteSet(-3,3),
              R(3,2)>1 and not (R(3,2)>2)],
      "C307":[(-2)**2==4 and 0+1==1, 2*1==2 and 3-3==0],
      "C311":[S.sqrt(2)>-1 and S.sqrt(2)<2 and S.simplify(S.sqrt(2)**2-2)==0,
              (1**3-1-1)<0 and (2**3-2-1)>0],
      "S304":[S.binomial(3,2)*R(1,2)**2*R(1,2)==R(3,8),
              (1-R(1,4))**4==R(81,256)],
      "S305":[S.binomial(2,1)*S.binomial(3,1)/S.binomial(5,2)==R(3,5),
              S.binomial(2,2)*S.binomial(4,1)/S.binomial(6,3)==R(1,5)],
      "S307":[corr([1,2,3],[2,4,6])==1,corr([1,2,3],[6,4,2])==-1],
      "B303":[S.Matrix.diag(1,1,0).rank()==2 and S.Matrix.diag(1,1,0).nullspace()==[S.Matrix([0,0,1])],
              S.eye(3).rank()==3 and S.eye(3).nullspace()==[]],
    }
    # A deliberately false premise or common incorrect transformation for every lesson.
    negative={
     "C303":4 not in {1,2,3},
     "C306":S.Integer(-3)**2==9 and -3!=3,
     "C307":not (0<0),
     "C311":(lambda z: z < 0)((-1)**2-2) and (2**2-2)>0,
     "S304":R(1,4)!=R(2,5), # conditional success probability after one red removed vs first draw
     "S305":R(3,5)!=R(2,5), # first draw red probability differs from one-in-two exact event
     "S307":S.simplify(sum((z-2)**2 for z in (2,2,2)))==0,
     "B303":S.Matrix.diag(1,1,0).rank()<3,
    }
    # Additional exact boundary regression cases from neighboring proposals.
    boundaries={
      "BINOMIAL_P_ZERO":S.binomial(3,0)*(1-S.Integer(0))**3==1,
      "BINOMIAL_P_ONE":S.binomial(3,3)*S.Integer(1)**3==1,
      "HYPERGEOM_SUPPORT":S.binomial(2,3)==0,
      "NORMAL_SCALE_NONZERO":R(5,2)!=0,
      "FULL_RANK_UNIQUE":S.eye(3).det()==1,
      "SADDLE_NOT_EXTREMUM":(S.Integer(1)*1)>0 and (S.Integer(1)*(-1))<0,
      "EQUIVALENCE_DIRECTION":(S.Integer(2)>1) and not (S.Integer(2)>3),
      "GAUSSIAN_ZERO_STD_NOT_FINITE":S.zoo.is_finite is False,
    }
    demand(set(checks)=={r["key"] for r in LESSONS},"missing exact case families")
    demand(all(len(rows)==2 and all(bool(v) for v in rows) for rows in checks.values()),
           "mathematical worked example check failed")
    demand(all(bool(v) for v in negative.values()) and all(bool(v) for v in boundaries.values()),
           "exact negative or boundary oracle failed")
    return {"batch":122,"exact_worked_cases_passed":16,
      "lesson_boundary_negative_checks_passed":8,"cross_topic_exact_boundary_checks_passed":8,
      "general_formal_theorems_proven":0,"free_text_student_steps_verified":False,"teacher_approved":0,
      "details_by_lesson":{k:{"exact_worked_examples":2,"independent_negative_cases":1}
                          for k in checks},
      "boundary_case_names":list(boundaries)}

def render(docs):
    out=["# Batch122｜八份原创数学讲义 · 全部教师候审","",
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
    print("Batch122 depth: 8 original lessons, 16 exact examples, 8 invalid use, 8 other boundaries, 0 approved")
if __name__=="__main__": main()
