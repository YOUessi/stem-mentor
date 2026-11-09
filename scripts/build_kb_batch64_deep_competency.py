#!/usr/bin/env python3
"""Batch64 teacher-only draft lessons and non-atom competency coverage *proposals*.

Do not confuse sample assessments with syllabus coverage or teacher approval.
No copyrighted curriculum text, student data or teacher signatures are emitted.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from collections import Counter
import build_kb_batch63_atom_context as C
import build_kb_batch62_anchor_triage as B62

ROOT=Path(__file__).resolve().parents[1]
LESSONS=ROOT/"knowledge/editorial_review/kb_batch64_deep_lessons.json"
MATRIX=ROOT/"docs/evaluation/KB_BATCH64_LESSON_MATRIX.json"
ABILITY=ROOT/"curriculum/highschool_math/k00_batch64_competency_proposal_matrix.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH64_CONTENT_AND_COMPETENCY.md"
SECTIONS=ROOT/"docs/evaluation/KB_BATCH62_NONATOM_REQUIREMENTS.json"
SCHEMA={"lesson_id","loc","title","kind","statement","assumptions","notation",
        "prerequisites","reasoning","examples","counterexample","wrong","why_wrong",
        "hints","near","far","source_license","teacher_review","student_publishable",
        "proof_certification","student_answer_verified","teacher_solution_visibility"}
STATUS={"source_license":"PROJECT_AUTHORED","teacher_review":"REVIEW_PENDING",
        "student_publishable":False,"proof_certification":"NOT_FORMALLY_CERTIFIED",
        "student_answer_verified":False,"teacher_solution_visibility":"TEACHER_ONLY"}
# These are *hypothesized classroom samples* under 14 section headings.
# They cannot establish every unnumbered official requirement or its equivalence.
# Each entry proposes exactly two manuscript example links, not two approved ability measures.
ABILITY_MAP=[
 ("KB64-DEEP-01","KB64-DEEP-02"),
 ("KB64-DEEP-04","KB64-DEEP-05"),
 ("KB64-DEEP-01","KB64-DEEP-03"),
 ("KB64-DEEP-06","KB64-DEEP-07"),
 ("KB64-DEEP-06","KB64-DEEP-10"),
 ("KB64-DEEP-12","KB64-DEEP-14"),
 ("KB64-DEEP-14","KB64-DEEP-12"),
 ("KB64-DEEP-12","KB64-DEEP-14"),
 ("KB64-DEEP-11","KB64-DEEP-05"),
 ("KB64-DEEP-11","KB64-DEEP-13"),
 ("KB64-DEEP-11","KB64-DEEP-03"),
 ("KB64-DEEP-13","KB64-DEEP-06"),
 ("KB64-DEEP-13","KB64-DEEP-10"),
 ("KB64-DEEP-13","KB64-DEEP-11"),
]
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
        "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
def require(ok,msg):
    if not ok: raise ValueError(msg)
def canonical(obj):
    return json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
def get(path):
    return json.loads(path.read_text(encoding="utf-8"))
def build(lessons=None,source=None,sections=None):
    lessons=deepcopy(get(LESSONS) if lessons is None else lessons)
    source=deepcopy(C.build() if source is None else source)
    sections=deepcopy(get(SECTIONS) if sections is None else sections)
    require(type(lessons) is list and len(lessons)==14,"exactly fourteen authored lessons required")
    require(sections["total_sections"]==14 and len(sections["rows"])==14,"section ledger changed")
    require(source["official_atomic_denominator"]=={t:None for t in TRACKS},
            "provisional source denominator must remain unknown")
    candidates={}
    for a in source["proposals"]:
        candidates.setdefault(a["parent_anchor_id"],[]).append(a)
    seen=set();matrix=[]
    for i,lesson in enumerate(lessons,1):
        require(type(lesson) is dict and set(lesson)==SCHEMA,"typed manuscript schema mismatch")
        key=f"KB64-DEEP-{i:02d}"
        require(lesson["lesson_id"]==key and key not in seen,"duplicate or out-of-order lesson ID")
        seen.add(key)
        require(all(type(lesson[k]) is type(v) and lesson[k]==v for k,v in STATUS.items()),
                "approval/certification/visibility forgery")
        require(lesson["kind"] in {"CONCEPT","METHOD","THEOREM_CANDIDATE"},
                "unsupported content type")
        require(type(lesson["loc"]) is list and len(lesson["loc"])==2 and
                all(type(n) is int for n in lesson["loc"]),"bad source coordinate")
        p,n=lesson["loc"];anchor=f"KB61-P{p:03d}-L{n:03d}"
        pair=candidates.get(anchor,[])
        require(len(pair)==2 and all(a["official_atomic_membership"]=="UNDETERMINED" and
                    a["teacher_review"]=="REVIEW_PENDING" and
                    a["student_publishable"] is False for a in pair),
                "source origin not a valid provisional candidate")
        require(len({a["source_window_sha256"] for a in pair})==1,
                "source evidence disagreement")
        for k,minlen in (("title",9),("statement",32),("counterexample",20),
                         ("wrong",12),("why_wrong",16),("near",10),("far",12)):
            require(type(lesson[k]) is str and len(lesson[k])>=minlen,
                    "insufficient original content: "+k)
        for k,n_min in (("assumptions",2),("notation",1),("prerequisites",2)):
            value=lesson[k]
            require(type(value) is list and len(value)>=n_min and
                    all(type(v) is str and len(v)>=3 for v in value),
                    "missing mathematical field "+k)
        steps=lesson["reasoning"]
        require(type(steps) is list and len(steps)>=3 and all(
                    type(s) is list and len(s)==2 and
                    all(type(x) is str and len(x)>= (12 if j==0 else 5) for j,x in enumerate(s)) for s in steps),
                "missing independent step justification")
        examples=lesson["examples"]
        require(type(examples) is list and len(examples)>=2 and all(
                    type(e) is list and len(e)==3 and all(type(x) is str and
                    len(x)>= (1 if j==1 else 8) for j,x in enumerate(e))
                    for e in examples),
                "incomplete worked example or answer check")
        hints=lesson["hints"]
        require(type(hints) is list and len(hints)==3 and all(
                    type(h) is str and len(h)>=10 for h in hints),"three hints required")
        matrix.append(dict(lesson_id=key,source_anchor_id=anchor,
            original_provenance_sha256=pair[0]["source_window_sha256"],
            hypothesized_atom_ids=[a["candidate_id"] for a in pair],
            teacher_examples=len(examples),step_justifications=len(steps),
            counterexample=True,three_hints=True,near_far=True,
            official_membership_confirmed=False,certified_general_proof=False,
            real_teacher_approved=False,student_visible=False,
            unresolved_math_equivalence=True,source_full_clause_reviewed=False))
    require([s["anchor_id"] for s in sections["rows"]]==[
            f"KB61-P{r['printed_page']:03d}-L{int(r['anchor_id'].split('-L')[1]):03d}"
            for r in sections["rows"]],"section identities changed")
    require(len(ABILITY_MAP)==14 and all(len(v)==2 and v[0]!=v[1]
                    for v in ABILITY_MAP),"ability sample map invalid")
    links=[]
    for i, (section, pair) in enumerate(zip(sections["rows"],ABILITY_MAP),1):
        require(section["coverage_status"]=="UNMAPPED" and
                section["review_status"]=="REVIEW_PENDING" and
                section["teacher_approved"] is False and
                section["unnumbered_requirements_checked"] is False and
                section["numbered_atom_membership"]=="NOT_A_STANDALONE_ATOM",
                "section authority or content status altered")
        require(section["category"] in {"COMPETENCY_BLOCK","PEDAGOGY_BLOCK","CONTENT_BLOCK"},
                "invalid curriculum evidence category")
        for j,key in enumerate(pair,1):
            require(key in seen,"orphan proposed manuscript")
            links.append(dict(proposal_id=f"KB64-COMP-{i:02d}-P{j}",
                official_section_anchor=section["anchor_id"],
                section_kind=section["category"],
                section_source_line_sha256=section["source_line_sha256"],
                proposed_lesson_id=key,
                proposed_example_id=key+f"-E{j:02d}",
                linkage_kind="EDITORIAL_SAMPLE_NOT_OFFICIAL_REQUIREMENT_MAPPING",
                abilities_covered=False,unnumbered_objectives_reviewed=False,
                rubric_independently_validated=False,teacher_approved=False,
                student_visible=False,coverage_status="UNMAPPED"))
    manuscript_sha=hashlib.sha256(LESSONS.read_bytes()).hexdigest() if lessons==get(LESSONS) else None
    report=dict(schema_version="kb64-teacher-only-manuscript-v1",
        draft_count=len(matrix),teacher_example_count=sum(x["teacher_examples"] for x in matrix),
        justified_steps=sum(x["step_justifications"] for x in matrix),
        authored_counterexamples=len(matrix),hint_tiers=3*len(matrix),
        manuscript_sha256=manuscript_sha,
        previous_batch_proposals_sha256=hashlib.sha256(C.OUT.read_bytes()).hexdigest(),
        pending_teacher_reviews=14,certified_general_proofs=0,student_published=0,
        confirmed_curriculum_coverage_atoms=0,official_denominators={t:None for t in TRACKS},
        rows=matrix)
    competency=dict(schema_version="kb64-competency-provisional-links-v1",
        source_ledger_sha256=hashlib.sha256(SECTIONS.read_bytes()).hexdigest(),
        blocks=len(sections["rows"]),links_count=len(links),
        abilities_certified=0,official_content_atoms_added=0,
        all_nonatom_sections_still_unmapped=True,teacher_approvals=0,
        student_visible=0,links=links)
    return report,competency
def validate(report,competency):
    require((report,competency)==build(),"matrix drift or fabricated authority")
    require(report["confirmed_curriculum_coverage_atoms"]==0 and
            report["certified_general_proofs"]==0 and report["student_published"]==0,
            "unsafe math or publication claim")
    require(competency["all_nonatom_sections_still_unmapped"] is True and
            competency["abilities_certified"]==competency["teacher_approvals"]==0,
            "unsafe competence mapping claim")
def render(report,comp):
    lessons=get(LESSONS)
    lines=["# Batch64｜14篇教师待审深度数学讲义与14个非原子课程栏目能力样例",
        "","**所有内容为原创、未获真实教师签核的教学草案；14份讲义不是正式课标知识原子，28个关联边不是28条学业要求，更不能提升七轨分母。**",
        "",f"- 讲义：{report['draft_count']}；教师例题：{report['teacher_example_count']}；有依据的推演步骤：{report['justified_steps']}；明确反例：{report['authored_counterexamples']}；提示：{report['hint_tiers']}。",
        f"- 课程非原子栏：{comp['blocks']}；教学例题候选关联：{comp['links_count']}；已经证明能力达标：0；学业要求独立审查：仍未完成。",
        "- 学生可发布：0；真实教师批准：0；一般数学证明形式认证：0；正式原子分母：全部未知。","",
        "| ID | 原创主题 | 候选来源 | 类型 | 状态 |","|---|---|---|---|---|"]
    for row,lesson in zip(report["rows"],lessons):
        lines.append(f"| {row['lesson_id']} | {lesson['title']} | {row['source_anchor_id']} | {lesson['kind']} | REVIEW_PENDING |")
    lines.extend(["","## 14个非知识原子来源栏：仅提交候选例题关联，不声称覆盖","",
                  "| 课标来源栏目 | 类别 | 候选教师侧例题（仅审核队列） | 覆盖状态 |",
                  "|---|---|---|---|"])
    for i in range(comp["blocks"]):
        first,second=comp["links"][2*i:2*i+2]
        lines.append(f"| {first['official_section_anchor']} | {first['section_kind']} | {first['proposed_example_id']}, {second['proposed_example_id']} | UNMAPPED |")
    lines.extend(["","## 发布/校验声明","",
        "- 只有有限枚举、精确分数或符号有界核查可标示为受控计算见证；本批不可把样例运算当作教师或一般定理证据。",
        "- 候选例题绑定的只是课程栏目坐标；必须后续阅读栏目全文、未编号要求并做教师确认才可确认能力覆盖。",
        "- 不写入批准索引，不把教师完整解答交给自由挑战状态下的学生。"])
    return "\n".join(lines)+"\n"
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    ap.add_argument("--verify-local",action="store_true",help="Reverify licensed local PDFKit page windows only on Mac")
    args=ap.parse_args()
    m,c=build()
    if args.verify_local:
        require(C.make_windows()==C.B61.load(C.WINDOWS),"original Mac PDFKit source mismatch")
    validate(m,c)
    expected=[(MATRIX,canonical(m)),(ABILITY,canonical(c)),(REPORT,render(m,c))]
    if args.check:
        for path,value in expected:
            require(path.exists() and path.read_text(encoding="utf-8")==value,
                    "stale or corrupted artifact "+str(path))
    else:
        for path,value in expected:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(value,encoding="utf-8")
    print("OK: 14 teacher-only lessons; 28 original worked examples; 42 reasoned steps; 14 nonatom sections still UNMAPPED; 28 tentative links; zero approvals/published")
if __name__=="__main__":
    main()
