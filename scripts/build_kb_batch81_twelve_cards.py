#!/usr/bin/env python3
"""12 original teacher-only P0 proof/method cards backed by exact finite guards."""
from __future__ import annotations
import argparse
from copy import deepcopy
from hashlib import sha256
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.kb_batch81_math import OPERATIONS,check
AUTHOR=ROOT/"knowledge/editorial_review/kb_batch81_authoring.json"
QUEUE=ROOT/"docs/evaluation/KB_BATCH80_PROOF_QUEUE.json"
OUT=ROOT/"knowledge/editorial_review/kb_batch81_twelve_math_cards.json"
MD=ROOT/"docs/evaluation/KB_BATCH81_TWELVE_MATH_GUARDS.md"

def reject(ok,why):
 if not ok:raise ValueError(why)

def dump(x):
 return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n"

def build(author=None,queue=None):
 author=json.loads(AUTHOR.read_text()) if author is None else author
 queue=json.loads(QUEUE.read_text()) if queue is None else queue
 reject(author["schema_version"]=="kb81-twelve-independent-p0-authoring-v1"
  and author["review_status"]=="REVIEW_PENDING"
  and author["copyright_origin"]=="ORIGINAL_PROJECT_AUTHORED","Unauthenticated authoring")
 base={r["id"]:r for r in queue["step_review_queue"]}
 cards=author["cards"]
 reject(len(cards)==12 and len({r["source_step"] for r in cards})==12,
        "12 distinct original proof obligations required")
 reject(set(r["finite_op"] for r in cards)==set(OPERATIONS),
        "Each mathematical guard must be used exactly once")
 result=[]
 for i,item in enumerate(cards):
  c=deepcopy(item)
  reject(c["id"]==f"KB81-P{i+1:02}","Card identity and ordering drift")
  sid=c["source_step"]
  reject(sid in base and base[sid]["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE",
         "Not an original P0 guard-class proof step")
  reject(base[sid]["review_card_id"] is None,"Existing draft collision")
  reject(c["kind"] in ("THEOREM","METHOD") and len(c["title"])>6
         and len(c["statement"])>=25,"Invalid mathematical statement")
  reject(len(c["assumptions"])>=2 and all(len(z)>=10 for z in c["assumptions"]),
         "Missing mathematical premises")
  reject(len(c["proof_steps"])==3 and all(len(z)>=16 for z in c["proof_steps"]),
         "Three explicit proof/reasoning steps required")
  reject(len(c["hints"])==3 and all(len(z)>=9 for z in c["hints"]),
         "Missing distinct tiered hints")
  reject(len(c["worked_examples"])==2 and all(len(z["teacher_solution"])>=25
         and len(z["question"])>=12 for z in c["worked_examples"]),
         "Two complete original examples required")
  for k in ("boundary","wrong_method","near","far"):
   reject(len(c[k])>=12,"Missing mathematical boundary or transfer: "+k)
  good,good_ev=check(c["finite_op"],c["valid"])
  bad,bad_ev=check(c["finite_op"],c["invalid"])
  reject(good=="FINITE_EXACT_WITNESS_ONLY" and bad=="CONDITIONS_NOT_ESTABLISHED",
         "Independent finite exact evidence check failed")
  c.update(
    original_step_sha256=base[sid]["source_sha256"],
    linked_historical_step_id=sid,
    source_kind="PROJECT_HISTORICAL_PROOF_DRAFT",
    curriculum_standard_version=author["curriculum_standard_version"],
    copyright_origin="ORIGINAL_PROJECT_AUTHORED",
    review_status="REVIEW_PENDING",teacher_solution_visibility="TEACHER_ONLY",
    student_publishable=False,student_free_text_verified=False,
    formal_math_certification="NOT_FORMALLY_VERIFIED",
    finite_instance_check="EXACT_WITNESS_NOT_GENERAL_THEOREM_PROOF",
    finite_positive_evidence=good_ev,finite_invalid_rejection=bad_ev,
    reviewer_id=None,official_curriculum_atom_id=None,
  )
  for ex in c["worked_examples"]:
   ex["visibility"]="TEACHER_ONLY"
  result.append(c)
 return {
  "schema_version":"kb81-twelve-p0-proof-conditions-v1",
  "standard_version":author["curriculum_standard_version"],
  "original_author_sha256":sha256(AUTHOR.read_bytes()).hexdigest(),
  "proof_source_sha256":sha256(QUEUE.read_bytes()).hexdigest(),
  "original_teacher_cards":12,"review_cards":result,
  "formal_certifications":0,"teacher_approvals":0,"student_releases":0,
  "official_atom_denominator":None
 }

def markdown(data):
 rows=["# Batch81 | 12原创数学高风险论证教师草案","",
  "对应历史P0未审查步骤，各篇包含完整前提、三步论证、两道原创例题、失效反例、三级提示及近远变式。",
  "**有限有理数见证不构成一般定理形式证明。全部保持 REVIEW_PENDING、TEACHER_ONLY。**","",
  "| 历史步骤 | 主题 | 关键非法前提/退化 |",
  "|---|---|---|"]
 for c in data["review_cards"]:
  rows.append(f"| {c['linked_historical_step_id']} | {c['title']} | {c['finite_invalid_rejection']['reason']} |")
 rows.extend(["","不得将这些卡的 teacher_solution 进入学生自主挑战检索上下文。",
  "原始历史证明来源SHA和每卡条件验证证据见同目录版本化JSON。"])
 return "\n".join(rows)+"\n"

def main():
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");args=p.parse_args()
 r=build()
 for dest,s in ((OUT,dump(r)),(MD,markdown(r))):
  if args.check:reject(dest.exists() and dest.read_text()==s,"Artifact drift "+str(dest))
  else:dest.write_text(s)
 print("Batch81 12 cards: 24 original solved examples, 36 review-only proof steps; 12 finite passes and 12 invalid rejections")
if __name__=="__main__":main()
