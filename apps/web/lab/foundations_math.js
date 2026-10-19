/* v0.10 pure mathematics: complex arithmetic and explicit finite sets.
 * No DOM, model APIs, or arbitrary expressions. Browser and Node share this code.
 */
(function(root,factory){
 const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.MentorFoundationsMath=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const finite=Number.isFinite;
 const valid=z=>Array.isArray(z)&&z.length===2&&z.every(finite);
 const clean=x=>Object.is(x,-0)?0:x;
 function complexInfo(z){
   if(!valid(z))return {status:'INVALID'};
   const r=Math.hypot(z[0],z[1]);
   if(!finite(r))return {status:'INVALID',reason:'NUMERIC_RANGE'};
   return {status:'OK',point:z.map(clean),modulus:r,conjugate:[clean(z[0]),clean(-z[1])],
     argument:r===0?null:Math.atan2(z[1],z[0])};
 }
 function complexOp(z,w,op){
   if(!valid(z)||!valid(w))return {status:'INVALID',result:null};
   const [a,b]=z,[c,d]=w;let result;
   if(op==='add')result=[a+c,b+d];
   else if(op==='subtract')result=[a-c,b-d];
   else if(op==='multiply')result=[a*c-b*d,a*d+b*c];
   else if(op==='divide'){
     if(c===0&&d===0)return {status:'UNDEFINED',reason:'ZERO_DIVISOR',result:null};
     // Scale denominator to avoid squaring tiny or huge components.
     const scale=Math.max(Math.abs(c),Math.abs(d)),u=c/scale,v=d/scale,den=u*u+v*v;
     result=[((a/scale)*u+(b/scale)*v)/den,((b/scale)*u-(a/scale)*v)/den];
   }else return {status:'INVALID',result:null};
   if(!result.every(finite))return {status:'INVALID',reason:'NUMERIC_RANGE',result:null};
   return {status:'OK',result:result.map(clean)};
 }
 function rotateComplex(z,degrees,scale=1){
   if(!valid(z)||!finite(degrees)||!finite(scale)||scale<0)return {status:'INVALID',result:null};
   const t=(degrees%360)*Math.PI/180,c=Math.cos(t),s=Math.sin(t);
   const result=[scale*(z[0]*c-z[1]*s),scale*(z[0]*s+z[1]*c)];
   if(!result.every(finite))return {status:'INVALID',result:null};
   return {status:'OK',result:result.map(clean),degrees,scale};
 }
 function finiteSets(U,A,B,op){
   if(![U,A,B].every(xs=>Array.isArray(xs)&&xs.every(finite)))return {status:'INVALID'};
   const universe=[...new Set(U)].sort((a,b)=>a-b),u=new Set(universe);
   const a=new Set(A.filter(v=>u.has(v))),b=new Set(B.filter(v=>u.has(v)));
   const rules={union:(p,q)=>p||q,intersection:(p,q)=>p&&q,difference:(p,q)=>p&&!q,
     symmetric:(p,q)=>p!==q,complementA:p=>!p,complementUnion:(p,q)=>!(p||q),
     complementIntersection:(p,q)=>!(p&&q)};
   if(!Object.hasOwn(rules,op))return {status:'INVALID'};
   const region={aOnly:[],both:[],bOnly:[],neither:[]};
   for(const x of universe)region[a.has(x)?(b.has(x)?'both':'aOnly'):(b.has(x)?'bOnly':'neither')].push(x);
   const result=universe.filter(x=>rules[op](a.has(x),b.has(x)));
   let alternate=null;
   if(op==='complementUnion')alternate=universe.filter(x=>!a.has(x)&&!b.has(x));
   if(op==='complementIntersection')alternate=universe.filter(x=>!a.has(x)||!b.has(x));
   return {status:'OK',U:universe,A:universe.filter(x=>a.has(x)),B:universe.filter(x=>b.has(x)),
     result,alternate,regions:region,discarded:[...new Set(A.concat(B).filter(x=>!u.has(x)))].sort((a,b)=>a-b),
     subsetAinB:[...a].every(x=>b.has(x)),subsetBinA:[...b].every(x=>a.has(x)),
     cardinality:result.length};
 }
 return {complexInfo,complexOp,rotateComplex,finiteSets};
});
