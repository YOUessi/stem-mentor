#!/usr/bin/env python3
"""Batch53 K00: cross-page discovery ledger; related topics never imply coverage.

Every row is an original editorial source candidate from Batch51/52. This
ledger is a review queue, not a certified syllabus denominator or an approved
knowledge record. Original copyrighted PDF page text is not committed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "docs/evaluation"
CURR = ROOT / "curriculum/highschool_math"
SOURCE = CURR / "k00_batch51_pdfkit_page_fingerprints.json"
VISUAL = CURR / "k00_batch51_page35_modelling_candidate_split.json"
BASE51 = EVAL / "KB_BATCH51_OFFICIAL_SOURCE_PAGE_GATE.json"
BASE52 = EVAL / "KB_BATCH52_CRITICAL_SOURCE_CROSSWALK.json"
EDITORIAL = EVAL / "KB_BATCH50_PROJECT_SCOPE_OVERLAY.json"
DEST = EVAL / "KB_BATCH53_CROSS_PAGE_REVIEW_QUEUE.json"
MARKDOWN = EVAL / "KB_BATCH53_CROSS_PAGE_REVIEW_QUEUE.md"
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A",
          "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")

# Human-curated, source-topic discovery leads, *not* mathematics equivalences.
# The first nine were absent from the Batch52 same-page links. The final seven
# are the visually read Batch51 page35 modelling candidates (not PDF text).
LINKS = {
    "KB52-COMPULSORY-P034-U01": ("KB32-C-P031-A006","KB32-C-P031-A007"),
    "KB52-COMPULSORY-P034-U02": ("KB32-C-P031-A002","KB32-C-P031-A003"),
    "KB52-SELECTIVE_COMPULSORY-P041-U01": ("KB32-S-P038-A001",),
    "KB52-SELECTIVE_COMPULSORY-P041-U03": ("KB32-S-P038-A005","KB32-S-P038-A009"),
    "KB52-SELECTIVE_COMPULSORY-P041-U04": ("KB32-S-P039-A001",),
    "KB52-SELECTIVE_COMPULSORY-P041-U05": ("KB32-S-P039-A005","KB32-S-P039-A006"),
    "KB52-SELECTIVE_COMPULSORY-P041-U07": ("KB32-S-P040-A001",),
    "KB52-SELECTIVE_COMPULSORY-P041-U08": ("KB32-S-P042-A001","KB32-S-P043-A008"),
    "KB52-ELECTIVE_C-P065-U07": ("KB33-C-P066-A001","KB33-C-P066-A003","KB33-C-P067-A002"),
    "KB51-C-P035-V001": ("KB32-C-P034-A003",),
    "KB51-C-P035-V002": ("KB32-C-P034-A003","KB31-C-P023-A004"),
    "KB51-C-P035-V003": ("KB32-C-P034-A004",),
    "KB51-C-P035-V004": ("KB32-C-P034-A004","KB32-C-P034-A005"),
    "KB51-C-P035-V005": ("KB32-C-P034-A001","KB32-C-P034-A005"),
    "KB51-C-P035-V006": ("KB32-C-P034-A001","KB32-C-P030-A001"),
    "KB51-C-P035-V007": ("KB32-C-P034-A003","KB32-C-P034-A004","KB32-C-P034-A005"),
}
# Short, specific failure mode to check during actual content equivalence review.
RISK = {
    "KB52-COMPULSORY-P034-U01":"古典概型必须另证所有基本结果等可能。",
    "KB52-COMPULSORY-P034-U02":"有限样本空间并不能单独推出等可能概率。",
    "KB52-SELECTIVE_COMPULSORY-P041-U01":"数列函数定义域不能误写成全体实数。",
    "KB52-SELECTIVE_COMPULSORY-P041-U03":"求通项时要区分首项和n大于1的差分。",
    "KB52-SELECTIVE_COMPULSORY-P041-U04":"差商收敛与仅有很小的割线斜率不是同一条件。",
    "KB52-SELECTIVE_COMPULSORY-P041-U05":"链式法则要求可导，且必须保留内层导数。",
    "KB52-SELECTIVE_COMPULSORY-P041-U07":"微积分史料是史实证据，不是公式的数学证明。",
    "KB52-SELECTIVE_COMPULSORY-P041-U08":"解析几何课程衔接不是独立数学定理。",
    "KB52-ELECTIVE_C-P065-U07":"经济模型属于选修案例，不能自动列为必修原子。",
    "KB51-C-P035-V001":"提出变量前应先确定真实研究对象与目标。",
    "KB51-C-P035-V002":"数学模型参数和现实单位不能混为一谈。",
    "KB51-C-P035-V003":"数值求解正确仍需核对结果对应的现实量。",
    "KB51-C-P035-V004":"数据不一致时须区分参数误差与结构假设失效。",
    "KB51-C-P035-V005":"形式计算正确不是模型具有外部效度的证明。",
    "KB51-C-P035-V006":"有限实例支持猜想不意味着一般定理已证明。",
    "KB51-C-P035-V007":"课题研究需要过程证据，不能仅以成品充当过程。",
}

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def assemble(*, source=None, visual=None, b51=None, b52=None, overlay=None, links=None):
    source = deepcopy(source if source is not None else load(SOURCE))
    visual = deepcopy(visual if visual is not None else load(VISUAL))
    b51 = deepcopy(b51 if b51 is not None else load(BASE51))
    b52 = deepcopy(b52 if b52 is not None else load(BASE52))
    overlay = deepcopy(overlay if overlay is not None else load(EDITORIAL))
    links = deepcopy(links if links is not None else LINKS)
    pdf_sha = source["official_pdf_sha256"]
    require(pdf_sha == visual["source_pdf_sha256"] ==
            b51["source_pdf_sha256"] == b52["source_pdf_sha256"],
            "PDF provenance digest mismatch")
    require(len(source["pages"]) == len(b51["pages"]) == 61 and
            {x["printed_page"] for x in source["pages"]} == set(range(13,74)),
            "61-page source coverage missing")
    require(source["pdf_total_pages"] == 188, "unexpected syllabus PDF")
    require(visual["source_printed_page"] == 35 and
            visual["pdf_page_index"] == 42 and
            visual["page_source_text_extractor"] ==
            "PDFKIT_CORRUPT_USE_VISUAL_RENDER_FOR_PROVISIONAL_SPLIT",
            "visual source cannot be treated as PDF text")
    require(len(visual["candidates"]) == 7 and len(b52["rows"]) == 28 and
            b52["new_triage_candidates"] == 28, "35 candidate count drift")
    require(overlay["summary"]["project_candidates"] == 313 and
            len(overlay["rows"]) == 313, "project editorial denominator drift")
    require(overlay["summary"]["official_atom_denominator"] is None and
            b51["review_gate"]["official_atomic_knowledge_denominator"] is None and
            all(b52["official_atomic_denominator"][t] is None for t in TRACKS),
            "falsely certified official denominator")
    require(overlay["summary"]["teacher_approved"] == 0 and
            overlay["summary"]["student_published"] == 0,
            "falsely approved editorial content")
    require(len(b51["legacy_non_equivalent_review_queue"]) == 12,
            "legacy non-equivalent queue count drift")
    pages = {p["printed_page"]:p for p in source["pages"]}
    editor = {r["editorial_id"]:r for r in overlay["rows"]}
    require(len(editor) == 313, "duplicate editorial IDs")
    require(all(not row["teacher_approved"] and not row["student_published"]
                and not row["math_certified"] and not row["official_clause_verified"]
                for row in editor.values()), "editorial record falsely certified or released")
    former_unlinked = {r["candidate_id"] for r in b52["rows"]
                       if not r["related_editorial_ids_not_equivalence"]}
    visuals = {r["id"] for r in visual["candidates"]}
    require(len(former_unlinked) == 9 and len(visuals) == 7, "prior review queue drift")
    require(set(links) == former_unlinked | visuals, "unreviewed cross-page link ID or omitted case")
    require(set(RISK) == set(links), "missing mathematics or pedagogical boundary note")
    result = []
    for r in b52["rows"]:
        require(r["source_page_pdfkit_text_sha256"] ==
                pages[r["printed_page"]]["pdfkit_text_sha256"], "unverifiable source page")
        require(r["source_pdf_sha256"] == pdf_sha and
                r["official_atom_certified"] is False and
                r["teacher_review"] == "REVIEW_PENDING" and
                r["student_publishable"] is False, "unauthorized syllabus or student approval")
        result.append({
            "source_candidate_id":r["candidate_id"],"source_page":r["printed_page"],
            "track":r["track"],"source_modality":"PDFKIT_TEXT_FINGERPRINT",
            "source_page_sha256":r["source_page_pdfkit_text_sha256"],
            "goal_original_paraphrase":r["original_editorial_paraphrase"],
            "related_same_page":r["related_editorial_ids_not_equivalence"],
            "related_cross_page":list(links.get(r["candidate_id"],())),
            "review_boundary_note":RISK.get(r["candidate_id"], "同页主题相关不代表逻辑等价或满足学业要求。"),
        })
    for r in visual["candidates"]:
        require(r["teacher_review"] == "REVIEW_PENDING" and
                r["student_published"] is False and
                r["mathematical_formal_certification"] is False,
                "visual requirement falsely approved")
        result.append({
            "source_candidate_id":r["id"],"source_page":35,"track":"COMPULSORY",
            "source_modality":"VISUAL_IMAGE_SHA_NOT_PDFKIT_TEXT",
            "source_page_sha256":visual["mac_rendered_page_png_sha256"],
            "goal_original_paraphrase":r["goal"],
            "related_same_page":[],"related_cross_page":list(links[r["id"]]),
            "review_boundary_note":RISK[r["id"]],
        })
    require(len(result) == len({x["source_candidate_id"] for x in result}) == 35,
            "duplicate or missing requirement candidates")
    require(Counter(x["source_page"] for x in result) ==
            {34:8,35:7,41:8,50:5,65:7}, "source candidates silently omitted")
    cross_page_count = 0
    for r in result:
        related = r["related_same_page"] + r["related_cross_page"]
        require(len(related) == len(set(related)), "duplicate topic links")
        require(related, "review candidate without any topic lead")
        require(len(r["review_boundary_note"]) >= 16, "missing condition boundary")
        for eid in related:
            require(eid in editor, "orphan editorial association")
            target = editor[eid]
            require(target["track"] == r["track"], "cross-track linkage contamination")
            expected_same = eid in r["related_same_page"]
            require((target["printed_page"] == r["source_page"]) == expected_same,
                    "same-page/cross-page misclassification")
            require(not target["teacher_approved"] and
                    not target["student_published"] and
                    not target["math_certified"] and
                    not target["official_clause_verified"],
                    "unapproved lesson falsely certified")
            if not expected_same:
                cross_page_count += 1
        r.update({
            "related_only_not_coverage":True,
            "cross_page_deduplication":"POTENTIAL_OVERLAP_REVIEW_PENDING",
            "mathematical_equivalence":"NOT_ASSESSED",
            "official_atom_certified":False,
            "full_lesson_proven":False,"teacher_review":"REVIEW_PENDING",
            "student_publishable":False,"original_pdf_text_committed":False,
        })
    legacy = []
    for old in b51["legacy_non_equivalent_review_queue"]:
        eid = old["editorial_id"]
        require(eid in editor and editor[eid]["track"] == old["track"] and
                editor[eid]["printed_page"] == old["printed_page"],
                "legacy scope source mismatch")
        require(old["mathematical_equivalence"] == "NOT_CERTIFIED" and
                old["teacher_review"] == "REVIEW_PENDING" and
                old["student_access"] is False,
                "legacy lesson improperly promoted")
        legacy.append({
            "editorial_id":eid,"source_page":old["printed_page"],
            "track":old["track"],"original_goal":editor[eid]["goal"],
            "source_scope_class":old["source_scope_class"],
            "mathematical_equivalence":"NOT_CERTIFIED",
            "teacher_review":"REVIEW_PENDING","student_visible":False,
            "requires_independent_content_review":True,
        })
    return {
        "schema_version":"kb53-provisional-cross-page-source-links-v1",
        "status":"DISCOVERY_QUEUE_ONLY_UNVERIFIED",
        "source_pdf_sha256":pdf_sha,
        "source_page_fingerprints_present":61,
        "source_candidates":len(result),
        "previously_no_same_page_link":len(former_unlinked),
        "previously_no_same_page_now_cross_page_topic_lead":
            sum(bool(r["related_cross_page"]) for r in result
                if r["source_candidate_id"] in former_unlinked),
        "page35_visual_only_candidates":7,
        "cross_page_topic_links":cross_page_count,
        "source_rows":result,
        "legacy_non_equivalent_rows":legacy,
        "project_editorial_candidates":313,
        "official_atomic_denominator":{t:None for t in TRACKS},
        "teacher_approved":0,"student_published":0,
        "scope_equivalence_certified":0,
        "statement":"An association locates possible related course material but never proves mathematical or official curricular equivalence.",
    }

def render(data):
    out=["# Batch53｜35项来源要求跨页关联审计（不是正式去重或官方分母）","",
         "本批首次对 Batch52 28项（含原先同页无关联的9项）及 Batch51 第35页图像7项建立跨页主题线索。"
         "所有线索仅用于人工审查，不能当作完整讲义、课标覆盖、数学等价或教师批准。","",
         "| 检查指标 | 数量 |","|---|---:|",
         f"| 来源页指纹 | {data['source_page_fingerprints_present']} |",
         f"| 来源候选（28文字页 + 7图像页） | {data['source_candidates']} |",
         f"| 原先缺乏同页链接、此次有跨页主题线索 | {data['previously_no_same_page_now_cross_page_topic_lead']} |",
         f"| 跨页相关主题链接数（允许一项多个） | {data['cross_page_topic_links']} |",
         f"| 历史非等价旧稿待核 | {len(data['legacy_non_equivalent_rows'])} |",
         "| 课程官方知识原子分母（七轨） | null |",
         "| 正式教师审核/学生深度发布 | 0 / 0 |","",
         "## 全部35项待审核跨页线索与数学边界",""]
    for r in data["source_rows"]:
        out.append(f"- **{r['source_candidate_id']}**（第{r['source_page']}页，{r['source_modality']}）"
                   f"：{r['goal_original_paraphrase']}；跨页主题："
                   f"{', '.join(r['related_cross_page']) or '无'}；同页主题："
                   f"{', '.join(r['related_same_page']) or '无'}。"
                   f"待核边界：{r['review_boundary_note']}")
    out += ["","## 12项历史关联的独立复核队列",""]
    for r in data["legacy_non_equivalent_rows"]:
        out.append(f"- {r['editorial_id']}（{r['track']}/第{r['source_page']}页/{r['source_scope_class']}）"
                   f"：{r['original_goal']}；尚未认证数学等价。")
    out += ["","## 仍然阻断","",
            "关联与重叠推测不减少官方原子数，也不增加官方覆盖率；来源原件仍需逐页（包括图表）"
            "做教研完整复核。538项未认证证明步骤和10组冲突独立处理。此批没有新教师批准或学生发布。",
            "下批按各页学习要求独立拆分、检查缺失原子和边界，推进12项历史旧稿逐步数学复核。",""]
    return "\n".join(out)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    data=assemble()
    payload=json.dumps(data,indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    md=render(data)
    if args.check:
        require(DEST.read_text(encoding="utf-8")==payload, "source review queue JSON drift")
        require(MARKDOWN.read_text(encoding="utf-8")==md, "source review queue report drift")
    else:
        DEST.write_text(payload,encoding="utf-8")
        MARKDOWN.write_text(md,encoding="utf-8")
    print(f"Batch53: {data['source_candidates']} candidate rows; "
          f"{data['previously_no_same_page_now_cross_page_topic_lead']} cross-page recovered; "
          f"{data['cross_page_topic_links']} links; {len(data['legacy_non_equivalent_rows'])} legacy pending; check={args.check}")

if __name__=="__main__":
    main()
