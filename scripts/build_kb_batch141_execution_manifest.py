#!/usr/bin/env python3
"""Verify that archived Mac logs, exit codes and mathematical audit really agree.

GitHub runners verify frozen evidence and hashes, not rerun a Mac-only licensed PDF.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch141_lineage as cards
import check_kb_batch141_math as oracle
LOG=ROOT/"docs/evaluation/logs"
OUT=ROOT/"docs/evaluation/KB_BATCH141_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH141_EXECUTION_2026-11-14.md"
PARENT="81cf8958ab41b31ddf747fbe4c7a5de52d1a57e6"
SOURCE="81709068e0f2768791d51bdc7d738fd161bb7c76"

def require(ok,why):
    if not ok: raise ValueError("KB141 evidence: "+why)

def build():
    logs={}
    for tag in ("FOCUSED","MAC_FULL","BROWSER"):
        p=LOG/("KB_BATCH141_"+tag+".log")
        e=LOG/("KB_BATCH141_"+tag+".exit")
        require(p.is_file() and e.is_file(), "missing Mac original log/exit "+tag)
        content=p.read_bytes()
        require(e.read_text(encoding="utf-8").strip()=="0","nonzero process exit "+tag)
        require(len(content)>100, "truncated log "+tag)
        logs[tag]={
           "log_path":str(p.relative_to(ROOT)),
           "exit_path":str(e.relative_to(ROOT)),
           "byte_count":len(content),
           "sha256":hashlib.sha256(content).hexdigest(),
           "exit_sha256":hashlib.sha256(e.read_bytes()).hexdigest(),
           "actual_exit_code":0,
        }
    logs_text={k:(ROOT/v["log_path"]).read_text(encoding="utf-8",errors="replace")
               for k,v in logs.items()}
    focus=logs_text["FOCUSED"]
    mac=logs_text["MAC_FULL"]
    browser=logs_text["BROWSER"]
    require(re.search(r"\b934 passed\b",focus),"standalone focused 934 missing")
    require(re.search(r"\b934 passed\b",mac),"Mac full script did not run KB141 focused suite")
    require(re.search(r"\b66,?293 passed, 5 skipped\b",mac),"complete backend suite missing")
    require(re.search(r"111 passed|# pass 111|111/111",mac),"Node suite missing")
    require("PASS KB141 independent math:" in mac,"exact math oracle missing")
    require("PASS KB141: 47 existing editorial cases" in mac,"provenance gate missing")
    require("PDF REHASHED" in mac,"private Mac original PDFKit source not replayed")
    require(re.search(r"\b2 passed\b",browser),"Chrome/Playwright pytest not finished")
    rows=cards.build(); math=oracle.evidence()
    require(rows["new_format_p0_union"]==127 and rows["new_source_locked_legacy_cards"]==47
       and rows["historical_proof_steps"]==538, "historical P0 card count drift")
    require(math["positive_or_boundary_cases"]==12 and math["invalid_premise_cases"]==12,
            "oracle case count drift")
    return {
       "schema":"kb141-mac-logged-evidence/1",
       "run_date":"2026-11-14",
       "test_host":"AUTHORIZED_MACBOOK_AIR_ONLY",
       "remote_base_sha":PARENT,"remote_source_sha":SOURCE,
       "gitHub_runner_can_only_replay_logs_and_source_locks":True,
       "full_mac_exit":0,"browser_mac_exit":0,
       "standalone_focused_passed":934,"backend_passed":66293,"backend_skipped":5,
       "node_passed":111,"browser_pytest_passed":2,
       "mac_private_pdfkit_rehashed":True,
       "new_review_lineage_cards":47,"new_format_p0_coverage":127,
       "historical_p0_denominator":127,"historical_proof_steps_unverified":538,
       "math_conflicts_still_open":10,
       "independent_math_positive":12,"independent_math_negative":12,
       "no_new_math_oracle_steps":35,
       "new_complete_teacher_lessons":0,"earlier_bounded_teacher_lessons":57,
       "official_course_atom_denominators":{x:None for x in cards.TRACKS},
       "human_teacher_approvals":0,"formal_general_proof_certifications":0,
       "student_authoritative_releases":0,"student_free_form_steps_verified":0,
       "logs":logs,
    }

def render(d):
    lines=[
      "# STEM Mentor｜Batch141 Mac真实开发、数学审查及测试交付报告",
      "",
      "本批源于GitHub远端 "+PARENT+"；已同步源提交 "+SOURCE+"。最终证据提交SHA以Draft PR远端为准。",
      "所有源码、审查材料与测试均在授权MacBook Air生成；Tang未使用，Mac主仓未提交修改保持不动。",
      "",
      "## 实际成果与严格数学边界",
      "",
      "- K01/K07：对剩余47个历史P0步骤，把KB29/30已有的数学前提、反例和历史步骤claim/reason逐项SHA-256双重锁定，统一可审查格式。新格式来源卡从80/127到127/127。",
      "- **这47条并不是47条从零推导的完整证明**；KB28/29/30此前已覆盖127/127历史编辑审核草案，迁移仅提升来源完整性、卡片一致性及变更门禁。",
      "- K07：独立SymPy和精确有理数检查12条高风险步骤的12个合法及12个失效输入，共24个有限实例。其他35条本批未增加独立数学Oracle，不夸大验证。",
      "- K09：每张来源卡对历史条件、失效边界、原步骤SHA和旧档案SHA执行回归，并注入伪批准、伪造分母、偷换前提等负例。",
      "- K08：学生端检索继续NO_APPROVED_EVIDENCE，不展示TEACHER_ONLY完整解答。所有教师稿状态REVIEW_PENDING。",
      "- 当前538个旧证明步骤仍未形式认证；10项数学冲突未裁决。七轨正式课标分母UNKNOWN；教师审批0、权威发布0。",
      "- 本批不新增正式深度讲义；此前57份仍为有界教师候审稿，不是正式课程覆盖率。",
      "",
      "## Mac真实测试",
      "",
      "| 测试 | 结果 |",
      "|---|---|",
      "| Batch141独立专项 | 934 passed（同全量运行重复，不累计） |",
      "| Python完整后端 | 66,293 passed · 5 skipped |",
      "| Node | 111 passed |",
      "| 受控Chrome/Playwright | EXIT 0；浏览器pytest 2 passed（不等于真实iPad） |",
      "| Mac原始PDFKit授权课标指纹 | PASS：本地重放，CI只核提交摘要 |",
      "| Batch141独立数学Oracle | 24/24个有限精确实例；非一般证明 |",
      "",
      "## 原始日志/退出码SHA-256（可重复哈希验证）",
      "",
      "| 日志 | Exit | SHA-256 | 字节 |",
      "|---|---:|---|---:|",
    ]
    for tag in ("FOCUSED","MAC_FULL","BROWSER"):
        row=d["logs"][tag]
        lines.append(f"| {row['log_path']} | {row['actual_exit_code']} | {row['sha256']} | {row['byte_count']} |")
    lines += [
      "",
      "日志由Mac实际运行生成，GitHub CI复核日志字节及条件文本，不得声称CI能重做私有PDF重放。",
      "",
      "## 发现、失败与下一批",
      "",
      "- Mac GitHub HTTPS fetch由于低速超时（低于100B/s超过15秒），源码通过GitHub原生Git对象API非强制快进提交；远端Git Blob需逐文件验证SHA。",
      "- K00：按正式课标编号要求逐条拆分、去重与七轨课程分母冻结，仍需原文证据及真实教师裁决。",
      "- K07：优先对47条中本批无独立数学Oracle的35条补量词证明级审核，并继续逐项处理538历史未认证步骤、10个冲突；不可把127张卡等同于证明认证。",
      "- K02–K06：恢复必修到选修的整模块原创深度讲义、题族、错因、提示与近远迁移，继续在K08/K09接入独立教学Agent评价。",
      "- 所有材料继续只供教师候审，学生未获批准的权威检索和自由文本步骤认证保持拒绝。",
      ""
    ]
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser()
    opts=p.add_mutually_exclusive_group(required=True)
    opts.add_argument("--write",action="store_true")
    opts.add_argument("--check",action="store_true")
    mode=p.parse_args()
    data=build();text=render(data)
    if mode.write:
        OUT.write_text(cards.canonical(data),encoding="utf-8")
        REPORT.write_text(text,encoding="utf-8")
    else:
        require(json.loads(OUT.read_text(encoding="utf-8"))==data,"manifest drift")
        require(REPORT.read_text(encoding="utf-8")==text,"execution report drift")
    print("PASS KB141 evidence: 934 focused, 66293 backend, 111 Node, 2 browser, 24 finite math cases")

if __name__=="__main__": main()
