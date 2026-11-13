#!/usr/bin/env python3
"""Byte-verifiable evidence of Mac local execution, not a replacement for running Mac PDFKit."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch143_lessons as lessons
import build_kb_batch143_source_gap as crosswalk
import check_kb_batch143_math as math_oracle
LOG=ROOT/"docs/evaluation/logs"
OUT=ROOT/"docs/evaluation/KB_BATCH143_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH143_EXECUTION_2026-11-14.md"
BASE="09483bc"
def demand(x,message):
    if not x:raise ValueError("Batch143 test evidence: "+message)
def build():
    logs={}
    for label in ("FOCUSED","MAC_FULL","BROWSER"):
        p=LOG/("KB_BATCH143_"+label+".log")
        exit=LOG/("KB_BATCH143_"+label+".exit")
        demand(p.is_file() and exit.is_file(),"missing Mac log or exit "+label)
        demand(exit.read_text(encoding="utf-8").strip()=="0","nonzero exit "+label)
        raw=p.read_bytes()
        demand(len(raw)>250,"truncated original log "+label)
        logs[label]=dict(log_path=str(p.relative_to(ROOT)),exit_path=str(exit.relative_to(ROOT)),
            bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
            exit_sha256=hashlib.sha256(exit.read_bytes()).hexdigest(),exit=0)
    m=(ROOT/logs["MAC_FULL"]["log_path"]).read_text(encoding="utf-8",errors="replace")
    f=(ROOT/logs["FOCUSED"]["log_path"]).read_text(encoding="utf-8",errors="replace")
    b=(ROOT/logs["BROWSER"]["log_path"]).read_text(encoding="utf-8",errors="replace")
    demand(re.search(r"\b508 passed\b",f),"508 independent focused tests missing")
    demand(re.search(r"\b(250|508) passed\b",m),"Mac full missing new deep content checks")
    demand(re.search(r"\b66,?293 passed, 5 skipped\b",m),"full backend suite absent")
    demand(re.search(r"111 passed|# pass 111|111/111",m),"Node suite absent")
    demand("PASS Batch143: 8 rigorous original lessons" in m,"eight authoring source-locked checks absent")
    demand("PASS 32 exact finite cases" in m,"independent exact Oracle absent")
    demand("PDF REHASHED" in m,"Mac original private PDFKit rehash absent")
    demand(re.search(r"\b2 passed\b",b),"browser regression pytest 2 absent")
    rows=lessons.build(); audit=lessons.audit(rows)
    scope=crosswalk.build(); exact=math_oracle.oracle()
    demand(audit["total_teacher_only_drafts"]==65 and audit["new_original_manuscripts"]==8,
          "draft inventory does not reconcile")
    demand(scope["candidate_editorial_denominator"]==239 and
           scope["historical_candidates_without_bounded_full_draft"]==215,"K00 gap count drift")
    demand(exact["total_cases"]==32 and exact["negative_precondition_rejections"]==16,
           "math case count drift")
    return dict(schema="kb143-mac-full-evidence/1",run_date="2026-11-14",
        source_parent_local_sha=BASE,development_device="AUTHORIZED_MACBOOK_AIR_ONLY",
        licensed_source_pdf_rehashed_only_on_mac=True,
        github_can_only_rehash_logs_not_read_private_licensed_pdf=True,
        focused_passed=508,backend_passed=66293,backend_skipped=5,node_passed=111,
        browser_pytest_passed=2,
        new_teacher_only_math_lessons=8,original_teacher_examples=16,
        new_student_hint_stages=24,new_near_far_transfer_tasks=16,
        independent_finite_exact_math_cases=32,positive_cases=16,
        invalid_precondition_cases_rejected=16,
        provisional_editorial_candidates=239,
        candidate_to_teacher_draft_matched=24,candidates_unmatched=215,
        teacher_only_lesson_total=65,official_atom_denominators={t:None for t in lessons.TRACKS},
        teacher_approved=0,student_authoritative=0,formal_general_proofs_certified=0,
        free_student_steps_verified=0,
        historical_uncertified_proof_steps=538,unresolved_math_conflicts=10,
        logs=logs)
def render(d):
    lines=["# STEM Mentor｜Batch143 Mac源码、教学内容与真实测试记录","",
      "本轮在授权 MacBook Air 独立 worktree feat/kb-batch143-cross-track-depth-and-guard 开发。基于上一轮Batch142源码本地SHA "+BASE+"；没有使用 Tang。",
      "GitHub远端最终提交SHA以Draft PR远端HEAD为准，不能用本地运行日志冒充远端CI通过。","",
      "## K00/K01：来源与官方覆盖的事实边界","",
      "- 建立239个历史编辑来源候选与65份有限教师候审稿的机器交叉索引：24个直接关联；215个历史编辑候选未有对应完整候审稿，另有41份候审稿来自其他编辑来源路径。",
      "- 每条候选保留证据等级、原文SHA256、课程轨道、缺口ID及REVIEW_PENDING。标题锚点、编号线索、选学示例绝不擅自转成官方原子。",
      "- 必修/选择性必修/选修A–E全部7条正式课标原子分母仍UNKNOWN；教师批准0、学生权威发布0。","",
      "## K02–K06：新增八篇完整原创候审教学稿","",
      "- 必修（4）：全称命题的否定与反例、奇偶性和对称定义域、正弦定理与SSA歧义、事件并集容斥与重叠。",
      "- 选择性必修（2）：直线斜率及竖直退化、超几何分布不放回抽样。",
      "- 选修A（1）：克拉默法则及奇异系数矩阵；选修D（1）：理想十二平均律的半音频率比。",
      "- 合计16道教师完整例题、8×3级不泄答案提示、16项近/远迁移；各稿含陈述、定义域、条件、逐步理由、失效反例和典型错解。",
      "- 原始课标仅在Mac通过PDFKit行SHA256重放，无版权课标全文入库。全部TEACHER_ONLY/REVIEW_PENDING，没有格式完整即自动审校。","",
      "## K07/K08/K09：数学独立验证与检索隔离","",
      "- SymPy和可完全穷举的小有限模型独立验算32个见证：16合法/边界、16失效条件拒绝；有限样本不能代替一般证明。",
      "- FTS5现可在Mac本地编辑预览检索65份草案，只暴露ID、轨道和复核状态；学生权威证据默认NO_APPROVED_EVIDENCE。",
      "- FastAPI仅发布七轨聚合计数和UNKNOWN分母，不新增任何未授权的教师完整解答、草案搜索路由。","",
      "## 本批真实Mac测试","",
      "| 测试 | 真实结果 |","|---|---|",
      "| 新增专项（独立执行） | 508 passed；与完整测试可能重叠，不重复累计 |",
      "| Python全量后端 | 66,293 passed；5 skipped |",
      "| Node | 111 passed |",
      "| Chrome/Playwright浏览器回归 | EXIT 0，browser pytest 2 passed（非实体iPad） |",
      "| Mac私有PDFKit来源行SHA | 8新增来源指纹重放PASS；全量PDF检查见Mac全量日志 |",
      "| 独立有限数学Oracle | 32/32，含16项非法前提拒绝，正式证明证书0 |","",
      "## 原始日志与文件摘要","",
      "| Mac原始日志 | 退出码 | SHA256 | 字节数 |",
      "|---|---:|---|---:|"]
    for label in ("FOCUSED","MAC_FULL","BROWSER"):
        r=d["logs"][label]
        lines.append(f'| {r["log_path"]} | {r["exit"]} | {r["sha256"]} | {r["bytes"]} |')
    lines+=["",
      "GitHub CI可以对这些归档日志、退出码与SHA256重放，不代表能在CI读取授权Mac的版权课标PDF；原始文本未上传。",
      "本轮沿用的Batch142日志均由同一授权Mac早一轮实际执行，按原始字节读取并保留对应执行报告，不伪称是Batch143重新执行。","",
      "## 发现与后续批次","",
      "- 首轮增量测试508项有1项失败，原因是机器可审计七轨JSON序列化后字典顺序不同导致Markdown报告渲染顺序漂移；改为按固定TRACKS轨道序列渲染，重新实跑508 passed。",
      "- K00正式七轨原子分母仍未完成，下一步要对真实编号条款按语义原子拆解、跨页去重并由人工审核，而不是将239个编辑候选当分母。",
      "- K07仍有历史538条未认证证明步骤、10项冲突，需转向一般条件证明而不只是有限案例。",
      "- K02–K06继续模块化扩写目前215个未匹配历史编辑候选；提高完整讲义/题族深度，再对K08接入未见题引用、先修门禁和真实Agent评测。",
      "- 真实教师审批前一切保持REVIEW_PENDING，不对学生正式发布。",""]
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser()
    a=p.add_mutually_exclusive_group(required=True)
    a.add_argument("--write",action="store_true")
    a.add_argument("--check",action="store_true")
    args=p.parse_args()
    data=build()
    if args.write:
        OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        REPORT.write_text(render(data),encoding="utf-8")
    else:
        demand(json.loads(OUT.read_text(encoding="utf-8"))==data,"manifest changed")
        demand(REPORT.read_text(encoding="utf-8")==render(data),"report changed")
    print("PASS KB143 Mac evidence: 508 focused, 66293 backend, 111 Node, 2 browser; 32 finite math cases")
if __name__=="__main__":main()
