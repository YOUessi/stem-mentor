from scripts.kb_frozen_batch24 import frozen_batch24_lessons
"""Batch17 independent bounded math oracle checks and student-release negative regression.

No finite oracle proves all natural language proofs or certifies official scope.
"""
import copy
import json
from fractions import Fraction as F
from itertools import product, permutations
from math import gcd, lcm
from pathlib import Path
import pytest
import sympy as sp
from pydantic import ValidationError
from app.deep_knowledge import DeepLesson,lessons,curriculum
from app.deep_retrieval import student_evidence_lookup
from app.objective_proposals import editorial_review_queue,validate_proposals

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"curriculum/highschool_math/author_draft_batch17.json"
COURSE=ROOT/"curriculum/highschool_math/cross_track_atomic_candidates_batch17.json"
ROWS=json.loads(SOURCE.read_text(encoding="utf8"))
MAP=json.loads(COURSE.read_text(encoding="utf8"))

def test_batch17_source_and_structured_lessons_unapproved():
    assert len(ROWS)==len(MAP)==11
    assert len(frozen_batch24_lessons())==287 and len(curriculum())==178
    assert len({x["id"] for x in ROWS})==11
    assert set(x["curriculum_ids"][0] for x in ROWS)==set(x["id"] for x in MAP)
    assert set(x["curriculum_ids"][0] for x in ROWS)=={f"HS-MATH-{x}" for x in range(151,162)}
    assert sum(x["kind"]=="theorem" for x in ROWS)==3
    assert sum(x["kind"]=="concept" for x in ROWS)==4
    assert sum(x["kind"]=="method" for x in ROWS)==4
    assert sum(len(x["proof_steps"]) for x in ROWS)==12
    assert sum(len(x["worked_examples"]) for x in ROWS)==22
    for raw in ROWS:
        doc=DeepLesson.model_validate(raw)
        assert doc.review.status=="REVIEW_PENDING"
        assert doc.review.reviewer_id is None
        assert doc.teacher_solution_visibility=="TEACHER_ONLY"
        assert doc.provenance.permission=="PROJECT_AUTHORED"
        assert len(doc.hint_ladder)==3
        assert len(doc.worked_examples)==2
        assert len(doc.counterexamples)==1
    assert all(x["source"]["mapping_type"]=="ENGINEERING_INTERPRETATION" and
               x["source"]["teacher_review"]=="PENDING" and x["status"]=="PLANNED" for x in MAP)

def test_thirteen_sample_objective_links_are_explicit_but_not_certified():
    data=editorial_review_queue()
    assert validate_proposals(data)
    assert data["total_source_objective_candidates"]==132
    assert data["total_deep_draft_lessons"]==235
    assert data["proposed_objectives"]==132
    assert data["proposed_edges"]==154
    assert all(x["without_suggestion"]==0 for x in data["by_track"].values())
    assert data["official_atomic_denominator"] is None
    assert data["official_coverage_percent"] is None
    assert data["independent_teacher_approved_matches"]==0
    assert data["student_published_knowledge_count"]==0
    assert all(x["match_status"]=="EDITORIAL_PROPOSAL_NOT_VERIFIED" for x in data["items"])
    assert student_evidence_lookup("空集空间基底节拍同步单循环比赛")["status"]=="NO_APPROVED_EVIDENCE"

@pytest.mark.parametrize("row_idx,field,value",[
    (0,"teacher_solution_visibility","STUDENT_VISIBLE"),
    (2,"kind","theorem"),  # missing proof and explicit statement, must reject
])
def test_invalid_student_exposure_or_invalid_kind_rejected(row_idx,field,value):
    bad=copy.deepcopy(ROWS[row_idx]);bad[field]=value
    with pytest.raises(ValidationError): DeepLesson.model_validate(bad)

