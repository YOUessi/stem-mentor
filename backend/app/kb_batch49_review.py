"""K00-K09 review gate for 20 independently authored content lessons; NOT teacher-approved."""
from __future__ import annotations
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from .kb_batch41_core_review import Lesson
from .kb_batch42_coverage import ROOT,GateError,TRACKS
from .kb_batch48_review import coverage_overlay as prev_overlay
from .kb_batch49_exact import INDEX_OP,SAMPLES,witness

SOURCE=ROOT/"knowledge/editorial_review/kb_batch49_modeling_inference.jsonl"
SOURCE_SHA="a781c7207a8dde638bcbf238ed44e7f2fb21e80bc2b6081f771689a6fc165dc4"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
AUDIT=ROOT/"docs/evaluation/KB_BATCH49_MODELLING_AUDIT.json"
MANUSCRIPT=ROOT/"docs/evaluation/KB_BATCH49_MODELLING_MANUSCRIPTS.md"
COVERAGE=ROOT/"docs/evaluation/KB_BATCH49_PROJECT_SCOPE_OVERLAY.json"
GAPS=ROOT/"docs/evaluation/KB_BATCH49_PROJECT_SCOPE_GAPS.md"

def validate(raw:str,*,check_pin=True):
    if check_pin and hashlib.sha256(raw.encode("utf-8")).hexdigest()!=SOURCE_SHA:
        raise GateError("Batch49 source hash changed")
    prev={r["editorial_id"]:r for r in prev_overlay()["rows"]}
    result=[];seen=set()
    for line in raw.splitlines():
        if not line.strip(): continue
        data=json.loads(line)
        eid=data.pop("editorial_id")
        if eid in seen:raise GateError("duplicate editorial unit")
        if eid not in prev:raise GateError("unknown curriculum goal")
        src=prev[eid]
        if src["editorial_status"]!="NO_DIRECT_LINK" or src["direct_review_drafts"]:
            raise GateError("already linked curriculum goal")
        if src["track"] not in ("COMPULSORY","SELECTIVE_COMPULSORY"):
            raise GateError("cross-track scope promotion")
        seen.add(eid)
        data["goal"]=src["goal"]
        unit=Lesson.model_validate(data)
        if (unit.status!="REVIEW_PENDING" or unit.student_publishable or unit.approved_reviewer is not None
            or unit.source_license!="PROJECT_AUTHORED" or unit.proof_status!="NOT_FORMALLY_CERTIFIED"
            or unit.teacher_solution_visibility!="TEACHER_ONLY"):
            raise GateError("unauthorized content promotion")
        if len(unit.conditions)<2 or len(unit.prerequisites)<2:raise GateError("insufficient content conditions")
        result.append((eid,unit,src))
    if len(result)!=20 or len(seen)!=20:raise GateError("expected exactly twenty original reviews")
    if sum(x[2]["track"]=="COMPULSORY" for x in result)!=14:raise GateError("incorrect compulsory batch scope")
    if sum(x[2]["track"]=="SELECTIVE_COMPULSORY" for x in result)!=6:raise GateError("incorrect selective batch scope")
    return tuple(result)

@lru_cache(maxsize=1)
def staged():
    return validate(SOURCE.read_text(encoding="utf-8"))

