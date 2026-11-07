"""Additional five strictly editorial/unreviewed optional elective candidate maps."""
import json
from copy import deepcopy
from pathlib import Path
SRC=Path(__file__).resolve().with_name("engineering_gap_candidates_batch23.json")
def apply(rows):
    extra=json.loads(SRC.read_text(encoding="utf-8"))
    if len(extra)!=5 or {x["id"] for x in extra}!={f"HS-MATH-{i}" for i in range(174,179)}:
        raise ValueError("Missing Batch23 editorial candidates")
    old={x["id"] for x in rows}
    if old.intersection(x["id"] for x in extra):
        raise ValueError("Duplicate engineering IDs")
    if {x["editorial_objective_id"] for x in extra}!={f"EDITORIAL-GAP-{i:03d}" for i in (18,19,23,24,26)}:
        raise ValueError("Wrong elective-gap relationship")
    for row in extra:
        source=row["source"]
        if row["level"]!="选修拓展" or row["elective_track"] not in {"ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"} or row["status"]!="PLANNED" or source["mapping_type"]!="ENGINEERING_INTERPRETATION" or source["teacher_review"]!="PENDING":
            raise ValueError("False official coverage or teacher approval")
    return rows+deepcopy(extra)
