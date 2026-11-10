#!/usr/bin/env python3
"""K00/K01 Batch87: all 428 SOURCE ANCHORS have editorials; official atom denominator UNKNOWN.

Only the Mac can verify original copyrighted syllabus PDFKit page/line hashes.
No copied source passage is ever written to repository outputs.
"""
from __future__ import annotations
import argparse,json,sys,hashlib
from collections import Counter,defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_kb_batch86_semantic_review as B86
ROOT=Path(__file__).resolve().parents[1]
AUTHOR=ROOT/"curriculum/highschool_math/kb_batch87_semantic_authoring.json"
OUT=ROOT/"docs/evaluation/KB_BATCH87_SEMANTIC_COVERAGE.json"
MD=ROOT/"docs/evaluation/KB_BATCH87_SEMANTIC_COVERAGE.md"
SCHEMA="kb87-428-of-428-source-anchor-editorial-proposals-v1"
AUTHOR_SCHEMA="kb87-90-source-specific-editorial-v1"
EXPECTED={"COMPULSORY":43,"SELECTIVE_COMPULSORY":19,"ELECTIVE_A":11,
          "ELECTIVE_B":17,"ELECTIVE_C":0,"ELECTIVE_D":0,"ELECTIVE_E":0}
def require(cond,msg):
    if not cond:raise ValueError(msg)
