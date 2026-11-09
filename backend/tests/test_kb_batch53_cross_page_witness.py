"""Batch53 regression for 35 source requirements + exact finite condition checks."""
from copy import deepcopy
from fractions import Fraction
import importlib.util
from pathlib import Path

import pytest

from app.kb_batch53_finite_witness import (
    PreconditionsNotEstablished as Missing,
    event_probability, conditional_probability, sequence_term_from_partial_sums,
    polynomial_derivative_at, derivative_affine_power_at, audit_frame_completeness,
    effective_compound_rate,
)

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location(
    "kb53_gate",ROOT/"scripts/build_kb_batch53_cross_page_review.py")
G=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)
DATA=G.assemble()
B52=G.load(G.BASE52)
B51=G.load(G.BASE51)
OVERLAY=G.load(G.EDITORIAL)
SOURCE=G.load(G.SOURCE)
VISUAL=G.load(G.VISUAL)


def test_baseline_coverage_and_no_overclaim():
    assert DATA["source_candidates"]==35
    assert DATA["previously_no_same_page_link"]==9
    assert DATA["previously_no_same_page_now_cross_page_topic_lead"]==9
    assert DATA["page35_visual_only_candidates"]==7
    assert DATA["cross_page_topic_links"]==29
    assert DATA["source_page_fingerprints_present"]==61
    assert DATA["project_editorial_candidates"]==313
    assert len(DATA["legacy_non_equivalent_rows"])==12
    assert set(DATA["official_atomic_denominator"])==set(G.TRACKS)
    assert all(x is None for x in DATA["official_atomic_denominator"].values())
    assert DATA["scope_equivalence_certified"]==0
    assert DATA["teacher_approved"]==DATA["student_published"]==0


@pytest.mark.parametrize("i",range(35))
def test_each_review_candidate_has_traceable_provisional_links(i):
    r=DATA["source_rows"][i]
    assert r["related_same_page"] or r["related_cross_page"]
    assert r["mathematical_equivalence"]=="NOT_ASSESSED"
    assert r["official_atom_certified"] is False
    assert r["full_lesson_proven"] is False
    assert r["student_publishable"] is False
    assert r["teacher_review"]=="REVIEW_PENDING"
    assert r["related_only_not_coverage"] is True
    assert r["cross_page_deduplication"]=="POTENTIAL_OVERLAP_REVIEW_PENDING"
    assert len(r["review_boundary_note"])>=16
    assert r["source_modality"] in {"PDFKIT_TEXT_FINGERPRINT","VISUAL_IMAGE_SHA_NOT_PDFKIT_TEXT"}
    if r["source_page"]==35:
        assert r["source_modality"]=="VISUAL_IMAGE_SHA_NOT_PDFKIT_TEXT"
        assert r["source_page_sha256"]==VISUAL["mac_rendered_page_png_sha256"]
    else:
        pp=next(p for p in SOURCE["pages"] if p["printed_page"]==r["source_page"])
        assert r["source_page_sha256"]==pp["pdfkit_text_sha256"]


@pytest.mark.parametrize("cid",list(G.LINKS))
def test_new_cross_page_links_track_and_source_are_consistent(cid):
    r=next(row for row in DATA["source_rows"] if row["source_candidate_id"]==cid)
    editor={r["editorial_id"]:r for r in OVERLAY["rows"]}
    assert tuple(r["related_cross_page"])==G.LINKS[cid]
    for eid in r["related_cross_page"]:
        e=editor[eid]
        assert e["track"]==r["track"]
        assert e["printed_page"]!=r["source_page"]
        assert e["teacher_approved"] is False
        assert e["student_published"] is False


@pytest.mark.parametrize("i",range(12))
def test_legacy_links_still_not_equivalent_or_released(i):
    r=DATA["legacy_non_equivalent_rows"][i]
    assert r["mathematical_equivalence"]=="NOT_CERTIFIED"
    assert r["teacher_review"]=="REVIEW_PENDING"
    assert r["student_visible"] is False
    assert r["requires_independent_content_review"] is True
    assert r["track"] in G.TRACKS


