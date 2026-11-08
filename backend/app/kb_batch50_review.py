"""Batch50: 20 original selective compulsory drafts, STRICTLY teacher-only.
313 project editorial candidates are NOT the official syllabus atom denominator.
"""
from __future__ import annotations
import hashlib
import json
from functools import lru_cache
from .kb_batch41_core_review import Lesson
from .kb_batch42_coverage import ROOT,GateError,TRACKS,Row
from .kb_batch49_review import coverage_overlay as previous
from .kb_batch50_exact import INDEX_OP,SAMPLES,witness

SOURCE = ROOT/"knowledge/editorial_review/kb_batch50_selective_statistics.jsonl"
SOURCE_SHA = "fd594c22a07b2ab10639b450c10b432602b1fe8951c6823e10fb61b9dd1a11c0"
PDF_SHA = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
AUDIT = ROOT/"docs/evaluation/KB_BATCH50_SELECTIVE_AUDIT.json"
MANUSCRIPT = ROOT/"docs/evaluation/KB_BATCH50_SELECTIVE_MANUSCRIPTS.md"
COVERAGE = ROOT/"docs/evaluation/KB_BATCH50_PROJECT_SCOPE_OVERLAY.json"
GAPS = ROOT/"docs/evaluation/KB_BATCH50_SCOPE_GAP_REVIEW.md"

def validate(raw:str, *,check_pin=True):
    if check_pin and hashlib.sha256(raw.encode("utf-8")).hexdigest()!=SOURCE_SHA:
        raise GateError("Batch50 authored source changed")
    before={r["editorial_id"]:r for r in previous()["rows"]}
    items=[];seen=set()
    for line in raw.splitlines():
        if not line.strip():continue
        data=json.loads(line)
        eid=data.pop("editorial_id")
        if eid in seen or eid not in before: raise GateError("duplicate/unknown editorial ID")
        src=before[eid]
        if src["editorial_status"]!="NO_DIRECT_LINK" or src["direct_review_drafts"]:
            raise GateError("already linked editorial atom")
        if src["track"]!="SELECTIVE_COMPULSORY":
            raise GateError("cross-track promotion")
        seen.add(eid)
        data["goal"]=src["goal"]
        lesson=Lesson.model_validate(data)
        if (lesson.status!="REVIEW_PENDING" or lesson.teacher_solution_visibility!="TEACHER_ONLY"
            or lesson.student_publishable or lesson.approved_reviewer is not None
            or lesson.proof_status!="NOT_FORMALLY_CERTIFIED"
            or lesson.source_license!="PROJECT_AUTHORED"):
            raise GateError("unauthorized approval or publication")
        if len(lesson.conditions)<2 or len(lesson.prerequisites)<2:
            raise GateError("insufficient mathematical premise / prerequisites")
        items.append((eid,lesson,src))
    if len(items)!=20 or len(seen)!=20:
        raise GateError("expected exactly 20 previously uncovered selective editorial goals")
    if {eid for eid,_,_ in items}!={k for k,r in before.items() if r["editorial_status"]=="NO_DIRECT_LINK"}:
        raise GateError("remaining editorial gaps not fully addressed")
    return tuple(items)

@lru_cache(maxsize=1)
def staged():
    return validate(SOURCE.read_text(encoding="utf-8"))

