"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const P=require("../../apps/web/lab/probability_math.js");
const near=(a,b,eps=1e-9)=>assert.ok(Math.abs(a-b)<=eps*Math.max(1,Math.abs(a),Math.abs(b)),`${a} vs ${b}`);
test("combination and permutation obey cardinality and degenerate counts",()=>{
 assert.equal(P.choose(5,2),10);assert.equal(P.choose(0,0),1);
 assert.equal(P.choose(6,7),0);assert.equal(P.permutations(5,2),20);
 assert.equal(P.permutations(5,0),1);assert.equal(P.choose(50,25),126410606437752);
 assert.throws(()=>P.choose(-1,0),/范围|非负整数/);
});
test("binomial n=0, p=0/1 and normalization",()=>{
 assert.equal(P.binomial(0,.3,0),1);
 assert.equal(P.binomial(5,0,0),1);
 assert.equal(P.binomial(5,1,5),1);
 assert.equal(P.binomial(5,0,1),0);
 assert.equal(P.binomial(5,1,3),0);
 near(Array.from({length:11},(_,k)=>P.binomial(10,.37,k)).reduce((a,b)=>a+b,0),1);
 assert.deepEqual(P.binomialSummary(10,.3).mean,3);
 near(P.binomialSummary(10,.3).variance,2.1);
});
test("binomial exact small mass and invalid probability",()=>{
 near(P.binomial(4,.5,2),6/16);
 near(P.binomial(3,.3,0),.343);
 assert.throws(()=>P.binomial(3,-.1,1),/概率|0|1/);
 assert.throws(()=>P.binomial(3,1.1,1),/概率|0|1/);
});
test("hypergeometric probability without replacement",()=>{
 near(P.hypergeometric(10,4,3,2),P.choose(4,2)*P.choose(6,1)/P.choose(10,3));
 near(Array.from({length:4},(_,k)=>P.hypergeometric(10,4,3,k)).reduce((a,b)=>a+b,0),1);
 assert.equal(P.hypergeometric(10,1,5,4),0);
 assert.equal(P.hypergeometric(10,4,0,0),1);
 near(P.hypergeometricSummary(10,4,3).mean,1.2);
 near(P.hypergeometricSummary(10,4,3).variance,3*(.4)*(.6)*(10-3)/(10-1));
});
test("hypergeometric rejects impossible population or sample",()=>{
 assert.throws(()=>P.hypergeometric(10,11,2,1),/范围|样本|总体/);
 assert.throws(()=>P.hypergeometric(8,3,9,2),/范围|样本|总体/);
});
test("probability tree leaves add to one and encode conditional branches",()=>{
 const t=P.twoStageTree(.6,.2,.7);
 near(t.leaves.reduce((s,v)=>s+v,0),1);
 near(t.leaves[0],.12);
 near(t.leaves[2],.28);
 near(t.probabilitySecond,.4);
 assert.equal(t.independent,false);
 assert.equal(P.twoStageTree(.5,.2,.2).independent,true);
});
test("2x2 joint probabilities and conditional-zero event",()=>{
 const j=P.jointEvents([.2,.3,.1,.4]);
 near(j.pA,.5);near(j.pB,.3);near(j.pAB,.2);
 near(j.pA_given_B,2/3);
 assert.equal(j.mutuallyExclusive,false);
 assert.equal(P.jointEvents([0,.5,.5,0]).mutuallyExclusive,true);
 const z=P.jointEvents([0,.3,0,.7]);
 assert.equal(z.pA_given_B,null);
 assert.throws(()=>P.jointEvents([.6,.6,0,0]),/归一|总和|概率/);
});
test("normal pdf valid density not event probability",()=>{
 near(P.normalPdf(0,0,1),1/Math.sqrt(2*Math.PI));
 near(P.normalPdf(1,0,1),P.normalPdf(-1,0,1));
 assert.ok(P.normalPdf(10,0,1)<1e-20);
 assert.throws(()=>P.normalPdf(0,0,0),/标准差|正/);
});
test("statistics mean, median and sample/population variance use proper denominators",()=>{
 const x=P.statistics([1,2,3,4]);
 near(x.mean,2.5);near(x.median,2.5);
 near(x.populationVariance,1.25);
 near(x.sampleVariance,5/3);
 const one=P.statistics([7]);
 near(one.mean,7);near(one.populationVariance,0);
 assert.equal(one.sampleVariance,null);
});
test("stable mean/variance with large data offset",()=>{
 const x=P.statistics([1e10+1,1e10+2,1e10+3]);
 near(x.mean,1e10+2,1e-14);
 near(x.populationVariance,2/3,1e-7);
});
test("linear regression exact slope and singular cases",()=>{
 const r=P.regression([1,2,3],[2,4,6]);
 near(r.slope,2);near(r.intercept,0);near(r.r,1);
 const deg=P.regression([1,1,1],[1,2,3]);
 assert.equal(deg.valid,false);
 const flat=P.regression([1,2,3],[2,2,2]);
 assert.equal(flat.valid,true);near(flat.slope,0);
 assert.equal(flat.r,null);
});
test("seeded Bernoulli simulation deterministic and bounded frequency",()=>{
 const a=P.simulateBernoulli(.3,1000,1234),b=P.simulateBernoulli(.3,1000,1234);
 assert.deepEqual(a,b);assert.ok(a.frequency>=0&&a.frequency<=1);
 assert.equal(a.trials,1000);assert.equal(a.theoreticalProbability,.3);
 assert.equal(P.simulateBernoulli(0,100,1).successes,0);
 assert.equal(P.simulateBernoulli(1,100,1).successes,100);
 assert.throws(()=>P.simulateBernoulli(.4,6000,12),/次数|范围/);
});
test("edge invalid sample and forbidden operations explicitly rejected",()=>{
 assert.throws(()=>P.statistics([]),/样本|空/);
 assert.throws(()=>P.statistics([NaN]),/有限|数/);
 assert.throws(()=>P.regression([1,2],[1]),/长度|配对/);
});

