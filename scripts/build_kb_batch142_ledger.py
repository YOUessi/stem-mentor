#!/usr/bin/env python3
"""Seven-track *provisional* coverage and mathematical risk ledger.

This is an auditable account of exactly what exists, not a claim that the
official curriculum denominator is known. Any change to input snapshots
requires an updated check and teacher review, not silent promotion.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch141_lineage as provenance
import check_kb_batch142_remaining_oracles as exact

LESSONS=ROOT/"docs/evaluation/KB_BATCH139_CORE_AUDIT.json"
OLDER=ROOT/"docs/evaluation/KB_BATCH141_EXACT_MATH_CASES.json"
OUT=ROOT/"docs/evaluation/KB_BATCH142_COVERAGE_AND_RISK.json"
MD=ROOT/"docs/evaluation/KB_BATCH142_COVERAGE_AND_RISK.md"


def build():
    original=json.loads(LESSONS.read_text(encoding="utf-8"))
    lineage=provenance.build()
    old=json.loads(OLDER.read_text(encoding="utf-8"))
    fresh=exact.oracle()
    assert original["total_manuscripts"]==57
    assert sum(original["by_track"].values())==57
    assert len(original["records"])==57 and len({r["candidate"] for r in original["records"]})==57
    assert all(r["review"]=="REVIEW_PENDING" for r in original["records"])
    assert set(original["by_track"])==set(provenance.TRACKS)
    assert old["tested_step_count"]==12 and len(old["cases"])==12
    assert fresh["newly_oracled_in_this_batch"]==35
    assert len({r["historical_step_id"] for r in old["cases"]+fresh["cases"]})==47
    assert len(lineage["records"])==47
    assert {r["historical_proof_step_id"] for r in lineage["records"]}=={
        r["historical_step_id"] for r in old["cases"]+fresh["cases"]}
    per_track={}
    for track in provenance.TRACKS:
        count=original["by_track"][track]
        per_track[track]={
            "provisional_teacher_manuscripts":count,
            "official_atom_denominator":None,
            "official_atoms_audited_as_complete":None,
            "official_coverage_ratio":None,
            "teacher_approved":0, "student_authoritative":0,
            "track_publishable":False
        }
    return dict(
        schema="kb142-seven-track-editorial-and-proofs-risk-ledger/1",
        standard_reference="China general senior high school mathematics 2017 edition 2020 revision",
        curriculum_source_semantic_verification="UNFINISHED",
        official_course_atom_census_complete=False,
        official_denominators_known=False,
        all_seven_official_coverage_ratio=None,
        per_track=per_track,
        historical_engineering_map_is_not_denominator=113,
        existing_teacher_only_draft_manuscripts=57,
        historical_p0_proof_step_denominator=127,
        p0_source_locked_cards=127,
        newly_source_locked_legacy_cards_in_kb141=47,
        independently_checked_kb141_steps_before_batch142=12,
        independently_checked_kb141_steps_added_batch142=35,
        independently_checked_kb141_steps_now=47,
        independent_exact_kb141_positive_cases=47,
        independent_exact_kb141_invalid_preconditions=47,
        kb141_subset_without_exact_witness=0,
        historical_formally_uncertified_proof_steps=538,
        unresolved_math_conflicts=10,
        human_teacher_approvals=0,
        student_authoritative_releases=0,
        free_student_steps_verified=0,
        general_formal_proof_certificates=0,
        scope_warning="127 P0 source-cards != 127 universal proofs; 47 finite-case audits are only a subset, 57 manuscripts != official syllabus coverage",
    )


def validate(data):
    expected=build()
    if data!=expected: raise ValueError("coverage/risk ledger drift or forged certification")
    return True


def render(data):
    lines=[
      "# Batch142｜七轨候审内容与P0证明风险清单","",
      "**重要：必修、选择性必修、选修A–E的正式知识原子分母全部仍 UNKNOWN；不得给出官方完成率。**","",
      "| 课程轨道 | 有限候审讲义 | 官方原子分母 | 教师批准 | 学生权威发布 |",
      "|---|---:|---|---:|---:|"]
    for t in provenance.TRACKS:
        row=data["per_track"][t]
        lines.append(f'| {t} | {row["provisional_teacher_manuscripts"]} | UNKNOWN | 0 | 0 |')
    lines.extend(["","## K07可验证事实","",
       "- 历史P0步骤127条均具有**来源锁定编辑卡**，不能视为完成127份形式化证明。",
       "- Batch141迁移的47张来源卡，之前12张具有独立有限正反例；本批为另35张建立各1条合法与1条失效前提精确见证。",
       "- 因此**该47张子集**目前47/47均有精确有限见证，共94个案例；不是整个127条P0的首次验证覆盖率。",
       "- 历史538条非形式认证证明步骤未因有限案例而改变状态；10项数学冲突仍未裁决。",
       "- 教师批准、学生发布、自由文本验证与通用证明证书均为0。","",
       "## 下一批待处理","",
       "1. 对K00七轨编号课标要求做跨页语义拆分/去重并冻结可审计官方原子分母，须人工核实。",
       "2. 对P0之外的历史证明逐项做通用条件证明/反例，不能用有限测试代替。",
       "3. 增补函数、几何、概率及选修的完整讲义/题族并在真实Agent端做隔离与评测。",""])
    return "\n".join(lines)


def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write",action="store_true")
    group.add_argument("--check",action="store_true")
    args=parser.parse_args()
    result=build()
    if args.write:
        OUT.write_text(provenance.canonical(result),encoding="utf-8")
        MD.write_text(render(result),encoding="utf-8")
    else:
        validate(json.loads(OUT.read_text(encoding="utf-8")))
        if MD.read_text(encoding="utf-8")!=render(result):
            raise ValueError("versioned human coverage report drift")
    print("PASS Batch142 seven-track scope accounting: 57 provisional drafts, UNKNOWN official denominators")


if __name__=="__main__":main()
