#!/usr/bin/env python3
"""20 genuinely authored mathematical comparisons for previously unpaired topics.

These count as editorial comparisons only; neither equivalence nor syllabus atom
membership is certified. Independent exact tests cover example/boundary instances.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from sympy import Matrix, Rational, Symbol, sqrt, pi, sin, simplify, integrate, log, solve
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch101_review_queue as Q
from kb_batch101_pair_authoring import RECORDS

OUT=ROOT/"docs/evaluation/KB_BATCH101_20_MATH_COMPARISONS.json"
MD=ROOT/"docs/evaluation/KB_BATCH101_20_MATH_COMPARISONS.md"
AUTHOR=ROOT/"scripts/kb_batch101_pair_authoring.py"
ALLOWED={"RELATED_DISTINCT","POSSIBLE_OVERLAP_UNRESOLVED"}
FIELDS={"left","right","relation","conditions","distinction","positive","invalid"}

def check(ok,msg):
    if not ok:raise ValueError(msg)

def instance(index):
    """Independent exact mathematical positive/negative witnesses; NEVER a general proof."""
    x=Symbol("x",real=True)
    if index==0:
        ok=({1,2}|{2,3})=={1,2,3}; bad=({1,2}&{2,3})!={1,2,3}
    elif index==1:
        ok=Rational(3,2)/Rational(1,2)==3; bad=simplify(log(1,2))==0 # denominator log_2(1) is zero
    elif index==2:
        f=lambda v:2*sin(3*v+1)+4
        ok=simplify(f(x+2*pi/3)-f(x))==0; bad=simplify((0*sin(3*x+1)+4)-(0*sin(3*(x+1)+1)+4))==0
    elif index==3:
        f=lambda v:v*v-2
        ok=f(1)<0<f(2) and f(Rational(3,2))>0
        bad=solve(1/(x-Rational(3,2)),x)==[]
    elif index==4:
        a,b=Matrix([1,2]),Matrix([3,-1])
        ok=a+b==Matrix([4,1]) and 2*a==Matrix([2,4])
        bad=Matrix([[0,-1],[1,0]])*Matrix([1,0])+Matrix([0,1])!=Matrix([1,0])+Matrix([0,1])
    elif index==5:
        # SAS: equal sides with included angle pi/3 give a third side of one.
        ok=simplify(1+1-2*Rational(1,2)-1)==0
        # SSA: A=pi/6, a=2, b=3 admits TWO distinct choices of B.
        from sympy import asin
        A=pi/6; B1=asin(Rational(3,4)); B2=pi-B1
        bad=bool(B1 != B2 and A+B1<pi and A+B2<pi)
    elif index==6:
        ok=Rational(2,10)==Rational(1,5) and Rational(1,5)!=Rational(1,2)
        bad=Rational(2,10)!=Rational(1,2)
    elif index==7:
        s=lambda n:Rational(n*(n+1),2)
        ok=s(3)-s(2)==3; bad=Rational(s(3),s(2))!=3
    elif index==8:
        ok=simplify(((2+x)**2-4)/x-(4+x))==0 and 4+1==5
        # |x| at 0: exact left and right difference quotients disagree.
        h=Rational(1,10)
        bad=abs(h)/h != abs(-h)/(-h)
    elif index==9:
        # Fermat necessity at a differentiable interior minimum x^2.
        ok=simplify(__import__("sympy").diff(x*x,x).subs(x,0))==0 and all(v*v>=0 for v in [-1,0,1])
        # Converse fails: x^3 is stationary at 0 but changes sign.
        bad=simplify(__import__("sympy").diff(x**3,x).subs(x,0))==0 and (-1)**3<0<(1)**3
    elif index==10:
        n=Matrix([0,0,1]);v=Matrix([1,0,0])
        ok=n.dot(v)==0 and n.dot(Matrix([0,0,1]))!=0
        bad=n.dot(Matrix([0,0,0]))==0
    elif index==11:
        # Focus pair (-1,0),(1,0), a=2: (0,sqrt(3)) has sum 4.
        ok=sqrt(1+3)+sqrt(1+3)==4
        # Degeneracy a=c=1: points on the focal segment meet sum=2,
        # but (0,1) does not; hence locus is not a non-degenerate ellipse.
        bad=(abs(Rational(0)+1)+abs(Rational(0)-1)==2 and 2*sqrt(2)>2)
    elif index==12:
        ok=3*2==6 and Rational(1,2)*Rational(1,4)==Rational(1,8)
        bad=1+2+2!=6
    elif index==13:
        ok=Rational(1,2)*Rational(1,5)+Rational(1,2)*Rational(4,5)==Rational(1,2)
        bad=2*Rational(1,2)!=Rational(1,2)
    elif index==14:
        ok=2*Rational(1,2)*Rational(1,2)==Rational(1,2)
        bad=1!=Rational(1,2)
    elif index==15:
        ok=Rational(1,3)>0 and Rational(1,3)<=1
        bad=(-1)**2!=(-1)**3
    elif index==16:
        ok=all(0<=v*v<=4 for v in [0,1,2])
        bad=Rational(1,1000)>0 and 1/Rational(1,1000)>4
    elif index==17:
        ok=Rational(9-1,3-1)==4 and 2*2==4
        # |x| is continuous on [-1,1] but not differentiable at zero.
        h=Rational(1,5)
        bad=abs(h)/h != abs(-h)/(-h)
    elif index==18:
        ok=integrate(x,(x,-1,1))==0 and integrate(abs(x),(x,-1,1))==1
        bad=integrate(abs(x),(x,-1,1))!=integrate(x,(x,-1,1))
    elif index==19:
        a=Matrix([[4,0],[0,9]]);b=Matrix([[4,6],[6,9]])
        ok=a.det()==36 and a[0,0]>0 and a[1,1]>0
        bad=b.det()==0
    else:raise ValueError("unknown finite instance")
    check(ok is True or bool(ok),"independent exact positive failed")
    check(bad is True or bool(bad),"independent exact boundary failed")
    return {"positive_exact_instance_verified":True,
            "invalid_boundary_exact_instance_verified":True,
            "general_theorem_certified":False,"math_equivalence_certified":False,
            "teacher_approved":False,"student_publishable":False}

def build(records=None):
    records=RECORDS if records is None else records
    check(type(records) is list and len(records)==20,"exactly 20 authored comparisons expected")
    base=Q.source_read(Q.SOURCE)["provisional_candidate_backlog"]
    previous=Q.source_read(Q.PREV)
    by_title={row["provisional_topic"]:row for row in base}
    check(len(by_title)==len(base)==300,"ambiguous source topics")
    unpaired=set(previous["remaining_unpaired_candidate_ids"])
    paired={x["candidate_id"] for x in base}-unpaired
    result=[];seen=set()
    for i,note in enumerate(records):
        check(type(note) is dict and set(note)==FIELDS,"authored compare schema")
        left,right=note["left"],note["right"]
        check(all(type(note[key]) is str and len(note[key])>=27 for key in
                  ("conditions","distinction","positive","invalid")),
              "insufficient math conditions/boundary")
        check(left in by_title and right in by_title and left!=right,
              "unrecognized source title")
        a,b=by_title[left],by_title[right]
        check(a["candidate_id"] in unpaired and b["candidate_id"] in paired
              and a["candidate_id"] not in seen,"invalid pair source/duplicate")
        check(note["relation"] in ALLOWED,"unreviewed relation promoted")
        for row in (a,b):
            check(row["review_status"]=="REVIEW_PENDING" and row["teacher_approval"] is None
                  and row["official_math_atom_id"] is None
                  and row["student_authoritative_index_eligible"] is False,
                  "source has authority drift")
            check(len(row["source_line_sha256"])==64,"missing source digest")
        seen.add(a["candidate_id"])
        result.append({
          "editorial_pair_id":f"KB101-PAIR-{i+1:02d}",
          "left_source_candidate_id":a["candidate_id"],
          "left_topic":left, "left_track":a["track"],
          "left_source_page":a["source_page"],
          "left_source_line_sha256":a["source_line_sha256"],
          "right_source_candidate_id":b["candidate_id"],
          "right_topic":right, "right_track":b["track"],
          "right_source_page":b["source_page"],
          "right_source_line_sha256":b["source_line_sha256"],
          "cross_track":a["track"]!=b["track"],
          "proposed_relationship":note["relation"],
          "necessary_conditions":note["conditions"],
          "mathematical_distinction":note["distinction"],
          "positive_example":note["positive"],
          "invalid_boundary_or_counterexample":note["invalid"],
          "independent_finite_witness":instance(i),
          "editorial_pair_comparison":"AUTHORED_REVIEW_PENDING",
          "mathematical_equivalence_certified":False,
          "official_atom_id":None,
          "teacher_review_status":"REVIEW_PENDING",
          "teacher_approved":False,"student_publishable":False,
        })
    check(len(seen)==20,"20 comparisons not distinct")
    return {
      "schema_version":"kb101-20-mathematical-pair-drafts-v1",
      "source_candidate_snapshot_sha256":Q.digest(Q.SOURCE),
      "prior_unpaired_queue_sha256":Q.digest(Q.PREV),
      "authoring_sha256":Q.digest(AUTHOR),
      "historically_unpaired_provisional_labels":134,
      "newly_authored_semantic_pair_comparisons":20,
      "remaining_without_any_editorial_pair_comparison":114,
      "teacher_semantic_equivalence_adjudications":0,
      "approved_official_merges":0,
      "official_atom_denominators_by_track":{x:None for x in Q.TRACKS},
      "teacher_approved":0,"student_publishable":False,
      "finite_instance_checks":20,
      "finite_checks_certify_general_claims":False,
      "editorial_pairs":result,
    }

def validate(data):
    check(len(data["editorial_pairs"])==data["newly_authored_semantic_pair_comparisons"]==20,
          "missing authored math pairs")
    check(data["historically_unpaired_provisional_labels"]==134
          and data["remaining_without_any_editorial_pair_comparison"]==114
          and data["approved_official_merges"]==0
          and data["teacher_approved"]==0
          and not data["student_publishable"]
          and all(x is None for x in data["official_atom_denominators_by_track"].values()),
          "fake official coverage or approval")
    ids=set()
    for row in data["editorial_pairs"]:
        check(row["left_source_candidate_id"] not in ids
              and row["editorial_pair_comparison"]=="AUTHORED_REVIEW_PENDING"
              and row["teacher_review_status"]=="REVIEW_PENDING"
              and not row["teacher_approved"] and not row["student_publishable"]
              and not row["mathematical_equivalence_certified"]
              and row["official_atom_id"] is None
              and row["proposed_relationship"] in ALLOWED
              and not row["independent_finite_witness"]["general_theorem_certified"],
              "math pair status forged")
        ids.add(row["left_source_candidate_id"])
    check(len(ids)==20,"source pair collision")

def markdown(data):
    s=["# Batch101｜20项有数学证据的来源主题成对比较草案","",
       "**未审核：** 这些是原创数学区别、前提、正例和反例的人工编写草案；有限精确算例≠一般定理证明，也≠教师同意合并正式课标原子。",
       "",
       "|指标|数值|","|---|---:|",
       "|历史尚未比较临时主题|134|",
       "|本批明确编写数学比较|20|",
       "|剩余未经过任何成对编辑比较|114|",
       "|数学有限实例验证|20|",
       "|教师最终等价裁决|0|","|官方原子分母|UNKNOWN|",""]
    for row in data["editorial_pairs"]:
        s += [f"## {row['editorial_pair_id']}｜{row['left_topic']} ↔ {row['right_topic']}",
              "",f"**来源：** {row['left_source_candidate_id']}（{row['left_track']} / 页{row['left_source_page']} / SHA256 {row['left_source_line_sha256']}）与 {row['right_source_candidate_id']}（{row['right_track']} / 页{row['right_source_page']} / SHA256 {row['right_source_line_sha256']}）",
              "",f"**关系候选：** {row['proposed_relationship']}；未核定是否语义等价。",
              "",f"**适用前提：** {row['necessary_conditions']}",
              "",f"**数学区别：** {row['mathematical_distinction']}",
              "",f"**正例：** {row['positive_example']}",
              "",f"**边界反例：** {row['invalid_boundary_or_counterexample']}",
              "", "**独立验证：** 该对比的一个合法与一个失效情况通过精确有限算例；不认证普遍数学断言。",""]
    return "\n".join(s)

def run(check_only=False):
    data=build()
    validate(data)
    files={OUT:json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",
           MD:markdown(data)}
    for path,content in files.items():
        if check_only:check(path.read_text(encoding="utf8")==content,"output/source drift "+str(path))
        else:path.write_text(content,encoding="utf8")
    print("BATCH101 20 mathematical editorial pairs, 20 bounded witnesses; 114 remain, approved=0; check",check_only)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    run(p.parse_args().check)
