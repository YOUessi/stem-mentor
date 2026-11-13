"""Batch56 source spans / teacher gates / bounded exact math regression."""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path

import pytest
from app.kb_batch56_scope_witnesses import exact_witness,ConditionsNotEstablished,FIELDS

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("kb56_source",ROOT/"scripts/build_kb_batch56_source_span_review.py")
G=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)
AUDIT=G.build()
ROWS=AUDIT["rows"]

def test_provenance_and_unverified_denominators():
    assert len(ROWS)==52 and AUDIT["source_pages_total"]==61
    assert AUDIT["source_pages_partially_annotated"]==list(range(15,25))
    assert AUDIT["starred_not_exam_requirements"]==2
    assert AUDIT["full_human_teacher_page_atomizations_completed"]==0
    assert AUDIT["teacher_approved"]==AUDIT["student_published"]==0
    assert AUDIT["historical_proof_steps_still_unverified"]==538
    assert AUDIT["mathematical_conflicts_still_open"]==10
    assert all(val is None for val in AUDIT["official_atomic_denominator"].values())
    assert all(r["official_atom_certified"] is False and r["student_publishable"] is False
               and r["formal_math_proof_certified"] is False and r["teacher_review"]=="REVIEW_PENDING"
               for r in ROWS)

@pytest.mark.parametrize("i",range(52))
def test_each_source_span_has_frozen_pdfkit_hash_and_no_forged_authority(i):
    r=ROWS[i];snap=G.load(G.SNAP)
    assert r["source_span_pdfkit_sha256"]==snap["attestations"][r["source_span_id"]]
    assert len(r["source_span_pdfkit_sha256"])==64
    assert r["source_page_pdfkit_sha256"]==next(p["pdfkit_text_sha256"]
        for p in G.load(G.PAGE)["pages"] if p["printed_page"]==r["printed_page"])
    assert r["source_scope_review"]=="EDITORIAL_PDFKIT_SPAN_TRIAGE_NOT_TEACHER_CERTIFIED"
    assert r["cross_page_deduplication"]=="PENDING"
    assert not r["related_lesson_math_equivalence_certified"]
    assert r["exam_requirement_status"]==("EXPLICITLY_NOT_EXAM_REQUIREMENT"
        if r["starred_optional"] else "NOT_DETERMINED_BY_THIS_AUDIT")

@pytest.mark.parametrize("page,count",sorted(G.EXPECT.items()))
def test_page_counts_exact_and_distinct(page,count):
    subset=[r for r in ROWS if r["printed_page"]==page]
    assert len(subset)==count and len({r["source_span_id"] for r in subset})==count

@pytest.mark.parametrize("page", [20,21])
def test_starred_optional_is_explicitly_excluded_from_exam_requirement(page):
    optional=[r for r in ROWS if r["printed_page"]==page and r["starred_optional"]]
    assert len(optional)==1
    assert optional[0]["source_kind"]=="OPTIONAL_STARRED"
    assert optional[0]["exam_requirement_status"]=="EXPLICITLY_NOT_EXAM_REQUIREMENT"

@pytest.mark.parametrize("page", [18,24])
def test_achievement_standards_cannot_be_counted_as_new_content_atoms(page):
    assert any(r["source_kind"]=="ACHIEVEMENT_REQUIREMENT" for r in ROWS if r["printed_page"]==page)
    assert all(not r["official_atom_certified"] for r in ROWS if r["printed_page"]==page)

def test_tsv_duplicate_rejected():
    copy=G.read_seeds();copy[1]["line_start"]=copy[0]["line_start"]
    copy[1]["line_end"]=copy[0]["line_end"]
    with pytest.raises(ValueError,match="duplicate source span"):G.build(seeds=copy)

def test_tsv_partial_or_invalid_page_rejected():
    with pytest.raises(ValueError):G.build(seeds=G.read_seeds()[:-1])
    copy=G.read_seeds();copy[0]["printed_page"]=75
    with pytest.raises(ValueError):G.build(seeds=copy)

