"""K00: conservative, reproducible source-marker inventory; never claims official atom coverage.

Input is PDFKit-extracted text from the official PDF; the PDF and extracted full
copyright text remain outside git. The output contains page/hash/marker only.
A numbered text marker is NOT necessarily a standalone curriculum objective.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/evaluation/KB_BATCH18_SOURCE_MARKERS.json"
STANDARD_URL = ("https://jyj.changdu.gov.cn/cdsjyj/c101476/202205/"
                "764ee1914e3c45aaba8e372f1b628a34/files/"
                "75676dfa9af0442db1457404a884a69f.pdf")
# Printed-page ranges; not student-ready official atom enumeration.
TRACKS = {
    "COMPULSORY": (13, 35, ["预备知识", "函数", "几何与代数", "概率与统计", "数学建模活动与数学探究活动"]),
    "SELECTIVE_COMPULSORY": (36, 50, ["函数", "几何与代数", "概率与统计", "数学建模活动与数学探究活动"]),
    "ELECTIVE_A": (51, 57, ["微积分", "空间向量与代数", "概率与统计"]),
    "ELECTIVE_B": (58, 63, ["微积分", "空间向量与代数", "应用统计", "模型"]),
    "ELECTIVE_C": (64, 68, ["逻辑推理初步", "数学模型", "社会调查与数据分析"]),
    "ELECTIVE_D": (69, 72, ["美与数学", "音乐中的数学", "美术中的数学", "体育运动中的数学"]),
    "ELECTIVE_E": (73, 73, ["拓展视野", "日常生活", "地方特色"]),
}
# Source PDF page 21 has printed page 13. PDFKit pages are numbered from 1.
PDF_OFFSET = 8
PAREN = re.compile(r"(?m)^\s*（\s*([0-9０-９]{1,2})\s*）")
NUMERIC = re.compile(r"(?m)^\s*([0-9０-９]{1,2})[．.]\s*")
NORMAL = str.maketrans("０１２３４５６７８９","0123456789")

def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf8")).hexdigest()

def section_content_only(text: str, active: bool, strict: bool):
    """For core courses, only text after 内容要求 and before 教学提示/学业要求."""
    if not strict:
        return [(text, 0)], active
    lines = text.splitlines(keepends=True)
    chunks = []
    buf, start, pos = [], 0, 0
    for line in lines:
        if "【" in line and "内容要求" in line:
            if buf: chunks.append(("".join(buf), start))
            buf = []
            active = True
            start = pos + len(line)
            pos += len(line)
            continue
        if "【" in line and ("教学提示" in line or "学业要求" in line):
            if buf: chunks.append(("".join(buf), start))
            buf = []
            active = False
        if active:
            if not buf: start = pos
            buf.append(line)
        pos += len(line)
    if buf: chunks.append(("".join(buf), start))
    return chunks, active

def build(directory: Path, pdf_sha: str) -> dict:
    pages = {}
    for printed in range(13,74):
        f = directory / f"page-{printed+PDF_OFFSET}.txt"
        if not f.is_file():
            raise ValueError(f"Missing PDFKit-extracted source page {printed}: {f}")
        text = f.read_text(encoding="utf8")
        if len(text.strip()) < 120:
            raise ValueError(f"Source page extraction incomplete: {printed}")
        pages[printed] = text
    anchors, structure, counts = [], [], Counter()
    for track, (first, last, themes) in TRACKS.items():
        # Source topic headings are topic-level editorial navigation, NOT atom counts.
        structure.append({"track": track, "printed_page_start": first,
                          "printed_page_end": last, "source_topics": themes,
                          "source_topic_count":len(themes),
                          "official_atomic_denominator":None,
                          "source_topic_status":"TOPIC_INDEX_REQUIRES_HUMAN_REVIEW"})
        active = False
        for printed in range(first, last+1):
            text=pages[printed]
            blocks, active = section_content_only(text,active,track in ("COMPULSORY","SELECTIVE_COMPULSORY"))
            for fragment,offset in blocks:
                for match in list(PAREN.finditer(fragment))+list(NUMERIC.finditer(fragment)):
                    k = "PAREN_NUMBER" if match.re is PAREN else "SECTION_NUMBER"
                    # Source text never enters the committed report; only a content digest.
                    beginning=offset+match.start()
                    context=text[beginning:beginning+100]
                    ordinal=match.group(1).translate(NORMAL)
                    anchors.append({"id":f"KB18-{track}-{printed:02d}-{beginning:04d}-{k}",
                         "track":track,"printed_page":printed,"pdf_page":printed+PDF_OFFSET,
                         "marker_kind":k,"marker_number":int(ordinal),
                         "evidence_sha256":sha(context),"evidence_length":len(context),
                         "candidate_status":"AUTO_LOCATED_UNREVIEWED_NOT_OFFICIAL_ATOM",
                         "linked_editorial_objective_ids":[],
                         "teacher_review":"PENDING"})
                    counts[track]+=1
    editorial=json.loads((ROOT/"curriculum/highschool_math/source_anchored_skill_candidates_batch12.json").read_text(encoding="utf8"))
    if editorial.get("verified_official_atomic_denominator") is not None:
        raise ValueError("legacy editorial objective list falsely asserts official denominator")
    objective_pages=Counter((row["track"],row["source"]["printed_page"]) for row in editorial["items"])
    gaps=[]
    for track,(first,last,_) in TRACKS.items():
        for printed in range(first,last+1):
            n=sum(a["printed_page"]==printed and a["track"]==track for a in anchors)
            if n>0 and objective_pages[(track,printed)]==0:
                gaps.append({"track":track,"printed_page":printed,"source_numbered_markers":n,
                             "editorial_objectives_on_same_page":0,
                             "status":"PAGE_WITHOUT_EDITORIAL_OBJECTIVE_NOT_CONFIRMED_ATOM_GAP"})
    keys=[a["id"] for a in anchors]
    if len(keys)!=len(set(keys)): raise ValueError("nonunique source anchors")
    if not all(counts[t] for t in TRACKS):
        # Elective E's open-ended structure can legitimately contain zero numbered clauses.
        if any(not counts[t] for t in TRACKS if t!="ELECTIVE_E"):
            raise ValueError("missing numbered anchors: check extraction")
    return {"scope":"SOURCE_PAGE_MARKERS_NOT_OFFICIAL_ATOMIC_DENOMINATOR",
        "standard_title":"普通高中数学课程标准（2017年版2020年修订）",
        "standard_url":STANDARD_URL,
        "standard_pdf_sha256":pdf_sha,
        "source_extraction":"macOS PDFKit; original PDF and raw text never committed",
        "printed_pages_examined":{"first":13,"last":73,"count":61},
        "project_topic_index_count":sum(len(row[2]) for row in TRACKS.values()),
        "verified_official_atomic_denominator":None,
        "official_atom_coverage_rate":None,
        "source_numbered_marker_candidates":len(anchors),
        "source_markers_by_track":{k:counts[k] for k in TRACKS},
        "source_topics":structure,
        "editorial_objectives_total":len(editorial["items"]),
        "unrepresented_source_pages":gaps,
        "unrepresented_source_page_count":len(gaps),
        "warning_on_page_matching":"Page co-location is not a topic/requirement match; no full-coverage claim is permitted.",
        "markers":anchors,
        "unverified_source_markers":len(anchors),
        "human_confirmed_source_atoms":0,
        "linking_completeness":"UNKNOWN; 132 editorial objectives cannot count as official coverage",
        "warning":("Numbered symbols may also be examples, subheadings, or repeated indices; "
                   "human reading of every source clause is required before upgrading "
                   "anything to a confirmed requirement. E is local/open-ended.")}

def verify_document(data):
    if data["scope"]!="SOURCE_PAGE_MARKERS_NOT_OFFICIAL_ATOMIC_DENOMINATOR":
        raise ValueError("incorrect scope")
    if data["verified_official_atomic_denominator"] is not None or data["official_atom_coverage_rate"] is not None:
        raise ValueError("invented official denominator or coverage")
    if data["human_confirmed_source_atoms"] != 0:
        raise ValueError("no human signed off on these candidates")
    if sum(data["source_markers_by_track"].values()) != len(data["markers"]):
        raise ValueError("source marker count mismatch")
    if data["unrepresented_source_page_count"] != len(data["unrepresented_source_pages"]):
        raise ValueError("page-gap count mismatch")
    for page in data["unrepresented_source_pages"]:
        if page["editorial_objectives_on_same_page"]!=0 or page["source_numbered_markers"]<=0:
            raise ValueError("invalid page-gap evidence")
    for row in data["markers"]:
        first,last,_=TRACKS[row["track"]]
        if row["printed_page"]<first or row["printed_page"]>last:
            raise ValueError("wrong source track")
        if row["candidate_status"] != "AUTO_LOCATED_UNREVIEWED_NOT_OFFICIAL_ATOM" or row["teacher_review"] != "PENDING":
            raise ValueError("incorrect approval")
        if row["linked_editorial_objective_ids"]:
            raise ValueError("unreviewed source link")
    return True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--pages-dir",type=Path)
    parser.add_argument("--pdf-file",type=Path)
    parser.add_argument("--check", action="store_true")
    args=parser.parse_args()
    if args.check:
        data=json.loads(OUTPUT.read_text(encoding="utf8"))
        verify_document(data)
        print(f"K00 snapshot PASS: {len(data['markers'])} unverified source markers / "
              f"{data['project_topic_index_count']} topic labels; official atom denominator UNKNOWN")
        return
    if not args.pages_dir or not args.pdf_file:
        parser.error("--pages-dir and --pdf-file required to build source snapshot")
    digest=hashlib.sha256(args.pdf_file.read_bytes()).hexdigest()
    data=build(args.pages_dir,digest)
    verify_document(data)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(f"K00 built: {len(data['markers'])} unreviewed marker candidates; by track "
          f"{data['source_markers_by_track']}; project topic labels {data['project_topic_index_count']}")
if __name__=="__main__":main()
