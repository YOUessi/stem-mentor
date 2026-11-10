#!/usr/bin/env python3
"""Batch86 K00/K01: 89 ORIGINAL source-specific editorials (not official atoms).

Mac may verify the copyrighted local source PDF and frozen PDFKit-extracted
page-line SHA. GitHub stores *only* provenance hashes and original paraphrases.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_kb_batch85_semantic_review as B85

ROOT=Path(__file__).resolve().parents[1]
AUTHOR=ROOT/"curriculum/highschool_math/kb_batch86_semantic_authoring.json"
OUT=ROOT/"docs/evaluation/KB_BATCH86_SEMANTIC_COVERAGE.json"
MD=ROOT/"docs/evaluation/KB_BATCH86_SEMANTIC_COVERAGE.md"
COUNTS={"COMPULSORY":32,"SELECTIVE_COMPULSORY":25,"ELECTIVE_A":16,"ELECTIVE_B":16,
        "ELECTIVE_C":0,"ELECTIVE_D":0,"ELECTIVE_E":0}
SCHEMA="kb86-338-of-428-source-editorial-proposals-v1"
EDITORIAL_SCHEMA="kb86-89-source-specific-editorial-v1"

def require(ok,msg):
    if not ok:raise ValueError(msg)
def load(p):return json.loads(Path(p).read_text(encoding="utf8"))
def dump(d):return json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n"

def build(auth=None,source=None,previous=None,verify_local_source=False):
    auth=load(AUTHOR) if auth is None else auth
    source=load(B85.B84.B83.B81.SOURCE) if source is None else source
    previous=B85.build() if previous is None else previous
    require(type(auth) is dict and set(auth)=={
        "schema_version","standard_version","source_lineage","copyright_policy",
        "teacher_review","records"},"unauthorized authoring field")
    require(auth["schema_version"]==EDITORIAL_SCHEMA
        and auth["standard_version"]=="普通高中数学课程标准（2017年版2020年修订）"
        and auth["source_lineage"]=="MAC_PDFKIT_SHA_VERIFIED_ORIGINAL_SOURCE"
        and auth["copyright_policy"]=="ORIGINAL_PARAPHRASES_NO_SOURCE_PASSAGE"
        and auth["teacher_review"]=="REVIEW_PENDING","copyright or false review state")
    require(previous["schema_version"]=="kb85-249-of-428-source-editorial-proposals-v1"
        and previous["cumulative_editorial_count"]==249
        and previous["pending_editorial_count"]==179
        and previous["teacher_approved"]==0
        and previous["official_curriculum_atom_denominator"] is None
        and previous["full_page_teacher_reviews"]==0
        and previous["student_deep_content_published"]==0,
        "previous review approval or coverage drift")
    require(source.get("source_pdf_sha256")==B85.B84.B83.SOURCE_PDF_SHA
        and sha256(B85.B84.B83.B81.dump(source).encode()).hexdigest()==B85.B84.B83.B81.SOURCE_QUEUE_SHA256
        and source.get("official_atom_denominator") is None
        and source.get("full_page_teacher_atomizations")==0
        and source.get("officially_certified_atom_count")==0
        and source.get("student_publishable_count")==0,"source queue or teacher authority spoofing")
    queue=source["anchor_review_queue"]
    require(len(queue)==428 and len({x["review_id"] for x in queue})==428,
            "source denominator changed")
    earlier={r["review_id"] for r in B85.B84.B83.B81.build()["rows"]}
    for p in (B85.B84.B83.AUTHOR,B85.B84.AUTHOR,B85.AUTHOR):
        earlier.update(r["review_id"] for r in load(p)["records"])
    require(len(earlier)==249,"earlier source collision")
    src={x["review_id"]:x for x in queue}
    selected={t:[x["review_id"] for x in queue
                  if x["track"]==t and x["review_id"] not in earlier][:n]
              for t,n in COUNTS.items()}
    require(type(auth["records"]) is list and len(auth["records"])==89
        and all(type(r) is dict and set(r)==B85.B84.FIELDS
                for r in auth["records"]),
            "source author row field or count")
    require(len({r["review_id"] for r in auth["records"]})==89,"duplicate source review ID")
    if verify_local_source:
        local=B85.B84.B83.B81.LOCAL_PDF
        require(local.is_file() and sha256(local.read_bytes()).hexdigest()==B85.B84.B83.SOURCE_PDF_SHA,
                "Mac source PDF unavailable or drifted")
        pages={p["printed_page"]:p["pdfkit_text_sha256"] for p in load(B85.B84.B83.B81.PARTS)["pages"]}
    collected={t:[] for t in COUNTS};compiled=[]
    candidates=[]
    for r in auth["records"]:
        rid,tr=r["review_id"],r["track"]
        require(rid not in earlier and rid in src and tr in COUNTS and src[rid]["track"]==tr,
                "source ID duplicate, missing, or track spoof")
        o=src[rid]
        collected[tr].append(rid)
        role=r["semantic_role_provisional"]
        require(role in B85.B84.B83.ROLES
                and not(o["kind"]=="MAJOR_NUMBER" and role!="CURRICULUM_HEADING")
                and not(o["kind"]=="CIRCLED_ITEM" and role=="CURRICULUM_HEADING"),
                "source kind mismatched to semantic role")
        units=r["possible_math_units_for_teacher_split"]
        require(type(units) is list and len(units)<=5
            and all(type(u) is str and len(u)>=6 for u in units)
            and len(units)==len(set(units)),
            "math split candidate shape or duplicate")
        require((role=="CURRICULUM_HEADING" and not units)
                or (role in ("MATHEMATICAL_REQUIREMENT","MIXED_CLAUSE") and bool(units))
                or role in ("COMPETENCY_REQUIREMENT","APPLICATION_CONTEXT"),
                "math units assigned to a heading or math requirement left empty")
        require(type(r["original_editorial_paraphrase"]) is str
            and len(r["original_editorial_paraphrase"])>=24
            and type(r["condition_or_scope_caution"]) is str
            and len(r["condition_or_scope_caution"])>=15,
            "too little source-specific original interpretation or boundary")
        require(r["cross_track_equivalence"]=="NOT_ADJUDICATED"
                and r["official_atom_count"] is None
                and r["teacher_confirmed"] is False
                and r["student_publishable"] is False,
                "unsanctioned formal math claim / teacher certification")
        if verify_local_source:
            page=o["printed_page"]
            raw=Path("/private/tmp",f"kb56_page_{page}.txt").read_bytes()
            require(sha256(raw).hexdigest()==pages[page]==o["source_page_pdfkit_sha256"],
                    "page original PDFKit SHA drift")
            lines=raw.decode("utf8").splitlines()
            require(1<=o["pdfkit_line"]<=len(lines)
                    and sha256(lines[o["pdfkit_line"]-1].encode()).hexdigest()==o["source_line_sha256"],
                    "anchored source line SHA drift")
            # This is not an OCR or inferred page offset; it checks the actual frozen Mac PDFKit line.
        compiled.append({**r,
            "source_pdf_sha256":B85.B84.B83.SOURCE_PDF_SHA,
            "source_page_pdfkit_sha256":o["source_page_pdfkit_sha256"],
            "source_line_sha256":o["source_line_sha256"],
            "printed_page":o["printed_page"],"pdfkit_line":o["pdfkit_line"],
            "source_kind":o["kind"],"source_parent_segment":o["parent_segment"],
            "review_status":"REVIEW_PENDING","teacher_approved":False,
            "student_authoritative_index_eligible":False,
            "math_certification":"NOT_FORMALLY_VERIFIED"})
        for ix,unit in enumerate(units,1):
            candidates.append({"provisional_id":f'{rid}-C{ix:02d}',"proposed_topic":unit,
                "source_review_id":rid,"track":tr,
                "cross_page_equivalence":"NOT_ADJUDICATED",
                "official_atom_id":None,"prerequisite_certification":"NOT_EVALUATED",
                "complete_deep_lesson_certified":False,"teacher_approved":False,
                "student_publishable":False})
    require(all(collected[tr]==selected[tr] for tr in COUNTS),
            "source selection order / track incompleteness")
    totals=Counter(x["track"] for x in queue)
    bytrack={t:{"source_review_anchor_denominator":totals[t],
                "editorially_paraphrased_source_anchors":
                    previous["by_track"][t]["editorially_paraphrased_source_anchors"]+len(collected[t]),
                "without_original_semantic_paraphrase":
                    totals[t]-previous["by_track"][t]["editorially_paraphrased_source_anchors"]-len(collected[t]),
                "official_mathematical_atom_denominator":None,
                "teacher_full_page_atomization":0,"student_approved_math_atoms":0}
             for t in COUNTS}
    require(sum(x["editorially_paraphrased_source_anchors"] for x in bytrack.values())==338
            and sum(x["without_original_semantic_paraphrase"] for x in bytrack.values())==90
            and sum(x["source_review_anchor_denominator"] for x in bytrack.values())==428,
            "bad coverage conservation")
    return {
        "schema_version":SCHEMA,"standard_version":auth["standard_version"],
        "source_pdf_sha256":B85.B84.B83.SOURCE_PDF_SHA,
        "source_queue_sha256":B85.B84.B83.B81.SOURCE_QUEUE_SHA256,
        "author_sha256":sha256(dump(auth).encode()).hexdigest(),
        "source_review_denominator":428,"previous_editorial_count":249,
        "new_editorial_count":89,"cumulative_editorial_count":338,
        "pending_editorial_count":90,
        "new_provisional_candidates":len(candidates),
        "provisional_candidates_not_deduplicated":candidates,
        "pending_anchor_ids_by_track":{
            tr:[x["review_id"] for x in queue
                if x["track"]==tr and x["review_id"] not in earlier
                and x["review_id"] not in {r["review_id"] for r in compiled}]
            for tr in COUNTS},
        "official_curriculum_atom_denominator":None,"full_page_teacher_reviews":0,
        "teacher_approved":0,"student_deep_content_published":0,
        "student_index_includes_unreviewed_material":False,
        "by_track":bytrack,
        "new_by_role":dict(Counter(r["semantic_role_provisional"] for r in compiled)),
        "new_rows":compiled}

def markdown(d):
    rows=["# Batch86｜数学课程来源逐行语义审查和未裁决候选","",
          "本批 **89项原始课标锚点原创释义**，累计338/428，仍有90项未解释。",
          "**428是来源锚点数，不是官方数学知识原子总数。**",
          "本批暂列知识主题也未完成跨页、跨轨去重，更未由真实教师逐页审定。",
          "源PDF仅存在Mac；不在仓库保存受版权保护的课标原文。",
          "老师全页原子化0/61、真实教师批准0、正式学生深度发布0。","",
          "| 轨道 | 来源锚点 | 编辑释义 | 尚无释义 | 官方原子分母 |",
          "|---|---:|---:|---:|---|"]
    for tr,x in d["by_track"].items():
        rows.append(f'| {tr} | {x["source_review_anchor_denominator"]} | {x["editorially_paraphrased_source_anchors"]} | {x["without_original_semantic_paraphrase"]} | 未知 |')
    rows+=["",f'本批可供后续人工拆分、去重的非官方候选主题：{d["new_provisional_candidates"]}，全部待审。',"",
           "| 来源 | 轨道 | 临时语义类型 | 原创解析 | 前提与风险 |",
           "|---|---|---|---|---|"]
    for r in d["new_rows"]:
        rows.append(f'| {r["review_id"]} | {r["track"]} | {r["semantic_role_provisional"]} | {r["original_editorial_paraphrase"]} | {r["condition_or_scope_caution"]} |')
    return "\n".join(rows)+"\n"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local-source",action="store_true")
    a=p.parse_args()
    d=build(verify_local_source=a.verify_local_source)
    for path,v in ((OUT,dump(d)),(MD,markdown(d))):
        if a.check:require(path.exists() and path.read_text(encoding="utf8")==v,
                           "generated coverage artifact drift "+str(path))
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(v,encoding="utf8")
    print(f'Batch86 source: +89, {d["cumulative_editorial_count"]}/428, {d["pending_editorial_count"]} pending; official math atoms UNKNOWN')
if __name__=="__main__":main()