def audit():
    items=[]
    for i,(eid,u,src) in enumerate(staged()):
        op=INDEX_OP.get(i)
        expected=None
        if op:
            good,value,bad=SAMPLES[op]
            w=witness(op,good);denied=witness(op,bad)
            if w["status"]!="FINITE_EXACT_CASE_ONLY" or w["exact_value"]!=value or denied["status"]!="CONDITIONS_NOT_ESTABLISHED":
                raise GateError("finite exact validation failed for "+op)
            expected=value
        canon=json.dumps(u.model_dump(mode="json"),ensure_ascii=False,sort_keys=True,separators=(",",":"))
        items.append(dict(editorial_id=eid,track=src["track"],goal=src["goal"],printed_page=src["printed_page"],
          editorial_line=src["source_line"],curriculum_source_sha256=src["source_sha256"],
          authored_content_sha256=hashlib.sha256(canon.encode()).hexdigest(),knowledge_kind=src["kind"],
          audit_status="REVIEW_PENDING",teacher_visibility="TEACHER_ONLY",
          math_proof_status="NOT_FORMALLY_CERTIFIED",finite_op=op,finite_witness=expected,
          mathematical_finite_case_available=bool(op),math_general_proof_certified=False,
          source_clause_certified=False,teacher_approved=False,student_published=False,
          student_freeform_step_verified=False,examples=len(u.examples),counterexamples=1,
          derivation_steps=len(u.derivation),hint_levels=len(u.hints),transfer_tasks=2))
    return dict(schema_version="kb49-audit-v1",source_sha256=SOURCE_SHA,standard_source_pdf_sha256=PDF_SHA,
      official_seven_track_denominator=None,
      caution="313 incomplete editorial goals are not official total. History-method modules are not mathematical numerical proofs.",
      summary=dict(new_review_drafts=20,compulsory=14,selective_compulsory=6,
         teacher_examples=40,explicit_counterexamples=20,reasoning_stages=60,
         graduated_hints=60,near_far_transfers=40,finite_math_oracles=17,
         nonnumeric_source_methods=3,teacher_approved=0,student_published=0),items=items)

def coverage_overlay():
    prev=prev_overlay()
    additions={eid for eid,_,_ in staged()}
    rows=[]
    for original in prev["rows"]:
        new=original["editorial_id"] in additions
        r={**original,"batch49_new_teacher_review_draft":new}
        if new:
            if r["editorial_status"]!="NO_DIRECT_LINK" or r["direct_review_drafts"]:
                raise GateError("duplicate content link")
            r["editorial_status"]="DRAFT_REVIEW_PENDING"
            r["direct_review_drafts"]=["kb49:"+r["editorial_id"]]
        rows.append(r)
    tracks={}
    for t in TRACKS:
        rr=[x for x in rows if x["track"]==t]
        tracks[t]=dict(project_candidate_count=len(rr),
           with_direct_review_draft=sum(x["editorial_status"]=="DRAFT_REVIEW_PENDING" for x in rr),
           legacy_association_only=sum(x["editorial_status"]=="LEGACY_ONLY_NOT_EQUIVALENT" for x in rr),
           missing_direct_editorial_link=sum(x["editorial_status"]=="NO_DIRECT_LINK" for x in rr),
           official_atom_denominator=None,official_verified_coverage=None,teacher_approved=0,student_published=0)
        assert len(rr)==sum(tracks[t][k] for k in
            ("with_direct_review_draft","legacy_association_only","missing_direct_editorial_link"))
    summary=dict(project_candidates=313,direct_review_drafts=281,legacy_only=12,
        missing_editorial_link=20,batch49_new=20,compulsory_remaining=0,
        selective_compulsory_remaining=20,teacher_approved=0,student_published=0,
        official_atom_denominator=None)
    assert len(rows)==313 and len(additions)==20
    assert (sum(x["with_direct_review_draft"] for x in tracks.values()),
            sum(x["legacy_association_only"] for x in tracks.values()),
            sum(x["missing_direct_editorial_link"] for x in tracks.values()))==(281,12,20)
    if any(any(x.get(k) for k in
       ("official_clause_verified","math_certified","teacher_approved","student_published")) for x in rows):
        raise GateError("unreviewed content promoted")
    return dict(schema_version="kb49-editorial-overlay-v1",
      base="docs/evaluation/KB_BATCH48_PROJECT_SCOPE_OVERLAY.json",
      warning="313 are incomplete project-authored editorial candidates; official atom denominator null.",
      summary=summary,tracks=tracks,rows=rows)

