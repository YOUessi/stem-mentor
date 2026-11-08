"""Batch32 pinned Mac source audit and independent finite-math negative tests."""
from __future__ import annotations
import copy
import json
import sys
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path
import pytest
from app.kb_batch32_selective_finite_math import OPS,finite,guarded_evaluate
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch32_source_atoms as atom
import build_kb_batch32_math_links as math_links

SRC=json.loads(atom.OUT.read_text(encoding="utf-8"))
MATH=json.loads(math_links.OUT.read_text(encoding="utf-8"))
LINKS=json.loads(math_links.LINKS.read_text(encoding="utf-8"))
FIX={x["op"]:x for x in LINKS["fixtures"]}

def test_source_full_rebuild_and_no_approvals():
    assert json.loads(atom.build())==SRC
    s=SRC["summary"]
    assert (s["new_editorial_atom_candidates"],s["batch31_editorial_candidates"],s["total_provisional_editorial_candidates"])==(130,87,217)
    assert (s["unique_pages_text_or_image_examined"],s["pages_remaining_without_content_inspection"])==(37,24)
    assert (s["by_track_partial_editorial_counts"]["COMPULSORY"],s["by_track_partial_editorial_counts"]["SELECTIVE_COMPULSORY"])==(125,92)
    assert s["source_page_35_pdfkit_corrupt_requires_visual_review"]
    assert not SRC["evidence_boundary"]["curriculum_requirements_exhaustively_decomposed"]
    assert not SRC["evidence_boundary"]["numbered_and_unnumbered_requirements_all_mapped"]
    assert all(v is None for v in SRC["official_denominators_by_track"].values())
    assert (s["teacher_approved_lessons"],s["student_published_deep_lessons"],s["teacher_verified_curriculum_atoms"])==(0,0,0)
    assert len({x["editorial_id"] for x in SRC["new_items"]})==130
    assert len({x["original_project_authored_goal"] for x in SRC["new_items"]})==130

@pytest.mark.parametrize("r",SRC["new_items"],ids=lambda x:x["editorial_id"])
def test_each_130_candidate_source_track_and_zero_student_approval(r):
    page=r["source_printed_page"]
    assert r["source_pdf_page_index_zero_based"]==page+7
    assert r["source_original_pdf_sha256"]==atom.PDF_SHA
    assert r["source_mac_pdfkit_page_sha256"]==atom.PAGE_DIGESTS[page]
    assert r["source_anchor_level"]=="PAGE_ONLY_NUMBERED_AND_UNNUMBERED_CLAUSES_NOT_VERIFIED"
    assert r["official_clause_alignment_verified"] is False
    assert r["teacher_review"]=="PENDING" and r["math_proof_certification"]=="NOT_FORMALLY_VERIFIED"
    assert r["official_atom_id"] is r["approved_lesson_id"] is None
    assert not r["student_publishable"] and r["student_solution_visibility"]=="NONE"
    assert r["syllabus_track"]==("COMPULSORY" if page<=35 else "SELECTIVE_COMPULSORY")

@pytest.mark.parametrize("bad",[
    "35|COMPULSORY|建模|method|Y|不能把文本乱码的图表视为已核实教学目标",
    "38|COMPULSORY|数列|concept|N|不能把选择性必修课程内容错误标成必修",
    "47|SELECTIVE_COMPULSORY|概率|method|Y|这个页面中选学标记需要正确逐项检查",
    "47|SELECTIVE_COMPULSORY|概率|method|N|短",
    "41|SELECTIVE_COMPULSORY|数列|proof|N|不存在的知识类型不能进入正式课程映射",
    "13|COMPULSORY|函数|method|N|完全没有被本批 PDFKit 文本初查核实的页面",
    "38|SELECTIVE_COMPULSORY|数列|concept|N|同一学习目标不允许在此重复\n38|SELECTIVE_COMPULSORY|数列|concept|N|同一学习目标不允许在此重复",
])
def test_scope_restriction_duplicate_or_bad_star_refusal(bad):
    with pytest.raises(ValueError):
        atom.parse_seed(bad)

def test_attested_seed_cannot_silently_change(monkeypatch):
    monkeypatch.setattr(atom,"SEED_SHA","0"*64)
    with pytest.raises(ValueError,match="seed drift"):
        atom.build()

@pytest.mark.parametrize("mutate",["source_sha","track","page_index","page_text"])
def test_source_ledger_tampering_refused(mutate):
    bad=copy.deepcopy(atom.previous.read_ledger())
    if mutate=="source_sha":bad["source"]["sha256"]="e"*64
    else:
        p=next(x for x in bad["pages"] if x["printed_page"]==38)
        if mutate=="track":p["tracks_present"]=["COMPULSORY"]
        if mutate=="page_index":p["pdf_page_index"]=12
        if mutate=="page_text":p["pdf_text_sha256"]="e"*64
    with pytest.raises(ValueError):
        atom.build(ledger=bad)

def test_page35_corrupted_text_not_masked_as_atoms():
    p=next(x for x in SRC["pages"] if x["printed_page"]==35)
    assert p["new_editorial_candidates"]==0
    assert p["inspection_state"]=="MAC_PDFKIT_TEXT_INSPECTED_BATCH32"
    assert p["unnumbered_clause_completeness"]=="UNKNOWN"
    assert SRC["high_priority_unresolved"][0].startswith("Printed p35")

