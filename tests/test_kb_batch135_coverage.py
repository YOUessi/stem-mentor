"""Coverage is calculated from bounded proposals, not declared national fractions."""
import copy
import json
import sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch135_coverage as coverage
import build_kb_batch133_atomization as atoms

@pytest.fixture(scope="module")
def matrix():return json.loads(coverage.OUT.read_text(encoding="utf-8"))

def test_frozen_audit_replay(matrix):
    assert coverage.validate(matrix)
    assert coverage.MD.read_text(encoding="utf-8")==coverage.render(matrix)
    assert matrix["scope_proposals"]==41
    assert matrix["full_teacher_draft_manuscripts"]==22
    assert matrix["incomplete_proposal_drafts"]==19
    assert matrix["teacher_examples"]==44 and matrix["hints"]==66
    assert matrix["finite_exact_oracle_cases"]==66

@pytest.mark.parametrize("i",range(41))
def test_each_source_and_review_bound(i,matrix):
    row=matrix["rows"][i]
    assert len(row["source_span_sha256"])==64
    assert row["teacher_review"]=="REVIEW_PENDING"
    assert row["official_atom_id"] is None
    assert row["math_general_proof_certified"] is False
    assert row["student_authoritative"] is False
    if row["has_complete_teacher_manuscript"]:
        assert row["manuscript_id"]
        assert row["missing_fields"]==[]
        assert row["teacher_examples"]==2
        assert row["student_hints"]==3
    else:
        assert row["manuscript_id"] is None
        assert len(row["missing_fields"])>=12
        assert row["teacher_examples"]==row["student_hints"]==0

@pytest.mark.parametrize("track",atoms.TRACKS)
def test_every_track_denominator_still_unknown(track,matrix):
    assert matrix["official_atom_denominators"][track] is None
    assert matrix["by_track"][track]["official_atom_denominator"] is None
    assert matrix["by_track"][track]["official_coverage_rate"] is None
    assert matrix["by_track"][track]["teacher_approved"]==0
    assert matrix["by_track"][track]["student_published"]==0

@pytest.mark.parametrize("field",["national_course_coverage_percentage","teacher_approvals",
                                     "student_authoritative_releases","certified_general_theorems"])
def test_forged_counts_rejected(field,matrix):
    tampered=copy.deepcopy(matrix);tampered[field]=98
    with pytest.raises(ValueError):coverage.validate(tampered)

@pytest.mark.parametrize("i",range(41))
def test_source_membership_or_content_tamper_rejected(i,matrix):
    tampered=copy.deepcopy(matrix)
    tampered["rows"][i]["has_complete_teacher_manuscript"]=not tampered["rows"][i]["has_complete_teacher_manuscript"]
    with pytest.raises(ValueError):coverage.validate(tampered)

def test_missing_queue_exact_and_a_to_e_zero_not_completion(matrix):
    missing={r["candidate_id"] for r in matrix["rows"] if not r["has_complete_teacher_manuscript"]}
    assert missing==set(matrix["missing_full_manuscript_queue"])
    assert len(missing)==19
    for track in ["ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"]:
        assert matrix["by_track"][track]["provisional_candidates"]==0
        assert matrix["by_track"][track]["official_atom_denominator"] is None
