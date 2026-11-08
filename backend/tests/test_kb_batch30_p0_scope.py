"""Batch30 K00/K07 review regression: source anchors, negative authority and exact algebra.

Tests assert bounded rational identity, domain rejection and review visibility;
they do not assert that an entire source theorem is formally proved.
"""
from __future__ import annotations
import copy
import json
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path

import pytest
import sympy as sp
from app.kb_batch30_exact_witnesses import SUPPORTED,evaluate

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch30_p0_audit as p0
import build_kb_batch30_k00_page52 as k00

EDITORIAL=json.loads(p0.EDITORIAL.read_text(encoding="utf8"))
FIX=json.loads(p0.FIXTURES.read_text(encoding="utf8"))
AUDIT=json.loads(p0.REPORT.read_text(encoding="utf8"))
PAGE=json.loads(k00.OUT.read_text(encoding="utf8"))
FIX_BY_OP={x["operation"]:x for x in FIX["fixtures"]}

def verified(op,data):
    r=evaluate(op,data)
    assert r["status"]=="VERIFIED_FINITE_INSTANCE",r
    assert all(r[x] is False for x in ("student_step_verified","complete_theorem_certified",
                                     "teacher_approved","official_curriculum_atom_verified"))
    return r["witness"]

def refusal(op,data):
    r=evaluate(op,data)
    assert r["status"]=="CONDITIONS_NOT_ESTABLISHED",r
    assert all(r[x] is False for x in ("student_step_verified","complete_theorem_certified",
                                     "teacher_approved","official_curriculum_atom_verified"))

def test_final_44_original_steps_complete_editorial_partition_not_formal_proof():
    assert json.loads(p0.build())==AUDIT
    s=AUDIT["summary"]
    assert (s["previous_batch28_editorial"],s["previous_batch29_editorial"],s["batch30_new_editorial"])==(35,48,44)
    assert (s["total_with_explicit_editorial_math_condition_reviews"],s["still_without_editorial_condition_review"])==(127,0)
    assert (s["formally_verified_historical_steps"],s["authentic_teacher_approvals"],s["student_published_deep_lessons"])==(0,0,0)
    assert s["formally_unverified_proof_steps_total"]==538
    assert len(AUDIT["batch30_new_editorial_rows"])==44
    assert len(AUDIT["prior_editorial_ids"])==83
    assert set(AUDIT["prior_editorial_ids"]).isdisjoint({x["risk_step_id"] for x in AUDIT["batch30_new_editorial_rows"]})
    assert all(s["official_"+t+"_knowledge_atom_denominator"] is None for t in ("compulsory","selective","elective"))

@pytest.mark.parametrize("note",EDITORIAL["entries"],ids=lambda x:x["risk_step_id"])
def test_case_specific_editorial_notes_not_authorized_to_student(note):
    assert len(note["necessary_hypotheses"])>=50
    assert len(note["explanatory_counterexample"])>=30
    assert len(note["next_review_action"])>=15
    assert note["math_status"]=="EDITORIAL_CONDITIONS_WITH_EXPLICIT_COUNTEREXAMPLE_NOT_CERTIFIED"
    assert note["student_publishable"] is False
    assert note["teacher_review"]==note["human_math_review"]=="PENDING"

@pytest.mark.parametrize("op",sorted(SUPPORTED))
def test_twenty_original_finite_witnesses_have_independent_refusal_cases(op):
    x=FIX_BY_OP[op]
    valid=evaluate(op,x["valid_exact_fixture"])
    invalid=evaluate(op,x["invalid_fixture"])
    assert valid["status"]=="VERIFIED_FINITE_INSTANCE"
    assert invalid["status"]=="CONDITIONS_NOT_ESTABLISHED"
    for r in (valid,invalid):
        assert all(r[t] is False for t in ("student_step_verified","complete_theorem_certified",
                                          "teacher_approved","official_curriculum_atom_verified"))

@pytest.mark.parametrize("mutation",["approve_root","change_status","student_expose","remove","duplicate","fake_id","trivial_conditions","fake_teacher"])
def test_editorial_claims_and_authority_cannot_be_forged(mutation):
    m=copy.deepcopy(EDITORIAL)
    if mutation=="approve_root":m["review_state"]="APPROVED"
    if mutation=="change_status":m["entries"][0]["math_status"]="VERIFIED"
    if mutation=="student_expose":m["student_visibility"]="PUBLIC"
    if mutation=="remove":m["entries"].pop()
    if mutation=="duplicate":m["entries"][0]["risk_step_id"]=m["entries"][1]["risk_step_id"]
    if mutation=="fake_id":m["entries"][0]["risk_step_id"]="fake-proof-id"
    if mutation=="trivial_conditions":m["entries"][0]["necessary_hypotheses"]="True"
    if mutation=="fake_teacher":m["entries"][0]["teacher_review"]="APPROVED"
    with pytest.raises(ValueError):p0.build(editorial=m)

