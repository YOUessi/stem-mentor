'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const file=path.resolve(__dirname,'../../apps/web/lab/interval_math.js'),exists=fs.existsSync(file);
test('v0.10 interval and inequality kernel exists',()=>assert.ok(exists));
const M=exists?require(file):null,T=(name,fn)=>test(name,{skip:!M},fn);
const I=(a,b,lc=true,rc=true)=>M.interval(a,b,lc,rc);
const same=(a,b)=>assert.deepEqual(a,b);

T('interval empty, singleton, reversed and infinite endpoints are distinct',()=>{
 same(I(2,1),[]);same(I(1,1,false,true),[]);same(I(1,1,true,false),[]);
 same(I(1,1),[{lo:1,hi:1,loClosed:true,hiClosed:true}]);
 same(I(-Infinity,2),[{lo:-Infinity,hi:2,loClosed:false,hiClosed:true}]);
 same(I(1,Infinity),[{lo:1,hi:Infinity,loClosed:true,hiClosed:false}]);
 same(I(Infinity,Infinity),[]);same(I(-Infinity,-Infinity),[]);
 assert.throws(()=>I(NaN,2));
});
T('normalization merges a touching boundary only if at least one includes it',()=>{
 same(M.union(I(0,1,false,false),I(1,2,false,false)),[...I(0,1,false,false),...I(1,2,false,false)]);
 same(M.union(I(0,1,false,true),I(1,2,false,false)),I(0,2,false,false));
 same(M.union(I(0,1,false,false),I(1,2,true,false)),I(0,2,false,false));
 same(M.union(I(0,1,false,false),I(1,1)),I(0,1,false,true));
 same(M.union(I(0,2,true,false),I(0,2,false,true)),I(0,2));
});
T('intersection accounts for open and closed coincident endpoints',()=>{
 same(M.intersect(I(0,1),I(1,2)),I(1,1));
 same(M.intersect(I(0,1,true,false),I(1,2)),[]);
 same(M.intersect(I(-Infinity,3),I(1,Infinity,false,false)),I(1,3,false,true));
});
T('complement relative to R preserves singleton holes and unbounded tails',()=>{
 same(M.complement([]),I(-Infinity,Infinity));
 same(M.complement(I(-Infinity,Infinity)),[]);
 same(M.complement(I(2,2)),[...I(-Infinity,2,false,false),...I(2,Infinity,false,false)]);
 same(M.complement([ ...I(-Infinity,2,false,false), ...I(2,Infinity,false,false)]),I(2,2));
 same(M.complement(I(0,2,false,false)),[...I(-Infinity,0,false,true),...I(2,Infinity,true,false)]);
});
T('difference does not silently close subtracted endpoints',()=>{
 same(M.difference(I(0,3),I(1,2)),[...I(0,1,true,false),...I(2,3,false,true)]);
 same(M.difference(I(0,3),I(1,2,false,false)),[...I(0,1),...I(2,3)]);
 same(M.difference(I(0,1),I(0,1)),[]);
});
T('membership and notation distinguish finite endpoints, R and empty',()=>{
 assert.equal(M.contains(I(0,1,false,true),0),false);
 assert.equal(M.contains(I(0,1,false,true),1),true);
 assert.equal(M.contains(I(-Infinity,Infinity),Infinity),false);
 assert.equal(M.format([]),'∅');assert.equal(M.format(I(-Infinity,Infinity)),'ℝ');
 assert.equal(M.format(I(1,1)),'{1}');assert.equal(M.format(I(0,2,false,true)),'(0, 2]');
 assert.match(M.format(I(1,Infinity)),/∞/);
});
T('interval algebra obeys membership for deterministic combinations and probes',()=>{
 for(let i=-2;i<=2;i++)for(let j=i;j<=2;j++)for(let mask=0;mask<4;mask++){
  const A=I(i,j,Boolean(mask&1),Boolean(mask&2)),B=I(-.5,1.5,false,true);
  for(let x=-3;x<=3;x+=.25){const a=M.contains(A,x),b=M.contains(B,x);
    assert.equal(M.contains(M.union(A,B),x),a||b);
    assert.equal(M.contains(M.intersect(A,B),x),a&&b);
    assert.equal(M.contains(M.difference(A,B),x),a&&!b);
    assert.equal(M.contains(M.complement(A),x),!a);
  }
 }
});
T('linear negative coefficient reverses inequality and zero coefficient is constant',()=>{
 same(M.solveLinear(-2,4,'le').intervals,I(2,Infinity));
 same(M.solveLinear(2,-4,'lt').intervals,I(-Infinity,2,false,false));
 same(M.solveLinear(0,0,'lt').intervals,[]);
 same(M.solveLinear(0,0,'le').intervals,I(-Infinity,Infinity));
 same(M.solveLinear(0,2,'gt').intervals,I(-Infinity,Infinity));
});
T('quadratic two roots respects all four comparison signs',()=>{
 same(M.solveQuadratic(1,0,-1,'le').intervals,I(-1,1));
 same(M.solveQuadratic(1,0,-1,'lt').intervals,I(-1,1,false,false));
 same(M.solveQuadratic(1,0,-1,'gt').intervals,[...I(-Infinity,-1,false,false),...I(1,Infinity,false,false)]);
 same(M.solveQuadratic(-1,0,1,'ge').intervals,I(-1,1));
});
T('quadratic repeated root, no root and linear degeneration never invent intervals',()=>{
 same(M.solveQuadratic(1,-2,1,'le').intervals,I(1,1));
 same(M.solveQuadratic(1,-2,1,'lt').intervals,[]);
 same(M.solveQuadratic(1,-2,1,'ge').intervals,I(-Infinity,Infinity));
 same(M.solveQuadratic(1,0,1,'le').intervals,[]);
 same(M.solveQuadratic(1,0,1,'gt').intervals,I(-Infinity,Infinity));
 same(M.solveQuadratic(0,-2,4,'le').intervals,I(2,Infinity));
 assert.equal(M.solveQuadratic(0,0,-1,'lt').kind,'CONSTANT');
});
T('absolute inequality handles negative radius, zero radius, and outer rays',()=>{
 same(M.solveAbs(2,-1,'le').intervals,[]);
 same(M.solveAbs(2,-1,'gt').intervals,I(-Infinity,Infinity));
 same(M.solveAbs(2,0,'le').intervals,I(2,2));
 same(M.solveAbs(2,0,'ge').intervals,I(-Infinity,Infinity));
 same(M.solveAbs(2,0,'lt').intervals,[]);
 same(M.solveAbs(2,1,'gt').intervals,[...I(-Infinity,1,false,false),...I(3,Infinity,false,false)]);
});
T('200 deterministic quadratic parameter sets agree with direct substitution away from roots',()=>{
 let seed=49019;const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
 const pred={lt:v=>v<0,le:v=>v<=0,gt:v=>v>0,ge:v=>v>=0};
 for(let k=0;k<200;k++){
   const a=Math.floor(rnd()*7)-3,b=Math.floor(rnd()*9)-4,c=Math.floor(rnd()*9)-4;
   for(const rel of Object.keys(pred)){
     const r=M.solveQuadratic(a,b,c,rel);
     for(let x=-5;x<=5;x+=.125){const y=a*x*x+b*x+c;
       if(Math.abs(y)<1e-9)continue;
       assert.equal(M.contains(r.intervals,x),pred[rel](y),JSON.stringify({a,b,c,rel,x,r}));
     }
   }
 }
});
T('invalid relations and nonfinite coefficients are rejected',()=>{
 assert.throws(()=>M.solveLinear(Infinity,0,'lt'));
 assert.throws(()=>M.solveQuadratic(1,0,1,'equal'));
 assert.throws(()=>M.solveAbs(0,NaN,'le'));
});
