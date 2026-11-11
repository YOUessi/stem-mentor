#!/usr/bin/env python3
"""K00/K01/K07: immutable source-provenance and explicitly incomplete
300-label candidate audit. No project label becomes an official syllabus atom.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"backend"),str(ROOT/"scripts")]
from kb_batch93_authoring import RECORDS
from app.kb_batch93_finite_oracles import check_all
PREVIOUS=ROOT/"docs/evaluation/KB_BATCH92_SOURCE_RELATIONS.json"
SOURCES=ROOT/"docs/evaluation/KB_BATCH89_P0_AND_CANDIDATE_BACKLOG.json"
AUTHOR=ROOT/"scripts/kb_batch93_authoring.py"
OUTPUT=ROOT/"docs/evaluation/KB_BATCH93_CANDIDATE_TRIAGE.json"
MARKDOWN=ROOT/"docs/evaluation/KB_BATCH93_CANDIDATE_TRIAGE.md"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY",*(f"ELECTIVE_{x}" for x in "ABCDE"))
def require(pred,msg):
    if not pred: raise ValueError(msg)
def read(p):
    def pairs(items):
        d={}
        for k,v in items:
            require(k not in d,"duplicate JSON field: "+k)
            d[k]=v
        return d
    return json.loads(Path(p).read_text(encoding="utf-8"),object_pairs_hook=pairs)
def stable(o):return json.dumps(o,sort_keys=True,ensure_ascii=False,indent=2)+"\n"

def build(source=None,previous=None,notes=None):
    source=read(SOURCES) if source is None else source
    previous=read(PREVIOUS) if previous is None else previous
    notes=RECORDS if notes is None else notes
    require(type(source) is dict and source["provisional_labels"]==300 and
            source["official_atom_denominator"] is None and
            source["teacher_approved"]==0 and source["student_published"]==0,
            "historical provisional syllabus falsely promoted")
    require(type(previous) is dict and previous["provisional_topics"]==300 and
            previous["source_anchor_count"]==428 and
            previous["cumulative_relation_pairs"]==84 and
            previous["cumulative_reviewed_provisional_topics"]==166 and
            previous["remaining_unpaired_provisional_topics"]==134 and
            previous["official_curriculum_atom_denominator"] is None and
            previous["teacher_approved"]==0 and
            previous["student_authoritative_release"]==0 and
            previous["teacher_adjudicated_atom_merges"]==0,
            "upstream audit count or authority drift")
    originals=source["provisional_candidate_backlog"]
    require(type(originals) is list and len(originals)==300,
            "missing original source label")
    byid={r["candidate_id"]:r for r in originals}
    require(len(byid)==300 and len(set(byid))==300,"duplicate original candidate")
    for s in originals:
        require(s["track"] in TRACKS and
                s["review_status"] == "REVIEW_PENDING" and
                s["official_math_atom_id"] is None and
                s["teacher_approval"] is None and
                s["student_authoritative_index_eligible"] is False and
                s["official_atom_count_contribution"] is None and
                type(s["source_line_sha256"]) is str and
                len(s["source_line_sha256"]) == 64,
                "forged prior source review or official authority")
    require(previous["general_theorem_proof_certificates"]==0 and
            all(v is None for v in previous["official_atom_denominators_by_track"].values()),
            "forged mathematical certification or syllabus count")
    unpaired=previous["remaining_unpaired_candidate_ids"]
    require(type(unpaired) is list and len(unpaired)==134 and
            len(set(unpaired))==134 and set(unpaired)<set(byid),
            "unreviewed candidate membership drift")
    paired=set(byid)-set(unpaired)
    require(len(paired)==166,"paired source count incorrect")
    require(type(notes) is list and len(notes)==24,
            "all 24 substantial original candidate notes required")
    finite=check_all()
    require(len(finite)==14,"finite verification coverage drift")
    touched=set()
    audits=[]
    for i,row in enumerate(notes,1):
        require(type(row) in (tuple,list) and len(row)==5,"author row structure")
        ident,maths,conditions,witness,boundary=row
        require(type(ident) is str and ident in unpaired and ident not in touched,
                "source not in unpaired queue or duplicate candidate")
        src=byid[ident]
        for text,minimum in ((maths,26),(conditions,25),(witness,25),(boundary,25)):
            require(type(text) is str and len(text.strip())>=minimum,
                    "mathematical substance or counterexample missing")
        require(src["track"] in TRACKS and src["review_status"]=="REVIEW_PENDING" and
                src["official_math_atom_id"] is None and
                src["teacher_approval"] is None and
                src["student_authoritative_index_eligible"] is False and
                src["relation_count"]==0 and
                src["cross_track_status"]=="NOT_YET_COMPARED" and
                len(src["source_line_sha256"])==64 and
                all(c in "0123456789abcdef" for c in src["source_line_sha256"]),
                "forged math authority or broken source-line provenance")
        touched.add(ident)
        audits.append({
            "review_id":f"KB93-SINGLE-{i:03d}",
            "candidate_id":ident,
            "provisional_topic":src["provisional_topic"],
            "track":src["track"],
            "source_review_id":src["source_review_id"],
            "source_page":src["source_page"],
            "source_line_sha256":src["source_line_sha256"],
            "editorial_math_scope":maths,
            "necessary_conditions":conditions,
            "controlled_worked_witness":witness,
            "counterexample_or_invalid_boundary":boundary,
            "finite_evidence":finite.get(ident,{"scope":"NO_INDEPENDENT_FINITE_CHECK",
                "general_theorem_certified":False,"teacher_approved":False,
                "student_publishable":False}),
            "review_status":"REVIEW_PENDING",
            "scope_classification":"SOURCE_CANDIDATE_MATH_EDITORIAL_ONLY",
            "pairwise_semantic_adjudication":"NOT_PERFORMED",
            "official_atom_id":None,
            "general_theorem_certified":False,
            "teacher_approved":False,
            "student_publishable":False,
        })
    require(len(touched)==24 and set(finite)<touched,
            "finite oracles must map to fully authored candidate notes")
    for r in previous["relation_reviews"]:
        require(r["review_status"]=="REVIEW_PENDING" and
                r["teacher_approved"] is False and
                r["math_equivalence_certified"] is False and
                r["student_publishable"] is False and
                r["final_atom_id"] is None, "upstream fabricated review")
        require(r["left_candidate_id"] in paired and r["right_candidate_id"] in paired,
                "pair relation source missing")
        for side in ("left","right"):
            s=r[side+"_source"]
            require(byid[s["candidate_id"]]["source_line_sha256"]==s["source_line_sha256"],
                    "stale source lineage")
    ledger=[]
    counter=Counter()
    for ident,src in sorted(byid.items()):
        if ident in paired:status="PAIR_RELATION_EDITORIAL_PENDING"
        elif ident in touched:status="SINGLE_CANDIDATE_EDITORIAL_PENDING"
        else:status="NOT_YET_INDIVIDUALLY_AUDITED"
        counter[status]+=1
        ledger.append({
            "candidate_id":ident, "track":src["track"],
            "provisional_topic":src["provisional_topic"],
            "source_review_id":src["source_review_id"],
            "source_page":src["source_page"],
            "source_line_sha256":src["source_line_sha256"],
            "scope_audit_state":status,
            "pairwise_semantic_resolution":"UNRESOLVED",
            "official_atom_id":None,"official_atom_count_contribution":None,
            "teacher_approved":False, "student_authoritative_index_eligible":False,
            "source_line_not_official_atom":True,
        })
    require(counter=={"PAIR_RELATION_EDITORIAL_PENDING":166,
                      "SINGLE_CANDIDATE_EDITORIAL_PENDING":24,
                      "NOT_YET_INDIVIDUALLY_AUDITED":110},
            "candidate triage ledger did not cover all 300 labels exactly once")
    per_track={}
    for track in TRACKS:
        subset=[r for r in ledger if r["track"]==track]
        per_track[track]={
            "provisional_labels":len(subset),
            "relation_compared_pending":sum(r["scope_audit_state"]=="PAIR_RELATION_EDITORIAL_PENDING" for r in subset),
            "individual_math_scope_pending":sum(r["scope_audit_state"]=="SINGLE_CANDIDATE_EDITORIAL_PENDING" for r in subset),
            "not_yet_individually_audited":sum(r["scope_audit_state"]=="NOT_YET_INDIVIDUALLY_AUDITED" for r in subset),
            "official_atom_denominator":None,
            "teacher_approved":0,
        }
    require(sum(v["provisional_labels"] for v in per_track.values())==300,
            "seven-track coverage mismatch")
    return {
        "schema_version":"kb93-mathematical-candidate-triage-v1",
        "standard_version":"普通高中数学课程标准（2017年版2020年修订）",
        "source_sha256":sha256(SOURCES.read_bytes()).hexdigest(),
        "prior_relation_sha256":sha256(PREVIOUS.read_bytes()).hexdigest(),
        "author_sha256":sha256(AUTHOR.read_bytes()).hexdigest(),
        "source_anchor_editorials":428,
        "provisional_labels":300,
        "relation_compared_draft_labels":166,
        "new_individual_math_scope_reviews":24,
        "still_without_any_individual_review":110,
        "remaining_without_pairwise_comparison":134,
        "fully_teacher_atomized_pages":0,
        "official_atom_denominator":None,
        "official_atom_denominators_by_track":{t:None for t in TRACKS},
        "teacher_approved":0,
        "student_authoritative_release":0,
        "teacher_equivalence_adjudications":0,
        "historical_uncertified_proof_steps":538,
        "unresolved_math_conflicts":10,
        "finite_math_checks":14,
        "finite_checks_are_general_certificates":False,
        "review_status":"REVIEW_PENDING",
        "per_track":per_track,
        "individual_math_review_notes":audits,
        "provisional_candidate_ledger":ledger,
    }

def render(data):
    lines=["# Batch93｜全300项候选溯源与24项数学范围独立审查",
        "",
        "注意：300是内部临时主题标签，428是来源行锚点，均非官方课标原子分母。七轨官方分母未知。",
        "所有单元仍为REVIEW_PENDING；0/61教师逐页原子化；0教师批准；0学生权威发布。",
        "",
        "|课程轨道|临时标签|仅关系编辑审查|本批独立数学审查|尚未个别审查|官方分母|",
        "|---|---:|---:|---:|---:|---|"]
    for track,v in data["per_track"].items():
        lines.append(f'|{track}|{v["provisional_labels"]}|{v["relation_compared_pending"]}|{v["individual_math_scope_pending"]}|{v["not_yet_individually_audited"]}|UNKNOWN|')
    lines+=["","本批24项记录不做等价裁决、不强制互配；原来剩余134项无成对审查的数量不变。",
            "14项有限数值/符号见证独立于编辑文案，只验证指定样例及错误条件，不能认证一般定理。",
            ""]
    for r in data["individual_math_review_notes"]:
        lines += [f'## {r["review_id"]}｜{r["provisional_topic"]}（{r["track"]}）',
                  f'源：{r["source_review_id"]} / 第{r["source_page"]}页 / SHA256 {r["source_line_sha256"]}',
                  "数学范围："+r["editorial_math_scope"],
                  "使用前提："+r["necessary_conditions"],
                  "原创算例："+r["controlled_worked_witness"],
                  "反例边界："+r["counterexample_or_invalid_boundary"],
                  "验证："+r["finite_evidence"].get("scope","EDITORIAL_NO_ORACLE"),""]
    lines+=["## 未结清的发布门槛",
            "134临时标签仍未开展成对比较；其中本批24项仅得到独立数学范围草案。",
            "尚无课标官方逐轨知识原子分母；选修E暂无项目候选不等于课程不存在。",
            "538条历史证明尚未通用认证、10组冲突未裁决。教师最终审校前不可发布权威教学证据。",""]
    return "\n".join(lines)

def run(check=False):
    data=build()
    files={OUTPUT:stable(data),MARKDOWN:render(data)}
    for p,content in files.items():
        if check:
            require(p.is_file() and p.read_text(encoding="utf-8")==content,
                    f"stale generated artifact: {p}")
        else:p.write_text(content,encoding="utf-8")
    return data

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    d=run(args.check)
    print("Batch93",len(d["provisional_candidate_ledger"]),"provisional,",
          d["new_individual_math_scope_reviews"],"individual editorial,",
          d["still_without_any_individual_review"],"unevaluated; oracles",d["finite_math_checks"])