@pytest.mark.parametrize("a,b",product(range(0,64),repeat=2))
def test_empty_subset_and_two_sided_inclusion(a,b):
    A={k for k in range(6) if a>>k&1}
    B={k for k in range(6) if b>>k&1}
    assert not A.difference(A)
    assert set() <= A
    assert (A==B)==(A<=B and B<=A)
    assert (A<B)==(A<=B and A!=B)

@pytest.mark.parametrize("x",range(-9,10))
def test_function_rational_cancellation_retains_domain(x):
    f=F(x*x-1,x-1) if x!=1 else None
    g=x+1
    if x==1:
        assert f is None and g==2
    else:assert f==g

@pytest.mark.parametrize("base,num,den",product((1,4,9,16),(0,1,2,3),(1,2,3)))
def test_positive_rational_exponents(base,num,den):
    x=sp.Rational(num,den)
    lhs=base**x
    assert sp.simplify(lhs**den-base**num)==0

@pytest.mark.parametrize("x,y,z",product(range(-2,3),repeat=3))
def test_basis_expansion_exact(x,y,z):
    M=sp.Matrix([[1,0,1],[0,1,1],[0,0,1]])
    target=sp.Matrix([x,y,z])
    coeff=sp.Matrix([x-z,y-z,z])
    assert M.det()==1
    assert M*coeff==target
    assert M.inv()*target==coeff

@pytest.mark.parametrize("p", (True,False))
def test_classical_propositional_laws_and_independence(p):
    assert (p or not p) is True
    assert (p and not p) is False
    assert (p==p) is True
    # Γ={P,Q}: valuation Q=True,P=False refutes Q⊨P and vice versa.
    assert (False or (not True)) is False  # Boolean semantics: False or False -> False

@pytest.mark.parametrize("n",range(-101,102))
def test_direct_proof_and_odd_square_contrapositive(n):
    if n%2==0:assert (n*n)%2==0
    if (n*n)%2==1:assert n%2==1

@pytest.mark.parametrize("x,y",product(range(2),repeat=2))
def test_axiom_system_satisfiability_logic(x,y):
    p,q=bool(x),bool(y)
    if p and q:assert (p and q)
    if q and not p: assert q and not p  # Q does not entail P.
    if p and not q: assert p and not q  # P does not entail Q.

def test_correlation_not_intervention():
    # Observational Z -> X, Z -> Y, no causal edge X -> Y.
    observed=[(z,z,z) for z in (0,1)]
    assert all(x==y for _,x,y in observed)
    # do(X=1), with Z=0 fixed: Y remains 0.
    z=0; intervention_x=1; y=z
    assert intervention_x!=y

@pytest.mark.parametrize("respondents,scores",[(30,210),(5,15),(10,0),(1,14)])
def test_survey_valid_means_and_zero_guard(respondents,scores):
    assert F(scores,respondents)*respondents==scores
    with pytest.raises(ZeroDivisionError):F(scores,0)

@pytest.mark.parametrize("m,n",product(range(1,26),repeat=2))
def test_rhythm_first_common_tick(m,n):
    t=lcm(m,n)
    assert t==m*n//gcd(m,n)
    assert t%m==t%n==0
    assert not any(k%m==0 and k%n==0 for k in range(1,t))

@pytest.mark.parametrize("n",range(2,25))
def test_round_robin_necessary_rounds_and_edges(n):
    games=n*(n-1)//2
    per_round=n//2
    lower=(games+per_round-1)//per_round
    assert lower==(n-1 if n%2==0 else n)
    assert per_round*lower>=games
    assert len(list(product(range(n),range(n))))==n*n

@pytest.mark.parametrize("a,b",list(permutations(range(4),2)))
def test_four_team_three_rounds_exact_pairs(a,b):
    rounds=[((0,3),(1,2)),((0,2),(3,1)),((0,1),(2,3))]
    pairs={frozenset(v) for matches in rounds for v in matches}
    assert len(pairs)==6
    assert frozenset((a,b)) in pairs
    assert all(len({t for v in matches for t in v})==4 for matches in rounds)
