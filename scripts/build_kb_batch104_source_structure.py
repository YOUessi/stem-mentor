#!/usr/bin/env python3
"""Mac PDFKit-grounded triage of printed pages 13/14/51; NOT formal atomization.

These three pages had zero explicit numbered requirement anchors in an older
heuristic. That absence must not be interpreted as either missing standards
or a complete mathematical-atom inventory. No official PDF passages are committed.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = (13, 14, 51)
FINGERPRINTS_SHA256 = "ec26621b7f358f892355d6e6b93622e529df30cfd6067fa1f48d77df48ffc19a"
PARTITION_SHA256 = "0737bbb2fe9e66170c900ab1b05ac36ca84fdf11bdb37798d4e43ea643cace12"
SOURCE_PDF_SHA256 = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
PDF = Path.home() / "Library/Caches/stem-mentor-source-review/highschool_math_standard_2020.pdf"
LOCALLINES = Path("/private/tmp")
FINGERPRINTS = ROOT / "curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
SEGMENTS = ROOT / "curriculum/highschool_math/k00_batch73_page_partition_witness.json"
OUT = ROOT / "docs/evaluation/KB_BATCH104_SOURCE_PAGES_13_14_51.json"
MD = ROOT / "docs/evaluation/KB_BATCH104_SOURCE_PAGES_13_14_51.md"
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A",
          "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")

# The editorial interpretation is human-readable but NOT copied official text.
# Each span covers a whole consecutive portion of the PDFKit page, including
# tables and footer fragments, so missing numbered markers remain visible.
SECTIONS = (
 (13, 1, 6, "COMPULSORY", "COURSE_SCOPE",
  "必修课程的主题集合、课程学分与建议总课时说明；这是课程序列约束，不是六个数学定理。"),
 (13, 7, 16, "COMPULSORY", "CONTINUED_COURSE_TABLE",
  "必修课程课时建议表的前半部分，涉及集合、逻辑、等式不等式、二次函数相关学习单元；这是主题目录而非数学知识原子计数。"),
 (13, 17, 17, "COMPULSORY", "PAGE_FOOTER",
  "源页尾部页码记号，不含可建立数学原子的教学陈述。"),
 (14, 1, 3, "COMPULSORY", "CONTINUED_COURSE_TABLE",
  "必修课时分配表的续表头和栏位说明，不应将表头数字误算为课程原子。"),
 (14, 4, 26, "COMPULSORY", "CONTINUED_COURSE_TABLE",
  "必修函数、几何与代数、概率统计、建模与探究等主题与建议课时；目录/课时不能当作有证明的知识条目。"),
 (14, 27, 31, "COMPULSORY", "SECTION_INTRO",
  "进入必修预备知识章节，介绍与初中内容衔接的课程意图；具体数学要求须跨页继续核对后再拆分。"),
 (14, 32, 32, "COMPULSORY", "PAGE_FOOTER",
  "源页尾部的纸质页码标识，不对应可证明的数学结论或新的教学知识原子。"),
 (51, 1, 3, "ELECTIVE_GENERAL", "COURSE_SCOPE",
  "选修课程定位和学生自主选择的说明，不能作为选修各方向正式知识条目数量。"),
 (51, 4, 14, "ELECTIVE_GENERAL", "TRACK_DEFINITION",
  "介绍选修A至E的适读人群与定位；选修E属于开放扩展，不能据此推断一个固定全国必学知识原子分母。"),
 (51, 15, 19, "ELECTIVE_GENERAL", "ASSESSMENT_POLICY",
  "说明选修修习评价等实施安排；属于课程政策，不是待证数学定理。"),
 (51, 20, 23, "ELECTIVE_A", "TRACK_TRANSITION",
  "开始列出选修A相关专题及学分，属于课程目录和轨道边界。"),
 (51, 24, 27, "ELECTIVE_A", "CROSS_PAGE_CONTENT_OPENING",
  "选修A的极限与连续性内容从此开始并延续至下一页；本页片段不足以完成该知识单元的原子化，必须连同第52页复核。"),
)
KINDS = {"COURSE_SCOPE", "CONTINUED_COURSE_TABLE", "SECTION_INTRO",
         "PAGE_FOOTER", "TRACK_DEFINITION", "ASSESSMENT_POLICY",
         "TRACK_TRANSITION", "CROSS_PAGE_CONTENT_OPENING"}
def require(condition: bool, why: str):
    if not condition:
        raise ValueError(why)
def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
def build(sections=SECTIONS, verify_local_pdf=False):
    require(sha256(FINGERPRINTS.read_bytes()).hexdigest()==FINGERPRINTS_SHA256,
            "source page fingerprint registry mutated")
    require(sha256(SEGMENTS.read_bytes()).hexdigest()==PARTITION_SHA256,
            "source partition evidence mutated")
    fingerprint = json.loads(FINGERPRINTS.read_text(encoding="utf8"))
    prior = json.loads(SEGMENTS.read_text(encoding="utf8"))
    require(prior["source_pdf_sha256"] == SOURCE_PDF_SHA256, "source PDF provenance mismatch")
    require(prior["full_page_teacher_reviews"] == 0, "review authority drift")
    require(prior["officially_certified_denominators"] == {t:None for t in TRACKS},
            "official denominators must remain unknown")
    meta = {int(p["printed_page"]):p for p in fingerprint["pages"] if int(p["printed_page"]) in PAGES}
    require(set(meta)==set(PAGES), "missing source page fingerprints")
    require(len(sections)==12, "expected twelve separate source-structure decisions")
    if verify_local_pdf:
        require(PDF.is_file() and sha256(PDF.read_bytes()).hexdigest()==SOURCE_PDF_SHA256,
                "Mac source PDF SHA drift or missing")
    page_rows = {}
    for page in PAGES:
        raw = LOCALLINES / f"kb56_page_{page}.txt"
        if verify_local_pdf:
            require(raw.is_file() and sha256(raw.read_bytes()).hexdigest()==meta[page]["pdfkit_text_sha256"],
                    "Mac PDFKit page text SHA drift")
        page_rows[page] = meta[page]
    by_page = {p:[] for p in PAGES}
    results=[]
    for idx,(page,lo,hi,track,kind,paraphrase) in enumerate(sections,1):
        require(page in PAGES and track in TRACKS + ("ELECTIVE_GENERAL",),
                "unexpected page or course track")
        require(kind in KINDS and len(paraphrase)>=16, "invalid source classification")
        require(type(lo) is int and type(hi) is int and 0<lo<=hi, "invalid source range")
        require((page!=51 and track=="COMPULSORY") or
                (page==51 and track in ("ELECTIVE_GENERAL","ELECTIVE_A")), "cross-track source classification")
        by_page[page].extend(range(lo,hi+1))
        results.append({
          "decision_id":f"KB104-STRUCT-{idx:02d}",
          "printed_page":page, "line_start":lo, "line_end":hi,
          "pdf_page_index":page_rows[page]["pdf_page_index"],
          "pdfkit_page_sha256":page_rows[page]["pdfkit_text_sha256"],
          "source_pdf_sha256":SOURCE_PDF_SHA256,
          "track_scope":track, "structural_class":kind,
          "original_editorial_paraphrase":paraphrase,
          "official_atom_count":None, "official_atom_id":None,
          "source_complete_math_atomization":False,
          "teacher_review_status":"REVIEW_PENDING",
          "student_authoritative":False,
          "cross_page_followup_required":kind in {"CROSS_PAGE_CONTENT_OPENING","SECTION_INTRO"},
        })
    for page,group in by_page.items():
        expected=next(int(s["last_line"]) for s in prior["segments"] if s["printed_page"]==page
                      and not any(v["printed_page"]==page and v["last_line"]>s["last_line"] for v in prior["segments"]))
        require(group==list(range(1,expected+1)),
                f"source page {page}: missing/overlapping/out-of-order coverage")
    report={
      "schema_version":"kb104-mac-pdfkit-structural-zero-anchor-triage-v1",
      "scope":"EDITORIAL_PAGE_STRUCTURE_NOT_OFFICIAL_ATOMIZATION",
      "source_pdf_sha256":SOURCE_PDF_SHA256,
      "source_page_fingerprints_sha256":sha256(FINGERPRINTS.read_bytes()).hexdigest(),
      "source_partition_sha256":sha256(SEGMENTS.read_bytes()).hexdigest(),
      "source_pages":list(PAGES),
      "source_page_line_counts":{str(p):len(by_page[p]) for p in PAGES},
      "decision_count":len(results),
      "covered_pdfkit_lines":sum(map(len,by_page.values())),
      "zero_numbered_source_anchors_is_not_zero_mathematical_scope":True,
      "cross_page_requirement_pending":[14,51],
      "official_atom_denominators_by_track":{t:None for t in TRACKS},
      "teacher_fully_atomized_pages":0,
      "teacher_approved":0,"student_authoritative_releases":0,
      "kind_counts":dict(sorted(Counter(r["structural_class"] for r in results).items())),
      "editorial_decisions":results,
    }
    return report
def markdown(report):
    lines=["# Batch104｜官方课标纸质第13、14、51页来源结构分段核查","",
       "**结论：** 这些页面没有旧启发式编号锚点并不等于数学课标不存在或已经完整覆盖。"
       "本报告是人工语义编辑草案，不是正式的课程原子分母、教师签字或原文转载。","",
       f"原 PDF SHA256：`{report['source_pdf_sha256']}`；3页、"
       f"{report['covered_pdfkit_lines']}条PDFKit行，{report['decision_count']}个连续结构区段。","",
       "| 页码 | 行号 | 轨道/范围 | 原创结构解释 |",
       "|---|---|---|---|"]
    for r in report["editorial_decisions"]:
        lines.append(f"| {r['printed_page']} | {r['line_start']}–{r['line_end']} | "
                     f"{r['track_scope']}/{r['structural_class']} | {r['original_editorial_paraphrase']} |")
    lines += ["","## 待做的严格审核","",
      "第14页引入预备知识，需联读第15页之后的具体要求，不能仅由目录结构计数。"
      "第51页由选修总体介绍过渡到选修A微积分，须联读第52页的后续内容再作语义原子划分。","",
      "正式七轨知识原子分母仍为 UNKNOWN；来源第13、14、51页不应虚构缺失的定理，也不应标记已完成逐页教师原子化。",""]
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local-source",action="store_true")
    args=p.parse_args()
    report=build(verify_local_pdf=args.verify_local_source)
    for path,value in ((OUT,canonical(report)),(MD,markdown(report))):
        if args.check:
            require(path.is_file() and path.read_text(encoding="utf8")==value,"generated audit drift "+str(path))
        else:
            path.write_text(value,encoding="utf8")
    print(f"Batch104 source audit: {report['decision_count']} source spans / {report['covered_pdfkit_lines']} PDFKit lines, check={args.check}, local={args.verify_local_source}")
if __name__=="__main__":main()
