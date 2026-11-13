#!/usr/bin/env python3
"""Batch109: original theorem/concept/method drafts, guarded evidence crosswalk."""
from __future__ import annotations
import argparse,json,sys,re
from collections import Counter
from hashlib import sha256
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch109_lesson_authoring import UNITS
from build_kb_batch109_scope import build as scope_build,serialize
from app.deep_knowledge import DEEP_DIR,DeepLesson,curriculum,lessons
PACK=DEEP_DIR/"batch109_function_probability.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH109_LESSONS_AUDIT.json"
MD=ROOT/"docs/evaluation/KB_BATCH109_LESSONS.md"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
        "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
DEPENDENCIES={1:[0],2:[0],3:[0],4:[0],5:[0],9:[8]}

def need(ok,msg):
    if not ok:raise ValueError(msg)

def build(units=UNITS):
    source=scope_build()
    anchors={r["key"]:r for r in source["candidates"]}
    mapping={r["id"]:r for r in curriculum()}
    need(len(units)==10,"must have 10 independently authored complete lessons")
    keys=[u.get("source_key") for u in units]
    need(len(set(keys))==10 and set(keys)<=set(anchors),"unknown/duplicate source link")
    prior=[]
    for path in sorted(DEEP_DIR.glob("*.json")):
        if path==PACK:continue
        # Freeze Batch109 counts when future batches are added.
        later=re.match(r"batch(\d+)",path.name)
        if later and int(later.group(1))>109:continue
        prior.extend(json.loads(path.read_text(encoding="utf8")))
    prior_ids=[r["id"] for r in prior]
    need(len(set(prior_ids))==len(prior_ids),"duplicate historical lesson ID")
    docs=[];links=[]
    for i,u in enumerate(units,1):
        need(u["curriculum_id"] in mapping,"unknown engineering mapping")
        need(u["kind"] in {"theorem","method","concept"},"unknown knowledge type")
        need(len(u["statement"])>=35 and len(u["assumptions"])>=2
             and len(u["notation"])>=2 and len(u["prereqs"])>=2,"thin math prerequisites")
        need(len(u["reasoning"])>=3,"missing proof or method justification")
        if u["kind"]=="theorem":
            need(all(len(claim)>=20 and len(reason)>=20 for claim,reason in u["reasoning"]),
                 "unreasoned proof step")
        else:
            need(all(type(s)==str and len(s)>=20 for s in u["reasoning"]),
                 "thin concept/method rationale")
        need(len(u["negative"])==3 and all(len(s)>=20 for s in u["negative"]),
             "missing concrete counterexample, mistake or explanation")
        need(len(u["examples"])==2 and all(
             len(e["steps"])>=2 and len(e["check"])>=12
             for e in u["examples"]),"missing two verified teacher worked examples")
        need(len(u["hints"])==3 and len(set(u["hints"]))==3
             and all(len(s)>=13 for s in u["hints"]),"invalid no-answer hint ladder")
        need(len(u["near"])>=12 and len(u["far"])>=12,
             "missing near/far transfer")
        src=anchors[u["source_key"]]
        need(src["page"] in (19,56) and src["track_hint"]==("COMPULSORY" if src["page"]==19 else "ELECTIVE_A"),
             "lesson/source curricular track inconsistency")
        need((src["page"]==19)==(mapping[u["curriculum_id"]]["level"]=="必修"),
             "compulsory editorial item cannot map to a noncompulsory engineering ID")
        need(src["math_witness"]["status"]=="FINITE_EXACT_INSTANCE_ONLY",
             "math witness unavailable or incorrectly promoted")
        deps=DEPENDENCIES.get(i-1,[])
        need(all(0<=d<i-1 for d in deps),"forward/cyclic lesson prerequisite")
        lesson_id=f"math.hs.batch109.{i:02d}"
        obj=dict(
          id=lesson_id,curriculum_ids=[u["curriculum_id"]],kind=u["kind"],
          title=u["title"],version="1.0.0",notation=u["notation"],
          prerequisites=u["prereqs"],
          prerequisite_lesson_ids=[f"math.hs.batch109.{d+1:02d}" for d in deps],
          definition=u["statement"] if u["kind"]=="concept" else None,
          statement=u["statement"],assumptions=u["assumptions"],
          proof_steps=[{"claim":claim,"reason":reason} for claim,reason in u["reasoning"]]
                     if u["kind"]=="theorem" else [],
          rationale_steps=u["reasoning"] if u["kind"]!="theorem" else [],
          boundaries=u["assumptions"],
          counterexamples=[dict(false_claim=u["negative"][0],
                                example=u["negative"][1],explanation=u["negative"][2])],
          misconceptions=[dict(error=u["negative"][0],why_wrong=u["negative"][2],
                 repair_question="请指出原推理中未满足的前提，并用具体反例或计算解释怎样修复。")],
          worked_examples=u["examples"],hint_ladder=u["hints"],
          transfer={"near":u["near"],"far":u["far"]},
          provenance={"kind":"PROJECT_AUTHORED","permission":"PROJECT_AUTHORED",
             "curriculum_standard":"普通高中数学课程标准（2017年版2020年修订）",
             "standard_url":"https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf",
             "author_role":"PROJECT_AUTHOR"},
          review={"status":"REVIEW_PENDING","reviewer_id":None,
                  "reviewed_at":None,"review_record":None},
          teacher_solution_visibility="TEACHER_ONLY")
        DeepLesson.model_validate(obj)
        docs.append(obj)
        links.append({"lesson_id":lesson_id,"source_candidate_id":src["id"],
                      "source_key":u["source_key"],"source_printed_page":src["page"],
                      "source_pdfkit_sha256":src["source_page_pdfkit_sha256"],
                      "source_track_hint":src["track_hint"],
                      "engineering_curriculum_id":u["curriculum_id"],
                      "engineering_level":mapping[u["curriculum_id"]]["level"],
                      "official_math_atom_id":None,"teacher_approved":False,
                      "general_proof_certified":False})
    need(not set(d["id"] for d in docs)&set(prior_ids),"duplicate deep lesson IDs")
    counts=Counter(d["kind"] for d in docs)
    cross_level=Counter(r["engineering_level"] for r in links)
    audit={
      "batch":109,"status":"REVIEW_PENDING","visibility":"TEACHER_ONLY",
      "number_of_new_deep_drafts":len(docs),
      "new_teacher_worked_examples":sum(len(d["worked_examples"]) for d in docs),
      "new_no_answer_hint_levels":sum(len(d["hint_ladder"]) for d in docs),
      "new_near_and_far_transfer_tasks":2*len(docs),
      "new_counterexamples":len(docs),"new_finite_math_witnesses":len(docs),
      "new_proof_step_candidates":sum(len(d["proof_steps"]) for d in docs),
      "new_prerequisite_id_edges":sum(len(d["prerequisite_lesson_ids"]) for d in docs),
      "lesson_type_counts":dict(counts),
      "historical_deep_lessons":len(prior),"all_deep_lessons":len(prior)+len(docs),
      "engineering_levels":dict(cross_level),
      "editorial_source_crosswalk":links,
      "official_seven_track_atom_denominators":{t:None for t in TRACKS},
      "teacher_approvals":0,"student_authoritative_releases":0,
      "proof_certificates":0,"arbitrary_student_steps_certified":0,
      "unreviewed_prior_prerequisite_labels":172,
      "uncertified_prior_proof_steps":538,"unresolved_prior_conflicts":10,
      "source_author_sha256":sha256((ROOT/"scripts/kb_batch109_lesson_authoring.py").read_bytes()).hexdigest(),
      "scope_output_sha256":sha256(serialize(source).encode()).hexdigest(),
      "limitations":[
        "6 compulsory-source and 4 elective-A-source proposals map to existing engineering IDs; optional expansion mappings do not promote elective materials into compulsory coverage.",
        "Proof steps are mathematical drafts for independent review; bounded witnesses cannot certify universal claims.",
        "All teacher solutions remain excluded from student RAG and self-challenge.",
        "Neither lesson count nor engineering ID count is a frozen official seven-track atom denominator."]
    }
    return docs,audit

