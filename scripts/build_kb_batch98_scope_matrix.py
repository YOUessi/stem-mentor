#!/usr/bin/env python3
"""K00/K01 auditable 24-source editorial+lesson delta over 300 provisional labels.
Do not report project candidate labels as official curriculum atoms.
"""
from __future__ import annotations
import argparse,json,sys
from collections import Counter
from hashlib import sha256
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch93_candidate_triage as B93
import build_kb_batch97_candidate_matrix as B97M
import build_kb_batch98_depth as B98
from kb_batch98_scope_authoring import SCOPES

OUTPUT=ROOT/"docs/evaluation/KB_BATCH98_300_PROVISIONAL_STATUS.json"
MARKDOWN=ROOT/"docs/evaluation/KB_BATCH98_300_PROVISIONAL_STATUS.md"
OUTSCOPES=ROOT/"docs/evaluation/KB_BATCH98_12_SCOPE_INTERPRETATIONS.json"
FROZEN_SOURCE_SHA256=B93.FROZEN_BATCH89_CANDIDATES_SHA256
TRACKS=B93.TRACKS

def require(condition,reason):
    if not condition:raise ValueError(reason)
def stable(o):return json.dumps(o,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+"\n"

def build(scopes=None,deep_report=None,old=None):
    old=B97M.build() if old is None else old
    deep_report=B98.build()[1] if deep_report is None else deep_report
    scopes=SCOPES if scopes is None else scopes
    src=B93.read(B93.SOURCES)["provisional_candidate_backlog"]
    require(type(src) is list and len(src)==300 and
        B93.candidate_snapshot_sha256(src)==FROZEN_SOURCE_SHA256,
        "frozen source snapshot SHA mismatch")
    original={x["candidate_id"]:x for x in src}
    require(type(scopes) is list and len(scopes)==12,"12 distinct editorial scope interpretations required")
    require(old["provisional_source_labels"]==300 and
        old["editorial_stages"]=={
            "PAIR_COMPARISON_NOT_ATOMIZED":166,
            "INDIVIDUAL_SCOPE_NOT_ATOMIZED":24,
            "NO_INDIVIDUAL_EDITORIAL":56,
            "FULL_DEEP_DRAFT_PENDING_TEACHER":54} and
        old["official_atom_denominator"] is None and old["teacher_approved"]==0,
        "prior candidate-stage ledger drift")
    deep={x["source_candidate_id"]:x for x in deep_report["canonical_lesson_source_links"]}
    require(len(deep)==12 and deep_report["new_individual_full_deep_drafts"]==12 and
        deep_report["cumulative_new_deep_drafts_since_batch94"]==66 and
        deep_report["still_without_any_individual_review"]==44 and
        deep_report["official_atom_denominator"] is None and
        deep_report["teacher_approved"]==deep_report["student_authoritative_release"]==0,
        "deep draft review/publish guard drift")
    required={"anchor","scope","assumptions","positive","nonexample","relation"}
    editorial={}
    for r in scopes:
        require(type(r) is dict and set(r)==required,"editorial schema rejected")
        aid=r["anchor"]
        require(type(aid) is str and aid in original and aid not in editorial and aid not in deep,
                "scope source duplicate or unknown")
        require(all(type(r[k]) is str and len(r[k])>=25 for k in required-{"anchor"}),
                "scope missing precise condition, comparison or nonexample")
        source=original[aid]
        require(source["review_status"]=="REVIEW_PENDING" and
                source["teacher_approval"] is None and
                source["official_math_atom_id"] is None and
                source["student_authoritative_index_eligible"] is False,
                "source was falsely reviewed or approved")
        prev=next((x for x in old["candidates"] if x["candidate_id"]==aid),None)
        require(prev and prev["editorial_stage"]=="NO_INDIVIDUAL_EDITORIAL" and
            prev["source_line_sha256"]==source["source_line_sha256"],
            "not a previously unreviewed source / altered SHA")
        editorial[aid]={**r,"source_track":source["track"],
           "source_review_id":source["source_review_id"],
           "source_page":source["source_page"],
           "source_line_sha256":source["source_line_sha256"],
           "status":"INDIVIDUAL_SCOPE_EDITORIAL_PENDING",
           "teacher_review_status":"REVIEW_PENDING",
           "automatic_general_theorem_proof":False,
           "teacher_approval":None,"official_atom_id":None,
           "student_publishable":False}
    old_ids={x["candidate_id"] for x in old["candidates"]}
    require(old_ids==set(original) and len(old_ids)==300,"source candidates changed")
    result=[]
    for r in old["candidates"]:
        aid=r["candidate_id"]
        v=dict(r)
        if aid in deep:
            require(v["editorial_stage"]=="NO_INDIVIDUAL_EDITORIAL",
                "deep draft cannot overwrite review state")
            v.update(editorial_stage="FULL_DEEP_DRAFT_PENDING_TEACHER",
                     deep_lesson_id=deep[aid]["lesson_id"],deep_draft_batch=98)
        elif aid in editorial:
            require(v["editorial_stage"]=="NO_INDIVIDUAL_EDITORIAL",
                "scope review cannot overwrite prior editorial")
            v.update(editorial_stage="INDIVIDUAL_SCOPE_EDITORIAL_PENDING",
                     batch98_editorial_scope_id=aid)
        require(v["source_line_sha256"]==original[aid]["source_line_sha256"] and
                v["teacher_approval"] is None and v["official_atom_id"] is None and
                v["teacher_review_status"]=="REVIEW_PENDING" and
                v["student_authoritative_index_eligible"] is False,
                "source authority elevated or provenance altered")
        result.append(v)
    counts=Counter(v["editorial_stage"] for v in result)
    require(counts==Counter({
       "PAIR_COMPARISON_NOT_ATOMIZED":166,
       "INDIVIDUAL_SCOPE_NOT_ATOMIZED":24,
       "INDIVIDUAL_SCOPE_EDITORIAL_PENDING":12,
       "NO_INDIVIDUAL_EDITORIAL":32,
       "FULL_DEEP_DRAFT_PENDING_TEACHER":66
    }),"unexpected stage total")
    tracks={t:{"provisional_source_labels":sum(r["track"]==t for r in result),
       "official_atom_denominator":None,
       "teacher_approved":0,
       "stages":dict(sorted(Counter(r["editorial_stage"] for r in result if r["track"]==t).items()))}
       for t in TRACKS}
    require(sum(x["provisional_source_labels"] for x in tracks.values())==300,
        "seven-track conservation failed")
    report={
      "schema_version":"kb98-provisional-scope-gate-v1",
      "source_scope":"PROJECT_PROVISIONAL_LABELS_NOT_OFFICIAL_ATOMS",
      "curriculum_standard":"普通高中数学课程标准（2017年版2020年修订）",
      "source_snapshot_sha256":sha256(B93.SOURCES.read_bytes()).hexdigest(),
      "frozen_candidate_canonical_sha256":FROZEN_SOURCE_SHA256,
      "stage_counts":dict(sorted(counts.items())),
      "project_source_anchors":428,
      "provisional_source_labels":300,
      "deep_draft_coverage_of_provisional_labels":66,
      "new_full_depth_lessons":12,
      "new_individual_scope_interpretations":12,
      "remaining_individually_unaudited_labels":32,
      "remaining_without_pairwise_comparison":134,
      "official_atom_denominator":None,
      "official_atom_denominators_by_track":{t:None for t in TRACKS},
      "human_full_page_atomization":"0/61",
      "teacher_approved":0,
      "student_authoritative_releases":0,
      "historical_uncertified_proof_steps":538,
      "historical_P0_steps_without_direct_review":106,
      "unresolved_mathematical_conflicts":10,
      "track_matrix":tracks,
      "candidates":result}
    return report,list(editorial.values())

def markdown(report,scopes):
    s=["# Batch98｜300个临时主题独立来源与状态台账（非官方知识原子）","",
       "课标七轨正式数学原子分母均 UNKNOWN；教师逐页原子化0/61、批准0、正式学生发布0。","",
       "| 编辑阶段 | 临时标签数 |","|---|---:|"]
    s += [f"| {k} | {v} |" for k,v in report["stage_counts"].items()]
    s+=["","| 轨道 | 临时来源标签 | 官方原子分母 |","|---|---:|---|"]
    s += [f"| {k} | {v['provisional_source_labels']} | UNKNOWN |" for k,v in report["track_matrix"].items()]
    s+=["","## 新增12项独立数学范围解释（均未经过教师审核）",""]
    for v in scopes:
        s += ["### "+v["anchor"]+"｜"+v["source_track"],"",
             "来源页："+str(v["source_page"])+"；来源行SHA："+v["source_line_sha256"],"",
             "**内容边界：** "+v["scope"],"",
             "**前提：** "+v["assumptions"],"",
             "**合法例：** "+v["positive"],"",
             "**失效例：** "+v["nonexample"],"",
             "**相邻主题比较：** "+v["relation"],""]
    s+=["所有来源解释只构成编辑草案，不能当作课标正式原子审定、一般定理证明或学生可发布内容。",""]
    return "\n".join(s)

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    a=p.parse_args()
    report,scopes=build()
    files={OUTPUT:stable(report), OUTSCOPES:stable(scopes), MARKDOWN:markdown(report,scopes)}
    for path,data in files.items():
        if a.check:require(path.is_file() and path.read_text(encoding="utf-8")==data,
                          "matrix drift: "+str(path))
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(data,encoding="utf-8")
    print("BATCH98 source-scope",len(scopes),"new; still unaudited",
          report["remaining_individually_unaudited_labels"], "CHECK" if a.check else "WRITTEN")

if __name__=="__main__":main()
