"""Append independent, explicitly non-official A/B candidate engineering nodes.

Never inflate these editorial candidates into a verified official course denominator.
"""
from copy import deepcopy
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
CANDIDATES=HERE/"elective_a_b_atomic_candidates_batch14.json"

def apply(rows):
    new=json.loads(CANDIDATES.read_text(encoding="utf-8"))
    original_ids={r["id"] for r in rows}
    if len(new)!=16 or len({r["id"] for r in new})!=16 or any(r["id"] in original_ids for r in new):
        raise ValueError("Elective candidate engineering IDs duplicated or incomplete")
    if any(r["source"]["teacher_review"]!="PENDING" or r["source"]["mapping_type"]!="ENGINEERING_INTERPRETATION" for r in new):
        raise ValueError("Never imply official certification of authored curriculum candidates")
    return rows+deepcopy(new)
