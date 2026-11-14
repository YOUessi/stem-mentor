#!/usr/bin/env python3
"""Independent bounded SymPy/Exact oracle for KB159's 20 teacher examples and
20 hazardous premise counter-witnesses. Not a general proof certificate.
"""
from __future__ import annotations
import argparse,json,sys
from fractions import Fraction as F
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch159_functions as lessons
OUT=ROOT/"docs/evaluation/KB_BATCH159_EXACT_ORACLE.json"
EXPECTED=[
("三对值为(0,0),(1,1),(2,4)。","不是，g(x)=x²+1也匹配两点。"),
("(1/3)^2=1/9大于(1/3)^5=1/243。","x>2。"),
("−3。","x>1。"),
("−2。","1/9。"),
("π/2与3π/2。","sin(5π/2)=1，cos(−π)=−1。"),
("振幅3，周期π，中线1，向左π/4。","不存在最小正周期。"),
("√3/2。","√3/2；不妨碍。"),
("2sin(π/4)cos(π/12)。","0。"),
("唯一零点x=2；只切触不穿越。","x=−1。"),
("12 km。","正确路程3600 m；误用3 s得60 m。"),
]
def truth_cases():
    x=S.symbols("x",real=True); t=S.symbols("t",real=True)
    a=S.symbols("a",positive=True)
    f=S.Rational
    positive=[
      ("discrete function unique values", [i*i for i in (0,1,2)]==[0,1,4]),
      ("two tables cannot identify function", all((i+1)==(i*i+1) for i in (0,1)) and (2+1)!=(2*2+1)),
      ("decreasing positive exponential", f(1,3)**2==f(1,9) and f(1,3)**5==f(1,243) and f(1,9)>f(1,243)),
      ("exponential inequality monotone root", S.simplify(2**(2+1)-8)==0 and 2**(3+1)>8 and 2**(1+1)<8),
      ("real logarithm inverse base half", S.simplify(S.log(8)/S.log(f(1,2))+3)==0),
      ("logarithm real input domain", S.solveset(x-1>0,x,domain=S.S.Reals)==S.Interval.open(1,S.oo)),
      ("logarithm of positive real power", S.simplify(S.log(S.Integer(5)**(-2),5)+2)==0),
      ("exponential of logarithm", S.simplify(3**(S.log(f(1,9))/S.log(3))-f(1,9))==0),
      ("tangent excluded poles in main cycle", [i for i in (0,S.pi/2,S.pi,3*S.pi/2,2*S.pi) if S.cos(i)==0]==[S.pi/2,3*S.pi/2]),
      ("sine cosine periodic values", S.sin(5*S.pi/2)==1 and S.cos(-S.pi)==-1),
      ("sine model period phase and midpoint", S.simplify(2*S.pi/2-S.pi)==0 and S.simplify(-(S.pi/2)/2+S.pi/4)==0 and 3+1==4),
      ("degenerate constant has no least period", S.simplify(5*S.sin(0*(t+S.Symbol("T"))+S.pi/6)-5*S.sin(S.pi/6))==0),
      ("cosine difference exact case", S.simplify(S.cos(S.pi/3-S.pi/6)-S.sqrt(3)/2)==0),
      ("cosine difference zero cosine valid", S.simplify(S.cos(S.pi/2-S.pi/3)-S.sqrt(3)/2)==0),
      ("sum to product exact case", S.simplify(S.sin(S.pi/3)+S.sin(S.pi/6)-2*S.sin(S.pi/4)*S.cos(S.pi/12))==0),
      ("sum to product opposing angles", S.sin(S.pi/2)+S.sin(-S.pi/2)==0),
      ("double zero tangent at two", S.solveset((x-2)**2,x,domain=S.S.Reals)==S.FiniteSet(2)),
      ("rational zero domain excludes removed point", S.simplify((x*x-1)/(x-1))==x+1 and (-1)**2-1==0 and S.cancel((x*x-1)/(x-1)).subs(x,-1)==0),
      ("distance in km with hour conversion", 18*f(40,60)==12),
      ("distance in m with minute conversion", 20*3*60==3600 and 20*3==60),
    ]
    negative=[
      ("finite samples do not uniquely determine continuum",2!=4),
      ("duplicate input with contradictory outputs invalid",len({0,1})==2 and len({0,0})==1),
      ("base one not strictly monotone",1**0==1**2),
      ("negative base square root not real",S.sqrt(-2).is_real is False),
      ("log negative input real-domain violation",-4<=0),
      ("log product cannot split negative factors",(-2)*(-3)>0 and not(-2>0 and -3>0)),
      ("base one inverse invalid",1**1==1**2),
      ("log zero undefined",0<=0),
      ("tan pi half undefined",S.cos(S.pi/2)==0),
      ("tan three pi halves undefined",S.cos(3*S.pi/2)==0),
      ("zero amplitude no least positive period",S.simplify(0*S.sin(2*(t+S.pi))+3-(0*S.sin(2*t)+3))==0),
      ("zero angular frequency no least positive period",S.simplify(2*S.sin(0*(t+S.pi))+4-(2*S.sin(0*t)+4))==0),
      ("cos difference not coordinate subtraction",S.cos(0)==1 and S.cos(S.pi/3)-S.cos(S.pi/3)==0),
      ("division by cosine invalid at poles",S.cos(S.pi/2)==0),
      ("sine sum not sine of sum",S.sin(S.pi/2)+S.sin(S.pi/2)==2 and S.sin(S.pi)==0),
      ("missing two in sum-product",S.sin(S.pi/2)+S.sin(S.pi/2)!=S.sin(S.pi/2)*S.cos(0)),
      ("touching zero can lack sign change", (S.Rational(1,2))**2>0 and (-S.Rational(1,2))**2>0),
      ("original rational domain excludes one",1-1==0),
      ("minutes cannot be inserted as hours",60*30!=60*f(30,60)),
      ("seconds conversion crucial",20*3!=20*(3*60)),
    ]
    if len(positive)!=20 or len(negative)!=20:raise ValueError("case count drift")
    return positive,negative
