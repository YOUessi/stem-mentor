#!/usr/bin/env python3
"""SHA-locked original Mac test logs, exit codes and source status; offline CI replay."""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch149_lessons as lessons
import build_kb_batch149_crosswalk as gaps
import build_kb_batch149_unnumbered_elective_queue as de
import check_kb_batch149_math as exact
LOG=ROOT/"docs/evaluation/logs"
OUT=ROOT/"docs/evaluation/KB_BATCH149_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH149_EXECUTION_2026-11-14.md"
PARENT_SHA="7372df46fee75c5be74f7009e3af17355c038874"
SOURCE_SHA="e10d1227ac3d36b7b4b251fad287e48fe5a45be7"
RUNS={"FOCUSED_INITIAL_FAILURE":1,"FOCUSED":0,"MAC_FULL":0,"BROWSER":0}
def req(cond,msg):
    if not cond:raise ValueError("Batch149 real Mac evidence: "+msg)
def sha(data):return hashlib.sha256(data).hexdigest()
def collect(logdir=LOG):
    records={};texts={}
    for label,expected in RUNS.items():
        path=logdir/f"KB_BATCH149_{label}.log"
        ex=logdir/f"KB_BATCH149_{label}.exit"
        req(path.is_file() and ex.is_file(),label+" original log/exit absent")
        raw=path.read_bytes();exit_bytes=ex.read_bytes()
        req(exit_bytes.decode("utf-8").strip()==str(expected),label+" exit code mismatch")
        req(len(raw)>=(300 if label=="BROWSER" else 750),label+" original log too short")
        texts[label]=raw.decode("utf-8",errors="replace")
        records[label]=dict(path=f"docs/evaluation/logs/{path.name}",
            exit_path=f"docs/evaluation/logs/{ex.name}",
            bytes=len(raw),sha256=sha(raw),exit=expected,exit_sha256=sha(exit_bytes))
    req("1 failed, 404 passed" in texts["FOCUSED_INITIAL_FAILURE"],"actual initial failing test missing")
    req(re.search(r"\b405 passed\b",texts["FOCUSED"]),"405 passing focused tests missing")
    full=texts["MAC_FULL"];browser=texts["BROWSER"]
    for required in ("Mac PDFKit source rehash PASS","PASS Batch149: 10 deep teacher manuscripts",
        "PASS Batch149 40/40 exact limited witnesses",
        "PASS Batch149 unnumbered D/E source-line SHA queue",
        "PASS Batch149 source→draft crosswalk","405 passed"):
        req(required in full,"Mac full execution missing "+required)
    req(re.search(r"\b66,?293 passed, 5 skipped\b",full),"full backend Python count missing")
    req(re.search(r"\b111 passed\b|# pass 111|111/111",full),"Node test count missing")
    req("GREEN v0.7 Chrome test: 9 passed" in browser,"Chrome 9 checks absent")
    req(re.search(r"\b2 passed\b",browser),"browser pytest result absent")
    req("Chrome browser suite passed" in browser,"browser script success absent")
    return records
def build(logdir=LOG):
    logs=collect(logdir)
    audit=lessons.audit(lessons.build())
    census=gaps.build()
    source=json.loads(de.OUT.read_text(encoding="utf-8"))
    oracle=exact.oracle()
    req(lessons.validate(lessons.build()) and gaps.validate(census) and de.validate(source),"source audit drift")
    req(audit["total_teacher_only_drafts"]==105 and audit["added_original_manuscripts"]==10,
        "105 deep manuscript inventory drift")
    req(census["matched_editorial_candidates"]==64 and census["missing_editorial_candidates"]==175,
        "239 candidate crosswalk drift")
    req(source["nonempty_source_lines"]==122 and source["pages_scanned"]==5 and
        len(source["crosspage_seams"])==4,"D/E source review drift")
    req(oracle["total_cases"]==40 and oracle["invalid_premise_rejections"]==20,
        "independent math cases drift")
    return dict(schema="kb149-real-mac-execution-evidence/1",run_date="2026-11-14",
        authorized_device="MACBOOK_AIR_ONLY",source_git_commit=SOURCE_SHA,base_git_commit=PARENT_SHA,
        private_pdf_replayed_only_on_mac=True,private_pdf_unavailable_to_github_ci=True,
        source_de_printed_pages=5,source_de_nonempty_lines=122,source_de_pending_crosspage_seams=4,
        total_pending_teacher_drafts=105,new_deep_teacher_drafts=10,
        teacher_examples=20,hint_steps=30,near_far_transfer_tasks=20,
        editorial_candidates_total=239,editorial_candidates_matched=64,
        editorial_candidates_missing=175,
        official_atom_denominators={t:None for t in lessons.TRACKS},
        full_official_census_completed=False,
        independent_exact_math_witnesses=40,invalid_or_counterexample_witnesses=20,
        unverified_general_historical_proof_steps=538,unresolved_math_conflicts=10,
        general_formal_certifications=0,student_free_text_certifications=0,
        teacher_approved=0,student_authoritative=0,
        initial_focused_passed=404,initial_focused_failed=1,
        final_focused_passed=405,full_backend_python_passed=66293,
        full_backend_python_skipped=5,node_passed=111,
        chrome_interaction_passed=9,browser_pytest_passed=2,
        warning="Finite witnesses, original source lines and historical editorial candidates are NOT complete official atom denominators.",
        logs=logs)
