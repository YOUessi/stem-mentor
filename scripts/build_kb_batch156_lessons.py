#!/usr/bin/env python3
"""KB156: ten original, teacher-only manuscripts; 315 official layout markers remain unreviewed.

The 2020 standard is never committed. Only the authorized Mac replays PDFKit
source-line hashes. This builder cannot approve content or certify proofs.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch154_lessons as old
import build_kb_batch155_review_matrix as source
TRACKS=old.TRACKS
PDF=old.PDF
AUTHOR=ROOT/"knowledge/editorial_review/kb_batch156_ten_authoring.jsonl"
LOCKS=ROOT/"knowledge/editorial_review/kb_batch156_source_line_sha256.json"
OUT=ROOT/"knowledge/editorial_review/kb_batch156_ten_teacher_lessons.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH156_DEPTH_AUDIT.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH156_TEN_MATH_LESSONS.md"
SAFE=ROOT/"knowledge/editorial_review/kb_batch156_student_safe_index.json"
IDS=(
"hs-semantic-pilot-121-c202","hs-semantic-pilot-122-c302",
"hs-semantic-pilot-122-c304","hs-semantic-pilot-122-c310",
"hs-semantic-pilot-119-s05","hs-semantic-pilot-119-s08",
"hs-semantic-pilot-119-s11","hs-semantic-pilot-120-a102",
"hs-semantic-pilot-120-b104","hs-semantic-pilot-120-ec102",
)
EXPECTED=dict(zip(IDS,("COMPULSORY",)*4+("SELECTIVE_COMPULSORY",)*3+
                  ("ELECTIVE_A","ELECTIVE_B","ELECTIVE_C")))
EVIDENCE="PDFKIT_HASHED_NOT_HUMAN_SEMANTICALLY_APPROVED"
HEX=re.compile(r"^[0-9a-f]{64}$")

def check(ok,msg):
    if not ok: raise ValueError("KB156 fail closed: "+msg)

def encode(x):
    return json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n"

def authored():
    rows=[json.loads(line) for line in AUTHOR.read_text(encoding="utf-8").splitlines() if line.strip()]
    check(tuple(x["id"] for x in rows)==IDS,"wrong, duplicated or missing original manuscript candidate")
    return rows

def actual_mac_line_locks():
    # Stable PDFKit page extractor introduced in earlier source-evidence batches.
    # Never store full PDFKit text, only original source page/line SHA-256 hashes.
    up=old.previous.previous.previous.previous.previous.prior.prior.prior.old.prior.upstream
    pages=up.prior.previous.prev.prior.prior.previous.source_pages()
    contexts=old.contexts()
    result={}
    for cid in IDS:
        r=contexts[cid]["source"]
        fp=up.fingerprint(pages,r)
        check(fp["span_sha256"]==r["source_span_sha256"],"PDF source span changed: "+cid)
        result[cid]=dict(page=r["printed_page"],start_line=r["start_line"],
             end_line=r["end_line"],span_sha256=fp["span_sha256"],
             line_sha256=fp["line_sha256"])
    return result

@lru_cache(maxsize=1)
def build():
    a=authored()
    locks=json.loads(LOCKS.read_text(encoding="utf-8"))
    contexts=old.contexts()
    prior=old.audit(old.build())
    existing={x["candidate"] for x in prior["rows"]}
    check(prior["total_teacher_only_drafts"]==145,"previous 145 manuscripts drift")
    check(not existing.intersection(IDS),"candidate already authored")
    check(set(locks)==set(IDS),"source lock missing or invented")
    missing=set(json.loads((ROOT/"docs/evaluation/KB_BATCH154_SOURCE_TO_DRAFT_GAPS.json").read_text())["unmatched_candidate_ids"])
    check(set(IDS)<=missing,"selected source previously covered")
    result=[]
    for d in a:
        cid=d["id"];ctx=contexts[cid];r=ctx["source"];lock=locks[cid]
        check(ctx["course_track"]==EXPECTED[cid],"track mismatch "+cid)
        check(r["original_pdf_sha256"]==PDF,"mixed official PDF version")
        check((lock["page"],lock["start_line"],lock["end_line"],lock["span_sha256"])==
              (r["printed_page"],r["start_line"],r["end_line"],r["source_span_sha256"]),
              "source span mismatch "+cid)
        check(len(lock["line_sha256"])==lock["end_line"]-lock["start_line"]+1 and
              all(HEX.fullmatch(h) for h in lock["line_sha256"]+[lock["span_sha256"]]),
              "source line hashes missing")
        check(d["type"] in ("Concept","Theorem","Method"),"unknown knowledge kind")
        for k in ("topic","formal","domain","assumptions","legal","failure","wrong","repair","near","far"):
            check(isinstance(d.get(k),str) and len(d[k])>=(8 if k=="topic" else 20),
                  "missing teaching substance "+cid+" "+k)
        check(len(d["steps"])==4 and len(d["examples"])==2 and len(d["hints"])==3,
              "incomplete proof/examples/hints "+cid)
        check(all(isinstance(x,str) and len(x)>=18 for x in d["steps"]+d["hints"]),
              "shallow explanation/hint "+cid)
        check(all(len(e["sol"])>=3 and len(e["q"])>=8 and len(e["a"])>=2 and
                  all(len(s)>=10 for s in e["sol"]) for e in d["examples"]),
              "teacher examples incomplete "+cid)
        result.append(dict(
          id="kb156-deep-"+cid.removeprefix("hs-semantic-pilot-"),
          source_candidate_id=cid,course_track=ctx["course_track"],
          knowledge_type=d["type"],title=d["topic"],
          standard_version="2017-edition-2020-revision-editorial-pilot",
          source_pdf_sha256=PDF,source_printed_page=lock["page"],
          source_start_line=lock["start_line"],source_end_line=lock["end_line"],
          source_span_sha256=lock["span_sha256"],source_line_sha256=lock["line_sha256"],
          source_evidence_status=EVIDENCE,official_atom_id=None,
          source_semantics_human_approved=False,
          formal_definition_or_theorem=d["formal"],notation_and_domain=d["domain"],
          applicability_and_hypotheses=d["assumptions"],why_method_is_legal=d["legal"],
          reasoned_steps=[dict(step=i+1,justification=s) for i,s in enumerate(d["steps"])],
          nonexample_or_failure=d["failure"],typical_wrong_solution=d["wrong"],
          why_wrong_and_repair=d["repair"],
          teacher_examples=[dict(question=e["q"],answer=e["a"],
                reasoned_solution=e["sol"]) for e in d["examples"]],
          student_hint_ladder=d["hints"],near_transfer=d["near"],far_transfer=d["far"],
          prerequisite_proposals=ctx["prerequisite_candidate_ids"],
          prerequisite_math_review="REVIEW_PENDING",
          teacher_review_status="REVIEW_PENDING",teacher_review_evidence=None,
          teacher_solution_visibility="TEACHER_ONLY",
          formal_proof_certified=False,free_student_step_verified=False,
          student_authoritative=False,
          elective_e_optional_example=ctx["elective_e_optional_example"]))
    validate(result)
    return result

def validate(rows):
    check(len(rows)==10 and len({r["id"] for r in rows})==10 and
          {r["source_candidate_id"] for r in rows}==set(IDS),"incomplete original content")
    locks=json.loads(LOCKS.read_text(encoding="utf-8"))
    for r in rows:
        cid=r["source_candidate_id"];lock=locks[cid]
        check(r["course_track"]==EXPECTED[cid] and
              r["source_pdf_sha256"]==PDF and
              r["source_evidence_status"]==EVIDENCE,"provenance invalid")
        check((r["source_printed_page"],r["source_start_line"],r["source_end_line"],
               r["source_span_sha256"],r["source_line_sha256"])==
              (lock["page"],lock["start_line"],lock["end_line"],
               lock["span_sha256"],lock["line_sha256"]),"source forged")
        check(r["teacher_review_status"]=="REVIEW_PENDING" and
              r["teacher_review_evidence"] is None and
              r["prerequisite_math_review"]=="REVIEW_PENDING" and
              r["teacher_solution_visibility"]=="TEACHER_ONLY" and
              r["source_semantics_human_approved"] is False and
              r["official_atom_id"] is None and
              r["formal_proof_certified"] is False and
              r["free_student_step_verified"] is False and
              r["student_authoritative"] is False and
              r["elective_e_optional_example"] is False,
              "forged teacher approval, theorem proof or student visibility")
        check(len(r["reasoned_steps"])==4 and len(r["teacher_examples"])==2
              and len(r["student_hint_ladder"])==3,"missing learning assets")
        for k in ("formal_definition_or_theorem","notation_and_domain",
                  "applicability_and_hypotheses","why_method_is_legal",
                  "nonexample_or_failure","typical_wrong_solution",
                  "why_wrong_and_repair","near_transfer","far_transfer"):
            check(isinstance(r[k],str) and len(r[k])>=20,"missing required field "+k)
    return True

def audit(rows):
    prev=old.audit(old.build())
    base=prev["rows"]
    additions=[dict(id=r["id"],candidate=r["source_candidate_id"],
                    track=r["course_track"],source_sha=r["source_span_sha256"],
                    review="REVIEW_PENDING") for r in rows]
    allrows=base+additions
    check(len(allrows)==155 and len({r["candidate"] for r in allrows})==155,
          "cumulative candidate count inconsistent")
    counts=Counter(r["track"] for r in allrows)
    src=source.build()
    check(src["numbered_source_layout_markers"]==315 and
          src["historical_editorial_leads"]==239 and
          src["teacher_only_manuscripts"]==145 and
          not src["official_source_scope_complete"],"K00 source review drift")
    return dict(schema="kb156-original-teacher-only-drafts/1",
       previous_teacher_only_drafts=145,added_original_manuscripts=10,
       total_teacher_only_drafts=155,
       by_track={t:counts[t] for t in TRACKS},
       source_numbered_markers_not_official_atoms=315,
       historical_editorial_leads=239,
       historical_candidates_with_drafts=114,
       historical_candidates_without_drafts=125,
       official_atom_denominators={t:None for t in TRACKS},
       official_coverage_rate=None,source_semantics_human_approved=False,
       teacher_approved=0,student_authoritative=0,
       general_proof_certified=0,student_free_text_steps_verified=0,
       new_teacher_examples=20,new_student_safe_hint_steps=30,new_near_far_tasks=20,
       rows=sorted(allrows,key=lambda r:r["candidate"]))

def to_markdown(rows):
    a=audit(rows)
    out=["# KB156｜10份跨主题原创深度教师候审讲义（不是已批准课标知识原子）",
         "",
         "145→155份候审稿；新增20道教师例题、30级启发提示、20项近远迁移。",
         "全部 REVIEW_PENDING / TEACHER_ONLY；未经过教师签字；有限数学验证不等于一般证明。",
         "官方课标七轨原子分母仍 UNKNOWN，315是排版编号锚而非知识原子分母。",
         ""]
    for r in rows:
        out += ["## "+r["title"],"",
            "来源候选 `"+r["source_candidate_id"]+"`；轨道 `"+r["course_track"]+
            "`；课标印刷页 "+str(r["source_printed_page"])+" / PDFKit行 "+
            str(r["source_start_line"])+"–"+str(r["source_end_line"])+
            "；锁定SHA256 `"+r["source_span_sha256"]+"`。","",
            "**审核：REVIEW_PENDING / TEACHER_ONLY；非官方已冻结原子。**","",
            "### 正式陈述",r["formal_definition_or_theorem"],"",
            "### 符号、定义域及对象",r["notation_and_domain"],"",
            "### 假设与适用边界",r["applicability_and_hypotheses"],"",
            "### 数学依据与合法性",r["why_method_is_legal"],"",
            "### 分步证明或论证"]
        for s in r["reasoned_steps"]:
            out.append(str(s["step"])+". "+s["justification"])
        out+=["","### 失效条件与反例",r["nonexample_or_failure"],"",
              "### 典型错解",r["typical_wrong_solution"],"",
              "### 错因与修复",r["why_wrong_and_repair"],"",
              "### 教师例题（学生自主挑战禁止直接索引）"]
        for i,e in enumerate(r["teacher_examples"]):
            out += ["**例"+str(i+1)+"：** "+e["question"],"**答案：** "+e["answer"]]
            out += ["- "+s for s in e["reasoned_solution"]]
        out+=["","### 学生启发提示（不含答案）"]
        for i,h in enumerate(r["student_hint_ladder"]):
            out.append(str(i+1)+". "+h)
        out+=["","### 近迁移",r["near_transfer"],"",
              "### 远迁移",r["far_transfer"],""]
    return "\n".join(out).rstrip()+"\n"

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write-mac",action="store_true")
    g.add_argument("--check-mac",action="store_true")
    g.add_argument("--check",action="store_true")
    x=p.parse_args()
    if x.write_mac:
        LOCKS.write_text(encode(actual_mac_line_locks()),encoding="utf-8")
    if x.check_mac:
        check(json.loads(LOCKS.read_text(encoding="utf-8"))==actual_mac_line_locks(),
              "Mac original PDFKit hash replay differs")
    rows=build()
    a=audit(rows)
    safe=[dict(id=r["id"],source_candidate_id=r["source_candidate_id"],
               course_track=r["course_track"],title=r["title"],
               review_status="REVIEW_PENDING",student_authoritative=False,
               teacher_solution_exposed=False) for r in rows]
    expected=((OUT,encode(rows)),(AUDIT,encode(a)),(REPORT,to_markdown(rows)),
              (SAFE,encode(safe)))
    if x.write_mac:
        for file,data in expected:
            file.write_text(data,encoding="utf-8")
    else:
        for file,data in expected:
            check(file.read_text(encoding="utf-8")==data,
                  "versioned artifact source drift "+str(file))
    print("PASS KB156 ten source-locked deep drafts; 155 pending; 315 layout markers not atoms")

if __name__=="__main__":main()
