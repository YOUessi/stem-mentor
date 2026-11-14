#!/usr/bin/env python3
"""Authentic KB151 Mac execution manifest: SHA-256 of actual log bytes and exits."""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch151_lessons as lessons
import build_kb_batch151_crosswalk as gaps
import check_kb_batch151_math as math
LOG=ROOT/"docs/evaluation/logs"
OUT=ROOT/"docs/evaluation/KB_BATCH151_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH151_EXECUTION_2026-11-14.md"
SOURCE_COMMIT="7f5357d42836ae372faddd9f77fec628cb14be26"
BASE_COMMIT="efd471a"
RUNS={"FOCUSED":0,"NODE":0,"BROWSER":0,"MAC_FULL":0}
def req(ok,msg):
    if not ok:raise ValueError("KB151 archived Mac evidence: "+msg)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def collect(logdir=LOG):
    records={};texts={}
    for label,rc in RUNS.items():
        f=logdir/f"KB_BATCH151_{label}.log";e=logdir/f"KB_BATCH151_{label}.exit"
        req(f.is_file() and e.is_file(),"missing real log/exit "+label)
        raw=f.read_bytes();exitbytes=e.read_bytes()
        req(exitbytes.decode("utf-8").strip()==str(rc),"unexpected exit code "+label)
        req(len(raw)>=400,"truncated log "+label)
        txt=raw.decode("utf-8",errors="replace")
        req("\x00" not in txt,"binary/non-text log "+label)
        records[label]=dict(path=f"docs/evaluation/logs/{f.name}",
            exit_path=f"docs/evaluation/logs/{e.name}",
            bytes=len(raw),sha256=sha(raw),exit=rc,exit_sha256=sha(exitbytes))
        texts[label]=txt
    req(re.search(r"\b256 passed\b",texts["FOCUSED"]),"256 focused tests missing")
    req(re.search(r"# pass 111\b",texts["NODE"]) and "# fail 0" in texts["NODE"],"Node111 not real")
    browser=texts["BROWSER"]
    req("GREEN v0.7 Chrome test: 9 passed" in browser,"Chrome 9 checks missing")
    req(re.search(r"\b2 passed\b",browser),"two browser pytest tests missing")
    req("Chrome browser suite passed" in browser,"browser final script not green")
    full=texts["MAC_FULL"]
    for tag in ("Mac PDFKit source rehash PASS",
                "PASS Batch151: 10 deep teacher manuscripts; 115 REVIEW_PENDING",
                "PASS Batch151 source→draft crosswalk: 74 matched, 165 unmatched",
                "PASS KB151 40/40 finite exact conditions",
                "256 passed"):
        req(tag in full,"full Mac script missing "+tag)
    req(re.search(r"\b66,?293 passed, 5 skipped\b",full),"backend 66293/5 skipped not evidenced")
    req(re.search(r"# pass 111\b",full),"Node 111 not evidenced in Mac full")
    return records
def build(logdir=LOG):
    logs=collect(logdir)
    row=lessons.build();req(lessons.validate(row),"schema invalid")
    audit=lessons.audit(row);cross=gaps.build()
    req(gaps.validate(cross),"crosswalk invalid")
    oracle=math.oracle()
    req(len(row)==10 and audit["total_teacher_only_drafts"]==115,"115 drafts wrong")
    req(cross["matched_editorial_candidates"]==74 and cross["missing_editorial_candidates"]==165,
        "historical candidate counts changed")
    req(oracle["total_cases"]==40 and oracle["invalid_premise_rejections"]==20,
        "exact math witness drift")
    return dict(schema="kb151-mac-original-execution-evidence/1",run_date="2026-11-14",
        source_git_commit=SOURCE_COMMIT,base_git_commit=BASE_COMMIT,
        authorized_device="MACBOOK_AIR_ONLY",source_pdf_private_mac_replay=True,
        new_teacher_review_pending_lessons=10,total_pending_teacher_manuscripts=115,
        new_teacher_worked_examples=20,new_hint_steps=30,new_near_far_tasks=20,
        editorial_source_candidate_total=239,editorial_candidates_linked=74,
        editorial_candidates_unlinked=165,
        official_atom_denominators={tr:None for tr in lessons.TRACKS},
        official_coverage_rate=None,official_census_certified=False,
        finite_exact_math_cases=40,invalid_premise_or_boundary_cases=20,
        general_formal_proofs_certified=0,free_student_steps_certified=0,
        teacher_approved=0,student_authoritative=0,
        historical_unverified_proof_steps=538,historical_math_conflicts_pending=10,
        focused_python_passed=256,node_passed=111,
        full_python_passed=66293,full_python_skipped=5,
        chrome_interaction_checks=9,browser_pytest_passed=2,
        content_validation_passed=True,privacy_guard_passed=True,
        warning="239 editorial leads, 315 numbered source markers and 115 pending drafts are NOT official curriculum atom denominators; finite witnesses are NOT universal proofs.",
        logs=logs)
