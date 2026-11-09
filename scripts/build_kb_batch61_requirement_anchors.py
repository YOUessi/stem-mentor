#!/usr/bin/env python3
"""Reproducible, copyright-safe candidate clause anchors, NOT official atom counts.

Source extraction is Mac-only. CI replays the pinned, text-free anchor ledger.
Markers are merely potential clause boundaries: manual parsing, mathematical
equivalence review and teacher attestation are mandatory for a real denominator.
"""
from __future__ import annotations
import argparse
import csv
import io
from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
CUR = ROOT / "curriculum/highschool_math"
DOC = ROOT / "docs/evaluation"
PAGES = CUR / "k00_batch51_pdfkit_page_fingerprints.json"
REGISTRY = CUR / "k00_batch61_source_anchor_registry.json"
OUT = DOC / "KB_BATCH61_CLAUSE_ANCHOR_COVERAGE.json"
MD = DOC / "KB_BATCH61_CLAUSE_ANCHOR_COVERAGE.md"
QUEUE = DOC / "KB_BATCH61_UNLINKED_ANCHOR_REVIEW_QUEUE.csv"
PDF_SHA = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
ROWS_PIN_SHA256 = "b66864829673875dff26462a23a4f44960b8d2b8d0eed79bfc5da027e41d46b0"  # human-reviewed commit anchor, not a cryptographic signature
SOURCE_REPORTS = (
    DOC / "KB_BATCH56_COMPULSORY_SOURCE_SPAN_REVIEW.json",
    DOC / "KB_BATCH57_SOURCE_SPAN_REVIEW.json",
    DOC / "KB_BATCH59_SELECTIVE_SOURCE_SPAN_REVIEW.json",
    DOC / "KB_BATCH60_ELECTIVE_SOURCE_REVIEW.json",
)
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A", "ELECTIVE_B",
          "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")
MARKERS = ("MAJOR_NUMBER", "SUBCLAUSE_NUMBER", "CIRCLED_ITEM", "SECTION_LABEL")
SPAN_RE = re.compile(r"^P(\d{3})-L(\d{3})-(\d{3})$")
MAJOR_RE = re.compile(r"^[0-9]+[.．、]")
SUB_RE = re.compile(r"^[（(]\s*[0-9]+\s*[）)]")
SECTION_RE = re.compile(r"^[【\[]\s*(内容要求|学业要求|教学提示|教学建议|内容与要求)\s*[】\]]")
CIRCLED = set("①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳")

def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)

def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"

def marker(line: str):
    line = line.lstrip()
    if not line:
        return None
    if line[0] in CIRCLED:
        return "CIRCLED_ITEM"
    norm = unicodedata.normalize("NFKC", line)
    compact = re.sub(r"\s+", "", norm)
    if SECTION_RE.match(compact):
        return "SECTION_LABEL"
    if SUB_RE.match(compact):
        return "SUBCLAUSE_NUMBER"
    if MAJOR_RE.match(compact):
        return "MAJOR_NUMBER"
    return None

def track_for(page: int, line: int) -> str:
    require(13 <= page <= 73 and line > 0, "invalid track coordinate")
    if page <= 36:
        return "COMPULSORY"
    if page <= 50:
        return "SELECTIVE_COMPULSORY"
    if page == 51 and line < 20:
        return "ELECTIVE_GENERAL"
    if page < 57 or (page == 57 and line < 16):
        return "ELECTIVE_A"
    if page < 64 or (page == 64 and line < 10):
        return "ELECTIVE_B"
    if page < 69 or (page == 69 and line < 6):
        return "ELECTIVE_C"
    if page < 73 or (page == 73 and line < 13):
        return "ELECTIVE_D"
    return "ELECTIVE_E"

