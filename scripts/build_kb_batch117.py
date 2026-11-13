#!/usr/bin/env python3
"""Mac-only authoring + reproducible static validation for Batch117.

The source PDF is deliberately never copied into Git; no model may mark teacher approval.
Use --write on Mac, --check in CI; --verify-local-source additionally checks the local PDF.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import sys
import re
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch117_lessons import UNITS
from app.deep_knowledge import DeepLesson,DEEP_DIR,curriculum

PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
PDF_LOCAL=Path("/private/tmp/stem-mentor-official-math-2020-batch51.pdf")
PRIVATE=Path("/private/tmp/kb117_pdfkit_lines_private.json")
OLD=ROOT/"docs/evaluation/KB_BATCH116_SOURCE_INVENTORY.json"
MANIFEST=ROOT/"docs/evaluation/KB_BATCH116_FULL_PDF_FINGERPRINTS.json"
SOURCE=ROOT/"curriculum/highschool_math/k00_batch117_source_triage.json"
CLAUSES=ROOT/"curriculum/highschool_math/k00_batch117_clause_candidates.json"
PACK=DEEP_DIR/"batch117_selective_counting.json"
MATH=ROOT/"docs/evaluation/KB_BATCH117_MATH_EXACT.json"
COVER=ROOT/"docs/evaluation/KB_BATCH117_COVERAGE.json"
MD=ROOT/"docs/evaluation/KB_BATCH117_LESSONS.md"
PAGES={"disjoint_add":(46,21,23),"uniform_product":(46,17,23),"permutations":(46,24,26),
       "combinations":(46,24,26),"binomial":(47,1,3),"conditional":(47,12,16),
       "total_probability":(47,16,19),"hypergeometric":(47,20,26)}
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A",
        "ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
RISK={21:"FORMULA_IMAGE_REVIEW",22:"FORMULA_IMAGE_REVIEW",
      35:"PDFKIT_CONTROL_TEXT_MANUAL_IMAGE_REQUIRED",51:"CROSS_TRACK_BOUNDARY",
      58:"FORMULA_IMAGE_REVIEW",59:"FORMULA_IMAGE_REVIEW",69:"CROSS_TRACK_BOUNDARY",
      73:"ELECTIVE_E_STARTS_MID_PAGE"}
def need(ok,msg):
    if not ok: raise ValueError(msg)
def dump(v):
    return json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def hashfile(f):
    return sha256(Path(f).read_bytes()).hexdigest()
def exact_witnesses():
    R=S.Rational
    x=S.symbols("x",real=True)
    A=S.Matrix([[1,0],[0,0]]);B=S.Matrix([[0,1],[0,0]])
    out={
      "disjoint_add": (len({1,2}|{3,4})==4,len({1,2,3}|{3,4})!=3+2,
                        "non-overlapping categories","overlapping double counts"),
      "uniform_product": (3*2==6,2+4!=2*4,"uniform 3x2 branches","nonuniform branch counts"),
      "permutations": (S.factorial(5)/S.factorial(3)==20,
                        S.factorial(5)/S.factorial(2)!=S.binomial(5,3),
                        "ordered 5P2","unranked group overcount"),
      "combinations": (S.binomial(6,3)==20,S.binomial(5,2)!=5*4,
                        "unranked 6C3","order overcount"),
      "binomial": (S.expand((x+2)**3-(x**3+6*x*x+12*x+8))==0,
                   (A*B+B*A)!=2*A*B,"commutative polynomial","noncommuting matrices"),
      "conditional": (R(2,6)/R(3,6)==R(2,3),
                      R(1,6)/R(3,6)!=R(1,6)/R(1,6),
                      "intersection divided by conditioning event","direction matters"),
      "total_probability": (R(3,4)*R(1,2)+R(1,4)*R(1,2)==R(1,2),
                             len({1,2}|{2,3})!=6,
                             "proper two-branch partition","overlapping nonexhaustive split"),
      "hypergeometric": (sum(S.binomial(2,k)*S.binomial(3,2-k)/S.binomial(5,2) for k in range(3))==1,
                          S.binomial(1,2)*S.binomial(1,0)/S.binomial(2,2)!=R(1,4),
                          "support sums exactly 1","without replacement not binomial"),
    }
    need(set(out)==set(u["key"] for u in UNITS),"math witness key mismatch")
    rows=[]
    for k,(good,bad,goodname,badname) in out.items():
        need(bool(good) and bool(bad),"failed exact witness "+k)
        rows.append({"key":k,"positive_witness":goodname,"counterexample":badname,
                     "positive_exact":True,"negative_exact":True,
                     "status":"FINITE_EXACT_INSTANCE_ONLY","universal_proof_certified":False,
                     "student_free_text_verified":False,"teacher_approved":False})
    return {"batch":117,"cases":rows,"positive_cases":8,"negative_cases":8,
            "proof_certificates":0,"teacher_approvals":0}
def sources(local=False):
    prior=json.loads(OLD.read_text())
    manifest=json.loads(MANIFEST.read_text())
    need(manifest["pdf_sha256"]==PDF_SHA and manifest["pdf_page_count"]==188,
         "188-page signed source mismatch")
    pages=prior["pages"]
    need(len(pages)==61 and [p["printed_page"] for p in pages]==list(range(13,74)),
         "61-page editorial range drift")
    known={p["printed_page"] for p in pages if p["structure_review_status"]!="NOT_REVIEWED"}
    need(len(known)==18,"prior structural review baseline unexpectedly changed")
    fingerprint={p["pdf_page_index"]:p["pdfkit_utf8_sha256"] for p in manifest["pages"]}
    needs=set(range(13,74))-known
    assert len(needs)==43
    counts={}
    if local:
        need(PDF_LOCAL.is_file() and hashfile(PDF_LOCAL)==PDF_SHA,
             "licensed PDF required only for optional local attestation")
        need(PRIVATE.is_file(),"re-extract private PDFKit inventory before local attestation")
        private=json.loads(PRIVATE.read_text())
        need([v["printed_page"] for v in private]==list(range(13,74)),
             "PDFKit inventory print range mismatch")
        counts={v["printed_page"]:v["line_count"] for v in private}
        need(all(v>0 for v in counts.values()),"blank PDFKit page")
    elif SOURCE.is_file():
        counts={p["printed_page"]:p["nonempty_pdfkit_line_count"] for p in json.loads(SOURCE.read_text())["pages"]}
    else:
        raise ValueError("initial --write requires --verify-local-source on authorized Mac")
    rows=[]
    for p in pages:
        number=p["printed_page"];index=p["pdf_page_index"]
        need(index==number+7,"PDF physical-page offset mismatch")
        need(fingerprint[index]==p["pdfkit_text_sha256"],"source changed in baseline")
        need(number in counts and 1<=counts[number]<=200,"missing line count")
        rows.append({"printed_page":number,"pdf_page_index":index,
          "source_pdf_sha256":PDF_SHA,"page_text_sha256":fingerprint[index],
          "nonempty_pdfkit_line_count":counts[number],
          "editorial_track_hint":p["track_hint"],"editorial_group":p["source_group_hint"],
          "prior_structure_review_status":p["structure_review_status"],
          "batch117_status":"PAGE_INDEXED_PENDING_HUMAN_REVIEW" if number in needs
                   else "PRIOR_STRUCTURE_REVIEW_RETAINED",
          "manual_visual_risk":RISK.get(number),
          "official_atomic_denominator":None,"teacher_approved":False,
          "student_authoritative":False})
    return {"batch":117,"source_pdf_sha256":PDF_SHA,"physical_pages_sha_locked":188,
        "editorial_page_range":[13,73],"page_count":61,
        "retained_prior_structure_review_count":18,
        "new_page_line_indices_without_human_structure_review":43,
        "complete_teacher_atomization_pages":0,
        "seven_track_official_atom_denominators":{k:None for k in TRACKS},
        "review_pending_page_numbers":sorted(needs),"pages":rows,
        "copyright_source_text_embedded":False,
        "not_a_coverage_denominator":"No teacher-certified official atom denominator exists; page and draft counts are not official atoms"}
def convert():
    src=sources()
    bypage={r["printed_page"]:r for r in src["pages"]}
    mapping=curriculum()
    if isinstance(mapping,(list,tuple)): cm={z["id"]:z for z in mapping}
    elif isinstance(mapping,dict): cm=mapping
    else:raise ValueError("unexpected curriculum map")
    existing={z["id"] for f in DEEP_DIR.glob("*.json") if f!=PACK for z in json.loads(f.read_text())}
    need(len(UNITS)==8 and len(set(u["key"] for u in UNITS))==8,"8 unique units required")
    docs=[];clause=[]
    for n,u in enumerate(UNITS,1):
        need(u["key"] in PAGES,"unanchored lesson")
        page,start,end=PAGES[u["key"]]
        need(1<=start<=end<=bypage[page]["nonempty_pdfkit_line_count"],"source span outside page")
        need(u["cid"] in cm,"unknown curriculum ID")
        need(cm[u["cid"]]["level"]=="选择性必修","cross-track leakage")
        need(bypage[page]["editorial_track_hint"]=="SELECTIVE_COMPULSORY","wrong page track")
        need(u["kind"] in {"theorem","method","concept"},"illegal knowledge kind")
        need(len(u["statement"])>=65 and len(u["assumptions"])>=2
          and len(u["notation"])>=2 and len(u["prereqs"])>=2,"insufficient formal meaning")
        need(len(u["reasoning"])==3 and len(u["examples"])==2
          and len(u["hints"])==3 and len(set(u["hints"]))==3,"incomplete lesson depth")
        need(len(u["near"])>=20 and len(u["far"])>=20
          and len(u["counterexample"])>=30,"missing transfer/counterexample")
        for e in u["examples"]:
            need(len(e["steps"])>=2 and len(e["check"])>=16,"worked answer incomplete")
        if u["kind"]=="theorem":
            need(all(isinstance(p,tuple) and len(p)==2 and min(map(len,p))>=18 for p in u["reasoning"]),
                 "theorem must give explicit claims and justification")
        else:
            need(all(isinstance(p,str) and len(p)>=24 for p in u["reasoning"]),
                 "method/concept need detailed rationale")
        lid=f"math.hs.batch117.{n:02d}"
        need(lid not in existing,"duplicate lesson ID")
        preds={"uniform_product":["math.hs.batch117.01"],"permutations":["math.hs.batch117.02"],
               "combinations":["math.hs.batch117.03"],"binomial":["math.hs.batch117.04"],
               "total_probability":["math.hs.batch117.06"],
               "hypergeometric":["math.hs.batch117.04"]}.get(u["key"],[])
        need(all(int(x.split(".")[-1])<n for x in preds),"prerequisite cycle")
        doc={"id":lid,"curriculum_ids":[u["cid"]],"kind":u["kind"],
          "title":u["title"],"version":"1.0.0","notation":u["notation"],
          "prerequisites":u["prereqs"],"prerequisite_lesson_ids":preds,
          "definition":u["statement"] if u["kind"]=="concept" else None,
          "statement":u["statement"],"assumptions":u["assumptions"],
          "proof_steps":[{"claim":a,"reason":b} for a,b in u["reasoning"]] if u["kind"]=="theorem" else [],
          "rationale_steps":u["reasoning"] if u["kind"]!="theorem" else [],
          "boundaries":u["assumptions"],
          "counterexamples":[{"false_claim":u["false_claim"],"example":u["counterexample"],
                              "explanation":u["why_wrong"]}],
          "misconceptions":[{"error":u["false_claim"],"why_wrong":u["why_wrong"],
              "repair_question":"逐项检查结果是否有序、可放回、样本划分是否互斥且完整，找出不成立的数学前提。"}],
          "worked_examples":u["examples"],"hint_ladder":u["hints"],
          "transfer":{"near":u["near"],"far":u["far"]},
          "provenance":{"kind":"PROJECT_AUTHORED","permission":"PROJECT_AUTHORED",
             "curriculum_standard":"普通高中数学课程标准（2017年版2020年修订）",
             "standard_url":"https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf",
             "author_role":"PROJECT_AUTHOR"},
          "review":{"status":"REVIEW_PENDING","reviewer_id":None,"reviewed_at":None,
                    "review_record":None},"teacher_solution_visibility":"TEACHER_ONLY"}
        DeepLesson.model_validate(doc)
        docs.append(doc)
        clause.append({"editorial_candidate_id":f"kb117.selective.{n:02d}",
             "lesson_id":lid,"engineering_curriculum_id":u["cid"],
             "printed_page":page,"line_range":[start,end],
             "pdf_page_index":bypage[page]["pdf_page_index"],
             "page_sha256":bypage[page]["page_text_sha256"],
             "track_hint":"SELECTIVE_COMPULSORY","official_atom_id":None,
             "review_status":"REVIEW_PENDING","math_verification":"FINITE_EXACT_INSTANCE_ONLY",
             "teacher_approved":False,
             "boundary_note":"Editorial expansion, not a formally certified official atom"})
    return docs,{"batch":117,"source_sha256":PDF_SHA,"items":clause,
                 "candidate_count":len(clause),"official_certified_atom_count":0}
def is_frozen_prior_pack(path):
    """Exclude Batch117+ from the frozen 490-draft historical denominator.

    A future Batch118 must not mutate the archived Batch117 baseline.
    Untagged historical packs are retained; only explicitly newer numbered
    batch packs are excluded.
    """
    name=Path(path).stem
    match=re.match(r"^batch(\d+)(?:_|$)",name)
    return Path(path)!=PACK and (match is None or int(match.group(1))<117)

def coverage(ds=None,cl=None):
    if ds is None or cl is None:ds,cl=convert()
    old=[r for f in sorted(DEEP_DIR.glob("*.json")) if is_frozen_prior_pack(f)
         for r in json.loads(f.read_text())]
    need(len(old)==490,"deep-draft baseline must not drift")
    return {"batch":117,"prior_deep_drafts":490,"new_deep_drafts":len(ds),
         "total_deep_drafts":len(old)+len(ds),
         "new_teacher_examples":sum(len(d["worked_examples"]) for d in ds),
         "new_hint_levels":sum(len(d["hint_ladder"]) for d in ds),
         "new_transfer_prompts":2*len(ds),"new_counterexamples":len(ds),
         "new_uncertified_proof_steps":sum(len(d["proof_steps"]) for d in ds),
         "teacher_approvals":0,"student_authoritative_releases":0,
         "official_atoms_certified":0,"seven_track_denominators":{x:None for x in TRACKS},
         "candidate_source_links":len(cl["items"]),
         "lessons":[{"id":d["id"],"kind":d["kind"],"review":"REVIEW_PENDING",
                     "teacher_solution_visibility":"TEACHER_ONLY",
                     "complete_structure":True,
                     "proof_steps_certified":0} for d in ds]}
def lesson_md(ds):
    lines=["# Batch117｜组合计数与概率·原创教师候审讲义","",
      "所有内容处于 REVIEW_PENDING / TEACHER_ONLY，不代表真实教师签字或一般证明机器认证。",
      "依据课标2020修订版相关来源页范围进行编辑扩展；课程正式知识原子分母仍未知。",""]
    for d in ds:
        lines.extend(["## "+d["title"],"",
            f"知识ID：{d['id']}；工程课程：{d['curriculum_ids'][0]}；类型：{d['kind']}","",
            "**陈述/定义**："+d["statement"],"",
            "**完整前提**："])
        lines.extend("- "+a for a in d["assumptions"])
        lines.extend(["","**记号**："])
        lines.extend("- "+a for a in d["notation"])
        lines.extend(["","**先修**："])
        lines.extend("- "+a for a in d["prerequisites"])
        lines.extend(["","**"+("分步证明（待审校）" if d["kind"]=="theorem" else "合法性解释与使用范围")+"**："])
        for j,step in enumerate(d["proof_steps"] or d["rationale_steps"],1):
            lines.append(f"{j}. "+(step["claim"]+"（依据："+step["reason"]+"）" if isinstance(step,dict) else step))
        e=d["counterexamples"][0]
        lines.extend(["","**错误说法**："+e["false_claim"],
                      "**反例**："+e["example"],"**错因**："+e["explanation"],""])
        for j,e in enumerate(d["worked_examples"],1):
            lines.extend([f"**例题{j}**：{e['question']}"])
            lines.extend(f"{k+1}. {s}" for k,s in enumerate(e["steps"]))
            lines.extend(["教师答案："+e["answer"],"核验："+e["check"],""])
        lines.extend(["**学生提示（分级，不包含完整教师答案）**："])
        lines.extend(f"{j+1}. {s}" for j,s in enumerate(d["hint_ladder"]))
        lines.extend(["","近迁移："+d["transfer"]["near"],
                      "远迁移："+d["transfer"]["far"],""])
    return "\n".join(lines).rstrip("\n")+"\n"
def generate(local=False):
    sc=sources(local)
    ds,clauses=convert()
    return {SOURCE:sc,CLAUSES:clauses,PACK:ds,MATH:exact_witnesses(),
            COVER:coverage(ds,clauses),MD:lesson_md(ds)}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--write",action="store_true")
    p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local-source",action="store_true")
    a=p.parse_args()
    need(a.write != a.check,"select either --write or --check")
    if a.write:
        need(a.verify_local_source,"only write on Mac with attested original")
        sc=sources(local=True)
        SOURCE.parent.mkdir(parents=True,exist_ok=True)
        SOURCE.write_text(dump(sc))
    generated=generate(local=a.verify_local_source)
    for path,obj in generated.items():
        serialized=obj if isinstance(obj,str) else dump(obj)
        if a.write:path.write_text(serialized)
        else:need(path.exists() and path.read_text()==serialized,
                  "committed artifact drift: "+str(path.relative_to(ROOT)))
    print("BATCH117", "WRITE" if a.write else "CHECK",
          "43 source pages indexed (not human reviewed); 8 original drafts; 16 exact witnesses; official denominator UNKNOWN")
if __name__=="__main__":main()
