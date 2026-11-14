#!/usr/bin/env python3
"""Replay *archived* authorized Mac execution evidence from committed logs.

GitHub's runner cannot access licensed local PDFKit source and must not claim
to have rerun Mac-only checks. This script verifies byte digests/exits and
the test summaries that the executing Mac recorded.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch146_lessons as author
import build_kb_batch146_crosswalk as census
import check_kb_batch146_math as math
import audit_kb_batch146_source_aliases as aliases
LOG=ROOT/"docs/evaluation/logs"
OUT=ROOT/"docs/evaluation/KB_BATCH146_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH146_EXECUTION_2026-11-14.md"
PARENT="c07c2d0a45dccb01319f5b594539d28cf0355782"
SOURCE_COMMIT="d3ea06ec07b723fcda8196f83237442f189e53c7"
def required(p,msg):
    if not p:raise ValueError("KB146 archived Mac evidence: "+msg)
def collected():
    result={}
    for label in ("FOCUSED","K00_FOCUSED","MAC_FULL","BROWSER"):
        fp=LOG/f"KB_BATCH146_{label}.log"
        ep=LOG/f"KB_BATCH146_{label}.exit"
        required(fp.is_file() and ep.is_file(),f"missing {label} log/exit")
        required(ep.read_text().strip()=="0",f"{label} Mac run failed")
        log=fp.read_bytes()
        required(len(log) >= (50 if label == "K00_FOCUSED" else 200), f"truncated {label} log")
        result[label]=dict(path=f"docs/evaluation/logs/{fp.name}",exit_path=f"docs/evaluation/logs/{ep.name}",
            bytes=len(log),sha256=hashlib.sha256(log).hexdigest(),
            exit_sha256=hashlib.sha256(ep.read_bytes()).hexdigest(),exit=0)
    return result
def build():
    logs=collected()
    txt={name:(LOG/f"KB_BATCH146_{name}.log").read_text(encoding="utf-8",errors="replace") for name in logs}
    focused,full,browser=(txt[x] for x in ("FOCUSED","MAC_FULL","BROWSER"))
    required(re.search(r"\b266 passed\b",focused),"focused 266 PASS absent")
    required(re.search(r"\b44 passed\b",txt["K00_FOCUSED"]),"K00 alias 44 PASS absent")
    required("PDF REHASHED original lines PASS" in full,"licensed original PDFKit SHA replay missing")
    required("PASS Batch146: 10 seven-track source-hashed teacher lessons" in full,"Mac lesson check missing")
    required("PASS Batch146 40 exact finite cases" in full,"Mac independent 40 case oracle missing")
    required("PASS Batch146 source crosswalk" in full,"seven-track source ledger missing")
    required(re.search(r"\b266 passed\b",full),"Mac scripted focused 266 PASS missing")
    required(re.search(r"\b66,?293 passed, 5 skipped\b",full),"full Python 66293/5 missing")
    required(re.search(r"\b111 passed|# pass 111|111/111",full),"Node 111 PASS missing")
    required(re.search(r"\b2 passed\b",browser),"browser pytest 2 PASS missing")
    source_alias=aliases.audit()
    required(source_alias["shared_source_span_group_count"]==7 and source_alias["candidate_count_in_shared_source_span_groups"]==19 and source_alias["shared_cue_group_count"]==17,"K00 source alias queue drift")
    draft=author.audit(author.build())
    cross=census.build()
    witness=math.oracle()
    required(draft["total_teacher_only_drafts"]==85,"draft inventory 85 drift")
    required(cross["historical_editorial_candidates"]==239 and cross["candidate_to_draft_matches"]==44
        and cross["candidates_without_bounded_teacher_draft"]==195,"historical provenance drift")
    required(witness["total_cases"]==40 and witness["rejected_invalid_premises"]==20,"math oracle drift")
    return dict(schema="kb146-real-mac-evidence/1",run_date="2026-11-14",
        development_device="AUTHORIZED_MACBOOK_AIR_ONLY",source_base_commit=PARENT,
        source_feature_commit=SOURCE_COMMIT,
        mac_original_pdfkit_lines_rehashed_locally=True,github_cannot_rehash_licensed_pdf=True,
        copyrighted_standard_pdf_uploaded=False,
        focused_tests_passed=266,k00_alias_focused_tests_passed=44,backend_python_passed=66293,backend_python_skipped=5,
        node_tests_passed=111,browser_pytest_passed=2,
        deep_teacher_manuscripts_added=10,deep_teacher_manuscripts_total=85,
        new_teacher_worked_examples=20,new_student_hint_steps=30,
        new_near_and_far_transfer_tasks=20,independent_bounded_exact_math_cases=40,
        invalid_math_premises_rejected=20,
        historical_editorial_candidate_count=239,shared_source_span_groups=7,shared_span_candidate_memberships=19,shared_layout_cue_groups=17,cross_page_shared_cue_groups=source_alias["cross_page_shared_cue_group_count"],source_aliases_auto_merged=0,linked_to_draft=44,
        unmatched_editorial_candidates=195,official_atom_denominators={t:None for t in author.TRACKS},
        teacher_approvals=0,student_authoritative_publications=0,
        general_formal_proof_certifications=0,free_student_text_steps_verified=0,
        first_negative_test_run_failed=10,
        first_failure_raw_log_archived=False,
        first_failure_root_cause="source_pdf_sha256 was not checked inside schema validator; original PDF SHA lock now mandatory",
        first_failure_repaired_and_266_tests_passed=True,
        historical_general_proof_certification_gap=538,unresolved_historical_math_conflicts=10,
        logs=logs)
def report(x):
    out=["# STEM Mentor｜Batch146 真实Mac开发、数学内容、源码与验收记录","",
       "仅授权MacBook Air参与知识库源码、数学内容与测试。独立 worktree：",
       "`~/Documents/文件/stem-mentor-kb-batch146`，分支 `feat/kb-batch146-rigorous-math-cases`。",
       "基于已核实GitHub Batch144 commit `"+PARENT+"`；本批源码commit `"+SOURCE_COMMIT+"`。",
       "主仓原有未提交修改、其他worktree未覆盖；Tang未参与开发。","",
       "## K00/K01 来源与真实覆盖边界",
       "- 私有原始课标PDFKit来源行在Mac重新哈希，与提交的来源位置和SHA-256一致；版权原文未入库。",
       "- 239是**历史编辑课程线索**而非国家课标知识原子分母：44条关联稿，195条缺完整候审稿。",
       "- K00别名专项审计：7个同页同源段组牵涉19条候选，17个共享版式cue组、其中跨页共用cue为0组；该0不代表完成跨页语义核对；全部保留人工裁决，自动合并为0。",
       "- 原有75份加新增10份共85份原创教师候审稿，选修E内容明确是学校选修示例。",
       "- 必修、选择性必修及选修A–E的真正官方原子分母全部 UNKNOWN；正式教师批准0、学生权威发布0。","",
       "## K02–K06 十份真实原创内容",
       "- 必修：复数代数形式相等与实虚部；二分法保留异号区间；弧度与圆弧长度。",
       "- 选择性必修：数学归纳法；有序排列与无序组合。",
       "- 选修A：拉格朗日中值定理；选修B：连续概率密度；选修C：相容性和完备性。",
       "- 选修D：黄金分割精确比与斐波那契近似；选修E：学校自主选修的整数同余。",
       "- 每单元严格保留适用域和假设、分步依据、错误用法/反例、20道完整教师例题、30层安全提示、20个近远迁移任务。均REVIEW_PENDING/TEACHER_ONLY。","",
       "## K07/K08/K09 数学与权限核验",
       "- 独立SymPy有限/精确样例40/40：20合法/边界见证，20无效前提拒绝。有限见证并非全称命题形式证明。",
       "- 本地编辑FTS5临时索引包含85份稿件但检索结果只列ID/轨道/状态/排名，不能作网络授权凭证；学生未批准证据一律拒答。",
       "- FastAPI `/api/knowledge/kb146-review-coverage`只返回七轨聚合及UNKNOWN分母，无教师解答。",
       "- 首轮266项负面回归出现10项失败：source PDF SHA字段可被篡改而没有被validator拒绝。首次失败的原始日志未归档，此数字为当时调试记录；已补充原始PDF SHA强制验证，复跑266项成功的日志已归档。",
       "- 仍有历史538个未认证证明步骤、10项未裁决数学冲突；自动批准/发布一律为0。","",
       "## 授权Mac真实测试",
       "| 项目 | 结果 |","|---|---|",
       "| 独立本批专项 | 266 passed（1条Starlette第三方弃用警告） |",
       "| K00来源重复片段专项 | 44 passed，7组共同原文段仍待语义裁决 |",
       "| 已归档日志防篡改回归 | 5 passed，覆盖退出码、日志缺失、假通过数字、PDF重放假标记 |",
       "| 脚本内专项 | 266 passed；与独立专项重复，不累计 |",
       "| 全量后端Python | 66,293 passed，5 skipped |",
       "| Node | 111 passed |",
       "| Chrome/Playwright + browser pytest | exit 0，2 passed；不是实体iPad验证 |",
       "| 原始Mac私有PDFKit逐行SHA | PASS，未上传PDF原文 |",
       "| 数学独立Oracle | 40/40；不等于普适形式认证 |","",
       "## 真实执行日志与字节哈希",
       "| 日志 | exit | SHA256 | bytes |","|---|---:|---|---:|"]
    for label in ("FOCUSED","K00_FOCUSED","MAC_FULL","BROWSER"):
        item=x["logs"][label]
        out.append(f'| `{item["path"]}` | {item["exit"]} | `{item["sha256"]}` | {item["bytes"]} |')
    out.extend(["",
       "GitHub Actions只能检查**提交的日志哈希和Schema/数学CI**，不能冒充重放Mac独有的授权PDF。最终GitHub Actions是否通过须单独查看对应commit和workflow。","",
       "## 下一批",
       "- K00：真实编号要求的原子拆分、相邻页去重、课程内容与选修边界审计，争取冻结可追溯的七轨分母。",
       "- K02–K06：对195条仍无候审深度稿的编辑线索继续逐模块补内容，同时防止误将线索直接当官方知识点。",
       "- K07：538历史未形式认证步骤与10冲突的真实数学裁决；K08未见题检索/拒答；K09教师审签与发布门禁。",""])
    return "\n".join(out)
def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check",action="store_true")
    args=p.parse_args()
    data=build()
    if args.write:
        OUT.write_text(author.encode(data),encoding="utf-8")
        REPORT.write_text(report(data),encoding="utf-8")
    else:
        required(json.loads(OUT.read_text(encoding="utf-8"))==data,"manifest changed")
        required(REPORT.read_text(encoding="utf-8")==report(data),"report changed")
    print("PASS Batch146 archived actual Mac evidence: 266 math focused, 44 K00 focused, 66293 backend, 111 node, 2 browser, 40 bounded math")
if __name__=="__main__":main()