def test_six_manual_source_math_links_and_rejections():
    assert json.loads(math_links.build())==MATH
    assert len(MATH["items"])==len(OPS)==6
    assert MATH["teacher_release_unchanged"] is True
    assert MATH["summary"]["formal_general_proof_certificates"]==0
    assert MATH["summary"]["student_freetext_steps_verified"]==0
    for op in OPS:
        good=guarded_evaluate(op,FIX[op]["valid"])
        bad=guarded_evaluate(op,FIX[op]["invalid"])
        assert good["status"]=="VERIFIED_FINITE_INSTANCE" and good["witness"]
        assert bad["status"]=="CONDITIONS_NOT_ESTABLISHED" and bad["witness"] is None
        assert not any(good[k] or bad[k] for k in (
            "whole_theorem_certified","student_freeform_step_verified","teacher_approved",
            "official_curriculum_atom_verified","student_solution_release_authorized"))

@pytest.mark.parametrize("mutation",["approval","publish","missing_fixture","wrong_atom","fake_op","short_rationale"])
def test_math_fixture_schema_or_wrong_atom_refused(mutation):
    d=copy.deepcopy(LINKS)
    if mutation=="approval":d["teacher_approved"]=True
    if mutation=="publish":d["student_publishable"]=True
    if mutation=="missing_fixture":d["fixtures"].pop()
    if mutation=="wrong_atom":d["fixtures"][0]["editorial_id"]="KB32-SELE-P038-A004"
    if mutation=="fake_op":d["fixtures"][1]["op"]="freeform_llm_grade"
    if mutation=="short_rationale":d["fixtures"][2]["math_justification"]="trivial"
    with pytest.raises(ValueError):
        math_links.build(links=d)

@pytest.mark.parametrize("bad",[
    "__import__('os').system('echo no')","1e3","1/0","00",True,2.5,"999999999",
    {"expr":"1+2"},[1,2],None
])
def test_math_numeric_parser_refuses_untrusted_inputs(bad):
    payload=dict(FIX["arithmetic_series"]["valid"],first=bad)
    assert guarded_evaluate("arithmetic_series",payload)["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("a,d,n",product(range(-3,4),range(-2,3),range(1,12)))
def test_arithmetic_formula_matches_direct_sum_exact(a,d,n):
    z=finite("arithmetic_series",{"first":a,"difference":d,"n":n})
    assert z["direct"]==z["formula"]==sum((F(a+d*k) for k in range(n)),F())

@pytest.mark.parametrize("n,k",[(n,k) for n in range(36) for k in range(n+1)])
def test_all_bounded_binomial_choice_cases(n,k):
    z=finite("binomial_choice",{"n":n,"k":k})
    assert z["count"]==comb(n,k)
    assert z["symmetry"] is z["pascal"] is True

@pytest.mark.parametrize("N,K,n,k",[
    (N,K,n,k) for N in range(2,10) for K in range(N+1)
    for n in range(N+1) for k in range(n+1) if k<=K and n-k<=N-K
])
def test_hypergeometric_exact_mass_grid(N,K,n,k):
    z=finite("hypergeometric_mass",{
        "population":N,"successes":K,"draws":n,"observed":k})
    assert z["mass"]==F(comb(K,k)*comb(N-K,n-k),comb(N,n))

@pytest.mark.parametrize("A,B,C,x,y",[
    (A,B,C,x,y) for A,B in product((-3,-2,-1,0,1,3),repeat=2) if (A,B)!=(0,0)
    for C,x,y in ((-1,0,0),(3,2,-2),(0,1,1))
])
def test_point_line_distance_squared_exact_nonnegative(A,B,C,x,y):
    z=finite("point_line_distance_squared",{"A":A,"B":B,"C":C,"x":x,"y":y})
    assert z["exact_distance_squared"]>=0
    assert z["exact_distance_squared"]==F((A*x+B*y+C)**2,A*A+B*B)

@pytest.mark.parametrize("m,b",product(range(-5,6),range(-3,4)))
def test_least_squares_line_exact_recovery_on_nonconstant_linear_samples(m,b):
    x=[0,1,2,4];y=[b+m*t for t in x]
    z=finite("least_squares_line",{"x":x,"y":y})
    assert z["slope"]==m and z["intercept"]==b
    assert z["sum_residuals"]==z["sum_x_residuals"]==0

@pytest.mark.parametrize("A,B",[(a,b) for a in range(4) for b in range(4)])
def test_conditional_probability_correct_for_all_small_subsets(A,B):
    universe=[0,1,2,3];a=[i for i in universe if (A>>i)&1]
    b=[i for i in universe if (B>>i)&1]
    z=guarded_evaluate("conditional_probability_finite",{
        "universe":universe,"event_a":a,"event_b":b})
    if not b:assert z["status"]=="CONDITIONS_NOT_ESTABLISHED"
    else:
        assert z["status"]=="VERIFIED_FINITE_INSTANCE"
        assert z["witness"]["conditional"]==F(len(set(a)&set(b)),len(b))
