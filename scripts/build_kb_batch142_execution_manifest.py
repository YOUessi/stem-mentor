#!/usr/bin/env python3
"""Batch142 byte-verified Mac logs. Never imply CI reran the private licensed PDF."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch141_lineage as upstream
import check_kb_batch142_remaining_oracles as math
import build_kb_batch142_ledger as coverage

LOG=ROOT/"docs/evaluation/logs"
OUT=ROOT/"docs/evaluation/KB_BATCH142_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH142_EXECUTION_2026-11-14.md"
BASE_SHA="c34a7ef999b0a35668509b4fa731edf90b4d1ca8"


def demand(b,msg):
    if not b: raise ValueError("KB142 real execution evidence: "+msg)


def build():
    meta={}
    for key in ("FOCUSED","MAC_FULL","BROWSER"):
        p=LOG/("KB_BATCH142_"+key+".log")
        e=LOG/("KB_BATCH142_"+key+".exit")
        demand(p.is_file() and e.is_file(),"missing Mac logfile or exit: "+key)
        demand(e.read_text().strip()=="0","nonzero process exit: "+key)
        raw=p.read_bytes()
        demand(len(raw)>180,"truncated log: "+key)
        meta[key]={
            "log_path":str(p.relative_to(ROOT)),
            "exit_path":str(e.relative_to(ROOT)),
            "sha256":hashlib.sha256(raw).hexdigest(),
            "exit_sha256":hashlib.sha256(e.read_bytes()).hexdigest(),
            "bytes":len(raw),"exit":0
        }
    f=(ROOT/meta["FOCUSED"]["log_path"]).read_text(errors="replace")
    m=(ROOT/meta["MAC_FULL"]["log_path"]).read_text(errors="replace")
    b=(ROOT/meta["BROWSER"]["log_path"]).read_text(errors="replace")
    demand(re.search(r"\b197 passed\b",f) is not None,"standalone focused result missing")
    demand(re.search(r"\b197 passed\b",m) is not None,"full script focused result missing")
    demand(re.search(r"\b66,?293 passed, 5 skipped\b",m) is not None,
           "full backend suite not observed")
    demand(re.search(r"111 passed|# pass 111|111/111",m) is not None,
           "Node suite not observed")
    demand("PASS Batch142: 35 exact legal + 35 exact invalid-premise" in m,
           "math oracle absent from full Mac run")
    demand("PASS Batch142 seven-track scope accounting" in m,"coverage gate absent")
    demand("PDF REHASHED" in m,"Mac PDFKit source replay absent")
    demand(re.search(r"\b2 passed\b",b) is not None,"browser pytest missing")
    exact=math.oracle(); ledger=coverage.build()
    demand(exact["new_legal_cases"]==exact["new_invalid_precondition_cases"]==35,
           "recomputed 70 exact cases missing")
    demand(ledger["independently_checked_kb141_steps_now"]==47,
           "47 migrated source cards missing exact witness")
    return dict(
        schema="kb142-real-mac-test-exit-hash-evidence/1",
        date="2026-11-14",host="AUTHORIZED_MACBOOK_AIR_ONLY",
        remote_pr167_base_sha=BASE_SHA,
        github_ci_can_only_rehash_committed_logs=True,
        mac_original_pdfkit_rehash=True,
        full_mac_exit=0,browser_mac_exit=0,
        focused_passed=197,backend_passed=66293,backend_skipped=5,
        node_passed=111,browser_pytest_passed=2,
        new_exact_math_positive=35,new_exact_math_negative=35,
        kb141_subset_covered_by_finite_cases=47,
        p0_source_card_denominator=127,
        historical_uncertified_proof_steps=538,unresolved_math_conflicts=10,
        new_original_deep_manuscripts=0,prior_teacher_manuscripts=57,
        official_course_denominators={t:None for t in upstream.TRACKS},
        teacher_approvals=0,student_authoritative_releases=0,
        free_student_steps_verified=0,general_formal_proofs_certified=0,
        logs=meta
    )


def render(d):
    lines=[
      "# STEM Mentor｜Batch142 Mac真实执行与验收","",
      "本批在授权MacBook Air独立工作树中开发、测试及生成数据；没有使用Tang，Mac主仓原有脏文件保持不动。",
      "基于Batch141远端Draft PR #167（远端提交 "+BASE_SHA+"）的等价源码树；最终交付SHA由新Draft PR远端决定。","",
      "## 本批交付与不可跨越的边界","",
      "- K07：35条此前没有新增独立Oracle的历史P0来源卡，每条1个精确正例及1个前提失效反例，共70个独立有限数学见证。",
      "- K01/K09：每条有限Oracle与原始证明步骤SHA绑定；新增负面回归验证来源篡改、伪认证、伪官方分母与学生提前发布。",
      "- K00：机器审计七轨现有57份候审讲义分布，必修、选择性必修及选修A–E正式知识原子分母均UNKNOWN。",
      "- K08：学生索引继续默认拒绝未批准证据，不泄漏教师例题完整答案或证书。",
      "- Batch141迁移的47张卡，现每张各有1对独立有限见证（12旧+35新）；不构成通用数学证明，也不是全部127条P0首次验证。",
      "- 历史538条证明步骤仍未形式认证，10项冲突未裁决，教师批准、学生权威发布、自由文本步骤认证均为0。",
      "- 本批新增完整原创讲义0份；之前57份仍为教师候审稿。","",
      "## Mac真实测试","",
      "| 类型 | 结果 |","|---|---|",
      "| Batch142独立专项 | 197 passed（在完整Mac脚本内也执行，不重复相加） |",
      "| 完整Python后端 | 66,293 passed；5 skipped |",
      "| Node | 111 passed |",
      "| Mac原始PDFKit课标哈希重放 | PASS（CI仅校验提交日志与指纹） |",
      "| Chrome/Playwright | EXIT 0；浏览器pytest 2 passed，不代表实体iPad |",
      "| 本批数学有限Oracle | 35合法+35前提失效=70项 |","",
      "## 原始日志和退出码","",
      "| 日志 | 退出码 | SHA256 | 字节 |","|---|---:|---|---:|"
    ]
    for key in ("FOCUSED","MAC_FULL","BROWSER"):
        x=d["logs"][key]
        lines.append(f'| {x["log_path"]} | {x["exit"]} | {x["sha256"]} | {x["bytes"]} |')
    lines += ["",
       "GitHub只能检查这些历史日志的真实字节与退出码，不能声称在GitHub Runner重复运行Mac私有PDFKit来源验证。","",
       "## 失败记录与下一批计划","",
       "- 首次数学Oracle发现三维向量例子的点积意外等于0，无法证实漏掉交叉项的错误；将见证改为非正交向量后重新通过精确Oracle和测试。",
       "- Mac访问GitHub原生fetch发生HTTP超时；交付必须验证远端基线及Git树，不得强推或覆盖。",
       "- K00：对完整课标的编号课程要求跨页拆分、去重，冻结真正可审计的七轨正式原子分母并待教师语义复核。",
       "- K07：从有限见证走向带完整量词和前提的逐步通用论证，裁决10项数学冲突及余下历史证明步骤。",
       "- K02–K06：恢复系统性的完整原创讲义、题族、典型错因和近远迁移，而不是长期只建设审查档案。",
       "- K08/K09：接入真实教学Agent和未见题冻结集，验证正确引用、条件核验、提示防泄漏和学习增益。",""
    ]
    return "\n".join(lines)


def main():
    parser=argparse.ArgumentParser()
    g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check",action="store_true")
    opt=parser.parse_args()
    data=build()
    if opt.write:
        OUT.write_text(upstream.canonical(data),encoding="utf-8")
        REPORT.write_text(render(data),encoding="utf-8")
    else:
        demand(json.loads(OUT.read_text(encoding="utf-8"))==data,"manifest drift")
        demand(REPORT.read_text(encoding="utf-8")==render(data),"report drift")
    print("PASS KB142 true Mac evidence: 197 focused; 66293 backend; 111 Node; 2 Chrome tests")


if __name__=="__main__":main()
