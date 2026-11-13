#!/usr/bin/env python3
"""Create and audit 6 independently authored deep drafts; editor-only.

Rebuilds deterministic JSON + complete Markdown; never fabricates
official knowledge atom coverage or teacher approval.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
import re
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch106_deep_authoring import UNITS
from app.deep_knowledge import DeepLesson, curriculum, DEEP_DIR
from app.kb_batch106_math import witness
ORACLE_KEYS=("not_forall","amgm","ivt","bisection","second_derivative","riemann")

AUTHOR=ROOT/"scripts/kb_batch106_deep_authoring.py"
PACK=DEEP_DIR/"batch106_scope_six.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH106_DEPTH_AUDIT.json"
MD=ROOT/"docs/evaluation/KB_BATCH106_SIX_TEACHER_LESSONS.md"
STANDARD="普通高中数学课程标准（2017年版2020年修订）"
URL="https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf"
# These links are explicitly authored *teacher-only draft dependencies*.
# They have no student publishing authority; remaining historical
# textual prerequisite labels are NOT silently promoted to edges.
LINKS={3:(2,)}
TRACKS=("必修","选择性必修","选修A","选修B","选修C","选修D","选修E")

def need(ok,reason):
    if not ok:raise ValueError(reason)

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"

def build(units=UNITS, links=LINKS):
    known={c["id"]:c for c in curriculum()}
    need(len(units)==6,"Batch106 requires 6 substantive lesson records")
    need(set(links) <= set(range(6)),"dangling author link")
    result=[]
    for i,row in enumerate(units):
        need(row["curriculum_id"] in known,"unknown project engineering curriculum ID")
        need(row["kind"] in {"concept","method","theorem"},"invalid knowledge kind")
        need(len(row["examples"])==2 and all(len(x["steps"])>=2 for x in row["examples"]), "two complete worked examples required")
        need(len(row["hints"])==3 and len(set(row["hints"]))==3,"incomplete nonleaking hint ladder")
        need(len(row["reasoning"])>=3 and len(row["statement"])>35,"insufficient mathematical statement")
        need(len(row["negative"])==3 and all(len(x)>10 for x in row["negative"]), "missing concrete counterexample or repair")
        need(len(row["prereqs"])>=1 and len(row["notation"])>=1,"missing teacher prerequisites or notation")
        deps=[f"math.hs.batch106.{j+1:02d}" for j in links.get(i,())]
        need(all(j<i for j in links.get(i,())),"prerequisite must precede dependent lesson")
        need(len(set(deps))==len(deps),"duplicate prerequisite")
        proof=row["reasoning"] if row["kind"]=="theorem" else []
        why=[] if proof else row["reasoning"]
        need(all(isinstance(s,dict) and len(s.get("claim",""))>=12 and len(s.get("reason",""))>=12 for s in proof),"incomplete step-by-step proof")
        need(all(isinstance(s,str) and len(s)>=16 for s in why),"missing method/definition rationale")
        payload={
           "id":f"math.hs.batch106.{i+1:02d}",
           "curriculum_ids":[row["curriculum_id"]],
           "kind":row["kind"],"title":row["title"],"version":"1.0.0",
           "notation":row["notation"],"prerequisites":row["prereqs"],
           "prerequisite_lesson_ids":deps,
           "definition":row["statement"] if row["kind"]=="concept" else None,
           "statement":row["statement"],"assumptions":row["assumptions"],
           "proof_steps":proof,"rationale_steps":why,
           "boundaries":row["assumptions"],
           "counterexamples":[{"false_claim":row["negative"][0],
                               "example":row["negative"][1],
                               "explanation":row["negative"][2]}],
           "worked_examples":row["examples"],
           "misconceptions":[{"error":row["negative"][0],
                              "why_wrong":row["negative"][2],
                              "repair_question":"请明确指出反例中的哪一项原命题前提失效，并尝试改正推理。"}],
           "hint_ladder":row["hints"],
           "transfer":{"near":row["transfers"][0],"far":row["transfers"][1]},
           "provenance":{"kind":"PROJECT_AUTHORED","permission":"PROJECT_AUTHORED",
                         "curriculum_standard":STANDARD,"standard_url":URL,
                         "author_role":"PROJECT_AUTHOR"},
           "review":{"status":"REVIEW_PENDING","reviewer_id":None,
                     "reviewed_at":None,"review_record":None},
           "teacher_solution_visibility":"TEACHER_ONLY",
        }
        DeepLesson.model_validate(payload)
        w=witness(ORACLE_KEYS[i])
        need(w["finite_or_symbolic_witness_passed"] and w["invalid_generalization_rejected"]
             and not w["general_proof_certified"] and not w["teacher_approved"],
             "bounded independent mathematical oracle failed")
        result.append(payload)
    existing=[]
    for path in sorted(DEEP_DIR.glob("*.json")):
        if path==PACK:continue
        for doc in json.loads(path.read_text(encoding="utf8")):
            # Reconstruct as-of Batch106, excluding subsequently authored
            # drafts; the frozen report must never rewrite its old denominator.
            match=re.match(r"^math\.hs\.batch([0-9]+)\.",doc["id"])
            if match and int(match.group(1))>106:
                continue
            existing.append(doc)
    preexisting={d["id"] for d in existing}
    ours={d["id"] for d in result}
    need(not preexisting & ours and len(preexisting)==len(existing),"duplicate lesson ID")
    for d in result:
        need(set(d["prerequisite_lesson_ids"]) <= preexisting|ours, "orphan link")
        need(set(d["prerequisite_lesson_ids"]) & {d["id"]} == set(), "self-link")
    mapped={x["id"] for x in curriculum()}
    status=Counter(d["review"]["status"] for d in existing+result)
    projects=Counter(x["level"] for x in curriculum())
    audit={
       "batch":"106","source_kind":"PROJECT_AUTHORED_ORIGINAL_EDITORIAL",
       "editorial_source_file_sha256":sha256(AUTHOR.read_bytes()).hexdigest(),
       "engineering_mapping_sha256":sha256((ROOT/"curriculum/highschool_math/curriculum_map.json").read_bytes()).hexdigest(),
       "new_deep_drafts":6,"new_worked_examples":12,"new_hint_levels":18,
       "new_theorem_drafts":sum(d["kind"]=="theorem" for d in result),
       "new_finite_math_witnesses":6,"new_bad_case_rejections":6,
       "prerequisite_edges_editor_only":sum(len(v) for v in links.values()),
       "existing_deep_lesson_documents":len(existing),
       "deep_lesson_documents_with_new_drafts":len(existing)+6,
       "existing_project_mapping_count":len(mapped),
       "engineering_map_counts_by_level":dict(sorted(projects.items())),
       "official_atom_denominator":None,
       "official_atom_denominators_by_seven_tracks":{t:None for t in TRACKS},
       "teacher_approved":0,"student_authoritative_index_eligible":0,
       "general_theorem_certificates":0,"unresolved_previous_textual_prerequisites":172,
       "unresolved_historical_proof_steps":538,"unresolved_math_conflicts":10,
       "all_new_review_status":"REVIEW_PENDING",
       "teacher_solution_visibility":"TEACHER_ONLY",
       "existing_and_new_review_states":dict(sorted(status.items())),
       "lesson_to_project_topic":[{"lesson_id":d["id"],"engineering_curriculum_id":d["curriculum_ids"][0],
          "engineering_label":known[d["curriculum_ids"][0]]["concept"],
          "engineering_level":known[d["curriculum_ids"][0]]["level"],
          "official_atom_id":None,"source_clauses_verified":False,
          "review_pending_source_candidate_id":("KB106-P016-C06","KB106-P016-C10","KB106-P053-C13","KB106-P053-C14","KB106-P053-C16","KB106-P053-C23")[i],
          "teacher_reviewed":False,"math_proof_formally_certified":False,
          "bounded_exact_witness":witness(ORACLE_KEYS[i]),
          "editor_only_prerequisite_lesson_ids":d["prerequisite_lesson_ids"]}
          for i,d in enumerate(result)],
       "limitations":[
          "All 6 curricula references are internal project engineering IDs, not official atoms.",
          "Finite exact checks cannot establish the universal truth of a theorem.",
          "Historical textual prerequisite backlog 172 remains pending independent human review.",
          "Student challenge paths cannot retrieve teacher-only examples, proofs or answers.",
       ]
    }
    need(audit["teacher_approved"]==audit["student_authoritative_index_eligible"]==0,
         "cannot manufacture human approval")
    return result,audit

def markdown(docs,audit):
    lines=["# Batch106｜6份原创数学深度讲义（教师候审）","",
       "**安全边界：** 所有条目 REVIEW_PENDING / TEACHER_ONLY；工程映射不是官方原子分母；",
       "独立的有限精确算例不能代替普遍证明或真实教师审核。","",
       f"本批新增 {len(docs)} 份、{audit['new_worked_examples']} 道例题、{audit['new_hint_levels']} 条提示。",""]
    for d in docs:
        lines += [f"## {d['id']}｜{d['title']}","",
         f"工程映射候选：{d['curriculum_ids'][0]}（尚未确认官方原子归属）","",
         "**数学陈述/定义：** "+d["statement"],"",
         "**适用前提：** "+"；".join(d["assumptions"]),"",
         "**记号：** "+"；".join(d["notation"]),"",
         "**先修：** "+"；".join(d["prerequisites"]),"",
         "**已显式编排的教师候审先修ID：** "+(", ".join(d["prerequisite_lesson_ids"]) or "无"),""]
        for j,p in enumerate(d["proof_steps"],1):
            lines.append(f"证明第{j}步：{p['claim']}。**理由：** {p['reason']}")
        for j,p in enumerate(d["rationale_steps"],1):
            lines.append(f"解释第{j}步：{p}")
        n=d["counterexamples"][0]
        m=d["misconceptions"][0]
        lines += ["", "**失效案例：** "+n["false_claim"]+"；"+n["example"],
                  "**数学原因：** "+n["explanation"],"",
                  "**修复追问：** "+m["repair_question"],""]
        for i,e in enumerate(d["worked_examples"],1):
            lines += [f"### 教师例题 {i}","",e["question"],"",
                      "分步："+ "；".join(e["steps"]),"",
                      "教师答案："+e["answer"],"","独立算例核验："+e["check"],""]
        lines += ["**启发式提示（教师可按层披露）：** "+"；".join(d["hint_ladder"]),"",
                  "**近迁移：** "+d["transfer"]["near"],"",
                  "**远迁移：** "+d["transfer"]["far"],""]
    return "\n".join(lines).rstrip()+"\n"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    docs,audit=build()
    for path,content in ((PACK,canonical(docs)),(AUDIT,canonical(audit)),(MD,markdown(docs,audit))):
        if args.check:
            need(path.is_file() and path.read_text(encoding="utf8")==content,f"artifact drift: {path}")
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding="utf8")
    print("Batch106",len(docs),"new teacher-only draft lessons, 12 worked examples, 6 finite oracles,",
          audit["prerequisite_edges_editor_only"],"curated candidate prereq links; --check",args.check)

if __name__=="__main__":main()
