"""Batch43 curated core/selective teacher manuscripts and strict source/visibility gates."""
from __future__ import annotations
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from .kb_batch41_core_review import Lesson
from .kb_batch42_coverage import ROOT, build as base_build, GateError, TRACKS
from .kb_batch43_exact import KEYS, VALID, INVALID, EXPECTED, witness

SOURCE=ROOT/"knowledge/editorial_review/kb_batch43_core_depth.jsonl"
SOURCE_SHA="d2573a7ff1428bee37c6053d2e5c92f235968923947e9944004854b2ef7eac35"
AUDIT=ROOT/"docs/evaluation/KB_BATCH43_CORE_DEPTH_AUDIT.json"
MANUSCRIPT=ROOT/"docs/evaluation/KB_BATCH43_CORE_DEPTH_MANUSCRIPTS.md"
COVERAGE=ROOT/"docs/evaluation/KB_BATCH43_PROJECT_SCOPE_OVERLAY.json"
GAPS=ROOT/"docs/evaluation/KB_BATCH43_PROJECT_SCOPE_GAPS.md"
OPS=(
"subset","complement","sufficient","equivalent","neg_exists","quadratic_inequality",
"change_base","unit_identity","bisection","parallel_nonzero","perpendicular_nonzero",
"ssa_acute","induction_sum","quadratic_derivative","fermat_quadratic",
"plane_distance_squared","line_slope","circle_line","permutation","combination",
"binomial_coefficients","total_probability","bayes_posterior","discrete_moments")

def validate(raw:str,*,check_pin=True):
    if check_pin and hashlib.sha256(raw.encode("utf-8")).hexdigest()!=SOURCE_SHA:
        raise GateError("Batch43 frozen authored source SHA drift")
    baseline=base_build()["rows"]
    index={row["editorial_id"]:row for row in baseline}
    result=[];seen=set()
    for lineno,line in enumerate(raw.splitlines(),1):
        if not line.strip():continue
        data=json.loads(line)
        eid=data.pop("editorial_id")
        if eid in seen:raise GateError("Duplicate editorial target")
        if eid not in index:raise GateError("Orphan editorial target")
        src=index[eid]
        if src["editorial_status"]!="NO_DIRECT_LINK" or src["track"] not in TRACKS[:2]:
            raise GateError("Batch43 must address genuinely unlinked core/selective goals")
        seen.add(eid)
        data["goal"]=src["goal"]
        data["derivation"]=[dict(statement=c,reason=r) for c,r in data["derivation"]]
        bad,ce,why=data["error"]
        data["error"]=dict(false_claim=bad,counterexample=ce,why_invalid=why)
        data["examples"]=[dict(question=q,steps=[s1,s2],answer=answer,check=check)
                          for q,s1,s2,answer,check in data["examples"]]
        unit=Lesson.model_validate(data)
        if unit.status!="REVIEW_PENDING" or unit.student_publishable or \
            unit.teacher_solution_visibility!="TEACHER_ONLY" or unit.proof_status!="NOT_FORMALLY_CERTIFIED":
            raise GateError("Forged teacher approval/proof or student publication")
        result.append((eid,unit,src))
    if len(result)!=24 or sum(src["track"]=="COMPULSORY" for _,_,src in result)!=12:
        raise GateError("Expected exactly 24 source-mapped manuscripts (12+12)")
    if len(OPS)!=24 or len(set(OPS))!=24 or set(OPS)!=set(KEYS):
        raise GateError("Exact case witness index mismatch")
    return tuple(result)

@lru_cache(maxsize=1)
def staged():
    return validate(SOURCE.read_text(encoding="utf-8"))

