"""Batch45 24 full original compulsory review lessons: frozen editable source and evidence.
Every drafted goal remains NON-OFFICIAL, REVIEW_PENDING and TEACHER_ONLY.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache

from .kb_batch41_core_review import Lesson
from .kb_batch42_coverage import ROOT, GateError, TRACKS
from .kb_batch44_review import coverage_overlay as previous_overlay
from .kb_batch45_exact import KEYS,VALID,INVALID,EXPECTED,witness

SOURCE=ROOT/"knowledge/editorial_review/kb_batch45_core_depth.jsonl"
SOURCE_SHA="79f51a9be48df535d36c1c7f87ef8b233f7bf593879cba8e686ae8f055aad5dd"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
AUDIT=ROOT/"docs/evaluation/KB_BATCH45_CORE_DEPTH_AUDIT.json"
MANUSCRIPT=ROOT/"docs/evaluation/KB_BATCH45_CORE_DEPTH_MANUSCRIPTS.md"
COVERAGE=ROOT/"docs/evaluation/KB_BATCH45_PROJECT_SCOPE_OVERLAY.json"
GAPS=ROOT/"docs/evaluation/KB_BATCH45_PROJECT_SCOPE_GAPS.md"
OPS=tuple(KEYS)

def validate(raw: str, *, check_pin=True):
    if check_pin and hashlib.sha256(raw.encode("utf-8")).hexdigest()!=SOURCE_SHA:
        raise GateError("Batch45 authoring SHA drift; explicit review required")
    rows={r["editorial_id"]:r for r in previous_overlay()["rows"]}
    result=[];seen=set()
    for line in raw.splitlines():
        if not line.strip():continue
        rec=json.loads(line)
        eid=rec.pop("editorial_id")
        if eid in seen:raise GateError("duplicate target")
        if eid not in rows:raise GateError("orphan target")
        src=rows[eid]
        if src["track"]!="COMPULSORY" or src["editorial_status"]!="NO_DIRECT_LINK" or src["direct_review_drafts"]:
            raise GateError("cannot overwrite existing or cross-track draft")
        seen.add(eid)
        rec["goal"]=src["goal"]
        rec["derivation"]=[dict(statement=step,reason=reason) for step,reason in rec["derivation"]]
        claim,bad,why=rec["error"]
        rec["error"]=dict(false_claim=claim,counterexample=bad,why_invalid=why)
        rec["examples"]=[dict(question=q,steps=[s1,s2],answer=a,check=c)
                         for q,s1,s2,a,c in rec["examples"]]
        lesson=Lesson.model_validate(rec)
        if (lesson.status!="REVIEW_PENDING" or lesson.student_publishable or
            lesson.approved_reviewer is not None or lesson.teacher_solution_visibility!="TEACHER_ONLY" or
            lesson.proof_status!="NOT_FORMALLY_CERTIFIED" or lesson.source_license!="PROJECT_AUTHORED"):
            raise GateError("forged approval/proof/student visibility")
        result.append((eid,lesson,src))
    if len(result)!=24 or len(seen)!=24 or len(OPS)!=24:
        raise GateError("Batch45 requires 24 full original nonduplicate compulsory lessons")
    if set(OPS)!=set(VALID)!=set(INVALID)!=set(EXPECTED):
        raise GateError("operator fixtures drift")
    return tuple(result)

@lru_cache(maxsize=1)
def staged():
    return validate(SOURCE.read_text(encoding="utf-8"))

def audit():
    items=[]
    for idx,(eid,lesson,src) in enumerate(staged()):
        op=OPS[idx]
        good=witness(op,VALID[op]);bad=witness(op,INVALID[op])
        if good["status"]!="FINITE_EXACT_CASE_ONLY" or good["exact_value"]!=EXPECTED[op] or bad["status"]!="CONDITIONS_NOT_ESTABLISHED":
            raise GateError("bounded math witness mismatch: "+op)
        canonical=json.dumps(lesson.model_dump(mode="json"),ensure_ascii=False,sort_keys=True,separators=(",",":"))
        items.append(dict(
            editorial_id=eid,goal=src["goal"],source_printed_page=src["printed_page"],
            source_line=src["source_line"],source_project_sha256=src["source_sha256"],
            content_sha256=hashlib.sha256(canonical.encode()).hexdigest(),
            project_editorial_kind=src["kind"],source_license="PROJECT_AUTHORED",
            source_standard="2017/2020 project-authored editorial paraphrase (NOT official-atom certified)",
            content_status="REVIEW_PENDING",teacher_solution_visibility="TEACHER_ONLY",
            theorem_proof_status="NOT_FORMALLY_CERTIFIED",student_publishable=False,
            teacher_approved=False,math_certified=False,student_freeform_step_verified=False,
            general_theorem_certified=False,official_clause_verified=False,
            math_finite_witness=good["exact_value"],math_premise_rejected=True,
            exact_operator=op,examples=2,derivation_steps=3,nonexamples=1,hint_levels=3,transfers=2))
    return dict(schema_version="kb45-core-review-v1",source_sha256=SOURCE_SHA,
        standard_pdf_sha256=PDF_SHA,
        warning="Only original editorial drafts and bounded exact witnesses; no teacher/formal certification or student publication.",
        summary=dict(new_review_drafts=24,compulsory=24,selective_compulsory=0,
            teacher_only_worked_examples=48,nonexamples=24,
            derivation_steps=72,hints=72,near_far_transfers=48,
            bounded_finite_math_witnesses=24,math_proofs_formally_certified=0,
            official_atom_denominator=None,teacher_approved=0,student_published=0),
        items=items)

def coverage_overlay():
    prev=previous_overlay()
    additions={eid for eid,_,_ in staged()}
    rows=[]
    for row in prev["rows"]:
        if row["editorial_id"] in additions:
            if row["editorial_status"]!="NO_DIRECT_LINK" or row["direct_review_drafts"]:
                raise GateError("attempt to certify preexisting draft")
            row={**row,"direct_review_drafts":[f"kb45:{row['editorial_id']}"],
                 "editorial_status":"DRAFT_REVIEW_PENDING",
                 "batch45_new_teacher_review_draft":True}
        else:
            row={**row,"batch45_new_teacher_review_draft":False}
        rows.append(row)
    if len(rows)!=313 or len(additions)!=24:raise GateError("project candidate set drift")
    tracks={}
    for t in TRACKS:
        selected=[r for r in rows if r["track"]==t]
        status=dict(project_candidate_count=len(selected),
            with_direct_review_draft=sum(r["editorial_status"]=="DRAFT_REVIEW_PENDING" for r in selected),
            legacy_association_only=sum(r["editorial_status"]=="LEGACY_ONLY_NOT_EQUIVALENT" for r in selected),
            missing_direct_editorial_link=sum(r["editorial_status"]=="NO_DIRECT_LINK" for r in selected),
            official_atom_denominator=None,official_verified_coverage=None,
            teacher_approved=0,student_published=0)
        if sum(status[k] for k in ("with_direct_review_draft","legacy_association_only","missing_direct_editorial_link"))!=len(selected):
            raise GateError("per-track accounting mismatch")
        tracks[t]=status
    summary=dict(project_candidates=313,direct_review_drafts=201,legacy_only=12,
                 missing_editorial_link=100,batch45_new=24,teacher_approved=0,
                 student_published=0,official_atom_denominator=None)
    if (sum(x["with_direct_review_draft"] for x in tracks.values()),
        sum(x["legacy_association_only"] for x in tracks.values()),
        sum(x["missing_direct_editorial_link"] for x in tracks.values()))!=(201,12,100):
        raise GateError("project coverage ledger expected 201/12/100")
    if any(r["teacher_approved"] or r["student_published"] or r["math_certified"]
           or r["official_clause_verified"] for r in rows):
        raise GateError("project draft incorrectly certified")
    return dict(schema_version="kb45-project-editorial-overlay-v1",
        warning="313 incomplete PROJECT editorial goals, NOT official syllabus denominator.",
        base="docs/evaluation/KB_BATCH44_PROJECT_SCOPE_OVERLAY.json",
        summary=summary,tracks=tracks,rows=rows)

def render_lessons():
    lines=["# Batch45｜24 篇原创必修高中数学教师审核稿","",
        "本批为项目编辑候选补缺，**不代表官方全量课标**，不用于学生端，未经真人教师批准。",
        "所有内容均 REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED。定义和方法只需合法性论证，不伪造形式证明。",""]
    for n,(eid,u,src) in enumerate(staged(),1):
        lines += [f"## {n:02d}. {u.title}｜{eid}｜页{src['printed_page']}",
            f"**项目课程编辑目标（非官方原子条款）**：{src['goal']}",
            f"**类型**：{src['kind']}；**课程来源行**：{src['source_line']}",
            "**数学表述**："+u.statement,
            "**使用范围与前提**："+"；".join(u.conditions),
            "**前置依赖**："+"；".join(u.prerequisites),
            "**分步论证及数学依据（待审核）**："]
        for j,step in enumerate(u.derivation,1):
            lines.append(f"{j}. {step.statement}（依据：{step.reason}）")
        lines += ["**典型错误**："+u.error.false_claim,
            "**失效反例**："+u.error.counterexample,
            "**为什么错误**："+u.error.why_invalid,
            "**教师侧典型例题（学生独立挑战不可直接查看）**："]
        for j,ex in enumerate(u.examples,1):
            lines += [f"- 例题{j}：{ex.question}",
                f"  - 过程1：{ex.steps[0]}",
                f"  - 过程2：{ex.steps[1]}",
                f"  - 答案：{ex.answer}；复核：{ex.check}"]
        lines += ["**分层提示（不泄漏例题完整答案）**："]
        for j,h in enumerate(u.hints,1):
            lines.append(f"{j}. {h}")
        lines += [f"**近迁移**：{u.near}",f"**远迁移**：{u.far}",
             f"**对应有限数学证据**：{OPS[n-1]}；只认可受控实例、不认证全部定理。",
             "**审核/发布**：REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED",""]
    return "\n".join(lines).rstrip()+"\n"

def render_gaps(overlay):
    s=overlay["summary"]
    lines=["# Batch45｜项目编辑候选缺稿矩阵（非官方知识原子分母）","",
      f"项目候选{s['project_candidates']}；直接待审核稿{s['direct_review_drafts']}；旧关系未认证{s['legacy_only']}；剩余无直接稿{s['missing_editorial_link']}。",
      "官方七轨道完整分母仍为 null，**不能以项目编辑候选总数计算官方覆盖率**。","",
      "|轨道|项目候选|待审核稿关联|仅旧关系|无直接稿|官方分母|",
      "|---|---:|---:|---:|---:|---|"]
    for track,val in overlay["tracks"].items():
        lines.append(f"|{track}|{val['project_candidate_count']}|{val['with_direct_review_draft']}|{val['legacy_association_only']}|{val['missing_direct_editorial_link']}|null|")
    lines += ["","## 后续批次缺稿候选（前60项）","","以下均需再次核对官方条款等价性：",""]
    for r in [x for x in overlay["rows"] if x["editorial_status"]=="NO_DIRECT_LINK"][:60]:
        lines.append(f"- {r['editorial_id']}｜{r['track']}｜页{r['printed_page']}｜{r['goal']}")
    lines += ["","## 未通过的发布门槛","",
       "- 必修、选择性必修和选修 A–E 的官方完整课标原子分母：null。",
       "- 12 项历史关联未获得等价认证。",
       "- 538 条历史证明步骤、10 组数学冲突仍需独立裁决。",
       "- 真实教师批准为0，学生端正式深度内容发布为0。",
       "- 下一批：继续必修34项与选择性必修66项项目编辑缺稿，严格检查课程来源。",""]
    return "\n".join(lines)

def generate(*,check=False):
    a=audit();b=coverage_overlay()
    docs={AUDIT:json.dumps(a,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
          MANUSCRIPT:render_lessons(),
          COVERAGE:json.dumps(b,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
          GAPS:render_gaps(b)}
    for p,txt in docs.items():
        if check:
            if not p.is_file() or p.read_text(encoding="utf-8")!=txt:
                raise GateError("generated evidence drift: "+str(p))
        else:
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(txt,encoding="utf-8")
    return a["summary"],b["summary"]

def student_retrieval_projection():
    return dict(status="NO_APPROVED_GOAL_EVIDENCE",review_pending=24,
        student_documents=[],teacher_solutions_exposed=[],teacher_approved=0,
        student_published=0,official_atom_denominator=None)

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    print("PASS",generate(check=parser.parse_args().check))
