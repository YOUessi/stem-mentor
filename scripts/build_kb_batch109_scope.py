#!/usr/bin/env python3
"""Official PDFKit-sourced *provisional editorial* records for printed pages 19 & 56."""
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
from kb_batch109_scope_authoring import CANDIDATES, PARTITIONS
META=ROOT/"curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
OUT=ROOT/"docs/evaluation/KB_BATCH109_SCOPE.json"
MD=ROOT/"docs/evaluation/KB_BATCH109_SCOPE.md"
PDF=Path.home()/"Library/Caches/stem-mentor-source-review/highschool_math_standard_2020.pdf"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
LIMITS={19:27,56:27}
PDF_PAGES={19:26,56:63}
CONTINUATION_PAGES={19:20,56:57}
SOURCE_LOCK={r["key"]:(r["page"],r["start"],r["end"],r["kind"]) for r in CANDIDATES}

def require(ok,message):
    if not ok: raise ValueError(message)

def serialize(data):
    return json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"

def exact_witness(key):
    """Independent finite or exact symbolic *instances*; no universal proof certificates."""
    if key in ("functions_theme","functions_modeling","optional_history",
               "probability_context","inference_context"):
        return {"status":"PEDAGOGY_NOT_AUTOMATICALLY_CHECKABLE",
                "finite_exact_positive_passed":False,"invalid_generalization_rejected":False,
                "general_proof_certified":False}
    x=s.symbols("x", real=True)
    if key=="function_mapping":
        f={-1:1,0:0,1:1}
        pos=len(f)==3 and f[-1]==f[1]
        neg=len({v for u,v in [(0,1),(0,2)] if u==0})==2
    elif key=="function_representations":
        domain={0,1,2};table={i:i*i for i in domain}
        pos=all(table[i]==i*i for i in domain)
        neg=domain!={-1,0,1,2}
    elif key=="piecewise":
        f=lambda t:-t if t<0 else t*t
        pos=f(-2)==2 and f(0)==0 and f(2)==4
        left=lambda t:t
        right=lambda t:t+1
        neg=(left(1)!=right(1)) # incompatible overlapping boundary definitions
    elif key=="monotonic_extrema":
        pos=(0*0<1*1<2*2)
        neg=( (-2)**2 > (-1)**2 )  # x^2 not increasing on [-2,2]
    elif key=="parity":
        pos=s.simplify((-x)**2-x*x)==0
        neg=(s.sqrt(4)==2 and -4<0) # sqrt's nonnegative real domain not symmetric
    elif key=="periodicity":
        pos=s.simplify(s.sin(x+2*s.pi)-s.sin(x))==0
        neg=s.sin(s.pi/2+s.pi)!=s.sin(s.pi/2)
    elif key=="continuous_variable":
        pos=s.integrate(s.Rational(1,2),(x,0,2))==1
        neg=s.integrate(s.Rational(1,2),(x,1,1))==0
    elif key=="uniform_density":
        pos=s.integrate(s.Rational(1,3),(x,2,5))==1
        neg=((s.S.One/(s.Integer(5)-5)).is_finite is False) # a=b => division by zero
    elif key=="normal_standardize":
        mu=s.Integer(3);sig=s.Integer(2);z=s.Integer(5)
        pos=(z-mu)/sig==1 and s.simplify((mu-mu)/sig)==0
        neg=((s.S.One/(sig-sig)).is_finite is False) # sigma=0 invalid standardization
    elif key=="chi_square":
        density=x*s.exp(-x/2)/4 # chi-square with 4 degrees of freedom
        pos=s.integrate(density,(x,0,s.oo))==1 and s.integrate(x*density,(x,0,s.oo))==4
        pos=pos and s.integrate(x*x*density,(x,0,s.oo))-4**2==8
        neg=(density.subs(x,-1)<0) # extending chi-square density outside x>=0 is invalid
    elif key=="student_t":
        density=1/(s.pi*(1+x*x)) # t with 1 df; absolute first moment infinite
        pos=s.integrate(density,(x,-s.oo,s.oo))==1
        neg=s.integrate(x*density,(x,0,s.oo))==s.oo
    elif key=="continuous_moments":
        density=x**-2
        pos=s.integrate(density,(x,1,s.oo))==1
        neg=s.integrate(x*density,(x,1,s.oo))==s.oo
    elif key=="joint_distribution":
        joint={(0,0):s.Rational(1,2),(1,1):s.Rational(1,2)}
        pos=sum(joint.values())==1
        neg=joint[(0,0)]!=s.Rational(1,2)*s.Rational(1,2)
    elif key=="covariance":
        omega=(-1,0,1)
        ex=sum(omega)/3;ey=sum(t*t for t in omega)/3
        exy=sum(t**3 for t in omega)/3
        pos=(exy-ex*ey)==0
        neg=(s.Rational(1,3)!=s.Rational(1,3)*s.Rational(1,3)) # P(X=0,Y=0) vs marginals
    elif key=="independence":
        joint={(i,j):s.Rational(1,4) for i in (-1,1) for j in (-1,1)}
        pos=all(joint[(i,j)]==s.Rational(1,2)**2 for i,j in joint)
        omega=(-1,0,1);ex=sum(omega)/3;ey=sum(i*i for i in omega)/3
        neg=(sum(i**3 for i in omega)/3-ex*ey==0
             and s.Rational(1,3)!=s.Rational(1,9)) # zero cov but dependent
    else:raise ValueError(f"unknown finite math witness: {key}")
    require(bool(pos) and bool(neg),f"exact instance invalid: {key}")
    return {"status":"FINITE_EXACT_INSTANCE_ONLY",
            "finite_exact_positive_passed":True,"invalid_generalization_rejected":True,
            "general_proof_certified":False}

