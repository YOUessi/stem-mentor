'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const modulePath=path.resolve(__dirname,'../../apps/web/lab/exploration_math.js');
const exists=fs.existsSync(modulePath);
test('required pure mathematics module exists',()=>assert.ok(exists,'exploration_math.js must be implemented'));
const M=exists?require(modulePath):null;
const T=(name,fn)=>test(name,{skip:!M},fn);
const close=(a,b,e=1e-9)=>assert.ok(Number.isFinite(a)&&Math.abs(a-b)<=e,`${a} != ${b}`);
const vec=(a,b,e=1e-9)=>{assert.equal(a.length,b.length);a.forEach((v,i)=>close(v,b[i],e))};

T('vector addition subtraction scale dot and length',()=>{
 const v=M.vectorMetrics([3,4],[-4,3],-2);
 assert.equal(v.status,'OK');vec(v.sum,[-1,7]);vec(v.difference,[7,1]);vec(v.scaled,[-6,-8]);
 close(v.dot,0);close(v.lengthA,5);close(v.lengthB,5);close(v.angleDegrees,90);
});
T('orthogonal projection uses signed dot product and orthogonal residual',()=>{
 const v=M.vectorMetrics([3,4],[2,0],1);
 vec(v.projection,[3,0]);vec(v.residual,[0,4]);close(v.projectionScalar,3);
 const anti=M.vectorMetrics([-3,4],[2,0],1);vec(anti.projection,[-3,0]);close(anti.projectionScalar,-3);
});
T('zero vectors do not acquire a direction or invented projection',()=>{
 const v=M.vectorMetrics([1,2],[0,0],1);
 close(v.dot,0);assert.equal(v.angleDegrees,null);assert.equal(v.projection,null);
 assert.equal(M.vectorMetrics([0,0],[1,0],1).angleDegrees,null);
 assert.equal(M.vectorMetrics([Infinity,0],[1,2],1).status,'INVALID');
});
for(const [angle,xy,tan] of [[0,[1,0],0],[90,[0,1],null],[180,[-1,0],0],[270,[0,-1],null],[360,[1,0],0],[-90,[0,-1],null],[450,[0,1],null]]){
 T(`unit circle canonical angle ${angle}`,()=>{const a=M.unitCircle(angle);vec(a.point,xy);if(tan===null)assert.equal(a.tan,null);else close(a.tan,tan);close(a.radians,angle*Math.PI/180)});
}
T('unit-circle multiple turns negative degrees and quadrant invariant',()=>{
 for(let theta=-720;theta<=720;theta+=7){const v=M.unitCircle(theta);close(v.cos*v.cos+v.sin*v.sin,1,2e-12);assert.ok(v.normalizedDegrees>=0&&v.normalizedDegrees<360)}
 assert.equal(M.unitCircle(45).quadrant,1);assert.equal(M.unitCircle(140).quadrant,2);assert.equal(M.unitCircle(220).quadrant,3);assert.equal(M.unitCircle(315).quadrant,4);assert.equal(M.unitCircle(90).quadrant,null);
 assert.equal(M.unitCircle(NaN).status,'INVALID');
});
for(const kind of ['quadratic','cubic','log','abs']){
 T(`secant limiting derivative for ${kind}`,()=>{
  const x=1.5,h=1e-6,d=M.derivativeInfo(kind,x,h);
  assert.equal(d.domainValid,true);assert.equal(d.secantValid,true);assert.equal(d.differentiable,true);
  assert.ok(Math.abs(d.secantSlope-d.tangentSlope)<1e-4);
 });
}
T('quadratic secant is 2x+h even for small increments',()=>{
 const d=M.derivativeInfo('quadratic',2,.5);close(d.y,4);close(d.nextY,6.25);close(d.secantSlope,4.5);close(d.tangentSlope,4);
 close(M.derivativeInfo('quadratic',2,1e-14).secantSlope,4,1e-12);
});
T('h=0 means absent secant, not zero division or fake tangent',()=>{
 const d=M.derivativeInfo('cubic',1,0);assert.equal(d.secantValid,false);assert.equal(d.secantSlope,null);close(d.tangentSlope,0);
});
T('absolute-value corner has no derivative but one-sided secants differ',()=>{
 const a=M.derivativeInfo('abs',0,.5),b=M.derivativeInfo('abs',0,-.5);
 assert.equal(a.differentiable,false);assert.equal(a.tangentSlope,null);close(a.secantSlope,1);close(b.secantSlope,-1);
});
T('log domain excludes invalid point and invalid second secant endpoint',()=>{
 const d=M.derivativeInfo('log',-1,.5);assert.equal(d.domainValid,false);assert.equal(d.y,null);assert.equal(d.tangentSlope,null);
 const e=M.derivativeInfo('log',1,-2);assert.equal(e.domainValid,true);assert.equal(e.secantValid,false);close(e.tangentSlope,1);
 assert.equal(M.derivativeInfo('unknown',0,1).status,'INVALID');
});
T('box horizontal plane gives actual four-vertex area',()=>{
 const b=M.boxGeometry(2,2,2),cut=M.slicePolyhedron(b.vertices,b.edges,[0,0,1],1);
 assert.equal(cut.status,'POLYGON');assert.equal(cut.points.length,4);close(cut.area,4);close(cut.perimeter,8);
 cut.points.forEach(p=>close(p[2],1));
});
T('central diagonal cube section is a regular hexagon, not a fixed rectangle',()=>{
 const b=M.boxGeometry(2,2,2),c=M.slicePolyhedron(b.vertices,b.edges,[1,1,1],1);
 assert.equal(c.status,'POLYGON');assert.equal(c.points.length,6);close(c.area,3*Math.sqrt(3));
 for(const p of c.points)close(p.reduce((a,v)=>a+v,0),1);
});
T('cube cut point edge face and empty are separate cases',()=>{
 const b=M.boxGeometry(2,2,2),slice=(n,d)=>M.slicePolyhedron(b.vertices,b.edges,n,d);
 assert.equal(slice([1,1,1],4).status,'POINT');
 const edge=slice([1,1,0],2);assert.equal(edge.status,'SEGMENT');assert.equal(edge.points.length,2);close(edge.area,0);close(edge.length,2);
 const face=slice([1,0,0],1);assert.equal(face.status,'POLYGON');assert.equal(face.points.length,4);close(face.area,4);
 const empty=slice([1,0,0],2);assert.equal(empty.status,'EMPTY');assert.deepEqual(empty.points,[]);
 assert.equal(slice([0,0,0],1).status,'INVALID');
});
T('plane scaling leaves intersection unchanged',()=>{
 const b=M.boxGeometry(2,3,4),a=M.slicePolyhedron(b.vertices,b.edges,[1,2,3],2),c=M.slicePolyhedron(b.vertices,b.edges,[7,14,21],14);
 assert.equal(a.points.length,c.points.length);close(a.area,c.area,1e-8);
});
T('square pyramid section narrows toward apex',()=>{
 const b=M.pyramidGeometry(4,4,4);
 const middle=M.slicePolyhedron(b.vertices,b.edges,[0,0,1],2);close(middle.area,4);assert.equal(middle.points.length,4);
 close(M.slicePolyhedron(b.vertices,b.edges,[0,0,1],0).area,16);
 assert.equal(M.slicePolyhedron(b.vertices,b.edges,[0,0,1],4).status,'POINT');
 assert.equal(M.slicePolyhedron(b.vertices,b.edges,[0,0,1],5).status,'EMPTY');
});
T('sphere plane produces circle tangent point empty, and zero-normal invalid',()=>{
 const s=M.sliceSphere(2,[0,0,1],1);assert.equal(s.status,'CIRCLE');close(s.radius,Math.sqrt(3));close(s.area,3*Math.PI);vec(s.center,[0,0,1]);
 assert.equal(M.sliceSphere(2,[0,0,1],2).status,'POINT');assert.equal(M.sliceSphere(2,[0,0,1],3).status,'EMPTY');assert.equal(M.sliceSphere(2,[0,0,0],1).status,'INVALID');
});
T('240 deterministic cube sections stay coplanar inside bounds with finite area',()=>{
 let seed=81723;const rng=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);
 const b=M.boxGeometry(2,2,2);
 for(let i=0;i<240;i++){
  const n=[rng()*2-1,rng()*2-1,rng()*2-1],d=rng()*4-2;
  const c=M.slicePolyhedron(b.vertices,b.edges,n,d);
  assert.notEqual(c.status,'INVALID');assert.ok(Number.isFinite(c.area)&&c.area>=0&&c.area<=7);
  for(const p of c.points){close(p[0]*n[0]+p[1]*n[1]+p[2]*n[2],d,2e-8);assert.ok(p[0]>=-1-1e-8&&p[0]<=1+1e-8);assert.ok(p[1]>=-1-1e-8&&p[1]<=1+1e-8);assert.ok(p[2]>=-1e-8&&p[2]<=2+1e-8)}
 }
});
T('cube triangular and pentagonal sections have independent analytic areas',()=>{
 const b=M.boxGeometry(2,2,2);
 const t=M.slicePolyhedron(b.vertices,b.edges,[1,1,1],-1);
 assert.equal(t.points.length,3);close(t.area,Math.sqrt(3)/2);
 const p=M.slicePolyhedron(b.vertices,b.edges,[1,1,2],1);
 assert.equal(p.points.length,5);close(p.area,7*Math.sqrt(6)/4);
});
