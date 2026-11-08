#!/usr/bin/env python3
"""K00 source-page original editorial outcomes, 2017/2020 verified original PDF.

Source: pinned original PDF; page numbers are PRINTED page numbers.
No copyrighted paragraphs, teacher approvals, official atom denominator,
and no student-visible answers are generated. K00 remains incomplete.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch31_atomic_core as previous

SEED = ROOT / "curriculum/highschool_math/k00_batch32_compulsory_selective_editorial.tsv"
OUT = ROOT / "docs/evaluation/KB_BATCH32_K00_CORE_SELECTIVE_ATOM_AUDIT.json"
SEED_SHA = "a851ae8ece74bfb33be0f080c635af6df52252a73b8ff7536e0118a928a98140"
PDF_SHA = previous.SOURCE_SHA
TRACKS = previous.TRACKS
PAGE_DIGESTS = dict(
    map(lambda s: (int(s.split("|")[0]), s.split("|")[1]), """29|b4198b0124ace029689a159a998206875be39465a84ef9f7f04c7a414e25349b
30|f393a2b0a62c61607e45dd7b9377ab3aa0e5052614555c7eb0bbd3515dd3a628
31|ddc3ece205c0269433ed41a771096e141e54fb10f4f452bd76615abae40de5f8
32|abe78b98d11dc60d9ac22fa8fe60c8171fb24d02b20a36aa7cd434a5a21a8fab
33|3abfd137d79c1e7e80cc644058511d60fd626fd3820b001968155879b258d6f8
34|d317c98a5b3ddd742d4b820dcf67d242472e879dd390f08a6ea5862c650f2962
35|adc54b4b4665ce3e08257ced12d04a40ad83ac5458f17f7b84bf23450b22a399
36|d267a92ba3997508065d9e2201624364302b4422fd56d2356011bf83cd895171
37|a9ff3f2978a3b63938207e275bc30cefe260d1073a885d323286c07bf44160fe
38|6d4df3bcd06b7d11fceec5475141ef45e27dda72677ad91283864dcc0a0c1c42
39|6a8d2c2a817c54a115c091f59224fd946078a67f7c8d398cd0f43be414f67393
40|cd603e94de558105c35d7cb22184822f66fd8517958f174ceeda265d4fcb3c55
41|132d3ebd256f5abb5ca9bce8faeba0a4fd0b17becf058c08a7003fb21c90ca80
42|6c429e184659d90d001bc2fd3c6796eeef521a3e4dad6d010aebf2a8fe8518f2
43|a78c1f5a04e31cbd3aac458ad29c31ac907b0cdecf171c2a0dbb1d51c3b0d50e
44|afed8d69b6b9569413bd4e6d642490096ec4717cb381b4ab7caff88e522de933
45|a8c307553da2a2e2d45b34a577d868158cf93731ad85e4cde71cc065bad1c504
46|b32d78e2ddc66651942d447957b3445e714ee286a7cb031e0c7579a9248696d6
47|065f9961bde333d41342d9a72bf4a649957da7cc164036286848553ff8abda15
48|224ebcf2165b5b659e8a3da26d48701656ae2e83b533708c3bccc314295e3aad
49|1beccf575a81912ea9738cf46c29e2e988b9e11ebbb443b3b5409029f9bf3d48
50|6428f8ae0e5f89047c73cfbc04822b49bd83b656b908ca7e27ec5e6979f05d4c""".splitlines())
)
STARRED_GOALS = {
    (38, "使用基例和归纳蕴含两部分证明简单数列恒等式"),
    (40, "围绕微积分历史人物和方法形成有来源的简要研究报告"),
    (44, "使用可溯源材料梳理解析几何形成过程并区分史实与推测"),
    (47, "对正概率条件使用全概率分母反推假设的条件概率"),
}
UNCERTAIN_SOURCE_PAGES = {35,36,37,49}
KINDS = {"concept", "theorem", "method"}

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def parse_seed(seed: str) -> list[tuple]:
    out = []
    seen = set()
    for raw in seed.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) != 6:
            raise ValueError("K00 seed must contain six editorial fields")
        pg, track, topic, kind, starred, goal = parts
        if not pg.isdecimal() or int(pg) not in PAGE_DIGESTS:
            raise ValueError("K00 seed page not inspected on Mac")
        pg = int(pg)
        exp = "COMPULSORY" if pg <= 35 else "SELECTIVE_COMPULSORY"
        if track != exp or kind not in KINDS or starred not in {"Y", "N"}:
            raise ValueError("K00 track/type/star value invalid")
        if pg in UNCERTAIN_SOURCE_PAGES:
            raise ValueError("K00 this page not independently usable for atomic goals")
        if (starred == "Y") != ((pg,goal) in STARRED_GOALS):
            raise ValueError("K00 optional marker must match anchored editorial item")
        if not 2 <= len(topic) <= 45 or not 14 <= len(goal) <= 130:
            raise ValueError("K00 short or oversized editorial outcome")
        if any(c in goal for c in ("\x00", "\n", "\r")) or "普通高中数学课程标准" in goal:
            raise ValueError("K00 unsafe copied/source content")
        if goal in seen:
            raise ValueError("K00 repeated learning goal")
        seen.add(goal)
        out.append((pg,track,topic,kind,starred == "Y",goal))
    if not out or [r[0] for r in out] != sorted(r[0] for r in out):
        raise ValueError("K00 seed missing or pages out of order")
    return out

def build(seed: str | None = None, ledger: dict | None = None) -> str:
    if seed is None:
        if sha(SEED.read_bytes()) != SEED_SHA:
            raise ValueError("Pinned original editorial seed drift; independent re-review required")
        seed = SEED.read_text(encoding="utf-8")
    frozen = previous.read_ledger()
    if ledger is not None and ledger != frozen:
        raise ValueError("Injected source ledger substitution")
    pages = {p["printed_page"]:p for p in frozen["pages"]}
    base = json.loads(previous.REPORT.read_text(encoding="utf-8"))
    if base != json.loads(previous.build()):
        raise ValueError("Previous 87-atom audit changed")
    if len(base["items"]) != 87 or any(x["student_publishable"] for x in base["items"]):
        raise ValueError("Previous candidate publication status invalid")
    rows = parse_seed(seed)
    counters = Counter()
    items = []
    for pg,track,topic,kind,starred,goal in rows:
        p = pages[pg]
        if p["tracks_present"] != [track] or p["pdf_page_index"] != pg + 7:
            raise ValueError("Candidate page and track do not match pinned original ledger")
        counters[pg] += 1
        items.append(dict(
            editorial_id=f"KB32-{track[:4]}-P{pg:03d}-A{counters[pg]:03d}",
            syllabus_track=track,source_printed_page=pg,source_pdf_page_index_zero_based=pg+7,
            source_original_pdf_sha256=PDF_SHA,
            source_pypdf_extracted_page_sha256=p["pdf_text_sha256"],
            source_mac_pdfkit_page_sha256=PAGE_DIGESTS[pg],
            source_anchor_level="PAGE_ONLY_NUMBERED_AND_UNNUMBERED_CLAUSES_NOT_VERIFIED",
            topic_editorial_label=topic,knowledge_type_editorial_candidate=kind,
            optional_starred=starred,original_project_authored_goal=goal,
            official_atom_id=None,official_clause_alignment_verified=False,
            teacher_review="PENDING",math_proof_certification="NOT_FORMALLY_VERIFIED",
            knowledge_unit_status="EDITORIAL_PROPOSAL_ONLY",
            approved_lesson_id=None,student_publishable=False,
            student_solution_visibility="NONE"))
    all_ids = {x["id"] for x in base["items"]} | {x["editorial_id"] for x in items}
    if len(all_ids) != len(base["items"]) + len(items):
        raise ValueError("Cross-batch editorial candidate ID collision")
    if len({x["original_project_authored_outcome"] for x in base["items"]} |
           {x["original_project_authored_goal"] for x in items}) != len(base["items"]) + len(items):
        raise ValueError("Cross-batch duplicated learning goal")
    if any(x["teacher_review"] != "PENDING" or x["student_publishable"] or
           x["official_atom_id"] is not None or x["approved_lesson_id"] is not None for x in items):
        raise ValueError("Student release or teacher approval forgery")
    new_track_counts = Counter(x["syllabus_track"] for x in items)
    track_counts = dict(base["by_track_editorial_candidate_counts"])
    for track,n in new_track_counts.items():
        track_counts[track] += n
    # This is a *source inspection* count, not a numbered/unnumbered requirement audit.
    base_examined = {p["printed_page"] for p in base["pages"]
                     if p["content_inspection"] != "AWAITING_ORIGINAL_CONTENT_INSPECTION"}
    newly_text_examined = sorted(set(PAGE_DIGESTS) - base_examined)
    scope_pages = set(range(13,74))
    inspected = base_examined | set(PAGE_DIGESTS)
    no_candidate_text_pages = sorted(set(PAGE_DIGESTS) - {r[0] for r in rows})
    by_page = []
    for pg in sorted(scope_pages):
        state = ("ASSISTANT_RENDERED_PRIOR_BATCH" if pg in previous.ASSISTANT_VISUALLY_INSPECTED
            else "MAC_PDFKIT_TEXT_INSPECTED_BATCH32" if pg in PAGE_DIGESTS
            else "MAC_PDFKIT_TEXT_PRIOR_BATCH" if pg in base_examined
            else "NOT_CONTENT_INSPECTED")
        by_page.append(dict(printed_page=pg,track_candidates=pages[pg]["tracks_present"],
            inspection_state=state,new_editorial_candidates=counters.get(pg,0),
            mac_pdfkit_text_sha256=PAGE_DIGESTS.get(pg),
            original_teacher_page_review="PENDING",
            unnumbered_clause_completeness="UNKNOWN",
            official_atom_count=None))
    summary=dict(
        pinned_original_pdf_sha256=PDF_SHA,
        source_scope_pages=len(scope_pages),mac_pdfkit_text_pages_new=len(newly_text_examined),
        page_inspected_earlier=len(base_examined),
        unique_pages_text_or_image_examined=len(inspected),
        pages_remaining_without_content_inspection=len(scope_pages-inspected),
        new_editorial_atom_candidates=len(items),
        batch31_editorial_candidates=len(base["items"]),
        total_provisional_editorial_candidates=len(base["items"])+len(items),
        by_track_partial_editorial_counts=track_counts,
        pages_with_new_candidates=len(counters),
        new_text_inspected_pages_without_new_atoms=no_candidate_text_pages,
        source_page_35_pdfkit_corrupt_requires_visual_review=True,
        official_atom_denominator=None,official_coverage_rate=None,
        teacher_verified_curriculum_atoms=0,teacher_approved_lessons=0,
        student_published_deep_lessons=0)
    return json.dumps(dict(
        schema_version="kb-batch32-partial-source-editorial-atom-audit-v1",
        scope="PARTIAL_COMPULSORY_SELECTIVE_COMPULSORY_SOURCE_INSPECTION_ONLY",
        source=dict(version="2017-edition-2020-revision",pdf_sha256=PDF_SHA,
                    pdf_total_pages=188,source_scope_printed_pages=[13,73],
                    source_pypdf_extract_sha256=sha(previous.LEDGER.read_bytes()),
                    batch32_editorial_seed_sha256=SEED_SHA,
                    original_pdf_copyrighted_source_not_committed=True),
        summary=summary,official_denominators_by_track={t:None for t in TRACKS},
        pages=by_page,new_items=items,
        high_priority_unresolved=[
            "Printed p35 contains control-character garbage in PDFKit text: must be independently visually checked before atomizing any unreadable graphic.",
            "Printed pp36-37 and 49 are introduction/learning expectations: source-inspected but no stand-alone knowledge atoms asserted.",
            "Printed pp13-14 and 51-73 require additional inspection and source clause mapping; even inspected pages may contain additional unnumbered clauses.",
            "Page-level hashes are not exact text-to-outcome proof; each editorial candidate still requires independent clause mapping and authentic teacher review.",
            "Neither 315 nor 317 numbered marker occurrences nor 217 editorial proposals are an official atom denominator."],
        evidence_boundary=dict(
            curriculum_requirements_exhaustively_decomposed=False,
            numbered_and_unnumbered_requirements_all_mapped=False,
            formal_math_proofs_verified=False,authentic_teacher_review=False,
            student_api_modified=False),
        ),ensure_ascii=False,indent=2)+"\n"

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--check",action="store_true")
    a.add_argument("--pdf",type=Path)
    a.add_argument("--pdfkit-digests",type=Path)
    args=a.parse_args()
    if args.pdf is not None and sha(args.pdf.read_bytes()) != PDF_SHA:
        raise ValueError("Original official PDF hash mismatch")
    if args.pdfkit_digests is not None:
        lines=args.pdfkit_digests.read_text().splitlines()
        got={int(t[0]):t[1] for s in lines if (t:=s.split("|")) and len(t)==3}
        if got != PAGE_DIGESTS:
            raise ValueError("Independent Mac PDFKit source-page extraction hash drift")
    output=build()
    if args.check:
        if OUT.read_text(encoding="utf8") != output:
            raise SystemExit("Batch32 K00 source audit report drift")
    else:
        OUT.write_text(output,encoding="utf8")
    s=json.loads(output)["summary"]
    print("PASS K00 Batch32",s["new_editorial_atom_candidates"],
          "new editorial candidates,",s["unique_pages_text_or_image_examined"],
          "source pages inspected; official syllabus denominators NULL")

if __name__ == "__main__":
    main()