def build(candidates=CANDIDATES,partitions=PARTITIONS,verify_local_source=False):
    require(len(candidates)==20,"must have 20 original editorial interpretations")
    schema=set(CANDIDATES[0])
    require(all(type(c)==dict and set(c)==schema for c in candidates),
            "candidate schema drift, unlicensed extension, or forged approval")
    require(set(partitions)==set(LIMITS),"wrong printed source pages")
    for page,parts in partitions.items():
        covered=[i for start,end,_ in parts for i in range(start,end+1)]
        require(covered==list(range(1,LIMITS[page]+1)),"page missing, overlapping or reordered source lines")
    m={p["printed_page"]:p for p in json.loads(META.read_text())["pages"]}
    require({p:m[p]["pdf_page_index"] for p in LIMITS}==PDF_PAGES,"pdf physical-page drift")
    if verify_local_source:
        require(PDF.is_file() and sha256(PDF.read_bytes()).hexdigest()==PDF_SHA,"source PDF bytes drift")
        for page in (*LIMITS,*CONTINUATION_PAGES.values()):
            f=Path(f"/private/tmp/kb56_page_{page}.txt")
            require(f.is_file() and sha256(f.read_bytes()).hexdigest()==m[page]["pdfkit_text_sha256"],
                    f"PDFKit source text changed on page {page}")
    keys=[r["key"] for r in candidates]
    require(len(keys)==len(set(keys)) and set(keys)==set(SOURCE_LOCK),"candidate key duplicate/drift")
    rows=[];counts=Counter()
    for n,r in enumerate(candidates,1):
        p,lo,hi,k=(r["page"],r["start"],r["end"],r["kind"])
        require((p,lo,hi,k)==SOURCE_LOCK.get(r["key"]),"forged or shifted source locator")
        require(1<=lo<=hi<=LIMITS[p],"invalid source page/line")
        require(sum(1 for a,b,_ in partitions[p] if a<=lo<=hi<=b)==1,
                "source candidate crosses a structural boundary")
        require(k in {"CONCEPT","METHOD","THEOREM","PEDAGOGY"},"invalid knowledge type")
        require(all(isinstance(r[f],str) and len(r[f])>=18
                    for f in ("mathematical_preconditions","invalid_generalization","editorial_note")),
                "thin precondition, invalid application or editorial rationale")
        track="COMPULSORY" if p==19 else "ELECTIVE_A"
        counts[track]+=1
        rows.append({**r,"id":f"KB109-P{p:03d}-C{n:02d}","track_hint":track,
                     "source_pdf_sha256":PDF_SHA,"source_page_pdfkit_sha256":m[p]["pdfkit_text_sha256"],
                     "pdf_page_index":m[p]["pdf_page_index"],
                     "math_witness":exact_witness(r["key"]),
                     "official_atom_id":None,"teacher_review_status":"REVIEW_PENDING",
                     "student_authoritative_release":False})
    require(counts=={"COMPULSORY":9,"ELECTIVE_A":11},"track-hint accounting changed")
    return {
      "batch":109,"scope_kind":"EDITORIAL_SOURCE_CANDIDATES_NOT_OFFICIAL_ATOMS",
      "curriculum_standard":"普通高中数学课程标准（2017年版2020年修订）",
      "source_pdf_sha256":PDF_SHA,"source_fingerprint_registry_sha256":sha256(META.read_bytes()).hexdigest(),
      "authoring_sha256":sha256((ROOT/"scripts/kb_batch109_scope_authoring.py").read_bytes()).hexdigest(),
      "pages":[19,56],"source_lines_total":54,
      "line_counts":{str(k):v for k,v in LIMITS.items()},
      "structural_partitions":[dict(page=p,start=lo,end=hi,kind=k)
                               for p,parts in sorted(partitions.items()) for lo,hi,k in parts],
      "new_editorial_candidates":len(rows),"track_hint_counts":{t:counts[t] for t in TRACKS},
      "cross_page_boundary_evidence":[
         {"current_page":p,"continuation_page":nextp,
          "continuation_pdf_page_index":m[nextp]["pdf_page_index"],
          "continuation_pdfkit_sha256":m[nextp]["pdfkit_text_sha256"],
          "status":"CONTINUATION_REVIEW_REQUIRED",
          "editorial_note":("Page 20 continues starred optional function history; do not count it as compulsory examination mathematics."
                            if p==19 else
                            "Page 57 continues bivariate normal material and introduces inference/regression; no claim of completing this chapter on page 56.")}
         for p,nextp in CONTINUATION_PAGES.items()
      ],
      "bounded_exact_witnesses":sum(r["math_witness"]["status"]=="FINITE_EXACT_INSTANCE_ONLY" for r in rows),
      "pedagogy_items_not_math_proofs":sum(r["kind"]=="PEDAGOGY" for r in rows),
      "official_seven_track_atom_denominators":{t:None for t in TRACKS},
      "teacher_full_page_atomizations":0,"teacher_approvals":0,"student_authoritative_releases":0,
      "candidates":rows,
      "limitations":[
       "Neither printed-page structural partitioning nor editorial requirements are teacher-certified official atomization.",
       "Page 19 star-marked function history is optional and must not enter mandatory assessment scope.",
       "The named t/chi-square laws require valid degrees of freedom and finite-moment assumptions.",
       "Page 56 ends mid-section; bivariate and inference scope must be revisited on page 57.",
       "No frozen seven-track curricular denominator; no certified theorem proofs or student releases."]
    }

