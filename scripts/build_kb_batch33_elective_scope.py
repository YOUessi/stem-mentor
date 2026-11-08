#!/usr/bin/env python3
"""Source-attested *editorial* electives A-E goals after Mac PDFKit content inspection.

Page-text hashes attest inspected source versions, not exact clause alignment,
mathematical truth, exhaustive enumeration, or teacher approval. The PDF itself
is deliberately not committed. E is open-ended locally developed curriculum.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch31_atomic_core as b31
import build_kb_batch32_source_atoms as b32

SOURCE=b31.SOURCE_SHA
SEED=ROOT/"curriculum/highschool_math/k00_batch33_elective_editorial.tsv"
REPORT=ROOT/"docs/evaluation/KB_BATCH33_ELECTIVE_SCOPE_AUDIT.json"
SEED_SHA="ad5b47d8aac24142ed5256eb238fad31256892c3ce65b2b6d70b512d99e5e7c4"
PDFKIT_PAGES=dict([
    (int(a),b) for line in """13|81eb58d96c63216762c58ffd4eae16a71f0c01262004c0e74932b6703c044e51
14|ce9fb625a4943a9e2cf8a67fd11cf9ef79f553dff8a7dbedfd803f1ef3c85c86
51|cf8d0e22ddc895499d3af33c0f3742d84af2d081c14050d01b31d68cce4c7335
52|80d2633ed69158a2bd4de8ab2a22c0eae71f3960473df9a88a522d028b2d585f
53|ae9e0d41b2c8f7ac33b967ff6c40ae2a875322373c7e8470ddce25838b929d3b
54|ae70a020497b64f1dea5548a386155c99213f145763073e493f49e0a6ceae1c8
55|b5aa0c8af2feebe5502df4e06ffc98719dd5b4eb2af270798f7431d68b5db5d0
56|2c3f24cab964ee1d79c58e1feb6f21f5bc5867a124934f7e5858cf0cc026f93b
57|dca127ce9bc7a223440713495ea73ba89e2654586fda16bab4dcf465d648f2f2
58|e119d314a74926dfadf4794e35ab3a665662ee3ec29ddcb3a119baaba50dcb7f
59|25cef7034650de2cdafb41e1b4bfdd895acb37c33cab7c939bfb57d7c84416dd
60|d353bd34002755a1ce77049c025851ef8af082fc5b4448e3c2725b3aaceffecf
61|c1828acf860fc1df7636a12b7f0a81c651be1673c10fc77991372d8c48fd851e
62|de2e8b994e242961359f2d5103f190b19c34ca307c84401b3259a457db365563
63|fe59743fdb65ba32a2778ce3e07e475946acbd6c9cc9a0f2d5b7839f58b17608
64|66ab74e49d2ed82487dc1ffd13864fb7f849f66c9d333354256ae9ab8d5fc81e
65|603c130ef7943eab9b85fb3a21dbd3937756a4737d3f7295886d4e0dc71616c5
66|61e51f81f6e99f1d29b4a38a373e9ef30c4f29846fc5d5f06abb1fd63a6cfbcb
67|1599fef264d80525a1633a61cbb419d81f6c3a88a36b59a254cb8ae9233c03a8
68|0991c86f2c3a6ff73b865092ce216abc8179ebb608b85130e44ea3960b02788c
69|2513690c1d4d0d539a2eeec0fd496ebbd1c7843f23841591857767b69634ab99
70|d0bea6643a57a6eaf4efcd8d92ab673ba09f594445a7a82718523ec14a331bcc
71|43917c317055b7ccca0233d3ad366b72d2a102879d312b6ef3f0ea15d88f08b8
72|9c0f82350e1e496246c4d631cb4714e7cfb0e20338e90b2fe9d2b84e1f1e5179
73|59980de5ee6959de6e1f635ff7a17abd29206e852bbdd2bd18b818135773a6a3""".splitlines() for a,b in [line.split("|")]
])
KINDS={"concept","method","theorem"}
# Independently inspected section transitions (first B p57, first C p64,
# first D p69, E open-ended local examples at end of p73). Not official IDs.
def allowed_tracks(page: int)->set[str]:
    if 52<=page<=56:return {"ELECTIVE_A"}
    if page==57:return {"ELECTIVE_A","ELECTIVE_B"}
    if 58<=page<=63:return {"ELECTIVE_B"}
    if page==64:return {"ELECTIVE_B","ELECTIVE_C"}
    if 65<=page<=68:return {"ELECTIVE_C"}
    if page==69:return {"ELECTIVE_C","ELECTIVE_D"}
    if 70<=page<=72:return {"ELECTIVE_D"}
    if page==73:return {"ELECTIVE_D","ELECTIVE_E"}
    return set()
# Mixed-section page safeguards: do not allow an arbitrary topic to exploit
# two allowed tracks on one page. Exact topic IDs are editorial, not official.
BOUNDARY_TOPIC={
 (57,"ELECTIVE_A"):{"参数估计","假设检验","拟合优度","多元回归"},
 (64,"ELECTIVE_B"):{"周期模型","参数曲线","空间曲线"},
 (64,"ELECTIVE_C"):{"逻辑推理"},
 (69,"ELECTIVE_C"):{"调查报告"},
 (69,"ELECTIVE_D"):{"数学审美"},
 (73,"ELECTIVE_D"):{"运动轨迹","赛事安排","运动统计"},
 (73,"ELECTIVE_E"):{"差分模型选题","球面几何选题","机器人数学选题","日常理财选题"},
}
def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
def parse(text:str)->list[tuple]:
    rows=[]; seen=set()
    for raw in text.splitlines():
        if not raw.strip() or raw.startswith("#"):continue
        parts=[p.strip() for p in raw.split("|")]
        if len(parts)!=5:raise ValueError("Need five source/editorial fields")
        pg,track,topic,kind,goal=parts
        if not pg.isdecimal() or int(pg) not in PDFKIT_PAGES or not 52<=int(pg)<=73:
            raise ValueError("No inspected elective source content on selected page")
        pg=int(pg)
        if track not in allowed_tracks(pg) or kind not in KINDS:
            raise ValueError("Track/kind mismatch with original elective section")
        if (pg,track) in BOUNDARY_TOPIC and topic not in BOUNDARY_TOPIC[(pg,track)]:
            raise ValueError("Mixed-page section topic not independently attested")
        if not 2<=len(topic)<=45 or not 16<=len(goal)<=140 or any(ch in goal for ch in "\n\r\x00"):
            raise ValueError("Unsafe or incomplete original editorial objective")
        if "普通高中数学课程标准" in goal or goal in seen:
            raise ValueError("Copied source title or repeated editorial objective")
        if track=="ELECTIVE_E" and not topic.endswith("选题"):
            raise ValueError("Elective E is open-ended local exemplar, not mandatory unit")
        seen.add(goal)
        rows.append((pg,track,topic,kind,goal))
    if len(rows)<70 or [r[0] for r in rows]!=sorted(r[0] for r in rows):
        raise ValueError("Not a substantive page-ordered elective audit")
    if set(r[1] for r in rows)!={f"ELECTIVE_{c}" for c in "ABCDE"}:
        raise ValueError("Elective A-E tracks not all represented")
    return rows

def build(seed:str|None=None, ledger:dict|None=None)->str:
    if seed is None:
        if sha(SEED)!=SEED_SHA:raise ValueError("Pinned original editorial seed drift")
        seed=SEED.read_text(encoding="utf-8")
    original=b31.read_ledger()
    if ledger is not None and ledger!=original:raise ValueError("Source ledger substitution refused")
    if json.loads(b31.REPORT.read_text(encoding="utf-8"))!=json.loads(b31.build()):
        raise ValueError("Prior source audit 31 drift")
    if json.loads(b32.OUT.read_text(encoding="utf-8"))!=json.loads(b32.build()):
        raise ValueError("Prior source audit 32 drift")
    source={p["printed_page"]:p for p in original["pages"]}
    rows=parse(seed)
    pages_inspected=set(PDFKIT_PAGES)
    previous_pages={p["printed_page"] for p in json.loads(b32.OUT.read_text())["pages"]
        if p["inspection_state"]!="NOT_CONTENT_INSPECTED"}
    if len(previous_pages)!=37 or len(previous_pages|pages_inspected)!=61:
        raise ValueError("Coverage count drift; page scope no longer trustworthy")
    counter=defaultdict(int)
    items=[]
    for page,track,topic,kind,goal in rows:
        ledger_page=source[page]
        if track not in ledger_page["tracks_present"] or ledger_page["pdf_page_index"]!=page+7:
            raise ValueError("Source-page association/track mismatch")
        counter[page]+=1
        items.append(dict(editorial_id=f"KB33-{track[-1]}-P{page:03d}-A{counter[page]:03d}",
            syllabus_track=track,source_printed_page=page,source_pdf_index_zero_based=page+7,
            source_original_pdf_sha256=SOURCE,source_pypdf_page_sha256=ledger_page["pdf_text_sha256"],
            source_mac_pdfkit_page_sha256=PDFKIT_PAGES[page],
            topic_editorial_label=topic,knowledge_type_editorial_candidate=kind,
            original_project_authored_goal=goal,
            source_anchor_level="PAGE_SECTION_ONLY_NOT_INDIVIDUAL_CLAUSE_VERIFIED",
            elective_E_local_exemplar_not_nationally_mandated=track=="ELECTIVE_E",
            official_atom_id=None,official_clause_alignment_verified=False,
            teacher_review="PENDING",math_proof_certification="NOT_FORMALLY_VERIFIED",
            knowledge_unit_status="EDITORIAL_PROPOSAL_ONLY",approved_lesson_id=None,
            student_publishable=False,student_solution_visibility="NONE"))
    if len({x["editorial_id"] for x in items})!=len(items):
        raise ValueError("Editorial id collision")
    prior31=json.loads(b31.REPORT.read_text())["items"]
    prior32=json.loads(b32.OUT.read_text())["new_items"]
    prior_text=[x["original_project_authored_outcome"] for x in prior31]+[
        x["original_project_authored_goal"] for x in prior32]
    if len(set(prior_text+[x["original_project_authored_goal"] for x in items]))!=len(prior_text)+len(items):
        raise ValueError("Duplicated core/elective editorial learning objective")
    if any(x["teacher_review"]!="PENDING" or x["student_publishable"] or x["official_atom_id"] is not None
           or x["approved_lesson_id"] is not None for x in items):
        raise ValueError("No teacher forgery or student publication")
    count_by_track=Counter(x["syllabus_track"] for x in items)
    cumulative=dict(json.loads(b32.OUT.read_text())["summary"]["by_track_partial_editorial_counts"])
    for k,v in count_by_track.items():cumulative[k]+=v
    page_rows=[]
    for page in range(13,74):
        page_rows.append(dict(printed_page=page,track_candidates=source[page]["tracks_present"],
            pdf_index_zero_based=page+7,mac_pdfkit_digest=PDFKIT_PAGES.get(page) or b32.PAGE_DIGESTS.get(page),
            batch33_text_inspected=page in pages_inspected,
            page35_damaged_visual_source_pending=(page==35),
            original_teacher_page_review="PENDING",unnumbered_clause_completeness="UNKNOWN",
            official_atom_count=None,new_editorial_candidates=counter[page]))
    report=dict(schema_version="kb-batch33-elective-page-editorial-v1",
        scope="FULL_61_PAGE_PDFKIT_TEXT_FIRST_PASS_NOT_COMPLETE_ATOMIC_CURRICULUM",
        original_pdf=dict(version="2017-edition-2020-revision",sha256=SOURCE,total_pdf_pages=188,
            source_scope_printed_pages=[13,73],pdf_binary_not_committed=True,
            original_pdf_byte_verified_on_mac=True,batch33_editorial_seed_sha256=SEED_SHA),
        summary=dict(scope_source_pages=61,previous_pages_inspected=37,
            new_pages_inspected_text=24,total_pages_inspected_text_or_visual=61,
            remaining_uninspected_pages=0,remaining_pages_not_exhaustively_clause_mapped=61,
            batch33_editorial_candidates=len(items),prior_editorial_candidates=len(prior_text),
            all_provisional_editorial_candidates=len(prior_text)+len(items),
            batch33_track_counts={t:count_by_track[t] for t in b31.TRACKS},
            cumulative_provisional_track_counts=cumulative,
            official_atomic_denominator=None,official_coverage_rate=None,
            teacher_verified_atomic_goals=0,teacher_approved_lessons=0,student_published_deep_lessons=0),
        official_denominators_by_track={t:None for t in b31.TRACKS},
        inspected_page_digests={str(k):v for k,v in sorted(PDFKIT_PAGES.items())},
        pages=page_rows,editorial_goals=items,
        high_priority_unresolved=[
            "61/61 pages have at least first-pass PDFKit text/image inspection; none has complete numbered and unnumbered clause-to-atom verification.",
            "Printed page 35 PDFKit output was corrupt around an embedded graphic; genuine visual check remains pending.",
            "E elective is school-defined and includes non-exhaustive exemplars, not a nationally fixed atomic denominator.",
            "Page 57/64/69/73 cross elective track transitions need independent human exact-clause mapping.",
            "Neither 315 nor 317 numbered marker occurrences nor any editorial proposal count is an official atomic denominator."],
        evidence_boundary=dict(numbered_and_unnumbered_requirements_all_mapped=False,
            teacher_approved=False,math_certified=False,student_api_modified=False))
    return json.dumps(report,ensure_ascii=False,indent=2)+"\n"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--pdf",type=Path)
    p.add_argument("--pdfkit-digests",type=Path)
    a=p.parse_args()
    if a.pdf is not None and sha(a.pdf)!=SOURCE:raise ValueError("Live original PDF sha mismatch")
    if a.pdfkit_digests is not None:
        lines=a.pdfkit_digests.read_text(encoding="utf-8").splitlines()
        got={}
        for line in lines:
            row=line.split("|")
            if len(row)==3 and row[0].isdecimal():
                got[int(row[0])]=row[1]
        if got!=PDFKIT_PAGES:raise ValueError("Live Mac PDFKit page digest mismatch")
        if not any(line=="SOURCE_SHA|"+SOURCE for line in lines):
            raise ValueError("PDFKit digest stream lacks pinned source SHA")
    val=build()
    if a.check:
        if REPORT.read_text(encoding="utf-8")!=val:
            raise SystemExit("Batch33 elective scope audit drift")
    else:
        REPORT.write_text(val,encoding="utf-8")
    s=json.loads(val)["summary"]
    print("PASS Batch33",s["batch33_editorial_candidates"],"elective editorial goals; source pages 61/61 first-pass, official denominator remains null")
if __name__=="__main__":main()
