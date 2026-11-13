"""Batch60 partial-source attestation, elective scope, exact math & Tutor isolation tests."""
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import sys
import pytest

from app.kb_batch60_elective_math_guards import check, FIELDS, ConditionsNotEstablished

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch60_elective_source_review as G

AUDIT=G.build()
ROWS=AUDIT["rows"]
CASES={
 "epsilon_n_tail":{"epsilon":Fraction(1,10),"N":11},
 "cramer3":{"matrix":((1,0,0),(0,2,0),(0,0,3)),"rhs":(2,6,12)},
 "vector_cross":{"left":(1,0,0),"right":(0,1,0)},
 "uniform_interval_probability":{"a":0,"b":10,"x":3,"y":8},
 "bernoulli_mle":{"observations":(1,0,1,1)},
 "t_statistic_squared":{"observations":(1,3,5),"mu0":2},
 "two_predictor_ols":{"x1":(0,1,0,1),"x2":(0,0,1,1),"y":(2,5,6,9)},
 "compound_interest":{"principal":100,"rate":Fraction(1,10),"periods":2},
 "cobb_douglas_integer":{"capital":2,"labor":3,"scale":4,"alpha":2,"beta":1},
 "harmonic_mean":{"values":(2,3,6)},
 "logistic_odds":{"odds":3,"threshold":Fraction(1,2)},
 "reflection_squared_distance":{"p":(2,3),"q":(5,-1)},
 "round_robin_match_count":{"teams":8},
 "survey_ht":{"values":(3,6),"inclusion_probabilities":(Fraction(1,2),Fraction(1,4))},
}

def test_no_official_denominator_or_teacher_approval():
    assert AUDIT["source_pages_total"]==61
    assert AUDIT["pages_newly_partially_located"]==[13,14]+list(range(51,74))
    assert AUDIT["pages_partially_located_combined"]==list(range(13,74))
    assert AUDIT["new_nonunique_source_leads"]==106
    assert AUDIT["combined_nonunique_source_leads"]==344
    assert AUDIT["official_full_reviewed_pages"]==0
    assert AUDIT["teacher_approved"]==AUDIT["student_published"]==0
    assert set(AUDIT["official_atomic_denominator"])==set(G.TRACKS)
    assert all(v is None for v in AUDIT["official_atomic_denominator"].values())
    assert AUDIT["local_defined_e_is_not_fixed_national_scope"]
    assert AUDIT["historical_unverified_proof_steps"]==538
    assert AUDIT["unresolved_math_conflicts"]==10

@pytest.mark.parametrize("i",range(106))
def test_source_record_attested_not_certified(i):
    r=ROWS[i];attest=G.load(G.SNAP)["attestations"]
    assert r["source_pdf_sha256"]==G.PDF_SHA
    assert r["source_span_pdfkit_sha256"]==attest[r["source_span_id"]]
    assert r["pdf_page_index"]==r["printed_page"]+7
    assert r["teacher_review"]=="REVIEW_PENDING"
    assert r["full_page_human_review"]=="PENDING"
    assert r["cross_page_mathematical_deduplication"]=="PENDING"
    assert r["source_lead_is_not_atomic_coverage"]
    assert r["same_topic_is_not_mathematical_equivalence"]
    assert not r["official_atom_certified"]
    assert not r["formal_general_proof_certified"]
    assert not r["student_publishable"]
    assert len(r["original_editorial_paraphrase"])>=20
    assert r["track"]==G.track_of(r["printed_page"],G.seeds()[i]["start"],G.seeds()[i]["end"])
    if r["track"].startswith("ELECTIVE"):
        assert r["nationally_compulsory"] is False

@pytest.mark.parametrize("p",[13,14]+list(range(51,74)))
def test_each_new_page_has_explicit_leads_but_no_full_review(p):
    items=[r for r in ROWS if r["printed_page"]==p]
    assert len(items)==AUDIT["counts_per_page"][str(p)]
    assert items and all(r["full_page_human_review"]=="PENDING" for r in items)

