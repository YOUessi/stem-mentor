"use strict";
/* Fixed, offline high-school probability and descriptive statistics core.
   Monte Carlo frequencies are NOT theoretical probabilities or p-values. */
(function(root,factory){
 const api=factory();
 if(typeof module==="object"&&module.exports)module.exports=api;
 root.MentorProbabilityMath=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
 const finite=x=>typeof x==="number"&&Number.isFinite(x);
 function int(n,min,max,name){
   if(!Number.isSafeInteger(n)||n<min||n>max)
     throw new RangeError(name+" 必须是范围 "+min+".."+max+" 的整数");
 }
 function probability(p){
   if(!finite(p)||p<0||p>1)throw new RangeError("概率必须在0到1之间");
 }
 function choose(n,k){
   int(n,0,50,"总体 n");
   if(!Number.isInteger(k))throw new RangeError("组合的选取数必须为整数");
   if(k<0||k>n)return 0;
   const r=Math.min(k,n-k);
   let x=1;
   for(let i=1;i<=r;i++){
      x=Math.round(x*(n-r+i)/i);
      if(!Number.isSafeInteger(x))throw new RangeError("组合值超出安全整数范围");
   }
   return x;
 }
 function permutations(n,k){
   int(n,0,18,"总体 n");
   if(!Number.isInteger(k))throw new RangeError("排列的选取数必须为整数");
   if(k<0||k>n)return 0;
   let v=1;
   for(let i=0;i<k;i++){v*=n-i;
     if(!Number.isSafeInteger(v))throw new RangeError("排列值超出安全整数范围");
   }
   return v;
 }
 function binomial(n,p,k){
   int(n,0,30,"二项试验次数");probability(p);
   if(!Number.isInteger(k))throw new RangeError("成功次数必须是整数");
   if(k<0||k>n)return 0;
   return choose(n,k)*Math.pow(p,k)*Math.pow(1-p,n-k);
 }
 function binomialSummary(n,p){
   int(n,0,30,"二项试验次数");probability(p);
   const pmf=Array.from({length:n+1},(_,k)=>binomial(n,p,k));
   return {pmf,mean:n*p,variance:n*p*(1-p),total:pmf.reduce((a,b)=>a+b,0),
     theoretical:true};
 }
 function hypergeometric(N,K,n,k){
   int(N,1,50,"总体规模");int(K,0,N,"成功个数");
   int(n,0,N,"抽取样本量");
   if(!Number.isInteger(k))throw new RangeError("成功次数必须是整数");
   const lo=Math.max(0,n-(N-K)),hi=Math.min(K,n);
   if(k<lo||k>hi)return 0;
   return choose(K,k)*choose(N-K,n-k)/choose(N,n);
 }
 function hypergeometricSummary(N,K,n){
   int(N,1,50,"总体规模");int(K,0,N,"成功个数");int(n,0,N,"样本量");
   const pmf=Array.from({length:Math.min(K,n)+1},
      (_,k)=>hypergeometric(N,K,n,k));
   const p=K/N;
   return {pmf,mean:n*p,
     variance:N===1?0:n*p*(1-p)*(N-n)/(N-1),
     total:pmf.reduce((a,b)=>a+b,0),theoretical:true,withoutReplacement:true};
 }
 function twoStageTree(p,q1,q0){
   [p,q1,q0].forEach(probability);
   const leaves=[p*q1,p*(1-q1),(1-p)*q0,(1-p)*(1-q0)];
   const pSecond=leaves[0]+leaves[2];
   return {leaves,probabilitySecond:pSecond,pFirst:p,
     conditionalGivenFirst:p===0?null:q1,
     conditionalGivenNotFirst:p===1?null:q0,
     undefinedConditionalFirst:p===0,
     undefinedConditionalNotFirst:p===1,
     independent:p===0||p===1||Math.abs(q1-q0)<1e-12,
     notProofOfIndependenceFromSample:true};
 }
 function jointEvents(j){
   if(!Array.isArray(j)||j.length!==4)throw new RangeError("联合事件必须有四个概率");
   j.forEach(probability);
   const total=j.reduce((a,b)=>a+b,0);
   if(Math.abs(total-1)>1e-10)throw new RangeError("四个联合概率总和必须归一为1");
   const [ab,aOnly,bOnly,neither]=j;
   const pA=ab+aOnly,pB=ab+bOnly;
   return {pA,pB,pAB:ab,pA_given_B:pB>0?ab/pB:null,
     pB_given_A:pA>0?ab/pA:null,
     mutuallyExclusive:ab===0,
     independent:Math.abs(ab-pA*pB)<1e-10,total,
     invalidConditionalWhenZero:pB===0};
 }
 function normalPdf(x,mu,sigma){
   if(![x,mu,sigma].every(finite))throw new TypeError("正态密度参数必须是有限数");
   if(sigma<=0)throw new RangeError("标准差必须是正数");
   const z=(x-mu)/sigma;
   return Math.exp(-.5*z*z)/(sigma*Math.sqrt(2*Math.PI));
 }
 function statistics(values){
   if(!Array.isArray(values)||values.length===0)throw new RangeError("样本不能为空");
   if(values.length>1000||values.some(x=>!finite(x)))
     throw new TypeError("样本必须是有限数且不超过1000个");
   let mean=0,m2=0;
   values.forEach((x,i)=>{
      const n=i+1,delta=x-mean;
      mean+=delta/n;
      m2+=delta*(x-mean);
   });
   const sorted=[...values].sort((a,b)=>a-b),n=values.length;
   const mid=n>>1;
   const median=n%2?sorted[mid]:(sorted[mid-1]+sorted[mid])/2;
   const counts=new Map();
   for(const x of sorted)counts.set(x,(counts.get(x)||0)+1);
   const highest=Math.max(...counts.values());
   const modes=highest<2?[]:[...counts.entries()].filter(e=>e[1]===highest).map(e=>e[0]);
   return {size:n,mean,median,modes,populationVariance:m2/n,
     sampleVariance:n<2?null:m2/(n-1),
     sampleStdDev:n<2?null:Math.sqrt(m2/(n-1)),
     min:sorted[0],max:sorted[n-1],meanIsSampleStatistic:true};
 }
 function regression(xs,ys){
   if(!Array.isArray(xs)||!Array.isArray(ys)||xs.length!==ys.length)
     throw new RangeError("回归需要同样长度的配对数据");
   if(xs.length<2)return {valid:false,error:"至少需要两个配对样本"};
   const x=statistics(xs),y=statistics(ys);
   const n=xs.length;
   if(x.populationVariance<=0)return {valid:false,error:"x没有变化，斜率未定义"};
   let cov=0;
   for(let i=0;i<n;i++)cov+=(xs[i]-x.mean)*(ys[i]-y.mean);
   cov/=n;
   const slope=cov/x.populationVariance;
   const intercept=y.mean-slope*x.mean;
   const r=y.populationVariance===0?null:
     Math.max(-1,Math.min(1,cov/Math.sqrt(x.populationVariance*y.populationVariance)));
   return {valid:true,n,slope,intercept,r,
     sampleDerived:true,causationProven:false};
 }
 function simulateBernoulli(p,n,seed){
   probability(p);int(n,0,5000,"模拟次数");
   if(!Number.isSafeInteger(seed))throw new TypeError("固定随机种子必须是安全整数");
   let state=(seed>>>0)||0x9E3779B9;
   let success=0;
   for(let i=0;i<n;i++){
      state^=state<<13;state^=state>>>17;state^=state<<5;
      const u=(state>>>0)/4294967296;
      if(u<p)success++;
   }
   return {trials:n,successes:success,frequency:n?success/n:null,
     theoreticalProbability:p,seed,simulation:true,
     notExactProbability:true};
 }
 function bernoulliTrajectory(p,n,seed){
   probability(p);int(n,0,5000,"模拟次数");
   if(!Number.isSafeInteger(seed))throw new TypeError("固定随机种子必须是安全整数");
   let state=(seed>>>0)||0x9E3779B9,successes=0;
   const points=[];
   for(let i=1;i<=n;i++){
     state^=state<<13;state^=state>>>17;state^=state<<5;
     if((state>>>0)/4294967296<p)successes++;
     points.push({trials:i,successes,frequency:successes/i});
   }
   return points;
 }
 function normalInterval(L,R,mu,sigma){
   normalPdf(0,mu,sigma);
   if(!finite(L)||!finite(R)||L>R)throw new RangeError("积分区间必须满足 L<R（或 L=R 表示0概率）");
   if(L===R)return 0;
   const count=Math.min(16384,Math.max(1024,Math.ceil((R-L)/sigma*90)+
     (Math.ceil((R-L)/sigma*90)%2)));
   const n=count%2===0?count:count+1,step=(R-L)/n;
   let value=normalPdf(L,mu,sigma)+normalPdf(R,mu,sigma);
   for(let i=1;i<n;i++)value+=(i%2?4:2)*normalPdf(L+i*step,mu,sigma);
   return Math.max(0,Math.min(1,value*step/3));
 }
 return Object.freeze({choose,permutations,binomial,binomialSummary,
   hypergeometric,hypergeometricSummary,twoStageTree,jointEvents,
   normalPdf,normalInterval,statistics,regression,simulateBernoulli,bernoulliTrajectory});
});
