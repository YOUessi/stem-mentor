#!/usr/bin/env python3
"""Batch125 K00/K01/K07: no false official census from heading-only source cues.

Re-audit every historical editorial proposal against the *kind* of its hashed
curriculum anchor. A heading hash is provenance, but NOT evidence of a whole
mathematical requirement. Never convert this audit into teacher approval.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch124_scope as old
OUT=ROOT/"docs/evaluation/KB_BATCH125_PROVENANCE_GRADES.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH125_PROVENANCE_AND_SCOPE.md"
QUE=ROOT/"docs/evaluation/KB_BATCH125_RESIDUAL_CUE_REVIEW.json"
GRADES={
 "NUMBERED_ANCHOR_PRESENT_NOT_CERTIFIED",
 "HEADING_OR_SUBTOPIC_ONLY_REQUIRES_CLAUSE",
 "OPTIONAL_EXAMPLE_NOT_REQUIRED_ATOM",
 "NO_LAYOUT_MARKER_ALTERNATE_EVIDENCE_REVIEW"}
def need(ok,msg):
    if not ok: raise ValueError(msg)
def serial(x): return json.dumps(x,indent=2,ensure_ascii=False,sort_keys=True,allow_nan=False)+"\n"
def hash_file(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def originals():
    data=old.prior()+old.build()["candidates"]
    q=old.triage(old.build())
    base=old.previous.base_scope.base()
    return data,q,base
def audit():
    candidates,queue,base=originals()
    need(len(candidates)==239 and len(queue)==405,"baseline changed; re-review instead of silently drifting")
    marker={m["editorial_marker_id"]:m for m in base["markers"]}
    need(len(marker)==405 and len({r["id"] for r in candidates})==239,"duplicate source / candidate")
    page={r["printed_page"]:r for r in base["pages"]}
    result=[]
    for r in candidates:
        src=r["source"];mid=src["matching_layout_cues"]
        need(src["original_pdf_sha256"]==old.previous.base_scope.evidence.PDF_SHA,
            "wrong licensed curriculum edition")
        need(src["frozen_page_sha256"]==page[src["printed_page"]]["source_page_sha256"],
            "untrusted page source digest")
        need(r["review_status"]=="REVIEW_PENDING" and r["student_authoritative"] is False
             and r["official_atom_id"] is None and r["official_atom_certified"] is False
             and r["teacher_evidence"] is None and r["proof_verification"]=="UNVERIFIED",
             "unauthorized promotion")
        need(len(set(mid))==len(mid) and all(m in marker for m in mid),"unknown marker ID")
        matches=[marker[x] for x in mid]
        need(all(m["printed_page"]==src["printed_page"] and m["track_hint"]==r["course_track"]
                 and src["start_line"]<=m["source_line"]<=src["end_line"] for m in matches),
             "misbound source marker/page/track")
        kinds=sorted({m["cue_kind"] for m in matches})
        if "NUMBERED_REQUIREMENT_CUE" in kinds:
            grade="NUMBERED_ANCHOR_PRESENT_NOT_CERTIFIED"
        elif "OPEN_ELECTIVE_EXAMPLE_CUE" in kinds:
            grade="OPTIONAL_EXAMPLE_NOT_REQUIRED_ATOM"
        elif kinds:
            grade="HEADING_OR_SUBTOPIC_ONLY_REQUIRES_CLAUSE"
        else: grade="NO_LAYOUT_MARKER_ALTERNATE_EVIDENCE_REVIEW"
        result.append({"candidate_id":r["id"],"course_track":r["course_track"],
                       "printed_page":src["printed_page"],"span_sha256":src["source_span_sha256"],
                       "marker_ids":list(mid),"marker_kinds":kinds,"evidence_grade":grade,
                       "needs_human_semantic_check":True,"official_atom_id":None,
                       "teacher_approved":False,"student_authoritative":False})
    residual=[]
    for q in queue:
        if q["linked_candidate_ids"]:continue
        kind=q["cue_kind"]
        need(kind in {"TOPIC_CUE","SUBTOPIC_CUE","NUMBERED_REQUIREMENT_CUE"},
             "unknown residual marker class")
        action={"TOPIC_CUE":"HEADING_ONLY_REVIEW_CHILD_REQUIREMENTS",
                "SUBTOPIC_CUE":"SUBTOPIC_LABEL_REVIEW_NEIGHBORING_REQUIREMENTS",
                "NUMBERED_REQUIREMENT_CUE":"NUMBERED_CLAUSE_REVIEW_CONTEXT_AND_ATOMS"}[kind]
        residual.append({"cue_id":q["cue_id"],"cue_kind":kind,"course_track":q["course_track"],
             "printed_page":q["printed_page"],"source_line":q["source_line"],
             "source_line_sha256":q["source_line_sha256"],"review_action":action,
             "previous_nonatom_proposal_pending":
                q["status"]=="NON_ATOM_ACTIVITY_EDITORIAL_PROPOSAL_PENDING_REVIEW",
             "is_official_atom":None,"teacher_review":"REVIEW_PENDING"})
    grades=collections.Counter(r["evidence_grade"] for r in result)
    pending=collections.Counter(r["cue_kind"] for r in residual)
    pertrack={}
    for track in sorted(set(r["course_track"] for r in result)|set(r["course_track"] for r in residual)):
        rs=[r for r in result if r["course_track"]==track]
        gaps=[r for r in residual if r["course_track"]==track]
        pertrack[track]={"editorial_proposals":len(rs),
            "with_numbered_anchor":sum(r["evidence_grade"]=="NUMBERED_ANCHOR_PRESENT_NOT_CERTIFIED" for r in rs),
            "without_numbered_anchor":sum(r["evidence_grade"]!="NUMBERED_ANCHOR_PRESENT_NOT_CERTIFIED" for r in rs),
            "residual_headings":sum(r["cue_kind"]=="TOPIC_CUE" for r in gaps),
            "residual_subtopics":sum(r["cue_kind"]=="SUBTOPIC_CUE" for r in gaps),
            "residual_numbered_requirements":sum(r["cue_kind"]=="NUMBERED_REQUIREMENT_CUE" for r in gaps),
            "official_atom_denominator":None,"teacher_approved":0}
    summary={"batch":125,"provenance_only_not_math_certification":True,
      "curriculum_pdf_sha256":old.previous.base_scope.evidence.PDF_SHA,
      "candidates":len(result),"layout_cues":405,
      "linked_cues":405-len(residual),"unlinked_cues":len(residual),
      "residual_cue_kinds":dict(sorted(pending.items())),
      "candidate_evidence_grades":dict(sorted(grades.items())),
      "prior_nonatom_proposals_unadjudicated":sum(r["previous_nonatom_proposal_pending"] for r in residual),
      "official_atom_denominator":None,"official_census_complete":False,
      "teacher_approved":0,"student_authoritative":0,
      "per_track":pertrack,
      "source_artifact_sha256":{"editorial_124":hash_file(old.OUT),
         "layout_124":hash_file(old.QUEUE),
         "coverage_124":hash_file(old.COVER)},
      "records":result}
    validate(summary,residual)
    return summary,residual
def validate(summary,residual):
    need(summary["candidates"]==239 and len(summary["records"])==239
         and summary["layout_cues"]==405 and len(residual)==135
         and summary["linked_cues"]==270 and summary["unlinked_cues"]==135,
         "baseline counts wrong")
    need(set(summary["candidate_evidence_grades"])<=GRADES
         and sum(summary["candidate_evidence_grades"].values())==239
         and sum(summary["residual_cue_kinds"].values())==135,
         "grade count drift")
    need(summary["official_atom_denominator"] is None
         and summary["official_census_complete"] is False
         and summary["teacher_approved"]==summary["student_authoritative"]==0,
         "official census / review approval fabricated")
    need(len({x["candidate_id"] for x in summary["records"]})==239
         and len({x["cue_id"] for x in residual})==135,"duplicated IDs")
    need(all(x["evidence_grade"] in GRADES and x["official_atom_id"] is None
            and x["teacher_approved"] is False and x["student_authoritative"] is False
            and x["needs_human_semantic_check"] is True for x in summary["records"]),
         "provenance promoted without review")
    need(all(x["is_official_atom"] is None and x["teacher_review"]=="REVIEW_PENDING"
             for x in residual),"unreviewed heading promoted or excluded")
    need(sum(sum(v[k] for k in ("editorial_proposals",)) for v in summary["per_track"].values())==239,
         "per-track denominator drift")
    # Verify that the published ledger is identical to the underlying frozen source
    # identity and cue classification; never trust client-provided grade or page.
    sources, original_queue, original_base = originals()
    byid={r["id"]:r for r in sources}
    bycue={r["cue_id"]:r for r in original_queue if not r["linked_candidate_ids"]}
    origmarkers={m["editorial_marker_id"]:m for m in original_base["markers"]}
    for item in summary["records"]:
        source=byid[item["candidate_id"]]
        src=source["source"]
        kinds=sorted({origmarkers[k]["cue_kind"] for k in src["matching_layout_cues"]})
        expected_grade=("NUMBERED_ANCHOR_PRESENT_NOT_CERTIFIED" if "NUMBERED_REQUIREMENT_CUE" in kinds
          else "OPTIONAL_EXAMPLE_NOT_REQUIRED_ATOM" if "OPEN_ELECTIVE_EXAMPLE_CUE" in kinds
          else "HEADING_OR_SUBTOPIC_ONLY_REQUIRES_CLAUSE" if kinds
          else "NO_LAYOUT_MARKER_ALTERNATE_EVIDENCE_REVIEW")
        need(item["course_track"]==source["course_track"] and
             item["printed_page"]==src["printed_page"] and
             item["span_sha256"]==src["source_span_sha256"] and
             item["marker_ids"]==src["matching_layout_cues"] and
             item["marker_kinds"]==kinds and item["evidence_grade"]==expected_grade,
             "source lineage or evidence grade was forged")
    action_by_kind={"TOPIC_CUE":"HEADING_ONLY_REVIEW_CHILD_REQUIREMENTS",
      "SUBTOPIC_CUE":"SUBTOPIC_LABEL_REVIEW_NEIGHBORING_REQUIREMENTS",
      "NUMBERED_REQUIREMENT_CUE":"NUMBERED_CLAUSE_REVIEW_CONTEXT_AND_ATOMS"}
    for item in residual:
        q=bycue[item["cue_id"]]
        need(item["cue_kind"]==q["cue_kind"] and
          item["course_track"]==q["course_track"] and
          item["printed_page"]==q["printed_page"] and
          item["source_line"]==q["source_line"] and
          item["source_line_sha256"]==q["source_line_sha256"] and
          item["review_action"]==action_by_kind[q["cue_kind"]] and
          item["previous_nonatom_proposal_pending"]==
            (q["status"]=="NON_ATOM_ACTIVITY_EDITORIAL_PROPOSAL_PENDING_REVIEW"),
          "remaining cue identity or triage was forged")
    need(summary["source_artifact_sha256"]=={
       "editorial_124":hash_file(old.OUT),"layout_124":hash_file(old.QUEUE),
       "coverage_124":hash_file(old.COVER)}, "historical audit source was changed")
    return True
def render(s,r):
    counts=s["candidate_evidence_grades"];c=s["residual_cue_kinds"]
    txt=["# Batch125｜课标来源证据强度与剩余版面线索审计","",
      "此报告由 GitHub 中既有的 405 条带哈希来源线索及 239 个工程候审目标重新计算；没有复制官方课标原文。",
      "**来源锚点不是完整知识原子**：仅标题/小节行的 SHA-256 不证明候选数学陈述获得课标正文支持。",
      "含编号要求的锚点也仅说明找到该要求，不说明已完成跨页语义拆分、教师批准或形式证明。","",
      f"候审目标：{s['candidates']}；带编号要求锚点：{counts.get('NUMBERED_ANCHOR_PRESENT_NOT_CERTIFIED',0)}；",
      f"仅标题/小节锚点：{counts.get('HEADING_OR_SUBTOPIC_ONLY_REQUIRES_CLAUSE',0)}；",
      f"可选实例锚点：{counts.get('OPTIONAL_EXAMPLE_NOT_REQUIRED_ATOM',0)}；",
      f"无布局锚点、需另查图示/段落：{counts.get('NO_LAYOUT_MARKER_ALTERNATE_EVIDENCE_REVIEW',0)}。","",
      f"仍未关联的135个线索：大标题 {c.get('TOPIC_CUE',0)}；小节标题 {c.get('SUBTOPIC_CUE',0)}；",
      f"带编号要求 {c.get('NUMBERED_REQUIREMENT_CUE',0)}（其中历史待审非原子提议 {s['prior_nonatom_proposals_unadjudicated']}）。",
      "**不能把135个未关联标题/要求等同135个遗漏的数学原子**，也不能把其余270条已关联线索等同完成。","",
      "|轨道|候审目标|含编号锚点|非编号或空锚点|剩余大标题|剩余小节标题|剩余编号条款|正式分母|",
      "|---|---:|---:|---:|---:|---:|---:|---|"]
    for k,v in s["per_track"].items():
        txt.append(f"|{k}|{v['editorial_proposals']}|{v['with_numbered_anchor']}|{v['without_numbered_anchor']}|{v['residual_headings']}|{v['residual_subtopics']}|{v['residual_numbered_requirements']}|UNKNOWN|")
    txt+=["","## 下一步需要人工/教师裁决的关键类","",
      "1. 对仅有章节/小节标题支持的候选，追加有实际要求内容的跨行来源证据，并按概念/定理/方法拆分；不得凭标题直接批准。",
      "2. 对10个无布局线索的候选，检查是否依赖官方图示、跨行未标记要求或先前项目自编扩展，保留许可和标注。",
      "3. 对6条仍未关联的编号要求逐一检查完整上下文；3条非原子活动提议仍待教师确认，不能提前排除。",
      "4. 真正的全量原子分母必须在逐条语义裁决、跨页去重、选修范围确认后冻结；这里的所有分母仍为UNKNOWN。","",
      "## 拒绝发布","",
      "所有记录仍为 REVIEW_PENDING / 不可学生权威引用；本审计不是数学验证，也没有正式教师签字。",""]
    return "\n".join(txt)
def main():
    p=argparse.ArgumentParser();m=p.add_mutually_exclusive_group(required=True)
    m.add_argument("--write",action="store_true");m.add_argument("--check",action="store_true")
    a=p.parse_args();summary,residual=audit()
    for file,body in [(OUT,serial(summary)),(QUE,serial(residual)),(REPORT,render(summary,residual))]:
        if a.write:file.write_text(body,encoding="utf-8")
        else:need(file.exists() and file.read_text(encoding="utf-8")==body,
                  "derived provenance audit has changed: "+str(file))
    print("Batch125 evidence audit:",summary["candidates"],"proposals;",
          summary["candidate_evidence_grades"],"residual",summary["residual_cue_kinds"])
if __name__=="__main__":main()
