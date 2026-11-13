#!/usr/bin/env python3
"""Batch139: eight original high-frequency core/elective teacher manuscripts.

Only Mac --write and --check-mac replay protected official PDFKit source lines.
Offline mode compares committed authorship, source-locks, and fail-closed metadata.
It does NOT certify nationwide official atoms, general mathematical proofs or approval.
"""
from __future__ import annotations
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch138_electives as prior
from build_kb_batch138_electives import PDF, TRACKS, check, encode

AUTHOR = ROOT / "knowledge/editorial_review/kb_batch139_core_authoring.json"
OUT = ROOT / "knowledge/editorial_review/kb_batch139_eight_core_lessons.json"
SAFE = ROOT / "knowledge/editorial_review/kb_batch139_student_safe_index.json"
AUDIT = ROOT / "docs/evaluation/KB_BATCH139_CORE_AUDIT.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH139_EIGHT_CORE_LESSONS.md"
IDS = (
 "hs-semantic-pilot-120-c103", "hs-semantic-pilot-120-c105",
 "hs-semantic-pilot-120-c111", "hs-semantic-pilot-124-c524",
 "hs-semantic-pilot-121-s203", "hs-semantic-pilot-121-s206",
 "hs-semantic-pilot-122-a302", "hs-semantic-pilot-123-a405",
)
EXPECTED = dict(zip(IDS, [
 "COMPULSORY","COMPULSORY","COMPULSORY","COMPULSORY",
 "SELECTIVE_COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_A",
]))
PREREQS = {
 IDS[0]: (), IDS[1]: (), IDS[2]: (), IDS[3]: (),
 IDS[4]: (), IDS[5]: (),
 IDS[6]: ("kb133-proposal-a_continuity",),
 IDS[7]: ("kb133-proposal-c_function_mapping",),
}
GAPS = {
 IDS[0]:"平面向量的模和坐标运算未在有审校证据的先修图中闭环",
 IDS[1]:"二维向量线性运算与线性无关仍缺正式课程ID",
 IDS[2]:"有限样本空间及组合计数的先修审查未闭环",
 IDS[3]:"均值、期望、独立同分布的先修审查未闭环",
 IDS[4]:"平面点向量及法向量的先修审查未闭环",
 IDS[5]:"概率公理与可数可加性的先修审查未闭环",
 IDS[6]:"原函数与黎曼可积性的先修审查未闭环",
 IDS[7]:"有限样本平方误差与统计因果边界的先修审查未闭环",
}
SOURCE_CONTEXT = "PDFKIT_HASHED_NOT_HUMAN_SEMANTICALLY_APPROVED"

@lru_cache(maxsize=1)
def build():
    candidates, locks = prior.contexts()
    authored = json.loads(AUTHOR.read_text(encoding="utf-8"))
    check(tuple(x["id"] for x in authored) == IDS, "missing, extra or reordered eight original author candidates")
    old = prior.build()
    older = prior.prior.build()
    previous_ids = {x["source_candidate_id"] for x in old} | {x["candidate_id"] for x in older["rows"]}
    check(not (set(IDS) & previous_ids), "reused earlier teacher manuscript ID")
    valid_prior = {x["candidate_id"] for x in older["rows"]}
    rows = []
    for a in authored:
        cid = a["id"]; c = candidates[cid]; lock = locks[cid]
        tr = c["course_track"]; src = c["source"]
        check(tr == EXPECTED[cid], "source track/category mismatch")
        check(src["printed_page"]==lock["page"] and src["start_line"]==lock["start_line"] and
              src["end_line"]==lock["end_line"], "source location mismatch")
        check(src["source_span_sha256"]==lock["span_sha256"], "candidate and PDFKit source hash mismatch")
        check(src["original_pdf_sha256"]==PDF,"official PDF version mismatch")
        check(len(lock["line_sha256"])==lock["end_line"]-lock["start_line"]+1, "wrong line span length")
        check(all(re.fullmatch(r"[0-9a-f]{64}",v) for v in [lock["span_sha256"]]+lock["line_sha256"]),
              "bad source line SHA")
        check(a["type"] in {"Theorem","Method","Concept"}, "unsupported manuscript type")
        check(set(PREREQS[cid]) <= valid_prior, "unknown previous proposal prerequisite")
        check(len(a["steps"])==4 and len(a["examples"])==2 and len(a["hints"])==3, "shallow manuscript")
        check(all(len(x["sol"])>=3 for x in a["examples"]), "unfinished teacher explanation")
        for f in ("formal","domain","assumptions","legal","failure","wrong","repair","near","far"):
            check(isinstance(a[f],str) and len(a[f])>=28, "short/invalid author field "+f)
        for s in a["steps"]+a["hints"]+[p for e in a["examples"] for p in e["sol"]]:
            check(isinstance(s,str) and len(s)>=12,"short proof, hint, or derivation")
        rows.append({
          "id":"kb139-deep-"+cid.removeprefix("hs-semantic-pilot-"),
          "source_candidate_id":cid, "course_track":tr,
          "source_pdf_sha256":PDF, "source_printed_page":lock["page"],
          "source_start_line":lock["start_line"], "source_end_line":lock["end_line"],
          "source_span_sha256":lock["span_sha256"],
          "source_line_sha256":lock["line_sha256"],
          "source_evidence_status":SOURCE_CONTEXT,
          "standard_version":"2017-edition-2020-revision-editorial-pilot",
          "knowledge_type":a["type"], "title":a["topic"],
          "formal_definition_or_theorem":a["formal"],
          "notation_and_domain":a["domain"],
          "applicability_and_hypotheses":a["assumptions"],
          "reasoned_steps":[{"step":i+1,"justification":s} for i,s in enumerate(a["steps"])],
          "why_method_is_legal":a["legal"],
          "nonexample_or_failure":a["failure"],
          "typical_wrong_solution":a["wrong"],
          "why_wrong_and_repair":a["repair"],
          "teacher_examples":[{"question":e["q"],"answer":e["a"],"reasoned_solution":e["sol"]} for e in a["examples"]],
          "student_hint_ladder":a["hints"], "near_transfer":a["near"],"far_transfer":a["far"],
          "prerequisite_proposals":list(PREREQS[cid]),
          "missing_prerequisite_gap":GAPS[cid],
          "prerequisite_math_review":"REVIEW_PENDING",
          "teacher_review_status":"REVIEW_PENDING", "teacher_review_evidence":None,
          "teacher_solution_visibility":"TEACHER_ONLY",
          "formal_proof_certified":False, "free_student_step_verified":False,
          "student_authoritative":False, "official_atom_id":None,
        })
    validate(rows)
    return rows

