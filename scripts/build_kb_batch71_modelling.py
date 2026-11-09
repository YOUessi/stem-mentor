#!/usr/bin/env python3
"""Batch71: seven original page-35 modelling/research lesson drafts and honest K00 lineage.

No PDF paragraph is reproduced here. Page-35 candidates were *previously* read
visually, but are not full official clauses or teacher-certified knowledge atoms.
Finite Fraction witnesses certify only the listed numeric example.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "curriculum/highschool_math/k00_batch51_page35_modelling_candidate_split.json"
AUTHOR = ROOT / "knowledge/editorial_review/kb_batch71_modelling_authoring.json"
OBJECTIVES = ROOT / "docs/evaluation/KB_BATCH67_UNNUMBERED_OBJECTIVE_QUEUE.json"
LINEAGE = ROOT / "curriculum/highschool_math/k00_batch71_page35_model_links.json"
OUT = ROOT / "docs/evaluation/KB_BATCH71_MODELLING_TEACHER_REVIEW.json"
MARKDOWN = ROOT / "docs/evaluation/KB_BATCH71_MODELLING_TEACHER_REVIEW.md"
COVERAGE = ROOT / "docs/evaluation/KB_BATCH71_SEVEN_TRACK_BLOCKERS.json"
FROZEN_SOURCE_SHA256 = "171f3f6147c06f51fce17b892225fcb5a70b0ab5840ac1952ca6d0c6cb94f1ce"
FROZEN_OBJECTIVE_SHA256 = "17d36b35b486a2e610ee4bd4f1eae897f719c8e3f729dc90b6eed557aee0877e"
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A", "ELECTIVE_B",
          "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")
KINDS = ("METHOD","METHOD","METHOD","METHOD","CONCEPT","METHOD","TEACHING_ACTIVITY")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def render_json(obj):
    return json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True) + "\n"


def as_exact(value):
    require(type(value) is int, "Numeric witness inputs must be exact integers")
    return Fraction(value)


def validate_authoring(author):
    require(author.get("schema_version")=="kb71-page35-original-modelling-lessons-v1",
            "Authoring schema version not supported")
    items=author.get("items")
    require(isinstance(items,list) and len(items)==7,"Seven complete authoring records required")
    expected=[f"KB51-C-P035-V{i:03d}" for i in range(1,8)]
    require([r.get("anchor") for r in items]==expected,"Page35 candidate id/order mismatch")
    for i,row in enumerate(items):
        require(row.get("knowledge_kind")==KINDS[i],"Knowledge-type mismatch")
        for key in ("title","definition","validity_why","boundary","near_transfer","far_transfer"):
            require(isinstance(row.get(key),str) and len(row[key]) >= (8 if key=="title" else 20),
                    "Missing original depth: " + key)
        require(len(row.get("assumptions",[]))>=2,"Incomplete model assumptions")
        require(len(row.get("symbols",[]))>=2,"Missing quantities and units")
        require(len(row.get("prerequisites",[]))>=2,"Missing prerequisite links")
        require(len(row.get("steps",[]))==4,"Four auditable reasoning steps required")
        for step in row["steps"]:
            require(isinstance(step,list) and len(step)==2 and
                    isinstance(step[0],str) and len(step[0])>=4 and isinstance(step[1],str) and len(step[1])>=15,
                    "Reasoning step lacks claim and justification")
        examples=row.get("worked_examples")
        require(isinstance(examples,list) and len(examples)>=2,
                "At least two complete original worked examples required")
        for ex in examples:
            require(len(ex.get("question",""))>=20 and len(ex.get("teacher_solution",""))>=30,
                    "Incomplete worked example")
        error=row.get("invalid_case",{})
        require(len(error.get("false_claim",""))>=16 and len(error.get("counterexample_explanation",""))>=20,"Missing invalid case evidence")
        require(len(row.get("hints",[]))==3 and len(set(row["hints"]))==3,
                "Three distinct graduated hints required")
        require(row["near_transfer"]!=row["far_transfer"],"Near/far transfer duplicate")
        rubric=row.get("scoring_rubric",[])
        require(len(rubric)==4 and all(isinstance(r,list) and len(r)==2 and
                len(r[0])>=4 and type(r[1]) is int and r[1]>0 for r in rubric) and
                sum(r[1] for r in rubric)==6,"Six-point criterion-specific rubric required")
        require(row.get("status")=="REVIEW_PENDING" and row.get("teacher_signature") is None,
                "Forged teacher approval")
        require(row.get("formal_certification")=="NOT_FORMALLY_CERTIFIED",
                "Forged mathematical proof certification")
        require(row.get("student_publishable") is False and
                row.get("teacher_solution_visibility")=="TEACHER_ONLY",
                "Teacher-only answer exposure")
        require(row.get("source_license")=="ORIGINAL_PROJECT_AUTHORED" and
                row.get("full_official_clause_review")=="NOT_COMPLETED",
                "Invalid source or fraudulent complete clause claim")
        require(isinstance(row.get("finite_case"),dict), "Missing bounded numeric witness")
    return items


def finite_witness(i, case):
    """Each case checked against *independent* exact arithmetic, not an LLM assertion."""
    typ=case.get("type")
    require(typ==("linear_fee","speed_distance","break_even","residual",
                 "algebra_domain","prime_counterexample","traceable_report")[i],
            "Wrong bounded math witness type")
    if i==0:
        v=as_exact(case["base"])+as_exact(case["rate"])*as_exact(case["time"])
        require(as_exact(case["time"])>=0 and as_exact(case["rate"])>=0,"Invalid nonnegative time/rate")
        require(v==as_exact(case["expected"]),"Incorrect linear pricing witness")
        return f"5+3×2={v} 元，仅为自编收费情境"
    if i==1:
        v=as_exact(case["speed_kmh"])*as_exact(case["minutes"])/60
        require(as_exact(case["speed_kmh"])>=0 and as_exact(case["minutes"])>=0,"Invalid speed/time")
        require(v==as_exact(case["expected_km"]),"Incorrect unit conversion")
        return f"12 km/h×20/60 h={v} km"
    if i==2:
        n=as_exact(case["minimum_units"])
        delta=as_exact(case["unit_price"])-as_exact(case["variable"])
        fixed=as_exact(case["fixed"])
        require(delta>0 and fixed>0 and n.denominator==1 and n>=1,"Invalid discrete profit model")
        require(delta*n>=fixed and delta*(n-1)<fixed,"Not the minimum integer break-even")
        return f"n={n} 收支≥0且 n={n-1} 仍亏损"
    if i==3:
        b=as_exact(case["intercept"]); m=as_exact(case["slope"])
        train=case["train"]; hold=case["holdout"]
        require(len(train)>=3 and all(len(p)==2 for p in train) and len(hold)==2,
                "Missing training/heldout separation")
        require(all(as_exact(y)==m*as_exact(x)+b for x,y in train),
                "Training points do not fit specified model")
        require(hold not in train,"Heldout point contaminates training")
        res=as_exact(hold[1])-(m*as_exact(hold[0])+b)
        require(res==as_exact(case["expected_residual"]),"Incorrect heldout residual")
        return f"训练残差均0；留出残差={res}（有限样本）"
    if i==4:
        m=as_exact(case["slope"]); f=as_exact(case["fixed"]); target=as_exact(case["target"])
        require(m!=0,"Zero slope is invalid for single-solution division")
        solution=(target-f)/m
        require(solution==as_exact(case["expected_solution"]) and
                solution>as_exact(case["max_t"])>=0,"Wrong algebraic/out-of-domain claim")
        return f"代数解t={solution}h，超出[0,{case['max_t']}]h"
    if i==5:
        n=as_exact(case["n"]); a=as_exact(case["factor1"]); b=as_exact(case["factor2"])
        v=n*n+n+41
        require(n.denominator==1 and n>=0 and a>1 and b>1,
                "Counterexample must be an integer in the claim domain")
        require(v==a*b==as_exact(case["expected"]),"Incorrect composite factorization")
        return f"p({n})={v}={a}×{b}，构成合法反例"
    if i==6:
        fixed=as_exact(case["fixed"]);rate=as_exact(case["rate"])
        xs=case["times"];ys=case["observed"]
        require(len(xs)==len(ys)>=3 and all(type(x) is int for x in xs),"Invalid research records")
        require(all(fixed+rate*as_exact(x)==as_exact(y) for x,y in zip(xs,ys)),
                "Recorded toy observations mismatch")
        out=as_exact(case["out_of_domain"])
        require(out>max(xs) and fixed+rate*out==as_exact(case["algebraic_forecast"]),
                "Failed out-of-range guard")
        return f"合成记录样本内残差0；{out}h 的代数预测超出 {max(xs)}h 记录范围"
    raise ValueError("No such finite witness")


def build(custom_author=None,custom_source=None,custom_objectives=None):
    require(sha256(SOURCE.read_bytes()).hexdigest()==FROZEN_SOURCE_SHA256,
            "Frozen page35 source hash drift")
    require(sha256(OBJECTIVES.read_bytes()).hexdigest()==FROZEN_OBJECTIVE_SHA256,
            "Frozen 14-objective queue hash drift")
    source=load(SOURCE) if custom_source is None else custom_source
    require(render_json(source)==render_json(load(SOURCE)),
            "Forged page35 candidate source")
    require(source["source_printed_page"]==35 and source["teacher_review"]=="REVIEW_PENDING" and
            source["official_atom_denominator"] is None and
            source["status"]=="PROJECT_AUTHORED_ATOMIC_SPLIT_CANDIDATES_NOT_OFFICIAL_VERIFIED",
            "Source claims full official review not evidenced")
    base=source["candidates"]
    require(len(base)==7 and [b["id"] for b in base]==
            [f"KB51-C-P035-V{i:03d}" for i in range(1,8)],
            "Page35 split identity invalid")
    objectives=load(OBJECTIVES) if custom_objectives is None else custom_objectives
    require(render_json(objectives)==render_json(load(OBJECTIVES)),"Forged 14 competencies")
    require(objectives["review_pending"]==14 and
            all(r["coverage_status"]=="UNMAPPED" for r in objectives["rows"]) and
            len(objectives["rows"])==14,"Cannot invent approved competency mapping")
    author=load(AUTHOR) if custom_author is None else custom_author
    rows=validate_authoring(author)
    linked=[];lineage=[]
    for i,(r,src) in enumerate(zip(rows,base)):
        require(src["kind"]==r["knowledge_kind"],"Kind mismatch with source")
        require(src["teacher_review"]=="REVIEW_PENDING" and
                src["full_lesson_available"] is False,"Source tampering/false completion")
        witness=finite_witness(i,r["finite_case"])
        row=deepcopy(r)
        row.update({
            "manuscript_id":f"KB71-MODEL-{i+1:02d}",
            "source_printed_page":35,"source_pdf_sha256":source["source_pdf_sha256"],
            "original_visual_review_sha256":source["mac_rendered_page_png_sha256"],
            "source_anchor":src["id"],"official_atomic_membership":"UNDETERMINED",
            "source_full_page_review":"NOT_COMPLETED",
            "finite_validation_level":"EXACT_NUMERIC_CASE_ONLY",
            "finite_validation_note":witness,
            "teacher_solution_index_visibility":"NOT_INDEXED_FOR_STUDENTS",
            "student_freeform_proof_steps_verified":False})
        linked.append(row)
        lineage.append({
            "candidate_id":src["id"],"candidate_kind":src["kind"],
            "source_page":35,"source_document_sha256":source["source_pdf_sha256"],
            "earlier_visual_render_sha256":source["mac_rendered_page_png_sha256"],
            "lesson_id":row["manuscript_id"],
            "internal_draft_full_fields":True,
            "official_clause_review":"NOT_DONE",
            "official_atomic_membership":"UNDETERMINED",
            "teacher_review":"REVIEW_PENDING","student_publishable":False})
    denominator={t:None for t in TRACKS}
    report={
        "schema_version":"kb71-modelling-teacher-review-v1",
        "scope":"SEVEN_ORIGINAL_PAGE35_TEACHER_ONLY_DRAFTS_NOT_OFFICIAL_ATOMS",
        "source_candidate_sha256":FROZEN_SOURCE_SHA256,
        "authoring_sha256":sha256(AUTHOR.read_bytes()).hexdigest(),
        "model_drafts":7,"worked_examples":sum(len(r["worked_examples"]) for r in linked),
        "reasoning_steps":sum(len(r["steps"]) for r in linked),
        "bounded_exact_checks":7,"formally_certified_math_proofs":0,
        "teacher_approved":0,"student_published":0,
        "official_atomic_denominator":denominator,"records":linked}
    links={"schema_version":"kb71-page35-lineage-v1","source_pdf_sha256":source["source_pdf_sha256"],
           "source_split_sha256":FROZEN_SOURCE_SHA256,
           "printed_page":35,"complete_editorial_drafts":7,
           "teacher_approved":0,"official_clause_certified":0,
           "official_denominator":None,"records":lineage}
    coverage={
        "schema_version":"kb71-seven-track-open-blockers-v1",
        "official_atom_denominator":denominator,"official_missing_atom_count":None,
        "unknown_not_zero":True,"teacher_full_page_reviews":0,
        "heuristic_anchor_leads_not_atom_denominator":428,
        "provisional_split_hypotheses_not_atom_denominator":62,
        "page35_modelling_editorial_drafts":7,
        "page35_teacher_approved":0,"unmapped_unnumbered_objectives":14,
        "historical_unverified_proof_steps":538,"unresolved_math_conflicts":10,
        "student_published":0,
        "next_blockers":[
            "全量逐页核对课标原文与跨页条款，七轨去重后才建立真实知识原子分母。",
            "教师核验第35页流程图与项目内7项拆分的官方语义范围。",
            "将14项未编号内容/教学要求分别评估可观察指标与真实证据。",
            "独立审查538历史证明步骤及10组数学冲突，开放签核前不发布。"]
    }
    return report,links,coverage


def render_markdown(report,links,coverage):
    parts=["# Batch71｜数学建模与探究：7篇原创教学草案（教师待审）","",
           "> 已有第35页视觉候选拆分不代表正式课标原子；此处为项目原创讲义，不复制课标原文。",
           "> REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED；禁止学生端直接检索完整解答。",
           "","## 课标来源与覆盖边界","",
           f"- 原版课标PDF SHA256：{links['source_pdf_sha256']}",
           f"- 既有第35页视觉审查图哈希：{links['records'][0]['earlier_visual_render_sha256']}",
           "- 7个内部拆分假设均有一篇原创完整字段教师稿，但正式教师审核为0。",
           "- 七轨官方知识原子分母全部未知（null），未编号要求14项未映射，正式课程覆盖未认证。",
           "","## 分项教师审查稿",""]
    for r in report["records"]:
        parts.extend([f"### {r['manuscript_id']}｜{r['title']}","",
                      f"类型：{r['knowledge_kind']}；来源候选：{r['source_anchor']}；审核状态：REVIEW_PENDING",
                      "","**正式概念/方法界定**",r["definition"],"",
                      "**先修知识**","；".join(r["prerequisites"]),"",
                      "**符号、适用对象与单位**","；".join(r["symbols"]),"",
                      "**全部模型假设**"])
        parts.extend("- "+x for x in r["assumptions"])
        parts.extend(["","**为何数学使用合法 / 何时不可用**",r["validity_why"],"",
                      "**推理和解题四步（非形式认证）**"])
        for j,(claim,basis) in enumerate(r["steps"],1):
            parts.append(f"{j}. {claim}：{basis}")
        parts.extend(["","**两道原创题族（解答仅供教师）**"])
        for i,ex in enumerate(r["worked_examples"],1):
            parts.append(f"{i}. {ex['question']}\n   - 教师解答：{ex['teacher_solution']}")
        parts.extend(["","**不适用例与典型错因**",r["invalid_case"]["false_claim"],
                      "反例/原因："+r["invalid_case"]["counterexample_explanation"],
                      "","**模型边界**",r["boundary"],"","**循序渐进提示**"])
        parts.extend(f"- H{i}：{hint}" for i,hint in enumerate(r["hints"],1))
        parts.extend(["","近迁移："+r["near_transfer"],
                      "远迁移："+r["far_transfer"],"","**评分量规（6分）**"])
        parts.extend(f"- {name}：{pts}分" for name,pts in r["scoring_rubric"])
        parts.extend(["","**独立精确有限实例见证**",
                      r["finite_validation_note"] + "；仅支持该数值例题，不代表原命题一般证明。",
                      "","---",""])
    parts.extend(["## 尚未解决的课标与数学发布门禁","",
                  "7份稿件不得冒充7个教师审核或正式课程原子。十四项未编号要求依然未映射；",
                  "10组冲突和538项历史证明步骤仍待真正独立复审。研究活动需实际教师签字，",
                  "正式课标分母仍未知，不能以此发布学生端。",""])
    return "\n".join(parts)


def write(check=False):
    report,links,coverage=build()
    for path,content in ((OUT,render_json(report)),(LINEAGE,render_json(links)),
                         (COVERAGE,render_json(coverage)),
                         (MARKDOWN,render_markdown(report,links,coverage))):
        if check:
            require(path.is_file() and path.read_text(encoding="utf-8")==content,
                    "Snapshot drift: "+str(path))
        else:
            path.write_text(content,encoding="utf-8")
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    d=write(check=args.check)
    print("Batch71: ",d["model_drafts"],"teacher-only lessons,",
          d["worked_examples"],"examples,",d["bounded_exact_checks"],
          "exact cases; zero teacher approval")
