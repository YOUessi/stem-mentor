"""Batch65 exact-case math and 31-source editorial coverage, fail-closed student retrieval."""
from __future__ import annotations
import json
import sys
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path

import pytest
from test_attested_release_batch08 import offline_reviewer_fixture

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch65_substantive_lessons as B
from app import kb_batch65_finite_witnesses as W

NEW=B.load(B.LESSONS)
M,I=B.build()

def test_provisional_scope_manifest_replays_and_is_not_official_denominator():
    assert B.load(B.MATRIX)==M
    assert B.load(B.TEACHER_INDEX)==I
    assert B.REPORT.read_text(encoding="utf-8")==B.render(M,I)
    assert M["parent_substantive_scopes"]==31
    assert M["provisional_atom_hypotheses"]==62
    assert M["prior_teacher_manuscripts"]==14
    assert M["new_teacher_manuscripts"]==17
    assert M["scopes_with_at_least_one_teacher_manuscript"]==31
    assert M["original_examples"]>=62
    assert M["reasoned_steps"]>=93
    assert M["teacher_approved"]==M["student_published"]==M["general_proofs_certified"]==0
    assert M["official_atomic_denominator"]=={x:None for x in B.TRACKS}
    assert M["unmapped_competency_sections"]==14
    assert not I["student_index_write_permitted"]
    assert all(not row["student_retrievable"] and row["access"]=="TEACHER_ONLY" for row in I["rows"])