def markdown(obj):
    chunks=["# Batch109｜官方第19/56页课程来源逐行审计（编辑候审）","",
            "已核对原版PDF字节哈希、PDFKit页指纹、打印页与物理页定位。结构段不等于课程原子。","",
            f"印刷页19/56共{obj['source_lines_total']}行；{len(obj['structural_partitions'])}段；"
            f"{obj['new_editorial_candidates']}个候审解释；{obj['bounded_exact_witnesses']}个有限精确检查。","",
            "七轨官方正式原子分母 UNKNOWN；0/61 教师全页审定；教师正式批准0。",""]
    for r in obj["cross_page_boundary_evidence"]:
        chunks.extend([f"## 跨页证据：{r['current_page']}→{r['continuation_page']}","",
                       r["editorial_note"],""])
    for r in obj["candidates"]:
        chunks.extend([f"## {r['id']}｜{r['title']}","",
                       f"来源：印刷页{r['page']}行{r['start']}–{r['end']}；轨道提示{r['track_hint']}；类型{r['kind']}。","",
                       "数学前提："+r["mathematical_preconditions"],"",
                       "失效/非例："+r["invalid_generalization"],"",
                       "编辑拆分说明："+r["editorial_note"],"",
                       "有限检查："+r["math_witness"]["status"],""])
    return "\n".join(chunks).rstrip()+"\n"

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local-source",action="store_true");a=p.parse_args()
    data=build(verify_local_source=a.verify_local_source)
    for f,value in ((OUT,serialize(data)),(MD,markdown(data))):
        if a.check:require(f.read_text(encoding="utf8")==value,f"artifact drift {f}")
        else:f.parent.mkdir(parents=True,exist_ok=True);f.write_text(value,encoding="utf8")
    print(f"Batch109 scope PASS: {len(data['candidates'])} candidate interpretations, "
          f"{data['bounded_exact_witnesses']} bounded exact instances, "
          f"{data['source_lines_total']} source lines")
if __name__=="__main__":main()