@pytest.mark.parametrize("mutation",["review","unsupported","duplicate","positive_bad","negative_bad"])
def test_oracle_fixtures_and_authority_negative_cases(mutation):
    m=copy.deepcopy(FIX)
    if mutation=="review":m["fixtures"][0]["teacher_review"]="APPROVED"
    if mutation=="unsupported":m["fixtures"][0]["operation"]="arbitrary_student_solution"
    if mutation=="duplicate":m["fixtures"][0]["operation"]=m["fixtures"][1]["operation"]
    if mutation=="positive_bad":m["fixtures"][0]["valid_exact_fixture"]={"sizes":[2,0]}
    if mutation=="negative_bad":m["fixtures"][0]["invalid_fixture"]={"sizes":[2,2]}
    with pytest.raises(ValueError):p0.build(fixtures=m)

def test_original_p0_sha_forgery_rejected():
    h=p0.load(p0.HISTORY)
    id_=EDITORIAL["entries"][0]["risk_step_id"]
    for item in h["p0_review_queue"]:
        if item["id"]==id_:item["verified_original_step_sha256"]="a"*64
    with pytest.raises(ValueError):p0.build(history=h)

def test_previous_batches_cannot_be_silently_edited():
    p=p0.load(p0.B29)
    p["remaining_unreviewed_step_ids"].pop()
    with pytest.raises(ValueError):p0.build(prior29=p)

def test_page52_real_original_render_resolves_only_marker_occurrences():
    assert json.loads(k00.build())==PAGE
    a=PAGE["marker_audit"];g=PAGE["global_scope"]
    assert (a["historical_page52_count"],a["rendered_original_page52_count"],a["reextracted_page52_count"])==(6,8,8)
    assert [x["marker"] for x in a["two_historically_omitted_numbered_markers"]]==["（２）","（４）"]
    assert (g["source_pages"],g["assistant_visually_rechecked_pages"],g["remaining_without_assistant_visual_recheck"])==(61,1,60)
    assert g["teacher_visually_rechecked_pages"]==0
    assert a["numbered_markers_are_atomic_knowledge_units"] is False
    assert all(v is None for v in g["verified_official_atom_denominators"].values())
    assert g["official_knowledge_atom_coverage_rate"] is None

@pytest.mark.parametrize("mutation",["old_pdf","new_pdf","old_marker","new_marker","old_pages","new_track"])
def test_source_page52_tampering_and_missing_content_rejected(mutation):
    a=k00.load(k00.ORIGINAL);b=k00.load(k00.REEXTRACT)
    if mutation=="old_pdf":a["source"]["sha256"]="a"*64
    elif mutation=="new_pdf":b["source"]["sha256"]="b"*64
    elif mutation=="old_marker":next(x for x in a["enumerated_source_anchors"] if x["printed_page"]==52)["marker"]="（９）"
    elif mutation=="new_marker":next(x for x in b["enumerated_source_anchors"] if x["printed_page"]==52)["marker"]="（９）"
    elif mutation=="old_pages":a["pages"].pop()
    elif mutation=="new_track":next(x for x in b["enumerated_source_anchors"] if x["printed_page"]==52)["track"]="ELECTIVE_B"
    with pytest.raises(ValueError):k00.build(old=a,new=b)

@pytest.mark.parametrize("a,h",[(a,h) for a,h in product(range(-4,5),(-3,-2,-1,1,2,3))])
def test_square_difference_quotient_sympy(a,h):
    w=verified("square_difference_quotient",dict(a=a,h=h))
    x=sp.symbols("x")
    assert sp.Rational(w["quotient"])==sp.Rational(w["simplified"])==2*a+h
    assert sp.Rational(w["limiting_derivative"])==sp.diff(x*x,x).subs(x,a)
    refusal("square_difference_quotient",dict(a=a,h=0))

@pytest.mark.parametrize("a,b",[(a,b) for a,b in product(range(-4,5),repeat=2) if a<b])
def test_mvt_quadratic_exact(a,b):
    w=verified("mvt_quadratic",dict(a=a,b=b))
    assert sp.Rational(w["derivative_at_c"])==sp.Rational(w["secant"])==a+b
    c=sp.Rational(w["c"])
    assert a<c<b

@pytest.mark.parametrize("k,x,z,y",[(k,x,z,y) for k in range(3) for x,z,y in product(range(-2,4),repeat=3) if x<z<y])
def test_convex_chord_exact(k,x,z,y):
    w=verified("convex_chord_quadratic",dict(k=k,b=1,c=4,x=x,z=z,y=y))
    assert sp.Rational(w["chord_minus_fz"])==k*(z-x)*(y-z)
    assert w["nonnegative"] is True

@pytest.mark.parametrize("rate,n",[(rate,n) for rate,n in product(("1/10","1/2","2","-1/2"),range(1,12))])
def test_annuity_exact_geometric_series(rate,n):
    w=verified("annuity_nonzero_rate",dict(n=n,rate=rate))
    q=sp.Rational(w["q"])
    assert sp.Rational(w["sum_of_discounts"])==sp.Rational(w["closed"])==sum((q**i for i in range(1,n+1)),sp.Rational(0))
    refusal("annuity_nonzero_rate",dict(n=n,rate=0))

