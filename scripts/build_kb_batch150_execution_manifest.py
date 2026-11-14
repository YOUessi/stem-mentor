#!/usr/bin/env python3
"""Versioned, SHA-checked original Mac Batch150 test evidence (offline CI replay)."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch150_de_boundary as scope

LOG=ROOT/"docs/evaluation/logs"
OUT=ROOT/"docs/evaluation/KB_BATCH150_EXECUTION_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH150_EXECUTION_2026-11-14.md"
SOURCE_SHA="8d5c5919183ef921a0c09acb90e6a46a86877ebd"
UPSTREAM_SOURCE_SHA="ec17b6aca761d0b11881fea441487296cff8d9ed"
RUNS={"FOCUSED":0,"MAC_FULL":0,"BROWSER":0}

def require(cond,message):
    if not cond:raise ValueError("KB150 real Mac archived evidence: "+message)

def hashbytes(data):
    return hashlib.sha256(data).hexdigest()

def collect(folder=LOG):
    records={};logs={}
    for name,expected in RUNS.items():
        log=folder/f"KB_BATCH150_{name}.log"
        ex=folder/f"KB_BATCH150_{name}.exit"
        require(log.is_file() and ex.is_file(),name+" missing original stdout/exit")
        raw,exit_raw=log.read_bytes(),ex.read_bytes()
        require(exit_raw.decode("utf-8").strip()==str(expected),
                name+" nonzero or forged exit")
        # Focused pytest -q logs legitimately contain only a progress line and summary.
        # Full/backend and browser captures must be substantially longer.
        lower_bound={"FOCUSED":80,"MAC_FULL":50000,"BROWSER":500}[name]
        require(len(raw)>=lower_bound,"original "+name+" log truncated")
        records[name]=dict(log_file=f"docs/evaluation/logs/{log.name}",
                           exit_file=f"docs/evaluation/logs/{ex.name}",
                           log_sha256=hashbytes(raw),log_bytes=len(raw),
                           exit_sha256=hashbytes(exit_raw),exit=expected)
        logs[name]=raw.decode("utf-8",errors="replace")
    require(re.search(r"\b36 passed\b",logs["FOCUSED"]),"36 scope negative tests absent")
    full=logs["MAC_FULL"]
    for needle in [
        "KB150 C/D/E semantic boundary PASS",
        "KB150 original Mac PDFKit SHA replay PASS",
        "122/122 licensed lines",
        "36 passed",
        "66293 passed, 5 skipped",
    ]:
        require(needle in full,"Mac full regression missing "+needle)
    require(bool(re.search(r"# pass 111|\b111 passed\b",full)),
            "Node test run absent")
    browser=logs["BROWSER"]
    require("GREEN v0.7 Chrome test: 9 passed" in browser,
            "Chrome interaction log missing")
    require(re.search(r"\b2 passed\b",browser) is not None and
            "Chrome browser suite passed" in browser,
            "browser pytest or final success missing")
    return records

def build(folder=LOG):
    logs=collect(folder)
    census=scope.build()
    require(scope.validate(census),"source/semantic label drift")
    require(census["source_line_counts"]=={
        "ELECTIVE_C":5,"ELECTIVE_D":100,"ELECTIVE_E":10,"PARATEXT":7},
        "lost original legal-source row")
    require(census["proposed_count"]==32 and
            census["approved_atom_denominators"]=={t:None for t in scope.TRACKS},
            "false official atom census")
    require(not census["teacher_approved"] and not census["student_authoritative"],
            "false teacher approval or premature release")
    return dict(schema="kb150-mac-original-evidence/1",run_date="2026-11-14",
        device="YOUTangdeMacBook-Air.local",
        original_local_source_sha=SOURCE_SHA,
        stacked_parent_source_sha=UPSTREAM_SOURCE_SHA,
        original_pdf_rehashed_in_mac_full=True,
        source_line_count=122,
        source_line_owner_counts=dict(census["source_line_counts"]),
        provisional_semantic_topics=32,
        by_track_pending_topics={
            t:sum(x["source_track"]==t for x in census["proposals"])
            for t in ("ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")},
        approved_official_atom_denominators={t:None for t in scope.TRACKS},
        teacher_approved=0,student_authoritative=0,
        general_formal_proofs_certified=0,student_free_text_steps_certified=0,
        pending_teacher_drafts_from_upstream=105,
        new_finished_manuscripts=0,
        backend_full_python_passed=66293,
        backend_full_python_skipped=5,node_passed=111,
        targeted_negative_tests_passed=36,
        chrome_interaction_checks_passed=9,browser_pytest_passed=2,
        summary="Source-line editorial boundary and 32 pending candidate ideas, not official atomic curriculum denominator, not completed teaching manuscripts.",
        logs=logs)

def render(v):
    lines=["# STEM Mentor Batch150｜Mac原始执行与课程分轨实质审计","",
      "本批通过授权Mac的原始PDFKit来源行完成C/D/E分界核对，原始课标文字没有上传。",
      "源码提交："+SOURCE_SHA+"；父源码："+UPSTREAM_SOURCE_SHA+"。原始测试日志与退出码保留原始字节和SHA-256。","",
      "## K00 校订结果","",
      "印刷页69的前5条来源行属于C社会调查，接下来的第6行进入D；印刷页73的前12行仍属于D体育内容，第13行转入E学校选修。重要的72→73体育项目跨页续句保持同一D主题证据链。","",
      "122条非空PDFKit行依来源版面分类：C 5、D 100、E 10、页眉页脚7；32份**原创课程原子候选提案**：C 2、D 17、E 13。它们不是完整讲义，也不是已审核课标原子。E主题是学校可选示例，不能声称全国学校统一必修。","",
      "本轮未补完整深度讲义；沿用上游105份REVIEW_PENDING教师候审稿。全部七轨国家课标正式知识原子分母仍UNKNOWN；教师批准0、学生权威发布0。","",
      "## K01/K08/K09 行为与负面门禁","",
      "新增32条提案的来源哈希、原文行跨页归属、重复候选待审与教师权限封锁；新增公开聚合查询路径，只提供数量与UNKNOWN，不返回版权课标文本、未批准知识单元或完整教师解答。36条专项负面/回归均真实执行通过。","",
      "## 真实Mac测试","",
      "| 运行 | 实测结论 |",
      "|---|---|",
      "| 原始PDFKit行SHA | 122/122，页69/73段落分界与页72/73续句 PASS |",
      "| K00专项 | 36 passed，包含伪造官方覆盖和授权状态拒绝 |",
      "| Python后端全量 | 66,293 passed，5 skipped |",
      "| Node | 111 passed |",
      "| Chrome与浏览器pytest | 9 passed + 2 passed（模拟环境，非实体iPad） |",
      "| Mac完整与Browser脚本 | EXIT 0，原始日志存档 |","",
      "### 日志与退出码SHA-256","",
      "| 运行 | 退出码 | 字节 | SHA-256 |",
      "|---|---:|---:|---|"]
    for key,info in sorted(v["logs"].items()):
        lines.append(f"| {key} | {info['exit']} | {info['log_bytes']} | {info['log_sha256']} |")
    lines.extend(["","## 未完成与下一批","",
      "这只是源码边界的真实纠正，不是必修、选必、选修全部课标原子分母冻结。需要按每个编号/未编号条款做跨页语义拆分、人工检查同义重复，并完成现有105份讲义到真实全量分母的覆盖映射。538条历史未认证证明步骤、10项数学冲突与教师审核继续独立推进。",
      "最终GitHub CI需要以远端动作结论为准，不可用Mac通过冒充GitHub CI通过。",""])
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    b=build()
    j=json.dumps(b,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    md=render(b)
    if args.check:
        require(OUT.read_text(encoding="utf-8")==j and
                REPORT.read_text(encoding="utf-8")==md,
                "original manifest or versioned report has drifted")
    else:
        OUT.write_text(j,encoding="utf-8")
        REPORT.write_text(md,encoding="utf-8")
    print("Batch150 original Mac evidence and SHA-256 logs validated (36 focused, 66,293 Python, 111 Node, 9+2 browser)")
if __name__=="__main__":
    main()
