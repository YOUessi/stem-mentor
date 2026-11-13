"""Batch17 project-authored engineering candidates; never the official atom denominator."""
import json
from copy import deepcopy
from pathlib import Path
SRC=Path(__file__).resolve().with_name("cross_track_atomic_candidates_batch17.json")
def apply(rows):
    extra=json.loads(SRC.read_text(encoding="utf8"))
    current={row["id"] for row in rows}
    if len(extra)!=11 or len({v["id"] for v in extra})!=11 or current.intersection(v["id"] for v in extra):
        raise ValueError("Batch17 requires 11 unique new engineering candidates")
    if any(v["source"]["mapping_type"]!="ENGINEERING_INTERPRETATION" or
           v["source"]["teacher_review"]!="PENDING" or
           v["status"]!="PLANNED" or
           v["editorial_objective_id"]==""
           for v in extra):
        raise ValueError("Cannot claim independent official status or approval")
    return rows+deepcopy(extra)