@pytest.mark.parametrize("a,epsilon,h",[(a,e,h) for a,e,h in product(range(-3,4),("1/2","1","3"),("1/100","-1/100"))])
def test_epsilon_delta_square_strict_for_legal_neighborhood(a,epsilon,h):
    r=evaluate("epsilon_delta_square",dict(a=a,epsilon=epsilon,h=h))
    assert r["status"]=="VERIFIED_FINITE_INSTANCE"
    w=r["witness"]
    assert F(w["actual_error"])<F(w["target_epsilon"])
    assert F(w["derived_upper_bound"])<F(w["target_epsilon"])

@pytest.mark.parametrize("n,k",[(n,k) for n in range(1,20) for k in range(n+1)])
def test_bernoulli_mle_finite_grid_comparison_and_boundary(n,k):
    grid=["0","1/10","1/4","1/2","3/4","9/10","1"]
    w=verified("bernoulli_mle",dict(n=n,k=k,grid=grid))
    assert F(w["mle"])==F(k,n)
    assert all(F(w["likelihood"])>=F(q) for q in w["competitor_likelihoods"])
    assert w["unique_global_optimum_not_certified"] is True

@pytest.mark.parametrize("slope,intercept",list(product(range(-4,5),range(-3,4))))
def test_ols_normal_equations_from_an_independent_line(slope,intercept):
    x=[-2,-1,0,1,2]
    y=[intercept+slope*z for z in x]
    w=verified("ols_two_parameter",dict(x=x,y=y))
    assert F(w["slope"])==slope and F(w["intercept"])==intercept
    assert all(F(w[k])==0 for k in ("residual_sum","residual_x_sum","sse"))
    refusal("ols_two_parameter",dict(x=[1,1,1],y=[1,2,3]))

@pytest.mark.parametrize("x,y,h",[(x,y,h) for x,y,h in product(range(-3,4),range(-2,3),("1/2","-1/3"))])
def test_partial_y_difference_quotient_exact(x,y,h):
    w=verified("partial_y_polynomial",dict(x=x,y=y,h=h))
    assert F(w["difference_quotient"])==F(w["simplified"])
    assert F(w["partial_at_y"])==x*x+6*y

@pytest.mark.parametrize("B,h",list(product(range(0,15),range(1,12))))
def test_cone_volume_and_prism_ratio_exact(B,h):
    w=verified("solid_cone_prism_volume",dict(B=B,h=h))
    assert F(w["prism"])==B*h and F(w["cone"])==F(B*h,3)

@pytest.mark.parametrize("a,b,c",[(a,b,c) for a,b,c in product(range(1,9),repeat=3) if a+b>c and a+c>b and b+c>a])
def test_law_of_cosines_legal_triangle_and_heron(a,b,c):
    w=verified("triangle_cosine",dict(a=a,b=b,c=c))
    assert F(w["cosA"])==F(b*b+c*c-a*a,2*b*c)
    assert F(w["sixteen_area_squared"])==(a+b+c)*(-a+b+c)*(a-b+c)*(a+b-c)
    assert -1<F(w["cosA"])<1

@pytest.mark.parametrize("u,v",list(product(product((-1,0,1),repeat=3),repeat=2)))
def test_lagrange_cross_product_identity_against_sympy(u,v):
    w=verified("cross_lagrange_3",dict(u=list(u),v=list(v)))
    assert F(w["cross_norm2"])==F(w["lagrange_gap"])==sp.Matrix(u).cross(sp.Matrix(v)).dot(sp.Matrix(u).cross(sp.Matrix(v)))
    assert [F(s) for s in w["cross"]]==list(sp.Matrix(u).cross(sp.Matrix(v)))

@pytest.mark.parametrize("c,s,u",[(c,s,u) for c,s in (("3/5","4/5"),("0","1"),("1","0"),("-3/5","4/5")) for u in product(range(-2,3),repeat=2)])
def test_rotation_preserves_euclidean_norm_with_orientation(c,s,u):
    w=verified("rotation_rational",dict(cos=c,sin=s,u=list(u)))
    assert F(w["det"])==1 and F(w["original_norm2"])==F(w["transformed_norm2"])

@pytest.mark.parametrize("n",range(1,250))
def test_induction_square_odd_finite_identity(n):
    w=verified("square_sum_induction",dict(n=n))
    assert w["previous_sum"]==sum((2*i-1 for i in range(1,n+1)))
    assert w["next_sum"]==w["target"]==(n+1)**2

def test_unknown_operator_and_arbitrary_student_payload_never_claim_verified():
    for op in ("student_text","sympy_eval","__import__","all_steps_verified"):
        assert evaluate(op,{"expr":"2+2=4"})["status"]=="UNSUPPORTED"
    for x in (True,3.14,"1e309","__import__('os')","10**100"):
        refusal("square_difference_quotient",dict(a=x,h=1))
