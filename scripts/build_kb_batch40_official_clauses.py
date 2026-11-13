#!/usr/bin/env python3
"""Reconcile 12 project editorial goals with source-anchored *topic scope*.

The original copyrighted official PDF is read only on the Mac when --pdf is
supplied. Git contains short probes, page fingerprints and original analysis,
never the PDF or whole-source passages. Topic match != official knowledge
atom equivalence, mathematical proof or teacher approval.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "curriculum/highschool_math/k00_batch40_twelve_clause_adjudications.json"
OLD = ROOT / "docs/evaluation/KB_BATCH36_47_LEGACY_SCOPE_AUDIT.json"
FINGERPRINTS = ROOT / "curriculum/highschool_math/k00_batch40_pdfkit_source_fingerprints.json"
OUT = ROOT / "docs/evaluation/KB_BATCH40_TWELVE_OFFICIAL_CLAUSE_AUDIT.json"
MARKDOWN = ROOT / "docs/evaluation/KB_BATCH40_CLAUSE_SCOPE_NOTES.md"
SWIFT = ROOT / "scripts/kb_batch40_pdfkit_extract.swift"

SHA = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
CLASS = {
 "KB33-A-P052-A001": "DIRECT_SCOPE",
 "KB33-A-P052-A002": "DIRECT_SCOPE",
 "KB33-A-P052-A003": "DIRECT_SCOPE",
 "KB33-A-P053-A002": "PARTIAL_DERIVATION",
 "KB33-A-P053-A004": "DIRECT_SCOPE",
 "KB33-A-P057-A002": "TOPIC_ONLY_NOT_EXPLICIT",
 "KB33-B-P058-A004": "TOPIC_ONLY_NOT_EXPLICIT",
 "KB33-B-P059-A002": "TOPIC_ONLY_NOT_EXPLICIT",
 "KB33-C-P065-A001": "DIRECT_SCOPE",
 "KB33-C-P066-A004": "DIRECT_SCOPE",
 "KB33-D-P071-A002": "CONTEXTUAL_APPLICATION",
 "KB33-E-P073-A004": "LOCAL_ELECTIVE_OPTION",
}
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A",
          "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def han(s: str) -> str:
    return re.sub(r"[^\u4e00-\u9fff]", "", s)

def verify_pdf(pdf: Path, source: dict) -> dict:
    if not pdf.is_file() or digest(pdf.read_bytes()) != SHA:
        raise ValueError("Original PDF SHA256 does not match frozen standard")
    cp = subprocess.run(["swift", str(SWIFT), str(pdf)], check=True,
                        capture_output=True, text=True)
    pages = json.loads(cp.stdout)
    if [p["printed_page"] for p in pages] != sorted({
        v["printed_page"] for v in source["entries"]
    }) or len(pages) != 9:
        raise ValueError("PDFKit pages incomplete or page index shifted")
    text = {p["printed_page"]: p["text"] for p in pages}
    for row in source["entries"]:
        if han(row["short_source_probe_chinese"]) not in han(text[row["printed_page"]]):
            raise ValueError("Source phrase not on expected original page: "
                             + row["editorial_candidate_id"])
    return {
        "pdf_sha256": SHA, "tool": "macOS PDFKit Swift original-page text",
        "page_fingerprints": [{
            "printed_page": p["printed_page"], "pdf_page_index": p["pdf_page_index"],
            "pdfkit_page_text_sha256": digest(p["text"].encode("utf-8")),
            "original_pdf_page_inspected": True, "teacher_verified": False
        } for p in pages],
        "source_passages_committed": False,
        "pdf_committed": False,
    }

def audit(source: dict | None = None, previous: dict | None = None,
          fingerprints: dict | None = None) -> dict:
    source = source if source is not None else load(SOURCE)
    previous = previous if previous is not None else load(OLD)
    fingerprints = fingerprints if fingerprints is not None else load(FINGERPRINTS)
    if source.get("source", {}).get("sha256") != SHA or source["source"]["total_pages"] != 188:
        raise ValueError("Wrong standard or PDF version")
    if source["source"]["printed_to_pdf_index_offset"] != 7:
        raise ValueError("Wrong original PDF page numbering")
    rows = source["entries"]
    if len(rows) != 12 or len({r["editorial_candidate_id"] for r in rows}) != 12:
        raise ValueError("Missing or duplicate source-to-editorial review")
    if {r["editorial_candidate_id"] for r in rows} != set(CLASS):
        raise ValueError("12 candidate ID set changed")
    if fingerprints["pdf_sha256"] != SHA or fingerprints["pdf_committed"]:
        raise ValueError("Untrusted PDF fingerprint metadata")
    page_pins = {p["printed_page"]: p for p in fingerprints["page_fingerprints"]}
    if len(page_pins) != 9 or set(page_pins) != {r["printed_page"] for r in rows}:
        raise ValueError("Missing or duplicated source pages")
    for n, p in page_pins.items():
        if p["pdf_page_index"] != n + 7 or len(p["pdfkit_page_text_sha256"]) != 64:
            raise ValueError("Invalid PDFKit page fingerprint")
        if not p["original_pdf_page_inspected"] or p["teacher_verified"]:
            raise ValueError("Source observation confused with teacher review")
    old = {r["editorial_candidate_id"]: r for r in previous["links"]
           if r["review_finding"] == "CLAUSE_UNVERIFIED"}
    if set(old) != set(CLASS):
        raise ValueError("Old 12 CLAUSE_UNVERIFIED baseline drift")
    seen = []
    for row in rows:
        cid = row["editorial_candidate_id"]
        legacy = old[cid]
        if row["source_scope_class"] != CLASS[cid]:
            raise ValueError("Source scope adjudication class drift for " + cid)
        if row["printed_page"] != legacy["source_printed_page"] or row["track"] != legacy["candidate_track"]:
            raise ValueError("Page/track mismatch for " + cid)
        if len(row["section_anchor"]) < 7 or len(han(row["short_source_probe_chinese"])) < 7:
            raise ValueError("Unsubstantiated page anchor")
        if len(row["mathematical_scope_note"]) < 18 or len(row["review_action"]) < 12:
            raise ValueError("Missing substantive mathematical boundary")
        if (row["teacher_review"] != "REVIEW_PENDING"
            or row["official_atomic_equivalence_certified"] is not False
            or row["legacy_lesson_certified"] is not False
            or row["student_publishable"] is not False):
            raise ValueError("Forged mathematical, official or teacher approval")
        seen.append({
            **row,
            "original_pdf_sha256": SHA,
            "pdf_page_index_zero_based": row["printed_page"] + 7,
            "pdfkit_page_text_sha256": page_pins[row["printed_page"]]["pdfkit_page_text_sha256"],
            "legacy_lesson_id": legacy["legacy_lesson_id"],
            "legacy_lesson_content_sha256": legacy["legacy_lesson_content_sha256"],
            "legacy_review_result_before_source_check": "CLAUSE_UNVERIFIED",
            "source_short_probe_sha256": digest(row["short_source_probe_chinese"].encode()),
            "teacher_solution": None,
        })
    counts = dict(sorted(Counter(x["source_scope_class"] for x in seen).items()))
    return {
        "schema_version": "kb-batch40-source-topical-review-v1",
        "source_pdf_sha256": SHA,
        "frozen_previous_review_sha256": digest(OLD.read_bytes()),
        "review_scope": "ASSISTANT_ORIGINAL_PDF_TOPIC_MATCH_NOT_TEACHER_CERTIFICATION",
        "summary": {
            "candidate_links_reviewed": 12,
            "source_pages_reinspected": 9,
            "class_count": counts,
            "official_atomic_equivalences_certified": 0,
            "general_theorems_formally_certified": 0,
            "teacher_approved": 0,
            "student_published": 0,
            "official_atomic_denominator": {t: None for t in TRACKS},
            "source_probe_verification": "PDFKIT_ORIGINAL_SOURCE_SHA_MATCHED_WHEN_EVIDENCE_CREATED",
        },
        "rows": seen,
        "student_retrieval": {"documents": [], "teacher_solutions": []},
        "warnings": [
            "A source-topic match is not exact official atomic knowledge equivalence.",
            "A/B/C/D are elective tracks; E is local optional examples, never a national mandatory atom list.",
            "The linked 12 legacy lessons remain REVIEW_PENDING; no teacher or proof certification was performed.",
            "The --check CI path verifies pinned audit consistency; rechecking PDF requires --pdf on Mac.",
        ]
    }

def markdown(a: dict) -> str:
    lines = [
        "# Batch40｜12 条选修课标候选与原始课标的逐页范围校对",
        "",
        "来源：教育部《普通高中数学课程标准（2017年版2020年修订）》；原 PDF SHA256："
        + SHA + "。仅存项目自写释义与短锚点，未提交原 PDF 或原文段落。",
        "",
        "**结论口径**：本批核对来源页面中确实出现的主题或例子，不自动批准旧讲义的数学等价性；"
        "AI 逐页检查不能代替真实教师复核。七类官方完整知识原子分母仍未知。",
        "",
        "| 编辑候选 | 印刷页/小节 | 来源范围结论 | 后续数学与课程审核 |",
        "|---|---|---|---|",
    ]
    for row in a["rows"]:
        lines.append("| " + " | ".join([
            row["editorial_candidate_id"],
            str(row["printed_page"]) + " " + row["section_anchor"],
            row["source_scope_class"],
            row["review_action"]
        ]) + " |")
    lines += ["", "## 边界与易错点", ""]
    for row in a["rows"]:
        lines.append("### " + row["editorial_candidate_id"] + " — " + row["source_scope_class"])
        lines.append(row["mathematical_scope_note"])
        lines.append("后续工作：" + row["review_action"] + "。")
        lines.append("")
    lines += [
        "## 交付门禁",
        "",
        "来源主题核查 12/12、原始课标页面 9 页，并不等于 12 个官方知识原子或 12 篇新讲义。",
        "其中显式范围 6、部分派生 1、未显式独立要求 3、应用情境 1、学校自选拓展 1。",
        "所有原有 287 篇深度草案与独立选修审核稿仍维持 REVIEW_PENDING，"
        "不自动进入学生正式索引；官方课程分母全部为 null。",
    ]
    return "\n".join(lines) + "\n"

def run() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--pdf", type=Path, default=None)
    args = p.parse_args()
    source = load(SOURCE)
    if args.pdf:
        verified = verify_pdf(args.pdf, source)
        if args.check:
            if verified != load(FINGERPRINTS):
                raise ValueError("Pinned page hashes differ from original PDF")
        else:
            FINGERPRINTS.write_text(json.dumps(verified, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = audit(source=source)
    content = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    md = markdown(result)
    if args.check:
        if OUT.read_text(encoding="utf-8") != content or MARKDOWN.read_text(encoding="utf-8") != md:
            raise ValueError("Generated Batch40 source audit or editorial notes drifted")
    else:
        OUT.write_text(content, encoding="utf-8")
        MARKDOWN.write_text(md, encoding="utf-8")
    print("Batch40: 12 clause-scope candidates; 9 original pages; "
          + str(result["summary"]["class_count"]) + "; CHECK=" + str(args.check))

if __name__ == "__main__":
    run()
