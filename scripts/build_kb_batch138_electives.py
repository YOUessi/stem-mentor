#!/usr/bin/env python3
"""Eight original, source-line-locked B/C/D/E manuscripts; NOT official full-course atoms.

--check-offline only checks committed fingerprints/artifacts, not protected source PDF.
--check-mac ALSO rehashes original 2017/2020 PDFKit page lines on authorized Mac.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch132_electives as upstream
import build_kb_batch137_coverage as prior

INPUTS = (
 ROOT/"knowledge/editorial_review/kb_batch138_authoring_inputs.json",
 ROOT/"knowledge/editorial_review/kb_batch138_authoring_inputs2.json",
)
OUT = ROOT/"knowledge/editorial_review/kb_batch138_eight_elective_lessons.json"
SAFE = ROOT/"knowledge/editorial_review/kb_batch138_student_safe_index.json"
REPORT = ROOT/"docs/evaluation/KB_BATCH138_ELECTIVES.md"
AUDIT = ROOT/"docs/evaluation/KB_BATCH138_ELECTIVE_AUDIT.json"
LOCKS = [
 ROOT/"curriculum/highschool_math/k00_batch131_line_fingerprints.json",
 ROOT/"curriculum/highschool_math/k00_batch132_source_fingerprints.json",
 ROOT/"curriculum/highschool_math/k00_batch128_source_line_locks.json",
 ROOT/"curriculum/highschool_math/k00_batch129_source_line_locks.json",
]
IDS = (
 "hs-semantic-pilot-121-b205", "hs-semantic-pilot-121-b203",
 "hs-semantic-pilot-121-ec202", "hs-semantic-pilot-121-ec204",
 "hs-semantic-pilot-121-ed201", "hs-semantic-pilot-121-ed202",
 "hs-semantic-pilot-120-ee104", "hs-semantic-pilot-120-ee106",
)
TRACKS = tuple(upstream.TRACKS)
PREREQS = {
 IDS[0]: ["kb133-proposal-sc_space_basis"],
 IDS[1]: ["kb133-proposal-sc_extreme_point"],
 IDS[2]: ["kb133-proposal-c_exponential_exp", "kb133-proposal-c_logarithm_law"],
 IDS[3]: ["kb133-proposal-c_set_subset", "kb133-proposal-c_union_intersection"],
 IDS[4]: ["kb133-proposal-c_period", "kb133-proposal-c_radian"],
 IDS[5]: ["kb133-proposal-c_radian"],
 IDS[6]: [],
 IDS[7]: [],
}
GAPS = {IDS[6]: "整数整除和带余除法先修原子不在已闭环的41条项目候选内",
        IDS[7]: "三角形相似判定先修原子不在已闭环的41条项目候选内"}
EXPECTED_TRACKS = {
 "ELECTIVE_B": (IDS[0], IDS[1]), "ELECTIVE_C": (IDS[2], IDS[3]),
 "ELECTIVE_D": (IDS[4], IDS[5]), "ELECTIVE_E": (IDS[6], IDS[7]),
}
PDF = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"

def check(c, why):
    if not c: raise ValueError(why)

def encode(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False)+"\n"

@lru_cache(maxsize=1)
def contexts():
    candidates, reviewed = upstream.historical()
    check(len(candidates)==239 and len(reviewed)==200, "historical 239 context review drift")
    src = {k: v for f in LOCKS for k,v in json.loads(f.read_text(encoding="utf-8")).items()}
    check(set(IDS)<=set(src), "no line fingerprint for one of eight candidates")
    check(set(IDS)<=set(candidates), "missing syllabus editorial objective")
    return candidates,src

def authors():
    a = [r for p in INPUTS for r in json.loads(p.read_text(encoding="utf-8"))]
    check(tuple(r["id"] for r in a)==IDS, "order/duplicate/missing eight authored lesson candidates")
    return a

@lru_cache(maxsize=1)
def build():
    candidates, locks = contexts()
    base = prior.build()
    check(base["full_teacher_draft_manuscripts"]==41 and base["scope_proposals"]==41, "bounded prior state drift")
    old_ids={r["source_candidate_id"] for r in base["rows"] if r["has_complete_teacher_manuscript"]} if False else {r["candidate_id"] for r in base["rows"]}
    check(not(set(IDS)&old_ids), "duplicate source draft")
    out = []
    for author in authors():
        cid=author["id"]
        c=candidates[cid]; lock=locks[cid]
        tr=c["course_track"]; src=c["source"]
        check(tr in EXPECTED_TRACKS and cid in EXPECTED_TRACKS[tr], "candidate track forged")
        check(src["printed_page"]==lock["page"] and
              src["start_line"]==lock["start_line"] and src["end_line"]==lock["end_line"],
              "page/line drift")
        check(len(lock["line_sha256"])==lock["end_line"]-lock["start_line"]+1, "source span line count drift")
        check(all(re.fullmatch("[a-f0-9]{64}", q) for q in lock["line_sha256"]+[lock["span_sha256"]]),
              "invalid source sha")
        check(author["type"] in ("Theorem","Concept","Method"),"invalid teaching type")
        record={
          "id": "kb138-deep-"+cid.removeprefix("hs-semantic-pilot-"),
          "source_candidate_id":cid, "course_track":tr,
          "source_pdf_sha256":PDF,"source_printed_page":lock["page"],
          "source_start_line":lock["start_line"],"source_end_line":lock["end_line"],
          "source_span_sha256":lock["span_sha256"],
          "source_evidence_status":"HISTORICAL_PDFKIT_LINE_HASHED_EDITORIAL_INTERPRETATION",
          "standard_version":"2017-edition-2020-revision-editorial-elective",
          "knowledge_type":author["type"],"title":author["topic"],
          "formal_definition_or_theorem":author["formal"],
          "notation_and_domain":author["domain"],
          "applicability_and_hypotheses":author["assumptions"],
          "reasoned_steps":[{"step":i+1,"justification":v} for i,v in enumerate(author["steps"])],
          "why_method_is_legal":author["legal"],"nonexample_or_failure":author["failure"],
          "typical_wrong_solution":author["wrong"],"why_wrong_and_repair":author["repair"],
          "teacher_examples":[{"question":e["q"],"answer":e["a"],"reasoned_solution":e["sol"]}
                              for e in author["examples"]],
          "student_hint_ladder":author["hints"],"near_transfer":author["near"],
          "far_transfer":author["far"],"prerequisite_proposals":PREREQS[cid],
          "missing_prerequisite_gap":GAPS.get(cid),
          "prerequisite_math_review":"REVIEW_PENDING",
          "teacher_review_status":"REVIEW_PENDING","teacher_review_evidence":None,
          "teacher_solution_visibility":"TEACHER_ONLY",
          "formal_proof_certified":False,"free_student_step_verified":False,
          "student_authoritative":False,"official_atom_id":None,
        }
        out.append(record)
    validate_rows_structure(out)
    return out

def validate_rows_structure(rows):
    check(len(rows)==8 and len({r["id"] for r in rows})==8,"eight complete distinct lessons required")
    base=prior.build()
    valid_prior={r["candidate_id"] for r in base["rows"]}
    for r in rows:
        check(r["teacher_review_status"]=="REVIEW_PENDING" and
              r["teacher_review_evidence"] is None and not r["student_authoritative"] and
              r["official_atom_id"] is None and r["teacher_solution_visibility"]=="TEACHER_ONLY" and
              r["formal_proof_certified"] is False and r["free_student_step_verified"] is False,
              "unauthorized knowledge promotion")
        check(len(r["reasoned_steps"])==4 and len(r["teacher_examples"])==2
              and len(r["student_hint_ladder"])==3
              and all(len(e["reasoned_solution"])>=3 for e in r["teacher_examples"]),
              "incomplete proof / examples / hint ladder")
        check(all(len(r[f])>=26 for f in (
              "formal_definition_or_theorem","notation_and_domain",
              "applicability_and_hypotheses","why_method_is_legal","nonexample_or_failure",
              "typical_wrong_solution","why_wrong_and_repair","near_transfer","far_transfer")),
              "shallow teaching content")
        check(len({p for p in r["prerequisite_proposals"]})==
              len(r["prerequisite_proposals"]) and
              set(r["prerequisite_proposals"])<=valid_prior,"unknown or duplicate prerequisite")
        check(re.fullmatch("[0-9a-f]{64}",r["source_span_sha256"]) is not None,
              "bad source evidence")
    return True

def rehash_mac(rows):
    # This loads protected PDFKit page records on the Mac only; not on GitHub CI.
    pages = upstream.prior.previous.prev.prior.prior.previous.source_pages()
    candidates,_ = contexts()
    for r in rows:
        source=candidates[r["source_candidate_id"]]["source"]
        actual=upstream.fingerprint(pages,source)
        check(actual["span_sha256"]==r["source_span_sha256"] and
              actual["page"]==r["source_printed_page"] and
              actual["start_line"]==r["source_start_line"] and
              actual["end_line"]==r["source_end_line"],"original PDFKit source line mismatch")
    return True

def audit(rows):
    prev=prior.build()
    count=Counter(r["course_track"] for r in rows)
    return {
      "schema":"kb138-elective-quality-pilot/1",
      "scope":"8_BOUNDED_ELECTIVE_B_C_D_E_SOURCE_CONTEXTS_NOT_OFFICIAL_CENSUS",
      "prior_review_manuscripts":prev["full_teacher_draft_manuscripts"],
      "new_review_manuscripts":8,"aggregate_review_manuscripts":49,
      "new_teacher_worked_examples":16,"new_student_safe_hint_stages":24,
      "new_near_transfer":8,"new_far_transfer":8,
      "by_track_new_manuscripts":{t:count.get(t,0) for t in TRACKS},
      "official_atom_denominators":{t:None for t in TRACKS},
      "official_course_coverage_rate":None,
      "known_provenance_status":"PDFKIT_FINGERPRINT_FROM_HISTORICAL_LOCAL_SOURCE_AUDIT",
      "teacher_approved":0,"student_authoritative_releases":0,
      "general_proofs_formally_certified":0,"student_free_text_steps_verified":0,
      "human_source_semantics_verified":False,
      "missing_prerequisite_review_count":sum(bool(r["missing_prerequisite_gap"]) for r in rows),
      "records":[{
        "manuscript_id":r["id"],"candidate_id":r["source_candidate_id"],
        "track":r["course_track"],"page":r["source_printed_page"],
        "source_span_sha256":r["source_span_sha256"],
        "teacher_review":"REVIEW_PENDING","student_authoritative":False,
        "prerequisites":r["prerequisite_proposals"],
        "missing_prerequisite_gap":r["missing_prerequisite_gap"]
      } for r in rows],
    }

def safe():
    return {"status":"NO_APPROVED_EVIDENCE","items":[],"teacher_solution_exposed":False,
            "source":"BATCH138_TEACHER_ONLY_EDITORIAL_DRAFTS","official_denominator":None}

def render(rows,obj):
    lines=[
       "# Batch138｜选修 B/C/D/E 原创深度候审讲义及原文证据门禁","",
       "**8份项目原创候审稿：B/C/D/E各2份；绝非官方全国课程知识总数或课程覆盖率。**",
       "历史239条编辑候选的PDFKit行哈希不等于这些解释已获正式教师确认。",
       "本轮来源原文只在授权Mac重哈希；不能将原文复制到仓库。所有正式七轨原子分母UNKNOWN。",
       "全部稿件 REVIEW_PENDING / TEACHER_ONLY；教师批准0；形式认证一般定理0；学生权威发布0。",""]
    for r in rows:
        lines += [
           "## "+r["title"]+" · "+r["course_track"],"",
           "- 来源候选："+r["source_candidate_id"]+"；纸质页码："+str(r["source_printed_page"])+
              "；行："+str(r["source_start_line"])+"—"+str(r["source_end_line"])+"；指纹："+r["source_span_sha256"],
           "- 分类："+r["knowledge_type"]+"；审核：REVIEW_PENDING，未形式证明、不得学生权威发布。",
           "### 形式陈述",r["formal_definition_or_theorem"],"### 记号和论域",r["notation_and_domain"],
           "### 必要前提",r["applicability_and_hypotheses"],"### 分步论证"
        ]
        lines += [str(i["step"])+". "+i["justification"] for i in r["reasoned_steps"]]
        lines += ["### 合法性与边界",r["why_method_is_legal"],r["nonexample_or_failure"],
                  "### 典型错法与修正",r["typical_wrong_solution"],r["why_wrong_and_repair"],
                  "### 教师例题（仅候审稿 / 学生检索不公开）"]
        for j,e in enumerate(r["teacher_examples"],1):
            lines += ["#### 例题"+str(j),e["question"],"教师答案："+e["answer"]]
            lines += [str(i)+". "+t for i,t in enumerate(e["reasoned_solution"],1)]
        lines += ["### 学生提示层级（学生查询仍默认拒答）"]
        lines += [str(i)+". "+t for i,t in enumerate(r["student_hint_ladder"],1)]
        lines += ["### 近迁移",r["near_transfer"],"### 远迁移",r["far_transfer"],
                  "先修建议："+(",".join(r["prerequisite_proposals"]) or "暂未锁定")+
                     "；待补先修："+(r["missing_prerequisite_gap"] or "无显式记录"),
                  ""]
    lines += ["## 精确验收边界","16道原创教师例题、24级提示、8组失效反例；独立数学Oracle仅支持已列出的有限数学见证，不认证整篇证明。",
              "正式课程原子分母依然未知；来源选修E含示例及校本拓展，不作为全国必学内容发布。"]
    return "\n".join(lines)+"\n"

def main():
    a=argparse.ArgumentParser()
    g=a.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check-offline",action="store_true")
    g.add_argument("--check-mac",action="store_true")
    args=a.parse_args()
    rows=build()
    matrix=audit(rows)
    if args.check_mac:rehash_mac(rows)
    if args.write:
        # Write only after Mac source attestation succeeds.
        rehash_mac(rows)
        OUT.write_text(encode(rows),encoding="utf-8")
        AUDIT.write_text(encode(matrix),encoding="utf-8")
        SAFE.write_text(encode(safe()),encoding="utf-8")
        REPORT.write_text(render(rows,matrix),encoding="utf-8")
    else:
        check(json.loads(OUT.read_text(encoding="utf-8"))==rows,"manuscript text/source/status drift")
        check(json.loads(AUDIT.read_text(encoding="utf-8"))==matrix,"coverage/approval drift")
        check(json.loads(SAFE.read_text(encoding="utf-8"))==safe(),"student safe index drift")
        check(REPORT.read_text(encoding="utf-8")==render(rows,matrix),"Markdown manuscript drift")
    print("PASS Batch138 8 source-line-locked B/C/D/E drafts; 49 cumulative bounded drafts; official total UNKNOWN", "MAC" if args.check_mac or args.write else "OFFLINE")
if __name__=="__main__":main()
