#!/usr/bin/env python3
"""Auditable Mac run logs/exit digests; GitHub offline replay never claims licensed PDF access."""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch144_lessons as author
import build_kb_batch144_crosswalk as cross
import check_kb_batch144_math as math
LOG=ROOT/"docs/evaluation/logs"
OUT=ROOT/"docs/evaluation/KB_BATCH144_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH144_EXECUTION_2026-11-14.md"
PARENT="95d8ea9b1a65d2b05281e97e2be27c113e1908b2"
def demand(ok,label):
    if not ok:raise ValueError("Batch144 proof-of-run: "+label)
def build():
    logs={}
    for label in ("FOCUSED","MAC_FULL","BROWSER"):
        fp=LOG/f"KB_BATCH144_{label}.log";ep=LOG/f"KB_BATCH144_{label}.exit"
        demand(fp.is_file() and ep.is_file(),"missing actual Mac log "+label)
        demand(ep.read_text().strip()=="0","nonzero run exit "+label)
        raw=fp.read_bytes()
        demand(len(raw)>200,"truncated Mac log "+label)
        logs[label]=dict(path=str(fp.relative_to(ROOT)),exit_path=str(ep.relative_to(ROOT)),
            bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
            exit_sha256=hashlib.sha256(ep.read_bytes()).hexdigest(),exit=0)
    focused=(ROOT/logs["FOCUSED"]["path"]).read_text(encoding="utf-8",errors="replace")
    full=(ROOT/logs["MAC_FULL"]["path"]).read_text(encoding="utf-8",errors="replace")
    browser=(ROOT/logs["BROWSER"]["path"]).read_text(encoding="utf-8",errors="replace")
    demand(re.search(r"\b227 passed\b",focused),"227 focused test passes absent")
    demand("PASS Batch144: 10 seven-track source-hashed teacher lessons" in full,"new lessons Mac source fingerprint check missing")
    demand("PDF REHASHED original lines PASS" in full,"original PDFKit source-line replay absent")
    demand("PASS Batch144 40/40 independent" in full,"independent math checks absent")
    demand("PASS Batch144 source crosswalk" in full,"seven-track coverage audit absent")
    demand(re.search(r"\b66,?293 passed, 5 skipped\b",full),"full backend Python suite absent")
    demand(re.search(r"\b111 passed|# pass 111|111/111",full),"full Node suite absent")
    demand(re.search(r"\b2 passed\b",browser),"Chrome/Playwright browser pytest absent")
    rows=author.build();deep=author.audit(rows)
    gap=cross.build();oracle=math.oracle()
    demand(deep["total_teacher_only_drafts"]==75 and deep["new_original_manuscripts"]==10,"draft inventory count drift")
    demand(gap["historical_editorial_candidates"]==239 and
           gap["candidate_to_draft_matches"]==34 and
           gap["candidates_without_bounded_teacher_draft"]==205,"editorial provenance count drift")
    demand(oracle["total_cases"]==40 and oracle["invalid_precondition_rejections"]==20,"math count drift")
    return dict(schema="kb144-real-mac-evidence/1",run_date="2026-11-14",
       source_parent_remote_commit=PARENT,development_device="AUTHORIZED_MACBOOK_AIR_ONLY",
       original_pdfkit_lines_rehashed_locally=True,
       github_does_not_reopen_licensed_pdf=True,mac_source_text_uploaded=False,
       focused_tests_passed=227,backend_python_passed=66293,backend_python_skipped=5,
       node_tests_passed=111,browser_pytest_passed=2,
       new_deep_teacher_manuscripts=10,teacher_manuscripts_total=75,
       new_teacher_worked_examples=20,new_student_safe_hint_steps=30,
       new_near_far_transfer_tasks=20,independent_exact_finite_math_cases=40,
       mathematical_negative_preconditions_rejected=20,
       historical_editorial_candidate_count=239,linked_candidate_drafts=34,
       candidate_draft_gaps=205,official_atom_denominators={t:None for t in author.TRACKS},
       historical_uncertified_proof_steps=538,unresolved_math_conflicts=10,
       teacher_approved=0,student_authoritative=0,general_formal_proof_certified=0,
       student_free_text_step_verified=0,first_focused_run_failed=11,
       first_focused_run_failed_cause="Legacy manuscripts missing title key in new editor FTS, and overly broad leak test matched a safe boolean key name",
       first_focused_run_fixed=True,logs=logs)
