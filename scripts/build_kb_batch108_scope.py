#!/usr/bin/env python3
"""Batch108: source-line-locked scope candidates, not official atom counts."""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path

import sympy as s

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from kb_batch108_scope_authoring import CANDIDATES,PARTITIONS
META=ROOT/"curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
OUT=ROOT/"docs/evaluation/KB_BATCH108_SCOPE.json"
MD=ROOT/"docs/evaluation/KB_BATCH108_SCOPE.md"
PDF=Path.home()/"Library/Caches/stem-mentor-source-review/highschool_math_standard_2020.pdf"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
        "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
SOURCE_LOCK={(r["key"]):(r["page"],r["start"],r["end"])
             for r in CANDIDATES}

def require(ok,reason):
    if not ok:raise ValueError(reason)

def serialize(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"

def exact_witness(key):
    """Exact, bounded counterexamples/positive checks. NOT universal theorem proofs."""
    x,y,z=s.symbols("x y z",real=True)
    M=s.Matrix
    if key in {"collaborative_guidance","pedagogy_guidance","competency_marker"}:
        return {"status":"NOT_AUTOMATICALLY_CHECKABLE","finite_exact_positive_passed":False,
                "invalid_generalization_rejected":False,"general_proof_certified":False}
    if key=="equality_inequality":
        pos=(-2<1 and -2*3<1*3)
        neg=not (-2*(-1)<1*(-1)) # sign must flip
    elif key=="quadratic_function":
        pos=(s.solve(x*x-2*x+1,x)==[1])
        neg=(len(s.solve(x*x-2*x+1,x))!=2)
    elif key=="set_language":
        pos=({1,2}|{2,3})=={1,2,3}
        neg=(1!={1})
    elif key=="logic_quantifier":
        domain=[0,1];predicate=lambda t:t==0
        pos=not all(predicate(t) for t in domain)
        neg=(not all(predicate(t) for t in domain))!=all(not predicate(t) for t in domain)
    elif key=="function_view":
        f=lambda a:a*a-1
        pos=f(1)==0 and f(-1)==0
        neg=f(0)!=0
    elif key=="gaussian_row":
        A=M([[1,1,0],[0,1,1],[1,0,1]])
        b=M([2,3,4]);sol=A.inv()*b
        B=A.copy();c=b.copy();B[0,:]=B[0,:]+2*B[1,:];c[0]=c[0]+2*c[1]
        pos=B*sol==c
        C=A.copy();d=b.copy();C[0,:]=M([[0,0,0]]);d[0]=0
        neg=C.rank()<A.rank() and C*(sol+C.nullspace()[0])==d and A*(sol+C.nullspace()[0])!=b
    elif key=="homogeneous_kernel":
        A=M([[1,2,3],[2,4,6],[0,1,1]])
        v=M([-1,-1,1])
        pos=A.det()==0 and A*v==M([0,0,0]) and v!=M([0,0,0])
        neg=(A*v==M([0,0,0]) and v!=M([0,0,0]))
    elif key=="consistency_rank":
        A=M([[1,0,0],[0,1,0],[0,0,0]])
        b=M([1,2,1]);pos=A.rank()==2 and A.row_join(b).rank()==3
        neg=A.rank()!=A.row_join(b).rank()
    elif key=="affine_solution":
        A=M([[1,1,0],[0,1,1],[0,0,0]])
        p=M([1,0,1]);v=M([-1,1,-1])
        pos=A*(p+2*v)==A*p and A*v==M([0,0,0])
        neg=A*(p+M([1,0,0]))!=A*p
    elif key=="cramer":
        A=M([[2,0,0],[0,3,0],[0,0,5]]);b=M([4,9,10])
        def replace_col(A,index,b):
            V=A.copy();V[:,index]=b;return V
        solution=A.inv()*b
        pos=A.det()!=0 and all(s.simplify(replace_col(A,i,b).det()/A.det()-solution[i])==0 for i in range(3))
        neg=M([[1,0,0],[0,1,0],[0,0,0]]).det()==0
    elif key=="plane_eq":
        normal=M([1,2,2]);p=M([1,1,-1])
        pos=(normal.dot(p)-1==0)
        neg=(M([0,0,0]).norm()==0)
    elif key=="line_eq":
        p=M([1,2,3]);v=M([1,0,2])
        pos=p+2*v==M([3,2,7])
        neg=(p+0*M([0,0,0])==p and p+3*M([0,0,0])==p)
    elif key=="point_plane_dist":
        normal=M([2,0,0]);p=M([3,0,0])
        pos=s.Abs(normal.dot(p))/normal.norm()==3
        neg=normal.dot(M([-3,0,0]))/normal.norm()<0
    elif key=="planar_reflection":
        J=M([[1,0],[0,-1]]);p=M([1,2]);q=M([4,6])
        pos=(J*(p-q)).norm()==(p-q).norm()
        neg=M([1,4]).norm()!=M([1,2]).norm()
    elif key=="symmetry_set":
        S={(-1,0),(1,0)};flip=lambda p:(-p[0],p[1])
        pos={flip(p) for p in S}==S
        neg=flip((1,0))!=(1,0)
    elif key=="rotation_matrix":
        R=M([[0,-1],[1,0]])
        pos=R.T*R==s.eye(2)
        N=M([[1,1],[0,1]])
        neg=N.det()==1 and N.T*N!=s.eye(2)
    elif key=="space_isometry":
        Q=M([[1,0,0],[0,-1,0],[0,0,1]]);t=M([4,5,6])
        a=M([0,2,-1]);b=M([3,0,2])
        pos=((Q*a+t)-(Q*b+t)).norm()==(a-b).norm()
        neg=M([[2,0,0],[0,1,0],[0,0,1]]).T*M([[2,0,0],[0,1,0],[0,0,1]])!=s.eye(3)
    else:raise ValueError("unknown math witness key")
    require(bool(pos) and bool(neg),f"failed exact math witness: {key}")
    return {"status":"FINITE_EXACT_WITNESS_ONLY","finite_exact_positive_passed":True,
            "invalid_generalization_rejected":True,"general_proof_certified":False}

def build(candidates=CANDIDATES,partitions=PARTITIONS,verify_local_source=False):
    require(len(candidates)==20,"require 20 distinct editorial candidates")
    schema=set(CANDIDATES[0])
    require(all(type(r) is dict and set(r)==schema for r in candidates),
            "candidate schema drift or forged approval field")
    keys=[r["key"] for r in candidates]
    require(len(keys)==len(set(keys)),"duplicate candidate key")
    require(set(keys)==set(SOURCE_LOCK),"missing source candidate or forged key")
    m={r["printed_page"]:r for r in json.loads(META.read_text())["pages"]}
    require(set(partitions)=={18,55},"wrong source pages")
    require({p:m[p]["pdf_page_index"] for p in partitions}=={18:25,55:62},
            "source PDF page index drift")
    limits={18:28,55:25}
    for p,segments in partitions.items():
        require([i for lo,hi,_ in segments for i in range(lo,hi+1)]
                ==list(range(1,limits[p]+1)),"missing/overlapping source lines")
    if verify_local_source:
        require(PDF.is_file() and sha256(PDF.read_bytes()).hexdigest()==PDF_SHA,
                "Mac PDF bytes mismatch")
        for p in partitions:
            f=Path(f"/private/tmp/kb56_page_{p}.txt")
            require(f.exists() and sha256(f.read_bytes()).hexdigest()==m[p]["pdfkit_text_sha256"],
                    "Mac PDFKit page fingerprint mismatch")
    rows=[];counts=Counter()
    for i,r in enumerate(candidates,1):
        p=r["page"];lo=r["start"];hi=r["end"]
        require((p,lo,hi)==SOURCE_LOCK.get(r["key"]),"source-clause lock mismatch")
        require(p in limits and type(lo)==int and type(hi)==int and 1<=lo<=hi<=limits[p],
                "invalid source line")
        require(sum(1 for low,high,_ in partitions[p] if low<=lo<=hi<=high)==1,
                "candidate straddles structural source segment")
        require(r["kind"] in {"CONCEPT","THEOREM","METHOD","PEDAGOGY"},
                "invalid candidate mathematical kind")
        require(all(len(r[k])>=18 for k in ("mathematical_preconditions","invalid_generalization",
                                           "editorial_note")),"thin math condition or invalid case")
        track="COMPULSORY" if p==18 else "ELECTIVE_A"
        counts[track]+=1
        rows.append({**r,"id":f"KB108-P{p:03d}-C{i:02d}",
                     "track_hint":track,"source_pdf_sha256":PDF_SHA,
                     "source_page_pdfkit_sha256":m[p]["pdfkit_text_sha256"],
                     "pdf_page_index":m[p]["pdf_page_index"],
                     "math_witness":exact_witness(r["key"]),
                     "official_atom_id":None,"teacher_review_status":"REVIEW_PENDING",
                     "student_authoritative_release":False})
    require(counts=={"COMPULSORY":8,"ELECTIVE_A":12},"seven track source conservation")
    return {
      "batch":108,"scope_kind":"EDITORIAL_SOURCE_CANDIDATES_NOT_OFFICIAL_ATOMS",
      "curriculum_standard":"普通高中数学课程标准（2017年版2020年修订）",
      "source_pdf_sha256":PDF_SHA,"source_fingerprint_registry_sha256":sha256(META.read_bytes()).hexdigest(),
      "authoring_sha256":sha256((ROOT/"scripts/kb_batch108_scope_authoring.py").read_bytes()).hexdigest(),
      "pages":[18,55],"source_lines_total":sum(limits.values()),"line_counts":{str(p):n for p,n in limits.items()},
      "structural_partitions":[{"page":p,"start":lo,"end":hi,"kind":k}
                                for p,part in sorted(partitions.items()) for lo,hi,k in part],
      "new_editorial_candidates":len(rows),"track_hint_counts":{x:counts[x] for x in TRACKS},
      "official_seven_track_atom_denominators":{x:None for x in TRACKS},
      "teacher_full_page_atomizations":0,"teacher_approvals":0,"student_authoritative_releases":0,
      "bounded_exact_witnesses":sum(x["math_witness"]["status"]=="FINITE_EXACT_WITNESS_ONLY" for x in rows),
      "pedagogy_items_not_math_proofs":sum(x["kind"]=="PEDAGOGY" for x in rows),
      "candidates":rows,
      "limitations":["Page 18 includes pedagogy and achievement descriptors, not 8 independently official atoms.",
       "Page 55 elective A source is not interchangeable with all project elective expansion tags.",
       "Finite exact cases are not a universal proof, a certified student step or teacher approval.",
       "No official seven-track mathematical atom denominator has yet been frozen."]
    }

def markdown(obj):
    parts=["# Batch108｜第18、55页课程证据逐段审查（候审）","",
           "来源PDF页级校验、逐行分区与课程数学编辑解释分开计数。","",
           f"来源行数：{obj['source_lines_total']}；结构分区：{len(obj['structural_partitions'])}；"
           f"候审编辑要求：{obj['new_editorial_candidates']}；有限精确见证：{obj['bounded_exact_witnesses']}。","",
           "正式七轨官方数学原子分母仍 UNKNOWN；没有教师审批或学生权威发布。",""]
    for r in obj["candidates"]:
        parts.extend([f"## {r['id']}｜{r['title']}","",
              f"印刷页{r['page']}行{r['start']}–{r['end']}；轨道提示{r['track_hint']}；类别{r['kind']}。","",
              "前提："+r["mathematical_preconditions"],"",
              "无效泛化："+r["invalid_generalization"],"",
              "课程拆分解释："+r["editorial_note"],"",
              "有限数学检查："+r["math_witness"]["status"],""])
    return "\n".join(parts).rstrip()+"\n"

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--check",action="store_true")
    parser.add_argument("--verify-local-source",action="store_true")
    args=parser.parse_args()
    data=build(verify_local_source=args.verify_local_source)
    outputs=((OUT,serialize(data)),(MD,markdown(data)))
    if args.check:
        for path,content in outputs:
            require(path.read_text(encoding="utf8")==content,f"drift {path.name}")
    else:
        for path,content in outputs:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding="utf8")
    print(f"Batch108 scope: {len(data['candidates'])} editorial, {data['bounded_exact_witnesses']} exact, {data['source_lines_total']} source lines; PASS")

if __name__=="__main__":
    main()
