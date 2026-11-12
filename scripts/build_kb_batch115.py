#!/usr/bin/env python3
"""Batch115: 4-page pinned source audit, original lessons, guarded census and refusal.
Finite SymPy witnesses do not certify theorems, and DRAFT is not student authority.
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter
from hashlib import sha256
from pathlib import Path
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch115_source import CANDIDATES,PARTITIONS
from kb_batch115_lessons import UNITS
from app.deep_knowledge import DeepLesson,DEEP_DIR,curriculum

PDF=Path.home()/"Library/Caches/stem-mentor-source-review/highschool_math_standard_2020.pdf"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
REGISTRY=ROOT/"curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
LIMITS={25:25,26:29,62:25,63:23}
INDICES={25:32,26:33,62:69,63:70}
NONMATH={"vector_scope","model_scope"}
KEYS={r["key"]:(r["page"],r["start"],r["end"],r["kind"]) for r in CANDIDATES}
SCOPE=ROOT/"docs/evaluation/KB_BATCH115_SCOPE.json"
PACK=DEEP_DIR/"batch115_vectors_inference.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH115_AUDIT.json"
COVER=ROOT/"docs/evaluation/KB_BATCH115_COVERAGE.json"
LESSON_MD=ROOT/"docs/evaluation/KB_BATCH115_LESSONS.md"

def need(condition,message):
    if not condition:raise ValueError(message)
def dumps(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def hashfile(path):return sha256(Path(path).read_bytes()).hexdigest()
def track(row):return "COMPULSORY" if row["page"] in (25,26) else "ELECTIVE_B"

def witness(key):
    """Only independently enumerated finite probes; all other candidates remain unverified."""
    R=sp.Rational
    samples={
       "vector_meaning":((4-1,6-2)==(1-(-2),4-0), (0,0)!=(1,0)),
       "vector_add":((2-3,-1+4)==(-1,3),sp.sqrt(5)!=3),
       "vector_dot":(3*4+4*(-3)==0,5!=0),
       "vector_orthogonal":(3*2+2*(-3)==0, (0*1+0*0)==0),
       "estimation":(R(3,4)**3*(1-R(3,4))==R(27,256), (1-R(0))**5==1),
       "hypothesis":(R(1,2)**4==R(1,16),R(1,16)>R(5,100)),
       "regression":(sum((x-1)*(y-3) for x,y in ((0,1),(1,3),(2,5)))==4,
                     sum((x-2)**2 for x in (2,2))==0),
       "exponential_model":(R(100)*R(11,10)**2==R(121),R(80)*R(3,4)**2==R(45))
    }
    if key not in samples:return {"status":"NOT_INDEPENDENTLY_CHECKED","positive":False,"boundary":False,"general_proof_certified":False}
    positive,boundary=samples[key]
    need(bool(positive) and bool(boundary),"finite witness failed: "+key)
    return {"status":"FINITE_EXACT_INSTANCE_ONLY","positive":True,"boundary":True,"general_proof_certified":False}

def source(candidates=CANDIDATES,partitions=PARTITIONS,verify_local_source=False):
    need(len(candidates)==24 and len(KEYS)==24,"24 unique source candidates required")
    need(set(partitions)==set(LIMITS),"page set drift")
    for p,parts in partitions.items():
        need([v for a,b,_ in parts for v in range(a,b+1)]==list(range(1,LIMITS[p]+1)),
             f"PDFKit line structure gap/overlap for {p}")
    registry=json.loads(REGISTRY.read_text())
    need(registry["official_pdf_sha256"]==PDF_SHA,"official PDF SHA drift")
    pages={p["printed_page"]:p for p in registry["pages"]}
    need({p:pages[p]["pdf_page_index"] for p in LIMITS}==INDICES,"source PDF page index drift")
    if verify_local_source:
        need(PDF.is_file() and hashfile(PDF)==PDF_SHA,"source PDF missing or modified")
        for p in LIMITS:
            txt=Path(f"/private/tmp/kb56_page_{p}.txt")
            need(txt.is_file() and hashfile(txt)==pages[p]["pdfkit_text_sha256"],f"PDFKit source SHA drift {p}")
            need(len(txt.read_text().splitlines())==LIMITS[p],f"PDFKit row count drift {p}")
    output=[];counts=Counter()
    for i,row in enumerate(candidates,1):
        need(set(row)==set(CANDIDATES[0]),"invalid/missing candidate field")
        key=row["key"]
        need(key in KEYS and KEYS[key]==(row["page"],row["start"],row["end"],row["kind"]),"source locator/type/id drift")
        p,lo,hi=row["page"],row["start"],row["end"]
        need(1<=lo<=hi<=LIMITS[p] and any(a<=lo<=hi<=b for a,b,_ in partitions[p]),"source span violates partition")
        need(row["kind"] in ("CONCEPT","THEOREM","METHOD","PEDAGOGY"),"illegal knowledge type")
        need((key in NONMATH)==(row["kind"]=="PEDAGOGY"),"nonmath categorized as theorem")
        need(all(len(row[f])>=18 for f in ("mathematical_preconditions","invalid_generalization","editorial_note")),"thin candidate")
        t=track(row);counts[t]+=1
        output.append({**row,"id":f"KB115-P{p:03d}-C{i:02d}","track_hint":t,
         "source_pdf_sha256":PDF_SHA,"source_page_pdfkit_sha256":pages[p]["pdfkit_text_sha256"],
         "pdf_page_index":pages[p]["pdf_page_index"],"math_witness":witness(key),
         "official_atom_id":None,"review_status":"REVIEW_PENDING","teacher_reviewer":None,
         "student_authoritative_release":False})
    need(counts["COMPULSORY"]==13 and counts["ELECTIVE_B"]==11 and sum(counts.values())==24,
         "candidate track counts differ from evidence")
    return {"batch":115,"scope_kind":"EDITORIAL_SOURCE_CANDIDATES_NOT_OFFICIAL_ATOMS",
     "curriculum_standard":"普通高中数学课程标准（2017年版2020年修订）",
     "source_pdf_sha256":PDF_SHA,"source_registry_sha256":hashfile(REGISTRY),
     "source_author_sha256":hashfile(ROOT/"scripts/kb_batch115_source.py"),
     "pages":list(LIMITS),"line_counts":{str(k):v for k,v in LIMITS.items()},
     "source_lines_total":sum(LIMITS.values()),
     "structural_partitions":[{"page":p,"start":a,"end":b,"kind":k} for p,ps in partitions.items() for a,b,k in ps],
     "candidates":output,"editorial_candidate_count":len(output),
     "candidate_counts_by_track":{t:counts[t] for t in TRACKS},
     "finite_exact_witnesses":sum(c["math_witness"]["positive"] for c in output),
     "official_seven_track_atom_denominators":{t:None for t in TRACKS},
     "teacher_full_page_atomizations":0,"teacher_approvals":0,"student_authoritative_releases":0,
     "limitations":["四页PDFKit结构行不等于完整官方原子分母。","有限实例不能代替一般定理证明。",
                    "ELECTIVE_B仅是来源轨道定位，须经独立课标审校确认细分归属。"]}

def lessons(units=UNITS,scope=None):
    if scope is None:scope=source()
    need(len(units)==len(UNITS)==8,"eight substantial lessons required")
    bykey={r["key"]:r for r in scope["candidates"]}
    curr={r["id"]:r for r in curriculum()}
    history=[r for p in sorted(DEEP_DIR.glob("*.json")) if p!=PACK
             for r in json.loads(p.read_text())]
    oldids={z["id"] for z in history}
    need(len(oldids)==len(history),"historical lesson IDs duplicate")
    docs=[];links=[]
    for i,u in enumerate(units,1):
        need(set(u)==set(UNITS[0]),"lesson authoring field tampered")
        need(u["kind"] in ("concept","theorem","method"),"unsupported kind")
        need(u["source_key"] in bykey and u["curriculum_id"] in curr,"unknown source or course ID")
        need(len(u["statement"])>=65 and len(u["assumptions"])>=2 and len(u["notation"])>=2
             and len(u["prereqs"])>=2,"lesson is not substantive")
        need(len(u["reasoning"])==3 and len(u["negative"])==3,"missing explanation/contradiction")
        need(len(u["examples"])==2 and all(len(e["steps"])>=2 and len(e["check"])>=18 for e in u["examples"]),
             "two checked worked examples required")
        need(len(u["hints"])==3 and len(set(u["hints"]))==3 and len(u["near"])>=25 and len(u["far"])>=25,
             "hints/transfers incomplete")
        src=bykey[u["source_key"]];expected="COMPULSORY" if i<=4 else "ELECTIVE_B"
        need(src["track_hint"]==expected,"source track mismatch")
        need(curr[u["curriculum_id"]]["level"]==("必修" if i<=4 else "选修拓展"),
             "engineering course track mismatch")
        need(src["math_witness"]["positive"],"source without finite witness")
        if u["kind"]=="theorem":
            need(all(len(r)==2 and min(map(len,r))>=20 for r in u["reasoning"]),"incomplete theorem rationale")
        else:need(all(len(r)>=20 for r in u["reasoning"]),"incomplete explanatory rationale")
        lid=f"math.hs.batch115.{i:02d}"
        need(lid not in oldids,"knowledge ID duplicate")
        d={"id":lid,"curriculum_ids":[u["curriculum_id"]],"kind":u["kind"],
          "title":u["title"],"version":"1.0.0",
          "notation":u["notation"],"prerequisites":u["prereqs"],"prerequisite_lesson_ids":[],
          "definition":u["statement"] if u["kind"]=="concept" else None,
          "statement":u["statement"],"assumptions":u["assumptions"],
          "proof_steps":[{"claim":x,"reason":y} for x,y in u["reasoning"]] if u["kind"]=="theorem" else [],
          "rationale_steps":u["reasoning"] if u["kind"]!="theorem" else [],
          "boundaries":u["assumptions"],
          "counterexamples":[{"false_claim":u["negative"][0],"example":u["negative"][1],
                              "explanation":u["negative"][2]}],
          "misconceptions":[{"error":u["negative"][0],"why_wrong":u["negative"][2],
             "repair_question":"找出定义域、样本独立性、边界或非零向量前提，并写出反例。"}],
          "worked_examples":u["examples"],"hint_ladder":u["hints"],
          "transfer":{"near":u["near"],"far":u["far"]},
          "provenance":{"kind":"PROJECT_AUTHORED","permission":"PROJECT_AUTHORED",
            "curriculum_standard":"普通高中数学课程标准（2017年版2020年修订）",
            "standard_url":"https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf",
            "author_role":"PROJECT_AUTHOR"},
          "review":{"status":"REVIEW_PENDING","reviewer_id":None,"reviewed_at":None,"review_record":None},
          "teacher_solution_visibility":"TEACHER_ONLY"}
        DeepLesson.model_validate(d)
        docs.append(d)
        links.append({"lesson_id":lid,"candidate_id":src["id"],"source_printed_page":src["page"],
                      "source_track_hint":expected,"engineering_curriculum_id":u["curriculum_id"],
                      "official_atom_id":None,"teacher_approved":False,"general_proof_certified":False})
    need(len({d["id"] for d in docs})==8,"duplicate new lesson IDs")
    audit={"batch":115,"teacher_approvals":0,"student_authoritative_releases":0,
     "formal_proof_certificates":0,"student_free_text_proof_certificates":0,
     "new_deep_drafts":len(docs),"new_teacher_worked_examples":sum(len(d["worked_examples"]) for d in docs),
     "new_hint_levels":sum(len(d["hint_ladder"]) for d in docs),
     "new_transfer_tasks":len(docs)*2,"new_counterexamples":len(docs),
     "new_uncertified_proof_steps":sum(len(d["proof_steps"]) for d in docs),
     "lesson_kind_counts":dict(Counter(d["kind"] for d in docs)),
     "prior_deep_drafts":len(history),"total_deep_drafts":len(history)+len(docs),
     "lesson_completeness":[{"id":d["id"],"required_structural_fields_present":True,
                             "example_count":2,"hint_count":3,"counterexample_count":1,
                             "review_status":"REVIEW_PENDING","proof_steps_machine_certified":0,
                             "teacher_reviewed":False} for d in docs],
     "source_links":links,"author_sha256":hashfile(ROOT/"scripts/kb_batch115_lessons.py")}
    return docs,audit

def coverage(scope=None,ds=None):
    if scope is None:scope=source()
    if ds is None:ds=lessons(scope=scope)[0]
    official=json.loads(REGISTRY.read_text())["pages"]
    need({z["printed_page"] for z in official}==set(range(13,74)),
         "official source pagination does not contain 61 consecutive pages")
    prior={}
    for p in sorted((ROOT/"docs/evaluation").glob("KB_BATCH*_SCOPE.json")):
        if p==SCOPE:continue
        old=json.loads(p.read_text())
        if old.get("source_pdf_sha256")!=PDF_SHA or not isinstance(old.get("line_counts"),dict):continue
        for page in map(int,old["line_counts"]):
            need(page not in prior,f"prior duplicated source page {page}")
            prior[page]=p.name
    need(not (set(prior)&set(scope["pages"])),"source page counted twice")
    marked={**prior,**{p:SCOPE.name for p in scope["pages"]}}
    records=[{"printed_page":z["printed_page"],"pdf_page_index":z["pdf_page_index"],
      "source_pdfkit_sha256":z["pdfkit_text_sha256"],
      "source_structure_candidate_review":z["printed_page"] in marked,
      "source_audit_file":marked.get(z["printed_page"]),
      "official_math_atoms":None,"teacher_verified_atomization":False,
      "teacher_review_record":None,"approved_math_atoms":0,"official_coverage":None} for z in official]
    need(len(marked)==18 and len(records)==61,"K00 page ledger drift")
    return {"batch":115,"official_source_pdf_pages":61,
      "source_structure_candidate_reviewed_pages":len(marked),
      "source_structure_reviewed_pages":sorted(marked),
      "source_structure_unreviewed_pages":sorted(set(range(13,74))-set(marked)),
      "teacher_verified_atomized_pages":0,
      "per_page_denominator_status":records,
      "seven_track_official_atom_denominator":{t:None for t in TRACKS},
      "seven_track_certified_coverage":{t:None for t in TRACKS},
      "seven_track_editorial_candidate_counts_current_batch":scope["candidate_counts_by_track"],
      "newly_authored_drafts":len(ds),"teacher_approved_drafts":0,
      "historical_unreviewed_prerequisite_edges":172,
      "historical_uncertified_proof_steps":538,
      "historical_unresolved_math_conflicts":10,
      "limitations":["已审来源结构页并非教师认证的课标原子化页面。","7轨正式分母全部未知而非0。",
                     "工程候审文档数量只用于代码规模审计，不能用于课程完成率计算。"]}

def markdown(scope,docs,audit,cov):
    o=["# Batch115｜必修向量与选修B统计/模型原创知识包","",
       f"课标结构页来源审核：{scope['pages']}，4页共{scope['source_lines_total']}行，"
       f"{scope['editorial_candidate_count']}个候审要求，8项有限数学见证。", "",
       f"累计结构登记页：{cov['source_structure_candidate_reviewed_pages']}/61；"
       "七轨正式原子分母均UNKNOWN，教师审批、形式化证明、学生权威发布均为0。",""]
    for d,link in zip(docs,audit["source_links"]):
        o += [f"## {d['id']}｜{d['title']}","",
              f"候审来源：{link['candidate_id']}，课标印刷页{link['source_printed_page']}，"
              f"工程ID {link['engineering_curriculum_id']}，轨道提示 {link['source_track_hint']}。","",
              "**定义/陈述**："+d["statement"],"",
              "**符号**："+"；".join(d["notation"]),"",
              "**全部假设**："+"；".join(d["assumptions"]),"",
              "**先修**："+"；".join(d["prerequisites"]),"",]
        if d["kind"]=="theorem":
            for j,p in enumerate(d["proof_steps"],1):o += [f"**未认证证明{j}**：{p['claim']}","论据："+p["reason"],""]
        else:
            for j,s in enumerate(d["rationale_steps"],1):o += [f"**解释{j}**：{s}",""]
        n=d["counterexamples"][0]
        o += ["**典型错法**："+n["false_claim"],"",
              "**反例**："+n["example"],"","**错因**："+n["explanation"],""]
        for k,e in enumerate(d["worked_examples"],1):
            o += [f"**教师例题{k}**："+e["question"],""]
            for j,s in enumerate(e["steps"],1):o += [f"{j}. {s}"]
            o += ["","**教师答案**："+e["answer"],"","**独立核对说明**："+e["check"],""]
        o += ["**不剧透三级提示**："+"；".join(d["hint_ladder"]),"",
              "**近迁移**："+d["transfer"]["near"],"",
              "**远迁移**："+d["transfer"]["far"],""]
    o += ["## 质量边界","",
         "当前为原创教学候审材料，有限符号实例只证明被检查的具体命题，不能取代一般证明和独立教研核对。教师完整答案保持TEACHER_ONLY。",""]
    return "\n".join(o)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--verify-local-source",action="store_true")
    a=parser.parse_args()
    s=source(verify_local_source=a.verify_local_source)
    ds,au=lessons(scope=s)
    cov=coverage(scope=s,ds=ds)
    outputs=((SCOPE,dumps(s)),(PACK,dumps(ds)),(AUDIT,dumps(au)),
             (COVER,dumps(cov)),(LESSON_MD,markdown(s,ds,au,cov)))
    for path,txt in outputs:
        if a.check:
            need(path.read_text()==txt,"generated artifact drift: "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(txt,encoding="utf-8")
    print(f"Batch115 OK: {len(s['pages'])} source pages, {len(s['candidates'])} candidates, "
          f"{len(ds)} original draft lessons, {au['new_uncertified_proof_steps']} uncertified steps; "
          f"{cov['source_structure_candidate_reviewed_pages']}/61 source pages, official denominators UNKNOWN")
if __name__=="__main__":main()
