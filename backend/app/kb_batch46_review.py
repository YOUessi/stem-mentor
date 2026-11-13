"""Batch46 K00/K01/K02/K03/K07/K08/K09: source pinned selective course manuscripts.
Editorial candidates are NOT a complete official syllabus. No certification or student publishing.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import hashlib
import json

from .kb_batch41_core_review import Lesson
from .kb_batch42_coverage import ROOT, GateError, TRACKS, Row
from .kb_batch45_review import coverage_overlay as previous_overlay
from .kb_batch46_exact import OPS, SAMPLES, witness

SOURCE=ROOT/"knowledge/editorial_review/kb_batch46_selective_depth.jsonl"
SOURCE_SHA="4fa55bbf53019135a628fd07fb25cfaf78e2d849393cfc831dcd7c8fe186de9c"
AUDIT=ROOT/"docs/evaluation/KB_BATCH46_SELECTIVE_DEPTH_AUDIT.json"
MANUSCRIPT=ROOT/"docs/evaluation/KB_BATCH46_SELECTIVE_DEPTH_MANUSCRIPTS.md"
COVERAGE=ROOT/"docs/evaluation/KB_BATCH46_PROJECT_SCOPE_OVERLAY.json"
GAPS=ROOT/"docs/evaluation/KB_BATCH46_PROJECT_SCOPE_GAPS.md"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"

def validate(raw: str, *,check_pin=True):
    if check_pin and hashlib.sha256(raw.encode("utf-8")).hexdigest()!=SOURCE_SHA:
        raise GateError("Batch46 original editorial source SHA drift")
    previous={r["editorial_id"]:r for r in previous_overlay()["rows"]}
    selected=[];used=set()
    for line in raw.splitlines():
        if not line.strip():continue
        data=json.loads(line)
        eid=data.pop("editorial_id")
        if eid in used:raise GateError("duplicate draft")
        if eid not in previous:raise GateError("orphan editorial target")
        src=previous[eid]
        if (src["track"]!="SELECTIVE_COMPULSORY" or
            src["editorial_status"]!="NO_DIRECT_LINK" or src["direct_review_drafts"]):
            raise GateError("previously covered or cross-track editorial target")
        used.add(eid)
        data["goal"]=src["goal"]
        lesson=Lesson.model_validate(data)
        if lesson.status!="REVIEW_PENDING" or lesson.student_publishable or lesson.approved_reviewer is not None:
            raise GateError("teacher-only gate violated")
        if lesson.proof_status!="NOT_FORMALLY_CERTIFIED" or lesson.source_license!="PROJECT_AUTHORED":
            raise GateError("mathematical proof or license certification forged")
        selected.append((eid,lesson,src))
    if len(selected)!=20 or len(used)!=20 or len(OPS)!=20 or len(SAMPLES)!=20:
        raise GateError("Batch46 needs 20 distinct complete selective drafts + independent finite evidence")
    return tuple(selected)

@lru_cache(maxsize=1)
def staged():
    return validate(SOURCE.read_text(encoding="utf-8"))

def audit():
    items=[]
    for i,(eid,lesson,src) in enumerate(staged()):
        op=OPS[i];valid,expected,invalid=SAMPLES[op]
        good=witness(op,valid);bad=witness(op,invalid)
        if (good["status"]!="FINITE_EXACT_CASE_ONLY" or good["exact_value"]!=expected or
            bad["status"]!="CONDITIONS_NOT_ESTABLISHED"):
            raise GateError("Exact finite math sample mismatch at "+op)
        canonical=json.dumps(lesson.model_dump(mode="json"),ensure_ascii=False,sort_keys=True,separators=(",",":"))
        items.append(dict(editorial_id=eid,track=src["track"],project_goal=src["goal"],
            source_printed_page=src["printed_page"],source_editorial_line=src["source_line"],
            source_sha256=src["source_sha256"],content_sha256=hashlib.sha256(canonical.encode()).hexdigest(),
            project_editorial_kind=src["kind"],review_status="REVIEW_PENDING",
            source_license="PROJECT_AUTHORED",teacher_visibility="TEACHER_ONLY",
            math_proof_status="NOT_FORMALLY_CERTIFIED",math_finite_op=op,
            math_finite_witness=good["exact_value"],invalid_premise_rejected=True,
            official_clause_certified=False,formal_proof_certified=False,
            teacher_approved=False,student_published=False,
            student_freeform_step_verified=False,examples=2,counterexamples=1,
            derivation_steps=3,hint_levels=3,near_far_transfers=2))
    return dict(schema_version="kb46-selective-audit-v1",authored_source_sha256=SOURCE_SHA,
        standard_source_pdf_sha256=PDF_SHA,official_atomic_denominator=None,
        warning="20 PROJECT EDITORIAL candidates, not official syllabus atoms. Finite exact checks do not prove general theorems.",
        summary=dict(new_review_drafts=20,selective_compulsory=20,
            teacher_only_examples=40,concrete_counterexamples=20,
            staged_derivation_steps=60,graduated_hints=60,near_far_transfers=40,
            bounded_math_oracles=20,approved=0,student_published=0),
        items=items)

def coverage_overlay():
    previous=previous_overlay()
    additions={eid for eid,_,_ in staged()}
    rows=[]
    for item in previous["rows"]:
        new=item["editorial_id"] in additions
        row={**item,"batch46_new_teacher_review_draft":new}
        if new:
            if row["editorial_status"]!="NO_DIRECT_LINK" or row["direct_review_drafts"]:
                raise GateError("not missing goal")
            row["editorial_status"]="DRAFT_REVIEW_PENDING"
            row["direct_review_drafts"]=[f"kb46:{row['editorial_id']}"]
        rows.append(row)
    tracks={}
    for t in TRACKS:
        selected=[r for r in rows if r["track"]==t]
        tracks[t]=dict(project_candidate_count=len(selected),
            with_direct_review_draft=sum(r["editorial_status"]=="DRAFT_REVIEW_PENDING" for r in selected),
            legacy_association_only=sum(r["editorial_status"]=="LEGACY_ONLY_NOT_EQUIVALENT" for r in selected),
            missing_direct_editorial_link=sum(r["editorial_status"]=="NO_DIRECT_LINK" for r in selected),
            official_atom_denominator=None,official_verified_coverage=None,
            teacher_approved=0,student_published=0)
        if sum(tracks[t][k] for k in ["with_direct_review_draft","legacy_association_only",
                                       "missing_direct_editorial_link"])!=len(selected):
            raise GateError("bad project editorial accounting")
    summary=dict(project_candidates=313,direct_review_drafts=221,legacy_only=12,
                 missing_editorial_link=80,batch46_new=20,
                 teacher_approved=0,student_published=0,official_atom_denominator=None)
    assert len(rows)==313 and len(additions)==20
    if (sum(v["with_direct_review_draft"] for v in tracks.values()),
        sum(v["legacy_association_only"] for v in tracks.values()),
        sum(v["missing_direct_editorial_link"] for v in tracks.values()))!=(221,12,80):
        raise GateError("expected project candidates 221/12/80")
    if any(any(r.get(k) for k in ["official_clause_verified","math_certified",
                                   "teacher_approved","student_published"]) for r in rows):
        raise GateError("draft silently promoted")
    return dict(schema_version="kb46-project-editorial-overlay-v1",
        base="docs/evaluation/KB_BATCH45_PROJECT_SCOPE_OVERLAY.json",
        warning="313 project editorial candidates, NOT a complete official seven-track atomic denominator.",
        summary=summary,tracks=tracks,rows=rows)

def render():
    out=["# Batch46｜选择性必修 20 篇原创数学教师侧审核讲义","",
         "来源：高中数学课标 2017/2020 对应页的项目原创编辑目标，不是逐项认证的官方知识原子。",
         "状态：REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED。有限例子核对不构成一般定理证明。",""]
    for n,(eid,u,src) in enumerate(staged(),1):
        out += [f"## {n:02d}. {u.title}（{eid}，印刷页{src['printed_page']}）",
            f"**项目编辑目标**：{src['goal']}；**知识类型**：{src['kind']}；**来源行**：{src['source_line']}",
            f"**正式表述**：{u.statement}",
            "**适用条件**："+"；".join(u.conditions),
            "**先修知识**："+"；".join(u.prerequisites),
            "**分步论证与理由（仍需教师审核）**："]
        for j,s in enumerate(u.derivation,1):out.append(f"{j}. {s.statement}（依据：{s.reason}）")
        out += ["**错误说法**："+u.error.false_claim,
                "**具体反例**："+u.error.counterexample,
                "**错因**："+u.error.why_invalid,
                "**教师侧完整例题，学生不可直接检索**："]
        for j,ex in enumerate(u.examples,1):
            out += [f"- 例{j}：{ex.question}",
                    f"  - 步骤1：{ex.steps[0]}",
                    f"  - 步骤2：{ex.steps[1]}",
                    f"  - 结果：{ex.answer}；交叉核对：{ex.check}"]
        out.append("**非剧透渐进提示（分级权限）**：")
        for j,h in enumerate(u.hints,1):out.append(f"{j}. {h}")
        out += [f"**近迁移**：{u.near}",f"**远迁移**：{u.far}",
                f"**有限精确实例检查**：{OPS[n-1]}（不意味着一般命题认证）",
                "**状态**：REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED",""]
    return "\n".join(out).rstrip()+"\n"

def render_gaps(o):
    s=o["summary"]
    out=["# Batch46｜课程项目编辑目标追踪（非官方全量分母）","",
         f"项目编辑候选{s['project_candidates']}；已有待审稿{s['direct_review_drafts']}；仅旧关联{s['legacy_only']}；剩余缺稿{s['missing_editorial_link']}。",
         "官方必修、选择性必修、选修 A–E **七轨道的原子知识总数仍为 null**，严禁当成真实课标覆盖率。",
         "", "|轨道|候选|关联待审稿|仅旧关联|缺稿|官方原子总数|",
         "|---|---:|---:|---:|---:|---|"]
    for t,v in o["tracks"].items():
        out.append(f"|{t}|{v['project_candidate_count']}|{v['with_direct_review_draft']}|{v['legacy_association_only']}|{v['missing_direct_editorial_link']}|null|")
    out += ["", "## 全部剩余未有直接审核稿的项目候选（逐条待办）",""]
    for row in o["rows"]:
        if row["editorial_status"]=="NO_DIRECT_LINK":
            out.append(f"- {row['editorial_id']}｜{row['track']}｜页{row['printed_page']}｜{row['goal']}")
    out += ["","## 发布门禁","",
        "- 12 项历史关联尚未完成等价认证。",
        "- 538 条历史证明步骤尚未形式认证，10 组数学冲突未裁决。",
        "- 教师正式批准0、学生正式深度发布0，未建立官方七轨道知识原子全量分母。",""]
    return "\n".join(out)

def generate(*,check=False):
    a=audit();b=coverage_overlay()
    docs={AUDIT:json.dumps(a,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
          MANUSCRIPT:render(),COVERAGE:json.dumps(b,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
          GAPS:render_gaps(b)}
    for p,t in docs.items():
        if check:
            if not p.is_file() or p.read_text(encoding="utf-8")!=t:raise GateError("generated file drift "+str(p))
        else:
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(t,encoding="utf-8")
    return a["summary"],b["summary"]

def student_retrieval_projection():
    return dict(status="NO_APPROVED_GOAL_EVIDENCE",review_pending=20,
                teacher_approved=0,student_published=0,
                student_documents=[],teacher_solutions_exposed=[],official_atom_denominator=None)

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    print("BATCH46",generate(check=p.parse_args().check))
