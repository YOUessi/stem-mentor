#!/usr/bin/env python3
"""Batch65: complete teacher manuscript proposals for the 31 substantive *candidate* scopes.

31/31 is an internal editorial queue denominator, NOT the curriculum's official atomic
denominator, mathematical certification, student availability or teacher approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
import build_kb_batch64_deep_competency as B64
import build_kb_batch63_atom_context as B63

ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / "knowledge/editorial_review/kb_batch65_remaining_substantive_lessons.json"
MATRIX = ROOT / "docs/evaluation/KB_BATCH65_REMAINING_SCOPE_MANIFEST.json"
TEACHER_INDEX = ROOT / "knowledge/editorial_review/kb_batch65_teacher_only_index.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH65_REMAINING_SCOPE_MANUSCRIPTS.md"
TRACKS = ("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
STATUS = B64.STATUS
SCHEMA = B64.SCHEMA

def require(ok: bool, msg: str):
    if not ok: raise ValueError(msg)

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def anchor_of(lesson):
    page, line = lesson["loc"]
    return f"KB61-P{page:03d}-L{line:03d}"

def build(new=None, old=None, source=None):
    new = deepcopy(load(LESSONS) if new is None else new)
    old = deepcopy(B64.get(B64.LESSONS) if old is None else old)
    source = deepcopy(B63.build() if source is None else source)
    require(type(new) is list and len(new)==17, "must have 17 original new manuscripts")
    require(type(old) is list and len(old)==14, "must retain all 14 prior manuscripts")
    require(source["provisional_candidate_count"]==62 and
            source["parent_substantive_scopes"]==31, "provisional source queue changed")
    require(source["official_atomic_denominator"]=={t: None for t in TRACKS},
            "official seven-track denominators are not yet known")
    parents = {}
    for cand in source["proposals"]:
        require(cand["teacher_review"]=="REVIEW_PENDING" and
                cand["official_atomic_membership"]=="UNDETERMINED" and
                cand["math_equivalence"]=="NOT_REVIEWED" and
                cand["full_source_context_verified"] is False and
                cand["student_publishable"] is False, "candidate has unreviewed authority drift")
        parents.setdefault(cand["parent_anchor_id"], []).append(cand)
    require(len(parents)==31 and all(len(v)==2 for v in parents.values()),
            "source parents must each have exactly two candidate atom hypotheses")
    rows=[]; indexed=[]; seen=set(); ids=set(); count_examples=0; count_steps=0
    for batch, entries in (("64",old),("65",new)):
        for i,lesson in enumerate(entries,1):
            require(type(lesson) is dict and set(lesson)==SCHEMA,
                    "manuscript schema mismatch")
            require(lesson["lesson_id"]==f"KB{batch}-DEEP-{i:02d}",
                    "manuscript ID/order invalid")
            require(all(type(lesson[k]) is type(v) and lesson[k]==v for k,v in STATUS.items()),
                    "illegal student publishing, unlicensed source or forged teacher certification")
            require(lesson["kind"] in {"CONCEPT","METHOD","THEOREM_CANDIDATE"},
                    "invalid lesson type")
            require(type(lesson["loc"]) is list and len(lesson["loc"])==2
                    and all(type(x) is int and x>0 for x in lesson["loc"]),
                    "bad source position")
            anchor=anchor_of(lesson)
            require(anchor in parents and anchor not in seen, "missing or duplicated source scope")
            require(lesson["lesson_id"] not in ids, "duplicate lesson id")
            seen.add(anchor);ids.add(lesson["lesson_id"])
            cands=parents[anchor]
            require(len({c["source_window_sha256"] for c in cands})==1,
                    "different source hash among atom hypotheses")
            for key, minimum in (("title",9),("statement",32),("counterexample",20),
                                 ("wrong",12),("why_wrong",16),("near",10),("far",12)):
                require(type(lesson[key]) is str and len(lesson[key])>=minimum,
                        "manuscript is shallow: "+key)
            for key,n in (("assumptions",2),("notation",1),("prerequisites",2)):
                require(type(lesson[key]) is list and len(lesson[key])>=n and
                        all(type(x) is str and len(x)>=3 for x in lesson[key]),
                        "invalid mathematical prerequisites/notation")
            require(type(lesson["reasoning"]) is list and len(lesson["reasoning"])>=3 and
                    all(type(v) is list and len(v)==2 and
                    all(type(z) is str and len(z)>=(12 if idx==0 else 5) for idx,z in enumerate(v))
                    for v in lesson["reasoning"]), "step or justification missing")
            require(type(lesson["examples"]) is list and len(lesson["examples"])>=2 and
                    all(type(v) is list and len(v)==3 and
                    all(type(z) is str and len(z)>=(1 if idx==1 else 8) for idx,z in enumerate(v))
                    for v in lesson["examples"]), "worked problem, answer or proof missing")
            require(type(lesson["hints"]) is list and len(lesson["hints"])==3 and
                    all(type(v) is str and len(v)>=10 for v in lesson["hints"]),
                    "three gradual hints required")
            count_examples += len(lesson["examples"]); count_steps += len(lesson["reasoning"])
            r={"lesson_id":lesson["lesson_id"],"title":lesson["title"],
               "source_anchor_id":anchor,"source_window_sha256":cands[0]["source_window_sha256"],
               "candidate_atom_hypotheses":[v["candidate_id"] for v in cands],
               "examples":len(lesson["examples"]),"reasoned_steps":len(lesson["reasoning"]),
               "provisional_parent_covered_by_manuscript":True,
               "full_source_clause_reviewed":False,
               "cross_page_math_equivalence_verified":False,
               "official_atom_membership_confirmed":False,"teacher_approved":False,
               "student_publishable":False,"general_theorem_formally_certified":False}
            rows.append(r)
            # Teacher-only search support; never add these to approved/student indices.
            indexed.append({"id":lesson["lesson_id"],"title":lesson["title"],
                            "scope":anchor,"source_sha256":cands[0]["source_window_sha256"],
                            "keywords":[lesson["title"],*lesson["notation"],*lesson["prerequisites"]],
                            "access":"TEACHER_ONLY","review":"REVIEW_PENDING",
                            "teacher_solution_visibility":"TEACHER_ONLY",
                            "student_retrievable":False,"certified":False})
    require(len(seen)==31 and set(parents)==seen,
            "missing substantive scope: teacher-only draft queue not complete")
    require(len(ids)==31 and len(indexed)==31, "duplicate draft")
    result={"schema_version":"kb65-substantive-scope-editorial-v1",
            "parent_substantive_scopes":31,"provisional_atom_hypotheses":62,
            "prior_teacher_manuscripts":14,"new_teacher_manuscripts":17,
            "scopes_with_at_least_one_teacher_manuscript":len(rows),
            "original_examples":count_examples,"reasoned_steps":count_steps,
            "source_manifest_sha256":hashlib.sha256(B63.OUT.read_bytes()).hexdigest(),
            "new_manuscripts_sha256":hashlib.sha256(LESSONS.read_bytes()).hexdigest() if new==load(LESSONS) else None,
            "official_atomic_denominator":{t:None for t in TRACKS},
            "unmapped_competency_sections":14,
            "full_official_clauses_teacher_reviewed":0,
            "teacher_approved":0,"general_proofs_certified":0,"student_published":0,
            "remaining_candidate_parents_without_manuscript":0,
            "rows":rows}
    index={"schema_version":"kb65-teacher-search-only-v1","access":"TEACHER_ONLY",
           "student_index_write_permitted":False,"release_approved_count":0,
           "rows":indexed}
    return result,index

def render(matrix,index):
    lines=["# Batch65｜17份新增原创讲义：31/31个实质性候选范围均有教师草案",
           "","**注意：31是经过Batch63初步定位的内部候选范围，不是官方课标知识原子分母，"
           "62是拆分假设，绝不可记为官方完成。全部内容等待教师审核。**","",
           f"- 新增讲义 {matrix['new_teacher_manuscripts']}，累计本系列教师稿 {len(matrix['rows'])}；"
           f"原创新旧例题共 {matrix['original_examples']}、分步依据 {matrix['reasoned_steps']}。",
           "- 所有七轨官方分母为 null；完整来源条款教师审查0；数学一般证明认证0；"
           "学生正式发布0。14条能力栏目依然 UNMAPPED。","",
           "| ID | 课标来源坐标 | 讲义主题 | 教师签核 |",
           "|---|---|---|---|"]
    for r in matrix["rows"]:
        lines.append(f"| {r['lesson_id']} | {r['source_anchor_id']} | {r['title']} | REVIEW_PENDING |")
    lines.extend(["","## 工程与教师审核的边界","",
                  "- 每条讲义均有完整假设、原创数学陈述、逐步论证、至少两个已写答案与依据的例题、"
                  "典型错误、反例、分层提示及近远迁移。",
                  "- 数学正确性并不能由Schema保证：有界有限算例见证只验证对应输入，"
                  "内容仍等待独立的教师核对，不能自动授予APPROVED。",
                  "- 教师专用索引仅供编审，禁止将未批准讲义/答案同步到学生RAG或提示上下文。",
                  "- 下一批优先开展跨页真实语义去重、整页原子化、选修E课程范围教师裁决、"
                  "第35页图示审核、538条历史未认证证明步骤和10组冲突裁决。"])
    return "\n".join(lines)+"\n"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local",action="store_true")
    args=p.parse_args()
    if args.verify_local:
        require(B64.C.make_windows()==B64.C.B61.load(B64.C.WINDOWS),
                "Mac locked original source page evidence changed")
    m,i=build()
    for path,value in ((MATRIX,canonical(m)),(TEACHER_INDEX,canonical(i)),(REPORT,render(m,i))):
        if args.check: require(path.exists() and path.read_text(encoding="utf-8")==value,
                               "artifact changed: "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(value,encoding="utf-8")
    print(f"Batch65 OK: {m['new_teacher_manuscripts']} new, {len(m['rows'])}/31 provisional scopes;"
          " 0 official atoms certified; 0 teacher approvals; 0 students published")
if __name__=="__main__":
    main()
