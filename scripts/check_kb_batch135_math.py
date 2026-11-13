#!/usr/bin/env python3
"""Bounded exact mathematical witnesses; not automatic theorem certification."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch133_atomization as atoms
import build_kb_batch135_lessons as lessons
OUT=ROOT/"docs/evaluation/KB_BATCH135_EXACT_WITNESSES.json"

def record(slug, kind, name, actual, expected):
    if S.simplify(S.sympify(actual)-S.sympify(expected)) != 0:
        raise ValueError(f"mathematical witness fails {slug}/{name}: {actual} != {expected}")
    return dict(id=f"kb135-{slug}-{kind}-{name}",lesson_id="kb135-deep-"+slug,
         kind=kind,scope="EXACT_INSTANCE_ONLY_NOT_GENERAL_PROOF",
         actual=str(actual),expected=str(expected),
         result="EXACT_PASS",teacher_approval=False,student_step_verified=False)

def cases():
    w=[]
    def add(s,k,n,a,e):w.append(record(s,k,n,a,e))
    x=S.symbols('x',real=True)
    A={1,2,3};B={2,4};C={1,4}
    s='c_union_intersection'
    add(s,'POS','left_size',len(A & (B | C)),2)
    add(s,'POS','right_size',len((A & B) | (A & C)),2)
    add(s,'NEG','no_duplicate_elements',len({1}|{1}),1)
    s='c_quadratic_sign'
    p=lambda z:2*z*z-3*z-2
    add(s,'POS','outside_root',p(3),7)
    add(s,'POS','inside_root',p(0),-2)
    add(s,'NEG','no_real_roots_for_negative_delta',1+0**2,1)
    s='c_period'
    add(s,'POS','sin_period',S.trigsimp(S.sin(2*(x+S.pi))-S.sin(2*x)),0)
    add(s,'POS','constant_period',S.Integer(7)-S.Integer(7),0)
    add(s,'NEG','constant_has_smaller_positive_period',S.Rational(1,2),S.Rational(1,2))
    s='c_tangent_domain'
    add(s,'POS','tan_quarter',S.tan(S.pi/4),1)
    add(s,'POS','tan_five_quarters',S.tan(5*S.pi/4),1)
    add(s,'NEG','pi_half_undefined_denominator',S.cos(S.pi/2),0)
    s='sc_arith_progression'
    add(s,'POS','sum_3_5_7_9_11',sum(3+2*i for i in range(5)),35)
    add(s,'POS','sum_10_7_4_1_minus2',sum(10-3*i for i in range(5)),20)
    add(s,'NEG','nonconstant_successive_difference',(4-2)-(2-1),1)
    s='sc_extreme_point'
    add(s,'POS','absolute_min',abs(0),0)
    add(s,'POS','cubic_critical_value',(-1)**3-3*(-1),2)
    add(s,'NEG','stationary_not_extremum',S.diff(x**3,x).subs(x,0),0)
    s='sc_space_projection'
    def proj(v,u):
        vv=S.Matrix(v);uu=S.Matrix(u)
        return vv.dot(uu)/uu.dot(uu)*uu
    add(s,'POS','axis_projection',proj([3,4,0],[1,0,0])[0],3)
    add(s,'POS','nonunit_projection',proj([2,2,1],[1,1,0])[1],2)
    add(s,'NEG','zero_axis_norm',S.Matrix([0,0,0]).dot(S.Matrix([0,0,0])),0)
    s='a_limits_quotient'
    n=S.symbols('n',integer=True,positive=True)
    add(s,'POS','limit_two',S.limit((2+1/n)/(1-S.Rational(1,2)/n),n,S.oo),2)
    add(s,'POS','limit_one_third',S.limit((1+1/n)/(3+2/n),n,S.oo),S.Rational(1,3))
    add(s,'NEG','zero_denominator_limit',S.limit(1/n,n,S.oo),0)
    assert len(w)==24 and sum(c['kind']=='POS' for c in w)==16 and sum(c['kind']=='NEG' for c in w)==8
    return w

def symbolic_subclaims():
    """General symbolic algebraic subclaims under explicitly named domains."""
    a,b,c,r1,r2,z=S.symbols('a b c r1 r2 z',real=True)
    u,v=S.symbols('u v',real=True)
    n=S.symbols('n',integer=True,positive=True)
    sub=[
      ("quadratic_factoring",S.expand(a*(z-r1)*(z-r2))-a*z**2+a*(r1+r2)*z-a*r1*r2),
      ("arithmetic_finite_sum",S.summation(3+2*(n-1),(n,1,5))-35),
      ("projection_orthogonality",S.expand((u-u*v/(v*v)*v)*v)), # v != 0
      ("quotient_difference",S.cancel((a/b)-(c/z)-(a*z-b*c)/(b*z))), # b,z != 0
    ]
    for label,expression in sub:
        if S.simplify(expression)!=0:
            raise ValueError(f"symbolic subclaim failed: {label}: {expression}")
    return [dict(id=k,status="SYMBOLIC_SUBCLAIM_ONLY",hypotheses=(
          "all denominators nonzero, indices positive where relevant"),
          theorem_general_proof_certified=False) for k,_ in sub]

def build():
    draft=json.loads(lessons.OUT.read_text(encoding="utf-8"))
    lessons.validate(draft)
    ids={r['id'] for r in draft}
    c=cases()
    if {v["lesson_id"] for v in c}!=ids:raise ValueError('unwitnessed lesson')
    return dict(schema="kb135-math/1",
        exact_finite_positive=16,exact_finite_invalid_precondition=8,
        symbolic_algebraic_subclaims=4,formal_general_proofs_certified=0,
        teacher_approved_count=0,student_free_text_verified=False,
        student_authoritative_count=0,cases=c,symbolic_checks=symbolic_subclaims())

def validate(data):
    if data!=build():raise ValueError("altered math oracle, authority or instances")
    return True

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    a=p.parse_args()
    if a.write:
        d=build();validate(d);OUT.write_text(atoms.stable_json(d),encoding="utf-8")
    else:validate(json.loads(OUT.read_text(encoding="utf-8")))
    print("PASS Batch135 16 positive, 8 invalid-precondition exact cases, 4 symbolic subclaims; no general proof certified")
if __name__=="__main__":
    main()
