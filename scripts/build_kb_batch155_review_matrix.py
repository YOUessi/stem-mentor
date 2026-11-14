#!/usr/bin/env python3
"""KB155: auditable, non-additive syllabus source obligations and human review queue.

315 numbered layout anchors, 41 proposed atoms, 239 editorial leads, 32
unnumbered C/D/E proposals, 145 unpublished manuscripts. These populations
overlap. Nothing here freezes an official syllabus denominator or certifies
mathematical correctness. No original copyrighted source text is bundled.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"curriculum/highschool_math/official_numbered_clause_evidence_batch18.json"
PROP=ROOT/"curriculum/highschool_math/k00_batch133_atomic_proposals.json"
LEADS=ROOT/"docs/evaluation/KB_BATCH147_SOURCE_BOUNDARY_QUEUE.json"
CDE=ROOT/"docs/evaluation/KB_BATCH150_DE_SEMANTIC_BOUNDARY.json"
DEPTH=ROOT/"docs/evaluation/KB_BATCH154_DEPTH_AUDIT.json"
GAPS=ROOT/"docs/evaluation/KB_BATCH154_SOURCE_TO_DRAFT_GAPS.json"
GRAPH=ROOT/"docs/evaluation/KB_BATCH154_SOURCE_GRAPH.json"
OUT=ROOT/"docs/evaluation/KB_BATCH155_REQUIREMENT_REVIEW_MATRIX.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH155_REQUIREMENT_REVIEW_MATRIX.md"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
        "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
HASH=re.compile(r"^[a-f0-9]{64}$")

def require(ok,msg):
    if not ok: raise ValueError("KB155 curriculum gate: "+msg)

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def encode(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"

def build():
    src,prop,leads,cde,depth,gaps,graph=map(load,(SRC,PROP,LEADS,CDE,DEPTH,GAPS,GRAPH))
    pdf=src["source"]["sha256"]
    require(bool(HASH.fullmatch(pdf)) and
       pdf==prop["source_pdf_sha256"]==leads["source_pdf_sha256"]==
       cde["official_pdf_sha256"]==graph["source_pdf_sha256"],"mixed syllabus PDF versions")
    require(len(src["pages"])==61 and {x["printed_page"] for x in src["pages"]}==set(range(13,74)),
            "source pages 13-73 missing")
    require(src["source"]["pdf_total_pages"]==188,"unexpected official PDF page count")
    marker=src["enumerated_source_anchors"]; pr=prop["records"]; lead=leads["candidates"]
    cdepr=cde["proposals"]; cdelines={x["line_id"]:x for x in cde["source_line_partition"]}
    drafts={x["candidate"]:x for x in depth["rows"]}
    require(len(marker)==315 and len({x["id"] for x in marker})==315,"numbered marker loss/dup")
    require(len(pr)==41 and len({x["id"] for x in pr})==41,"provisional proposal loss")
    require(len(lead)==239 and len({x["id"] for x in lead})==239,"editorial source loss")
    require(len(cdepr)==32 and len({x["id"] for x in cdepr})==32 and
            len(cdelines)==122,"CDE unnumbered source loss")
    require(len(drafts)==145 and depth["total_teacher_only_drafts"]==145,"draft inventory drift")
    require(gaps["matched_editorial_candidates"]==104 and gaps["missing_editorial_candidates"]==135 and
            set(gaps["unmatched_candidate_ids"])=={x["id"] for x in lead}-set(drafts),
            "draft/lead crosswalk disagreement")
    require(graph["source_numbered_markers"]==315 and graph["original_cde_lines_classified"]==122 and
            graph["pending_teacher_manuscripts"]==145 and graph["risk_pages"]==53,"previous graph drift")
    require(not graph["seven_track_official_census_complete"] and
            all(graph["official_atom_denominators"][t] is None for t in TRACKS),
            "official count previously forged")
    pids={x["id"] for x in pr}; lids={x["id"] for x in lead}
    # Historical drafts tied to all 41 kb133 proposals have source_sha=None in
    # the compressed coverage audit, although each proposal has a complete
    # versioned SHA line/span lock. Reconcile, never manufacture teacher review.
    proposals={x["id"]:x for x in pr}
    historical_sha_gaps=[]
    for d in drafts.values():
        if d.get("source_sha") is not None:
            require(HASH.fullmatch(d["source_sha"]),"bad existing manuscript source SHA")
            continue
        require(d["candidate"] in proposals,"unrecoverable historical manuscript source lock")
        source=proposals[d["candidate"]]["source_lock"]
        require(HASH.fullmatch(source["span_sha256"]) and
                len(source["line_sha256"])==source["end_line"]-source["start_line"]+1,
                "legacy proposal source span corrupt")
        historical_sha_gaps.append(dict(draft_id=d["id"],candidate_id=d["candidate"],
          track=d["track"],printed_page=source["printed_page"],
          start_line=source["start_line"],end_line=source["end_line"],
          source_span_sha256=source["span_sha256"],source_line_sha256=source["line_sha256"],
          reconciliation="EXISTING_PROPOSAL_SOURCE_LOCK_NOT_NEW_PDF_REHASH",
          draft_audit_source_sha_was_null=True,teacher_review="REVIEW_PENDING",
          mathematical_verification="NOT_CERTIFIED",official_atom_id=None))
    require(len(historical_sha_gaps)==41 and
            {v["candidate_id"] for v in historical_sha_gaps}==pids,
            "41 older proposal-linked draft SHA gaps not reconciled")
    mk_lookup={(x["printed_page"],x["line_number"]):x for x in marker}
    require(len(mk_lookup)==315,"source marker positions duplicated")
    editorial_by_page=defaultdict(list)
    proposal_by_page=defaultdict(list)
    for x in lead:
        require(x["track"] in TRACKS and x["page"] in range(13,74) and
                0<x["start"]<=x["end"] and HASH.fullmatch(x["span_sha"]) and
                x["semantic_review"]=="REVIEW_PENDING" and x["official_atom_id"] is None and
                x["teacher_approved"] is False,"editorial lead corrupted")
        editorial_by_page[x["page"]].append(x)
    for x in pr:
        s=x["source_lock"]
        require(x["track"] in TRACKS and x["atomization_review"]=="REVIEW_PENDING" and
                x["official_atom_id"] is None and x["teacher_approval"] is None and
                x["student_authoritative"] is False and
                len(s["line_sha256"])==s["end_line"]-s["start_line"]+1 and
                all(HASH.fullmatch(h) for h in s["line_sha256"]),"provisional source drift")
        proposal_by_page[s["printed_page"]].append(x)
    allrows=[]
    for m in sorted(marker,key=lambda x:(x["printed_page"],x["line_number"])):
        page,line,track=m["printed_page"],m["line_number"],m["track"]
        require(m["id"]==f"STD2020-P{page}-L{line:03d}" and
                m["pdf_page_index"]==page+7 and track in TRACKS and
                HASH.fullmatch(m["line_sha256"]) and
                m["status"]=="SOURCE_ENUMERATION_UNREVIEWED_NOT_OFFICIAL_ATOM" and
                not m["approved_lesson_ids"],"numbered source evidence drift")
        matches_lead=sorted(x["id"] for x in editorial_by_page[page]
                            if x["track"]==track and x["start"]<=line<=x["end"])
        matches_prop=sorted(x["id"] for x in proposal_by_page[page]
                            if x["track"]==track and x["source_lock"]["start_line"]<=line<=x["source_lock"]["end_line"])
        drafts_on_line=sorted(drafts[x]["id"] for x in matches_lead if x in drafts)
        allrows.append(dict(id=m["id"],record_kind="NUMBERED_SOURCE_LAYOUT_MARKER",
            course_track=track,printed_page=page,pdf_page_index=page+7,pdfkit_line=line,
            source_line_sha256=m["line_sha256"],
            overlapping_41_proposal_ids=matches_prop,
            overlapping_editorial_lead_ids=matches_lead,
            overlapping_teacher_only_draft_ids=drafts_on_line,
            link_semantics="LINE_OVERLAP_NOT_KNOWLEDGE_EQUIVALENCE",
            next_action=("HUMAN_SPLIT_OR_VALIDATE_UNPAIRED_REQUIREMENT" if not
                         (matches_lead or matches_prop) else "HUMAN_CHECK_SOURCE_SEMANTICS_AND_DUPLICATES"),
            official_atom_id=None,review_state="REVIEW_PENDING",teacher_approved=False,
            student_publishable=False))
    require(len(allrows)==315,"marker matrix incomplete")
    cde_rows=[]
    for p in sorted(cdepr,key=lambda x:x["id"]):
        ids=p["source_line_ids"]; hashes=p["source_line_sha256"]
        require(p["source_track"] in ("ELECTIVE_C","ELECTIVE_D","ELECTIVE_E") and
                bool(ids) and len(ids)==len(hashes)==len(set(ids)) and
                p["teacher_review"]=="REVIEW_PENDING" and
                p["official_knowledge_atom_id"] is None and
                p["teacher_approved"] is False and
                p["student_authoritative"] is False and not p["lesson_complete"],
                "CDE proposal incorrectly certified")
        for lid,h in zip(ids,hashes):
            require(lid in cdelines and cdelines[lid]["original_line_sha256"]==h and
                    cdelines[lid]["classification"]==p["source_track"],
                    "CDE line SHA/track mismatch")
        optional=p["source_track"]=="ELECTIVE_E"
        require(p["is_school_elective_example"] is optional,
                "optional E example conflated with nationwide compulsory")
        cde_rows.append(dict(id=p["id"],record_kind="UNNUMBERED_CDE_EDITORIAL_PROPOSAL",
            course_track=p["source_track"],printed_pages=sorted({cdelines[x]["printed_page"] for x in ids}),
            source_line_ids=ids,source_line_sha256=hashes,
            original_paraphrase=p["original_paraphrase"],
            is_school_elective_example=optional,mathematical_conditions_review="NOT_YET_CHECKED",
            semantic_duplicate_with_other_proposals="UNDETERMINED",
            next_action="HUMAN_SPLIT_REQUIREMENT_VERIFY_MATH_AND_DEDUP",
            official_atom_id=None,review_state="REVIEW_PENDING",teacher_approved=False,
            student_publishable=False))
    page_map={x["printed_page"]:x for x in graph["pages"]}
    pages=[]
    for page in range(13,74):
        base=page_map[page]
        sub=[r for r in allrows if r["printed_page"]==page]
        csub=[r for r in cde_rows if page in r["printed_pages"]]
        needs=[r for r in sub if not (r["overlapping_editorial_lead_ids"] or
                                     r["overlapping_41_proposal_ids"])]
        gaps_on_page=[x["id"] for x in editorial_by_page[page] if x["id"] not in drafts]
        draft_on_page=[x["id"] for x in editorial_by_page[page] if x["id"] in drafts]
        risk=list(base["risk_flags"])
        require(len(sub)==base["numbered_source_markers"] and
                len(needs)==base["numbered_without_existing_proposal_or_lead"],
                "page marker count inconsistent with previous source graph")
        pages.append(dict(printed_page=page,pdf_text_sha256=base["pdf_text_sha256"],
            course_tracks_with_numbered_sources=sorted({x["course_track"] for x in sub}),
            source_markers=len(sub),marker_ids=[x["id"] for x in sub],
            unpaired_layout_markers=len(needs),unpaired_marker_ids=[x["id"] for x in needs],
            CDE_unnumbered_proposal_ids=[x["id"] for x in csub],
            editorial_leads_with_unpublished_draft_ids=sorted(draft_on_page),
            editorial_leads_missing_deep_draft_ids=sorted(gaps_on_page),
            source_risk_flags=risk,
            next_review_queue_priority=(len(risk)*10+len(needs)*3+len(gaps_on_page)),
            scope_in_unnumbered_lines="UNKNOWN",scope_review="REVIEW_PENDING",
            official_atom_count=None))
    relations=leads["candidate_relation_edges"]
    require(len(relations)==89,"historical boundary relation queue changed")
    relation_rows=[]
    for edge in relations:
        require(edge["a"] in lids and edge["b"] in lids and edge["a"]!=edge["b"] and
                not edge["auto_merge_allowed"] and edge["human_decision"]=="REVIEW_PENDING" and
                edge["semantic_equivalence"]=="UNDETERMINED",
                "unauthorized semantic merge/adjudication")
        relation_rows.append(dict(source_lead_a=edge["a"],source_lead_b=edge["b"],
            relation=edge["relation"],printed_pages=edge["source_page_pair"],
            automatic_merge_permitted=False,human_semantic_decision="REVIEW_PENDING"))
    by_track={}
    for t in TRACKS:
        sub=[r for r in allrows if r["course_track"]==t]
        psub=[r for r in cde_rows if r["course_track"]==t]
        leads_t=[r for r in lead if r["track"]==t]
        drafts_t=[r for r in drafts.values() if r["track"]==t]
        base=graph["by_track"][t]
        require(len(sub)==base["source_numbered_markers"] and
                len(psub)==base["nonnumbered_cde_editorial_proposals"] and
                len(leads_t)==base["historic_editorial_leads"] and
                len(drafts_t)==base["unpublished_teacher_manuscripts"],
                "track reconciliation mismatch")
        by_track[t]=dict(numbered_source_markers=len(sub),
            numbered_markers_without_any_line_overlap=sum(not
                (r["overlapping_editorial_lead_ids"] or r["overlapping_41_proposal_ids"]) for r in sub),
            numbered_markers_with_unpublished_draft_overlap=sum(bool(r["overlapping_teacher_only_draft_ids"]) for r in sub),
            provisional_atom_proposals=sum(r["track"]==t for r in pr),
            unnumbered_CDE_editorial_proposals=len(psub),
            historical_editorial_leads=len(leads_t),leads_with_teacher_only_draft=sum(r["id"] in drafts for r in leads_t),
            leads_without_teacher_only_draft=sum(r["id"] not in drafts for r in leads_t),
            total_teacher_only_drafts=len(drafts_t),
            official_atom_denominator=None,teacher_approved=0,student_authoritative=0)
    require(sum(x["leads_without_teacher_only_draft"] for x in by_track.values())==135 and
            sum(x["leads_with_teacher_only_draft"] for x in by_track.values())==104,
            "track linked/absent draft conservation failed")
    sorted_pages=sorted(pages,key=lambda x:(-x["next_review_queue_priority"],x["printed_page"]))
    return dict(schema="kb155-source-review-matrix-not-official-atoms/1",
        standard="2017-edition-2020-revision",
        source_pdf_sha256=pdf,official_pdf_pages=188,printed_source_pages=61,
        numbered_source_layout_markers=315,provisional_atom_proposals=41,
        independent_CDE_unnumbered_proposals=32,classified_CDE_original_nonempty_lines=122,
        historical_editorial_leads=239,teacher_only_manuscripts=145,
        editorial_leads_with_teacher_only_drafts=104,editorial_leads_missing_teacher_only_drafts=135,
        historical_pending_source_relation_records=len(relations),
        draft_audit_source_sha_null_count_before_reconciliation=len(historical_sha_gaps),
        old_draft_proposal_lineage_reconciliations=historical_sha_gaps,
        source_marker_obligations=allrows,unnumbered_CDE_editorial_obligations=cde_rows,
        source_relation_review_queue=relation_rows,by_page=pages,
        by_track=by_track,prioritized_source_pages=[x["printed_page"] for x in sorted_pages],
        official_atom_denominators={x:None for x in TRACKS},
        current_official_completion_rate=None,official_source_scope_complete=False,
        crosspage_semantic_dedup_human_complete=False,human_semantic_merges=0,
        math_proof_certified_by_this_audit=0,real_teacher_approved=0,student_authoritative=0,
        interpretation="These are overlapping, unapproved, nonadditive *review populations*, not a national official atomic curriculum denominator.")
def validate(x):
    require(x["schema"]=="kb155-source-review-matrix-not-official-atoms/1","bad version")
    require(len(x["source_marker_obligations"])==x["numbered_source_layout_markers"]==315,
            "source marker row count")
    require(len(x["unnumbered_CDE_editorial_obligations"])==x["independent_CDE_unnumbered_proposals"]==32,
            "unnumbered CDE source row count")
    require(len(x["source_relation_review_queue"])==x["historical_pending_source_relation_records"]==89,
            "crosspage relation row count")
    require(len(x["old_draft_proposal_lineage_reconciliations"])==
            x["draft_audit_source_sha_null_count_before_reconciliation"]==41,
            "41 historical candidate source lineages lost")
    for legacy in x["old_draft_proposal_lineage_reconciliations"]:
        require(legacy["draft_audit_source_sha_was_null"] is True and
                legacy["reconciliation"]=="EXISTING_PROPOSAL_SOURCE_LOCK_NOT_NEW_PDF_REHASH" and
                legacy["teacher_review"]=="REVIEW_PENDING" and
                legacy["mathematical_verification"]=="NOT_CERTIFIED" and
                legacy["official_atom_id"] is None and
                HASH.fullmatch(legacy["source_span_sha256"]) and
                len(legacy["source_line_sha256"])==legacy["end_line"]-legacy["start_line"]+1,
                "legacy missing audit SHA repaired falsely")
    require(len(x["by_page"])==x["printed_source_pages"]==61 and
            {p["printed_page"] for p in x["by_page"]}==set(range(13,74)),"source page loss")
    require(set(x["by_track"])==set(TRACKS) and
            x["historical_editorial_leads"]==239 and x["teacher_only_manuscripts"]==145 and
            x["editorial_leads_with_teacher_only_drafts"]==104 and
            x["editorial_leads_missing_teacher_only_drafts"]==135,"source/draft counts")
    require(x["official_source_scope_complete"] is False and
            x["crosspage_semantic_dedup_human_complete"] is False and
            x["human_semantic_merges"]==x["math_proof_certified_by_this_audit"]==
            x["real_teacher_approved"]==x["student_authoritative"]==0 and
            x["current_official_completion_rate"] is None and
            all(x["official_atom_denominators"][t] is None for t in TRACKS),
            "falsely published official course completion")
    ids=set()
    for r in x["source_marker_obligations"]:
        require(r["id"] not in ids, "duplicated numbered source marker")
        ids.add(r["id"])
        require(r["review_state"]=="REVIEW_PENDING" and not r["student_publishable"] and
                not r["teacher_approved"] and r["official_atom_id"] is None and
                r["link_semantics"]=="LINE_OVERLAP_NOT_KNOWLEDGE_EQUIVALENCE" and
                HASH.fullmatch(r["source_line_sha256"]), "marker review guard bypass")
    require(len(ids)==315, "duplicate marker positions")
    uids=set()
    for r in x["unnumbered_CDE_editorial_obligations"]:
        require(r["id"] not in uids, "duplicate unnumbered candidate")
        uids.add(r["id"])
        require(r["review_state"]=="REVIEW_PENDING" and
                r["course_track"] in ("ELECTIVE_C","ELECTIVE_D","ELECTIVE_E") and
                r["is_school_elective_example"]==(r["course_track"]=="ELECTIVE_E") and
                r["official_atom_id"] is None and not r["student_publishable"] and not r["teacher_approved"] and
                r["semantic_duplicate_with_other_proposals"]=="UNDETERMINED" and
                len(r["source_line_sha256"])==len(r["source_line_ids"]) and
                all(HASH.fullmatch(h) for h in r["source_line_sha256"]), "CDE review guard bypass")
    require(len(uids)==32, "duplicate CDE source candidate")
    for r in x["source_relation_review_queue"]:
        require(r["source_lead_a"]!=r["source_lead_b"] and
                not r["automatic_merge_permitted"] and
                r["human_semantic_decision"]=="REVIEW_PENDING","unauthorized semantic dedup")
    for p in x["by_page"]:
        require(p["scope_in_unnumbered_lines"]=="UNKNOWN" and
                p["scope_review"]=="REVIEW_PENDING" and p["official_atom_count"] is None,
                "page falsely finalized")
    for t,r in x["by_track"].items():
        require(r["official_atom_denominator"] is None and r["teacher_approved"]==
                r["student_authoritative"]==0 and
                r["leads_with_teacher_only_draft"]+r["leads_without_teacher_only_draft"]==
                r["historical_editorial_leads"],"track scope falsely finalized")
    return True

def render(x):
    lines=["# KB155｜全量已检出来源的机器可审核任务矩阵（非课标原子总数）","",
       "**来源锚不是知识原子；行重叠不是语义相同；候审讲义不是教师批准。**",
       f"来源PDF SHA-256: `{x['source_pdf_sha256']}`。仅包含原创转述与来源元数据，不存储版权课标原文。","",
       "| 来源人口 | 本批机器对账结果 | 不能解释为 |",
       "|---|---:|---|",
       f"| 61页中的编号排版标记 | {x['numbered_source_layout_markers']} | 正式原子分母 |",
       f"| 已有暂定原子提案 | {x['provisional_atom_proposals']} | 已批准的原子 |",
       f"| 未编号C/D/E暂定提案 | {x['independent_CDE_unnumbered_proposals']} | 全国统一必修 |",
       f"| 历史编辑来源线索 | {x['historical_editorial_leads']} | 未去重的知识总数 |",
       f"| 编辑候审讲义 | {x['teacher_only_manuscripts']} | 上线可教原子 |",
       f"| 旧审计source_sha为空、已定位原提案source_lock | {x['draft_audit_source_sha_null_count_before_reconciliation']} | 重新数学认证或教师签字 |",
       f"| 跨页/同页待裁决来源关系 | {x['historical_pending_source_relation_records']} | 已确认等价/重复 |","",
       "## 七轨缺口（历史编辑线索，不是官方完成率）","",
       "| 轨道 | 编号标记 | 无相关行提案标记 | 编辑线索缺稿 | 候审讲义 | 未编号CDE提案 | 官方原子分母 |",
       "|---|---:|---:|---:|---:|---:|---|"]
    for t in TRACKS:
        a=x["by_track"][t]
        lines.append(f"| {t} | {a['numbered_source_markers']} | {a['numbered_markers_without_any_line_overlap']} | {a['leads_without_teacher_only_draft']} | {a['total_teacher_only_drafts']} | {a['unnumbered_CDE_editorial_proposals']} | UNKNOWN |")
    lines+=["","## 先核对高风险来源页","",
       "| 课标印刷页 | 编号来源 | 未关联行标记 | 编辑线索缺稿 | 来源风险 |",
       "|---:|---:|---:|---:|---|"]
    pmap={p["printed_page"]:p for p in x["by_page"]}
    for pg in x["prioritized_source_pages"][:30]:
        p=pmap[pg]
        lines.append(f"| {pg} | {p['source_markers']} | {p['unpaired_layout_markers']} | {len(p['editorial_leads_missing_deep_draft_ids'])} | {', '.join(p['source_risk_flags']) or '未识别（仍须审）'} |")
    lines+=["","## 可执行审核顺序","",
      "1. 教研人员依据本地合法课标PDF的哈希/页码/行号，确认该来源是否真包含知识要求；未编号文字不能被跳过。",
      "2. 逐句拆分数学对象、量词、限制条件与方法适用边界；正式知识ID仅在人工确认后赋值。",
      "3. 审核89条来源关系的语义是否等价（含跨页衔接），禁止依据行重叠自动合并。",
      "4. 依未匹配的135条历史编辑线索建设分模块原创讲义、题族及反例；审核数学证明后交教师签字。",
      "5. 未完成七轨原子分母与真人审校前：正式课程覆盖率UNKNOWN、APPROVED=0、学生权威发布=0。","",
      "此文件由 `scripts/build_kb_batch155_review_matrix.py` 从已锁定的既有来源/稿件资产再生。"
      "完整315个编号记录、32个未编号来源提案、89条来源关系与61页审查队列见同名JSON。",""]
    return "\n".join(lines)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    v=build();validate(v)
    targets=[(OUT,encode(v)),(REPORT,render(v))]
    if args.check:
        for path,raw in targets:require(path.exists() and path.read_text(encoding="utf-8")==raw, f"stale: {path}")
    else:
        for path,raw in targets:path.write_text(raw,encoding="utf-8")
    print("KB155 PASS: 61 source pages / 315 numbered markers / 32 CDE proposals / "
          "239 leads / 145 drafts; official denominators UNKNOWN")
if __name__=="__main__":main()
