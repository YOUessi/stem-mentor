"""Batch98 K00-K09 regression: source integrity, teacher-only release, finite math premises."""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
import json
import sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch98_depth as BD
import build_kb_batch98_scope_matrix as BM
from kb_batch98_authoring import RECORDS
from kb_batch98_scope_authoring import SCOPES
from app.deep_knowledge import DeepLesson, lessons
from app.deep_retrieval import editor_draft_search, editor_draft_full, student_evidence_lookup, EditorOnlyError
from app.kb_batch98_exact_oracles import (
    IDS,check,verify_all,cuboid_vertices,point_line_sq,point_plane_sq,
    normal_standardized,pearson_2x2,reciprocal_epsilon_N,
    squared_poly_on_closed_interval,apply_isometry,spatial_line_distance_sq,
    bivariate_cov_determinant,diagonal_input_output,discrete_growth,circle_rotation)

@pytest.fixture(scope="module")
def result():
    return BD.build()

@pytest.fixture(scope="module")
def ledger():
    return BM.build()

def test_twelve_new_lessons_complete_and_provisional_denominator_unchanged(result):
    docs,report=result
    assert len(docs)==len(IDS)==12
    assert report["prior_full_deep_drafts"]==54
    assert report["cumulative_new_deep_drafts_since_batch94"]==66
    assert report["still_without_any_individual_review"]==44
    assert report["official_atom_denominator"] is None
    assert all(x is None for x in report["official_atom_denominators_by_track"].values())
    assert report["fully_teacher_atomized_pages"]==report["teacher_approved"]==0
    assert report["student_authoritative_release"]==report["general_theorem_certificates"]==0
    assert report["historical_uncertified_proof_steps"]==538
    assert report["P0_historical_steps_without_teacher_cards"]==106
    assert report["unresolved_math_conflicts"]==10

def test_24_unique_provisional_source_labels_without_official_approval(result,ledger):
    report,scopes=ledger
    deep={x["source_candidate_id"] for x in result[1]["canonical_lesson_source_links"]}
    shallow={x["anchor"] for x in scopes}
    assert len(deep)==len(shallow)==12 and deep.isdisjoint(shallow)
    assert report["provisional_source_labels"]==300
    assert report["remaining_individually_unaudited_labels"]==32
    assert report["deep_draft_coverage_of_provisional_labels"]==66
    assert report["new_individual_scope_interpretations"]==12
    assert sum(report["stage_counts"].values())==300
    assert report["stage_counts"]=={
        "PAIR_COMPARISON_NOT_ATOMIZED":166,
        "INDIVIDUAL_SCOPE_NOT_ATOMIZED":24,
        "INDIVIDUAL_SCOPE_EDITORIAL_PENDING":12,
        "NO_INDIVIDUAL_EDITORIAL":32,
        "FULL_DEEP_DRAFT_PENDING_TEACHER":66}
    assert set(report["track_matrix"])==set(BM.TRACKS)
    assert sum(x["provisional_source_labels"] for x in report["track_matrix"].values())==300
    assert all(x["official_atom_denominator"] is None for x in report["track_matrix"].values())
    assert report["official_atom_denominator"] is None
    assert all(x is None for x in report["official_atom_denominators_by_track"].values())
    assert report["human_full_page_atomization"]=="0/61"
    assert report["teacher_approved"]==report["student_authoritative_releases"]==0
    assert report["remaining_without_pairwise_comparison"]==134
    assert report["historical_uncertified_proof_steps"]==538
    assert report["historical_P0_steps_without_direct_review"]==106
    assert report["unresolved_mathematical_conflicts"]==10
    assert all(v["teacher_approval"] is None and v["official_atom_id"] is None
               and v["student_authoritative_index_eligible"] is False for v in report["candidates"])

@pytest.mark.parametrize("i",range(12))
def test_full_lesson_types_and_source_frozen(i,result):
    doc,ref=result[0][i],result[1]["canonical_lesson_source_links"][i]
    model=DeepLesson.model_validate(doc)
    assert model.id==f"math.hs.batch98.{i+1:02d}"
    assert model.review.status=="REVIEW_PENDING"
    assert model.review.reviewer_id is None and model.review.review_record is None
    assert model.teacher_solution_visibility=="TEACHER_ONLY"
    assert doc["curriculum_ids"]==[RECORDS[i]["curriculum_id"]]
    assert ref["source_candidate_id"]==RECORDS[i]["anchor"]==IDS[i]
    assert ref["source_line_sha256"]==BM.B93.read(BM.B93.SOURCES)["provisional_candidate_backlog"][
        next(j for j,r in enumerate(BM.B93.read(BM.B93.SOURCES)["provisional_candidate_backlog"])
             if r["candidate_id"]==ref["source_candidate_id"])]["source_line_sha256"]
    assert ref["official_atom_id"] is None and not ref["teacher_approved"] and not ref["student_publishable"]
    assert ref["finite_evidence"]["general_theorem_certified"] is False
    assert len(model.assumptions)>=2 and len(model.worked_examples)==2
    assert len(model.hint_ladder)==3 and len(model.boundaries)>=1
    assert len(model.counterexamples)>=1 and len(model.misconceptions)>=1
    assert model.transfer.near!=model.transfer.far
    if model.kind=="theorem":
        assert len(model.proof_steps)==3 and len(model.rationale_steps)==0
    else:
        assert len(model.rationale_steps)==3 and len(model.proof_steps)==0
    if model.kind=="concept":
        assert model.definition==RECORDS[i]["definition"]
    else:
        assert RECORDS[i]["definition"] in model.statement
        assert RECORDS[i]["statement"] in model.statement

