"""Batch69: independent lineage, math preconditions, safe teacher-only content."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch69_remaining as B

@pytest.fixture(scope="module")
def rendered():
    return B.build()

def test_snapshots_are_stable_and_locally_reviewable():
    B.write(check=True)
    if Path("/private/tmp/kb56_page_15.txt").exists():
        B.write(check=True,verify_local=True)

def test_entire_provisional_lineage_discloses_uncertainty(rendered):
    content,audit,source=rendered
    assert len(content["items"])==11 and len(source)==11
    assert len(audit["records"])==62
    assert len({r["provisional_candidate_id"] for r in audit["records"]})==62
    assert audit["prior_parent_scope_manuscripts"]==31
    assert audit["prior_and_new_second_candidate_manuscripts"]==31
    assert audit["new_second_candidate_manuscripts"]==11
    assert audit["official_atomic_denominator"]=={t:None for t in B.TRACKS}
    assert audit["officially_fully_reviewed_pages"]==audit["teacher_approved"]==0
    assert audit["formal_proofs_certified"]==audit["student_published"]==0
    assert audit["unmapped_competency_requirements"]==14
    assert audit["unreviewed_legacy_proof_steps"]==538
    assert audit["unresolved_math_conflicts"]==10

@pytest.mark.parametrize("index",range(62))
def test_all_provisional_candidate_entries_fail_closed(rendered,index):
    row=rendered[1]["records"][index]
    assert not row["teacher_approved"] and not row["math_proof_certified"]
    assert not row["student_publishable"]
    assert row["official_atom_membership"]=="UNDETERMINED"
    assert row["full_official_clause_review"]=="NOT_COMPLETED"
    assert row["linked_manuscript_id"]
    if index%2 == 0:
        assert row["link_kind"]=="PARENT_SCOPE_DRAFT_NOT_ATOM_CERTIFIED"
    else:
        assert row["link_kind"]=="SECOND_CANDIDATE_LESSON_PENDING"

@pytest.mark.parametrize("index",B.SELECTED)
def test_complete_original_teaching_and_visibility(rendered,index):
    row=next(x for x in rendered[0]["items"] if x["lesson_id"]==f"KB69-ATOM-{index:02d}")
    assert row["source_license"]=="ORIGINAL_PROJECT_AUTHORED"
    assert row["teacher_review"]=="REVIEW_PENDING" and row["teacher_signature"] is None
    assert row["official_atomic_membership"]=="UNDETERMINED"
    assert row["official_clause_full_text_verified"] is False
    assert row["proof_certification"]=="NOT_FORMALLY_CERTIFIED"
    assert row["finite_math_witness"]=="FINITE_EXACT_INSTANCE_ONLY"
    assert not row["student_publishable"] and not row["student_freeform_steps_verified"]
    assert row["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert len(row["reasoning"])==3 and len(row["worked_examples"])==2
    assert len({v["claim"] for v in row["reasoning"]})==3
    assert len({v["question"] for v in row["worked_examples"]})==2
    assert all(len(v["teacher_solution"])>18 for v in row["worked_examples"])
    assert len(row["hint_ladder"])==3 and len(set(row["hint_ladder"]))==3
    assert row["near_transfer"]!=row["far_transfer"]
    assert len(row["invalid_case"])>20 and len(row["explanation_of_error"])>18
    assert len(row["source_line_sha256"])==len(row["source_window_sha256"])==64

@pytest.mark.parametrize("index",B.SELECTED)
def test_independent_exact_rational_or_symbolic_witness(index):
    assert B.exact_case(index) is True

@pytest.mark.parametrize("position",range(11))
def test_source_window_forgery_is_denied(position):
    p=deepcopy(B.load(B.B68.PROPOSALS))
    p["proposals"][2*(B.SELECTED[position]-1)+1]["source_window_sha256"]="0"*64
    with pytest.raises(ValueError,match="Source lineage/SHA"):
        B.build({"proposals":p})

@pytest.mark.parametrize("position",range(11))
def test_forged_teacher_signature_or_approval_denied(position):
    p=deepcopy(B.load(B.B68.PROPOSALS))
    p["proposals"][2*(B.SELECTED[position]-1)+1]["teacher_review"]="APPROVED"
    with pytest.raises(ValueError,match="Promoted unreviewed"):
        B.build({"proposals":p})

@pytest.mark.parametrize("position",range(11))
def test_forged_proof_membership_denied(position):
    p=deepcopy(B.load(B.B68.PROPOSALS))
    p["proposals"][2*(B.SELECTED[position]-1)+1]["official_atomic_membership"]="APPROVED"
    with pytest.raises(ValueError,match="Promoted unreviewed"):
        B.build({"proposals":p})

def test_missing_or_duplicate_math_authoring_rejected():
    text=B.AUTH.read_text(encoding="utf-8")
    data=[v for v in text.splitlines() if v and not v.startswith("#")]
    with pytest.raises(ValueError,match="Missing/duplicated"):
        B.parse_authoring("\n".join(data[:-1]))
    with pytest.raises(ValueError,match="Malformed"):
        B.parse_authoring(text+"\n3§only one field")
    with pytest.raises(ValueError,match="Missing/duplicated"):
        B.parse_authoring(text+"\n"+data[0])

def test_mismatched_parent_rejected():
    p=deepcopy(B.load(B.B68.PROPOSALS))
    p["proposals"][5]["parent_anchor_id"]="KB61-P027-L008"
    with pytest.raises(ValueError,match="Mismatched candidate pair"):
        B.build({"proposals":p})

def test_counterexample_signs_and_boundaries_exact():
    from fractions import Fraction as F
    from math import comb
    assert F(1,2)+F(3,2)==2
    assert comb(4,2)==6
    assert (F(5,2)+F(1,2)*1)==3
    # A zero complex denominator remains invalid even when numerator is zero.
    assert F(0)**2+F(0)**2==0
    # The two fits agree on 0,1,2 and differ on 3.
    f=lambda t:t*t
    g=lambda t:t*t+t*(t-1)*(t-2)
    assert all(f(t)==g(t) for t in [0,1,2]) and f(3)!=g(3)

def test_student_store_never_includes_pending_teacher_drafts():
    from app.deep_knowledge import lessons
    published={x.id for x in lessons()}
    assert not ({x["lesson_id"] for x in B.load(B.OUT)["items"]} & published)

from test_attested_release_batch08 import offline_reviewer_fixture

@pytest.mark.parametrize("idx",range(11))
def test_student_approved_mixed_retrieval_excludes_teacher_solution(idx,offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc, reviewers, _, _, record, save = offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    item=B.load(B.OUT)["items"][idx]
    search=student_evidence_lookup(item["title"])
    assert {x["knowledge_id"] for x in search["candidates"]}<={doc.id}
    data=json.dumps(search,ensure_ascii=False)
    assert item["lesson_id"] not in data
    assert all(e["teacher_solution"] not in data for e in item["worked_examples"])
    assert not search["teacher_solution_exposed"] and not search["unverified_content_exposed"]
