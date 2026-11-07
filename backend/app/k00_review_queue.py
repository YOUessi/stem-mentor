"""Typed, conservative K00 progress summary for the existing student-facing API.

The detailed teacher review worklist remains an audit artifact. Student API
only sees counts and UNKNOWN denominators. Never count a worklist entry as a
verified lesson, knowledge atom, or proof of completeness.
"""

def public_review_summary():
    # Rebuild task types in-memory from pinned, validated sources. In a deployed
    # app the frozen artifact can be checked by the batch20 CI gate as well.
    from app.official_clause_audit import source_clause_ledger
    from app.official_topic_outline import de_outline
    from app.k00_gap_audit import gap_tickets
    from app.standard_scope import source_inventory
    a = source_clause_ledger()
    pages = len(a["pages"])
    markers = len(a["enumerated_source_anchors"])
    outlines = len(de_outline()["items"])
    gap = len(gap_tickets()["tickets"])
    return {
        "source_pages_needing_requirement_review": pages,
        "numbered_markers_needing_atomization": markers,
        "unnumbered_d_e_headings_needing_atomization": outlines,
        "editorial_gap_tickets_pending_verification": gap,
        "review_tasks_not_unique_atoms": pages + markers + outlines + gap,
        "editorial_objective_candidates_not_verified_atoms": len(source_inventory()["items"]),
        "official_atomic_denominator": None,
        "approved": 0,
        "student_publishable": 0,
        "complete": False,
        "notice": "Review-task counts have overlaps and are not a verified atomic curriculum denominator.",
    }
