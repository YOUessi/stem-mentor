"""Source-locked, teacher-pending mathematical comparison and finite-witness tests."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import json

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch101_math_pairs as PAIR
from kb_batch101_pair_authoring import RECORDS

@pytest.fixture(scope="module")
def data():
    return PAIR.build()

def test_20_original_mathematical_reviews_are_not_certified_atoms(data):
    PAIR.validate(data)
    assert data["historically_unpaired_provisional_labels"]==134
    assert data["newly_authored_semantic_pair_comparisons"]==20
    assert data["remaining_without_any_editorial_pair_comparison"]==114
    assert data["teacher_semantic_equivalence_adjudications"]==0
    assert data["approved_official_merges"]==0
    assert data["teacher_approved"]==0
    assert not data["student_publishable"]
    assert all(v is None for v in data["official_atom_denominators_by_track"].values())
    assert not data["finite_checks_certify_general_claims"]

@pytest.mark.parametrize("index",range(20))
def test_every_pair_has_exact_lineage_math_conditions_boundaries_and_pending_status(data,index):
    row=data["editorial_pairs"][index]
    assert row["left_topic"]==RECORDS[index]["left"]
    assert row["right_topic"]==RECORDS[index]["right"]
    assert len(row["left_source_line_sha256"])==len(row["right_source_line_sha256"])==64
    assert row["left_source_candidate_id"]!=row["right_source_candidate_id"]
    assert row["teacher_review_status"]=="REVIEW_PENDING"
    assert row["editorial_pair_comparison"]=="AUTHORED_REVIEW_PENDING"
    assert row["proposed_relationship"] in PAIR.ALLOWED
    assert row["official_atom_id"] is None
    assert not row["teacher_approved"]
    assert not row["student_publishable"]
    assert not row["mathematical_equivalence_certified"]
    assert all(len(row[k])>=27 for k in ("necessary_conditions","mathematical_distinction",
                                           "positive_example","invalid_boundary_or_counterexample"))

@pytest.mark.parametrize("index",range(20))
def test_exact_instance_positive_and_invalid_case_not_general_certificate(data,index):
    witness=PAIR.instance(index)
    assert witness["positive_exact_instance_verified"] is True
    assert witness["invalid_boundary_exact_instance_verified"] is True
    assert witness==data["editorial_pairs"][index]["independent_finite_witness"]
    assert witness["general_theorem_certified"] is False
    assert witness["math_equivalence_certified"] is False
    assert witness["teacher_approved"] is False

@pytest.mark.parametrize("attack",(
    "missing_record","duplicate_record","missing_math_conditions",
    "relabel_unknown_left","relabel_unknown_right","fake_approved_relation"))
def test_source_pair_builder_rejects_mutated_authoring(attack):
    records=deepcopy(RECORDS)
    if attack=="missing_record":records.pop()
    elif attack=="duplicate_record":records[1]=deepcopy(records[0])
    elif attack=="missing_math_conditions":records[0]["conditions"]=" "
    elif attack=="relabel_unknown_left":records[0]["left"]="不存在的原子"
    elif attack=="relabel_unknown_right":records[0]["right"]="不存在的原子"
    elif attack=="fake_approved_relation":records[0]["relation"]="MATH_EQUIVALENCE_APPROVED"
    with pytest.raises(ValueError):
        PAIR.build(records)

@pytest.mark.parametrize("attack",(
    "fake_official_denom","fake_teacher_adjudication","fake_approval",
    "fake_student_release","fake_math_certification","fake_status",
    "duplicate_id","fake_official_atom_id","fake_relation"))
def test_downstream_math_pair_report_rejects_authority_mutations(data,attack):
    rows=deepcopy(data)
    p=rows["editorial_pairs"]
    if attack=="fake_official_denom": rows["official_atom_denominators_by_track"]["ELECTIVE_A"]=100
    elif attack=="fake_teacher_adjudication": rows["teacher_approved"]=1
    elif attack=="fake_approval":p[0]["teacher_approved"]=True
    elif attack=="fake_student_release":p[0]["student_publishable"]=True
    elif attack=="fake_math_certification":p[0]["mathematical_equivalence_certified"]=True
    elif attack=="fake_status":p[0]["teacher_review_status"]="APPROVED"
    elif attack=="duplicate_id":p[1]["left_source_candidate_id"]=p[0]["left_source_candidate_id"]
    elif attack=="fake_official_atom_id":p[0]["official_atom_id"]="HS-MATH-X"
    elif attack=="fake_relation":p[0]["proposed_relationship"]="CERTIFIED_SAME"
    with pytest.raises(ValueError):
        PAIR.validate(rows)

def test_unpaired_queue_114_is_not_official_teacher_adjudication(data):
    ids={p["left_source_candidate_id"] for p in data["editorial_pairs"]}
    assert len(ids)==20
    assert data["approved_official_merges"]==0
    assert data["teacher_semantic_equivalence_adjudications"]==0

def test_reproducible_author_and_artifact_snapshot(data):
    assert PAIR.OUT.exists() and PAIR.MD.exists()
    assert json.loads(PAIR.OUT.read_text(encoding="utf8"))==data
    assert PAIR.MD.read_text(encoding="utf8")==PAIR.markdown(data)
    assert PAIR.Q.digest(PAIR.AUTHOR)==data["authoring_sha256"]
    assert PAIR.Q.digest(PAIR.Q.SOURCE)==data["source_candidate_snapshot_sha256"]
    assert PAIR.Q.digest(PAIR.Q.PREV)==data["prior_unpaired_queue_sha256"]