def load(p):return json.loads(Path(p).read_text(encoding="utf8"))
def dump(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2)+"\n"
def build(auth=None,source=None,previous=None,verify_local_source=False):
    auth=load(AUTHOR) if auth is None else auth
    source=load(B86.B85.B84.B83.B81.SOURCE) if source is None else source
    previous=B86.build() if previous is None else previous
    require(type(auth) is dict and set(auth)=={
        "schema_version","standard_version","source_lineage","copyright_policy",
        "teacher_review","records"},"authoring schema changed")
    require(auth["schema_version"]==AUTHOR_SCHEMA
        and auth["standard_version"]=="普通高中数学课程标准（2017年版2020年修订）"
        and auth["source_lineage"]=="MAC_PDFKIT_SHA_VERIFIED_ORIGINAL_SOURCE"
        and auth["copyright_policy"]=="ORIGINAL_PARAPHRASES_NO_SOURCE_PASSAGE"
        and auth["teacher_review"]=="REVIEW_PENDING","source/approval spoofing")
    require(previous["schema_version"]=="kb86-338-of-428-source-editorial-proposals-v1"
        and previous["cumulative_editorial_count"]==338
        and previous["pending_editorial_count"]==90
        and previous["teacher_approved"]==0
        and previous["official_curriculum_atom_denominator"] is None
        and previous["full_page_teacher_reviews"]==0
        and previous["student_deep_content_published"]==0,"previous coverage or approvals drifted")
    queue=source["anchor_review_queue"]
    require(len(queue)==428 and len({q["review_id"] for q in queue})==428
        and source["source_pdf_sha256"]==B86.B85.B84.B83.SOURCE_PDF_SHA
        and hashlib.sha256(B86.B85.B84.B83.B81.dump(source).encode()).hexdigest()==B86.B85.B84.B83.B81.SOURCE_QUEUE_SHA256
        and source["official_atom_denominator"] is None
        and source["full_page_teacher_atomizations"]==0
        and source["officially_certified_atom_count"]==0
        and source["student_publishable_count"]==0,
        "frozen source or official atom status altered")
    pending=previous["pending_anchor_ids_by_track"]
    require({tr:len(ids) for tr,ids in pending.items()}==EXPECTED,
            "previous pending queue changed")
    rowids=[q["review_id"] for q in queue]
    newids={rid for ids in pending.values() for rid in ids}
    earlier=set(rowids)-newids
    require(len(earlier)==338 and len(newids)==90
        and not (earlier & newids),"prior/new source intersection")
    records=auth["records"]
    require(type(records) is list and len(records)==90
        and all(type(r) is dict and set(r)==B86.B85.B84.FIELDS for r in records),
        "author row shape, unexpected field or missing entries")
    require(len({r["review_id"] for r in records})==90,"duplicate source anchors")
    source_index={q["review_id"]:q for q in queue}
    newby=defaultdict(list);compiled=[];candidates=[]
    if verify_local_source:
        local=B86.B85.B84.B83.B81.LOCAL_PDF
        require(local.is_file()
            and hashlib.sha256(local.read_bytes()).hexdigest()==B86.B85.B84.B83.SOURCE_PDF_SHA,
            "Mac local copyrighted source PDF unavailable or modified")
        source_pages={p["printed_page"]:p["pdfkit_text_sha256"] for p in
                      load(B86.B85.B84.B83.B81.PARTS)["pages"]}
    for r in records:
        rid,tr=r["review_id"],r["track"]
        require(rid in newids and rid not in earlier and rid in source_index
            and tr in EXPECTED and source_index[rid]["track"]==tr,
            "unknown/moved/reused source anchor")
        origin=source_index[rid]
        role=r["semantic_role_provisional"]
        units=r["possible_math_units_for_teacher_split"]
        require(role in B86.B85.B84.B83.ROLES
            and not(origin["kind"]=="MAJOR_NUMBER" and role!="CURRICULUM_HEADING")
            and not(origin["kind"]=="CIRCLED_ITEM" and role=="CURRICULUM_HEADING"),
            "source kind and editorial role inconsistent")
        require(type(units) is list and len(units)<=5
            and all(type(u) is str and len(u)>=6 for u in units)
            and len(units)==len(set(units)),"invalid provisional math unit list")
        require((role=="CURRICULUM_HEADING" and not units)
            or (role in ("MATHEMATICAL_REQUIREMENT","MIXED_CLAUSE") and bool(units))
            or role in ("COMPETENCY_REQUIREMENT","APPLICATION_CONTEXT"),
            "heading promoted to mathematics or math requirement left empty")
        require(type(r["original_editorial_paraphrase"]) is str
            and len(r["original_editorial_paraphrase"])>=24
            and type(r["condition_or_scope_caution"]) is str
            and len(r["condition_or_scope_caution"])>=15,
            "missing substantial original interpretation or mathematical caution")
        require(r["cross_track_equivalence"]=="NOT_ADJUDICATED"
            and r["official_atom_count"] is None
            and r["teacher_confirmed"] is False
            and r["student_publishable"] is False,
            "unsanctioned teacher/official/student approval")
        if verify_local_source:
            page=origin["printed_page"]
            file=B86.B85.B84.B83.B81.LOCAL_LINES/f"kb56_page_{page}.txt"
            require(file.is_file(),"local PDFKit source page missing")
            raw=file.read_bytes()
            require(hashlib.sha256(raw).hexdigest()==source_pages[page]==origin["source_page_pdfkit_sha256"],
                    "Mac PDFKit page SHA drift")
            lines=raw.decode("utf8").splitlines()
            line=origin["pdfkit_line"]
            require(1<=line<=len(lines)
                and hashlib.sha256(lines[line-1].encode()).hexdigest()==origin["source_line_sha256"],
                "Mac PDFKit line SHA drift")
        newby[tr].append(rid)
        compiled.append({**r,"printed_page":origin["printed_page"],
            "pdfkit_line":origin["pdfkit_line"],
            "source_pdf_sha256":B86.B85.B84.B83.SOURCE_PDF_SHA,
            "source_page_pdfkit_sha256":origin["source_page_pdfkit_sha256"],
            "source_line_sha256":origin["source_line_sha256"],
            "source_kind":origin["kind"],
            "source_parent_segment":origin["parent_segment"],
            "review_status":"REVIEW_PENDING","teacher_approved":False,
            "math_certification":"NOT_FORMALLY_VERIFIED",
            "student_authoritative_index_eligible":False})
        for i,u in enumerate(units,1):
            candidates.append({"source_review_id":rid,"track":tr,"provisional_id":f"{rid}-C{i:02}",
                "topic":u,"cross_page_equivalence":"NOT_ADJUDICATED",
                "official_atom_id":None,"teacher_approved":False,
                "deep_lesson_complete":False,"student_publishable":False})
    require(all(newby[tr]==pending[tr] for tr in EXPECTED),"selection order or missing anchor")
    bytrack={}
    totals=Counter(q["track"] for q in queue)
    for tr in EXPECTED:
        bytrack[tr]={
            "source_anchor_denominator":totals[tr],
            "original_editorial_coverage":previous["by_track"][tr]["editorially_paraphrased_source_anchors"]+len(newby[tr]),
            "source_anchors_without_editorial":totals[tr]-previous["by_track"][tr]["editorially_paraphrased_source_anchors"]-len(newby[tr]),
            "official_atom_denominator":None,"teacher_full_page_atomization":0,
            "teacher_approved_math_atoms":0,"student_published_math_atoms":0}
    require(sum(t["source_anchor_denominator"] for t in bytrack.values())==428
        and sum(t["original_editorial_coverage"] for t in bytrack.values())==428
        and sum(t["source_anchors_without_editorial"] for t in bytrack.values())==0,
        "428 source-coverage conservation failure")
    return {
        "schema_version":SCHEMA,"standard_version":auth["standard_version"],
        "source_pdf_sha256":B86.B85.B84.B83.SOURCE_PDF_SHA,
        "source_queue_sha256":B86.B85.B84.B83.B81.SOURCE_QUEUE_SHA256,
        "author_sha256":hashlib.sha256(dump(auth).encode()).hexdigest(),
        "source_review_denominator":428,
        "previous_editorial_count":338,"new_editorial_count":90,
        "cumulative_editorial_count":428,"pending_editorial_count":0,
        "new_provisional_math_topic_count":len(candidates),
        "new_provisional_math_topics_not_deduplicated":candidates,
        "by_track":bytrack,"new_by_role":dict(Counter(r["semantic_role_provisional"] for r in compiled)),
        "official_curriculum_atom_denominator":None,"full_page_teacher_reviews":0,
        "teacher_approved":0,"student_deep_content_published":0,
        "student_index_includes_unreviewed_material":False,
        "not_yet_adjudicated":"Cross-page and cross-track equivalent mathematical requirements, official atomic denominator, completeness and teacher review",
        "new_rows":compiled}