def audit():
    details=[]
    for ix,(eid,unit,src) in enumerate(staged()):
        content=json.dumps(unit.model_dump(mode="json"),ensure_ascii=False,sort_keys=True,separators=(",",":"))
        op=OPS[ix]
        verified=witness(op,VALID[op])
        invalid=witness(op,INVALID[op])
        if verified["status"]!="FINITE_EXACT_CASE_ONLY" or verified["exact_value"]!=EXPECTED[op] or \
            invalid["status"]!="CONDITIONS_NOT_ESTABLISHED":
            raise GateError("Math fixture drift")
        details.append(dict(
            editorial_id=eid,track=src["track"],source_standard="2017/2020 project editorial candidate",
            source_project_sha256=src["source_sha256"],source_line=src["source_line"],
            source_printed_page=src["printed_page"],goal=src["goal"],
            kind=src["kind"],lesson_sha256=hashlib.sha256(content.encode()).hexdigest(),
            exact_operator=op,finite_verified_case=verified["exact_value"],
            invalid_premise_rejected=True,finite_case_only=True,
            general_theorem_certified=False,student_freeform_step_verified=False,
            official_clause_equivalence_approved=False,
            teacher_approved=False,status="REVIEW_PENDING",
            student_publishable=False,teacher_solution_visibility="TEACHER_ONLY",
            proof_status="NOT_FORMALLY_CERTIFIED",
            examples=2,nonexamples=1,hint_levels=3,transfer_exercises=2))
    return dict(schema_version="kb43-review-v1",source_sha256=SOURCE_SHA,
      source_pdf_sha256="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195",
      summary=dict(project_candidate_lessons=24,compulsory=12,selective_compulsory=12,
        teacher_only_examples=48,nonexamples=24,hints=72,near_far=48,
        bounded_exact_operators=24,official_denominator=None,
        general_theorems_formally_certified=0,teacher_approved=0,student_published=0),
      items=details)

def coverage_overlay():
    base=base_build()
    added={eid for eid,_,_ in staged()}
    if len(added)!=24:raise GateError("Missing overlay IDs")
    rows=[]
    for r in base["rows"]:
        original_status=r["editorial_status"]
        if r["editorial_id"] in added:
            if original_status!="NO_DIRECT_LINK":raise GateError("Attempt to hide previously completed goal")
            nr={**r,"direct_review_drafts":[f"kb43:{r['editorial_id']}"],
                "editorial_status":"DRAFT_REVIEW_PENDING","batch43_new_teacher_review_draft":True}
        else:
            nr={**r,"batch43_new_teacher_review_draft":False}
        rows.append(nr)
    counts={}
    for track in TRACKS:
        rr=[r for r in rows if r["track"]==track]
        counts[track]=dict(
            project_candidate_count=len(rr),
            with_direct_review_draft=sum(x["editorial_status"]=="DRAFT_REVIEW_PENDING" for x in rr),
            legacy_association_only=sum(x["editorial_status"]=="LEGACY_ONLY_NOT_EQUIVALENT" for x in rr),
            missing_direct_editorial_link=sum(x["editorial_status"]=="NO_DIRECT_LINK" for x in rr),
            official_atom_denominator=None,official_verified_coverage=None,
            teacher_approved=0,student_published=0)
        if sum(counts[track][k] for k in
            ("with_direct_review_draft","legacy_association_only","missing_direct_editorial_link"))!=len(rr):
            raise GateError("Coverage count discrepancy")
    summary=dict(project_candidates=len(rows),
        direct_review_drafts=sum(r["editorial_status"]=="DRAFT_REVIEW_PENDING" for r in rows),
        legacy_only=sum(r["editorial_status"]=="LEGACY_ONLY_NOT_EQUIVALENT" for r in rows),
        missing_editorial_link=sum(r["editorial_status"]=="NO_DIRECT_LINK" for r in rows),
        batch43_new=24,teacher_approved=0,student_published=0,official_atom_denominator=None)
    if summary["direct_review_drafts"]!=157 or summary["legacy_only"]!=12 or \
        summary["missing_editorial_link"]!=144:raise GateError("Expected overlay 157/12/144")
    if any(r["teacher_approved"] or r["student_published"] or r["math_certified"] or
       r["official_clause_verified"] for r in rows):raise GateError("False trust status")
    return dict(schema_version="kb43-project-editorial-overlay-v1",
        warning="313 is an INCOMPLETE PROJECT editorial list, never an official syllabus denominator; batch42 source ledger remains frozen.",
        base_matrix="docs/evaluation/KB_BATCH42_PROJECT_SCOPE_MATRIX.json",
        summary=summary,tracks=counts,rows=rows)

