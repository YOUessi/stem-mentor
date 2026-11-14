#!/usr/bin/env python3
"""Hash-lock actual Mac test logs and exits; CI replays without licensed PDF."""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch148_official_clause_gate as k00
import review_kb_batch148_conflicts as k07
LOG=ROOT/"docs/evaluation/logs"
OUT=ROOT/"docs/evaluation/KB_BATCH148_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH148_EXECUTION_2026-11-14.md"
PARENT_SHA="92bcf91aa401bb4cf5f9722963319bce7874ac43"
SOURCE_SHA="d2a6cf7befcfeef87cff72782e16a867784430bc"
NAMES=("FOCUSED","MAC_FULL","BROWSER")
def req(ok,msg):
    if not ok:raise ValueError("Batch148 archived Mac evidence: "+msg)
def encode(v):return json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
def collect(logdir=LOG):
    meta={};texts={}
    for n in NAMES:
        f=logdir/("KB_BATCH148_"+n+".log");e=logdir/("KB_BATCH148_"+n+".exit")
        req(f.is_file() and e.is_file(),"missing original log/exit "+n)
        req(e.read_text(encoding="utf-8").strip()=="0","nonzero exit "+n)
        raw=f.read_bytes();req(len(raw)>500,"truncated log "+n)
        texts[n]=raw.decode("utf-8",errors="replace")
        meta[n]=dict(path="docs/evaluation/logs/"+f.name,
                     exit_path="docs/evaluation/logs/"+e.name,
                     bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
                     exit=0,exit_sha256=hashlib.sha256(e.read_bytes()).hexdigest())
    req(re.search(r"\b730 passed\b",texts["FOCUSED"]),"no focused 730 summary")
    full=texts["MAC_FULL"];browser=texts["BROWSER"]
    for tag in ("PDF REHASHED original lines PASS",
                "PASS K00 Batch148: 315 numbered anchors/61 source pages",
                "PASS K07 Batch148: 10 source conflicts","730 passed"):
        req(tag in full,"full Mac missing "+tag)
    req(re.search(r"\b66,?293 passed, 5 skipped\b",full),"backend 66293/5 result missing")
    req(re.search(r"(\b111 passed\b|# pass 111|111/111)",full),"Node 111 missing")
    req("GREEN v0.7 Chrome test: 9 passed" in browser,"Chrome 9 missing")
    req(re.search(r"\b2 passed\b",browser),"browser pytest 2 missing")
    return meta
def build(logdir=LOG):
    logs=collect(logdir);c=k00.build();m=k07.build()
    k00.validate_report(c);k07.validate(m)
    req(c["source_numbered_marker_count"]==315 and
        c["provisional_atom_proposal_count"]==41 and
        c["historical_editorial_leads"]==239 and
        c["teacher_pending_manuscripts"]==95 and
        c["relation_edges_pending"]==89,"K00 inventory drift")
    req(m["independent_exact_cases"]==40 and m["conflicts_total"]==10 and
        m["math_conflicts_human_resolved"]==0,"K07 math adjudication drift")
    return dict(schema="kb148-real-authorized-mac-execution-v1",run_date="2026-11-14",
      device="AUTHORIZED_YOUTANG_MACBOOK_AIR_ONLY",base_git_commit=PARENT_SHA,
      source_git_commit=SOURCE_SHA,private_pdf_stays_mac_only=True,
      original_pdfkit_replay_passed=True,github_can_replay_private_pdf=False,
      numbered_source_markers=315,official_source_scan_pages=61,
      editorial_atom_proposals=41,historical_editorial_leads=239,
      editorial_leads_with_drafts=54,editorial_leads_missing_drafts=185,
      teacher_pending_manuscripts=95,new_deep_manuscripts=0,
      source_boundary_relation_records_pending=89,
      official_atom_denominators={t:None for t in k00.TRACKS},
      official_atomic_census_complete=False,teacher_approved=0,
      student_authoritative=0,historical_uncertified_general_proof_steps=538,
      unresolved_version_conflicts=10,math_finite_oracles_passed=40,
      new_negative_or_invalid_math_cases=20,general_proof_certificates=0,
      free_student_steps_certified=0,focused_python_passed=730,
      full_backend_python_passed=66293,full_backend_python_skipped=5,
      node_passed=111,chrome_interaction_passed=9,browser_pytest_passed=2,
      initial_failures_not_archived=[
       "K00 counted-track dictionary comparison mismatched absent zero-track keys; corrected",
       "K07 line distance test wrongly chose (3,4) on 3x+4y-5=0; corrected to (3,-1)",
       "SymPy Piecewise directional limit did not follow branch as expected; used exact branch evaluation"
      ],logs=logs)