@pytest.mark.parametrize("failure",[
    "wrong_pdf_sha","dropped_source_page","false_official_denominator",
    "false_teacher_approval","missing_link_id","orphan_cross_page",
    "wrong_cross_track","wrong_same_page","false_b52_approved",
    "visual_as_pdfkit","visual_student_published","duplicate_visual_candidate",
    "missing_legacy_review","wrong_legacy_track",
])
def test_fail_closed_manipulated_review_records(failure):
    kw={}
    if failure=="wrong_pdf_sha":
        x=deepcopy(SOURCE); x["official_pdf_sha256"]="0"*64;kw["source"]=x
    if failure=="dropped_source_page":
        x=deepcopy(SOURCE);x["pages"].pop();kw["source"]=x
    if failure=="false_official_denominator":
        x=deepcopy(B52);x["official_atomic_denominator"]["COMPULSORY"]=313;kw["b52"]=x
    if failure=="false_teacher_approval":
        x=deepcopy(OVERLAY);x["rows"][0]["teacher_approved"]=True;kw["overlay"]=x
    if failure=="missing_link_id":
        x=deepcopy(G.LINKS);x.pop(next(iter(x)));kw["links"]=x
    if failure=="orphan_cross_page":
        x=deepcopy(G.LINKS);key=next(iter(x));x[key]=("NOT-A-REAL-EDITORIAL-ID",);kw["links"]=x
    if failure=="wrong_cross_track":
        x=deepcopy(G.LINKS);key=next(iter(x));x[key]=("KB32-S-P038-A001",);kw["links"]=x
    if failure=="wrong_same_page":
        x=deepcopy(G.LINKS);key=next(iter(x));x[key]=("KB32-C-P034-A001",);kw["links"]=x
    if failure=="false_b52_approved":
        x=deepcopy(B52);x["rows"][0]["official_atom_certified"]=True;kw["b52"]=x
    if failure=="visual_as_pdfkit":
        x=deepcopy(VISUAL);x["page_source_text_extractor"]="PDFKIT_FULL_PAGE_VERIFIED";kw["visual"]=x
    if failure=="visual_student_published":
        x=deepcopy(VISUAL);x["candidates"][0]["student_published"]=True;kw["visual"]=x
    if failure=="duplicate_visual_candidate":
        x=deepcopy(VISUAL);x["candidates"][1]["id"]=x["candidates"][0]["id"];kw["visual"]=x
    if failure=="missing_legacy_review":
        x=deepcopy(B51);x["legacy_non_equivalent_review_queue"].pop();kw["b51"]=x
    if failure=="wrong_legacy_track":
        x=deepcopy(B51);x["legacy_non_equivalent_review_queue"][0]["track"]="COMPULSORY";kw["b51"]=x
    with pytest.raises(ValueError):
        G.assemble(**kw)


@pytest.mark.parametrize("weights,event,expected",[
    ([1,1,1,1],[1,3],Fraction(1,2)),
    ([1,3],[1],Fraction(3,4)),
    ([0,2,2],[0,1],Fraction(1,2)),
    ([1,4,5],[],Fraction(0)),
    ([1,4,5],[0,1,2],Fraction(1)),
])
def test_weighted_probability_is_not_assumed_classical(weights,event,expected):
    assert event_probability(weights,event)==expected


@pytest.mark.parametrize("weights,event",[
    ([1,3],[1]),([0,2],[1]),([1,1],[3]),([1,1],[0,0]),([0,0],[0]),
    ([-1,2],[0]),([True,1],[0]),([1.0,2],[0]),
])
def test_classical_model_rejects_missing_preconditions(weights,event):
    with pytest.raises(Missing):
        event_probability(weights,event,classical_model=True)


