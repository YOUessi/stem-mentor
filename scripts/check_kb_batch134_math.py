#!/usr/bin/env python3
"""24 reproducible *finite* exact witnesses for Batch134's eight teacher-only lessons.

No result certifies a general theorem or any student's free-form answer.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch134_lessons as lessons
import build_kb_batch133_atomization as atoms
OUT=ROOT/"docs/evaluation/KB_BATCH134_EXACT_FINITE_WITNESSES.json"
def witness(slug,kind,label,actual,expected):
    assert S.simplify(actual-expected)==0,(slug,label,actual,expected)
    return dict(id="kb134-"+slug+"-"+kind+"-"+label,lesson_id="kb134-deep-"+slug,
       scope="EXACT_FINITE_INSTANCE_NOT_GENERAL_THEOREM",kind=kind,
       actual=str(actual),expected=str(expected),status="EXACT_PASS",teacher_approval=False)
def cases():
    x=S.symbols("x",real=True);n=S.symbols("n",integer=True,positive=True)
    # The oracle is calculated independently of prose and lesson answer strings.
    w=[]
    def add(slug,kind,label,actual,expected):w.append(witness(slug,kind,label,actual,expected))
    slug="c_inequality_product"
    add(slug,"POS","mean_4_9",S.Rational(4+9,2)-S.sqrt(4*9),S.Rational(1,2))
    add(slug,"POS","fixed_sum_equal",S.Integer(5)*5,25)
    add(slug,"NEG","negative_pair",S.Rational(-1-4,2)-S.sqrt((-1)*(-4)),S.Rational(-9,2))
    slug="c_parity"
    add(slug,"POS","even_square",(-S.Integer(2))**2-S.Integer(2)**2,0)
    add(slug,"POS","odd_cube",(-S.Integer(2))**3+S.Integer(2)**3,0)
    add(slug,"NEG","nonsymmetric_domain",S.Integer(1) if S.Rational(-1,2) not in S.Interval.open(0,1) else 0,1)
    slug="c_log_inverse"
    add(slug,"POS","log8",S.log(8,2),3)
    add(slug,"POS","logquarter",S.log(S.Rational(1,4),2),-2)
    add(slug,"NEG","base_one_noninjective",S.Integer(1)**0-S.Integer(1)**2,0)
    slug="c_cosine_difference"
    add(slug,"POS","pi_six",S.cos(S.pi/3-S.pi/6),S.sqrt(3)/2)
    add(slug,"POS","pi_half",S.cos(S.pi/4+S.pi/4),0)
    add(slug,"NEG","not_linear",S.cos(0)-(S.cos(S.pi/3)-S.cos(S.pi/3)),1)
    slug="sc_derivative_monotone"
    add(slug,"POS","cube_order",S.Integer(2)**3-(-S.Integer(1))**3,9)
    add(slug,"POS","square_interval",S.Integer(2)**2-S.Integer(0)**2,4)
    add(slug,"NEG","one_point_zero",S.diff(-x**3,x).subs(x,0),0)
    slug="sc_space_distance"
    add(slug,"POS","345",S.sqrt(3**2+4**2+0**2),5)
    add(slug,"POS","3412",S.sqrt(3**2+4**2+12**2),13)
    add(slug,"NEG","skew_metric",S.sqrt(2**2+1**2)-S.sqrt(1**2+1**2),S.sqrt(5)-S.sqrt(2))
    slug="a_sequence_limit"
    add(slug,"POS","one_over_n",S.limit(1/n,n,S.oo),0)
    add(slug,"POS","two_plus_ninv",S.limit((2*n+1)/n,n,S.oo),2)
    add(slug,"NEG","oscillation",S.Integer(-1)**2-S.Integer(-1)**3,2)
    slug="a_integral_area"
    add(slug,"POS","signed_vs_area",S.integrate(S.Abs(x),(x,-1,1)),1)
    add(slug,"POS","shifted_area",S.integrate(S.Abs(x-1),(x,0,2)),1)
    add(slug,"NEG","signed_cancellation",S.integrate(x,(x,-1,1)),0)
    assert len(w)==24 and sum(z["kind"]=="POS" for z in w)==16 and sum(z["kind"]=="NEG" for z in w)==8
    return w
def build():
    r=json.loads(lessons.OUT.read_text(encoding="utf-8"));lessons.validate(r)
    return dict(schema="kb134-math/1",finite_positive_cases=16,finite_negative_cases=8,
       theorem_general_proof_certified=False,student_free_text_verified=False,
       teacher_approved_count=0,student_authoritative_count=0,cases=cases())
def validate(x):
    if x!=build():raise ValueError("altered exact finite math evidence or false claim")
    return True
def main():
    p=argparse.ArgumentParser();p.add_argument("--write",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args()
    if a.write==a.check: raise ValueError("choose --write or --check")
    if a.write:
        d=build();validate(d);OUT.write_text(atoms.stable_json(d),encoding="utf-8")
    else:validate(json.loads(OUT.read_text()))
    print("PASS 16 positive + 8 negative exact finite SymPy witnesses; 0 general proofs")
if __name__=="__main__":main()
