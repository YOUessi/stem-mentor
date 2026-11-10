#!/usr/bin/env python3
"""Batch82: independent finite witnesses for all 10 frozen historical conflicts.

No source version selection, formal theorem certification or teacher approval.
Outputs are deterministic and reject upstream source/authoring tampering.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.kb_batch82_conflict_witness import OPS,check

SOURCE=ROOT/"docs/evaluation/KB_BATCH70_TEN_CONFLICT_PROOF_REVIEW.json"
AUTHOR=ROOT/"knowledge/editorial_review/kb_batch82_conflict_case_authoring.json"
OUT=ROOT/"docs/evaluation/KB_BATCH82_CONFLICT_EXACT_EVIDENCE.json"
DOC=ROOT/"docs/evaluation/KB_BATCH82_CONFLICT_EXACT_EVIDENCE.md"
SOURCE_SHA="38acbf47ca53b0c480f96daabc6746798f0a75e0349dad2560f8b2030cf9ba8c"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def encoded(data):
    return json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n"


def must(condition,message):
    if not condition:
        raise ValueError(message)


def build(source=None, author=None, source_hash=None):
    source=read(SOURCE) if source is None else source
    author=read(AUTHOR) if author is None else author
    actual=hashlib.sha256(SOURCE.read_bytes()).hexdigest() if source_hash is None else source_hash
    must(actual==SOURCE_SHA, "historical conflict dossier SHA altered")
    # Freeze the entire dossier, not merely its len or status.
    must(source==read(SOURCE),"source data disagrees with frozen original")
    must(source["conflicts_resolved"]==source["teacher_approved"]==source["general_proofs_certified"]==0,
         "historical conflict state illegally promoted")
    records=source["records"]
    must(len(records)==len(OPS)==10,"expected ten independent conflict records")
    must(author["schema_version"]=="kb82-independent-conflict-exact-evidence-v1"
         and author["review_status"]=="REVIEW_PENDING"
         and author["authoring_origin"]=="ORIGINAL_PROJECT_AUTHORED"
         and author["teacher_approved"] is False
         and author["student_publishable"] is False
         and author["general_proof_certified"] is False,"authoring release state violation")
    items=author["cases"]
    must(len(items)==10 and [v["op"] for v in items]==list(OPS),"conflict case order drift")
    result=[]
    for ix,(record,item) in enumerate(zip(records,items),1):
        must(record["conflict_index"]==ix-1
             and record["dispute_resolution"]=="UNRESOLVED_PENDING_INDEPENDENT_MATH_AND_TEACHER_REVIEW"
             and record["version_winner"] is None
             and record["general_proof_certified"] is False
             and record["student_publishable"] is False
             and record["teacher_review"]=="REVIEW_PENDING",
             "conflict already adjudicated or source order altered")
        must(len(item["reason"])>=20 and len(item["transfer"])>=12 and len(item["topic"])>=3,
             "independent reason or transfer too short")
        must(len(item["invalid"])>=2,"require at least two independent failed-condition witnesses")
        good,ev=check(item["op"],item["valid"])
        must(good=="FINITE_EXACT_WITNESS_ONLY" and bool(ev),"positive condition witness failed")
        rejected=[]
        for invalid in item["invalid"]:
            state,reasons=check(item["op"],invalid)
            must(state=="CONDITIONS_NOT_ESTABLISHED" and bool(reasons.get("failed_condition")),
                 "invalid case unexpectedly passed")
            rejected.append({"input":invalid,"evidence":reasons})
        extra=[]
        for valid in item.get("extra_valid",[]):
            state,evidence=check(item["op"],valid)
            must(state=="FINITE_EXACT_WITNESS_ONLY", "extra positive case unexpectedly rejected")
            extra.append({"input":valid,"evidence":evidence})
        result.append({
            "review_packet_id":f"KB82-IC-{ix:02}", "historical_conflict_id":record["conflict_id"],
            "active_sha256":record["active_sha256"],"candidate_sha256":record["candidate_sha256"],
            "op":item["op"],"topic":item["topic"],"independent_reason":item["reason"],
            "far_transfer":item["transfer"],"source_original_assumptions":record["assumptions"],
            "source_precise_statement":record["precise_statement"],
            "positive":{"input":item["valid"],"finite_evidence":ev},
            "negative":rejected,"extra_positive":extra,
            "review_status":"REVIEW_PENDING","teacher_solution_visibility":"TEACHER_ONLY",
            "student_publishable":False,"teacher_approved":False,
            "formal_math_certification":"NOT_FORMALLY_VERIFIED",
            "active_version_preferred":None,"candidate_version_preferred":None,
            "conflict_resolution":"UNRESOLVED_NEEDS_INDEPENDENT_TEACHER",
            "evidence_scope":"FINITE_EXACT_CASES_AND_PRECONDITIONS_ONLY",
        })
    must(len({r["historical_conflict_id"] for r in result})==10,
         "independent conflict ids collided")
    out={
        "schema_version":"kb82-exact-conflict-witnesses-v1",
        "conflicts_total":10,"conflicts_resolved":0,"general_proofs_formally_certified":0,
        "teacher_approved":0,"student_publishable":0,"scope":"PROJECT_HISTORICAL_DRAFT_CONFLICTS_NOT_OFFICIAL_ATOMS",
        "source_dossier_sha256":SOURCE_SHA,
        "authoring_sha256":hashlib.sha256(AUTHOR.read_bytes()).hexdigest(),
        "witnesses":result,
        "finite_positive_cases":sum(1+len(x["extra_positive"]) for x in result),
        "finite_negative_cases":sum(len(x["negative"]) for x in result),
        "official_curriculum_atom_denominator":None,
    }
    must(out["finite_positive_cases"]>=10 and out["finite_negative_cases"]>=20,
         "insufficient independent bounded evidence")
    return out


def markdown(out):
    rows=[
        "# Batch82｜10组历史数学冲突的独立精确实例复核",
        "",
        "**全部10组仍未裁决，教师批准0，形式证明认证0。**",
        "数学工具在有界整数/有理数实例中独立核验前提和计算，不能凭这些算例决定冲突两版本谁正确。",
        "结果全部仅为编辑侧审查证据，禁止进入学生权威检索。",
        "",
        f"来源SHA256：\u0060{out['source_dossier_sha256']}\u0060；原创作者稿SHA256：\u0060{out['authoring_sha256']}\u0060。",
        f"有限正例{out['finite_positive_cases']}项、失效前提负例{out['finite_negative_cases']}项；全部冲突结论待人工裁决。",
        "",
        "| 编号 | 数学争议 | 正向有界检查 | 负面前提拒绝 | 状态 |",
        "|---|---|---:|---:|---|",
    ]
    for r in out["witnesses"]:
        rows.append(f"| {r['review_packet_id']} | {r['topic']} | {1+len(r['extra_positive'])} | {len(r['negative'])} | REVIEW_PENDING |")
    rows+=["","## 真正未完成的事情",
           "逐条比较活跃版/候选版在完整域、量词、边界条件和一般性证明中的正确性；需要独立数学教师签署裁决，任何自动化程序不代签。",
           "通过GitHub版本化审查后，才可决定是否从学生权威知识库撤回错误版本；本批没有改变任何学生可见索引。",
           ""]
    return "\n".join(rows)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    data=build()
    expected={OUT:encoded(data),DOC:markdown(data)}
    if args.check:
        for path,contents in expected.items():
            must(path.exists() and path.read_text(encoding="utf-8")==contents,
                 "generated conflict evidence drift: "+str(path))
    else:
        for path,contents in expected.items():
            path.write_text(contents,encoding="utf-8")
    print(f"Batch82: {len(data['witnesses'])} conflicts, {data['finite_positive_cases']} exact valid, "
          f"{data['finite_negative_cases']} rejected, unresolved=10, check={args.check}")


if __name__=="__main__":
    main()