def render(v):
    rows=[
    "# STEM Mentor Batch149｜真实Mac执行与GitHub审查证据","",
    "全部开发与测试在授权MacBook Air独立工作树完成；原主仓和Tang未改动，未强推、未合并main。","",
    "上游源码SHA: "+PARENT_SHA+"。本批源码SHA: "+SOURCE_SHA+"。真实失败及修复日志均保留原始字节与退出码。","",
    "## K00/K01：课程原子范围与Schema",
    "原始2017/2020课标印刷页69–73：122条PDFKit非空来源行的逐行SHA-256及4个跨页衔接待审队列。包括标题与说明，绝不能算作122个知识原子；第73页D/E分界保留语义待审状态。七轨正式原子分母全部UNKNOWN，版权原文不上传。","",
    "## K02–K06：10份原创完整教师候审稿",
    "必修：古典概型、分层随机抽样、一元二次不等式；选择性必修：条件概率和独立、贝叶斯/全概率；选修A：收敛数列有界性证明；选修B：二元函数定义域；选修C：直接/反证法；选修D：对称与平移；选修E：球面大圆最短路（学校选修示例）。",
    "每稿正式陈述、适用域、前提、合法性、4个分步论证、反例错因、两道带解教师例题、3级不泄答案学生提示、近远迁移。新增20题教师例题、30级提示、20项迁移。全部REVIEW_PENDING/TEACHER_ONLY。",
    "共105份教师候审稿；239条历史编辑候选中64条有关联完整稿，175条未关联；另41篇稿件来自其他历史路径。绝不把这个统计冒充国家课标完成率。","",
    "## K07：独立数学验证",
    "10个主题各4项有限SymPy/有理数精确核验：40/40（20项合法/边界、20项失效前提/错误泛化）。538条历史证明步骤仍未获得一般证明认证，10项数学版本冲突仍待实质裁决；有限例子不等于形式证明。","",
    "## K08：Agent与隐私边界",
    "105份教师候审草案已进入Mac本地只读编辑预览SQLite FTS5，不向学生提供检索接口。新GET /api/knowledge/kb149-review-coverage仅返回数量，学生证据统一NO_APPROVED_EVIDENCE；教师答案和受版权保护的课标原文未公开。","",
    "## K09：真实回归与失败修复",
    "专项第一次404通过、1失败：报告按字母序反序列化by_track，渲染却按七轨预定义顺序，两个输出不一致。修复为显式按课程轨道顺序生成表格后，重跑405全部通过；原始失败日志与非零退出码仍版本化。","",
    "| 实际测试 | 结果 |","|---|---|",
    "| Mac原始PDFKit来源SHA | PASS，5页122条非空原文来源行（不上传文字） |",
    "| 数学独立有限Oracle | 40/40（20合法，20负面） |",
    "| KB149专项 | 初次404通过/1失败；修复后405通过 |",
    "| 后端完整Python | 66,293通过，5跳过 |",
    "| Node | 111通过 |",
    "| Chrome交互与浏览器pytest | 9通过、2通过（模拟非实体iPad） |",
    "| Mac及Browser脚本 | 均EXIT 0 |","",
    "### 原始Mac日志、真实退出码、SHA-256","",
    "| 日志 | 退出码 | 字节 | SHA-256 |","|---|---:|---:|---|"]
    for label in RUNS:
        d=v["logs"][label]
        rows.append(f'| {label} | {d["exit"]} | {d["bytes"]} | {d["sha256"]} |')
    rows.extend(["","每项另有同名.exit原始退出码文件，字节哈希列在机器可读JSON。CI只能验证已归档日志及确定性数学和审核门禁，不能访问Mac私有PDF。","",
      "## 待完成",
      "七轨正式原子分母仍UNKNOWN，教师批准0、学生权威发布0。尚须对122条来源行逐句人工判定、全61页未编号和跨页语义去重，补齐175条历史编辑来源缺稿，裁决10项版本冲突、538条未一般认证证明，并开展真实Agent未见题基准。",""])
    return "\n".join(rows).rstrip("\n")+"\n"
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    a=p.parse_args();v=build()
    if a.write:
        OUT.write_text(lessons.encode(v),encoding="utf-8")
        REPORT.write_text(render(v),encoding="utf-8")
    else:
        req(json.loads(OUT.read_text(encoding="utf-8"))==v,"manifest drift")
        req(REPORT.read_text(encoding="utf-8")==render(v),"report drift")
    print("PASS Batch149 immutable 4 Mac log/exit pairs, SHA, source and review checks")
if __name__=="__main__":main()
