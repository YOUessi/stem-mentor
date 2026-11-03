"""Explicit independent editing candidates; not an official syllabus denominator."""
from copy import deepcopy
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
CANDIDATES=HERE / "elective_a_b_atomic_candidates_batch15.json"
def apply(rows):
    new=json.loads(CANDIDATES.read_text(encoding="utf-8"))
    ids={x["id"] for x in rows}
    if len(new)!=9 or len({x["id"] for x in new})!=9 or ids.intersection(x["id"] for x in new):
        raise ValueError("Batch15 independent curriculum IDs incomplete or duplicate")
    if any(x["source"]["teacher_review"]!="PENDING" or x["source"]["mapping_type"]!="ENGINEERING_INTERPRETATION" for x in new):
        raise ValueError("No author self-certified curriculum mapping")
    return rows+deepcopy(new)
