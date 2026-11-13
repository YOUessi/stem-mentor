#!/usr/bin/env python3
"""Batch143 source-locked ORIGINAL editor-only math manuscripts, not official approvals."""
from __future__ import annotations
import argparse
from collections import Counter
from functools import lru_cache
import json
import re
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch138_electives as source
import build_kb_batch139_core as old
TRACKS=tuple(old.TRACKS)
AUTHOR=ROOT/"knowledge/editorial_review/kb_batch143_eight_authoring.json"
LOCKS=ROOT/"knowledge/editorial_review/kb_batch143_source_line_sha256.json"
OUT=ROOT/"knowledge/editorial_review/kb_batch143_eight_teacher_lessons.json"
SAFE=ROOT/"knowledge/editorial_review/kb_batch143_student_safe_index.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH143_DEPTH_AUDIT.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH143_EIGHT_MATH_LESSONS.md"
IDS=("hs-semantic-pilot-121-c203","hs-semantic-pilot-123-c404",
     "hs-semantic-pilot-120-c108","hs-semantic-pilot-124-c521",
     "hs-semantic-pilot-120-s107","hs-semantic-pilot-122-s305",
     "hs-semantic-pilot-120-a108","hs-semantic-pilot-120-ed105")
EXPECTED=dict(zip(IDS,(
 "COMPULSORY","COMPULSORY","COMPULSORY","COMPULSORY",
 "SELECTIVE_COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_D"
)))
EVIDENCE="PDFKIT_HASHED_NOT_HUMAN_SEMANTICALLY_APPROVED"
def check(condition,message):
    if not condition: raise ValueError(message)
