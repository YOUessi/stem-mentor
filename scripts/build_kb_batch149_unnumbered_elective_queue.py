#!/usr/bin/env python3
"""K00 source-line review queue for unnumbered electives D/E; no copyright text, no auto atom census."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch149_lessons as lessons
SRC=ROOT/"curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
ENUM=ROOT/"curriculum/highschool_math/official_numbered_clause_evidence_batch18.json"
OUT=ROOT/"docs/evaluation/KB_BATCH149_UNNUMBERED_DE_REVIEW_QUEUE.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH149_UNNUMBERED_DE_REVIEW_QUEUE.md"
PAGES=range(69,74)
HASH=re.compile(r"[0-9a-f]{64}\Z")
def hash_text(text):return hashlib.sha256(text.encode("utf-8")).hexdigest()
def source_lines():
    return lessons.previous.prior.prior.prior.old.prior.upstream.prior.previous.prev.prior.prior.previous.source_pages()
def validate(v):
    require=lambda p,msg: (_ for _ in ()).throw(ValueError("KB149 K00: "+msg)) if not p else None
    source=json.loads(SRC.read_text(encoding="utf-8"))
    enumerated=json.loads(ENUM.read_text(encoding="utf-8"))
    require(source["official_pdf_sha256"]==lessons.PDF==enumerated["source"]["sha256"],"wrong source standard")
    require(v["source_pdf_sha256"]==lessons.PDF,"wrong PDF signature")
    require(v["pages_scanned"]==5 and v["printed_page_set"]==list(PAGES),"wrong D/E page range")
    require(v["source_status"]=="SHA_ONLY_LINE_QUEUE_NOT_SEMANTIC_ATOMS","false source authority")
    require(len(v["page_rows"])==5 and len(v["line_rows"])==v["nonempty_source_lines"],"page or line loss")
    require(len({x["line_id"] for x in v["line_rows"]})==len(v["line_rows"]),"duplicate line")
    require(len(v["crosspage_seams"])==4,"missing page seam review")
    require(v["all_seven_official_atom_denominators"]=={t:None for t in lessons.TRACKS},
            "invented official denominator")
    require(v["unnumbered_atomization_complete"] is False and
            v["crosspage_semantic_dedup_complete"] is False and
            v["human_approved_clauses"]==0 and v["student_authoritative"]==0 and
            v["teacher_approved"]==0,"unauthorized completion or publication")
    fp={int(p["printed_page"]):p for p in source["pages"]}
    for p in v["page_rows"]:
        n=p["printed_page"]
        require(n in PAGES and p["pdf_page_index"]==n+7 and
                p["original_pdfkit_page_sha256"]==fp[n]["pdfkit_text_sha256"] and
                p["source_numbered_markers"]==0 and p["track_hint"]==("ELECTIVE_D" if n<73 else "ELECTIVE_D_OR_E_SEMANTIC_BOUNDARY_PENDING") and
                p["semantic_review"]=="REVIEW_PENDING" and p["official_atoms_certified"]==0,
                "false page provenance or track split")
        require(p["nonempty_lines"]==sum(r["printed_page"]==n for r in v["line_rows"]),"line count drift")
    for r in v["line_rows"]:
        n=r["printed_page"]
        require(n in PAGES and r["pdf_page_index"]==n+7 and r["line_number"]>=1 and
                r["line_id"]==f"STD2020-SOURCELINE-P{n:02d}-L{r['line_number']:03d}" and
                bool(HASH.fullmatch(r["line_sha256"])) and
                r["track_hint"]==("ELECTIVE_D" if n<73 else "ELECTIVE_D_OR_E_SEMANTIC_BOUNDARY_PENDING") and
                r["line_is_knowledge_atom"] is False and r["official_atom_id"] is None and
                r["teacher_review"]=="REVIEW_PENDING" and r["curriculum_semantic_classification"]=="UNDETERMINED" and
                r["student_authoritative"] is False,"forged line semantic authority")
    for seam in v["crosspage_seams"]:
        require(seam["left_page"] in range(69,73) and seam["right_page"]==seam["left_page"]+1 and
                bool(HASH.fullmatch(seam["left_last_nonempty_line_sha256"])) and
                bool(HASH.fullmatch(seam["right_first_nonempty_line_sha256"])) and
                seam["semantic_duplicate"]=="UNDETERMINED" and
                seam["continuation"]=="UNDETERMINED" and
                seam["teacher_review"]=="REVIEW_PENDING","forged crosspage de-duplication")
    require(v["nonempty_source_lines"]==sum(p["nonempty_lines"] for p in v["page_rows"]),
            "line totals mismatch")
    return True

def build():
    """Mac-only read; all emitted evidence SHA only, no copyrighted text."""
    original=source_lines()
    fingerprints=json.loads(SRC.read_text(encoding="utf-8"))
    enumerated=json.loads(ENUM.read_text(encoding="utf-8"))
    fpm={int(r["printed_page"]):r for r in fingerprints["pages"]}
    assert fingerprints["official_pdf_sha256"]==lessons.PDF
    rows=[];page_rows=[];seams=[]
    for p in PAGES:
        assert p in original and p in fpm
        assert not any(a["printed_page"]==p for a in enumerated["enumerated_source_anchors"])
        lines=original[p]
        hint="ELECTIVE_D" if p<73 else "ELECTIVE_D_OR_E_SEMANTIC_BOUNDARY_PENDING"
        for number,line in enumerate(lines,1):
            if not line.strip():continue
            rows.append(dict(line_id=f"STD2020-SOURCELINE-P{p:02d}-L{number:03d}",
                printed_page=p,pdf_page_index=p+7,line_number=number,
                line_sha256=hash_text(line),track_hint=hint,
                line_is_knowledge_atom=False,official_atom_id=None,teacher_review="REVIEW_PENDING",
                curriculum_semantic_classification="UNDETERMINED",student_authoritative=False))
        page_rows.append(dict(printed_page=p,pdf_page_index=p+7,track_hint=hint,
            original_pdfkit_page_sha256=fpm[p]["pdfkit_text_sha256"],
            physical_lines=len(lines),nonempty_lines=sum(r["printed_page"]==p for r in rows),
            source_numbered_markers=0,semantic_review="REVIEW_PENDING",official_atoms_certified=0))
    for left in range(69,73):
        l=[r for r in rows if r["printed_page"]==left]
        r=[r for r in rows if r["printed_page"]==left+1]
        assert l and r
        seams.append(dict(left_page=left,right_page=left+1,
            left_last_nonempty_line_sha256=l[-1]["line_sha256"],
            right_first_nonempty_line_sha256=r[0]["line_sha256"],
            continuation="UNDETERMINED",semantic_duplicate="UNDETERMINED",
            teacher_review="REVIEW_PENDING"))
    result=dict(schema="kb149-de-unnumbered-source-line-queue/1",
        source_status="SHA_ONLY_LINE_QUEUE_NOT_SEMANTIC_ATOMS",
        source_pdf_sha256=lessons.PDF,pages_scanned=5,printed_page_set=list(PAGES),
        nonempty_source_lines=len(rows),page_rows=page_rows,line_rows=rows,
        crosspage_seams=seams,
        all_seven_official_atom_denominators={t:None for t in lessons.TRACKS},
        unnumbered_atomization_complete=False,crosspage_semantic_dedup_complete=False,
        teacher_approved=0,student_authoritative=0,human_approved_clauses=0,
        warning="No numbered source markers found here != no mathematical course content. These are SHA-only original lines including headings, NOT human-reviewed syllabus atomic requirements.")
    validate(result)
    return result
def render(v):
    lines=["# KB149｜选修D/E未编号课标内容：原始行位置与跨页边界审查队列","",
      "这些是原始课标PDFKit核验的**来源行**，不是完整课程知识原子，也不是已确认的未编号知识要求。页73的D/E分界尚待人工原文复核；所有分母仍UNKNOWN。","",
      "| 印刷页 | 课程候选 | 原始行数 | 非空来源行 | 已编号标记 | 课标原子已认证 |",
      "|---:|---|---:|---:|---:|---:|"]
    for p in v["page_rows"]:
        lines.append(f'| {p["printed_page"]} | {p["track_hint"]} | {p["physical_lines"]} | {p["nonempty_lines"]} | 0 | 0 |')
    lines.extend(["",f'合计{v["nonempty_source_lines"]}条非空原始来源行、{len(v["crosspage_seams"])}个跨页连续性候选，都等待教师与课标审校人员人工裁决。',"",
    "不得按字符长度或标点拆分代替语义原子裁决；不得把来源行数当作官方课程分母，亦不得声称选修D/E无内容。","",
    "下一步：在Mac合法本地原文逐行审阅，定课程归属、数学概念/定理/方法/探究活动、跨页续句与真实重复，所有裁决留下依据和复核人；若没有复核，正式原子分母始终为空。","",
    "JSON仅含原始行哈希、页面及审查状态，不含受版权保护的原文。",""])
    return "\n".join(lines)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write-mac",action="store_true")
    g.add_argument("--check-mac",action="store_true")
    g.add_argument("--check",action="store_true")
    a=p.parse_args()
    if a.write_mac:
        v=build()
        OUT.write_text(lessons.encode(v),encoding="utf-8")
        REPORT.write_text(render(v),encoding="utf-8")
    else:
        v=json.loads(OUT.read_text(encoding="utf-8"))
        validate(v)
        if a.check_mac:
            assert build()==v,"original Mac PDFKit SHA line replay failed"
        assert REPORT.read_text(encoding="utf-8")==render(v),"report mutation"
    print(f'PASS Batch149 unnumbered D/E source-line SHA queue: {v["nonempty_source_lines"]} nonempty lines, 5 pages, 4 unadjudicated page seams, 0 official atoms')
if __name__=="__main__":main()
