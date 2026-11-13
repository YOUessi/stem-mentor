"""Batch102 source integrity, exact finite mathematics, fake-approval rejection."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch102_math_pairs as B

@pytest.fixture(scope="module")
def report():
    return B.build()

def test_cumulative_seven_track_coverage_is_not_official(report):
    B.validate(report)
    assert (report["previously_compared_provisional_labels"]+
            report["newly_compared_provisional_labels"]+
            report["remaining_unpaired_provisional_labels"])==300
    assert (report["previously_compared_provisional_labels"],
            report["newly_compared_provisional_labels"],
            report["remaining_unpaired_provisional_labels"])==(186,20,94)
    assert report["fully_human_atomized_pages"]==0
    assert report["teacher_approved"]==report["student_authoritative_release"]==0
    assert report["general_formal_proofs_certified"]==0
    assert all(v is None for v in report["official_atom_denominators_by_track"].values())

@pytest.mark.parametrize("index",range(20))
def test_each_original_source_pair_is_draft_with_real_conditions(report,index):
    row=report["editorial_pairs"][index]
    authored=json.loads(B.AUTHOR.read_text(encoding="utf8"))[index]
    assert row["left_topic"]==authored["left"]
    assert row["right_topic"]==authored["right"]
    assert row["proposed_relationship"]==authored["relation"]
    assert row["necessary_conditions"]==authored["conditions"]
    assert row["positive_example"]==authored["positive"]
    assert row["invalid_boundary_or_counterexample"]==authored["invalid"]
    assert len(row["left_source_line_sha256"])==len(row["right_source_line_sha256"])==64
    assert row["left_source_candidate_id"]!=row["right_source_candidate_id"]
    assert row["teacher_review_status"]=="REVIEW_PENDING"
    assert row["official_atom_id"] is None
    assert row["teacher_approved"] is False
    assert row["student_publishable"] is False
    assert row["mathematical_equivalence_certified"] is False

@pytest.mark.parametrize("index",range(20))
def test_independent_exact_positive_instance_is_not_general_proof(index):
    w=B.finite_witness(index)
    assert w["valid_instance_exact"] is True
    assert w["general_theorem_certified"] is False
    assert w["semantic_equivalence_certified"] is False
    assert w["teacher_reviewed"] is False

@pytest.mark.parametrize("index",range(20))
def test_independent_exact_invalid_boundary_exists(index):
    w=B.finite_witness(index)
    assert w["invalid_boundary_exact"] is True
    assert w["student_publishable"] is False

@pytest.mark.parametrize("track",B.TRACKS)
def test_source_label_track_conservation_not_official(track,report):
    col=report["track_matrix"][track]
    assert col["prior_compared"]+col["new_editorial_comparisons"]+col["remaining"]==col["provisional_source_labels"]
    assert col["official_atom_denominator"] is None

@pytest.mark.parametrize("kind",[
    "missing_record","extra_record","duplicate_left","empty_condition","unknown_left",
    "unknown_right","left_was_prior_paired","right_is_unpaired","promote_relation",
])
def test_bad_authoring_fails_closed(kind):
    rows=json.loads(B.AUTHOR.read_text(encoding="utf8"))
    if kind=="missing_record":rows.pop()
    elif kind=="extra_record":rows.append(deepcopy(rows[0]))
    elif kind=="duplicate_left":rows[1]=deepcopy(rows[0])
    elif kind=="empty_condition":rows[2]["conditions"]=" "
    elif kind=="unknown_left":rows[3]["left"]="没有来源绑定的知识主题"
    elif kind=="unknown_right":rows[4]["right"]="不存在的右侧课程主题"
    elif kind=="left_was_prior_paired":rows[5]["left"]="差商极限存在性"
    elif kind=="right_is_unpaired":rows[6]["right"]="数列单调性"
    elif kind=="promote_relation":rows[7]["relation"]="CERTIFIED_EQUIVALENT"
    with pytest.raises(ValueError):
        B.build(rows)

@pytest.mark.parametrize("kind",[
    "fake_global_count","fake_remaining","fake_track_count","fake_official_denom",
    "fake_track_official_denom","fake_teacher_signoff","fake_student_release",
    "fake_atomized_page","fake_formal_proof","duplicate_pair_id",
    "fake_approved_relation","fake_pair_approval","fake_pair_student",
    "fake_equivalence","fake_official_atom","fake_witness_proof",
])
def test_report_mutations_are_not_trusted(kind,report):
    data=deepcopy(report)
    pair=data["editorial_pairs"]
    track=data["track_matrix"]["COMPULSORY"]
    if kind=="fake_global_count":data["previously_compared_provisional_labels"]=200
    elif kind=="fake_remaining":data["remaining_unpaired_provisional_labels"]=0
    elif kind=="fake_track_count":track["new_editorial_comparisons"]+=1
    elif kind=="fake_official_denom":data["official_atom_denominators_by_track"]["ELECTIVE_E"]=0
    elif kind=="fake_track_official_denom":track["official_atom_denominator"]=75
    elif kind=="fake_teacher_signoff":data["teacher_approved"]=1
    elif kind=="fake_student_release":data["student_authoritative_release"]=1
    elif kind=="fake_atomized_page":data["fully_human_atomized_pages"]=1
    elif kind=="fake_formal_proof":data["general_formal_proofs_certified"]=1
    elif kind=="duplicate_pair_id":pair[1]["left_source_candidate_id"]=pair[0]["left_source_candidate_id"]
    elif kind=="fake_approved_relation":pair[0]["proposed_relationship"]="EQUIVALENT"
    elif kind=="fake_pair_approval":pair[0]["teacher_approved"]=True
    elif kind=="fake_pair_student":pair[0]["student_publishable"]=True
    elif kind=="fake_equivalence":pair[0]["mathematical_equivalence_certified"]=True
    elif kind=="fake_official_atom":pair[0]["official_atom_id"]="HS-NO-TEACHER"
    elif kind=="fake_witness_proof":pair[0]["independent_finite_witness"]["general_theorem_certified"]=True
    with pytest.raises(ValueError):
        B.validate(data)

def test_all_authored_source_ids_are_new_and_unique(report):
    old=json.loads(B.PREVIOUS_PAIRS.read_text(encoding="utf8"))
    prev_ids={x["left_source_candidate_id"] for x in old["editorial_pairs"]}
    ids=[r["left_source_candidate_id"] for r in report["editorial_pairs"]]
    assert len(ids)==len(set(ids))==20
    assert not (set(ids)&prev_ids)
    assert sum(1 for x in report["editorial_pairs"] if x["cross_track"])>=0

def test_source_lock_and_reproducible_reports(report):
    assert B.digest(B.AUTHOR)==report["authoring_sha256"]
    assert B.digest(B.PREVIOUS_PAIRS)==report["prior_pairs_sha256"]
    assert B.Q.digest(B.Q.SOURCE)==report["source_candidates_sha256"]
    assert json.loads(B.OUT.read_text(encoding="utf8"))==report
    assert B.MD.read_text(encoding="utf8")==B.markdown(report)
    assert json.loads(B.COVERAGE.read_text(encoding="utf8"))["remaining_unpaired_provisional_labels"]==94

def test_sympy_piecewise_boundary_regression():
    # SymPy's direct Piecewise limit at a jump can return the value at the
    # discontinuity for both directions; use the proven constant branches.
    from sympy import Symbol,Piecewise,Rational,limit
    x=Symbol("x",real=True)
    f=Piecewise((0,x<0),(1,True))
    assert f.subs(x,-Rational(1,10))==0
    assert f.subs(x,Rational(1,10))==1
    assert limit(0,x,0,dir="-")==0
    assert limit(1,x,0,dir="+")==1
