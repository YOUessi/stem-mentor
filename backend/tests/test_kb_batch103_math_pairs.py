"""Batch103: strict provenance, negative source/schema mutations, finite-oracle limits."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch103_math_pairs as B

@pytest.fixture(scope="module")
def data():
    return B.build()

def test_source_locked_and_no_teacher_authority(data):
    assert B.validate(data)
    assert data["previously_compared"]==206
    assert data["new_editorial_comparisons"]==20
    assert data["still_unpaired"]==74
    assert data["previously_compared"]+data["new_editorial_comparisons"]+data["still_unpaired"]==300
    assert data["teacher_approved"]==data["student_authoritative_release"]==0
    assert data["fully_human_atomized_source_pages"]==0
    assert data["teacher_semantic_adjudications"]==data["formal_universal_proofs"]==0
    assert len(data["editorial_pairs"])==20
    assert all(v is None for v in data["official_atom_denominators_by_track"].values())

@pytest.mark.parametrize("i",range(20))
def test_authored_mathematics_and_provenance(data,i):
    row=data["editorial_pairs"][i]
    authored=json.loads(B.AUTHOR.read_text(encoding="utf-8"))[i]
    assert row["id"]==f"KB103-PAIR-{i+1:02d}"
    assert row["left_topic"]==authored["left"]
    assert row["right_topic"]==authored["right"]
    assert row["necessary_conditions"]==authored["conditions"]
    assert row["worked_positive_example"]==authored["positive"]
    assert row["invalid_boundary_or_counterexample"]==authored["invalid"]
    assert len(row["left_line_sha256"])==len(row["right_line_sha256"])==64
    assert row["left_source_candidate_id"]!=row["right_source_candidate_id"]
    assert row["teacher_review_status"]=="REVIEW_PENDING"
    assert row["teacher_approved"] is False and row["student_publishable"] is False
    assert row["official_atom_id"] is None and row["semantic_relation_certified"] is False

@pytest.mark.parametrize("i",range(20))
def test_each_positive_and_negative_instance_is_checked_but_not_formal(i):
    witness=B.finite_witness(i)
    assert witness["exact_positive"] is True
    assert witness["exact_invalid_boundary"] is True
    assert witness["formal_universal_proof"] is False
    assert witness["teacher_approved"] is False
    assert witness["student_publishable"] is False
    assert witness["semantic_equivalence_certified"] is False

@pytest.mark.parametrize("track",B.TRACKS)
def test_source_conservation_by_provisional_track(data,track):
    t=data["track_matrix"][track]
    assert t["previously_compared"]+t["new_comparisons"]+t["still_unpaired"]==t["provisional_labels"]
    assert t["official_atom_denominator"] is None

@pytest.mark.parametrize("kind",[
    "missing","extra","duplicate","unknown_left","unknown_right","empty_conditions",
    "short_distinction","short_positive","short_negative","promoted_relationship",
    "reused_left","unpaired_right","missing_field","extra_field",
])
def test_invalid_authoring_fails_closed(kind):
    data=json.loads(B.AUTHOR.read_text(encoding="utf-8"))
    if kind=="missing":data.pop()
    elif kind=="extra":data.append(deepcopy(data[0]))
    elif kind=="duplicate":data[1]=deepcopy(data[0])
    elif kind=="unknown_left":data[1]["left"]="fake-unknown-source"
    elif kind=="unknown_right":data[2]["right"]="fake-unknown-comparison-source"
    elif kind=="empty_conditions":data[3]["conditions"]=""
    elif kind=="short_distinction":data[4]["distinction"]="too short"
    elif kind=="short_positive":data[5]["positive"]="too short"
    elif kind=="short_negative":data[6]["invalid"]="too short"
    elif kind=="promoted_relationship":data[7]["relation"]="OFFICIAL_EQUIVALENT"
    elif kind=="reused_left":data[8]["left"]="等差关系的情境识别"
    elif kind=="unpaired_right":data[9]["right"]="空间点线点面距离"
    elif kind=="missing_field":del data[10]["conditions"]
    elif kind=="extra_field":data[11]["teacher_approved"]=True
    with pytest.raises(ValueError):B.build(data)

@pytest.mark.parametrize("kind",[
    "fake_denominator","fake_elective_e_count","fake_signoff","fake_student_release",
    "fake_page_review","fake_proof","fake_count","fake_track_count",
    "fake_approval","fake_student_pair","fake_relation_certification","fake_atom",
    "fake_source_sha","fake_witness_certification","fake_pair_id","fake_math_text",
])
def test_untrusted_report_mutation_fails_closed(data,kind):
    changed=deepcopy(data)
    first=changed["editorial_pairs"][0]
    if kind=="fake_denominator":changed["official_atom_denominators_by_track"]["COMPULSORY"]=75
    elif kind=="fake_elective_e_count":changed["official_atom_denominators_by_track"]["ELECTIVE_E"]=0
    elif kind=="fake_signoff":changed["teacher_approved"]=1
    elif kind=="fake_student_release":changed["student_authoritative_release"]=1
    elif kind=="fake_page_review":changed["fully_human_atomized_source_pages"]=1
    elif kind=="fake_proof":changed["formal_universal_proofs"]=1
    elif kind=="fake_count":changed["still_unpaired"]=0
    elif kind=="fake_track_count":changed["track_matrix"]["COMPULSORY"]["new_comparisons"]+=1
    elif kind=="fake_approval":first["teacher_approved"]=True
    elif kind=="fake_student_pair":first["student_publishable"]=True
    elif kind=="fake_relation_certification":first["semantic_relation_certified"]=True
    elif kind=="fake_atom":first["official_atom_id"]="fabricated"
    elif kind=="fake_source_sha":first["left_line_sha256"]="0"*64
    elif kind=="fake_witness_certification":first["finite_exact_witness"]["formal_universal_proof"]=True
    elif kind=="fake_pair_id":first["id"]="KB103-PAIR-99"
    elif kind=="fake_math_text":first["worked_positive_example"]="mathematically unreviewed text"
    with pytest.raises(ValueError):B.validate(changed)

def test_immutable_source_sets_and_no_duplicate_previous_pairs(data):
    source=B.PREV.Q.source_read(B.SOURCE)["provisional_candidate_backlog"]
    original_ids={row["candidate_id"] for row in source}
    previous=json.loads(B.PREV.OUT.read_text(encoding="utf-8"))
    prev_ids={row["left_source_candidate_id"] for row in previous["editorial_pairs"]}
    current={row["left_source_candidate_id"] for row in data["editorial_pairs"]}
    assert len(current)==20
    assert current<=original_ids
    assert not current & prev_ids
    assert B.digest(B.AUTHOR)==data["author_sha256"]
    assert B.digest(B.PREV.OUT)==data["batch102_report_sha256"]

def test_generated_json_markdown_coverage_fully_reproducible(data):
    assert json.loads(B.OUT.read_text(encoding="utf-8"))==data
    assert B.MD.read_text(encoding="utf-8")==B.markdown(data)
    assert json.loads(B.COVERAGE.read_text(encoding="utf-8"))==B.coverage(data)
    assert B.coverage(data)["remaining_unpaired"]==74
