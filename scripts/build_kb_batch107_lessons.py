#!/usr/bin/env python3
"""Build ten reviewed-only, complete teaching drafts and evidence crosswalk."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from hashlib import sha256
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch107_lesson_authoring import UNITS
from app.deep_knowledge import DeepLesson,curriculum,DEEP_DIR,lessons
from app.kb_batch107_math import check
from build_kb_batch107_source import build as build_source

SOURCE_KEYS=("quad_two","quad_positive","zero_graph","singleton",
             "cross_product","projection","linear_dependence",
             "orthogonal","signed_area","matrix_multiply")
PACK=DEEP_DIR/"batch107_math_ten.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH107_TEN_LESSONS_AUDIT.json"
MD=ROOT/"docs/evaluation/KB_BATCH107_TEN_LESSONS.md"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A",
        "ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")


def need(ok, msg):
    if not ok: raise ValueError(msg)


def canonical(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"


def build(units=UNITS,source_keys=SOURCE_KEYS):
    known={c["id"]:c for c in curriculum()}
    need(len(units)==10 and len(source_keys)==10,"ten original lessons required")
    need(len(set(source_keys))==10,"duplicate editorial source keys")
    source=build_source()
    anchor={c["oracle_key"]:c for c in source["candidates"]}
    need(set(source_keys) <= set(anchor),"orphan source candidate")
    prior=[]
    for path in sorted(DEEP_DIR.glob("*.json")):
        if path==PACK:continue
        prior.extend(json.loads(path.read_text(encoding="utf8")))
    ids=[x["id"] for x in prior]
    need(len(ids)==len(set(ids)), "historical deep IDs already duplicated")
    result=[]
    # Explicit editor-only dependencies; no text edge promoted to official ID.
    deps={1:[0],2:[0],5:[4],6:[4],8:[1]}
    for i,r in enumerate(units):
        need(r["curriculum_id"] in known,"unknown engineering curriculum mapping")
        need(r["kind"] in {"concept","method","theorem"},"unknown kind")
        need(len(r["examples"])==2 and all(len(e["steps"])>=2 and
             len(e["check"])>=15 for e in r["examples"]),"two substantive checked worked examples")
        need(len(r["hints"])==3 and len(set(r["hints"]))==3,"missing hint ladder")
        need(len(r["reasoning"])>=3 and len(r["statement"])>=40,"incomplete math narrative")
        need(len(r["negative"])==3 and all(len(s)>=20 for s in r["negative"]),
             "missing counterexample with explanation")
        need(len(r["assumptions"])>=2 and len(r["prereqs"])>=2
             and len(r["notation"])>=2,"missing math assumptions/notation/prereqs")
        proof=r["reasoning"] if r["kind"]=="theorem" else []
        rationale=[] if proof else r["reasoning"]
        need(all(isinstance(s,dict) and len(s["claim"])>=25 and len(s["reason"])>=25
             for s in proof),"proof reasons incomplete")
        need(all(isinstance(s,str) and len(s)>=25 for s in rationale),
             "definition/method explanation incomplete")
        source_candidate=anchor[source_keys[i]]
        internal=known[r["curriculum_id"]]
        # Internal mapping may say 必修/选修拓展, but cannot elevate to an
        # official track; that requires a separate teacher seven-track review.
        crosswalk={"editorial_candidate_id":source_candidate["candidate_id"],
                   "source_printed_page":source_candidate["page"],
                   "source_track_hint":source_candidate["track"],
                   "engineering_id":r["curriculum_id"],
                   "engineering_level":internal["level"],
                   "official_atom_id":None,"crosswalk_teacher_approved":False}
        checkresult=check(source_keys[i])
        need(checkresult["finite_exact_positive_passed"] and
             checkresult["invalid_generalization_rejected"] and
             not checkresult["teacher_approved"] and
             not checkresult["universal_proof_certified"],
             "oracle authority escalation")
        index=i+1
        did=f"math.hs.batch107.{index:02d}"
        prereqids=[f"math.hs.batch107.{j+1:02d}" for j in deps.get(i,[])]
        need(all(j<i for j in deps.get(i,[])),"forward/cyclic prereq")
        obj={
            "id":did,"curriculum_ids":[r["curriculum_id"]],
            "kind":r["kind"],"title":r["title"],"version":"1.0.0",
            "notation":r["notation"],"prerequisites":r["prereqs"],
            "prerequisite_lesson_ids":prereqids,
            "definition":r["statement"] if r["kind"]=="concept" else None,
            "statement":r["statement"],"assumptions":r["assumptions"],
            "proof_steps":proof,"rationale_steps":rationale,
            "boundaries":r["assumptions"],
            "counterexamples":[{"false_claim":r["negative"][0],
                                "example":r["negative"][1],
                                "explanation":r["negative"][2]}],
            "misconceptions":[{"error":r["negative"][0],
                                "why_wrong":r["negative"][2],
                                "repair_question":"这条错误推理缺少什么前提？请先构造或解释反例，再补全合法条件。"}],
            "worked_examples":r["examples"],"hint_ladder":r["hints"],
            "transfer":{"near":r["transfers"][0],"far":r["transfers"][1]},
            "provenance":{"kind":"PROJECT_AUTHORED","permission":"PROJECT_AUTHORED",
                 "curriculum_standard":"普通高中数学课程标准（2017年版2020年修订）",
                 "standard_url":"https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf",
                 "author_role":"PROJECT_AUTHOR"},
            "review":{"status":"REVIEW_PENDING","reviewer_id":None,
                      "reviewed_at":None,"review_record":None},
            "teacher_solution_visibility":"TEACHER_ONLY",
        }
        DeepLesson.model_validate(obj)
        result.append(obj)
    need(not set(x["id"] for x in result) & set(ids),"duplicate new lesson IDs")
    count=Counter(x["kind"] for x in result)
    status=Counter(x["review"]["status"] for x in prior+result)
    audit={
       "batch":107,"source":"ORIGINAL_MATH_EDITORIAL_TEACHER_PENDING",
       "author_file_sha256":sha256((ROOT/"scripts/kb_batch107_lesson_authoring.py").read_bytes()).hexdigest(),
       "engineering_map_sha256":sha256((ROOT/"curriculum/highschool_math/curriculum_map.json").read_bytes()).hexdigest(),
       "number_of_new_deep_drafts":10,"new_teacher_worked_examples":20,
       "new_nonleaking_hint_levels":30,"new_counterexamples":10,
       "new_near_and_far_transfers":20,
       "new_bounded_exact_witnesses":10,"new_invalid_generalization_rejections":10,
       "new_teacher_draft_prerequisite_edges":sum(len(v) for v in deps.values()),
       "new_lesson_types":dict(count),
       "preexisting_deep_lessons":len(prior),"with_new_drafts":len(prior)+len(result),
       "review_counts":dict(status),
       "source_to_engineering_crosswalk":[
           {"lesson_id":r["id"],"source_key":source_keys[i],
            "editorial_source_candidate_id":anchor[source_keys[i]]["candidate_id"],
            "source_page":anchor[source_keys[i]]["page"],
            "source_track_hint":anchor[source_keys[i]]["track"],
            "engineering_curriculum_id":r["curriculum_ids"][0],
            "engineering_level":known[r["curriculum_ids"][0]]["level"],
            "approved_official_atom_id":None,"teacher_approved":False,
            "general_proof_certified":False,"bounded_math_evidence":check(source_keys[i]),
            "draft_prerequisite_lesson_ids":r["prerequisite_lesson_ids"]}
           for i,r in enumerate(result)],
       "official_seven_track_denominators":{t:None for t in TRACKS},
       "teacher_approvals":0,"student_authoritative_releases":0,
       "unreviewed_prior_prerequisite_labels":172,
       "uncertified_prior_proof_steps":538,
       "unresolved_prior_conflicts":10,
       "scope_notices":[
           "Source candidate is not an officially certified atom and internal curriculum ID is not a seven-track source crosswalk.",
           "Proof steps are teacher-pending mathematical arguments, not machine-certified universal proofs.",
           "Student independent challenge cannot retrieve the full teacher worked example, proof or final answer.",
           "Historical 172 textual prerequisites are not promoted by this draft dependency graph.",
           "No artificial REVIEW_PENDING to APPROVED transition is permitted."]}
    need(audit["teacher_approvals"]==audit["student_authoritative_releases"]==0,
         "cannot invent teacher approval")
    return result,audit


def markdown(docs,audit):
    lines=["# Batch107｜10份完整原创数学讲义（教师候审，非学生权威知识）","",
          "全部REVIEW_PENDING / TEACHER_ONLY；仅供教师核查。正式七轨原子分母未知，",
          "精确有限实例不等于普遍证明认证，所有教师答案不得进入独立挑战。","",
          f"本批：{len(docs)}份、{audit['new_teacher_worked_examples']}道分步例题、"
          f"{audit['new_nonleaking_hint_levels']}条提示、"
          f"{audit['new_near_and_far_transfers']}项近远迁移。",""]
    for i,r in enumerate(docs):
        e=audit["source_to_engineering_crosswalk"][i]
        lines.extend([f"## {r['id']}｜{r['title']}","",
           f"工程条目：{r['curriculum_ids'][0]}；来源编辑候选：{e['editorial_source_candidate_id']}（"
           f"第{e['source_page']}页；非教师确认的正式课标原子）。","",
           "**正式陈述：** "+r["statement"],"",
           "**适用前提：** "+"；".join(r["assumptions"]),"",
           "**数学记号：** "+"；".join(r["notation"]),"",
           "**先修：** "+"；".join(r["prerequisites"]),"",
           "**候审先修ID：** "+(", ".join(r["prerequisite_lesson_ids"]) or "无"),""])
        for j,z in enumerate(r["proof_steps"],1):
            lines.extend([f"**证明第{j}步：** {z['claim']}","**依据：** "+z["reason"],""])
        for j,z in enumerate(r["rationale_steps"],1):
            lines.extend([f"**说明第{j}步：** {z}",""])
        bad=r["counterexamples"][0]
        lines.extend(["**典型错法：** "+bad["false_claim"],"",
            "**具体反例：** "+bad["example"],"",
            "**数学失效原因：** "+bad["explanation"],"",
            "**追问：** "+r["misconceptions"][0]["repair_question"],""])
        for j,z in enumerate(r["worked_examples"],1):
            lines.extend([f"### 教师例题{j}","",z["question"],"",
                *[f"{k}. {s}" for k,s in enumerate(z["steps"],1)],
                "","**教师答案：** "+z["answer"],"",
                "**检查：** "+z["check"],""])
        lines.extend(["**提示阶梯（按需逐级披露）：** "+"；".join(r["hint_ladder"]),"",
            "**近迁移：** "+r["transfer"]["near"],"",
            "**远迁移：** "+r["transfer"]["far"],""])
    return "\n".join(lines).rstrip()+"\n"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    docs,audit=build()
    for path,content in ((PACK,canonical(docs)),(AUDIT,canonical(audit)),(MD,markdown(docs,audit))):
        if args.check:
            need(path.is_file() and path.read_text(encoding="utf8")==content,"artifact drift "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding="utf8")
    # Read back through the actual app loader on the active Mac instance.
    lessons.cache_clear()
    loaded={item.id for item in lessons()}
    need(all(x["id"] in loaded for x in docs),"deep knowledge app loader failed")
    print("Batch107: ten teacher-only complete lessons, twenty checked worked examples, ten bounded oracles; --check",args.check)

if __name__=="__main__":main()
