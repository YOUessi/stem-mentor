#!/usr/bin/env python3
"""Replay byte hashes of actual archived Mac evidence; never impersonate test execution."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch140_proof_guards as guards
import check_kb_batch140_math as oracle

OUT=ROOT/"docs/evaluation/KB_BATCH140_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH140_EXECUTION_2026-11-14.md"
LOG=ROOT/"docs/evaluation/logs"
PARENT_SHA="9df4209a4467385fb4ddf7e89e775716c98cd7e3"
NAMES=("FOCUSED","MAC_FULL","BROWSER")

def require(ok,msg):
    if not ok:raise ValueError("Batch140 execution evidence: "+msg)

def build():
    logs={}
    for n in NAMES:
        fp=LOG/("KB_BATCH140_"+n+".log")
        ep=LOG/("KB_BATCH140_"+n+".exit")
        require(fp.is_file() and ep.is_file(),"missing original log or exit "+n)
        raw=fp.read_bytes();code=ep.read_text().strip()
        require(code=="0","non-zero exit "+n+"="+code)
        require(len(raw)>100,"empty log "+n)
        logs[n]={
            "log":str(fp.relative_to(ROOT)), "exit":str(ep.relative_to(ROOT)),
            "sha256":hashlib.sha256(raw).hexdigest(),
            "bytes":len(raw),"exit_sha256":hashlib.sha256(ep.read_bytes()).hexdigest(),
            "exit_code":0
        }
    f=(ROOT/logs["FOCUSED"]["log"]).read_text(errors="replace")
    m=(ROOT/logs["MAC_FULL"]["log"]).read_text(errors="replace")
    b=(ROOT/logs["BROWSER"]["log"]).read_text(errors="replace")
    require(bool(re.search(r"\b370 passed\b",f)),"focused 370 tests missing")
    require(bool(re.search(r"\b373 passed\b",m)),"Mac script did not call Batch140 tests")
    require(bool(re.search(r"\b66,?293 passed, 5 skipped\b",m)),"full Python backend test numbers missing")
    require(bool(re.search(r"# pass 111|111/111|111 passed",m)),"111 Node tests missing")
    require("PASS Batch140 independent SymPy" in m,"math oracle missing")
    require("PDF REHASHED" in m,"Mac-only protected official source PDF replay absent")
    require(bool(re.search(r"\b2 passed\b",b)),"browser pytest missing")
    p=guards.build(); e=oracle.evidence()
    require(p["p0_with_distinct_review_cards"]==80 and p["p0_without_review_cards"]==47 and
       p["p0_with_any_earlier_editorial_review"]==127,"P0 provenance drift")
    require(e["positive_boundary_count"]==24 and e["invalid_premise_count"]==24,"math Oracle drift")
    return {
        "schema":"kb140-mac-evidence/1", "run_date":"2026-11-14",
        "source_parent_remote_sha":PARENT_SHA,
        "test_source":"AUTHORIZED_MAC_NOT_TANG",
        "ci_can_only_replay_archived_logs":True,
        "original_mac_execution_all_zero":True,
        "focused_pytest_passed":370,"python_backend_passed":66293,"backend_skipped":5,
        "node_passed":111, "browser_pytest_passed":2, "chrome_playwright_exit_code":0,
        "mac_pdfkit_source_rehashed":True, "new_p0_source_cards":24,
        "p0_denominator":127,"p0_with_newer_cards":80,"p0_without_newer_cards":47,
        "p0_with_earlier_editorial_reviews":127,
        "math_finite_cases":48,"math_valid_cases":24,"math_invalid_premises":24,
        "historical_unverified_steps":538,"math_conflicts_unresolved":10,
        "new_complete_teacher_manuscripts":0, "previous_bounded_teacher_manuscripts":57,
        "official_track_denominators":{"COMPULSORY":None,"SELECTIVE_COMPULSORY":None,
             **{"ELECTIVE_"+q:None for q in "ABCDE"}},
        "teacher_approvals":0,"general_proof_certifications":0,
        "student_authoritative_releases":0,"logs":logs,
    }

def render(d):
    lines=[
      "# STEM Mentor｜Batch140 Mac真实测试与GitHub交付证据",
      "",
      "源远端父提交 "+d["source_parent_remote_sha"]+"；最终交付SHA以GitHub独立分支为准；源码和测试均在授权Mac完成，未使用Tang。",
      "",
      "## 一、本批源码与数学成果",
      "",
      "- K07/K01：针对24条KB80中最高风险P0历史证明步骤，各建立一份原始claim/reason及SHA-256锁定的逐步条件审查，写明必须前提、推导合法性、不适用边界和反例，全部REVIEW_PENDING。",
      "- K07：独立SymPy/精确算例48/48（24组合法/边界见证、24组前提失效拒绝），不构成任何一般定理的形式证明或学生自由文本证明的认证。",
      "- K00/K01历史口径纠正：KB28/KB29/KB30此前已为全部127条P0建立较早的编辑候审记录（35+48+44）；本批基于另一来源卡体系把36+20张扩至80张，尚有47条缺该新版卡，**绝不把47称为从未接受数学审查的步骤**。",
      "- 原有538条未认证历史证明步骤、10项未裁决数学冲突保持开放；教师批准和学生权威发布均为0。",
      "- 本批不新增完整讲义；上一批57份是有界教师候审稿，不是课程覆盖率。七轨正式知识原子分母继续UNKNOWN。",
      "- K08学生API仍拒绝未批准证据，不泄漏教师解答或不受支持的学生步骤认证。",
      "",
      "## 二、授权Mac全量与专项测试",
      "",
      "| 验收 | 实测 |",
      "|---|---|",
      "| Batch140专项 | 370 passed（与全量重叠，不重复累计） |",
      "| Python后端全量 | 66,293 passed · 5 skipped |",
      "| Node | 111 passed |",
      "| 浏览器pytest | 2 passed |",
      "| Chrome/Playwright模拟 | EXIT 0（非真实iPad设备） |",
      "| Mac PDFKit私有课标行重放 | PASS，GitHub CI只可验证摘要，不能自行读取私人PDF |",
      "| 独立SymPy有限数学Oracle | 48 passed（不等于全称数学证明） |",
      "",
      "## 三、真实原始日志摘要",
      "",
      "| 日志 | Exit | SHA-256 | 字节 |",
      "|---|---:|---|---:|",
    ]
    for n in NAMES:
        r=d["logs"][n]
        lines.append("| "+r["log"]+" | 0 | "+r["sha256"]+" | "+str(r["bytes"])+" |")
    lines += ["",
       "3份原始日志及3份退出码文件均在版本库，机器可读字节与退出码哈希在KB_BATCH140_TEST_MANIFEST.json；不是GitHub CI自身的Mac重放。",
       "",
       "## 四、失败记录、修复与下一批",
       "",
       "- 初次运行因部分数学前提文字不足审查门禁而失败；补足实际适用条件后再测试，未降低质量门槛。",
       "- 初次SymPy椭圆有限实例混用了Python浮点与精确有理数，导致等式对比失败；已改为精确有理数并重跑48组。",
       "- 溯源发现历史KB28/29/30已涵盖全部127个P0编辑提案；保留不同审查层次，避免统计性误导。",
       "- 下一批K00必须逐条拆分原始课标编号要求并跨页去重，建立可审计的必修、选择性必修、选修A–E正式课程分母。",
       "- 下一批K07继续给剩余47条历史P0补建新式源锁定验证卡，分开量词层证明、有限见证和教师审查。",
       "- 下一批K02–K06恢复整模块原创讲义、题族、错因、提示与近远迁移，K08/K09独立测检索和越权剧透，审核以前保持学生端拒答。",
       ""
    ]
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--write",action="store_true")
    group.add_argument("--check",action="store_true")
    a=p.parse_args()
    d=build();md=render(d)
    if a.write:
        OUT.write_text(guards.encode(d),encoding="utf-8")
        REPORT.write_text(md,encoding="utf-8")
    else:
        require(json.loads(OUT.read_text(encoding="utf-8"))==d,"manifest does not match actual logs")
        require(REPORT.read_text(encoding="utf-8")==md,"Markdown report does not match actual logs")
    print("PASS Batch140 evidence: Mac 370 focused; 66293 backend, 111 Node, 2 browser; 48 mathematical finite checks")
if __name__=="__main__":
    main()
