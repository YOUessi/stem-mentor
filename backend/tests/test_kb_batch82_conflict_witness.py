"""Batch82 independent tests: ten conflicts, exact math, mutation and review guards."""
from copy import deepcopy
from pathlib import Path
import json
import sys

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch82_conflict_evidence as G
from app.kb_batch82_conflict_witness import OPS,KEYS,check


@pytest.fixture(scope="module")
def artifact():
    return G.build()


@pytest.fixture(scope="module")
def authoring():
    return G.read(G.AUTHOR)


def test_frozen_outputs_exactly_reproduce_content(artifact):
    assert G.OUT.read_text(encoding="utf-8")==G.encoded(artifact)
    assert G.DOC.read_text(encoding="utf-8")==G.markdown(artifact)


def test_total_conflicts_remain_open(artifact):
    assert artifact["conflicts_total"]==10
    assert artifact["conflicts_resolved"]==0
    assert artifact["teacher_approved"]==0
    assert artifact["general_proofs_formally_certified"]==0
    assert artifact["official_curriculum_atom_denominator"] is None
    assert artifact["finite_positive_cases"]==16
    assert artifact["finite_negative_cases"]==20


@pytest.mark.parametrize("ix",range(10))
def test_unique_original_sha_and_pending_teacher_review(ix,artifact):
    row=artifact["witnesses"][ix]
    original=G.read(G.SOURCE)["records"][ix]
    assert row["historical_conflict_id"]==original["conflict_id"]
    assert row["active_sha256"]==original["active_sha256"]
    assert row["candidate_sha256"]==original["candidate_sha256"]
    assert row["active_version_preferred"] is row["candidate_version_preferred"] is None
    assert row["conflict_resolution"]=="UNRESOLVED_NEEDS_INDEPENDENT_TEACHER"
    assert row["review_status"]=="REVIEW_PENDING"
    assert row["teacher_approved"] is row["student_publishable"] is False
    assert row["formal_math_certification"]=="NOT_FORMALLY_VERIFIED"
    assert row["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert row["evidence_scope"]=="FINITE_EXACT_CASES_AND_PRECONDITIONS_ONLY"
    assert row["op"]==OPS[ix]


@pytest.mark.parametrize("ix",range(10))
def test_valid_example_is_exact_and_independently_computed(ix,artifact,authoring):
    a=authoring["cases"][ix]
    status,evidence=check(a["op"],a["valid"])
    assert status=="FINITE_EXACT_WITNESS_ONLY"
    assert evidence==artifact["witnesses"][ix]["positive"]["finite_evidence"]


@pytest.mark.parametrize("ix",range(10))
@pytest.mark.parametrize("negative_ix",(0,1))
def test_two_distinct_boundary_failures_for_every_conflict(ix,negative_ix,artifact,authoring):
    a=authoring["cases"][ix]
    status,evidence=check(a["op"],a["invalid"][negative_ix])
    assert status=="CONDITIONS_NOT_ESTABLISHED"
    assert evidence["failed_condition"]
    assert evidence==artifact["witnesses"][ix]["negative"][negative_ix]["evidence"]


@pytest.mark.parametrize("ix",range(10))
def test_exact_extra_valid_examples_when_present(ix,authoring):
    row=authoring["cases"][ix]
    for case in row.get("extra_valid",[]):
        status,evidence=check(row["op"],case)
        assert status=="FINITE_EXACT_WITNESS_ONLY"
        assert evidence


@pytest.mark.parametrize("ix",range(10))
@pytest.mark.parametrize("evil",(True,1.25,"3",None))
def test_nonexact_or_boolean_values_fail_closed(ix,evil,authoring):
    row=authoring["cases"][ix]
    arg=deepcopy(row["valid"])
    first=next(iter(arg))
    arg[first]=evil
    with pytest.raises(ValueError):
        check(row["op"],arg)


@pytest.mark.parametrize("ix",range(10))
@pytest.mark.parametrize("case",("bad_schema","extra_key","wrong_operation","deep_array"))
def test_invalid_input_schema_fails_closed(ix,case,authoring):
    row=authoring["cases"][ix]
    args=deepcopy(row["valid"])
    op=row["op"]
    if case=="bad_schema":
        del args[next(iter(args))]
    elif case=="extra_key":
        args["silent_bypass"]=0
    elif case=="wrong_operation":
        op="missing_unverified_operation"
    else:
        args[next(iter(args))]=[[[[[[1]]]]]]
    with pytest.raises(ValueError):
        check(op,args)


@pytest.mark.parametrize("ix",range(10))
@pytest.mark.parametrize("tamper",("promote_review","replace_valid_with_invalid","replace_invalid_with_valid","erase_boundary"))
def test_independent_editorial_mutation_is_rejected(ix,tamper,authoring):
    a=deepcopy(authoring)
    row=a["cases"][ix]
    if tamper=="promote_review":
        a["teacher_approved"]=True
    elif tamper=="replace_valid_with_invalid":
        row["valid"]=deepcopy(row["invalid"][0])
    elif tamper=="replace_invalid_with_valid":
        row["invalid"][0]=deepcopy(row["valid"])
    else:
        row["reason"]=""
    with pytest.raises(ValueError):
        G.build(author=a)


def test_historical_conflict_dossier_source_sha_is_immutable():
    with pytest.raises(ValueError,match="SHA altered"):
        G.build(source_hash="0"*64)


def test_historical_conflict_dossier_record_mutation_is_rejected():
    d=deepcopy(G.read(G.SOURCE))
    d["records"][0]["version_winner"]="FORGED"
    with pytest.raises(ValueError,match="frozen original"):
        G.build(source=d)


def test_math_tampered_enum_or_duplicate_rejected(authoring):
    a=deepcopy(authoring)
    a["cases"][5]["op"]=a["cases"][4]["op"]
    with pytest.raises(ValueError):
        G.build(author=a)


def test_all_conflicts_are_review_packages_not_an_official_curriculum_denominator(artifact):
    assert len(set(row["historical_conflict_id"] for row in artifact["witnesses"]))==10
    assert all(row["review_packet_id"].startswith("KB82-IC-") for row in artifact["witnesses"])
    assert all(row["student_publishable"] is False for row in artifact["witnesses"])
    assert not any("teacher_solution" in row for row in artifact["witnesses"])
    assert "428" not in artifact["schema_version"]


@pytest.mark.parametrize("ix",range(10))
def test_unsupported_student_freeform_math_is_not_silently_accepted(ix,authoring):
    row=authoring["cases"][ix]
    with pytest.raises(ValueError):
        check(row["op"],{"untrusted_freeform_proof":"obviously true"})
