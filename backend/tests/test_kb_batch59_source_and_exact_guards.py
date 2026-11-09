"""Batch59 source SHA/optional-scope/competency and exact selective guards."""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import sys

import pytest
from app.kb_batch59_math_guards import check, FIELDS, ConditionsNotEstablished

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch59_selective_source_review as G

AUDIT=G.build()
ROWS=AUDIT["rows"]
COMP=AUDIT["competency_requirement_queue"]
VALID={
    "arithmetic_partial_sum":{"first":3,"difference":-2,"n":8},
    "geometric_partial_sum":{"first":-4,"ratio":Fraction(-1,2),"n":6},
    "affine_square_derivative":{"a":2,"b":3,"x":1},
    "space_basis_coordinates":{"basis":((1,0,0),(1,1,0),(0,0,2)),"vector":(5,3,4)},
    "line_slope_relation":{"line1":((0,0),(0,2)),"line2":((2,1),(2,4))},
    "ellipse_focal_parameters":{"a":5,"c":3},
    "binomial_coefficient":{"n":6,"k":3},
    "hypergeometric_probability":{"population":10,"successes":4,"draws":3,"observed":2},
    "bayes_two_hypotheses":{"prior":Fraction(1,4),"likelihood_a":Fraction(1,2),
                            "likelihood_not_a":Fraction(1,6)},
    "pearson_squared":{"xs":(1,2,3),"ys":(2,4,6)},
    "least_squares":{"xs":(1,2,3),"ys":(2,4,6)},
    "two_by_two_chi_square":{"table":((10,20),(20,10)),}
}

def test_seven_tracks_and_nonunique_page_denominator():
    assert AUDIT["source_pages_total"]==61
    assert AUDIT["newly_partially_annotated_pages"]==list(range(37,51))
    assert AUDIT["partially_annotated_pages_combined"]==list(range(15,51))
    assert AUDIT["previous_nonunique_source_spans"]==130
    assert AUDIT["new_nonunique_source_spans"]==108
    assert AUDIT["combined_nonunique_source_spans"]==238
    assert AUDIT["project_editorial_candidates_not_official_atoms"]==313
    assert set(AUDIT["official_atomic_denominator"])==set(G.TRACKS)
    assert all(v is None for v in AUDIT["official_atomic_denominator"].values())
    assert AUDIT["full_teacher_reviewed_page_atomizations"]==0
    assert AUDIT["unverified_historical_proof_steps"]==538
    assert AUDIT["unresolved_math_conflicts"]==10
    assert AUDIT["teacher_approved"]==AUDIT["student_published"]==0

@pytest.mark.parametrize("i",range(108))
def test_each_source_pointer_has_page_sha_and_no_promotion(i):
    r=ROWS[i]
    snap=G.load(G.SNAP)
    assert r["source_pdf_sha256"]==G.PDF_SHA
    assert r["source_span_pdfkit_sha256"]==snap["attestations"][r["source_span_id"]]
    assert r["pdf_page_index"]==r["printed_page"]+7
    assert r["teacher_review"]=="REVIEW_PENDING"
    assert r["full_page_human_review"]=="PENDING"
    assert r["cross_page_mathematical_deduplication"]=="PENDING"
    assert not r["official_atom_certified"] and not r["mathematical_scope_equivalence_certified"]
    assert not r["formal_general_proof_certified"] and not r["student_publishable"]
    assert 20<=len(r["original_editorial_paraphrase"])<=G.MAX_CLAUSE
    assert not r["starred_optional"] or r["exam_requirement_status"]=="EXPLICITLY_OPTIONAL_NOT_EXAM"
    assert r["track"]=="SELECTIVE_COMPULSORY"

@pytest.mark.parametrize("i",range(42))
def test_each_noncontent_requirement_remains_in_independent_unmapped_queue(i):
    item=COMP[i]
    matching=[r for r in ROWS if r["candidate_id"]==item["candidate_id"]]
    assert len(matching)==1
    assert matching[0]["source_kind"] in ("ACHIEVEMENT_REQUIREMENT","TEACHING_GUIDANCE","ACTIVITY_REQUIREMENT")
    assert item["source_span_id"]==matching[0]["source_span_id"]
    assert matching[0]["requirement_coverage_status"]=="UNMAPPED"
    assert item["coverage"]=="UNMAPPED" and item["not_a_certified_content_atom"]
    assert item["linked_approved_assessment_ids"]==[]
    assert item["teacher_review"]=="REVIEW_PENDING"

@pytest.mark.parametrize("p",range(37,51))
def test_each_new_page_has_source_leads_but_not_completeness(p):
    selected=[r for r in ROWS if r["printed_page"]==p]
    assert selected and len(selected)==AUDIT["counts_per_page"][str(p)]
    assert len({r["source_span_id"] for r in selected})==len(selected)
    assert all(r["full_page_human_review"]=="PENDING" for r in selected)

