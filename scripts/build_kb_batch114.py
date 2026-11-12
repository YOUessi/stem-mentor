#!/usr/bin/env python3
"""Batch114: copyright-safe source anchors + authored lessons + exact finite checks.
Only Mac may use the pinned official PDF; CI checks stored fingerprints and artifacts.
Official atomic denominators are UNKNOWN until real teacher atomization.
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from fractions import Fraction
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch114_source import CANDIDATES,PARTITIONS
from kb_batch114_authoring import UNITS
from app.deep_knowledge import DeepLesson, DEEP_DIR, curriculum
PDF=Path.home()/"Library/Caches/stem-mentor-source-review/highschool_math_standard_2020.pdf"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
REGISTRY=ROOT/"curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
LIMITS={24:29,61:26}
PDF_INDICES={24:31,61:68}
IMMUTABLE={r["key"]:(r["page"],r["start"],r["end"],r["kind"]) for r in CANDIDATES}
NONMATH={"history_activity","statistics_overview"}
SRC=ROOT/"docs/evaluation/KB_BATCH114_SCOPE.json"
PACK=DEEP_DIR/"batch114_functions_statistics.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH114_AUDIT.json"
COVER=ROOT/"docs/evaluation/KB_BATCH114_COVERAGE.json"
MD=ROOT/"docs/evaluation/KB_BATCH114_LESSONS.md"

def need(test,message):
    if not test: raise ValueError(message)
def dumps(obj):return json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n"
def h(path):return sha256(path.read_bytes()).hexdigest()
def track(row):return "COMPULSORY" if row["page"]==24 else "ELECTIVE_B"

def witness(key):
    if key in NONMATH:return dict(status="PEDAGOGY_NOT_MATH_PROOF",positive=False,boundary=False,general_proof_certified=False)
    R=sp.Rational; x=sp.symbols("x",real=True)
    checks={
      "log_inverse":(sp.log(8,2)==3,sp.log(-1,2).is_real is False),
      "circle_trig":(sp.sin(sp.pi/2)==1,sp.sin(2*sp.pi)==0),
      "cos_difference":(sp.trigsimp(sp.cos(x-x)-sp.cos(x)*sp.cos(x)-sp.sin(x)**2)==0,sp.cos(0)!=0),
      "model_interpretation":(sp.Integer(2)**3==8,sp.Integer(2)**4!=10),
      "function_plot":(R(1,2)**2<R(3,4)**2,sp.sin(sp.pi)==0),
      "numeric_solver":(R(5,4)**2-2<0,R(3,2)**2-2>0),
      "representation":(sp.expand((x-1)*(x-2)*x).subs(x,2)==0,sp.expand((x-1)*(x-2)*x).subs(x,3)!=0),
      "monotonicity":(R(1,2)<R(3,4),-(R(3,4)) < -R(1,2)),
      "root_graph":(sp.Integer(1)**2-2<0,sp.Integer(2)**2-2>0),
      "regression_overview":(sp.Integer(1)+sp.Integer(2)==3,sp.Integer(2)**3!=10),
      "clustering_overview":(abs(R(2)-R(3))==1,abs(R(2)-R(5))!=1),
      "design_overview":(R(1)+R(1)==2,R(2)*R(3)!=R(2)+R(3)),
      "continuous_density":(sp.integrate(2*x,(x,0,1))==1,sp.integrate(2*x,(x,R(1,2),1))==R(3,4)),
      "normal_standardize":(sp.sqrt(9)==3,R(5-2,3)==1),
      "chi_t_moments":(R(4,4-2)==2,sp.Integer(2)-2==0),
      "uniform_moments":(sp.integrate(x,(x,2,8))/6==5,sp.integrate((x-5)**2,(x,2,8))/6==3),
      "joint_marginal":(sum([R(1,4)]*4)==1,sum([R(1,4)]*2)==R(1,2)),
      "covariance_independence":(sum([R(-1,3),R(0),R(1,3)])==0,R(1,3)!=R(1,9)),
      "parameter_inference":(R(3,100)<R(5,100),R(3,100)!=R(97,100))
    }
    need(key in checks,"finite witness missing "+key)
    a,b=checks[key]
    need(bool(a) and bool(b),"finite witness failed "+key)
    return dict(status="FINITE_EXACT_INSTANCES_ONLY",positive=True,boundary=True,general_proof_certified=False)

def source(candidates=CANDIDATES,partitions=PARTITIONS,verify_local_source=False):
    need(len(IMMUTABLE)==21 and len(candidates)==21,"candidate count or duplicate ID")
    need(set(partitions)==set(LIMITS),"wrong source page set")
    for p,regions in partitions.items():
        need([x for a,b,_ in regions for x in range(a,b+1)]==list(range(1,LIMITS[p]+1)),"missing/overlapping PDFKit lines")
    reg=json.loads(REGISTRY.read_text())
    need(reg["official_pdf_sha256"]==PDF_SHA,"source PDF SHA changed")
    pages={z["printed_page"]:z for z in reg["pages"]}
    need({p:pages[p]["pdf_page_index"] for p in LIMITS}==PDF_INDICES,"source index changed")
    if verify_local_source:
        need(PDF.is_file() and h(PDF)==PDF_SHA,"pinned source PDF missing or changed")
        for p in LIMITS:
            f=Path(f"/private/tmp/kb56_page_{p}.txt")
            need(f.is_file() and h(f)==pages[p]["pdfkit_text_sha256"],f"PDFKit source line SHA drift {p}")
            need(len(f.read_text().splitlines())==LIMITS[p],"PDFKit line-count changed")
    cnt=Counter();xs=[]
    for i,row in enumerate(candidates,1):
        need(set(row)==set(CANDIDATES[0]),"untrusted source extra or missing field")
        k=row["key"]
        need(k in IMMUTABLE and IMMUTABLE[k]==(row["page"],row["start"],row["end"],row["kind"]),"source locator/type mutation")
        p,lo,hi=row["page"],row["start"],row["end"]
        need(1<=lo<=hi<=LIMITS[p],"line out of bounds")
        need(any(a<=lo<=hi<=b for a,b,_ in partitions[p]),"locator straddles structural partitions")
        need(row["kind"] in ("THEOREM","CONCEPT","METHOD","PEDAGOGY"),"illegal kind")
        need((k in NONMATH)==(row["kind"]=="PEDAGOGY"),"pedagogy falsely certified as maths")
        need(all(len(row[f])>=18 for f in ("mathematical_preconditions","invalid_generalization","editorial_note")),"thin source")
        t=track(row);cnt[t]+=1
        xs.append({**row,"id":f"KB114-P{p:03d}-C{i:02d}",
          "track_hint":t,"source_pdf_sha256":PDF_SHA,
          "source_page_pdfkit_sha256":pages[p]["pdfkit_text_sha256"],
          "pdf_page_index":pages[p]["pdf_page_index"],
          "math_witness":witness(k),"official_atom_id":None,
          "review_status":"REVIEW_PENDING","teacher_reviewer":None,
          "student_authoritative_release":False})
    need(cnt=={"COMPULSORY":10,"ELECTIVE_B":11},"candidate seven-track mismatch")
    return dict(batch=114,scope_kind="EDITORIAL_CANDIDATES_NOT_OFFICIAL_ATOMS",
      curriculum_standard="普通高中数学课程标准（2017年版2020年修订）",
      source_pdf_sha256=PDF_SHA,source_registry_sha256=h(REGISTRY),
      source_author_sha256=h(ROOT/"scripts/kb_batch114_source.py"),
      pages=[24,61],line_counts={str(k):v for k,v in LIMITS.items()},
      source_lines_total=sum(LIMITS.values()),source_candidate_counts_by_track={t:cnt[t] for t in TRACKS},
      structural_partitions=[dict(page=p,start=a,end=b,kind=k) for p,v in sorted(partitions.items()) for a,b,k in v],
      candidates=xs,editorial_candidate_count=len(xs),
      finite_exact_witnesses=sum(z["math_witness"]["positive"] for z in xs),
      official_seven_track_atom_denominators={t:None for t in TRACKS},
      teacher_full_page_atomizations=0,teacher_approvals=0,student_authoritative_releases=0,
      limitations=["PDFKit行含页脚、目录与教学提示，非数学原子分母。",
        "官方七轨分母均未知，来源候选不等于认证知识单元。",
        "有限见证不等于一般命题证明；教师审批与学生权威发布均为0。"])

def lessons(units=UNITS,scope=None):
    if scope is None: scope=source()
    need(len(UNITS)==8 and len(units)==8,"eight original teacher drafts required")
    bykey={r["key"]:r for r in scope["candidates"]}
    curr={r["id"]:r for r in curriculum()}
    historical=[]
    for path in sorted(DEEP_DIR.glob("batch*.json")):
        m=re.match(r"batch(\d+)",path.name)
        if m and int(m.group(1))>=114:continue
        historical+=json.loads(path.read_text())
    oldids=[r["id"] for r in historical]
    need(len(set(oldids))==len(oldids),"historical knowledge IDs duplicated")
    docs=[];links=[]
    for i,u in enumerate(units,1):
        need(set(u)==set(UNITS[0]),"lesson keys mutated")
        need(u["kind"] in ("concept","method","theorem"),"invalid lesson type")
        need(u["source_key"] in bykey and u["curriculum_id"] in curr,"orphan source/curriculum link")
        need(len(u["statement"])>=55 and len(u["assumptions"])>=2 and len(u["notation"])>=2 and len(u["prereqs"])>=2,"thin lesson")
        need(len(u["reasoning"])>=3 and len(u["negative"])==3,"missing reasoning/negative")
        need(len(u["examples"])==2 and all(len(e["steps"])>=2 and len(e["check"])>=15 for e in u["examples"]),"missing worked examples")
        need(len(u["hints"])==3 and len(set(u["hints"]))==3,"hint ladder incomplete")
        need(len(u["near"])>=25 and len(u["far"])>=25,"transfer missing")
        if u["kind"]=="theorem":
            need(all(len(r)==2 and all(len(v)>=20 for v in r) for r in u["reasoning"]),"theorem reason missing")
        else: need(all(len(r)>=20 for r in u["reasoning"]),"rationale missing")
        src=bykey[u["source_key"]];expected="COMPULSORY" if i<=4 else "ELECTIVE_B"
        need(src["track_hint"]==expected,"lesson source track mismatch")
        need(curr[u["curriculum_id"]]["level"]==("必修" if i<=4 else "选修拓展"),
             "engineering level not aligned to editorial source")
        need(src["math_witness"]["positive"],"source no finite mathematical witness")
        lid=f"math.hs.batch114.{i:02d}"
        need(lid not in oldids,"lesson ID collision")
        doc=dict(id=lid,curriculum_ids=[u["curriculum_id"]],kind=u["kind"],title=u["title"],
          version="1.0.0",notation=u["notation"],prerequisites=u["prereqs"],
          prerequisite_lesson_ids=[],definition=u["statement"] if u["kind"]=="concept" else None,
          statement=u["statement"],assumptions=u["assumptions"],
          proof_steps=[dict(claim=x,reason=y) for x,y in u["reasoning"]] if u["kind"]=="theorem" else [],
          rationale_steps=u["reasoning"] if u["kind"]!="theorem" else [],
          boundaries=u["assumptions"],
          counterexamples=[dict(false_claim=u["negative"][0],example=u["negative"][1],explanation=u["negative"][2])],
          misconceptions=[dict(error=u["negative"][0],why_wrong=u["negative"][2],
            repair_question="请确定哪项定义域、独立性或除零前提被遗漏，并构造反例。")],
          worked_examples=u["examples"],hint_ladder=u["hints"],transfer=dict(near=u["near"],far=u["far"]),
          provenance=dict(kind="PROJECT_AUTHORED",permission="PROJECT_AUTHORED",
            curriculum_standard="普通高中数学课程标准（2017年版2020年修订）",
            standard_url="https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf",
            author_role="PROJECT_AUTHOR"),
          review=dict(status="REVIEW_PENDING",reviewer_id=None,reviewed_at=None,review_record=None),
          teacher_solution_visibility="TEACHER_ONLY")
        DeepLesson.model_validate(doc)
        docs.append(doc)
        links.append(dict(lesson_id=lid,source_candidate_id=src["id"],source_key=src["key"],
            source_printed_page=src["page"],source_track_hint=expected,
            engineering_curriculum_id=u["curriculum_id"],official_atom_id=None,
            teacher_approved=False,general_proof_certified=False))
    proofsteps=sum(len(z["proof_steps"]) for z in docs)
    audit=dict(batch=114,review_status="REVIEW_PENDING",visibility="TEACHER_ONLY",
      new_deep_drafts=len(docs),new_teacher_worked_examples=2*len(docs),
      new_hint_levels=3*len(docs),new_transfer_tasks=2*len(docs),
      new_counterexamples=len(docs),new_uncertified_proof_steps=proofsteps,
      lesson_kind_counts=dict(Counter(z["kind"] for z in docs)),
      prior_deep_drafts=len(historical),total_deep_drafts=len(historical)+len(docs),
      source_links=links,teacher_approvals=0,student_authoritative_releases=0,
      formal_proof_certificates=0,student_free_text_proof_certificates=0,
      author_sha256=h(ROOT/"scripts/kb_batch114_authoring.py"),
      scope_sha256=sha256(dumps(scope).encode()).hexdigest())
    return docs,audit

def coverage(scope=None,ds=None):
    if scope is None:scope=source()
    if ds is None:ds=lessons(scope=scope)[0]
    reg=json.loads(REGISTRY.read_text())
    pages=reg["pages"]
    need({p["printed_page"] for p in pages}==set(range(13,74)),"61-page pinned registry incomplete")
    # Auditable page denominator is known (61); curriculum *atom* denominator is not.
    prior={}
    for file in sorted((ROOT/"docs/evaluation").glob("KB_BATCH*_SCOPE.json")):
        if file==SRC:continue
        try:
            ob=json.loads(file.read_text())
            if ob.get("source_pdf_sha256")!=PDF_SHA or not isinstance(ob.get("line_counts"),dict):continue
            for p in map(int,ob["line_counts"]):
                need(p not in prior,"duplicate independent prior source page")
                prior[p]=file.name
        except (ValueError,KeyError,TypeError):
            raise
    for p in scope["pages"]:need(p not in prior,"current page already present in previous source audit")
    found={**prior,**{p:"KB_BATCH114_SCOPE.json" for p in scope["pages"]}}
    rows=[]
    for p in pages:
        n=p["printed_page"]
        rows.append(dict(printed_page=n,pdf_page_index=p["pdf_page_index"],
           source_pdfkit_sha256=p["pdfkit_text_sha256"],source_structural_audit_file=found.get(n),
           source_structure_candidate_review=n in found,
           teacher_verified_atomization=False,teacher_review_record=None,
           official_math_atoms=None,approved_math_atoms=0,official_coverage=None))
    need(len(rows)==61 and all(not x["teacher_verified_atomization"] for x in rows),"false teacher atomization")
    return dict(batch=114,official_source_pdf_pages=61,
       source_structure_candidate_reviewed_pages=len(found),
       source_structure_reviewed_pages=sorted(found),
       source_structure_unreviewed_pages=sorted(set(range(13,74))-set(found)),
       teacher_verified_atomized_pages=0,
       per_page_denominator_status=rows,
       seven_track_official_atom_denominator={t:None for t in TRACKS},
       seven_track_certified_coverage={t:None for t in TRACKS},
       seven_track_editorial_candidate_counts_current_batch=scope["source_candidate_counts_by_track"],
       newly_authored_drafts=len(ds),teacher_approved_drafts=0,
       historical_unreviewed_prerequisite_edges=172,
       historical_uncertified_proof_steps=538,
       historical_unresolved_math_conflicts=10,
       limitations=["61为印刷页审计分母，不是正式原子分母。",
          "来源结构候审不代表整页正式课程原子化，全部教师审核仍为0。",
          "审查状态与学生自由解题验证状态严格隔离。"])

def markdown(scope,docs,audit,cover):
    out=["# Batch114｜函数与应用统计：24/61页来源候审及原创教学讲义","",
      "PDF原文不收入Git；教师审校与一般定理形式证明均未完成。","",
      f"源结构复核：本批{scope['source_lines_total']}行，{scope['editorial_candidate_count']}个编辑候选，"
      f"{scope['finite_exact_witnesses']}个有限数学见证；已标记来源页{cover['source_structure_candidate_reviewed_pages']}，"
      f"剩余来源页{cover['source_structure_unreviewed_pages']}。官方七轨原子分母全部UNKNOWN。","",
      "## 8份教师候审讲义（非学生权威知识）",""]
    for d,link in zip(docs,audit["source_links"]):
        out += [f"### {d['id']}｜{d['title']}","",
          f"来源：{link['source_candidate_id']}；印刷页{link['source_printed_page']}；轨道{link['source_track_hint']}；工程ID{link['engineering_curriculum_id']}。","",
          "**陈述/定义**："+d["statement"],"","**符号**："+"；".join(d["notation"]),"",
          "**先修**："+"；".join(d["prerequisites"]),"",
          "**全部前提**："+"；".join(d["assumptions"]),"",]
        for j,p in enumerate(d["proof_steps"],1):
            out += [f"**待审证明步骤{j}**：{p['claim']}","依据："+p["reason"],""]
        for j,r in enumerate(d["rationale_steps"],1):out += [f"**理由/讲解{j}**：{r}",""]
        bad=d["counterexamples"][0]
        out += ["**不合法的泛化**："+bad["false_claim"],"",
                "**具体反例**："+bad["example"],"","**错误根源**："+bad["explanation"],""]
        for j,e in enumerate(d["worked_examples"],1):
            out += [f"**教师例题{j}**：{e['question']}",""]
            for i,s in enumerate(e["steps"],1):out += [f"{i}. {s}"]
            out += ["","答案："+e["answer"],"","独立核对："+e["check"],""]
        out += ["**不剧透三级提示**："+"；".join(d["hint_ladder"]),"",
                "**近迁移**："+d["transfer"]["near"],"",
                "**远迁移**："+d["transfer"]["far"],""]
    out += ["## 审核界限","",
      "教学草案结构字段齐全并不意味着教师已经审校。所有定理的证明步骤仍待人工审查。",
      "教师批准0，形式证明证书0，学生独立作答自动批准0，学生权威检索放行0。",""]
    return "\n".join(out)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--verify-local-source",action="store_true")
    a=parser.parse_args()
    sc=source(verify_local_source=a.verify_local_source)
    ds,au=lessons(scope=sc)
    co=coverage(scope=sc,ds=ds)
    for path,txt in ((SRC,dumps(sc)),(PACK,dumps(ds)),(AUDIT,dumps(au)),(COVER,dumps(co)),(MD,markdown(sc,ds,au,co))):
        if a.check:need(path.read_text()==txt,"generated artifact drift: "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(txt,encoding="utf8")
    print(f"Batch114 OK: {len(sc['candidates'])} source candidates, {len(ds)} lessons, "
          f"{au['new_uncertified_proof_steps']} pending proof steps, "
          f"{co['source_structure_candidate_reviewed_pages']}/61 provisional page source audits; "
          "all 7 atom denominators UNKNOWN")
if __name__=="__main__":main()