def test_starred_flag_must_agree_with_source_kind():
    copy=G.read_seeds()
    r=next(z for z in copy if z["source_kind"]=="OPTIONAL_STARRED")
    r["starred_optional"]=False;r["_raw_starred"]="N"
    with pytest.raises(ValueError,match="optional-star"):G.build(seeds=copy)

def test_source_sha_and_span_hash_drift_rejected():
    p=G.load(G.PAGE);p["official_pdf_sha256"]="0"*64
    with pytest.raises(ValueError,match="source SHA"):G.build(pages=p)
    a=G.load(G.SNAP);a["attestations"].pop(next(iter(a["attestations"])))
    with pytest.raises(ValueError):G.build(attestation=a)

def test_legacy_313_and_all_promotion_attempts_rejected():
    overlay=G.load(G.OVERLAY)
    overlay["rows"][0]["teacher_approved"]=True
    with pytest.raises(ValueError,match="falsely approved"):G.build(overlay=overlay)
    b54=G.load(G.B54); b54["official_atomic_denominator"]["COMPULSORY"]=52
    with pytest.raises(ValueError,match="falsely certified"):G.build(base54=b54)
    b55=G.load(G.B55); b55["frozen_unverified_proof_steps"]=0
    with pytest.raises(ValueError,match="risk inventory drift"):G.build(base55=b55)

def test_local_pdf_cannot_be_faked_by_any_arbitrary_path(tmp_path):
    fake=tmp_path/"fake.pdf";fake.write_bytes(b"%PDF-1.0\nnot the official source")
    with pytest.raises(ValueError,match="PDF absent or SHA mismatch"):
        G.attest_source(source_dir=tmp_path,pdf_path=fake,rows=G.read_seeds(),pages=G.load(G.PAGE))

