"""Batch90 source-locked editorial relation gate and negative regression checks."""
import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/"scripts")]
import build_kb_batch90_relations as B

@pytest.fixture(scope="module")
def sources():
    return B.B89.build()[1], B.B88.build()

@pytest.fixture(scope="module")
def reference(sources):
    return B.build(prior=sources[0], previous=sources[1])

def data():
    return B.load(B.AUTHOR)

def invalid(raw, sources, match):
    with pytest.raises(ValueError, match=match):
        B.build(raw=raw, prior=sources[0], previous=sources[1])

def test_counts_are_editorial_not_official(reference):
    assert reference["new_editorial_pairs"] == 24
    assert reference["new_candidate_id_coverage"] == 48
    assert reference["new_cross_track_relations"] == 8
    assert reference["new_relation_types"] == {
        "RELATED_DISTINCT": 21, "POSSIBLE_OVERLAP": 3}
    assert reference["cumulative_candidate_id_coverage"] == 118
    assert reference["remaining_candidate_ids_without_any_relation"] == 182
    assert reference["official_curriculum_atom_denominator"] is None
    assert reference["teacher_approved"] == reference["student_published"] == 0
    assert reference["complete_teacher_atomization_pages"] == 0

@pytest.mark.parametrize("i", range(24))
def test_original_relation_is_all_source_and_review_locked(reference, i):
    r=reference["source_locked_relations"][i]
    assert r["review_id"] == f"KB90-REL-{i+1:03d}"
    assert r["student_authoritative_index_eligible"] is False
    assert r["teacher_approved"] is False and r["student_publishable"] is False
    assert r["math_equivalence_certified"] is False
    assert r["human_equivalence_adjudication"] == "NOT_PERFORMED"
    for side in ("left_source", "right_source"):
        s=r[side]
        assert len(s["source_line_sha256"]) == 64
        assert s["candidate_id"] and s["source_review_id"] and s["track"]

@pytest.mark.parametrize("flag",["teacher_approved","semantic_equivalence_certified",
                                "student_publishable"])
def test_forged_root_authority_rejected(flag, sources):
    d=data(); d[flag]=True
    invalid(d, sources, "forged authority")

@pytest.mark.parametrize("flag",["teacher_approved","math_equivalence_certified",
                                "student_publishable"])
def test_forged_relation_release_rejected(flag, sources):
    d=data(); d["relations"][0][flag]=True
    invalid(d, sources, "unearned teacher")

def test_forged_final_atom_rejected(sources):
    d=data();d["relations"][0]["final_atom_id"]="OFFICIAL-MATH-001"
    invalid(d, sources, "unearned teacher")

def test_unknown_candidate_rejected(sources):
    d=data();d["relations"][0]["left_candidate_id"]="NO_SUCH_SOURCE"
    invalid(d, sources, "invalid relation endpoint")

def test_already_compared_candidate_not_recounted(sources):
    d=data()
    d["relations"][0]["left_candidate_id"]=sources[1]["reviewed_relations"][0]["left_candidate_id"]
    invalid(d, sources, "previously paired")

def test_repeated_candidate_rejected(sources):
    d=data()
    d["relations"][1]["left_candidate_id"]=d["relations"][0]["left_candidate_id"]
    invalid(d, sources, "repeat candidate")

def test_swapped_duplicate_pair_rejected(sources):
    d=data()
    d["relations"][1]["left_candidate_id"]=d["relations"][0]["right_candidate_id"]
    d["relations"][1]["right_candidate_id"]=d["relations"][0]["left_candidate_id"]
    invalid(d, sources, "duplicate/swapped relation")

def test_reordered_relation_identifier_rejected(sources):
    d=data();d["relations"][0],d["relations"][1]=d["relations"][1],d["relations"][0]
    invalid(d, sources, "relation id changed")

def test_missing_relation_rejected(sources):
    d=data();d["relations"].pop()
    invalid(d, sources, "24 complete")

def test_unsubstantiated_editorial_rejected(sources):
    d=data();d["relations"][0]["worked_witness"]="2+2=4"
    invalid(d, sources, "missing substantial")

def test_illicit_payload_extra_key_rejected(sources):
    d=data();d["relations"][0]["teacher_solution"]="EXPOSE TEACHER ANSWER"
    invalid(d, sources, "relation schema drift")

def test_unknown_standard_rejected(sources):
    d=data();d["standard_version"]="2026 invented syllabus"
    invalid(d, sources, "forged authority")

def test_previous_scope_inflation_rejected(sources):
    prior=copy.deepcopy(sources[0]);prior["official_atom_denominator"]=300
    with pytest.raises(ValueError, match="upstream provisional"):
        B.build(prior=prior,previous=sources[1])

def test_duplicate_json_keys_parser_rejected(tmp_path):
    p=tmp_path/"poison.json";p.write_text('{"teacher_approved":false,"teacher_approved":true}')
    with pytest.raises(ValueError,match="duplicate source JSON key"):
        B.load(p)

def test_output_is_deterministic_from_mac_authored_sources(reference):
    assert B.OUT.read_text(encoding="utf8")==B.dump(reference)
    assert B.DOC.read_text(encoding="utf8")==B.markdown(reference)
    allids=set(reference["remaining_unpaired_candidate_ids"])
    assert len(allids)==182
    reviewed={r["left_candidate_id"] for r in data()["relations"]}|{
        r["right_candidate_id"] for r in data()["relations"]}
    assert not reviewed & allids
