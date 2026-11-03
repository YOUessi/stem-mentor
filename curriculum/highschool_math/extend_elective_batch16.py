"""Batch16 independent project-authored candidate topics, never official atom IDs."""
import json
from copy import deepcopy
from pathlib import Path
HERE=Path(__file__).resolve().parent
SRC=HERE/"elective_b_c_d_e_atomic_candidates_batch16.json"

def apply(rows):
    new=json.loads(SRC.read_text(encoding="utf8"))
    old={x["id"] for x in rows}
    if len(new)!=12 or len({x["id"] for x in new})!=12 or old.intersection(x["id"] for x in new):
        raise ValueError("Batch16 expected 12 unique new engineering IDs")
    if any(x["source"]["mapping_type"]!="ENGINEERING_INTERPRETATION"
           or x["source"]["teacher_review"]!="PENDING"
           or x["status"]!="PLANNED" for x in new):
        raise ValueError("Candidate cannot imply official certification or finished teaching product")
    return rows+deepcopy(new)