def render(v):
    lines=[
     "# STEM Mentor Batch148｜真实Mac数学课标与证明冲突验收","",
     "仅授权MacBook Air独立worktree修改/测试；未使用Tang；未合并或强推main，也未改动原主仓未提交文件。","",
     "来源提交："+PARENT_SHA+"；本批源码提交："+SOURCE_SHA+"。","",
     "## K00/K01 全范围来源级审计","",
     "对国家2017版2020修订数学课标61个印刷页(13–73)的315个编号标记建立逐行哈希审计，关联41个原子编辑提案、239个历史线索与95份教师候审讲义。",
     "315个编号标记、41个提案、239个线索和95份草案是不同统计实体；不能相互替代，更不是正式知识原子分母。",
     "239历史线索中54已关联候审稿，185未关联；89条跨页/同页来源关系仍要教师语义裁决。全部7轨正式原子分母仍UNKNOWN；未编号课程要求、选修D/E和跨页句子未完整核定。",
     "机器拒绝丢失编号、篡改PDF/行哈希、伪造批准和悬空先修。许可PDF原文仅Mac保存，不上传。","",
     "## K07十项实际冲突数学见证","",
     "覆盖复合函数定义域、奇偶、分段函数、介值定理、点线距离、二项分布、超几何、回归、三角形面积、向量线性运算。",
     "每个冲突有4项SymPy/精确有限验证（合法、边界、无效前提、错误泛化）；共40/40通过，其中20项为前提/错误反例。",
     "每例保存两版源SHA和独立中文解释，但10项版本冲突全部仍未裁决；538项历史证明步骤仍未得到一般形式认证。","",
     "## K08/K09安全接口与真实测试","",
     "新增GET /api/knowledge/kb148-curriculum-evidence-status，仅暴露七轨数量、审核状态和数学冲突统计，不暴露版权原文/未审讲义/教师解答。学生端仍NO_APPROVED_EVIDENCE。",
     "本批专项730项测试覆盖所有315编号、61页、239来源线索、41原子提案、40数学Oracle和虚假权限/来源及答案泄露负面回归。未新增深度讲义（0份）；累计95份皆TEACHER_ONLY/REVIEW_PENDING。",
     "初始修复三项问题：K00零计数轨道对照、点线距离选错边界点、SymPy Piecewise单侧极限。初始失败仅在控制台显示，原始失败日志未保存，不冒充已归档失败证据。","",
     "| Mac真实验收 | 结果 |","|---|---|",
     "| 许可课标原始PDFKit来源重放 | PASS，188页原始清单与61页行哈希 |",
     "| K00机器审计 | PASS，315标记/61页，官方分母UNKNOWN |",
     "| K07精确数学见证 | 40/40 PASS，10冲突依然待人工裁决 |",
     "| 增量pytest | 730 passed（1条第三方弃用警告） |",
     "| 完整Python后端 | 66,293 passed，5 skipped |",
     "| Node | 111 passed |",
     "| Chrome交互与浏览器pytest | 9 passed / 2 passed（非实体iPad） |",
     "| Mac与浏览器脚本退出码 | 0 / 0 |","",
     "## 原始日志、退出码及SHA-256","",
     "| 日志 | exit | SHA-256 | bytes |","|---|---:|---|---:|"]
    for n in NAMES:
        p=v["logs"][n];lines.append("| "+p["path"]+" | 0 | "+p["sha256"]+" | "+str(p["bytes"])+" |")
    lines+=["","各日志有同名.exit退出码，SHA-256也在JSON清单。GitHub CI只能重播已提交日志内容与哈希，不能重新读取Mac许可PDF。","",
        "## 下一批","",
        "逐条拆分课标编号与未编号内容、裁决跨页语义重复，建立真实可审核的七轨正式原子分母；沿185条历史缺稿线索补充整模块原创讲义。",
        "真实裁决10个冲突，解决538项一般形式认证债务，扩展教学Agent未见题检索/条件拒答评估与教师审核签核。","",
        "教师批准0，学生权威发布0；尚未达到完整课程及上线验收门槛。",""]
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    a=p.parse_args();v=build()
    if a.write:
        OUT.write_text(encode(v),encoding="utf-8")
        REPORT.write_text(render(v),encoding="utf-8")
    else:
        req(json.loads(OUT.read_text(encoding="utf-8"))==v,"manifest drift")
        req(REPORT.read_text(encoding="utf-8")==render(v),"human report drift")
    print("PASS Batch148 immutable Mac tests: 730 focused, 66293 backend, 111 Node, 9 Chrome, 2 browser, 40 math")
if __name__=="__main__":main()
