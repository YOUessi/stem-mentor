#!/usr/bin/env python3
"""Build 20 source-locked original deep teacher drafts and provisional per-track coverage.

All source topics and engineering IDs are project editor mappings, not official atoms.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch99_scope_matrix as B99
import build_kb_batch99_seven_track_guard as TRACK
from kb_batch100_authoring import ROWS,SELECTED
from app.deep_knowledge import DeepLesson,curriculum
from app.kb_batch100_oracles import evaluate

PACK=ROOT/"knowledge/deep/v1/batch100_deep_source_20.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH100_SOURCE_DEPTH_MATRIX.json"
DOC=ROOT/"docs/evaluation/KB_BATCH100_DEEP_LESSONS.md"
AUTH=ROOT/"scripts/kb_batch100_authoring.py"
STANDARD="普通高中数学课程标准（2017年版2020年修订）"
URL="https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf"
# Explicit project engineering *candidates*. Topic semantics remain unverified.
ALIGNMENTS={0:"HS-MATH-074",2:"HS-MATH-124",3:"HS-MATH-124",4:"HS-MATH-124",
 5:"HS-MATH-163",6:"HS-MATH-163",7:"HS-MATH-139",9:"HS-MATH-139",
 10:"HS-MATH-133",11:"HS-MATH-141",12:"HS-MATH-133",13:"HS-MATH-133",
 15:"HS-MATH-134",16:"HS-MATH-167",17:"HS-MATH-133",18:"HS-MATH-138",
 19:"HS-MATH-155",21:"HS-MATH-156",30:"HS-MATH-159",31:"HS-MATH-158"}
# 5 and 6 source ELECTIVE_A, hence HS-MATH-163 applies. 17 has no exact
# three-sector engineering topic in ELECTIVE_B: flag semantic work outstanding.
ALIGNMENTS[17]="HS-MATH-133"
def need(condition,msg):
    if not condition:raise ValueError(msg)
def dump(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"

def build(selected=SELECTED,records=ROWS,alignments=ALIGNMENTS):
    previous,scopes=B99.build()
    source={r["anchor"]:r for r in scopes}
    mapping={r["id"]:r for r in curriculum()}
    need(len(selected)==20 and len(set(selected))==20 and set(selected)==set(records)
         and set(selected)==set(alignments),"must include 20 distinct original authored units")
    need(previous["remaining_without_individual_editorial"]==0
         and previous["completed_full_depth_drafts_pending_teacher"]==66
         and previous["official_atom_denominator"] is None
         and previous["teacher_approved"]==0,"upstream authority drift")
    result=[];links=[]
    for number,index in enumerate(selected,1):
        record=records[index]
        need(index in range(32) and set(record)=={"kind","title","examples","why","notation","prereqs","hints","transfer"},
             "author record fields drift")
        source_item=B99.ROWS[index];anchor=source_item["anchor"]
        need(anchor in source and source[anchor]["source_line_sha256"] and
             source[anchor]["status"]=="INDIVIDUAL_SCOPE_EDITORIAL_PENDING",
             "source SHA or editorial status missing")
        item=source[anchor]
        track=item["source_track"]
        curriculum_id=alignments[index]
        need(curriculum_id in mapping,"unknown engineering curriculum candidate")
        mapped=TRACK.map_engineering_track(mapping[curriculum_id])
        need(mapped is None or track==mapped,"known cross-track curriculum assignment is forbidden")
        need(record["kind"] in {"concept","method","theorem"},"unknown pedagogical kind")
        need(len(record["examples"])==2 and
             all(set(e)=={"question","steps","answer","check"} and
                 len(e["steps"])>=2 and e["answer"] and len(e["check"])>=10
                 for e in record["examples"]),"two independent worked examples required")
        need(len(record["why"])==3 and len(record["hints"])==3 and
             len(record["transfer"])==2,"reasoning, hints or transfer absent")
        theorem=record["kind"]=="theorem"
        proof=[]
        if theorem:
            for step in record["why"]:
                parts=step.split("=>")
                need(len(parts)==2 and len(parts[0])>=20 and len(parts[1])>=12,
                     "theorem proof lacks independent reason")
                proof.append(dict(claim=parts[0],reason=parts[1]))
        else:
            need(all("=>" not in x and len(x)>=20 for x in record["why"]),
                 "method/concept explanations incomplete")
        payload={
          "id":f"math.hs.batch100.{number:02d}",
          "curriculum_ids":[curriculum_id],
          "kind":record["kind"],"title":record["title"],"version":"1.0.0",
          "notation":record["notation"],"prerequisites":record["prereqs"],
          "prerequisite_lesson_ids":[],
          "definition":item["scope"] if record["kind"]=="concept" else None,
          "statement":item["scope"],"assumptions":[item["assumptions"],
              "下列方法或陈述只对上述定义域及非退化条件成立；遇到所列反例必须回到原前提重新判定。"],
          "proof_steps":proof,
          "rationale_steps":[] if theorem else record["why"],
          "boundaries":[item["assumptions"],
                        "来源正例（仅为具体算例，不代表一般证明）："+item["positive"]],
          "counterexamples":[dict(false_claim="不检查前提即可把该性质推广到所有情况。",
                    example=item["nonexample"],
                    explanation="该算例违反前述有效性条件；若遇到该退化情况，不得直接使用原命题。")],
          "worked_examples":record["examples"],
          "misconceptions":[dict(error="直接忽略约束并使用原公式："+item["nonexample"],
                  why_wrong="原式所需数学对象、定义域或非零条件未确认；应检查反例中的实际退化。",
                  repair_question="请从题意列出全部前提，指出此例具体违反了哪一项。")],
          "hint_ladder":record["hints"],
          "transfer":{"near":record["transfer"][0],"far":record["transfer"][1]},
          "provenance":{"kind":"PROJECT_AUTHORED","permission":"PROJECT_AUTHORED",
              "curriculum_standard":STANDARD,"standard_url":URL,"author_role":"PROJECT_AUTHOR"},
          "review":{"status":"REVIEW_PENDING","reviewer_id":None,"reviewed_at":None,
              "review_record":None},"teacher_solution_visibility":"TEACHER_ONLY"
        }
        validated=DeepLesson.model_validate(payload)
        need(validated.review.status=="REVIEW_PENDING","authority escalation")
        checks=evaluate(index)
        need(checks["exact_positive"] and checks["invalid_case_rejected"]
             and checks["general_theorem_certified"] is False,
             "bounded maths check failed")
        result.append(payload)
        links.append({
            "lesson_id":payload["id"],"source_candidate_id":anchor,
            "source_track":track,"source_page":item["source_page"],
            "source_line_sha256":item["source_line_sha256"],
            "source_snapshot_sha256":item["source_snapshot_sha256"],
            "engineering_id":curriculum_id,
            "engineering_topic":mapping[curriculum_id]["concept"],
            "engineering_track":mapped,"engineering_track_status":("MATCH_EDITORIAL_ONLY" if mapped==track else "TRACK_UNRESOLVED"),
            "engineering_topic_alignment":"UNREVIEWED_EDITORIAL_CANDIDATE",
            "official_atom_id":None,"teacher_approved":False,
            "student_authoritative_index_eligible":False,
            "review_status":"REVIEW_PENDING","proof_certified":False,
            "bounded_exact_instance_witness":checks})
    need(len({x["source_candidate_id"] for x in links})==20,"duplicate source")
    updated=[]
    processed={x["source_candidate_id"] for x in links}
    for row in previous["candidates"]:
        row=dict(row)
        if row["candidate_id"] in processed:
            need(row["editorial_stage"]=="INDIVIDUAL_SCOPE_EDITORIAL_PENDING",
                 "cannot upgrade an unaudited source")
            row["editorial_stage"]="FULL_DEEP_DRAFT_PENDING_TEACHER"
            row["batch100_deep_lesson_source_id"]=next(x["lesson_id"] for x in links
                         if x["source_candidate_id"]==row["candidate_id"])
        updated.append(row)
    stages=dict(sorted(Counter(x["editorial_stage"] for x in updated).items()))
    need(stages=={"PAIR_COMPARISON_NOT_ATOMIZED":166,
                 "INDIVIDUAL_SCOPE_NOT_ATOMIZED":24,
                 "INDIVIDUAL_SCOPE_EDITORIAL_PENDING":24,
                 "FULL_DEEP_DRAFT_PENDING_TEACHER":86}, "conservation failure")
    by_track={}
    for track in TRACK.TRACKS:
        group=[x for x in updated if x["track"]==track]
        by_track[track]={"provisional_label_count":len(group),
                "full_drafts_pending_teacher":sum(x["editorial_stage"]=="FULL_DEEP_DRAFT_PENDING_TEACHER" for x in group),
                "official_atom_denominator":None,"approved":0}
    audit={"schema_version":"kb100-20-depth-editor-only-v1",
         "source_baseline_sha256":previous["source_sha256"],
         "source_author_sha256":sha256(AUTH.read_bytes()).hexdigest(),
         "previous_report_sha256":sha256(B99.OUTPUT.read_bytes()).hexdigest(),
         "source_anchors":428,"provisional_labels":300,"full_depth_drafts":86,
         "new_original_deep_drafts":20,"draft_examples":40,
         "graduated_hints":60,"proof_bearing_theorem_drafts":sum(x["kind"]=="theorem" for x in result),
         "finite_math_oracle_count":20,"universally_formal_certificates":0,
         "remaining_without_pairwise_semantic_comparison":134,
         "official_atom_denominator":None,
         "official_atom_denominators_by_track":{k:None for k in TRACK.TRACKS},
         "teacher_atomized_source_pages":"0/61",
         "teacher_approved":0,"student_authoritative_releases":0,
         "remaining_uncertified_historical_proof_steps":538,
         "P0_proof_steps_without_direct_teacher_cards":106,
         "unresolved_math_conflicts":10,
         "stage_counts":stages,"track_counts":by_track,
         "canonical_lesson_source_links":links,"provisional_candidate_matrix":updated}
    return result,audit

def markdown(docs,audit):
    source={x["lesson_id"]:x for x in audit["canonical_lesson_source_links"]}
    lines=["# Batch100｜20份来源锁定原创数学讲义（仅供教师审校）","",
           "**不得自动向学生发布：** 所有文档 REVIEW_PENDING / TEACHER_ONLY，"
           "正式课标七轨原子分母未知，任何有限数值核查并非一般定理证明。","",
           f"已关联原创深度草案 {audit['full_depth_drafts']}，本批新增20；正式教师批准0。",""]
    for d in docs:
        anchor=source[d["id"]]
        lines.extend(["## "+d["id"]+"｜"+d["title"],"",
           "来源锚点："+anchor["source_candidate_id"]+"；纸质页："+str(anchor["source_page"])+
           "；轨道："+anchor["source_track"]+"；行 SHA256："+anchor["source_line_sha256"],"",
           "工程主题候选："+anchor["engineering_id"]+"（语义未人工确认）","",
           "**正式陈述：** "+d["statement"],"",
           "**前提：** "+"；".join(d["assumptions"]), "",
           "**符号：** "+"；".join(d["notation"]), "",
           "**先修文字（非已解析边）：** "+"；".join(d["prerequisites"]), ""])
        if d["definition"]:lines.extend(["**定义：** "+d["definition"],""])
        for j,s in enumerate(d["proof_steps"],1):
            lines.append(f"证明步骤{j}："+s["claim"]+"。理由："+s["reason"])
        for j,s in enumerate(d["rationale_steps"],1):
            lines.append(f"合法性解释{j}："+s)
        n=d["counterexamples"][0]
        m=d["misconceptions"][0]
        lines.extend(["", "**条件边界：** "+"；".join(d["boundaries"]), "",
          "**失效反例：** "+n["example"]+"；"+n["explanation"],"",
          "**典型错因：** "+m["error"]+"；"+m["why_wrong"]+"；"+m["repair_question"],""])
        for k,e in enumerate(d["worked_examples"],1):
            lines.extend([f"**教师例题{k}：** "+e["question"],
               "步骤："+"；".join(e["steps"]), "答案："+e["answer"],
               "独立核验："+e["check"],""])
        lines.extend(["**三级启发：** "+"；".join(d["hint_ladder"]), "",
           "**近迁移：** "+d["transfer"]["near"],"",
           "**远迁移：** "+d["transfer"]["far"],""])
    return "\n".join(lines).rstrip()+"\n"

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
    docs,audit=build()
    outputs={PACK:dump(docs),AUDIT:dump(audit),DOC:markdown(docs,audit)}
    for path,value in outputs.items():
        if a.check:
            need(path.is_file() and path.read_text(encoding="utf8")==value,
                 "generated artifact drift: "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(value,encoding="utf8")
    print("BATCH100:",len(docs),"full teacher drafts, 40 examples, 60 hints; 300 provisional stages;",
          "official denominator UNKNOWN; check",a.check)
if __name__=="__main__":main()
