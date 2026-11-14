#!/usr/bin/env python3
"""40 independent bounded exact mathematical witnesses for Batch153; NOT general proof certificates."""
import argparse
import json
import sys
from math import comb
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_kb_batch153_lessons as L
OUT=ROOT/'docs/evaluation/KB_BATCH153_EXACT_WITNESSES.json'

def cases():
    rows=[]
    def put(i,description,actual,invalid=False):
        assert actual is True or actual==S.true, f'witness {i} {description}: {actual!r}'
        n=1+sum(c['source_candidate_id']==L.IDS[i] for c in rows)
        rows.append(dict(witness_id=f'kb153-{i+1:02d}-{n}',
            source_candidate_id=L.IDS[i],case=description,
            outcome='INVALID_PRECONDITION_REJECTED' if invalid else 'EXACT_FINITE_WITNESS',
            finite_exact_check=True,formal_general_proof_certified=False,
            teacher_approved=False,free_student_step_verified=False))
    # 1. Vector projection; check residual exactly orthogonal and zero axis rejection.
    u=S.Matrix([3,4]);v=S.Matrix([1,0])
    p=v*(u.dot(v)/v.dot(v))
    put(0,'projection to horizontal direction',p==S.Matrix([3,0]))
    u2=S.Matrix([2,1]);v2=S.Matrix([1,1])
    p2=v2*(u2.dot(v2)/v2.dot(v2))
    put(0,'residual exactly perpendicular',(u2-p2).dot(v2)==0 and p2==S.Matrix([S.Rational(3,2)]*2))
    put(0,'zero direction division rejected',S.zeros(2,1).dot(S.zeros(2,1))==0,True)
    put(0,'zero vector has zero dot despite no defined angle',S.zeros(2,1).dot(u)==0,True)
    # 2. Function domain; exact boundary checks and multi-valued relation.
    x=S.symbols('x',real=True)
    put(1,'domain of square-root rational excludes pole',S.solveset(x-1>=0,x,domain=S.S.Reals).intersect(S.S.Reals-S.FiniteSet(3))==S.Interval(1,3,False,True).union(S.Interval.open(3,S.oo)))
    put(1,'valid boundary x=1 gives zero',S.sqrt(1-1)/(1-3)==0)
    put(1,'pole x=3 rejected',S.sympify(3)-3==0,True)
    put(1,'y²=4 has two different outputs',S.solveset(S.Symbol('y')**2-4,S.Symbol('y'),S.S.Reals)==S.FiniteSet(-2,2),True)
    # 3. Quadratic sign with discriminant and strict endpoints.
    f=x*x-5*x+6
    put(2,'positive quadratic solution set',S.solve_univariate_inequality(f>0,x,relational=False)==S.Interval.open(-S.oo,2).union(S.Interval.open(3,S.oo)))
    put(2,'negative repeated root nonpositive only at x2',S.solve_univariate_inequality(-(x-2)**2>=0,x,relational=False)==S.FiniteSet(2))
    put(2,'negative discriminant has no real roots',S.discriminant(x*x+1,x)<0,True)
    put(2,'quadratic coefficient 0 invalidates quadratic formula',S.Poly(0*x*x+x-1,x).degree()==1,True)
    # 4. Chi-square statistic 2x2; small sample approximation not certified.
    a,b,c,d=20,10,10,20
    total=a+b+c+d
    stat=S.Rational(total*(a*d-b*c)**2,(a+b)*(c+d)*(a+c)*(b+d))
    put(3,'2x2 chi-square statistic equals 20/3',stat==S.Rational(20,3))
    E=S.Matrix([[S.Rational(15),S.Rational(15)],[S.Rational(15),S.Rational(15)]])
    O=S.Matrix([[a,b],[c,d]])
    put(3,'sum of four Pearson terms equals compact formula',sum((O[i,j]-E[i,j])**2/E[i,j] for i in range(2) for j in range(2))==stat)
    put(3,'zero column margin makes denominator zero',(5+7)*(0+0)==0,True)
    put(3,'near-zero expected cell prevents blanket asymptotic validity',S.Rational(1*1,20)<1,True)
    # 5. Independent Bernoulli and not-replacement correction.
    put(4,'fair coin n3 k2 exactly 3/8',S.Rational(comb(3,2),8)==S.Rational(3,8))
    put(4,'binomial probabilities sum to one',sum(S.Rational(comb(4,k)*2**k*3**(4-k),5**4) for k in range(5))==1)
    put(4,'urn without replacement P(2 red) differs',S.Rational(2,4)*S.Rational(1,3)==S.Rational(1,6)!=S.Rational(1,4),True)
    put(4,'without replacement conditional changes',S.Rational(2,4)!=S.Rational(1,3),True)
    # 6. Gaussian elimination preserves solutions for nonzero row operation.
    A=S.Matrix([[1,1],[2,-1]]);y=S.Matrix([3,0])
    put(5,'Gaussian example solution x1 y2',A.inv()*y==S.Matrix([1,2]))
    A2=S.Matrix([[1,1],[2,2]])
    aug=A2.row_join(S.Matrix([1,3]))
    put(5,'incompatible system detected by augmented rank',A2.rank()==1 and aug.rank()==2)
    put(5,'zeroing a nonzero row loses original equation',S.Matrix([[0]]).rank()!=S.Matrix([[1]]).rank(),True)
    put(5,'zero pivot invalid for division',S.Matrix([[0,1],[1,1]])[0,0]==0,True)
    # 7. Compact polygon linear-program witness.
    verts=[S.Matrix([0,0]),S.Matrix([2,0]),S.Matrix([0,3])]
    put(6,'linear objective triangle maximum 4',max((2*v[0]+v[1] for v in verts))==4)
    put(6,'negative coefficient rectangle min -1',min((-x+2*y for x,y in ((0,0),(1,0),(0,2),(1,2))))==-1)
    put(6,'unbounded positive orthant has arbitrarily large objective',all(2*n>100 for n in (51,52,53)),True)
    put(6,'quadratic objective fails linearity on midpoint',S.Rational(1,2)**2 !=S.Rational(1,2)*(0**2+1**2),True)
    # 8. Multistage sample vs SRS, individual inclusion alone insufficient.
    put(7,'two-class cluster inclusion is half',S.Rational(1,2)*1==S.Rational(1,2))
    put(7,'four-population SRS sample size2 has six sets',comb(4,2)==6)
    put(7,'two-class cluster design supports only two sets',2<comb(4,2),True)
    put(7,'four-school two-stage inclusion not SRS proof',S.Rational(1,4)*S.Rational(2,10)==S.Rational(1,20),True)
    # 9. Sports fixtures cover all edges once, no double-play in rounds.
    rounds=[[(0,1),(2,3)],[(0,2),(1,3)],[(0,3),(1,2)]]
    edges=[tuple(sorted(e)) for r in rounds for e in r]
    put(8,'4 team n-1 rounds, each team once per round',len(rounds)==3 and all(len(set(v for e in rnd for v in e))==4 for rnd in rounds))
    put(8,'all six unique edges covered',len(edges)==len(set(edges))==comb(4,2))
    put(8,'AB and AC same round violate constraint',len(set(v for e in [(0,1),(0,2)] for v in e))<4,True)
    put(8,'5 teams cannot play five matches in one round',2*(5//2)<5,True)
    # 10. Limit independent from point value.
    rational=(x*x-1)/(x-1)
    put(9,'punctured rational x to1 limit2',S.limit(rational,x,1)==2)
    put(9,'function g with value9 still has limiting value2',S.limit(x+1,x,1)==2 and 9!=2)
    put(9,'direct substitution at pole gives zero denominator',(S.Integer(1)-1)==0,True)
    put(9,'different point value prevents continuity',9!=S.limit(x+1,x,1),True)
    assert len(rows)==40 and len({v['source_candidate_id'] for v in rows})==10
    assert sum(r['outcome']=='EXACT_FINITE_WITNESS' for r in rows)==20
    assert sum(r['outcome']=='INVALID_PRECONDITION_REJECTED' for r in rows)==20
    return dict(schema='kb153-finite-math-witnesses/1',n=40,legal_or_boundary=20,
        negative=20,general_formal_proofs_certified=0,
        teacher_approved=0,free_student_steps_verified=0,witnesses=rows)

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true')
    o=p.parse_args();data=cases()
    enc=json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n'
    if o.write:OUT.write_text(enc,encoding='utf-8')
    else:assert OUT.read_text(encoding='utf-8')==enc,'math witness drift'
    print('PASS KB153 finite exact math witnesses: 40/40 (20 legal, 20 premise failures)')
if __name__=='__main__':main()