@pytest.mark.parametrize("i",range(17))
def test_new_manuscript_complete_source_and_teacher_only(i):
    l=NEW[i];r=next(row for row in M["rows"] if row["lesson_id"]==l["lesson_id"])
    assert r["source_anchor_id"]==B.anchor_of(l)
    assert len(r["source_window_sha256"])==64
    assert len(r["candidate_atom_hypotheses"])==2
    assert len(l["examples"])>=2 and len(l["reasoning"])>=3
    assert l["assumptions"] and l["notation"] and l["prerequisites"]
    assert l["counterexample"] and l["wrong"] and l["why_wrong"]
    assert len(l["hints"])==3 and l["near"] and l["far"]
    assert l["teacher_review"]=="REVIEW_PENDING"
    assert l["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert not l["student_publishable"] and not l["student_answer_verified"]
    assert l["proof_certification"]=="NOT_FORMALLY_CERTIFIED"
    assert r["official_atom_membership_confirmed"] is False
    assert r["full_source_clause_reviewed"] is False
    assert r["general_theorem_formally_certified"] is False

@pytest.mark.parametrize("mutation",[
    "delete","duplicate","different_anchor","fake_teacher","publish","certified",
    "verified_student","leak","fake_lesson_type","wrong_source","missing_proof",
    "missing_example","missing_reason","missing_hint","no_counterexample",
    "no_assumption","false_denominator","official_membership","review_candidate",
])
def test_schema_and_provenance_fail_closed(mutation):
    lessons=deepcopy(NEW);source=None;v=lessons[0]
    if mutation=="delete":lessons.pop()
    elif mutation=="duplicate":lessons[-1]=deepcopy(v)
    elif mutation=="different_anchor":v["loc"]=[14,4]
    elif mutation=="fake_teacher":v["teacher_review"]="APPROVED"
    elif mutation=="publish":v["student_publishable"]=True
    elif mutation=="certified":v["proof_certification"]="CERTIFIED"
    elif mutation=="verified_student":v["student_answer_verified"]=True
    elif mutation=="leak":v["teacher_solution_visibility"]="STUDENT"
    elif mutation=="fake_lesson_type":v["kind"]="GENERAL_PROOF_CERTIFIED"
    elif mutation=="wrong_source":v["source_license"]="COPYRIGHT_UNKNOWN"
    elif mutation=="missing_proof":v["reasoning"].pop()
    elif mutation=="missing_example":v["examples"].pop()
    elif mutation=="missing_reason":v["reasoning"][0][1]=""
    elif mutation=="missing_hint":v["hints"].pop()
    elif mutation=="no_counterexample":v["counterexample"]=""
    elif mutation=="no_assumption":v["assumptions"]=[]
    elif mutation in ("false_denominator","official_membership","review_candidate"):
        import build_kb_batch63_atom_context as S
        source=deepcopy(S.build())
        if mutation=="false_denominator":source["official_atomic_denominator"]["COMPULSORY"]=31
        if mutation=="official_membership":source["proposals"][0]["official_atomic_membership"]="CONFIRMED"
        if mutation=="review_candidate":source["proposals"][0]["teacher_review"]="APPROVED"
    with pytest.raises(ValueError): B.build(new=lessons,source=source)

@pytest.mark.parametrize("n,expected",[
    ((1,2,3), (True,True,False,False)),
    ((-1,0,1), (False,True,True,False)),
])
def test_quantifier_finite(n,expected):
    assert W.finite_quantifier(n,lambda x:x>0)==expected

@pytest.mark.parametrize("values", [(),list(range(129)),[0.5], [True]])
def test_quantifier_rejects_unattested(values):
    with pytest.raises(W.FailedPremise):W.finite_quantifier(values,lambda x:x>=0)

def test_quantifier_predicate_requires_real_booleans():
    with pytest.raises(W.FailedPremise):
        W.finite_quantifier([1,2],lambda x:1)

@pytest.mark.parametrize("args,expected",[
    ((1,3,2),("<",F(2),F(6))),((1,3,-2),(">",F(-2),F(-6))),
    ((F(-1,2),0,-3),(">",F(3,2),F(0))),
])
def test_inequality_multiplier_cases(args,expected):
    assert W.inequality_scaled(*args)==expected

@pytest.mark.parametrize("args",[(3,1,2),(1,3,0),(1,2,0.5)])
def test_inequality_rejects_false_or_unsafe(args):
    with pytest.raises(W.FailedPremise):W.inequality_scaled(*args)

@pytest.mark.parametrize("a,b,c,disc,n",[
    (1,2,1,0,1),(2,-3,1,1,2),(1,0,1,-4,0),(1,-5,6,1,2),
    (F(1,2),1,F(1,2),0,1),
])
def test_quadratic_discriminant_exact(a,b,c,disc,n):
    assert W.quadratic_discriminant(a,b,c)==(F(disc),n)

def test_quadratic_fail_zero_lead():
    with pytest.raises(W.FailedPremise):W.quadratic_discriminant(0,2,1)
    assert W.quadratic_sign(1,-4,3,2)==-1
    assert W.quadratic_sign(1,-4,3,1)==0
    assert W.quadratic_sign(1,-4,3,0)==1

@pytest.mark.parametrize("args,expected",[
    ((-8,1,3),True),((-8,2,3),True),((-4,1,2),False),
    ((0,-2,3),False),((0,2,3),True),((9,-1,2),True),
])
def test_rational_power_domain(args,expected):
    assert W.real_rational_power_domain(*args) is expected
@pytest.mark.parametrize("args",[(0,0,1),(-4,1,0),(-4,2,4),(-4,1,2.0)])
def test_rational_power_rejects_undefined_or_unreduced(args):
    with pytest.raises(W.FailedPremise):W.real_rational_power_domain(*args)

@pytest.mark.parametrize("base,x,y,expected",[
    (2,3,5,"<"),(F(1,2),3,5,">"),(3,7,2,">"),(F(1,4),4,1,"<"),
])
def test_log_order_cases(base,x,y,expected):
    assert W.log_monotone_orientation(base,x,y)==expected
@pytest.mark.parametrize("args",[(1,2,3),(0,2,3),(-1,2,3),(2,0,3),(2,2,2)])
def test_log_rejects_wrong_domain(args):
    with pytest.raises(W.FailedPremise):W.log_monotone_orientation(*args)

def test_unit_circle_exact_nonzero_cosine_gate():
    assert W.unit_circle_rational_pair(F(3,5),F(4,5))==(F(1),True)
    assert W.unit_circle_rational_pair(0,1)==(F(1),False)
    with pytest.raises(W.FailedPremise):W.unit_circle_rational_pair(F(3,5),F(3,5))

def test_bisection_polynomial_continuity_and_no_uniqueness_claim():
    lo,hi,exact=W.polynomial_bisect([1,0,-2],1,2,6)
    assert hi-lo==F(1,64) and not exact
    assert W.polynomial_value([1,0,-2],lo)*W.polynomial_value([1,0,-2],hi)<0
    # polynomial has roots -1,0,1; a bracket with sign change is not uniqueness.
    assert W.polynomial_bisect([1,0,-1,0],-2,2,3)==(F(0),F(0),True)
    with pytest.raises(W.FailedPremise):W.polynomial_bisect([1,0,1],-1,1,3)
    with pytest.raises(W.FailedPremise):W.polynomial_bisect([1,0,-2],1,2,25)

def test_vector_basis_and_collinear_rejection():
    assert W.vector_basis_coefficients((1,0),(0,1),(2,-3))==(2,-3,1)
    assert W.vector_basis_coefficients((1,1),(1,-1),(4,0))==(2,2,-2)
    with pytest.raises(W.FailedPremise):W.vector_basis_coefficients((1,0),(2,0),(0,1))

def test_complex_division_exact_with_conjugate():
    assert W.complex_quotient(1,1,1,-1)==(0,1)
    assert W.complex_quotient(3,4,0,1)==(4,-3)
    with pytest.raises(W.FailedPremise):W.complex_quotient(1,1,0,0)

def test_genuine_three_coordinate_intersection_and_false_projection():
    assert W.line_intersection_3d((0,0,0),(1,0,0),(0,0,0),(0,1,0))==(0,0,0)
    assert W.line_intersection_3d((0,0,0),(1,0,0),(0,0,1),(0,1,0)) is None
    assert W.line_intersection_3d((0,0,0),(1,0,0),(0,1,0),(1,0,0)) is None
    assert W.line_intersection_3d((0,0,0),(1,0,0),(2,0,0),(1,0,0))==(0,0,0)
    with pytest.raises(W.FailedPremise):
        W.line_intersection_3d((0,0,0),(0,0,0),(0,0,0),(0,1,0))

def test_classical_probability_requires_explicit_finite_uniform_outcomes():
    assert W.equiprobable_event_probability([1,2,3,4,5,6],True,[2,4,6])==F(1,2)
    assert W.equiprobable_event_probability(["H","T"],True,["H"])==F(1,2)
    for args in [
        ([1,2],False,[1]),([1,2],1,[1]),([1,1],True,[1]),
        ([1,2],True,[1,1]),([1,2],True,[3]),([],True,[]) ]:
        with pytest.raises(W.FailedPremise):W.equiprobable_event_probability(*args)

def test_differential_is_not_finite_increment_general_identity():
    assert W.polynomial_differential([1,0,0],2,F(1,10))==(F(2,5),F(41,100),F(1,100))
    assert W.polynomial_differential([3,1],2,1)==(3,3,0)
    assert W.polynomial_differential([1,0,0,0],1,1)==(3,7,4)
    with pytest.raises(W.FailedPremise):W.polynomial_differential([1,0,0],2,0)

@pytest.mark.parametrize("bad",[0.5,True,False])
def test_float_boolean_never_count_as_math_certification(bad):
    with pytest.raises(W.FailedPremise):W.quadratic_discriminant(1,bad,0)
    with pytest.raises(W.FailedPremise):W.complex_quotient(1,0,bad,1)
    with pytest.raises(W.FailedPremise):W.vector_basis_coefficients((1,bad),(0,1),(2,3))

def test_real_signed_approved_mixed_index_never_exposes_unapproved_work(offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    from app.deep_knowledge import lessons
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    indexed={x.id for x in lessons()}
    assert all(manuscript["lesson_id"] not in indexed for manuscript in NEW)
    for manuscript in NEW:
        result=student_evidence_lookup(manuscript["title"])
        assert {item["knowledge_id"] for item in result["candidates"]}<={doc.id}
        assert manuscript["lesson_id"] not in json.dumps(result,ensure_ascii=False)
        assert not result["teacher_solution_exposed"]
        assert not result["unverified_content_exposed"]
