#!/usr/bin/env python3
"""KB159: coherent compulsory function module; source-locked review drafts only.

This is a 10-candidate AUTHORING pilot, not a nationally frozen syllabus atom
denominator. The PDF is never committed and its text is never serialized.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch158_lessons as previous
TRACKS=previous.TRACKS
PDF=previous.PDF
IDS=tuple(f"hs-semantic-pilot-124-c{i}" for i in range(501,511))
AUTHOR=ROOT/"knowledge/editorial_review/kb_batch159_ten_authoring.jsonl"
LOCKS=ROOT/"knowledge/editorial_review/kb_batch159_source_line_sha256.json"
OUT=ROOT/"knowledge/editorial_review/kb_batch159_ten_teacher_lessons.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH159_DEPTH_AUDIT.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH159_FUNCTIONS_CHAPTER.md"
SAFE=ROOT/"knowledge/editorial_review/kb_batch159_student_safe_index.json"
ATOMS=ROOT/"docs/evaluation/KB_BATCH159_PROVISIONAL_ATOM_DOSSIERS.json"
REV=ROOT/"docs/evaluation/KB_BATCH159_PROVISIONAL_ATOM_DOSSIERS.md"
EVIDENCE="PDFKIT_HASHED_NOT_HUMAN_SEMANTICALLY_APPROVED"
DUPLICATES={
"hs-semantic-pilot-124-c503":["hs-semantic-pilot-124-c504"],
"hs-semantic-pilot-124-c504":["hs-semantic-pilot-124-c503"],
"hs-semantic-pilot-124-c507":["hs-semantic-pilot-123-c409"],
}
MODULE_PREREQS={
 "hs-semantic-pilot-124-c503":["hs-semantic-pilot-124-c502"],
 "hs-semantic-pilot-124-c504":["hs-semantic-pilot-124-c502","hs-semantic-pilot-124-c503"],
 "hs-semantic-pilot-124-c505":["hs-semantic-pilot-124-c501"],
 "hs-semantic-pilot-124-c506":["hs-semantic-pilot-124-c505"],
 "hs-semantic-pilot-124-c507":["hs-semantic-pilot-124-c505"],
 "hs-semantic-pilot-124-c508":["hs-semantic-pilot-124-c507"],
 "hs-semantic-pilot-124-c509":["hs-semantic-pilot-124-c501"],
 "hs-semantic-pilot-124-c510":["hs-semantic-pilot-124-c501","hs-semantic-pilot-124-c506"],
}
def require(ok,msg):
    if not ok: raise ValueError("KB159 fail closed: "+msg)
def serialize(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def author_rows():
    rows=[json.loads(x) for x in AUTHOR.read_text(encoding="utf-8").splitlines() if x.strip()]
    require(tuple(x.get("id") for x in rows)==IDS,"unique 10 chapter IDs/order")
    return rows
def mac_pdfkit_line_locks():
    # These extraction functions compare against the already pinned, local PDFKit
    # evidence. No output ever contains standard text.
    up=previous.old.previous.previous.previous.previous.previous.prior.prior.prior.old.prior.upstream
    pages=up.prior.previous.prev.prior.prior.previous.source_pages()
    ctx=previous.old.contexts()
    result={}
    for cid in IDS:
        s=ctx[cid]["source"]
        fp=up.fingerprint(pages,s)
        require(fp["span_sha256"]==s["source_span_sha256"],"source span drift "+cid)
        result[cid]=dict(page=s["printed_page"],start_line=s["start_line"],
            end_line=s["end_line"],span_sha256=fp["span_sha256"],
            line_sha256=fp["line_sha256"])
    return result
@lru_cache(maxsize=1)
def build():
    old=previous.audit(previous.build())
    require(old["total_teacher_only_drafts"]==175,"previous total changed")
    seen={r["candidate"] for r in old["rows"]}
    require(not seen.intersection(IDS),"duplicate previously written source")
    ctx=previous.old.contexts()
    locks=json.loads(LOCKS.read_text(encoding="utf8"))
    require(set(locks)==set(IDS),"missing source locks")
    rows=[]
    for d in author_rows():
        cid=d["id"]; c=ctx[cid]; s=c["source"]; lock=locks[cid]
        require(c["course_track"]=="COMPULSORY","incorrect course track")
        require(s["original_pdf_sha256"]==PDF,"wrong syllabus")
        require((lock["page"],lock["start_line"],lock["end_line"],lock["span_sha256"])==
               (s["printed_page"],s["start_line"],s["end_line"],s["source_span_sha256"]),
               "source lock mismatch "+cid)
        require(len(lock["line_sha256"])==lock["end_line"]-lock["start_line"]+1 and
                all(re.fullmatch("[0-9a-f]{64}",h) for h in lock["line_sha256"]+[lock["span_sha256"]]),
                "incomplete original line SHA "+cid)
        require(d["type"] in ("Concept","Theorem","Method"),"invalid knowledge type")
        for k in ("topic","formal","domain","assumptions","legal","failure","wrong","repair","near","far"):
            require(isinstance(d.get(k),str) and len(d[k])>=(8 if k=="topic" else 25),
                    "missing authoring "+k+" "+cid)
        require(len(d["steps"])==4 and len(d["examples"])==2 and len(d["hints"])==3,
                "depth assets missing "+cid)
        require(all(isinstance(x,str) and len(x)>=20 for x in d["steps"]+d["hints"]),
                "shallow reasoning or hint "+cid)
        require(all(len(e["q"])>=15 and len(e["a"])>=2 and len(e["sol"])>=3 and
                    all(len(line)>=12 for line in e["sol"]) for e in d["examples"]),
                "teacher examples shallow "+cid)
        rows.append(dict(
            id="kb159-deep-"+cid.removeprefix("hs-semantic-pilot-"),
            source_candidate_id=cid,course_track="COMPULSORY",
            knowledge_type=d["type"],title=d["topic"],
            standard_version="2017-edition-2020-revision-editorial-pilot",
            source_pdf_sha256=PDF,source_printed_page=lock["page"],
            source_start_line=lock["start_line"],source_end_line=lock["end_line"],
            source_span_sha256=lock["span_sha256"],source_line_sha256=lock["line_sha256"],
            source_evidence_status=EVIDENCE,official_atom_id=None,
            source_semantics_human_approved=False,
            formal_definition_or_theorem=d["formal"],notation_and_domain=d["domain"],
            applicability_and_hypotheses=d["assumptions"],why_method_is_legal=d["legal"],
            reasoned_steps=[dict(step=i+1,justification=x) for i,x in enumerate(d["steps"])],
            nonexample_or_failure=d["failure"],typical_wrong_solution=d["wrong"],
            why_wrong_and_repair=d["repair"],
            teacher_examples=[dict(question=e["q"],answer=e["a"],reasoned_solution=e["sol"]) for e in d["examples"]],
            student_hint_ladder=d["hints"],near_transfer=d["near"],far_transfer=d["far"],
            prerequisite_proposals=c["prerequisite_candidate_ids"],
            module_prerequisite_candidate_ids=MODULE_PREREQS.get(cid,[]),
            prerequisite_math_review="REVIEW_PENDING",
            teacher_review_status="REVIEW_PENDING",teacher_review_evidence=None,
            teacher_solution_visibility="TEACHER_ONLY",formal_proof_certified=False,
            free_student_step_verified=False,student_authoritative=False,
            possible_semantic_overlap_ids=DUPLICATES.get(cid,[]),
            elective_e_optional_example=False))
    validate(rows)
    return rows
def validate(rows):
    require(len(rows)==10 and len({r["source_candidate_id"] for r in rows})==10,
            "incomplete module")
    locks=json.loads(LOCKS.read_text(encoding="utf8"))
    for node,parents in MODULE_PREREQS.items():
        require(node in IDS and all(p in IDS and IDS.index(p)<IDS.index(node) for p in parents),
                "orphan/cyclic module prerequisite edge")
    for r in rows:
        cid=r["source_candidate_id"];lock=locks[cid]
        require(cid in IDS and r["source_pdf_sha256"]==PDF and
          r["source_evidence_status"]==EVIDENCE and
          (r["source_printed_page"],r["source_start_line"],r["source_end_line"],
           r["source_span_sha256"],r["source_line_sha256"])==
          (lock["page"],lock["start_line"],lock["end_line"],
           lock["span_sha256"],lock["line_sha256"]),"forged source provenance")
        require(r["teacher_review_status"]=="REVIEW_PENDING" and
          r["teacher_review_evidence"] is None and
          r["teacher_solution_visibility"]=="TEACHER_ONLY" and
          r["official_atom_id"] is None and
          r["source_semantics_human_approved"] is False and
          r["formal_proof_certified"] is False and
          r["student_authoritative"] is False and
          r["free_student_step_verified"] is False and
          r["prerequisite_math_review"]=="REVIEW_PENDING","forged approval")
        require(len(r["teacher_examples"])==2 and len(r["student_hint_ladder"])==3,
                "missing tutoring assets")
    return True
def audit(rows):
    old=previous.audit(previous.build())
    allrows=old["rows"]+[dict(id=r["id"],candidate=r["source_candidate_id"],
                      track=r["course_track"],source_sha=r["source_span_sha256"],
                      review="REVIEW_PENDING") for r in rows]
    require(len(allrows)==185 and len({r["candidate"] for r in allrows})==185,"inventory drift")
    counts=Counter(r["track"] for r in allrows)
    return dict(schema="kb159-compulsory-functions-depth-not-official-atoms/1",
      module="COMPULSORY_FUNCTION_REPRESENTATIONS_EXP_LOG_TRIG_ZERO_MODEL",
      previous_teacher_only_drafts=175,added_original_manuscripts=10,
      total_teacher_only_drafts=185,historical_editorial_leads=239,
      historical_leads_with_pending_drafts=144,historical_leads_without_drafts=95,
      source_numbered_markers_not_official_atoms=315,
      official_atom_denominators={t:None for t in TRACKS},
      official_coverage_rate=None,
      by_track={t:counts[t] for t in TRACKS},
      student_authoritative=0,teacher_approved=0,
      proof_certified_from_bounded_oracle=0,
      teacher_examples=20,student_hint_steps=30,transfer_tasks=20,
      possible_semantic_overlap_pairs=[list(x) for x in sorted(set(
         tuple(sorted((r["source_candidate_id"],x)))
         for r in rows for x in r["possible_semantic_overlap_ids"]))],
      review="REVIEW_PENDING",rows=sorted(allrows,key=lambda r:r["candidate"]))
def provisional_atom_dossiers(rows):
    # A candidate dossier is a review question, NOT a frozen atom. Similar
    # descriptions across historical candidates may correspond to one atom.
    dossiers=[]
    for r in rows:
        dossiers.append(dict(
          candidate_id=r["source_candidate_id"],course_track="COMPULSORY",
          source_printed_page=r["source_printed_page"],
          source_line_sha256=r["source_line_sha256"],
          source_span_sha256=r["source_span_sha256"],
          proposed_math_objective=r["formal_definition_or_theorem"],
          proposed_kind=r["knowledge_type"],
          proposed_prerequisites=r["prerequisite_proposals"],
          module_prerequisites=r["module_prerequisite_candidate_ids"],
          domain_condition_review=r["applicability_and_hypotheses"],
          counterexample_review=r["nonexample_or_failure"],
          potential_semantic_overlap_ids=r["possible_semantic_overlap_ids"],
          uniqueness_human_decision="PENDING",
          source_requirement_human_approval="PENDING",
          official_atom_id=None,official_atom_count_contribution=None,
          teacher_approved=False,student_authoritative=False))
    return dict(schema="kb159-provisional-atom-dossiers-not-official/1",
          source_pdf_sha256=PDF,review_pages=sorted({r["source_printed_page"] for r in rows}),
          candidate_dossiers=10,unique_official_atoms=None,
          overlapping_editorial_dossiers=len([x for x in dossiers if x["potential_semantic_overlap_ids"]]),
          official_atom_denominators={t:None for t in TRACKS},
          national_coverage_rate=None,teacher_approved=0,student_authoritative=0,
          dossiers=dossiers)
def markdown(rows):
    header=["# KB159｜必修函数连续模块10篇教师候审讲义","",
      "10个历史编辑候选≠10个唯一官方原子；与既有讲义的潜在交叉必须教师裁决。","",
      "新增20道教师例题、30级不剧透提示、20道迁移；185份累计教师候审稿，教师批准0。",""]
    for r in rows:
        header.extend(["## "+r["title"],"",
          "候选："+r["source_candidate_id"]+"；原始PDFKit印刷页"+
          str(r["source_printed_page"])+"；源段SHA："+r["source_span_sha256"],"",
          "**状态 REVIEW_PENDING / TEACHER_ONLY；非已认证课标原子。**","",
          "### 正式定义/命题",r["formal_definition_or_theorem"],"",
          "### 符号、域与前提",r["notation_and_domain"],r["applicability_and_hypotheses"],"",
          "### 数学依据",r["why_method_is_legal"],"",
          "### 分步推导"])
        header.extend(str(s["step"])+". "+s["justification"] for s in r["reasoned_steps"])
        header.extend(["","### 失效与典型错法",r["nonexample_or_failure"],
             r["typical_wrong_solution"],r["why_wrong_and_repair"],"",
             "### 教师例题（不得学生直接检索）"])
        for e in r["teacher_examples"]:
            header.extend(["**题：**"+e["question"],"**答：**"+e["answer"]])
            header.extend("- "+line for line in e["reasoned_solution"])
        header.extend(["","### 学生三级提示"])
        header.extend(str(i+1)+". "+h for i,h in enumerate(r["student_hint_ladder"]))
        header.extend(["","### 近迁移",r["near_transfer"],"","### 远迁移",r["far_transfer"],""])
    return "\n".join(header).rstrip()+"\n"
def review_markdown(d):
    lines=["# KB159｜K00必修函数原子拆分候审队列","",
       "以下10条仅为原始课程来源哈希锁定的**独立编辑候选**，既非教师裁决后的课程原子，也不能作为国家课标分母。","",
       "| 候选 | 页 | 可能语义重叠 | 审核结果 |",
       "|---|---:|---|---|"]
    for r in d["dossiers"]:
        lines.append("| "+r["candidate_id"]+" | "+str(r["source_printed_page"])+" | "+
             ",".join(r["potential_semantic_overlap_ids"])+" | PENDING |")
    lines.extend(["","跨页同义、包含关系及多候选同一原子裁决尚未完成；应由真实教师核对来源、定义域和课程归属，七轨正式分母仍 UNKNOWN。",""])
    return "\n".join(lines)
def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write-mac",action="store_true")
    group.add_argument("--check-mac",action="store_true")
    group.add_argument("--check",action="store_true")
    args=parser.parse_args()
    if args.write_mac:LOCKS.write_text(serialize(mac_pdfkit_line_locks()),encoding="utf8")
    if args.check_mac:
        require(json.loads(LOCKS.read_text(encoding="utf8"))==mac_pdfkit_line_locks(),
                "original Mac PDFKit source replay")
    rows=build()
    a=audit(rows); dossiers=provisional_atom_dossiers(rows)
    safe=[dict(id=r["id"],source_candidate_id=r["source_candidate_id"],course_track=r["course_track"],
               title=r["title"],review_status="REVIEW_PENDING",
               student_authoritative=False,teacher_solution_exposed=False) for r in rows]
    expected=((OUT,serialize(rows)),(AUDIT,serialize(a)),(REPORT,markdown(rows)),
              (SAFE,serialize(safe)),(ATOMS,serialize(dossiers)),
              (REV,review_markdown(dossiers)))
    if args.write_mac:
        for p,body in expected:p.write_text(body,encoding="utf8")
    else:
        for p,body in expected:require(p.read_text(encoding="utf8")==body,"artifact drift "+str(p))
    print("PASS KB159 10 full compulsory function drafts; 20 examples; 185 pending; national denominator UNKNOWN")
if __name__=="__main__":main()
