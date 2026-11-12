#!/usr/bin/env python3
"""Machine-auditable curriculum denominator gap and teacher-only lesson completeness.

The known total of 61 is PDF SOURCE pages, NOT official math atoms. This matrix
explicitly refuses to divide by an unknown seven-track knowledge denominator.
"""
from __future__ import annotations
import json,sys,argparse
from pathlib import Path
from collections import Counter
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from build_kb_batch110_scope import build as current_scope,TRACKS,serialize
from build_kb_batch110_lessons import build as current_lessons
from app.deep_knowledge import DeepLesson
SOURCE=ROOT/"curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
OUT=ROOT/"docs/evaluation/KB_BATCH110_COVERAGE.json"
MD=ROOT/"docs/evaluation/KB_BATCH110_COVERAGE.md"

def need(cond,msg):
    if not cond: raise ValueError(msg)

def build(prior_sources=None, current=None, lesson_pack=None):
    reg=json.loads(SOURCE.read_text(encoding="utf8"))
    pages={x["printed_page"]:x for x in reg["pages"]}
    need(set(pages)==set(range(13,74)),"61-page source registry incomplete")
    need(all(x["full_page_human_review"]=="PENDING" for x in pages.values()),
         "teacher full-page certification must use explicit teacher evidence")
    if prior_sources is None:
        prior_sources=[json.loads((ROOT/f"docs/evaluation/KB_BATCH{n}_SCOPE.json")
                            .read_text(encoding="utf8")) for n in (108,109)]
    if current is None:current=current_scope()
    if lesson_pack is None:lesson_pack=current_lessons()
    scopes=[*prior_sources,current]
    scoped_pages={};candidates=[];partition_count=0
    for s in scopes:
        need(s["source_pdf_sha256"]==reg["official_pdf_sha256"],"source PDF SHA mismatch")
        need(set(s["official_seven_track_atom_denominators"].values())=={None},
             "cannot forge official atomic denominator")
        need(s["teacher_full_page_atomizations"]==0 and s["teacher_approvals"]==0,
             "unexpected teacher certification claim")
        for p,n in s["line_counts"].items():
            p=int(p)
            need(p in pages and p not in scoped_pages,"overlapping source page or unknown page")
            need(n>0,"invalid source line count")
            scoped_pages[p]=int(n)
        partition_count+=len(s["structural_partitions"])
        candidates.extend(s["candidates"])
    counts=Counter(x["track_hint"] for x in candidates)
    need(set(counts)<=set(TRACKS),"unknown candidate track")
    need(sum(counts.values())==60 and len(scoped_pages)==6,
         "historical scope comparison denominator drift")
    docs,audit=lesson_pack
    rows=[]
    for doc in docs:
        lesson=DeepLesson.model_validate(doc)
        need(lesson.review.status=="REVIEW_PENDING" and
             lesson.review.reviewer_id is None and
             lesson.teacher_solution_visibility=="TEACHER_ONLY",
             "draft must not gain authority")
        checks=dict(
          substantive_statement=len(lesson.statement)>=50,
          domain_and_hypotheses=len(lesson.assumptions)>=2,
          notation=len(lesson.notation)>=2,
          prerequisites=len(lesson.prerequisites)>=2,
          complete_explanations_or_candidate_proof=
               len(lesson.proof_steps if lesson.kind=="theorem" else lesson.rationale_steps)>=3,
          concrete_failure_example=len(lesson.counterexamples)>=1,
          misconception=len(lesson.misconceptions)>=1,
          two_worked_teacher_examples=len(lesson.worked_examples)>=2,
          three_no_answer_hint_levels=len(lesson.hint_ladder)>=3,
          near_far_transfer=bool(lesson.transfer.near and lesson.transfer.far),
          project_license=lesson.provenance.permission=="PROJECT_AUTHORED",
          safe_teacher_visibility=lesson.teacher_solution_visibility=="TEACHER_ONLY"
        )
        need(all(checks.values()),"content structure missing "+doc["id"])
        rows.append(dict(id=doc["id"],kind=doc["kind"],status="REVIEW_PENDING",
                         teacher_approved=False,student_authoritative=False,
                         general_proof_certified=False,field_checks=checks,
                         machine_structure_completeness=sum(checks.values())/len(checks)))
    result=dict(
      batch=110,scope="MACHINE_AUDIT_NO_OFFICIAL_ATOM_DENOMINATOR",
      source_pdf_pages_total=61,
      source_pages_with_editorial_line_partitions=len(scoped_pages),
      editorial_line_partition_coverage=len(scoped_pages)/61,
      official_teacher_full_page_atomizations=0,
      source_pages_partially_editorially_partitioned=[
         dict(printed_page=p,pdf_page_index=pages[p]["pdf_page_index"],
              pdfkit_sha256=pages[p]["pdfkit_text_sha256"],line_count=scoped_pages[p],
              teacher_full_page_review="PENDING") for p in sorted(scoped_pages)],
      source_pages_not_in_three_batch_comparison=sorted(set(pages)-set(scoped_pages)),
      editorial_source_structural_partitions=partition_count,
      provisional_candidates_in_these_three_batches=len(candidates),
      provisional_candidate_counts_by_track={t:counts[t] for t in TRACKS},
      official_atom_coverage_by_track={t:dict(total=None,draft=None,approved=0,
                                              coverage_fraction=None,missing_total="UNKNOWN")
                                     for t in TRACKS},
      current_batch_lesson_completeness=rows,
      new_lesson_structural_complete=len(rows),
      new_lesson_teacher_approved=0,
      general_proof_certificates=0,
      arbitrary_student_solution_verified=0,
      legacy_debt=dict(unverified_prerequisite_labels=172,
                       uncertified_historical_proof_steps=538,
                       unresolved_math_conflicts=10),
      source_registry_sha256=sha256(SOURCE.read_bytes()).hexdigest(),
      limitations=[
        "6/61 is only the three latest batches' source-line partition coverage, not total historical or teacher-approved page audit.",
        "The 60 source candidates are not 60 official atoms and do not define a valid curricular denominator.",
        "All twelve machine field checks are syntax/structure completeness, not mathematical correctness or teacher review.",
        "All seven official atomic coverage fractions intentionally remain null until authoritative per-track denominators exist."
      ])
    return result