def render(x):
    out=["# STEM Mentor｜Batch144 授权Mac源码、教学内容与真实验收",
      "","全部源码和内容仅在授权Mac独立worktree feat/kb-batch144-seven-track-source-lessons 实作，基于GitHub Batch143远端提交 "+PARENT+"；Tang未使用。",
      "本报告记录原始Mac执行、日志哈希和事实边界；不能用GitHub CI结果代替教师签字。","",
      "## K00/K01/课程关联",
      "- 239个来源候选只是历史编辑线索，不是中国高中数学官方知识原子分母。",
      "- 既有65份加新10份，共75份未审核原创候审讲义；其中34条候选直接匹配，205条尚未关联完整候审稿。",
      "- 必修、选择性必修、选修A–E七轨国家课标原子分母仍UNKNOWN，批准/发布均0。","",
      "## K02–K06 十篇完整新增原创稿",
      "- 必修：向量三角形法则、元素属于与单元素集合、周期与最小正周期。",
      "- 选择性必修：等差通项与恒差条件、圆的标准方程及退化。",
      "- 选修A：子空间闭合；选修B：线性相关非平凡系数；选修C：有效期利率与复利还款；选修D：理想纯音；选修E：机器人坐标变换顺序。",
      "- 20道完整教师例题、30级学生安全提示、20项近/远迁移；逐步推理/反例/错误解法/适用条件和来源指纹均保存。全部REVIEW_PENDING/TEACHER_ONLY。","",
      "## K07/K08/K09 验证、检索与隔离",
      "- 独立40/40有限或符号精确见证：20合法/边界、20失效前提，普适形式认证0。",
      "- 编辑端本地FTS5仅暴露来源ID、课程、候审状态及排序，不作为网络权限鉴别；没有新增学生公开草案搜索接口。",
      "- FastAPI新增 /api/knowledge/kb144-review-coverage 只返回聚合七轨状态，不返回教师例题/答案。学生证据查找仍NO_APPROVED_EVIDENCE。",
      "- 第一轮227项专项发现11项失败：旧65份草案中某些没有title字段引发编辑检索KeyError；一个隐私断言把安全聚合布尔字段名误判泄漏。均修复后重新完整运行227项通过。","",
      "## 授权Mac实际测试",
      "| 检查 | 真实结果 |","|---|---|",
      "| 本批专项pytest | 227 passed；1条第三方弃用警告 |",
      "| 完整Python后端 | 66,293 passed；5 skipped |",
      "| Node | 111 passed |",
      "| Chrome/Playwright | 退出码0；browser pytest 2 passed（不等同实体iPad） |",
      "| 许可课标原始PDFKit行哈希 | 本机重算通过；原文未上传 |",
      "| 独立数学Oracle | 40/40（含20项非法前提） |",
      "注意：专项227项在完整Mac脚本中再次运行，不与全量测试简单叠加。","",
      "## Mac原始日志及哈希",
      "| 日志文件 | exit | SHA256 | bytes |","|---|---:|---|---:|"]
    for label in ("FOCUSED","MAC_FULL","BROWSER"):
        z=x["logs"][label]
        out.append(f'| {z["path"]} | {z["exit"]} | {z["sha256"]} | {z["bytes"]} |')
    out+=["","GitHub CI仅验证已提交的证据数据/日志哈希，不重放Mac本地版权PDF。GitHub远端commit及CI另行核查；不伪报已合并main。","",
      "## 后续关键缺口",
      "- K00继续真实编号要求语义拆分/跨页重复与选学范围审核，冻结各轨官方分母；仍未完成。",
      "- K07历史538条未形式认证证明步骤及10项数学冲突需要实质一般证明与裁决，有限见证不能代替。",
      "- K02–K06沿205个候选缺口铺开整模块稿件；K08推进未见题Agent评测、引用与条件拒答；K09需要真实教师审校/发布门禁。",""]
    return "\n".join(out)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    args=p.parse_args();v=build()
    if args.write:
        OUT.write_text(author.encode(v),encoding="utf-8")
        REPORT.write_text(render(v),encoding="utf-8")
    else:
        demand(json.loads(OUT.read_text(encoding="utf-8"))==v,"manifest bytes/metadata drift")
        demand(REPORT.read_text(encoding="utf-8")==render(v),"report drift")
    print("PASS Batch144 source/hash-proof Mac evidence: focused 227, backend 66293, node 111, browser 2, math 40")
if __name__=="__main__":main()