def test_regeneration_json_and_markdown_exact():
    assert G.OUTPUT.read_text(encoding="utf8")==json.dumps(AUDIT,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    assert G.REPORT.read_text(encoding="utf8")==G.report(AUDIT)
    assert "官方七轨" in G.report(AUDIT)

@pytest.mark.parametrize("idx",[0,7,18,26,31,34,37,42,45,48,51])
def test_student_rag_and_tutor_block_unapproved_source_spans(idx):
    from app.deep_retrieval import student_evidence_lookup
    from app.model_tutor_draft import draft_next_question
    query=ROWS[idx]["candidate_id"]
    res=student_evidence_lookup(query,limit=3)
    assert res["status"]=="NO_APPROVED_EVIDENCE"
    assert res["candidates"]==[] and res["teacher_solution_exposed"] is False
    draft=draft_next_question(query,mode="GUIDE",help_requested=True,
        consent_to_cloud=True,operator_scope="EDITOR_LOCAL",
        provider_url="https://api.openai.com/v1/chat/completions",
        provider_model="offline-test-do-not-call")
    assert draft.status=="BLOCKED" and draft.reason=="NO_APPROVED_MATH_EVIDENCE"
    assert not draft.model_called and not draft.student_visible

@pytest.mark.parametrize("op,valid",[
    ("finite_set_complement",{"universe":[1,2,3],"subset":[1,3]}),
    ("finite_quantifier_negation",{"truth_values":[True,False]}),
    ("agm_square",{"a":1,"b":4}),
    ("quadratic_discriminant",{"a":1,"b":-2,"c":1}),
    ("exponent_integer_order",{"base":2,"m":1,"n":3}),
    ("rational_unit_circle_tan",{"sin":Fraction(3,5),"cos":Fraction(4,5)}),
    ("polynomial_bisection",{"coefficients":[-2,0,1],"left":1,"right":2}),
    ("log_exponential_inverse",{"base":3,"integer_exponent":-2}),
])
def test_each_bounded_witness_has_no_formal_claim_and_rejects_fake_approval(op,valid):
    r=exact_witness(op,**valid)
    assert r["status"]=="FINITE_EXACT_CASE_ONLY"
    assert not r["teacher_approved"] and not r["student_solution_verified"]
    assert not r["source_clause_certified"]
    assert r["scope"]=="NOT_FORMAL_GENERAL_PROOF"
    with pytest.raises(ConditionsNotEstablished):exact_witness(op,**(valid|{"teacher_approved":True}))
    for arg in FIELDS[op]:
        with pytest.raises(ConditionsNotEstablished):exact_witness(op,**{k:v for k,v in valid.items() if k!=arg})

@pytest.mark.parametrize("bad",[
    {"universe":[1,2],"subset":[3]}, {"universe":[1,2,2],"subset":[]},
    {"universe":[1,True],"subset":[1]},
])
def test_universe_and_type_guards(bad):
    with pytest.raises(ConditionsNotEstablished):exact_witness("finite_set_complement",**bad)

@pytest.mark.parametrize("values",[[],[1,False],[0,1],[True]*13])
def test_invalid_finite_quantifier_domain(values):
    with pytest.raises(ConditionsNotEstablished):exact_witness("finite_quantifier_negation",truth_values=values)

@pytest.mark.parametrize("a,b",[(-1,1),(True,2),(0.1,1),(1,-1)])
def test_nonnegative_agm_guards(a,b):
    with pytest.raises(ConditionsNotEstablished):exact_witness("agm_square",a=a,b=b)

def test_agm_squared_gap_and_equality():
    for a in range(5):
        for b in range(5):
            r=exact_witness("agm_square",a=a,b=b)["result"]
            assert r["square_gap"]==(a-b)**2 and r["inequality_holds"] and (r["equality"]==(a==b))

def test_bisection_requires_strict_sign_change_and_does_not_claim_uniqueness():
    q=exact_witness("polynomial_bisection",coefficients=[-2,0,1],left=1,right=2)["result"]
    assert q["interval_width"]==Fraction(1,2) and q["uniqueness"]=="UNDETERMINED"
    for co,a,b in [([-1,0,1],-2,2),([1],0,1),([0],0,1),([-1,0,1],1,1)]:
        with pytest.raises(ConditionsNotEstablished):
            exact_witness("polynomial_bisection",coefficients=co,left=a,right=b)

def test_quadratic_disc_real_roots_and_degeneracy():
    for a,b,c,expected in [(1,0,1,0),(1,2,1,1),(1,0,-1,2)]:
        assert exact_witness("quadratic_discriminant",a=a,b=b,c=c)["result"]["real_root_count"]==expected
    with pytest.raises(ConditionsNotEstablished):
        exact_witness("quadratic_discriminant",a=0,b=2,c=3)

def test_exponent_base_and_integer_order():
    for base in [Fraction(1,2),Fraction(3,2),2]:
        for m in [-3,0,2]:
            for n in [-2,0,3]:
                r=exact_witness("exponent_integer_order",base=base,m=m,n=n)["result"]
                assert r["ordered_correctly"]
    for base in [-1,0,1,True,1.1]:
        with pytest.raises(ConditionsNotEstablished):
            exact_witness("exponent_integer_order",base=base,m=0,n=1)

def test_trig_cosine_zero_domain_and_unit_circle():
    with pytest.raises(ConditionsNotEstablished):
        exact_witness("rational_unit_circle_tan",sin=1,cos=0)
    with pytest.raises(ConditionsNotEstablished):
        exact_witness("rational_unit_circle_tan",sin=1,cos=1)
    r=exact_witness("rational_unit_circle_tan",sin=Fraction(3,5),cos=Fraction(4,5))["result"]
    assert r["tan"]==Fraction(3,4) and not r["angle_certified"]

def test_logarithm_base_domain_and_finite_integer_scope():
    for base in [-1,0,1,Fraction(1,1)]:
        with pytest.raises(ConditionsNotEstablished):
            exact_witness("log_exponential_inverse",base=base,integer_exponent=2)
    r=exact_witness("log_exponential_inverse",base=Fraction(3,2),integer_exponent=-2)["result"]
    assert r["positive_argument"]==Fraction(4,9) and not r["arbitrary_real_logarithm_computed"]

@pytest.mark.parametrize("op",list(FIELDS))
def test_unknown_arbitrary_free_form_proofs_never_accepted(op):
    with pytest.raises(ConditionsNotEstablished):
        exact_witness(op,student_free_text="obviously true")
