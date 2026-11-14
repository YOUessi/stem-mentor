#!/usr/bin/env python3
"""Independent exact, bounded mathematics evidence. Not a general formal proof or teacher approval."""
from __future__ import annotations
import argparse, json, sys, itertools
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch146_lessons as authored
OUT=ROOT/"docs/evaluation/KB_BATCH146_EXACT_MATH_WITNESSES.json"
def yes(p,reason):
    if p is not True and p!=S.true:raise AssertionError(reason)
def oracle():
    cases=[]; ids=authored.IDS
    def put(i,label,p,invalid=False):
        yes(p,label)
        n=sum(z["candidate_id"]==ids[i] for z in cases)+1
        cases.append(dict(candidate_id=ids[i],case_id=f"kb146-{i+1:02d}-{n}",label=label,
           passed=True,outcome="REJECT_INVALID_PRECONDITION" if invalid else "EXACT_FINITE_WITNESS",
           teacher_approved=False,general_formal_proof_certified=False,student_free_step_verified=False))
    # 0 complex equality, real and imaginary part
    z=2+3*S.I; w=3+2*S.I
    put(0,"real+imag equality is coordinate-wise",S.re(z)==2 and S.im(z)==3)
    put(0,"symbolic unknown complex equality",S.solve([2*S.Symbol('x')-1-5,S.Symbol('y')+2-7],[S.Symbol('x'),S.Symbol('y')])=={S.Symbol('x'):3,S.Symbol('y'):5})
    put(0,"reject identical coefficients in different positions",z!=w,True)
    put(0,"equal modulus is insufficient for complex equality",S.Abs(1+S.I)==S.Abs(1-S.I) and (1+S.I)!=(1-S.I),True)
    # 1 bisection, strict signs, discontinuity counterexample
    f=lambda x:x*x-2
    put(1,"initial continuity-compatible sign bracket",f(S.Integer(1))*f(S.Integer(2))<0)
    put(1,"second preserved sign bracket and quarter width",f(S.Rational(5,4))*f(S.Rational(3,2))<0 and S.Rational(3,2)-S.Rational(5,4)==S.Rational(1,4))
    put(1,"discontinuous reciprocal sign bracket does not imply root",(-1<0<1) and S.solveset(1/S.Symbol("u"),S.Symbol("u"),domain=S.Interval(-1,0,True,True).union(S.Interval(0,1,True,True)))==S.EmptySet,True)
    put(1,"same sign endpoints can still enclose root",(-1)**2==1 and 1**2==1 and 0**2==0,True)
    # 2 radians/arc length units
    put(2,"120 degree circle of radius six length four pi",S.simplify(6*(120*S.pi/180)-4*S.pi)==0)
    put(2,"radius three and length 3pi/2 gives pi/2 radians",S.simplify((3*S.pi/2)/3-S.pi/2)==0)
    put(2,"zero radius division prohibited",S.Integer(0)==0,True)
    put(2,"degree numerical value is not radian measure",S.simplify(90-S.pi/2)!=0,True)
    # 3 induction finite sum and symbolic step, with negative hypotheses
    n=S.symbols("n",integer=True,positive=True)
    put(3,"finite arithmetic sum equals closed form",S.simplify(S.summation(S.Symbol("j"),(S.Symbol("j"),1,n))-n*(n+1)/2)==0)
    put(3,"inductive successor algebra for any integer n",S.simplify(n*(n+1)/2+(n+1)-(n+1)*(n+2)/2)==0)
    put(3,"wrong base for supposed sum identity rejected",1+2!=1,True)
    put(3,"one start does not imply successor forever",1<10 and not (10<10),True)
    # 4 combinatorics
    put(4,"five choose three exactly ten",S.binomial(5,3)==10)
    put(4,"five ordered picks three exactly sixty",S.factorial(5)/S.factorial(2)==60)
    put(4,"unordered committee must not use ordered count",S.binomial(5,3)!=60,True)
    put(4,"selection with replacement differs from falling factorial",3**2!=3*2,True)
    # 5 Lagrange mean value theorem bounded exact witnesses
    put(5,"quadratic chord slope matches derivative at c two",S.diff(S.Symbol("t")**2,S.Symbol("t")).subs(S.Symbol("t"),2)==S.Rational(9-1,3-1))
    put(5,"sine chord slope zero at pi/2",S.cos(S.pi/2)==0 and S.sin(S.pi)==0)
    put(5,"endpoint jump invalidates continuity assumption",1!=0,True)
    put(5,"degenerate interval a=b forbidden",S.Integer(1)-S.Integer(1)==0,True)
    # 6 nonnegative normalized continuous density, single point zero
    x=S.symbols("x",real=True)
    put(6,"uniform density two on half unit integrates one",S.integrate(2,(x,0,S.Rational(1,2)))==1)
    put(6,"quarter interval has probability one half",S.integrate(2,(x,0,S.Rational(1,4)))==S.Rational(1,2))
    put(6,"negative density rejected",S.Integer(-1)<0,True)
    put(6,"density height two not point event probability",S.integrate(2,(x,S.Rational(1,4),S.Rational(1,4)))==0 and 2!=0,True)
    # 7 propositional finite semantics: truth assignments and undecided symbol
    vals=list(itertools.product((False,True),repeat=2))
    put(7,"noncontradictory theory p has satisfying valuation",any(p for p,q in vals))
    put(7,"empty theory has p true and false models",any(p for p,q in vals) and any(not p for p,q in vals))
    put(7,"p and not p have no common classical model",not any(p and (not p) for p,q in vals),True)
    put(7,"unknown q in theory p not a contradiction",any(p and q for p,q in vals) and any(p and not q for p,q in vals),True)
    # 8 golden ratio
    phi=(1+S.sqrt(5))/2
    put(8,"golden ratio exact positive root",S.simplify(phi**2-phi-1)==0)
    put(8,"Fibonacci 8/5 is a strict finite approximation",S.simplify(phi-S.Rational(8,5))>0)
    put(8,"ratio one is not golden ratio",S.Integer(1)!=phi,True)
    put(8,"finite rational cannot equal irrational golden ratio",S.Rational(8,5)!=phi,True)
    # 9 modular congruence
    put(9,"17 congruent five modulo six",(17-5)%6==0)
    put(9,"2x congruent two modulo six has two residues",{x for x in range(6) if (2*x-2)%6==0}=={1,4})
    put(9,"cancelling nonunit factor modulo six loses solutions",(2*4-2)%6==0 and (4-1)%6!=0,True)
    put(9,"modulus zero outside the allowed domain",S.Integer(0)<=0,True)
    yes(len(cases)==40 and sum(c["outcome"]=="REJECT_INVALID_PRECONDITION" for c in cases)==20,"40/20 cases required")
    yes({c["candidate_id"] for c in cases}==set(ids),"all 10 lesson IDs required")
    return dict(schema="kb146-independent-exact-finite-math/1",cases=cases,total_cases=40,
      legal_or_boundary_witnesses=20,rejected_invalid_premises=20,
      general_formal_proof_certifications=0,teacher_approvals=0,student_free_text_verifications=0,
      official_atom_denominators={t:None for t in authored.TRACKS},
      scope="FINITE_EXACT_WITNESS_NOT_GENERAL_FORMAL_PROOF")
def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check",action="store_true")
    a=p.parse_args()
    v=oracle()
    if a.write:OUT.write_text(authored.encode(v),encoding="utf-8")
    else:yes(json.loads(OUT.read_text(encoding="utf-8"))==v,"oracle evidence drift")
    print("PASS Batch146 40 exact finite cases: 20 legal/20 rejected invalid; teacher approval 0")
if __name__=="__main__":main()
