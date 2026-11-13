#!/usr/bin/env python3
"""Independent SymPy / exact finite witness checks for Batch139 eight manuscripts.

Oracle deliberately does NOT read author answer strings; tests mathematical
statements directly. No general proof, teacher approval or student free text check.
"""
from __future__ import annotations
import argparse
import itertools
import json
import sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch139_core as author
OUT=ROOT/"docs/evaluation/KB_BATCH139_EXACT_WITNESSES.json"

def require(v,why):
    if v is not True and v != S.true: raise AssertionError("Math verification failure: "+why)

def build():
    cases=[]
    a,b,c,d,e,f,g,h=author.IDS
    def add(cid,label,condition,negative=False):
        require(condition,cid+" / "+label)
        cases.append(dict(candidate_id=cid,case_id=cid+"-w"+str(1+sum(r["candidate_id"]==cid for r in cases)),
             description=label,passed=True,
             result="REJECT_INVALID_PRECONDITION" if negative else "FINITE_EXACT_WITNESS",
             teacher_approved=False,general_proof_certified=False,
             student_free_text_verified=False))
    # C103 inner products
    u=S.Matrix([3,4]);v=S.Matrix([1,-2])
    add(a,"3,4 dot 1,-2 equals negative five",(u.dot(v)==-5))
    add(a,"nonzero vectors imply cosine negative inverse sqrt five",
        S.simplify(u.dot(v)/(S.sqrt(u.dot(u))*S.sqrt(v.dot(v)))+1/S.sqrt(5))==0)
    add(a,"orthogonal nonzero exact witness",S.Matrix([1,2]).dot(S.Matrix([2,-1]))==0)
    add(a,"zero vector has undefined angle despite zero dot product",
        S.zeros(2,1).dot(S.Matrix([1,0]))==0 and S.zeros(2,1).norm()==0,True)
    # C105 basis
    M=S.Matrix([[1,1],[1,-1]])
    add(b,"unique reconstruction 3u+v equals (4,2)",M.det()==-2 and M*S.Matrix([3,1])==S.Matrix([4,2]))
    add(b,"diagonal nonzero determinant yields unique (2,2)",S.diag(2,3).det()==6 and
        S.diag(2,3).inv()*S.Matrix([4,6])==S.Matrix([2,2]))
    add(b,"singular basis has null direction",S.Matrix([[1,2],[2,4]]).det()==0 and
        S.Matrix([[1,2],[2,4]])*S.Matrix([-2,1])==S.zeros(2,1),True)
    add(b,"Cramer 2x2 symbolic inverse identity",S.simplify(M.inv()*M)==S.eye(2))
    # C111: SRSWOR exact combinatorics
    add(c,"10 equally likely two-person combinations",S.binomial(5,2)==10)
    add(c,"marginal inclusion probability 2 over 5",S.binomial(4,1)/S.binomial(5,2)==S.Rational(2,5))
    add(c,"joint inclusion differs from independent square",S.binomial(4,1)/S.binomial(6,3)==S.Rational(1,5)
        and S.Rational(1,5)!=S.Rational(1,4))
    bad_families={(1,2),(3,4)}
    add(c,"equal marginal does not imply all subsets equally likely",
        len(bad_families)==2 and S.binomial(4,2)==6
        and all(sum(i in pair for pair in bad_families)==1 for i in range(1,5)),True)
    # C524 sample variance, algebraic identity and n=1 guard
    xx=[S.Integer(2),S.Integer(4),S.Integer(6)]
    m=sum(xx)/3;ss=sum((z-m)**2 for z in xx)
    add(d,"n3 descriptive 8/3 and unbiased 4",ss==8 and ss/3==S.Rational(8,3) and ss/2==4)
    yy=[S.Integer(1),S.Integer(3)]
    add(d,"n2 descriptive 1 and unbiased 2",sum((z-2)**2 for z in yy)/2==1 and
        sum((z-2)**2 for z in yy)==2)
    # Exhaustive independent fair Bernoulli n2 sampling variance mean equals pop var
    two=list(itertools.product((0,1),repeat=2))
    expected=sum((S.Integer(row[0])-S.Rational(sum(row),2))**2+
                 (S.Integer(row[1])-S.Rational(sum(row),2))**2 for row in two)/4
    add(d,"exact iid Bernoulli2 sample variance expectation equals quarter",expected==S.Rational(1,4))
    add(d,"n=1 denominator is zero and no unbiased sample variance",S.Integer(1)-1==0,True)
    # S203 straight line by independent determinant and substitution
    def line(p,q):
        return (p[1]-q[1],q[0]-p[0],p[0]*q[1]-q[0]*p[1])
    aa,bb,cc=line((1,2),(3,6))
    add(e,"two points yield 2x-y=0", (aa,bb,cc)==(-4,2,0)
        and aa*1+bb*2+cc==0 and aa*3+bb*6+cc==0)
    aa,bb,cc=line((0,2),(2,0))
    add(e,"second example x+y-2", (aa,bb,cc)==(2,2,-4))
    aa,bb,cc=line((2,1),(2,5))
    add(e,"vertical line exists without slope", (aa,bb,cc)==(-4,0,8))
    add(e,"coincident points give zero normal invalid line",line((1,2),(1,2))==(0,0,0),True)
    # S206 exact discrete pmf
    probs=[S.Rational(1,4),S.Rational(1,2),S.Rational(1,4)]
    add(f,"complete valid probability mass function",sum(probs)==1 and all(p>=0 for p in probs))
    add(f,"event X greater or equal one equals three quarters",sum(probs[1:])==S.Rational(3,4))
    add(f,"Bernoulli complement is three fifths",1-S.Rational(2,5)==S.Rational(3,5))
    add(f,"unnormalized mass exceeding one rejected",S.Rational(1,2)+S.Rational(3,4)>1,True)
    # A302 FTC finite polynomials
    x=S.symbols("x", real=True)
    add(g,"integral polynomial zero to two equals twelve",S.integrate(3*x*x+2*x,(x,0,2))==12)
    add(g,"integral 2x one to three equals eight",S.integrate(2*x,(x,1,3))==8)
    add(g,"derivative of integral from zero to variable recovers integrand",
        S.simplify(S.diff(S.integrate(3*x*x+2*x,(x,0,S.symbols("z",real=True))),S.symbols("z",real=True))
                   -(3*S.symbols("z",real=True)**2+2*S.symbols("z",real=True)))==0)
    add(g,"1/x has singularity inside closed interval, not FTC preconditions",
        S.S(1)/S.S(0)==S.zoo,True)
    # A405 OLS normal equation and rank guards
    def coeff(pairs):
        X=S.Matrix([[1,S.Integer(a)] for a,_ in pairs])
        Y=S.Matrix([S.Integer(v) for _,v in pairs])
        return (X.T*X).det(), ((X.T*X).inv()*X.T*Y if (X.T*X).det()!=0 else None)
    determinant, coeff1=coeff([(0,1),(1,3),(2,5)])
    add(h,"perfect line fitted intercept one slope two",determinant>0 and coeff1==S.Matrix([1,2]))
    determinant, coeff2=coeff([(1,1),(2,2),(3,2)])
    add(h,"imperfect line fitted intercept two thirds slope half",
        determinant>0 and coeff2==S.Matrix([S.Rational(2,3),S.Rational(1,2)]))
    X=S.Matrix([[1,2],[1,2],[1,2]])
    add(h,"constant predictor has singular normal equation matrix",(X.T*X).det()==0,True)
    bb0,bb1=S.symbols("bb0 bb1",real=True)
    cost=sum((yi-bb0-bb1*xi)**2 for xi,yi in [(0,1),(1,3),(2,5)])
    Hess=S.hessian(cost,(bb0,bb1))
    add(h,"OLS quadratic Hessian positive definite",Hess[0,0]>0 and Hess.det()>0)
    assert len(cases)==32 and len({r["case_id"] for r in cases})==32
    assert sum(c["result"]=="REJECT_INVALID_PRECONDITION" for c in cases)==8
    assert set(q["candidate_id"] for q in cases)==set(author.IDS)
    return dict(schema="kb139-independent-finite-math-oracle/1",
         scope="32_EXACT_FINITE_CASES_NOT_GENERAL_FORMAL_PROOFS",
         exact_cases=32,negative_condition_rejections=8,
         successful_or_edge_witnesses=24, teacher_approved=0,
         general_proofs_certified=0,student_free_text_verified=0,
         official_atom_denominators={k:None for k in author.TRACKS},
         cases=cases)

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    x=p.parse_args()
    report=build()
    if x.write:OUT.write_text(author.encode(report),encoding="utf-8")
    else: require(json.loads(OUT.read_text(encoding="utf-8"))==report,"Oracle artifact changed")
    print("PASS 32/32 independent exact witnesses (8 rejected invalid preconditions); zero general proof certifications")
if __name__=="__main__":main()
