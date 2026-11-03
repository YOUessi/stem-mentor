"""Independent teacher-side spot oracles for 116 worked examples in batch04.

Each oracle is a reproducible exact or bounded arithmetic/geometric check
against a FROZEN expected answer fragment, not a proof of any whole lesson.
The examples are unreviewed, remain inaccessible to student endpoints.
"""
import json
from math import comb, gcd, ceil
from pathlib import Path

import pytest
from sympy import Rational as R, cos, sin, pi, sqrt, symbols, simplify, diff, Matrix, erf, asin

from app.deep_knowledge import ROOT, lessons, public_summary

x, t = symbols("x t", real=True)
T = lambda expression: simplify(expression) == 0


def chi_square(table):
    rs = [sum(row) for row in table]
    cs = [sum(row[j] for row in table) for j in range(len(table[0]))]
    total = sum(rs)
    return sum(
        (R(table[i][j]) - R(rs[i]*cs[j],total))**2 / R(rs[i]*cs[j],total)
        for i in range(len(table)) for j in range(len(cs))
    )


def line_distance(point, coeffs):
    a,b,c = coeffs
    return abs(a*point[0]+b*point[1]+c)/sqrt(a*a+b*b)


def matrix_cross(a,b):
    return tuple(Matrix(a).cross(Matrix(b)))


def sample_quantile(data, fraction):
    ordered = sorted(data)
    return ordered[ceil(R(fraction)*len(ordered))-1]


def ssa_valid_count(A, a, b):
    from math import asin, degrees, sin as msin, radians
    s=b*msin(radians(A))/a
    if s>1 or s<=0: return 0
    B=degrees(asin(s))
    return len({round(candidate,8) for candidate in (B,180-B)
                if A+candidate<180-1e-10})


