"""Public K00 provenance-status aggregates only; never publish editorial content."""
from __future__ import annotations
import sys
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch154_scope_graph as ledger
from . import kb_batch154_index as drafts

@lru_cache(maxsize=1)
def _trusted():
    v=ledger.build()
    ledger.validate(v)
    if ledger.load(ledger.OUT)!=v:
        raise ValueError("K00 source graph on disk does not match validated source")
    if ledger.REPORT.read_text(encoding="utf-8")!=ledger.render(v):
        raise ValueError("K00 source graph report has drifted")
    return v

def public_status():
    v=_trusted()
    prior=drafts.public_coverage()
    if prior["editorial_review_manuscripts"]!=v["pending_teacher_manuscripts"] or \
       prior["editorial_candidates_linked"]!=v["linked_editorial_leads"] or \
       prior["editorial_candidates_unlinked"]!=v["missing_editorial_leads"]:
        raise ValueError("K08 editor manuscript/source coverage disagree")
    return {
        "schema":"kb154-aggregate-only-unapproved-curriculum-status/1",
        "source_pages_indexed":v["source_pages_scanned"],
        "numbered_source_markers_not_atoms":v["source_numbered_markers"],
        "cde_original_lines_classified":v["original_cde_lines_classified"],
        "cde_unnumbered_editorial_proposals_not_atoms":v["cde_proposals_from_unnumbered_sources"],
        "pending_page_scope_review":v["risk_pages"],
        "editorial_source_candidates":v["historical_editorial_leads"],
        "editorial_candidates_linked":v["linked_editorial_leads"],
        "editorial_candidates_unlinked":v["missing_editorial_leads"],
        "pending_teacher_manuscripts":v["pending_teacher_manuscripts"],
        "official_atom_denominators":v["official_atom_denominators"],
        "official_atomic_census_complete":False,
        "student_authoritative":0,
        "teacher_approved":0,
        "teacher_solution_or_copyright_source_included":False,
    }
