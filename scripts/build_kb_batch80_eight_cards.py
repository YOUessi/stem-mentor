#!/usr/bin/env python3
"""Batch80 eight original, teacher-only assumption-sensitive proof review cards."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.kb_batch80_math import OPS, check as math_check
AUTHOR=ROOT/"knowledge/editorial_review/kb_batch80_proof_guard_authoring.json"
PARENT=ROOT/"docs/evaluation/KB_BATCH78_PROOF_DEBT_MATRIX.json"
PREV79=ROOT/"knowledge/editorial_review/kb_batch79_condition_proof_cards.json"
OUTPUT=ROOT/"knowledge/editorial_review/kb_batch80_eight_proof_guard_cards.json"
SUMMARY=ROOT/"docs/evaluation/KB_BATCH80_EIGHT_PROOF_GUARDS.md"

def read(path):
    return json.loads(path.read_text(encoding="utf8"))

def dump(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+"\n"

def build(author=None,ledger=None,previous=None):
    author=read(AUTHOR) if author is None else author
    ledger=read(PARENT) if ledger is None else ledger
    previous=read(PREV79) if previous is None else previous
    if author["schema_version"]!="kb80-eight-original-math-proof-guard-authoring-v1":
        raise ValueError("Authoring schema mutated")
    if author["review_status"]!="REVIEW_PENDING" or author["copyright_origin"]!="ORIGINAL_PROJECT_AUTHORED":
        raise ValueError("Authorship/review metadata missing")
    cards=author["cards"]
    if len(cards)!=8 or len({x["source_step"] for x in cards})!=8:
        raise ValueError("Expected eight distinct new proof review obligations")
    history={x["id"]:x for x in ledger["proof_obligations"]}
    older={x["linked_historical_step_id"] for x in ledger["review_cards"]+previous["review_cards"]}
    if len(history)!=538 or len(older)!=28:
        raise ValueError("Previous review lineage has drifted")
    output=[]
    for k,original in enumerate(cards):
        c=deepcopy(original)
        if c["id"]!=f"KB80-P{k+1:02}" or c["finite_op"]!=OPS[k]:
            raise ValueError("Stable authored card identity/operation misordered")
        sid=c["source_step"]
        if sid not in history or sid in older:
            raise ValueError("Orphan or duplicate historical step")
        hist=history[sid]
        if hist["risk_priority"]!="P0_GUARD_AND_COUNTEREXAMPLE":
            raise ValueError("New review card must link to unreviewed P0")
        if c["kind"] not in ("THEOREM","METHOD") or not c["title"] or not c["statement"]:
            raise ValueError("Required mathematical type/statement missing")
        for field in ("boundary","wrong_method","near","far"):
            if not isinstance(c[field],str) or len(c[field].strip())<16:
                raise ValueError("Missing independently authored mathematical boundary")
        if len(c["assumptions"])<2 or any(len(s.strip())<10 for s in c["assumptions"]):
            raise ValueError("Missing mathematical assumptions")
        if len(c["proof_steps"])!=3 or any(len(s.strip())<16 for s in c["proof_steps"]):
            raise ValueError("Incomplete three-stage reasoning")
        if len(c["hints"])!=3 or any(len(s.strip())<12 for s in c["hints"]):
            raise ValueError("Incomplete tiered non-solution hints")
        if len(c["worked_examples"])!=2 or any(
                not z.get("question") or len(z.get("teacher_solution",""))<15
                for z in c["worked_examples"]):
            raise ValueError("Teacher examples must have two complete teacher solutions")
        st,ev=math_check(c["finite_op"],c["valid"])
        rejected,reason=math_check(c["finite_op"],c["invalid"])
        if st!="GUARD_PASSED_FINITE_CASE_ONLY" or rejected!="CONDITIONS_NOT_ESTABLISHED":
            raise ValueError("Exact finite positive/negative evidence does not match")
        c["original_step_sha256"]=hist["original_step_sha256"]
        c["linked_historical_step_id"]=sid
        c["source_kind"]="PROJECT_HISTORICAL_PROOF_DRAFT"
        c["curriculum_standard_version"]=author["curriculum_standard_version"]
        c["copyright_origin"]="ORIGINAL_PROJECT_AUTHORED"
        c["review_status"]="REVIEW_PENDING"
        c["teacher_solution_visibility"]="TEACHER_ONLY"
        c["student_publishable"]=False
        c["student_free_text_verified"]=False
        c["formal_math_certification"]="NOT_FORMALLY_VERIFIED"
        c["finite_instance_check"]="CONDITIONS_ONLY_NOT_GENERAL_PROOF"
        c["finite_positive_evidence"]=ev
        c["finite_invalid_rejection"]=reason
        c["reviewer_id"]=None
        c["official_curriculum_atom_id"]=None
        for example in c["worked_examples"]:
            example["visibility"]="TEACHER_ONLY"
        output.append(c)
    result=dict(schema_version="kb80-eight-p0-proof-guard-cards-v1",
       standard_version=author["curriculum_standard_version"],
       original_author_sha256=hashlib.sha256(AUTHOR.read_bytes()).hexdigest(),
       proof_ledger_sha256=hashlib.sha256(PARENT.read_bytes()).hexdigest(),
       original_teacher_cards=8,distinct_prior_review_links=28,
       all_review_links_after_batch=36,
       formal_certifications=0,teacher_approvals=0,student_releases=0,
       official_atom_denominator=None,review_cards=output)
    return result

def markdown(d):
    rows=["# Batch80｜8项高风险历史证明前提复核（教师侧草案）","",
      "本批8条对应先前99条未有审查卡的历史P0，全部有两例、三段推理、前提失效见证与三级启发提示。",
      "**仅证明受限数值实例与不适用条件被机器检查；未做一般定理形式化认证。**",
      "","| 历史证明步骤 | 数学主题 | 正例 | 拒绝例 |","|---|---|---|---|"]
    for c in d["review_cards"]:
        rows.append(f"| {c['linked_historical_step_id']} | {c['title']} | "
           f"{c['valid']} | {c['invalid']} |")
    rows += ["","所有内容来源为原创编辑草案，保持REVIEW_PENDING/TEACHER_ONLY。",
             "教师正式签核前，不能进入学生权威检索或完整答案索引。"]
    return "\n".join(rows)+"\n"

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    arg=p.parse_args()
    data=build()
    for f,content in [(OUTPUT,dump(data)),(SUMMARY,markdown(data))]:
        if arg.check:
            if not f.exists() or f.read_text(encoding="utf8")!=content:
                raise SystemExit("Batch80 math card artifact drift "+str(f))
        else:
            f.write_text(content,encoding="utf8")
    print("B80 8 original teacher cards; 8 guarded finite positive and 8 invalid instances; 0 certified")
if __name__=="__main__":
    main()