def render():
    out=["# Batch43｜24 篇原创必修/选择性必修教师审核稿（不得学生发布）","",
      "每个项目编辑目标均关联 Batch31/32 原创候选、页面和 SHA，但不代表官方课标原子已经逐项等价认证。",
      "所有稿件均为 REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED；教师解答仅在本地审核稿，不进入学生检索或模型调用。",
      "24 种有限精确见证仅校验指定输入，绝不宣称证明了一般定理或自动批改自由文本。",""]
    for j,(eid,u,src) in enumerate(staged(),1):
        out += [f"## {j:02d}. {u.title}｜{eid}｜{src['track']}｜课标印刷页 {src['printed_page']}",
                f"**项目自编学习目标（非官方条款 ID）**：{src['goal']}",
                f"**知识类型**：{src['kind']}；**编辑来源**：{src['source_batch']} 行 {src['source_line']}。",
                f"**正式数学表述**：{u.statement}",
                "**适用条件**："+"；".join(u.conditions),
                "**前置知识**："+"；".join(u.prerequisites),
                "**逐步推理及数学依据（待教师核验）**："]
        out += [f"{n}. {step.statement}。依据：{step.reason}" for n,step in enumerate(u.derivation,1)]
        out += [f"**典型错法**：{u.error.false_claim}",
                f"**反例或非例**：{u.error.counterexample}",
                f"**为什么错**：{u.error.why_invalid}",
                "**两道典型题（完整解答仅供教师审核）**："]
        for n,ex in enumerate(u.examples,1):
            out += [f"- 题{n}：{ex.question}",f"  - 推导1：{ex.steps[0]}",
                    f"  - 推导2：{ex.steps[1]}",
                    f"  - 结果：{ex.answer}；核验：{ex.check}"]
        out += ["**提示阶梯**："]+[f"{n}. {h}" for n,h in enumerate(u.hints,1)]
        out += [f"**近迁移**：{u.near}",f"**远迁移**：{u.far}",
                f"**有限算子**：{OPS[j-1]}（仅受控精确输入实例）",
                "**审核状态**：REVIEW_PENDING；学生可见 false；一般定理形式认证 false",""]
    return "\n".join(out).rstrip()+"\n"

def render_gaps(data):
    s=data["summary"]
    lines=["# Batch43｜项目编辑目标覆盖增量审计（非官方课标分母）","",
        "Batch42 固定矩阵保持不变；本文件单独记录新增 24 篇审核稿的局部增量。",
        f"项目候选 {s['project_candidates']}，有独立待审稿 {s['direct_review_drafts']}，仅旧关联 {s['legacy_only']}，无直接稿 {s['missing_editorial_link']}。",
        "七个课标官方完整原子分母均为 null，不得计算声称全量覆盖率。",
        "","|轨道|项目候选|有待审稿|仅历史关联|缺直接稿|官方分母|",
        "|---|---:|---:|---:|---:|---|"]
    for k in TRACKS:
        t=data["tracks"][k]
        lines.append(f"|{k}|{t['project_candidate_count']}|{t['with_direct_review_draft']}|{t['legacy_association_only']}|{t['missing_direct_editorial_link']}|未核实|")
    lines.extend(["","## 剩余必修与选择性必修候选（前 45 项）",""])
    missing=[r for r in data["rows"] if r["editorial_status"]=="NO_DIRECT_LINK"]
    for r in missing[:45]:
        lines.append(f"- {r['editorial_id']}｜{r['track']}｜页 {r['printed_page']}：{r['goal']}")
    lines+=["","## 审核边界","",
        "所有 24 篇仍由真实数学教师逐条校对定理假设、证明、习题答案和课标归属，未经批准绝不进入学生端。",
        "证明步骤有界实例通过 ≠ 一般定理获证；历史 538 条未形式认证步骤及 10 组历史冲突不因本批自动减少。",
        "下一批先核验官方编号/未编号完整原子，再对剩余 144 项未关联编辑候选分域补课，处理 12 项仅旧关联。",
        ""]
    return "\n".join(lines)

def generate(*,check=False):
    a=audit();b=coverage_overlay()
    files={AUDIT:json.dumps(a,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
           MANUSCRIPT:render(),
           COVERAGE:json.dumps(b,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
           GAPS:render_gaps(b)}
    for path,body in files.items():
        if check:
            if path.read_text(encoding="utf-8")!=body:raise GateError("Batch43 generated output drift: "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(body,encoding="utf-8")
    return a["summary"],b["summary"]

def student_retrieval_projection():
    return dict(status="NO_APPROVED_GOAL_EVIDENCE",student_documents=[],
        teacher_solutions_exposed=[],teacher_approved=0,student_published=0,
        review_pending=24,official_atomic_denominator=None)

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    print("PASS",generate(check=p.parse_args().check))