def extract(local_source_dir: Path, pdf: Path) -> dict:
    require(pdf.is_file() and sha256(pdf.read_bytes()).hexdigest() == PDF_SHA, "original PDF SHA mismatch")
    fp = load(PAGES)
    require(fp["official_pdf_sha256"] == PDF_SHA and len(fp["pages"]) == 61, "page inventory drift")
    by_page = {x["printed_page"]: x for x in fp["pages"]}
    require(set(by_page) == set(range(13, 74)), "missing source pages")
    entries, counts, controls = [], {}, {}
    for page in range(13, 74):
        p = local_source_dir / f"kb56_page_{page}.txt"
        require(p.is_file(), f"missing local PDFKit page {page}")
        raw = p.read_bytes()
        require(sha256(raw).hexdigest() == by_page[page]["pdfkit_text_sha256"], f"PDFKit page SHA mismatch {page}")
        lines = raw.decode("utf-8").splitlines()
        counts[str(page)] = len(lines)
        controls[str(page)] = sum(1 for c in raw.decode("utf-8") if ord(c) < 32 and c not in "\r\n\t")
        for ix, line in enumerate(lines, 1):
            kind = marker(line)
            if kind:
                entries.append(dict(printed_page=page, pdf_page_index=page+7,
                                    pdfkit_line=ix, kind=kind, track_hint=track_for(page, ix),
                                    source_line_sha256=sha256(line.encode("utf-8")).hexdigest(),
                                    source_page_pdfkit_sha256=by_page[page]["pdfkit_text_sha256"],
                                    teacher_review="REVIEW_PENDING",
                                    certified_official_atom=False,
                                    full_page_review_completed=False,
                                    duplicate_equivalence_review="PENDING",
                                    student_publishable=False))
    return dict(schema_version="kb61-anchor-registry-v1", source_pdf_sha256=PDF_SHA,
                page_line_counts=counts, page_control_scalar_counts=controls,
                includes_copyright_passages=False, scope="NON_EXHAUSTIVE_HEURISTIC_CLAUSE_START_ANCHORS",
                rows=entries)