test("running Bernoulli frequencies match the final simulation",()=>{
 const s=P.simulateBernoulli(.37,250,812);
 const line=P.bernoulliTrajectory(.37,250,812);
 assert.equal(line.length,250);
 assert.equal(line.at(-1).successes,s.successes);
 assert.equal(line.at(-1).frequency,s.frequency);
 assert.equal(line[0].trials,1);
 assert.ok(line.every(row=>row.frequency>=0&&row.frequency<=1));
});
test("normal interval mass is approximate integration not density height",()=>{
 const p=P.normalInterval(-1,1,0,1);
 assert.ok(Math.abs(p-.6826894921)<.00001);
 assert.equal(P.normalInterval(2,2,0,1),0);
 assert.throws(()=>P.normalInterval(2,1,0,1),/区间|L<R/);
});

test("sample statistics identifies tied modes and no repeated mode",()=>{
 const x=P.statistics([1,1,2,2,3]);
 assert.deepEqual(x.modes,[1,2]);
 assert.deepEqual(P.statistics([1,2,3]).modes,[]);
 const c=P.statistics([4,4,4]);
 assert.deepEqual(c.modes,[4]);
 assert.equal(c.sampleStdDev,0);
});
test("zero-probability conditioning events are undefined, not numeric branch probabilities",()=>{
 const impossible=P.twoStageTree(0,.4,.7);
 assert.equal(impossible.conditionalGivenFirst,null);
 assert.equal(impossible.conditionalGivenNotFirst,.7);
 const certain=P.twoStageTree(1,.4,.7);
 assert.equal(certain.conditionalGivenFirst,.4);
 assert.equal(certain.conditionalGivenNotFirst,null);
 near(impossible.leaves.reduce((s,x)=>s+x,0),1);
 near(certain.leaves.reduce((s,x)=>s+x,0),1);
});
test("binomial mass always normalizes on a seeded parameter grid",()=>{
  for(const n of [0,1,2,5,10,20,25]){
    for(const p of [0,.001,.1,.25,.5,.8,.999,1]){
      const data=P.binomialSummary(n,p);
      near(data.total,1,1e-9);
      assert.equal(data.pmf.length,n+1);
      assert.ok(data.pmf.every(v=>Number.isFinite(v)&&v>=0&&v<=1+1e-12));
      near(data.mean,n*p);
      near(data.variance,n*p*(1-p));
    }
  }
});
test("finite-population hypergeometric distributions normalize across valid supports",()=>{
  for(const N of [1,2,3,7,15,30]){
    for(const K of [0,Math.floor(N/2),N]){
      for(const n of [0,Math.floor(N/2),N]){
        const r=P.hypergeometricSummary(N,K,n);
        near(r.total,1,1e-9);
        assert.ok(r.pmf.every(v=>Number.isFinite(v)&&v>=0&&v<=1+1e-12));
      }
    }
  }
});
test("normal probability tails integrate to about one and point intervals are zero",()=>{
  for(const mu of [-2,0,3]){
    for(const sigma of [.3,1,2.5]){
      near(P.normalInterval(mu-8*sigma,mu+8*sigma,mu,sigma),1,1e-6);
      assert.equal(P.normalInterval(mu,mu,mu,sigma),0);
      near(P.normalInterval(mu-sigma,mu,mu,sigma),
        P.normalInterval(mu,mu+sigma,mu,sigma),1e-6);
    }
  }
});
