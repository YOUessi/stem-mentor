#!/usr/bin/env python3
"""Source-locked, *provisional* enumerated requirement-marker census.

Only editorial labels and hashes are committed; original copyrighted PDF
text is read from Mac private scratch. Marker counts are not official atoms.
Fail closed on source change, cross-track line boundaries or fake approval.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "curriculum/highschool_math/k00_batch117_source_triage.json"
CACHE = Path("/private/tmp/kb117_pdfkit_lines_private.json")
OUT = ROOT / "curriculum/highschool_math/k00_batch118_provisional_marker_ledger.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH118_SOURCE_MARKER_CENSUS.md"
PDF_SHA = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
TRACKS = ("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
          "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
# The *line* is authoritative at transitions, NOT a page-wide label.
TRANSITIONS = ((13,1,"COMPULSORY"),(36,16,"SELECTIVE_COMPULSORY"),
               (50,20,"ELECTIVE_UNASSIGNED"),(51,20,"ELECTIVE_A"),
               (57,16,"ELECTIVE_B"),(64,10,"ELECTIVE_C"),
               (69,6,"ELECTIVE_D"),(73,13,"ELECTIVE_E"))
# Actual, line-by-line editorial source inspected in Batch118; this is NOT
# teacher certification of each mathematical atom or PDF-image formula.
MANUAL_EDITORIAL_PAGES = tuple(range(37,51)) + tuple(range(64,74))
IMAGE_RISK = {21,22,35,51,52,53,54,55,56,57,58,59,69,73}
BULLET = re.compile(r"^[①②③④⑤⑥⑦⑧⑨⑩]")
SUBITEM = re.compile(r"^（\s*[0-9０-９]+\s*）")
TOPIC = re.compile(r"^[0-9０-９]+\s*[．.、]")
E_EXAMPLES = {16,18,19,21}

def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)

def h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def track_at(page: int, line: int) -> str:
    result = None
    for p, l, tr in TRANSITIONS:
        if (page,line) >= (p,l):
            result = tr
    require(result is not None, "track unassigned")
    return result

def marker_kind(line: str, page: int, number: int) -> str | None:
    trimmed = line.strip()
    if BULLET.match(trimmed): return "NUMBERED_REQUIREMENT_CUE"
    if SUBITEM.match(trimmed): return "SUBTOPIC_CUE"
    if TOPIC.match(trimmed): return "TOPIC_CUE"
    if page == 73 and number in E_EXAMPLES: return "OPEN_ELECTIVE_EXAMPLE_CUE"
    return None

# On printed p35 PDFKit emits embedded CR/control glyphs. The persisted
# private line-index representation and the original raw-page PDFKit digest
# have different canonicalizations; BOTH must match their pinned attestations.
PAGE35_CANONICAL_LINE_SHA = "98ba796a53012a7400fb4f7c2155156edc712f1296a173b8a6123876eb6874b3"

def stable_page_sha(page, lines, prior):
    digest = h("\n".join(lines))
    if page == 35:
        require(digest == PAGE35_CANONICAL_LINE_SHA, "page35 private cache drift")
        return prior["page_text_sha256"]
    return digest

def source_pages():
    raw = json.loads(CACHE.read_text(encoding="utf-8"))
    prev = json.loads(SOURCE.read_text(encoding="utf-8"))
    require(len(raw)==61 and len(prev["pages"])==61, "61-page manifest or source mismatch")
    require(prev["source_pdf_sha256"]==PDF_SHA, "untrusted source PDF")
    for i, p in enumerate(raw):
        page = i+13
        old = prev["pages"][i]
        lines = p["lines"]
        require(p["printed_page"]==page and p["pdf_index"]==page+7,
                "wrong physical/printed page mapping")
        require(old["page_text_sha256"]==stable_page_sha(page,lines,old), f"page {page} source drift")
        require(old["nonempty_pdfkit_line_count"]==len(lines), f"page {page} missing lines")
        require(old["source_pdf_sha256"]==PDF_SHA, "mixed sources")
    return raw

def produce():
    raw = source_pages()
    prev = json.loads(SOURCE.read_text())
    pages, markers = [], []
    for entry in raw:
        p = entry["printed_page"]
        lines = entry["lines"]
        partition = []
        previous = None
        for lineno, line in enumerate(lines,1):
            tr = track_at(p,lineno)
            if tr!=previous:
                partition.append({"from_line":lineno, "track":tr})
                previous=tr
            kind = marker_kind(line,p,lineno)
            if kind is None: continue
            line_sha = h(line)
            key = h(f"{p}:{lineno}:{kind}:{line_sha}")[:20]
            markers.append({
                "editorial_marker_id":f"syllabus-cue-{key}",
                "printed_page":p,"pdf_page_index":p+7,"source_line":lineno,
                "source_line_sha256":line_sha,
                "page_text_sha256":stable_page_sha(p,lines,prev["pages"][p-13]),
                "track_hint":tr,"cue_kind":kind,
                "source_status":"SOURCE_HASH_LOCKED_NOT_TEACHER_ATOMIZED",
                "math_proof_status":"UNVERIFIED",
                "review_status":"REVIEW_PENDING",
                "official_atom_id":None,
                "teacher_review_evidence":None,
                "student_authoritative":False,
                "needs_formula_visual_recheck":p in IMAGE_RISK,
            })
        pages.append({
            "printed_page":p,"pdf_page_index":p+7,
            "source_line_count":len(lines),
            "source_page_sha256":stable_page_sha(p,lines,prev["pages"][p-13]),
            "line_track_partitions":partition,
            "editorial_source_line_review":"INSPECTED_PENDING_TEACHER" if p in MANUAL_EDITORIAL_PAGES else "INDEXED_PENDING_EDITORIAL",
            "official_atom_denominator":None,
            "mathematics_image_risk":p in IMAGE_RISK,
        })
    counts = Counter(m["track_hint"] for m in markers)
    categories = {t:{
        "provisional_source_cue_count":counts[t],
        "official_atom_denominator":None,
        "certified_atom_count":0,
        "teacher_approved_count":0,
        "outstanding":"SEMANTIC_ATOM_SPLIT_AND_TEACHER_REVIEW"
    } for t in TRACKS}
    categories["ELECTIVE_UNASSIGNED"]={
        "provisional_source_cue_count":counts["ELECTIVE_UNASSIGNED"],
        "official_atom_denominator":None,
        "certified_atom_count":0,"teacher_approved_count":0,
        "outstanding":"ELECTIVE_GENERAL_PREAMBLE_NOT_AN_ELECTIVE_TRACK"}
    data={
        "schema_version":"kb118-provisional-source-marker-ledger-v1",
        "original_pdf_sha256":PDF_SHA,
        "source_line_encoding":"Mac PDFKit, printable source extracted in private; hashed only",
        "source_text_committed":False,
        "curriculum_standard":"普通高中数学课程标准（2017年版2020年修订）",
        "printed_content_page_range":[13,73],
        "total_printed_content_pages":61,
        "total_indexed_source_lines":sum(len(p["lines"]) for p in raw),
        "batch118_editorial_line_inspection_pages":list(MANUAL_EDITORIAL_PAGES),
        "official_atom_total_denominator":None,
        "official_atom_complete_census":False,
        "total_provisional_markers":len(markers),
        "teacher_approved_total":0,
        "student_authoritative_count":0,
        "not_equivalent_to_official_atoms":True,
        "track_counts":categories,"pages":pages,"markers":markers,
    }
    validate(data)
    return data

def validate(data):
    prev=json.loads(SOURCE.read_text())
    require(data["original_pdf_sha256"]==prev["source_pdf_sha256"]==PDF_SHA,"PDF drift")
    require(data["schema_version"]=="kb118-provisional-source-marker-ledger-v1","schema")
    require(data["source_text_committed"] is False, "copyrighted text cannot be committed")
    require(data["not_equivalent_to_official_atoms"] is True,"fake denominator")
    require(data["official_atom_total_denominator"] is None
            and data["official_atom_complete_census"] is False,"fake certification")
    require(data["teacher_approved_total"]==0 and data["student_authoritative_count"]==0,
            "fake teacher approval/publication")
    require(set(data["track_counts"])==set(TRACKS)|{"ELECTIVE_UNASSIGNED"},"wrong tracks")
    for t,v in data["track_counts"].items():
        require(v["official_atom_denominator"] is None
                and v["teacher_approved_count"]==0
                and v["certified_atom_count"]==0,"unattested track")
    pages = data["pages"]
    require(len(pages)==61 and [p["printed_page"] for p in pages]==list(range(13,74)),
            "missing or repeated printed pages")
    require(sum(p["source_line_count"] for p in pages)==data["total_indexed_source_lines"],
            "missing lines")
    for p,older in zip(pages,prev["pages"]):
        require(p["source_page_sha256"]==older["page_text_sha256"],
                "unattested page checksum")
        require(p["source_line_count"]==older["nonempty_pdfkit_line_count"],
                "page line count drift")
        require(p["official_atom_denominator"] is None,"faked page atom count")
        require(p["line_track_partitions"][0]["from_line"]==1, "no initial track")
        require(p["line_track_partitions"]==[
            {"from_line":n,"track":track_at(p["printed_page"],n)}
            for n in range(1,p["source_line_count"]+1)
            if n==1 or track_at(p["printed_page"],n)!=track_at(p["printed_page"],n-1)
        ],"cross-track page boundary")
        expected="INSPECTED_PENDING_TEACHER" if p["printed_page"] in MANUAL_EDITORIAL_PAGES else "INDEXED_PENDING_EDITORIAL"
        require(p["editorial_source_line_review"]==expected,"fake page review")
    require(data["batch118_editorial_line_inspection_pages"]==list(MANUAL_EDITORIAL_PAGES),
            "editorial review trace")
    require(len(data["markers"])==data["total_provisional_markers"],"marker count drift")
    keys=set()
    counts=Counter()
    last=(-1,-1)
    for m in data["markers"]:
        p,n=m["printed_page"],m["source_line"]
        require((p,n)>last and m["pdf_page_index"]==p+7
                and 13<=p<=73 and 1<=n<=pages[p-13]["source_line_count"],
                "unordered/invalid marker")
        last=(p,n)
        require(m["editorial_marker_id"] not in keys,"duplicate marker")
        keys.add(m["editorial_marker_id"])
        require(m["track_hint"]==track_at(p,n),"marker cross-track tampering")
        require(m["page_text_sha256"]==pages[p-13]["source_page_sha256"],"marker source drift")
        require(re.fullmatch(r"[0-9a-f]{64}",m["source_line_sha256"]) is not None,
                "invalid line hash")
        key=h(f"{p}:{n}:{m['cue_kind']}:{m['source_line_sha256']}")[:20]
        require(m["editorial_marker_id"]==f"syllabus-cue-{key}","marker identity mismatch")
        require(m["cue_kind"] in {"NUMBERED_REQUIREMENT_CUE","SUBTOPIC_CUE","TOPIC_CUE","OPEN_ELECTIVE_EXAMPLE_CUE"},
                "bad cue")
        require(m["source_status"]=="SOURCE_HASH_LOCKED_NOT_TEACHER_ATOMIZED"
                and m["math_proof_status"]=="UNVERIFIED"
                and m["review_status"]=="REVIEW_PENDING"
                and m["official_atom_id"] is None
                and m["teacher_review_evidence"] is None
                and m["student_authoritative"] is False, "fake approval or proof")
        counts[m["track_hint"]]+=1
    for t,rec in data["track_counts"].items():
        require(rec["provisional_source_cue_count"]==counts[t],"track marker denominator drift")
    require(sum(counts.values())==data["total_provisional_markers"],"marker ledger mismatch")
    return True

def markdown(data):
    rows=["# Batch118 | 课标61页逐行来源线索计数（非正式原子分母）","",
          "来源：项目Mac授权原件《普通高中数学课程标准（2017年版2020年修订）》，PDF SHA-256: "+PDF_SHA+".",
          "本清单不包含课标原句；在Mac本地逐行抽取、验证页与行哈希，GitHub只存校验和、类别和待审状态。",
          "**线索 != 正式课标知识原子。** 一个线索可包含多个原子，也可能仅是标题；跨页连句、图示与扩展例子还需人工拆分。正式官方分母继续为UNKNOWN。","",
          "| 归属轨 | 可复核枚举线索（非原子） | 正式原子分母 | 教师批准 |",
          "|---|---:|---|---:|"]
    for t in (*TRACKS, "ELECTIVE_UNASSIGNED"):
        v = data["track_counts"][t]
        rows.append(f"| {t} | {v['provisional_source_cue_count']} | UNKNOWN | 0 |")
    rows+=["",f"本地来源行总数：{data['total_indexed_source_lines']}；逐页指纹：61/61；线索总计：{data['total_provisional_markers']}。","",
           "Batch118具体逐行编辑检查（非教师原子审核）：印刷37–50页与64–73页，共24页。其余37页保持机器索引或此前编辑候审状态，不升级教师审核。",
           "跨轨页级陷阱已改为行级边界：印刷36:16选择性必修；50:20选修总说明；51:20选修A；57:16选修B；64:10选修C；69:6选修D；73:13选修E。",
           "PDFKit可能错误抽取数学表达式，特别是印刷21/22/35、51–59、69/73；线索的存在不代表公式图片已完成复核。",
           "后续仍需：逐条语义拆分、跨页去重、概念定理方法判别、先修检查、独立符号验证、真实教师逐项审校、学生安全发布测试。",""]
    return "\n".join(rows)

def main():
    ap=argparse.ArgumentParser()
    grp=ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--write",action="store_true")
    grp.add_argument("--check",action="store_true")
    ap.add_argument("--verify-local-source",action="store_true")
    a=ap.parse_args()
    if a.write:
        data=produce()
        OUT.write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
        REPORT.write_text(markdown(data))
    else:
        data=json.loads(OUT.read_text())
        validate(data)
        require(REPORT.read_text()==markdown(data),"Markdown report drift")
        if a.verify_local_source:
            require(data==produce(),"local PDFKit source line drift")
    print("Batch118 source marker ledger:",data["total_indexed_source_lines"],
          "source lines /",len(data["pages"]),"pages /",
          data["total_provisional_markers"],"editorial cues; OFFICIAL denominators UNKNOWN")

if __name__=="__main__":
    main()
