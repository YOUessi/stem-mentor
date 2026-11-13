#!/usr/bin/env python3
"""Batch70: original mathematical reasoning obligations for ten legacy conflicts.

Not a formal proof verifier. Does not promote a conflicting source version.
"""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from math import comb
from pathlib import Path
import argparse
import json

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"docs/evaluation/KB_CONFLICT_RISK_BATCH07.json"
AUTHORING=ROOT/"knowledge/editorial_review/kb_batch70_conflict_math_authoring.json"
OUT=ROOT/"docs/evaluation/KB_BATCH70_TEN_CONFLICT_PROOF_REVIEW.json"
MD=ROOT/"docs/evaluation/KB_BATCH70_TEN_CONFLICT_TEACHER_REVIEW.md"
PIN_SHA="796f13f5a8be2d3874971f960a5a2d34135b07fefa49d90ba6dc525a2f8508f2"
IDS=("math.hs.function.composition-domain","math.hs.function.parity",
"math.hs.function.piecewise","math.hs.function.zero-ivt","math.hs.geometry.point-line-distance",
"math.hs.probability.binomial-distribution","math.hs.probability.hypergeometric",
"math.hs.statistics.correlation-regression","math.hs.triangle.area-sine","math.hs.vector.linear-operations")
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")

def require(flag,msg):
    if not flag: raise ValueError(msg)
def load(path): return json.loads(path.read_text(encoding="utf-8"))
def canonical(obj): return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n"

def validate_authoring(data):
    items=data.get("items",[])
    require(len(items)==10 and tuple(v.get("conflict_id") for v in items)==IDS,
            "Missing/duplicate/reordered conflict IDs")
    for v in items:
        require(v["knowledge_kind"] in ("THEOREM","CONCEPT","METHOD"),"Unsupported knowledge kind")
        for field in ("title","precise_statement","boundary","near_transfer","far_transfer"):
            require(isinstance(v.get(field),str) and len(v[field])>=(8 if field=="title" else 20),
                    "Missing precise mathematical content: "+field)
        require(len(v.get("assumptions",[]))>=2,"Incomplete assumptions")
        ss=v.get("proof_steps",[])
        require(len(ss)>=4 and [s["step"] for s in ss]==list(range(1,len(ss)+1)),
                "Missing/incorrectly ordered proof obligations")
        for s in ss:
            require(len(s.get("claim",""))>=10 and len(s.get("justification",""))>=8,
                    "Unsupported claim-reason depth")
        require(len(v.get("hints",[]))==3 and len(set(v["hints"]))==3,
                "Missing distinct progressive hints")
        require(v["near_transfer"]!=v["far_transfer"],"Non-distinct transfers")
        for field,keys in (("worked_example",("question","teacher_solution")),
                           ("invalid_case",("false_claim","counterexample_explanation"))):
            require(all(len(v.get(field,{}).get(key,""))>=18 for key in keys),
                    "Incomplete example or counterexample: "+field)
        require(v["source_license"]=="ORIGINAL_PROJECT_AUTHORED","Source license violation")
        require(v["teacher_review"]=="REVIEW_PENDING" and v["teacher_signature"] is None,
                "Forged teacher certification")
        require(v["proof_certification"]=="NOT_FORMALLY_CERTIFIED","Forged proof certification")
        require(v["teacher_solution_visibility"]=="TEACHER_ONLY" and v["student_publishable"] is False,
                "Teacher answer exposure")
    return items

def exact_case(i):
    """Independent bounded exact witnesses: never universally certify a theorem."""
    if i==0:
        g=lambda x:x-2
        return g(F(3))==1 and g(F(2))==0 and F(1,g(F(3)))==1
    if i==1:
        even=lambda x:x*x; odd=lambda x:x*x*x
        return all(even(-j)==even(j) and odd(-j)==-odd(j) for j in range(-6,7))
    if i==2:
        f=lambda x:x*x if x<0 else x+1
        return f(F(0))==1 and f(F(-2))==4 and f(F(2))==3 and F(0)**2!=F(0)+1
    if i==3:
        f=lambda x:x**3-x
        return f(F(-2))==-6 and f(F(2))==6 and all(f(F(j))==0 for j in (-1,0,1))
    if i==4:
        return F(3)**2+F(4)**2==25 and abs(3*0+4*0-10)==10 and F(10,5)==2
    if i==5:
        a=[F(comb(3,k),8) for k in range(4)]
        return a==[F(1,8),F(3,8),F(3,8),F(1,8)] and sum(a)==1
    if i==6:
        a=[F(comb(2,k)*comb(2,2-k),comb(4,2)) for k in range(3)]
        return a==[F(1,6),F(4,6),F(1,6)] and sum(a)==1 and F(1,6)!=F(1,4)
    if i==7:
        x=[F(0),F(1),F(2)]; y=[F(1),F(3),F(5)]
        xm=sum(x)/3; ym=sum(y)/3
        xx=sum((t-xm)**2 for t in x)
        xy=sum((t-xm)*(s-ym) for t,s in zip(x,y))
        return xx==2 and xy==4 and xy/xx==2 and ym-xy/xx*xm==1
    if i==8:
        return F(3*4,2)==6 and F(3*4,2)*F(3,5)==F(18,5) and F(18,5)!=6
    if i==9:
        u=(F(1),F(2));v=(F(-3),F(4));a=F(2)
        add=lambda x,y:tuple(p+q for p,q in zip(x,y))
        scale=lambda s,x:tuple(s*q for q in x)
        return len(u)==len(v) and scale(a,add(u,v))==add(scale(a,u),scale(a,v))==(-4,12) and len(u)!=len((3,4,5))
    raise ValueError("Unknown finite check index")

