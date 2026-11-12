#!/usr/bin/env python3
"""Batch113: independently reproducible source, rigor, draft and RAG audit.

Offline artifact inputs: local project authored code, frozen original-source SHA
registry. Mac-only option checks official PDF and PDFKit line bytes. Passing
finite algebra checks never promotes proof steps or student authority.
"""
from __future__ import annotations
import argparse,json,re,sys
from collections import Counter
from hashlib import sha256
from pathlib import Path
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch113_source import CANDIDATES,PARTITIONS
from kb_batch113_lesson_authoring import UNITS
from app.deep_knowledge import DEEP_DIR,DeepLesson,curriculum
PDF=Path.home()/"Library/Caches/stem-mentor-source-review/highschool_math_standard_2020.pdf"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
REGISTRY=ROOT/"curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
LIMITS={23:28,60:27}
INDICES={23:30,60:67}
BOUNDARIES={22:23,59:60}
LOCK={r["key"]:(r["page"],r["start"],r["end"],r["kind"]) for r in CANDIDATES}
NONMATH={"pedagogical_scope","space_outline"}
SOURCE_OUT=ROOT/"docs/evaluation/KB_BATCH113_SCOPE.json"
PACK=DEEP_DIR/"batch113_function_vectors_ellipse.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH113_AUDIT.json"
COVER=ROOT/"docs/evaluation/KB_BATCH113_COVERAGE.json"
MD=ROOT/"docs/evaluation/KB_BATCH113_LESSONS.md"

def need(ok,message):
    if not ok:raise ValueError(message)