def markdown(obj):
    lines=["# Batch110｜七轨原子分母与教学内容完整度事实矩阵","",
      "官方七轨知识原子分母尚未建立，全部覆盖分数必须保持 UNKNOWN。",
      "工程源页61页与知识原子数量没有可替代关系。","",
      f"最近三批仅比较{obj['source_pages_with_editorial_line_partitions']}/61页的连续文本结构；"
      f"{obj['provisional_candidates_in_these_three_batches']}条为编辑候选，不是官方原子。","",
      "## 课程轨道分母","",
      "| 轨道 | 编辑候选（三批） | 官方原子分母 | 教师批准 |",
      "|---|---:|---|---:|"]
    for t,d in obj["official_atom_coverage_by_track"].items():
        lines.append(f"| {t} | {obj['provisional_candidate_counts_by_track'][t]} | UNKNOWN | {d['approved']} |")
    lines.extend(["","## 本批8份教学草案的机器结构完整性（不是数学证明审定）",""])
    for r in obj["current_batch_lesson_completeness"]:
        lines.append(f"- {r['id']}：字段{len(r['field_checks'])}/{len(r['field_checks'])}，"
                     f"状态{r['status']}，教师批准0，学生权威发布0。")
    lines.extend(["","## 仍未清零的历史风险","",
        "172条先修标签待语义复核、538条历史证明步骤未认证、10项数学冲突待裁决。","",
        "后续应对61页逐页建立可信原子候选清单，并由教师逐条核对和冻结版本；"
        "再以有效七轨分母进行课程缺口计算。",""])
    return "\n".join(lines).rstrip()+"\n"

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    args=p.parse_args();obj=build()
    for path,value in ((OUT,serialize(obj)),(MD,markdown(obj))):
        if args.check:need(path.read_text(encoding="utf8")==value,"artifact drift "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(value,encoding="utf8")
    print("Batch110 coverage PASS: 7 denominators UNKNOWN, 8 lesson structures complete, 0 teacher approvals")
if __name__=="__main__":main()