def encode(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
@lru_cache(maxsize=1)
def build():
    c,_=source.contexts()
    lock=json.loads(LOCKS.read_text(encoding="utf-8"))
    authored=json.loads(AUTHOR.read_text(encoding="utf-8"))
    check(tuple(x["id"] for x in authored)==IDS,"wrong authoring order/count")
    previous=json.loads(old.AUDIT.read_text(encoding="utf-8"))
    used={v["candidate"] for v in previous["records"]}
    check(not (used&set(IDS)),"candidate already used in previous 57 teacher manuscripts")
    check(previous["total_manuscripts"]==57,"prior teacher inventory mismatch")
    rows=[]
    for a in authored:
        cid=a["id"]
        s=c[cid]["source"]; loc=lock[cid]; tr=c[cid]["course_track"]
        check(tr==EXPECTED[cid],"untrusted/mismatched track")
        check(s["original_pdf_sha256"]==old.PDF,"wrong original source standard")
        check((s["printed_page"],s["start_line"],s["end_line"],s["source_span_sha256"])==
              (loc["page"],loc["start_line"],loc["end_line"],loc["span_sha256"]),"source location and hashes differ")
        check(len(loc["line_sha256"])==loc["end_line"]-loc["start_line"]+1,"source line span mismatch")
        check(all(re.fullmatch("[a-f0-9]{64}",x) for x in loc["line_sha256"]+[loc["span_sha256"]]),"bad hash")
        check(a["type"] in {"Concept","Theorem","Method"},"unsupported type")
        check(len(a["steps"])==4 and len(a["examples"])==2 and len(a["hints"])==3,"incomplete exposition")
        check(all(len(e["sol"])>=3 and len(e["a"])>=2 for e in a["examples"]),"shallow answers")
        for f in ("topic","formal","domain","assumptions","legal","failure","wrong","repair","near","far"):
            check(isinstance(a[f],str) and len(a[f])>=(8 if f=="topic" else 25),"insufficient authored "+f)
        for s0 in a["steps"]+a["hints"]+[v for e in a["examples"] for v in e["sol"]]:
            check(isinstance(s0,str) and len(s0)>=10,"shallow steps/hints")
        rows.append(dict(
            id="kb143-deep-"+cid.removeprefix("hs-semantic-pilot-"),
            source_candidate_id=cid,course_track=tr,knowledge_type=a["type"],title=a["topic"],
            standard_version="2017-edition-2020-revision-editorial-pilot",
            source_pdf_sha256=old.PDF,source_printed_page=loc["page"],
            source_start_line=loc["start_line"],source_end_line=loc["end_line"],
            source_span_sha256=loc["span_sha256"],source_line_sha256=loc["line_sha256"],
            source_evidence_status=EVIDENCE,
            official_atom_id=None,source_semantics_human_approved=False,
            formal_definition_or_theorem=a["formal"],notation_and_domain=a["domain"],
            applicability_and_hypotheses=a["assumptions"],
            why_method_is_legal=a["legal"],
            reasoned_steps=[dict(step=i+1,justification=s) for i,s in enumerate(a["steps"])],
            nonexample_or_failure=a["failure"],typical_wrong_solution=a["wrong"],
            why_wrong_and_repair=a["repair"],
            teacher_examples=[dict(question=e["q"],answer=e["a"],reasoned_solution=e["sol"])
                              for e in a["examples"]],
            student_hint_ladder=a["hints"],near_transfer=a["near"],far_transfer=a["far"],
            prerequisite_proposals=c[cid]["prerequisite_candidate_ids"],
            prerequisite_math_review="REVIEW_PENDING",
            teacher_review_status="REVIEW_PENDING",teacher_review_evidence=None,
            teacher_solution_visibility="TEACHER_ONLY",
            formal_proof_certified=False,free_student_step_verified=False,
            student_authoritative=False
        ))
    validate(rows)
    return rows
def validate(rows):
    check(len(rows)==8 and len({r["id"] for r in rows})==8,"wrong row count/duplicates")
    for r in rows:
        check(r["source_candidate_id"] in IDS and r["course_track"]==EXPECTED[r["source_candidate_id"]],"wrong source track")
        check(r["source_evidence_status"]==EVIDENCE and r["source_pdf_sha256"]==old.PDF
            and r["official_atom_id"] is None and r["source_semantics_human_approved"] is False,
            "source/evidence fraud")
        check(r["teacher_review_status"]=="REVIEW_PENDING" and r["teacher_review_evidence"] is None
            and r["teacher_solution_visibility"]=="TEACHER_ONLY"
            and r["prerequisite_math_review"]=="REVIEW_PENDING"
            and r["formal_proof_certified"] is False and r["free_student_step_verified"] is False
            and r["student_authoritative"] is False,"unauthorized promotion")
        check(len(r["reasoned_steps"])==4 and len(r["student_hint_ladder"])==3
            and len(r["teacher_examples"])==2 and all(len(v["reasoned_solution"])>=3 for v in r["teacher_examples"]),
            "missing teaching/proof fields")
    return True
def audit(rows):
    prev=json.loads(old.AUDIT.read_text(encoding="utf-8"))
    ours=[dict(id=r["id"],candidate=r["source_candidate_id"],track=r["course_track"],
               source_sha=r["source_span_sha256"],review="REVIEW_PENDING") for r in rows]
    all_rows=prev["records"]+ours
    check(len(all_rows)==65 and len({r["candidate"] for r in all_rows})==65,"65 unique manuscript candidates")
    counts=Counter(r["track"] for r in all_rows)
    return dict(schema="kb143-depth-and-risk/1",
        total_teacher_only_drafts=65,new_original_manuscripts=8,
        by_track={t:counts.get(t,0) for t in TRACKS},
        official_atom_denominators={t:None for t in TRACKS},
        official_coverage_rate=None,teacher_approved=0,student_authoritative=0,
        student_free_text_verified=0,general_proof_certified=0,
        new_teacher_examples=16,new_hint_stages=24,
        new_near_far_transfer_tasks=16,source_context_human_approved=False,
        prior_finite_manuscripts=57,
        unsupported_claim="65 editor-only manuscripts do not form a complete official syllabus",
        rows=sorted(all_rows,key=lambda r:r["candidate"]))
def safe():
    return dict(status="NO_APPROVED_EVIDENCE",items=[],teacher_solution_exposed=False,
                unverified_content_exposed=False,official_coverage_rate=None,
                student_authoritative=False)
def render(rows,ledger):
    lines=["# Batch143｜跨主题8篇原创教师候审数学讲义","",
      "**课程编号候选的PDFKit哈希仅锁定来源行，不代表语义确认或教师审核。**",
      "累计65篇教师候审稿；正式官方原子分母UNKNOWN；教师批准0、学生权威发布0。",""]
    for r in rows:
        lines.extend(["## "+r["title"]+" · "+r["course_track"],"",
          "来源候选："+r["source_candidate_id"]+"；印刷页"+str(r["source_printed_page"])+
          "，行"+str(r["source_start_line"])+"–"+str(r["source_end_line"])+
          "；SHA-256 "+r["source_span_sha256"],
          "审核：REVIEW_PENDING；完整解答：TEACHER_ONLY；形式认证：否。","",
          "### 正式陈述",r["formal_definition_or_theorem"],"",
          "### 记号、论域与前提",r["notation_and_domain"],r["applicability_and_hypotheses"],"",
          "### 数学合法性",r["why_method_is_legal"],"",
          "### 逐步推理"])
        lines.extend([str(s["step"])+". "+s["justification"] for s in r["reasoned_steps"]])
        lines.extend(["","### 非例与失效前提",r["nonexample_or_failure"],"",
             "### 典型错误与修复",r["typical_wrong_solution"],r["why_wrong_and_repair"],"",
             "### 教师例题（不得直出给学生独立挑战）"])
        for j,e in enumerate(r["teacher_examples"],1):
            lines.extend(["**例题"+str(j)+"："+e["question"]+"**"])
            lines.extend([str(i)+". "+s for i,s in enumerate(e["reasoned_solution"],1)])
            lines.append("教师参考答案："+e["answer"])
        lines.extend(["","### 学生逐级提示（不含最终答案）"])
        lines.extend([str(i)+". "+s for i,s in enumerate(r["student_hint_ladder"],1)])
        lines.extend(["","### 迁移","近迁移："+r["near_transfer"],"远迁移："+r["far_transfer"],""])
    lines.extend(["## 本批验收界限",
      "这8篇不替代课标全量原子审查；SymPy/穷举案例不等于普适证明；须经真实教师正式审核方可学生发布。","",
      "## 下一批", "七轨课标原子拆分/跨页去重；历史538条证明步骤的逐步一般论证；继续扩课、题族和独立RAG评测。",""])
    return "\n".join(lines)
def check_mac_source(rows):
    # Match against original PDFKit-extracted lines on Mac. Never commit original text.
    pages=old.prior.upstream.prior.previous.prev.prior.prior.previous.source_pages()
    contexts,_=source.contexts()
    for r in rows:
        actual=old.prior.upstream.fingerprint(pages,contexts[r["source_candidate_id"]]["source"])
        check(actual["span_sha256"]==r["source_span_sha256"]
           and actual["line_sha256"]==r["source_line_sha256"],"Mac original PDF differs")
    return True
def main():
    ap=argparse.ArgumentParser()
    action=ap.add_mutually_exclusive_group(required=True)
    action.add_argument("--write",action="store_true")
    action.add_argument("--check",action="store_true")
    action.add_argument("--check-mac",action="store_true")
    args=ap.parse_args()
    rows=build(); led=audit(rows)
    if args.write:
        OUT.write_text(encode(rows),encoding="utf-8")
        AUDIT.write_text(encode(led),encoding="utf-8")
        REPORT.write_text(render(rows,led),encoding="utf-8")
        SAFE.write_text(encode(safe()),encoding="utf-8")
    else:
        check(json.loads(OUT.read_text(encoding="utf-8"))==rows,"lesson drift")
        check(json.loads(AUDIT.read_text(encoding="utf-8"))==led,"denominator/coverage drift")
        check(REPORT.read_text(encoding="utf-8")==render(rows,led),"human report drift")
        check(json.loads(SAFE.read_text(encoding="utf-8"))==safe(),"student guard drift")
        if args.check_mac:check_mac_source(rows)
    print("PASS Batch143: 8 rigorous original lessons, 65 editor-only drafts, UNKNOWN official denominators")
if __name__=="__main__":main()
