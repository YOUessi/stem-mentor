#!/usr/bin/env python3
"""Verify genuine Mac logs/exit codes and regenerate a versioned evidence report."""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch147_lessons as lessons
import build_kb_batch147_crosswalk as census
import check_kb_batch147_math as math
import audit_kb_batch147_source_edges as boundaries
LOG=ROOT/"docs/evaluation/logs"
OUT=ROOT/"docs/evaluation/KB_BATCH147_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH147_EXECUTION_2026-11-14.md"
PARENT_SHA="fad0d2a4fb3e8349f7785fd96277fdea751a8604"
SOURCE_SHA="35e825141ac5f0223d1f4a1b6cb0901089907248"
def req(ok,msg):
    if not ok:raise ValueError("Batch147 immutable Mac evidence: "+msg)
def collect():
    out={}
    for key in ("FOCUSED","K00_FOCUSED","MAC_FULL","BROWSER"):
        file=LOG/f"KB_BATCH147_{key}.log"
        ex=LOG/f"KB_BATCH147_{key}.exit"
        req(file.is_file() and ex.is_file(),f"{key} log or exit missing")
        req(ex.read_text(encoding="utf-8").strip()=="0",f"{key} execution nonzero")
        raw=file.read_bytes()
        req(len(raw)>(80 if key=="K00_FOCUSED" else 250),f"{key} truncated")
        out[key]=dict(path=f"docs/evaluation/logs/KB_BATCH147_{key}.log",exit_path=f"docs/evaluation/logs/KB_BATCH147_{key}.exit",
            bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
            exit_sha256=hashlib.sha256(ex.read_bytes()).hexdigest(),exit=0)
    return out
def archived_negative_runs():
    result={}
    for label,expected_rc,expected_text in (("ARCHIVE_NEGATIVE_INITIAL_FAILURE",1,"6 failed"),
        ("ARCHIVE_NEGATIVE",0,"6 passed")):
        file=ROOT/"docs/evaluation/logs"/f"KB_BATCH147_{label}.log"
        ex=ROOT/"docs/evaluation/logs"/f"KB_BATCH147_{label}.exit"
        req(file.is_file() and ex.is_file(),f"{label} archived regression missing")
        req(ex.read_text(encoding="utf-8").strip()==str(expected_rc),f"{label} expected exit {expected_rc}")
        raw=file.read_bytes()
        req(expected_text in raw.decode("utf-8",errors="replace"),f"{label} missing test summary")
        result[label]=dict(path=str(file.relative_to(ROOT)),exit_path=str(ex.relative_to(ROOT)),
            exit=expected_rc,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
            exit_sha256=hashlib.sha256(ex.read_bytes()).hexdigest())
    return result

