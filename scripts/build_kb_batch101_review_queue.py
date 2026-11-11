#!/usr/bin/env python3
"""Build an explicitly NON-AUTHORITATIVE source-locked K00/K01/K08 teacher review queue.

This creates ranked *candidates* for 134 unpaired provisional themes and 172
textual prerequisites, plus a page-by-page audit of 61 source pages.
Scores measure character overlap, never mathematical implication/equivalence.
No suggested relation or prerequisite is placed in the student graph.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "backend")]
import build_kb_batch93_candidate_triage as B93
from app.deep_knowledge import DeepLesson

REGISTRY = ROOT / "curriculum/highschool_math/k00_batch61_source_anchor_registry.json"
PREV = ROOT / "docs/evaluation/KB_BATCH92_SOURCE_RELATIONS.json"
SOURCE = B93.SOURCES
OUT = ROOT / "docs/evaluation/KB_BATCH101_REVIEW_QUEUE.json"
MD = ROOT / "docs/evaluation/KB_BATCH101_REVIEW_QUEUE.md"
LESSONS = [ROOT / f"knowledge/deep/v1/batch{n}_deep_scope_{size}.json"
           for n, size in ((94,14),(95,16),(96,12),(97,12),(98,12))]
LESSONS.append(ROOT / "knowledge/deep/v1/batch100_deep_source_20.json")
TRACKS = tuple(B93.TRACKS)

def require(ok, message):
    if not ok:
        raise ValueError(message)

def source_read(path):
    return B93.read(path)

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def grams(s):
    s = re.sub(r"[\\s，。；：、（）()\[\]【】《》/\\\\·_\-]+", "", s.casefold())
    return {s[i:i+2] for i in range(len(s)-1)} or {s}

def lexical(a,b):
    aa,bb=grams(a),grams(b)
    return round(len(aa & bb) / len(aa | bb), 5)

def audit_source_pages(reg=None):
    reg = source_read(REGISTRY) if reg is None else reg
    rows=reg["rows"]
    counts=reg["page_line_counts"]
    require(len(rows)==428 and len(counts)==61, "frozen source page/anchor census drift")
    require(reg["includes_copyright_passages"] is False, "cannot publish copyrighted source excerpts")
    page_index=defaultdict(list)
    seen_page_lines=set()
    page_digests={}
    for r in rows:
        page=str(r["printed_page"])
        line=r["pdfkit_line"]
        require(page in counts and type(line) is int and 1 <= line <= counts[page],
                "source anchor outside enumerated page/line census")
        require((page,line) not in seen_page_lines,"duplicate source page/line anchor")
        seen_page_lines.add((page,line))
        prior_digest=page_digests.setdefault(page,r["source_page_pdfkit_sha256"])
        require(prior_digest==r["source_page_pdfkit_sha256"],
                "contradictory PDF extraction digest on same source page")
        require(r["track_hint"] in TRACKS and r["teacher_review"]=="REVIEW_PENDING"
                and r["certified_official_atom"] is False and r["student_publishable"] is False
                and r["full_page_review_completed"] is False,
                "source page review authority drift")
        require(len(r["source_line_sha256"])==64 and len(r["source_page_pdfkit_sha256"])==64,
                "invalid source line/page digest")
        page_index[str(r["printed_page"])].append(r)
    # The page map may be PDF physical page identifiers and includes every recognized page.
    result=[]
    for p,lines in sorted(counts.items(),key=lambda x:int(x[0])):
        relevant=page_index.get(p,[])
        result.append({
          "printed_page":int(p), "pdfkit_line_count":lines,
          "project_anchor_count":len(relevant),
          "source_tracks":[*sorted({x["track_hint"] for x in relevant})],
          "full_page_human_atomization":"NOT_PERFORMED",
          "official_atom_count":None, "missing_coverage_reason":"NO_COMPLETE_HUMAN_PAGE_REVIEW",
          "teacher_approved":0, "student_publishable":False})
    require(len(result)==61, "all 61 course-source pages must be represented")
    return result

def read_lessons():
    lessons={}
    for f in LESSONS:
        payload=source_read(f)
        require(type(payload) is list, "lesson file shape invalid")
        for x in payload:
            doc=DeepLesson.model_validate(x)
            require(doc.id not in lessons and doc.review.status=="REVIEW_PENDING"
                    and doc.teacher_solution_visibility=="TEACHER_ONLY"
                    and not doc.prerequisite_lesson_ids,
                    "prerequisite graph or teacher approval unexpectedly changed")
            lessons[doc.id]=doc
    require(len(lessons)==86, "historical 86 teacher pending deep lessons changed")
    require(sum(len(d.prerequisites) for d in lessons.values())==172,
            "historical 172 textual prerequisites changed")
    return lessons

def semantic_queue(source=None,previous=None):
    source=source_read(SOURCE) if source is None else source
    previous=source_read(PREV) if previous is None else previous
    originals=source["provisional_candidate_backlog"]
    require(B93.candidate_snapshot_sha256(originals)==B93.FROZEN_BATCH89_CANDIDATES_SHA256,
            "source candidates no longer equal the frozen checksum")
    ids={r["candidate_id"]:r for r in originals}
    require(len(ids)==300 and len(originals)==300, "duplicate/vanished source candidates")
    outstanding=previous["remaining_unpaired_candidate_ids"]
    require(len(outstanding)==len(set(outstanding))==134
            and all(x in ids for x in outstanding), "unpaired queue source drift")
    already=set(ids)-set(outstanding)
    require(len(already)==166, "previously compared source census drift")
    out=[]
    for src_id in outstanding:
        row=ids[src_id]
        require(row["review_status"]=="REVIEW_PENDING" and row["teacher_approval"] is None
                and row["official_math_atom_id"] is None
                and not row["student_authoritative_index_eligible"], "source authority drift")
        ranking=sorted((
            (lexical(row["provisional_topic"], ids[k]["provisional_topic"]), k)
            for k in already if ids[k]["track"]==row["track"]
        ),key=lambda x:(-x[0],x[1]))
        # Fallback to other tracks, but never certify cross-track equivalence.
        if len(ranking)<3:
            ranking += sorted(((lexical(row["provisional_topic"], ids[k]["provisional_topic"]),k)
                for k in already if ids[k]["track"]!=row["track"]),
                key=lambda x:(-x[0],x[1]))
        picks=[]
        for score,k in ranking:
            if score < 0.12: continue  # Weak coincidences are NOT candidate evidence.
            if len(picks)==3: break
            target=ids[k]
            picks.append({
                "candidate_id":k,"track":target["track"],"topic":target["provisional_topic"],
                "source_line_sha256":target["source_line_sha256"],
                "lexical_overlap_score":score,
                "cross_track":target["track"]!=row["track"],
                "equivalence_status":"UNREVIEWED_NOT_CERTIFIED",
            })
        require(len(picks)<=3 and len({p["candidate_id"] for p in picks})==len(picks),
                "duplicate relation reviewer candidates")
        out.append({
            "source_candidate_id":src_id,"source_topic":row["provisional_topic"],
            "source_track":row["track"],"source_line_sha256":row["source_line_sha256"],
            "suggestions":picks,
            "candidate_signal":"LEXICAL_NEIGHBOR_UNVERIFIED" if picks else "MANUAL_SEARCH_REQUIRED",
            "pairwise_semantic_review":"NOT_PERFORMED",
            "human_review_required":True,"official_atom_id":None,
            "teacher_approved":False,"student_publishable":False,
            "math_equivalence_certified":False,
        })
    return out

def prerequisite_queue(lessons=None):
    lessons=read_lessons() if lessons is None else lessons
    out=[]
    for lesson in sorted(lessons.values(),key=lambda d:d.id):
        for i,text in enumerate(lesson.prerequisites,1):
            options=sorted(
                ((lexical(text,other.title),other.id,other.title)
                 for other in lessons.values() if other.id!=lesson.id),
                key=lambda x:(-x[0],x[1]))
            top=[o for o in options if o[0]>=0.16][:3]
            require(len(top)<=3, "candidate list overflow")
            out.append({
               "queue_id":f"{lesson.id}#pre{i}",
               "lesson_id":lesson.id,"lesson_title":lesson.title,
               "textual_prerequisite":text,
               "suggestions":[{
                  "lesson_id":k,"lesson_title":title,"lexical_overlap_score":score,
                  "edge_type":"SUGGESTION_NOT_RESOLVED",
                  "mathematical_implication_verified":False,
               } for score,k,title in top],
               "resolution":"EDITORIAL_CANDIDATES_ONLY" if top else "MANUAL_DISCOVERY_REQUIRED",
               "approved_edge_id":None,"teacher_approved":False,
               "student_graph_eligible":False,
            })
    require(len(out)==172 and len(set(x["queue_id"] for x in out))==172,
            "prerequisite note conservation failed")
    return out

def validate_report(report):
    require(report["official_curriculum_atom_denominator"] is None
            and all(x is None for x in report["official_atom_denominators_by_track"].values()),
            "fake official seven-track denominator")
    require(report["teacher_approved"]==report["student_published"]==0,
            "unapproved material promoted")
    require(report["remaining_unpaired_provisional_topics"]==134
            and report["unresolved_textual_prerequisites"]==172
            and report["human_atomized_pages"]==0,"false coverage closure")
    seen=set()
    for row in report["semantic_pair_reviewer_queue"]:
        require(row["source_candidate_id"] not in seen
                and not row["student_publishable"] and not row["teacher_approved"]
                and row["official_atom_id"] is None
                and row["pairwise_semantic_review"]=="NOT_PERFORMED"
                and not row["math_equivalence_certified"],
                "semantic queue authority or duplication failure")
        seen.add(row["source_candidate_id"])
        require(len(row["suggestions"])<=3 and
            row["candidate_signal"] == ("LEXICAL_NEIGHBOR_UNVERIFIED" if row["suggestions"] else "MANUAL_SEARCH_REQUIRED")
            and all(
            x["lexical_overlap_score"]>=0.12 and
            x["equivalence_status"]=="UNREVIEWED_NOT_CERTIFIED" for x in row["suggestions"]),
            "unreviewed semantic suggestion was certified")
    require(len(seen)==134, "semantic queue completeness failure")
    seen=set()
    for r in report["text_prerequisite_reviewer_queue"]:
        require(r["queue_id"] not in seen
                and r["approved_edge_id"] is None and not r["teacher_approved"]
                and not r["student_graph_eligible"]
                and r["resolution"] in {"MANUAL_DISCOVERY_REQUIRED","EDITORIAL_CANDIDATES_ONLY"},
                "unreviewed prerequisite promoted")
        seen.add(r["queue_id"])
        require(len(r["suggestions"])<=3 and
            r["resolution"] == ("EDITORIAL_CANDIDATES_ONLY" if r["suggestions"] else "MANUAL_DISCOVERY_REQUIRED")
            and all(
            o["lexical_overlap_score"]>=0.16 and o["lesson_id"]!=r["lesson_id"]
            and not o["mathematical_implication_verified"] for o in r["suggestions"]),
            "self-link or unverified math claim promoted")
    require(len(seen)==172, "prerequisite note missing")

def build():
    pages=audit_source_pages()
    semantic=semantic_queue()
    prereq=prerequisite_queue()
    bytrack=Counter(r["source_track"] for r in semantic)
    return {
      "schema_version":"kb101-fail-closed-review-workqueue-v1",
      "standard_version":"普通高中数学课程标准（2017年版2020年修订）",
      "source_snapshots_sha256":{str(p.relative_to(ROOT)):digest(p)
         for p in [REGISTRY,SOURCE,PREV,*LESSONS]},
      "page_census":61,"source_anchor_census":428,
      "provisional_project_theme_census":300,"previously_editorially_paired_theme_census":166,
      "remaining_unpaired_provisional_topics":134,
      "unresolved_textual_prerequisites":172,
      "deep_drafts_teacher_pending":86,
      "human_atomized_pages":0,"official_curriculum_atom_denominator":None,
      "official_atom_denominators_by_track":{track:None for track in TRACKS},
      "teacher_approved":0,"student_published":0,
      "unpaired_by_track":dict(sorted(bytrack.items())),
      "recommendation_scoring":"CHARACTER_BIGRAM_JACCARD_HEURISTIC_NOT_MATHEMATICAL_PROOF",
      "min_lexical_signal_semantic":0.12, "min_lexical_signal_prerequisite":0.16,
      "semantic_manual_search_required":sum(not x["suggestions"] for x in semantic),
      "prerequisite_manual_search_required":sum(not x["suggestions"] for x in prereq),
      "page_evidence":pages,
      "semantic_pair_reviewer_queue":semantic,
      "text_prerequisite_reviewer_queue":prereq,
    }

def markdown(x):
    s=["# Batch101｜K00/K01/K08未决语义与先修人工复核队列","",
       "**审核边界：** 所有排名都是文字二元组重叠的编辑候选，不是数学等价、正式原子合并或先修关系认证。学生权威图谱仍为0条新增边。","",
       "|审查任务|数量|真实完成状态|","|---|---:|---|",
       "|课程来源逐页核查|61|0份完整教师逐页原子化|",
       "|来源证据锚点|428|项目锚点，不是官方知识原子|",
       "|临时主题|300|不能当作七轨官方分母|",
       "|临时主题待成对语义裁决|134|全部建候选队列，仍待审核|",
       "|文本先修说明|172|全部建候选队列，仍未形成正式边|",
       "|深度讲义草案|86|全部REVIEW_PENDING|",
       f"|无可信词面邻居的主题|{x['semantic_manual_search_required']}|人工领域检索，不强行匹配|",
       f"|无可信词面邻居的先修|{x['prerequisite_manual_search_required']}|人工领域检索，不强行构图|","",
       "|轨道|待语义裁决临时标签|官方原子分母|","|---|---:|---|"]
    for track in TRACKS:
        s.append(f"|{track}|{x['unpaired_by_track'].get(track,0)}|UNKNOWN|")
    s+=["","## 134项语义比较待复核候选","",
        "|待比较标签|主题|建议比较标签/相似度（仅词面）|","|---|---|---|"]
    for a in x["semantic_pair_reviewer_queue"]:
        v=", ".join(f"{z['candidate_id']}({z['lexical_overlap_score']:.2f})"
                    for z in a["suggestions"]) or "MANUAL_SEARCH_REQUIRED"
        s.append(f"|{a['source_candidate_id']}|{a['source_topic'].replace('|','／')}|{v}|")
    s+=["","## 172条文本先修待复核候选","",
        "|原讲义|先修文字|候选目标讲义ID/重叠得分|","|---|---|---|"]
    for a in x["text_prerequisite_reviewer_queue"]:
        v=", ".join(f"{z['lesson_id']}({z['lexical_overlap_score']:.2f})"
                    for z in a["suggestions"]) or "MANUAL_DISCOVERY_REQUIRED"
        s.append(f"|{a['lesson_id']}|{a['textual_prerequisite'].replace('|','／')}|{v}|")
    s+=["","## 禁止自动提升的发布门槛","",
        "任何候选都必须由教师核对定义域、假设、是否充要、跨轨适用范围、前置循环与引用证据。",
        "完整61页逐页原子化尚未实施，官方七轨原子分母全部UNKNOWN。不能把0条未匹配或0个主题当作官方覆盖完毕。",
        "下一批：逐组补充人工数学区分意见，真实完成来源全文与先修边审核，补齐尚缺的教学单元、严格边界测试和冻结集。",""]
    return "\n".join(s)

def run(check=False):
    x=build()
    validate_report(x)
    outputs={OUT:json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n",
             MD:markdown(x)}
    for path,value in outputs.items():
        if check:
            require(path.read_text(encoding="utf8")==value,"artifact/source drift: "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(value,encoding="utf8")
    print("BATCH101 REVIEW QUEUE pages=61 anchors=428 themes=134 prereqs=172 approved=0 check",check)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    run(parser.parse_args().check)