def render_manuscripts():
    lines=["# Batch49｜建模、空间几何、推断及数学文化：20 篇原创教师审核稿","",
      "以下项目编辑目标对应课标印刷页，但并未取得官方原子条款逐项等价确认。",
      "14 必修 + 6 选择性必修。史料主题仅提供核验方法，未提供未经确认的历史断言。",
      "**所有内容：REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED。**",""]
    for i,(eid,u,src) in enumerate(staged()):
        lines.extend([f"## {i+1:02d}. {u.title}（{eid}，印刷页{src['printed_page']}）",
            f"**项目编辑目标**：{src['goal']}；**类别**：{src['kind']}；**编辑来源行**：{src['source_line']}",
            f"**正式表述**：{u.statement}","**适用条件**："+"；".join(u.conditions),
            "**先修**："+"；".join(u.prerequisites),"**分步论证及其依据（仍需教师审核）**："])
        for j,p in enumerate(u.derivation,1):
            lines.append(f"{j}. {p.statement}（依据：{p.reason}）")
        lines.extend([f"**典型错解/断言**：{u.error.false_claim}",
          f"**具体反例/不适用例**：{u.error.counterexample}",
          f"**错因**：{u.error.why_invalid}","**两道教师侧完整例题（学生挑战不可直接检索）**："])
        for j,e in enumerate(u.examples,1):
            lines.extend([f"- 例题{j}：{e.question}",f"  - 步骤1：{e.steps[0]}",
                f"  - 步骤2：{e.steps[1]}",f"  - 结果：{e.answer}；核对：{e.check}"])
        lines.append("**三级非剧透提示**：")
        for j,h in enumerate(u.hints,1):lines.append(f"{j}. {h}")
        lines.extend([f"**近迁移**：{u.near}",f"**远迁移**：{u.far}",
          f"**有限数学实例验证**：{INDEX_OP.get(i,'不适用（史料方法；不能伪造数学证明）')}",
          "**审核门禁**：REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED",""])
    return "\n".join(lines).rstrip()+"\n"

def render_gaps(o):
    s=o["summary"]
    lines=["# Batch49｜项目课程编辑追踪（绝非官方完整课程分母）","",
      f"313条项目编辑候选中，{s['direct_review_drafts']}条有直接待审稿，12条仅非等价历史关联，{s['missing_editorial_link']}条无直接稿。",
      "官方七轨道原子知识分母全部为null；不能将281/313描述成课标覆盖率。","",
      "|轨道|候选|直接待审稿|仅非等价旧关联|缺稿|官方分母|",
      "|---|---:|---:|---:|---:|---|"]
    for t,v in o["tracks"].items():
        lines.append(f"|{t}|{v['project_candidate_count']}|{v['with_direct_review_draft']}|{v['legacy_association_only']}|{v['missing_direct_editorial_link']}|null|")
    lines.extend(["","## 剩余20项项目编辑目标（均选择性必修）",""])
    for r in o["rows"]:
        if r["editorial_status"]=="NO_DIRECT_LINK":
            lines.append(f"- {r['editorial_id']}｜页{r['printed_page']}｜{r['goal']}")
    lines.extend(["","## 独立阻断","- 官方条款完整原子化未完成，分母未确认。",
        "- 12个历史关联非数学等价认证；538条历史证明步骤待形式核验；10组数学冲突待裁决。",
        "- 真教师批准0、学生正式发布0；17项有限数学核验不能替代一般证明。",""])
    return "\n".join(lines)

def generate(*,check=False):
    a=audit();b=coverage_overlay()
    files={AUDIT:json.dumps(a,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
           COVERAGE:json.dumps(b,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
           MANUSCRIPT:render_manuscripts(),GAPS:render_gaps(b)}
    for path,content in files.items():
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8")!=content:raise GateError("artifact drift "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding="utf-8")
    return a["summary"],b["summary"]

def student_retrieval_projection():
    return dict(status="NO_APPROVED_GOAL_EVIDENCE",review_pending=20,teacher_approved=0,
       student_published=0,student_documents=[],teacher_solutions_exposed=[],
       official_atom_denominator=None)

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    print("BATCH49",generate(check=p.parse_args().check))
