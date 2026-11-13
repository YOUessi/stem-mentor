#!/usr/bin/env python3
"""Machine-auditable bounded lesson quality and missing-content ledger.

Never substitute these 41 editorial proposals for the seven-track national
syllabus denominator. No 'APPROVED' records created here.
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch133_atomization as atoms
import build_kb_batch134_graph as graph
import build_kb_batch135_lessons as new_lessons
import check_kb_batch135_math as latest_math

OUT=ROOT/"docs/evaluation/KB_BATCH135_BOUNDED_COMPLETENESS.json"
MD=ROOT/"docs/evaluation/KB_BATCH135_BOUNDED_COMPLETENESS.md"
MANUSCRIPTS=(
    ROOT/"knowledge/editorial_review/kb_batch133_six_core_lessons.json",
    ROOT/"knowledge/editorial_review/kb_batch134_eight_proof_lessons.json",
    new_lessons.OUT)
ORACLES=(
    ROOT/"docs/evaluation/KB_BATCH133_EXACT_MATH_WITNESSES.json",
    ROOT/"docs/evaluation/KB_BATCH134_EXACT_FINITE_WITNESSES.json",
    latest_math.OUT)

def fail_if(x, why):
    if x: raise ValueError(why)

def build():
    inventory=json.loads(atoms.OUT.read_text(encoding="utf-8"))
    atoms.validate(inventory)
    g=json.loads(graph.OUT.read_text(encoding="utf-8"))
    graph.validate(g)
    ordered=inventory["records"]
    drafts=[r for path in MANUSCRIPTS for r in json.loads(path.read_text(encoding="utf-8"))]
    fail_if(len(drafts)!=22 or len({r["id"] for r in drafts})!=22,"duplicate or missing lesson")
    by_source={}
    for d in drafts:
        key=d.get("source_candidate_id",d.get("candidate_id"))
        fail_if(key in by_source,"duplicate manuscript mapped to proposal")
        by_source[key]=d
    fail_if(not set(by_source).issubset({r["id"] for r in ordered}),"foreign source")
    required=("formal_definition_or_theorem","notation_and_domain",
              "applicability_and_hypotheses","reasoned_steps","why_method_is_legal",
              "nonexample_or_failure","typical_wrong_solution","why_wrong_and_repair",
              "teacher_examples","student_hint_ladder","near_transfer","far_transfer")
    rows=[]
    for r in ordered:
        linked=by_source.get(r["id"])
        content=linked is not None and all(bool(linked.get(k)) for k in required)
        if linked:
            fail_if(linked["student_authoritative"] or linked["teacher_review_status"]!="REVIEW_PENDING",
                "unreviewed editorial proposal incorrectly released")
            lock=linked.get("source_span_sha256")
            if lock is None:lock=linked["source_line_lock"]["span_sha256"]
            fail_if(lock!=r["source_lock"]["span_sha256"],"source line mismatch")
            fail_if(linked["source_pdf_sha256"]!=r["source_pdf_sha256"],"source PDF mismatch")
        rows.append({
            "candidate_id":r["id"],
            "track":r["track"],
            "knowledge_type":r["knowledge_type"],
            "source_span_sha256":r["source_lock"]["span_sha256"],
            "has_complete_teacher_manuscript":bool(content),
            "manuscript_id":linked["id"] if linked else None,
            "missing_fields":[k for k in required if not linked or not linked.get(k)],
            "teacher_examples":len(linked["teacher_examples"]) if linked else 0,
            "student_hints":len(linked["student_hint_ladder"]) if linked else 0,
            "prerequisite_proposals":r["prerequisite_proposals"],
            "teacher_review":"REVIEW_PENDING",
            "math_general_proof_certified":False,
            "student_authoritative":False,
            "official_atom_id":None,
        })
    sample_count=0
    for path in ORACLES:
        cases=json.loads(path.read_text(encoding="utf-8"))["cases"]
        sample_count+=len(cases)
    totals={}
    for track in atoms.TRACKS:
        sub=[r for r in rows if r["track"]==track]
        totals[track]={
            "provisional_candidates":len(sub),
            "complete_teacher_manuscript_drafts":sum(r["has_complete_teacher_manuscript"] for r in sub),
            "candidates_still_missing_full_draft":sum(not r["has_complete_teacher_manuscript"] for r in sub),
            "official_atom_denominator":None,
            "official_coverage_rate":None,
            "teacher_approved":0,
            "student_published":0,
        }
    queue=[r["candidate_id"] for r in rows if not r["has_complete_teacher_manuscript"]]
    return dict(
        schema="kb135-quality-matrix/1",
        source="BOUNDED_41_EDITORIAL_PROPOSALS_NOT_FULL_NATIONAL_CENSUS",
        syllabus_version="2017-edition-2020-revision-editorial-only",
        all_seven_track_denominators_known=False,
        official_atom_denominators={t:None for t in atoms.TRACKS},
        national_course_coverage_percentage=None,
        scope_proposals=41,full_teacher_draft_manuscripts=22,
        incomplete_proposal_drafts=19,teacher_examples=44,
        hints=66,near_transfer_exercises=22,far_transfer_exercises=22,
        finite_exact_oracle_cases=sample_count,
        batch135_symbolic_subclaims=4,
        certified_general_theorems=0,teacher_approvals=0,student_authoritative_releases=0,
        by_track=totals,
        missing_full_manuscript_queue=queue,
        rows=rows,
    )

def validate(output):
    if output!=build():raise ValueError("frozen coverage invalid or forged denominator/approval")
    return True

def render(a):
    s=["# Batch135｜41条有限原子候选的内容完整度与审核矩阵","",
       "**特别注意：以下分母为41条来源锁定的项目拟议原子，不是七轨官方课标知识原子分母。七轨官方分母均UNKNOWN。**","",
       f"拟议原子{a['scope_proposals']}；完整候审讲义{a['full_teacher_draft_manuscripts']}；缺完整讲义{a['incomplete_proposal_drafts']}。"]
    s.extend([f"教师例题{a['teacher_examples']}、三级提示{a['hints']}、近远变式各{a['near_transfer_exercises']}；"
              f"历史与新增精确有限样例合计{a['finite_exact_oracle_cases']}；新增符号子命题{a['batch135_symbolic_subclaims']}。",
              "一般定理认证0、真实教师批准0、学生权威发布0。有限代数见证不可替代对条件/全称量词的一般证明。","",
              "| 七轨 | 拟议节点 | 完整教师草案 | 未完成草案 | 官方原子分母 | 教师批准 |",
              "|---|---:|---:|---:|---|---:|"])
    for t in atoms.TRACKS:
        row=a["by_track"][t]
        s.append(f"| {t} | {row['provisional_candidates']} | {row['complete_teacher_manuscript_drafts']} | {row['candidates_still_missing_full_draft']} | UNKNOWN | 0 |")
    s.extend(["","## 逐条可核对内容/先修/审核账本",""])
    for r in a["rows"]:
        s.append(f"- {r['candidate_id']} · {r['track']} · {r['knowledge_type']} · "
          f"{'完整教师草案' if r['has_complete_teacher_manuscript'] else '缺完整草案'} · "
          f"例题{r['teacher_examples']} · 提示{r['student_hints']} · "
          f"先修{len(r['prerequisite_proposals'])} · 来源摘要{r['source_span_sha256']} · REVIEW_PENDING")
    s.extend(["","## 后续交付优先级","",
      "补齐清单中19个缺完整草案的原子，再扩展七轨未覆盖的课程要求；选修B–E本有限41条子集没有节点，**不**代表已完成或没有课程内容。源码/课标对照仍需教师语义核验。",
      "对历史538条未认证证明步骤、172条待审先修关系和10项冲突须重新读取对应最新事实源，不从本有限子集推断其已解决。"])
    return "\n".join(s)+"\n"

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    z=p.parse_args()
    if z.write:
        d=build();validate(d)
        OUT.write_text(atoms.stable_json(d),encoding="utf-8")
        MD.write_text(render(d),encoding="utf-8")
    else:
        d=json.loads(OUT.read_text(encoding="utf-8"))
        validate(d)
        if MD.read_text(encoding="utf-8")!=render(d):
            raise ValueError("coverage markdown drift")
    print("PASS 41 bounded candidates, 22 teacher drafts, 19 missing; official denominators UNKNOWN")
if __name__=="__main__":main()
