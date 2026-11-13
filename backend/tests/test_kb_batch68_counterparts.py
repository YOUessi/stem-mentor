"""Batch68 source-backed counterpart drafts, independent finite checks and fail-closed Agent."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch68_counterparts as B

@pytest.fixture(scope="module")
def generated():
    return B.build()

def test_frozen_reproducibility_and_mac_source():
    B.write(check=True)
    if Path("/private/tmp/kb56_page_15.txt").is_file():
        B.write(check=True,verify_local=True)

def test_lineage_and_seven_track_unknown_denominators(generated):
    lessons, ledger, loc = generated
    assert len(lessons["items"])==20 and len(ledger["records"])==62
    assert len(loc)==20
    assert ledger["official_atomic_denominator"]=={t:None for t in B.TRACKS}
    assert ledger["total_provisional_candidates"]==62
    assert ledger["explicitly_drafted_second_candidates"]==20
    assert ledger["not_explicitly_drafted_in_batch68"]==42
    assert ledger["teacher_approved"]==ledger["formal_proofs_certified"]==0
    assert ledger["student_published"]==ledger["officially_fully_reviewed_pages"]==0
    assert len({x["editorial_id"] for x in lessons["items"]})==20

@pytest.mark.parametrize("idx", B.SELECTED)
def test_each_teacher_draft_is_substantive_and_safe(generated,idx):
    r=next(v for v in generated[0]["items"] if v["lesson_id"]==f"KB68-ATOM-{idx:02}")
    assert r["source_license"]=="ORIGINAL_PROJECT_AUTHORED"
    assert r["official_atomic_membership"]=="UNDETERMINED"
    assert r["teacher_review"]=="REVIEW_PENDING"
    assert r["teacher_signature"] is None
    assert r["proof_certification"]=="NOT_FORMALLY_CERTIFIED"
    assert r["finite_math_witness"]=="FINITE_EXACT_INSTANCE_ONLY"
    assert not r["official_clause_full_text_verified"]
    assert not r["student_publishable"] and not r["student_freeform_steps_verified"]
    assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert len(r["reasoning"])==3
    assert len({step["claim"] for step in r["reasoning"]})==3
    assert len(r["worked_examples"])==2
    assert len({e["question"] for e in r["worked_examples"]})==2
    assert len({e["teacher_solution"] for e in r["worked_examples"]})==2
    assert len(r["hint_ladder"])==3 and all(r["hint_ladder"])
    assert len(set(r["hint_ladder"]))==3
    assert r["notation"] and r["notation"]!="使用题中已明确的变量、论域及数学符号"
    assert len(r["invalid_case"])>15 and len(r["explanation_of_error"])>12
    assert r["near_transfer"]!=r["far_transfer"]
    assert r["source_page"]>=15
    assert len(r["source_line_sha256"])==len(r["source_window_sha256"])==64

@pytest.mark.parametrize("idx", B.SELECTED)
def test_independent_exact_math_boundary(idx):
    assert B.exact_case(idx) is True

@pytest.mark.parametrize("i",range(62))
def test_all_provisional_atoms_keep_unknown_official_status(generated,i):
    row=generated[1]["records"][i]
    assert row["official_atom_approved"] is False
    assert row["full_official_clause_review"]=="NOT_COMPLETED"
    assert row["teacher_approved"] is False
    assert row["independent_math_proof_certified"] is False
    assert row["student_publishable"] is False
    if row["author_draft_id"]:
        assert row["content_review"]=="REVIEW_PENDING"

@pytest.mark.parametrize("idx",range(20))
def test_provenance_forgery_denied(idx):
    props=deepcopy(B.load(B.PROPOSALS))
    j=2*(B.SELECTED[idx]-1)+1
    props["proposals"][j]["source_window_sha256"]="0"*64
    with pytest.raises(ValueError,match="Source page/window SHA"):
        B.build({"proposals":props})

@pytest.mark.parametrize("idx",range(20))
def test_fake_teacher_review_denied(idx):
    props=deepcopy(B.load(B.PROPOSALS))
    j=2*(B.SELECTED[idx]-1)+1
    props["proposals"][j]["teacher_review"]="APPROVED"
    with pytest.raises(ValueError,match="Forged teacher status"):
        B.build({"proposals":props})

@pytest.mark.parametrize("idx",range(20))
def test_draft_already_certified_not_accepted(idx):
    props=deepcopy(B.load(B.PROPOSALS))
    j=2*(B.SELECTED[idx]-1)+1
    props["proposals"][j]["content_lesson_complete"]=True
    with pytest.raises(ValueError,match="already certified complete"):
        B.build({"proposals":props})

def test_authoring_row_missing_or_short_rejected():
    lines=B.DATA.read_text(encoding="utf-8")
    with pytest.raises(ValueError,match="Missing, repeated"):
        B.parse_authoring("\n".join(lines.splitlines()[:-1]))
    with pytest.raises(ValueError,match="exactly fifteen"):
        B.parse_authoring(lines+"\n1§bad data\n")

def test_forged_status_or_student_publish_release_denied():
    for key,value in [("teacher_review","APPROVED"),("student_publishable",True),
                      ("math_equivalence","CERTIFIED"),("official_atomic_membership","CERTIFIED")]:
        props=deepcopy(B.load(B.PROPOSALS))
        target=props["proposals"][1]
        target[key]=value
        with pytest.raises(ValueError,match="Forged teacher status|improperly promoted"):
            B.build({"proposals":props})

def test_unsafe_cross_page_prerequisite_denied():
    props=deepcopy(B.load(B.PROPOSALS))
    props["proposals"][1]["parent_anchor_id"]="KB61-P016-L010"
    with pytest.raises(ValueError,match="shared source scope"):
        B.build({"proposals":props})

def test_student_knowledge_store_contains_no_new_draft():
    from app.deep_knowledge import lessons
    ids={x.id for x in lessons()}
    assert not ids.intersection({x["lesson_id"] for x in B.load(B.OUT)["items"]})

from test_attested_release_batch08 import offline_reviewer_fixture

@pytest.mark.parametrize("idx",range(20))
def test_nonempty_student_approved_retrieval_does_not_leak_draft(idx,offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    lesson=B.load(B.OUT)["items"][idx]
    found=student_evidence_lookup(lesson["title"])
    assert {x["knowledge_id"] for x in found["candidates"]}<={doc.id}
    raw=json.dumps(found,ensure_ascii=False)
    assert lesson["lesson_id"] not in raw
    assert all(e["teacher_solution"] not in raw for e in lesson["worked_examples"])
    assert not found["teacher_solution_exposed"]
    assert not found["unverified_content_exposed"]


def test_amgm_negative_premise_arithmetic_is_not_misreported():
    row=next(x for x in B.load(B.OUT)["items"] if x["lesson_id"]=="KB68-ATOM-08")
    assert "-5/2" in row["invalid_case"]
    assert "-5，" not in row["invalid_case"]
    from fractions import Fraction
    assert (Fraction(-1)+Fraction(-4))/2==Fraction(-5,2)

def test_hint_templates_cannot_be_missing_or_repeated():
    hints=B.HINTS.read_text(encoding="utf-8")
    with pytest.raises(ValueError,match="Expected 20 matching"):
        B.parse_hints("\n".join(hints.splitlines()[:-1]))
    bad=hints.replace("首先把正切表达式按定义重新写成正弦与余弦的商。",
                      "先找分母会变成零的角度再考虑化简。")
    with pytest.raises(ValueError,match="Repeating hints"):
        B.parse_hints(bad)

@pytest.mark.parametrize("idx", B.SELECTED)
def test_unique_domain_specific_progressive_hints(idx):
    v=next(v for v in B.load(B.OUT)["items"] if v["lesson_id"]==f"KB68-ATOM-{idx:02}")
    hints=B.parse_hints()[idx]
    assert v["notation"]==hints[0]
    assert v["hint_ladder"]==hints[1:]
    assert len(set(v["hint_ladder"]))==3
