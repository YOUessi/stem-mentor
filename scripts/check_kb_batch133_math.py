#!/usr/bin/env python3
"""Batch133: 12 independent exact worked-example witnesses + 6 negative-boundary checks.

These prove the selected finite instances ONLY. They do not certify arbitrary theorems,
free-form student reasoning or the original syllabuses' semantic interpretations.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from sympy import Abs, EmptySet, Integer, Rational, S, Symbol, diff, limit, simplify, solveset, sqrt
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch133_atomization as atoms
import build_kb_batch133_lessons as lessons
OUT=ROOT/"docs/evaluation/KB_BATCH133_EXACT_MATH_WITNESSES.json"
def cases():
    x=Symbol("x",real=True)
    U=set(range(1,7)); A={2,4,6}
    U2={1,2,3,4}; A2={2,3}; B2={1,2}
    q=Integer(2); first=Integer(3)
    f=x**3-x-1;g=x**2-2
    c_cubic=2/sqrt(3)
    result=[
      ("c_complement_example1",U-A=={1,3,5}),
      ("c_complement_example2",U2-(A2|B2)=={4}),
      ("c_quantifier_negation_example1",Integer(0)**2<=0),
      ("c_quantifier_negation_example2",solveset(x**2+1,x,domain=S.Reals)==EmptySet),
      ("c_quadratic_roots_example1",solveset(2*x*x-3*x-2,x,domain=S.Reals)=={Integer(2),-Rational(1,2)}),
      ("c_quadratic_roots_example2",solveset(x*x-4*x+4,x,domain=S.Reals)=={Integer(2)}),
      ("c_zero_theorem_example1",f.subs(x,1)==-1 and f.subs(x,2)==5),
      ("c_zero_theorem_example2",g.subs(x,Rational(3,2))==Rational(1,4) and g.subs(x,Rational(5,4))==-Rational(7,16)),
      ("sc_geom_progression_example1",sum(first*q**i for i in range(4))==45),
      ("sc_geom_progression_example2",sum(Integer(5) for i in range(6))==30),
      ("a_mean_value_example1",simplify(diff(x*x,x).subs(x,2)-((Integer(3)**2-1)/(3-1)))==0),
      ("a_mean_value_example2",simplify(diff(x**3,x).subs(x,c_cubic)-4)==0 and bool(c_cubic>0) and bool(c_cubic<2)),
      ("neg_complement_universe",({1,2,3}-{1}) != (set(range(1,8))-{1})),
      ("neg_quantifier_all_fail_wrong",not all(z*z<=0 for z in [-2,-1,0,1,2])),
      ("neg_quadratic_degree_zero",solveset(2*x-4,x,domain=S.Reals)=={Integer(2)}),
      ("neg_ivt_discontinuous",all((-1 if z<0 else 1)!=0 for z in [Rational(i,8) for i in range(-8,9)])),
      ("neg_geometric_quotient_zero",simplify(1-S(1))==0),
      ("neg_mvt_absolute_value",limit(Abs(x)/x,x,0,dir="-")==-1 and limit(Abs(x)/x,x,0,dir="+")==1)
    ]
    return [{"id":n,"outcome":"EXACT_FINITE_WITNESS_PASS" if ok else "FAIL",
             "scope":"FINITE_SYMPY_EXACT_INSTANCE_NOT_GENERAL_THEOREM"} for n,ok in result]
def audit(data):
    expected={r["id"] for r in cases()}
    if not isinstance(data,dict) or data.get("batch")!=133 or data.get("source_scope")!="TEACHER_EXAMPLE_EXACT_ORACLES_ONLY":
        raise ValueError("bad oracle provenance")
    cs=data.get("cases",[])
    if len(cs)!=18 or {r["id"] for r in cs}!=expected or any(r["outcome"]!="EXACT_FINITE_WITNESS_PASS" for r in cs):
        raise ValueError("math oracle wrong or altered")
    if data.get("full_theorem_certified") is not False or data.get("teacher_approved")!=0 or data.get("student_free_steps_verified") is not False:
        raise ValueError("forged math review status")
    return True
def main():
    parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    a=parser.parse_args()
    atoms.validate(json.loads(atoms.OUT.read_text()))
    lessons.validate(json.loads(lessons.OUT.read_text()))
    new=dict(batch=133,source_scope="TEACHER_EXAMPLE_EXACT_ORACLES_ONLY",
             full_theorem_certified=False,teacher_approved=0,
             student_free_steps_verified=False,cases=cases())
    audit(new)
    if a.write:OUT.write_text(atoms.stable_json(new),encoding="utf-8")
    else:
        old=json.loads(OUT.read_text());audit(old)
        if old!=new:raise ValueError("oracle outputs differ from reexecuted SymPy check")
    print("PASS exact",len(new["cases"]),"finite checks; general theorem approval=0")
if __name__=="__main__":main()
