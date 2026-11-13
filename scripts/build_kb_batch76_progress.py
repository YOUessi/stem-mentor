#!/usr/bin/env python3
"""Machine-auditable *project candidate* denominator; official denominator stays null."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import build_kb_batch76_equivalence as E
import build_kb_batch76_eight_lessons as T
import build_kb_batch75_lessons as B75

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"docs/evaluation/KB_BATCH76_CANDIDATE_COMPLETENESS.json"
MD=ROOT/"docs/evaluation/KB_BATCH76_CANDIDATE_COMPLETENESS.md"
FIELDS=("definition","symbols","assumptions","statement","reasoning_steps",
        "mathematical_validity","invalid_boundary","counterexample","common_wrong_method",
        "worked_examples","graduated_hints","near_transfer","far_transfer","prerequisite_topics")
def canon(x):return json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
def build():
 comp=E.audit();packs=T.build()
 old=json.loads(B75.OUT.read_text(encoding="utf8"))["teacher_drafts"]
 all_rows=old+packs["teacher_drafts"]
 by_anchor={}
 for row in all_rows:by_anchor.setdefault(row["source_editorial_subspan_id"],[]).append(row["id"])
 candidates=[]
 for source in comp["cases"]:
  ids=sorted(by_anchor.get(source["source_editorial_subspan_id"],[]))
  candidates.append(dict(candidate_id=source["source_editorial_subspan_id"],
    track_hint=source["track_hint"],source_sha256=source["source_subspan_sha256"],
    linked_review_only_teacher_draft_ids=ids,
    linked_teacher_draft_count=len(ids),teacher_approved=False,
    official_knowledge_atom=None,source_certified=False,
    publishing_allowed=False,full_teacher_clause_review=False))
 matrix=[]
 for row in packs["teacher_drafts"]:
  assert T.verify_case(row["finite_case"])
  present={k: bool(row.get(k)) for k in FIELDS}
  matrix.append(dict(lesson_id=row["id"],candidate_id=row["source_editorial_subspan_id"],
   track_hint=row["curriculum_track_hint"],required_field_presence=present,
   editorial_field_presence_count=sum(present.values()),editorial_field_count=len(FIELDS),
   bounded_exact_case_verified=True,number_of_worked_examples=len(row["worked_examples"]),
   number_of_reasoned_steps=len(row["reasoning_steps"]),
   prerequisites_linked_to_approved_ids=False,
   verified_universal_proof=False,teacher_review="REVIEW_PENDING",
   student_publishable=False,teacher_approved=False))
 counts=Counter(z["track_hint"] for z in candidates)
 with_lessons=Counter(z["track_hint"] for z in candidates if z["linked_teacher_draft_count"])
 out=dict(schema_version="kb76-honest-project-candidate-coverage-v1",
  syllabus_version="普通高中数学课程标准(2017年版2020年修订)",
  source_pdf_sha256=comp["source_pdf_sha256"],
  comparison_sha256=hashlib.sha256(E.OUT.read_bytes()).hexdigest(),
  lesson_pack_sha256=hashlib.sha256(T.OUT.read_bytes()).hexdigest(),
  candidate_denominator_scope="Only 26 Batch75 project atom candidates; NOT national standard denominator",
  candidate_denominator=26,
  candidate_with_any_review_only_teacher_draft=sum(bool(r["linked_teacher_draft_count"]) for r in candidates),
  candidate_without_draft=sum(not r["linked_teacher_draft_count"] for r in candidates),
  new_draft_count=8,bounded_exact_case_verified_count=8,
  approved_teacher_count=0,student_published_count=0,formal_proof_certified_count=0,
  fully_teacher_atomized_pages=0,
  official_full_denominators=comp["official_denominators"],
  by_track={t:dict(candidate_count=counts[t],with_review_only_teacher_draft=with_lessons[t],
                   official_denominator=None) for t in comp["official_denominators"]},
  candidates=candidates,lesson_completeness=matrix)
 validate(out);return out

def validate(x):
 comp=E.audit();pack=T.build()
 assert x["comparison_sha256"]==hashlib.sha256(E.OUT.read_bytes()).hexdigest()
 assert x["lesson_pack_sha256"]==hashlib.sha256(T.OUT.read_bytes()).hexdigest()
 assert x["candidate_denominator"]==len(x["candidates"])==26
 assert x["new_draft_count"]==len(x["lesson_completeness"])==8
 assert x["bounded_exact_case_verified_count"]==8
 assert x["candidate_with_any_review_only_teacher_draft"]+x["candidate_without_draft"]==26
 assert x["approved_teacher_count"]==x["student_published_count"]==x["formal_proof_certified_count"]==0
 assert x["fully_teacher_atomized_pages"]==0
 assert x["official_full_denominators"]==comp["official_denominators"]
 assert all(z is None for z in x["official_full_denominators"].values())
 assert sum(v["candidate_count"] for v in x["by_track"].values())==26
 assert sum(v["with_review_only_teacher_draft"] for v in x["by_track"].values())==x["candidate_with_any_review_only_teacher_draft"]
 assert all(v["official_denominator"] is None for v in x["by_track"].values())
 assert {r["candidate_id"] for r in x["candidates"]}=={r["source_editorial_subspan_id"] for r in comp["cases"]}
 assert all(r["official_knowledge_atom"] is None and not r["publishing_allowed"]
            and not r["source_certified"] and not r["teacher_approved"] for r in x["candidates"])
 old=json.loads(B75.OUT.read_text(encoding="utf8"))["teacher_drafts"]
 exact_links={}
 for r in old+pack["teacher_drafts"]:exact_links.setdefault(r["source_editorial_subspan_id"],set()).add(r["id"])
 for r in x["candidates"]:
  assert r["linked_review_only_teacher_draft_ids"]==sorted(exact_links.get(r["candidate_id"],set()))
  assert r["linked_teacher_draft_count"]==len(r["linked_review_only_teacher_draft_ids"])
 for item in x["lesson_completeness"]:
  assert item["lesson_id"] in {r["id"] for r in pack["teacher_drafts"]}
  assert item["editorial_field_count"]==len(FIELDS)
  assert item["editorial_field_presence_count"]==len(FIELDS)
  assert all(item["required_field_presence"].values())
  assert item["number_of_worked_examples"]==2 and item["number_of_reasoned_steps"]>=4
  assert item["bounded_exact_case_verified"] is True and item["teacher_review"]=="REVIEW_PENDING"
  assert not item["prerequisites_linked_to_approved_ids"] and not item["verified_universal_proof"]
  assert not item["teacher_approved"] and not item["student_publishable"]
 return True

def report(x):
 lines=["# Batch76｜26个项目候选的覆盖与审核状态（官方分母未知）","",
  "- **本矩阵分母仅是Batch75已有的26个候选**，不是中国高中数学的全部官方知识原子分母。",
  f"- 项目候选已有关联教师草案 {x['candidate_with_any_review_only_teacher_draft']}/26；未关联 {x['candidate_without_draft']}/26。",
  "- 8篇新原创内容的14项字段均有稿件；8个有限精确算例通过；一般形式证明认证仍为0。",
  "- 教师签批0，学生发布0，61页完整课程原子化教师审核0；七轨官方分母全部null。",
  "", "| 轨道 | 候选数（非官方） | 有未批准教师稿 | 官方分母 |", "|---|---:|---:|---|"]
 for track,v in x["by_track"].items():
  lines.append(f"| {track} | {v['candidate_count']} | {v['with_review_only_teacher_draft']} | 未知 |")
 lines+=["","## 继续开发与人工审核","- 对未关联的候选先开展来源语义核验,区分真正缺失与跨页重复；不能从词面推定等价。",
        "- 独立教师复核八篇数学推导与边界，保留原稿仅供教师审阅。",
        "- 补齐61页官方逐条原子化分母后才可能计算国家课标完成比例。",""]
 return "\n".join(lines)
def main():
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
 x=build();m=report(x)
 if a.check:
  assert OUT.read_text(encoding="utf8")==canon(x)
  assert MD.read_text(encoding="utf8")==m
 else:OUT.write_text(canon(x),encoding="utf8");MD.write_text(m,encoding="utf8")
 print("KB76 candidate completeness",x["candidate_with_any_review_only_teacher_draft"],"/26 linked draft candidates, no official denominators")
if __name__=="__main__":main()
