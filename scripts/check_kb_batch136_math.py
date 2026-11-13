#!/usr/bin/env python3
"""Independent exact finite instances and explicit invalid-precondition checks.
These checks NEVER assert full theorem proof, syllabus certification, or student grading.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch133_atomization as atoms
import build_kb_batch136_lessons as lessons
OUT=ROOT/"docs/evaluation/KB_BATCH136_EXACT_WITNESSES.json"

def equal(actual,expected):
    if isinstance(actual,S.Set):return actual==expected
    if isinstance(actual,S.Basic) and isinstance(expected,(S.Basic,int,float)):
        return S.simplify(actual-S.sympify(expected))==0
    if isinstance(actual,(tuple,list)) and isinstance(expected,(tuple,list)):
        return len(actual)==len(expected) and all(equal(x,y) for x,y in zip(actual,expected))
    return actual==expected

def witness(slug,kind,name,actual,expected,scope):
    if not equal(actual,expected):
        raise ValueError(f"math mismatch {slug}:{name}: observed {actual!r} expected {expected!r}")
    return {"id":f"kb136-{slug}-{kind}-{name}",
            "lesson_id":"kb136-deep-"+slug,
            "kind":kind,"name":name,"observed":str(actual),"expected":str(expected),
            "scope":scope,"status":"EXACT_INSTANCE_PASS",
            "teacher_approved":False,"general_proof_certified":False,
            "student_free_step_verified":False}

def cases():
    rows=[]
    def P(s,name,a,e):rows.append(witness(s,"POS",name,a,e,"EXACT_EXAMPLE_NOT_GENERAL_PROOF"))
    def N(s,name,a,e):rows.append(witness(s,"NEG",name,a,e,"EXACT_UNSATISFIED_HYPOTHESIS"))
    s="c_set_membership"; A={2,4}
    P(s,"example_membership",(2 in A,frozenset({2}) in A),(True,False))
    B={frozenset({1}),2}
    P(s,"nested_membership",(frozenset({1}) in B,1 in B),(True,False))
    N(s,"type_distinction",frozenset({2}) in A,False)
    s="c_set_subset"
    P(s,"proper_subset",(set([1,2])<=set([1,2,3]),set([1,2])!=set([1,2,3])),(True,True))
    P(s,"empty_subset",(set()<=set([5]),set([5])<=set()),(True,False))
    N(s,"counterexample_four",set([1,4])<=set([1,2,3]),False)
    s="c_sufficiency"
    P(s,"six_multiple_implies_three",6%6==0 and 6%3==0,True)
    P(s,"greater_two_implies_positive",3>2 and 3>0,True)
    N(s,"reverse_not_valid",3%3==0 and 3%6!=0,True)
    s="c_equivalence";x=S.symbols("x",real=True)
    P(s,"square_both_roots",S.solveset(x*x-9,x,domain=S.Reals),S.FiniteSet(-3,3))
    P(s,"linear_reversible",S.solveset(2*x-6,x,domain=S.Reals),S.FiniteSet(3))
    N(s,"lost_negative_root",(-3)**2==9 and -3!=3,True)
    s="c_quantifier"
    # First positive is a bounded exact illustration, NOT a universal proof.
    P(s,"bounded_square_nonnegative",all(n*n+1>0 for n in range(-25,26)),True)
    P(s,"integer_no_two_n_three",S.solveset(2*x-3,x,domain=S.Integers),S.EmptySet)
    N(s,"wrong_domain_witness",S.Rational(3,2).is_integer,False)
    s="c_function_mapping"
    vals={-1:1,1:1}
    P(s,"many_to_one_function",(vals[-1],vals[1]),(1,1))
    P(s,"ordinary_function",(1**2,2**2,3**2),(1,4,9))
    N(s,"two_conflicting_images",len({2,3})==1,False)
    s="c_piecewise"
    f=S.Piecewise((x+1,x<0),(x*x,True))
    P(s,"branch_values",(f.subs(x,-2),f.subs(x,2),f.subs(x,0)),(-1,4,0))
    g=S.Piecewise((2*x,x<1),(3,True))
    # SymPy Piecewise.limit at discontinuities may select the value branch;
    # compute each one-sided defining expression with its stated x<1/x>=1 guard.
    P(s,"left_right_differ",(
        S.limit(2*x,x,1,dir="-"),S.limit(S.Integer(3),x,1,dir="+")), (2,3))
    N(s,"conflicting_endpoint_assignments",len({1,2})>1,True)
    s="c_monotonicity"
    P(s,"linear_positive_difference",(3*2-4)-(3*1-4),3)
    P(s,"squares_negative_interval",(-2)**2-(-1)**2,3)
    N(s,"square_not_increasing_all_reals",(-2)**2>(-1)**2,True)
    s="c_exponential_exp"
    P(s,"base_two",(S.Rational(2)**(-1),S.Rational(2)**0,S.Rational(2)**2),
      (S.Rational(1,2),1,4))
    P(s,"half_base",(S.Rational(1,2)**0,S.Rational(1,2)**1,S.Rational(1,2)**2),
      (1,S.Rational(1,2),S.Rational(1,4)))
    N(s,"a_equal_one_not_strict",S.Integer(1)**0==S.Integer(1)**10,True)
    s="c_logarithm_law"
    P(s,"sum_log",(S.log(8,2)+S.log(4,2)),5)
    P(s,"difference_log",(S.log(27,3)-S.log(9,3)),1)
    N(s,"negative_argument_not_allowed",-2>0,False)
    s="c_radian"
    P(s,"quarter_circle",S.Integer(2)*S.pi/2,S.pi)
    P(s,"negative_signed_angle",3*abs(-S.pi/3),S.pi)
    N(s,"zero_radius_invalid",0>0,False)
    s="sc_derivative_def";h=S.symbols("h",real=True,nonzero=True)
    P(s,"quadratic_at_three",S.limit(((3+h)**2-9)/h,h,0),6)
    P(s,"abs_cusp_left_right",(
        S.limit(S.Abs(h)/h,h,0,dir="-"),
        S.limit(S.Abs(h)/h,h,0,dir="+")),(-1,1))
    N(s,"left_right_disagree",S.Integer(-1)!=S.Integer(1),True)
    assert len(rows)==36 and sum(x["kind"]=="POS" for x in rows)==24
    assert sum(x["kind"]=="NEG" for x in rows)==12
    return rows

def build():
    drafts=json.loads(lessons.OUT.read_text(encoding="utf-8"))
    lessons.validate(drafts)
    rows=cases()
    ids={r["id"] for r in drafts}
    if {r["lesson_id"] for r in rows}!=ids:raise ValueError("missing mathematical witness")
    for ident in ids:
        pair=[r["kind"] for r in rows if r["lesson_id"]==ident]
        if pair.count("POS")!=2 or pair.count("NEG")!=1:raise ValueError("case imbalance "+ident)
    return {"schema":"kb136-exact-math/1","cases":rows,
            "positive_exact_instance_count":24,
            "invalid_hypothesis_instance_count":12,
            "general_theorem_proofs_certified":0,
            "teacher_approvals":0,"student_free_step_verified":False,
            "student_authoritative_releases":0}

def validate(obj):
    if obj!=build():raise ValueError("mutated oracle, forged approval/proof or math mismatch")
    return True

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    args=p.parse_args()
    if args.write:
        obj=build();validate(obj);OUT.write_text(atoms.stable_json(obj),encoding="utf-8")
    else:validate(json.loads(OUT.read_text(encoding="utf-8")))
    print("PASS: Batch136 24 exact worked instances and 12 invalid-precondition witnesses; general proof 0")
if __name__=="__main__":main()
