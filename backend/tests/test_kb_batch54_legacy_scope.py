"""Batch54: 12 independent scope drafts, 61-page blocker ledger, exact finite boundaries."""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import pytest

from app.kb_batch54_exact_review import reviewed_finite_witness as check, PreconditionsNotEstablished

ROOT=Path(__file__).resolve().parents[2]
S=importlib.util.spec_from_file_location("kb54_author",ROOT/"scripts/author_kb_batch54_legacy_scope.py")
G=importlib.util.module_from_spec(S)
S.loader.exec_module(G)
ROWS,GATE,SOURCE,EDITOR=G.build()
AUDIT=G.payload(ROWS,GATE,SOURCE,EDITOR)

def test_all_legacy_targets_get_independent_draft_not_certification():
    assert len(ROWS)==12
    assert {r["editorial_candidate_id"] for r in ROWS}=={
        x["editorial_id"] for x in SOURCE["legacy_non_equivalent_rows"]}
    assert AUDIT["official_source_pages"]==61
    assert AUDIT["legacy_mathematical_scope_equivalence_certified"]==0
    assert AUDIT["legacy_actual_teacher_approvals"]==0
    assert AUDIT["student_published"]==0
    assert all(v is None for v in AUDIT["official_atomic_denominator"].values())
    assert all(v is None for v in AUDIT["official_coverage_ratio"].values())
    assert AUDIT["student_retrieval"]["teacher_solutions"]==[]

@pytest.mark.parametrize("index",range(12))
def test_each_legacy_card_complete_and_locked(index):
    r=ROWS[index]
    assert G.Legacy54.model_validate(r)
    assert r["review"]=={"status":"REVIEW_PENDING","reviewer_id":None,
                         "reviewed_at":None,"review_record":None}
    assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert r["student_publishable"] is False
    assert r["proof_verification"]=="NOT_FORMALLY_CERTIFIED"
    assert r["source_license"]=="PROJECT_AUTHORED"
    original=next(x for x in SOURCE["legacy_non_equivalent_rows"] if x["editorial_id"]==r["editorial_candidate_id"])
    page=next(x for x in GATE["pages"] if x["printed_page"]==original["source_page"])
    assert r["syllabus_track"]==original["track"]
    assert r["source_printed_page"]==page["printed_page"]
    assert r["source_pdf_sha256"]==SOURCE["source_pdf_sha256"]
    assert r["source_page_sha256"]==page["pdfkit_page_text_sha256"]
    assert r["source_standard_version"]=="CN-HS-MATH-2017-REV2020"
    assert r["official_scope_equivalence"]=="NOT_CERTIFIED"
    assert r["source_editorial_goal"]==original["original_goal"]
    assert len(r["prerequisite_topics"])==3 and len(r["notation"])>=1
    assert len(r["reasoning_steps"])==3
    assert len(r["worked_examples"])==2
    assert len(r["hint_ladder"])==3
    assert all(x["steps"][0]!=x["steps"][1] for x in r["worked_examples"])
    assert len(r["transfer"]["near"])>11 and len(r["transfer"]["far"])>11

@pytest.mark.parametrize("index",range(61))
def test_each_source_page_keeps_uncertified_denominator(index):
    p=AUDIT["source_pages"][index]
    assert p["page"]==index+13 and p["pdf_page_index"]==index+20
    assert len(p["source_page_sha256"])==64
    assert p["official_atom_count"] is None
    assert p["full_page_manual_atomization"]=="NOT_COMPLETED"
    assert p["source_page_fingerprint_present"] is True