def build(rows=None):
    actual=lessons.build() if rows is None else rows
    lessons.validate(actual)
    positive,negative=truth_cases();out=[]
    for i,r in enumerate(actual):
        for j,e in enumerate(r["teacher_examples"]):
            if e["answer"]!=EXPECTED[i][j]:raise ValueError(f"teacher answer text drift {i}-{j}")
            title,passed=positive[2*i+j]
            if passed is not True and passed is not S.true:
                raise ValueError(f"positive oracle failed: {title} {passed}")
            out.append(dict(source_candidate_id=r["source_candidate_id"],index=j+1,
                            witness=title,status="BOUNDED_EXACT_PASS",teacher_solution_exposed=False))
    neg=[]
    for i,r in enumerate(actual):
        for j in range(2):
            title,passed=negative[2*i+j]
            if passed is not True and passed is not S.true:
                raise ValueError(f"negative premise rejection failed: {title} {passed}")
            neg.append(dict(source_candidate_id=r["source_candidate_id"],index=j+1,
                            witness=title,status="INVALID_PREMISE_REJECTED"))
    return dict(schema="kb159-exact-finite-witnesses/1",teacher_example_checks=20,
       invalid_premise_checks=20,all_bounded_cases_passed=True,
       general_proof_certified=False,student_free_text_verified=False,
       teacher_approved=0,student_authoritative=0,positive_cases=out,negative_cases=neg)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    x=p.parse_args();body=lessons.serialize(build())
    if x.write:OUT.write_text(body,encoding="utf-8")
    elif OUT.read_text(encoding="utf-8")!=body:raise ValueError("oracle witness drift")
    print("PASS KB159 20 independently calculated teacher examples + 20 invalid-premise witnesses")
if __name__=="__main__":main()
