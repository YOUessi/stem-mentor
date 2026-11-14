"""Editorial C/D/E source boundaries: public counts only, never original text or draft claims."""
from __future__ import annotations
import json
import sys
from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch150_de_boundary as boundary

@lru_cache(maxsize=1)
def public_status():
    v=json.loads(boundary.OUT.read_text(encoding="utf-8"))
    boundary.validate(v)
    return dict(
        scope="PROVISIONAL_EDITORIAL_C_D_E_LINE_CLASSIFICATION_NOT_OFFICIAL_ATOM_CENSUS",
        source_document_version="2017_REVISED_2020",
        source_line_counts=dict(v["source_line_counts"]),
        preliminary_semantic_topic_proposals=v["proposed_count"],
        school_elective_examples_only=True,
        source_c_to_d_boundary={"printed_page":69,"source_line":6},
        source_d_to_e_boundary={"printed_page":73,"source_line":13},
        approved_atom_denominators={t:None for t in boundary.TRACKS},
        official_course_coverage_rate=None,
        source_line_assignment_teacher_approved=False,
        teacher_approved=0,student_authoritative=0,
        student_evidence_status="NO_APPROVED_EVIDENCE",
        licensed_syllabus_text_included=False,
        teacher_solution_or_manuscript_included=False)
