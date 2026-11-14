#!/usr/bin/env python3
"""Batch151: ten source-locked original teacher manuscripts (NOT reviewed official syllabus atoms).

All mathematically substantial authoring is in knowledge/editorial_review/kb_batch151_ten_authoring.json.
Licensed source text remains on the authorized Mac; versioned evidence contains only hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch149_lessons as previous

TRACKS = previous.TRACKS
PDF = previous.PDF
AUTHOR = ROOT / "knowledge/editorial_review/kb_batch151_ten_authoring.json"
LOCKS = ROOT / "knowledge/editorial_review/kb_batch151_source_line_sha256.json"
OUT = ROOT / "knowledge/editorial_review/kb_batch151_ten_teacher_lessons.json"
AUDIT = ROOT / "docs/evaluation/KB_BATCH151_DEPTH_AUDIT.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH151_TEN_MATH_LESSONS.md"
SAFE = ROOT / "knowledge/editorial_review/kb_batch151_student_safe_index.json"
IDS = (
    "hs-semantic-pilot-119-c08", "hs-semantic-pilot-120-c102",
    "hs-semantic-pilot-120-c107", "hs-semantic-pilot-119-s04",
    "hs-semantic-pilot-119-s09", "hs-semantic-pilot-119-a05",
    "hs-semantic-pilot-119-b04", "hs-semantic-pilot-119-ec02",
    "hs-semantic-pilot-120-ed106", "hs-semantic-pilot-120-ee105",
)
EXPECTED = dict(zip(IDS, (
    "COMPULSORY", "COMPULSORY", "COMPULSORY",
    "SELECTIVE_COMPULSORY", "SELECTIVE_COMPULSORY",
    "ELECTIVE_A", "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E",
)))
SHA = re.compile(r"[0-9a-f]{64}\Z")
EVIDENCE = "PDFKIT_HASHED_NOT_HUMAN_SEMANTICALLY_APPROVED"

def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError("Batch151: " + message)

def encode(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"

def contexts():
    return previous.contexts()

def source_fingerprints():
    """Re-hash precise PDFKit source lines *on Mac*, never upload copyrighted text."""
    pages = previous.previous.prior.prior.prior.old.prior.upstream.prior.previous.prev.prior.prior.previous.source_pages()
    fp_fn = previous.previous.prior.prior.prior.old.prior.upstream.fingerprint
    records = contexts()
    result = {}
    for cid in IDS:
        src = records[cid]["source"]
        fp = fp_fn(pages, src)
        check(fp["span_sha256"] == src["source_span_sha256"], "original PDFKit span drift " + cid)
        result[cid] = dict(
            page=src["printed_page"], start_line=src["start_line"],
            end_line=src["end_line"], span_sha256=fp["span_sha256"],
            line_sha256=fp["line_sha256"],
        )
    return result

@lru_cache(maxsize=1)
def build():
    author = json.loads(AUTHOR.read_text(encoding="utf-8"))
    locks = json.loads(LOCKS.read_text(encoding="utf-8"))
    c = contexts()
    check(tuple(row["id"] for row in author) == IDS, "ten original source candidate IDs/order changed")
    check(set(locks) == set(IDS), "incomplete source PDF line locks")
    old = previous.audit(previous.build())
    check(old["total_teacher_only_drafts"] == 105, "previous inventory 105 changed")
    used = {r["candidate"] for r in old["rows"]}
    check(not used.intersection(IDS), "candidate previously authored")
    rows = []
    for a in author:
        cid = a["id"]
        context = c[cid]
        source = context["source"]
        lock = locks[cid]
        check(context["course_track"] == EXPECTED[cid], "incorrect track " + cid)
        check(source["original_pdf_sha256"] == PDF, "wrong syllabus PDF SHA")
        check((lock["page"], lock["start_line"], lock["end_line"], lock["span_sha256"]) ==
              (source["printed_page"], source["start_line"], source["end_line"], source["source_span_sha256"]),
              "source locator/hash mismatch " + cid)
        check(len(lock["line_sha256"]) == source["end_line"] - source["start_line"] + 1
              and all(SHA.fullmatch(h) for h in lock["line_sha256"] + [lock["span_sha256"]]),
              "bad line SHA sequence")
        check(a["type"] in {"Concept", "Theorem", "Method"}, "invalid knowledge type")
        for key in ("topic", "formal", "domain", "assumptions", "legal", "failure", "wrong", "repair", "near", "far"):
            check(isinstance(a.get(key), str) and len(a[key]) >= (8 if key == "topic" else 20),
                  "missing rigorous authoring field " + key)
        check(len(a["steps"]) == 4 and len(a["examples"]) == 2 and len(a["hints"]) == 3, "incomplete depth")
        check(all(isinstance(s, str) and len(s) >= 18 for s in a["steps"] + a["hints"]), "shallow steps or hints")
        check(all(len(e["sol"]) >= 3 and len(e["q"]) >= 8 and len(e["a"]) >= 2 and
                  all(len(s) >= 10 for s in e["sol"]) for e in a["examples"]), "shallow teacher example")
        row = dict(
            id="kb151-deep-" + cid.removeprefix("hs-semantic-pilot-"), source_candidate_id=cid,
            course_track=context["course_track"], knowledge_type=a["type"], title=a["topic"],
            standard_version="2017-edition-2020-revision-editorial-pilot",
            source_pdf_sha256=PDF, source_printed_page=lock["page"],
            source_start_line=lock["start_line"], source_end_line=lock["end_line"],
            source_span_sha256=lock["span_sha256"], source_line_sha256=lock["line_sha256"],
            source_evidence_status=EVIDENCE,
            official_atom_id=None, source_semantics_human_approved=False,
            formal_definition_or_theorem=a["formal"], notation_and_domain=a["domain"],
            applicability_and_hypotheses=a["assumptions"], why_method_is_legal=a["legal"],
            reasoned_steps=[dict(step=j+1, justification=text) for j,text in enumerate(a["steps"])],
            nonexample_or_failure=a["failure"], typical_wrong_solution=a["wrong"],
            why_wrong_and_repair=a["repair"],
            teacher_examples=[dict(question=e["q"], answer=e["a"], reasoned_solution=e["sol"]) for e in a["examples"]],
            student_hint_ladder=a["hints"], near_transfer=a["near"], far_transfer=a["far"],
            prerequisite_proposals=context["prerequisite_candidate_ids"],
            prerequisite_math_review="REVIEW_PENDING",
            teacher_review_status="REVIEW_PENDING", teacher_review_evidence=None,
            teacher_solution_visibility="TEACHER_ONLY", formal_proof_certified=False,
            free_student_step_verified=False, student_authoritative=False,
            elective_e_optional_example=context["elective_e_optional_example"],
        )
        rows.append(row)
    validate(rows)
    return rows

def validate(rows):
    check(len(rows) == 10 and {r["source_candidate_id"] for r in rows} == set(IDS)
          and len({r["id"] for r in rows}) == 10, "not ten distinct source-locked manuscripts")
    locks = json.loads(LOCKS.read_text(encoding="utf-8"))
    for i,r in enumerate(rows):
        cid = IDS[i]
        check(r["source_candidate_id"] == cid and r["course_track"] == EXPECTED[cid]
              and r["source_pdf_sha256"] == PDF and r["source_evidence_status"] == EVIDENCE,
              "untrusted source/course status")
        lock = locks[cid]
        check((r["source_printed_page"], r["source_start_line"],r["source_end_line"],
               r["source_span_sha256"],r["source_line_sha256"]) ==
              (lock["page"],lock["start_line"],lock["end_line"],lock["span_sha256"],lock["line_sha256"]),
              "forged original source fingerprint")
        check(r["teacher_review_status"] == "REVIEW_PENDING" and r["teacher_review_evidence"] is None
              and r["prerequisite_math_review"] == "REVIEW_PENDING"
              and r["teacher_solution_visibility"] == "TEACHER_ONLY"
              and r["source_semantics_human_approved"] is False
              and r["official_atom_id"] is None and r["formal_proof_certified"] is False
              and r["free_student_step_verified"] is False and r["student_authoritative"] is False,
              "forged approval, proof or publishing")
        check(r["elective_e_optional_example"] is (cid == "hs-semantic-pilot-120-ee105"), "school elective tag wrong")
        for key in ("title","formal_definition_or_theorem","notation_and_domain",
                    "applicability_and_hypotheses","why_method_is_legal","nonexample_or_failure",
                    "typical_wrong_solution","why_wrong_and_repair","near_transfer","far_transfer"):
            check(isinstance(r.get(key),str) and len(r[key]) >= (8 if key=="title" else 20),
                  "missing content " + key)
        check(len(r["reasoned_steps"])==4 and
              all(z["step"]==j+1 and len(z["justification"])>=18
                  for j,z in enumerate(r["reasoned_steps"])), "invalid step reasoning")
        check(len(r["student_hint_ladder"])==3 and
              all(len(x)>=18 for x in r["student_hint_ladder"]), "invalid hint ladder")
        check(len(r["teacher_examples"])==2 and
              all(len(e["reasoned_solution"])>=3 and len(e["question"])>=8 and
                  all(len(s)>=10 for s in e["reasoned_solution"]) for e in r["teacher_examples"]),
              "missing teacher examples")
    return True

def audit(rows):
    old = previous.audit(previous.build())
    additions = [dict(id=r["id"],candidate=r["source_candidate_id"],track=r["course_track"],
                      source_sha=r["source_span_sha256"],review="REVIEW_PENDING") for r in rows]
    allrows = old["rows"]+additions
    check(len(allrows)==115 and len({r["candidate"] for r in allrows})==115, "115 distinct drafts expected")
    counts=Counter(v["track"] for v in allrows)
    return dict(schema="kb151-seven-track-deep-editor-inventory/1",
                prior_teacher_pending_manuscripts=105, added_original_manuscripts=10,
                total_teacher_only_drafts=115, by_track={t:counts[t] for t in TRACKS},
                official_atom_denominators={t:None for t in TRACKS},
                official_coverage_rate=None, teacher_approved=0, student_authoritative=0,
                free_student_steps_verified=0, formal_general_proofs_certified=0,
                original_teacher_examples=20, student_hint_steps=30, near_far_tasks=20,
                source_semantics_human_approved=False,
                rows=sorted(allrows,key=lambda r:r["candidate"]))

def student_safe():
    return dict(status="NO_APPROVED_EVIDENCE",items=[],teacher_solution_exposed=False,
                unpublished_manuscripts_exposed=False,official_coverage_rate=None,
                student_authoritative=False)

def render(rows,ledger):
    out=["# KB151｜跨七轨10份原创数学深度候审稿（不是正式课标课程原子）", "",
         "原始PDFKit来源行只确认位置和版本；每份仍待真实教师审查，不能发布为学生权威答案。",
         "105→115份候审稿；20道教师例题；30级启发提示；20项近远迁移；七轨正式分母UNKNOWN。",""]
    for r in rows:
        out.extend(["## "+r["title"],"",
            f'候选 {r["source_candidate_id"]}，课程 {r["course_track"]}；印刷第{r["source_printed_page"]}页'
            f'{r["source_start_line"]}–{r["source_end_line"]}行；SHA256 {r["source_span_sha256"]}',
            "REVIEW_PENDING / TEACHER_ONLY；不视为形式证明或官方原子认证。","",
            "### 定义/定理",r["formal_definition_or_theorem"],"",
            "### 记号与定义域",r["notation_and_domain"],"",
            "### 假设与适用条件",r["applicability_and_hypotheses"],"",
            "### 方法合法性说明",r["why_method_is_legal"],"",
            "### 分步论证"])
        out.extend(f'{s["step"]}. {s["justification"]}' for s in r["reasoned_steps"])
        out.extend(["","### 不适用例",r["nonexample_or_failure"],"",
                    "### 典型错误",r["typical_wrong_solution"],"",
                    "### 错因修复",r["why_wrong_and_repair"],"",
                    "### 教师例题（学生自主挑战不可直接获取）"])
        for i,e in enumerate(r["teacher_examples"],1):
            out.extend([f'例{i}：{e["question"]}',f'参考答案：{e["answer"]}'])
            out.extend(f"- {s}" for s in e["reasoned_solution"])
        out.extend(["","### 学生启发提示（无答案）"])
        out.extend(f'{i}. {x}' for i,x in enumerate(r["student_hint_ladder"],1))
        out.extend(["","### 近迁移",r["near_transfer"],"",
                    "### 远迁移",r["far_transfer"],""])
    return "\n".join(out).rstrip("\n")+"\n"

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write-mac",action="store_true")
    g.add_argument("--write",action="store_true")
    g.add_argument("--check",action="store_true")
    g.add_argument("--check-mac",action="store_true")
    args=p.parse_args()
    if args.write_mac:
        LOCKS.write_text(encode(source_fingerprints()),encoding="utf-8")
    rows=build();ledger=audit(rows)
    if args.write or args.write_mac:
        OUT.write_text(encode(rows),encoding="utf-8")
        AUDIT.write_text(encode(ledger),encoding="utf-8")
        REPORT.write_text(render(rows,ledger),encoding="utf-8")
        SAFE.write_text(encode(student_safe()),encoding="utf-8")
    else:
        check(json.loads(OUT.read_text(encoding="utf-8"))==rows, "immutable manuscript drift")
        check(json.loads(AUDIT.read_text(encoding="utf-8"))==ledger,"coverage audit drift")
        check(REPORT.read_text(encoding="utf-8")==render(rows,ledger),"published report drift")
        check(json.loads(SAFE.read_text(encoding="utf-8"))==student_safe(),"student safety drift")
        if args.check_mac:
            check(source_fingerprints()==json.loads(LOCKS.read_text(encoding="utf-8")),
                  "Mac original PDFKit lines disagree with committed source hashes")
            print("Mac PDFKit source rehash PASS; copyrighted standard text not exported")
    print("PASS Batch151: 10 deep teacher manuscripts; 115 REVIEW_PENDING; 0 APPROVED")

if __name__=="__main__":
    main()