def test_five_track_boundaries_and_school_defined_E():
    b=[r for r in ROWS if r["source_kind"]=="TRACK_BOUNDARY"]
    assert {(r["printed_page"],r["track"]) for r in b}=={
        (51,"ELECTIVE_A"),(57,"ELECTIVE_B"),(64,"ELECTIVE_C"),
        (69,"ELECTIVE_D"),(73,"ELECTIVE_E")}
    local=[r for r in ROWS if r["track"]=="ELECTIVE_E"]
    assert all(r["source_kind"] in ("TRACK_BOUNDARY","LOCAL_DEFINED_SCOPE") for r in local)
    assert all(not r["official_atom_certified"] for r in local)

def test_independent_competency_requirements_not_discarded():
    queue=AUDIT["new_noncontent_requirement_queue"]
    assert len(queue)>=4
    for q in queue:
        assert q["status"]=="UNMAPPED"
        assert q["teacher_review"]=="REVIEW_PENDING"
        assert q["linked_approved_assessments"]==[]
        assert sum(r["source_span_id"]==q["source_span_id"] for r in ROWS)==1

def test_output_is_deterministically_rebuildable():
    assert G.OUT.read_text(encoding="utf8")==json.dumps(AUDIT,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    assert G.MD.read_text(encoding="utf8")==G.render(AUDIT)

def test_duplicate_and_incomplete_source_ledger_blocked():
    rows=G.seeds()
    rows[1]["page"]=rows[0]["page"]
    rows[1]["start"]=rows[0]["start"]
    rows[1]["end"]=rows[0]["end"]
    with pytest.raises(ValueError,match="duplicate source span"):G.build(rows=rows)
    with pytest.raises(ValueError,match="source record count"):G.build(rows=G.seeds()[:-1])

def test_elective_boundary_and_school_defined_scope_cannot_be_forged():
    rows=G.seeds()
    rows[0]["track"]="ELECTIVE_A"
    with pytest.raises(ValueError,match="elective track"):G.build(rows=rows)
    rows=G.seeds()
    e=next(r for r in rows if r["track"]=="ELECTIVE_E" and r["kind"]=="LOCAL_DEFINED_SCOPE")
    e["track"]="COMPULSORY"
    with pytest.raises(ValueError,match="elective track"):G.build(rows=rows)
    rows=G.seeds()
    e=next(r for r in rows if r["track"]=="ELECTIVE_E" and r["kind"]=="LOCAL_DEFINED_SCOPE")
    e["kind"]="CONTENT"
    with pytest.raises(ValueError,match="E fixed curriculum"):G.build(rows=rows)

def test_fake_approval_and_source_sha_drift_rejected():
    prev=G.load(G.PREV);prev["teacher_approved"]=1
    with pytest.raises(ValueError,match="prior teacher approval"):G.build(previous=prev)
    prev=G.load(G.PREV);prev["official_atomic_denominator"]["ELECTIVE_A"]=999
    with pytest.raises(ValueError,match="prior teacher approval"):G.build(previous=prev)
    snap=G.load(G.SNAP);snap["full_page_human_review_certified"]=True
    with pytest.raises(ValueError,match="provenance forged"):G.build(snapshot=snap)
    snap=G.load(G.SNAP);snap["attestations"].pop(next(iter(snap["attestations"])))
    with pytest.raises(ValueError,match="source record count"):G.build(snapshot=snap)

def test_corrupt_or_missing_pdf_cannot_be_attested(tmp_path):
    bad=tmp_path/"fake.pdf";bad.write_bytes(b"fabricated syllabus")
    with pytest.raises(ValueError,match="official PDF SHA drift"):G.attest(bad,tmp_path)

@pytest.mark.parametrize("op",sorted(FIELDS))
def test_exact_witness_is_finite_and_cannot_promote_review(op):
    value=check(op,**CASES[op])
    assert value["operation"]==op and value["status"]=="FINITE_EXACT_CASE_ONLY"
    assert value["scope"]=="NOT_FORMAL_GENERAL_PROOF"
    assert value["official_atom_certified"] is False
    assert value["teacher_approved"] is False
    assert value["student_solution_verified"] is False
    with pytest.raises(ConditionsNotEstablished,match="forged approval"):
        check(op,**CASES[op],teacher_approved=True)

@pytest.mark.parametrize("op",sorted(FIELDS))
def test_each_witness_rejects_missing_required_parameters(op):
    key=FIELDS[op][0]
    with pytest.raises(ConditionsNotEstablished):
        check(op,**{k:v for k,v in CASES[op].items() if k!=key})

def test_math_exact_expected_values_and_domains():
    assert check("epsilon_n_tail",**CASES["epsilon_n_tail"])["values"]["tail_bound"]==Fraction(1,11)
    assert check("cramer3",**CASES["cramer3"])["values"]["solution"]==(2,3,4)
    assert check("vector_cross",**CASES["vector_cross"])["values"]["cross"]==(0,0,1)
    assert check("uniform_interval_probability",**CASES["uniform_interval_probability"])["values"]["probability"]==Fraction(1,2)
    assert check("bernoulli_mle",**CASES["bernoulli_mle"])["values"]["estimate"]==Fraction(3,4)
    assert check("two_predictor_ols",**CASES["two_predictor_ols"])["values"]["coefficients"]==(2,3,4)
    assert check("compound_interest",**CASES["compound_interest"])["values"]["future_value"]==121
    assert check("cobb_douglas_integer",**CASES["cobb_douglas_integer"])["values"]["production"]==48
    assert check("harmonic_mean",**CASES["harmonic_mean"])["values"]["harmonic_mean"]==3
    assert check("logistic_odds",**CASES["logistic_odds"])["values"]["probability"]==Fraction(3,4)
    assert check("reflection_squared_distance",**CASES["reflection_squared_distance"])["values"]["squared_distance"]==25
    assert check("round_robin_match_count",**CASES["round_robin_match_count"])["values"]["matches"]==28
    assert check("survey_ht",**CASES["survey_ht"])["values"]["weighted_sample_total"]==30

@pytest.mark.parametrize("op,patch",[
    ("epsilon_n_tail",{"epsilon":Fraction(1,10),"N":10}),
    ("epsilon_n_tail",{"epsilon":0,"N":12}),
    ("cramer3",{"matrix":((1,2,3),(2,4,6),(3,6,9)),"rhs":(1,2,3)}),
    ("uniform_interval_probability",{"a":2,"b":2,"x":2,"y":2}),
    ("bernoulli_mle",{"observations":(True,0,1)}),
    ("t_statistic_squared",{"observations":(3,3,3),"mu0":3}),
    ("two_predictor_ols",{"x1":(1,1,1),"x2":(2,2,2),"y":(1,2,3)}),
    ("compound_interest",{"principal":100,"rate":-1,"periods":2}),
    ("cobb_douglas_integer",{"capital":0,"labor":3,"scale":2,"alpha":2,"beta":1}),
    ("harmonic_mean",{"values":(1,0,3)}),
    ("logistic_odds",{"odds":0,"threshold":Fraction(1,2)}),
    ("round_robin_match_count",{"teams":1}),
    ("survey_ht",{"values":(2,3),"inclusion_probabilities":(Fraction(1,2),0)}),
])
def test_invalid_math_preconditions_rejected(op,patch):
    with pytest.raises(ConditionsNotEstablished):check(op,**patch)

@pytest.mark.parametrize("op",sorted(FIELDS))
def test_exact_math_rejects_unrestricted_floats(op):
    data=deepcopy(CASES[op])
    key=next((k for k,v in data.items() if type(v) in (int,Fraction)),None)
    if key is not None:
        data[key]=1.5
    else:
        key=next(iter(data))
        if isinstance(data[key],(tuple,list)) and data[key]:
            data[key]=(1.5,)+tuple(data[key][1:])
    with pytest.raises(ConditionsNotEstablished):check(op,**data)
