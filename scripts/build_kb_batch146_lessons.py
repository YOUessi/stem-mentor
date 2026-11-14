#!/usr/bin/env python3
"""Batch146 original seven-track deep math lessons; source-hash locked, editor only."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch144_lessons as prior
TRACKS=prior.TRACKS
AUTHOR=ROOT/"knowledge/editorial_review/kb_batch146_ten_authoring.json"
LOCKS=ROOT/"knowledge/editorial_review/kb_batch146_source_line_sha256.json"
OUT=ROOT/"knowledge/editorial_review/kb_batch146_ten_teacher_lessons.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH146_DEPTH_AUDIT.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH146_TEN_MATH_LESSONS.md"
SAFE=ROOT/"knowledge/editorial_review/kb_batch146_student_safe_index.json"
IDS=('hs-semantic-pilot-119-c01', 'hs-semantic-pilot-123-c410', 'hs-semantic-pilot-123-c408', 'hs-semantic-pilot-119-s06', 'hs-semantic-pilot-120-s112', 'hs-semantic-pilot-119-a06', 'hs-semantic-pilot-120-b101', 'hs-semantic-pilot-120-ec103', 'hs-semantic-pilot-120-ed103', 'hs-semantic-pilot-119-ee02')
EXPECTED=dict(zip(IDS,('COMPULSORY',)*3+('SELECTIVE_COMPULSORY',)*2+('ELECTIVE_A','ELECTIVE_B','ELECTIVE_C','ELECTIVE_D','ELECTIVE_E')))
PDF=prior.PDF
def check(ok,message):
    if not ok:raise ValueError("Batch146: "+message)
def encode(obj):return json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
def source_fingerprints():
    # Locally licensed source text stays exclusively on the authorized Mac.
    pages=prior.prior.old.prior.upstream.prior.previous.prev.prior.prior.previous.source_pages()
    contexts,_=prior.prior.source.contexts()
    out={}
    for cid in IDS:
        s=contexts[cid]["source"]
        fp=prior.prior.old.prior.upstream.fingerprint(pages,s)
        out[cid]=dict(page=s["printed_page"],start_line=s["start_line"],
            end_line=s["end_line"],span_sha256=fp["span_sha256"],
            line_sha256=fp["line_sha256"])
    return out
@lru_cache(maxsize=1)
def build():
    contexts,_=prior.prior.source.contexts()
    locks=json.loads(LOCKS.read_text(encoding="utf-8"))
    authored=json.loads(AUTHOR.read_text(encoding="utf-8"))
    check(tuple(a["id"] for a in authored)==IDS,"wrong ten source candidate IDs/order")
    check(set(locks)==set(IDS),"source-lock candidates drift")
    old=prior.audit(prior.build())
    check(old["total_teacher_only_drafts"]==75,"previous inventory has changed")
    used={r["candidate"] for r in old["rows"]}
    check(not used.intersection(IDS),"duplicate candidate vs prior 75")
    rows=[]
    for a in authored:
        cid=a["id"]; c=contexts[cid]; s=c["source"]; lock=locks[cid]
        check(c["course_track"]==EXPECTED[cid],"incorrect course track")
        check(s["original_pdf_sha256"]==PDF,"untrusted official standard version")
        check((lock["page"],lock["start_line"],lock["end_line"],lock["span_sha256"])==
            (s["printed_page"],s["start_line"],s["end_line"],s["source_span_sha256"]),"PDF source span altered")
        check(len(lock["line_sha256"])==s["end_line"]-s["start_line"]+1 and
              all(re.fullmatch("[a-f0-9]{64}",h) for h in [lock["span_sha256"]]+lock["line_sha256"]),
              "source line hashes altered")
        check(a["type"] in ("Concept","Theorem","Method"),"knowledge type invalid")
        for f in ("topic","formal","domain","assumptions","legal","failure","wrong","repair","near","far"):
            check(isinstance(a.get(f),str) and len(a[f])>=(8 if f=="topic" else 20),"missing complete field "+f)
        check(len(a["steps"])==4 and len(a["examples"])==2 and len(a["hints"])==3,"reasoning/teaching cardinality")
        check(all(isinstance(t,str) and len(t)>=18 for t in a["steps"]+a["hints"]),"shallow reasoning or hints")
        check(all(len(e["sol"])>=3 and all(len(t)>=10 for t in e["sol"]) and
                  len(e["q"])>=8 and len(e["a"])>=2 for e in a["examples"]),"shallow teacher examples")
        r=dict(id="kb146-deep-"+cid.removeprefix("hs-semantic-pilot-"),
            source_candidate_id=cid,course_track=c["course_track"],knowledge_type=a["type"],
            title=a["topic"],standard_version="2017-edition-2020-revision-editorial-pilot",
            source_pdf_sha256=PDF,source_printed_page=lock["page"],
            source_start_line=lock["start_line"],source_end_line=lock["end_line"],
            source_span_sha256=lock["span_sha256"],source_line_sha256=lock["line_sha256"],
            source_evidence_status="PDFKIT_HASHED_NOT_HUMAN_SEMANTICALLY_APPROVED",
            official_atom_id=None,source_semantics_human_approved=False,
            formal_definition_or_theorem=a["formal"],notation_and_domain=a["domain"],
            applicability_and_hypotheses=a["assumptions"],why_method_is_legal=a["legal"],
            reasoned_steps=[dict(step=j+1,justification=v) for j,v in enumerate(a["steps"])],
            nonexample_or_failure=a["failure"],typical_wrong_solution=a["wrong"],
            why_wrong_and_repair=a["repair"],
            teacher_examples=[dict(question=e["q"],answer=e["a"],reasoned_solution=e["sol"]) for e in a["examples"]],
            student_hint_ladder=a["hints"],near_transfer=a["near"],far_transfer=a["far"],
            prerequisite_proposals=c["prerequisite_candidate_ids"],prerequisite_math_review="REVIEW_PENDING",
            teacher_review_status="REVIEW_PENDING",teacher_review_evidence=None,
            teacher_solution_visibility="TEACHER_ONLY",formal_proof_certified=False,
            free_student_step_verified=False,student_authoritative=False)
        rows.append(r)
    validate(rows)
    return rows
def validate(rows):
    check(len(rows)==10 and {r["source_candidate_id"] for r in rows}==set(IDS) and
          len({r["id"] for r in rows})==10,"ten unique source-based lessons required")
    known=json.loads(LOCKS.read_text(encoding="utf-8"))
    check(set(known)==set(IDS),"source locks must cover all ten entries")
    for r in rows:
        cid=r["source_candidate_id"]
        check(r["course_track"]==EXPECTED[cid] and r["source_pdf_sha256"]==PDF and r["official_atom_id"] is None
              and r["source_semantics_human_approved"] is False and
              r["source_evidence_status"]=="PDFKIT_HASHED_NOT_HUMAN_SEMANTICALLY_APPROVED","source status fraud")
        check(r["teacher_review_status"]=="REVIEW_PENDING" and
              r["prerequisite_math_review"]=="REVIEW_PENDING" and
              r["teacher_review_evidence"] is None and r["teacher_solution_visibility"]=="TEACHER_ONLY" and
              not r["formal_proof_certified"] and not r["free_student_step_verified"] and
              not r["student_authoritative"],"unauthorized student publishing")
        fp=known[cid]
        check((r["source_printed_page"],r["source_start_line"],r["source_end_line"],r["source_span_sha256"],r["source_line_sha256"])==
              (fp["page"],fp["start_line"],fp["end_line"],fp["span_sha256"],fp["line_sha256"]),
              "original source digest or position mutated")
        for fld in ("title","formal_definition_or_theorem","notation_and_domain",
                    "applicability_and_hypotheses","why_method_is_legal","nonexample_or_failure",
                    "typical_wrong_solution","why_wrong_and_repair","near_transfer","far_transfer"):
            check(isinstance(r.get(fld),str) and len(r[fld])>=(8 if fld=="title" else 20),
                  "shallow or missing field "+fld)
        check(len(r["reasoned_steps"])==4 and all(isinstance(z.get("justification"),str) and
              len(z["justification"])>=18 and z.get("step")==j+1
              for j,z in enumerate(r["reasoned_steps"])),"missing reasoned proof-step details")
        check(len(r["student_hint_ladder"])==3 and
              all(isinstance(z,str) and len(z)>=18 for z in r["student_hint_ladder"]),"missing student hints")
        check(len(r["teacher_examples"])==2 and all(isinstance(e.get("question"),str) and len(e["question"])>=8
            and isinstance(e.get("answer"),str) and len(e["answer"])>=2
            and len(e.get("reasoned_solution",[]))>=3
            and all(isinstance(z,str) and len(z)>=10 for z in e["reasoned_solution"])
            for e in r["teacher_examples"]),"missing teacher-only example details")
        check(len(r["teacher_examples"])==2 and len(r["student_hint_ladder"])==3
              and len(r["reasoned_steps"])==4,"invalid teaching payload")
    return True
def audit(rows):
    old=prior.audit(prior.build())
    new=[dict(id=r["id"],candidate=r["source_candidate_id"],track=r["course_track"],
              source_sha=r["source_span_sha256"],review="REVIEW_PENDING") for r in rows]
    all_rows=old["rows"]+new
    check(len(all_rows)==85 and len({r["candidate"] for r in all_rows})==85,"inventory 85 drift")
    counts=Counter(r["track"] for r in all_rows)
    return dict(schema="kb146-seven-track-ten-lesson-audit/1",total_teacher_only_drafts=85,
        prior_teacher_only_drafts=75,new_original_manuscripts=10,
        by_track={t:counts.get(t,0) for t in TRACKS},
        official_atom_denominators={t:None for t in TRACKS},
        official_coverage_rate=None,teacher_approved=0,student_authoritative=0,
        free_student_steps_verified=0,formal_general_proofs_certified=0,
        new_teacher_examples=20,new_student_safe_hint_steps=30,new_near_far_tasks=20,
        source_semantics_human_approved=False,rows=sorted(all_rows,key=lambda r:r["candidate"]))
def student_safe():
    return dict(status="NO_APPROVED_EVIDENCE",items=[],teacher_solution_exposed=False,
        unpublished_manuscripts_exposed=False,official_coverage_rate=None,student_authoritative=False)
def render(rows,ledger):
    lines=["# Batch146｜七轨10份原创深度候审讲义","",
       "原始课标本地PDFKit行SHA只确认来源位置，不是官方数学原子认定或教师审核。",
       "累计85份候审稿；官方七轨分母UNKNOWN；教师批准0；学生发布0。",""]
    for r in rows:
        lines.extend(["## "+r["title"]+" · "+r["course_track"],"",
          "候选："+r["source_candidate_id"]+"；来源印刷页"+
          str(r["source_printed_page"])+"行"+str(r["source_start_line"])+
          "–"+str(r["source_end_line"])+"；SHA256 "+r["source_span_sha256"],
          "状态：REVIEW_PENDING / TEACHER_ONLY；未形式证明认证。","",
          "### 正式定义或陈述",r["formal_definition_or_theorem"],"",
          "### 论域与适用条件",r["notation_and_domain"],r["applicability_and_hypotheses"],"",
          "### 数学合法性",r["why_method_is_legal"],"","### 分步论证"])
        lines.extend([str(v["step"])+". "+v["justification"] for v in r["reasoned_steps"]])
        lines.extend(["","### 不适用例",r["nonexample_or_failure"],"",
           "### 典型错法与修正",r["typical_wrong_solution"],r["why_wrong_and_repair"],"",
           "### 教师完整例题（学生独立挑战不得访问）"])
        for i,e in enumerate(r["teacher_examples"],1):
            lines.append("**例题"+str(i)+"："+e["question"]+"**")
            lines.extend([str(j)+". "+x for j,x in enumerate(e["reasoned_solution"],1)])
            lines.append("教师参考答案："+e["answer"])
        lines.extend(["","### 学生安全提示阶梯"])
        lines.extend([str(j)+". "+x for j,x in enumerate(r["student_hint_ladder"],1)])
        lines.extend(["","### 迁移","近迁移："+r["near_transfer"],
            "远迁移："+r["far_transfer"],""])
    lines.extend(["## 验收边界","10份候审稿无法替代七轨全国分母；有限代数见证不是普适证明；真实教师尚未审核。",""])
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser()
    a=p.add_mutually_exclusive_group(required=True)
    a.add_argument("--write",action="store_true")
    a.add_argument("--check",action="store_true")
    a.add_argument("--check-mac",action="store_true")
    a.add_argument("--init-source-locks",action="store_true")
    args=p.parse_args()
    if args.init_source_locks:
        LOCKS.write_text(encode(source_fingerprints()),encoding="utf-8")
        print("PASS original private PDF source fingerprints captured without raw text")
        return
    rows=build(); led=audit(rows)
    if args.write:
        OUT.write_text(encode(rows),encoding="utf-8")
        AUDIT.write_text(encode(led),encoding="utf-8")
        REPORT.write_text(render(rows,led),encoding="utf-8")
        SAFE.write_text(encode(student_safe()),encoding="utf-8")
    else:
        check(json.loads(OUT.read_text(encoding="utf-8"))==rows,"lesson content drift")
        check(json.loads(AUDIT.read_text(encoding="utf-8"))==led,"coverage audit drift")
        check(REPORT.read_text(encoding="utf-8")==render(rows,led),"report drift")
        check(json.loads(SAFE.read_text(encoding="utf-8"))==student_safe(),"student safe default drift")
        if args.check_mac:
            check(source_fingerprints()==json.loads(LOCKS.read_text(encoding="utf-8")),"Mac PDF lines disagree")
            print("PDF REHASHED original lines PASS (licensed Mac source not uploaded)")
    print("PASS Batch146: 10 seven-track source-hashed teacher lessons, 85 REVIEW_PENDING, 0 APPROVED")
if __name__=="__main__":main()
