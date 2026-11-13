#!/usr/bin/env python3
"""Batch102 source-locked mathematical editorial comparisons.

Finite exact witnesses check individual calculations and counterexamples only.
No official syllabus atom, general theorem or teacher decision is certified.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

from sympy import Matrix, Rational as R, Symbol, sqrt, pi, sin, cos, diff, limit, oo
from sympy import simplify, integrate, binomial, Piecewise

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"scripts"), str(ROOT/"backend")]
import build_kb_batch101_review_queue as Q

AUTHOR = ROOT/"scripts/kb_batch102_pair_authoring.json"
PREVIOUS_PAIRS = ROOT/"docs/evaluation/KB_BATCH101_20_MATH_COMPARISONS.json"
OUT = ROOT/"docs/evaluation/KB_BATCH102_20_MATH_COMPARISONS.json"
MD = ROOT/"docs/evaluation/KB_BATCH102_20_MATH_COMPARISONS.md"
COVERAGE = ROOT/"docs/evaluation/KB_BATCH102_COVERAGE.json"
TRACKS = tuple(Q.TRACKS)
ALLOWED = {"RELATED_DISTINCT", "POSSIBLE_OVERLAP_UNRESOLVED"}
FIELDS = {"left", "right", "relation", "conditions", "distinction", "positive", "invalid"}

def insist(condition, reason):
    if not condition:
        raise ValueError(reason)

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def finite_witness(i):
    """One independent legal/illegal *finite* mathematical instance per comparison."""
    x = Symbol("x", real=True)
    h = Symbol("h", real=True, nonzero=True)
    n = Symbol("n", positive=True, integer=True)
    if i == 0:
        good = [3, 5, 7, 9] == [3+2*k for k in range(4)]
        bad = [5-3, 8-5, 9-8] != [2, 2, 2]
    elif i == 1:
        good = sum((2, 5, 8, 11)) == 26
        bad = sum((2, 5, 8, 11)) != 4*11
    elif i == 2:
        S = lambda k: R(k*(k+1), 2)
        good = S(4)-S(3) == 4
        bad = S(4)/S(3) != 4
    elif i == 3:
        good = limit((R(7)-R(7))/h, h, 0) == 0
        bad = limit((R(7)-R(7))/h, h, 0) != 7
    elif i == 4:
        q = simplify(((2+h)**3-8)/h)
        good = limit(q, h, 0) == 12
        bad = q.subs(h, 1) == 19 and q.subs(h, 1) != 12
    elif i == 5:
        p = Matrix([2, 3, 4])
        good = p[0] == 2 and p.dot(p) == 29
        bad = p[2] != 0
    elif i == 6:
        u, v = Matrix([2,2,0]), Matrix([1,0,0])
        proj = v * (u.dot(v)/v.dot(v))
        good = proj == Matrix([2,0,0]) and (u-proj).dot(v) == 0
        bad = Matrix([0,0,0]).dot(Matrix([0,0,0])) == 0
    elif i == 7:
        good = abs(R(2))/sqrt(R(1)) == 2
        bad = sqrt(R(2)) != 2 and simplify(abs(R(2))/sqrt(2)-sqrt(2)) == 0
    elif i == 8:
        good = simplify(x-(-x)) == 2*x and simplify((2*x).subs(x,0)) == 0
        bad = simplify((x+1)-x) == 1
    elif i == 9:
        good = 4*3 == 12 and binomial(4,2) == 6
        bad = 4*3 != binomial(4,2)
    elif i == 10:
        hg = binomial(2,2)*binomial(2,0)/binomial(4,2)
        bi = R(1,2)**2
        good = hg == R(1,6)
        bad = bi == R(1,4) and hg != bi
    elif i == 11:
        good = R(5-3,2) == 1
        bad = R(1) != 0 and R(0) == 0  # nonzero σ is required to form the ratio
        bad = bad and Matrix([[4, 6],[6, 9]]).det() == 0
    elif i == 12:
        f = x*x
        jump = Piecewise((0,x<0),(1,True))
        good = limit(f,x,1) == f.subs(x,1) == 1
        bad = (jump.subs(x,-R(1,10))==0 and jump.subs(x,R(1,10))==1 and
               limit(0,x,0,dir="-") != limit(1,x,0,dir="+"))
    elif i == 13:
        d = diff(sin(x*x),x)
        good = simplify(d - 2*x*cos(x*x)) == 0
        bad = simplify(d.subs(x,1) - cos(1)) != 0
    elif i == 14:
        good = limit(1/n+1/n**2,n,oo) == 0
        bad = limit((1/n)/(1/n**2),n,oo) == oo
    elif i == 15:
        good = integrate(2*x,(x,0,2)) == 4
        bad = integrate(x**2,(x,0,2)) == R(8,3) != 4
    elif i == 16:
        y=Symbol("y",real=True)
        f=x*x+y*y
        good = diff(f,x).subs({x:1,y:2})==2 and diff(f,y).subs({x:1,y:2})==4
        bad = (diff(f,x)+diff(f,y)).subs({x:1,y:2})==6 != 2
    elif i == 17:
        good = limit(1-1/n,n,oo)==1 and R(1,2) < R(2,3) < 1
        bad = limit(n,n,oo)==oo
    elif i == 18:
        p1,p2 = R(30,40),R(10,40)
        good = p1==R(3,4) and p2==R(1,4)
        bad = p1!=p2
    elif i == 19:
        phi=(1+sqrt(5))/2
        good = simplify(phi**2-phi-1)==0
        bad = simplify(2-phi)!=0
    else:
        raise ValueError("finite witness index not in 0..19")
    insist(bool(good), f"exact valid witness failed at {i}")
    insist(bool(bad), f"exact invalid-boundary witness failed at {i}")
    return {"valid_instance_exact": True, "invalid_boundary_exact": True,
            "general_theorem_certified": False, "semantic_equivalence_certified": False,
            "teacher_reviewed": False, "student_publishable": False}

def build(authored=None):
    notes = json.loads(AUTHOR.read_text(encoding="utf8")) if authored is None else authored
    insist(isinstance(notes,list) and len(notes)==20,"exactly 20 authored source comparisons required")
    source = Q.source_read(Q.SOURCE)["provisional_candidate_backlog"]
    prev_unpaired = Q.source_read(Q.PREV)["remaining_unpaired_candidate_ids"]
    prev_pairs = json.loads(PREVIOUS_PAIRS.read_text(encoding="utf8"))
    insist(len(source)==300 and len({r["candidate_id"] for r in source})==300, "frozen source candidate ID collision")
    insist(len(prev_unpaired)==134 and len(set(prev_unpaired))==134, "frozen unpaired list mismatch")
    insist(len(prev_pairs["editorial_pairs"])==20, "prior math comparisons drift")
    by_title={x["provisional_topic"]:x for x in source}
    insist(len(by_title)==300, "ambiguous source titles")
    older=set(prev_unpaired)
    prev_new={x["left_source_candidate_id"] for x in prev_pairs["editorial_pairs"]}
    insist(len(prev_new)==20 and prev_new<=older,"prior comparison must come from unpaired set")
    remaining=older-prev_new
    earlier={x["candidate_id"] for x in source}-remaining
    insist(len(remaining)==114 and len(earlier)==186, "batch101 baseline drift")
    seen=set()
    result=[]
    for i,r in enumerate(notes):
        insist(type(r) is dict and set(r)==FIELDS, f"invalid authored schema {i}")
        insist(r["relation"] in ALLOWED,"unreviewed mathematical relation promotion")
        insist(all(isinstance(r[field],str) and len(r[field].strip())>=32 for field in
                   ("conditions","distinction","positive","invalid")), "mathematical explanation insufficient")
        a,b=by_title.get(r["left"]),by_title.get(r["right"])
        insist(a is not None and b is not None and a!=b, "unanchored or identical source titles")
        insist(a["candidate_id"] in remaining and a["candidate_id"] not in seen,
                "duplicate/non-outstanding source candidate")
        insist(b["candidate_id"] in earlier, "right-side source is not previously compared")
        for item in (a,b):
            insist(item["review_status"]=="REVIEW_PENDING" and
                   item["teacher_approval"] is None and item["official_math_atom_id"] is None
                   and item["student_authoritative_index_eligible"] is False, "source authority drift")
            insist(len(item["source_line_sha256"])==64, "missing source line SHA")
        seen.add(a["candidate_id"])
        result.append({
            "editorial_pair_id": f"KB102-PAIR-{i+1:02d}",
            "left_source_candidate_id":a["candidate_id"],"left_topic":r["left"],
            "left_track":a["track"],"left_source_page":a["source_page"],
            "left_source_line_sha256":a["source_line_sha256"],
            "right_source_candidate_id":b["candidate_id"],"right_topic":r["right"],
            "right_track":b["track"],"right_source_page":b["source_page"],
            "right_source_line_sha256":b["source_line_sha256"],
            "cross_track":a["track"]!=b["track"],
            "proposed_relationship":r["relation"],
            "necessary_conditions":r["conditions"],
            "mathematical_distinction":r["distinction"],
            "positive_example":r["positive"],
            "invalid_boundary_or_counterexample":r["invalid"],
            "independent_finite_witness":finite_witness(i),
            "editorial_pair_comparison":"AUTHORED_REVIEW_PENDING",
            "mathematical_equivalence_certified":False,"official_atom_id":None,
            "teacher_review_status":"REVIEW_PENDING","teacher_approved":False,
            "student_publishable":False
        })
    insist(len(seen)==20,"not 20 unique comparisons")
    distribution=Counter(x["track"] for x in source)
    prior_by_track=Counter(x["track"] for x in source if x["candidate_id"] in earlier)
    now_by_track=Counter(x["left_track"] for x in result)
    remaining_by_track=Counter(x["track"] for x in source
                                if x["candidate_id"] in remaining-seen)
    rows={t:{"provisional_source_labels":distribution[t],
             "prior_compared":prior_by_track[t], "new_editorial_comparisons":now_by_track[t],
             "remaining":remaining_by_track[t], "official_atom_denominator":None}
          for t in TRACKS}
    return {
        "schema_version":"kb102-mathematical-pairs-v1",
        "source_candidates_sha256":Q.digest(Q.SOURCE),
        "prior_pairs_sha256":digest(PREVIOUS_PAIRS),
        "authoring_sha256":digest(AUTHOR),
        "previously_compared_provisional_labels":186,
        "newly_compared_provisional_labels":20,
        "remaining_unpaired_provisional_labels":94,
        "official_atom_denominators_by_track":{t:None for t in TRACKS},
        "fully_human_atomized_pages":0,
        "teacher_semantic_adjudications":0,
        "teacher_approved":0,
        "student_authoritative_release":0,
        "finite_math_witnesses":20,
        "general_formal_proofs_certified":0,
        "track_matrix":rows,
        "editorial_pairs":result
    }

def validate(data):
    insist(data["previously_compared_provisional_labels"]+
           data["newly_compared_provisional_labels"]+
           data["remaining_unpaired_provisional_labels"]==300,"global conservation")
    insist(data["previously_compared_provisional_labels"]==186 and
           data["newly_compared_provisional_labels"]==20 and
           data["remaining_unpaired_provisional_labels"]==94,"batch102 coverage fabricated")
    insist(data["teacher_semantic_adjudications"]==data["teacher_approved"]==
           data["student_authoritative_release"]==data["general_formal_proofs_certified"]==
           data["fully_human_atomized_pages"]==0,"unauthorized certification")
    insist(all(v is None for v in data["official_atom_denominators_by_track"].values()),
           "unknown official denominators fabricated")
    insist(len(data["editorial_pairs"])==20 and data["finite_math_witnesses"]==20,
           "mathematical comparisons lost")
    for t,cols in data["track_matrix"].items():
        insist(t in TRACKS and cols["official_atom_denominator"] is None and
               cols["prior_compared"]+cols["new_editorial_comparisons"]+cols["remaining"]==
               cols["provisional_source_labels"], "seven-track conservation")
    seen=set()
    for row in data["editorial_pairs"]:
        insist(row["left_source_candidate_id"] not in seen and
               row["teacher_review_status"]=="REVIEW_PENDING" and
               row["official_atom_id"] is None and not row["teacher_approved"] and
               not row["student_publishable"] and not row["mathematical_equivalence_certified"] and
               row["editorial_pair_comparison"]=="AUTHORED_REVIEW_PENDING" and
               row["proposed_relationship"] in ALLOWED and
               row["independent_finite_witness"]["valid_instance_exact"] and
               row["independent_finite_witness"]["invalid_boundary_exact"] and
               not row["independent_finite_witness"]["general_theorem_certified"],
               "promoted/duplicate/unverified review object")
        seen.add(row["left_source_candidate_id"])

def markdown(data):
    lines=["# Batch102｜20项条件边界明确的数学成对编辑审查","",
           "> 教师审核前均为 REVIEW_PENDING。这是工程临时来源标签的数学区别草案，不是官方原子、教师合并裁决或形式证明。","",
           "|状态|数量|","|---|---:|",
           "|Batch101已有编辑比较|186|","|Batch102新增独立数学比较|20|",
           "|累计已比较|206/300|","|剩余未比较|94|",
           "|有限精确正/反实例|20组|","|真实教师批准及学生权威发布|0|",
           "|七轨官方原子分母|UNKNOWN|",""]
    for a in data["editorial_pairs"]:
        lines += [f"## {a['editorial_pair_id']}｜{a['left_topic']} ↔ {a['right_topic']}","",
          f"来源锚点：{a['left_source_candidate_id']} ({a['left_track']} 第{a['left_source_page']}页; sha256={a['left_source_line_sha256']})；{a['right_source_candidate_id']} ({a['right_track']} 第{a['right_source_page']}页; sha256={a['right_source_line_sha256']})。","",
          f"**关系候选（非认证）：** {a['proposed_relationship']}",
          f"**全部必要前提：** {a['necessary_conditions']}",
          f"**数学区别及限制：** {a['mathematical_distinction']}",
          f"**合法实例：** {a['positive_example']}",
          f"**失效/反例：** {a['invalid_boundary_or_counterexample']}",
          "**验证边界：** 一组精确算例成功，不能推出一般定理或两个来源语义等价；人工审核仍必需。",""]
    return "\n".join(lines)

def run(check_only=False):
    data=build()
    validate(data)
    files={OUT:json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n",
           MD:markdown(data),
           COVERAGE:json.dumps({k:data[k] for k in
                 ("schema_version","previously_compared_provisional_labels",
                  "newly_compared_provisional_labels","remaining_unpaired_provisional_labels",
                  "official_atom_denominators_by_track","fully_human_atomized_pages",
                  "teacher_approved","student_authoritative_release","track_matrix")},
                 ensure_ascii=False,indent=2,sort_keys=True)+"\n"}
    for p,v in files.items():
        if check_only:
            insist(p.read_text(encoding="utf8")==v, f"author/source/output drift: {p}")
        else:
            p.write_text(v,encoding="utf8")
    print(f"BATCH102 exact comparisons {len(data['editorial_pairs'])} / provisional 206 of 300, 94 unpaired, teacher approvals 0, check={check_only}")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    run(ap.parse_args().check)
