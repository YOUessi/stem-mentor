#!/usr/bin/env python3
"""Batch89 twelve previously unlinked historic P0 proof drafts and 300-topic backlog.
No teacher signature, official syllabus atomization, or formal theorem certification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"backend"),str(ROOT/"scripts")]
import build_kb_batch86_p0_reviews as B86
import build_kb_batch87_candidate_census as B87
import build_kb_batch88_relations as B88
from app.kb_batch89_exact_witness import check_all

AUTHOR = ROOT/"knowledge/editorial_review/kb_batch89_p0_teacher_authoring.json"
OUT = ROOT/"knowledge/editorial_review/kb_batch89_p0_teacher_drafts.json"
AUDIT = ROOT/"docs/evaluation/KB_BATCH89_P0_AND_CANDIDATE_BACKLOG.json"
DOC = ROOT/"docs/evaluation/KB_BATCH89_P0_AND_CANDIDATE_BACKLOG.md"
SCHEMA = "kb89-12-unique-P0-teacher-proof-authoring-v1"
CARD_FIELDS = {"id","source_step","kind","title","assumptions","statement","proof_steps",
               "boundary","wrong_method","worked_examples","hints","near","far","prerequisites"}
ROOT_FIELDS = {"schema_version","standard_version","provenance","review_status",
               "teacher_approved","formal_general_certified","student_publishable",
               "student_free_text_verified","cards"}
STATUSES={"REVIEW_PENDING","TEACHER_ONLY","NOT_FORMALLY_CERTIFIED"}

def require(x,why):
    if not x: raise ValueError(why)

def duplicate_guard(items):
    out={}
    for k,v in items:
        require(k not in out, "duplicate JSON key "+k)
        out[k]=v
    return out

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),object_pairs_hook=duplicate_guard)

def serialize(obj):
    return json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n"

def build(author=None,history=None,census=None,relations=None):
    author=load(AUTHOR) if author is None else author
    history=B86.build() if history is None else history
    census=B87.build() if census is None else census
    relations=B88.build() if relations is None else relations
    require(type(author) is dict and set(author)==ROOT_FIELDS,"authoring fields drift")
    require(author["schema_version"]==SCHEMA
            and author["standard_version"]=="普通高中数学课程标准（2017年版2020年修订）"
            and author["provenance"]=="ORIGINAL_PROJECT_MATH_AUTHORING_ON_MAC"
            and author["review_status"]=="REVIEW_PENDING"
            and author["teacher_approved"] is False
            and author["formal_general_certified"] is False
            and author["student_publishable"] is False
            and author["student_free_text_verified"] is False,"illicit release or authoring claims")
    require(history["historical_steps"]==538 and history["P0_total"]==182
            and history["combined_unique_P0_steps_with_drafts"]==64
            and history["remaining_P0_without_source_step_cards"]==118
            and history["unresolved_conflicts"]==10
            and history["formal_math_certifications"]==history["teacher_approvals"]==0,
            "upstream mathematical proof census drift")
    queue=load(B86.B85.B81.PROOFS)["step_review_queue"]
    require(hashlib.sha256(B86.B85.B81.dump(load(B86.B85.B81.PROOFS)).encode()).hexdigest()
            == B86.B85.B81.EXPECTED_SHA["proofs"],"historical proof SHA drift")
    idx={x["id"]:x for x in queue}
    require(len(idx)==len(queue)==538,"source step ledger collision")
    cards=author["cards"]
    require(type(cards) is list and len(cards)==12,"twelve complete drafts required")
    eligible=set(history["remaining_P0_source_step_ids"])
    seen=set()
    compiled=[]
    finite_witnesses=check_all()
    for i,c in enumerate(cards,1):
        require(type(c) is dict and set(c)==CARD_FIELDS,"teacher card schema violation")
        sid=c["source_step"]
        require(c["id"]==f"KB89-P{i:02d}" and type(sid) is str
                and sid in eligible and sid in idx and sid not in seen
                and idx[sid]["risk_priority"].startswith("P0_")
                and idx[sid]["review_card_id"] is None,
                "not an unreviewed unique historical P0 source step")
        seen.add(sid)
        require(c["kind"]=="THEOREM","cannot invent a different knowledge type")
        require(all(type(c[k]) is str and len(c[k].strip())>=min_len for k,min_len in
                    (("title",8),("statement",30),("boundary",28),("wrong_method",18),
                     ("near",15),("far",18))),"insufficient explicit maths explanation")
        require(type(c["assumptions"]) is list and len(c["assumptions"])>=2
                and all(type(v) is str and len(v)>=10 for v in c["assumptions"]),
                "mathematical assumptions missing")
        require(type(c["proof_steps"]) is list and len(c["proof_steps"])==3
                and all(type(v) is str and len(v)>=22 for v in c["proof_steps"]),
                "three independently reviewable substantial proof steps required")
        require(type(c["worked_examples"]) is list and len(c["worked_examples"])==2
                and all(type(v) is dict and set(v)=={"question","teacher_solution"}
                    and len(v["question"])>=15 and len(v["teacher_solution"])>=24
                    for v in c["worked_examples"]), "teacher-only solved examples missing")
        require(type(c["hints"]) is list and len(c["hints"])==3
                and len(set(c["hints"]))==3 and all(type(v) is str and len(v)>=12 for v in c["hints"]),
                "three distinct non-spoiler hints required")
        require(type(c["prerequisites"]) is list and len(c["prerequisites"])>=2
                and all(type(v) is str and len(v)>=4 for v in c["prerequisites"]), "prereqs missing")
        compiled.append({**c,"original_historical_step_sha256":idx[sid]["source_sha256"],
            "original_risk_groups":idx[sid]["risk_groups"],
            "source_kind":"HISTORICAL_PROJECT_DRAFT_STEP_NOT_OFFICIAL_CURRICULUM_ATOM",
            "review_status":"REVIEW_PENDING","teacher_review_signature":None,
            "teacher_solution_visibility":"TEACHER_ONLY",
            "student_authoritative_index_eligible":False,
            "student_publishable":False,"general_theorem_formally_certified":False,
            "student_free_text_verified":False,
            "official_curriculum_atom_id":None,
            "evidence_scope":"EDITORIAL_GENERAL_PROOF_ARGUMENT_NOT_FORMALLY_CERTIFIED",
            "finite_mathematical_witness":finite_witnesses[i-1],
            "worked_examples":[{**v,"visibility":"TEACHER_ONLY"} for v in c["worked_examples"]]})
    require(len(seen)==12 and len(eligible-seen)==106,"risk census count mismatch")
    require(census["exact_string_distinct_label_count"]==300
            and census["official_curriculum_atom_denominator"] is None
            and census["total_full_page_teacher_atomizations"]==0
            and census["teacher_approved_complete_lessons"]==0,"official curriculum gate failure")
    require(relations["reviewed_relation_count"]==36
            and relations["semantic_equivalence_adjudicated_count"]==0
            and relations["official_curriculum_atom_denominator"] is None
            and relations["teacher_approved_atoms"]==0,"unapproved relation gate failure")
    ids={x["candidate_id"]:x for x in census["provisional_candidates"]}
    adjacency={k:[] for k in ids}
    for pair in relations["reviewed_relations"]:
        for side in ("left","right"):
            candidate=pair[side]["candidate_id"]
            require(candidate in adjacency and pair[side]["source_line_sha256"]==ids[candidate]["source_line_sha256"],
                    "relation source SHA mismatch")
            adjacency[candidate].append(pair["review_id"])
    bytrack=Counter()
    compared=Counter()
    backlog=[]
    for x in census["provisional_candidates"]:
        uid=x["candidate_id"]
        tr=x["track"]
        bytrack[tr]+=1
        if adjacency[uid]: compared[tr]+=1
        backlog.append({"candidate_id":uid,"provisional_topic":x["provisional_topic"],
          "track":tr,"source_review_id":x["source_review_id"],
          "source_line_sha256":x["source_line_sha256"],
          "source_page":x["printed_page"],"reviewed_relation_ids":adjacency[uid],
          "relation_count":len(adjacency[uid]),
          "cross_track_status":"EDITORIAL_PAIRS_ONLY" if adjacency[uid] else "NOT_YET_COMPARED",
          "prerequisite_validation":"NOT_EVALUATED",
          "official_math_atom_id":None,"official_atom_count_contribution":None,
          "teacher_approval":None,"review_status":"REVIEW_PENDING",
          "student_authoritative_index_eligible":False})
    nseen=sum(bool(v) for v in adjacency.values())
    require(len(backlog)==300 and nseen==70 and
            sum(len(v) for v in adjacency.values())==72 and
            sum(bytrack.values())==300 and
            set(bytrack)==set(census["by_track"])-{"ELECTIVE_E"},"candidate audit lost identities")
    result={"schema_version":"kb89-P0-and-unadjudicated-300-topic-scope-audit-v1",
      "source_queue_sha256":B86.B85.B81.EXPECTED_SHA["proofs"],
      "authoring_sha256":hashlib.sha256(AUTHOR.read_bytes()).hexdigest(),
      "new_unique_P0_drafts":12,"unique_P0_with_teacher_drafts":76,
      "P0_historical_step_denominator":182,"P0_missing_teacher_drafts":106,
      "historical_proof_steps_not_formally_certified":538,
      "historic_math_conflicts_not_resolved":10,
      "source_anchor_editorials":428,"provisional_labels":300,
      "cross_track_pairs_reviewed_as_proposals":36,
      "provisional_candidates_with_any_pair":nseen,
      "provisional_candidates_unpaired":300-nseen,
      "per_track":{tr:{"provisional":bytrack[tr],"paired_in_editorial":compared[tr],
                 "unpaired":bytrack[tr]-compared[tr],
                 "official_atom_denominator":None,"approved_lessons":0}
                   for tr in B87.TRACKS},
      "official_atom_denominator":None,"full_page_teacher_atomizations":0,
      "teacher_approved":0,"student_published":0,
      "formal_general_certificates":0,"student_free_text_verified":0,
      "teacher_pending_packets":12,
      "provisional_candidate_backlog":backlog,
      "remaining_unlinked_P0_source_step_ids":sorted(eligible-seen)}
    packet={"schema_version":"kb89-original-12-P0-teacher-drafts-v1",
      "source_step_ledger_sha256":B86.B85.B81.EXPECTED_SHA["proofs"],
      "authoring_sha256":result["authoring_sha256"],
      "teacher_approved":0,"student_published":0,
      "general_formal_certificates":0,"student_free_text_verified":0,
      "official_curriculum_atom_denominator":None,"cards":compiled}
    return packet,result

def markdown(packet,audit):
    lines=["# Batch89｜12份高风险历史证明教师审稿草案及300个未裁决主题台账","",
       "**全部草案仅供教师审稿，不代表已批准/已形式化认证/已发布。**",
       "已完成428条项目来源锚点初步解释；300为未去重临时主题，并不是官方课程知识原子分母。",
       "36对编辑关系涉及70个临时主题（有些主题参与多对），仍有230个没有任何配对审查。",
       "历史P0源步骤182项中，已有独立源ID教师草案从64增至76，仍有106项缺；538条历史步骤仍未形式认证。",
       "原历史10组数学冲突继续待教师裁决；所有新稿的证明仍属于人工编写、待核对的论证。","",
       "| 课程轨道 | 临时主题 | 有编辑配对 | 无配对 | 正式知识原子分母 |",
       "|---|---:|---:|---:|---|"]
    for track,v in audit["per_track"].items():
        lines.append(f"| {track} | {v['provisional']} | {v['paired_in_editorial']} | {v['unpaired']} | 未知 |")
    lines += ["","## 每份待教师独立核对的数学证明与错因",""]
    for c in packet["cards"]:
        lines += [f"### {c['id']}｜{c['title']}","",
          f"冻结历史步骤：{c['source_step']} / SHA256 `{c['original_historical_step_sha256']}`；**不是官方课程原子ID**。",
          "","**全部前提：**"+"；".join(c["assumptions"]),
          "","**数学陈述：**"+c["statement"],"",
          "**逐步论证（仍待独立数学审核）：**"]
        lines += [f"{j}. {v}" for j,v in enumerate(c["proof_steps"],1)]
        lines += ["", "**不适用边界/反例：**"+c["boundary"],"",
          "**典型错误方法：**"+c["wrong_method"],"",
          "**仅教师可见的原创例题与分步解答：**"]
        for v in c["worked_examples"]:
            lines += [f"- 题：{v['question']} **教师解：**{v['teacher_solution']}"]
        lines += ["","**学生提示梯度（不要直接泄漏答案）：**"]
        lines += [f"{j}. {v}" for j,v in enumerate(c["hints"],1)]
        lines += ["", "**近迁移：**"+c["near"],"","**远迁移：**"+c["far"],"",
          "**先修主题（尚未映射正式ID）：**"+"；".join(c["prerequisites"]),""]
    lines += ["## 剩余阻断","",
      "1. 教师逐页完整拆解61页目前0/61；正式必修、选择性必修、A–E七轨知识原子分母仍未知。",
      "2. 230个未曾配对的临时主题需跨页跨轨语义审查；所有暂定同义对不可未经教师批准合并。",
      "3. 106个历史P0源步骤仍无直接教师稿；当前12份不代表完成一般形式认证。",
      "4. 未见题、完整教师签署及学生正式检索发布目前仍是0；审核门禁不能绕开。",""]
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    v=p.parse_args()
    packet,audit=build()
    for dest,content in ((OUT,serialize(packet)),(AUDIT,serialize(audit)),(DOC,markdown(packet,audit))):
        if v.check:
            require(dest.exists() and dest.read_text(encoding="utf8")==content,
                    "generated file drift "+str(dest))
        else:
            dest.write_text(content,encoding="utf8")
    print("Batch89: 12 new uniquely linked P0 drafts; 76/182 historical P0 draft-covered; 300 provisional topics, 230 unpaired; 0 teacher-approved")
if __name__=="__main__":main()

