#!/usr/bin/env python3
"""Byte-for-byte evidence of REAL Batch156 authorized Mac acceptance, including an initial failed test.

A passing exit file without an authentic original stdout log is not acceptable.
Mathematical finite cases, approval, and official syllabus denominators remain distinct.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch156_lessons as lesson
import check_kb_batch156_math as oracle
LOG_DIR=ROOT/"docs/evaluation/logs"
PREFIX="KB_BATCH156"
SOURCE_COMMIT="f8f6bb41c8b4f7dce68b7dd3a15f2619596f287c"
SUCCESS=("FOCUSED","NODE","BROWSER","MAC_FULL")
EXPECTED_FAILURE="FOCUSED_INITIAL"
MANIFEST=ROOT/"docs/evaluation/KB_BATCH156_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH156_EXECUTION_2026-11-14.md"

def require(ok,msg):
    if not ok:raise ValueError("KB156 real Mac evidence invalid: "+msg)

def sha(bs):return hashlib.sha256(bs).hexdigest()

def read_runs(base=LOG_DIR):
    runs={};txt={}
    for name in (*SUCCESS,EXPECTED_FAILURE):
        path=base/f"{PREFIX}_{name}.log"
        exit_path=base/f"{PREFIX}_{name}.exit"
        require(path.is_file() and exit_path.is_file(),"missing log/exit "+name)
        body=path.read_bytes();code=exit_path.read_bytes()
        expected=b"1" if name==EXPECTED_FAILURE else b"0"
        require(len(body)>100 and code.strip()==expected,
                "missing real bytes or changed outcome "+name)
        s=body.decode("utf-8")
        require("\x00" not in s,"binary data in "+name)
        runs[name]=dict(path="docs/evaluation/logs/"+path.name,
             sha256=sha(body),bytes=len(body),
             exit_path="docs/evaluation/logs/"+exit_path.name,
             exit_sha256=sha(code),exit_code=int(expected))
        txt[name]=s
    require(re.search(r"\b273 passed\b",txt["FOCUSED"]) is not None,
            "273 focused tests not evidenced")
    require(re.search(r"\b10 failed, 263 passed\b",txt["FOCUSED_INITIAL"]) is not None and
            "invalid search limit" in txt["FOCUSED_INITIAL"],
            "first failing test and exact regression cause not archived")
    require("# pass 111" in txt["NODE"] and "# fail 0" in txt["NODE"],
            "111 Node tests not evidenced")
    br=txt["BROWSER"]
    require("Chrome browser suite passed" in br and
            re.search(r"\b2 passed\b",br) is not None and
            "GREEN v0.7 Chrome test: 9 passed" in br,
            "Chrome and browser-pytest evidence missing")
    full=txt["MAC_FULL"]
    for pattern,description in (
        (r"66,?293 passed, 5 skipped","backend full"),
        (r"# pass 111","Node in Mac full"),
        (r"PASS KB156 ten source-locked deep drafts","ten-authored-source-check"),
        (r"PASS KB156 40/40 independent exact bounded witnesses","independent math witness"),
        (r"273 passed","included focused regression"),
        (r"Mac PDFKit source rehash PASS","private authorized original source"),
    ):
        require(re.search(pattern,full) is not None,description+" absent from Mac full log")
    return runs

def build(log_dir=LOG_DIR):
    logs=read_runs(log_dir)
    records=lesson.build()
    require(lesson.validate(records),"10 original manuscripts failed schema")
    audit=lesson.audit(records)
    math=oracle.build()
    require(audit["total_teacher_only_drafts"]==155 and
            audit["historical_candidates_with_drafts"]==114 and
            audit["historical_candidates_without_drafts"]==125 and
            audit["teacher_approved"]==audit["student_authoritative"]==0,
            "draft approval/provenance conservation")
    require(math["verified_bounded_cases"]==40 and
            math["invalid_premise_or_false_generalization_rejected"]==20 and
            math["general_theorems_formally_proven"]==0,
            "independent exact witness bounds")
    require(all(x is None for x in audit["official_atom_denominators"].values()),
            "fabricated national curriculum knowledge atomic denominator")
    # CI has no licensed original PDF. The archived Mac full log attests the
    # actual rehash; source SHA locks are verified by the offline lesson builder.
    require(set(json.loads(lesson.LOCKS.read_text(encoding="utf-8")))==set(lesson.IDS),
            "Mac original PDFKit authoring source hash locks missing")
    return dict(schema="kb156-verified-mac-original-log-byte-evidence/1",
       source_commit=SOURCE_COMMIT,date="2026-11-14",
       environment="AUTHORIZED_MACBOOK_AIR_ONLY",mac_full_exit=0,
       added_teacher_only_manuscripts=10,total_teacher_only_manuscripts=155,
       original_teacher_examples=20,student_safe_hint_steps=30,near_far_transfers=20,
       old_unapproved_editorial_candidates=239,editorial_with_teacher_draft=114,
       editorial_without_teacher_draft=125,
       numbered_syllabus_layout_markers_not_atomic_denominators=315,
       official_atom_denominators=audit["official_atom_denominators"],
       official_course_completion_rate=None,
       real_teacher_approved=0,student_authoritative_releases=0,
       formal_general_proof_certifications=0,student_free_steps_certified=0,
       independent_bounded_sympy_cases=40,positive_bounded_cases=20,
       false_premise_rejections=20,backend_passed=66293,
       backend_skipped=5,node_passed=111,focused_passed=273,
       initial_focused_failed=10,initial_focused_passed=263,
       browser_simulation_green_v07_passed=9,browser_pytest_passed=2,
       logs=logs,
       warnings=["Historical source markers and 155 drafts do not determine official course atoms",
                 "Bounded symbolic witnesses do not certify theorems for all inputs",
                 "No teacher approval, no authoritative student retrieval",
                 "Teacher examples and raw licensed PDF source are not exposed through public API",
                 "Initial test failure preserved rather than erased"] )

def render(m):
    out=["# KB156｜授权Mac真实开发与原始验收（2026-11-14）","",
         "源代码commit: `"+SOURCE_COMMIT+"`。工作树位于MacBook Air独立feature branch，不修改既有主仓工作区，无Tang、无主分支合并或强推。","",
         "## 本轮原创教学内容与代码",
         "新增10篇完整原创教师候审稿：必修4（并集交集、全集空集、必要充分条件、单位圆正切边界）；选择性必修3（等比有限求和q=1、仿射链式法则a=0特例、三维平面非零法向量）；选修A/B/C各1（非零方向正交投影、协方差半正定与退化、反证法有效前提）。",
         "每篇有定义/定理陈述、符号域、全部适用假设、四条分步证明或合法性解释、失效反例、错因修复、两道原创教师例题、三级学生无剧透提示、近远迁移。累计155份候审，新增20题、30级提示、20项迁移。全部 `REVIEW_PENDING/TEACHER_ONLY`。",
         "新增编辑者隔离FTS5检索、公共聚合状态API和fail-closed的学生检索；老师完整答案不进入学生索引或公开返回。","",
         "## K00/K01官方范围的真实边界",
         "本地授权2020修订课标PDFKit原始位置及SHA-256重新校验。历史239条编辑候选现114已有关联候审稿、125缺稿；315条编号**排版来源标记不是知识原子分母**，七轨正式课程原子分母全部UNKNOWN。未完成跨页语义去重/条款拆分、真实教师审查；不能宣称全国课程覆盖率。原始版权PDF或课标全文不上传。","",
         "## K07独立数学验证及其边界",
         "使用SymPy精确计算40/40项有限见证，20项合法/边界和20项错误泛化/失效前提反例。关键检查包括q=1分母零、a=0复合常数求导、非零法向、协方差半正定、投影分母非零和反证法。**这些不证明一般定理，不批准学生自由推导，也不能替代真人教师审核。**","",
         "## K09真实执行、失败保留与日志SHA-256",
         "Mac完整回归 `bash scripts/mac_check.sh` 退出码0；后端**66,293 passed、5 skipped**；Node **111 passed**；Batch156专项**273 passed**；Chrome v0.7模拟**9 passed**，另浏览器pytest**2 passed**。各种专项与全量运行有交集，不做数量叠加。浏览器模拟不是实体iPad验收。",
         "专项首次测试 **10 failed、263 passed**，根因是新增测试误以为编辑检索允许limit=50，实际上既有安全门禁只允许1–20；仅将测试改为limit=20，没有放宽产品安全约束。首次失败及修复后成功的原始stdout、退出码都存档。","",
         "| 原始执行日志 | 实际退出码 | 字节数 | SHA-256 |","|---|---:|---:|---|"]
    for name,r in sorted(m["logs"].items()):
        out.append(f"| {name} | {r['exit_code']} | {r['bytes']} | `{r['sha256']}` |")
    out+=["","以上SHA-256对应实际Mac日志原始字节，退出码字节也在机器可读JSON清单中单独锁定；独立负例测试应拒绝改动日志、伪造退出码、错报测试数和虚假审核。第三方anyio/Starlette弃用警告未消除。","",
         "## 下一批计划",
         "优先K00以官方逐句需求拆分、验证选修D/E无编号来源、跨页人工语义裁决并冻结七轨真正原子分母；沿125条缺稿历史线索建设更多原创完整讲义；对538条历史未获一般证明的步骤和10项冲突继续实质数学核验；K08冻结未见题与规则baseline/真实模型API对照，待真实教师审查才可授权发布。",""]
    return "\n".join(out)

def main():
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--write",action="store_true")
    group.add_argument("--check",action="store_true")
    args=p.parse_args()
    m=build();report=render(m)
    if args.write:
        MANIFEST.write_text(json.dumps(m,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
        REPORT.write_text(report,encoding="utf-8")
    else:
        require(json.loads(MANIFEST.read_text(encoding="utf-8"))==m,"manifest content modified")
        require(REPORT.read_text(encoding="utf-8")==report,"report content modified")
    print("PASS KB156 authentic Mac 5 run logs + source PDFKit rehash + zero teacher approvals")
if __name__=="__main__":main()
