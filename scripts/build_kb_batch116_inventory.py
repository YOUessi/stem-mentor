#!/usr/bin/env python3
"""61-page source *inventory*, not official knowledge atoms or teacher certification.

Mac-only provenance checks use a locally authorized PDF and volatile PDFKit text.
Committed reports contain only hashes, page numbers, and project-authored labels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
FULL_MANIFEST = ROOT / "docs/evaluation/KB_BATCH116_FULL_PDF_FINGERPRINTS.json"
OUT = ROOT / "docs/evaluation/KB_BATCH116_SOURCE_INVENTORY.json"
QUEUE = ROOT / "docs/evaluation/KB_BATCH116_REVIEW_QUEUE.md"
PDF = Path.home() / "Library/Caches/stem-mentor-source-review/highschool_math_standard_2020.pdf"
PDF_SHA = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A", "ELECTIVE_B",
          "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")
# Printed-page segments are independently readable editorial headings, not atomic denominators.
# Page 51 introduces elective tracks; page 69 crosses from C into D.
GROUPS = (
    (13, 14, "COMPULSORY", "course_plan"),
    (15, 18, "COMPULSORY", "logic_sets_inequalities"),
    (19, 24, "COMPULSORY", "functions_trig"),
    (25, 30, "COMPULSORY", "vectors_spatial_geometry"),
    (31, 34, "COMPULSORY", "probability_descriptive_statistics"),
    (35, 36, "COMPULSORY", "modeling_inquiry"),
    (37, 37, "SELECTIVE_COMPULSORY", "course_plan"),
    (38, 41, "SELECTIVE_COMPULSORY", "sequence_calculus"),
    (42, 46, "SELECTIVE_COMPULSORY", "spatial_vectors_analytic_geometry"),
    (47, 49, "SELECTIVE_COMPULSORY", "counting_probability_statistics"),
    (50, 50, "SELECTIVE_COMPULSORY", "modeling_inquiry"),
    (51, 51, "MULTI_TRACK_TRANSITION", "elective_course_introduction"),
    (52, 57, "ELECTIVE_A", "advanced_calculus_algebra_statistics"),
    (58, 64, "ELECTIVE_B", "advanced_topics_models"),
    (65, 68, "ELECTIVE_C", "logic_economic_social_models_survey"),
    (69, 69, "MULTI_TRACK_TRANSITION", "social_survey_to_art_mathematics"),
    (70, 73, "ELECTIVE_D", "art_music_sport_mathematics"),
)
FLAGS = {
    21: ("formula_layout_review",), 22: ("formula_layout_review",),
    35: ("unreliable_pdfkit_control_bytes",),
    51: ("elective_track_boundary",), 58: ("elective_track_boundary",),
    59: ("formula_layout_review",), 69: ("elective_track_boundary",),
    73: ("pdf_excerpt_ends_mid_topic",),
}

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def render(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"

def previous_reviewed():
    reviewed = {}
    for f in sorted((ROOT / "docs/evaluation").glob("KB_BATCH*_SCOPE.json")):
        item = json.loads(f.read_text())
        if item.get("source_pdf_sha256") != PDF_SHA or not isinstance(item.get("line_counts"), dict):
            continue
        for p in map(int, item["line_counts"]):
            require(13 <= p <= 73 and p not in reviewed, f"duplicate previously reviewed page {p}")
            reviewed[p] = f.name
    return reviewed

def inventory(*, verify_local_source=False, source_pages=None, groups=GROUPS,
              denominators=None, teacher_approvals=0, full_manifest=None):
    reg = json.loads(REGISTRY.read_text())
    require(reg.get("official_pdf_sha256") == PDF_SHA, "source PDF identity changed")
    orig = reg["pages"] if source_pages is None else source_pages
    require(len(orig) == 61, "page register incomplete or duplicated")
    bypage = {p["printed_page"]: p for p in orig}
    require(len(bypage) == 61 and set(bypage) == set(range(13,74)),
            "page register is not consecutive 13..73")
    require(all(bypage[p]["pdf_page_index"] == p + 7 for p in bypage),
            "PDF-to-printed page mapping changed")
    canonical = {p["printed_page"]:p for p in reg["pages"]}
    require(all(bypage[p]["pdfkit_text_sha256"] == canonical[p]["pdfkit_text_sha256"] for p in bypage),
            "page fingerprint changed from authenticated manifest")
    # Cross-validate the previously registered 61-page excerpt against all 188
    # independently PDFKit-hashed physical pages. No raw passages may be stored.
    full = json.loads(FULL_MANIFEST.read_text()) if full_manifest is None else full_manifest
    require(full.get("pdf_sha256") == PDF_SHA and full.get("pdf_page_count") == 188,
            "full original PDF source identity / physical page count changed")
    whole = full.get("pages")
    require(isinstance(whole,list) and len(whole) == 188, "188-page fingerprint record incomplete")
    require(full.get("legacy_excerpt_index_first") == 20 and
            full.get("legacy_excerpt_index_last") == 80 and
            full.get("legacy_excerpt_index_count") == 61 and
            full.get("outside_excerpt_page_count") == 127 and
            full.get("copyright_source_text_embedded") is False,
            "full PDF metadata or copyright contract changed")
    require([r.get("pdf_page_index") for r in whole] == list(range(188)),
            "full PDF indices missing, duplicated, or reordered")
    for r in whole:
        require(set(r) == {"pdf_page_index","pdfkit_utf8_sha256","unicode_scalar_count",
            "newline_count","control_scalar_count","has_extractable_text","legacy_61_page_excerpt"},
            "full PDF manifest has missing fields or copyrighted extra text")
        require(len(r["pdfkit_utf8_sha256"]) == 64 and r["unicode_scalar_count"] >= 0,
            "bad full PDF fingerprint")
        require(r["legacy_61_page_excerpt"] == (20 <= r["pdf_page_index"] <= 80),
            "legacy page extent falsified")
    require(all(whole[p+7]["pdfkit_utf8_sha256"] == bypage[p]["pdfkit_text_sha256"]
                for p in range(13,74)), "full PDF hash not equal to 61 pinned page hashes")
    assigned = {}
    for lo, hi, track, label in groups:
        require(lo <= hi and track in TRACKS + ("MULTI_TRACK_TRANSITION",), "invalid track group")
        require(label and all(p not in assigned for p in range(lo, hi + 1)), "overlapping track groups")
        assigned.update({p: (track, label) for p in range(lo, hi + 1)})
    require(set(assigned) == set(range(13,74)), "chapter / track group gap")
    require(assigned[51][0] == assigned[69][0] == "MULTI_TRACK_TRANSITION",
            "mixed track boundaries lost")
    require(assigned[73][0] == "ELECTIVE_D", "end-of-excerpt track drift")
    # Source pages 13..73 are a bounded reference excerpt, not full official standard.
    official = {t: None for t in TRACKS}
    require(denominators is None or denominators == official,
            "official denominator cannot be invented by editor")
    require(teacher_approvals == 0, "no human teacher review records exist")
    if verify_local_source:
        require(PDF.is_file() and sha(PDF) == PDF_SHA, "authorized local original missing or modified")
    reviewed = previous_reviewed()
    records = []
    for p in range(13,74):
        src = bypage[p]
        if verify_local_source:
            f = Path(f"/private/tmp/kb56_page_{p}.txt")
            require(f.is_file() and sha(f) == src["pdfkit_text_sha256"],
                    f"page {p} local PDFKit bytes missing or altered")
        track, group = assigned[p]
        records.append({
            "printed_page": p, "pdf_page_index": src["pdf_page_index"],
            "pdfkit_text_sha256": src["pdfkit_text_sha256"],
            "source_group_hint": group, "track_hint": track,
            "manual_visual_review_flags": list(FLAGS.get(p, ())),
            "prior_structure_review_artifact": reviewed.get(p),
            "structure_review_status": "PROVISIONAL_STRUCTURAL_REVIEW" if p in reviewed else "NOT_REVIEWED",
            "complete_teacher_atomization": False, "official_atom_count": None,
            "teacher_approval_record": None, "authoritative_student_release": False,
        })
    open_pages = [r for r in records if r["structure_review_status"] == "NOT_REVIEWED"]
    counts = Counter(r["track_hint"] for r in open_pages)
    return {
        "batch": 116, "source_extent": "PARTIAL_PRINTED_PAGES_13_TO_73_NOT_ENTIRE_STANDARD",
        "source_pdf_sha256": PDF_SHA, "source_manifest_sha256": sha(REGISTRY),
        "full_pdf_fingerprint_manifest_sha256": sha(FULL_MANIFEST),
        "full_original_pdf_physical_pages": 188,
        "physical_pages_outside_legacy_61_excerpt": 127,
        "whole_pdf_pages_provenance_fingerprinted": 188,
        "source_page_count": 61, "structure_reviewed_count": len(reviewed),
        "structure_unreviewed_count": len(open_pages), "reviewed_printed_pages": sorted(reviewed),
        "unreviewed_printed_pages": [x["printed_page"] for x in open_pages],
        "pending_review_pages_by_track_hint": {t: counts[t] for t in TRACKS + ("MULTI_TRACK_TRANSITION",)},
        "chapter_groups": [{"first":lo,"last":hi,"track_hint":t,"editorial_group":g} for lo,hi,t,g in groups],
        "pages": records,
        "seven_track_official_atom_denominators": official,
        "seven_track_approved_atom_counts": {t: 0 for t in TRACKS},
        "seven_track_certified_coverage": {t: None for t in TRACKS},
        "teacher_fully_atomized_pages": 0, "teacher_approvals": 0, "student_authority_releases": 0,
        "known_outside_extent": ["ELECTIVE_E_NOT_PRESENT_IN_THIS_61_PAGE_EXCERPT",
                                 "DOCUMENT_CONTINUES_BEYOND_PRINTED_PAGE_73"],
        "review_rules": [
            "Hash-verified access to source is not certified atomization.",
            "Chapter group labels are editorial scope hints, not official knowledge atoms.",
            "No denominator or completion percentage is permitted until independently verified.",
            "Mixed-track pages and malformed PDFKit equations require source-image review.",
        ]
    }

def review_queue(v):
    lines = [
        "# Batch116｜61页来源范围与逐章审校队列", "",
        "已在Mac用原PDF的PDFKit读取并哈希锁定整份188个物理PDF页，但此台账的数学课程结构审查只覆盖印刷页13–73（61页）。",
        "其余127个物理PDF页目前只有来源指纹，不能因此推断它们都是未覆盖知识点。",
        "选修E在这61页中尚无独立完整条目分母，不能据此当作0。章节分组仅是人工可复核的工程候审提示。", "",
        f"前期有证据的结构页：{v['structure_reviewed_count']}/61；待结构审查：{v['structure_unreviewed_count']}/61；",
        "教师正式逐页原子化：0/61；七轨官方原子分母均UNKNOWN；教师批准0、学生权威发布0。", "",
        "| 印刷页范围 | 轨道提示 | 内容分组 | 待结构审查页 | 图像专项风险 |",
        "|---|---|---|---:|---|",
    ]
    for g in v["chapter_groups"]:
        rows = [p for p in v["pages"] if (g["first"] <= p["printed_page"] <= g["last"]
                and p["structure_review_status"] == "NOT_REVIEWED")]
        flagged = [str(p["printed_page"]) for p in v["pages"]
                   if g["first"] <= p["printed_page"] <= g["last"] and p["manual_visual_review_flags"]]
        lines.append(f"| {g['first']}–{g['last']} | {g['track_hint']} | {g['editorial_group']} | {len(rows)} | {','.join(flagged) or '—'} |")
    lines += ["", "## 验收门槛", "",
        "1. 每页核对原件的章节、【内容要求】、学业要求、星号可选项及跨页连续性；保存合法的来源定位证据，不复制教材正文。",
        "2. 每条拟议原子分型为概念、定理、方法、实践能力，核对必要条件、唯一ID、来源区间及归属轨道；跨轨或未证实项保持争议。",
        "3. 已识别内容与缺口分别登记，七轨分母只有在**整个正式课程范围**完成独立核验才可从UNKNOWN变成数字。",
        "4. 教师正式审校前不得APPROVED，学生独立解题验证及权威发布仍为0；禁止公开教师完整答案。",
        "5. PDFKit 失真页35与跨轨页51、69必须看原始页面图像；第73页不是课标终点。", "",
        "## 本批优先队列", "",
        "先处理前期未逐页校核的37–50页（选择性必修）、27–36页（必修）、64–73页（选修分轨），",
        "然后检查整份课标的实际末页、选修E及此前遗漏的范围。课程分母在此之前不允许填写猜测值。", ""
    ]
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--verify-local-source", action="store_true")
    a = p.parse_args()
    v = inventory(verify_local_source=a.verify_local_source)
    require(v["structure_reviewed_count"] == 18 and v["structure_unreviewed_count"] == 43,
            "historic structure review snapshot drift: reevaluate before freezing")
    for f, body in ((OUT, render(v)), (QUEUE, review_queue(v))):
        if a.check:
            require(f.read_text() == body, "generated file drift " + str(f))
        else:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(body, encoding="utf-8")
    print("Batch116 source ledger: 61 fingerprints, 18 provisional structure pages, 43 pending, "
          "7 track atom denominators UNKNOWN, teacher-approved 0")
if __name__ == "__main__":
    main()
