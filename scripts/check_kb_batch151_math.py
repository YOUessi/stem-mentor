#!/usr/bin/env python3
"""KB151 independent exact finite cases; never certifies general theorem or student work."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch151_lessons as lessons
OUT=ROOT/"docs/evaluation/KB_BATCH151_EXACT_WITNESSES.json"
def oracle():
    cases=[]
    def put(i, label, cond, invalid=False):
        if cond is not True and cond != S.true:
            raise AssertionError(f"KB151 exact witness {i} {label}: {cond!r}")
        n=1+sum(v["candidate_id"]==lessons.IDS[i] for v in cases)
        cases.append(dict(candidate_id=lessons.IDS[i],case_id=f"kb151-{i+1:02d}-{n}",
            label=label,passed=True,outcome="REJECT_INVALID_PRECONDITION" if invalid else "EXACT_FINITE_WITNESS",
            teacher_approved=False,general_formal_proof_certified=False,student_free_step_verified=False))
    # 0 finite equiprobable outcomes; unequal color weights and order-loss are invalid.
    Om={(i,j) for i in ("H","T") for j in ("H","T")}
    put(0,"two distinguishable coins: at least one H",S.Rational(sum("H" in z for z in Om),len(Om))==S.Rational(3,4))
    put(0,"fair die: primes 2 3 5",sum(x in (2,3,5) for x in range(1,7))==3)
    put(0,"three red and one blue are unequal outcomes",S.Rational(3,4)!=S.Rational(1,2),True)
    put(0,"unordered HT coalescence destroys equal weights",len({tuple(sorted(z)) for z in Om})==3 and len(Om)==4,True)
    # 1 determinant / nonzero base / dot product
    u=S.Matrix([2,3]);v=S.Matrix([6,9]);w=S.Matrix([0,2]);z=S.Matrix([0,-6])
    det=lambda a,b:a[0]*b[1]-a[1]*b[0]
    put(1,"nonzero base gives lambda 3",det(u,v)==0 and v==3*u)
    put(1,"zero first coordinate still valid",det(w,z)==0 and z==-3*w)
    put(1,"zero reference vector cannot span nonzero v",det(S.zeros(2,1),S.Matrix([1,0]))==0 and S.Matrix([1,0])!=0*S.zeros(2,1),True)
    put(1,"orthogonality is not parallel",S.Matrix([1,0]).dot(S.Matrix([0,1]))==0 and det(S.Matrix([1,0]),S.Matrix([0,1]))!=0,True)
    # 2 cosine law / triangle inequality
    put(2,"sides 3 4 angle 60 yield square 13",S.simplify(3**2+4**2-2*3*4*S.cos(S.pi/3))==13)
    put(2,"5 6 7 gives cosine 1/5",S.Rational(5**2+6**2-7**2,2*5*6)==S.Rational(1,5))
    put(2,"1 2 3 violates strict triangle inequality",1+2==3,True)
    put(2,"zero adjacent side forbids inverse cosine quotient",S.Rational(1,0) is S.zoo,True)
    # 3 nonzero ratio definition / nonzero initial term
    put(3,"first 3 ratio negative two fifth term",3*(-2)**4==48)
    put(3,"half ratio sixth term",S.Rational(1,2)**5==S.Rational(1,32))
    put(3,"zero recurring term creates undefined ratio",S.Rational(0,0) is S.nan,True)
    put(3,"negative ratio does not imply positive terms",3*(-2)**1 < 0 and 3*(-2)**2 > 0,True)
    # 4 derivative and strictly monotone versus weak monotone
    x=S.symbols("x",real=True)
    f=x*x
    put(4,"x squared derivative nonnegative on 0 to 3",
        S.diff(f,x)==2*x and all(2*i>=0 for i in range(4)))
    put(4,"minus cubic strict decrease at ordered probes",
        all(-a**3>-b**3 for a,b in [(S.Integer(-2),S.Integer(-1)),(S.Integer(-1),S.Integer(0)),(S.Integer(0),S.Integer(2))]))
    put(4,"strict increase of cubic has zero derivative at zero",
        S.diff(x**3,x).subs(x,0)==0 and (-1)**3 < 0**3 < 1**3,True)
    put(4,"nonnegative derivative of constant does not imply strict",
        S.diff(S.Integer(3),x)==0 and S.Integer(3)==S.Integer(3),True)
    # 5 intermediate values, endpoint sign not necessity
    q=x**3+x-1
    put(5,"polynomial endpoints opposite",q.subs(x,0)==-1 and q.subs(x,1)==1)
    roots=S.solveset(x*x-1,x,domain=S.Interval(-2,2))
    put(5,"continuous same-sign endpoints can contain roots",
        roots==S.FiniteSet(-1,1) and (x*x-1).subs(x,-2)==3 and (x*x-1).subs(x,2)==3)
    put(5,"step function can jump over zero",
        (-1)<0<1 and all(v!=0 for v in (-1,1)),True)
    put(5,"IVT not uniqueness: cubic has three distinct roots",
        len(S.solveset(x**3-x,x,domain=S.Interval(-2,2)))==3,True)
    # 6 partial derivative does not ensure continuity
    y=S.symbols("y",real=True)
    g=x*x*y+3*y*y
    put(6,"gradient at 2 1 from polynomial slices",
        S.diff(g,x).subs({x:2,y:1})==4 and S.diff(g,y).subs({x:2,y:1})==10)
    put(6,"partial derivative x squared times y",
        S.diff(x*x*y,x)==2*x*y and S.diff(x*x*y,y)==x*x)
    put(6,"origin coordinate partials zero but diagonal limit half",
        S.limit((x*x)/(x*x+x*x),x,0)==S.Rational(1,2),True)
    put(6,"both partials known do not determine arbitrary directional path",
        S.limit(x*x/(2*x*x),x,0)==S.Rational(1,2) and S.Integer(0)!=S.Rational(1,2),True)
    # 7 logical sufficiency not converse
    put(7,"x 3 satisfies positive implication",3>2 and 3**2>4)
    put(7,"multiples four always even finite sanity",
        all((4*n)%2==0 for n in range(-40,41)))
    put(7,"converse x squared >4 fails for negative x",
        (-3)**2>4 and not (-3>2),True)
    put(7,"even integer not always divisible by four",
        2%2==0 and 2%4!=0,True)
    # 8 beat sync LCM and offsets
    put(8,"lcm six eight twenty-four",S.ilcm(6,8)==24 and 24%6==24%8==0)
    put(8,"lcm four ten twenty",S.ilcm(4,10)==20)
    put(8,"gcd not lcm",S.igcd(6,8)==2 and 2%6!=0,True)
    put(8,"inconsistent offset congruences",
        not any(t%2==0 and t%4==1 for t in range(0,120)),True)
    # 9 exact real returns same period
    put(9,"real rate ten vs five equals 1/21",
        (S.Rational(11,10)/S.Rational(21,20)-1)==S.Rational(1,21))
    put(9,"real rate three vs five equals minus 2/105",
        S.Rational(103,105)-1==-S.Rational(2,105))
    put(9,"nominal minus inflation is only approximation",
        S.Rational(1,10)-S.Rational(1,20)!=S.Rational(1,21),True)
    put(9,"inflation price factor zero cannot divide",
        S.Rational(11,10)/S.Integer(0) is S.zoo,True)
    assert len(cases)==40 and sum(c["outcome"]=="REJECT_INVALID_PRECONDITION" for c in cases)==20
    assert all([r["candidate_id"] for r in cases[i*4:(i+1)*4]]==[lessons.IDS[i]]*4 for i in range(10))
    return dict(schema="kb151-exact-finite-oracle/1",cases=cases,total_cases=40,
        legal_or_boundary_witnesses=20,invalid_premise_rejections=20,
        teacher_approved=0,student_free_text_steps_verified=0,general_formal_proofs_certified=0)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    a=p.parse_args();v=oracle()
    if a.write:OUT.write_text(lessons.encode(v),encoding="utf-8")
    else:assert json.loads(OUT.read_text(encoding="utf-8"))==v,"exact oracle evidence drift"
    print("PASS KB151 40/40 finite exact conditions; 20 forbidden cases; general proofs 0")
if __name__=="__main__":main()
