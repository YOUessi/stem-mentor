#!/usr/bin/env python3
"""Batch74 editorial disposition of every unanchored Batch73 source span.

Never upgrades editorial classification to official syllabus atom or a
teacher-signed review; original PDF text stays on the authorized Mac.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import build_kb_batch73_page_partition as B73

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/evaluation/KB_BATCH73_PAGE_PARTITION_COVERAGE.json"
OUTPUT = ROOT / "docs/evaluation/KB_BATCH74_UNMARKED_REVIEW.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH74_UNMARKED_REVIEW.md"
PDF_SHA = B73.B61.PDF_SHA
CLASSES = {
    "PAGE_FURNITURE", "CROSS_PAGE_CONTINUATION", "CURRICULUM_OR_TRACK_OVERVIEW",
    "PEDAGOGICAL_GUIDANCE", "SUBSTANTIVE_UNNUMBERED", "MIXED_REQUIRES_SPLIT",
    "GRAPHIC_VISUAL_INSPECTED_PENDING_TEACHER", "SCHOOL_DEFINED_ELECTIVE"
}
# These are project-authored editorial notes based on inspecting pinned Mac PDFKit
# spans. No quotations from the source and no copyright-source text is emitted.
# Labels are provisional; they never constitute official denominator or teacher approval.
TRIAGE = {
"013-001":"MIXED_REQUIRES_SPLIT|必修总论与课时表并存；分清课程结构和知识要求",
"014-001":"MIXED_REQUIRES_SPLIT|课时表续页与主题说明；核查表格跨页单元",
"016-001":"SUBSTANTIVE_UNNUMBERED|量词与充分必要条件主题范围承接上一页",
"017-001":"CROSS_PAGE_CONTINUATION|基本不等式优化要求跨页承接，核对完整先决条件",
"018-001":"PEDAGOGICAL_GUIDANCE|等式不等式与函数教学组织建议",
"019-001":"CROSS_PAGE_CONTINUATION|函数主题导言跨页承接",
"020-001":"PAGE_FURNITURE|单独页眉，不可单独计课程原子",
"021-001":"CROSS_PAGE_CONTINUATION|对数函数性质要求跨页接续",
"022-001":"PAGE_FURNITURE|单独页眉",
"023-001":"CROSS_PAGE_CONTINUATION|二分法近似求根要求跨页接续",
"024-001":"PEDAGOGICAL_GUIDANCE|对数与三角函数的教学方式和工具建议",
"025-001":"MIXED_REQUIRES_SPLIT|函数模块学业要求结尾与几何代数导言同段",
"026-001":"PAGE_FURNITURE|单独页眉",
"027-001":"SUBSTANTIVE_UNNUMBERED|复数表示运算范围及带星号三角表示需分层",
"028-001":"PAGE_FURNITURE|单独页眉",
"029-001":"MIXED_REQUIRES_SPLIT|四项立体几何判定定理与教学建议同段，必须原子化",
"030-001":"PEDAGOGICAL_GUIDANCE|立体几何的教学观察与证明建议",
"031-001":"CROSS_PAGE_CONTINUATION|概率统计主题导言接续",
"032-001":"SUBSTANTIVE_UNNUMBERED|抽样与统计表征的内容范围承接",
"034-001":"PAGE_FURNITURE|单独页眉",
"035-001":"GRAPHIC_VISUAL_INSPECTED_PENDING_TEACHER|已查验原PDF第35页流程图，提取文本损坏仍需教师审核语义",
"036-001":"PEDAGOGICAL_GUIDANCE|建模结题与信息技术应用建议",
"037-001":"MIXED_REQUIRES_SPLIT|选必课时续表与函数导言连续，需分条",
"038-001":"PAGE_FURNITURE|单独页眉",
"040-001":"PAGE_FURNITURE|单独页眉",
"041-001":"CROSS_PAGE_CONTINUATION|数学文化与微积分发展活动跨页接续",
"042-001":"PAGE_FURNITURE|单独页眉",
"043-001":"CROSS_PAGE_CONTINUATION|空间向量中法向量的要求跨页承接",
"044-001":"CROSS_PAGE_CONTINUATION|平行直线距离要求跨页承接",
"045-001":"PEDAGOGICAL_GUIDANCE|向量几何和圆锥曲线课程教学建议",
"046-001":"MIXED_REQUIRES_SPLIT|解析几何能力要求结束并开始概率统计主题",
"048-001":"CROSS_PAGE_CONTINUATION|正态分布认识目标跨页接续",
"049-001":"PEDAGOGICAL_GUIDANCE|独立性、分布、统计和回归的教学建议",
"050-001":"MIXED_REQUIRES_SPLIT|概率统计素养结尾与建模探究主题开头",
"051-001":"CURRICULUM_OR_TRACK_OVERVIEW|A-E类定位及学习人群，属于选修总论",
"051-020":"MIXED_REQUIRES_SPLIT|选修A专题与微积分导言需拆分",
"052-001":"SUBSTANTIVE_UNNUMBERED|选修A极限、连续、积分专题范围承接",
"054-001":"PAGE_FURNITURE|单独页眉",
"056-001":"SUBSTANTIVE_UNNUMBERED|选修A连续分布、联合分布与统计推断范围",
"057-016":"MIXED_REQUIRES_SPLIT|选修B专题课时与微积分导言",
"058-001":"SUBSTANTIVE_UNNUMBERED|选修B含二元函数与偏导的课程范围",
"060-001":"SUBSTANTIVE_UNNUMBERED|三阶矩阵、行列式与三元线性方程组范围",
"061-001":"SUBSTANTIVE_UNNUMBERED|选修B应用统计范围与模型假设",
"062-001":"CROSS_PAGE_CONTINUATION|选修B随机变量内容跨页接续",
"063-001":"SUBSTANTIVE_UNNUMBERED|选修B五类实际数学模型清单",
"064-001":"PAGE_FURNITURE|单独页眉",
"064-010":"MIXED_REQUIRES_SPLIT|选修C逻辑推理专题简介与课时",
"065-001":"CROSS_PAGE_CONTINUATION|选修C逻辑条件辨别要求接续",
"066-001":"SUBSTANTIVE_UNNUMBERED|选修C社会经济模型的范围",
"067-001":"CROSS_PAGE_CONTINUATION|选修C社会调查样本估计目标承接",
"068-001":"SUBSTANTIVE_UNNUMBERED|选修C社会调查与数据分析范围",
"069-006":"MIXED_REQUIRES_SPLIT|选修D美与数学专题及四项课程结构",
"070-001":"PAGE_FURNITURE|单独页眉",
"072-001":"PAGE_FURNITURE|单独页眉",
"073-001":"CROSS_PAGE_CONTINUATION|运动数学的测量/建模要求接续",
"073-013":"SCHOOL_DEFINED_ELECTIVE|选修E由学校开发或选用，不设全国固定原子分母"
}

PRIORITY = {
    "PAGE_FURNITURE": "LOW",
    "CROSS_PAGE_CONTINUATION": "MEDIUM",
    "CURRICULUM_OR_TRACK_OVERVIEW": "HIGH",
    "PEDAGOGICAL_GUIDANCE": "MEDIUM",
    "SUBSTANTIVE_UNNUMBERED": "HIGH",
    "MIXED_REQUIRES_SPLIT": "HIGH",
    "GRAPHIC_VISUAL_INSPECTED_PENDING_TEACHER": "HIGH",
    "SCHOOL_DEFINED_ELECTIVE": "BLOCKED_LOCAL_SCOPE",
}
NEXT = {
    "PAGE_FURNITURE": "EXCLUDE_FROM_ATOM_CANDIDATES_AFTER_PAGE_REVIEW",
    "CROSS_PAGE_CONTINUATION": "MERGE_WITH_NEIGHBORING_CONTEXT_BEFORE_ATOMIZATION",
    "CURRICULUM_OR_TRACK_OVERVIEW": "SEPARATE_TRACK_SCOPE_FROM_KNOWLEDGE",
    "PEDAGOGICAL_GUIDANCE": "MAP_TO_TEACHING_COMPETENCY_EVIDENCE",
    "SUBSTANTIVE_UNNUMBERED": "PROPOSE_ATOMS_FROM_COMPLETE_CONTEXT",
    "MIXED_REQUIRES_SPLIT": "SPLIT_TABLE_HEADING_AND_MATH_CLAUSE",
    "GRAPHIC_VISUAL_INSPECTED_PENDING_TEACHER": "TEACHER_REVIEW_OF_VISUAL_PROCESS",
    "SCHOOL_DEFINED_ELECTIVE": "REQUIRE_SCHOOL_OFFERING_LIST",
}


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def verify(records, source_audit):
    expected = {r["segment_id"] for r in source_audit["review_risks"]}
    assert len(expected) == 56 and len(records) == 56, "risk inventory cardinality drift"
    assert {x["segment_id"] for x in records} == expected, "missing/extra source segment"
    spans = {s["segment_id"]: s for s in source_audit["segments"]}
    for x in records:
        s = spans[x["segment_id"]]
        assert x["source_pdf_sha256"] == PDF_SHA
        assert x["span_sha256"] == B73.load(B73.WITNESS)["segments"][next(
            i for i,w in enumerate(B73.load(B73.WITNESS)["segments"])
            if w["segment_id"] == s["segment_id"])]["span_sha256"]
        assert x["track_hint"] == s["track_hint"]
        assert x["classification"] in CLASSES
        assert x["next_action"] == NEXT[x["classification"]]
        assert x["priority"] == PRIORITY[x["classification"]]
        assert x["review_status"] == "PROJECT_EDITORIAL_TRIAGE"
        assert x["teacher_review"] == "REVIEW_PENDING"
        assert x["mathematical_equivalence"] == "UNDETERMINED"
        assert x["official_atom_count"] is None
        assert x["student_publishable"] is False
        assert len(x["original_editorial_note"]) >= 4
        assert x["original_editorial_note"] == TRIAGE[x["segment_id"][6:9]+"-"+x["segment_id"][11:14]].split("|",1)[1]
    assert len({x["original_editorial_note"] for x in records}) >= 38


def build():
    audit = B73.load(AUDIT)
    witness = B73.load(B73.WITNESS)
    B73.validate_witness(witness)
    risks = audit["review_risks"]
    assert len(risks) == len(TRIAGE) == 56
    lookup = {s["segment_id"]: s for s in witness["segments"]}
    result = []
    for r in risks:
        sid = r["segment_id"]
        key = sid[6:9] + "-" + sid[11:14]
        assert key in TRIAGE, f"unreviewed {sid}"
        c,note = TRIAGE[key].split("|",1)
        s = lookup[sid]
        result.append(dict(
            segment_id=sid,
            printed_page=s["printed_page"],
            first_line=s["first_line"],
            last_line=s["last_line"],
            source_pdf_sha256=PDF_SHA,
            span_sha256=s["span_sha256"],
            track_hint=s["track_hint"],
            preceding_anchor_id=s["preceding_anchor_id"],
            classification=c,
            original_editorial_note=note,
            priority=PRIORITY[c],
            next_action=NEXT[c],
            review_status="PROJECT_EDITORIAL_TRIAGE",
            teacher_review="REVIEW_PENDING",
            mathematical_equivalence="UNDETERMINED",
            official_atom_count=None,
            student_publishable=False,
        ))
    verify(result,audit)
    counts = dict(sorted(Counter(x["classification"] for x in result).items()))
    priorities = dict(sorted(Counter(x["priority"] for x in result).items()))
    tracks = sorted(set(x["track_hint"] for x in result) | set(B73.TRACKS))
    track_backlog = {
        t: dict(editorial_segments=sum(x["track_hint"] == t for x in result),
                high_priority_unresolved=sum(x["track_hint"] == t and x["priority"] == "HIGH" for x in result),
                official_atom_denominator=None,
                confirmed_missing_atoms=None,
                teacher_approved=0)
        for t in tracks
    }
    payload = dict(
        schema_version="kb74-56-unanchored-editorial-v1",
        source_pdf_sha256=PDF_SHA,
        parent_witness_sha256=sha256(B73.WITNESS.read_bytes()).hexdigest(),
        parent_audit_sha256=sha256(AUDIT.read_bytes()).hexdigest(),
        no_copyright_source_text=True,
        complete_official_denominators={t:None for t in B73.TRACKS},
        teacher_approved_count=0,
        student_published_count=0,
        teacher_full_page_reviews=0,
        editor_reviewed_segments=len(result),
        teacher_reviewed_segments=0,
        classifications=counts,
        priorities=priorities,
        track_backlog=track_backlog,
        records=result,
    )
    report = [
        "# Batch74｜56段非编号来源的项目级编辑分诊（未完成教师原子化）",
        "",
        f"- 来源PDF SHA-256：`{PDF_SHA}`",
        "- 完整性：56/56条 Batch73 高优先级非锚定区间均有独立项目编辑归类、原始片段SHA和后续审查动作。",
        "- 不含课标版权原文；不是全页教师审核、官方条款确认或认证的知识原子分母。",
        "- 官方七轨分母仍然为 null；教师批准0，学生发布0。",
        "",
        "## 来源候选分类（只供复核调度）",
    ]
    report.extend(f"- {c}：{n}段" for c,n in counts.items())
    report += ["", "## 七轨与选修总论来源分诊（均不代表官方分母）"]
    report.extend(f"- {t}：编辑分诊 {v['editorial_segments']} 段，高优先级 {v['high_priority_unresolved']} 段；官方分母未知" for t,v in track_backlog.items())
    report += [
        "",
        "## 高风险跟进",
        "- 第29页四条立体几何判定定理已独立形成四份含假设、分步证明、反例和精确坐标见证的教师草案；尚需独立数学及教师审核。",
        "- 第35页原件已在Mac上视觉核验，并将数学建模流程及返回分支作独立结构记录；PDFKit仍损坏，真实教师审核未完成。",
        "- 第51/57/64/69/73页分别存在跨轨和专题边界，需要细分，不得串轨。",
        "- 选修E需要学校的实际开课方案，绝不把全国固定官方分母编造为0。",
        "- 其他跨页续句必须连同前后邻段核对，再决定是否单独建立原子。",
        "",
        "## 下一批",
        "逐条细分高优先级未编号内容、提交第35页流程语义供教师审核、把真正的课程要求映射到概念/定理/方法/能力，然后再扩写已确认缺口的完整原创讲义与题族；维持教师批准和学生发布门禁。",
        "",
    ]
    return payload, "\n".join(report)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    ap.add_argument("--verify-local-source",action="store_true")
    args=ap.parse_args()
    if args.verify_local_source:
        B73.validate_witness(B73.load(B73.WITNESS), verify_mac_source=True)
    payload,md=build()
    if args.check:
        assert OUTPUT.read_text(encoding="utf8") == canonical(payload), "Batch74 JSON out of date"
        assert REPORT.read_text(encoding="utf8") == md, "Batch74 report out of date"
    else:
        OUTPUT.write_text(canonical(payload),encoding="utf8")
        REPORT.write_text(md,encoding="utf8")
    print(f"Batch74 editorial triage {len(payload['records'])}/56; {payload['classifications']}; source_check={args.verify_local_source}; official_denominator=unknown")


if __name__=="__main__":
    main()
