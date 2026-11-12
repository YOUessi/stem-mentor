#!/usr/bin/env python3
"""Fail-closed physical-page scope segmentation of the 188-page source.

Boundary labels are **editorial navigation**, not automatically certified
official syllabi or assertions that examples cannot yield curriculum review.
Only identifiers, locked hashes, risks and statuses are committed.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"docs/evaluation/KB_BATCH116_FULL_PDF_FINGERPRINTS.json"
TARGET=ROOT/"docs/evaluation/KB_BATCH117_WHOLE_PDF_SCOPE.json"
MARKDOWN=ROOT/"docs/evaluation/KB_BATCH117_WHOLE_PDF_SCOPE.md"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
# These headings were independently checked in the author's licensed local
# original using macOS PDFKit on 2026-11-13. They are *section cues*, not
# atom coverage statements or a substitute for checking formulas in images.
SEGMENTS=(
    (0,19,"FRONT_MATTER_FOUNDATION","标准前言、结构、课程目标与整体说明"),
    (20,80,"CORE_CURRICULUM_CONTENT","课标七轨课程内容区域（第73印刷页包含选修E页内转换）"),
    (81,86,"ACADEMIC_QUALITY","学业质量描述及水平要求"),
    (87,106,"IMPLEMENTATION_GUIDANCE","教学、评价、教材及实施建议"),
    (107,113,"APPENDIX_COMPETENCY_LEVELS","附录1：学科核心素养水平"),
    (114,187,"APPENDIX_TEACHING_CASES","附录2：教学与评价案例（含数学示例）"),
)
def require(value,why):
    if not value: raise ValueError(why)
def produce():
    src=json.loads(INPUT.read_text())
    require(src["pdf_page_count"]==188 and len(src["pages"])==188,"unexpected PDF length")
    require(src["pdf_sha256"]=="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195","source identity drift")
    require([p["pdf_page_index"] for p in src["pages"]]==list(range(188)),"reordered or missing physical pages")
    pages=[]
    for lo,hi,label,description in SEGMENTS:
        for i in range(lo,hi+1):
            p=src["pages"][i]
            pages.append({
                "pdf_page_index":i,
                "pdfkit_utf8_sha256":p["pdfkit_utf8_sha256"],
                "editorial_section_cue":label,
                "legacy_printed_content_page":i-7 if 20<=i<=80 else None,
                "official_atom_count":None,
                "teacher_review_status":"NOT_REVIEWED",
                "source_text_embedded":False,
                "followup":"VERIFY_FIGURES_AND_CROSS_SECTION_CONTENT" if i in (42,58,76,80,114,146,178,179,182,183) else "NEEDS_ATOM_BY_ATOM_SCOPE_REVIEW",
            })
    require(len(pages)==188 and [x["pdf_page_index"] for x in pages]==list(range(188)),"missing/overlapping sections")
    require(sum(hi-lo+1 for lo,hi,_,_ in SEGMENTS)==188,"segment denominator drift")
    segments=[{"index_range":[lo,hi],"page_count":hi-lo+1,
               "editorial_section_cue":label,"description":description,
               "official_atom_count":None,"human_classification_certified":False}
              for lo,hi,label,description in SEGMENTS]
    data={"source_pdf_sha256":src["pdf_sha256"],"total_physical_pdf_pages":188,
          "old_content_range_pdf_indices":[20,80],
          "old_content_range_physical_pages":61,
          "outside_old_content_range_physical_pages":127,
          "all_original_source_text_omitted":True,
          "human_certified_curriculum_atom_count":0,
          "teacher_approved_count":0,
          "official_seven_track_atom_denominators":{t:None for t in TRACKS},
          "explicit_limitation":"Section cue is navigation only. Do not equate 188 physical pages with 188 syllabus pages, and do not automatically exclude material in cases/appendices.",
          "segments":segments,"pages":pages}
    md=["# Batch117｜188个物理PDF页的完整范围结构（候审导航）","",
        "此分类使用Mac已授权的本地2020修订课标原件，以PDFKit抽取的章节起始标题定位；**不是教师认证的正式课程知识原子化**。源文本、版权原件不提交。","",
        "| 物理页索引（0起） | 页数 | 编辑性章节线索 | 状态 |",
        "|---|---:|---|---|"]
    for s in segments:
        md.append(f"| {s['index_range'][0]}–{s['index_range'][1]} | {s['page_count']} | {s['description']} | 结构导航／待人工逐原子确认 |")
    md.extend(["","**数目边界**：此前印刷13–73页映射为物理索引20–80（61页）；范围外有127个物理页，包括整体课程目标、学业质量、实施建议与附录。不能把127页一概认定为无教学价值，特别是附录实例可做非规范性教学素材。","",
        "**跨轨与公式风险**：印刷73页包含选修E页内开始；印刷35页PDFKit控制字符失真；数学公式及图形必须回到Mac原PDF图像核对。","",
        "**未完成**：七轨官方知识原子分母全部 UNKNOWN；教师正式逐页原子化0；正式批准0；学生端权威发布0。","",
        "本文件与同名JSON是编辑性结构台账，不得作为知识库完成率或审批率的分母。",""])
    return data,"\n".join(md)
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--write",action="store_true")
    a.add_argument("--check",action="store_true")
    opt=a.parse_args()
    require(opt.write!=opt.check,"choose --write or --check")
    data,md=produce()
    result={TARGET:json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+"\n",MARKDOWN:md}
    for path,s in result.items():
        if opt.write: path.write_text(s)
        else:require(path.exists() and path.read_text()==s,f"artifact drift: {path}")
    print("Batch117 whole-PDF navigation CHECK",len(data["pages"]),"pages, 6 editorial segments, 7 denominators UNKNOWN, 0 approvals")
if __name__=="__main__":main()
