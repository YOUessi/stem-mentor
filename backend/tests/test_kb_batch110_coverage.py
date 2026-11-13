"""Official-denominator anti-inflation and lesson field coverage regression."""
from copy import deepcopy
from pathlib import Path
import json,sys
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch110_coverage as B

@pytest.fixture(scope="module")
def report():return B.build()

def test_honest_seven_track_denominators(report):
    assert len(report["official_atom_coverage_by_track"])==7
    for item in report["official_atom_coverage_by_track"].values():
        assert item["total"] is None and item["coverage_fraction"] is None
        assert item["missing_total"]=="UNKNOWN" and item["approved"]==0
    assert report["source_pdf_pages_total"]==61
    assert report["source_pages_with_editorial_line_partitions"]==6
    assert report["official_teacher_full_page_atomizations"]==0

def test_no_fake_promotion_of_source_candidates_to_teacher_approved(report):
    assert report["provisional_candidates_in_these_three_batches"]==60
    assert report["provisional_candidate_counts_by_track"]["ELECTIVE_B"]==2
    assert report["new_lesson_teacher_approved"]==0
    assert report["general_proof_certificates"]==0
    assert report["arbitrary_student_solution_verified"]==0

@pytest.mark.parametrize("i",range(8))
def test_each_lesson_complete_but_unapproved(report,i):
    r=report["current_batch_lesson_completeness"][i]
    assert r["id"]==f"math.hs.batch110.{i+1:02d}"
    assert len(r["field_checks"])==12
    assert all(r["field_checks"].values())
    assert r["machine_structure_completeness"]==1
    assert r["status"]=="REVIEW_PENDING"
    assert not r["teacher_approved"]
    assert not r["student_authoritative"]
    assert not r["general_proof_certified"]

@pytest.mark.parametrize("kind",["fake_denominator","fake_teacher","bad_source_sha",
    "duplicate_page","missing_page"])
def test_coverage_rejects_authority_and_source_manipulations(kind):
    s=[json.loads((ROOT/f"docs/evaluation/KB_BATCH{n}_SCOPE.json")
        .read_text(encoding="utf8")) for n in (108,109)]
    if kind=="fake_denominator":
        s[0]["official_seven_track_atom_denominators"]["COMPULSORY"]=100
    elif kind=="fake_teacher":
        s[0]["teacher_approvals"]=1
    elif kind=="bad_source_sha":
        s[1]["source_pdf_sha256"]="unauthorized"
    elif kind=="duplicate_page":
        s[1]["line_counts"]["18"]=28
    elif kind=="missing_page":
        s[1]["line_counts"]={}
    with pytest.raises(ValueError):
        B.build(prior_sources=s)

def test_coverage_frozen_artifacts(report):
    assert B.OUT.read_text(encoding="utf8")==B.serialize(report)
    assert B.MD.read_text(encoding="utf8")==B.markdown(report)
