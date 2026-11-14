#!/usr/bin/env python3
"""K00 full 61-page evidence triage. Counts source review work, never official atoms.

No raw copyrighted PDF passages are stored. Source hashes, page IDs and review
obligations are regenerated from repository versions and reviewed source locks.
"""
from __future__ import annotations
import argparse,collections,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch155_review_matrix as source
import build_kb_batch158_scope_ledger as ledger
OUT=ROOT/"docs/evaluation/KB_BATCH158_PAGE_REVIEW_MATRIX.json"
MD=ROOT/"docs/evaluation/KB_BATCH158_PAGE_REVIEW_MATRIX.md"
def enc(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def check(x,msg):
    if not x:raise ValueError("KB158 page-source triage: "+msg)
def build():
    l=ledger.build(); b=source.build()
    base=json.loads((ROOT/"curriculum/highschool_math/official_numbered_clause_evidence_batch18.json").read_text(encoding="utf-8"))
    rows=l["numbered_marker_review_rows"]
    check(len(rows)==315 and len(base["pages"])==61,"pinned 61-page/315-marker corpus drift")
    pages=[]; seen=set()
    for page in base["pages"]:
        p=page["printed_page"]
        anchors=[x for x in rows if x["printed_page"]==p]
        cde=[x for x in b["unnumbered_CDE_editorial_obligations"] if p in x["printed_pages"]]
        relations=[x for x in b["source_relation_review_queue"] if p in x["printed_pages"]]
        priorities=collections.Counter(x["priority"] for x in anchors)
        priority_score=4*(priorities["P0_UNMAPPED_LAYOUT_LINE"]+priorities["P0_MULTIPLE_POSSIBLE_SEMANTIC_UNITS"])+2*priorities["P1_NO_LINKED_COMPLETE_DRAFT"]+priorities["P2_DRAFT_EXISTS_NEEDS_TEACHER_SEMANTIC_REVIEW"]+3*len(relations)+2*len(cde)
        check(p not in seen,"duplicate printed page");seen.add(p)
        check(len(anchors)==page["source_numbered_marker_count"],"source enumeration mismatch page "+str(p))
        check(all(x["source_line_sha256"] and x["review_state"]=="REVIEW_PENDING" for x in anchors),"marker provenance/approval tamper")
        pages.append(dict(printed_page=p, pdf_page_index=page["pdf_page_index"],
           source_page_sha256=page["pdf_text_sha256"],tracks=page["tracks_present"],
           numbered_layout_markers=len(anchors),numbered_marker_ids=[x["id"] for x in anchors],
           ambiguous_multi_unit_markers=priorities["P0_MULTIPLE_POSSIBLE_SEMANTIC_UNITS"],
           unmapped_layout_markers=priorities["P0_UNMAPPED_LAYOUT_LINE"],
           source_markers_without_a_pending_draft=priorities["P1_NO_LINKED_COMPLETE_DRAFT"],
           with_pending_draft_but_semantics_unreviewed=priorities["P2_DRAFT_EXISTS_NEEDS_TEACHER_SEMANTIC_REVIEW"],
           cde_unumbered_proposal_ids=[x["id"] for x in cde],
           boundary_relation_records=len(relations),
           boundary_relation_kinds=dict(sorted(collections.Counter(x["relation"] for x in relations).items())),
           triage_score_not_atomic_count=priority_score,official_atom_count=None,
           human_semantic_split_complete=False,teacher_approved=0))
    check(set(range(13,74))==seen,"printed page census incomplete")
    check(sum(x["numbered_layout_markers"] for x in pages)==315,"marker conservation")
    check(sum(x["unmapped_layout_markers"] for x in pages)==l["triage_priority_counts"]["P0_UNMAPPED_LAYOUT_LINE"],"unmapped conservation")
    check(sum(x["ambiguous_multi_unit_markers"] for x in pages)==l["triage_priority_counts"]["P0_MULTIPLE_POSSIBLE_SEMANTIC_UNITS"],"ambiguous conservation")
    check(all(x["official_atom_count"] is None for x in pages),"fabricated official denominator")
    score_order=sorted(pages,key=lambda x:(-x["triage_score_not_atomic_count"],x["printed_page"]))
    return dict(schema="kb158-page-semantic-review-prioritization-v1",
       original_source_sha256=l["source_pdf_sha256"],
       official_atom_denominators=l["official_atom_denominators"],
       official_coverage_rate=None,teacher_approved=0,student_authoritative=0,
       source_pages=61,numbered_layout_markers=315,
       cde_proposals_unique=32,relation_records_unique=89,
       cde_page_memberships=sum(len(x["cde_unumbered_proposal_ids"]) for x in pages),
       crosspage_relation_page_memberships=sum(x["boundary_relation_records"] for x in pages),
       review_completed=0,
       risk_sorted_page_ids=[x["printed_page"] for x in score_order],
       pages=pages)
def validate(o):
    check(o==build(),"stale/tampered or invented source-page counts")
    return True
def markdown(d):
    lines=["# KB158 K00｜61页逐页审查矩阵（原子分母仍未知）","",
      "**本表不是课程知识原子计数。** 315个排版标记、32个C/D/E非编号提案和89条关系记录相互重叠，禁止相加。",
      "各源页留有PDF页指纹；不包含课标正文、未经核实的语义合并或教师批准。","",
      "| 印刷页 | 轨道 | 编号标记 | P0未关联 | P0多义 | 缺候审稿 | CDE提案 | 边界关系 | 审查优先分 |",
      "|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
    for row in sorted(d["pages"],key=lambda x:(-x["triage_score_not_atomic_count"],x["printed_page"])):
        lines.append(f'| {row["printed_page"]} | {",".join(row["tracks"])} | {row["numbered_layout_markers"]} | {row["unmapped_layout_markers"]} | {row["ambiguous_multi_unit_markers"]} | {row["source_markers_without_a_pending_draft"]} | {len(row["cde_unumbered_proposal_ids"])} | {row["boundary_relation_records"]} | {row["triage_score_not_atomic_count"]} |')
    lines+=["","优先级评分仅用于安排逐句人审；同一关系可能涉及多页，**页关联和不等于唯一候选数**。","",
      "## 未完成事项","",
      "1. 对每个编号标记和非编号课程要求划定完整语义范围、列出合法课程原子候选，执行跨页同义/包含/无关裁决。",
      "2. 由真实教师复核数学假设、课程归属和审核状态，才能建立可冻结的七轨正式知识原子分母。",
      "3. 目前175份讲义均为REVIEW_PENDING/TEACHER_ONLY，学生端权威证据为0。",""]
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    opt=p.parse_args();d=build();validate(d)
    targets=((OUT,enc(d)),(MD,markdown(d)))
    if opt.write:
        for path,value in targets:path.write_text(value,encoding="utf-8")
    else:
        for path,value in targets:check(path.read_text(encoding="utf-8")==value,"artifact drift "+str(path))
    print("PASS KB158 K00 61 complete source-page triage rows; national denominators UNKNOWN")
if __name__=="__main__":main()
