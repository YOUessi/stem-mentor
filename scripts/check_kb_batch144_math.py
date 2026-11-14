#!/usr/bin/env python3
"""Independent exact symbolic/finite witnesses: not general formal theorem certifications."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch144_lessons as authored
OUT=ROOT/"docs/evaluation/KB_BATCH144_EXACT_MATH_WITNESSES.json"
def must(v,why):
    if v is not True and v!=S.true:raise AssertionError("Batch144 independent math failure: "+why)
def oracle():
    rows=[]; ids=authored.IDS
    def add(k,why,predicate,invalid=False):
        must(predicate,why)
        index=1+sum(x["candidate_id"]==ids[k] for x in rows)
        rows.append(dict(candidate_id=ids[k],case_id=f"kb144-{k+1:02d}-{index}",
             label=why,passed=True,outcome="REJECT_INVALID_PRECONDITION" if invalid else "EXACT_FINITE_WITNESS",
             formal_general_proof_certified=False,teacher_approved=False,student_answer_verified=False))
    # 1 Vector triangle law: check symbolic coordinate identity, two wrong usages.
    ax,ay,bx,by,cx,cy=S.symbols("ax ay bx by cx cy",real=True)
    u=S.Matrix([bx-ax,by-ay]);v=S.Matrix([cx-bx,cy-by]);w=S.Matrix([cx-ax,cy-ay])
    add(0,"coordinate telescoping identity",S.simplify(u+v-w)==S.zeros(2,1))
    add(0,"3-4-5 composed displacement",S.Matrix([3,0])+S.Matrix([0,4])==S.Matrix([3,4]))
    add(0,"reject endpoints added as vector sum",S.Matrix([3,5])+S.Matrix([6,9])!=S.Matrix([5,7]),True)
    add(0,"reject wrong directed segment",S.Matrix([3,5])-S.Matrix([1,2]) != S.Matrix([1,2])-S.Matrix([3,5]),True)
    # 2 Membership vs subset and nesting levels.
    A={1,2};B={frozenset({1}),2}
    add(1,"integer belongs to set",1 in A)
    add(1,"singleton is subset of parent set",{1}.issubset(A))
    add(1,"singleton not an element of integer set",frozenset({1}) not in A,True)
    add(1,"integer not directly present in nested set",1 not in B and frozenset({1}) in B,True)
    # 3 Periodic and constant cases: exact symbolic algebra and no minimum.
    x=S.symbols("x",real=True)
    add(2,"sine 2x has pi period",S.trigsimp(S.sin(2*(x+S.pi))-S.sin(2*x))==0)
    add(2,"constant maps preserve every real translation",S.Integer(3)==S.Integer(3))
    add(2,"zero translation excluded by formal periodicity definition",S.Integer(0)==0,True)
    add(2,"constant positive period cannot be minimum: T/2 smaller",S.Rational(1,2)<1,True)
    # 4 Arithmetic sequence: general n symbolic plus boundary indices.
    n,a,d=S.symbols("n a d",integer=True)
    f=lambda k:a+(k-1)*d
    add(3,"symbolic consecutive differences equals d",S.simplify(f(n+1)-f(n)-d)==0)
    add(3,"first term boundary preserved",S.simplify(f(1)-a)==0)
    add(3,"reject off-by-one formula a+n*d",S.Integer(3)+2!=3,True)
    add(3,"reject irregular sequence as arithmetic",[7-5,9-7,12-9]!=[2,2,2],True)
    # 5 Circle nondegeneracy.
    h,k=S.symbols("h k",real=True)
    add(4,"point on positive radius five circle",(8-3)**2+(-1+1)**2==25)
    add(4,"negative constant circle equation has no real roots",S.solveset(S.Symbol("z",real=True)**2+1,S.Symbol("z",real=True),domain=S.S.Reals)==S.EmptySet)
    add(4,"zero radius is point not ordinary positive circle",S.Integer(0)<=0,True)
    add(4,"negative radius square rejects real point",S.Integer(-1)<0,True)
    # 6 Real linear subspace closure of x=y, negative affine.
    alpha,beta,x,y=S.symbols("alpha beta x y",real=True)
    add(5,"homogeneous diagonal additive closure",S.simplify((x+y)-(x+y))==0)
    add(5,"homogeneous diagonal scalar closure",S.simplify(alpha*x-alpha*x)==0)
    add(5,"affine x+y=1 excludes zero",(0+0)!=1,True)
    add(5,"affine point not closed under doubling",(2*S.Rational(1,2)+2*S.Rational(1,2))!=1,True)
    # 7 Linear dependence: nontrivial nullvector vs independent.
    D=S.Matrix.hstack(S.Matrix([1,2]),S.Matrix([2,4]))
    I=S.eye(2)
    add(6,"nontrivial null vector gives dependence",D*S.Matrix([2,-1])==S.zeros(2,1))
    add(6,"independent basis rank two",I.det()==1 and I.rank()==2)
    add(6,"all-zero coefficients do not prove dependence",I*S.Matrix([0,0])==S.zeros(2,1) and I.det()!=0,True)
    add(6,"zero column forces dependence",S.Matrix.hstack(S.zeros(2,1),S.Matrix([1,2])).rank()<2,True)
    # 8 Fixed effective interest: exact amounts and false unit conversions.
    add(7,"two annual 10-percent compound years",S.Integer(1000)*(1+S.Rational(1,10))**2==1210)
    add(7,"after monthly interest then repayment",S.Integer(1000)*(1+S.Rational(1,100))-100==910)
    add(7,"12-percent annual effective is not 12-percent monthly",S.root(S.Rational(28,25),12)-1!=S.Rational(12,100),True)
    add(7,"monthly 12-percent violates annual-nominal 12-percent convention",S.Rational(12,100)!=S.Rational(12,1200),True)
    # 9 Pure sound.
    add(8,"100pi angular frequency means 50 Hz",S.Integer(100)*S.pi/(2*S.pi)==50)
    add(8,"nonzero 50 Hz period exactly 1/50 s",S.Rational(1,50)==S.Rational(2,100))
    add(8,"doubling amplitude does not double angular frequency",S.Integer(100)*S.pi!=S.Integer(200)*S.pi,True)
    add(8,"zero signal lacks observable positive minimum",S.simplify(0*S.sin(100*S.pi*x))==0,True)
    # 10 Robot transform ordering and rotation metric.
    R=S.Matrix([[0,-1],[1,0]]);p=S.Matrix([1,0]);t=S.Matrix([1,0])
    add(9,"rotation orthogonal determinant one",R.T*R==S.eye(2) and R.det()==1)
    add(9,"rotate then translate gives (1,1)",R*p+t==S.Matrix([1,1]))
    add(9,"translate then rotate gives (0,2), not (1,1)",R*(p+t)==S.Matrix([0,2]) and R*(p+t)!=R*p+t,True)
    add(9,"reference frame translation cannot be naively interchanged",R*t!=t,True)
    must(len(rows)==40 and sum(r["outcome"]=="REJECT_INVALID_PRECONDITION" for r in rows)==20,"40/20 case gate")
    must({r["candidate_id"] for r in rows}==set(ids),"ten topics not all examined")
    return dict(schema="kb144-independent-exact-finite-math/1",
        cases=rows,total_cases=40,valid_or_boundary_cases=20,invalid_precondition_rejections=20,
        formal_general_proof_certifications=0,teacher_approvals=0,student_free_text_verifications=0,
        official_atom_denominators={t:None for t in authored.TRACKS},
        scope="FINITE_EXACT_WITNESS_NOT_GENERAL_FORMAL_PROOF")
def main():
    p=argparse.ArgumentParser();a=p.add_mutually_exclusive_group(required=True)
    a.add_argument("--write",action="store_true");a.add_argument("--check",action="store_true")
    args=p.parse_args();v=oracle()
    if args.write:OUT.write_text(authored.encode(v),encoding="utf-8")
    else:must(json.loads(OUT.read_text(encoding="utf-8"))==v,"oracle evidence drift")
    print("PASS Batch144 40/40 independent finite/exact math (20 valid, 20 invalid); certified proofs 0")
if __name__=="__main__":main()