@pytest.mark.parametrize("mutation",[
    "delete_legacy","fake_teacher","fake_editorial_teacher","fake_official",
    "missing_source_page","wrong_source_sha","duplicate_card","fake_old_link",
    "lost_cross_page_candidate","missing_card","false_page_review"
])
def test_scope_gate_fails_closed(mutation):
    kw={}
    if mutation=="delete_legacy":
        x=deepcopy(SOURCE);x["legacy_non_equivalent_rows"].pop();kw["source"]=x
    if mutation=="fake_teacher":
        x=deepcopy(SOURCE);x["legacy_non_equivalent_rows"][0]["teacher_review"]="APPROVED";kw["source"]=x
    if mutation=="fake_editorial_teacher":
        x=deepcopy(EDITOR);x["rows"][0]["teacher_approved"]=True;kw["overlay"]=x
    if mutation=="fake_official":
        x=deepcopy(SOURCE);x["official_atomic_denominator"]["ELECTIVE_A"]=200;kw["source"]=x
    if mutation=="missing_source_page":
        x=deepcopy(GATE);x["pages"].pop();kw["gate"]=x
    if mutation=="wrong_source_sha":
        x=deepcopy(GATE);x["source_pdf_sha256"]="0"*64;kw["gate"]=x
    if mutation=="duplicate_card":
        x=deepcopy(G.CARDS);x[1]["cid"]=x[0]["cid"];kw["cards"]=x
    if mutation=="fake_old_link":
        x=deepcopy(EDITOR);target=next(r for r in x["rows"] if r["editorial_id"]==G.CARDS[0]["cid"])
        target["direct_review_drafts"]=["falsified:approved"];kw["overlay"]=x
    if mutation=="lost_cross_page_candidate":
        x=deepcopy(SOURCE);x["source_rows"].pop();kw["source"]=x
    if mutation=="missing_card":
        x=deepcopy(G.CARDS);x.pop();kw["cards"]=x
    if mutation=="false_page_review":
        x=deepcopy(GATE);x["pages"][10]["full_page_human_review"]="APPROVED";kw["gate"]=x
    with pytest.raises(ValueError):G.build(**kw)

@pytest.mark.parametrize("index",range(12))
def test_student_lookup_and_tutor_deny_unapproved_legacy(index):
    from app.deep_retrieval import student_evidence_lookup
    from app.model_tutor_draft import draft_next_question
    r=ROWS[index]
    query=r["title"]+"；"+r["claim"][:100]
    res=student_evidence_lookup(query,limit=3)
    assert res["status"]=="NO_APPROVED_EVIDENCE"
    assert res["candidates"]==[]
    assert res["teacher_solution_exposed"] is False
    draft=draft_next_question(query,mode="GUIDE",help_requested=True,
        consent_to_cloud=True,operator_scope="EDITOR_LOCAL",
        provider_url="https://api.openai.com/v1/chat/completions",
        provider_model="offline-test-do-not-call")
    assert draft.status=="BLOCKED" and draft.reason=="NO_APPROVED_MATH_EVIDENCE"
    assert draft.model_called is False
    assert draft.student_visible is False and draft.question_draft is None

def test_specific_exact_positive_witnesses_all_twelve():
    assert check("epsilon_inverse_n",epsilon=Fraction(1,11))["N"]==12
    assert check("bounded_prefix",values=[Fraction(1,2),-1,2])["bound"]==2
    assert check("monotone_prefix",values=[1,2,2,3])["nondecreasing"]
    assert check("ivt_polynomial",coefficients=[-2,0,1],left=1,right=2)["zero_bracketed_by_continuous_polynomial"]
    m=check("mvt_quadratic",p=1,q=0,r=0,left=1,right=3)
    assert m["witness_c"]==2 and m["slope"]==m["derivative_at_witness"]==4
    assert check("binomial_tail",trials=2,at_least=2)["p_value_under_fair_coin_null"]==Fraction(1,4)
    x=check("quadratic_differential",p=1,q=0,r=0,x=1,h=Fraction(1,10))
    assert (x["finite_delta"],x["linear_differential"],x["remainder"])==(Fraction(21,100),Fraction(1,5),Fraction(1,100))
    assert check("ftc_polynomial",coefficients=[0,2],left=0,right=2)["integral"]==4
    assert check("classical_logic",p=True)["noncontradiction"]
    assert check("production_power",A=2,L=4,K=9,alpha=1,beta=1)["Q"]==72
    assert check("beat_lcm",periods=[6,8],beats_per_minute=120)["seconds"]==12
    assert check("affine_recurrence",a=2,b=1,x0=0,n=3)["iterated_value"]==7

