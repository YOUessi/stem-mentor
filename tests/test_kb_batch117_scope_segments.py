"""Physical scope completeness (not mathematical syllabus completion)."""
from __future__ import annotations
from pathlib import Path
import json
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch117_scope_segments as b

def test_whole_pdf_scope_segments_are_gapless_and_cover_original():
    data,md=b.produce()
    assert len(data["pages"])==188
    assert len(data["segments"])==6
    assert [x["pdf_page_index"] for x in data["pages"]]==list(range(188))
    assert sum(x["page_count"] for x in data["segments"])==188
    assert data["old_content_range_physical_pages"]+data["outside_old_content_range_physical_pages"]==188
    assert all(x["official_atom_count"] is None for x in data["pages"])
    assert all(x["teacher_review_status"]=="NOT_REVIEWED" for x in data["pages"])
    assert data["teacher_approved_count"]==0
    assert all(x is None for x in data["official_seven_track_atom_denominators"].values())
    assert data["all_original_source_text_omitted"] is True

@pytest.mark.parametrize("i,label",[(0,"FRONT_MATTER_FOUNDATION"),(20,"CORE_CURRICULUM_CONTENT"),
(80,"CORE_CURRICULUM_CONTENT"),(81,"ACADEMIC_QUALITY"),(87,"IMPLEMENTATION_GUIDANCE"),
(107,"APPENDIX_COMPETENCY_LEVELS"),(114,"APPENDIX_TEACHING_CASES"),(187,"APPENDIX_TEACHING_CASES")])
def test_section_boundary_conservative(i,label):
    data,_=b.produce()
    assert data["pages"][i]["editorial_section_cue"]==label
    assert data["pages"][i]["official_atom_count"] is None

def test_188_page_structure_is_reproducible():
    data,md=b.produce()
    assert b.TARGET.read_text()==json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    assert b.MARKDOWN.read_text()==md
