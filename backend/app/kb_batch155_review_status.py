"""Safe K00 aggregate status. Never returns source excerpts or teacher solutions."""
from __future__ import annotations
import json,sys
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch155_review_matrix as matrix

@lru_cache(maxsize=1)
def _trusted_matrix():
    live=matrix.build()
    matrix.validate(live)
    if json.loads(matrix.OUT.read_text(encoding="utf-8"))!=live:
        raise ValueError("KB155 source metadata drift, refusing public status")
    if matrix.REPORT.read_text(encoding="utf-8")!=matrix.render(live):
        raise ValueError("KB155 review report drift, refusing public status")
    return live

def public_status():
    m=_trusted_matrix()
    return dict(schema="kb155-safe-status-aggregate/1",
        numbered_source_markers_not_atoms=m["numbered_source_layout_markers"],
        unnumbered_CDE_proposals_not_atoms=m["independent_CDE_unnumbered_proposals"],
        editorial_source_leads_not_atoms=m["historical_editorial_leads"],
        pending_teacher_manuscripts_not_approved=m["teacher_only_manuscripts"],
        source_pages_indexed=m["printed_source_pages"],
        unpaired_numbered_markers=sum(
            v["numbered_markers_without_any_line_overlap"] for v in m["by_track"].values()),
        pending_source_semantic_relation_records=m["historical_pending_source_relation_records"],
        missing_editorial_deep_manuscript_leads=m["editorial_leads_missing_teacher_only_drafts"],
        official_atom_denominators=m["official_atom_denominators"],
        official_completion_rate=None,
        human_source_semantic_review_complete=False,
        teacher_approved=0,student_authoritative=0,
        original_source_text_included=False,teacher_solutions_included=False)
