#!/usr/bin/env python3
"""Review all 145 unpublished draft records for *structural* depth, not theorem truth.

No original syllabus text, teacher example, answer, or student data is emitted.
Does not equate field presence with pedagogical approval or proof verification.
"""
from __future__ import annotations
import argparse,json,re,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"backend"),str(ROOT/"scripts")]
from app import kb_batch154_index
import build_kb_batch155_review_matrix as matrix
import build_kb_batch155_eight_line_locks as eight

OUT=ROOT/"docs/evaluation/KB_BATCH155_DRAFT_FIELD_READINESS.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH155_DRAFT_FIELD_READINESS.md"
TRACKS=matrix.TRACKS
STRING_FIELDS=("formal_definition_or_theorem","notation_and_domain",
    "applicability_and_hypotheses","why_method_is_legal","nonexample_or_failure",
    "typical_wrong_solution","why_wrong_and_repair","near_transfer","far_transfer")
HASH=re.compile(r"[a-f0-9]{64}\Z")
def require(c,msg):
    if not c:raise ValueError("KB155 depth audit: "+msg)
def encode(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def check_one(r):
    cid=r.get("source_candidate_id",r.get("candidate_id"))
    require(isinstance(cid,str) and bool(cid),"draft source candidate missing")
    require(r.get("knowledge_type") in {"Concept","Theorem","Method"},"unrecognized draft knowledge type")
    require(r.get("course_track") in TRACKS,"draft course track unknown")
    require(r.get("teacher_review_status")=="REVIEW_PENDING" and
            r.get("teacher_solution_visibility")=="TEACHER_ONLY" and
            r.get("teacher_review_evidence") is None and not r.get("student_authoritative") and
            not r.get("formal_proof_certified") and not r.get("free_student_step_verified"),
            "counterfeit teacher approval/mathematical certification")
    require(HASH.fullmatch(r["source_pdf_sha256"]),"source PDF hash missing")
    for field in STRING_FIELDS:
        require(isinstance(r.get(field),str) and bool(r[field].strip()),"required depth field "+field)
    steps=r.get("reasoned_steps")
    require(isinstance(steps,list) and len(steps)>=4 and
            all(isinstance(t,dict) and bool(str(t.get("justification","")).strip()) for t in steps),
            "inadequate reasoned steps")
    examples=r.get("teacher_examples")
    require(isinstance(examples,list) and len(examples)>=2 and
            all(isinstance(e,dict) and bool(str(e.get("question","")).strip()) and
                bool(str(e.get("answer","")).strip()) and
                isinstance(e.get("reasoned_solution"),list) and
                len(e["reasoned_solution"])>=2 for e in examples),
            "incomplete teacher worked examples")
    hints=r.get("student_hint_ladder")
    require(isinstance(hints,list) and len(hints)>=3 and
            all(isinstance(t,str) and bool(t.strip()) for t in hints),
            "missing non-answer student hints")
    source_span=r.get("source_span_sha256")
    legacy_lock=r.get("source_line_lock")
    if source_span is None:
        require(isinstance(legacy_lock,dict) and HASH.fullmatch(legacy_lock.get("span_sha256","")),
                "no source span hash or valid legacy proof lock")
        source_span=legacy_lock["span_sha256"]
    else:
        require(HASH.fullmatch(source_span),"invalid source span SHA")
    if legacy_lock is not None:
        require(legacy_lock["span_sha256"]==source_span,
                "two different source locks")
    line_hashes=r.get("source_line_sha256")
    if line_hashes is None:
        line_hashes=legacy_lock.get("line_sha256") if isinstance(legacy_lock,dict) else None
    if line_hashes is None:
        prior={v["id"]:v for v in matrix.load(matrix.PROP)["records"]}
        if cid in prior:
            evidence=prior[cid]["source_lock"]
            line_hashes=evidence["line_sha256"]
            provenance="RECONCILED_FROM_EXISTING_41_PROPOSAL_SOURCE_LOCK"
            require(source_span==evidence["span_sha256"],"proposal source SHA drift")
        else:
            locks={v["source_candidate_id"]:v for v in matrix.load(eight.OUT)["locks"]}
            require(cid in locks,"missing eight Mac-rehashed evidence row")
            evidence=locks[cid]
            line_hashes=evidence["source_line_sha256"]
            provenance="RECONCILED_FROM_NEW_EIGHT_MAC_PDFKIT_REHASH"
            require(source_span==evidence["source_span_sha256"] and
                    r["source_pdf_sha256"]==evidence["source_pdf_sha256"],
                    "rehashed eight source SHA drift")
    else:
        provenance=("LEGACY_SOURCE_LINE_LOCK" if legacy_lock is not None else
                    "DIRECT_SOURCE_SPAN_AND_LINE_LOCK")
    require(isinstance(line_hashes,list) and len(line_hashes)>0 and
            all(HASH.fullmatch(v) for v in line_hashes),"source line hashes absent")
    return dict(draft_id=r["id"],candidate_id=cid,course_track=r["course_track"],
        knowledge_type=r["knowledge_type"],
        structural_fields_present=9,
        reasoned_step_count=len(steps),teacher_example_count=len(examples),
        student_hint_level_count=len(hints),near_transfer_present=True,far_transfer_present=True,
        source_provenance_shape=provenance,
        provenance_span_sha256=source_span,
        proof_status="NOT_FORMALLY_CERTIFIED",source_semantics_status="PENDING_HUMAN_REVIEW",
        teacher_review_status="REVIEW_PENDING",student_publishable=False)
def build():
    raw=kb_batch154_index.load()
    require(len(raw)==145 and len({r["id"] for r in raw})==145,"draft registry drift")
    source_matrix=matrix.build()
    matrix.validate(source_matrix)
    rows=[check_one(r) for r in raw]
    require(len({r["candidate_id"] for r in rows})==145,"duplicate manuscript source candidate")
    depth=matrix.load(matrix.DEPTH)
    audit_ids={r["id"] for r in depth["rows"]}
    require(audit_ids=={r["draft_id"] for r in rows},
            "authoritative 145 draft audit and reconstructed raw row differ")
    by_track={}
    for t in TRACKS:
        sub=[x for x in rows if x["course_track"]==t]
        require(len(sub)==depth["by_track"][t],"draft track count drift")
        by_track[t]=dict(teacher_pending_drafts=len(sub),
            concepts=sum(x["knowledge_type"]=="Concept" for x in sub),
            theorems=sum(x["knowledge_type"]=="Theorem" for x in sub),
            methods=sum(x["knowledge_type"]=="Method" for x in sub),
            full_structural_field_contract=sum(x["structural_fields_present"]==9 and
                x["reasoned_step_count"]>=4 and x["teacher_example_count"]>=2 and
                x["student_hint_level_count"]>=3 for x in sub),
            legacy_source_lock_shape=sum(x["source_provenance_shape"]==
                "LEGACY_SOURCE_LINE_LOCK" for x in sub),
            fully_math_certified=0,teacher_approved=0,student_authoritative=0,
            official_atom_denominator=None)
    legacy=Counter(z["source_provenance_shape"] for z in rows)
    return dict(schema="kb155-145-draft-structural-readiness-not-math-correctness/1",
        all_pending_manuscripts=145,all_drafts_with_full_field_presence=len(rows),
        per_draft_rows=rows,by_track=by_track,
        legacy_source_lock_shapes=legacy["LEGACY_SOURCE_LINE_LOCK"],
        direct_source_span_shapes=legacy["DIRECT_SOURCE_SPAN_AND_LINE_LOCK"],
        inherited_41_proposal_line_locks=legacy["RECONCILED_FROM_EXISTING_41_PROPOSAL_SOURCE_LOCK"],
        rehashed_eight_missing_line_locks=legacy["RECONCILED_FROM_NEW_EIGHT_MAC_PDFKIT_REHASH"],
        historical_audit_rows_with_null_source_sha=
            source_matrix["draft_audit_source_sha_null_count_before_reconciliation"],
        theoretical_proof_certifications=0,arbitrary_student_steps_certified=0,
        teacher_approved=0,student_authoritative=0,
        official_atom_denominators={t:None for t in TRACKS},
        completeness_meaning="PRESENCE_ONLY_MATHEMATICAL_TRUTH_NOT_CERTIFIED",
        teacher_review_complete=False)
def validate(v):
    require(v["schema"]=="kb155-145-draft-structural-readiness-not-math-correctness/1" and
       len(v["per_draft_rows"])==v["all_pending_manuscripts"]==
       v["all_drafts_with_full_field_presence"]==145,"draft census drift")
    require(v["legacy_source_lock_shapes"]+v["direct_source_span_shapes"]+
            v["inherited_41_proposal_line_locks"]+
            v["rehashed_eight_missing_line_locks"]==145 and
            v["rehashed_eight_missing_line_locks"]==8 and
            v["inherited_41_proposal_line_locks"]==35 and
       v["historical_audit_rows_with_null_source_sha"]==41,"source shape mismatch")
    require(v["completeness_meaning"]=="PRESENCE_ONLY_MATHEMATICAL_TRUTH_NOT_CERTIFIED" and
       not v["teacher_review_complete"] and
       v["theoretical_proof_certifications"]==v["arbitrary_student_steps_certified"]==
       v["teacher_approved"]==v["student_authoritative"]==0 and
       all(v["official_atom_denominators"][t] is None for t in TRACKS),
       "content completeness falsely turned into mathematical certification")
    require(len({r["draft_id"] for r in v["per_draft_rows"]})==145,"draft duplicated")
    for r in v["per_draft_rows"]:
        require(r["structural_fields_present"]==9 and
            r["reasoned_step_count"]>=4 and r["teacher_example_count"]>=2 and
            r["student_hint_level_count"]>=3 and
            r["teacher_review_status"]=="REVIEW_PENDING" and
            r["proof_status"]=="NOT_FORMALLY_CERTIFIED" and
            r["source_semantics_status"]=="PENDING_HUMAN_REVIEW" and
            not r["student_publishable"] and
            HASH.fullmatch(r["provenance_span_sha256"]),
            "shallow or authority-forged manuscript")
    return True
def render(x):
    t=["# KB155｜145份候审讲义的逐条结构门禁（不证明数学正确）","",
       "全部145份能找到9组核心讲义文本字段、≥4条分步理由、≥2道教师例题、≥3级学生提示及近远迁移；**字段齐全不等于定理已证或教师批准**。","",
       f"来源审计字段中有{x['historical_audit_rows_with_null_source_sha']}个旧提案source_sha为空：前置K00表按旧source_lock可追溯重建，但旧记录保持不变。"
       f"原始讲义的来源行SHA: 102份自身具备（其中{x['legacy_source_lock_shapes']}份使用旧字典）；另外35份继承已有41条暂定提案的锁定行SHA，8份在Mac本地真实重新哈希补齐。",
       "41条审计source_sha空值与43份讲义缺行SHA是不同维度，不可直接相加。","",
       "| 轨道 | 候审稿 | 概念 | 定理 | 方法 | 字段完整 | 数学正式认证 | 教师通过 |",
       "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for k in TRACKS:
        p=x["by_track"][k]
        t.append(f"| {k} | {p['teacher_pending_drafts']} | {p['concepts']} | {p['theorems']} | {p['methods']} | {p['full_structural_field_contract']} | 0 | 0 |")
    t+=["","需要教师后续对每项定理的前提和逐步证明、方法边界、题族迁移逐项审查；Student Agent不得直接索引教师解答。七轨课标正式原子分母仍UNKNOWN。","","逐条结果、来源哈希、数学证明未认证状态见同名JSON，无教学正文和版权课标原文。",""]
    return "\n".join(t)
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
    v=build();validate(v)
    targets=[(OUT,encode(v)),(REPORT,render(v))]
    if a.check:
        for p,raw in targets:require(p.exists() and p.read_text(encoding="utf-8")==raw,"audit drift "+str(p))
    else:
        for p,raw in targets:p.write_text(raw,encoding="utf-8")
    print(f"KB155: {len(v['per_draft_rows'])} editor-only manuscripts structurally readable; "
          "no theorem certification, teacher approval, or official completion.")
if __name__=="__main__":main()