def audit():
    items=[]
    for i,(eid,u,src) in enumerate(staged()):
        op=INDEX_OP.get(i)
        expected=None
        if op:
            valid,value,invalid=SAMPLES[op]
            ok=witness(op,valid);no=witness(op,invalid)
            if (ok["status"]!="FINITE_EXACT_CASE_ONLY" or ok["exact_value"]!=value
                or no["status"]!="CONDITIONS_NOT_ESTABLISHED"
                or ok["general_theorem_certified"] or ok["student_freeform_step_verified"]):
                raise GateError("finite mathematics oracle regression: "+op)
            expected=value
        canonical=json.dumps(u.model_dump(mode="json"),sort_keys=True,ensure_ascii=False,separators=(",",":"))
        items.append(dict(editorial_id=eid,track=src["track"],kind=src["kind"],goal=src["goal"],
          printed_page=src["printed_page"],editorial_source_line=src["source_line"],
          curriculum_source_sha256=src["source_sha256"],
          lesson_sha256=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
          review_status="REVIEW_PENDING",teacher_visibility="TEACHER_ONLY",
          math_proof_status="NOT_FORMALLY_CERTIFIED",finite_op=op,finite_witness=expected,
          finite_instance_checked=bool(op),formal_general_proof_certified=False,
          official_clause_certified=False,teacher_approved=False,student_published=False,
          student_freeform_step_verified=False,examples=len(u.examples),
          explicit_counterexamples=1,reasoning_stages=len(u.derivation),
          hint_levels=len(u.hints),transfer_tasks=2))
    return dict(schema_version="kb50-audit-v1",source_sha256=SOURCE_SHA,
      standard_pdf_sha256=PDF_SHA,official_seven_track_denominator=None,
      caution="Project editorial goal is NOT official independently certified curriculum atom. A finite calculation is NOT a mathematical proof.",
      summary=dict(new_drafts=20,selective_compulsory=20,examples=40,counterexamples=20,
       reasoning_stages=60,graduated_hints=60,transfers=40,finite_exact_oracles=17,
       research_method_drafts_without_numeric_proof=3,teacher_approved=0,student_published=0),
      items=items)

def coverage_overlay():
    prev=previous()
    ids={eid for eid,_,_ in staged()}
    rows=[]
    for record in prev["rows"]:
        new=record["editorial_id"] in ids
        r={**record,"batch50_new_teacher_review_draft":new}
        if new:
            if r["editorial_status"]!="NO_DIRECT_LINK" or r["direct_review_drafts"]:
                raise GateError("duplicate editorial link")
            r["editorial_status"]="DRAFT_REVIEW_PENDING"
            r["direct_review_drafts"]=["kb50:"+r["editorial_id"]]
        rows.append(r)
    tracks={}
    for name in TRACKS:
        sub=[r for r in rows if r["track"]==name]
        tracks[name]=dict(project_candidate_count=len(sub),
          with_direct_review_draft=sum(r["editorial_status"]=="DRAFT_REVIEW_PENDING" for r in sub),
          legacy_association_only=sum(r["editorial_status"]=="LEGACY_ONLY_NOT_EQUIVALENT" for r in sub),
          missing_direct_editorial_link=sum(r["editorial_status"]=="NO_DIRECT_LINK" for r in sub),
          official_atom_denominator=None,official_verified_coverage=None,teacher_approved=0,student_published=0)
        assert len(sub)==sum(tracks[name][k] for k in
          ("with_direct_review_draft","legacy_association_only","missing_direct_editorial_link"))
    if len(rows)!=313 or len(ids)!=20: raise GateError("editorial ledger row drift")
    summary=dict(project_candidates=313,direct_review_drafts=301,legacy_only=12,
      missing_editorial_link=0,batch50_new=20,compulsory_remaining=0,
      selective_compulsory_remaining=0,teacher_approved=0,student_published=0,
      official_atom_denominator=None)
    if (sum(x["with_direct_review_draft"] for x in tracks.values()),
        sum(x["legacy_association_only"] for x in tracks.values()),
        sum(x["missing_direct_editorial_link"] for x in tracks.values()))!=(301,12,0):
        raise GateError("scope counts mismatch")
    if any(any(r.get(k) for k in ("official_clause_verified","math_certified",
                                 "teacher_approved","student_published")) for r in rows):
        raise GateError("unreviewed unit promoted")
    return dict(schema_version="kb50-editorial-overlay-v1",
      base="docs/evaluation/KB_BATCH49_PROJECT_SCOPE_OVERLAY.json",
      warning="313 incomplete project-authored editorial goals NOT official syllabus atom denominator. 12 legacy-only non-equivalent items remain.",
      summary=summary,tracks=tracks,rows=rows)

