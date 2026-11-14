"""K00 full-page source coverage, editorial triage and tamper negatives."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch158_page_triage as page
import build_kb_batch158_scope_ledger as scope
@pytest.fixture(scope="module")
def obj():
    rows=json.loads(page.OUT.read_text(encoding="utf-8"))
    assert page.validate(rows) and page.MD.read_text(encoding="utf-8")==page.markdown(rows)
    return rows
@pytest.mark.parametrize("printed_page",range(13,74))
def test_all_61_official_printed_pages_are_source_locked_not_approvals(obj,printed_page):
    row=obj["pages"][printed_page-13]
    assert row["printed_page"]==printed_page
    assert row["pdf_page_index"]==printed_page+7
    assert len(row["source_page_sha256"])==64
    assert row["official_atom_count"] is None
    assert row["teacher_approved"]==0
    assert row["human_semantic_split_complete"] is False
    assert row["numbered_layout_markers"]==len(row["numbered_marker_ids"])
    assert row["triage_score_not_atomic_count"]>=0
@pytest.mark.parametrize("field,bad",[
    ("official_coverage_rate",1.0),("review_completed",315),
    ("teacher_approved",1),("source_pages",60),
    ("numbered_layout_markers",314),("cde_proposals_unique",33),
    ("relation_records_unique",88),("official_atom_denominators",{"COMPULSORY":315}),
])
def test_reject_fabricated_release_numbers(obj,field,bad):
    altered=copy.deepcopy(obj);altered[field]=bad
    with pytest.raises(ValueError):page.validate(altered)
@pytest.mark.parametrize("printed_page",range(13,23))
def test_reject_source_fingerprint_tampering(obj,printed_page):
    altered=copy.deepcopy(obj);altered["pages"][printed_page-13]["source_page_sha256"]="0"*64
    with pytest.raises(ValueError):page.validate(altered)
def test_61_page_conservation_and_overlap_not_added(obj):
    assert len(obj["pages"])==obj["source_pages"]==61
    assert sum(r["numbered_layout_markers"] for r in obj["pages"])==315
    assert obj["cde_proposals_unique"]==32
    assert obj["relation_records_unique"]==89
    assert obj["official_coverage_rate"] is None
    assert all(v is None for v in obj["official_atom_denominators"].values())
    assert all(x["teacher_approved"]==0 for x in obj["pages"])
    s=scope.build()
    assert s["pending_manuscripts"]==175
    assert s["historical_editorial_leads_with_unpublished_draft"]==134
    assert s["historical_editorial_leads_without_unpublished_draft"]==105
def test_source_page_report_does_not_copy_official_pdf_prose(obj):
    raw=page.MD.read_text(encoding="utf-8")
    assert "UNKNOWN" not in raw or obj["official_coverage_rate"] is None
    assert "学生端权威证据为0" in raw
    assert "课标正文" in raw
