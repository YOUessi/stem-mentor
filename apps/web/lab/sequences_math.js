"use strict";
/* Fixed finite high-school sequence models. No expression evaluation or model calls. */
(function(root,factory){
  const api=factory();
  if(typeof module==="object"&&module.exports)module.exports=api;
  root.MentorSeqMath=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  const MAX_TERMS=30,MAX_MAGNITUDE=1e14;
  const checkN=n=>{
    if(!Number.isSafeInteger(n)||n<1||n>MAX_TERMS)
      throw new RangeError("数列项数 n 必须是 1..30 的正整数");
  };
  const checkParams=p=>{
    for(const value of Object.values(p)){
      if(typeof value!=="number"||!Number.isFinite(value))
        throw new TypeError("数列参数必须是有限数");
    }
  };
  const safe=value=>{
    if(!Number.isFinite(value)||Math.abs(value)>MAX_MAGNITUDE)
      throw new RangeError("数列项过大或溢出；请调小参数以便可靠绘图");
    return value;
  };
  function finalize(terms,special="GENERAL"){
    // Kahan summation retains small partial-sum contributions near cancellation.
    let sum=0,correction=0;
    const sums=[];
    for(const term of terms){
      const delta=safe(term)-correction;
      const next=safe(sum+delta);
      correction=(next-sum)-delta;
      sum=next;
      sums.push(sum);
    }
    return {terms,sums,special,finiteOnly:true,infiniteSumProven:false};
  }
  function arithmetic(p,n){
    checkN(n);checkParams(p);
    const terms=Array.from({length:n},(_,i)=>safe(p.a1+i*p.d));
    return finalize(terms,p.d===0?"CONSTANT":"GENERAL");
  }
  function geometric(p,n){
    checkN(n);checkParams(p);
    const terms=[safe(p.a1)];
    for(let i=1;i<n;i++)terms.push(safe(terms[i-1]*p.q));
    const special=p.q===1?"Q_ONE":
      p.q===0?"Q_ZERO":p.q===-1?"Q_NEG_ONE":"GENERAL";
    return finalize(terms,special);
  }
  function linearRecurrence(p,n){
    checkN(n);checkParams(p);
    const terms=[safe(p.a1)];
    for(let i=1;i<n;i++)terms.push(safe(p.r*terms[i-1]+p.c));
    return finalize(terms,p.r===1?"R_ONE":p.r===0?"R_ZERO":"GENERAL");
  }
  function twoTermRecurrence(p,n){
    checkN(n);checkParams(p);
    const terms=[safe(p.a1)];
    if(n>=2)terms.push(safe(p.a2));
    for(let i=2;i<n;i++)terms.push(safe(terms[i-1]+terms[i-2]));
    return finalize(terms,"FIBONACCI_LIKE");
  }
  function compare(p,n){
    checkN(n);checkParams(p);
    const a=arithmetic({a1:p.a1,d:p.d},n);
    const g=geometric({a1:p.a1,q:p.q},n);
    const crossover=g.terms.findIndex((v,i)=>i>0&&Math.abs(v)>Math.abs(a.terms[i])+1e-9);
    return {arithmetic:a.terms,geometric:g.terms,arithmeticSums:a.sums,
      geometricSums:g.sums,firstMagnitudeCrossover:crossover<0?null:crossover+1,
      finiteOnly:true,notInfiniteProof:true};
  }
  function generate(type,p,n){
    if(type==="arithmetic")return arithmetic(p,n);
    if(type==="geometric")return geometric(p,n);
    if(type==="linear")return linearRecurrence(p,n);
    if(type==="two-term")return twoTermRecurrence(p,n);
    throw new RangeError("不支持的数列模型");
  }
  return Object.freeze({arithmetic,geometric,linearRecurrence,twoTermRecurrence,
    compare,generate,MAX_TERMS,MAX_MAGNITUDE});
});
