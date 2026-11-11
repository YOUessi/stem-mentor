#!/usr/bin/env python3
"""K00+K01+K02–K06+K08+K09: 20 fully structured original DRAFT lessons.
Source anchors are PROJECT provisional labels; this cannot settle official atomic coverage.
Generated file is directly discovered by deep_knowledge.lessons() and editor-only FTS5.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/"backend"),
              str(Path(__file__).resolve().parents[1]/"scripts")]
from kb_batch91_authoring import DATA, STANDARD, PROOF_REASONS
from app.deep_knowledge import DeepLesson, curriculum
from app.kb_batch91_independent_oracles import evaluate_all
import build_kb_batch90_relations as B90
import build_kb_batch89_proofs_and_scope as B89
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"knowledge/deep/v1/batch91_source_backed_20.json"
SCOPE=ROOT/"docs/evaluation/KB_BATCH91_AUDITABLE_SCOPE.json"
DOC=ROOT/"docs/evaluation/KB_BATCH91_SOURCE_BACKED_DEEP_LESSONS.md"
SOURCE=ROOT/"scripts/kb_batch91_authoring.py"
URL="https://jyj.changdu.gov.cn/cdsjyj/c101476/202205/764ee1914e3c45aaba8e372f1b628a34/files/75676dfa9af0442db1457404a884a69f.pdf"
TRACK={"COMPULSORY":"必修","SELECTIVE_COMPULSORY":"选择性必修",
       **{"ELECTIVE_"+c:"选修拓展" for c in "ABCDE"}}
# Pedagogical prerequisite graph is deliberately smaller than the curriculum
# mapping; these are editor-only draft relations, not official atomic IDs.
PREREQUISITE_LINKS = {
    "math.hs.batch91.12": ["math.hs.batch91.03"],  # piecewise branch -> continuity
    "math.hs.batch91.13": ["math.hs.batch91.10"],  # derivative sign -> MVT bounds
    "math.hs.batch91.15": ["math.hs.batch91.12"],  # continuity -> multivariable check
    "math.hs.batch91.18": ["math.hs.batch91.07"],  # geometric growth -> compounding
    "math.hs.batch91.19": ["math.hs.batch91.04"],  # sine period -> wave frequency
    "math.hs.batch91.20": ["math.hs.batch91.07"],  # geometric ratio -> music model
}

def must(ok,why):
    if not ok: raise ValueError(why)
def dumped(obj):
    return json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n"

def build(auth=None,previous=None,history=None):
    rows=DATA if auth is None else auth
    previous=B90.build() if previous is None else previous
    history=B89.build()[1] if history is None else history
    must(previous["source_anchor_editorials"]==428 and
         previous["provisional_candidate_total"]==300 and
         previous["remaining_candidate_ids_without_any_relation"]==182 and
         previous["official_curriculum_atom_denominator"] is None and
         previous["teacher_approved"]==0 and previous["student_published"]==0,
         "upstream K00/approval guard drift")
    must(history["provisional_labels"]==300 and
         history["official_atom_denominator"] is None and
         history["teacher_approved"]==0 and history["student_published"]==0,
         "unapproved baseline or mislabeled official atom count")
    must(type(rows) is list and len(rows)==20,"all twenty substantial lessons required")
    candidates={r["candidate_id"]:r for r in history["provisional_candidate_backlog"]}
    must(len(candidates)==300,"provisional source denominator drift")
    mapped={r["id"]:r for r in curriculum()}
    ids=set(); anchors=set(); cards=[]; links=[]
    finite=evaluate_all()
    for i,r in enumerate(rows,1):
        must(type(r) is dict and set(r)=={"anchor","curriculum_id","kind","title",
             "definition","statement","assumptions","steps","boundary","negative",
             "wrong","examples","hints","transfer","notation","prerequisites"},
             "unrecognized or missing author fields")
        anchor=r["anchor"]; key=r["curriculum_id"]
        must(type(anchor) is str and anchor in candidates and anchor not in anchors,
             "orphan/duplicate source anchor")
        must(type(key) is str and key in mapped,"unknown engineering curriculum hook")
        src=candidates[anchor]
        must(src["official_math_atom_id"] is None and
             src["teacher_approval"] is None and
             src["student_authoritative_index_eligible"] is False and
             src["source_line_sha256"] and src["source_review_id"],
             "source improperly certified or provenance incomplete")
        must(src["track"] in TRACK,"unknown original seven-track source")
        label=f"math.hs.batch91.{i:02d}"
        must(label not in ids,"duplicate new lesson")
        ids.add(label); anchors.add(anchor)
        must(r["kind"] in {"concept","theorem","method"},"unexpected lesson kind")
        for k,n in (("definition",30),("statement",30),("boundary",24),("title",8)):
            must(type(r[k]) is str and len(r[k])>=n,"insufficient "+k)
        must(type(r["assumptions"]) is list and len(r["assumptions"])>=2
             and all(type(v) is str and len(v)>=9 for v in r["assumptions"]),
             "mathematical domain assumptions missing")
        must(type(r["steps"]) is list and len(r["steps"])>=3,"derivation too short")
        if r["kind"]=="theorem":
            must(all(type(v) is tuple and len(v)==2 and len(v[0])>=4 and len(v[1])>=20
                     for v in r["steps"]),"proof needs each premise and step reason")
        else:
            must(all(type(v) is str and len(v)>=13 for v in r["steps"]),
                 "concept/method rationale incomplete")
        must(type(r["examples"]) is list and len(r["examples"])==2
             and all(type(v) is dict and set(v)=={"question","steps","answer","check"}
                    and len(v["steps"])>=2 and len(v["check"])>=8
                    for v in r["examples"]),"two worked exact examples required")
        must(type(r["negative"]) is tuple and len(r["negative"])==3 and
             all(len(s)>=10 for s in r["negative"]),"negative witness absent")
        must(type(r["wrong"]) is tuple and len(r["wrong"])==3 and
             all(len(s)>=10 for s in r["wrong"]),"wrong method and repair absent")
        must(type(r["hints"]) is list and len(r["hints"])==3 and
             len(set(r["hints"]))==3 and all(len(v)>=9 for v in r["hints"]),
             "non-leaking three-level hints required")
        must(type(r["transfer"]) is tuple and len(r["transfer"])==2 and
             all(len(x)>=12 for x in r["transfer"]),"near/far transfers missing")
        must(type(r["notation"]) is list and len(r["notation"])>=3
             and type(r["prerequisites"]) is list and len(r["prerequisites"])>=2,
             "symbols/prerequisites missing")
        record={
          "id":label,"curriculum_ids":[key],"kind":r["kind"],"title":r["title"],
          "version":"1.0.0","notation":r["notation"],"prerequisites":r["prerequisites"],
          "prerequisite_lesson_ids":PREREQUISITE_LINKS.get(label,[]),
          "definition":r["definition"] if r["kind"]=="concept" else None,
          "statement":r["statement"] if r["kind"]!="concept" else None,
          "assumptions":r["assumptions"],
          "proof_steps":[{"claim":x+"："+y,"reason":PROOF_REASONS[anchor][j]} for j,(x,y) in enumerate(r["steps"])]
                          if r["kind"]=="theorem" else [],
          "rationale_steps":r["steps"] if r["kind"]!="theorem" else [],
          "boundaries":[r["boundary"]],
          "counterexamples":[dict(false_claim=r["negative"][0],
                                  example=r["negative"][1],
                                  explanation=r["negative"][2])],
          "worked_examples":r["examples"],
          "misconceptions":[dict(error=r["wrong"][0],why_wrong=r["wrong"][1],
                                 repair_question=r["wrong"][2])],
          "hint_ladder":r["hints"],
          "transfer":{"near":r["transfer"][0],"far":r["transfer"][1]},
          "provenance":{"kind":"PROJECT_AUTHORED","permission":"PROJECT_AUTHORED",
            "curriculum_standard":STANDARD,"standard_url":URL,
            "author_role":"PROJECT_AUTHOR"},
          "review":{"status":"REVIEW_PENDING","reviewer_id":None,
            "reviewed_at":None,"review_record":None},
          "teacher_solution_visibility":"TEACHER_ONLY"
        }
        DeepLesson.model_validate(record)
        cards.append(record)
        links.append({
          "knowledge_id":label,"source_candidate_id":anchor,
          "source_review_id":src["source_review_id"],
          "source_line_sha256":src["source_line_sha256"],
          "source_track":src["track"],"source_page":src["source_page"],
          "source_topic_provisional":src["provisional_topic"],
          "engineering_curriculum_id":key,
          "engineering_level":mapped[key]["level"],
          "cross_track_mapping_is_editorial_only":TRACK[src["track"]]!=mapped[key]["level"],
          "curriculum_atom_id":None,"teacher_review":None,
          "math_general_proof_certificate":None,
          "student_publishable":False,
          "editor_status":"REVIEW_PENDING",
          "finite_mathematical_evidence":finite[i]
        })
    must(len(anchors)==len(cards)==20,"missing lesson-to-source bijection")
    must(set(PREREQUISITE_LINKS).issubset(ids) and
         all(set(v).issubset(ids) and len(v)==len(set(v)) and k not in v
             for k,v in PREREQUISITE_LINKS.items()),"invalid draft prerequisite graph")
    bytrack=Counter(x["source_track"] for x in links)
    must(set(bytrack)>={"COMPULSORY","SELECTIVE_COMPULSORY",
                       "ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D"},
         "insufficient cross-track lesson coverage")
    # Separate coverage denominators; no automatic semantic merge or official count.
    baseline=Counter(r["track"] for r in candidates.values())
    already=Counter()
    for c in candidates.values():
        if c["relation_count"]: already[c["track"]]+=1
    paired91=set()
    for v in previous["source_locked_relations"]:
        paired91.update((v["left_candidate_id"],v["right_candidate_id"]))
    pertrack={}
    for track in TRACK:
        current={x["source_candidate_id"] for x in links if x["source_track"]==track}
        pertrack[track]={
          "project_provisional_candidate_count":baseline[track],
          "new_deep_draft_candidates":len(current),
          "remaining_without_batch91_deep_draft":baseline[track]-len(current),
          "previously_related_candidate_count":already[track],
          "source_track_official_atom_denominator":None,
          "approved":0
        }
    must(sum(x["project_provisional_candidate_count"] for x in pertrack.values())==300,
         "seven track provisional denominator mismatch")
    report={
      "schema_version":"kb91-source-audited-editor-deep-coverage-v1",
      "standard_version":STANDARD,"source_author_sha256":sha256(SOURCE.read_bytes()).hexdigest(),
      "scope_relations_sha256":sha256(B90.OUT.read_bytes()).hexdigest(),
      "source_backlog_sha256":sha256(B89.AUDIT.read_bytes()).hexdigest(),
      "official_curriculum_atom_denominator":None,"official_atom_counts_by_track":
                 {k:None for k in TRACK},
      "source_anchor_count":428,"source_provisional_labels":300,
      "source_relations_editorial":60,"unpaired_provisional_labels":182,
      "full_page_teacher_atomization_reviews":0,
      "canonical_new_deep_lessons":len(cards),
      "finite_exact_positive_cases":len(finite),
      "finite_boundary_or_counterexample_rejections":len(finite),
      "canonical_lesson_source_links":links,
      "per_track":pertrack,"teacher_approved":0,
      "student_authoritative_release":0,
      "student_free_text_step_certifications":0,
      "general_theorem_proof_certifications":0,
      "historical_proof_steps_not_certified":538,
      "P0_historical_steps_without_teacher_cards":106,
      "unresolved_math_conflicts":10,
      "source_relation_status":"EDITORIAL_PROVISIONAL_NOT_A_DEDUPLICATED_SYLLABUS",
      "student_solution_access":"TEACHER_ONLY_DRAFTS_NOT_STUDENT_INDEXED"
    }
    return cards,report

def markdown(cards,report):
    lines=[
      "# Batch91｜20份原创深度讲义：来源锚点×可审核知识结构×教师防泄漏",
      "",
      "本批全部为Mac原创、REVIEW_PENDING教师侧草案。每份具有定义/适用范围、"
      "完整假设、逐步证明或合法性解释、反例、错因、两道独立例题、三级提示、近远迁移。","",
      "**428来源锚点≠300临时主题≠官方课标完整原子分母。** 后者仍未知；"
      "现有60组关系仅编辑对照，不是正式去重或相同数学原子判决。","",
      "已完成教师审核0；历史538条证明步骤仍未获一般形式认证；"
      "学生自由文本未经证明验证不得擅自通过。","",
    ]
    mapping={v["knowledge_id"]:v for v in report["canonical_lesson_source_links"]}
    for c in cards:
        x=mapping[c["id"]]
        lines += [f'## {c["id"]}｜{c["title"]}',"",
          f'来源候选：{x["source_candidate_id"]}（{x["source_track"]}，'
          f'页码{x["source_page"]}）；原始行SHA-256：{x["source_line_sha256"]}',"",
          f'工程课程钩子：{x["engineering_curriculum_id"]}，'
          f'跨轨仅为编辑映射：{x["cross_track_mapping_is_editorial_only"]}；'
          '学生发布：否；真实教师审核：待审。',"",
          '**正式定义/问题背景：**'+(c["definition"] or c["statement"]), "",
          "**记号：**"+"；".join(c["notation"]),"",
          "**假设/论域：**"+"；".join(c["assumptions"]),"",
          "**定理陈述/方法边界：**"+(c["statement"] or c["definition"]),"",
          "**逐步论证：**"]
        for i,step in enumerate(c["proof_steps"],1):
            lines.append(f'{i}. {step["claim"]}（依据：{step["reason"]}）')
        for i,step in enumerate(c["rationale_steps"],1):
            lines.append(f'{i}. {step}')
        lines += ["","**不适用条件：**"+"；".join(c["boundaries"]),""]
        for n in c["counterexamples"]:
            lines += [f'**反例：**{n["false_claim"]}；{n["example"]}；{n["explanation"]}',""]
        for n in c["misconceptions"]:
            lines += [f'**典型错法：**{n["error"]}；原因：{n["why_wrong"]}；修复提问：{n["repair_question"]}',""]
        lines += ["**教师侧题族（不可直接对学生泄漏解答）：**"]
        for i,ex in enumerate(c["worked_examples"],1):
            lines += [f'{i}. {ex["question"]}',"   - "+'；'.join(ex["steps"]),
                      f'   - 教师答案：{ex["answer"]}；检查：{ex["check"]}']
        lines += ["","**学生可用渐进式提示（独立作答时仅按层展示）：**"]
        lines += [f'{i}. {v}' for i,v in enumerate(c["hint_ladder"],1)]
        lines += ["",f'近迁移：{c["transfer"]["near"]}',
                  f'远迁移：{c["transfer"]["far"]}',""]
    return "\n".join(lines).rstrip()+"\n"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    cards,scope=build()
    outputs={OUT:dumped(cards),SCOPE:dumped(scope),DOC:markdown(cards,scope)}
    for path,content in outputs.items():
        if args.check:
            must(path.is_file() and path.read_text(encoding="utf-8")==content,
                 f"generated artifact drift: {path}")
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding="utf-8")
    print("BATCH91",len(cards),"drafts",len(scope["per_track"]),
          "tracks","check" if args.check else "written","official_denominator=UNKNOWN")

if __name__=="__main__":main()
