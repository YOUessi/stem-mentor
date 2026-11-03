"""Independent exact checks for Batch07's eight new teacher-side theorem drafts.

Checks each of sixteen fixed worked examples against independently constructed
finite arithmetic or symbolic facts; does not certify whole theorem proofs.
"""
from __future__ import annotations
import math
import subprocess
import sys
from pathlib import Path
from fractions import Fraction
from sympy import symbols, diff, simplify, sqrt
import pytest

ROOT=Path(__file__).resolve().parents[2]
from app.deep_knowledge import lessons

x=symbols("x",real=True)
LESSONS={v.id:v for v in lessons()}
ORACLES={
"math.hs.sets.de-morgan-laws":[
  ("{4}",lambda:set(range(1,5)) - ({1,2}|{2,3}) == {4}),
  ("{1,3,4}",lambda:set(range(1,5)) - ({1,2}&{2,3}) == {1,3,4}),
],
"math.hs.function.strict-inverse-monotonic":[
  ("(x-2)/3",lambda:simplify((3*x+2-2)/3-x)==0),
  ("√y",lambda:sqrt(4)==2 and sqrt(0)==0),
],
"math.hs.sequence.arithmetic-nth-term":[
  ("a6=28",lambda:3+(6-1)*5==28),
  ("a4=1，a5=-1",lambda:7+3*(-2)==1 and 7+4*(-2)==-1),
],
"math.hs.calculus.product-derivative":[
  ("5x⁴",lambda:simplify(diff(x**2*x**3,x)-5*x**4)==0),
  ("7",lambda:diff((x+1)*(2*x-3),x).subs(x,2)==7),
],
"math.hs.geometry.circle-chord-length":[
  ("8",lambda:2*math.isqrt(5*5-3*3)==8),
  ("d=3",lambda:3**2-3**2==0 and 3**2-4**2<0),
],
"math.hs.statistics.variance-affine":[
  ("Var(Y)=4",lambda:sum((i-9)**2 for i in (7,11))//2==4),
  ("Var(Z)=4",lambda:sum((i-8)**2 for i in (6,10))//2==4),
],
"math.hs.probability.bayes-partition":[
  ("1/12",lambda:Fraction(9,1000)/(Fraction(9,1000)+Fraction(99,1000))==Fraction(1,12)),
  ("3/4",lambda:Fraction(3,8)/(Fraction(1,8)+Fraction(3,8))==Fraction(3,4)),
],
"math.hs.counting.two-set-inclusion-exclusion":[
  ("15 人",lambda:len(set(range(1,11)) | set(range(8,16)))==15),
  ("13 个",lambda:len({i for i in range(1,21) if i%2==0 or i%3==0})==13),
],
}
assert len(ORACLES)==8

def test_generator_reproducible():
    result=subprocess.run([sys.executable,str(ROOT/"scripts/build_kb_batch07_lessons.py"),"--check"],
        cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr

@pytest.mark.parametrize("knowledge_id,case",[
    (knowledge_id,case)
    for knowledge_id,pairs in ORACLES.items()
    for case in range(2)
])
def test_independent_fixed_example(knowledge_id,case):
    doc=LESSONS[knowledge_id]
    needle,oracle=ORACLES[knowledge_id][case]
    assert needle in doc.worked_examples[case].answer
    assert oracle(), f"Incorrect independently evaluated example {knowledge_id} #{case+1}"
    assert len(doc.worked_examples[case].steps)>=2
    assert len(doc.worked_examples[case].check)>=10
    assert doc.review.status=="REVIEW_PENDING"
    assert doc.teacher_solution_visibility=="TEACHER_ONLY"

@pytest.mark.parametrize("knowledge_id",sorted(ORACLES))
def test_positive_and_negative_examples_have_proof_obligations(knowledge_id):
    lesson=LESSONS[knowledge_id]
    assert len(lesson.proof_steps)==3
    assert all(step.claim and step.reason for step in lesson.proof_steps)
    assert lesson.counterexamples[0].false_claim
    assert lesson.counterexamples[0].explanation
    assert lesson.misconceptions[0].repair_question
    assert len(lesson.hint_ladder)==3
    assert lesson.transfer.near and lesson.transfer.far
    assert lesson.prerequisites and lesson.prerequisite_lesson_ids

def test_cross_subject_negative_math_invariants():
    assert ({1,2}|{2,3}) != ({1,2}&{2,3})
    assert (-1)**2 == (+1)**2  # x^2 is not injective on R
    assert 1+2 != 4+2          # common difference does not specify a1
    assert simplify(diff(x*x**2,x)-diff(x,x)*diff(x**2,x))!=0
    assert 2**2-3**2<0       # no real chord for r=2,d=3
    assert Fraction(9,10)!=Fraction(1,12)  # likelihood not posterior
    assert 10+8!=10+8-3  # intersection counted twice before subtraction