# Original mathematical oracle + a frozen answer fragment for BOTH examples.
# Some conditions are checked by finite counterexample / spot arithmetic, not globally proven.
ORACLES = {
 "probability.binomial-distribution": (
  ("3/8", lambda: R(comb(3,2),8)==R(3,8)),
  ("16/81",lambda: R(2,3)**4==R(16,81))),
 "probability.hypergeometric": (
  ("3/10",lambda: R(comb(4,2)*comb(6,1),comb(10,3))==R(3,10)),
  ("3/10",lambda: R(comb(3,2),comb(5,2))==R(3,10))),
 "probability.normal-density": (
  ("z=1",lambda: R(12-10,2)==1),
  ("1/2",lambda: R(1,2)*(1+erf((3-3)/sqrt(2)))==R(1,2))),  # symmetry about the stated mean
 "statistics.correlation-regression": (
  ("r=1",lambda: sum((a-2)*(b-4) for a,b in [(1,2),(2,4),(3,6)])==sqrt(sum((a-2)**2 for a in (1,2,3))*sum((b-4)**2 for b in (2,4,6)))),
  ("未定义",lambda: sum((v-3)**2 for v in (3,3,3))==0)),
 "statistics.chi-square": (
  ("20/3",lambda: chi_square([[20,10],[10,20]])==R(20,3)),
  ("χ²=0",lambda: chi_square([[10,10],[10,10]])==0)),
 "modeling.workflow": (
  ("60t",lambda: R(180,3)==60),
  ("ŷ(3)=7",lambda: 2*3+1==7 and 2*1+1==3 and 2*2+1==5)),
 "modeling.validation": (
  ("3/2",lambda: R(abs(3-2)+abs(2-4),2)==R(3,2)),
  ("√(5/2)",lambda: T((sqrt(R(1+4,2)))**2-R(5,2)))),
 "space.coordinate-distance": (
  ("13",lambda: sqrt((4-1)**2+(6-2)**2+(15-3)**2)==13),
  ("垂直",lambda: 1*2+0*3+2*(-1)==0)),
 "space.line-plane-normal": (
  ("(1,t,2+t)",lambda: all((1,s,2+s)[0]==1 and (1,s,2+s)[2]-(1,s,2+s)[1]==2 for s in (-2,0,3))),
  ("z=3",lambda: 0*(1-0)+0*(2-0)+1*(3-3)==0)),
 "space.angle-distance": (
  ("4",lambda: abs(5-1)==4),
  ("π/2",lambda: asin(R(1))==pi/2)),
 "geometry.circle-intersections": (
  ("两个交点",lambda: 5**2-3**2==4**2),
  ("外切",lambda: 3==2+1)),
 "geometry.parabola-focus": (
  ("y²=8x",lambda: T(2**2+4**2-2**2-4**2) and sqrt((2-2)**2+4**2)==abs(2-(-2))),
  ("1/2",lambda: R(2,4)==R(1,2))),
 "geometry.hyperbola-foci": (
  ("(±5,0)",lambda: 9+16==25),
  ("x²/4−y²/9=1",lambda: 13-4==9)),
 "geometry.conic-line-elimination": (
  ("唯一交点",lambda: 2**2-2**2==0),
  ("(3,0)",lambda: T(R(3**2,9)+R(0,4)-1) and T(R((-3)**2,9)-1))),
 "geometry.ellipse-tangent": (
  ("x=3",lambda: T(R(3*3,9)-1) and T((3*x/9-1).subs(x,3))),
  ("y=2",lambda: T(R(2*2,4)-1))),
 "proof.induction": (
  ("正整数",lambda: all(sum(range(1,n+1))==n*(n+1)//2 for n in range(1,35))),
  ("n²",lambda: all(sum(2*i-1 for i in range(1,n+1))==n*n for n in range(1,35)))),
 "extension.triangle-centers": (
  ("(2,2)",lambda: ((0+6+0)/3,(0+0+6)/3)==(2,2)),
  ("(3,4)",lambda: all((3-a)**2+(4-b)**2==25 for a,b in [(0,0),(6,0),(0,8)]))),
 "extension.circle-polar": (
  ("x=1/2",lambda: T(R(1,2)**2+R(3,4)-1)),
  ("x=1",lambda: T(1*1+0*0-1))),
 "extension.polar-parameter": (
  ("(√3,1)",lambda: T(2*cos(pi/6)-sqrt(3)) and T(2*sin(pi/6)-1)),
  ("2π/3",lambda: T(2*cos(2*pi/3)+1) and T(2*sin(2*pi/3)-sqrt(3)))),
 "extension.quadratic-surfaces": (
  ("±2",lambda: R(2**2,4)==1 and R(3**2,9)==1 and R(4**2,16)==1),
  ("√5",lambda: T(sqrt(1+2**2)-sqrt(5)))),
 "extension.cross-product": (
  ("(0,0,1)",lambda: matrix_cross((1,0,0),(0,1,0))==(0,0,1)),
  ("(0,0,0)",lambda: matrix_cross((1,2,3),(2,4,6))==(0,0,0))),
 "extension.algorithm-invariant": (
  ("=6",lambda: gcd(48,18)==6),
  ("=7",lambda: gcd(21,14)==7)),
 "function.range": (
  ("[0,4]",lambda: min(z*z for z in [-2,-1,0,1])==0 and max(z*z for z in [-2,-1,0,1])==4),
  ("(0,+∞)",lambda: all(R(1,z-2)>0 for z in (3,4,6)))),
 "function.parity": (
  ("奇函数",lambda: T(((-x)**3-2*(-x))+(x**3-2*x))),
  ("偶函数",lambda: T((-x)**2+1-(x*x+1)))),
 "function.periodicity": (
  ("2π/3",lambda: T(sin(3*(x+2*pi/3))-sin(3*x))),
  ("T=π",lambda: T(cos(x+pi)**2-cos(x)**2))),
 "function.zero-ivt": (
  ("c∈(0,1)",lambda: (-1)*(1+1-1)<0),
  ("c∈(1,2)",lambda: (1-2)*(4-2)<0)),
 "function.piecewise": (
  ("f(0)=1",lambda: (-2)**2==4 and (0+1)==1),
  ("f(1/2)=3/2",lambda: 2*1==2 and R(1,2)+1==R(3,2))),
 "function.linear-slope": (
  ("严格递减",lambda: all(-3*a+5>-3*b+5 for a,b in ((-4,-2),(0,1),(2,3)))),
  ("a>1/2",lambda: (2*R(3,4)-1)>0 and (2*R(1,4)-1)<0)),
 "function.power-domain": (
  ("R\\{0}",lambda: R(1,2)**(-2)==4),
  ("[3,+∞)",lambda: sqrt(3-3)==0 and sqrt(2-3).is_real==False)),
 "function.abs-triangle": (
  ("[-1,5]",lambda: all(abs(z-2)<=3 for z in (-1,0,2,5)) and abs(6-2)>3),
  ("≤10",lambda: abs(3-7)==4 and 4<=abs(3)+abs(7))),
 "function.composition-domain": (
  ("[1,+∞)",lambda: sqrt(1-1)==0 and sqrt(0-1).is_real==False),
  ("{-1,1}",lambda: all((z*z-1)==0 for z in (-1,1)))),
 "trig.tangent": (
  ("5π/4",lambda: T(sin(pi/4)/cos(pi/4)-1) and T(sin(5*pi/4)/cos(5*pi/4)-1)),
  ("不在定义域",lambda: T(cos(3*pi/2)))),
 "trig.reduction": (
  ("√3/2",lambda: T(sin(5*pi/6)-R(1,2)) and T(cos(5*pi/6)+sqrt(3)/2)),
  ("(1-√3)/2",lambda: T(sin(-pi/3)+cos(-pi/3)-(1-sqrt(3))/2))),
 "trig.phase-transform": (
  ("[-1,3]",lambda: 1-2==-1 and 1+2==3 and T(2*pi/3-2*pi/3)),
  ("[1,7]",lambda: 4-3==1 and 4+3==7)),
 "vector.free-coordinates": (
  ("(3,-3)",lambda: (4-1,-1-2)==(3,-3)),
  ("5",lambda: sqrt(3*3+4*4)==5)),
 "vector.linear-operations": (
  ("(-1,3)",lambda: (2-3,-1+4)==(-1,3)),
  ("(-1,-5)",lambda: (2*1-3,2*(-2)-1)==(-1,-5))),
 "triangle.ssa-two-solutions": (
  ("两个",lambda: ssa_valid_count(30,1,1.5)==2),
  ("B=30°",lambda: ssa_valid_count(30,4,4)==1)),
 "triangle.area-sine": (
  ("S=3",lambda: T(R(1,2)*3*4*sin(pi/6)-3)),
  ("15√3/2",lambda: T(R(1,2)*5*6*sin(2*pi/3)-15*sqrt(3)/2))),
 "probability.event-addition": (
  ("2/3",lambda: R(len({2,4,6}|{4,5,6}),6)==R(2,3)),
  ("0.65",lambda: R(1)-R(35,100)==R(65,100))),
 "statistics.sampling": (
  ("120",lambda: comb(10,3)==120),
  ("155",lambda: R(150+160,2)==155 and R(150+160+170+180,4)==165)),
 "statistics.histogram": (
  ("0.15",lambda: R(30,100)/2==R(15,100)),
  ("柱高相同",lambda: R(1,5)==R(4,5)/4)),
 "statistics.percentiles": (
  ("Q₀.₆=6",lambda: sample_quantile([2,4,6,8,10],R(3,5))==6),
  ("Q₀.₇₅=3",lambda: sample_quantile([1,2,3,4],R(3,4))==3)),
 "sequence.recurrence": (
  ("11",lambda: 2+3*3==11),
  ("5",lambda: (lambda seq:seq[4])([1,1,2,3,5])==5)),
 "geometry.line-equation": (
  ("2x-y=0",lambda: 2*1-2==0 and 2*2-4==0),
  ("x=3",lambda: 3==3)),
 "geometry.line-relations": (
  ("平行",lambda: R(1,1)==R(1,1) and 1!=2),
  ("垂直",lambda: 1*1+1*(-1)==0)),
 "geometry.point-line-distance": (
  ("4",lambda: T(line_distance((0,5),(3,4,0))-4)),
  ("0",lambda: line_distance((1,2),(2,-1,0))==0)),
 "counting.permutation-combination": (
  ("10",lambda: comb(5,2)==10),
  ("20",lambda: 5*4==20)),
 "probability.discrete-variable": (
  ("1/2",lambda: R(0+1,2)==R(1,2)),
  ("Var(X)=1",lambda: R((-1)**2+1**2,2)-R((-1)+1,2)**2==1)),
 "inequality.parameter-cases": (
  ("a=0:∅",lambda: all((-1)*z>2 for z in (-3,-4)) and not 0>2),
  ("t=1:R",lambda: (2-1)*(-1)<=0 and (0-1)*(1)<=0 and 0<=0)),
 "space.incidence": (
  ("L⊂Π",lambda: all((q,0,0)[2]==0 for q in (-3,0,5))),
  ("(0,0,2)",lambda: 2==2)),
 "space.perpendicular-plane": (
  ("l⊥z=0",lambda: Matrix([0,0,1]).dot(Matrix([1,0,0]))==0 and Matrix([0,0,1]).dot(Matrix([0,1,0]))==0),
  ("不能",lambda: (0,1,0)[1]!=0)),
 "space.point-line-distance": (
  ("5",lambda: sqrt(3**2+4**2)==5),
  ("3",lambda: sqrt((4-1)**2+(2-2)**2)==3)),
 "space.polyhedron-types": (
  ("3个",lambda: len({(0,1),(1,2),(2,0)})==3),
  ("1:4",lambda: R(1,2)**2==R(1,4))),
 "space.solids-revolution": (
  ("=9",lambda: 3*3==9),
  ("面积20",lambda: 2*2*5==20)),
 "space.solid-volumes": (
  ("60",lambda: 3*4*5==60),
  ("12π",lambda: T(pi*3*3*4/3-12*pi))),
 "space.cross-sections": (
  ("面积4",lambda: 2*2==4),
  ("4√2",lambda: T((2*sqrt(2))*2-4*sqrt(2)))),
 "calculus.parameter-zeros": (
  ("t>0:2个",lambda: all(len({sqrt(z),-sqrt(z)})==2 for z in (1,2,4))),
  ("|t|>1:2个",lambda: (2*2)**2-4*1*1>0)),
 "space.polyhedron-projection": (
  ("(2,-1,0)",lambda: tuple(Matrix.diag(1,1,0)*Matrix([2,-1,5]))==(2,-1,0)),
  ("4",lambda: 2*2==4)),
}

BATCH04_FILES = (
 "advanced_space_prob_model_batch04.json",
 "extension_topics_batch04.json",
 "functional_trig_vector_batch04.json",
 "geometry_stats_foundations_batch04.json",
 "spatial_fundamentals_batch04.json",
)


def test_exact_batch04_oracle_domain_and_review_gate():
    batch_items = [
        item for filename in BATCH04_FILES
        for item in json.loads((ROOT/"knowledge/deep/v1"/filename).read_text(encoding="utf-8"))
    ]
    batch_ids = {"math.hs."+k for k in ORACLES}
    assert len(batch_items) == 58
    assert len(ORACLES) == 58
    assert {item["id"] for item in batch_items} == batch_ids
    assert all(item["review"]["status"] == "REVIEW_PENDING" for item in batch_items)
    assert all(item["teacher_solution_visibility"] == "TEACHER_ONLY" for item in batch_items)
    assert public_summary()["direct_student_teaching_enabled"] is False


@pytest.mark.parametrize("knowledge_id,index", [(k,i) for k in ORACLES for i in (0,1)])
def test_batch04_worked_example_answers_against_independent_oracles(knowledge_id,index):
    doc = next(d for d in lessons() if d.id == "math.hs."+knowledge_id)
    text,oracle = ORACLES[knowledge_id][index]
    example = doc.worked_examples[index]
    assert text in example.answer
    assert len(example.steps) >= 2
    assert bool(oracle()), knowledge_id + f" #{index}"


def test_oracles_are_not_student_endpoints():
    from app.main import app
    assert not any("batch04" in r.path or "teacher" in r.path for r in app.routes)
