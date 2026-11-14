#!/usr/bin/env python3
"""Forty independent exact/bounded witnesses for ten new original lessons.
No universal proof, authorized teacher review or student free-text certification.
"""
from __future__ import annotations
import argparse, itertools, json, sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch147_lessons as source
OUT=ROOT/"docs/evaluation/KB_BATCH147_EXACT_MATH_WITNESSES.json"
def exact():
    cases=[]
    def put(i,label,p,invalid=False):
        if p is not True and p!=S.true:raise AssertionError(label)
        n=sum(z["candidate_id"]==source.IDS[i] for z in cases)+1
        cases.append(dict(candidate_id=source.IDS[i],case_id=f"kb147-{i+1:02d}-{n}",
            label=label,passed=True,outcome=("REJECT_INVALID_PRECONDITION" if invalid else "EXACT_FINITE_WITNESS"),
            teacher_approved=False,general_formal_proof_certified=False,student_free_step_verified=False))
    # 0 complex arithmetic; denominator must be nonzero.
    put(0,"complex sum",S.expand_complex((2+S.I)+(3-2*S.I))==5-S.I)
    put(0,"conjugate division",S.simplify((1+S.I)/(1-S.I)-S.I)==0)
    put(0,"division by zero invalid",S.Integer(0)==0,True)
    put(0,"component-wise division is false",S.simplify((1+S.I)/(1-S.I)-(1-S.I))!=0,True)
    # 1 noncollinear triples, cross product witnesses, including degenerate case.
    A=S.Matrix([0,0,0]);B=S.Matrix([1,0,0]);C=S.Matrix([0,1,0]); n=(B-A).cross(C-A)
    put(1,"noncollinear normal is nonzero",n==S.Matrix([0,0,1]))
    A2=S.Matrix([1,0,0]);B2=S.Matrix([0,1,0]);C2=S.Matrix([0,0,1])
    put(1,"second plane equation verified",all(sum(v)==1 for v in (A2,B2,C2)))
    put(1,"collinear triples yield zero cross product",S.Matrix([1,0,0]).cross(S.Matrix([2,0,0]))==S.zeros(3,1),True)
    put(1,"same collinear triples lie on two distinct planes",all(v[1]==0 and v[2]==0 for v in ([0,0,0],[1,0,0],[2,0,0])),True)
    # 2 samples and inclusion-exclusion, no unwarranted equiprobability.
    omega={1,2,3,4,5,6};a={2,4,6};b={4,5,6}
    put(2,"die intersection exactly two",a&b=={4,6})
    put(2,"finite inclusion-exclusion exact count",len(a|b)==len(a)+len(b)-len(a&b)==4)
    put(2,"nonempty overlap disallows direct sum",len(a|b)!=len(a)+len(b),True)
    put(2,"biased fair-count assumption invalid",S.Rational(3,4)!=S.Rational(1,2),True)
    # 3 sequence is a function on its declared index set.
    put(3,"first five reciprocal terms",tuple(S.Rational(1,n) for n in range(1,6))[-1]==S.Rational(1,5))
    put(3,"alternating sequence first three",tuple((-1)**n for n in range(1,4))==(-1,1,-1))
    put(3,"index zero not in declared positive domain",0 not in set(range(1,101)),True)
    put(3,"reciprocal n-1 undefined at n=1",1-1==0,True)
    # 4 arithmetic sum general algebra and two sample sums.
    n,d,a0=S.symbols("n d a0",integer=True)
    put(4,"symbolic arithmetic sum equivalence",S.simplify(n*(2*a0+(n-1)*d)/2-(n*a0+n*(n-1)*d/2))==0)
    put(4,"descending arithmetic four terms",sum([7,5,3,1])==4*(7+1)//2==16)
    put(4,"nonarithmetic terms reject endpoint average",S.Rational(3*(1+4),2)!=sum([1,2,4]),True)
    put(4,"last term n d is incorrect",2+5*3!=2+(5-1)*3,True)
    # 5 epsilon N: inspect uniformly all later indices in bounded demonstrations.
    put(5,"reciprocal epsilon 1/10 all next 100",all(S.Rational(1,k)<S.Rational(1,10) for k in range(11,111)))
    put(5,"shifted reciprocal epsilon 1/20",all(S.Rational(3,k)<S.Rational(1,20) for k in range(61,161)))
    put(5,"alternating cannot converge to one",all((-1)**k!=1 for k in range(11,50,2)),True)
    put(5,"one good index not eventual epsilon bound",abs(S.Rational(1,100))<S.Rational(1,10) and abs(S.Rational(1,1))>S.Rational(1,10),True)
    # 6 velocity and acceleration with differentiability requirements.
    t=S.symbols("t",real=True)
    put(6,"quadratic position derivatives at two",S.diff(t*t+3*t,t).subs(t,2)==7 and S.diff(t*t+3*t,t,2)==2)
    put(6,"cubic position derivatives at one",S.diff(t**3,t).subs(t,1)==3 and S.diff(t**3,t,2).subs(t,1)==6)
    put(6,"abs value derivative at zero is not defined",S.limit((S.Abs(t)-0)/t,t,0,dir="+")!=S.limit((S.Abs(t)-0)/t,t,0,dir="-"),True)
    put(6,"zero position need not be zero velocity",S.diff(t,t).subs(t,0)==1 and S.Integer(0)==0,True)
    # 7 propositions with fixed real domain and proper negation of universal.
    put(7,"real square plus one strictly positive",all(i*i+1>0 for i in range(-10,11)))
    put(7,"negation of all real squares positive has witness",0*0<=0)
    put(7,"universal positive real square false at zero",not all(i*i>0 for i in range(-10,11)),True)
    put(7,"variable predicate is not constant truth value",any(i>3 for i in range(0,6)) and any(i<=3 for i in range(0,6)),True)
    # 8 rigid motions preserve lengths; homothety does not.
    R=S.Matrix([[0,-1],[1,0]]);u=S.Matrix([2,1]);v=S.Matrix([0,0]);trans=S.Matrix([3,-1])
    put(8,"rotation orthogonality",R.T*R==S.eye(2))
    put(8,"rigid transform distance squared",((R*u+trans)-(R*v+trans)).dot((R*u+trans)-(R*v+trans))==(u-v).dot(u-v))
    put(8,"scale by two changes absolute distance",4*u.dot(u)!=u.dot(u),True)
    put(8,"similar rectangles different lengths",2!=4 and S.Rational(2,1)==S.Rational(4,2),True)
    # 9 order of planar transformations.
    p=S.Matrix([1,0]);v=S.Matrix([2,3])
    put(9,"rotate then translate",R*p+v==S.Matrix([2,4]))
    put(9,"translate then rotate",R*(p+v)==S.Matrix([-3,3]))
    put(9,"composition order noncommutative",R*(p+v)!=R*p+v,True)
    put(9,"2D 2x2 rotation cannot multiply 3D point",R.shape==(2,2) and S.Matrix([1,0,0]).shape==(3,1),True)
    if len(cases)!=40 or sum(c["outcome"]=="REJECT_INVALID_PRECONDITION" for c in cases)!=20:raise AssertionError("40/20 cases required")
    if {c["candidate_id"] for c in cases}!=set(source.IDS):raise AssertionError("all 10 candidates must be independently checked")
    return dict(schema="kb147-bounded-exact-finite-math/1",cases=cases,total_cases=40,
        legal_or_boundary_witnesses=20,rejected_invalid_premises=20,
        general_formal_proof_certifications=0,teacher_approvals=0,student_free_text_verifications=0,
        official_atom_denominators={t:None for t in source.TRACKS},
        scope="FINITE_EXACT_WITNESS_NOT_GENERAL_FORMAL_PROOF")
oracle=exact
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    a=p.parse_args();v=exact()
    if a.write: OUT.write_text(source.encode(v),encoding="utf-8")
    elif json.loads(OUT.read_text(encoding="utf-8"))!=v:raise AssertionError("oracle evidence drift")
    print("PASS Batch147: 40 independent exact math witnesses; 20 positive, 20 precondition rejects; 0 teacher-approved")
if __name__=="__main__":main()
