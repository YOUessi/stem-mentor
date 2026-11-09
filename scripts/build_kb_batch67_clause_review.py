#!/usr/bin/env python3
"""Batch67: auditable cross-page clause distinctions and unnumbered objective queue.

No copyright text is committed. Six math comparisons are independent editorial
scope assessments, not teacher certification of full official clauses.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "curriculum/highschool_math"
DOC = ROOT / "docs/evaluation"
EDITOR = ROOT / "knowledge/editorial_review"
PROPOSALS = SRC / "k00_batch63_provisional_atom_proposals.json"
QUEUED = DOC / "KB_BATCH66_DUPLICATE_REVIEW_QUEUE.json"
REGISTRY = SRC / "k00_batch61_source_anchor_registry.json"
WINDOWS = SRC / "k00_batch63_context_windows.json"
CROSS = SRC / "k00_batch64_competency_proposal_matrix.json"
ASSESSMENTS = EDITOR / "kb_batch66_competency_assessments.json"
LESSONS = DOC / "KB_BATCH65_REMAINING_SCOPE_MANIFEST.json"
OUT = DOC / "KB_BATCH67_CLAUSE_CONTRAST_REVIEW.json"
ABILITIES = DOC / "KB_BATCH67_UNNUMBERED_OBJECTIVE_QUEUE.json"
METRICS = DOC / "KB_BATCH67_SEVEN_TRACK_COVERAGE.json"
REPORT = DOC / "KB_BATCH67_SOURCE_AND_MATH_REVIEW.md"
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A", "ELECTIVE_B",
          "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")

# Written from Mac-local original syllabus excerpts (text not reproduced).
# A distinctive mathematical prerequisite is not a proof that two official
# requirements are equivalent, and neither editorial comparison is approved.
SCOPE = [
 ("GENERAL_VS_SPECIALIZED_FUNCTION",
  "一般函数的对应关系/任意定义域与具体对数函数的正实数定义域不同。",
  "f(x)=x² 在 x=-1 有定义；log₂(x) 在 x=-1 无实数意义。",
  "用“都是函数”推断两个条款是同一教学原子，忽略真子类的定义域。"),
 ("GENERAL_VS_LOG_DOMAIN",
  "函数的唯一对应与对数 x>0、底数a>0且a≠1的特殊结构不能合并。",
  "f(x)=x+1 在 x=0 有定义；log₂(0) 在实数中无定义。",
  "把一般函数的定义域和对数函数的定义域等同。"),
 ("MONOTONICITY_VS_LOG_BASE",
  "一般区间单调性是上位定义；对数函数的方向另取决于底数。",
  "log₂(4)>log₂(2)；log₍₁⁄₂₎(4)<log₍₁⁄₂₎(2)。",
  "忽略 0<a<1 情形，把所有对数函数当作严格递增。"),
 ("AMGM_VS_TRIG_DOMAIN",
  "非负数的算术—几何均值边界与三角式变形时正切的定义域约束不是同一命题。",
  "a=0,b=4 满足 AM–GM；cosθ=0 时 tanθ 无定义，不能约分。",
  "把均值不等式的非负约束套到三角恒等变换中。"),
 ("DIVISION_VS_QUADRATIC_SIGN",
  "等式除以未知量的非零前提与二次不等式解集的符号区间法是不同任务。",
  "x²=x 的 x=0 根不能被除以 x 的变形抹掉；x²−x>0 的两端区间需逐段验证。",
  "除以含零因子的表达式丢根，或只求零点就把零点算入严格不等式。"),
 ("AMGM_VS_QUADRATIC_SIGN",
  "AM–GM 的非负两数条件与任意二次函数的正负区间分析不等价。",
  "a=1,b=4 时 2≤5/2；x²−5x+4 在 x=2 为负，在 x=0 为正。",
  "把均值不等式的下界无条件用作任意二次函数全域的符号判断。"),
]
OBJECTIVES = [
 ("显式区分集合元素、子集和集合运算并评价三种表征的适用性","误把课程内容清单看作单一可量化学业要求"),
 ("教学活动需帮助学生完成从具体计算到抽象数学对象的过渡","课堂教学提示并非学生已掌握的数学定理"),
 ("从情境提取对象特征、转换集合语言并解释反例","尚无逐项核对条款全文和真实评分者标注"),
 ("区分一般函数概念、图像、初等函数结构和应用任务","栏目摘要含多个目标，不能由单道题直接代表"),
 ("说明函数表征转换及模型适用域，而不只是符号操作","教学建议不是可与测试成绩一一对应的知识原子"),
 ("区分向量、复数和空间关系的多种数学对象","整体栏目不能由一份有限见证证明覆盖"),
 ("结合物理情境和几何/代数视角解释向量运算","实践教学建议需课堂观察证据"),
 ("验证二维基底非共线前提并解释空间几何结论","有限实例不代表完整领域课程能力认证"),
 ("区分概率和统计及其不同推理前提","内容概要不是固定知识原子数"),
 ("检查随机试验假设、事件集合、等可能和统计采样偏差","教学过程需要教学场景记录"),
 ("构建有限样本空间并验证古典概型的等可能前提","学生能力表现及评分一致性未经审核"),
 ("表达模型假设、变量单位、推导和现实边界","建模叙述是过程规范而非独立定理"),
 ("对建模课题的选题、实施、报告和交流提供过程证据","教学过程不能用自动题目匹配取代"),
 ("按建模研究目标收集证据、撰写报告并解释局限","真实报告/演示尚未经过课程教师审查"),
]

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def encode(obj):
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

def need(flag, detail):
    if not flag:
        raise ValueError(detail)

def witness(i):
    """Exact finite examples with guard assertions; NOT universal proofs."""
    if i == 0:
        return F(-1)**2 == 1 and not (F(-1) > 0)
    if i == 1:
        return (F(0) + 1) == 1 and not (F(0) > 0)
    if i == 2:
        b = F(1, 2)
        return 2**2 == 4 and 2**1 == 2 and b**(-2) == 4 and b**(-1) == 2 and -2 < -1
    if i == 3:
        return F(0) * 4 == 0 and F(0 + 4, 2) == 2 and F(0) == 0
    if i == 4:
        f = lambda x: x*x-x
        return f(F(0)) == 0 and f(F(-1)) > 0 and f(F(2)) > 0 and f(F(1)) == 0
    if i == 5:
        q = lambda x: x*x - 5*x + 4
        return F(2) <= F(1 + 4, 2) and q(F(0)) > 0 and q(F(2)) < 0 and q(F(5)) > 0
    raise ValueError("unsupported finite witness key")

def verify_source_local(registry, locations, source_dir=Path("/private/tmp")):
    # Only on the authorized Mac. This verifies original PDFKit page bytes against
    # the frozen registry, not the visual reading of a PDF diagram or full clause.
    page_rows = {}
    for anchor in locations:
        page = anchor["printed_page"]
        f = source_dir / f"kb56_page_{page}.txt"
        need(f.is_file(), "Mac source page unavailable: " + str(f))
        raw = f.read_bytes()
        expected = next(x["source_page_pdfkit_sha256"] for x in registry["rows"]
                        if x["printed_page"] == page)
        need(hashlib.sha256(raw).hexdigest() == expected, "Mac source page digest changed")
        lines = raw.decode("utf-8").splitlines()
        need(0 < anchor["pdfkit_line"] <= len(lines), "source line out of range")
        need(hashlib.sha256(lines[anchor["pdfkit_line"] - 1].encode()).hexdigest() ==
             anchor["source_line_sha256"], "source anchor line digest changed")
        page_rows[page] = True
    return len(page_rows)

def build(sources=None):
    sources = sources or {}
    props = sources.get("proposals", load(PROPOSALS))
    queue = sources.get("queue", load(QUEUED))
    reg = sources.get("registry", load(REGISTRY))
    windows = sources.get("windows", load(WINDOWS))
    cross = sources.get("cross", load(CROSS))
    assessments = sources.get("assessments", load(ASSESSMENTS))
    lessons = sources.get("lessons", load(LESSONS))
    candidates = props["proposals"]
    lookup = {x["candidate_id"]: x for x in candidates}
    need(len(candidates) == 62 and len(lookup) == 62, "62 unique internal candidates expected")
    need(len(queue["rows"]) == len(SCOPE) == 6, "six candidate pairs expected")
    need(len(reg["rows"]) == 428 and len(windows["rows"]) == 45, "source lineage changed")
    need(len(cross["links"]) == 28 and len(assessments) == len(OBJECTIVES) == 14,
         "competency source mapping count changed")
    need(lessons["scopes_with_at_least_one_teacher_manuscript"] == 31,
         "prior source-lesson link count changed")

    all_anchors = {f"KB61-P{r['printed_page']:03d}-L{r['pdfkit_line']:03d}": r
                   for r in reg["rows"]}
    need(len(all_anchors) == 428, "duplicate official source coordinates")
    full = {r["anchor_id"]:r for r in windows["rows"]}
    pairs = []
    local_locations = {}
    for i, (pair, spec) in enumerate(zip(queue["rows"], SCOPE)):
        left, right = lookup[pair["left"]], lookup[pair["right"]]
        need(left["source_page"] != right["source_page"], "not cross page")
        need(left["teacher_review"] == right["teacher_review"] == "REVIEW_PENDING",
             "candidate teacher status forged")
        need(left["math_equivalence"] == right["math_equivalence"] == "NOT_REVIEWED",
             "preexisting equivalence status changed")
        need(pair["merge_permitted"] is False and pair["requires_full_clauses"] is True,
             "unsafe merge in source queue")
        for c in (left, right):
            a=all_anchors[c["parent_anchor_id"]]
            w=full[c["parent_anchor_id"]]
            need(c["source_window_sha256"] == w["source_window_sha256"] and
                 a["source_line_sha256"] == w["source_line_sha256"] and
                 a["printed_page"] == c["source_page"], "broken source window or anchor")
            local_locations[c["parent_anchor_id"]] = a
        need(witness(i) is True, "mathematical finite witness failed")
        relation, scope, example, failure = spec
        pairs.append(dict(review_id=f"KB67-CROSS-{i+1:02d}",
                          left=pair["left"], right=pair["right"],
                          left_page=left["source_page"], right_page=right["source_page"],
                          left_source_window_sha256=left["source_window_sha256"],
                          right_source_window_sha256=right["source_window_sha256"],
                          left_mathematical_topic=left["editorial_subtopic"],
                          right_mathematical_topic=right["editorial_subtopic"],
                          relation_hypothesis=relation, editorial_distinction=scope,
                          exact_finite_example=example, misleading_reasoning=failure,
                          math_evidence="FINITE_EXACT_INSTANCE_ONLY",
                          reviewer_decision="NOT_REVIEWED_BY_TEACHER",
                          official_clause_complete=False, merge_permitted=False,
                          student_publishable=False, teacher_review="REVIEW_PENDING"))
    obj = []
    sections = [x for x in cross["links"] if x["proposal_id"].endswith("-P1")]
    need(len(sections) == 14, "cannot identify 14 distinct section proposals")
    for i, (link, assessment, spec) in enumerate(zip(sections, assessments, OBJECTIVES)):
        a=all_anchors[link["official_section_anchor"]]
        need(a["source_line_sha256"] == link["section_source_line_sha256"], "bad competency source hash")
        need(link["coverage_status"] == "UNMAPPED" and link["abilities_covered"] is False and
             link["teacher_approved"] is False, "source competency was silently approved")
        need(assessment["id"] == f"KB66-ASM-{i+1:02d}" and
             assessment["teacher_review"] == "REVIEW_PENDING" and
             assessment["student_publishable"] is False, "assessment status changed")
        goal, blocker = spec
        obj.append(dict(section_anchor=link["official_section_anchor"],
                        section_source_line_sha256=a["source_line_sha256"],
                        section_kind=link["section_kind"],
                        draft_assessment_id=assessment["id"],
                        draft_observable_criterion=goal,
                        outstanding_review_evidence=blocker,
                        official_full_clause_verified=False, teacher_review="REVIEW_PENDING",
                        assessment_proves_coverage=False, coverage_status="UNMAPPED",
                        student_publishable=False))
        local_locations[link["official_section_anchor"]] = a
    leads = Counter(x["track_hint"] for x in reg["rows"])
    proposal_leads=Counter(all_anchors[x["parent_anchor_id"]]["track_hint"] for x in candidates)
    need(set(leads).issubset(TRACKS) and sum(leads.values()) == 428, "seven track leads changed")
    need(set(proposal_leads).issubset(TRACKS), "invalid candidate track hint")
    need(all(x["official_atomic_membership"] == "UNDETERMINED" and
             x["teacher_review"] == "REVIEW_PENDING" for x in candidates),
         "provisional candidates falsely promoted")
    coverage = {t:dict(official_atom_denominator=None,
                       heuristic_source_leads=leads[t],
                       internal_provisional_atom_splits=proposal_leads[t],
                       fully_verified_official_clauses=0, teacher_approved=0,
                       student_publishable=0, coverage_fraction=None) for t in TRACKS}
    c = dict(schema_version="kb67-source-contrast-v1",
             source="Mac-original-PDFKit-anchor-window-hashes-no-copyright-text",
             source_candidate_total=62, pairs_reviewed_for_editorial_distinction=6,
             teacher_confirmed_equivalences=0, automatic_merges=0,
             full_clause_teacher_reviews=0, source_visual_diagram_page35="PENDING_MANUAL_REVIEW",
             rows=pairs)
    a = dict(schema_version="kb67-unnumbered-objective-review-v1",
             curriculum_requirements_fully_mapped=0, review_pending=14,
             source_text_not_embedded=True, rows=obj)
    m = dict(schema_version="kb67-conservative-tracks-v1", tracks=coverage,
             source_leads_total=428, candidate_splits_total=62,
             teacher_approved_total=0, official_denominator_known=0,
             confirmed_full_page_teacher_reviews=0,
             legacy_113_entries_not_a_curriculum_denominator=True,
             missing_official_atoms_count=None,
             unknown_scope_not_equivalent_to_zero=True)
    need(sum(v["internal_provisional_atom_splits"] for v in coverage.values()) == 62,
         "62 provisional splits must be completely partitioned")
    return c,a,m,list(local_locations.values())

def write(check=False, verify_local=False, sources=None):
    c,a,m,locations = build(sources)
    if verify_local:
        count=verify_source_local(load(REGISTRY),locations)
        need(count >= 5, "too few independent source pages verified")
    payload = {OUT:encode(c),ABILITIES:encode(a),METRICS:encode(m)}
    summary = [
        "# Batch67｜跨页条款数学差异核查与未编号能力审核工作单",
        "",
        "本报告是原创编辑审查线索，不转载课标原文、不是教师签核或官方原子分母。",
        "",
        "## 六组跨页候选逐组数学条件核对",
        "",
        "| 编号 | 主题差异 | 数学有限见证 | 结论 |",
        "| --- | --- | --- | --- |",
    ]
    for x in c["rows"]:
        summary.append(f"| {x['review_id']} | {x['editorial_distinction']} | {x['exact_finite_example']} | 不自动合并；待核对条款全文及教师批准 |")
    summary.extend(["", "## 十四项未编号内容/教学/学业栏目（全部仍未映射）", "",
                    "| 来源锚点 | 教师侧自编测评 | 可观测目标（未确认对应官方条款） | 待补证据 |",
                    "| --- | --- | --- | --- |"])
    for x in a["rows"]:
        summary.append(f"| {x['section_anchor']} | {x['draft_assessment_id']} | {x['draft_observable_criterion']} | {x['outstanding_review_evidence']} |")
    summary.extend(["", "## 七轨分母与范围门禁", "",
                    "| 轨道 | 来源线索 | 项目临时拆分 | 官方数学原子分母 | 教师正式批准 |",
                    "| --- | ---: | ---: | --- | ---: |"])
    for t,r in m["tracks"].items():
        summary.append(f"| {t} | {r['heuristic_source_leads']} | {r['internal_provisional_atom_splits']} | 未确定(null) | 0 |")
    summary.extend(["",
                    "61/61页局部来源线索 ≠ 全页教师审核，实际完成0/61；113条旧工程映射不是课标原子分母。",
                    "6组数学实例不认证一般定理，不认证学生自由步骤；不得把编辑区别直接当作已完成去重。",
                    "第35页建模流程图仍需人工视觉审核（图片信息不能由文本SHA证明完整）。",
                    "选修E在启发式起点表中的0只是当前提取结果，不表示选修E没有学校自主课程。",
                    "14项栏目仍UNMAPPED；31篇内部范围草案与14篇能力测评不代表官方覆盖。",
                    "",
                    "## 下一批",
                    "对完整课标条款逐页人工审查、图示复核、学业能力与测评真实对应签核；",
                    "建立七轨官方原子分母与完整缺失矩阵；逐章补充原创定义/定理/证明/题族；",
                    "针对538个未经形式认证的历史证明步骤与10组冲突开展独立数学审查。", ""])
    payload[REPORT] = "\n".join(summary)
    for path,txt in payload.items():
        if check:
            need(path.exists() and path.read_text(encoding="utf-8") == txt,
                 "Batch67 generated output drift: "+str(path))
        else:
            path.write_text(txt,encoding="utf-8")
    return c,a,m

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--verify-local",action="store_true")
    args=parser.parse_args()
    c,a,m=write(check=args.check,verify_local=args.verify_local)
    print("Batch67: cross-page",len(c["rows"]),"unnumbered",len(a["rows"]),
          "provisional",m["candidate_splits_total"],"official denominators all unknown")
