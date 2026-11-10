#!/usr/bin/env python3
"""Seven-track K00 source→triage→editorial subspan→draft lineage, NOT official atoms."""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCES={
 "partition":ROOT/"docs/evaluation/KB_BATCH73_PAGE_PARTITION_COVERAGE.json",
 "triage":ROOT/"docs/evaluation/KB_BATCH74_UNMARKED_REVIEW.json",
 "subspan":ROOT/"docs/evaluation/KB_BATCH75_EDITORIAL_SUBCLAUSE_MATRIX.json",
 "draft":ROOT/"knowledge/editorial_review/kb_batch77_unlinked_candidate_drafts.json",
}
OUT=ROOT/"curriculum/highschool_math/kb_batch78_auditable_lineage.json"
MD=ROOT/"docs/evaluation/KB_BATCH78_SEVEN_TRACK_SOURCE_LINEAGE.md"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
def read(p):return json.loads(p.read_text(encoding="utf8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2)+"\n"
def build(input_override=None):
    data={k:read(p) if input_override is None or k not in input_override else input_override[k] for k,p in SOURCES.items()}
    x,y,z,w=[data[k] for k in SOURCES]
    if not (len(x["segments"])==484 and len(y["records"])==56 and len(z["records"])==60 and len(w["candidates"])==26):
        raise ValueError("484/56/60/26 editorial source counts drifted")
    if len({r["segment_id"] for r in x["segments"]})!=484 or len({r["segment_id"] for r in y["records"]})!=56:
        raise ValueError("Duplicate page/triage segment")
    if len({r["id"] for r in z["records"]})!=60 or len({r["candidate_id"] for r in w["candidates"]})!=26:
        raise ValueError("Duplicate editorial subspan or candidate")
    pdf={data[k]["source_pdf_sha256"] for k in SOURCES}
    if len(pdf)!=1:raise ValueError("Source standard PDF differs across stages")
    prior={r["segment_id"]:r for r in x["segments"]}
    tri={r["segment_id"]:r for r in y["records"]}
    sub={r["id"]:r for r in z["records"]}
    if len(w["by_track"])!=7 or any(w["official_denominators"][t] is not None for t in TRACKS):
        raise ValueError("Falsified official denominators")
    if w["local_denominator"]!=26 or w["local_candidates_with_drafts"]!=26 or w["teacher_approvals"]!=0:
        raise ValueError("Local candidate coverage falsely reported")
    if x["teacher_full_page_reviews"]!=y["teacher_full_page_reviews"]!=z["teacher_full_page_reviews"]!=w["teacher_full_page_reviews"]!=0:
        raise ValueError("Fake teacher full-page review")
    edges=[];nodes=[]
    for r in x["segments"]:
        if r["official_clause_membership"]!="UNDETERMINED" or r["counted_in_official_atom_denominator"] or r["student_publishable"]:
            raise ValueError("Uncertified page segment promoted")
        nodes.append(dict(id="SOURCE:"+r["segment_id"],track_hint=r["track_hint"],kind="PDFKIT_SOURCE_LINE_PARTITION",
                          printed_page=r["printed_page"],source_segment=r["segment_id"]))
    for r in y["records"]:
        s=prior.get(r["segment_id"])
        if not s or any(r[k]!=s[k] for k in ("printed_page","first_line","last_line","track_hint")):
            raise ValueError("Source triage has no exact parent")
        if r["source_pdf_sha256"] not in pdf or r["teacher_review"]!="REVIEW_PENDING" or r["official_atom_count"] is not None:
            raise ValueError("Triage cannot certify mathematical atoms")
        if r["student_publishable"]:raise ValueError("Triage leaked to student")
        nodes.append(dict(id="TRIAGE:"+r["segment_id"],kind=r["classification"],track_hint=r["track_hint"],
                          printed_page=r["printed_page"],source_span_sha256=r["span_sha256"],
                          editorial_action=r["next_action"],priority=r["priority"]))
        edges.append(dict(source="TRIAGE:"+r["segment_id"],parent="SOURCE:"+r["segment_id"],relation="SOURCE_LINES"))
    for r in z["records"]:
        parent=tri.get(r["source_segment_id"])
        if not parent or any(r[k]!=parent[k] for k in ("track_hint","printed_page")):
            raise ValueError("Unlinked editorial subspan")
        if r["parent_span_sha256"]!=parent["span_sha256"]:
            raise ValueError("Parent SHA mismatch")
        if not parent["first_line"]<=r["first_line"]<=r["last_line"]<=parent["last_line"]:
            raise ValueError("Subspan line extent escaped source")
        if r["official_atom_contribution"] is not None or r["teacher_review"]!="REVIEW_PENDING" or r["student_publishable"]:
            raise ValueError("Unreviewed editorial component certified")
        nodes.append(dict(id="SUBSPAN:"+r["id"],track_hint=r["track_hint"],kind=r["role"],
                          printed_page=r["printed_page"],source_span_sha256=r["local_source_subspan_sha256"],
                          source_segment_id=r["source_segment_id"],
                          author_paraphrase=r["project_authored_paraphrase"]))
        edges.append(dict(source="SUBSPAN:"+r["id"],parent="TRIAGE:"+r["source_segment_id"],relation="EDITORIAL_SPLIT"))
    for r in w["candidates"]:
        parent=sub.get(r["candidate_id"])
        if not parent or r["track_hint"]!=parent["track_hint"] or r["source_sha256"]!=parent["local_source_subspan_sha256"]:
            raise ValueError("Candidate not traceable to original source subspan")
        if r["official_atom_id"] is not None or r["source_certified"] or r["teacher_approved"] or r["student_publishable"]:
            raise ValueError("Project draft cannot become approved")
        if r["teacher_review"]!="REVIEW_PENDING" or not r["review_only_teacher_draft_ids"]:
            raise ValueError("Candidate has no tracked draft")
        if len(r["review_only_teacher_draft_ids"])!=r["review_only_teacher_draft_count"]:
            raise ValueError("Uncounted or duplicated editorial drafts")
        nodes.append(dict(id="CANDIDATE:"+r["candidate_id"],kind="LOCAL_MATH_TOPIC_CANDIDATE",
                          track_hint=r["track_hint"],source_sha256=r["source_sha256"],
                          teacher_draft_ids=r["review_only_teacher_draft_ids"],review_status="REVIEW_PENDING"))
        edges.append(dict(source="CANDIDATE:"+r["candidate_id"],parent="SUBSPAN:"+r["candidate_id"],relation="NOT_OFFICIAL_ATOM"))
    counts={}
    for t in TRACKS:
        s=x["tracks"][t];u=y["track_backlog"][t];v=w["by_track"][t]
        if s["official_atom_denominator"] is not None or u["official_atom_denominator"] is not None or v["official_denominator"] is not None:
            raise ValueError("Illegal known seven-track official denominator")
        q=dict(track=t,
            anchored_line_partition_segments=s["heuristic_segment_count"],
            heuristic_source_anchors=s["heuristic_anchor_count"],
            unanchored_editorial_triage_segments=u["editorial_segments"],
            high_priority_unresolved_triage=u["high_priority_unresolved"],
            subspan_editorial_components=z["project_track_counts"].get(t,0),
            local_candidate_topics=v["local_candidates"],
            local_candidate_topics_with_review_only_drafts=v["with_review_only_drafts"],
            teacher_approved=0,official_atom_denominator=None,official_coverage=None,
            status="CANDIDATE_INVENTORY_NOT_OFFICIAL_COVERAGE")
        for a,field,nodeset in [(q["anchored_line_partition_segments"],"SOURCE",x["segments"]),
             (q["unanchored_editorial_triage_segments"],"TRIAGE",y["records"]),
             (q["subspan_editorial_components"],"SUBSPAN",z["records"]),
             (q["local_candidate_topics"],"CANDIDATE",w["candidates"])]:
            if field=="SOURCE":n=sum(r["track_hint"]==t for r in nodeset)
            elif field=="TRIAGE":n=sum(r["track_hint"]==t for r in nodeset)
            elif field=="SUBSPAN":n=sum(r["track_hint"]==t for r in nodeset)
            else:n=sum(r["track_hint"]==t for r in nodeset)
            if a!=n:raise ValueError("Track "+t+" "+field+" count drift "+str((a,n)))
        if q["local_candidate_topics"]!=q["local_candidate_topics_with_review_only_drafts"]:
            raise ValueError("Previously linked candidate drafts lost")
        counts[t]=q
    if sum(v["anchored_line_partition_segments"] for v in counts.values())+x["tracks"]["ELECTIVE_GENERAL"]["heuristic_segment_count"]!=484:
        raise ValueError("484-page-partition conservation violated")
    if sum(v["local_candidate_topics"] for v in counts.values())!=26:
        raise ValueError("26 local candidates lost")
    general=y["track_backlog"].get("ELECTIVE_GENERAL",{})
    if general.get("editorial_segments")!=1 or general.get("official_atom_denominator") is not None:
        raise ValueError("Elective general scope cannot be silently absorbed into A–E")
    return dict(schema_version="kb-batch78-seven-track-provenance-v1",
        standard_version="2017年版2020年修订",source_pdf_sha256=x["source_pdf_sha256"],
        sources_sha256={k:sha(p) for k,p in SOURCES.items()},
        by_track=counts,general_elective_scope_triage=1,general_elective_source_segment_count=1,
        total_page_line_partitions=484,total_unanchored_editorial_triage=56,
        total_subspan_editorial_components=60,total_local_math_topic_candidates=26,
        local_candidate_topics_with_review_only_drafts=26,
        official_full_curriculum_atom_denominator=None,teacher_full_page_reviews=0,
        student_publishable_count=0,officially_certified_atom_count=0,
        edges=edges,nodes=nodes)
def markdown(data):
    lines=["# Batch78｜高中数学七轨来源到草案的可审核图谱",
      "","> 484来源区间、56未锚定分诊、60子片段、26局部主题候选是不同层级，不可相加成为官方知识点数。",
      "七轨官方知识原子分母均未知；选修总论单独保留，不冒充选修A–E任一已审核原子。",
      "", "| 课程轨道 | 来源区间 | 无锚定待审区间 | 子片段 | 局部主题 | 有待审稿 | 官方原子分母 |",
      "|---|---:|---:|---:|---:|---:|---|"]
    for k,v in data["by_track"].items():
        lines.append("| "+k+" | "+str(v["anchored_line_partition_segments"])+" | "+
                     str(v["unanchored_editorial_triage_segments"])+" | "+
                     str(v["subspan_editorial_components"])+" | "+str(v["local_candidate_topics"])+" | "+
                     str(v["local_candidate_topics_with_review_only_drafts"])+" | UNKNOWN |")
    lines+=["","- 课程来源、分诊、子片段和教师草案之间的完整边列表见JSON。",
      "- 无来源ID、跨轨SHA冲突、片段越界、伪造已审校/官方分母均拒绝。",
      "- 下一批必须逐页做数学实体与课程义务判断及跨页数学等价审查；未进行真人教师审查不得发布。"]
    return "\n".join(lines)+"\n"
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");arg=p.parse_args()
    result=build()
    for f,s in [(OUT,dump(result)),(MD,markdown(result))]:
        if arg.check:
            if not f.exists() or f.read_text(encoding="utf8")!=s:raise SystemExit("K00 evidence graph drift: "+str(f))
        else:f.write_text(s,encoding="utf8")
    print(json.dumps({k:{c:v[c] for c in ("anchored_line_partition_segments","unanchored_editorial_triage_segments","subspan_editorial_components","local_candidate_topics")} for k,v in result["by_track"].items()},ensure_ascii=False))
if __name__=="__main__":main()
