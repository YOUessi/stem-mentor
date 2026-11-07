"""Project-authored Batch22 candidates: source-page anchored, not official atoms."""
import json
from copy import deepcopy
from pathlib import Path

SRC=Path(__file__).resolve().with_name("engineering_gap_candidates_batch22.json")

def apply(rows):
    extra=json.loads(SRC.read_text(encoding="utf-8"))
    current={x["id"] for x in rows}
    assert len(extra)==12 and len({x["id"] for x in extra})==12
    if current.intersection(x["id"] for x in extra):
        raise ValueError("Duplicate engineering map ID")
    for x in extra:
        if (x["level"]!="选修拓展" or x.get("elective_track") not in
            {"ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"} or
            x["source"]["teacher_review"]!="PENDING" or
            x["source"]["mapping_type"]!="ENGINEERING_INTERPRETATION" or
            x["status"]!="PLANNED" or not x["editorial_objective_id"].startswith("EDITORIAL-GAP-")):
            raise ValueError("Illegal curriculum approval or source scope")
    return rows+deepcopy(extra)
