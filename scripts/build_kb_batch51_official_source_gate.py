#!/usr/bin/env python3
"""K00/K01: source-evidence coverage is not curriculum-atom coverage.

No licensed text is embedded. Both extractor marker occurrences and topic
headings are source *candidates*, never the official atomic denominator.
The optional macOS PDFKit scan was run against the SHA-pinned local original.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURR = ROOT / "curriculum/highschool_math"
EVAL = ROOT / "docs/evaluation"
SOURCE = CURR / "official_pypdf59_reextract_batch26.json"
DE = CURR / "official_unnumbered_de_outline_batch18.json"
PDFKIT = CURR / "k00_batch51_pdfkit_page_fingerprints.json"
EDITOR = EVAL / "KB_BATCH50_PROJECT_SCOPE_OVERLAY.json"
CLAUSES = CURR / "k00_batch40_twelve_clause_adjudications.json"
SPLIT35 = CURR / "k00_batch51_page35_modelling_candidate_split.json"
OUT = EVAL / "KB_BATCH51_OFFICIAL_SOURCE_PAGE_GATE.json"
MD = EVAL / "KB_BATCH51_UNNUMBERED_AND_LEGACY_REVIEW.md"
PDF_SHA = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
PAGE35_PNG_SHA = "bfcf80effdcf8289eb4eb1bc006bdad55476d0872a14c43a5ebff1232548b435"
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A", "ELECTIVE_B",
          "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")

# Mac PDFKit inspection of page opening passages on 2026-11-09.
# These are *triage labels*, NOT a complete read or teacher certification.
NO_MARKER_TRIAGE = {
    13: "COURSE_STRUCTURE",
    14: "COURSE_HOURS_TABLE",
    18: "TEACHING_GUIDANCE_WITH_CONTENT",
    24: "TEACHING_GUIDANCE_WITH_CONTENT",
    30: "GEOMETRY_TEACHING_GUIDANCE_WITH_CONTENT",
    34: "ACHIEVEMENT_REQUIREMENTS",
    35: "PDFKIT_TEXT_CORRUPTION_VISUAL_REVIEW_REQUIRED",
    36: "MODELLING_ACTIVITY_GUIDANCE",
    37: "SELECTIVE_STRUCTURE_TABLE",
    41: "ACHIEVEMENT_REQUIREMENTS",
    45: "GEOMETRY_TEACHING_GUIDANCE",
    49: "PROBABILITY_TEACHING_GUIDANCE",
    50: "MODELLING_CONTENT_REQUIREMENTS",
    51: "ELECTIVE_TRACK_SELECTION_RULES",
    65: "ALTERNATE_ARABIC_NUMBERING_MISSED_BY_MARKER_EXTRACTOR",
}
CRITICAL = {34, 35, 41, 50, 65}

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def sha256(text: bytes) -> str:
    return hashlib.sha256(text).hexdigest()

def index_unique(rows, key, name):
    result = {}
    for r in rows:
        require(r.get(key) not in result, f"duplicate {name}: {r.get(key)}")
        result[r[key]] = r
    return result

def assemble(source=None, de=None, pdfkit=None, editor=None, clauses=None, split35=None):
    source = source if source is not None else load(SOURCE)
    de = de if de is not None else load(DE)
    pdfkit = pdfkit if pdfkit is not None else load(PDFKIT)
    editor = editor if editor is not None else load(EDITOR)
    clauses = clauses if clauses is not None else load(CLAUSES)
    split35 = split35 if split35 is not None else load(SPLIT35)
    for label, found in (
        ("pypdf source", source["source"]["sha256"]),
        ("D/E source", de["source_pdf_sha256"]),
        ("PDFKit source", pdfkit["official_pdf_sha256"]),
        ("legacy clause source", clauses["source"]["sha256"]),
        ("visually inspected page 35", split35["source_pdf_sha256"]),
    ):
        require(found == PDF_SHA, f"source drift in {label}")
    require(source["denominator_contract"]["official_atomic_knowledge_denominator"] is None,
            "uncertified official denominator in source")
    require(editor["summary"]["official_atom_denominator"] is None,
            "editorial denominator masquerades as official")
    require(len(source["pages"]) == len(pdfkit["pages"]) == 61,
            "partial PDF source page scan")
    require(pdfkit["pdf_total_pages"] == source["source"]["pdf_total_pages"] == 188,
            "source page count drift")
    require(de["summary"]["fully_complete"] is False,
            "D/E outlines cannot be flagged complete")
    require(de["summary"]["teacher_verified_knowledge_atoms"] == 0,
            "D/E outline falsely teacher certified")
    require(set(editor["tracks"]) == set(TRACKS),
            "missing or unknown curriculum track")
    sp = index_unique(source["pages"], "printed_page", "pypdf source page")
    pp = index_unique(pdfkit["pages"], "printed_page", "PDFKit source page")
    require(set(sp) == set(pp) == set(range(13, 74)),
            "source pages must be every printed content page 13..73")
    for page in range(13, 74):
        require(sp[page]["pdf_page_index"] == pp[page]["pdf_page_index"] == page+7,
                f"bad original source PDF page mapping: {page}")
        require(len(pp[page]["pdfkit_text_sha256"]) == 64
                and pp[page]["unicode_scalar_count"] > 0,
                f"source page missing text or fingerprint: {page}")
        require(pp[page]["full_page_human_review"] == "PENDING",
                "PDFKit extraction cannot certify full-page human review")
    numbered = index_unique(source["enumerated_source_anchors"], "id", "numbered source marker")
    de_topics = index_unique(de["items"], "id", "D/E source topic")
    candidates = index_unique(editor["rows"], "editorial_id", "editorial candidate")
    clause_index = index_unique(clauses["entries"], "editorial_candidate_id", "legacy adjudication")
    require(len(numbered) == 317 and len(de_topics) == 23, "source enumeration unexpectedly drifted")
    require(len(candidates) == 313, "editorial candidate set unexpectedly drifted")
    require(len(clause_index) == 12, "12-legacy-source adjudication incomplete")
    require(split35["source_printed_page"] == 35 and split35["pdf_page_index"] == 42,
            "page35 visual review provenance mismatch")
    require(split35["rendered_source_image_committed"] is False
            and split35["source_passages_committed"] is False,
            "copyright original image or source passages must not be committed")
    require(split35["mac_rendered_page_png_sha256"] == PAGE35_PNG_SHA,
            "page35 original-image fingerprint drift")
    require(split35["official_atom_denominator"] is None
            and split35["teacher_review"] == "REVIEW_PENDING", "page35 falsely certified")
    new35 = index_unique(split35["candidates"], "id", "provisional page35 split")
    require(len(new35)==7 and not (set(new35)&set(candidates)), "page35 split IDs drift or collide")
    require(all(x["teacher_review"] == "REVIEW_PENDING"
                and x["cross_page_deduplication"] == "PENDING"
                and not x["full_lesson_available"] and not x["student_published"]
                and not x["mathematical_formal_certification"] for x in new35.values()),
            "provisional modelling requirements promoted without review")
    require(all(a["track"] in TRACKS and a["printed_page"] in sp for a in numbered.values()),
            "marker outside source or track")
    require(all(a["track"] in TRACKS and a["printed_page"] in sp for a in de_topics.values()),
            "D/E topic outside source or track")
    require(all(a["track"] in TRACKS and a["printed_page"] in sp for a in candidates.values()),
            "editorial candidate outside original source")
    require(all(a["teacher_review"] == "PENDING" and not a["approved_lesson_ids"]
                for a in numbered.values()), "source marker falsely approved")
    require(all(a["teacher_review"] == "PENDING" and not a["student_available"]
                for a in de_topics.values()), "outline falsely approved")
    require(all(not x["teacher_approved"] and not x["student_published"]
                and not x["math_certified"] and not x["official_clause_verified"]
                for x in candidates.values()), "unverified curriculum association falsely certified")
    require(all(not a["official_atomic_equivalence_certified"]
                and not a["legacy_lesson_certified"]
                and not a["student_publishable"]
                and a["teacher_review"] == "REVIEW_PENDING"
                for a in clause_index.values()), "legacy equivalence or publication falsely certified")
    legacy = {x["editorial_id"]:x for x in candidates.values() if not x["direct_review_drafts"]}
    require(set(legacy) == set(clause_index), "legacy-only links not fully adjudicated")
    require(all(x["legacy_associations_unverified"] for x in legacy.values()),
            "legacy-only link without traceable old association")
    counts_n = Counter((a["printed_page"],a["track"]) for a in numbered.values())
    counts_d = Counter((a["printed_page"],a["track"]) for a in de_topics.values())
    counts_e = Counter((a["printed_page"],a["track"]) for a in candidates.values())
    require(all(sum(n for (p,t),n in counts_n.items() if p==page)
                == sp[page]["source_numbered_marker_count"] for page in sp),
            "source page numbered ledger count mismatch")
    bytrack = Counter(a["track"] for a in numbered.values())
    require(dict(bytrack) == {t:n for t,n in source["denominator_contract"]
                            ["by_track_source_numbered_candidates"].items() if n},
            "numbered markers by track drifted")
    result_pages = []
    for page in range(13,74):
        tracks = sorted(set(t for p,t in (*counts_n.keys(),*counts_d.keys(),*counts_e.keys()) if p == page))
        n = sum(v for (p,t),v in counts_n.items() if p==page)
        d = sum(v for (p,t),v in counts_d.items() if p==page)
        e = sum(v for (p,t),v in counts_e.items() if p==page)
        no_anchor = n+d == 0
        # A same-page reference is only a navigational candidate, never semantic coverage.
        result_pages.append({
            "printed_page":page, "pdf_page_index":page+7, "tracks":tracks,
            "pdfkit_page_text_sha256":pp[page]["pdfkit_text_sha256"],
            "pdfkit_unicode_scalars":pp[page]["unicode_scalar_count"],
            "pdfkit_control_scalars":pp[page]["control_scalar_count"],
            "numbered_marker_occurrences_not_atoms":n,
            "D_E_unnumbered_topic_outlines_not_atoms":d,
            "project_editorial_candidates_not_official_atoms":e,
            "possible_same_page_crosswalk_only":bool((n+d) and e),
            "source_anchor_gap":no_anchor,
            "triage_label":NO_MARKER_TRIAGE.get(page,"PENDING_FULL_PAGE_REVIEW"),
            "critical_manual_review":page in CRITICAL,
            "full_page_human_review":"PENDING", "teacher_verified_official_atoms":0,
            "official_atomic_denominator":None,
            "mathematical_semantic_equivalence":"NOT_ASSESSED",
        })
    require({r["printed_page"] for r in result_pages if r["source_anchor_gap"]}
            == set(NO_MARKER_TRIAGE), "the manually triaged gap pages changed")
    legacy_queue = []
    for cid, row in sorted(legacy.items()):
        a = clause_index[cid]
        require(a["printed_page"] == row["printed_page"] and a["track"] == row["track"],
                f"legacy source attribution inconsistent: {cid}")
        legacy_queue.append({
            "editorial_id":cid, "track":row["track"], "printed_page":row["printed_page"],
            "legacy_lesson_count":len(row["legacy_associations_unverified"]),
            "source_scope_class":a["source_scope_class"],
            "source_topic_review":"SOURCE_TOPIC_CHECKED_NO_ATOM_EQUIVALENCE",
            "mathematical_equivalence":"NOT_CERTIFIED",
            "teacher_review":"REVIEW_PENDING", "student_access":False,
            "blocking_action":"NEW_INDEPENDENT_MATH_SCOPE_AND_TEACHER_REVIEW",
        })
    result = {
        "schema_version":"kb-batch51-k00-official-source-coverage-gate-v1",
        "source_pdf_sha256":PDF_SHA,
        "source_pdf_not_committed":True,
        "page35_visual_evidence":{
            "rendered_original_local_png_sha256":split35["mac_rendered_page_png_sha256"],
            "original_image_committed":False,
            "image_read_outcome":"VISIBLE_MODELLING_AND_INQUIRY_ACTIVITY_NOT_EMPTY_PAGE",
            "new_project_authored_split_candidates":len(new35),
            "cross_page_deduplication":"PENDING",
            "teacher_review":"REVIEW_PENDING",
            "new_split_ids":sorted(new35),
        },
        "source_passages_not_committed":True,
        "status":"SOURCE_AUDIT_ONLY_OFFICIAL_ATOM_DENOMINATOR_UNRESOLVED",
        "source_page_denominator":61,
        "source_evidence_units_not_official_atoms":{
            "numbered_marker_occurrences":len(numbered),
            "D_E_unnumbered_topic_outlines":len(de_topics),
            "combined_heterogeneous_evidence_count":len(numbered)+len(de_topics),
            "warning":"Mixed source markers and headings do not define one-to-one knowledge atoms.",
        },
        "editorial_scope_not_official":{
            "project_candidates":len(candidates),
            "direct_pending_review":len(candidates)-len(legacy),
            "legacy_only_unverified":len(legacy),
            "teacher_approved":0,"student_published":0,
        },
        "review_gate":{
            "official_atomic_knowledge_denominator":None,
            "official_coverage_fraction":None,
            "human_full_page_reviews_completed":0,
            "formal_mathematical_equivalence_reviews_completed":0,
            "teacher_approved_lessons":0,"student_deep_content_published":0,
            "safety":"HARD_FAIL_CLOSED",
        },
        "track_evidence":[
            {"track":t,
             "numbered_marker_occurrences_not_atoms":sum(v for (p,tt),v in counts_n.items() if tt==t),
             "D_E_topics_not_atoms":sum(v for (p,tt),v in counts_d.items() if tt==t),
             "project_candidates_not_atoms":sum(v for (p,tt),v in counts_e.items() if tt==t),
             "official_atomic_denominator":None,"official_coverage_fraction":None,
             "teacher_approved":0}
            for t in TRACKS
        ],
        "pages":result_pages,
        "source_gap_pages":[p["printed_page"] for p in result_pages if p["source_anchor_gap"]],
        "high_priority_gap_pages":sorted(CRITICAL),
        "legacy_non_equivalent_review_queue":legacy_queue,
        "next_actions":[
            "Visually reread source page 35: text extraction is corrupted.",
            "Decompose numbered and unnumbered student outcome sentences per theme, including pages 34, 41, 50, 65.",
            "Inspect the entire source's 61 printed pages, not only marker occurrences.",
            "Review 12 legacy-only associations with mathematical hypotheses and teachers.",
            "Only after independent source audit and review freeze official seven-track atomic denominators.",
        ],
    }
    return result

def markdown(data):
    pages = data["pages"]; legacy = data["legacy_non_equivalent_review_queue"]
    rows = [
        "# Batch51｜K00 原始课标证据页覆盖与 12 条非等价旧稿关联",
        "",
        "## 证据与严格边界",
        "",
        f"- 原件 SHA256：\x60{PDF_SHA}\x60；Mac 上对原始 PDF 的 61 个课程内容印刷页进行了 PDFKit 逐页提取和 SHA 指纹校验，原文未入库。",
        "- 来源存在 317 个编号标记**出现次数**及 D/E 23 个未编号主题提纲，**340 不是官方原子数，也不是完整课程目标数**。",
        "- 自编 313 个编辑候选（301 份直接待审、12 条仅历史关联）也**不是**正式课程分母；七轨道的官方原子分母和正式覆盖率继续为 null。",
        "- 逐页文本指纹仅证明读取了锁定 PDF 的页面，不证明教研已逐页审查；完整教师批准 0，学生端正式发布 0。",
        "",
        "## 15 个编号抽取器盲区页（按原件起始内容初筛）",
        "",
        "| 印刷页 | 现有编号出现 | D/E主题 | 项目候选 | 初筛性质（不代表正式审查） |",
        "|---:|---:|---:|---:|---|",
    ]
    for p in pages:
        if not p["source_anchor_gap"]: continue
        rows.append(f"| {p['printed_page']} | 0 | 0 | {p['project_editorial_candidates_not_official_atoms']} | {p['triage_label']} |")
    rows += ["", "其中 34、41、50 页包含对学习或内容的要求而无原编号标记；65 页存在不同于旧提取正则的阿拉伯式章节编号。35 页 PDFKit 字符流损坏，但在 Mac 上通过原件页面渲染已**确实看到数学建模循环图、探究活动和必修课题研究要求**；该观察不等于教师逐条审核。", "",
             "## 第 35 页新发现的 7 条原子化编辑候选（全部非官方认证）", "",
             "原件图像只在 Mac 临时目录读取，未提交版权页面；图像 SHA256 与 7 条原创改写见 `curriculum/highschool_math/k00_batch51_page35_modelling_candidate_split.json`。候选包括问题数学化、假设与变量、模型求解、现实检验与修订、计算正确性与现实适切性、探究猜想与证据、完整课题研究。它们仍须与 34–36 页去重、逐条教师审核，**不加入已核准官方原子分母，不算完整新讲义**。", "",
             "## 12 条历史旧稿关联：只能做待审来源定位",
             "", "| 编辑候选 | 轨道 | 印刷页 | 课标来源核查类别 | 教师/数学等价 |",
             "|---|---|---:|---|---|"]
    for q in legacy:
        rows.append(f"| {q['editorial_id']} | {q['track']} | {q['printed_page']} | {q['source_scope_class']} | REVIEW_PENDING / NOT_CERTIFIED |")
    rows += ["", "## 下一批处理顺序", "",
             "1. 结合原件图像对 35 页重读；复查 34/41/50/65 页未编号内容，抽取语义完整的原创教学目标草案并保留行/页锚。",
             "2. 扩展到 61 页的每条编号要求、未编号要求、学业要求及探究任务，标注主题/领域/可选性/年份/课程轨道；教师独立核对后冻结每轨原子分母。",
             "3. 将 12 条历史关联分别替换为独立数学范围核查，证明类逐步审查前提与结论、反例和越界条件，不得借相同页码判定数学等价。",
             "4. 课程未获教师签字前，始终禁用未批准内容的正式学生 RAG 和挑战答案输出。", ""]
    return "\n".join(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    d=assemble()
    outputs={OUT:json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
             MD:markdown(d)}
    for path,expected in outputs.items():
        if args.check:
            require(path.exists() and path.read_text(encoding="utf-8")==expected,
                    f"stale source audit: {path}")
        else:
            path.write_text(expected,encoding="utf-8")
    print("K00 Batch51 source evidence:",len(d["pages"]),"pages;",
          d["source_evidence_units_not_official_atoms"]["numbered_marker_occurrences"],
          "marker occurrences; 23 D/E outlines; 15 blind-spot pages; 12 legacy blocks;",
          "official atom denominators: null")

if __name__ == "__main__":
    main()