def markdown(d):
    lines=["# Batch87｜428条来源锚点原创解释全部完成；正式课程知识原子仍未审定","",
      "本批新增90条独立原创语义释义和严格数学使用边界。累计**428/428来源锚点有项目草案释义**。",
      "**428是项目来源锚点分母，绝不是高中数学官方数学知识原子分母或课程内容完成率。**",
      "目前正式跨页/跨轨知识原子拆分与等价核对尚未裁决，全页教师审核0/61，学生内容发布0。",
      "禁止上传原始有版权标准PDF及任何整段引用，原PDF仅在Mac按SHA校验。","",
      "| 课程轨道 | 源锚点分母 | 已有原创解释 | 未解释 | 官方原子分母 |",
      "|---|---:|---:|---:|---|"]
    for tr,x in d["by_track"].items():
        lines.append(f'| {tr} | {x["source_anchor_denominator"]} | {x["original_editorial_coverage"]} | {x["source_anchors_without_editorial"]} | 未知 |')
    lines+=["",f'本批新增{d["new_provisional_math_topic_count"]}个未去重的教学主题候选。标题和活动要求不计为数学原子。',
            "这些仅供下一阶段逐章数学等价判定；全部REVIEW_PENDING。","",
            "| 原始锚点ID | 轨道 | 语义角色 | 原创理解 | 必要前提及反例边界 |",
            "|---|---|---|---|---|"]
    for r in d["new_rows"]:
        lines.append(f'| {r["review_id"]} | {r["track"]} | {r["semantic_role_provisional"]} | {r["original_editorial_paraphrase"]} | {r["condition_or_scope_caution"]} |')
    return "\n".join(lines)+"\n"
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local-source",action="store_true");args=p.parse_args()
    x=build(verify_local_source=args.verify_local_source)
    for path,value in ((OUT,dump(x)),(MD,markdown(x))):
        if args.check:
            require(path.is_file() and path.read_text(encoding="utf8")==value,
                    "generated artifact drift "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(value,encoding="utf8")
    print(f'Batch87 source editorial {x["cumulative_editorial_count"]}/428; official seven-track denominator UNKNOWN; teachers=0.')
if __name__=="__main__":main()
