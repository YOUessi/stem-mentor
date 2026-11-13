"""Batch133 official source *proposal* audit & teacher-only safety regression.

No test in this module upgrades candidate counts to the complete syllabus denominator.
Mac-only licensed-PDF replay is performed by --check-mac outside GitHub Actions.
"""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch133_atomization as a
import build_kb_batch133_lessons as l
import check_kb_batch133_math as m

@pytest.fixture(scope="module")
def inventory():
    return json.loads(a.OUT.read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def lessons():
    return json.loads(l.OUT.read_text(encoding="utf-8"))

def test_complete_offline_contract(inventory,lessons):
    assert a.validate(inventory) and l.validate(lessons)
    assert inventory["proposed_count"]==41
    assert inventory["official_atom_denominator"] is None
    assert inventory["full_source_census_complete"] is False

def test_authorized_student_index_is_empty(inventory):
    index=json.loads(a.INDEX.read_text(encoding="utf-8"))
    assert index==a.safe_student_export(inventory)
    assert index["items"]==[] and index["publishable_count"]==0
    serialized=json.dumps(index)
    for term in ("teacher_examples","reasoned_solution","formal_definition_or_theorem"):
        assert term not in serialized

@pytest.mark.parametrize("spec",a.spec_rows(),ids=lambda x:x["slug"])
def test_each_source_proposal_has_locked_condition(spec,inventory):
    row=next(r for r in inventory["records"] if r["id"]=="kb133-proposal-"+spec["slug"])
    assert row["source_lock"]["printed_page"]==spec["printed_page"]
    assert len(row["source_lock"]["line_sha256"])==spec["end_line"]-spec["start_line"]+1
    assert row["student_authoritative"] is False
    assert row["official_atom_id"] is None
    assert row["atomization_review"]=="REVIEW_PENDING"
    assert row["false_inference"] and row["hypothesis"]

@pytest.mark.parametrize("field,forged",[
    ("teacher_approval",{"reviewer":"fake_teacher"}),
    ("official_atom_id","OFFICIAL-CLAIM-NOT-REVIEWED"),
    ("student_authoritative",True),
    ("atomization_review","APPROVED"),
    ("source_evidence_status","OFFICIAL_ATOM_CERTIFIED"),
    ("formal_proof_certified",True),
    ("source_pdf_sha256","0"*64),
])
@pytest.mark.parametrize("which",range(41))
def test_poisoned_authority_rejected(which,field,forged,inventory):
    x=copy.deepcopy(inventory)
    x["records"][which][field]=forged
    with pytest.raises(ValueError):
        a.validate(x)

@pytest.mark.parametrize("which",range(41))
@pytest.mark.parametrize("corruption",["line","span","boundary"])
def test_poisoned_source_commitments_rejected(which,corruption,inventory):
    x=copy.deepcopy(inventory)
    lock=x["records"][which]["source_lock"]
    if corruption=="line":
        lock["line_sha256"][0]="f"*64 if lock["line_sha256"][0]!="f"*64 else "e"*64
    elif corruption=="span":
        lock["span_sha256"]="f"*64 if lock["span_sha256"]!="f"*64 else "e"*64
    else:
        lock["start_line"]=0
    with pytest.raises(ValueError):
        a.validate(x)

@pytest.mark.parametrize("track",a.TRACKS)
def test_track_denominator_forgery_rejected(track,inventory):
    x=copy.deepcopy(inventory)
    x["track_denominators"][track]=5
    with pytest.raises(ValueError):
        a.validate(x)

@pytest.mark.parametrize("track",a.TRACKS)
def test_track_count_forgery_rejected(track,inventory):
    x=copy.deepcopy(inventory)
    x["by_track_proposals"][track]+=1
    with pytest.raises(ValueError):
        a.validate(x)

@pytest.mark.parametrize("which",range(41))
def test_orphan_prereq_rejected(which,inventory):
    x=copy.deepcopy(inventory)
    x["records"][which]["prerequisite_proposals"]=["fake-proposal"]
    with pytest.raises(ValueError):
        a.validate(x)

@pytest.mark.parametrize("which",range(6))
@pytest.mark.parametrize("field,forged",[
    ("teacher_review_status","APPROVED"),
    ("teacher_review_evidence",{"signature":"fake"}),
    ("teacher_solution_visibility","STUDENT"),
    ("student_authoritative",True),
    ("formal_proof_certified",True),
    ("free_student_step_verified",True),
])
def test_lessons_never_self_approve(which,field,forged,lessons):
    x=copy.deepcopy(lessons)
    x[which][field]=forged
    with pytest.raises(ValueError):
        l.validate(x)

@pytest.mark.parametrize("which",range(6))
def test_lesson_solution_removal_fails_gate(which,lessons):
    x=copy.deepcopy(lessons)
    x[which]["teacher_examples"][0]["reasoned_solution"]=[]
    with pytest.raises(ValueError):
        l.validate(x)

@pytest.mark.parametrize("which",range(6))
def test_lesson_shortened_reasoning_fails_gate(which,lessons):
    x=copy.deepcopy(lessons)
    x[which]["reasoned_steps"]=[]
    with pytest.raises(ValueError):
        l.validate(x)

@pytest.mark.parametrize("which",range(6))
def test_lesson_source_swap_fails_gate(which,lessons):
    x=copy.deepcopy(lessons)
    x[which]["source_line_lock"]=lessons[(which+1)%6]["source_line_lock"]
    with pytest.raises(ValueError):
        l.validate(x)

@pytest.mark.parametrize("case",m.cases(),ids=lambda r:r["id"])
def test_exact_finite_witnesses(case):
    assert case["outcome"]=="EXACT_FINITE_WITNESS_PASS"
    assert case["scope"]=="FINITE_SYMPY_EXACT_INSTANCE_NOT_GENERAL_THEOREM"

def test_math_oracles_recomputed():
    old=json.loads(m.OUT.read_text())
    assert m.audit(old)
    assert old["cases"]==m.cases()
    assert old["full_theorem_certified"] is False

def test_math_oracle_forged_approval_rejected():
    old=json.loads(m.OUT.read_text())
    old["teacher_approved"]=1
    with pytest.raises(ValueError):
        m.audit(old)

def test_preview_has_no_source_pdf_text(inventory):
    doc=a.REPORT.read_text(encoding="utf-8")
    assert "不是课标原文" in doc
    assert "UNKNOWN" in doc
    assert "REVIEW_PENDING" in doc
    assert "正式原子分母" not in doc or "UNKNOWN" in doc
    assert not any("原文全文" in r for r in [doc])

def test_source_row_and_lesson_linkage(inventory,lessons):
    refs={r["id"]:r for r in inventory["records"]}
    for row in lessons:
        assert row["candidate_id"] in refs
        assert row["source_line_lock"]==refs[row["candidate_id"]]["source_lock"]
        assert len(row["teacher_examples"])==2
        assert len(row["student_hint_ladder"])==3
