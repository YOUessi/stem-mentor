#!/usr/bin/env python3
"""Batch63 risk-lesson manuscript gate. No teacher approvals are synthesized."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import build_kb_batch63_atom_context as C

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"knowledge/editorial_review/kb_batch63_risk_conditions.json"
COVER=ROOT/"docs/evaluation/KB_BATCH63_RISK_LESSON_MATRIX.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH63_RISK_LESSONS.md"
LOCATIONS=[(16,24),(16,16),(17,12),(20,13),(22,12),(22,27),
           (26,13),(26,20),(27,8),(28,5),(31,10),(58,35)]
REQUIRED={"lesson_id","loc","title","kind","statement","assumptions","notation",
          "prerequisites","reasoning","counterexample","examples",
          "wrong","why_wrong","hints","near","far","source_license",
          "teacher_review","student_publishable","proof_certification",
          "student_answer_verified","teacher_solution_visibility"}
STATUS={"source_license":"PROJECT_AUTHORED","teacher_review":"REVIEW_PENDING",
        "student_publishable":False,"proof_certification":"NOT_FORMALLY_CERTIFIED",
        "student_answer_verified":False,"teacher_solution_visibility":"TEACHER_ONLY"}
def require(ok,msg):
    if not ok:raise ValueError(msg)
def canonical(v):
    return json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
def load():
    return json.loads(SEED.read_text(encoding="utf-8"))
def build(lessons=None,atom_manifest=None):
    lessons=deepcopy(load() if lessons is None else lessons)
    atom_manifest=deepcopy(C.build() if atom_manifest is None else atom_manifest)
    require(len(lessons)==len(LOCATIONS)==12,"expected 12 substantive original lessons")
    known={}
    for p in atom_manifest["proposals"]:
        known.setdefault(p["parent_anchor_id"],[]).append(p)
    need=set();out=[]
    for n,item in enumerate(lessons,1):
        require(set(item)==REQUIRED,f"lesson {n} missing/extra schema field")
        require(item["lesson_id"]==f"KB63-RISK-{n:02d}","wrong lesson ID or order")
        require(tuple(item["loc"])==LOCATIONS[n-1],"lesson source coordinate drift")
        require(item["lesson_id"] not in need,"duplicate manuscript")
        need.add(item["lesson_id"])
        require(all(item[k]==v for k,v in STATUS.items()),"forged approval, math proof or visibility")
        require(item["kind"] in {"CONCEPT","METHOD","THEOREM_CANDIDATE"},
                "unsupported content kind")
        for key,minlen in [("title",9),("statement",38),("counterexample",25),
                           ("wrong",12),("why_wrong",20),("near",10),("far",12)]:
            require(type(item[key]) is str and len(item[key])>=minlen,
                    "underwritten content "+key)
        for key,n_min in [("assumptions",2),("notation",1),("prerequisites",2)]:
            a=item[key]
            require(type(a) is list and len(a)>=n_min and
                    all(type(s) is str and len(s)>= (1 if key=="notation" else 2) for s in a),key+" missing")
        steps=item["reasoning"]
        require(type(steps) is list and len(steps)>=3 and
                all(type(s) is list and len(s)==2 and
                    len(s[0])>=12 and len(s[1])>=6 for s in steps),
                "unjustified step or incomplete derivation")
        require(type(item["hints"]) is list and len(item["hints"])==3 and
                all(type(s) is str and len(s)>=12 for s in item["hints"]),
                "three progressive hints required")
        examples=item["examples"]
        require(type(examples) is list and len(examples)>=2 and
                all(type(e) is list and len(e)==3 and
                    len(e[0])>=8 and len(e[1])>=1 and len(e[2])>=10
                    for e in examples),
                "2 worked examples with answer and check required")
        page,line=item["loc"];source_id=f"KB61-P{page:03d}-L{line:03d}"
        require(source_id in known and len(known[source_id])==2,
                "missing source-attested editorial candidate")
        src=known[source_id]
        require(all(p["official_atomic_membership"]=="UNDETERMINED" and
                    p["content_lesson_complete"] is False and
                    p["teacher_review"]=="REVIEW_PENDING" for p in src),
                "source split falsely promoted")
        out.append(dict(lesson_id=item["lesson_id"],teacher_only_manuscript_present=True,
            original_claim=item["statement"],kind=item["kind"],
            source_anchor_id=source_id,source_provisional_atom_ids=[p["candidate_id"] for p in src],
            source_window_sha256=src[0]["source_window_sha256"],
            source_link_status="PROVISIONAL_SCOPE_ONLY_NOT_ATOM_EQUIVALENCE",
            structured_assumptions_count=len(item["assumptions"]),
            justified_reasoning_steps=len(steps),
            worked_examples=len(examples),common_error_present=True,
            counterexample_present=True,hint_depth=len(item["hints"]),
            near_and_far_transfer_present=True,
            independent_math_general_proof_certified=False,
            automatic_content_review_passed=True,
            original_curriculum_goal_fully_matched=False,
            real_teacher_approved=False,student_publishable=False,
            risk_lesson_still_review_pending=True))
    return dict(schema_version="kb63-risk-manuscript-matrix-v1",
        manuscript_sha256=sha256(SEED.read_bytes()).hexdigest(),
        source_candidate_manifest_sha256=sha256(C.OUT.read_bytes()).hexdigest(),
        teacher_only_lessons=len(out),
        minimum_worked_examples=sum(r["worked_examples"] for r in out),
        justified_steps=sum(r["justified_reasoning_steps"] for r in out),
        negative_counterexamples=sum(r["counterexample_present"] for r in out),
        total_hints=sum(r["hint_depth"] for r in out),
        curriculum_equivalences_confirmed=0,formal_general_proofs_certified=0,
        teacher_approvals=0,student_visible_lessons=0,
        original_teacher_side_content_not_indexed_for_students=True,
        rows=out)
def validate(m):
    require(m==build(),"content matrix deviates from teacher-only original manuscripts")
    require(m["teacher_approvals"]==0 and m["student_visible_lessons"]==0 and
            m["curriculum_equivalences_confirmed"]==0 and
            m["formal_general_proofs_certified"]==0 and
            m["original_teacher_side_content_not_indexed_for_students"] is True,
            "invalid authority claim")
def render(m):
    rows=load()
    lines=["# Batch63｜12篇原创高风险数学条件讲义（教师待审）","",
       "以下所有讲义都只是原创教师侧草案：**不属于已完成官方课标覆盖，不具有教师签核，不向学生教学Agent索引发布，也不认证一般定理。**","",
       f"- 讲义：{m['teacher_only_lessons']}；教师例题：{m['minimum_worked_examples']}；逐步理由：{m['justified_steps']}；反例：{m['negative_counterexamples']}；提示阶梯：{m['total_hints']}。","",
       "| 讲义ID | 课程候选来源 | 原创主题 | 类型 | 状态 |","|---|---|---|---|---|"]
    for row,check in zip(rows,m["rows"]):
        lines.append(f"| {row['lesson_id']} | {check['source_anchor_id']} | {row['title']} | {row['kind']} | REVIEW_PENDING |")
    lines.extend(["","## 审核要点与禁区","",
       "- 每篇均包含至少三段有独立依据的演算/证明步骤、两个教师例题、条件反例、典型误解、三级启发和近远迁移。",
       "- 示例核对和有限实例证据只说明受控具体计算正确，**不能**替代普遍定理的证明或教研签核。",
       "- 第35页流程图尚缺图像人工鉴定；31处来源窗口未完成跨页、未编号内容与等价审核。",
       "- 正式学生RAG仅加载经过独立验证的有效教师审核签名内容，以上12份文件不得发布。",""])
    return "\n".join(lines)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    m=build();validate(m)
    if args.check:
        require(COVER.read_text(encoding="utf-8")==canonical(m),"stale matrix")
        require(REPORT.read_text(encoding="utf-8")==render(m),"stale summary")
    else:
        COVER.write_text(canonical(m),encoding="utf-8")
        REPORT.write_text(render(m),encoding="utf-8")
    print(f"Batch63 {m['teacher_only_lessons']} draft manuscripts, {m['minimum_worked_examples']} worked examples, {m['justified_steps']} reasoned steps; zero approvals")
if __name__=="__main__":
    main()
