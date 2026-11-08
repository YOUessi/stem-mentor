"""Batch44: twenty original compulsory review manuscripts, exact bounded witness gates,
and a non-official 313-row project editorial coverage overlay. Nothing is approved.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from .kb_batch41_core_review import Lesson
from .kb_batch42_coverage import ROOT, GateError, TRACKS, Row
from .kb_batch43_review import coverage_overlay as previous_overlay
from .kb_batch44_exact import KEYS, VALID, INVALID, EXPECTED, witness

SOURCE=ROOT/"knowledge/editorial_review/kb_batch44_core_depth.jsonl"
SOURCE_SHA="751fcaf04ed8b6b52d492e75bbb918ae47d4a3623c88b35e6d4f6976a0181e69"
AUDIT=ROOT/"docs/evaluation/KB_BATCH44_CORE_DEPTH_AUDIT.json"
MANUSCRIPT=ROOT/"docs/evaluation/KB_BATCH44_CORE_DEPTH_MANUSCRIPTS.md"
COVERAGE=ROOT/"docs/evaluation/KB_BATCH44_PROJECT_SCOPE_OVERLAY.json"
GAPS=ROOT/"docs/evaluation/KB_BATCH44_PROJECT_SCOPE_GAPS.md"
OPS=(
    "set_predicate","set_symdiff","function_table","maximum_on_interval",
    "real_power_domain","rational_power","positive_exp_law",
    "positive_exp_monotonic","log_inverse_integer","angle_degree_to_radian",
    "vector_equal","zero_vector_direction","displacement","triangle_vector",
    "vector_scale","vector_dot","vector_projection","complex_parts",
    "complex_equal","complex_modulus_sq",
)

def validate(raw: str, *, check_pin:bool=True):
    if check_pin and hashlib.sha256(raw.encode("utf-8")).hexdigest()!=SOURCE_SHA:
        raise GateError("Batch44 frozen original editorial content SHA mismatch")
    prev=previous_overlay()
    index={r["editorial_id"]:r for r in prev["rows"]}
    result=[];seen=set()
    for line in raw.splitlines():
        if not line.strip():
            continue
        data=json.loads(line)
        eid=data.pop("editorial_id")
        if eid in seen:
            raise GateError("duplicate Batch44 editorial target")
        if eid not in index:
            raise GateError("orphan Batch44 editorial target")
        src=index[eid]
        if src["track"]!="COMPULSORY" or src["editorial_status"]!="NO_DIRECT_LINK":
            raise GateError("Batch44 target already linked or not compulsory")
        seen.add(eid)
        data["goal"]=src["goal"]
        data["derivation"]=[dict(statement=s,reason=reason) for s,reason in data["derivation"]]
        false_claim,example,reason=data["error"]
        data["error"]=dict(false_claim=false_claim,counterexample=example,why_invalid=reason)
        data["examples"]=[dict(question=q,steps=[s1,s2],answer=ans,check=check)
                          for q,s1,s2,ans,check in data["examples"]]
        unit=Lesson.model_validate(data)
        if unit.status!="REVIEW_PENDING" or unit.approved_reviewer is not None or unit.student_publishable or \
            unit.teacher_solution_visibility!="TEACHER_ONLY" or unit.proof_status!="NOT_FORMALLY_CERTIFIED":
            raise GateError("forged approval or teacher solution visibility")
        result.append((eid,unit,src))
    if len(result)!=20 or len(seen)!=20:
        raise GateError("Batch44 requires twenty genuinely unlinked compulsory manuscripts")
    if len(OPS)!=20 or set(OPS)!=set(KEYS) or len(KEYS)!=len(VALID)!=len(INVALID)!=len(EXPECTED):
        raise GateError("operator index or finite fixtures changed")
    return tuple(result)

@lru_cache(maxsize=1)
def staged():
    return validate(SOURCE.read_text(encoding="utf-8"))

def audit():
    items=[]
    for eid,unit,src in staged():
        op=OPS[len(items)]
        good,bad=witness(op,VALID[op]),witness(op,INVALID[op])
        if good["status"]!="FINITE_EXACT_CASE_ONLY" or good["exact_value"]!=EXPECTED[op] or \
            bad["status"]!="CONDITIONS_NOT_ESTABLISHED":
            raise GateError("exact finite witness fixture mismatch: "+op)
        content=json.dumps(unit.model_dump(mode="json"),ensure_ascii=False,sort_keys=True,
                           separators=(",",":"))
        items.append(dict(editorial_id=eid,project_editorial_kind=src["kind"],
            source_line=src["source_line"],source_printed_page=src["printed_page"],
            source_standard="2017/2020 project editorial goal (not official clause certified)",
            source_project_sha256=src["source_sha256"],
            goal=src["goal"],lesson_sha256=hashlib.sha256(content.encode()).hexdigest(),
            content_status="REVIEW_PENDING",student_publishable=False,teacher_approved=False,
            teacher_solution_visibility="TEACHER_ONLY",proof_status="NOT_FORMALLY_CERTIFIED",
            official_clause_verified=False,math_certified=False,
            general_theorem_certified=False,student_freeform_step_verified=False,
            exact_operator=op,finite_case_witness=good["exact_value"],
            invalid_premise_rejected=True,examples=2,nonexamples=1,hint_levels=3,
            near_far=2))
    return dict(schema_version="kb44-core-review-v1",source_sha256=SOURCE_SHA,
                source_pdf_sha256="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195",
                warning="Only bounded finite arithmetic witnesses; NONE certify a universal theorem or authorize student publication.",
                summary=dict(project_candidate_lessons=20,compulsory=20,selective_compulsory=0,
                    teacher_only_examples=40,nonexamples=20,hints=60,near_far=40,
                    exact_bounded_operators=20,official_atom_denominator=None,
                    formal_theorems_certified=0,teacher_approved=0,student_published=0),
                items=items)

def coverage_overlay():
    previous=previous_overlay()
    additions={eid for eid,_,_ in staged()}
    rows=[]
    for r in previous["rows"]:
        if r["editorial_id"] in additions:
            if r["editorial_status"]!="NO_DIRECT_LINK" or r["direct_review_drafts"]:
                raise GateError("trying to cover an already-linked target")
            nr={**r,"direct_review_drafts":[f"kb44:{r['editorial_id']}"],
                "editorial_status":"DRAFT_REVIEW_PENDING","batch44_new_teacher_review_draft":True}
        else:
            nr={**r,"batch44_new_teacher_review_draft":False}
        rows.append(nr)
    if len(rows)!=313 or len(additions)!=20:
        raise GateError("crosswalk denominator or new target count drift")
    tracks={}
    for track in TRACKS:
        rr=[r for r in rows if r["track"]==track]
        tracks[track]=dict(project_candidate_count=len(rr),
            with_direct_review_draft=sum(r["editorial_status"]=="DRAFT_REVIEW_PENDING" for r in rr),
            legacy_association_only=sum(r["editorial_status"]=="LEGACY_ONLY_NOT_EQUIVALENT" for r in rr),
            missing_direct_editorial_link=sum(r["editorial_status"]=="NO_DIRECT_LINK" for r in rr),
            official_atom_denominator=None,official_verified_coverage=None,
            teacher_approved=0,student_published=0)
        v=tracks[track]
        if v["with_direct_review_draft"]+v["legacy_association_only"]+v["missing_direct_editorial_link"]!=len(rr):
            raise GateError("per-track ledger arithmetic mismatch")
    summary=dict(project_candidates=313,direct_review_drafts=177,legacy_only=12,
        missing_editorial_link=124,batch44_new=20,teacher_approved=0,student_published=0,
        official_atom_denominator=None)
    if (sum(t["with_direct_review_draft"] for t in tracks.values()),
        sum(t["legacy_association_only"] for t in tracks.values()),
        sum(t["missing_direct_editorial_link"] for t in tracks.values()))!=(177,12,124):
        raise GateError("Batch44 overlay must be 177/12/124")
    if any(r["teacher_approved"] or r["student_published"] or
           r["math_certified"] or r["official_clause_verified"] for r in rows):
        raise GateError("false certification/approval status")
    return dict(schema_version="kb44-project-editorial-overlay-v1",
        warning="313 incomplete project editorial goals; never an official syllabus denominator.",
        base="docs/evaluation/KB_BATCH43_PROJECT_SCOPE_OVERLAY.json",
        summary=summary,tracks=tracks,rows=rows)

def render_lessons():
    lines=["# Batch44｜20 篇原创必修数学教师审核稿","",
        "仅针对项目编辑目标补齐审核材料，不等于官方课标全量原子覆盖；未经教师审核禁止发布。",
        "全部 REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED。",
        "其中定义与方法的三段是解释和合法性论证，不冒充一般定理证明。",""]
    for n,(eid,lesson,src) in enumerate(staged(),1):
        lines.extend([f"## {n:02d}. {lesson.title}｜{eid}｜必修｜印刷页{src['printed_page']}",
            f"**项目编辑目标（非官方条款 ID）**：{src['goal']}",
            f"**知识类型**：{src['kind']}；**课程来源行**：{src['source_line']}",
            "**正式陈述**："+lesson.statement,
            "**适用前提**："+"；".join(lesson.conditions),
            "**先修**："+"；".join(lesson.prerequisites),
            "**逐步推理与依据（未经教师审核）**："])
        lines.extend(f"{j}. {s.statement}。依据：{s.reason}" for j,s in enumerate(lesson.derivation,1))
        lines.extend(["**错误主张**："+lesson.error.false_claim,
            "**具体反例**："+lesson.error.counterexample,
            "**错误原因**："+lesson.error.why_invalid,
            "**两道教师例题（学生自主挑战不得直接暴露）**："])
        for j,ex in enumerate(lesson.examples,1):
            lines.extend([f"- 例题{j}：{ex.question}",
                f"  - 推导：{ex.steps[0]}；{ex.steps[1]}",
                f"  - 答案：{ex.answer}；核对：{ex.check}"])
        lines.extend(["**分层提示**："]+[f"{j}. {h}" for j,h in enumerate(lesson.hints,1)])
        lines.extend(["**近迁移**："+lesson.near,"**远迁移**："+lesson.far,
            f"**有限计算算子**：{OPS[n-1]}（仅合法有限实例）",
            "**审核状态**：REVIEW_PENDING；学生发布否；定理一般性认证否",""])
    return "\n".join(lines).rstrip()+"\n"

def render_gaps(data):
    s=data["summary"]
    lines=["# Batch44｜项目自编课程目标缺稿账本（非官方完整分母）","",
        f"项目目标 {s['project_candidates']}；有独立待审稿 {s['direct_review_drafts']}；仅旧稿关系 {s['legacy_only']}；缺稿 {s['missing_editorial_link']}。",
        "七个官方完整课程知识原子分母均为 null；缺稿数不能充当官方未覆盖数。","",
        "|课程轨道|项目候选|直接待审稿|仅旧关联|缺直接稿|官方完整原子分母|",
        "|---|---:|---:|---:|---:|---|"]
    for track,counts in data["tracks"].items():
        lines.append(f"|{track}|{counts['project_candidate_count']}|{counts['with_direct_review_draft']}|"
                     f"{counts['legacy_association_only']}|{counts['missing_direct_editorial_link']}|null|")
    lines.extend(["","## 下一批实际内容缺口","","以下是尚无独立审核稿的前 60 项；所有项目仍需要官方条款逐项复核。",""])
    for r in [r for r in data["rows"] if r["editorial_status"]=="NO_DIRECT_LINK"][:60]:
        lines.append(f"- {r['editorial_id']}｜{r['track']}｜页 {r['printed_page']}：{r['goal']}")
    lines.extend(["","## 未完成门槛","",
        "- 未核验真实官方课程条款的七轨道完整原子分母。",
        "- 12 项只有历史讲义范围关联，未自动获得等价认证。",
        "- 历史 538 条证明步骤尚未形式认证；10 组内容冲突尚未裁决。",
        "- 数学教师批准 0，学生端正式深度内容发布 0。",
        "- 下一批继续必修、选择性必修未覆盖目标，审查可重复证明，联动 K08 真实 API 安全基线。",""])
    return "\n".join(lines)

def generate(*,check=False):
    a=audit();b=coverage_overlay()
    documents={AUDIT:json.dumps(a,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
       MANUSCRIPT:render_lessons(),
       COVERAGE:json.dumps(b,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
       GAPS:render_gaps(b)}
    for p,content in documents.items():
        if check:
            if not p.is_file() or p.read_text(encoding="utf-8")!=content:
                raise GateError("Batch44 report drift: "+str(p))
        else:
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(content,encoding="utf-8")
    return a["summary"],b["summary"]

def student_retrieval_projection():
    return dict(status="NO_APPROVED_GOAL_EVIDENCE",review_pending=20,
        student_documents=[],teacher_solutions_exposed=[],teacher_approved=0,
        student_published=0,official_atom_denominator=None)

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    print("PASS",generate(check=p.parse_args().check))
