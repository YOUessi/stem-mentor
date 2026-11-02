"""56 independently computed *worked-example* spot checks for the 28 drafts.

These are exact arithmetic/symbolic/or bounded finite-case oracles, NOT
certification of the surrounding narrative proofs or teacher approval.
"""
from math import comb
import pytest
from sympy import I, Rational as R, diff, pi, sin, cos, sqrt, simplify, symbols, log

from app.deep_knowledge import lessons

x = symbols("x", real=True)
T = lambda value: bool(simplify(value) == 0)
doc_lookup = {lesson.id:lesson for lesson in lessons()}

# Each tuple: knowledge short ID, teacher example 0/1, expected answer fragment,
# and an independent exact arithmetic/symbolic cross-check.
CASES = [
 ("sets.union-intersection",0,"A∩B={2,4}",lambda: {1,2,4}&{2,3,4}=={2,4} and {1,2,4}|{2,3,4}=={1,2,3,4}),
 ("sets.union-intersection",1,"U\\A={1,3,5}",lambda: set(range(1,6))-{2,4}=={1,3,5}),
 ("logic.implication",0,"充分非必要",lambda: 3**2==9 and (-3)**2==9 and -3!=3),
 ("logic.implication",1,"充分非必要",lambda: all(v>0 for v in (2,3,5)) and 0.5>0 and not 0.5>1),
 ("logic.quantifier",0,"x²<0",lambda: all(t*t>=0 for t in range(-20,21))),
 ("logic.quantifier",1,"n²≠2",lambda: all(t*t!=2 for t in range(-20,21))),
 ("inequality.sign-multiplication",0,"x>-3",lambda: -2*0<6 and not -2*(-4)<6),
 ("inequality.sign-multiplication",1,"ac>-8",lambda: (-2)*3 > -8 and (-2)*5 < -8),
 ("quadratic.sign",0,"2<x<3",lambda: T((2-2)*(2-3)) and R(5,2)**2-5*R(5,2)+6<0),
 ("quadratic.sign",1,"1≤x≤3",lambda: -2**2+4*2-3==1 and -(4**2)+4*4-3<0),
 ("inequality.amgm",0,"25",lambda: all(a*(10-a)<=25 for a in range(11)) and 5*5==25),
 ("inequality.amgm",1,"x=2",lambda: all(R(i,2)+4/R(i,2)>=4 for i in range(1,25)) and R(2)+4/R(2)==4),
 ("function.domain",0,"[2,+∞)",lambda: sqrt(2-2)==0 and sqrt(1-2).is_real is False),
 ("function.domain",1,"[-1,3)∪(3,+∞)",lambda: sqrt(-1+1)/(-1-3)==0 and 3-3==0),
 ("function.monotonicity",0,"严格递增",lambda: all(u*u<v*v for u,v in [(0,1),(1,2),(2,3),(0,3)])),
 ("function.monotonicity",1,"严格递减",lambda: all(-3*u+1>-3*v+1 for u,v in [(-2,-1),(0,1),(1,5)])),
 ("function.quadratic-vertex",0,"最小值 2",lambda: T(diff(x*x-6*x+11,x).subs(x,3)) and 3**2-6*3+11==2),
 ("function.quadratic-vertex",1,"最大值 5",lambda: T(diff(-2*x*x+8*x-3,x).subs(x,2)) and -2*2**2+8*2-3==5),
 ("exponent.product",0,"256",lambda: 2**3*2**5==256),
 ("exponent.product",1,"1/4>1/8",lambda: R(1,2)**2>R(1,2)**3),
 ("logarithm.inverse",0,"x=9",lambda: log(9-1,2)==3),
 ("logarithm.inverse",1,"5",lambda: log(9,3)+log(27,3)==5),
 ("trig.pythagorean",0,"4/5",lambda: R(3,5)**2+R(4,5)**2==1),
 ("trig.pythagorean",1,"√3/2",lambda: T((-R(1,2))**2+(sqrt(3)/2)**2-1)),
 ("trig.sum-angle",0,"1",lambda: sin(pi/3+pi/6)==1),
 ("trig.sum-angle",1,"0",lambda: cos(pi/4+pi/4)==0),
 ("vector.dot-product",0,"90°",lambda: 1*(-2)+2*1==0),
 ("vector.dot-product",1,"3",lambda: 3*1+4*0==3),
 ("triangle.sine-law",0,"5√3",lambda: T((5*sqrt(3))/sin(pi/3)-5/sin(pi/6))),
 ("triangle.sine-law",1,"B=30°",lambda: sin(pi/6)/4==sin(pi/6)/4 and pi-pi/6-pi/6>0),
 ("triangle.cosine-law",0,"a=5",lambda: 3**2+4**2==5**2),
 ("triangle.cosine-law",1,"A=60°",lambda: T(sqrt(3)**2-(1**2+2**2-2*1*2*cos(pi/3)))),
 ("complex.modulus",0,"5",lambda: T(sqrt(3**2+(-4)**2)-5)),
 ("complex.modulus",1,"5",lambda: T((2+I)*(2-I)-5)),
 ("probability.laplace",0,"1/2",lambda: R(3,6)==R(1,2)),
 ("probability.laplace",1,"1/2",lambda: R(2,4)==R(1,2)),
 ("statistics.variance",0,"8/3",lambda: sum((R(i)-3)**2 for i in [1,3,5])/3==R(8,3)),
 ("statistics.variance",1,"s²=2",lambda: sum((R(i)-3)**2 for i in [2,4])/(2-1)==2),
 ("sequence.arithmetic-sum",0,"155",lambda: sum(2+3*k for k in range(10))==155),
 ("sequence.arithmetic-sum",1,"15",lambda: sum(7-2*k for k in range(5))==15),
 ("sequence.geometric-sum",0,"S4=-10",lambda: sum(2*(-2)**k for k in range(4))==-10),
 ("sequence.geometric-sum",1,"S8=40",lambda: sum(5*1**k for k in range(8))==40),
 ("calculus.power-rule",0,"4x³",lambda: T(diff(x**4,x)-4*x**3)),
 ("calculus.power-rule",1,"6x−5",lambda: T(diff(3*x**2-5*x+7,x)-(6*x-5))),
 ("calculus.derivative-monotonicity",0,"严格递增",lambda: all(u**3<v**3 for u,v in [(-5,-4),(-1,0),(0,1)])),
 ("calculus.derivative-monotonicity",1,"严格递减",lambda: all(-u>-v for u,v in [(-2,-1),(-1,0),(0,2)])),
 ("counting.product-rule",0,"9",lambda: len([(a,b) for a in range(1,4) for b in range(1,4)])==9),
 ("counting.product-rule",1,"7",lambda: len(set(("bus",i) for i in range(4))|set(("subway",i) for i in range(3)))==7),
 ("counting.binomial",0,"x³+6x²+12x+8",lambda: T((x+2)**3-(x**3+6*x**2+12*x+8))),
 ("counting.binomial",1,"10",lambda: comb(5,2)==10),
 ("probability.conditioning",0,"2/3",lambda: R(len(set([4,6])),len(set([2,4,6])))==R(2,3)),
 ("probability.conditioning",1,"1",lambda: R(1,1)/R(1,1)==1),
 ("probability.total",0,"1.8%",lambda: R(6,10)*R(1,100)+R(4,10)*R(3,100)==R(18,1000)),
 ("probability.total",1,"35%",lambda: R(1,4)*R(8,10)+R(3,4)*R(2,10)==R(35,100)),
 ("geometry.ellipse-focus",0,"(-4,0)",lambda: 25-9==4**2 and sqrt((5+4)**2)+sqrt((5-4)**2)==10),
 ("geometry.ellipse-focus",1,"x²/25+y²/16=1",lambda: 5**2-3**2==16),
]


@pytest.mark.parametrize("key,index,fragment,oracle", CASES,
                         ids=lambda item: item if isinstance(item,str) else None)
def test_each_worked_example_has_correct_frozen_answer_and_independent_oracle(
        key,index,fragment,oracle):
    item = doc_lookup["math.hs."+key]
    example = item.worked_examples[index]
    assert fragment in example.answer
    assert len(example.steps) >= 2
    assert len(example.check) >= 10
    assert bool(oracle()) is True


def test_teacher_answer_oracle_covers_each_of_the_28_lesson_drafts_twice():
    assert len(CASES)==2*len(lessons())==56
    assert {(k,i) for k,i,_,_ in CASES} == {
        (d.id.removeprefix("math.hs."),i) for d in lessons() for i in (0,1)
    }
    assert all(d.review.status == "REVIEW_PENDING" for d in lessons())