def validate(registry: dict, verify_source=False) -> None:
    fp=load(PAGES)
    page_hash={x["printed_page"]:x["pdfkit_text_sha256"] for x in fp["pages"]}
    require(registry["schema_version"]=="kb61-anchor-registry-v1" and
            registry["source_pdf_sha256"]==PDF_SHA and
            registry["includes_copyright_passages"] is False and
            registry["scope"]=="NON_EXHAUSTIVE_HEURISTIC_CLAUSE_START_ANCHORS", "registry provenance")
    counts=registry["page_line_counts"]; controls=registry["page_control_scalar_counts"]
    require(set(map(int,counts))==set(range(13,74)) and
            set(map(int,controls))==set(range(13,74)), "61 pages not indexed")
    require(all(type(v) is int and 0<v<1000 for v in counts.values()) and
            all(type(v) is int and v>=0 for v in controls.values()), "invalid page measurements")
    require(sha256(json.dumps(registry["rows"],sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf-8")).hexdigest()==ROWS_PIN_SHA256,
            "anchor row evidence differs from pinned snapshot")
    seen=set()
    for r in registry["rows"]:
        require(set(r)=={"printed_page","pdf_page_index","pdfkit_line","kind","track_hint",
                        "source_line_sha256","source_page_pdfkit_sha256","teacher_review",
                        "certified_official_atom","full_page_review_completed",
                        "duplicate_equivalence_review","student_publishable"}, "invalid or privileged anchor field")
        page,line=r["printed_page"],r["pdfkit_line"]
        require(type(page) is int and type(line) is int and 13<=page<=73 and
                1<=line<=counts[str(page)] and (page,line) not in seen,"anchor coordinate invalid or duplicate")
        seen.add((page,line))
        require(r["kind"] in MARKERS and r["track_hint"]==track_for(page,line) and
                r["pdf_page_index"]==page+7, "marker kind / track wrong")
        require(r["source_page_pdfkit_sha256"]==page_hash[page] and
                re.fullmatch(r"[a-f0-9]{64}",r["source_line_sha256"]), "source attestation drift")
        require(r["teacher_review"]=="REVIEW_PENDING" and
                r["certified_official_atom"] is False and r["full_page_review_completed"] is False and
                r["duplicate_equivalence_review"]=="PENDING" and r["student_publishable"] is False,
                "untrusted approval or premature coverage")
    require(registry["rows"]==sorted(registry["rows"],key=lambda x:(x["printed_page"],x["pdfkit_line"])),
            "nondeterministic anchor ordering")
    require(len(seen)>100,"implausibly empty anchor inventory")

def leads():
    rows=[]
    expected=(52,78,108,106)
    for path,n in zip(SOURCE_REPORTS,expected):
        data=load(path)
        subset=data["rows"]
        require(len(subset)==n, "source lead baseline changed")
        for r in subset:
            m=SPAN_RE.fullmatch(r["source_span_id"])
            require(m is not None,"unparseable source coordinate")
            page,a,b=map(int,m.groups())
            require(13<=page<=73 and 0<a<=b,"invalid source lead interval")
            require(r["printed_page"]==page and r["source_pdf_sha256"]==PDF_SHA and
                    r["teacher_review"]=="REVIEW_PENDING" and not r["student_publishable"],
                    "source lead approval/scope drift")
            rows.append((page,a,b,r["source_span_id"]))
    require(len(rows)==344,"partial lead count is not the official denominator")
    return rows

def build(registry=None, lead_rows=None):
    r=deepcopy(load(REGISTRY) if registry is None else registry)
    validate(r)
    ls=leads() if lead_rows is None else lead_rows
    require(len(ls)==344,"source lead inventory drift")
    page_leads=defaultdict(list)
    for page,a,b,key in ls:
        require(13<=page<=73 and 0<a<=b<=r["page_line_counts"][str(page)],"lead outside attested lines")
        page_leads[page].append((a,b,key))
    by_page=defaultdict(list)
    for row in r["rows"]:
        page,line=row["printed_page"],row["pdfkit_line"]
        hits=sorted({key for a,b,key in page_leads[page] if a<=line<=b})
        enriched=dict(row, partial_source_lead_ids=hits,
                      has_partially_located_source_lead=bool(hits),
                      knowledge_atom_completeness="NOT_EVALUATED",
                      official_denominator_membership="UNDETERMINED")
        by_page[page].append(enriched)
    page_summary=[]
    for p in range(13,74):
        found=by_page[p]
        missing=[x["pdfkit_line"] for x in found if not x["has_partially_located_source_lead"]]
        page_summary.append(dict(printed_page=p,line_count=r["page_line_counts"][str(p)],
                                 control_scalar_count=r["page_control_scalar_counts"][str(p)],
                                 source_leads=len(page_leads[p]),heuristic_clause_anchors=len(found),
                                 anchors_without_partial_source_lead=missing,
                                 full_page_human_review="PENDING",
                                 potentially_unreadable_figure_or_formula=r["page_control_scalar_counts"][str(p)]>0,
                                 mathematical_equivalence_audit="PENDING"))
    all_rows=[item for p in range(13,74) for item in by_page[p]]
    kinds=Counter(a["kind"] for a in all_rows)
    tracks=Counter(a["track_hint"] for a in all_rows)
    for track in (*TRACKS, "ELECTIVE_GENERAL"):
        tracks.setdefault(track,0)
    return dict(schema_version="kb61-heuristic-anchor-audit-v1",
                source_pdf_sha256=PDF_SHA, source_pages_total=61,
                earlier_partial_source_leads=344,
                candidate_anchor_count=len(all_rows),
                candidate_anchor_count_by_kind=dict(sorted(kinds.items())),
                candidate_anchor_count_by_track_hint=dict(sorted(tracks.items())),
                candidate_anchors_without_partial_lead=sum(not a["has_partially_located_source_lead"] for a in all_rows),
                pages_with_control_code_evidence=[p["printed_page"] for p in page_summary if p["potentially_unreadable_figure_or_formula"]],
                official_atomic_denominator={t:None for t in TRACKS},
                full_page_teacher_review_completed=0, teacher_approved=0, student_published=0,
                conflict_count_still_unadjudicated=10, historical_unverified_proof_steps=538,
                candidate_anchors_are_not_official_atoms=True,
                source_lead_is_not_equivalent_to_content_coverage=True,
                manual_unenumerated_and_visual_requirements_still_pending=True,
                pages=page_summary, anchors=all_rows)

def render(report):
    lines=["# K00 Batch61｜61页课标候选条款起点与漏关联矩阵（非官方分母）","",
           f"来源非去重线索：{report['earlier_partial_source_leads']}；机器候选起点：{report['candidate_anchor_count']}；未落在现有局部来源线索中的候选起点：{report['candidate_anchors_without_partial_lead']}。","",
           "**这些是自动检测的编号/章节起点，不是独立数学知识原子；机器无法保证包含跨行、未编号、图示要求。正式七轨分母均为null，仍需逐页教师审核及跨页等价复核。**","",
           "| 印刷页 | PDFKit行数 | 机器候选起点 | 未落在既有来源线索起点 | 控制字符/图像人工审查 |",
           "|---:|---:|---:|---:|---|"]
    for p in report["pages"]:
        lines.append(f"| {p['printed_page']} | {p['line_count']} | {p['heuristic_clause_anchors']} | {len(p['anchors_without_partial_source_lead'])} | {'是' if p['potentially_unreadable_figure_or_formula'] else '未检出控制字符（非通过）'} |")
    lines+=["","## 待复核起点位置（仅行号，不复制课标正文）",""]
    for p in report["pages"]:
        if p["anchors_without_partial_source_lead"]:
            lines.append(f"- 印刷页 {p['printed_page']}: "+", ".join(map(str,p["anchors_without_partial_source_lead"])))
    lines+=["","## 必须坚持的发布门槛","",
            "- 所有新定位信息仍为 REVIEW_PENDING；没有教师签署的任何课程/测评/定理不得发表。",
            "- PDFKit 控制字符、扫描图示、多栏错行、未编号句子必须独立人工补审。",
            "- 相同主题/相同来源页/已链接讲义不等于数学等价或真实能力覆盖。",
            "- 该矩阵仅帮助确定下一批重点审校坐标；不能把候选起点数量当官方课程分母。",""]
    return "\n".join(lines)

def render_queue(report):
    output=io.StringIO()
    writer=csv.writer(output,lineterminator="\n")
    writer.writerow(["candidate_anchor_id","printed_page","pdfkit_line","track_hint","marker_kind",
                     "source_line_sha256","triage_priority","reason","review_state","certified_atom"])
    for row in report["anchors"]:
        if row["has_partially_located_source_lead"]:
            continue
        priority="P1" if row["kind"]=="MAJOR_NUMBER" else "P0"
        writer.writerow([f"KB61-P{row['printed_page']:03d}-L{row['pdfkit_line']:03d}",
                         row["printed_page"],row["pdfkit_line"],row["track_hint"],
                         row["kind"],row["source_line_sha256"],priority,
                         "NO_EXISTING_PARTIAL_SOURCE_LEAD_OVERLAP_NOT_PROOF_OF_CONTENT_GAP",
                         "REVIEW_PENDING",False])
    return output.getvalue()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--extract",action="store_true",help="Mac only: rebuild source-free anchor registry")
    parser.add_argument("--check",action="store_true",help="CI: validate and compare committed JSON and Markdown")
    parser.add_argument("--verify-local-source",type=Path)
    parser.add_argument("--source-dir",type=Path,default=Path("/private/tmp"))
    args=parser.parse_args()
    if args.extract:
        require(args.verify_local_source is not None,"--extract requires pinned original PDF")
        registry=extract(args.source_dir,args.verify_local_source)
        validate(registry)
        REGISTRY.write_text(canonical(registry),encoding="utf-8")
    registry=load(REGISTRY)
    validate(registry)
    if args.verify_local_source is not None:
        fresh=extract(args.source_dir,args.verify_local_source)
        require(fresh==registry,"local PDFKit anchor attestation drift")
    audit=build(registry=registry)
    if args.check:
        require(OUT.is_file() and OUT.read_text(encoding="utf-8")==canonical(audit),
                "generated JSON audit stale")
        require(MD.is_file() and MD.read_text(encoding="utf-8")==render(audit),
                "generated Markdown audit stale")
        require(QUEUE.is_file() and QUEUE.read_text(encoding="utf-8")==render_queue(audit),
                "generated review queue stale")
    else:
        OUT.write_text(canonical(audit),encoding="utf-8")
        MD.write_text(render(audit),encoding="utf-8")
        QUEUE.write_text(render_queue(audit),encoding="utf-8")
    print(f"61-page anchor audit: {audit['candidate_anchor_count']} candidates; "
          f"{audit['candidate_anchors_without_partial_lead']} unlinked, "
          f"7 official denominators null; check={args.check}")

if __name__=="__main__":
    main()
