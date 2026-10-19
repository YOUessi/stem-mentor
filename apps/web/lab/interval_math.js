/* Real interval algebra and fixed-family inequalities, shared by Node and UI. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.MentorIntervalMath=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const finite=Number.isFinite;
 function interval(lo,hi,loClosed=true,hiClosed=true){
   if(typeof lo!=='number'||typeof hi!=='number'||Number.isNaN(lo)||Number.isNaN(hi))throw new TypeError('Numeric interval endpoints required');
   const lc=finite(lo)&&Boolean(loClosed),rc=finite(hi)&&Boolean(hiClosed);
   if(lo>hi||lo===Infinity||hi===-Infinity||(lo===hi&&!(lc&&rc)))return [];
   return [{lo:Object.is(lo,-0)?0:lo,hi:Object.is(hi,-0)?0:hi,loClosed:lc,hiClosed:rc}];
 }
 function normalize(parts){
   if(!Array.isArray(parts))throw new TypeError('Interval list required');
   const sorted=parts.flatMap(p=>interval(p.lo,p.hi,p.loClosed,p.hiClosed))
     .sort((a,b)=>a.lo<b.lo?-1:a.lo>b.lo?1:Number(b.loClosed)-Number(a.loClosed));
   const out=[];
   for(const p of sorted){
     const last=out.at(-1);
     if(!last||p.lo>last.hi||(p.lo===last.hi&&!p.loClosed&&!last.hiClosed)){out.push({...p});continue}
     if(p.lo===last.lo)last.loClosed=last.loClosed||p.loClosed;
     if(p.hi>last.hi){last.hi=p.hi;last.hiClosed=p.hiClosed}
     else if(p.hi===last.hi)last.hiClosed=last.hiClosed||p.hiClosed;
   }
   return out;
 }
 function contains(parts,x){
   if(!finite(x))return false;
   return parts.some(p=>(x>p.lo||x===p.lo&&p.loClosed)&&(x<p.hi||x===p.hi&&p.hiClosed));
 }
 const union=(a,b)=>normalize(a.concat(b));
 function intersect(a,b){
   const out=[];
   for(const p of normalize(a))for(const q of normalize(b)){
     const lo=Math.max(p.lo,q.lo),hi=Math.min(p.hi,q.hi);
     const lc=(lo>p.lo||p.loClosed)&&(lo>q.lo||q.loClosed);
     const rc=(hi<p.hi||p.hiClosed)&&(hi<q.hi||q.hiClosed);
     out.push(...interval(lo,hi,lc,rc));
   }
   return normalize(out);
 }
 function complement(parts){
   const sorted=normalize(parts),out=[];let left=-Infinity,closed=false;
   for(const p of sorted){
     out.push(...interval(left,p.lo,closed,!p.loClosed));
     left=p.hi;closed=!p.hiClosed;
   }
   out.push(...interval(left,Infinity,closed,false));return normalize(out);
 }
 const difference=(a,b)=>intersect(a,complement(b));
 const R=()=>interval(-Infinity,Infinity,false,false);
 const ops={lt:x=>x<0,le:x=>x<=0,gt:x=>x>0,ge:x=>x>=0};
 function validate(values,relation){
   if(!values.every(finite)||!Object.hasOwn(ops,relation))throw new RangeError('Finite coefficients and lt/le/gt/ge required');
 }
 function solveLinear(a,b,relation){
   validate([a,b],relation);
   if(a===0)return {kind:'CONSTANT',roots:[],intervals:ops[relation](b)?R():[],relation};
   const root=-b/a,closed=relation==='le'||relation==='ge';
   const left=(relation==='lt'||relation==='le')===(a>0);
   if(!finite(root))throw new RangeError('Root exceeds supported numeric range');
   return {kind:'LINEAR',roots:[root],intervals:left?interval(-Infinity,root,false,closed):interval(root,Infinity,closed,false),relation};
 }
 function solveQuadratic(a,b,c,relation){
   validate([a,b,c],relation);
   if(a===0)return solveLinear(b,c,relation);
   // Normalize the coefficients so their squared products remain finite.
   const scale=Math.max(Math.abs(a),Math.abs(b),Math.abs(c)),A=a/scale,B=b/scale,C=c/scale;
   const discriminant=B*B-4*A*C,positive=a>0;
   const inner=relation==='lt'||relation==='le',closed=relation==='le'||relation==='ge';
   const wantsInside=inner===positive;
   if(discriminant<0)return {kind:'QUADRATIC',roots:[],discriminant,intervals:ops[relation](a)?R():[],relation};
   if(discriminant===0){
     const r=-B/(2*A);let intervals;
     if(wantsInside)intervals=closed?interval(r,r):[];
     else intervals=closed?R():complement(interval(r,r));
     return {kind:'QUADRATIC',roots:[r],discriminant,intervals,relation};
   }
   const sqrt=Math.sqrt(discriminant),q=-.5*(B+(B>=0?1:-1)*sqrt);
   const roots=[q/A,C/q].sort((x,y)=>x-y);
   if(!roots.every(finite))throw new RangeError('Roots exceed supported numeric range');
   const [l,r]=roots;
   const intervals=wantsInside?interval(l,r,closed,closed):
     union(interval(-Infinity,l,false,closed),interval(r,Infinity,closed,false));
   return {kind:'QUADRATIC',roots,discriminant,intervals,relation};
 }
 function solveAbs(h,r,relation){
   validate([h,r],relation);
   const inner=relation==='lt'||relation==='le',closed=relation==='le'||relation==='ge';
   let intervals;
   if(r<0)intervals=inner?[]:R();
   else if(inner)intervals=interval(h-r,h+r,closed,closed);
   else intervals=complement(interval(h-r,h+r,!closed,!closed));
   return {kind:'ABSOLUTE',roots:r<0?[]:r===0?[h]:[h-r,h+r],intervals,relation};
 }
 function num(x){
   if(x===Infinity)return '+∞';if(x===-Infinity)return '−∞';
   if(Object.is(x,-0))return '0';if(Number.isInteger(x))return String(x);
   return Number(x.toPrecision(6)).toString();
 }
 function format(parts){
   const xs=normalize(parts);if(!xs.length)return '∅';
   if(xs.length===1&&xs[0].lo===-Infinity&&xs[0].hi===Infinity)return 'ℝ';
   return xs.map(p=>p.lo===p.hi?'{'+num(p.lo)+'}':(p.loClosed?'[':'(')+num(p.lo)+', '+num(p.hi)+(p.hiClosed?']':')')).join(' ∪ ');
 }
 return {interval,normalize,contains,union,intersect,complement,difference,solveLinear,solveQuadratic,solveAbs,format};
});
