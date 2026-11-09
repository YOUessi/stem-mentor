#!/usr/bin/env python3
"""Batch66 independent capability rubrics + conservative cross-page hypothesis review.

These are original teacher-side assessment drafts. They DO NOT close the
14 unnumbered source sections and DO NOT establish the official denominators.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from copy import deepcopy
from itertools import combinations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TASKS=ROOT/"knowledge/editorial_review/kb_batch66_competency_assessments.json"
CROSS=ROOT/"curriculum/highschool_math/k00_batch64_competency_proposal_matrix.json"
CAND=ROOT/"curriculum/highschool_math/k00_batch63_provisional_atom_proposals.json"
ANCHORS=ROOT/"curriculum/highschool_math/k00_batch61_source_anchor_registry.json"
LESSON_MATRIX=ROOT/"docs/evaluation/KB_BATCH65_REMAINING_SCOPE_MANIFEST.json"
OUT=ROOT/"docs/evaluation/KB_BATCH66_AUDIT_MATRIX.json"
DUPS=ROOT/"docs/evaluation/KB_BATCH66_DUPLICATE_REVIEW_QUEUE.json"
INDEX=ROOT/"knowledge/editorial_review/kb_batch66_teacher_assessment_index.json"
BACKLOG=ROOT/"docs/evaluation/KB_BATCH66_ANCHOR_REVIEW_BACKLOG.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH66_ASSESSMENT_REVIEW.md"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))
def canon(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2)+"\n"
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,msg):
    if not ok: raise ValueError(msg)

def bigrams(text):
    s="".join(c for c in text if c.isalnum())
    return {s[i:i+2] for i in range(len(s)-1)}

def review_pairs(proposals):
    pairs=[]
    for a,b in combinations(proposals,2):
        if a["parent_anchor_id"]==b["parent_anchor_id"]: continue
        if a["source_page"]==b["source_page"]: continue
        x,y=bigrams(a["editorial_subtopic"]),bigrams(b["editorial_subtopic"])
        overlap=len(x&y)/len(x|y) if x|y else 0
        same_condition=a["known_math_failure_to_test"]==b["known_math_failure_to_test"]
        if overlap < .15 and not same_condition: continue
        pairs.append({"left":a["candidate_id"],"right":b["candidate_id"],
                      "left_page":a["source_page"],"right_page":b["source_page"],
                      "shared_failure_note":same_condition,
                      "editorial_bigram_overlap":round(overlap,4),
                      "review_status":"HYPOTHESIS_NOT_MATH_EQUIVALENCE",
                      "requires_full_clauses":True,"merge_permitted":False})
    pairs.sort(key=lambda r:(not r["shared_failure_note"],-r["editorial_bigram_overlap"],r["left"],r["right"]))
    return pairs

def build(cards=None):
    cards=deepcopy(load(TASKS) if cards is None else cards)
    cross=load(CROSS);source=load(CAND);registry=load(ANCHORS);lessons=load(LESSON_MATRIX)
    need(type(cards) is list and len(cards)==14,"exactly 14 original assessment drafts required")
    need(len(cross["links"])==28 and cross["blocks"]==14,"source competency sections changed")
    need(len(registry["rows"])==428 and len(source["proposals"])==62,"source anchors/atom hypotheses changed")
    need(lessons["scopes_with_at_least_one_teacher_manuscript"]==31,"lesson source mapping changed")
    need(all(lessons["official_atomic_denominator"][t] is None for t in TRACKS),
         "false official atom denominator")
    approved_ids=set()
    anchor_lookup={(r["printed_page"],r["pdfkit_line"]):r for r in registry["rows"]}
    linkage={l["proposal_id"].split("-P")[0]:l for l in cross["links"] if l["proposal_id"].endswith("-P1")}
    need(len(linkage)==14,"not exactly fourteen independent unnumbered-section links")
    rows=[];teacher_index=[];ids=set();keys=set()
    for n,card in enumerate(cards,1):
        need(type(card) is dict, "assessment not a record")
        need(card["id"]==f"KB66-ASM-{n:02d}" and card["id"] not in ids,"duplicate assessment id")
        ids.add(card["id"]);keys.add(card["witness_key"])
        need(card["source_license"]=="PROJECT_AUTHORED" and
             card["task_kind"]=="INDEPENDENT_TEACHER_ASSESSMENT_DRAFT" and
             card["section_alignment"]=="NOT_REVIEWED" and
             card["math_verification"]=="FINITE_CASE_WITNESS_ONLY" and
             card["teacher_review"]=="REVIEW_PENDING" and
             card["answer_visibility"]=="TEACHER_ONLY" and
             all(card[k] is False for k in ("student_publishable","student_answer_verified","general_theorem_certified")),
             "unapproved assessment has privileged or forged status")
        for f in ("domain","question","teacher_expected_answer","typical_wrong_answer",
                  "wrong_reason","near_transfer","far_transfer","counterexample_or_failure_boundary"):
            need(type(card[f]) is str and len(card[f])>=(4 if f=="domain" else 12),"assessment content is shallow: "+f)
        need(type(card["justification_steps"]) is list and len(card["justification_steps"])==3
             and all(type(s) is str and len(s)>=8 for s in card["justification_steps"]),
             "reasoned assessment steps missing")
        need(type(card["three_stage_hints"]) is list and len(card["three_stage_hints"])==3
             and all(type(s) is str and len(s)>=8 for s in card["three_stage_hints"]),
             "three progressive hints missing")
        rubric=card["scoring_rubric"]
        need(type(rubric) is list and len(rubric)==3 and
             all(type(r["points"]) is int and r["points"]>0 and len(r["criterion"])>=12 for r in rubric)
             and sum(r["points"] for r in rubric)==6,"independent six-point rubric missing")
        link=linkage[f"KB64-COMP-{n:02d}"]
        need(link["coverage_status"]=="UNMAPPED" and not link["abilities_covered"]
             and not link["teacher_approved"] and not link["rubric_independently_validated"],
             "prior unmapped source block was silently approved")
        source_anchor=link["official_section_anchor"]
        page=int(source_anchor[6:9]);line=int(source_anchor[11:14])
        a=anchor_lookup.get((page,line))
        need(a is not None and a["source_line_sha256"]==link["section_source_line_sha256"],
             "source section position/hash mismatch")
        need(a["full_page_review_completed"] is False and a["teacher_review"]=="REVIEW_PENDING",
             "source unnumbered block was silently approved")
        row={"assessment_id":card["id"],"source_section_anchor":source_anchor,
             "source_line_sha256":a["source_line_sha256"],"source_section_kind":link["section_kind"],
             "source_requirement_review":"NOT_DONE","rubric_quality_gate":"STRUCTURALLY_VALID_ONLY",
             "mathematical_case_evidence":"FINITE_EXACT_WITNESS_ONLY",
             "official_skill_alignment":"UNMAPPED","full_source_clause_approved":False,
             "teacher_approved":False,"student_published":False}
        rows.append(row)
        teacher_index.append({"id":card["id"],"domain":card["domain"],"source_section_anchor":source_anchor,
                              "access":"TEACHER_ONLY","review":"REVIEW_PENDING","student_retrievable":False})
    from app.kb_batch66_competency_witnesses import GOLDEN,verify_finite_cases
    need(keys==set(GOLDEN)==set(verify_finite_cases()),"task witness set or exact golden mismatch")
    props=source["proposals"]
    need(all(p["official_atomic_membership"]=="UNDETERMINED"
             and p["math_equivalence"]=="NOT_REVIEWED" and p["teacher_review"]=="REVIEW_PENDING"
             for p in props),"unreviewed candidate falsely certified")
    pair_queue=review_pairs(props)
    need(pair_queue and all(not p["merge_permitted"] for p in pair_queue),
         "no cross-page review queue, or auto-merging attempted")
    track_leads=Counter(r["track_hint"] for r in registry["rows"])
    need(sum(track_leads.values())==428,"invalid source lead partition")
    parent_to_lessons={r["source_anchor_id"]:r["lesson_id"] for r in lessons["rows"]}
    needs_review=[]
    section_to_assessment={r["source_section_anchor"]:r["assessment_id"] for r in rows}
    for anchor in registry["rows"]:
        anchor_id=f"KB61-P{anchor['printed_page']:03d}-L{anchor['pdfkit_line']:03d}"
        needs_review.append({"anchor_id":anchor_id,"printed_page":anchor["printed_page"],
            "source_line_sha256":anchor["source_line_sha256"],
            "source_kind":anchor["kind"],"track_hint_not_authoritative":anchor["track_hint"],
            "editorial_manuscript_id":parent_to_lessons.get(anchor_id),
            "independent_assessment_id":section_to_assessment.get(anchor_id),
            "official_atomic_membership":"UNDETERMINED",
            "full_source_clause_teacher_review":"NOT_DONE",
            "math_equivalence_review":"NOT_REVIEWED",
            "teacher_approved":False,"student_published":False})
    need(len(needs_review)==428 and len({r["anchor_id"] for r in needs_review})==428,
         "anchor backlog nonunique or incomplete")
    need(sum(r["editorial_manuscript_id"] is not None for r in needs_review)==31 and
         sum(r["independent_assessment_id"] is not None for r in needs_review)==14,
         "manuscript/assessment backlog linkage incomplete")
    backlog={"schema_version":"kb66-source-anchor-backlog-v1",
             "source_registry_sha256":sha(ANCHORS),"source_lead_count":428,
             "teacher_reviewed_complete_clauses":0,"official_atom_denominator":{t:None for t in TRACKS},
             "rows":needs_review}
    m={"schema_version":"kb66-competency-evidence-v1",
       "inputs_sha256":{"source_pdf":registry["source_pdf_sha256"],"anchor_registry":sha(ANCHORS),
                        "provisional_atom_hypotheses":sha(CAND),
                        "competency_proposals":sha(CROSS),"prior_lesson_manifest":sha(LESSON_MATRIX),
                        "original_assessments":sha(TASKS) if cards==load(TASKS) else None},
       "source_pages_with_some_leads":61,"heuristic_clause_anchors":428,"review_backlog_items":428,
       "internal_manuscript_anchor_links":31,"assessment_anchor_links":14,
       "heuristic_anchor_leads_by_track":{t:track_leads.get(t,0) for t in TRACKS},
       "unreviewed_provisional_atom_hypotheses":62,"internal_scope_manuscripts":31,
       "independent_assessment_drafts":14,"finite_exact_witnesses":14,
       "rubric_total_points":84,"source_unnumbered_sections_still_unmapped":14,
       "potential_cross_page_duplicate_pairs":len(pair_queue),
       "math_equivalence_certified_pairs":0,"teacher_full_page_reviews":0,
       "official_atom_denominator":{t:None for t in TRACKS},
       "teacher_approvals":0,"student_published":0,
       "rubric_items":rows}
    q={"schema_version":"kb66-lexical-overlap-review-only-v1",
       "source_candidate_count":62,"total_unordered_candidate_pairs":62*61//2,
       "same_parent_pairs_excluded":31,
       "cross_page_overlap_candidates":len(pair_queue),
       "nonoverlap_pairs_not_established_equivalent":True,
       "same_terms_do_not_prove_math_equivalence":True,
       "math_equivalence_certified":0,"auto_merge_permitted":False,
       "rows":pair_queue}
    index={"schema_version":"kb66-teacher-index-only-v1","student_index_write_permitted":False,
           "contains_teacher_answers":False,"rows":teacher_index}
    return m,q,index,backlog

def render(m,q,index,backlog):
    cards=load(TASKS)
    lines=["# Batch66｜14项独立能力测评草案、跨页数学等价审查队列与真实缺口", "",
           "**严格范围声明：**14项是教师侧原创测评草案，不是已核对的课标学业条款；"
           "它们的原始栏目仍为 UNMAPPED。62是内部拆分假设，不是官方七轨知识原子总数。", "",
           f"- 来源：61页有局部线索、428个启发式起点、62个未核实原子假设、31篇内部范围稿件。",
           f"- 教师测评草案：{m['independent_assessment_drafts']}，每篇6分独立量规，总计84分；"
           "数学实例见证14项，但未认证一般定理或完整自然语言解析。",
           f"- 跨页词形近似待审配对：{len(q['rows'])}，**数学等价已认证：0，自动合并：0**。",
           "- 14/14栏目目标仍未全文逐条审核与映射；七轨正式分母均为 null；教师审核及学生发布均为0。",
           "- 428/428条启发式起点逐项保留独立待审状态，其中31项连至内部范围稿件、14项连至独立能力草案；不是428个内容原子。",
           "- 学生正式检索索引没有纳入此稿，教师完整答案不进入学生 prompt。","",
           "## 七轨起点线索（不是课程原子数）",""]
    for t,n in m["heuristic_anchor_leads_by_track"].items():
        lines.append(f"- {t}: {n} 条启发式位置；正式知识原子分母：未知。")
    lines+=["","## 14份原创测评：题目、条件、解析、错因、教师评分", ""]
    for card,row in zip(cards,m["rubric_items"]):
        lines += [f"### {card['id']} · {card['domain']}",
                  f"来源栏目线索：{row['source_section_anchor']}；**真实对应能力未审**，状态 UNMAPPED。",
                  f"题目（教师侧）：{card['question']}",
                  f"参考答案（教师侧）：{card['teacher_expected_answer']}",
                  "分步依据："]
        lines += [f"{j}. {s}" for j,s in enumerate(card["justification_steps"],1)]
        lines += [f"典型误解：{card['typical_wrong_answer']}；原因：{card['wrong_reason']}",
                  f"反例/失效边界：{card['counterexample_or_failure_boundary']}",
                  "分项量规："]
        lines += [f"- {r['criterion']}：{r['points']}分" for r in card["scoring_rubric"]]
        lines += [f"近迁移：{card['near_transfer']}",f"远迁移：{card['far_transfer']}",
                  "提示梯度（不直接暴露参考答案）："+"；".join(card["three_stage_hints"]),""]
    lines+=["## 跨页候选复核的工作规则","",
            "只使用自编主题概述的字符二元组近似或相同的失效条件来排序。"
            "该规则不代表官方条款同义，也不能把题目/概念合并。必须核对完整原文、"
            "同一数学对象的定义域与量词、跨轨道适用范围，并由真实教师审核。","",
            "下一批：对待审高优先配对逐条阅读完整来源；独立拆分未编号条款并建立"
            "可审计的七轨正式原子分母；重验历史538步和10组数学冲突；教师侧人工审校后再考虑发布。"]
    return "\n".join(lines)+"\n"

def main():
    a=argparse.ArgumentParser();a.add_argument("--check",action="store_true")
    opt=a.parse_args()
    m,q,index,backlog=build()
    files={OUT:canon(m),DUPS:canon(q),INDEX:canon(index),BACKLOG:canon(backlog),REPORT:render(m,q,index,backlog)}
    if opt.check:
        for p,expected in files.items():
            need(p.exists() and p.read_text(encoding="utf-8")==expected,"stale build artifact: "+str(p))
    else:
        for p,content in files.items():
            p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding="utf-8")
    print(f"Batch66 check={opt.check} rubric=14 exact=14 cross-page-review={len(q['rows'])} "
          "teacher_approved=0 official_denominator=null")

if __name__=="__main__":main()
