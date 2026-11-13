#!/usr/bin/env python3
"""Independent exact finite checks for seven Batch137 teacher-only manuscripts.
No finite check certifies a theorem over all real inputs or student free text.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch133_atomization as atoms
import build_kb_batch137_lessons as authored
OUT=ROOT/"docs/evaluation/KB_BATCH137_EXACT_WITNESSES.json"
def equal(a,b):
    if a is S.oo and b is S.oo:return True
    if isinstance(a, (S.MatrixBase, S.Set)):
        return a==b
    if isinstance(a, (tuple,list)) and isinstance(b,(tuple,list)):
        return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    if isinstance(a,(S.Basic,int,float)) and isinstance(b,(S.Basic,int,float)):
        try:return S.simplify(S.sympify(a)-S.sympify(b))==0
        except (TypeError,ValueError):return a==b
    return a==b
def record(slug,kind,label,got,expected):
    if not equal(got,expected):
        raise ValueError(f"math failed {slug}/{label}: {got!r} != {expected!r}")
    return dict(id=f"kb137-{slug}-{kind}-{label}",lesson_id=f"kb137-deep-{slug}",
                kind=kind,name=label,observed=str(got),expected=str(expected),
                verification_scope="EXACT_FINITE_EXAMPLE_ONLY" if kind=="POS" else "EXACT_INVALID_PRECONDITION",
                status="EXACT_INSTANCE_PASS",teacher_approved=False,formal_proof_certified=False,
                student_free_step_verified=False)
def cases():
    out=[]
    def P(s,n,x,y):out.append(record(s,"POS",n,x,y))
    def N(s,n,x,y):out.append(record(s,"NEG",n,x,y))
    s="sc_sequence_model"
    a=[4]
    for _ in range(3):a.append(a[-1]+3)
    P(s,"recurrence_four_terms",tuple(a),(4,7,10,13))
    P(s,"explicit_three_terms",tuple(n*(n+1) for n in (1,2,3)),(2,6,12))
    N(s,"recurrence_without_initial_nonunique",(1+2,4+2),(3,6))
    s="sc_induction_optional";k=S.symbols("k",integer=True,positive=True)
    P(s,"sum_natural_induction_bridge",S.simplify(k*(k+1)/2+(k+1)-(k+1)*(k+2)/2),0)
    P(s,"sum_even_induction_bridge",S.simplify(k*(k+1)+2*(k+1)-(k+1)*(k+2)),0)
    N(s,"base_case_missing",1>=2,False)
    s="sc_derivative_rules";x=S.symbols("x",real=True)
    P(s,"product_rule_example",S.diff(x*x*(x+1),x),3*x*x+2*x)
    q=(x*x+1)/(x+1)
    P(s,"quotient_rule_example",S.simplify(S.diff(q,x)-(x*x+2*x-1)/(x+1)**2),0)
    N(s,"quotient_denominator_zero",(x+1).subs(x,-1)!=0,False)
    s="sc_space_basis"
    e1=S.Matrix([1,0,0]);e2=S.Matrix([0,1,0]);e3=S.Matrix([0,0,1])
    M=S.Matrix.hstack(e1,e2,e3)
    P(s,"standard_basis",M.inv()*S.Matrix([2,-1,3]),S.Matrix([2,-1,3]))
    M=S.diag(1,2,3)
    P(s,"scaled_basis",M.inv()*S.Matrix([1,4,6]),S.Matrix([1,2,2]))
    dependent=S.Matrix([[1,0,1],[0,1,1],[0,0,0]])
    N(s,"coplanar_rank_deficiency",(dependent.rank(),dependent.det()),(2,0))
    s="a_monotone_convergence";n=S.symbols("n",positive=True,integer=True)
    P(s,"increasing_limit",S.limit(1-1/n,n,S.oo),1)
    P(s,"decreasing_limit",S.limit(1/(n+1),n,S.oo),0)
    N(s,"unbounded_example",S.limit(n,n,S.oo),S.oo)
    s="a_function_limit"
    P(s,"linear_at_two",S.limit(3*x-1,x,2),5)
    P(s,"square_at_zero",S.limit(x*x,x,0),0)
    N(s,"sign_discontinuous",(
        S.limit(x/S.Abs(x),x,0,dir="-"),S.limit(x/S.Abs(x),x,0,dir="+")),(-1,1))
    s="a_continuity"
    P(s,"quadratic_at_one",(S.limit(x*x,x,1),1**2),(1,1))
    P(s,"removable_discontinuity",S.limit(x,x,0),0)
    N(s,"assigned_bad_value",(S.limit(x,x,0),2),(0,2))
    assert len(out)==21
    return out
def build():
    manuscripts=json.loads(authored.OUT.read_text(encoding="utf-8"))
    authored.validate(manuscripts)
    checks=cases()
    if {r["lesson_id"] for r in checks}!={r["id"] for r in manuscripts}:
        raise ValueError("math coverage missing")
    for lesson in manuscripts:
        matched=[r["kind"] for r in checks if r["lesson_id"]==lesson["id"]]
        if matched.count("POS")!=2 or matched.count("NEG")!=1:
            raise ValueError("exact witness imbalance "+lesson["id"])
    return dict(schema="kb137-exact-cases/1",cases=checks,
                positive_exact_instance_count=14,invalid_hypothesis_instance_count=7,
                general_theorem_proofs_certified=0,teacher_approvals=0,
                student_free_step_verified=False,student_authoritative_releases=0)
def validate(obj):
    if obj!=build():raise ValueError("oracle tampered or status forged")
    return True
def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    z=p.parse_args()
    if z.write:
        d=build();validate(d);OUT.write_text(atoms.stable_json(d),encoding="utf-8")
    else:validate(json.loads(OUT.read_text(encoding="utf-8")))
    print("PASS 21 independent exact finite cases; no general theorem certification")
if __name__=="__main__":main()
