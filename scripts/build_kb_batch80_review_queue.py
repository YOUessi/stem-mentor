#!/usr/bin/env python3
"""Batch80: immutable source-linked K00 review denominators and K07 proof review debt.

Candidate review denominators are machine-countable, NOT official atom denominators.
Finite checking and human review status remain separate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "anchors": "docs/evaluation/KB_BATCH61_CLAUSE_ANCHOR_COVERAGE.json",
    "partitions": "docs/evaluation/KB_BATCH73_PAGE_PARTITION_COVERAGE.json",
    "triage": "docs/evaluation/KB_BATCH74_UNMARKED_REVIEW.json",
    "subspans": "docs/evaluation/KB_BATCH75_EDITORIAL_SUBCLAUSE_MATRIX.json",
    "lineage": "curriculum/highschool_math/kb_batch78_auditable_lineage.json",
    "proofs": "docs/evaluation/KB_BATCH78_PROOF_DEBT_MATRIX.json",
    "proof79": "knowledge/editorial_review/kb_batch79_condition_proof_cards.json",
    "conflicts": "docs/evaluation/KB_BATCH70_TEN_CONFLICT_PROOF_REVIEW.json",
    "guard80": "knowledge/editorial_review/kb_batch80_eight_proof_guard_cards.json",
}
EXPECTED_INPUT_CANONICAL_SHA256 = {
    "anchors": "6751fce34f1dcd6fc2f1c172c3d3ad10102e09a28b0bdc71de903d755f131e69",
    "partitions": "f84ae0cdceea23202dbdb66e5efb5e676a5cc5b0d83ec47659e1b6c899e15e3d",
    "triage": "9b756e1681e5fa3793576da89cfef2488287273e7a5bc96bc6798dd21494f115",
    "subspans": "3d4495316a5a33d883ed6a86184b41c3dae68346eddd53093bcd1cba80131b34",
    "lineage": "9029311b5aa39395d9b5f6d7bb0b833a7eaca15627cc613940e64e4e9cf7fc39",
    "proofs": "51eaf613de8d2138e36b9b5433659a275dbf8db41a9beb2f68be66a3aef6385b",
    "proof79": "2165170b86e813335e90cf2d663a18b7670cdae55980ab6ca57b515538a0ed72",
    "conflicts": "85ef088fb2318537a840604ba8ae7e2e10ce1825c0b141b5d9d9f52a7c9e013a",
    "guard80": "06bd845e306aa0fe6a62ef05b4328a7ce5bcfc5ad7e95692f2887cb1c092f8f6",
}

TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A", "ELECTIVE_B",
          "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")
OUT_CURR = ROOT / "curriculum/highschool_math/kb_batch80_review_queue.json"
OUT_PROOFS = ROOT / "docs/evaluation/KB_BATCH80_PROOF_QUEUE.json"
OUT_MD = ROOT / "docs/evaluation/KB_BATCH80_AUDIT_PROGRESS.md"


def load_inputs():
    return {k: json.loads((ROOT / p).read_text(encoding="utf-8")) for k,p in FILES.items()}


def check(condition, reason):
    if not condition:
        raise ValueError(reason)


def build(data=None):
    data = load_inputs() if data is None else data
    for key in FILES:
        canonical=json.dumps(data[key],ensure_ascii=False,sort_keys=True,
                             separators=(",", ":")).encode("utf-8")
        check(hashlib.sha256(canonical).hexdigest()==EXPECTED_INPUT_CANONICAL_SHA256[key],
              "Frozen independent input altered: "+key)
    a, p, tri, sub = (data[k] for k in ("anchors", "partitions", "triage", "subspans"))
    lin, proof, card79, con = (data[k] for k in ("lineage", "proofs", "proof79", "conflicts"))
    pdfs = {a["source_pdf_sha256"], p["source_pdf_sha256"], tri["source_pdf_sha256"],
            sub["source_pdf_sha256"], lin["source_pdf_sha256"]}
    check(len(pdfs)==1,"Source standard SHA divergence")
    check(len(a["anchors"])==428 and len(p["segments"])==484 and len(tri["records"])==56
          and len(sub["records"])==60,"K00 upstream inventory drift")
    check(a["full_page_teacher_review_completed"]==0 and p["teacher_full_page_reviews"]==0
          and lin["teacher_full_page_reviews"]==0,"Teacher review promoted without evidence")
    check(all(a["official_atomic_denominator"].get(t) is None for t in TRACKS)
          and all(p["official_denominator_by_track"].get(t) is None for t in TRACKS)
          and lin["official_full_curriculum_atom_denominator"] is None,
          "Official denominator must remain unknown")
    check(len({s["segment_id"] for s in p["segments"]})==484,"Duplicate source segment")
    check(len({(x["printed_page"],x["pdfkit_line"]) for x in a["anchors"]})==428,
          "Duplicate source anchor coordinate")
    lookup=defaultdict(list)
    for s in p["segments"]:
        check(s["official_clause_membership"]=="UNDETERMINED"
              and s["counted_in_official_atom_denominator"] is False
              and s["student_publishable"] is False,"Source segment was falsely approved")
        for n in range(s["first_line"],s["last_line"]+1):
            lookup[(s["printed_page"],n)].append(s)
    rows=[]
    for x in a["anchors"]:
        matched=lookup[(x["printed_page"],x["pdfkit_line"])]
        check(len(matched)==1,"Anchor has zero or multiple source line partitions")
        s=matched[0]
        check(s["track_hint"]==x["track_hint"],"Anchor track crossed course boundary")
        check(x["certified_official_atom"] is False and x["official_denominator_membership"]=="UNDETERMINED"
              and x["teacher_review"]=="REVIEW_PENDING" and x["student_publishable"] is False,
              "Anchor false review/approval claim")
        rows.append(dict(
            review_id=f"KB80-A{str(x['printed_page']).zfill(3)}-L{str(x['pdfkit_line']).zfill(3)}",
            kind=x["kind"],track=x["track_hint"],printed_page=x["printed_page"],
            pdfkit_line=x["pdfkit_line"],source_line_sha256=x["source_line_sha256"],
            source_page_pdfkit_sha256=x["source_page_pdfkit_sha256"],
            parent_segment=s["segment_id"],source_segment_range=[s["first_line"],s["last_line"]],
            partially_located_lead=bool(x["has_partially_located_source_lead"]),
            action="REVIEW_MATH_OBLIGATION_AND_CROSS_PAGE_EQUIVALENCE",
            status="REVIEW_PENDING",official_atom_count=None,student_publishable=False))
    check(len({r["review_id"] for r in rows})==428,"Duplicated review obligation IDs")
    check(len({r["printed_page"] for r in rows})<=61,"Page inventory drift")
    triage_ids={r["segment_id"] for r in tri["records"]}
    check(len(triage_ids)==56,"Duplicated unanchored triage")
    subspan_ids={x["id"] for x in sub["records"]}
    check(len(subspan_ids)==60,"Duplicated editorial subspan")
    counts=Counter(r["track"] for r in rows)
    by_track={}
    for t in TRACKS:
        check(counts[t]==a["candidate_anchor_count_by_track_hint"][t],
              "Anchor per-track counts drift: "+t)
        by_track[t]=dict(
            anchor_review_obligations=counts[t],
            page_source_partitions=p["tracks"][t]["heuristic_segment_count"],
            pending_unanchored_segments=sum(s["track_hint"]==t for s in tri["records"]),
            pending_editorial_subspans=sum(s["track_hint"]==t for s in sub["records"]),
            local_draft_topics=lin["by_track"][t]["local_candidate_topics"],
            teacher_approved=0,official_atom_denominator=None,atom_coverage=None,
            review_status="PENDING_HUMAN_ATOMIZATION_AND_CROSS_PAGE_EQUIVALENCE")
    check(sum(counts.values())==428 and len(a["pages"])==61,
          "Anchor/page conservation broken")
    curr=dict(schema_version="kb80-provisional-review-denominators-v1",
         standard_version="2017年版2020年修订",
         source_pdf_sha256=next(iter(pdfs)),source_inputs_sha256={
           k:hashlib.sha256((ROOT/v).read_bytes()).hexdigest()
           for k,v in FILES.items() if k in ("anchors","partitions","triage","subspans","lineage")},
         candidate_review_denominator=428,
         source_line_partition_count=484,nonanchor_triage_count=56,
         editorial_subspan_count=60,local_candidate_topic_count=26,
         all_source_pages=61,full_page_teacher_atomizations=0,
         officially_certified_atom_count=0,
         official_atom_denominator=None,student_publishable_count=0,
         elective_general_not_absorbed_into_any_track=True,
         by_track=by_track,anchor_review_queue=rows)
    obligations=proof["proof_obligations"]
    check(len(obligations)==538 and len({r["id"] for r in obligations})==538,
          "538 proof obligations changed or duplicated")
    cards=proof["review_cards"]+card79["review_cards"]+data["guard80"]["review_cards"]
    links={}
    origins={x["id"]:x for x in obligations}
    for c in cards:
        k=c["linked_historical_step_id"]
        check(k in origins and k not in links,"Proof card duplicated or orphaned")
        check(c["original_step_sha256"]==origins[k]["original_step_sha256"],
              "Linked proof SHA mismatch")
        check(c["review_status"]=="REVIEW_PENDING"
              and c["formal_math_certification"]=="NOT_FORMALLY_VERIFIED"
              and c["student_publishable"] is False
              and c["teacher_solution_visibility"]=="TEACHER_ONLY",
              "Proof card was illegally released")
        check(origins[k]["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE",
              "Linked proof must be in historical P0 review queue")
        links[k]=c["id"]
    check(len(links)==36 and len(proof["review_cards"])==16
          and len(card79["review_cards"])==12 and len(data["guard80"]["review_cards"])==8,"Previously completed 36 review links lost")
    conflict_ids={r["conflict_id"] for r in con["records"]}
    check(len(con["records"])==10 and len(conflict_ids)==10
          and con["conflicts_resolved"]==0 and con["teacher_approved"]==0,
          "Conflicts were falsely adjudicated")
    queue=[]
    for row in obligations:
        k=row["id"]
        check(row["status"]=="NOT_FORMALLY_VERIFIED"
              and row["teacher_review"]=="PENDING"
              and row["student_publishable"] is False
              and row["student_step_verified"] is False
              and row["whole_proof_certified"] is False,
              "Historical step falsely verified")
        topic=k.rsplit("#",1)[0]
        queue.append(dict(id=k,source_sha256=row["original_step_sha256"],
            risk_priority=row["risk_priority"],risk_groups=row["risk_groups"],
            source_audit=row["origin"],review_card_id=links.get(k),
            conflict_id=topic if topic in conflict_ids else None,
            next_action="TEACHER_MATH_ADJUDICATION" if topic in conflict_ids
               else "VERIFY_HYPOTHESES_AND_COUNTEREXAMPLES",
            formal_certification="NOT_FORMALLY_VERIFIED",
            review_status="REVIEW_PENDING",student_publishable=False))
    check(sum(x["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE" for x in queue)==127,
          "P0 frozen risk count changed")
    check(sum(x["review_card_id"] is not None for x in queue)==36,
          "Reviewed card links dropped")
    by_risk=Counter(x["risk_priority"] for x in queue)
    unresolved=[x for x in queue
         if x["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE"
         and x["review_card_id"] is None]
    check(len(unresolved)==91,"Unlinked urgent proof workload drift")
    proof_out=dict(schema_version="kb80-proof-review-tracking-v1",
        historical_step_denominator=538,p0_historical_steps=127,
        review_only_p0_card_links=36,p0_without_review_card=91,
        formally_certified_steps=0,teacher_approved_steps=0,
        unresolved_conflicts=10,
        original_ledger_sha256=hashlib.sha256((ROOT/FILES["proofs"]).read_bytes()).hexdigest(),
        by_risk=dict(by_risk),
        urgent_unlinked_step_ids=[x["id"] for x in unresolved],
        conflicts=[dict(id=r["conflict_id"],candidate_sha256=r["candidate_sha256"],
             active_sha256=r["active_sha256"],
             math_risk_fields=r["changed_risk_fields"],
             status="UNRESOLVED_NEEDS_INDEPENDENT_TEACHER") for r in con["records"]],
        step_review_queue=queue)
    md=["# Batch80｜可审计课程候选审查分母与证明债务待办","","**不是官方课程知识原子分母。**",
      f"本批建立 {len(rows)} 条精确页码/行号/SHA审查任务；保留 {len(triage_ids)} 个非锚定分区与 {len(subspan_ids)} 个编辑子片段，不能相加充当官方原子。",
      "",
      "| 轨道 | 待原子化来源锚点 | 来源分区 | 非锚定待审 | 子片段 | 暂定主题草案 | 官方原子分母 |",
      "|---|---:|---:|---:|---:|---:|---|"]
    for t,v in by_track.items():
        md.append(f"| {t} | {v['anchor_review_obligations']} | {v['page_source_partitions']} | {v['pending_unanchored_segments']} | {v['pending_editorial_subspans']} | {v['local_draft_topics']} | UNKNOWN |")
    md += ["","## K07：保持全部538条证明债务可追踪",
       f"- P0 高风险 {127}，其中 {36} 条已有编辑审查卡（本批新增8条）；**{len(unresolved)} 条仍无审查卡**。",
       "- 形式认证0；真实教师批准0；10组历史数学冲突仍未裁决。",
       "- 针对全部538条，保留ID、原始SHA、风险、已关联审查卡与待审核动作。",
       "- 本项目审稿卡和有限精确实例不构成对原命题或学生自由推导的形式证明。",
       "","## 继续推进：逐页人工课程原子化；针对P0清单优先补齐定理前提、严格证明与反例；10冲突独立裁决；教师签署后才能发布。"]
    return curr,proof_out,"\n".join(md)+"\n"


def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--check",action="store_true")
    args=pa.parse_args()
    curr,pr,md=build()
    for path,obj in ((OUT_CURR,curr),(OUT_PROOFS,pr),(OUT_MD,md)):
        serialized=obj if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
        if args.check:
            check(path.exists() and path.read_text(encoding="utf-8")==serialized,
                "Generated audit file drift: "+str(path))
        else:
            path.write_text(serialized,encoding="utf-8")
    print(json.dumps(dict(review_anchors=428,p0=127,p0_with_cards=36,p0_without=91,
                          official_denominators="UNKNOWN",unresolved_conflicts=10),
                     ensure_ascii=False))


if __name__=="__main__":
    main()
