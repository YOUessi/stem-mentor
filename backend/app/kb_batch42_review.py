"""Batch42 authored 20 high-frequency compulsory/selective manuscripts; never student-publishable.
Each exact PROJECT editorial source ID is checked against the independently pinned source ledger.
"""
from __future__ import annotations
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from .kb_batch41_core_review import Lesson
from .kb_batch42_coverage import ROOT, candidates, GateError

SOURCE=ROOT/"knowledge/editorial_review/kb_batch42_core_extension.jsonl"
SOURCE_SHA="02e1847c2800187cf4c9b2fa288ee10abc16b5c5e9687b98f3b05cdbd3fad81d"
MANUSCRIPT=ROOT/"docs/evaluation/KB_BATCH42_CORE_EXTENSION_MANUSCRIPTS.md"
AUDIT=ROOT/"docs/evaluation/KB_BATCH42_CORE_EXTENSION_AUDIT.json"

def validate(raw:str,*,check_pin=True):
    if check_pin and hashlib.sha256(raw.encode()).hexdigest()!=SOURCE_SHA:
        raise GateError("Batch42 frozen authored source SHA drift")
    indexed={r["editorial_id"]:r for r in candidates()}
    result=[]; seen=set()
    for line in raw.splitlines():
        if not line.strip():continue
        record=json.loads(line)
        eid=record.pop("editorial_id")
        if eid not in indexed:raise GateError("Orphan reviewer manuscript goal")
        if eid in seen:raise GateError("Duplicate reviewer manuscript goal")
        seen.add(eid)
        src=indexed[eid]
        if src["track"] not in ("COMPULSORY","SELECTIVE_COMPULSORY"):
            raise GateError("Only core/selective syllabus editorial targets")
        record["goal"]=src["goal"]
        record["derivation"]=[dict(statement=a,reason=b) for a,b in record["derivation"]]
        bad,ce,why=record["error"]
        record["error"]=dict(false_claim=bad,counterexample=ce,why_invalid=why)
        record["examples"]=[dict(question=q,steps=[s1,s2],answer=a,check=c)
                            for q,s1,s2,a,c in record["examples"]]
        item=Lesson.model_validate(record)
        if item.status!="REVIEW_PENDING" or item.student_publishable or item.proof_status!="NOT_FORMALLY_CERTIFIED":
            raise GateError("Author forged validation or release")
        result.append((eid,item,src))
    if len(result)!=20 or sum(src["track"]=="COMPULSORY" for _,_,src in result)!=10:
        raise GateError("20 exact new authored goals, 10+10 tracks, required")
    return tuple(result)

@lru_cache(maxsize=1)
def staged():
    return validate(SOURCE.read_text(encoding="utf-8"))

def audit():
    records=[]
    for eid,d,src in staged():
        serialized=json.dumps(d.model_dump(mode="json"),sort_keys=True,ensure_ascii=False,separators=(",",":"))
        records.append(dict(
            editorial_id=eid,source_sha256=src["source_sha256"],source_line=src["source_line"],
            source_printed_page=src["printed_page"],track=src["track"],kind=src["kind"],
            goal=src["goal"],manuscript_sha256=hashlib.sha256(serialized.encode()).hexdigest(),
            review_status="REVIEW_PENDING",teacher_solutions="TEACHER_ONLY",
            proof_status="NOT_FORMALLY_CERTIFIED",
            teacher_approved=False,student_publishable=False,
            source_clause_alignment_certified=False,
            exact_case_math_witness_certified_as_general_proof=False))
    return dict(schema_version="kb-batch42-review-manuscripts-v1",
        source_sha256=SOURCE_SHA,source_standard="2017/2020 curriculum project editorial draft",
        summary=dict(draft_count=len(records),
            by_track=dict(COMPULSORY=10,SELECTIVE_COMPULSORY=10),
            teacher_examples=len(records)*2,distinct_counterexamples=len(records),
            hint_levels=len(records)*3,near_far_transfers=len(records)*2,
            official_atomic_denominator=None,teacher_approved=0,student_published=0),
        records=records)

def render():
    out=["# Batch42｜20 篇原创必修/选择性必修教师审核稿（不可对学生发布）","",
        "来源为 Batch31/32 项目编辑学习目标，不能冒充官方知识原子 ID。证明型推导需教师审查；非定理的步骤是合法性解释，不是形式证明。",
        "全部 REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED，教师完整解答不可进入学生自主挑战或大模型 prompt。",""]
    for i,(eid,d,src) in enumerate(staged(),1):
        out += [f"## {i:02d}. {d.title}｜{eid}｜{src['track']}｜页 {src['printed_page']}",
            f"**项目编辑目标：** {src['goal']}",
            f"**类型：** {src['kind']}；**源行号：** {src['source_line']}（非官方原子）",
            f"**数学表述：** {d.statement}",
            "**前提与定义域：** "+"；".join(d.conditions),
            "**先修：** "+"；".join(d.prerequisites),
            "**分步论证／方法依据（教师仍须审核）：**"]
        out += [f"{j}. {step.statement}。依据：{step.reason}" for j,step in enumerate(d.derivation,1)]
        out += [f"**典型错法：** {d.error.false_claim}",
            f"**具体反例：** {d.error.counterexample}",
            f"**错误原因：** {d.error.why_invalid}",
            "**例题及教师侧解答（学生侧严禁直接检索）：**"]
        for j,ex in enumerate(d.examples,1):
            out += [f"- 例题{j}：{ex.question}",
                f"  - 步骤1：{ex.steps[0]}",
                f"  - 步骤2：{ex.steps[1]}",
                f"  - 解答：{ex.answer}。自检：{ex.check}"]
        out += ["**提示阶梯：**"] + [f"{j}. {h}" for j,h in enumerate(d.hints,1)]
        out += [f"**近迁移：** {d.near}",f"**远迁移：** {d.far}",
            "**审核：** REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED，student_publishable=false",""]
    return "\n".join(out).rstrip()+"\n"

def generate(*,check=False):
    m=json.dumps(audit(),ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    n=render()
    if check:
        if AUDIT.read_text(encoding="utf-8")!=m or MANUSCRIPT.read_text(encoding="utf-8")!=n:
            raise GateError("Batch42 manuscript/audit generated artifact drift")
    else:
        AUDIT.write_text(m,encoding="utf-8")
        MANUSCRIPT.write_text(n,encoding="utf-8")
    return audit()["summary"]

def student_retrieval_projection():
    return dict(status="UNPUBLISHED_REVIEW_ONLY",
        approved=0,student_published=0,review_pending=len(staged()),
        student_documents=[],teacher_solutions_exposed=[],
        official_atomic_denominators={t:None for t in
            ("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")})

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    print("PASS",generate(check=p.parse_args().check))
