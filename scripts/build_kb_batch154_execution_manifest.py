#!/usr/bin/env python3
"""Versioned immutable-byte audit of REAL authorized-Mac Batch154 runs.

A finite witness does not prove a universal theorem; an editor draft is never
teacher-approved; historical source markers are not course-atom denominators.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch154_lessons as lessons
import build_kb_batch154_crosswalk as crosswalk
import build_kb_batch154_scope_graph as graph
import check_kb_batch154_math as oracle

SOURCE_COMMIT = "1aa4da57d3c6c240b590bcc1a6d7620047cfaa76"
PREFIX = "KB_BATCH154"
LOG_NAMES = ("FOCUSED", "NODE", "BROWSER", "MAC_FULL")
LOGDIR = ROOT / "docs/evaluation/logs"
MANIFEST = ROOT / "docs/evaluation/KB_BATCH154_TEST_MANIFEST.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH154_EXECUTION_2026-11-14.md"

def require(condition, message):
    if not condition:
        raise ValueError("KB154 archived evidence invalid: " + message)

def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def read_runs(logdir: Path = LOGDIR):
    rows, texts = {}, {}
    for name in LOG_NAMES:
        p = logdir / f"{PREFIX}_{name}.log"
        e = logdir / f"{PREFIX}_{name}.exit"
        require(p.is_file() and e.is_file(), f"missing {name} log or exit")
        data, exit_bytes = p.read_bytes(), e.read_bytes()
        require(len(data) > 100 and exit_bytes.strip() == b"0", f"empty/failed {name}")
        text = data.decode("utf-8")
        require("\x00" not in text, f"NUL or binary {name}")
        texts[name] = text
        rows[name] = dict(path="docs/evaluation/logs/" + p.name, sha256=digest(data),
                          bytes=len(data), exit_path="docs/evaluation/logs/" + e.name,
                          exit_sha256=digest(exit_bytes), exit_code=0)
    require(re.search(r"\b828 passed\b", texts["FOCUSED"]) is not None,
            "828 focused tests not evidenced")
    require("# pass 111" in texts["NODE"] and "# fail 0" in texts["NODE"],
            "111 Node tests not evidenced")
    require("IPAD PILOT CHROME PASS 9" in texts["BROWSER"] and
            re.search(r"\b2 passed\b", texts["BROWSER"]) is not None and
            "Chrome browser suite passed" in texts["BROWSER"],
            "Chrome/pytest browser tests not evidenced")
    full = texts["MAC_FULL"]
    for pattern, meaning in (
        (r"\b66,?293 passed, 5 skipped\b", "backend full"),
        (r"PASS KB154 source graph: 61 pages, 315 numbered markers", "source graph"),
        (r"PASS KB154 exact bounded math witnesses 40/40", "SymPy independent"),
        (r"PASS Batch154: 10 deep teacher manuscripts", "original lessons"),
        (r"Mac PDFKit source rehash PASS", "private source rehash"),
        (r"# pass 111", "Node in full"),
    ):
        require(re.search(pattern, full) is not None, meaning + " absent from Mac full log")
    return rows

def build(logdir: Path = LOGDIR):
    runs = read_runs(logdir)
    manuscripts = lessons.build()
    require(len(manuscripts) == 10 and lessons.validate(manuscripts), "10-source-locked lessons")
    inventory = lessons.audit(manuscripts)
    cross = crosswalk.build()
    require(crosswalk.validate(cross), "editorial crosswalk")
    scoped = graph.build()
    require(graph.validate(scoped), "61-page source graph conservation")
    math = oracle.run()
    require(math["n"] == 40 and math["negative"] == 20 and
            math["legal_or_boundary"] == 20, "40 finite exact witnesses")
    require(inventory["total_teacher_only_drafts"] == 145 and
            inventory["teacher_approved"] == inventory["student_authoritative"] == 0,
            "false authority or draft count")
    require(cross["matched_editorial_candidates"] == 104 and
            cross["missing_editorial_candidates"] == 135, "source draft links")
    require(scoped["source_pages_scanned"] == 61 and
            scoped["source_numbered_markers"] == 315 and
            scoped["original_cde_lines_classified"] == 122 and
            scoped["cde_proposals_from_unnumbered_sources"] == 32, "official source counts")
    require(scoped["risk_pages"] == 53, "source risk queue drift")
    require(not scoped["seven_track_official_census_complete"] and
            not scoped["cross_page_semantic_dedup_human_review_complete"],
            "falsified national source closure")
    require(all(v is None for v in scoped["official_atom_denominators"].values()),
            "fabricated official knowledge atom denominators")
    return dict(schema="kb154-real-mac-byte-evidence/1",
                source_commit=SOURCE_COMMIT, date="2026-11-14",
                environment="AUTHORIZED_MACBOOK_AIR_ONLY",
                historic_editorial_candidates=239, source_links=104, source_gaps=135,
                pending_teacher_manuscripts=145, newly_authored_manuscripts=10,
                teacher_examples=20, student_safe_hint_steps=30, near_far_transfers=20,
                source_pdf_pages=188, source_pages_indexed=61,
                numbered_markers_not_atoms=315, cde_classified_source_lines=122,
                cde_unnumbered_proposals_pending=32, pages_with_pending_source_risks=53,
                official_atom_denominators={t: None for t in lessons.TRACKS},
                official_completion_rate=None, teacher_approved=0, student_authoritative=0,
                general_formal_proof_certificates=0, arbitrary_student_proof_steps_certified=0,
                historical_uncertified_proof_steps=538, pending_math_conflicts=10,
                bounded_exact_witnesses=40, invalid_hypotheses_witnesses=20,
                focused_passed=828, backend_passed=66293, backend_skipped=5,
                node_passed=111, chrome_simulated_checks=9, browser_pytest_passed=2,
                warnings=["Finite exact examples are not general proof certification",
                          "Private standard rehash is local; no licensed standard raw text committed",
                          "A draft is not a human teacher approval"],
                logs=runs)

def render(m: dict) -> str:
    lines = [
        "# KB154｜Mac 原始验收记录（2026-11-14）", "",
        "源码起点为授权 MacBook Air 工作树 commit `" + SOURCE_COMMIT + "`。独立 worktree 开发；未操作 Tang、未改动主仓既有未提交内容、不合并 main、不强推。", "",
        "## 本批实际完成的数学内容与边界",
        "新增10份原创、来源SHA锁定的 REVIEW_PENDING / TEACHER_ONLY 候审讲义：分段函数唯一分支、介值定理零点条件、对数换底条件、古典概率样本空间、导数差商、带截距OLS退化、极限四则运算、定积分黎曼和、社会调查频率、投影与仿射平行保持。",
        "各含符号定义/域/必要条件/分步说明/反例/典型错误/两道教师解答题/三级学生提示/近远迁移。新增教师例题20、提示30、迁移20，累计145份候审；教师批准0，学生权威发布0。", "",
        "## K00/K01 正式来源范围追踪（绝不虚构课标分母）",
        "61页（印刷页13–73）索引、315个编号标记、122条C/D/E分类非空行、32项未编号选修编辑提案、53页风险待审。上述标记/行/提案不属于国家课标原子分母，不能相加。",
        "历史239条编辑候选：104已关联候审完整稿，135尚未关联。七轨正式课标原子分母全部 UNKNOWN，未完成跨页语义去重和真人核定。C/D/E选修的边界不得按整页推定，E轨学校示例不得算作必修。", "",
        "## K07 数学有效性与教学 Agent 安全",
        "独立SymPy条件见证40/40通过，其中20个适用或边界样本、20个失效前提或错误泛化拒绝。538条历史证明步骤未获一般形式认证，10项冲突未被教师裁决。学生自由作答不能借此宣称自动验证；学生检索默认 NO_APPROVED_EVIDENCE，教师解答不可泄漏。", "",
        "## K09 Mac真实执行与保存的原始字节",
        "本轮实际执行：后端66293 passed/5 skipped；Node111 passed；专项828 passed；Chrome模拟交互9组和浏览器pytest2 passed；完整Mac脚本退出码0。专项与全量有重叠，不重复相加；有第三方弃用警告，且Chrome模拟不是实体iPad测试。", "",
        "| 实际日志 | 退出码 | 字节 | SHA-256 |", "|---|---:|---:|---|"
    ]
    for name, rec in sorted(m["logs"].items()):
        lines.append(f"| {name} | {rec['exit_code']} | {rec['bytes']} | `{rec['sha256']}` |")
    lines += ["", "每个日志及退出码独立存档，并在机器可读manifest记录原始字节SHA；篡改/虚假批准负面测试会失败。Mac私有正版课标通过PDFKit本地指纹复核，不上传原始课标正文。", "",
              "## 后续未完成",
              "K00须按原课标逐句拆分并经教师审核、跨页语义裁决，才能冻结七轨官方分母；继续135条历史候选缺稿、538条未一般证明步骤和10项数学冲突；K08须补真实未见题API与规则baseline对照。所有讲义保持 REVIEW_PENDING。", ""]
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    args = p.parse_args()
    m = build()
    doc = render(m)
    if args.write:
        MANIFEST.write_text(json.dumps(m, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                            encoding="utf-8")
        REPORT.write_text(doc, encoding="utf-8")
    else:
        require(json.loads(MANIFEST.read_text(encoding="utf-8")) == m, "manifest changed")
        require(REPORT.read_text(encoding="utf-8") == doc, "report changed")
    print("PASS KB154 archived Mac four original log/exit SHA pairs; math/scope/teacher guards")

if __name__ == "__main__":
    main()
