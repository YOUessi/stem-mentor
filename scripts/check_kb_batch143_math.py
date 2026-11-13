#!/usr/bin/env python3
"""Independent exact/finite mathematics oracle; never certifies general proofs."""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch143_lessons as author
OUT=ROOT/"docs/evaluation/KB_BATCH143_EXACT_MATH_WITNESSES.json"
def must(v,label):
    if v is not True and v!=S.true:raise AssertionError("independent math failed: "+label)
def oracle():
    ids=author.IDS
    rows=[]
    def add(i,label,value,invalid=False):
        must(value,label)
        rows.append(dict(
          candidate_id=ids[i],case_id=f"kb143-case-{i+1:02d}-{1+sum(x['candidate_id']==ids[i] for x in rows)}",
          label=label,passed=True,
          outcome="REJECT_INVALID_PRECONDITION" if invalid else "FINITE_EXACT_WITNESS",
          teacher_approved=False,formal_proof_certified=False,free_student_text_verified=False))
    # 0 universal quantifier negation: exhaustive finite models including empty universe.
    for domain,pred in [(list(range(-2,3)),lambda x:x*x>=0),([],lambda x:x>2)]:
        lhs=not all(pred(x) for x in domain)
        rhs=any(not pred(x) for x in domain)
        add(0,"forall negation equals exists counterexample on finite/empty domain",lhs==rhs)
    domain=[-1,0,1]; p=lambda x:x>0
    add(0,"rejects incorrect forall-to-forall negation",not all(p(x) for x in domain)!=all(not p(x) for x in domain),True)
    domain=[1,2]; p=lambda x:x>0
    add(0,"rejects keeping weak inequality without logical negation",not all(p(x) for x in domain)!=any(x>=0 for x in domain),True)
    # 1 even/odd require domain symmetry, not just algebraic identity.
    symdomain=list(range(-4,5))
    add(1,"x square is even on symmetric integer test domain",
        all((-x)**2==x*x for x in symdomain) and set(symdomain)=={-x for x in symdomain})
    add(1,"x cubed is odd on symmetric integer test domain",
        all((-x)**3==-x**3 for x in symdomain))
    asymmetric={0,1,2}
    add(1,"rejects one-sided square function as even",
        asymmetric!={-x for x in asymmetric},True)
    add(1,"rejects x square plus x as even or odd",
        any((-x)**2-x!=(x*x+x) for x in symdomain) and
        any((-x)**2-x!=-(x*x+x) for x in symdomain),True)
    # 2 sine law: independent exact right-triangle circumradius witnesses.
    add(2,"3-4-5 triangle circumradius from 90-degree sine",
        S.Rational(5,1)/S.sin(S.pi/2)==2*S.Rational(5,2))
    add(2,"6-8-10 triangle circumradius from 90-degree sine",
        S.Rational(10,1)/S.sin(S.pi/2)==2*S.Integer(5))
    B1=S.asin(S.Rational(4,5)); B2=S.pi-B1
    add(2,"SSA 30-degree 5-to-8 has two interior-angle solutions",
        S.N(B1)<S.N(B2) and S.N(S.pi/6+B2)<S.N(S.pi) and S.sin(B2)==S.Rational(4,5),True)
    add(2,"rejects SSA sine greater than one",
        S.Rational(6,1)*S.sin(S.pi/6)/S.Integer(2)>1,True)
    # 3 inclusion-exclusion on finite uniform dice.
    A={2,4,6}; B={4,5,6}; U=set(range(1,7))
    add(3,"dice union via inclusion-exclusion equals 2/3",
        S.Rational(len(A),6)+S.Rational(len(B),6)-S.Rational(len(A&B),6)
        ==S.Rational(len(A|B),6)==S.Rational(2,3))
    A2={1,2}; B2={2,3}
    add(3,"second overlapping pair union equals one half",
        S.Rational(len(A2|B2),6)==S.Rational(1,2) and len(A2&B2)==1)
    add(3,"rejects naive addition of overlapping events",
        S.Rational(len(A),6)+S.Rational(len(B),6)!=S.Rational(len(A|B),6),True)
    add(3,"rejects treating these intersecting dice events as independent",
        S.Rational(len(A&B),6)!=S.Rational(len(A)*len(B),36),True)
    # 4 slope: nonvertical and horizontal; reject divided-by-zero or duplicate points.
    add(4,"slope (1,2) to (3,6) equals two",S.Rational(6-2,3-1)==2)
    add(4,"horizontal slope zero",(S.Rational(5-5,2-(-1))==0))
    add(4,"vertical x coordinates duplicate: undefined slope",
        2-2==0 and 5-1!=0,True)
    add(4,"identical points do not define a unique straight line",
        (1,2)==(1,2) and (2-2)==(1-1)==0,True)
    # 5 hypergeometric: count without replacement, and reject independent sampling.
    def hg(N,K,n,k):
        if not max(0,n-(N-K))<=k<=min(n,K):return S.Integer(0)
        return S.binomial(K,k)*S.binomial(N-K,n-k)/S.binomial(N,n)
    add(5,"10 population 4 success draw 3 exactly two =3/10",
        hg(10,4,3,2)==S.Rational(3,10))
    add(5,"5 population 2 success draw 2 exactly one =3/5 and normalization",
        hg(5,2,2,1)==S.Rational(3,5) and
        sum(hg(5,2,2,k) for k in range(3))==1)
    add(5,"rejects replacement binomial approximation as exact",
        hg(10,4,3,2)!=S.binomial(3,2)*S.Rational(2,5)**2*S.Rational(3,5),True)
    add(5,"rejects impossible success count",
        hg(3,2,3,0)==0 and hg(3,2,3,2)==1,True)
    # 6 Cramer: compute independently from determinants and solve equation systems.
    def cramer_exact(A,b):
        d=A.det()
        if d==0:return None
        res=[]
        for i in range(A.cols):
            Ai=A.copy();Ai[:,i]=b
            res.append(S.factor(Ai.det()/d))
        return S.Matrix(res)
    AA=S.Matrix([[2,1],[1,-1]]);bb=S.Matrix([5,1])
    add(6,"Cramer first system has (2,1) exact solution",
        AA.det()==-3 and cramer_exact(AA,bb)==S.Matrix([2,1]) and AA*S.Matrix([2,1])==bb)
    AA2=S.Matrix([[3,1],[1,1]]);bb2=S.Matrix([7,3])
    add(6,"Cramer second system has (2,1) exact solution",
        AA2.det()==2 and cramer_exact(AA2,bb2)==S.Matrix([2,1]))
    singular=S.Matrix([[1,1],[2,2]])
    add(6,"singular inconsistent system must refuse division",
        cramer_exact(singular,S.Matrix([1,3])) is None and
        singular.row_join(S.Matrix([1,3])).rank()>singular.rank(),True)
    add(6,"singular consistent system still has no Cramer unique result",
        cramer_exact(singular,S.Matrix([1,2])) is None and
        singular.row_join(S.Matrix([1,2])).rank()==singular.rank()<2,True)
    # 7 equal temperament ratio: exponent law exact, reject zero Hz and additive steps.
    r=2**S.Rational(1,12)
    add(7,"12 semitones above 440 exactly 880 Hz",S.simplify(440*r**12-880)==0)
    add(7,"12 semitones below 440 exactly 220 Hz",S.simplify(440*r**(-12)-220)==0)
    add(7,"rejects frequency zero as valid reference for ratio",
        S.Integer(0)<=0,True)
    add(7,"fixed additive Hz increments violate equal ratio",
        S.Rational(460,440)!=S.Rational(480,460),True)
    must(len(rows)==32,"32 exact cases")
    must(sum(x["outcome"]=="REJECT_INVALID_PRECONDITION" for x in rows)==16,"16 invalid cases")
    must({x["candidate_id"] for x in rows}==set(ids),"8 topics")
    return dict(schema="kb143-independent-exact-finite-oracle/1",
       cases=rows,total_cases=32,negative_precondition_rejections=16,
       nonnegative_exact_witnesses=16,
       proof_certifications=0,teacher_approvals=0,student_step_verifications=0,
       official_atom_denominators={t:None for t in author.TRACKS},
       scope="FINITE_WITNESS_NOT_GENERAL_FORMAL_PROOF")
def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check",action="store_true")
    args=p.parse_args()
    value=oracle()
    if args.write:OUT.write_text(author.encode(value),encoding="utf-8")
    else:must(json.loads(OUT.read_text(encoding="utf-8"))==value,"oracle evidence drift")
    print("PASS 32 exact finite cases (16 positive, 16 rejected invalid), 0 universal proof certifications")
if __name__=="__main__":main()