def validate(rows):
    check(len(rows)==8 and len({r["id"] for r in rows})==8, "eight unique lessons required")
    for r in rows:
        check(r["teacher_review_status"]=="REVIEW_PENDING" and r["teacher_review_evidence"] is None
              and r["teacher_solution_visibility"]=="TEACHER_ONLY" and r["official_atom_id"] is None
              and r["student_authoritative"] is False and r["formal_proof_certified"] is False
              and r["free_student_step_verified"] is False and r["prerequisite_math_review"]=="REVIEW_PENDING",
              "attempted unauthorized publication / teacher / proof status")
        check(r["source_pdf_sha256"]==PDF and r["source_evidence_status"]==SOURCE_CONTEXT
              and r["course_track"]==EXPECTED[r["source_candidate_id"]], "forged course source")
        check(len(r["reasoned_steps"])==4 and len(r["teacher_examples"])==2
              and len(r["student_hint_ladder"])==3, "incomplete manuscript")
        check(r["prerequisite_proposals"]==list(PREREQS[r["source_candidate_id"]]),"prerequisite changed")
    return True

def rehash_mac(rows):
    # Protected PDFKit content never reaches GitHub; compare actual line SHA on authorized Mac.
    pages = prior.upstream.prior.previous.prev.prior.prior.previous.source_pages()
    candidates,_ = prior.contexts()
    for r in rows:
        src = candidates[r["source_candidate_id"]]["source"]
        actual = prior.upstream.fingerprint(pages,src)
        check(actual["span_sha256"]==r["source_span_sha256"]
              and actual["line_sha256"]==r["source_line_sha256"]
              and actual["page"]==r["source_printed_page"],
              "Mac original PDFKit source differs from committed certificate")
    return True

def full_inventory(rows):
    older = prior.prior.build()
    old = prior.build()
    combined = [dict(id=x["id"],track=x["course_track"],candidate=x["source_candidate_id"],
                     source_sha=x["source_span_sha256"],review="REVIEW_PENDING") for x in old]
    combined += [dict(id=x["id"],track=x["course_track"],candidate=x["source_candidate_id"],
                      source_sha=x["source_span_sha256"],review="REVIEW_PENDING") for x in rows]
    for r in older["rows"]:
        source = r.get("source_lock",{})
        # A prior bounded candidate has its own authoritative document SHA only in the older ledger.
        combined.append(dict(id=r.get("manuscript_id") or r["candidate_id"],track=r["track"],
                             candidate=r["candidate_id"],source_sha=source.get("span_sha256"),
                             review="REVIEW_PENDING"))
    check(len(combined)==57 and len(set(x["candidate"] for x in combined))==57,
          "57 unique bounded teacher manuscripts required")
    counts = Counter(r["track"] for r in combined)
    return dict(schema="kb139-bounded-author-manuscript-ledger/1",
                scope="57_BOUNDED_EDITED_MANUSCRIPTS_NOT_OFFICIAL_TRACK_DENOMINATORS",
                source_pdf_sha256=PDF, new_manuscripts=8, total_manuscripts=57,
                by_track={k:counts.get(k,0) for k in TRACKS},
                official_atom_denominators={k:None for k in TRACKS},
                official_coverage_rate=None, source_semantics_human_approved=False,
                teacher_approved=0,student_authoritative=0,formal_proof_certified=0,
                student_free_text_verified=0,
                new_examples=16,new_hint_stages=24,new_near_transfer=8,new_far_transfer=8,
                math_exact_witnesses_expected=32, unresolved_prerequisite_cards=8,
                records=sorted(combined,key=lambda r:r["candidate"]))

