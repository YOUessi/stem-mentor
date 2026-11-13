#!/usr/bin/env python3
"""Batch73: Mac-attested, *complete line partition* of 61 partial-source pages.

The original PDFKit text never enters the repository. A line partition is not
an official clause parse, knowledge-atom denominator, or teacher attestation.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

import build_kb_batch61_requirement_anchors as B61

ROOT = Path(__file__).resolve().parents[1]
CUR = ROOT / "curriculum/highschool_math"
DOC = ROOT / "docs/evaluation"
REG = CUR / "k00_batch61_source_anchor_registry.json"
PAGES = CUR / "k00_batch51_pdfkit_page_fingerprints.json"
PROPOSALS = CUR / "k00_batch63_provisional_atom_proposals.json"
REQUIREMENTS = DOC / "KB_BATCH72_INDEPENDENT_REQUIREMENTS.json"
WITNESS = CUR / "k00_batch73_page_partition_witness.json"
AUDIT = DOC / "KB_BATCH73_PAGE_PARTITION_COVERAGE.json"
REPORT = DOC / "KB_BATCH73_PAGE_PARTITION_COVERAGE.md"
SOURCE = Path("/private/tmp")
# Pinned after Mac PDFKit verification. This is a versioned integrity check,
# not evidence of mathematical equivalence or an official curriculum count.
WITNESS_ROWS_SHA = "ef7afa925aec3d91adf13ba7f62a9498c801842552f59bc96522e1552a26f644"
TRACKS = tuple(B61.TRACKS)
ALLOWED_TRACKS = set(TRACKS) | {"ELECTIVE_GENERAL"}
HEX64 = re.compile(r"^[a-f0-9]{64}$")
SPAN = re.compile(r"^P(\d{3})-L(\d{3})-(\d{3})$")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def digest(data):
    return sha256(data).hexdigest()


def rows_digest(rows):
    return digest(json.dumps(rows, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode())


def page_anchors(reg):
    anchors = defaultdict(dict)
    for r in reg["rows"]:
        p, line = r["printed_page"], r["pdfkit_line"]
        require(line not in anchors[p], "duplicate source anchor")
        anchors[p][line] = r
    return anchors


def create_witness(source_dir=SOURCE, registry=None):
    registry = load(REG) if registry is None else registry
    B61.validate(registry)
    inventory = load(PAGES)
    require(inventory["official_pdf_sha256"] == registry["source_pdf_sha256"], "source PDF lineage")
    pages = {p["printed_page"]: p for p in inventory["pages"]}
    require(set(pages) == set(range(13, 74)), "not the complete 61-page inventory")
    anchors = page_anchors(registry)
    segments = []
    for page in range(13, 74):
        raw = (source_dir / f"kb56_page_{page}.txt").read_bytes()
        require(digest(raw) == pages[page]["pdfkit_text_sha256"], f"Mac PDFKit source drift page {page}")
        lines = raw.decode("utf-8").splitlines()
        total = registry["page_line_counts"][str(page)]
        require(len(lines) == total and total > 0, "source page line count mismatch")
        boundary = {1, total + 1} | set(anchors[page])
        # Explicitly split when the track changes WITHIN an individual page.
        # In particular the generic elective preface is NOT elective A.
        for n in range(2, total + 1):
            if B61.track_for(page, n) != B61.track_for(page, n - 1):
                boundary.add(n)
        edges = sorted(boundary)
        require(edges[0] == 1 and edges[-1] == total + 1, "unpartitioned source page")
        prior_anchor = None
        for start, next_start in zip(edges, edges[1:]):
            end = next_start - 1
            require(start <= end, "empty source segment")
            marker = anchors[page].get(start)
            if marker:
                require(digest(lines[start - 1].encode()) == marker["source_line_sha256"],
                        "line-level anchor SHA drift")
                prior_anchor = f"KB61-P{page:03d}-L{start:03d}"
            is_transition = start > 1 and B61.track_for(page, start) != B61.track_for(page, start - 1)
            kind = ("ANCHOR_WINDOW" if marker else
                    "TRACK_TRANSITION_CONTINUATION" if is_transition else
                    "UNMARKED_PREAMBLE" if prior_anchor is None else "UNMARKED_CONTINUATION")
            segments.append(dict(
                segment_id=f"KB73-P{page:03d}-L{start:03d}-{end:03d}",
                printed_page=page, first_line=start, last_line=end,
                line_count=end - start + 1,
                section_kind=kind,
                marker_kind=marker["kind"] if marker else None,
                anchor_id=prior_anchor if marker else None,
                preceding_anchor_id=None if marker else prior_anchor,
                track_hint=B61.track_for(page, start),
                source_page_pdfkit_sha256=pages[page]["pdfkit_text_sha256"],
                first_line_sha256=digest(lines[start - 1].encode()),
                last_line_sha256=digest(lines[end - 1].encode()),
                span_sha256=digest("\n".join(lines[start - 1:end]).encode()),
                teacher_full_clause_review="NOT_DONE",
                mathematical_equivalence_review="NOT_DONE",
                officially_certified_atom=False,
                teacher_approved=False,
                student_publishable=False,
            ))
    return dict(
        schema_version="kb73-full-page-partition-v1",
        scope="MAC_PDFKIT_LINE_PARTITION_NOT_OFFICIAL_CLAUSES",
        source_pdf_sha256=registry["source_pdf_sha256"],
        includes_copyright_text=False,
        full_page_teacher_reviews=0,
        teacher_approved=0,
        student_published=0,
        officially_certified_denominators={track: None for track in TRACKS},
        segment_count=len(segments), segments=segments,
    )


def validate_witness(witness, verify_mac_source=False, source_dir=SOURCE):
    registry = load(REG)
    B61.validate(registry)
    require(set(witness) == {"schema_version", "scope", "source_pdf_sha256",
                            "includes_copyright_text", "full_page_teacher_reviews",
                            "teacher_approved", "student_published",
                            "officially_certified_denominators", "segment_count", "segments"},
            "witness schema or source privacy violated")
    require(witness["schema_version"] == "kb73-full-page-partition-v1" and
            witness["scope"] == "MAC_PDFKIT_LINE_PARTITION_NOT_OFFICIAL_CLAUSES" and
            witness["source_pdf_sha256"] == B61.PDF_SHA and
            witness["includes_copyright_text"] is False, "source provenance / copyright guard")
    require(witness["officially_certified_denominators"] == {t: None for t in TRACKS} and
            witness["teacher_approved"] == witness["student_published"] ==
            witness["full_page_teacher_reviews"] == 0, "invented curriculum or teacher approval")
    segs = witness["segments"]
    require(witness["segment_count"] == len(segs) and len(segs) >= 428, "missing segment")
    require(rows_digest(segs) == WITNESS_ROWS_SHA, "source witness pin mismatch")
    anchors = page_anchors(registry)
    inventory = {r["printed_page"]: r["pdfkit_text_sha256"] for r in load(PAGES)["pages"]}
    by_page = defaultdict(list)
    for s in segs:
        require(set(s) == {"segment_id", "printed_page", "first_line", "last_line",
                           "line_count", "section_kind", "marker_kind", "anchor_id",
                           "preceding_anchor_id", "track_hint", "source_page_pdfkit_sha256",
                           "first_line_sha256", "last_line_sha256", "span_sha256",
                           "teacher_full_clause_review", "mathematical_equivalence_review",
                           "officially_certified_atom", "teacher_approved", "student_publishable"},
                "segment has unauthorized content or field")
        p, a, b = s["printed_page"], s["first_line"], s["last_line"]
        require(type(p) is int and type(a) is int and type(b) is int and
                13 <= p <= 73 and 1 <= a <= b and s["line_count"] == b-a+1 and
                s["segment_id"] == f"KB73-P{p:03d}-L{a:03d}-{b:03d}", "segment coordinate invalid")
        require(s["track_hint"] in ALLOWED_TRACKS and
                s["track_hint"] == B61.track_for(p,a) ==
                B61.track_for(p,b), "track boundary crossed or mislabeled")
        require(s["source_page_pdfkit_sha256"] == inventory[p] and
                all(isinstance(s[k],str) and HEX64.fullmatch(s[k]) for k in
                    ("first_line_sha256","last_line_sha256","span_sha256")), "source checksum invalid")
        require(s["teacher_full_clause_review"] == s["mathematical_equivalence_review"] ==
                "NOT_DONE" and s["officially_certified_atom"] is False and
                s["teacher_approved"] is False and s["student_publishable"] is False,
                "premature publication/certification")
        if a in anchors[p]:
            anchor = anchors[p][a]
            require(s["section_kind"] == "ANCHOR_WINDOW" and
                    s["marker_kind"] == anchor["kind"] and
                    s["anchor_id"] == f"KB61-P{p:03d}-L{a:03d}" and
                    s["preceding_anchor_id"] is None and
                    s["first_line_sha256"] == anchor["source_line_sha256"],
                    "broken original anchor provenance")
        else:
            require(s["section_kind"] in ("TRACK_TRANSITION_CONTINUATION",
                    "UNMARKED_PREAMBLE","UNMARKED_CONTINUATION") and
                    s["marker_kind"] is None and s["anchor_id"] is None,
                    "fabricated numbered clause")
        by_page[p].append(s)
    require(set(by_page) == set(range(13,74)), "missing printed pages")
    observed_anchors = []
    for p in range(13,74):
        rows = by_page[p]
        require(rows[0]["first_line"] == 1 and
                rows[-1]["last_line"] == registry["page_line_counts"][str(p)],
                "uncatalogued start or end lines")
        require(all(left["last_line"]+1 == right["first_line"]
                    for left,right in zip(rows,rows[1:])), "source partition gap or overlap")
        observed_anchors.extend((p,r["first_line"]) for r in rows if r["section_kind"] == "ANCHOR_WINDOW")
    require(set(observed_anchors) ==
            {(p,n) for p,page in anchors.items() for n in page}
            and len(observed_anchors) == len(registry["rows"]) == 428,
            "missing/extra source marker")
    if verify_mac_source:
        actual = create_witness(source_dir,registry)
        require(actual == witness, "Mac source text differs from pinned segment evidence")
    return True


def build(witness=None):
    witness = load(WITNESS) if witness is None else witness
    validate_witness(witness)
    props = load(PROPOSALS)["proposals"]
    reqs = load(REQUIREMENTS)["records"]
    registry = load(REG)
    require(len(props) == 62 and len(reqs) == 28, "previous candidate inventory drift")
    anchors = {f"KB61-P{x['printed_page']:03d}-L{x['pdfkit_line']:03d}"
               for x in registry["rows"]}
    require(len(anchors) == 428, "source marker lineage drift")
    proposal_counts = Counter()
    for r in props:
        require(r["parent_anchor_id"] in anchors and
                r["teacher_review"] == "REVIEW_PENDING" and
                r["official_atomic_membership"] == "UNDETERMINED" and
                not r["student_publishable"], "unapproved atom or orphan source")
        proposal_counts[r["parent_anchor_id"]] += 1
    req_map = defaultdict(list)
    for r in reqs:
        match = SPAN.fullmatch(r["source_span_id"])
        require(match is not None, "unparseable nonatom source span")
        p, a, b = map(int,match.groups())
        require(p == r["printed_page"] and a <= b and
                13 <= p <= 73 and b <= registry["page_line_counts"][str(p)] and
                r["full_clause_teacher_review"] == "NOT_DONE" and
                r["coverage_status"] == "UNMAPPED" and
                not r["student_publishable"], "nonatom requirement scope / approval drift")
        req_map[p].append((a,b,r["source_candidate_id"]))
    annotation = []
    touched = set()
    for s in witness["segments"]:
        p,a,b = s["printed_page"],s["first_line"],s["last_line"]
        cross = [id for x,y,id in req_map[p] if max(x,a) <= min(y,b)]
        touched.update(cross)
        annotation.append(dict(
            segment_id=s["segment_id"], printed_page=p, first_line=a,
            last_line=b, track_hint=s["track_hint"],
            evidence_kind=s["section_kind"],
            candidate_atom_splits=proposal_counts.get(s["anchor_id"],0),
            linked_nonatom_requirement_ids=sorted(cross),
            full_text_and_cross_page_teacher_review="NOT_DONE",
            official_clause_membership="UNDETERMINED",
            counted_in_official_atom_denominator=False,
            student_publishable=False,
        ))
    require(len(touched) == 28 and sum(x["candidate_atom_splits"] for x in annotation) == 62,
            "lost provisional split or nonatom requirement")
    tracks = {}
    for track in (*TRACKS,"ELECTIVE_GENERAL"):
        subset = [r for r in annotation if r["track_hint"] == track]
        tracks[track] = dict(
            heuristic_segment_count=len(subset),
            pdfkit_lines_accounted_for=sum(r["last_line"]-r["first_line"]+1 for r in subset),
            heuristic_anchor_count=sum(r["evidence_kind"]=="ANCHOR_WINDOW" for r in subset),
            provisional_atom_candidates=sum(r["candidate_atom_splits"] for r in subset),
            official_atom_denominator=None,
            confirmed_missing_atoms=None, teacher_approved=0,
            student_published=0,
        )
    require(sum(t["heuristic_anchor_count"] for t in tracks.values()) == 428,
            "anchor accounting mismatch")
    require(sum(t["provisional_atom_candidates"] for t in tracks.values()) == 62,
            "candidate accounting mismatch")
    risky = [dict(segment_id=r["segment_id"], printed_page=r["printed_page"],
                  reason=("NOT_MARKER_ANCHORED" if r["evidence_kind"]!="ANCHOR_WINDOW"
                          else "LONG_UNVERIFIED_WINDOW"),
                  lines=r["last_line"]-r["first_line"]+1)
             for r in annotation if r["evidence_kind"]!="ANCHOR_WINDOW" or
             r["last_line"]-r["first_line"] >= 24]
    result = dict(
        schema_version="kb73-full-page-audit-v1", source_pdf_sha256=B61.PDF_SHA,
        witness_rows_sha256=rows_digest(witness["segments"]),
        official_denominator_by_track={t: None for t in TRACKS},
        curriculum_scope_complete=False, full_source_pages_line_partitioned=61,
        teacher_full_page_reviews=0, heuristic_source_anchors=428,
        internal_provisional_atom_splits=62, independent_nonatom_requirements=28,
        approved_lessons=0, student_published=0,
        page_partition_is_not_full_clause_parse=True,
        source_text_embedded=False,
        tracks=tracks, review_risks=risky, segments=annotation,
    )
    md = ["# Batch73｜高中数学课程标准全页行分区核验（非课程完成认证）",
          "",
          "Mac PDFKit源文本只在授权Mac上计算SHA与区间分区；GitHub不保存原文。",
          "这是**61页全部行均有来源分区**的工程完整性，不代表61页课程条款已经人工/教师逐条审查。",
          "428个启发式起点不等于数学知识原子；62项拆分和28项非知识要求均是待审候选。",
          "所有官方知识原子分母仍为null，真人教师审查、形式化证明和学生发布均为0。",
          "",
          "| 轨道提示 | 非权威起点 | 分区数 | 原文行数 | 临时原子假设 | 官方知识原子分母 |",
          "|---|---:|---:|---:|---:|---|"]
    for t,c in tracks.items():
        md.append(f"| {t} | {c['heuristic_anchor_count']} | {c['heuristic_segment_count']} | {c['pdfkit_lines_accounted_for']} | {c['provisional_atom_candidates']} | **未知** |")
    md += ["", f"总计：61页、{len(annotation)}个不重叠行分区、428个启发式起点、"
           f"{len(risky)}项需优先审查的非锚定/长区间风险；28/28项非知识候选在分区中有位置链接。",
           "",
           "## 未关闭的审查风险",
           "1. PDFKit行分区不识别段落跨页、表格/图示与完整句法，尤其第35页建模流程图必须人工查看原版图像。",
           "2. 第51、57、64、69、73页含跨轨转换；分区在轨道切换处强制切断，避免误记选修范围。",
           "3. 选修E的0个启发式起点不是官方0个知识点；选修总论 ELECTIVE_GENERAL 不强行并入选修A。",
           "4. 每段依然没有真人教师签核或数学等价裁决；当前无法计算官方课程覆盖百分比。",
           "5. 下一轮从长区间与非编号分区逐页审查完整原文和第35页图示，再拆分真正知识原子、建立七轨官方分母。",
           ""]
    return result, "\n".join(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate-source", action="store_true",
                    help="Mac only: verify 61 PDFKit page hashes and emit text-free segment witness")
    ap.add_argument("--verify-local-source", action="store_true",
                    help="Mac only: compare witness against every source line")
    ap.add_argument("--check", action="store_true")
    opt = ap.parse_args()
    if opt.generate_source:
        require(not opt.check, "do not regenerate source in check mode")
        obj = create_witness()
        WITNESS.write_text(canonical(obj), encoding="utf-8")
        print("new witness rows digest", rows_digest(obj["segments"]))
        # After first creation the maintainer pins the hash in this script.
        if WITNESS_ROWS_SHA == "ef7afa925aec3d91adf13ba7f62a9498c801842552f59bc96522e1552a26f644":
            return
    witness = load(WITNESS)
    validate_witness(witness, verify_mac_source=opt.verify_local_source)
    data, md = build(witness)
    if opt.check:
        require(AUDIT.read_text(encoding="utf-8") == canonical(data), "audit JSON drift")
        require(REPORT.read_text(encoding="utf-8") == md, "audit markdown drift")
    else:
        AUDIT.write_text(canonical(data), encoding="utf-8")
        REPORT.write_text(md, encoding="utf-8")
    print("61 pages, 428 anchors, segments", witness["segment_count"],
          "nonatom", data["independent_nonatom_requirements"], "risks",len(data["review_risks"]))


if __name__ == "__main__":
    main()