@pytest.mark.parametrize("op,kwargs",[
    ("epsilon_inverse_n",{"epsilon":-1}),
    ("epsilon_inverse_n",{"epsilon":0}),
    ("epsilon_inverse_n",{"epsilon":1.0}),
    ("bounded_prefix",{"values":[1]}),
    ("bounded_prefix",{"values":[False,1]}),
    ("monotone_prefix",{"values":[1,"2"]}),
    ("ivt_polynomial",{"coefficients":[0,1],"left":1,"right":1}),
    ("ivt_polynomial",{"coefficients":[0,1],"left":0,"right":2.5}),
    ("mvt_quadratic",{"p":1,"q":0,"r":0,"left":3,"right":1}),
    ("binomial_tail",{"trials":0,"at_least":0}),
    ("binomial_tail",{"trials":2,"at_least":3}),
    ("quadratic_differential",{"p":1,"q":0,"r":0,"x":1,"h":True}),
    ("ftc_polynomial",{"coefficients":[],"left":0,"right":1}),
    ("ftc_polynomial",{"coefficients":[1],"left":2,"right":1}),
    ("classical_logic",{"p":1}),
    ("production_power",{"A":2,"L":0,"K":4,"alpha":1,"beta":1}),
    ("production_power",{"A":2,"L":4,"K":4,"alpha":-1,"beta":1}),
    ("beat_lcm",{"periods":[0,8],"beats_per_minute":120}),
    ("beat_lcm",{"periods":[3,8],"beats_per_minute":0}),
    ("beat_lcm",{"periods":[3],"beats_per_minute":120}),
    ("affine_recurrence",{"a":2,"b":1,"x0":0,"n":-1}),
    ("affine_recurrence",{"a":2,"b":1,"x0":0,"n":True}),
    ("forged_approval",{"status":"APPROVED"}),
    ("epsilon_inverse_n",{"epsilon":1,"status":"APPROVED"}),
])
def test_invalid_or_unestablished_premises_rejected(op,kwargs):
    with pytest.raises(PreconditionsNotEstablished):check(op,**kwargs)

@pytest.mark.parametrize("n",range(0,21))
def test_affine_recurrence_a_one_branch_and_formula(n):
    r=check("affine_recurrence",a=1,b=2,x0=3,n=n)
    assert r["iterated_value"]==3+2*n==r["finite_sum_formula"]
    assert r["a_equals_one_branch_used"] is True

@pytest.mark.parametrize("n",range(0,21))
def test_affine_recurrence_a_zero_branch(n):
    r=check("affine_recurrence",a=0,b=2,x0=3,n=n)
    assert r["iterated_value"]==(3 if n==0 else 2)
    assert r["finite_sum_formula"]==r["iterated_value"]

@pytest.mark.parametrize("p",[-3,-1,0,1,2,5])
@pytest.mark.parametrize("x",[-3,-1,0,1,4])
def test_differential_quadratic_exact_remainder(p,x):
    r=check("quadratic_differential",p=p,q=2,r=1,x=x,h=Fraction(1,7))
    assert r["remainder"]==Fraction(p,49)==r["expected_remainder"]

@pytest.mark.parametrize("p",[False,True])
def test_two_boolean_semantics_rows(p):
    r=check("classical_logic",p=p)
    assert r["noncontradiction"] is True
    assert r["excluded_middle"] is True
    assert r["same_syntax"] is False

def test_no_overclaim_in_negative_finite_examples():
    assert check("bounded_prefix",values=[1,-1,1,-1])["status"]=="FINITE_PREFIX_ONLY_NOT_CONVERGENCE"
    assert not check("monotone_prefix",values=[1,-1,1,-1])["nondecreasing"]
    r=check("ivt_polynomial",coefficients=[1,0,1],left=-1,right=1)
    assert r["zero_bracketed_by_continuous_polynomial"] is False
    assert r["root_unique"]=="UNDETERMINED"
    assert check("binomial_tail",trials=2,at_least=2)["posterior_h0"]=="NOT_DETERMINED"
    assert check("beat_lcm",periods=[3,4],beats_per_minute=None)["seconds"] is None

def test_generated_seed_sha_and_page_ledger_exactly_replay():
    G.create(check=True)
    file_a=json.loads((ROOT/"docs/evaluation/KB_BATCH54_SCOPE_AND_DENOMINATOR_AUDIT.json").read_text())
    assert file_a["official_atomic_denominator"]==AUDIT["official_atomic_denominator"]
    assert len(file_a["source_pages"])==61
    assert file_a["legacy_only_replacement_manuscripts"]==12