def dump(o):
    return json.dumps(o,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
def track(row):
    return "COMPULSORY" if row["page"]==23 else "ELECTIVE_B"

def witness(key):
    if key in NONMATH:
        return dict(status="PEDAGOGY_NOT_MATH_PROOF",finite_positive=False,
            finite_boundary=False,general_proof_certified=False)
    R=sp.Rational
    A=sp.Matrix
    x,y=sp.symbols("x y",real=True)
    checks={
      "root_precision":(1**2-2<0<2**2-2, R(3,2)**2-2>0),
      "model_selection":([2*2**i for i in range(3)]==[2,4,8], 2*2**3!=10),
      "model_domain":(2**R(1,2)>0, -1 not in range(4)),
      "growth_order":(sp.log(16,2)==4, 16<2**16),
      "log_growth":(sp.log(8,2)==3, sp.log(R(1,2),2)==-1),
      "parameter_meaning":(R(11,10)**3==R(1331,1000), R(3,60)==R(1,20)),
      "mapping_function":(len({1:2,2:3})==2, len({1:2,1:3})==1),
      "monotonic_symbol":(2*R(1,2)<2*1, (0**2)<(1**2)),
      "rational_power":(sp.sqrt(4)==2, sp.Pow(-2,R(1,2)).is_real is False),
      "extrapolation":(2*2**2==8, 2*2**3!=10),
      "cross_product":(A([1,0,0]).cross(A([0,1,0]))==A([0,0,1]),
                        A([0,1,0]).cross(A([1,0,0]))==A([0,0,-1])),
      "projection":(A([3,4,2]).dot(A([1,0,0]))==3,A([1,1,0]).dot(A([1,-1,0]))==0),
      "linear_independence":(A([1,0,0]).cross(A([0,1,0]))!=A([0,0,0]),
                          A.hstack(A([1,0,0]),A([0,0,0])).rank()==1),
      "skew_distance":(A([0,1,1]).dot(A([1,0,0]).cross(A([0,1,0])))==1,
                       A([1,0,0]).cross(A([2,0,0]))==A([0,0,0])),
      "line_plane_angle":(A([0,0,2]).dot(A([0,0,3]))==6,
                           A([1,0,0]).dot(A([0,0,1]))==0),
      "matrix_product":(A([[1,1],[0,1]])*A([[1,0],[1,1]])!=
                         A([[1,0],[1,1]])*A([[1,1],[0,1]]),A.eye(3)*A.eye(3)==A.eye(3)),
      "determinant":(A.diag(1,2,0).det()==0,A.diag(1,2,3).det()==6),
      "elimination":(A([[1,1],[1,-1]]).det()==-2,
                      A([[1,1,1],[0,1,1],[0,0,1]]).det()==1),
      "solution_structure":(A([[1,0],[0,0]])*A([2,3])==A([2,0]),
                            A([[1,0],[0,0]])*A([2,6])==A([2,0])),
      "cramer":(A.eye(3).det()==1,A.diag(1,1,0).det()==0)
    }
    need(key in checks,f"no finite math example for {key}")
    pos,invalid=checks[key]
    need(bool(pos) and bool(invalid),"bounded example failed "+key)
    return dict(status="FINITE_EXACT_OR_BOUNDED_INSTANCE_ONLY",finite_positive=True,
        finite_boundary=True,general_proof_certified=False)

def source(candidates=CANDIDATES,partitions=PARTITIONS,verify_local_source=False):
    need(len(CANDIDATES)==22 and len(LOCK)==22,"source cardinality drift")
    need(len(candidates)==22 and len({r["key"] for r in candidates})==22,"duplicated source ID")
    need(set(partitions)==set(LIMITS),"source pages mismatch")
    for p,regions in partitions.items():
        need([n for lo,hi,_ in regions for n in range(lo,hi+1)]==
             list(range(1,LIMITS[p]+1)),f"missing or overlapping PDFKit lines {p}")
    registry=json.loads(REGISTRY.read_text(encoding="utf8"))
    need(registry["official_pdf_sha256"]==PDF_SHA,"official PDF provenance mismatch")
    pages={r["printed_page"]:r for r in registry["pages"]}
    need({p:pages[p]["pdf_page_index"] for p in LIMITS}==INDICES,"PDF index mismatch")
    if verify_local_source:
        need(PDF.is_file() and sha256(PDF.read_bytes()).hexdigest()==PDF_SHA,
             "Mac-only original PDF hash unavailable or changed")
        for p in (22,23,59,60):
            f=Path(f"/private/tmp/kb56_page_{p}.txt")
            need(f.is_file() and sha256(f.read_bytes()).hexdigest()==pages[p]["pdfkit_text_sha256"],
                 f"Mac-only PDFKit source hash changed {p}")
            if p in LIMITS:
                need(len(f.read_text(encoding="utf8").splitlines())==LIMITS[p],
                     f"PDFKit line count drift {p}")
    counts=Counter();rows=[]
    for i,r in enumerate(candidates,1):
        need(set(r)==set(CANDIDATES[0]),"untrusted source field including fake approval")
        need(r["key"] in LOCK and LOCK[r["key"]]==(r["page"],r["start"],r["end"],r["kind"]),
             "source span, type or category altered")
        p,lo,hi=r["page"],r["start"],r["end"]
        need(1<=lo<=hi<=LIMITS[p],"source invalid line range")
        need(any(a<=lo<=hi<=b for a,b,_ in partitions[p]),"candidate crosses structural partition")
        need(r["kind"] in ("CONCEPT","THEOREM","METHOD","PEDAGOGY"),"bad kind")
        need((r["key"] in NONMATH)==(r["kind"]=="PEDAGOGY"),"pedagogy mathematical category mismatch")
        need(all(len(r[f])>=18 for f in ("mathematical_preconditions","invalid_generalization",
              "editorial_note")),"source requirement too thin")
        t=track(r);counts[t]+=1
        rows.append({**r,"id":f"KB113-P{p:03d}-C{i:02d}",
          "track_hint":t,"source_pdf_sha256":PDF_SHA,
          "source_page_pdfkit_sha256":pages[p]["pdfkit_text_sha256"],
          "pdf_page_index":pages[p]["pdf_page_index"],"math_witness":witness(r["key"]),
          "official_atom_id":None,"review_status":"REVIEW_PENDING",
          "teacher_reviewer":None,"student_authoritative_release":False})
    need(counts=={"COMPULSORY":11,"ELECTIVE_B":11},"seven-track categories changed")
    return dict(batch=113,scope_kind="PROVISIONAL_EDITORIAL_SOURCE_CANDIDATES",
      curriculum_standard="普通高中数学课程标准（2017年版2020年修订）",
      source_pdf_sha256=PDF_SHA,source_registry_sha256=sha256(REGISTRY.read_bytes()).hexdigest(),
      author_sha256=sha256((ROOT/"scripts/kb_batch113_source.py").read_bytes()).hexdigest(),
      pages=[23,60],line_counts={str(k):v for k,v in LIMITS.items()},
      source_lines_total=sum(LIMITS.values()),
      candidate_counts_by_track={t:counts[t] for t in TRACKS},
      structural_partitions=[dict(page=p,start=a,end=b,kind=k)
          for p,parts in sorted(partitions.items()) for a,b,k in parts],
      candidates=rows,new_editorial_candidates=len(rows),
      finite_exact_witnesses=sum(x["math_witness"]["finite_positive"] for x in rows),
      pedagogy_not_math_proofs=len(NONMATH),
      cross_page_continuations=[dict(from_page=p,to_page=q,
         previous_pdfkit_sha256=pages[p]["pdfkit_text_sha256"],
         status="NOT_ATOMIZED_BY_TEACHER") for p,q in BOUNDARIES.items()],
      official_seven_track_atom_denominators={t:None for t in TRACKS},
      teacher_full_page_atomizations=0,teacher_approvals=0,student_authoritative_releases=0,
      limitations=["55 source lines include 2 printed page-number footers, not 55 math atoms.",
        "PDFKit page60 line19/20 is visually scrambled; provenance is not certified transcription.",
        "20 bounded math witnesses are not universal proofs; 2 pedagogy items are not theorems.",
        "Seven official atom denominators UNKNOWN; zero teacher certification."])

def lessons(units=UNITS,scope=None):
    if scope is None:scope=source()
    need(len(UNITS)==9 and len(units)==9,"nine substantive lessons required")
    src={r["key"]:r for r in scope["candidates"]}
    previous_scope=json.loads((ROOT/"docs/evaluation/KB_BATCH112_SCOPE.json").read_text(encoding="utf8"))
    backfill=next(r for r in previous_scope["candidates"] if r["key"]=="quadratic_region")
    src[backfill["key"]]=backfill
    ids={c["id"]:c for c in curriculum()}
    older=[]
    for path in sorted(DEEP_DIR.glob("*.json")):
        n=re.match(r"batch(\d+)",path.name)
        if n and int(n.group(1))>112:continue
        if path==PACK:continue
        older+=json.loads(path.read_text(encoding="utf8"))
    oldids=[d["id"] for d in older]
    need(len(oldids)==len(set(oldids)),"historical lesson IDs duplicated")
    docs=[];links=[]
    for i,u in enumerate(units,1):
        need(set(u)==set(UNITS[0]),"unauthorized source or lesson field")
        need(u["kind"] in ("theorem","concept","method"),"unsupported draft lesson type")
        need(u["source_key"] in src and u["curriculum_id"] in ids,"missing source or curriculum")
        need(len(u["statement"])>=50 and len(u["notation"])>=2 and
             len(u["prereqs"])>=2 and len(u["assumptions"])>=2,"missing premise/notation")
        need(len(u["reasoning"])>=3,"unjustified proof or method")
        if u["kind"]=="theorem":
            need(all(len(s)==2 and all(len(v)>=18 for v in s) for s in u["reasoning"]),
                 "theorem proof step without adequate reason")
        else:
            need(all(len(s)>=20 for s in u["reasoning"]),"method or concept explanation too thin")
        need(len(u["negative"])==3 and all(len(s)>=20 for s in u["negative"]),
             "missing negative case or explanation")
        need(len(u["examples"])==2 and all(len(e["steps"])>=2 and
             len(e["question"])>=18 and len(e["check"])>=18 for e in u["examples"]),
             "not enough independently checked worked examples")
        need(len(u["hints"])==3 and len(set(u["hints"]))==3 and
             all(len(s)>=16 for s in u["hints"]),"incomplete no-spoiler hint ladder")
        need(len(u["near"])>=25 and len(u["far"])>=25,"missing near/far transfer")
        row=src[u["source_key"]]
        expected="COMPULSORY" if i<=4 else "ELECTIVE_B"
        need(row["track_hint"]==expected,"source track mismatch")
        need(ids[u["curriculum_id"]]["level"]==("必修" if i<=4 else "选修拓展"),
             "engineering level/source mismatch")
        need(row["math_witness"]["finite_positive"],"source lacks math evidence")
        lid=f"math.hs.batch113.{i:02d}"
        need(lid not in oldids,"existing lesson ID collision")
        deps=({"math.hs.batch113.02"} if i==4 else set())
        need(all(d in [x["id"] for x in docs] for d in deps),"prerequisite not previously authored")
        d=dict(id=lid,curriculum_ids=[u["curriculum_id"]],kind=u["kind"],
          title=u["title"],version="1.0.0",notation=u["notation"],
          prerequisites=u["prereqs"],prerequisite_lesson_ids=sorted(deps),
          definition=u["statement"] if u["kind"]=="concept" else None,
          statement=u["statement"],assumptions=u["assumptions"],
          proof_steps=[dict(claim=a,reason=b) for a,b in u["reasoning"]] if u["kind"]=="theorem" else [],
          rationale_steps=u["reasoning"] if u["kind"]!="theorem" else [],
          boundaries=u["assumptions"],
          counterexamples=[dict(false_claim=u["negative"][0],
            example=u["negative"][1],explanation=u["negative"][2])],
          misconceptions=[dict(error=u["negative"][0],why_wrong=u["negative"][2],
             repair_question="请指出推导中遗漏的数学假设、定义域或边界条件，并给出有效反例。")],
          worked_examples=u["examples"],hint_ladder=u["hints"],
          transfer=dict(near=u["near"],far=u["far"]),
          provenance=dict(kind="PROJECT_AUTHORED",permission="PROJECT_AUTHORED",
             curriculum_standard="普通高中数学课程标准（2017年版2020年修订）",
             standard_url="https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf",
             author_role="PROJECT_AUTHOR"),
          review=dict(status="REVIEW_PENDING",reviewer_id=None,
             reviewed_at=None,review_record=None),
          teacher_solution_visibility="TEACHER_ONLY")
        DeepLesson.model_validate(d)
        docs.append(d)
        links.append(dict(lesson_id=lid,source_candidate_id=row["id"],
          source_key=row["key"],source_printed_page=row["page"],
          source_track_hint=expected,engineering_curriculum_id=u["curriculum_id"],
          source_pdfkit_sha256=row["source_page_pdfkit_sha256"],
          backfilled_from_batch112=(i==9),engineering_mapping_is_only_prerequisite=(i==6),official_math_atom_id=None,
          teacher_approved=False,general_proof_certified=False))
    a=dict(batch=113,status="REVIEW_PENDING",visibility="TEACHER_ONLY",
       new_deep_drafts=len(docs),new_teacher_worked_examples=sum(len(d["worked_examples"]) for d in docs),
       new_hint_levels=sum(len(d["hint_ladder"]) for d in docs),
       new_transfer_tasks=2*len(docs),new_counterexamples=len(docs),
       new_prerequisite_edges=sum(len(d["prerequisite_lesson_ids"]) for d in docs),
       new_proof_step_candidates=sum(len(d["proof_steps"]) for d in docs),
       lesson_type_counts=dict(Counter(d["kind"] for d in docs)),
       historical_deep_lessons=len(older),all_deep_lessons=len(older)+len(docs),
       source_links=links,official_seven_track_atom_denominators={t:None for t in TRACKS},
       teacher_approvals=0,student_authoritative_releases=0,
       general_proof_certificates=0,arbitrary_student_steps_certified=0,
       author_sha256=sha256((ROOT/"scripts/kb_batch113_lesson_authoring.py").read_bytes()).hexdigest(),
       source_scope_sha256=sha256(dump(scope).encode()).hexdigest())
    return docs,a

def coverage(sc=None,a=None):
    if sc is None:sc=source()
    if a is None:a=lessons(scope=sc)[1]
    reg=json.loads(REGISTRY.read_text(encoding="utf8"))
    need({x["printed_page"] for x in reg["pages"]}==set(range(13,74)),
         "61-page official registry missing")
    prior=[json.loads((ROOT/f"docs/evaluation/KB_BATCH{n}_SCOPE.json").read_text(encoding="utf8"))
           for n in (109,110,111,112)]
    pages=set()
    for v in (*prior,sc):
        need(v["source_pdf_sha256"]==PDF_SHA,"source version diverged")
        need(all(x is None for x in v["official_seven_track_atom_denominators"].values()),
             "fictional approved denominator")
        need(v["teacher_approvals"]==0,"fake page review")
        for page in v["line_counts"]:
            need(int(page) not in pages,"duplicated scoped page")
            pages.add(int(page))
    need(len(pages)==10,"five-batch reviewed page counter drift")
    docs,_=lessons(scope=sc)
    completed=[]
    for d in docs:
        obj=DeepLesson.model_validate(d)
        fields={"statement":len(obj.statement)>=50,"assumptions":len(obj.assumptions)>=2,
          "notation":len(obj.notation)>=2,"prerequisites":len(obj.prerequisites)>=2,
          "reasoning":len(obj.proof_steps if obj.kind=="theorem" else obj.rationale_steps)>=3,
          "negative_example":bool(obj.counterexamples),"misconception":bool(obj.misconceptions),
          "two_worked_examples":len(obj.worked_examples)==2,
          "hint_ladder":len(obj.hint_ladder)==3,
          "near_far":bool(obj.transfer.near and obj.transfer.far),
          "license":obj.provenance.permission=="PROJECT_AUTHORED",
          "teacher_only":obj.teacher_solution_visibility=="TEACHER_ONLY"}
        need(all(fields.values()),"lesson not structurally complete "+obj.id)
        completed.append(dict(id=obj.id,field_checks=fields,
          editorial_field_fraction=sum(fields.values())/len(fields),
          review_status="REVIEW_PENDING",general_proof_certified=False,
          teacher_approved=False,student_authoritative=False))
    return dict(batch=113,official_source_pages=61,recent_source_pages=sorted(pages),
      recent_source_pages_fraction=len(pages)/61,
      recent_pages_are_editorial_not_teacher_atomized=True,
      teacher_certified_full_pages=0,
      source_candidate_counts_by_track=sc["candidate_counts_by_track"],
      official_atom_coverage_by_track={t:dict(total=None,approved=0,
         coverage_fraction=None,missing_total="UNKNOWN") for t in TRACKS},
      new_lesson_field_checks=completed,teacher_approved_lessons=0,
      unreviewed_legacy_prerequisites=172,uncertified_legacy_proof_steps=538,
      unresolved_legacy_math_conflicts=10,
      limitations=["10/61 only source text page review in five most recent batches, not atom coverage.",
        "Course denominators of all seven official tracks remain UNKNOWN.",
        "9 structurally complete lesson drafts have zero teacher signoffs and zero formal proof certificates."])

def markdown(scope,docs,audit,cov):
    lines=["# Batch113｜官方课标23/60页及第59页闭椭圆二次函数补缺","",
      "所有内容为项目原创编辑草案；PDF行区间仅定位原课标，不复制课标全文。","",
      "本批页23/60的候选要求与跨页源标记，尚未经真实教师核对；",
      f"{scope['source_lines_total']}条来源行、{len(scope['candidates'])}项编辑候选、{scope['finite_exact_witnesses']}项有限见证。",
      "必修与选修B来源分轨，官方七轨原子分母全部UNKNOWN。","",
      "## 九份完整教师侧候审讲义",""]
    for d,link in zip(docs,audit["source_links"]):
        lines += [f"### {d['id']}｜{d['title']}","",
          f"**来源**：{link['source_candidate_id']}；印刷页{link['source_printed_page']}；轨道{link['source_track_hint']}；工程ID {link['engineering_curriculum_id']}。","",
          "**正式陈述/定义**："+d["statement"],"",
          "**适用假设**："+"；".join(d["assumptions"]),"",
          "**符号**："+"；".join(d["notation"]),"",
          "**先修**："+"；".join(d["prerequisites"]),"",]
        for n,p in enumerate(d["proof_steps"],1):
            lines += [f"**待审证明步骤{n}**：{p['claim']}","依据："+p["reason"],""]
        for n,s in enumerate(d["rationale_steps"],1):lines += [f"**方法/定义讲解{n}**：{s}",""]
        c=d["counterexamples"][0]
        lines += ["**典型错误**："+c["false_claim"],"","**反例**："+c["example"],"",
          "**错误原因**："+c["explanation"],""]
        for n,e in enumerate(d["worked_examples"],1):
            lines += [f"**教师侧例题{n}**：{e['question']}",""]
            for j,s in enumerate(e["steps"],1):lines += [f"{j}. {s}"]
            lines += ["","解答："+e["answer"],"","独立核对："+e["check"],""]
        lines += ["**不剧透三级提示**："+"；".join(d["hint_ladder"]),"",
          "**近迁移**："+d["transfer"]["near"],"",
          "**远迁移**："+d["transfer"]["far"],""]
    lines += ["## 审核边界","",
      "新增候审证明不等于形式证明。教师批准为零、学生权威发布为零，来源PDF原文保留在Mac。","",
      "未完成：所有七轨官方原子分母未知，172条历史先修、538条证明步骤和10项冲突待人工审校。",""]
    return "\n".join(lines)

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--check",action="store_true")
    pa.add_argument("--verify-local-source",action="store_true")
    args=pa.parse_args()
    s=source(verify_local_source=args.verify_local_source)
    d,a=lessons(scope=s);c=coverage(sc=s,a=a)
    for f,data in ((SOURCE_OUT,dump(s)),(PACK,dump(d)),(AUDIT,dump(a)),
                   (COVER,dump(c)),(MD,markdown(s,d,a,c))):
        if args.check:
            need(f.read_text(encoding="utf8")==data,"generated artifact drift "+str(f))
        else:
            f.parent.mkdir(parents=True,exist_ok=True)
            f.write_text(data,encoding="utf8")
    print("Batch113 PASS",s["source_lines_total"],len(s["candidates"]),
          s["finite_exact_witnesses"],len(d),"new drafts",
          a["new_proof_step_candidates"],"uncertified proof steps")
if __name__=="__main__":main()
