#!/usr/bin/env python3
"""Batch95: source-locked 16 complete original editor-side maths drafts.

This is not the official curriculum atomic denominator or teacher certification.
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
import build_kb_batch93_candidate_triage as B93
import build_kb_batch94_deep_scope as B94
from kb_batch95_authoring import RECORDS
from app.deep_knowledge import DeepLesson,curriculum
from app.kb_batch95_math_oracles import verify_all,IDS

PACK=ROOT/"knowledge/deep/v1/batch95_deep_scope_16.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH95_SOURCE_LESSON_MATRIX.json"
DOC=ROOT/"docs/evaluation/KB_BATCH95_DEEP_LESSONS.md"
AUTHOR=ROOT/"scripts/kb_batch95_authoring.py"
STANDARD="普通高中数学课程标准（2017年版2020年修订）"
URL="https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf"

def require(ok,desc):
    if not ok:raise ValueError(desc)
def dump(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"

def build(records=None,prior=None):
    records=RECORDS if records is None else records
    prior=B94.build()[1] if prior is None else prior
    require(type(records) is list and len(records)==16,"exactly 16 complete individually authored lessons")
    require(prior["new_individual_full_deep_drafts"]==14 and
        prior["still_without_any_individual_review"]==96 and
        prior["remaining_without_pairwise_comparison"]==134 and
        prior["official_atom_denominator"] is None and
        all(v is None for v in prior["official_atom_denominators_by_track"].values()) and
        prior["fully_teacher_atomized_pages"]==0 and
        prior["teacher_approved"]==0 and
        prior["student_authoritative_release"]==0 and
        prior["historical_uncertified_proof_steps"]==538 and
        prior["P0_historical_steps_without_teacher_cards"]==106 and
        prior["unresolved_math_conflicts"]==10,
        "upstream official-denominator or review drift")
    earlier={r["source_candidate_id"] for r in prior["canonical_lesson_source_links"]}
    baseline=B93.build()
    candidates={r["candidate_id"]:r for r in baseline["provisional_candidate_ledger"]}
    source={r["candidate_id"]:r for r in B93.read(B93.SOURCES)["provisional_candidate_backlog"]}
    known={r["id"]:r for r in curriculum()}
    require(len(candidates)==len(source)==300 and len(earlier)==14,"freeze original candidate registry")
    witnesses=verify_all()
    require(set(witnesses)==set(IDS) and len(IDS)==16,"exact witness-source registry required")
    required={"anchor","curriculum_id","kind","title","definition","statement","assumptions",
        "steps","boundary","negative","wrong","examples","hints","transfer","notation","prerequisites"}
    seen=set();docs=[];links=[]
    for index,row in enumerate(records,1):
        require(type(row) is dict and set(row)==required,"type-specific fields must be complete")
        anchor=row["anchor"]
        require(type(anchor) is str and anchor in candidates and anchor in source and
                anchor not in earlier and anchor not in seen,"source absent/previously audited/duplicate")
        seen.add(anchor)
        a=candidates[anchor];b=source[anchor]
        require(a["scope_audit_state"]=="NOT_YET_INDIVIDUALLY_AUDITED" and
            a["source_line_sha256"]==b["source_line_sha256"] and
            b["review_status"]=="REVIEW_PENDING" and
            b["teacher_approval"] is None and
            b["student_authoritative_index_eligible"] is False and
            b["official_math_atom_id"] is None,
            "canonical source, SHA, draft state mismatch")
        require(row["curriculum_id"] in known,"unknown engineering curriculum id")
        require(row["kind"] in {"concept","method","theorem"},"unsupported math item type")
        for fld,minlen in (("title",8),("definition",24),("statement",28),("boundary",25)):
            require(type(row[fld]) is str and len(row[fld])>=minlen,"missing "+fld)
        require(type(row["assumptions"]) is list and len(row["assumptions"])>=2 and
            all(type(s) is str and len(s)>=12 for s in row["assumptions"]),
            "full theorem/method domain assumptions required")
        require(type(row["steps"]) is list and len(row["steps"])>=3,"at least three explanation steps")
        theorem=row["kind"]=="theorem"
        if theorem:
            require(all(type(s) is tuple and len(s)==2 and
                   all(type(v) is str and len(v)>=12 for v in s)
                   for s in row["steps"]),"reasoned theorem proofs required")
        else:
            require(all(type(s) is str and len(s)>=12 for s in row["steps"]),
                    "method rationale required")
        require(type(row["negative"]) is tuple and len(row["negative"])==3 and
            all(type(s) is str and len(s)>=12 for s in row["negative"]),"worked counterexample absent")
        require(type(row["wrong"]) is tuple and len(row["wrong"])==3 and
            all(type(s) is str and len(s)>=12 for s in row["wrong"]),"misconception repair absent")
        require(type(row["examples"]) is list and len(row["examples"])==2 and
            all(type(e) is dict and set(e)=={"question","steps","answer","check"} and
                len(e["question"])>=15 and len(e["steps"])>=2 and
                all(type(st) is str and len(st)>=12 for st in e["steps"]) and
                len(e["answer"])>=2 and len(e["check"])>=12 for e in row["examples"]),
            "two original complete worked examples required")
        require(row["examples"][0]["question"]!=row["examples"][1]["question"],
            "distinct examples required")
        require(type(row["hints"]) is list and len(row["hints"])==3 and
            len(set(row["hints"]))==3 and all(len(h)>=10 for h in row["hints"]),
            "three non-identical scaffolded hints required")
        require(type(row["transfer"]) is tuple and len(row["transfer"])==2 and
            all(type(s) is str and len(s)>=12 for s in row["transfer"]),
            "near and far transfer required")
        require(len(row["notation"])>=3 and len(row["prerequisites"])>=2,
            "notation/prerequisite links required")
        item={
            "id":f"math.hs.batch95.{index:02d}",
            "curriculum_ids":[row["curriculum_id"]],"kind":row["kind"],"title":row["title"],
            "version":"1.0.0","notation":row["notation"],"prerequisites":row["prerequisites"],
            "prerequisite_lesson_ids":[],
            "definition":row["definition"] if row["kind"]=="concept" else None,
            "statement":row["statement"] if row["kind"]!="concept" else row["statement"],
            "assumptions":row["assumptions"],
            "proof_steps":[dict(claim=s[0],reason=s[1]) for s in row["steps"]] if theorem else [],
            "rationale_steps":[] if theorem else row["steps"],
            "boundaries":[row["boundary"]],
            "counterexamples":[dict(false_claim=row["negative"][0],
                    example=row["negative"][1],explanation=row["negative"][2])],
            "worked_examples":row["examples"],
            "misconceptions":[dict(error=row["wrong"][0],why_wrong=row["wrong"][1],
                    repair_question=row["wrong"][2])],
            "hint_ladder":row["hints"],"transfer":{"near":row["transfer"][0],
                "far":row["transfer"][1]},
            "provenance":{"kind":"PROJECT_AUTHORED","permission":"PROJECT_AUTHORED",
                "curriculum_standard":STANDARD,"standard_url":URL,"author_role":"PROJECT_AUTHOR"},
            "review":{"status":"REVIEW_PENDING","reviewer_id":None,"reviewed_at":None,
                "review_record":None},"teacher_solution_visibility":"TEACHER_ONLY"}
        DeepLesson.model_validate(item)
        docs.append(item)
        links.append({"lesson_id":item["id"],"source_candidate_id":anchor,
            "provisional_topic":b["provisional_topic"],"source_track":b["track"],
            "source_review_id":b["source_review_id"],"source_page":b["source_page"],
            "source_line_sha256":b["source_line_sha256"],
            "engineering_curriculum_id":row["curriculum_id"],
            "engineering_level":known[row["curriculum_id"]]["level"],
            "cross_track_mapping_editorial_only":
                known[row["curriculum_id"]]["level"]!=
                {"COMPULSORY":"必修","SELECTIVE_COMPULSORY":"选择性必修"}.get(
                    b["track"],"选修拓展"),
            "official_atom_id":None,"teacher_approved":False,"student_publishable":False,
            "general_theorem_certified":False,"finite_evidence":witnesses[anchor],
            "review_status":"REVIEW_PENDING"})
    require(seen==set(witnesses),"all evidence must match authored anchors")
    counts=Counter(r["source_track"] for r in links)
    require(set(counts)=={"COMPULSORY","SELECTIVE_COMPULSORY",
        "ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D"},
        "six source tracks required; E is a zero-anchor separate unresolved track")
    prior_counts=Counter(r["source_track"] for r in prior["canonical_lesson_source_links"])
    report={"schema_version":"kb95-source-deep-editor-draft-v1",
        "source_baseline_sha256":sha256(B94.AUDIT.read_bytes()).hexdigest(),
        "source_author_sha256":sha256(AUTHOR.read_bytes()).hexdigest(),
        "total_source_anchors":428,"provisional_labels":300,
        "relation_compared_pending":166,"prior_individual_scope_pending":24,
        "prior_full_deep_drafts":14,"new_individual_full_deep_drafts":16,
        "cumulative_new_deep_drafts_since_batch94":30,
        "still_without_any_individual_review":96-16,
        "remaining_without_pairwise_comparison":134,
        "official_atom_denominator":None,
        "official_atom_denominators_by_track":{k:None for k in B93.TRACKS},
        "fully_teacher_atomized_pages":0,"teacher_approved":0,
        "student_authoritative_release":0,
        "historical_uncertified_proof_steps":538,
        "P0_historical_steps_without_teacher_cards":106,
        "unresolved_math_conflicts":10,
        "finite_math_checks":len(witnesses),"general_theorem_certificates":0,
        "per_track":{k:{"project_provisional_labels":sum(r["track"]==k for r in source.values()),
              "batch94_deep_drafts":prior_counts[k],"batch95_deep_drafts":counts[k],
              "official_curriculum_atom_denominator":None,"teacher_approved":0}
              for k in B93.TRACKS},
        "canonical_lesson_source_links":links,
        "teacher_full_solutions":"EDITOR_ONLY_REVIEW_PENDING"}
    return docs,report

def to_markdown(docs,report):
    links={x["lesson_id"]:x for x in report["canonical_lesson_source_links"]}
    lines=["# Batch95｜16份原创来源锁定高中数学深度讲义（教师审稿草案）","",
        "**权威边界：** 全部 REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED；",
        "428来源行及300临时主题不是官方课标原子分母。七轨正式分母未知；教师逐页审核0/61。",""]
    for doc in docs:
        link=links[doc["id"]]
        lines+=["## "+doc["id"]+"｜"+doc["title"],"",
           "来源："+link["source_candidate_id"]+"；轨道："+link["source_track"]+
           "；页："+str(link["source_page"])+"；行SHA："+link["source_line_sha256"],"",
           "工程课程映射："+link["engineering_curriculum_id"]+"；教师审查待完成。","",
           "**正式定义/陈述：** "+(doc["definition"] + "；正式性质/命题：" + doc["statement"] if doc["definition"] and doc["statement"] else (doc["definition"] or doc["statement"])),"",
           "**论域与前提：** "+"；".join(doc["assumptions"]),"",
           "**符号及先修：** "+"；".join(doc["notation"])+"；先修："+"；".join(doc["prerequisites"]),"",
           "**证明及合法性依据：**"]
        lines+=["- "+s["claim"]+"。理由："+s["reason"] for s in doc["proof_steps"]]
        lines+=["- "+s for s in doc["rationale_steps"]]
        n=doc["counterexamples"][0];m=doc["misconceptions"][0]
        lines+=["","**边界：** "+doc["boundaries"][0],"",
           "**失效反例：** "+n["false_claim"]+"；"+n["example"]+"；"+n["explanation"],"",
           "**常见错因：** "+m["error"]+"；"+m["why_wrong"]+"；"+m["repair_question"],"",
           "**教师侧两题（学生独立挑战不泄漏解答）：**"]
        for i,e in enumerate(doc["worked_examples"],1):
            lines += [f"{i}. "+e["question"],"    - 推导："+"；".join(e["steps"]),
                      "    - 教师答案："+e["answer"]+"；独立检查："+e["check"]]
        lines += ["","**三级提示：**"]
        lines += [f"{i}. {s}" for i,s in enumerate(doc["hint_ladder"],1)]
        lines += ["","**近迁移：** "+doc["transfer"]["near"],
                  "**远迁移：** "+doc["transfer"]["far"],""]
    return "\n".join(lines).rstrip()+"\n"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    docs,scope=build()
    files={PACK:dump(docs),AUDIT:dump(scope),DOC:to_markdown(docs,scope)}
    for path,body in files.items():
        if args.check:
            require(path.is_file() and path.read_text(encoding="utf-8")==body,
                "generated output drift "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(body,encoding="utf-8")
    print("BATCH95",len(docs),"original draft lessons",
          scope["still_without_any_individual_review"],"not individually audited",
          "CHECK" if args.check else "WRITTEN")

if __name__=="__main__":main()
