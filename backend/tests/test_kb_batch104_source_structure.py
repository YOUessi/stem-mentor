"""K00 source structural gaps: exact page coverage and non-authoritative gates."""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch104_source_structure as B

def test_all_pdfkit_lines_on_three_pages_have_original_editorial_classification():
    r=B.build()
    assert r["source_pages"]==[13,14,51]
    assert r["source_page_line_counts"]=={"13":17,"14":32,"51":27}
    assert r["covered_pdfkit_lines"]==76 and r["decision_count"]==12
    assert sum(r["kind_counts"].values())==12
    assert r["zero_numbered_source_anchors_is_not_zero_mathematical_scope"] is True
    assert r["cross_page_requirement_pending"]==[14,51]
    assert r["teacher_fully_atomized_pages"]==0
    assert r["student_authoritative_releases"]==r["teacher_approved"]==0
    assert all(v is None for v in r["official_atom_denominators_by_track"].values())
    assert len(r["official_atom_denominators_by_track"])==7
    assert all(row["teacher_review_status"]=="REVIEW_PENDING"
               and row["official_atom_count"] is None
               and row["official_atom_id"] is None
               and not row["source_complete_math_atomization"]
               and not row["student_authoritative"]
               for row in r["editorial_decisions"])

@pytest.mark.parametrize("page",B.PAGES)
def test_local_mac_source_pdfkit_line_hashes_match_pinned_repo_fingerprints(page):
    # GitHub runners do not have the original copyright-protected Mac PDF.
    # CI still checks pinned source-registry hashes and the generated audit.
    if not B.PDF.is_file() or not (B.LOCALLINES/f"kb56_page_{page}.txt").is_file():
        pytest.skip("Mac-only pinned PDFKit source evidence unavailable on this runner")
    report=B.build(verify_local_pdf=True)
    items=[x for x in report["editorial_decisions"] if x["printed_page"]==page]
    assert items
    raw=(B.LOCALLINES/f"kb56_page_{page}.txt").read_bytes()
    assert sha256(raw).hexdigest()==items[0]["pdfkit_page_sha256"]
    assert all(x["source_pdf_sha256"]==B.SOURCE_PDF_SHA256 for x in items)

@pytest.mark.parametrize("mutation",[
 "missing_range", "overlap", "reordered", "page_out_of_scope",
 "unknown_kind", "unknown_track", "false_track", "empty_explanation",
 "invalid_line", "duplicate_span", "no_source_continuation"
])
def test_source_structure_builder_refuses_forged_missing_or_unbounded_edits(mutation):
    data=list(deepcopy(B.SECTIONS))
    if mutation=="missing_range":
        p=list(data[1]);p[1]+=1;data[1]=tuple(p)
    elif mutation=="overlap":
        p=list(data[1]);p[1]-=1;data[1]=tuple(p)
    elif mutation=="reordered":
        data[0],data[1]=data[1],data[0]
    elif mutation=="page_out_of_scope":
        p=list(data[2]);p[0]=52;data[2]=tuple(p)
    elif mutation=="unknown_kind":
        p=list(data[2]);p[4]="OFFICIAL_ATOM";data[2]=tuple(p)
    elif mutation=="unknown_track":
        p=list(data[2]);p[3]="ELECTIVE_F";data[2]=tuple(p)
    elif mutation=="false_track":
        p=list(data[2]);p[3]="ELECTIVE_A";data[2]=tuple(p)
    elif mutation=="empty_explanation":
        p=list(data[2]);p[5]="";data[2]=tuple(p)
    elif mutation=="invalid_line":
        p=list(data[2]);p[1]=0;data[2]=tuple(p)
    elif mutation=="duplicate_span":
        data[3]=data[2]
    else:
        p=list(data[-1]);p[4]="TEACHER_APPROVED";data[-1]=tuple(p)
    with pytest.raises((ValueError,StopIteration)):
        B.build(tuple(data))

def test_deterministic_audit_and_original_markdown_no_copied_standard_passages():
    r=B.build()
    assert B.OUT.read_text(encoding="utf8")==B.canonical(r)
    assert B.MD.read_text(encoding="utf8")==B.markdown(r)
    assert "UNKNOWN" in B.MD.read_text(encoding="utf8")
    assert all(len(s["original_editorial_paraphrase"])>14 for s in r["editorial_decisions"])
    assert r["source_pdf_sha256"]==B.SOURCE_PDF_SHA256
    assert r["source_page_fingerprints_sha256"]==sha256(B.FINGERPRINTS.read_bytes()).hexdigest()
    assert r["source_partition_sha256"]==sha256(B.SEGMENTS.read_bytes()).hexdigest()

def test_p51_elective_a_transition_is_not_accidental_elective_e_atom_count():
    r=B.build()
    parts=[s for s in r["editorial_decisions"] if s["printed_page"]==51]
    assert [x["track_scope"] for x in parts]==[
        "ELECTIVE_GENERAL","ELECTIVE_GENERAL","ELECTIVE_GENERAL",
        "ELECTIVE_A","ELECTIVE_A"]
    assert parts[-1]["cross_page_followup_required"] is True
    assert parts[-1]["structural_class"]=="CROSS_PAGE_CONTENT_OPENING"
    assert r["official_atom_denominators_by_track"]["ELECTIVE_E"] is None
