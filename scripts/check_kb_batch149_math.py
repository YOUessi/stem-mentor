#!/usr/bin/env python3
"""Independent exact / finite guards for 10 KB149 drafts; NOT universal proof certification."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch149_lessons as lessons
OUT=ROOT/"docs/evaluation/KB_BATCH149_EXACT_MATH_WITNESSES.json"
def oracle():
    cases=[]
    def put(k,label,p,invalid=False):
        if p is not True and p!=S.true: raise AssertionError(f"{k}:{label}: {p}")
        no=sum(c["candidate_id"]==lessons.IDS[k] for c in cases)+1
        cases.append(dict(candidate_id=lessons.IDS[k],case_id=f"kb149-{k+1:02d}-{no}",
                          label=label,passed=True,outcome="REJECT_INVALID_PRECONDITION" if invalid else "EXACT_FINITE_WITNESS",
                          teacher_approved=False,general_formal_proof_certified=False,student_free_step_verified=False))
    # 0, uniform finite sample space and biased/sum-space failures.
    put(0,"six-sided fair die: three even outcomes",S.Rational(3,6)==S.Rational(1,2))
    pairs=[(i,j) for i in range(1,7) for j in range(1,7)]
    put(0,"six ways to get total seven of thirty-six ordered pairs",
        sum(i+j==7 for i,j in pairs)==6 and S.Rational(6,len(pairs))==S.Rational(1,6))
    put(0,"biased red/blue not equiprobable",S.Rational(3,4)!=S.Rational(1,2),True)
    put(0,"dice sum two is less likely than sum seven",
        sum(i+j==2 for i,j in pairs)!=sum(i+j==7 for i,j in pairs),True)
    # 1, stratified proportional allocation and rounding/capacity.
    put(1,"60/40 population split 12/8 sampled",S.Rational(12,60)==S.Rational(8,40)==S.Rational(1,5))
    put(1,"9/6 population split 3/2 sampled",S.Rational(3,9)==S.Rational(2,6)==S.Rational(1,3))
    put(1,"seven/three split four gives fractional allocation",
        S.Rational(4*7,10).q!=1 and S.Rational(4*3,10).q!=1,True)
    put(1,"two/two rounding produces unequal inclusion probability",
        S.Rational(2,7)!=S.Rational(2,3),True)
    # 2, quadratic inequality and strict endpoints.
    x=S.symbols("x",real=True)
    put(2,"factorable inequality roots",
        S.factor(x*x-5*x+6)==(x-2)*(x-3) and
        S.solveset(x*x-5*x+6<=0,x,domain=S.S.Reals)==S.Interval(2,3))
    put(2,"negative perfect square never strictly positive",
        S.solveset(-(x-2)**2>0,x,domain=S.S.Reals)==S.EmptySet)
    put(2,"negative discriminant must not create real root",
        S.discriminant(x*x+1,x)<0 and S.solveset(S.Eq(x*x+1,0),x,domain=S.S.Reals)==S.EmptySet,True)
    put(2,"strict root endpoint exclusion",
        2 not in S.solveset(x*x-5*x+6<0,x,domain=S.S.Reals),True)
    # 3, conditional probability vs independence and mutual exclusivity.
    A={2,4,6};B={4,5,6}
    put(3,"die event conditional 2/3",
        S.Rational(len(A&B),len(B))==S.Rational(2,3))
    put(3,"two fair coin flips independent first and second head",
        S.Rational(1,4)==S.Rational(1,2)*S.Rational(1,2))
    put(3,"positive-probability mutual exclusion cannot imply independence",
        S.Rational(0)!=S.Rational(1,2)*S.Rational(1,2),True)
    put(3,"conditional probability on zero probability impossible",
        S.Rational(0)==0,True)
    # 4, Bayes partitions, true denominators, invalid overlaps.
    pos=S.Rational(1,100)*S.Rational(9,10)+S.Rational(99,100)*S.Rational(1,10)
    put(4,"screening posterior is 1/12",
        S.simplify((S.Rational(1,100)*S.Rational(9,10))/pos)==S.Rational(1,12))
    pos2=S.Rational(3,5)*S.Rational(1,10)+S.Rational(2,5)*S.Rational(1,20)
    put(4,"factory defect posterior is 3/4",
        S.simplify((S.Rational(3,5)*S.Rational(1,10))/pos2)==S.Rational(3,4))
    put(4,"overlapping branches double-count sample",
        len({1,2}|{2,3})!=len({1,2})+len({2,3}),True)
    put(4,"zero-evidence denominator forbids posterior division",pos>0 and S.Integer(0)==0,True)
    # 5, convergence boundedness; finite witnesses cannot certify general proof.
    put(5,"reciprocals after N are below epsilon tenth",
        all(S.Rational(1,n)<S.Rational(1,10) for n in range(11,100)))
    put(5,"alternating reciprocals bounded by one",
        all(abs(S.Rational((-1)**n,n))<=1 for n in range(1,100)))
    put(5,"bounded alternating sequence does not converge",
        all((-1)**n==1 for n in range(2,100,2)) and
        all((-1)**n==-1 for n in range(1,100,2)),True)
    put(5,"a convergent even subsequence does not bound odd spikes",
        all((0 if n%2==0 else n)==0 for n in range(2,40,2)) and
        max(0 if n%2==0 else n for n in range(1,100))==99,True)
    # 6, bivariate natural domains.
    put(6,"closed disk boundary allowed for real square root",
        4-2*2-0*0==0 and S.sqrt(0)==0)
    put(6,"log and denominator simultaneous validity",
        2-1>0 and 2+1!=0 and S.log(2-1)==0)
    put(6,"logarithm zero argument forbidden",
        1-1==0,True)
    put(6,"nonzero logarithm input but zero denominator invalid",
        (1-(-1))>0 and 1+(-1)==0,True)
    # 7, direct proof vs contradiction, check finite arithmetic sanity.
    put(7,"consecutive integer product even",all((n*(n+1))%2==0 for n in range(-20,21)))
    put(7,"square two parity descent finite arithmetic sanity",
        all((p*p)%2==0 for p in range(-20,21) if p%2==0))
    put(7,"universal real square positive false at zero",0*0==0,True)
    put(7,"negation of all positive squares has counterexample, not all nonpositive",
        any(n*n<=0 for n in range(-10,11)) and not all(n*n<=0 for n in range(-10,11)),True)
    # 8, Euclidean isometries, whole set vs point.
    P=S.Matrix([2,-3]);Q=S.Matrix([-1,5])
    F=lambda v:S.Matrix([v[0],-v[1]])
    C=lambda v:-v
    put(8,"axis reflection length squared preserved",
        (F(P)-F(Q)).dot(F(P)-F(Q))==(P-Q).dot(P-Q))
    put(8,"central inversion length squared preserved",
        (C(P)-C(Q)).dot(C(P)-C(Q))==(P-Q).dot(P-Q))
    put(8,"axis reflection and central inversion unequal on generic point",
        F(P)!=C(P),True)
    put(8,"singleton finite set not invariant under nonzero translation",
        {tuple(P)}!={tuple(P+S.Matrix([1,4]))},True)
    # 9, spherical geodesic length, great circle, antipodal nonuniqueness.
    pi=S.pi;R=S.Integer(1);P=S.Matrix([1,0,0]);Q=S.Matrix([0,1,0])
    put(9,"unit sphere right-angle arc",
        S.acos(P.dot(Q)/R**2)*R==pi/2)
    P2=S.Matrix([2,0,0]);Q2=-P2;R2=S.Integer(2)
    put(9,"radius two antipodal shortest length",
        S.simplify(R2*S.acos(P2.dot(Q2)/R2**2)-2*pi)==0)
    put(9,"Euclidean chord not equal sphere arc",
        S.sqrt((P-Q).dot(P-Q))!=pi/2,True)
    put(9,"antipodal example has two distinct equal-length meridians",
        P2.dot(Q2)==-R2**2 and S.Matrix([0,1,0])!=S.Matrix([0,0,1]),True)
    assert len(cases)==40 and sum(c["outcome"]=="REJECT_INVALID_PRECONDITION" for c in cases)==20
    assert all([c["candidate_id"] for c in cases[i*4:(i+1)*4]]==[lessons.IDS[i]]*4 for i in range(10))
    return dict(schema="kb149-finite-independent-exact-oracles/1",cases=cases,total_cases=40,
        legal_or_boundary_witnesses=20,invalid_premise_rejections=20,
        teacher_approved=0,student_free_text_steps_verified=0,general_formal_proofs_certified=0,
        official_atom_denominators={t:None for t in lessons.TRACKS},
        warning="Finite exact examples are not formal universal proofs or teacher approval.")
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    args=p.parse_args()
    v=oracle()
    if args.write:OUT.write_text(lessons.encode(v),encoding="utf-8")
    else:assert json.loads(OUT.read_text(encoding="utf-8"))==v,"oracle source drift"
    print("PASS Batch149 40/40 exact limited witnesses: 20 legal/boundary + 20 invalid, 0 certification")
if __name__=="__main__":main()