def test_starred_scope_has_five_distinct_positions_and_correct_types():
    optional=[r for r in ROWS if r["starred_optional"]]
    assert len(optional)==5
    assert set(r["printed_page"] for r in optional)=={38,40,44,47}
    assert all(r["source_kind"]=="OPTIONAL_STARRED" for r in optional)
    assert all(r["exam_requirement_status"]=="EXPLICITLY_OPTIONAL_NOT_EXAM" for r in optional)

def test_elective_boundary_does_not_promote_track_content():
    boundary=[r for r in ROWS if r["source_kind"]=="TRACK_BOUNDARY"]
    assert len(boundary)==1
    assert boundary[0]["printed_page"]==50
    assert boundary[0]["exam_requirement_status"]=="TRACK_BOUNDARY_NOT_AN_ATOM"
    assert not boundary[0]["official_atom_certified"]
    assert not AUDIT["source_passages_or_pdf_committed"]

def test_regeneration_and_md_are_stable():
    assert G.OUTPUT.read_text(encoding="utf8")==json.dumps(AUDIT,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    assert G.REPORT.read_text(encoding="utf8")==G.render(AUDIT)
    assert "七轨" in G.render(AUDIT)

def test_duplicate_or_missing_sources_rejected():
    seeds=G.read_seeds()
    seeds[1]["line_start"]=seeds[0]["line_start"]
    seeds[1]["line_end"]=seeds[0]["line_end"]
    seeds[1]["printed_page"]=seeds[0]["printed_page"]
    with pytest.raises(ValueError,match="duplicate source span"):G.build(seeds=seeds)
    with pytest.raises(ValueError,match="inventory"):G.build(seeds=G.read_seeds()[:-1])

def test_star_injection_and_wrong_optional_location_rejected():
    seeds=G.read_seeds()
    seeds[0]["source_kind"]="OPTIONAL_STARRED"
    seeds[0]["optional_starred_flag"]="Y"
    with pytest.raises(ValueError,match="outside confirmed"):G.build(seeds=seeds)
    seeds=G.read_seeds()
    starred=next(r for r in seeds if r["source_kind"]=="OPTIONAL_STARRED")
    starred["optional_starred_flag"]="N"
    with pytest.raises(ValueError,match="starred optional mismatch"):G.build(seeds=seeds)

def test_elective_boundary_cannot_be_moved():
    seeds=G.read_seeds()
    boundary=next(r for r in seeds if r["source_kind"]=="TRACK_BOUNDARY")
    boundary["line_start"]=19
    with pytest.raises(ValueError,match="boundary cannot be moved"):G.build(seeds=seeds)

def test_forged_teacher_approval_denominator_risk_and_pdf_snapshot_rejected():
    previous=G.load(G.OLD)
    previous["official_atomic_denominator"]["SELECTIVE_COMPULSORY"]=108
    with pytest.raises(ValueError,match="scope or approval"):G.build(old=previous)
    overlay=G.load(G.OVERLAY)
    overlay["rows"][0]["teacher_approved"]=True
    with pytest.raises(ValueError,match="false teacher approval"):G.build(overlay=overlay)
    risk=G.load(G.RISK);risk["conflicts_resolved"]=1
    with pytest.raises(ValueError,match="risk baseline"):G.build(risk=risk)
    snap=G.load(G.SNAP);snap["any_full_page_human_review_certified"]=True
    with pytest.raises(ValueError,match="provenance forged"):G.build(snapshot=snap)
    snap=G.load(G.SNAP);snap["attestations"].pop(next(iter(snap["attestations"])))
    with pytest.raises(ValueError,match="inventory"):G.build(snapshot=snap)

def test_missing_and_corrupted_pdf_rejected_on_mac(tmp_path):
    bad_pdf=tmp_path/"fake.pdf";bad_pdf.write_bytes(b"not a standard")
    with pytest.raises(ValueError,match="missing or changed SHA"):
        G.source_attest(tmp_path,bad_pdf,G.read_seeds(),G.load(G.PAGE))

@pytest.mark.parametrize("op",sorted(FIELDS))
def test_exact_guard_honors_finite_only_and_rejects_approval_injection(op):
    result=check(op,**VALID[op])
    assert result["status"]=="FINITE_EXACT_CASE_ONLY"
    assert result["scope"]=="NOT_FORMAL_GENERAL_PROOF"
    assert result["official_atom_certified"] is False
    assert result["teacher_approved"] is False
    assert result["student_solution_verified"] is False
    with pytest.raises(ConditionsNotEstablished):
        check(op,**VALID[op],teacher_approved=True)

@pytest.mark.parametrize("op",sorted(FIELDS))
def test_exact_guard_rejects_missing_required_input(op):
    missing=next(iter(VALID[op]))
    with pytest.raises(ConditionsNotEstablished):
        check(op,**{k:v for k,v in VALID[op].items() if k!=missing})

@pytest.mark.parametrize("op",sorted(FIELDS))
def test_exact_guard_does_not_accept_float_or_unknown_inputs(op):
    original=VALID[op]
    for key,val in original.items():
        if type(val) in (int,Fraction):
            mutated=dict(original,**{key:0.5})
            with pytest.raises(ConditionsNotEstablished):
                check(op,**mutated)
            break
    else:
        with pytest.raises(ConditionsNotEstablished):
            check(op,**dict(original,unexpected="free-form-LLM-says-true"))

def test_arithmetic_and_geometric_negative_ratio_plus_q_one():
    assert check("arithmetic_partial_sum",first=1,difference=2,n=5)["values"]["sum"]==25
    assert check("geometric_partial_sum",first=3,ratio=1,n=4)["values"]=={"sum":12,"branch":"RATIO_ONE"}
    assert check("geometric_partial_sum",first=2,ratio=0,n=4)["values"]["sum"]==2
    with pytest.raises(ConditionsNotEstablished):check("arithmetic_partial_sum",first=1,difference=2,n=0)
    with pytest.raises(ConditionsNotEstablished):check("geometric_partial_sum",first=1,ratio=2,n=1001)

def test_chain_rule_no_missing_inner_and_polynomial_reference():
    import sympy as s
    x=s.Symbol("x")
    for a,b,at in [(2,3,1),(-3,7,-2),(0,4,5)]:
        res=check("affine_square_derivative",a=a,b=b,x=at)
        assert res["values"]["derivative_at_x"]==s.diff((a*x+b)**2,x).subs(x,at)
    assert check("affine_square_derivative",a=2,b=3,x=1)["values"]["derivative_at_x"]==20

def test_spatial_linear_independence_and_degenerate_basis():
    values=check("space_basis_coordinates",**VALID["space_basis_coordinates"])["values"]
    assert values["coordinates"]==(2,3,2)
    with pytest.raises(ConditionsNotEstablished,match="dependent"):
        check("space_basis_coordinates",basis=((1,0,0),(2,0,0),(0,0,1)),vector=(1,2,3))

def test_line_vertical_slope_and_coincident_point_boundary():
    res=check("line_slope_relation",**VALID["line_slope_relation"])["values"]
    assert res["parallel_directions"] and res["slope1"] is None
    with pytest.raises(ConditionsNotEstablished):
        check("line_slope_relation",line1=((0,0),(0,0)),line2=((0,1),(1,1)))

def test_ellipse_circle_special_case_and_focal_inequality():
    assert check("ellipse_focal_parameters",a=5,c=3)["values"]["b_squared"]==16
    assert check("ellipse_focal_parameters",a=4,c=0)["values"]["special_case"]=="CIRCLE"
    for params in [(3,3),(3,4),(0,0)]:
        with pytest.raises(ConditionsNotEstablished):
            check("ellipse_focal_parameters",a=params[0],c=params[1])

def test_binomial_and_hypergeometric_ranges_and_sanity():
    assert check("binomial_coefficient",n=6,k=3)["values"]["coefficient"]==20
    p=check("hypergeometric_probability",**VALID["hypergeometric_probability"])["values"]["probability"]
    assert p==Fraction(3,10)
    with pytest.raises(ConditionsNotEstablished):
        check("binomial_coefficient",n=4,k=5)
    with pytest.raises(ConditionsNotEstablished):
        check("hypergeometric_probability",population=5,successes=2,draws=5,observed=1)

def test_bayes_positive_evidence_and_optional_status():
    val=check("bayes_two_hypotheses",**VALID["bayes_two_hypotheses"])["values"]
    assert val["posterior"]==Fraction(1,2)
    assert val["curriculum_scope"]=="EXPLICIT_STARRED_OPTIONAL"
    with pytest.raises(ConditionsNotEstablished):
        check("bayes_two_hypotheses",prior=1,likelihood_a=0,likelihood_not_a=0)

def test_pearson_zero_variance_and_causality_boundary():
    assert check("pearson_squared",**VALID["pearson_squared"])["values"]["r_squared"]==1
    assert check("pearson_squared",xs=(1,2,3),ys=(3,2,1))["values"]["r_sign"]==-1
    with pytest.raises(ConditionsNotEstablished):
        check("pearson_squared",xs=(1,1,1),ys=(2,3,4))

def test_ols_extrapolation_not_certified():
    res=check("least_squares",**VALID["least_squares"])["values"]
    assert res["slope"]==2 and res["intercept"]==0
    assert "extrapolation" in res["warning"]
    with pytest.raises(ConditionsNotEstablished):
        check("least_squares",xs=(1,1,1),ys=(2,3,4))

def test_chi_square_exact_and_expected_positive():
    r=check("two_by_two_chi_square",table=((10,20),(20,10)))["values"]
    assert r["chi_square"]==Fraction(20,3)
    assert all(x>0 for row in r["expected"] for x in row)
    with pytest.raises(ConditionsNotEstablished):
        check("two_by_two_chi_square",table=((0,0),(1,2)))

def test_unknown_operator_and_false_free_text_proof_rejected():
    with pytest.raises(ConditionsNotEstablished,match="unsupported"):
        check("model_claims_student_correct",student_text="Because LLM says so")