def test_classical_and_condition_probability_with_positive_denominator():
    assert event_probability([2,2,2,2],[0,2],classical_model=True)==Fraction(1,2)
    assert conditional_probability([1,3,1,5],[0,1],[1,2])==Fraction(3,4)
    with pytest.raises(Missing,match="zero-probability"):
        conditional_probability([1,0,2],[0],[1])


@pytest.mark.parametrize("n,result",[(1,2),(2,3),(3,5),(4,7)])
def test_partial_sum_first_term_and_following_terms(n,result):
    assert sequence_term_from_partial_sums([2,5,10,17],n)==result


@pytest.mark.parametrize("n",[-1,0,5,True,1.5])
def test_partial_sum_undefined_index_rejected(n):
    with pytest.raises(Missing):
        sequence_term_from_partial_sums([2,5,10,17],n)


@pytest.mark.parametrize("coeffs,x,expected",[
    ([2],5,0),([0,1],2,1),([1,0,1],3,6),
    ([5,-3,2],Fraction(1,2),-1),([0,0,1,1],-1,1),
])
def test_polynomial_derivative_exact_at_rational_x(coeffs,x,expected):
    assert polynomial_derivative_at(coeffs,x)==expected


@pytest.mark.parametrize("a,b,n,x,expected",[
    (2,3,2,1,20),(-1,3,3,0,-27),(0,4,2,6,0),
    (Fraction(1,2),0,2,2,1),(3,-3,1,0,3),
])
def test_chain_rule_keeps_inner_derivative(a,b,n,x,expected):
    assert derivative_affine_power_at(a,b,n,x)==expected


@pytest.mark.parametrize("population,observed,status",[
    (["a","b"],["a","b"],"FRAME_IDENTITIES_EXACTLY_MATCH"),
    (["a","b"],["a","a"],"COUNT_EQUAL_WITH_DUPLICATES_NOT_COMPLETE"),
    (["a","b"],["c","b"],"COUNT_EQUAL_WRONG_MEMBERS_NOT_COMPLETE"),
    (["a","b"],["a"],"COUNT_DIFFERENT_NOT_COMPLETE"),
    (["a","b"],["b","a"],"FRAME_IDENTITIES_EXACTLY_MATCH"),
])
def test_census_count_not_equivalent_to_verified_frame(population,observed,status):
    assert audit_frame_completeness(population,observed)==status


@pytest.mark.parametrize("rate,m,expected",[
    (0,12,0),(Fraction(1,10),1,Fraction(1,10)),
    (Fraction(1,5),2,Fraction(21,100)),
])
def test_compounding_requires_stated_frequency(rate,m,expected):
    assert effective_compound_rate(rate,m)==expected


@pytest.mark.parametrize("m",[-1,0,False,366,1.2])
def test_compounding_missing_or_invalid_frequency(m):
    with pytest.raises(Missing):
        effective_compound_rate(Fraction(1,10),m)


@pytest.mark.parametrize("i",range(35))
def test_unapproved_source_candidates_never_enter_student_rag_or_cloud(i):
    from app.deep_retrieval import student_evidence_lookup
    from app.model_tutor_draft import draft_next_question
    row=DATA["source_rows"][i]
    query=row["goal_original_paraphrase"][:150]
    evidence=student_evidence_lookup(query,limit=3)
    assert evidence["status"]=="NO_APPROVED_EVIDENCE"
    assert evidence["candidates"]==[]
    assert evidence["teacher_solution_exposed"] is False
    draft=draft_next_question(
        query, mode="GUIDE", help_requested=True,
        consent_to_cloud=True, operator_scope="EDITOR_LOCAL",
        provider_url="https://api.openai.com/v1/chat/completions",
        provider_model="offline-test-do-not-call")
    assert draft.status=="BLOCKED"
    assert draft.reason=="NO_APPROVED_MATH_EVIDENCE"
    assert draft.model_called is False
    assert draft.student_visible is False
    assert draft.question_draft is None
