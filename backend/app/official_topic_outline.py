"""Separate D/E unnumbered outline so zero numbered markers never imply empty tracks."""
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from .official_clause_audit import source_clause_ledger

SOURCE=Path(__file__).resolve().parents[2]/"curriculum/highschool_math/official_unnumbered_de_outline_batch18.json"

def validate_outline(data):
    ledger=source_clause_ledger()
    if data["scope"]!="UNNUMBERED_D_E_OUTLINE_NOT_ATOMIC_COUNT":
        raise ValueError("Wrong unnumbered topic scope")
    if data["source_pdf_sha256"]!=ledger["source"]["sha256"]:
        raise ValueError("Source PDF SHA mismatch")
    page={p["printed_page"]:p for p in ledger["pages"]}
    ids=set()
    counts=Counter()
    for row in data["items"]:
        if row["id"] in ids:raise ValueError("Duplicated unnumbered topic")
        ids.add(row["id"])
        track=row["track"]
        if track not in ("ELECTIVE_D","ELECTIVE_E"):raise ValueError("Unknown unnumbered track")
        p=row["printed_page"]
        if row["pdf_page_index"]!=p+7 or track not in page[p]["tracks_present"]:
            raise ValueError("Topic source page/track mismatch")
        if row["page_text_sha256"]!=page[p]["pdf_text_sha256"]:
            raise ValueError("Topic page hash mismatch")
        if row["id"] != f"STD2020-{track}-TOPIC-{counts[track]+1:02d}":
            raise ValueError("Topic page or ID order changed")
        if row["source_kind"]!="UNNUMBERED_TOPIC_OUTLINE" or not row["project_authored_heading"]:
            raise ValueError("Missing independently authored topic title")
        if track=="ELECTIVE_E" and row["offering_type"]!="SCHOOL_SELECTED_EXAMPLE_OR_OPTION":
            raise ValueError("E optional module cannot be declared universal")
        if track=="ELECTIVE_D" and row["offering_type"]!="CURRICULUM_THEME_SUBTOPIC":
            raise ValueError("D curricular topic mislabeled")
        if row["atom_decomposition_review"]!="PENDING" or row["teacher_review"]!="PENDING" or row["student_available"] is not False:
            raise ValueError("Unreviewed outline must not be released")
        counts[track]+=1
    summary=data["summary"]
    if (summary["ELECTIVE_D_subtopic_headings"]!=counts["ELECTIVE_D"] or
        summary["ELECTIVE_E_scoped_examples_or_modules"]!=counts["ELECTIVE_E"] or
        summary["teacher_verified_knowledge_atoms"]!=0 or
        summary["fully_complete"] is not False):
        raise ValueError("False D/E source outline progress")
    return data

@lru_cache(maxsize=1)
def de_outline():
    return validate_outline(json.loads(SOURCE.read_text(encoding="utf-8")))
