#!/usr/bin/env python3
"""Batch58 K00 independent competencies/activities audit; never count these as atoms.

This uses authored source paraphrases, not reproduced textbook/standard passages.
Source PDF SHA and page/span attestation are inherited from checked Batch56/57.
A candidate course link is *not* a completed assessment or mathematical equivalence.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "docs/evaluation"
SOURCE_PATHS = (
    EVAL / "KB_BATCH56_COMPULSORY_SOURCE_SPAN_REVIEW.json",
    EVAL / "KB_BATCH57_SOURCE_SPAN_REVIEW.json",
)
OUT_JSON = EVAL / "KB_BATCH58_COMPETENCY_COVERAGE.json"
OUT_MD = EVAL / "KB_BATCH58_COMPETENCY_COVERAGE.md"
OUT_DRAFT_MD = EVAL / "KB_BATCH58_ASSESSMENT_REVIEW_MANUSCRIPTS.md"
DRAFTS = ROOT / "curriculum/highschool_math/kb_batch58_competency_assessment_drafts.json"
CATEGORIES = ("ACHIEVEMENT_REQUIREMENT", "TEACHING_GUIDANCE", "ACTIVITY_REQUIREMENT")
SOURCE_SHA = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A", "ELECTIVE_B",
          "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")


def require(condition: bool, reason: str):
    if not condition:
        raise ValueError(reason)


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf8"))


def build(*, source56=None, source57=None, drafts=None):
    s56 = deepcopy(source56 if source56 is not None else read(SOURCE_PATHS[0]))
    s57 = deepcopy(source57 if source57 is not None else read(SOURCE_PATHS[1]))
    drafts = deepcopy(drafts if drafts is not None else read(DRAFTS))
    require(s56["pinned_original_pdf_sha256"] == s57["official_pdf_sha256"] == SOURCE_SHA,
            "source-PDF integrity mismatch")
    require(len(s56["rows"]) == s56["candidate_source_spans"] == 52,
            "Batch56 source inventory drift")
    require(len(s57["rows"]) == s57["new_source_spans"] == 78,
            "Batch57 source inventory drift")
    require(s56["teacher_approved"] == s57["teacher_approved"] == 0 and
            s56["student_published"] == s57["student_published"] == 0,
            "unauthorized approval / publication")
    for source in (s56, s57):
        require(set(source["official_atomic_denominator"]) == set(TRACKS)
                and all(x is None for x in source["official_atomic_denominator"].values()),
                "official atomic denominator cannot be fabricated")
    rows = []
    allids = set()
    for batch, source in ((56, s56), (57, s57)):
        for row in source["rows"]:
            cid = row["candidate_id"]
            require(cid not in allids and re.fullmatch(r"KB5[67]-C-P\d{3}-S\d{3}", cid),
                    "duplicate / forged source candidate")
            allids.add(cid)
            require(row["source_pdf_sha256"] == SOURCE_SHA
                    and row["pdf_page_index"] == row["printed_page"] + 7
                    and re.fullmatch("[a-f0-9]{64}", row["source_page_pdfkit_sha256"])
                    and re.fullmatch("[a-f0-9]{64}", row["source_span_pdfkit_sha256"]),
                    "invalid PDF source pointer")
            require(row["teacher_review"] == "REVIEW_PENDING"
                    and row["student_publishable"] is False
                    and row["official_atom_certified"] is False,
                    "source may not be promoted to approved/published/official atom")
            if row["source_kind"] not in CATEGORIES:
                continue
            require(not row["starred_optional"], "optional material misclassified as mandatory competency")
            require(len(row["original_editorial_paraphrase"]) >= 19,
                    "source competency paraphrase missing")
            require(row["mathematical_or_policy_guard"], "missing scope guard")
            related = (row["related_same_page_editorial_ids_not_equivalence"] if batch == 56
                       else row["same_page_related_editorial_ids_not_equivalence"])
            require(isinstance(related, list) and len(related) == len(set(related)),
                    "duplicate/invalid related editorial IDs")
            require(all(re.fullmatch(r"KB\d+-C-P\d{3}-A\d{3}", i) for i in related),
                    "forged editorial crosswalk")
            require(not row.get("related_lesson_math_equivalence_certified", False)
                    and not row.get("mathematical_scope_equivalence_certified", False),
                    "thematic match must not be certified")
            rows.append({
                "competency_review_id": "KB58-" + cid,
                "source_candidate_id": cid,
                "source_batch": batch,
                "source_kind": row["source_kind"],
                "curriculum_track": "COMPULSORY",
                "printed_page": row["printed_page"],
                "source_span_id": row["source_span_id"],
                "pdf_sha256": SOURCE_SHA,
                "source_page_pdfkit_sha256": row["source_page_pdfkit_sha256"],
                "source_span_pdfkit_sha256": row["source_span_pdfkit_sha256"],
                "original_scope_paraphrase": row["original_editorial_paraphrase"],
                "condition_or_policy_guard": row["mathematical_or_policy_guard"],
                "related_editorial_ids_only_for_discovery": related,
                "mathematical_equivalence": "NOT_CERTIFIED",
                "assessment_artifact_ids": [],
                "rubric_evidence_ids": [],
                "student_activity_ids": [],
                "assessment_coverage": "UNMAPPED",
                "review": "REVIEW_PENDING",
                "teacher_approved": False,
                "student_publishable": False,
                "official_atom": False,
            })
    rows.sort(key=lambda r: (r["printed_page"], r["source_candidate_id"]))
    require(len(rows) == 28, "competency/teaching/activity source inventory drift")
    counts = dict(sorted(Counter(r["source_kind"] for r in rows).items()))
    require(counts == {"ACHIEVEMENT_REQUIREMENT": 11, "ACTIVITY_REQUIREMENT": 3,
                       "TEACHING_GUIDANCE": 14}, "requirement category drift")
    require(all(x["curriculum_track"] == "COMPULSORY" for x in rows),
            "course scope change requires source review")
    # Draft assessment plans are original teacher-only proposals. They DO NOT
    # count as validated assessment evidence, human approval, or atom coverage.
    require(drafts.get("schema_version") == "kb58-teacher-only-assessment-proposals-v1",
            "assessment schema changed")
    proposals = drafts.get("items")
    require(isinstance(proposals, list) and len(proposals) == 14,
            "assessment proposal inventory must contain 14 source-linked drafts")
    required_sources = {r["source_candidate_id"] for r in rows
                        if r["source_kind"] in ("ACHIEVEMENT_REQUIREMENT", "ACTIVITY_REQUIREMENT")}
    proposal_map = {}
    for proposal in proposals:
        src = proposal["source_candidate_id"]
        require(src in required_sources and src not in proposal_map,
                "orphan/duplicated assessment proposal")
        require(re.fullmatch(r"KB58-ASSESS-\d{2}", proposal["draft_id"]) is not None,
                "invalid assessment proposal ID")
        require(proposal["kind"] == "ASSESSMENT_PROPOSAL"
                and proposal["review_status"] == "REVIEW_PENDING"
                and proposal["teacher_solution_visibility"] == "TEACHER_ONLY"
                and proposal["formal_general_proof_certified"] is False
                and proposal["student_published"] is False
                and proposal["math_verification_status"] ==
                "FINITE_WITNESS_ONLY_NOT_GENERAL_CERTIFICATION",
                "draft assessment promoted without human authorization")
        for field, min_chars in (("original_problem", 18), ("assumptions", 12),
                                  ("nonexample_or_boundary", 12),
                                  ("common_wrong_method", 10), ("repair_question", 9),
                                  ("near_transfer", 10), ("far_transfer", 12)):
            require(isinstance(proposal.get(field), str) and len(proposal[field]) >= min_chars,
                    "assessment field incomplete: " + field)
        for field, min_chars in (("worked_solution_steps", 12), ("hint_ladder", 6),
                                  ("scoring_rubric", 5)):
            content = proposal.get(field)
            require(isinstance(content, list) and len(content) >= 3
                    and all(isinstance(s, str) and len(s) >= min_chars for s in content),
                    "assessment explanation/rubric insufficient: " + field)
        proposal_map[src] = proposal["draft_id"]
    require(set(proposal_map) == required_sources
            and len(set(proposal_map.values())) == 14,
            "achievement/activity assessment drafts not source-complete")
    for row in rows:
        row["teacher_only_assessment_draft_ids_not_verified"] = (
            [proposal_map[row["source_candidate_id"]]]
            if row["source_candidate_id"] in proposal_map else [])
    return {
        "schema_version": "kb58-independent-competency-coverage-v1",
        "scope": "PARTIAL_SOURCE_SPANS_15_TO_36_NOT_OFFICIAL_COMPLETE_DENOMINATOR",
        "source_pdf_sha256": SOURCE_SHA,
        "source_span_count_inherited_not_unique_atoms": 130,
        "review_queue_items": len(rows),
        "counts_by_kind": counts,
        "related_editorial_link_candidates_not_verified": sum(
            len(r["related_editorial_ids_only_for_discovery"]) for r in rows),
        "teacher_only_draft_assessment_proposals": len(proposal_map),
        "source_requirements_with_draft_proposals_not_approved": len(proposal_map),
        "assessment_verified": 0,
        "assessment_unmapped": len(rows),
        "teacher_approved": 0,
        "student_published": 0,
        "official_atomic_denominator": dict.fromkeys(TRACKS),
        "not_included_as_knowledge_atoms": True,
        "note": "K00 content atoms and independent achievement/activity/pedagogy "
                "requirements need separate evidence and coverage denominators. "
                "This is a partial source audit, not completion of either denominator.",
        "rows": rows,
    }


def render(a: dict) -> str:
    lines = [
        "# Batch58｜学业要求、教学提示与探究活动独立覆盖队列", "",
        "本报告是项目原创来源释义审计；不收录或转载课标原文。"
        "证据仅定位至已锁定PDF的源页与PDFKit片段SHA。", "",
        f"原始PDF SHA256：\x60{SOURCE_SHA}\x60；Batch56/57共130条非去重来源记录，"
        f"其中{a['review_queue_items']}项是非知识原子的学业/教学/活动审查要求。", "",
        f"**本批新增{a['teacher_only_draft_assessment_proposals']}份教师待审原创学业/活动测评草案，"
        "但28项仍没有与已验收题族、量规或教学活动建立可认证映射；"
        "即使关联项目编辑目标或待审草案，也不能判定为已覆盖。**",
        "七轨官方知识原子完整分母仍为null；没有真实教师批准/学生正式发布。", "",
        "| 类别 | 独立审查条数 | 有效评测证据 | 待补齐 |",
        "|---|---:|---:|---:|",
    ]
    for k, n in a["counts_by_kind"].items():
        lines.append(f"| {k} | {n} | 0 | {n} |")
    lines += ["", "## 逐项待审追踪", "",
              "| 来源ID / 课程页 | 来源要求的项目原创释义 | 现有关联 | 验收缺口 |",
              "|---|---|---|---|"]
    for r in a["rows"]:
        safe = r["original_scope_paraphrase"].replace("|", "／").replace("\n", " ")
        lines.append(f"| \x60{r['source_candidate_id']}\x60 / P{r['printed_page']} | "
                     f"{safe} | {len(r['related_editorial_ids_only_for_discovery'])}个主题线索"
                     f"（未证等价） | 无独立题族/量规/活动验收证据 |")
    lines += ["", "## 下一批必要条件", "",
              "1. 逐项定义可观察的学业表现、题目与评分量规，将证据ID和所需先修知识联系起来。",
              "2. 区分知识原子、学业目标、教学建议、建模活动与选学范围；对选修A–E分别审查。",
              "3. 独立教师审查来源语义、题族对齐及数学证明，之后方能从UNMAPPED升级。",
              "4. 第35页图示需查看原PDF，不得依靠乱码或主题推断设为已完成。",
              "5. 继续覆盖37–73页及未审页，完成跨页去重后才能确定正式分母。", ""]
    return "\n".join(lines)


def render_assessment_manuscripts(a: dict, drafts: dict) -> str:
    """Teacher-only original activity plans; never used as student prompt payload."""
    source = {r["source_candidate_id"]: r for r in a["rows"]}
    lines = [
        "# Batch58｜14份学业表现与综合活动测评草案（教师侧）", "",
        "**REVIEW_PENDING · TEACHER_ONLY · NOT_FORMALLY_CERTIFIED**。"
        "下列题目、示例解答与评分建议仅供独立教研评审，不接入学生挑战模式。",
        "有限实例计算与形式证明、真实教师验收是不同的门槛；所有内容均为原创。",
        "源课标仅引用Batch56/57锁定的PDFKit页码与SHA，不复制原文。", "",
    ]
    for item in drafts["items"]:
        src = source[item["source_candidate_id"]]
        lines += [f"## {item['draft_id']}｜{item['source_candidate_id']}（P{src['printed_page']}）", "",
                  "**课程范围与前提：**" + item["assumptions"], "",
                  "**教学任务：**" + item["original_problem"], "",
                  "**教师侧解题或论证步骤（不面向学生直接展示）：**", ""]
        for i, step in enumerate(item["worked_solution_steps"], 1):
            lines.append(f"{i}. {step}")
        lines += ["", "**不适用情形/反例：**" + item["nonexample_or_boundary"],
                  "**典型错法：**" + item["common_wrong_method"],
                  "**修复追问：**" + item["repair_question"], "",
                  "**三级启发式提示（分级访问）：**"]
        for i, hint in enumerate(item["hint_ladder"], 1):
            lines.append(f"{i}. {hint}")
        lines += ["", "**近迁移：**" + item["near_transfer"],
                  "**远迁移：**" + item["far_transfer"], "",
                  "**评分量规草案：**"]
        for i, rubric in enumerate(item["scoring_rubric"], 1):
            lines.append(f"{i}. {rubric}")
        lines += ["", "**审核状态：**REVIEW_PENDING／TEACHER_ONLY；"
                  "有限实例见证不等于普适数学证明或教学效果验证。", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    audit = build()
    expected = json.dumps(audit, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    report = render(audit)
    manuscript = render_assessment_manuscripts(audit, read(DRAFTS))
    if args.check:
        require(OUT_JSON.read_text(encoding="utf8") == expected, "JSON audit drift")
        require(OUT_MD.read_text(encoding="utf8") == report, "Markdown audit drift")
        require(OUT_DRAFT_MD.read_text(encoding="utf8") == manuscript,
                "teacher manuscript drift")
    else:
        OUT_JSON.write_text(expected, encoding="utf8")
        OUT_MD.write_text(report, encoding="utf8")
        OUT_DRAFT_MD.write_text(manuscript, encoding="utf8")
    print(f"Batch58 K00: {audit['review_queue_items']} independent requirements; "
          f"{audit['assessment_verified']} verified; {audit['assessment_unmapped']} unmapped")


if __name__ == "__main__":
    main()