def build():
    logs=collect()
    archive_replays=archived_negative_runs()
    txt={key:(LOG/f"KB_BATCH147_{key}.log").read_text(encoding="utf-8",errors="replace") for key in logs}
    req(re.search(r"\b283 passed\b",txt["FOCUSED"]), "283 combined focused passes not recorded")
    req(re.search(r"\b17 passed\b",txt["K00_FOCUSED"]), "17 K00 focused passes not recorded")
    full=txt["MAC_FULL"];browser=txt["BROWSER"]
    for needle in ("PDF REHASHED original lines PASS",
       "PASS Batch147: 10 seven-track source-hashed teacher lessons",
       "PASS Batch147: 40 independent exact math witnesses",
       "PASS Batch147 source crosswalk",
       "PASS Batch147 K00: 239 provisional leads"):
        req(needle in full,"full run missing: "+needle)
    req(re.search(r"\b266 passed\b",full),"in-script lesson-focused 266 absent")
    req(re.search(r"\b17 passed\b",full),"in-script K00 focused 17 absent")
    req(re.search(r"\b66,?293 passed, 5 skipped\b",full),"66,293 backend/5 skipped absent")
    req(re.search(r"\b111 passed|# pass 111|111/111",full),"111 Node tests absent")
    req(re.search(r"\b2 passed\b",browser),"browser pytest two passes missing")
    req("GREEN v0.7 Chrome test: 9 passed" in browser,"nine Chrome interactive checks missing")
    audit=lessons.audit(lessons.build())
    gaps=census.build()
    k00=boundaries.make()
    exact=math.oracle()
    req(audit["total_teacher_only_drafts"]==95 and audit["new_original_manuscripts"]==10,"draft audit drift")
    req(gaps["historical_editorial_candidates"]==239 and
        gaps["candidate_to_draft_matches"]==54 and gaps["candidates_without_bounded_teacher_draft"]==185,
        "historic editorial crosswalk drift")
    req(len(k00["candidate_relation_edges"])==89 and len(k00["candidates"])==239 and
        len({(e["a"],e["b"]) for e in k00["candidate_relation_edges"]})==69,
        "K00 source-boundary graph drift")
    req(exact["total_cases"]==40 and exact["rejected_invalid_premises"]==20,
        "exact oracle count drift")
    return dict(schema="kb147-real-mac-execution-evidence/1",
        base_git_commit=PARENT_SHA,source_git_commit=SOURCE_SHA,
        device="AUTHORIZED_YOUTANG_MACBOOK_AIR_ONLY",run_date="2026-11-14",
        licensed_original_standard_pdf_remains_mac_only=True,
        original_pdfkit_line_sha_replay_passed=True,github_can_replay_private_pdf=False,
        focused_tests_passed=283,independent_k00_tests_passed=17,
        backend_python_passed=66293,backend_python_skipped=5,node_tests_passed=111,
        chrome_interaction_passed=9,browser_pytest_passed=2,
        deep_teacher_review_drafts_added=10,deep_teacher_review_drafts_total=95,
        teacher_examples_added=20,student_hint_steps_added=30,near_far_tasks_added=20,
        independent_finite_math_checks_passed=40,invalid_hypotheses_rejected=20,
        source_historical_editorial_leads=239,linked_teacher_drafts=54,unlinked_historical_leads=185,
        k00_source_boundary_relation_records=89,k00_source_boundary_distinct_pairs=69,
        k00_source_boundary_pair_counts=k00["edge_counts"],
        official_atom_denominators={t:None for t in lessons.TRACKS},
        official_syllabus_census_completed=False,teacher_approvals=0,
        authoritative_student_publications=0,general_formal_proof_certifications=0,
        free_student_solution_steps_certified=0,
        initial_incremental_failures=1,initial_archive_regression_failures=6,
        initial_archive_failure_log_archived=True,
        initial_archive_failure_cause="First archived-log mutation tests used temporary paths outside repository; the evidence collector called relative_to(ROOT). Fixed canonical report paths and reading from mocked LOG; rerun required",
        initial_failure_log_archived=False,
        initial_failure_cause="First 266-case run called oracle(), while independent module exported exact(); reconciled the name and reran 266/266",
        historical_uncertified_steps=538,unresolved_historical_math_conflicts=10,
        logs=logs,archived_negative_tests=archive_replays)
