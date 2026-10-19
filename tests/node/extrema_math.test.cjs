"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const X=require("../../apps/web/lab/extrema_math.js");
const near=(a,b,tol=1e-8)=>assert.ok(Math.abs(a-b)<tol, `${a} != ${b}`);
test("quadratic convex minimum interior but maximum is endpoint",()=>{
 const r=X.analyze("quadratic",{a:1,b:-2,c:0,L:0,R:3});
 assert.equal(r.valid,true);near(r.globalMin.value,-1);near(r.globalMin.points[0],1);
 near(r.globalMax.value,3);near(r.globalMax.points[0],3);
 assert.deepEqual(r.stationary,[1]);assert.equal(r.closed,true);
});
test("concave quadratic can maximize at internal stationary",()=>{
 const r=X.analyze("quadratic",{a:-2,b:0,c:4,L:-1,R:2});
 near(r.globalMax.value,4);near(r.globalMax.points[0],0);
 near(r.globalMin.value,-4);near(r.globalMin.points[0],2);
});
test("constant function extrema attained at all points in interval",()=>{
 const r=X.analyze("quadratic",{a:0,b:0,c:7,L:-2,R:3});
 assert.equal(r.constant,true);assert.equal(r.globalMax.allPoints,true);
 assert.equal(r.globalMin.allPoints,true);
});
test("linear function does not invent stationary points",()=>{
 const r=X.analyze("quadratic",{a:0,b:-3,c:0,L:1,R:4});
 assert.deepEqual(r.stationary,[]);near(r.globalMax.value,-3);
 near(r.globalMin.value,-12);
});
test("cubic stationary local extrema can lose to endpoint globally",()=>{
 const r=X.analyze("cubic",{a:1,k:0,L:-2,R:3});
 assert.deepEqual(r.stationary,[-1,1]);
 near(r.globalMax.value,18);near(r.globalMax.points[0],3);
});
test("absolute cusp is candidate but not differentiable",()=>{
 const r=X.analyze("absolute",{a:2,h:1,k:0,L:-1,R:3});
 near(r.globalMin.value,0);assert.deepEqual(r.nondifferentiable,[1]);
 assert.deepEqual(r.stationary,[]);
 assert.deepEqual(r.globalMax.points,[-1,3]);
});
test("sine critical points include translated finite interval",()=>{
 const r=X.analyze("sine",{A:1,w:1,phi:0,k:0,L:0,R:Math.PI*2});
 near(r.globalMax.value,1);near(r.globalMax.points[0],Math.PI/2,1e-7);
 near(r.globalMin.value,-1);near(r.globalMin.points[0],Math.PI*1.5,1e-7);
});
test("sin with negative amplitude and frequency still finds correct extremum",()=>{
 const r=X.analyze("sine",{A:-2,w:-1,phi:0,k:1,L:0,R:2*Math.PI});
 near(r.globalMin.value,-1);near(r.globalMax.value,3);
 assert.ok(r.stationary.length>=2);
});
test("log defined only on whole positive closed interval",()=>{
 const r=X.analyze("log",{L:.5,R:4});
 near(r.globalMin.value,Math.log(.5));near(r.globalMax.value,Math.log(4));
 assert.deepEqual(r.stationary,[]);
 for(const input of [{L:0,R:4},{L:-2,R:4}]){
    const bad=X.analyze("log",input);
    assert.equal(bad.valid,false);assert.match(bad.error,/定义域|大于0/);
 }
});
test("inverted or zero-length intervals are invalid, never silently swapped",()=>{
 for(const v of [{L:2,R:2},{L:3,R:-1},{L:Infinity,R:2}]){
   const bad=X.analyze("quadratic",{a:1,b:0,c:0,...v});
   assert.equal(bad.valid,false);
 }
});
test("finite sampling never beats exact candidate extrema",()=>{
 const cases=[
 ["quadratic",{a:1.25,b:-.35,c:1,L:-2,R:3}],
 ["cubic",{a:-.4,k:2,L:-2,R:3}],
 ["absolute",{a:-1.5,h:.3,k:0,L:-3,R:3}],
 ["sine",{A:2,w:2,phi:.6,k:1,L:-2,R:2}],
 ["log",{L:.25,R:3}]
 ];
 for(const [kind,p] of cases){
   const r=X.analyze(kind,p);
   assert.ok(r.valid);
   for(let i=0;i<=1000;i++){
     const x=p.L+(p.R-p.L)*i/1000;
     const y=X.value(kind,p,x);
     assert.ok(y>=r.globalMin.value-1e-7,[kind,"min",x,y]);
     assert.ok(y<=r.globalMax.value+1e-7,[kind,"max",x,y]);
   }
 }
});
test("never infer global extrema from stationary points alone",()=>{
 const r=X.analyze("quadratic",{a:1,b:0,c:0,L:-1,R:4});
 assert.equal(r.globalMin.points[0],0);
 assert.equal(r.globalMax.points[0],4);
 assert.ok(r.candidates.some(c=>c.type==="endpoint"));
 assert.equal(r.isProof,false);
});