def markdown(docs,audit):
    lines=["# Batch109｜十份函数、概率统计原创完整讲义（教师候审）","",
           "全部REVIEW_PENDING / TEACHER_ONLY；教师证明步骤仍待独立审查。","",
           f"新增{len(docs)}份深度候审讲义、{audit['new_teacher_worked_examples']}道教师分步例题、"
           f"{audit['new_no_answer_hint_levels']}级不剧透提示及"
           f"{audit['new_near_and_far_transfer_tasks']}项迁移练习。",""]
    for d,link in zip(docs,audit["editorial_source_crosswalk"]):
        lines.extend([f"## {d['id']}｜{d['title']}","",
          f"来源候选：{link['source_candidate_id']}；工程映射{link['engineering_curriculum_id']}（"
          f"{link['engineering_level']}），并非正式原子归属。","",
          "**正式陈述：** "+d["statement"],"",
          "**定义与条件：** "+"；".join(d["assumptions"]),"",
          "**记号：** "+"；".join(d["notation"]),"",
          "**先修：** "+"；".join(d["prerequisites"]),""])
        if d["proof_steps"]:
            for j,p in enumerate(d["proof_steps"],1):
                lines.extend([f"**证明第{j}步：** {p['claim']}","**依据：** "+p["reason"],""])
        else:
            for j,s in enumerate(d["rationale_steps"],1):
                lines.extend([f"**概念/方法解释第{j}步：** {s}",""])
        ce=d["counterexamples"][0]
        lines.extend(["**典型错误：** "+ce["false_claim"],"",
                      "**具体反例：** "+ce["example"],"",
                      "**失效原因：** "+ce["explanation"],""])
        for j,e in enumerate(d["worked_examples"],1):
            lines.extend([f"### 教师例题{j}",e["question"],"",
                          *[f"{k}. {s}" for k,s in enumerate(e["steps"],1)],
                          "","**教师答案：** "+e["answer"],"",
                          "**独立代入检查：** "+e["check"],""])
        lines.extend(["**提示阶梯：** "+"；".join(d["hint_ladder"]),"",
                      "**近迁移：** "+d["transfer"]["near"],"",
                      "**远迁移：** "+d["transfer"]["far"],""])
    return "\n".join(lines).rstrip()+"\n"

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    args=p.parse_args();docs,audit=build()
    outputs=((PACK,serialize(docs)),(AUDIT,serialize(audit)),(MD,markdown(docs,audit)))
    if args.check:
        for path,value in outputs:need(path.read_text(encoding="utf8")==value,f"drift {path}")
    else:
        for path,value in outputs:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(value,encoding="utf8")
    print(f"Batch109 lessons: {len(docs)} full teacher drafts, {audit['new_teacher_worked_examples']} examples, "
          f"{audit['new_proof_step_candidates']} proof-step candidates; PASS")

if __name__=="__main__":main()