def build(custom_authoring=None,custom_source=None):
    require(sha256(SOURCE.read_bytes()).hexdigest()==PIN_SHA,"Frozen source SHA mismatch")
    risk=load(SOURCE) if custom_source is None else custom_source
    require(canonical(risk)==canonical(load(SOURCE)),"Forged frozen source comparison")
    orig=risk.get("conflicts",[])
    require(len(orig)==10 and tuple(r["id"] for r in orig)==IDS,"Source conflict identity/order drift")
    require(risk["summary"]["unresolved_conflicts"]==10,"Unexpected baseline resolution")
    data=load(AUTHORING) if custom_authoring is None else custom_authoring
    records=[]
    for i,(item,old) in enumerate(zip(validate_authoring(data),orig)):
        require(old["candidate_sha256"]!=old["active_sha256"],
                "Unexpected equal competing versions")
        require(exact_case(i),"Independent finite check failed")
        new=deepcopy(item)
        new.update(conflict_index=i,packet_id=f"KB70-CONFLICT-{i+1:02d}",active_sha256=old["active_sha256"],
                   candidate_sha256=old["candidate_sha256"],
                   changed_risk_fields=old["mathematical_risk_fields"],
                   historical_kinds=[old["active_kind"],old["candidate_kind"]],
                   version_winner=None,
                   dispute_resolution="UNRESOLVED_PENDING_INDEPENDENT_MATH_AND_TEACHER_REVIEW",
                   bounded_math_check="FINITE_EXACT_INSTANCE_ONLY",
                   general_proof_certified=False,student_freeform_steps_verified=False,
                   official_atomic_membership="UNDETERMINED")
        records.append(new)
    return dict(schema_version="kb70-conflict-reasoning-v1",source_sha256=PIN_SHA,
                new_packets=len(records),new_draft_claim_reason_steps=sum(len(r["proof_steps"]) for r in records),
                bounded_checks=10,conflicts_resolved=0,
                historical_unverified_proof_steps_remaining=538,
                general_proofs_certified=0,teacher_approved=0,student_published=0,
                official_atomic_denominator={track:None for track in TRACKS},
                scope="ORIGINAL_MATH_REVIEW_NOT_VERSION_ADJUDICATION",
                warning="Limited exact cases and human-readable draft arguments DO NOT certify universal proofs.",
                records=records)

def render_markdown(data):
    parts=["# Batch70｜十组数学冲突：原创独立论证义务与反例（教师侧）","",
           "> 所有材料仍为 REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED。",
           "> 有界精确示例不是形式证明；本批未选出任何历史冲突的胜出版本。","",
           "冻结风险来源 SHA256: "+data["source_sha256"],""]
    for r in data["records"]:
        parts+=["## "+str(r["conflict_index"]+1)+". "+r["title"],"",
                "对应冲突ID: "+r["conflict_id"],
                "候选/现行来源SHA: "+r["candidate_sha256"]+" / "+r["active_sha256"],
                "知识类型: "+r["knowledge_kind"],"","### 数学前提"]
        parts+=["- "+v for v in r["assumptions"]]
        parts+=["","### 精确陈述",r["precise_statement"],"","### 逐步论证（待教师及独立数学审核）"]
        parts+=[str(s["step"])+". 论断："+s["claim"]+"；依据："+s["justification"]
                for s in r["proof_steps"]]
        parts+=["","### 适用边界",r["boundary"],"","### 原创例题（教师侧解答）",
                r["worked_example"]["question"],
                "教师解答："+r["worked_example"]["teacher_solution"],
                "","### 错法与反例",r["invalid_case"]["false_claim"],
                "原因："+r["invalid_case"]["counterexample_explanation"],
                "","### 分层提示"]
        parts+=["- H"+str(i+1)+"："+v for i,v in enumerate(r["hints"])]
        parts+=["","近迁移："+r["near_transfer"],"远迁移："+r["far_transfer"],
                "","审核阻断：10组历史冲突仍未裁决，本条不可自动批准或发布学生端。",""]
    return "\n".join(parts).rstrip()+"\n"

def write(check=False):
    report=build()
    for path,text in ((OUT,canonical(report)),(MD,render_markdown(report))):
        if check:
            require(path.is_file() and path.read_text(encoding="utf-8")==text,
                    "Snapshot mismatch: "+str(path))
        else:
            path.write_text(text,encoding="utf-8")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    args=p.parse_args()
    data=write(check=args.check)
    print("Batch70",data["new_packets"],"packets,",data["new_draft_claim_reason_steps"],
          "draft mathematical steps; resolved",data["conflicts_resolved"])
