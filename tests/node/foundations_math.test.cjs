'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const file=path.resolve(__dirname,'../../apps/web/lab/foundations_math.js');
const exists=fs.existsSync(file);
test('v0.10 complex and finite-set kernel exists',()=>assert.ok(exists));
const M=exists?require(file):null;
const T=(name,fn)=>test(name,{skip:!M},fn);
const close=(a,b,e=1e-10)=>assert.ok(Number.isFinite(a)&&Math.abs(a-b)<=e,`${a} != ${b}`);
const pair=(a,b)=>{assert.equal(a.length,2);a.forEach((v,i)=>close(v,b[i]))};

T('complex point modulus conjugation and principal argument',()=>{
 const v=M.complexInfo([3,4]);assert.equal(v.status,'OK');close(v.modulus,5);
 pair(v.conjugate,[3,-4]);close(v.argument,Math.atan2(4,3));
 assert.equal(M.complexInfo([0,0]).argument,null);
 assert.equal(M.complexInfo([NaN,1]).status,'INVALID');
});
T('complex arithmetic uses actual real and imaginary products',()=>{
 pair(M.complexOp([1,2],[3,-4],'add').result,[4,-2]);
 pair(M.complexOp([1,2],[3,-4],'subtract').result,[-2,6]);
 pair(M.complexOp([1,2],[3,-4],'multiply').result,[11,2]);
 pair(M.complexOp([1,2],[3,-4],'divide').result,[-.2,.4]);
 assert.equal(M.complexOp([1,2],[0,0],'divide').status,'UNDEFINED');
 assert.equal(M.complexOp([1,2],[3,4],'unknown').status,'INVALID');
});
T('nonzero small divisor is not mistaken for zero and division is inverse',()=>{
 close(M.complexOp([1e-10,0],[1e-10,0],'divide').result[0],1);
 for(let i=-4;i<=4;i++)for(let j=-4;j<=4;j++){
   if(i===0&&j===0)continue;
   const z=[2.3,-1.7],w=[i,j];
   pair(M.complexOp(M.complexOp(z,w,'multiply').result,w,'divide').result,z);
 }
});
T('complex rotation supports negative and multi-turn angles and collapse to zero',()=>{
 pair(M.rotateComplex([2,0],90,1).result,[0,2]);
 pair(M.rotateComplex([0,2],-90,2).result,[4,0]);
 pair(M.rotateComplex([3,4],720,1).result,[3,4]);
 pair(M.rotateComplex([3,4],35,0).result,[0,0]);
 assert.equal(M.rotateComplex([1,2],20,-1).status,'INVALID');
});
T('finite sets are unique subsets of explicit U and do not mutate inputs',()=>{
 const U=[1,2,3,4,4],A=[1,1,3,9],B=[2,3],before=JSON.stringify([U,A,B]);
 const v=M.finiteSets(U,A,B,'union');
 assert.equal(v.status,'OK');assert.deepEqual(v.U,[1,2,3,4]);
 assert.deepEqual(v.A,[1,3]);assert.deepEqual(v.result,[1,2,3]);
 assert.deepEqual(v.discarded,[9]);assert.equal(JSON.stringify([U,A,B]),before);
 assert.deepEqual(v.regions,{aOnly:[1],both:[3],bOnly:[2],neither:[4]});
});
T('set operations and relative complements respect the selected universe',()=>{
 const U=[1,2,3,4],A=[1,2],B=[2,3],run=op=>M.finiteSets(U,A,B,op).result;
 assert.deepEqual(run('intersection'),[2]);assert.deepEqual(run('difference'),[1]);
 assert.deepEqual(run('symmetric'),[1,3]);assert.deepEqual(run('complementA'),[3,4]);
 assert.deepEqual(run('complementUnion'),[4]);assert.deepEqual(run('complementIntersection'),[1,3,4]);
 assert.deepEqual(M.finiteSets([],[],[],'complementA').result,[]);
 assert.deepEqual(M.finiteSets(U,[],[],'complementA').result,U);
 assert.deepEqual(M.finiteSets(U,U,[],'complementA').result,[]);
 assert.equal(M.finiteSets(U,A,B,'bad').status,'INVALID');
});
T('all 256 pairs of subsets satisfy De Morgan and membership predicates',()=>{
 const U=[1,2,3,4],sub=n=>U.filter((x,i)=>n&(1<<i));
 for(let a=0;a<16;a++)for(let b=0;b<16;b++){
   const A=sub(a),B=sub(b);
   for(const [op,pred] of [
     ['union',(p,q)=>p||q],['intersection',(p,q)=>p&&q],
     ['difference',(p,q)=>p&&!q],['symmetric',(p,q)=>p!==q],
     ['complementA',p=>!p],['complementUnion',(p,q)=>!(p||q)],
     ['complementIntersection',(p,q)=>!(p&&q)]]){
      const v=M.finiteSets(U,A,B,op);
      assert.deepEqual(v.result,U.filter(x=>pred(A.includes(x),B.includes(x))));
      if(op.startsWith('complement')&&op!=='complementA')assert.deepEqual(v.result,v.alternate);
   }
 }
});