def safe():
    return dict(status="NO_APPROVED_EVIDENCE",items=[],
                teacher_solution_exposed=False,unverified_content_exposed=False,
                official_denominator=None,student_authoritative=False)

def render(rows,ledger):
    lines=["# Batch139｜必修/选择性必修/选修A：8篇原创教师候审讲义","",
           "**全部是课标锚点的项目编辑候选；不构成国家正式知识原子分母或教师认证。**",
           "原始PDFKit文本仅留在授权Mac；GitHub只保存哈希和原创教学稿。",
           "57份累计候审稿、正式课程分母UNKNOWN、教师批准0、学生发布0、一般定理形式认证0。",""]
    for r in rows:
        lines.extend(["## "+r["title"]+" · "+r["course_track"],"",
           "候选 "+r["source_candidate_id"]+"；印刷页 "+str(r["source_printed_page"])+"，行"+
           str(r["source_start_line"])+"–"+str(r["source_end_line"])+"；原文行摘要 "+r["source_span_sha256"],
           "审核 REVIEW_PENDING；答案 TEACHER_ONLY；非官方正式原子。","",
           "### 精确陈述",r["formal_definition_or_theorem"],"### 记号与论域",r["notation_and_domain"],
           "### 使用前提",r["applicability_and_hypotheses"],"### 逐步论证"])
        lines.extend([str(s["step"])+". "+s["justification"] for s in r["reasoned_steps"]])
        lines.extend(["### 方法合法性",r["why_method_is_legal"],"### 不适用与反例",r["nonexample_or_failure"],
                      "### 典型错法",r["typical_wrong_solution"],"### 错因与修正",r["why_wrong_and_repair"],
                      "### 教师例题（不可直接向学生展示）"])
        for i,e in enumerate(r["teacher_examples"],1):
            lines.extend(["#### 例题 "+str(i),e["question"],"教师参考答案："+e["answer"]])
            lines.extend([str(j)+". "+s for j,s in enumerate(e["reasoned_solution"],1)])
        lines.extend(["### 分层提示（非答案层）"]+
                    [str(i)+". "+s for i,s in enumerate(r["student_hint_ladder"],1)]+
                    ["### 近迁移",r["near_transfer"],"### 远迁移",r["far_transfer"],
                     "先修提案："+(", ".join(r["prerequisite_proposals"]) or "待建立")+
                     "；未闭环："+r["missing_prerequisite_gap"],""])
    lines.extend(["## 课程覆盖与数学证明事实边界","",
                  "按七轨机器统计的57份编辑候审稿，不是正式全国课程知识覆盖率。",
                  "数学Oracle将独立检查32组有限精确见证，不能推断8篇定理的普遍认证。",
                  "未获得教师签字时学生检索保持NO_APPROVED_EVIDENCE。"])
    return "\n".join(lines)+"\n"

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check-offline",action="store_true")
    g.add_argument("--check-mac",action="store_true")
    args=p.parse_args()
    rows=build(); ledger=full_inventory(rows); document=render(rows,ledger)
    if args.write or args.check_mac: rehash_mac(rows)
    if args.write:
        OUT.write_text(encode(rows),encoding="utf-8")
        AUDIT.write_text(encode(ledger),encoding="utf-8")
        SAFE.write_text(encode(safe()),encoding="utf-8")
        REPORT.write_text(document,encoding="utf-8")
    else:
        check(json.loads(OUT.read_text(encoding="utf-8"))==rows,"authored/source manuscript drift")
        check(json.loads(AUDIT.read_text(encoding="utf-8"))==ledger,"bounded denominator or approvals drift")
        check(json.loads(SAFE.read_text(encoding="utf-8"))==safe(),"student index leaked")
        check(REPORT.read_text(encoding="utf-8")==document,"Markdown manuscript incomplete or changed")
    print("PASS Batch139 8 source-locked lessons / 57 bounded manuscripts; official course denominator UNKNOWN",
          "MAC" if args.write or args.check_mac else "OFFLINE")
if __name__=="__main__":main()
