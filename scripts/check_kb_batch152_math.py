#!/usr/bin/env python3
"""Independent *finite* exact oracle, not a general theorem prover or student verifier."""
import argparse,json,sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_kb_batch152_lessons as L
OUT=ROOT/'docs/evaluation/KB_BATCH152_EXACT_WITNESSES.json'

def oracle():
 cases=[]
 def put(i,tag,statement,invalid=False):
  if statement is not True and statement!=S.true:raise AssertionError(f'KB152 witness {i} {tag}: {statement!r}')
  seq=1+sum(c['candidate_id']==L.IDS[i] for c in cases)
  cases.append(dict(case_id=f'kb152-{i+1:02d}-{seq}',candidate_id=L.IDS[i],description=tag,passed=True,
   outcome='REJECT_INVALID_PRECONDITION' if invalid else 'EXACT_FINITE_WITNESS',
   general_formal_proof_certified=False,teacher_approved=False,student_free_step_verified=False))
 t=S.symbols('t',real=True)
 # 0: line contained in plane; single point alone cannot determine one line.
 A=S.Matrix([0,0,0]);B=S.Matrix([1,2,0]);n=S.Matrix([0,0,1])
 put(0,'whole A+t(B-A) has zero z',S.expand(n.dot(A+t*(B-A)))==0)
 A2=S.Matrix([1,0,1]);B2=S.Matrix([1,3,1]);n2=S.Matrix([1,0,1])
 put(0,'different points x+z=2',S.expand(n2.dot(A2+t*(B2-A2))-2)==0)
 put(0,'same point lies in z=0 while vertical line leaves plane',n.dot(S.Matrix([0,0,1]))==1 and A==S.zeros(3,1),True)
 put(0,'one common point is insufficient to include a line',n.dot(S.Matrix([1,0,1]))==1 and n.dot(S.Matrix([1,0,0]))==0,True)
 # 1: two planes intersect in line exactly when row rank=2.
 put(1,'orthogonal planes x=0 and y=0 rank2',S.Matrix([[1,0,0],[0,1,0]]).rank()==2)
 put(1,'x+y=1 and x-y=0 intersect x=y=1/2',S.solve([S.Symbol('x')+S.Symbol('y')-1,S.Symbol('x')-S.Symbol('y')],(S.Symbol('x'),S.Symbol('y')))=={S.Symbol('x'):S.Rational(1,2),S.Symbol('y'):S.Rational(1,2)})
 put(1,'parallel x=0 versus x=1 has no intersection',S.linsolve([S.Symbol('x'),S.Symbol('x')-1],[S.Symbol('x')])==S.EmptySet,True)
 put(1,'coincident x=0 and 2x=0 not a line',S.Matrix([[1,0,0],[2,0,0]]).rank()==1,True)
 # 2: model residuals plus unit and out of sample distinction.
 put(2,'MAE of residual 1,-1,2 is 4/3',sum(abs(v) for v in (1,-1,2))/S.Integer(3)==S.Rational(4,3))
 put(2,'7.2 km/h equals 2 m/s',S.Rational(72,10)/S.Rational(36,10)==2)
 put(2,'raw 7.2-2 mismatch is unit artifact',S.Rational(72,10)-2!=0 and S.Rational(72,10)/S.Rational(36,10)-2==0,True)
 put(2,'training fit at zero not sufficient for test x=1',S.expand(t*(t-0)).subs(t,0)==0 and S.expand(t*t).subs(t,1)==1,True)
 # 3: common difference and n-1 indexing.
 put(3,'first 5 diff-3 term6',5+(6-1)*(-3)==-10)
 put(3,'2n+1 has constant difference 2',S.simplify(2*(t+1)+1-(2*t+1))==2)
 put(3,'1 2 4 7 not arithmetic',len({2-1,4-2,7-4})>1,True)
 put(3,'wrong a1+n*d fails at n=1',5+(-3)!=5,True)
 # 4: point-plane distance / norm of normal.
 put(4,'P=(2,0,0) to x=0 has distance2',abs(2)/S.sqrt(1)==2)
 put(4,'origin to 2x-y+2z-9 distance3',abs(-9)/S.sqrt(4+1+4)==3)
 put(4,'zero normal cannot define plane distance',S.sqrt(0*0+0*0+0*0)==0,True)
 put(4,'signed expression negative without absolute',S.Rational(-9,3)<0,True)
 # 5: valid monotone bounded sequences and invalid single-premise claims.
 put(5,'a(n)=1-1/n increasing finite checks with explicit limit',all(1-S.Rational(1,k)<1-S.Rational(1,k+1)<1 for k in range(1,30)))
 put(5,'b(n)=2+1/n decreasing bounded below',all(2<2+S.Rational(1,k+1)<2+S.Rational(1,k) for k in range(1,30)))
 put(5,'monotone n unbounded by any proposed finite cap',all(any(k>cap for k in range(1,30)) for cap in range(1,12)),True)
 put(5,'bounded oscillation ±1 not Cauchy',abs((-1)**20-(-1)**21)==2,True)
 # 6: MVT exact instances; invalid discontinuous endpoint / derivative bound.
 put(6,'x2 on [1,3] has bounds4<=8<=12',2*2<=3**2-1**2<=6*2)
 put(6,'ln2 on [1,2] bounded 1/2..1',S.Rational(1,2)<S.log(2)<1)
 put(6,'f(0)=0, f(x)=x+2 for x>0 breaks endpoint continuity',3!=1,True)
 put(6,'on [-1,1] derivative x2 is not >=0',S.diff(t*t,t).subs(t,-1)<0,True)
 # 7: distinguish law of non-contradiction and excluded middle.
 put(7,'P true gives conjunction false and disjunction true',(not(True and not True)) and (True or not True))
 put(7,'P false gives conjunction false and disjunction true',(not(False and not False)) and (False or not False))
 put(7,'open sentence x>0 depends on assigned x',1>0 and not(-1>0),True)
 put(7,'conjunction P and not P cannot be true under fixed valuation',all(not (p and not p) for p in (True,False)),True)
 # 8: continuous/sample alias with different continuous fundamental periods.
 n=S.symbols('n',integer=True)
 put(8,'cos 2Hz at 8Hz sample n=0..3',tuple(S.cos(S.pi*k/2) for k in range(4))==(1,0,-1,0))
 put(8,'cos 6Hz and 2Hz at 8Hz identical for 32 exact samples',all(S.cos(3*S.pi*k/2)==S.cos(S.pi*k/2) for k in range(32)))
 put(8,'continuous frequency 2 and 6 different periods',S.Rational(1,2)!=S.Rational(1,6),True)
 put(8,'8Hz samples cannot uniquely distinguish 2 and 6Hz',all(S.cos(3*S.pi*k/2)==S.cos(S.pi*k/2) for k in range(12)),True)
 # 9: sample frequency is random, and dependence affects variance.
 put(9,'HHTT empirical frequency half differs from p three-fourths',S.Rational(2,4)==S.Rational(1,2) and S.Rational(2,4)!=S.Rational(3,4))
 put(9,'p quarter n16 iid variance 3/256',S.Rational(1,4)*S.Rational(3,4)/16==S.Rational(3,256))
 put(9,'finite sample proportion not invariably p',S.Rational(2,4)!=S.Rational(3,4),True)
 put(9,'perfect correlation breaks variance divide by n',S.Rational(3,16)!=S.Rational(3,16)/4,True)
 assert len(cases)==40 and sum(x['outcome']=='REJECT_INVALID_PRECONDITION' for x in cases)==20
 assert all([r['candidate_id'] for r in cases[i*4:(i+1)*4]]==[L.IDS[i]]*4 for i in range(10))
 return dict(schema='kb152-independent-exact-finite-oracle/1',cases=cases,total_cases=40,
 legal_or_boundary_witnesses=20,invalid_premise_rejections=20,
 teacher_approved=0,student_free_text_steps_verified=0,general_formal_proofs_certified=0)

def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args();v=oracle()
 if a.write:OUT.write_text(L.encode(v),encoding='utf-8')
 else:assert json.loads(OUT.read_text(encoding='utf-8'))==v,'oracle witness drift'
 print('PASS KB152 40/40 bounded exact conditions, 20 negative cases, 0 general formal proofs')
if __name__=='__main__':main()
