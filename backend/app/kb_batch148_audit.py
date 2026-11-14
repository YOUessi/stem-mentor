"""K00/K07 public aggregate only; never publish unreviewed content to learners."""
from __future__ import annotations
import sys
from functools import lru_cache
from pathlib import Path
from . import kb_batch147_index as previous

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch148_official_clause_gate as k00
import review_kb_batch148_conflicts as k07

@lru_cache(maxsize=1)
def _audits():
    c=k00.build();proof=k07.build()
    k00.validate_report(c);k07.validate(proof)
    if k00.read(k00.OUT)!=c or k07.json.loads(k07.OUT.read_text(encoding="utf-8"))!=proof:
        raise ValueError("published K00/K07 audit drift")
    return c,proof

def public_status():
    c,p=_audits()
    return dict(
       scope="SOURCE_METADATA_ONLY_NOT_OFFICIAL_CURRICULUM_COMPLETENESS",
       source_numbered_markers=c["source_numbered_marker_count"],
       source_pages=c["source_scan_pages"],
       provisional_atom_proposals=c["provisional_atom_proposal_count"],
       historical_editorial_leads=c["historical_editorial_leads"],
       unpublished_teacher_review_manuscripts=c["teacher_pending_manuscripts"],
       by_track={t:dict(numbered_source_markers=v["numbered_source_markers"],
           provisional_atom_proposals=v["source_proposal_rows"],
           editorial_leads=v["editorial_leads"],
           pending_manuscripts=v["deep_teacher_pending_drafts"],
           official_atom_denominator=None) for t,v in c["by_track"].items()},
       official_atom_denominators=c["official_atom_denominators"],
       official_course_coverage_rate=None,
       unresolved_math_conflicts=p["conflicts_total"],
       bounded_conflict_math_witnesses=p["independent_exact_cases"],
       general_proof_certificates=0,
       teacher_approved=0,student_authoritative=0,
       student_solution_exposed=False,
       draft_content_exposed=False,
       syllabus_text_exposed=False)

def student_evidence_lookup(query, *, limit=8):
    # Previous layer checks inputs and returns no evidence until a genuine teacher review.
    return previous.student_evidence_lookup(query,limit=limit)
