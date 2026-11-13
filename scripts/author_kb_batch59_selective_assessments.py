#!/usr/bin/env python3
"""Batch59: replayable quality gate for 14 original teacher-only assessments.

Crosswalk and teacher reviewer remain pending. Tests of arithmetic examples
and schema do not constitute authentic teacher approval or student assessment.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import re

import build_kb_batch59_selective_source_review as SOURCE

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"curriculum/highschool_math/kb_batch59_selective_assessment_drafts.json"
OUT=ROOT/"docs/evaluation/KB_BATCH59_SELECTIVE_ASSESSMENTS.md"
COVER=ROOT/"docs/evaluation/KB_BATCH59_ASSESSMENT_CROSSWALK.json"
ASSOCIATED_WITNESSES={
    "KB59-ASSESS-01":["arithmetic_partial_sum"],
    "KB59-ASSESS-02":["affine_square_derivative"],
    "KB59-ASSESS-04":["space_basis_coordinates"],
    "KB59-ASSESS-06":["ellipse_focal_parameters"],
    "KB59-ASSESS-08":[],
    "KB59-ASSESS-09":["binomial_coefficient"],
    "KB59-ASSESS-10":["hypergeometric_probability","binomial_coefficient"],
    "KB59-ASSESS-11":["pearson_squared","least_squares","two_by_two_chi_square"],
    "KB59-ASSESS-12":["least_squares"],
}
REQUIRED={
 "assessment_id","source_requirement_id","topic","question","assumptions",
 "reasoning_steps","typical_wrong_method","counterexample_or_failure",
 "hint_ladder","near_transfer","far_transfer","rubric","approval_state",
 "visibility","formal_proof_certified","student_answer_verified",
 "real_teacher_signature","student_publishable","source_license",
 "general_math_certificate"
}
def need(ok,why):
    if not ok:raise ValueError(why)

def load(path):
    return json.loads(Path(path).read_text(encoding="utf8"))

def build(*,manuscripts=None,source=None):
    manuscripts=deepcopy(manuscripts if manuscripts is not None else load(SEED))
    source=deepcopy(source if source is not None else SOURCE.build())
    targets={r["candidate_id"]:r for r in source["rows"]
             if r["source_kind"] in ("ACHIEVEMENT_REQUIREMENT","ACTIVITY_REQUIREMENT")}
    need(len(targets)==14,"source achievement/activity baseline drift")
    need(len(manuscripts)==14,"14 original teacher drafts required")
    ids=set();used=set();out=[]
    for idx,item in enumerate(manuscripts,1):
        need(set(item)==REQUIRED,"missing or extra assessment fields")
        ident=item["assessment_id"];src=item["source_requirement_id"]
        need(ident==f"KB59-ASSESS-{idx:02d}" and ident not in ids,
             "assessment ID duplicated or reordered")
        need(src in targets and src not in used,
             "assessment orphaned, duplicated or mapped to non-achievement source")
        ids.add(ident);used.add(src)
        need(item["approval_state"]=="REVIEW_PENDING" and item["visibility"]=="TEACHER_ONLY"
             and item["real_teacher_signature"] is None
             and item["source_license"]=="ORIGINAL_EDITORIAL_WORK"
             and item["general_math_certificate"]=="NOT_FORMALLY_CERTIFIED"
             and item["formal_proof_certified"] is False
             and item["student_answer_verified"] is False
             and item["student_publishable"] is False,
             "forged teacher approval, formal certification or release")
        for k in ("topic","question","assumptions","typical_wrong_method",
                  "counterexample_or_failure","near_transfer","far_transfer","rubric"):
            need(isinstance(item[k],str) and len(item[k])>=(4 if k=="topic" else 10),
                 "incomplete original assessment field: "+k)
        steps=item["reasoning_steps"]
        need(isinstance(steps,list) and len(steps)>=3
             and all(set(step)=={"index","claim","reason"}
                     and step["index"]==j
                     and len(step["claim"])>=12 and len(step["reason"])>=12
                     for j,step in enumerate(steps,1)),
             "incomplete justified reasoning steps")
        need(isinstance(item["hint_ladder"],list)
             and len(item["hint_ladder"])==3
             and all(isinstance(h,str) and len(h)>=10 for h in item["hint_ladder"]),
             "three-level hint ladder must remain present")
        # Explicitly track small testable finite cases without asserting whole-proof validity.
        out.append({
            "assessment_id":ident,"source_requirement_id":src,
            "source_span_id":targets[src]["source_span_id"],
            "source_pdf_sha256":targets[src]["source_pdf_sha256"],
            "target_kind":targets[src]["source_kind"],
            "bounded_exact_witness_families":ASSOCIATED_WITNESSES.get(ident,[]),
            "teacher_assessment_draft_present":True,
            "real_student_response_evaluated":False,
            "independent_teacher_rubric_verified":False,
            "curriculum_competency_achieved":False,
            "approval_state":"REVIEW_PENDING",
            "student_publishable":False
        })
    need(used==set(targets),"14 requirements not all bound")
    need(source["non_content_requirements_separately_unmapped"]==42
         and all(x["coverage"]=="UNMAPPED" for x in source["competency_requirement_queue"]),
         "drafts cannot erase independent unmapped requirements")
    return {
        "schema_version":"kb59-original-assessment-review-v1",
        "source_requirements":14,
        "teacher_only_review_drafts":len(out),
        "total_distinct_noncontent_requirements_unmapped":42,
        "teacher_verified_assessments":0,
        "live_student_attempts":0,
        "mathematical_general_proofs_certified":0,
        "official_atomic_denominator":{t:None for t in SOURCE.TRACKS},
        "bounded_witnesses_are_not_full_rubric_certificates":True,
        "source_passages_or_pdf_committed":False,
        "rows":out
    }

def render(data,manuscripts):
    lines=[
        "# Batch59｜14项选择性必修学业及课题活动教师待审测评稿","",
        "本文件为原创教师侧测评草案，**不得被学生端作为完整解答检索**。来源定位/内容对应非学业达标证据；教师真实审核数为0。","",
        "源课标范围印刷第37–50页；所有题目、案例、错因、解题依据与提示均为项目自编内容；不复制版权教材原文。","",
        f"草案 {data['teacher_only_review_drafts']} 项，独立能力/教学/活动要求 {data['total_distinct_noncontent_requirements_unmapped']} 项全部仍 UNMAPPED。", "",
    ]
    for item in manuscripts:
        rid=item["source_requirement_id"]
        lines.extend([
            f"## {item['assessment_id']}｜{item['topic']}","",
            f"**课程要求线索：** `{rid}`（并非认证的唯一数学等价映射）。","",
            "**原创题：** "+item["question"],"",
            "**适用条件：** "+item["assumptions"],"",
            "**教师侧三阶段解答及每步依据：**",""
        ])
        for s in item["reasoning_steps"]:
            lines.append(f"{s['index']}. {s['claim']} **依据：** {s['reason']}")
        lines.extend(["", "**典型错法：** "+item["typical_wrong_method"],"",
                      "**反例或失效条件：** "+item["counterexample_or_failure"],"",
                      "**三级提示（学生端需按授权分级，不得直接显示完整稿）：**",""])
        lines.extend(f"{i}. {h}" for i,h in enumerate(item["hint_ladder"],1))
        lines.extend(["", "**近迁移：** "+item["near_transfer"],"",
                      "**远迁移：** "+item["far_transfer"],"",
                      "**评分关注点：** "+item["rubric"],"",
                      "`REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED`",""])
    lines.extend(["## 正式验收阻断","",
                  "这些草案仅提供能力要求相关的可观察题目与量规草案，尚无真实学生作答或独立教研审核。42项非内容来源要求全部仍UNMAPPED，不能把14篇草案或有限符号实例计作学生能力达到标准。","",
                  "真实教师审核及数学一般命题形式认证均为0；不得自动标记APPROVED，也不得让学生挑战模式检索教师侧完整解答。",""])
    return "\n".join(lines)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    manuscripts=load(SEED)
    audit=build(manuscripts=manuscripts)
    expected=json.dumps(audit,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    expected_md=render(audit,manuscripts)
    if args.check:
        need(COVER.read_text(encoding="utf8")==expected,"assessment crosswalk generation drift")
        need(OUT.read_text(encoding="utf8")==expected_md,"teacher manuscript generation drift")
    else:
        COVER.write_text(expected,encoding="utf8")
        OUT.write_text(expected_md,encoding="utf8")
    print("KB59: 14 teacher-only assessments; 42 competencies remain UNMAPPED, approved=0")

if __name__=="__main__":main()
