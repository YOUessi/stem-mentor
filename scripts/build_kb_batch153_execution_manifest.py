#!/usr/bin/env python3
"""Immutable, independently inspectable record of *actual* Mac Batch153 runs.

The manifest attests finite tests and drafts only. It never upgrades human approval
or claims a finite SymPy witness is a proof of a general theorem.
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
import build_kb_batch153_lessons as lessons
import build_kb_batch153_crosswalk as crosswalk
import check_kb_batch153_math as math_guard

LOGDIR = ROOT / "docs/evaluation/logs"
MANIFEST = ROOT / "docs/evaluation/KB_BATCH153_TEST_MANIFEST.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH153_EXECUTION_2026-11-14.md"
SOURCE_COMMIT = "04ed86e0f0b27accc5400cf5e641f0200b069388"
LOG_NAMES = ("FOCUSED", "NODE", "BROWSER", "MAC_FULL")

def require(ok: bool, msg: str):
    if not ok:
        raise ValueError("KB153 evidence invalid: " + msg)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_runs(logdir: Path = LOGDIR):
    records, texts = {}, {}
    for label in LOG_NAMES:
        logfile = logdir / f"KB_BATCH153_{label}.log"
        exitfile = logdir / f"KB_BATCH153_{label}.exit"
        require(logfile.is_file() and exitfile.is_file(), "missing log/exit: " + label)
        raw, exit_raw = logfile.read_bytes(), exitfile.read_bytes()
        require(len(raw) > 100, "empty or truncated log " + label)
        require(exit_raw.strip() == b"0", "nonzero or forged exit " + label)
        txt = raw.decode("utf-8")
        require("\x00" not in txt, "NUL in log " + label)
        records[label] = dict(path=f"docs/evaluation/logs/{logfile.name}",
                              exit_path=f"docs/evaluation/logs/{exitfile.name}",
                              bytes=len(raw), sha256=sha(raw),
                              exit_code=0, exit_sha256=sha(exit_raw))
        texts[label] = txt
    require(re.search(r"\b262 passed\b", texts["FOCUSED"]) is not None, "262 focused checks missing")
    require("# pass 111" in texts["NODE"] and "# fail 0" in texts["NODE"], "111 Node checks missing")
    require("GREEN v0.7 Chrome test: 9 passed" in texts["BROWSER"], "Chrome checks missing")
    require(re.search(r"\b2 passed\b", texts["BROWSER"]) is not None, "browser pytest missing")
    require("Chrome browser suite passed" in texts["BROWSER"], "browser final success missing")
    full = texts["MAC_FULL"]
    require(re.search(r"\b66,?293 passed, 5 skipped\b", full) is not None, "full Python result missing")
    require("# pass 111" in full, "full-script Node result missing")
    require("PASS KB153 finite exact math witnesses: 40/40" in full, "math oracle missing")
    require(re.search(r"\b262 passed\b", full) is not None, "KB153 regression in full script missing")
    require("Mac PDFKit source rehash PASS" in full, "private source replay missing")
    return records

def build(logdir: Path = LOGDIR):
    logs = read_runs(logdir)
    rows = lessons.build()
    require(len(rows) == 10 and lessons.validate(rows), "10 drafts failed validation")
    audit = lessons.audit(rows)
    gap = crosswalk.build()
    require(crosswalk.validate(gap), "source mapping failed")
    oracle = math_guard.cases()
    require(audit["total_teacher_only_drafts"] == 135, "135-draft inventory failed")
    require(gap["matched_editorial_candidates"] == 94 and gap["missing_editorial_candidates"] == 145,
            "94/145 editorial status failed")
    require(oracle["n"] == 40 and oracle["negative"] == 20 and oracle["legal_or_boundary"] == 20,
            "40/20 finite cases failed")
    require(all(x is None for x in audit["official_atom_denominators"].values()),
            "false official denominator")
    require(audit["teacher_approved"] == audit["student_authoritative"] == 0,
            "false student or teacher authority")
    return dict(schema="kb153-real-mac-evidence/1", date="2026-11-14",
                source_commit=SOURCE_COMMIT, authorized_device="MACBOOK_AIR_ONLY",
                source_pdfkit_private_rehash=True, added_drafts=10,
                teacher_only_pending_drafts=135, teacher_approved=0,
                student_authoritative=0, original_teacher_examples=20,
                student_hint_levels=30, near_far_transfer_tasks=20,
                historical_editorial_candidates=239, source_links=94, source_gaps=145,
                official_atom_denominators={t: None for t in lessons.TRACKS},
                official_completion_rate=None, formal_general_proofs=0,
                arbitrary_student_steps_certified=0, historical_proof_steps_unverified=538,
                mathematical_conflicts_pending=10, exact_finite_witnesses=40,
                invalid_premise_or_false_generalization_witnesses=20,
                focused_passed=262, full_backend_passed=66293,
                full_backend_skipped=5, node_passed=111,
                chrome_checks_passed=9, browser_pytest_passed=2,
                warning="Finite cases do not certify universal proofs; draft count is not national syllabus coverage.",
                logs=logs)

def render(m: dict):
    ls = [
        "# KB153 | Mac 原始验收记录（2026-11-14）", "",
        "本批只在授权 MacBook Air 独立 worktree 开发、测试。原始源码 commit `" + SOURCE_COMMIT + "`；未操作 Tang、未编辑主仓未提交修改、未合并 main、未强推。", "",
        "## 实际知识内容",
        "新增十份原创 REVIEW_PENDING / TEACHER_ONLY 候审讲义：正交投影、函数唯一输出与定义域、一元二次不等式分支、Pearson 列联表适用边界、二项分布 iid 前提、高斯消元可逆行变换、凸多边形线性规划顶点最优、多阶段抽样与 SRS、单循环赛程图论、学校选修点值与极限分离。",
        "每篇有形式化陈述/定义域/完整前提/逐步说明、失效案例、典型错因、2 道原创教师例题、3 级不剧透提示及近远迁移。新增教师例题20、提示30、迁移20，累计135篇候审；教师正式批准0、学生权威证据0。", "",
        "## K00/K01 来源真实性和未完成内容",
        "历史编辑线索不是官方课程分母。现存239条历史编辑线索中94条已经与完整候审稿关联，145条缺稿。七轨国家课标的正式可审计原子分母仍全为 UNKNOWN。来源位置与 Mac 私有已授权 PDFKit 哈希关联，禁止提交版权源文本。所有内容保留 REVIEW_PENDING。",
        "",
        "## K07 数学可靠性",
        "40/40条独立精确有限见证通过：20个适用/边界样本，20个错误前提/错误泛化拒绝。不等同一般定理形式认证。历史538条未一般认证证明步骤、10项数学冲突仍待实质核查与教师确认。", "",
        "## K08/K09 教学Agent隔离及Mac真实运行",
        "135篇候审稿仅供本地EDITOR_LOCAL临时 FTS5 编辑预检索；学生始终 NO_APPROVED_EVIDENCE，聚合接口不公开教师答案。已实跑：Python全量 66,293 passed/5 skipped、Node 111 passed、Batch153专项262 passed、Chrome交互9通过、浏览器pytest 2 passed；完整Mac脚本退出码0。专项与全量存在重叠，不重复累计；Python有1条第三方依赖弃用警告；模拟浏览器不等于实体iPad。",
        "",
        "| 原始记录 | 退出码 | 字节 | SHA-256 |", "|---|---:|---:|---|"
    ]
    for label, log in sorted(m["logs"].items()):
        ls.append(f"| {label} | {log['exit_code']} | {log['bytes']} | `{log['sha256']}` |")
    ls += ["", "所有日志有真实退出码 .exit 文件，所有原始字节SHA均在 JSON manifest 记录；CI能离线重演日志完整性与负面篡改测试（不能在CI使用Mac私有课标PDF）。", "",
           "## 未完成与下一批",
           "K00必须逐条核实国家标准课程原子与跨页语义重复，并将 UNKNOWN 分母变为真正教师核实的机器可审计分母；补足145条历史编辑来源缺稿，继续538条一般未经证明步骤、10项数学冲突，增加未见题 Agent 与规则基线/真实API验证。未获教师审查不得正式发布。", ""]
    return "\n".join(ls)

def main():
    p = argparse.ArgumentParser()
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = p.parse_args()
    m = build()
    rendered = render(m)
    if args.write:
        MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        REPORT.write_text(rendered, encoding="utf-8")
    else:
        require(json.loads(MANIFEST.read_text(encoding="utf-8")) == m, "manifest altered")
        require(REPORT.read_text(encoding="utf-8") == rendered, "report altered")
    print("PASS KB153 four actual original Mac log+exit SHA pairs; full, browser, math, review gates")

if __name__ == "__main__":
    main()