@pytest.mark.parametrize("i",range(1,13))
def test_independent_finite_premises_called(i):
    v=check(i)
    assert v["source_candidate_id"]==IDS[i-1]
    assert v["finite_positive_case"] is True
    assert v["invalid_premise_rejected"] is True
    assert v["general_theorem_certified"] is v["teacher_approved"] is v["student_publishable"] is False

@pytest.mark.parametrize("bad",[True,False,0,-1,13,1.0,"1",None])
def test_illegal_witness_id_rejected(bad):
    with pytest.raises(ValueError):check(bad)

@pytest.mark.parametrize("i",range(12))
def test_teacher_only_search_never_leaks(i,result):
    doc=result[0][i]
    assert any(x.id==doc["id"] for x in lessons())
    assert any(x["knowledge_id"]==doc["id"] for x in editor_draft_search(
        doc["title"],scope="EDITOR_LOCAL",limit=20))
    with pytest.raises(EditorOnlyError):editor_draft_search(doc["title"])
    with pytest.raises(EditorOnlyError):editor_draft_full(doc["id"])
    result=student_evidence_lookup(doc["title"])
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert result["teacher_solution_exposed"] is False
    for e in doc["worked_examples"]:
        assert e["answer"] not in json.dumps(result,ensure_ascii=False)

@pytest.mark.parametrize("i",range(12))
def test_mutated_deep_source_or_proof_assumptions_rejected(i):
    rec=deepcopy(RECORDS);rec[i]["anchor"]="FAKE-SOURCE"
    with pytest.raises(ValueError,match="source"):BD.build(records=rec)
    rec=deepcopy(RECORDS);rec[i]["assumptions"]=[]
    with pytest.raises(ValueError,match="assumptions"):BD.build(records=rec)
    rec=deepcopy(RECORDS);rec[i]["examples"]=rec[i]["examples"][:1]
    with pytest.raises(ValueError,match="examples"):BD.build(records=rec)

@pytest.mark.parametrize("i",range(12))
def test_scope_provenance_review_and_counterexample(i,ledger):
    row=ledger[1][i]
    assert row["anchor"]==SCOPES[i]["anchor"]
    assert row["status"]=="INDIVIDUAL_SCOPE_EDITORIAL_PENDING"
    assert row["teacher_approval"] is row["official_atom_id"] is None
    assert row["student_publishable"] is row["automatic_general_theorem_proof"] is False
    assert row["source_line_sha256"]==next(x for x in ledger[0]["candidates"]
        if x["candidate_id"]==row["anchor"])["source_line_sha256"]
    assert all(len(row[k])>=25 for k in ("scope","assumptions","positive","nonexample","relation"))

@pytest.mark.parametrize("i",range(12))
def test_fake_scope_or_missing_logic_rejected(i):
    scopes=deepcopy(SCOPES);scopes[i]["anchor"]="FAKE-SOURCE"
    with pytest.raises(ValueError,match="scope source"):BM.build(scopes=scopes)
    scopes=deepcopy(SCOPES);scopes[i]["nonexample"]=""
    with pytest.raises(ValueError,match="scope missing"):BM.build(scopes=scopes)

def test_duplicate_between_deep_and_scope_rejected():
    scopes=deepcopy(SCOPES)
    scopes[0]["anchor"]=RECORDS[0]["anchor"]
    with pytest.raises(ValueError,match="scope source"):BM.build(scopes=scopes)

def test_builder_files_are_deterministic(result,ledger):
    assert json.loads(BD.PACK.read_text())==result[0]
    assert json.loads(BD.AUDIT.read_text())==result[1]
    assert BD.DOC.read_text()==BD.to_markdown(*result)
    assert json.loads(BM.OUTPUT.read_text())==ledger[0]
    assert json.loads(BM.OUTSCOPES.read_text())==ledger[1]
    assert BM.MARKDOWN.read_text()==BM.markdown(*ledger)

def test_independent_exact_parameter_sweeps_and_caveats():
    assert len(cuboid_vertices(2,3,4))==8
    for a,b,c in product(range(1,4),repeat=3):
        vertices=cuboid_vertices(a,b,c)
        assert len(vertices)==8
        assert (a,b,c) in vertices and (0,0,0) in vertices
    for n in range(1,60):
        eps=Q(1,n)
        threshold=reciprocal_epsilon_N(eps)
        assert threshold==n+1
        assert all(Q(1,k)<eps for k in range(threshold,threshold+15))
    for left,right in ((-4,-2),(-2,1),(0,3),(2,5),(-3,0)):
        mn,mx=squared_poly_on_closed_interval(left,right)
        brute=[Q(k,10)**2 for k in range(10*left,10*right+1)]
        assert mn==min(brute) and mx==max(brute)
    assert pearson_2x2(((1,1),(1,1)))[0]==0
    assert pearson_2x2(((1,0),(0,1)))[2] is False
    assert bivariate_cov_determinant(2,3,Q(1,2))==27
    with pytest.raises(ValueError):normal_standardized(0,-1,1)
    with pytest.raises(ValueError):diagonal_input_output(2,0,1,1)
    with pytest.raises(ValueError):spatial_line_distance_sq((0,0,0),(0,0,0),(1,0,0),(0,1,0))
    with pytest.raises(ValueError):discrete_growth(1,Q(-3,2),2)
    with pytest.raises(ValueError):apply_isometry(((1,1),(0,1)),(1,2))
    with pytest.raises(ValueError):circle_rotation((0,0),(0,0),0)
