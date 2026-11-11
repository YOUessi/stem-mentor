#!/usr/bin/env python3
"""Batch94 14 original K02–K06 draft lessons, K00 source audit and K07 witnesses.
Machine verification is finite; no unsupervised teacher approval or student release.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch94_authoring import RECORDS
from app.deep_knowledge import DeepLesson,curriculum
from app.kb_batch94_math_oracles import verify_all
import build_kb_batch93_candidate_triage as B93

PACK=ROOT/"knowledge/deep/v1/batch94_deep_scope_14.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH94_SOURCE_LESSON_MATRIX.json"
DOC=ROOT/"docs/evaluation/KB_BATCH94_DEEP_LESSONS.md"
AUTHOR=ROOT/"scripts/kb_batch94_authoring.py"
STANDARD="普通高中数学课程标准（2017年版2020年修订）"
URL="https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf"

def ensure(cond,why):
    if not cond:raise ValueError(why)
def stable(x):
    return json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+"\n"

def build(records=None,baseline=None):
    records=RECORDS if records is None else records
    baseline=B93.build() if baseline is None else baseline
    ensure(type(records) is list and len(records)==14,"Batch94 requires 14 original complete lessons")
    ensure(baseline["provisional_labels"]==300 and baseline["source_anchor_editorials"]==428 and
        baseline["still_without_any_individual_review"]==110 and
        baseline["remaining_without_pairwise_comparison"]==134 and
        baseline["official_atom_denominator"] is None and
        all(v is None for v in baseline["official_atom_denominators_by_track"].values()) and
        baseline["fully_teacher_atomized_pages"]==0 and baseline["teacher_approved"]==0 and
        baseline["student_authoritative_release"]==0 and
        baseline["historical_uncertified_proof_steps"]==538 and
        baseline["unresolved_math_conflicts"]==10,
        "upstream curriculum/source/authority drift")
    scope={x["candidate_id"]:x for x in baseline["provisional_candidate_ledger"]}
    source={x["candidate_id"]:x for x in B93.read(B93.SOURCES)["provisional_candidate_backlog"]}
    known={x["id"]:x for x in curriculum()}
    ensure(len(scope)==len(source)==300,"candidate registry must be unique")
    evidence=verify_all()
    ensure(len(evidence)==14,"all authored mathematical witnesses required")
    seen=set();docs=[];links=[]
    schema={"anchor","curriculum_id","kind","title","definition","statement","assumptions",
       "steps","boundary","negative","wrong","examples","hints","transfer","notation","prerequisites"}
    for i,row in enumerate(records,1):
        ensure(type(row) is dict and set(row)==schema,"authoring field completeness")
        anchor=row["anchor"]
        ensure(type(anchor) is str and anchor in scope and anchor not in seen,
               "missing or duplicate canonical source")
        seen.add(anchor)
        src=source[anchor]; candidate=scope[anchor]
        ensure(candidate["scope_audit_state"]=="NOT_YET_INDIVIDUALLY_AUDITED",
               "Batch94 must reduce genuinely unaudited sources")
        ensure(src["review_status"]=="REVIEW_PENDING" and
               src["official_math_atom_id"] is None and
               src["teacher_approval"] is None and
               src["student_authoritative_index_eligible"] is False and
               src["source_line_sha256"]==candidate["source_line_sha256"],
               "source snapshot authority or SHA mismatch")
        cid=row["curriculum_id"]
        ensure(type(cid) is str and cid in known,"unknown engineering curriculum hook")
        ensure(row["kind"] in ("theorem","concept","method"),"invalid type")
        for field,minlen in (("title",8),("definition",25),("statement",25),("boundary",28)):
            ensure(type(row[field]) is str and len(row[field])>=minlen,"missing "+field)
        ensure(type(row["assumptions"]) is list and len(row["assumptions"])>=2 and
            all(type(v) is str and len(v)>=12 for v in row["assumptions"]),
            "missing substantive theorem/method assumptions")
        ensure(type(row["steps"]) is list and len(row["steps"])>=3,"inadequate reasoning")
        if row["kind"]=="theorem":
            ensure(all(type(s) is tuple and len(s)==2 and min(map(len,s))>=12
                        for s in row["steps"]),"unjustified theorem proof")
            proof=[dict(claim=s[0],reason=s[1]) for s in row["steps"]]
            reasoning=[]
        else:
            ensure(all(type(s) is str and len(s)>=12 for s in row["steps"]),
                   "missing method rationale")
            proof=[];reasoning=row["steps"]
        ensure(type(row["negative"]) is tuple and len(row["negative"])==3 and
               all(type(x) is str and len(x)>=8 for x in row["negative"]),
               "invalid generalization/counterexample incomplete")
        ensure(type(row["wrong"]) is tuple and len(row["wrong"])==3 and
               all(type(x) is str and len(x)>=8 for x in row["wrong"]),
               "student misconception incomplete")
        ensure(type(row["examples"]) is list and len(row["examples"])==2 and
               all(type(e) is dict and set(e)=={"question","steps","answer","check"}
                   and len(e["question"])>=15 and len(e["steps"])>=2
                   and all(len(s)>=10 for s in e["steps"])
                   and len(e["answer"])>=2 and len(e["check"])>=8
                   for e in row["examples"]),
               "two original fully worked examples required")
        ensure(row["examples"][0]["question"]!=row["examples"][1]["question"],
               "duplicate question is not a problem family")
        ensure(type(row["hints"]) is list and len(row["hints"])==3 and
               len(set(row["hints"]))==3 and all(len(h)>=8 for h in row["hints"]),
               "three original nonidentical hints required")
        ensure(type(row["transfer"]) is tuple and len(row["transfer"])==2 and
               all(len(s)>=12 for s in row["transfer"]),
               "near/far transfers incomplete")
        ensure(type(row["notation"]) is list and len(row["notation"])>=3 and
               len(row["prerequisites"])>=2,
               "mathematical notation/prerequisite absent")
        ident=f"math.hs.batch94.{i:02d}"
        payload={
            "id":ident,"curriculum_ids":[cid],"kind":row["kind"],
            "title":row["title"],"version":"1.0.0",
            "notation":row["notation"],"prerequisites":row["prerequisites"],
            "prerequisite_lesson_ids":[],
            "definition":row["definition"] if row["kind"]=="concept" else None,
            "statement":row["statement"] if row["kind"]!="concept" else row["statement"],
            "assumptions":row["assumptions"],"proof_steps":proof,"rationale_steps":reasoning,
            "boundaries":[row["boundary"]],
            "counterexamples":[dict(false_claim=row["negative"][0],
                     example=row["negative"][1],explanation=row["negative"][2])],
            "worked_examples":row["examples"],
            "misconceptions":[dict(error=row["wrong"][0],why_wrong=row["wrong"][1],
                                  repair_question=row["wrong"][2])],
            "hint_ladder":row["hints"],
            "transfer":{"near":row["transfer"][0],"far":row["transfer"][1]},
            "provenance":{"kind":"PROJECT_AUTHORED","permission":"PROJECT_AUTHORED",
                          "curriculum_standard":STANDARD,"standard_url":URL,
                          "author_role":"PROJECT_AUTHOR"},
            "review":{"status":"REVIEW_PENDING","reviewer_id":None,
                       "reviewed_at":None,"review_record":None},
            "teacher_solution_visibility":"TEACHER_ONLY"
        }
        DeepLesson.model_validate(payload)
        docs.append(payload)
        links.append({"lesson_id":ident,"source_candidate_id":anchor,
             "provisional_topic":src["provisional_topic"],
             "source_track":src["track"],"source_review_id":src["source_review_id"],
             "source_page":src["source_page"],
             "source_line_sha256":src["source_line_sha256"],
             "engineering_curriculum_id":cid,"engineering_level":known[cid]["level"],
             "cross_track_mapping_editorial_only":known[cid]["level"] !=
                   ({"COMPULSORY":"必修","SELECTIVE_COMPULSORY":"选择性必修"}
                    .get(src["track"],"选修拓展")),
             "official_atom_id":None,"teacher_approved":False,"student_publishable":False,
             "general_theorem_certified":False,"finite_evidence":evidence[anchor],
             "review_status":"REVIEW_PENDING"})
    ensure(seen==set(evidence),"math witnesses must match 14 authorship sources")
    original=Counter(x["track"] for x in source.values())
    new=Counter(x["source_track"] for x in links)
    ensure(set(new)=={"COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A",
                      "ELECTIVE_B","ELECTIVE_C","ELECTIVE_D"},
           "ensure all six existing nonempty provisional source tracks receive lessons")
    bytrack={k:{"project_provisional_labels":original[k],
               "batch94_editor_deep_draft":new[k],
               "official_curriculum_atom_denominator":None,"teacher_approved":0}
             for k in B93.TRACKS}
    report={"schema_version":"kb94-source-deep-editor-draft-v1",
            "source_baseline_sha256":sha256(B93.OUTPUT.read_bytes()).hexdigest(),
            "source_author_sha256":sha256(AUTHOR.read_bytes()).hexdigest(),
            "total_source_anchors":428,"provisional_labels":300,
            "relation_compared_pending":166,"prior_individual_scope_pending":24,
            "new_individual_full_deep_drafts":14,
            "still_without_any_individual_review":110-14,
            "remaining_without_pairwise_comparison":134,
            "official_atom_denominator":None,
            "official_atom_denominators_by_track":{k:None for k in B93.TRACKS},
            "fully_teacher_atomized_pages":0,"teacher_approved":0,
            "student_authoritative_release":0,
            "historical_uncertified_proof_steps":538,
            "P0_historical_steps_without_teacher_cards":106,
            "unresolved_math_conflicts":10,
            "finite_math_checks":len(evidence),
            "general_theorem_certificates":0,
            "per_track":bytrack,"canonical_lesson_source_links":links,
            "teacher_full_solutions":"EDITOR_ONLY_REVIEW_PENDING"}
    return docs,report

def to_markdown(docs,report):
    links={x["lesson_id"]:x for x in report["canonical_lesson_source_links"]}
    out=["# Batch94｜14份独立来源、完整结构原创数学教学草案","",
         "**严格边界：** 14篇是结构化深度草案，不是14个官方数学原子；未有真人教师批准，不向学生自主挑战暴露完整解答。",
         "428来源锚点与300临时标签不是七轨官方原子分母；七轨正式分母仍未知，教师完整逐页原子化0/61。",""]
    for doc in docs:
        link=links[doc["id"]]
        out.extend([f'## {doc["id"]}｜{doc["title"]}',"",
           f'课标内部来源：{link["source_candidate_id"]}；轨道：{link["source_track"]}；页码：{link["source_page"]}；SHA256：{link["source_line_sha256"]}',"",
           f'工程映射：{link["engineering_curriculum_id"]}；状态：REVIEW_PENDING／TEACHER_ONLY／NOT_FORMALLY_CERTIFIED。',"",
           "**定义及表述：** "+(doc["definition"] + "；正式性质/命题：" + doc["statement"] if doc["definition"] and doc["statement"] else (doc["definition"] or doc["statement"])), "",
           "**论域与假设：** "+'；'.join(doc["assumptions"]),"",
           "**符号：** "+'；'.join(doc["notation"]),"",
           "**证明/方法合法性：**"])
        for s in doc["proof_steps"]:
            out.append(f'- **{s["claim"]}**：{s["reason"]}')
        for s in doc["rationale_steps"]:
            out.append("- "+s)
        n=doc["counterexamples"][0];m=doc["misconceptions"][0]
        out.extend(["","**边界：** "+doc["boundaries"][0],"",
          f'**无效泛化反例：** {n["false_claim"]}；{n["example"]}；{n["explanation"]}',"",
          f'**常见错因与纠偏：** {m["error"]}；{m["why_wrong"]}；{m["repair_question"]}',"",
          "**教师侧例题（不自动公开解答）：**"])
        for i,e in enumerate(doc["worked_examples"],1):
            out.extend([f'{i}. {e["question"]}',
                "   - 推导："+'；'.join(e["steps"]),
                f'   - 教师答案：{e["answer"]}；独立核查：{e["check"]}'])
        out.extend(["","**分级提示（独立挑战按需最低层）：**"])
        out.extend(f'{i}. {h}' for i,h in enumerate(doc["hint_ladder"],1))
        out.extend(["",f'**近迁移：** {doc["transfer"]["near"]}',
             f'**远迁移：** {doc["transfer"]["far"]}',""])
    return "\n".join(out).rstrip()+"\n"

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    args=p.parse_args(); docs,report=build()
    outs={PACK:stable(docs),AUDIT:stable(report),DOC:to_markdown(docs,report)}
    for path,contents in outs.items():
        if args.check:
            ensure(path.exists() and path.read_text(encoding="utf-8")==contents,
                   "generated output drift: "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(contents,encoding="utf-8")
    print("BATCH94",len(docs),"deep drafts",report["still_without_any_individual_review"],
          "remaining without individual audit","CHECK" if args.check else "WRITTEN")
if __name__=="__main__":main()
