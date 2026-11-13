"""Independent exact check of all 16 Batch117 worked-example answers.

Authoring examples and teacher-facing solutions are never served as student
authority; these finite checks establish only the stated numerical examples.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product, permutations, combinations

import pytest
import sympy as sp

from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
PACK=json.loads((ROOT/"knowledge/deep/v1/batch117_selective_counting.json").read_text())
DOCS={d["title"].split("：")[0]:d for d in PACK}

def ex(i,j):
    return PACK[i]["worked_examples"][j]

CASES=[
    (0,0,"3种。",len({2,4}|{4,5}) == 3),
    (0,1,"7种。",len(set(range(4)) | set(range(4,7))) == 7),
    (1,0,"6种。",len(list(product(range(3),range(2))))==6),
    (1,1,"6种。",len(list(permutations("ABC",2)))==6),
    (2,0,"20种。",len(list(permutations(range(5),2)))==20),
    (2,1,"24种。",len(list(permutations(range(4),3)))==24),
    (3,0,"10种。",len(list(combinations(range(5),2)))==10),
    (3,1,"20种。",len(list(combinations(range(6),3)))==20),
    (4,0,"x³+6x²+12x+8。",sp.expand((sp.Symbol("x")+2)**3)==sp.Symbol("x")**3+6*sp.Symbol("x")**2+12*sp.Symbol("x")+8),
    (4,1,"24。",sp.expand((2*sp.Symbol("x")-1)**4).coeff(sp.Symbol("x"),2)==24),
    (5,0,"2/3。",Fraction(2,6)/Fraction(3,6)==Fraction(2,3)),
    (5,1,"条件概率0，且不独立。",Fraction(0,6)!=Fraction(1,6)*Fraction(1,6)),
    (6,0,"1/2。",Fraction(3,4)*Fraction(1,2)+Fraction(1,4)*Fraction(1,2)==Fraction(1,2)),
    (6,1,"1.8%。",Fraction(6,10)*Fraction(1,100)+Fraction(4,10)*Fraction(3,100)==Fraction(18,1000)),
    (7,0,"3/5。",Fraction(sp.binomial(2,1)*sp.binomial(3,1),sp.binomial(5,2))==Fraction(3,5)),
    (7,1,"均值1；P(X=2)=1/5。",(Fraction(3*2,6),Fraction(sp.binomial(2,2)*sp.binomial(4,1),sp.binomial(6,3)))==(1,Fraction(1,5))),
]

@pytest.mark.parametrize("i,j,answer,expected",CASES,ids=lambda x:str(x))
def test_all_sixteen_example_answers_have_independent_exact_witness(i,j,answer,expected):
    assert expected is True, (i,j,"bad math oracle")
    assert ex(i,j)["answer"]==answer
    assert len(ex(i,j)["steps"])>=2
    assert ex(i,j)["question"]

@pytest.mark.parametrize("case,is_wrong",[
    ("overlapping_addition",3+2!=len({1,2,3}|{3,4})),
    ("nonuniform_branches",2*4!=2+4),
    ("zero_permutation",sp.factorial(0)==1 and sp.factorial(5)/sp.factorial(5)==1),
    ("unordered_not_permutation",len(list(combinations(range(5),2)))!=len(list(permutations(range(5),2)))),
    ("noncommuting_matrices", (sp.Matrix([[1,0],[0,0]])*sp.Matrix([[0,1],[0,0]])+sp.Matrix([[0,1],[0,0]])*sp.Matrix([[1,0],[0,0]]))!=2*sp.Matrix([[1,0],[0,0]])*sp.Matrix([[0,1],[0,0]])),
    ("empty_condition_undefined",(sp.S.Zero/sp.S.Zero) is sp.S.NaN),
    ("not_a_partition", ({1,2}&{2,3}) and ({1,2}|{2,3})!={1,2,3,4,5,6}),
    ("without_replacement_not_binomial",sp.binomial(1,2)==0 and Fraction(1,4)>0),
])
def test_misuse_boundary_has_exact_counterexample(case,is_wrong):
    assert bool(is_wrong),case

def test_all_new_math_answers_are_teacher_only():
    assert len(PACK)==8
    for d in PACK:
        assert d["review"]["status"]=="REVIEW_PENDING"
        assert d["teacher_solution_visibility"]=="TEACHER_ONLY"
        assert d["review"]["reviewer_id"] is None
