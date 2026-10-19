"use strict";
const test=require('node:test');
const assert=require('node:assert/strict');
const S=require('../../apps/web/lab/sequences_math.js');
const near=(a,b,eps=1e-8)=>assert.ok(Math.abs(a-b)<=eps*Math.max(1,Math.abs(a),Math.abs(b)),`${a} != ${b}`);

test('arithmetic first term and n indexing',()=>{
  assert.deepEqual(S.arithmetic({a1:3,d:2},5).terms,[3,5,7,9,11]);
  assert.deepEqual(S.arithmetic({a1:3,d:2},5).sums,[3,8,15,24,35]);
  assert.equal(S.arithmetic({a1:9,d:0},1).terms[0],9);
});
test('geometric q=1 exactly uses n*a1',()=>{
  const x=S.geometric({a1:3,q:1},12);
  assert.equal(x.terms[11],3);assert.equal(x.sums[11],36);
  assert.equal(x.special,'Q_ONE');
});
test('geometric q=0 and q=-1',()=>{
  let x=S.geometric({a1:7,q:0},5);
  assert.deepEqual(x.terms,[7,0,0,0,0]);
  assert.deepEqual(x.sums,[7,7,7,7,7]);
  assert.equal(x.special,'Q_ZERO');
  x=S.geometric({a1:2,q:-1},6);
  assert.deepEqual(x.terms,[2,-2,2,-2,2,-2]);
  assert.deepEqual(x.sums,[2,0,2,0,2,0]);
  assert.equal(x.special,'Q_NEG_ONE');
});
test('near-unity geometric uses stable finite recurrence (not 0/0 closed form)',()=>{
  const q=1+1e-10,a1=2,n=24,x=S.geometric({a1,q},n);
  assert.equal(x.special,'GENERAL');
  let sum=0,value=a1;
  for(let i=0;i<n;i++){sum+=value;value*=q}
  near(x.sums[n-1],sum);
  assert.ok(x.sums[n-1]>48);
});
test('negative ratio alternation and zero initial term',()=>{
  const x=S.geometric({a1:-2,q:-2},5);
  assert.deepEqual(x.terms,[-2,4,-8,16,-32]);
  assert.deepEqual(x.sums,[-2,2,-6,10,-22]);
  assert.deepEqual(S.geometric({a1:0,q:2},5).terms,[0,0,0,0,0]);
});
test('linear recurrence differs from arithmetic when r !=1',()=>{
  const x=S.linearRecurrence({a1:1,r:2,c:1},5);
  assert.deepEqual(x.terms,[1,3,7,15,31]);
  assert.deepEqual(x.sums,[1,4,11,26,57]);
  assert.deepEqual(S.linearRecurrence({a1:7,r:1,c:-2},4).terms,[7,5,3,1]);
  assert.deepEqual(S.linearRecurrence({a1:5,r:0,c:3},4).terms,[5,3,3,3]);
});
test('two-term recurrence uses two initial conditions and correct partial sums',()=>{
  assert.deepEqual(S.twoTermRecurrence({a1:1,a2:1},8).terms,[1,1,2,3,5,8,13,21]);
  assert.deepEqual(S.twoTermRecurrence({a1:0,a2:2},5).sums,[0,2,4,8,14]);
});
test('partial sums equal direct summation for 30 seeded samples',()=>{
  for(let seed=1;seed<=30;seed++){
    const a1=(seed%7)-3,q=(seed%9-4)/4, n=10;
    const x=S.geometric({a1,q},n);
    let sum=0;
    for(let i=0;i<n;i++){sum+=x.terms[i];near(sum,x.sums[i],1e-10)}
  }
});
test('comparison is finite, uses magnitude, and not an asymptotic proof',()=>{
  const x=S.compare({a1:1,d:1,q:2},10);
  assert.equal(x.arithmetic[0],1);
  assert.equal(x.geometric[0],1);
  assert.equal(x.geometric[9],512);
  assert.ok(x.firstMagnitudeCrossover>=2);
  assert.equal(x.notInfiniteProof,true);
  const neg=S.compare({a1:1,d:1,q:-2},10);
  assert.ok(neg.firstMagnitudeCrossover>0);
});
test('invalid n and nonfinite parameters rejected rather than NaN plotted',()=>{
  for(const n of [0,-1,1.5,31,NaN,Infinity]){
    assert.throws(()=>S.geometric({a1:2,q:1},n),/n|正整数|项数/);
  }
  assert.throws(()=>S.geometric({a1:1,q:Infinity},4),/参数|有限/);
  assert.throws(()=>S.twoTermRecurrence({a1:NaN,a2:2},3),/参数|有限/);
});
test('numerical overflow is explicit without Infinity or fabricated zeros',()=>{
  assert.throws(()=>S.geometric({a1:1e10,q:1e10},10),/范围|溢出|过大/);
});
test('no inferred limit of infinite series from finite display',()=>{
  const g=S.geometric({a1:1,q:0.5},12);
  assert.equal(g.finiteOnly,true);
  assert.equal(g.terms.length,12);
  assert.equal(g.infiniteSumProven,false);
});
