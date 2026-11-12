#!/usr/bin/env python3
"""Rebuildable, fail-closed PDFKit source audit for printed pages 20 and 57.

The small exact instances are mathematical witness tests, NOT universal proof.
No copyright PDF text is shipped; local source bytes are checked only on Mac.
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from kb_batch110_source_authoring import CANDIDATES,PARTITIONS
META=ROOT/"curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
PDF=Path.home()/"Library/Caches/stem-mentor-source-review/highschool_math_standard_2020.pdf"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
LIMITS={20:35,57:23}
PDF_PAGES={20:27,57:64}
BOUNDARIES={20:21,57:58}
OUT=ROOT/"docs/evaluation/KB_BATCH110_SCOPE.json"
MD=ROOT/"docs/evaluation/KB_BATCH110_SCOPE.md"
LOCK={r["key"]:(r["page"],r["start"],r["end"],r["kind"]) for r in CANDIDATES}
PEDAGOGY={"optional_history","power_exp_log_theme","log_graph_continuation",
          "regression_application","elective_b_boundary","elective_b_calculus"}

def require(condition,msg):
    if not condition: raise ValueError(msg)

def serialize(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"

def exact_witness(key):
    """A positive instance plus a failure of invalid inference, using exact rational arithmetic."""
    if key in PEDAGOGY:
        return dict(status="PEDAGOGY_NOT_A_MATH_PROOF",finite_exact_positive_passed=False,
                    invalid_generalization_rejected=False,general_proof_certified=False)
    r=sp.Rational
    if key=="power_functions":
        pos=sp.sqrt(4)==2 and sp.Rational(1,2)**-1==2
        neg=sp.zoo==1/sp.Integer(0)
    elif key=="rational_exponents":
        pos=sp.Pow(16,r(3,4))==8
        neg=(sp.sqrt(-4).is_real is False)
    elif key=="real_exponents":
        pos=sp.simplify(2**sp.sqrt(2)*2**(3-sp.sqrt(2)))==8
        neg=(sp.sqrt(-2).is_real is False)
    elif key=="exp_function":
        pos=sp.Pow(3,0)==1 and sp.Pow(3,2)==9
        neg=sp.Pow(1,0)==sp.Pow(1,3)
    elif key=="exp_monotonic":
        pos=sp.Pow(2,3)>sp.Pow(2,1)
        neg=sp.Pow(r(1,2),3)<sp.Pow(r(1,2),1)
    elif key=="log_properties":
        pos=sp.log(8,2)==3 and sp.log(100,10)==2
        neg=sp.log(2+8,2)!=sp.log(2,2)+sp.log(8,2)
    elif key=="bivariate_normal":
        good=sp.Matrix([[1,r(1,2)],[r(1,2),1]])
        bad=sp.Matrix([[1,2],[2,1]])
        pos=good.det()==r(3,4)
        neg=bad.det()<0
    elif key=="moment_estimation":
        p=r(2,3);sample=(1,1,0)
        pos=r(sum(sample),len(sample))==p
        # Different distributions share mean 1, but have different variances.
        outcomes=((0,r(1,2)),(2,r(1,2)))
        mixture_mean=sum(v*w for v,w in outcomes)
        mixture_variance=sum((v-mixture_mean)**2*w for v,w in outcomes)
        neg=(mixture_mean==1 and mixture_variance==1 and
             (r(1)-r(1))**2==0)
    elif key=="maximum_likelihood":
        p=sp.symbols("p",real=True)
        L=p**3
        pos=L.subs(p,1)==1 and L.subs(p,r(1,2))==r(1,8)
        neg=sp.solveset(sp.diff(L,p),p,domain=sp.Interval.open(0,1))==sp.EmptySet
    elif key=="test_logic":
        pos=sp.binomial(10,10)*r(1,2)**10==r(1,1024)
        # Same one-sided p-value, different posterior probabilities depending on prior.
        # Under alternative H1: P(heads)=1, ten heads has likelihood 1.
        lh0=r(1,1024); lh1=r(1)
        post1=(r(1,2)*lh0)/(r(1,2)*lh0+r(1,2)*lh1)
        post2=(r(1,10)*lh0)/(r(1,10)*lh0+r(9,10)*lh1)
        neg=post1!=post2 and post1!=lh0 and post2!=lh0
    elif key=="normal_mean_testing":
        data=(1,2,3,4); n=4;bar=r(sum(data),n);mu0=r(2)
        s2=sum((r(v)-bar)**2 for v in data)/(n-1)
        z=(bar-mu0)/(r(2)/sp.sqrt(n))  # known sigma=2
        t=(bar-mu0)/(sp.sqrt(s2)/sp.sqrt(n)) # sample s, df=3
        pos=bar==r(5,2) and z==r(1,2) and s2==r(5,3)
        neg=sp.simplify(t-z)!=0 # Z and t are not interchangeable without premises
    elif key=="goodness_of_fit":
        pos=(12-10)**2/r(10)+(8-10)**2/r(10)==r(4,5)
        # Formula remains computable for small positive expectation, but
        # Pearson asymptotic chi-square assumptions are not thereby certified.
        small_expected=(r(1,2),r(19,2))
        bad_formula=sum((observed-e)**2/e for observed,e in
                        zip((1,9),small_expected))
        neg=small_expected[0]<5 and bool(sp.sympify(bad_formula).is_finite)
    elif key=="linear_regression":
        # Explicit confounded toy structural model: X=Z, Y=Z.
        # Observations show perfect slope 1, but intervening on X while
        # holding Z fixed does not change Y; no causal effect of X on Y.
        zs=(-1,0,1)
        xs=zs;ys=zs
        pos=sum(x*y for x,y in zip(xs,ys))==sum(x*x for x in xs)
        z_fixed=1; intervention_x=9
        observed_regression_prediction=intervention_x
        actual_interventional_y=z_fixed
        neg=(observed_regression_prediction!=actual_interventional_y)
    elif key=="least_squares":
        xs=(0,1,2);ys=(1,3,5)
        xbar=r(sum(xs),3);ybar=r(sum(ys),3)
        sxx=sum((x-xbar)**2 for x in xs)
        sxy=sum((x-xbar)*(y-ybar) for x,y in zip(xs,ys))
        pos=sxx==2 and sxy/sxx==2 and ybar-2*xbar==1
        neg=sum((x-1)**2 for x in (1,1,1))==0
    else: raise ValueError("unrecognized exact witness "+key)
    require(bool(pos) and bool(neg),"invalid exact witness "+key)
    return dict(status="FINITE_EXACT_INSTANCE_ONLY",finite_exact_positive_passed=True,
                invalid_generalization_rejected=True,general_proof_certified=False)

def track(r):
    if r["page"]==20: return "COMPULSORY"
    return "ELECTIVE_A" if r["start"]<=15 else "ELECTIVE_B"

def build(candidates=CANDIDATES,partitions=PARTITIONS,verify_local_source=False):
    require(len(candidates)==20,"expected 20 substantive source interpretations")
    require(len(LOCK)==len(CANDIDATES),"duplicate original candidate key")
    require(set(partitions)==set(LIMITS),"source page set drift")
    require(all(isinstance(r,dict) and set(r)==set(CANDIDATES[0]) for r in candidates),
            "schema drift or unauthorised status field")
    for p,segs in partitions.items():
        coverage=[i for lo,hi,_ in segs for i in range(lo,hi+1)]
        require(coverage==list(range(1,LIMITS[p]+1)),"missing/overlapping/out-of-order line")
    m={x["printed_page"]:x for x in json.loads(META.read_text(encoding="utf8"))["pages"]}
    require({p:m[p]["pdf_page_index"] for p in LIMITS}==PDF_PAGES,"PDF page index drift")
    if verify_local_source:
        require(PDF.is_file() and sha256(PDF.read_bytes()).hexdigest()==PDF_SHA,"PDF SHA drift")
        for p in (*LIMITS,*BOUNDARIES.values()):
            fp=Path(f"/private/tmp/kb56_page_{p}.txt")
            require(fp.is_file() and sha256(fp.read_bytes()).hexdigest()==m[p]["pdfkit_text_sha256"],
                    f"PDFKit page {p} SHA drift or unavailable cache")
            if p in LIMITS:
                require(len(fp.read_text(encoding="utf8").splitlines())==LIMITS[p],
                        f"PDFKit line count drift on {p}")
    keys=[x["key"] for x in candidates]
    require(len(set(keys))==20 and set(keys)==set(LOCK),"source candidate IDs drift")
    out=[];counts=Counter()
    for n,r in enumerate(candidates,1):
        p,lo,hi,k=r["page"],r["start"],r["end"],r["kind"]
        require(LOCK[r["key"]]==(p,lo,hi,k),"source candidate locator changed")
        require(1<=lo<=hi<=LIMITS[p],"line out of bounds")
        require(sum(1 for a,b,_ in partitions[p] if a<=lo<=hi<=b)==1,
                "source candidate crosses source structure boundary")
        require(k in {"THEOREM","CONCEPT","METHOD","PEDAGOGY"},"invalid type")
        require((r["key"] in PEDAGOGY)==(k=="PEDAGOGY"),"proof/pedagogy type drift")
        require(all(isinstance(r[f],str) and len(r[f])>=18 for f in
                ("mathematical_preconditions","invalid_generalization","editorial_note")),
                "thin assumptions or missing negative example")
        t=track(r)
        require(not(p==57 and lo<=15<hi),"candidate crosses A/B track boundary")
        counts[t]+=1
        out.append({**r,"id":f"KB110-P{p:03d}-C{n:02d}","track_hint":t,
                    "source_pdf_sha256":PDF_SHA,
                    "source_page_pdfkit_sha256":m[p]["pdfkit_text_sha256"],
                    "pdf_page_index":m[p]["pdf_page_index"],
                    "math_witness":exact_witness(r["key"]),
                    "official_atom_id":None,"review_status":"REVIEW_PENDING",
                    "teacher_reviewer":None,"student_authoritative_release":False})
    require(counts=={"COMPULSORY":9,"ELECTIVE_A":9,"ELECTIVE_B":2},
            "candidate track account drift")
    return dict(batch=110,scope_kind="PROVISIONAL_EDITORIAL_SOURCE_CANDIDATES",
                curriculum_standard="普通高中数学课程标准（2017年版2020年修订）",
                source_pdf_sha256=PDF_SHA,source_registry_sha256=sha256(META.read_bytes()).hexdigest(),
                author_sha256=sha256((ROOT/"scripts/kb_batch110_source_authoring.py").read_bytes()).hexdigest(),
                pages=sorted(LIMITS),source_lines_total=sum(LIMITS.values()),
                line_counts={str(k):v for k,v in LIMITS.items()},
                structural_partitions=[dict(page=p,start=a,end=b,kind=k)
                    for p,ss in sorted(partitions.items()) for a,b,k in ss],
                candidate_counts_by_track={t:counts[t] for t in TRACKS},
                candidates=out,new_editorial_candidates=len(out),
                finite_exact_witnesses=sum(x["math_witness"]["status"]=="FINITE_EXACT_INSTANCE_ONLY" for x in out),
                pedagogy_not_math_proofs=sum(x["kind"]=="PEDAGOGY" for x in out),
                cross_page_continuations=[dict(from_page=p,to_page=q,
                    next_pdfkit_sha256=m[q]["pdfkit_text_sha256"],status="NOT_ATOMIZED_BY_TEACHER")
                    for p,q in BOUNDARIES.items()],
                official_seven_track_atom_denominators={t:None for t in TRACKS},
                teacher_full_page_atomizations=0,teacher_approvals=0,
                student_authoritative_releases=0,
                remaining_known_debt=dict(unreviewed_prior_prerequisite_labels=172,
                   uncertified_prior_proof_steps=538,unresolved_prior_conflicts=10),
                limitations=[
                  "Source-partition audit is not teacher-certified atomization or a global denominator.",
                  "Page 20 contains explicitly optional star-marked function history.",
                  "Page 57 switches from elective A to elective B at printed line 16.",
                  "No source copyright passages are committed; only coordinates and SHA evidence.",
                  "Exact witnesses are finite cases, not proof certificates or teacher approval."
                ])

def markdown(obj):
    out=["# Batch110｜官方课标印刷20/57页来源与范围审计（候审）","",
        f"本批{obj['source_lines_total']}条PDFKit来源行，{len(obj['structural_partitions'])}个结构段，"
        f"{obj['new_editorial_candidates']}个原创课程候选；数学有限精确见证{obj['finite_exact_witnesses']}组。","",
        "正式七轨课标原子分母仍为 UNKNOWN；没有教师审批或学生权威发布。","",
        "20页星号函数史仅选学；57页第16行起切换选修B，不可混入A轨。",""]
    for row in obj["candidates"]:
        out+=["## "+row["id"]+"｜"+row["title"],"",
             f"来源：印刷页{row['page']}行{row['start']}–{row['end']}；轨道{row['track_hint']}；知识类型{row['kind']}。","",
             "**前提：** "+row["mathematical_preconditions"],"",
             "**错误泛化：** "+row["invalid_generalization"],"",
             "**拆分理由：** "+row["editorial_note"],"",
             "证据等级："+row["math_witness"]["status"],""]
    return "\n".join(out).rstrip()+"\n"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local-source",action="store_true")
    a=p.parse_args();data=build(verify_local_source=a.verify_local_source)
    for path,content in ((OUT,serialize(data)),(MD,markdown(data))):
        if a.check:require(path.read_text(encoding="utf8")==content,"artifact drift "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding="utf8")
    print("Batch110 scope PASS",len(data["candidates"]),data["finite_exact_witnesses"],
          data["candidate_counts_by_track"])
if __name__=="__main__":main()
