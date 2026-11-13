"""K00 source-ledger denominator is a *provisional* editorial candidate count only."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch143_source_gap as gap

def audit():return json.loads(gap.OUT.read_text(encoding="utf-8"))

def test_exact_regeneration_and_human_report():
    d=audit()
    assert gap.validate(d)
    assert gap.render(d)==gap.MD.read_text(encoding="utf-8")
    assert d["candidate_editorial_denominator"]==239
    assert d["teacher_only_manuscript_total"]==65
    assert d["crosswalked_historical_candidates"]==24
    assert d["historical_candidates_without_bounded_full_draft"]==215
    assert len(d["older_draft_candidates_without_this_239_ledger"])==41
    assert d["official_census_complete"] is False

@pytest.mark.parametrize("t,n,matched,pending",[
    ("COMPULSORY",75,8,67),
    ("SELECTIVE_COMPULSORY",51,4,47),
    ("ELECTIVE_A",30,3,27),
    ("ELECTIVE_B",30,2,28),
    ("ELECTIVE_C",24,2,22),
    ("ELECTIVE_D",17,3,14),
    ("ELECTIVE_E",12,2,10),
])
def test_seven_track_source_candidates_are_not_official_atom_denominators(t,n,matched,pending):
    d=audit();r=d["by_track"][t]
    assert r["historical_editorial_candidates"]==n
    assert r["candidate_to_draft_crosswalk_count"]==matched
    assert r["candidate_without_draft"]==pending
    assert r["official_atom_denominator"] is None
    assert r["official_coverage_fraction"] is None
    assert r["human_approved_atoms"]==0
    assert r["student_authoritative"]==0

@pytest.mark.parametrize("field,value",[
 ("official_coverage_fraction",1),
 ("teacher_approved",1),
 ("student_authoritative",1),
 ("official_census_complete",True),
 ("candidate_editorial_denominator",113),
 ("historical_candidates_without_bounded_full_draft",0),
 ("official_atom_denominators",{"COMPULSORY":113}),
])
def test_forgery_of_approval_denominator_or_candidate_gap_is_rejected(field,value):
    x=audit()
    x[field]=value
    with pytest.raises(ValueError):gap.validate(x)

@pytest.mark.parametrize("i",range(239))
def test_every_historical_candidate_preserves_provenance_and_pending_status(i):
    r=audit()["records"][i]
    assert r["official_atom_id"] is None
    assert r["teacher_review"]=="REVIEW_PENDING"
    assert not r["proof_certified"]
    assert not r["student_authoritative"]
    assert r["grade"] in gap.EVIDENCE
    assert len(r["source_span_sha256"])==64

@pytest.mark.parametrize("grade",gap.EVIDENCE)
def test_every_source_grade_fails_closed_for_student_certification(grade):
    d=audit()
    assert any(r["grade"]==grade for r in d["records"])
    assert all(r["official_atom_id"] is None for r in d["records"] if r["grade"]==grade)