def render_manuscripts():
    lines=["# Batch50｜选择性必修统计、回归与研究：20 篇原创教师待审稿","",
      "项目编辑目标具有课标印刷页线索但**尚未**逐项确认为独立官方条款；不计为国家正式课程覆盖率。",
      "前17篇有有限数学实例核验，后3篇为研究活动方法学，不伪造一般定理的证明。",
      "**全部 REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED，不得面向学生公开完整教师侧解答。**",""]
    for i,(eid,u,src) in enumerate(staged()):
        lines += [f"## {i+1:02d}. {u.title}｜{eid}｜课标印刷页{src['printed_page']}",
          f"**项目编辑目标**：{src['goal']}；**类型**：{src['kind']}；**来源行**：{src['source_line']}",
          f"**数学陈述/定义**：{u.statement}","**适用条件**："+"；".join(u.conditions),
          "**先修关系**："+"；".join(u.prerequisites),"**逐步推理与逐项依据（尚未经教师认证）**："]
        for j,step in enumerate(u.derivation,1):
            lines.append(f"{j}. {step.statement}（依据：{step.reason}）")
        lines += [f"**典型错误断言**：{u.error.false_claim}",
          f"**具体反例/不适用例**：{u.error.counterexample}",
          f"**错因**：{u.error.why_invalid}","**教师侧例题（自主解题中不能直接公开答案）**："]
        for j,e in enumerate(u.examples,1):
            lines += [f"- 例题{j}：{e.question}",f"  - 推理1：{e.steps[0]}",
                      f"  - 推理2：{e.steps[1]}",f"  - 答案：{e.answer}；核对：{e.check}"]
        lines += ["**三级非剧透提示**："]
        for j,h in enumerate(u.hints,1):lines.append(f"{j}. {h}")
        lines += [f"**近迁移**：{u.near}",f"**远迁移**：{u.far}",
          f"**独立有限数学实例见证**：{INDEX_OP.get(i,'不适用：研究活动方法而非数值定理')}",
          "**状态**：REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED",""]
    return "\n".join(lines).rstrip()+"\n"

def render_gaps(overlay):
    t=overlay["tracks"]
    lines=["# Batch50｜课程范围审计：编辑候选零缺稿 ≠ 官方知识库完整覆盖","",
      "313是项目编辑候选，不是官方完整原子分母；301份直接待审稿、12项旧关联、0项无稿。正式七轨道课程知识原子分母保持null。",
      "真实教师批准0，正式学生发布0；有限实例检查不等于数学证明。","",
      "|轨道|项目候选|直接待审稿|仅历史非等价关联|直接缺稿|官方分母|",
      "|---|---:|---:|---:|---:|---|"]
    for name,x in t.items():
        lines.append(f"|{name}|{x['project_candidate_count']}|{x['with_direct_review_draft']}|{x['legacy_association_only']}|{x['missing_direct_editorial_link']}|null|")
    lines += ["","## 12项仅旧稿关联的编辑目标（不等价认证）",""]
    for r in overlay["rows"]:
        if r["editorial_status"]=="LEGACY_ONLY_NOT_EQUIVALENT":
            lines.append(f"- {r['editorial_id']}｜{r['track']}｜页{r['printed_page']}｜{r['goal']}")
    lines += ["","## 明确尚未达到的正式验收条件",
      "- 2017/2020版原课标七轨道逐条、未编号要求拆分去重：全量分母未认证。",
      "- 12项非等价历史关联必须重新核对范围、补足相关精确数学内容并教师复核。",
      "- 历史538项证明步骤未完成形式认证，10项数学冲突仍待裁决。",
      "- 301条直接关联仅代表具备待审稿，不等于教师已批准的正式讲义；需逐篇语义校核与课堂试验。",
      "- K08生产索引、冻结API vs 规则基线对比及真实教师审核尚未完成。",""]
    return "\n".join(lines)
def generate(*,check=False):
    docs={AUDIT:json.dumps(audit(),ensure_ascii=False,indent=2,sort_keys=True)+"\n",
          COVERAGE:json.dumps(coverage_overlay(),ensure_ascii=False,indent=2,sort_keys=True)+"\n",
          MANUSCRIPT:render_manuscripts(),GAPS:render_gaps(coverage_overlay())}
    for file,content in docs.items():
        if check:
            if not file.is_file() or file.read_text(encoding="utf-8")!=content:
                raise GateError("generated content drift: "+str(file))
        else:
            file.parent.mkdir(parents=True,exist_ok=True);file.write_text(content,encoding="utf-8")
    return audit()["summary"],coverage_overlay()["summary"]
def student_retrieval_projection():
    return dict(status="NO_APPROVED_GOAL_EVIDENCE",review_pending=20,
      teacher_approved=0,student_published=0,student_documents=[],
      teacher_solutions_exposed=[],official_atom_denominator=None)
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    print("BATCH50",generate(check=p.parse_args().check))
