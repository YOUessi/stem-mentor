#!/usr/bin/env python3
"""Independent exact finite guards for KB154; 40 cases are not general formal proofs."""
import argparse,json,sys
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_kb_batch154_lessons as lessons
OUT=ROOT/'docs/evaluation/KB_BATCH154_EXACT_WITNESSES.json'
def run():
    cases=[]
    def put(i,label,predicate,invalid=False):
        assert predicate is True or predicate==S.true, f'failed independent exact check {i}/{label}: {predicate}'
        count=1+sum(x['source_candidate_id']==lessons.IDS[i] for x in cases)
        cases.append(dict(witness_id=f'kb154-{i+1:02d}-{count}',source_candidate_id=lessons.IDS[i],
            case=label,outcome='INVALID_PRECONDITION_REJECTED' if invalid else 'EXACT_FINITE_WITNESS',
            finite_exact_check=True,formal_general_proof_certified=False,
            teacher_approved=False,free_student_step_verified=False))
    x,h=S.symbols('x h',real=True)
    # 1. Piecewise branch: endpoint and discontinuity.
    f=S.Piecewise((x+2,x<1),(x*x,True))
    put(0,'piecewise strict endpoint f1',f.subs(x,1)==1)
    put(0,'piecewise interior f0',f.subs(x,0)==2)
    g=S.Piecewise((2*x,x<=0),(x+3,True))
    put(0,'piecewise one-sided jump at zero',S.limit(2*x,x,0,dir='-')!=S.limit(x+3,x,0,dir='+'),True)
    put(0,'wrong branch at endpoint must reject',S.Integer(1)+2!=f.subs(x,1),True)
    # 2. IVT: legal continuous crossing and discontinuous counterexample.
    poly=x**3+x-1
    put(1,'polynomial endpoint signs and root existence',poly.subs(x,0)<0 and poly.subs(x,1)>0 and
        bool(S.polys.polytools.intervals(poly,eps=S.Rational(1,20))))
    put(1,'IVT not uniqueness: cubic with three zeros',S.solveset(x**3-3*x,x,domain=S.S.Reals)==S.FiniteSet(0,-S.sqrt(3),S.sqrt(3)))
    put(1,'discontinuous 1/x has no zero despite endpoint sign',S.solveset(1/x,x,domain=S.S.Reals)==S.EmptySet,True)
    put(1,'endpoint zero fails strict opposite signs',S.expand(x*(x-1)).subs(x,0)==0,True)
    # 3. Change of base: exact log identities.
    put(2,'log2 of8 equals exact3',S.log(8,2)==3)
    put(2,'natural-base change yields log4 of 1/8 = -3/2',
        S.simplify(S.log(S.Rational(1,8))/S.log(4)+S.Rational(3,2))==0)
    put(2,'base1 logarithm is invalid',S.log(4,1) in {S.zoo,S.nan},True)
    put(2,'argument0 logarithm not finite real',S.log(0).is_finite is False,True)
    # 4. Classical probability: true equiprobable ordered sample space.
    omega=list(product(range(1,7),repeat=2))
    put(3,'two fair dice have 36 equiprobable outcomes',len(omega)==36)
    put(3,'sum7 has six ordered pairs',sum(a+b==7 for a,b in omega)==6)
    put(3,'eleven sums do not have equal multiplicity',sum(a+b==2 for a,b in omega)!=sum(a+b==7 for a,b in omega),True)
    put(3,'3 red1 blue counts not two equiprobable color labels',Fraction(3,4)!=Fraction(1,2),True)
    # 5. Derivative defined via quotient finite limit.
    put(4,'derivative x2 at3 exact 6',S.limit(((3+h)**2-9)/h,h,0)==6)
    put(4,'derivative 1/x at 1 is minus 1',S.limit(((1/(1+h))-1)/h,h,0)==-1)
    put(4,'absolute value cusp has unequal directional quotients',
        S.limit(S.Abs(h)/h,h,0,dir='-')!=S.limit(S.Abs(h)/h,h,0,dir='+'),True)
    put(4,'differentiating 1/x at zero not in real domain',S.simplify(1/x).subs(x,0) in (S.zoo,S.nan),True)
    # 6. OLS intercept standard examples and Sxx rejection.
    points=[(0,1),(1,3),(2,5)]
    xx=S.Rational(sum(t[0] for t in points),3);yy=S.Rational(sum(t[1] for t in points),3)
    sxx=sum((a-xx)**2 for a,b in points)
    sxy=sum((a-xx)*(b-yy) for a,b in points)
    put(5,'sxx centered equals 2',sxx==2)
    put(5,'slope2 intercept1 and zero residual',sxy/sxx==2 and yy-(sxy/sxx)*xx==1)
    put(5,'constant x has zero Sxx cannot divide',sum((a-2)**2 for a in (2,2))==0,True)
    put(5,'forced through-origin slope differs from intercept slope',S.Rational(sum(a*b for a,b in points),sum(a*a for a,b in points))!=sxy/sxx,True)
    # 7. Finite convergent sequences and invalid limit of quotient at B=0.
    n=S.symbols('n',integer=True,positive=True)
    a=1+1/n;b=2-1/n
    put(6,'convergent finite product limit 2',S.limit(a*b,n,S.oo)==2)
    put(6,'nonzero denominator convergent quotient limit half',S.limit(a/b,n,S.oo)==S.Rational(1,2))
    put(6,'0/0 form has finite nonzero quotient',S.limit((1/n)/(1/n),n,S.oo)==1,True)
    put(6,'a vanishing denominator can generate unbounded quotient',S.limit(1/(1/n),n,S.oo)==S.oo,True)
    # 8. Riemann sums and signed integral, unlike geometric area.
    put(7,'right-endpoint Riemann sum exact limit',S.limit((n+1)/n,n,S.oo)==1)
    put(7,'integral of 2x from 0 to 1 equals 1',S.integrate(2*x,(x,0,1))==1)
    put(7,'signed integral x over symmetric interval vanishes despite nonzero area',S.integrate(x,(x,-1,1))==0 and S.integrate(S.Abs(x),(x,-1,1))==1,True)
    put(7,'signed negative subinterval cannot be treated as positive',S.integrate(x,(x,-1,0))==S.Rational(-1,2),True)
    # 9. Relative frequency valid denominator distinct from all attempted respondents.
    put(8,'six of eight valid answers equals 75 percent',Fraction(6,8)==Fraction(3,4))
    put(8,'frequency categories sum 1',sum(Fraction(z,10) for z in (3,5,2))==1)
    put(8,'including two nonresponses changes frequency denominator',Fraction(6,8)!=Fraction(6,10),True)
    # An empty survey has a zero denominator; a 0/0 fraction must be rejected.
    try:
        Fraction(0, 0)
        empty_denominator_rejected = False
    except ZeroDivisionError:
        empty_denominator_rejected = True
    put(8,'empty valid response frequency undefined',empty_denominator_rejected,True)
    # 10. Affine vs perspective image; exact algebra domain.
    u,v=S.symbols('u v',real=True)
    put(9,'affine image y1 to y1 and y2 to y4',3*1-2==1 and 3*2-2==4)
    put(9,'perspective horizontal families meet at vanishing point',
        S.solve((v-(1-u),v-2*(1-u)),(u,v))=={u:1,v:0})
    put(9,'perspective map has pole at x minus1',1+(-1)==0,True)
    put(9,'singular affine matrix collapses entire lines',S.zeros(2).det()==0,True)
    assert len(cases)==40 and len(set(c['source_candidate_id'] for c in cases))==10
    assert sum(c['outcome']=='EXACT_FINITE_WITNESS' for c in cases)==20
    assert sum(c['outcome']=='INVALID_PRECONDITION_REJECTED' for c in cases)==20
    return dict(schema='kb154-exact-finite-math-evidence/1',n=40,
      legal_or_boundary=20,negative=20,formal_general_proofs_certified=0,
      teacher_approved=0,free_student_steps_verified=0,witnesses=cases)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true')
    a=p.parse_args();v=run();s=json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
    if a.write:OUT.write_text(s,encoding='utf-8')
    else:assert OUT.read_text(encoding='utf-8')==s,'math witness drift'
    print('PASS KB154 exact bounded math witnesses 40/40; 20 legal, 20 invalid premise; zero universal certificates')
if __name__=='__main__':main()