def report(x):
    lines=["# STEM Mentor｜Batch147 MacBook Air 原创课程、来源边界、数学验证与交付报告","",
       "本批仅在授权 MacBook Air 的独立工作树开发、编写与执行；没有使用 Tang、合并 main 或改写既有历史。",
       "源码分支：feat/kb-batch147-source-depth-next；原始主仓未提交内容未进入本批。",
       f'源起Git SHA：`{PARENT_SHA}`；本批源码SHA：`{SOURCE_SHA}`。',"",
       "## K00/K01：课标来源与可审计缺口",
       "- 课程基准：教育部2017年版2020年修订课标；原始许可188页PDF仅保存在Mac，源页/行PDFKit SHA重放通过，不上传版权原文。",
       "- 历史239条只是编辑来源线索，并非国家完整官方原子分母；本批新增10份课程讲义来源绑定后，54条已联候审稿、185条缺稿。",
       "- 建立239候选的逐条来源元数据审查图、同页区间重叠及相邻页首尾连续线索，产生89条待裁决的元数据关系记录，涉及69对不同候选；20条记录对应重复候选对的另一种关系标签。",
       "- 同页/相邻页元数据相似只是审查提示，不自动合并或证明同一官方知识原子；七轨正式原子分母仍全部UNKNOWN，所有审核未通过。",
       "",
       "## K02–K06：10份完整原创教师候审讲义",
       "- 必修3篇：复数非零除数与共轭有理化；不共线三点唯一确定平面；样本空间、事件并交补和非等可能条件。",
       "- 选择性必修2篇：正整数指标域上的数列；等差数列前n项和倒序配对证明。",
       "- 选修A：数列极限ε-N定义；B：导数与速度加速度的单位；C：命题、开放句与量词；D：几何形态不变量和审美边界；E：机器人二维坐标变换，明确标记学校拓展示例。",
       "- 每篇含形式陈述、全部使用前提、4步论证、非例/失效边界、典型错法与修复、2道完整教师例题、3级安全提示、近远迁移。新增20例题、30级提示、20项迁移。",
       "- 累计95份REVIEW_PENDING/TEACHER_ONLY；没有真实教师审校；学生默认拒答未获批准证据。",
       "",
       "## K07/K08/K09：数学正确性和Agent安全",
       "- 独立SymPy/有限精确见证40/40，其中20合法或边界样例、20前提失效拒绝；不能当普遍定理形式证明。",
       "- 编辑本地FTS5检索覆盖95份未审核讲义，只返回ID/轨道/审查状态及排序；学生端返回NO_APPROVED_EVIDENCE。",
       "- FastAPI /api/knowledge/kb147-review-coverage仅暴露聚合数量，绝不返回教师详细解法。",
       "- 初次专项运行1项失败，因校验入口名称oracle/exact不一致；修正后283项专项通过。该失败的初次原始日志未归档，不能冒称已有失败证据文件。",
       "- 归档日志防篡改负面测试首次6项失败：临时测试目录不在仓库内，错误使用Path.relative_to(ROOT)；修复固定逻辑路径并读取测试副本。保留失败日志，修复后独立6/6通过。",
       "- 仍有历史538条未经普适形式认证的证明步骤和10项待裁决数学冲突。",
       "",
       "## Mac真实测试",
       "| 项目 | 结果 |","|---|---|",
       "| Batch147全部增量 | 283 passed（1条第三方弃用警告） |",
       "| 独立K00复跑 | 17 passed（与283有重叠） |",
       "| Mac脚本专项 | 266+17 passed（与增量重叠，不累计） |",
       "| 原始PDFKit源行SHA重放 | PASS，许可原文未上传 |",
       "| 后端Python全量 | 66,293 passed，5 skipped |",
       "| Node | 111 passed |",
       "| Chrome交互与浏览器pytest | Chrome 9 passed，pytest 2 passed（非实体iPad） |",
       "| 完整Mac脚本与浏览器脚本退出 | EXIT 0 / EXIT 0 |","",
       "## 原始Mac日志与退出码字节摘要",
       "| 日志 | exit | SHA-256 | 大小bytes |",
       "|---|---:|---|---:|"]
    for key in ("FOCUSED","K00_FOCUSED","MAC_FULL","BROWSER"):
        log=x["logs"][key]
        lines.append(f'| `{log["path"]}` | {log["exit"]} | `{log["sha256"]}` | {log["bytes"]} |')
    lines.append("")
    lines.append("### 归档证据负面测试的首次失败与修复重跑（均真实保留）")
    lines.append("| 执行 | 退出码 | SHA-256 | 大小bytes |")
    lines.append("|---|---:|---|---:|")
    for label in ("ARCHIVE_NEGATIVE_INITIAL_FAILURE","ARCHIVE_NEGATIVE"):
        item=x["archived_negative_tests"][label]
        lines.append(f'| `{item["path"]}` | {item["exit"]} | `{item["sha256"]}` | {item["bytes"]} |')
    lines.extend(["",
       "本报告中版本化的日志可用于GitHub重新校验退出码、数学测试和摘要；GitHub runner不能替代授权Mac上许可课标的PDFKit重放。",
       "",
       "## 下批优先项",
       "- K00：继续对正式编号课程要求做逐句原子化与跨页语义判定，由真实教师审核后才能冻结七轨分母。",
       "- K02–K06：沿185条缺稿的历史编辑线索拓展完整讲义，重新对齐正式课标与题族结构。",
       "- K07：处理538条历史形式认证缺口、10项冲突的真实数学裁决。",
       "- K08/K09：未见题结构检索对照、数学前提拒答、教师签核和逐章发布门禁。",
       "",
       "当前发布状态：0教师APPROVED；0学生权威发布；0自由文本学生步骤认证。",""])
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check",action="store_true")
    a=p.parse_args();d=build()
    if a.write:
        OUT.write_text(lessons.encode(d),encoding="utf-8")
        REPORT.write_text(report(d),encoding="utf-8")
    else:
        req(json.loads(OUT.read_text(encoding="utf-8"))==d,"manifest drift")
        req(REPORT.read_text(encoding="utf-8")==report(d),"human report drift")
    print("PASS Batch147 Mac evidence: 283 focused, 17 K00, 66293 backend, 111 Node, 9 Chrome, 2 browser, 40 math")
if __name__=="__main__":main()
