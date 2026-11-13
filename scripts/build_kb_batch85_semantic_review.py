#!/usr/bin/env python3
"""Batch85: 80 ORIGINAL source-specific interpretations; no certified math atoms."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_kb_batch84_semantic_review as B84

ROOT=Path(__file__).resolve().parents[1]
AUTHOR=ROOT/"curriculum/highschool_math/kb_batch85_semantic_authoring.json"
OUT=ROOT/"docs/evaluation/KB_BATCH85_SEMANTIC_COVERAGE.json"
MD=ROOT/"docs/evaluation/KB_BATCH85_SEMANTIC_COVERAGE.md"
COUNTS={"COMPULSORY":30,"SELECTIVE_COMPULSORY":25,
        "ELECTIVE_A":15,"ELECTIVE_B":10,
        "ELECTIVE_C":0,"ELECTIVE_D":0,"ELECTIVE_E":0}

def require(ok,why):
    if not ok:raise ValueError(why)
def load(p):return json.loads(Path(p).read_text(encoding="utf8"))
def dump(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n"

def build(auth=None,source=None,previous=None,verify_local_source=False):
    auth=load(AUTHOR) if auth is None else auth
    source=load(B84.B83.B81.SOURCE) if source is None else source
    previous=B84.build() if previous is None else previous
    require(type(auth) is dict and set(auth)=={
        "schema_version","standard_version","source_lineage","copyright_policy",
        "teacher_review","records"},"author schema/extra fields")
    require(auth["schema_version"]=="kb85-80-source-specific-editorial-v1"
            and auth["source_lineage"]=="MAC_PDFKIT_SHA_VERIFIED_ORIGINAL_SOURCE"
            and auth["copyright_policy"]=="ORIGINAL_PARAPHRASES_NO_SOURCE_PASSAGE"
            and auth["teacher_review"]=="REVIEW_PENDING"
            and auth["standard_version"]=="普通高中数学课程标准（2017年版2020年修订）",
            "source or unauthorized approval")
    require(source.get("source_pdf_sha256")==B84.B83.SOURCE_PDF_SHA
            and source.get("official_atom_denominator") is None
            and source.get("full_page_teacher_atomizations")==0
            and source.get("officially_certified_atom_count")==0
            and source.get("student_publishable_count")==0
            and sha256(B84.B83.B81.dump(source).encode()).hexdigest()==B84.B83.B81.SOURCE_QUEUE_SHA256,
            "source SHA or teacher-state spoofing")
    require(previous.get("schema_version")=="kb84-169-of-428-source-editorial-proposals-v1"
            and previous.get("cumulative_editorial_count")==169
            and previous.get("pending_editorial_count")==259
            and previous.get("teacher_approved")==0
            and previous.get("official_curriculum_atom_denominator") is None
            and previous.get("student_deep_content_published")==0,
            "prior source coverage or approval mutated")
    prior={r["review_id"] for r in B84.B83.B81.build()["rows"]}
    prior.update(r["review_id"] for r in load(B84.B83.AUTHOR)["records"])
    prior.update(r["review_id"] for r in load(B84.AUTHOR)["records"])
    require(len(prior)==169,"prior source anchor collision")
    queue=source["anchor_review_queue"]
    src={r["review_id"]:r for r in queue}
    require(len(queue)==len(src)==428,"frozen source count")
    by_source=Counter(r["track"] for r in queue)
    expected={tr:[r["review_id"] for r in queue
                  if r["track"]==tr and r["review_id"] not in prior][:n]
              for tr,n in COUNTS.items()}
    rows=auth["records"]
    require(type(rows) is list and len(rows)==80
            and all(type(r) is dict and set(r)==B84.FIELDS for r in rows),
            "author record schema and row count")
    require(len({r["review_id"] for r in rows})==80,"duplicate source anchor")
    bynew={tr:[] for tr in COUNTS}
    compiled=[]
    if verify_local_source:
        require(B84.B83.B81.LOCAL_PDF.is_file()
                and sha256(B84.B83.B81.LOCAL_PDF.read_bytes()).hexdigest()==B84.B83.SOURCE_PDF_SHA,
                "Mac original source PDF missing or hash changed")
        pages={int(p["printed_page"]):p["pdfkit_text_sha256"]
               for p in load(B84.B83.B81.PARTS)["pages"]}
    for r in rows:
        rid,tr=r["review_id"],r["track"]
        require(rid in src and rid not in prior and tr in COUNTS
                and src[rid]["track"]==tr,"source ID or track tamper")
        bynew[tr].append(rid)
        origin=src[rid]
        role=r["semantic_role_provisional"]
        require(role in B84.B83.ROLES
                and not(origin["kind"]=="MAJOR_NUMBER" and role!="CURRICULUM_HEADING")
                and not(origin["kind"]=="CIRCLED_ITEM" and role=="CURRICULUM_HEADING"),
                "source kind role mismatch")
        units=r["possible_math_units_for_teacher_split"]
        require(type(units) is list and len(units)<=5
                and all(type(u) is str and len(u)>=6 for u in units)
                and len(units)==len(set(units)),
                "invalid suggested math units")
        require((role=="CURRICULUM_HEADING" and not units)
                or (role in ("MATHEMATICAL_REQUIREMENT","MIXED_CLAUSE") and bool(units))
                or (role in ("COMPETENCY_REQUIREMENT","APPLICATION_CONTEXT")),
                "heading promoted to math unit or missing math requirements")
        require(type(r["original_editorial_paraphrase"]) is str
                and len(r["original_editorial_paraphrase"])>=20
                and type(r["condition_or_scope_caution"]) is str
                and len(r["condition_or_scope_caution"])>=7,
                "missing source-specific interpretation and condition")
        require(r["teacher_confirmed"] is False
                and r["student_publishable"] is False
                and r["official_atom_count"] is None
                and r["cross_track_equivalence"]=="NOT_ADJUDICATED",
                "teacher/official/student authority spoof")
        if verify_local_source:
            page,line=origin["printed_page"],origin["pdfkit_line"]
            fn=B84.B83.B81.LOCAL_LINES/f"kb56_page_{page}.txt"
            require(fn.is_file() and page in pages,"Mac PDFKit source page absent")
            data=fn.read_bytes()
            require(sha256(data).hexdigest()==origin["source_page_pdfkit_sha256"]==pages[page],
                    "PDFKit source page content changed")
            source_lines=data.decode("utf8").splitlines()
            require(1<=line<=len(source_lines)
                    and sha256(source_lines[line-1].encode()).hexdigest()==origin["source_line_sha256"],
                    "PDFKit source line changed")
        compiled.append({
            **r,"source_pdf_sha256":B84.B83.SOURCE_PDF_SHA,
            "source_page_pdfkit_sha256":origin["source_page_pdfkit_sha256"],
            "source_line_sha256":origin["source_line_sha256"],
            "printed_page":origin["printed_page"],"pdfkit_line":origin["pdfkit_line"],
            "source_kind":origin["kind"],"source_parent_segment":origin["parent_segment"],
            "review_status":"REVIEW_PENDING","teacher_approved":False,
            "math_certification":"NOT_FORMALLY_VERIFIED",
            "student_authoritative_index_eligible":False})
    require(all(bynew[tr]==expected[tr] for tr in COUNTS),
            "source-specific selection order drift")
    by_track={
        tr:{"source_review_anchor_denominator":by_source[tr],
            "editorially_paraphrased_source_anchors":previous["by_track"][tr]["editorially_paraphrased_source_anchors"]+len(bynew[tr]),
            "without_original_semantic_paraphrase":by_source[tr]-previous["by_track"][tr]["editorially_paraphrased_source_anchors"]-len(bynew[tr]),
            "official_mathematical_atom_denominator":None,
            "teacher_full_page_atomization":0,"student_approved_math_atoms":0}
        for tr in COUNTS}
    require(sum(r["source_review_anchor_denominator"] for r in by_track.values())==428
            and sum(r["editorially_paraphrased_source_anchors"] for r in by_track.values())==249
            and sum(r["without_original_semantic_paraphrase"] for r in by_track.values())==179,
            "coverage conservation failure")
    return {
        "schema_version":"kb85-249-of-428-source-editorial-proposals-v1",
        "standard_version":auth["standard_version"],
        "source_pdf_sha256":B84.B83.SOURCE_PDF_SHA,
        "source_queue_sha256":B84.B83.B81.SOURCE_QUEUE_SHA256,
        "author_sha256":sha256(dump(auth).encode()).hexdigest(),
        "source_review_denominator":428,"previous_editorial_count":169,
        "new_editorial_count":80,"cumulative_editorial_count":249,
        "pending_editorial_count":179,
        "candidate_splits_not_deduplicated":sum(len(x["possible_math_units_for_teacher_split"]) for x in rows),
        "official_curriculum_atom_denominator":None,"full_page_teacher_reviews":0,
        "teacher_approved":0,"student_deep_content_published":0,
        "by_track":by_track,
        "new_by_role":dict(Counter(x["semantic_role_provisional"] for x in rows)),
        "new_rows":compiled,"student_index_includes_unreviewed_material":False}

def markdown(d):
    lines=["# Batch85｜课标原始来源逐行原创语义分诊（项目内部，待审）","",
           "**249/428表示来源锚点项目编辑工作进度，绝非正式官方知识原子覆盖率或完整讲义数量。**",
           "课标PDF保留在Mac；本矩阵仅保留源SHA/页行索引与原创释义。",
           "教师全页原子化0/61，批准0，学生正式深度发布0；七轨官方原子分母未知。","",
           "| 轨道 | 来源锚点 | 已编辑 | 尚缺编辑 | 官方原子分母 |",
           "|---|---:|---:|---:|---|"]
    for k,v in d["by_track"].items():
        lines.append(f'| {k} | {v["source_review_anchor_denominator"]} | '
                     f'{v["editorially_paraphrased_source_anchors"]} | '
                     f'{v["without_original_semantic_paraphrase"]} | 未知 |')
    lines += ["",f'本批新增{d["new_editorial_count"]}条原创逐行解释；未跨轨去重候选主题{d["candidate_splits_not_deduplicated"]}个。',
              "章节标题不算知识原子，机器检查不替代真实教师审核。","",
              "| 来源锚点 | 轨道 | 角色 | 原创语义分析 | 适用条件与失效风险 |",
              "|---|---|---|---|---|"]
    for r in d["new_rows"]:
        lines.append(f'| {r["review_id"]} | {r["track"]} | {r["semantic_role_provisional"]} | '
                     f'{r["original_editorial_paraphrase"]} | {r["condition_or_scope_caution"]} |')
    return "\n".join(lines)+"\n"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local-source",action="store_true")
    opts=p.parse_args()
    data=build(verify_local_source=opts.verify_local_source)
    for path,value in ((OUT,dump(data)),(MD,markdown(data))):
        if opts.check:require(path.is_file() and path.read_text(encoding="utf8")==value,
                              "generated artifact drift: "+str(path))
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(value,encoding="utf8")
    print(f'Batch85: +80 reviewed anchors, {data["cumulative_editorial_count"]}/428; {data["pending_editorial_count"]} pending; official atoms unknown')
if __name__=="__main__":main()
