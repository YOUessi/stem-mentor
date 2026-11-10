#!/usr/bin/env python3
"""Write teacher-only guarded transformations with computed exact counterexamples."""
from __future__ import annotations
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"backend"))
import argparse
import json
from hashlib import sha256
from app.kb_batch84_guarded_transformations import verified_cards,check_case
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"knowledge/editorial_review/kb_batch84_guarded_transformation_cards.json"
MD=ROOT/"docs/evaluation/KB_BATCH84_MATH_GUARDS.md"

def dump(o):
    return json.dumps(o,ensure_ascii=False,sort_keys=True,indent=2)+"\n"

def build():
    data=list(verified_cards())
    if len(data)!=10 or len({d["op"] for d in data})!=10:
        raise ValueError("incomplete exact transformation audit")
    if any(not isinstance(d.get("valid_guarded_example"),str)
           or len(d["valid_guarded_example"])<25
           or d["review_state"]!="REVIEW_PENDING" or not d["teacher_only"]
           or d["student_authoritative_index_eligible"]
           or d["general_theorem_certified"]
           or d["teacher_approved"]
           or d["student_answer_verified"] for d in data):
        raise ValueError("false proof, student verification or teacher approval")
    if any(check_case(d["op"],d["payload"])["status"]!="FINITE_EXACT_COUNTEREXAMPLE_ONLY"
           for d in data):
        raise ValueError("invalid exact witness")
    return {
        "schema_version":"kb84-guarded-transformations-exact-counterexample-v1",
        "source":"ORIGINAL_MATH_WORK_NOT_COPYRIGHT_TEXTBOOK",
        "teacher_review":"REVIEW_PENDING",
        "visibility":"TEACHER_ONLY",
        "general_math_proof_certified":False,
        "independent_student_step_verification":False,
        "student_index_eligible":False,
        "card_count":len(data),
        "cards":data,
    }

def markdown(d):
    lines=["# Batch84｜10项数学推导失效前提审查卡","",
           "**待教师审核，仅对所列整数输入给出精确反例；不能认证一般定理。**",
           "教师完整论证不得在学生自主挑战时作为检索证据，独立学生解答状态不变。","",
           "| ID | 错误命题 | 失效反例 | 合法适用例 | 修复前提 |","|---|---|---|---|---|"]
    for c in d["cards"]:
        lines.append(f'| {c["id"]} | {c["claim"]} | {c["worked_example"]} | {c["valid_guarded_example"]} | {c["assumptions"]} |')
    lines+=["","每项有前提、三步论证、失效反例与合法适用例各一、错误原因、三级提示、近远迁移；完整原稿仅存放在 knowledge/editorial_review，未进入已批准学生索引。",""]
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");args=p.parse_args()
    d=build()
    for path,text in ((OUT,dump(d)),(MD,markdown(d))):
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf8")!=text:
                raise ValueError("math guard generated artifact drift: "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(text,encoding="utf8")
    print("Batch84: 10 teacher-only transformations; exact finite counterexamples; 0 teacher approvals")

if __name__=="__main__":
    main()