def render(v):
    lines=["# STEM Mentor KB151｜真实Mac开发、测试、交付证据","",
        "只在MacBook Air独立worktree开发，没有编辑Mac主仓或者使用Tang；该实验未合并main。",
        "原始源码提交 "+SOURCE_COMMIT+"；父提交 "+BASE_COMMIT+"。本报告的测试退出码和日志均来自实际执行。","",
        "## K00与K01：来源和课程分母",
        "课程来源通过Mac私有授权PDFKit逐行SHA定位，不提交原文。十篇讲义对应十条此前未匹配的历史编辑候选。239条是历史编辑线索，不是国家课标知识原子。74条关联候审讲义，165条未关联；另外41篇来自其他历史路径。七轨正式原子分母UNKNOWN。","",
        "## K02–K06：十篇原创完整候审稿",
        "必修：古典概型树状图、非零向量共线判定、余弦定理内积证明；选择性必修：非零公比等比数列、导数符号与单调性；选修A：介值定理；B：偏导数和连续性；C：充分与必要条件；D：节拍同步最小公倍数；E：名义复利和通胀实际购买力（明确标记学校自选示例）。",
        "每篇正式陈述、适用条件、四步论证、负面反例、典型错法及修复、两道教师例题、三级不剧透提示、近远迁移。合计115篇REVIEW_PENDING/TEACHER_ONLY，教师审批和学生权威发布都为0。","",
        "## K07：独立有限数学核验",
        "40/40精确有限验证通过，其中20项适用或边界见证、20项错误前提或泛化拒绝。一般形式证明仍为0；历史538条证明步骤未获一般认证、10项冲突待裁决。","",
        "## K08/K09：教学Agent安全与真实回归",
        "临时SQLite FTS5索引115篇仅限EDITOR_LOCAL预览，检索只返回标识和候审状态；学生查询仍NO_APPROVED_EVIDENCE，外部聚合接口不公开教师解答。最初复制旧索引时出现11项专项失败，已纠正模块引用，最终256 passed；最初失败的原始日志未归档，不冒充原始失败证据。","",
        "| Mac测试项目 | 真实结果 |","|---|---|",
        "| 原始授权PDFKit来源SHA与Schema | PASS（私有PDF不上传） |",
        "| 精确有限数学见证 | 40/40 |",
        "| Batch151 专项pytest | 256 passed；1条第三方弃用警告 |",
        "| 后端Python全量 | 66,293 passed，5 skipped |",
        "| Node | 111 passed |",
        "| Chrome交互 | 9 checks passed |",
        "| 浏览器pytest | 2 passed（模拟，非实体iPad） |",
        "| Mac与browser执行脚本 | EXIT 0 |","",
        "## 原始Mac日志及SHA-256","",
        "| 日志 | 退出码 | 字节 | SHA-256 |","|---|---:|---:|---|"]
    for label,r in sorted(v["logs"].items()):
        lines.append("| "+label+" | "+str(r["exit"])+" | "+str(r["bytes"])+" | "+r["sha256"]+" |")
    lines+=["","每项另有同名.exit文件，退出码原始字节哈希在机器Manifest内。CI复核已归档的日志及确定性检查，不访问Mac私有PDF。","",
        "## 仍未完成的门槛及下一批",
        "K00正式国家课标七轨原子分母和跨页语义去重；165个未匹配历史编辑候选深度稿；538条未获一般认证证明步骤；10项版本数学冲突教师裁决；真实API对比规则基线的未见题、条件拒答、泄漏、时延与成本评估；真实教师批准方可权威发布。",""]
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    args=p.parse_args();data=build()
    if args.write:
        OUT.write_text(lessons.encode(data),encoding="utf-8")
        REPORT.write_text(render(data),encoding="utf-8")
    else:
        req(json.loads(OUT.read_text(encoding="utf-8"))==data,"manifest changed")
        req(REPORT.read_text(encoding="utf-8")==render(data),"report changed")
    print("PASS KB151 immutable 4 Mac log/exit pairs, SHA, draft and math guards")
if __name__=="__main__":main()
