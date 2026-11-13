#!/usr/bin/env python3
"""Rebuildable K00/K01/K07/K08 audit: printed 22/59, eight original lessons.

The PDF and raw extracted text remain ONLY on the authorized Mac. GitHub holds
SHA/line provenance, original interpretations, finite witnesses and draft lessons.
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter
from hashlib import sha256
from pathlib import Path
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch112_source import CANDIDATES,PARTITIONS
from kb_batch112_lesson_authoring import UNITS
from app.deep_knowledge import DEEP_DIR,DeepLesson,curriculum
PDF=Path.home()/"Library/Caches/stem-mentor-source-review/highschool_math_standard_2020.pdf"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
REGISTRY=ROOT/"curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
LIMITS={22:31,59:28}
INDICES={22:29,59:66}
BOUNDARIES={22:23,59:60}
LOCK={r["key"]:(r["page"],r["start"],r["end"],r["kind"]) for r in CANDIDATES}
PEDAGOGY={"function_overview","vector_overview"}
SOURCE_OUT=ROOT/"docs/evaluation/KB_BATCH112_SCOPE.json"
PACK=DEEP_DIR/"batch112_trig_limits.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH112_AUDIT.json"
COVER=ROOT/"docs/evaluation/KB_BATCH112_COVERAGE.json"
MD=ROOT/"docs/evaluation/KB_BATCH112_LESSONS.md"
DEPENDENCIES={2:[1],5:[4]}

def need(ok,message):
    if not ok:raise ValueError(message)
def dump(obj):
    return json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
def track(row):
    return "COMPULSORY" if row["page"]==22 else "ELECTIVE_B"

def witness(key):
    """Two distinct finite positive and boundary examples. No universal theorem certification."""
    if key in PEDAGOGY:
        return dict(status="PEDAGOGY_NOT_MATH_PROOF",finite_positive=False,
                    finite_boundary=False,general_proof_certified=False)
    P=sp.pi
    R=sp.Rational
    x,y=sp.symbols("x y",real=True)
    cases={
      "sin_model":lambda:(sp.sin(2*(P/3)+P/6)==sp.sin(5*P/6),
                            sp.sin(P/3)==sp.sin(P/3+2*P)),
      "same_angle":lambda:(sp.simplify(sp.sin(P/5)**2+sp.cos(P/5)**2-1)==0,sp.cos(P/2)==0),
      "tangent_ratio":lambda:(sp.tan(P/4)==sp.sin(P/4)/sp.cos(P/4),sp.cos(P/2)==0),
      "cos_diff":lambda:(sp.cos(P/3-P/6)==sp.cos(P/3)*sp.cos(P/6)+sp.sin(P/3)*sp.sin(P/6),
                             sp.cos(P/3-P/3)!=sp.cos(P/3)**2-sp.sin(P/3)**2),
      "addition":lambda:(sp.cos(P/3+P/6)==sp.cos(P/3)*sp.cos(P/6)-sp.sin(P/3)*sp.sin(P/6),
                            sp.cos(P/3+P/3)!=sp.cos(P/3)**2+sp.sin(P/3)**2),
      "double":lambda:(sp.cos(2*P/6)==1-2*sp.sin(P/6)**2,
                          sp.cos(2*P/6)!=sp.cos(P/6)**2),
      "sum_product":lambda:(2*sp.sin(P/3)*sp.cos(P/6)==sp.sin(P/2)+sp.sin(P/6),
                               2*sp.sin(P/3)*sp.cos(P/6)!=sp.sin(P/2)),
      "trig_modelling":lambda:(sp.sin(P/4+2*P)==sp.sin(P/4),
                                  sp.sin(P/4+P)!=sp.sin(P/4)),
      "bisection":lambda:(sp.Integer(1)**2-2<0 and sp.Integer(2)**2-2>0,
                             (R(5,4)**2-2)<0 and (R(3,2)**2-2)>0),
      "integral_concept":lambda:(sp.integrate(x,(x,0,1))==R(1,2),
                                     sp.integrate(x,(x,-1,1))==0),
      "riemann_sum":lambda:(sp.summation(sp.Symbol("k"),(sp.Symbol("k"),1,4))/16==R(5,8),
                                R(5,8)!=R(1,2)),
      "ftc":lambda:(sp.integrate(2*x,(x,1,3))==3**2-1**2,
                        sp.integrate(3*x*x,(x,2,0))==-8),
      "volume_area":lambda:(sp.integrate(x,(x,0,2))==2,
                                 sp.integrate(x,(x,-1,1))==0),
      "bivariate":lambda:((x*y).subs({x:2,y:3})==6,(x*y).subs({x:0,y:2})==0),
      "partial":lambda:(sp.diff(x*x*y+3*y*y,x).subs({x:2,y:1})==4,
                            sp.diff(x*x*y+3*y*y,y).subs({x:2,y:1})==10),
      "stationary":lambda:(sp.diff(x*x-y*y,x).subs({x:0,y:0})==0,
                                (x*x-y*y).subs({x:1,y:0})>0 and (x*x-y*y).subs({x:0,y:1})<0),
      "polygon":lambda:(3*2-2*0==6,3*0-2*1==-2),
      "quadratic_region":lambda:((x*x+y*y).subs({x:0,y:0})==0,
                                       (x*x+y*y).subs({x:1,y:0})==1),
    }
    need(key in cases,"missing finite witness: "+key)
    a,b=cases[key]()
    need(bool(a) and bool(b),"finite math witness failed: "+key)
    return dict(status="FINITE_EXACT_OR_BOUNDED_INSTANCE_ONLY",finite_positive=True,
                finite_boundary=True,general_proof_certified=False)

def source(candidates=CANDIDATES,partitions=PARTITIONS,verify_local_source=False):
    need(len(candidates)==20 and len(LOCK)==20 and len(set(LOCK))==20,
         "source candidate/ID cardinality drift")
    need(set(partitions)==set(LIMITS),"source page set drift")
    for page,spans in partitions.items():
        ranges=[n for a,b,_ in spans for n in range(a,b+1)]
        need(ranges==list(range(1,LIMITS[page]+1)),f"missing/overlapping line on {page}")
    registry=json.loads(REGISTRY.read_text(encoding="utf8"))
    need(registry["official_pdf_sha256"]==PDF_SHA,"official PDF SHA mismatch")
    pages={r["printed_page"]:r for r in registry["pages"]}
    need({p:pages[p]["pdf_page_index"] for p in LIMITS}==INDICES,
         "PDF index drift")
    if verify_local_source:
        need(PDF.is_file() and sha256(PDF.read_bytes()).hexdigest()==PDF_SHA,
             "original source file unavailable or changed")
        for p in (*LIMITS,*BOUNDARIES.values()):
            f=Path(f"/private/tmp/kb56_page_{p}.txt")
            need(f.is_file() and sha256(f.read_bytes()).hexdigest()==
                 pages[p]["pdfkit_text_sha256"],f"page {p} PDFKit byte drift")
            if p in LIMITS:
                need(len(f.read_text(encoding="utf8").splitlines())==LIMITS[p],
                    f"page {p} line count drift")
    counts=Counter();out=[]
    for index,row in enumerate(candidates,1):
        need(set(row)==set(CANDIDATES[0]),"unauthorized field including approval")
        key=row["key"]
        need(key in LOCK and LOCK[key]==
             (row["page"],row["start"],row["end"],row["kind"]),
             "source location or type changed")
        page,lo,hi=row["page"],row["start"],row["end"]
        need(1<=lo<=hi<=LIMITS[page],"source line bounds")
        need(any(a<=lo<=hi<=b for a,b,_ in partitions[page]),
             "candidate crossing structural boundary")
        need(row["kind"] in ("CONCEPT","THEOREM","METHOD","PEDAGOGY"),
             "invalid kind")
        need((key in PEDAGOGY)==(row["kind"]=="PEDAGOGY"),"kind changed")
        need(all(len(row[f])>=18 for f in
             ("mathematical_preconditions","invalid_generalization","editorial_note")),
             "thin source premise or nonexample")
        counts[track(row)]+=1
        out.append({**row,"id":f"KB112-P{page:03d}-C{index:02d}",
          "track_hint":track(row),"source_pdf_sha256":PDF_SHA,
          "source_page_pdfkit_sha256":pages[page]["pdfkit_text_sha256"],
          "pdf_page_index":pages[page]["pdf_page_index"],
          "math_witness":witness(key),"official_atom_id":None,
          "review_status":"REVIEW_PENDING","teacher_reviewer":None,
          "student_authoritative_release":False})
    need(counts=={"COMPULSORY":10,"ELECTIVE_B":10},"seven-track source partition drift")
    return dict(batch=112,scope_kind="PROVISIONAL_EDITORIAL_SOURCE_CANDIDATES",
        curriculum_standard="普通高中数学课程标准（2017年版2020年修订）",
        source_pdf_sha256=PDF_SHA,source_registry_sha256=sha256(REGISTRY.read_bytes()).hexdigest(),
        author_sha256=sha256((ROOT/"scripts/kb_batch112_source.py").read_bytes()).hexdigest(),
        pages=[22,59],line_counts={str(k):v for k,v in LIMITS.items()},
        source_lines_total=sum(LIMITS.values()),candidate_counts_by_track={t:counts[t] for t in TRACKS},
        structural_partitions=[dict(page=p,start=a,end=b,kind=k)
             for p,s in sorted(partitions.items()) for a,b,k in s],
        candidates=out,new_editorial_candidates=len(out),
        finite_exact_witnesses=sum(c["math_witness"]["finite_positive"] for c in out),
        pedagogy_not_math_proofs=len(PEDAGOGY),
        cross_page_continuations=[dict(from_page=p,to_page=q,
           next_pdfkit_sha256=pages[q]["pdfkit_text_sha256"],
           status="NOT_ATOMIZED_BY_TEACHER") for p,q in BOUNDARIES.items()],
        official_seven_track_atom_denominators={t:None for t in TRACKS},
        teacher_full_page_atomizations=0,teacher_approvals=0,
        student_authoritative_releases=0,
        limitations=["PDFKit extracted math formulas require human visual review; page 22 PDFKit has a broken same-angle fraction.",
            "Finite witnesses are not general proof certificates or teacher approvals.",
            "20 editorial candidates are NOT 20 certified curriculum atoms.",
            "Page 59 is elective B; it cannot count as elective A or selective compulsory."])

def lessons(units=UNITS,scope=None):
    if scope is None:scope=source()
    need(len(units)==8,"expected eight independently authored lessons")
    links=[];docs=[]
    bykey={r["key"]:r for r in scope["candidates"]}
    maps={x["id"]:x for x in curriculum()}
    older=[]
    for p in sorted(DEEP_DIR.glob("*.json")):
        n=re.match(r"batch(\d+)",p.name)
        if n and int(n.group(1))>111:continue
        if p==PACK:continue
        older+=json.loads(p.read_text(encoding="utf8"))
    ids={x["id"] for x in older}
    need(len(ids)==len(older),"historical duplicated lesson IDs")
    keys=[u["source_key"] for u in units]
    need(len(set(keys))==8,"duplicated source link")
    for i,u in enumerate(units):
        need(set(u)==set(UNITS[0]),"unauthorized lesson field including approval")
        kind=u["kind"];key=u["source_key"];cid=u["curriculum_id"]
        need(key in bykey and cid in maps,"unknown source or curriculum")
        need(kind in ("concept","theorem","method"),"invalid lesson type")
        need(len(u["statement"])>=50 and len(u["assumptions"])>=2
             and len(u["notation"])>=2 and len(u["prereqs"])>=2,
             "thin mathematical statement or conditions")
        need(len(u["reasoning"])>=3,"missing reasoning/proof steps")
        if kind=="theorem":
            need(all(len(s)==2 and len(s[0])>=18 and len(s[1])>=18
                     for s in u["reasoning"]),"unjustified theorem steps")
        else:need(all(len(x)>=20 for x in u["reasoning"]),"thin explanation")
        need(len(u["negative"])==3 and all(len(x)>=20 for x in u["negative"]),
             "missing concrete false inference")
        need(len(u["examples"])==2 and all(len(e["steps"])>=2 and
             len(e["question"])>=15 and len(e["check"])>=15
             for e in u["examples"]),"two worked independent examples required")
        need(len(u["hints"])==3 and len(set(u["hints"]))==3 and
             all(len(x)>=16 for x in u["hints"]),"bad spoiler-safe hint ladder")
        need(len(u["near"])>=20 and len(u["far"])>=20,"near/far transfer missing")
        sr=bykey[key];expected="COMPULSORY" if i<4 else "ELECTIVE_B"
        need(sr["track_hint"]==expected,"source track mismatch")
        need(maps[cid]["level"]==("必修" if i<4 else "选修拓展"),
             "engineering level/source track mismatch")
        need(sr["math_witness"]["finite_positive"],"source has no bounded instance")
        deps=DEPENDENCIES.get(i,[])
        need(all(0<=j<i for j in deps),"backward prerequisites only")
        id=f"math.hs.batch112.{i+1:02d}"
        doc=dict(id=id,curriculum_ids=[cid],kind=kind,title=u["title"],version="1.0.0",
          notation=u["notation"],prerequisites=u["prereqs"],
          prerequisite_lesson_ids=[f"math.hs.batch112.{j+1:02d}" for j in deps],
          definition=u["statement"] if kind=="concept" else None,statement=u["statement"],
          assumptions=u["assumptions"],
          proof_steps=[dict(claim=a,reason=b) for a,b in u["reasoning"]] if kind=="theorem" else [],
          rationale_steps=u["reasoning"] if kind!="theorem" else [],
          boundaries=u["assumptions"],
          counterexamples=[dict(false_claim=u["negative"][0],example=u["negative"][1],
                                explanation=u["negative"][2])],
          misconceptions=[dict(error=u["negative"][0],why_wrong=u["negative"][2],
            repair_question="请指出这个说法违反了什么定义域、量词或定理前提，并用具体反例修复推理。")],
          worked_examples=u["examples"],hint_ladder=u["hints"],
          transfer=dict(near=u["near"],far=u["far"]),
          provenance=dict(kind="PROJECT_AUTHORED",permission="PROJECT_AUTHORED",
            curriculum_standard="普通高中数学课程标准（2017年版2020年修订）",
            standard_url="https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf",
            author_role="PROJECT_AUTHOR"),
          review=dict(status="REVIEW_PENDING",reviewer_id=None,
                      reviewed_at=None,review_record=None),
          teacher_solution_visibility="TEACHER_ONLY")
        DeepLesson.model_validate(doc)
        need(id not in ids,"historical duplicate lesson ID")
        docs.append(doc)
        links.append(dict(lesson_id=id,source_candidate_id=sr["id"],
           source_key=key,source_printed_page=sr["page"],source_track_hint=expected,
           source_pdfkit_sha256=sr["source_page_pdfkit_sha256"],
           engineering_curriculum_id=cid,engineering_level=maps[cid]["level"],
           official_math_atom_id=None,teacher_approved=False,general_proof_certified=False))
    a=dict(batch=112,status="REVIEW_PENDING",visibility="TEACHER_ONLY",
      new_deep_drafts=len(docs),new_teacher_worked_examples=sum(len(d["worked_examples"]) for d in docs),
      new_hint_levels=sum(len(d["hint_ladder"]) for d in docs),
      new_transfer_tasks=2*len(docs),new_counterexamples=len(docs),
      new_prerequisite_edges=sum(len(x["prerequisite_lesson_ids"]) for x in docs),
      new_proof_step_candidates=sum(len(x["proof_steps"]) for x in docs),
      lesson_type_counts=dict(Counter(x["kind"] for x in docs)),
      historical_deep_lessons=len(older),all_deep_lessons=len(older)+len(docs),
      source_links=links,official_seven_track_atom_denominators={t:None for t in TRACKS},
      teacher_approvals=0,student_authoritative_releases=0,
      general_proof_certificates=0,arbitrary_student_steps_certified=0,
      author_sha256=sha256((ROOT/"scripts/kb_batch112_lesson_authoring.py").read_bytes()).hexdigest(),
      source_scope_sha256=sha256(dump(scope).encode()).hexdigest())
    return docs,a

def coverage(sc=None,a=None):
    if sc is None:sc=source()
    if a is None:a=lessons(scope=sc)[1]
    reg=json.loads(REGISTRY.read_text(encoding="utf8"))
    need({x["printed_page"] for x in reg["pages"]}==set(range(13,74)),
         "full 61-page registry missing")
    previous=[json.loads((ROOT/f"docs/evaluation/KB_BATCH{n}_SCOPE.json").read_text(encoding="utf8"))
              for n in (109,110,111)]
    used=set()
    for s in (*previous,sc):
        need(s["source_pdf_sha256"]==PDF_SHA,"forged source version")
        need(set(s["official_seven_track_atom_denominators"].values())=={None},
             "forged official denominators")
        need(s["teacher_approvals"]==0,"forged teacher approval")
        for page in s["line_counts"]:
            need(int(page) not in used,"duplicate source page across batches")
            used.add(int(page))
    need(len(used)==8,"four-batch coverage wrong")
    checks=[]
    docs,_=lessons(scope=sc)
    for doc in docs:
        lesson=DeepLesson.model_validate(doc)
        fields={"statement":len(lesson.statement)>=50,"assumptions":len(lesson.assumptions)>=2,
          "notation":len(lesson.notation)>=2,"prerequisites":len(lesson.prerequisites)>=2,
          "reasoning":len(lesson.proof_steps if lesson.kind=="theorem" else lesson.rationale_steps)>=3,
          "counterexample":len(lesson.counterexamples)>=1,"misconception":len(lesson.misconceptions)>=1,
          "worked_examples":len(lesson.worked_examples)==2,
          "hint_ladder":len(lesson.hint_ladder)==3,
          "near_far":bool(lesson.transfer.near and lesson.transfer.far),
          "license":lesson.provenance.permission=="PROJECT_AUTHORED",
          "privacy":lesson.teacher_solution_visibility=="TEACHER_ONLY"}
        need(all(fields.values()),"draft structure incomplete "+doc["id"])
        checks.append(dict(id=doc["id"],field_checks=fields,status="REVIEW_PENDING",
                           field_completion=sum(fields.values())/len(fields),
                           teacher_approved=False,student_authoritative=False))
    return dict(batch=112,source_pdf_pages_total=61,scoped_pages_in_four_latest_batches=sorted(used),
        recent_source_page_fraction=len(used)/61,teacher_certified_full_pages=0,
        source_candidate_counts_by_track=sc["candidate_counts_by_track"],
        official_atom_coverage_by_track={t:dict(total=None,approved=0,
                     coverage_fraction=None,missing_total="UNKNOWN") for t in TRACKS},
        new_lesson_field_checks=checks,teacher_approved_lessons=0,
        unreviewed_legacy_prerequisites=172,uncertified_legacy_proof_steps=538,
        unresolved_legacy_math_conflicts=10,
        limitations=["Eight pages are only the latest four batches, not total historical page review.",
          "No seven-track denominator exists; do not treat page count or editorial candidates as atomic curriculum coverage.",
          "Field completeness and finite witnesses do not substitute teacher approval or general theorem proof."])

def markdown(scope,docs,audit,cov):
    lines=["# Batch112｜官方课标22/59页：三角与极限八份完整教师候审讲义","",
      "来源文本仅用SHA与行区间定位，内容为原创；不收录版权教材原文。","",
      "所有课程候选仍REVIEW_PENDING。有限数学检验不能自动批准一般证明。","",
      "## K00来源与K01分母门禁","",
      f"印刷页22/59：{scope['source_lines_total']}行，{len(scope['structural_partitions'])}结构段，",
      f"20条编辑要求候选；{scope['finite_exact_witnesses']}组有限数学正反检验。",
      "两页分别归属必修与选修B，七轨官方知识原子分母全部UNKNOWN。",""]
    for d,link in zip(docs,audit["source_links"]):
        lines += [f"## {d['id']}｜{d['title']}","",
           f"来源候选：{link['source_candidate_id']}；轨道：{link['source_track_hint']}；工程映射：{link['engineering_curriculum_id']}。","",
           "**原创建议陈述：** "+d["statement"],"",
           "**适用前提：** "+"；".join(d["assumptions"]),"",
           "**符号：** "+"；".join(d["notation"]),"",
           "**先修：** "+"；".join(d["prerequisites"]),"",]
        for i,r in enumerate(d["proof_steps"],1):
            lines += [f"**候审证明第{i}步：** {r['claim']}","**依据：** "+r["reason"],""]
        for i,r in enumerate(d["rationale_steps"],1):
            lines += [f"**解释第{i}步：** {r}",""]
        c=d["counterexamples"][0]
        lines += ["**错误主张：** "+c["false_claim"],"","**具体反例：** "+c["example"],"",
                  "**失效原因：** "+c["explanation"],""]
        for i,e in enumerate(d["worked_examples"],1):
            lines += [f"### 教师侧例题{i}","",e["question"],""]
            for n,step in enumerate(e["steps"],1):lines += [f"{n}. {step}"]
            lines += ["","**答案：** "+e["answer"],"","**独立代回：** "+e["check"],""]
        lines += ["**不剧透提示：** "+"；".join(d["hint_ladder"]),"",
            "**近迁移：** "+d["transfer"]["near"],"",
            "**远迁移：** "+d["transfer"]["far"],""]
    lines += ["## 剩余风险","",
       "七轨正式分母UNKNOWN；0教师批准/0学生权威发布；172先修标签、538历史证明步骤未审核；10冲突待裁决。",""]
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    ap.add_argument("--verify-local-source",action="store_true")
    a=ap.parse_args();s=source(verify_local_source=a.verify_local_source)
    docs,log=lessons(scope=s);cv=coverage(sc=s,a=log)
    pairs=((SOURCE_OUT,dump(s)),(PACK,dump(docs)),(AUDIT,dump(log)),
           (COVER,dump(cv)),(MD,markdown(s,docs,log,cv)))
    for path,data in pairs:
        if a.check:need(path.read_text(encoding="utf8")==data,"generated artifact drift "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(data,encoding="utf8")
    print("Batch112 PASS",s["source_lines_total"],len(s["candidates"]),
          s["finite_exact_witnesses"],len(docs),"draft lessons",
          log["new_proof_step_candidates"],"unverified proof steps")
if __name__=="__main__":main()
