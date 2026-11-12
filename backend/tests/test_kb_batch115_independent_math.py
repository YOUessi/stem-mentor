"""Independent exact and adverse math cases for Batch115: not general proof certification."""
from fractions import Fraction as Q
from pathlib import Path
import json
import sympy as sp
import pytest
ROOT=Path(__file__).resolve().parents[2]
R=sp.Rational
x=sp.Symbol("x", real=True)

# Independently constructed from mathematics, not from each lesson's answer field.
EXAMPLES=[
 ("115.01.1 free vector equality", (4-1,6-2)==(1-(-2),4-0) and (4-1,6-2)==(3,4)),
 ("115.01.2 zero vector", (2-2,3-3)==(-5-(-5),7-7)==(0,0)),
 ("115.02.1 add-subtract", (2-3,-1+4)==(-1,3) and (2-(-3),-1-4)==(5,-5)),
 ("115.02.2 displacement magnitude", sp.sqrt(1**2+2**2)==sp.sqrt(5) and sp.sqrt(5)<3),
 ("115.03.1 orthogonal nonzero vectors", 3*4+4*(-3)==0 and 3**2+4**2==25 and 4**2+(-3)**2==25),
 ("115.03.2 dot angle cosine", 1*(-1)+2*3==5 and sp.simplify(5/sp.sqrt(50)-1/sp.sqrt(2))==0),
 ("115.04.1 orthogonal unknown k", 2*3+2*(-3)==0 and (3,2)!=(0,0)),
 ("115.04.2 zero-angle false", 0*1+0*0==0 and sp.sqrt(0**2+0**2)==0),
 ("115.05.1 interior Bernoulli MLE", R(3,4)==R(3,4) and R(3,4)**3*(1-R(3,4))==R(27,256)),
 ("115.05.2 all failures MLE", (1-0)**5==1 and (1-R(1,2))**5<R(1)),
 ("115.06.1 binomial one-sided p", sum(sp.binomial(4,k)*R(1,2)**4 for k in range(4,5))==R(1,16)),
 ("115.06.2 significance 0.1", R(1,16)<R(1,10)),
 ("115.07.1 least squares three points", sum((a-1)*(b-3) for a,b in [(0,1),(1,3),(2,5)])==4 and sum((a-1)**2 for a in (0,1,2))==2),
 ("115.07.2 least squares two points", sum((a-1)*(b-3) for a,b in [(0,1),(2,5)])==4 and sum((a-1)**2 for a in (0,2))==2),
 ("115.08.1 discrete exponential growth", Q(100)*Q(11,10)**2==Q(121) and Q(121)-Q(110)!=Q(110)-Q(100)),
 ("115.08.2 exponential decay", Q(80)*Q(3,4)**2==Q(45) and Q(45,60)==Q(60,80)),
]
@pytest.mark.parametrize("label,result",EXAMPLES,ids=[x for x,_ in EXAMPLES])
def test_independent_exact_example(label,result):
    assert result is True or result is sp.S.true,label

def test_zero_vector_is_not_angle():
    a=sp.Matrix([0,0]);b=sp.Matrix([1,0])
    assert a.dot(b)==0 and sp.sqrt(a.dot(a))==0
    assert sp.simplify(a.dot(b)/(sp.sqrt(a.dot(a))*sp.sqrt(b.dot(b)))) is sp.nan

def test_projection_with_zero_basis_is_division_by_zero():
    a=sp.Matrix([4,2]);z=sp.Matrix([0,0])
    assert a.dot(z)==0 and z.dot(z)==0
    assert sp.simplify(sp.Rational(0)/sp.Rational(0)) is sp.nan

def test_orthogonal_nonzero_condition_and_pitfall():
    a=sp.Matrix([3,2]);b=sp.Matrix([2,-3])
    assert a.dot(b)==0 and a.norm()>0 and b.norm()>0
    # The zero-vector counterexample refutes unconditional angle inference.
    assert sp.Matrix([0,0]).dot(b)==0

def test_bernoulli_all_success_boundary_and_open_parameter():
    p=sp.symbols("p",real=True)
    assert sp.diff(p**3,p).subs(p,R(1,2))>0
    assert (p**3).subs(p,1)==1
    assert (p**3).subs(p,R(999,1000))<1
    # Open interval only has supremum 1; not an achieved MLE.
    assert sp.limit(p**3,p,1,dir="-")==1

def test_pvalue_not_posterior_and_significance_threshold():
    p=R(1,16)
    assert p>R(5,100) and p<R(1,10)
    assert p != R(4,100) # p value depends on the null tail, not a posterior.
    doc=json.loads((ROOT/"knowledge/deep/v1/batch115_vectors_inference.json").read_text())[5]
    assert "不是P(H0|data)" in doc["statement"]

def test_design_matrix_degeneracy():
    xs=[2,2];ys=[3,5]
    xb=sum(xs)/len(xs);yb=sum(ys)/len(ys)
    sxx=sum((t-xb)**2 for t in xs)
    assert sxx==0 and yb==4
    assert all(abs((4-2*b)+b*t-4)<1e-10 for b in (-3,-2,0,1,4) for t in xs)
    assert sp.simplify(sp.Rational(0)/sp.Rational(0)) is sp.nan

def test_exponential_constant_relative_not_absolute():
    terms=[Q(100),Q(110),Q(121)]
    assert terms[1]/terms[0]==terms[2]/terms[1]==Q(11,10)
    assert terms[1]-terms[0]==10 and terms[2]-terms[1]==11
    assert terms[1]-terms[0]!=terms[2]-terms[1]

def test_historical_batch114_census_keeps_frozen_cohort():
    # The prior batch's published census must not accidentally include later packs.
    prior=json.loads((ROOT/"docs/evaluation/KB_BATCH114_AUDIT.json").read_text())
    assert prior["total_deep_drafts"]==482
    current=json.loads((ROOT/"docs/evaluation/KB_BATCH115_AUDIT.json").read_text())
    assert current["prior_deep_drafts"]==prior["total_deep_drafts"]
    assert current["total_deep_drafts"]==current["prior_deep_drafts"]+8
