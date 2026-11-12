"""16 worked answers checked independently of authored rationales, exact arithmetic only."""
from fractions import Fraction as F
from itertools import product
from math import comb
import json
from pathlib import Path
import pytest
import sympy as s

ROOT=Path(__file__).resolve().parents[1]
PACK=json.loads((ROOT/"knowledge/deep/v1/batch118_probability_distribution.json").read_text())

CASES=[
(0,0,"p(0)=1/4,p(1)=1/2,p(2)=1/4。",dict(zip((0,1,2),(
    F(sum(sum(bits)==i for bits in product((0,1),repeat=2)),4) for i in (0,1,2))))=={0:F(1,4),1:F(1,2),2:F(1,4)}),
(0,1,"a=2/5。",1-F(1,5)-F(2,5)==F(2,5)),
(1,0,"7。",sum(F((x+(7-x)),6) for x in range(1,7))==7),
(1,1,"1/2。",sum(F(3*x-2*x,2) for x in (0,1))==F(1,2)),
(2,0,"E[X]=2，Var(X)=1。",sum(F((x-2)**2,2) for x in (1,3))==1),
(2,1,"9。",sum(F((3*x-4-(-1))**2,2) for x in (0,2))==9),
(3,0,"3/8。",sum(sum(bits)==2 for bits in product((0,1),repeat=3))==3),
(3,1,"9/16。",F(3,4)**2==F(9,16)),
(4,0,"均值5/2；方差5/4。",5*F(1,2)==F(5,2) and 5*F(1,2)*F(1,2)==F(5,4)),
(4,1,"均值1；方差3/4。",4*F(1,4)==1 and 4*F(1,4)*F(3,4)==F(3,4)),
(5,0,"6/5。",3*F(4,10)==F(6,5)),
(5,1,"1。",3*F(2,6)==1),
(6,0,"z=2。",s.simplify((14-10)/s.sqrt(4))==2),
(6,1,"P(−1≤Z≤2)。",((95-100)/5,(110-100)/5)==(-1,2)),
(7,0,"r=1。",s.Rational(4,1)/s.sqrt(2*8)==1),
(7,1,"r=−1。",s.Rational(-2,1)/s.sqrt(2*2)==-1),
]

@pytest.mark.parametrize("i,j,expected,math_valid",CASES)
def test_sixteen_independent_author_exercise_oracles(i,j,expected,math_valid):
    assert math_valid is True, (i,j,"independent math witness failed")
    assert PACK[i]["worked_examples"][j]["answer"]==expected
    assert PACK[i]["worked_examples"][j]["steps"]
    assert PACK[i]["teacher_solution_visibility"]=="TEACHER_ONLY"

@pytest.mark.parametrize("label,witness",[
("invalid_pmf",F(1,2)+F(2,3)>1),
("nonindependence_expectation",F(1,2)+F(1,2)==1),
("variance_negative_scale",(F(-2))**2==4),
("without_replacement_binomial_wrong",F(1,2)!=1),
("correlated_binomial_variance",s.Rational(1,2)!=1),
("hypergeometric_not_half",3*F(4,10)!=F(3,2)),
("standardization_not_normality",len({-1,1})==2),
("pearson_zero_variance",sum((x-2)**2 for x in (2,2,2))==0),
("binomial_full_normalization",sum(F(comb(4,k),16) for k in range(5))==1),
("hypergeometric_distribution_sum",sum(F(comb(2,k)*comb(4,3-k),comb(6,3)) for k in (0,1,2))==1),
])
def test_boundary_invalid_generalizations_have_finite_exact_counterexamples(label,witness):
    assert bool(witness),label

def test_theorem_assumptions_not_machine_proof_certificates():
    audit=json.loads((ROOT/"docs/evaluation/KB_BATCH118_MATH_EXACT.json").read_text())
    assert audit["positive_cases"]==audit["negative_cases"]==8
    assert audit["general_proofs_certified"]==audit["teacher_approved"]==0
    assert all(not c["general_proof_machine_certified"] for c in audit["cases"])
