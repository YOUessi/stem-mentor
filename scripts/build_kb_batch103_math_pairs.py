#!/usr/bin/env python3
"""Batch103: twenty source-anchored core/selective/elective math comparisons.

Editorial REVIEW_PENDING only. Exact bounded witnesses are not formal proofs,
syllabus atom counts, teacher sign-offs, or student knowledge approvals.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

from sympy import Matrix, Rational as R, Symbol, binomial, cos, diff, expand, ln, pi, simplify, sin, sqrt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "backend")]
import build_kb_batch102_math_pairs as PREV

AUTHOR = ROOT / "scripts/kb_batch103_pair_authoring.json"
OUT = ROOT / "docs/evaluation/KB_BATCH103_20_MATH_COMPARISONS.json"
MD = ROOT / "docs/evaluation/KB_BATCH103_20_MATH_COMPARISONS.md"
COVERAGE = ROOT / "docs/evaluation/KB_BATCH103_COVERAGE.json"
SOURCE = PREV.Q.SOURCE
FIELDS = PREV.FIELDS
TRACKS = PREV.TRACKS
ALLOWED = PREV.ALLOWED

def need(condition, reason):
    if not condition:
        raise ValueError(reason)

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def canonical(data):
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"

def finite_witness(i):
    """Independent *finite* examples, not a certificate of universal validity."""
    from sympy import limit, oo
    x=Symbol("x",real=True)
    n=Symbol("n",integer=True,positive=True)
    if i==0:
        # epsilon-N tail behavior, bounded oscillation is not convergence
        good=limit(1/n,n,oo)==0 and R(1,101)<R(1,100)
        bad=(-1)**4==1 and (-1)**5==-1
    elif i==1:
        # finite prefix plus small tail, converse refuted by oscillation
        good=limit(1/n,n,oo)==0 and all(abs(R(1,k))<=1 for k in range(1,21))
        bad=abs((-1)**20)==abs((-1)**21)==1 and (-1)**20!=(-1)**21
    elif i==2:
        good=[2,6,18,54]==[2*3**k for k in range(4)]
        bad=R(19,6)!=R(6,2)
    elif i==3:
        good=limit(1/n,n,oo)==0 and R(1,101)<R(1,100)
        bad=limit(n,n,oo)==oo
    elif i==4:
        f=(x*x-1)/(x-1)
        good=limit(f,x,1)==2 and simplify(f-(x+1))==0
        bad=(x*x-1).subs(x,1)==0 and (x-1).subs(x,1)==0
    elif i==5:
        good=diff(x**3,x)==3*x*x and diff(x**3,x,2)==6*x
        bad=diff(x**3,x).subs(x,0)==0 and (-1)**3<0<1**3
    elif i==6:
        good=Matrix([2,3,4]).dot(Matrix([2,3,4]))==29
        bad=Matrix([2,1]).dot(Matrix([2,1]))!=2
    elif i==7:
        u=Matrix([2,-1,3]);z=Matrix.zeros(3,1)
        good=z+u==u and z.dot(u)==0
        bad=z.norm()==0
    elif i==8:
        u,v=Matrix([1,2,-1]),Matrix([2,-1,3])
        good=u+v==Matrix([3,1,2]) and 2*u-v==Matrix([0,5,-5])
        bad=2*u-v!=u+v
    elif i==9:
        u,v=Matrix([1,2,3]),Matrix([2,1,0])
        good=u.dot(v)==4 and u+v==Matrix([3,3,3])
        bad=Matrix.zeros(3,1).norm()==0
    elif i==10:
        u,v=Matrix([1,0,0]),Matrix([0,1,0])
        good=u.dot(v)==0 and u.cross(v)==Matrix([0,0,1])
        bad=Matrix.zeros(3,1).norm()==0
    elif i==11:
        n=Matrix([0,0,1])
        good=n.dot(Matrix([1,0,0]))==0 and n.cross(Matrix([0,0,1]))==Matrix.zeros(3,1)
        bad=n.dot(Matrix([1,0,1]))!=0
    elif i==12:
        n,p=Matrix([2,0,0]),Matrix([3,4,5])
        good=abs(n.dot(p))/n.norm()==3
        bad=abs(n.dot(p))==6 and abs(n.dot(p))!=3
    elif i==13:
        a,b=Matrix([0,0]),Matrix([0,1])
        good=b-a!=Matrix.zeros(2,1)
        bad=a-a==Matrix.zeros(2,1)
    elif i==14:
        good=R(1)*R(-1)==-1 and Matrix([0,1]).dot(Matrix([1,0]))==0
        bad=Matrix([0,1])[0]==0 # slope undefined for vertical direction
    elif i==15:
        u,v=Matrix([1,0,0]),Matrix([0,1,0])
        w=Matrix([0,0,1])
        good=abs(u.cross(v).dot(w))/u.cross(v).norm()==1
        bad=u.cross(u)==Matrix.zeros(3,1)
    elif i==16:
        e=R(0)*R(1,2)+R(1)*R(1,2)
        e2=R(0)**2*R(1,2)+R(1)**2*R(1,2)
        good=e==R(1,2) and e2-e**2==R(1,4)
        bad=R(-1,2)+R(3,2)==1 and R(-1,2)<0
    elif i==17:
        sample=[1,2,3,4]
        good=sample[2]==3 and R(1)+(len(sample)-1)*R(3,4)==R(13,4)
        bad=R(13,4)!=sample[2]
    elif i==18:
        good=binomial(4,2)==6 and expand((x+1)**4).coeff(x,2)==6
        bad=4*3!=binomial(4,2)
    elif i==19:
        table=[[10,10],[10,10]]
        good=sum(map(sum,table))==40 and R(table[0][0],sum(table[0]))==R(1,2)
        bad=sum([0,0])==0 # cannot condition on empty row
    else:
        raise ValueError("unsupported finite oracle index")
    need(bool(good), f"positive exact witness fails at {i}")
    need(bool(bad), f"boundary exact witness fails at {i}")
    return {"exact_positive":True,"exact_invalid_boundary":True,
            "formal_universal_proof":False,"teacher_approved":False,
            "student_publishable":False,"semantic_equivalence_certified":False}

def build(authored=None):
    rows=json.loads(AUTHOR.read_text(encoding="utf-8")) if authored is None else authored
    need(isinstance(rows,list) and len(rows)==20,"must author exactly 20 comparisons")
    previous=PREV.build()
    PREV.validate(previous)
    source=PREV.Q.source_read(SOURCE)["provisional_candidate_backlog"]
    need(len(source)==300,"source census changed")
    source_by_title={item["provisional_topic"]:item for item in source}
    need(len(source_by_title)==300,"source titles are not unique")
    prior_unpaired=set(PREV.Q.source_read(PREV.Q.PREV)["remaining_unpaired_candidate_ids"])
    batch101=json.loads(PREV.PREVIOUS_PAIRS.read_text(encoding="utf-8"))
    earlier_new={x["left_source_candidate_id"] for x in batch101["editorial_pairs"]}
    previous_new={x["left_source_candidate_id"] for x in previous["editorial_pairs"]}
    outstanding=prior_unpaired-earlier_new-previous_new
    need(len(outstanding)==94 and len(previous_new)==len(earlier_new)==20
         and not (earlier_new & previous_new),"Batch101/102 frozen parent changed")
    prior_compared={x["candidate_id"] for x in source}-outstanding
    need(len(prior_compared)==206,"prior compared count incorrect")
    result=[]
    visited=set()
    for index,row in enumerate(rows):
        need(isinstance(row,dict) and set(row)==FIELDS,"authored row schema")
        need(row["relation"] in ALLOWED,"unauthorized relationship certification")
        need(all(isinstance(row[k],str) and len(row[k].strip())>=30
                 for k in ("conditions","distinction","positive","invalid")),
             "short/missing mathematical explanation")
        a=source_by_title.get(row["left"])
        b=source_by_title.get(row["right"])
        need(a is not None and b is not None and a!=b,"source topic unknown")
        need(a["candidate_id"] in outstanding and a["candidate_id"] not in visited,
             "duplicate/previously compared left source")
        need(b["candidate_id"] in prior_compared,"right source not earlier compared")
        for item in (a,b):
            need(item["review_status"]=="REVIEW_PENDING" and item["teacher_approval"] is None
                 and item["official_math_atom_id"] is None
                 and item["student_authoritative_index_eligible"] is False,
                 "source authority promotion detected")
            need(len(item["source_line_sha256"])==64 and len(item["candidate_id"])>0,
                 "source identity invalid")
        visited.add(a["candidate_id"])
        result.append({
            "id":f"KB103-PAIR-{index+1:02d}",
            "left_source_candidate_id":a["candidate_id"],"left_topic":row["left"],
            "left_track":a["track"],"left_page":a["source_page"],
            "left_line_sha256":a["source_line_sha256"],
            "right_source_candidate_id":b["candidate_id"],"right_topic":row["right"],
            "right_track":b["track"],"right_page":b["source_page"],
            "right_line_sha256":b["source_line_sha256"],
            "cross_engineering_track":a["track"]!=b["track"],
            "proposed_relation":row["relation"],
            "necessary_conditions":row["conditions"],
            "mathematical_distinction":row["distinction"],
            "worked_positive_example":row["positive"],
            "invalid_boundary_or_counterexample":row["invalid"],
            "finite_exact_witness":finite_witness(index),
            "semantic_relation_certified":False,"official_atom_id":None,
            "teacher_review_status":"REVIEW_PENDING",
            "teacher_approved":False,"student_publishable":False,
        })
    need(len(visited)==20,"authored distinct left source count")
    totals=Counter(r["track"] for r in source)
    prior=Counter(r["track"] for r in source if r["candidate_id"] in prior_compared)
    newly=Counter(r["left_track"] for r in result)
    remaining=Counter(r["track"] for r in source
                      if r["candidate_id"] in outstanding-visited)
    track_matrix={track:{"provisional_labels":totals[track],
                         "previously_compared":prior[track],
                         "new_comparisons":newly[track],
                         "still_unpaired":remaining[track],
                         "official_atom_denominator":None}
                  for track in TRACKS}
    return {
        "schema_version":"kb103-core-source-pairs-v1",
        "source_sha256":PREV.Q.digest(SOURCE),
        "batch102_report_sha256":digest(PREV.OUT),
        "author_sha256":digest(AUTHOR),
        "provisional_labels":300,
        "previously_compared":206,"new_editorial_comparisons":20,
        "still_unpaired":74,
        "official_atom_denominators_by_track":{track:None for track in TRACKS},
        "teacher_semantic_adjudications":0,
        "fully_human_atomized_source_pages":0,"teacher_approved":0,
        "student_authoritative_release":0,"formal_universal_proofs":0,
        "track_matrix":track_matrix,"editorial_pairs":result
    }

def validate(data):
    need(isinstance(data,dict) and data==build(),
         "report differs from complete source-locked draft with frozen unknown/approval guards")
    return True

def markdown(data):
    lines=[
        "# Batch103｜20项跨领域数学成对审查（候审）","",
        "> 只针对项目300个临时工程标签：绝非官方知识原子分母、一般定理形式证明或教师批准。所有内容 REVIEW_PENDING。","",
        f"已完成项目标签编辑比较：{data['previously_compared']} + {data['new_editorial_comparisons']} = 226/300；未比较：{data['still_unpaired']}。","",
        "正式七轨课标知识原子总数：UNKNOWN；正式教师审核：0；学生权威发布：0。","",
        "|内部轨道|临时标签|之前成对|新增成对|剩余未成对|官方原子分母|",
        "|---|---:|---:|---:|---:|---|",
    ]
    for track,c in data["track_matrix"].items():
        lines.append(f"|{track}|{c['provisional_labels']}|{c['previously_compared']}|{c['new_comparisons']}|{c['still_unpaired']}|UNKNOWN|")
    lines.append("")
    for row in data["editorial_pairs"]:
        lines += [
            f"## {row['id']}｜{row['left_topic']} ↔ {row['right_topic']}","",
            f"- 来源：{row['left_source_candidate_id']}（{row['left_track']}，第{row['left_page']}页，sha256={row['left_line_sha256']}）",
            f"- 参照：{row['right_source_candidate_id']}（{row['right_track']}，第{row['right_page']}页，sha256={row['right_line_sha256']}）",
            f"- 关系候选：{row['proposed_relation']}；跨项目轨道：{row['cross_engineering_track']}",
            f"- 适用前提：{row['necessary_conditions']}",
            f"- 两知识边界：{row['mathematical_distinction']}",
            f"- 独立原创正例：{row['worked_positive_example']}",
            f"- 反例与不适用：{row['invalid_boundary_or_counterexample']}",
            "- 检查范围：仅具体数值/符号正反例通过，**不证明普适命题、不通过教师审核、不进入学生权威检索**。",""
        ]
    return "\n".join(lines)+"\n"

def coverage(data):
    return {
        "schema_version":data["schema_version"],
        "source_sha256":data["source_sha256"],
        "provisional_project_label_count":300,
        "previous_editorially_paired":206,
        "newly_editorially_paired":20,
        "total_editorially_paired":226,
        "remaining_unpaired":74,
        "track_matrix":data["track_matrix"],
        "official_atom_denominators_by_track":data["official_atom_denominators_by_track"],
        "teacher_atomized_pages":0,
        "teacher_approved":0,
        "student_authoritative_release":0,
        "proven_universal_theorems":0,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    data=build()
    content={OUT:canonical(data), MD:markdown(data), COVERAGE:canonical(coverage(data))}
    if args.check:
        for path,expected in content.items():
            need(path.exists() and path.read_text(encoding="utf-8")==expected,
                 f"missing/stale/unauthorized generated report: {path}")
        print("BATCH103 CHECK PASS: 20 mathematical source pairs; 226/300 provisional; 74 pending; no approvals")
    else:
        for path,txt in content.items():
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(txt,encoding="utf-8")
        print("BATCH103 WRITE PASS:",*(str(p.relative_to(ROOT)) for p in content))

if __name__=="__main__":
    main()
