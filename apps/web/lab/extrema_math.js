"use strict";
/* Fixed closed-interval finite extrema; no general symbolic parser. */
(function(root,factory){
 const api=factory();
 if(typeof module==="object"&&module.exports)module.exports=api;
 root.MentorExtremaMath=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
 const MODELS=new Set(["quadratic","cubic","absolute","sine","log"]);
 const parameters={
   quadratic:["a","b","c"],cubic:["a","k"],absolute:["a","h","k"],
   sine:["A","w","phi","k"],log:[]
 };
 const EPS=1e-9;
 const error=message=>({valid:false,error:message,isProof:false});
 const near=(a,b)=>Math.abs(a-b)<=EPS*Math.max(1,Math.abs(a),Math.abs(b));
 function value(kind,p,x){
   switch(kind){
     case "quadratic":return (p.a*x+p.b)*x+p.c;
     case "cubic":return p.a*(x*x*x-3*x)+p.k;
     case "absolute":return p.a*Math.abs(x-p.h)+p.k;
     case "sine":return p.A*Math.sin(p.w*x+p.phi)+p.k;
     case "log":return x>0?Math.log(x):NaN;
     default:return NaN;
   }
 }
 function derivative(kind,p,x){
   if(kind==="quadratic")return 2*p.a*x+p.b;
   if(kind==="cubic")return p.a*(3*x*x-3);
   if(kind==="absolute")return p.a===0?0:near(x,p.h)?null:p.a*Math.sign(x-p.h);
   if(kind==="sine")return p.A*p.w*Math.cos(p.w*x+p.phi);
   if(kind==="log")return x>0?1/x:null;
   return null;
 }
 function analyze(kind,p){
   if(!MODELS.has(kind)||!p||typeof p!=="object")return error("不支持的固定函数模型");
   const keys=["L","R",...parameters[kind]];
   if(keys.some(k=>typeof p[k]!=="number"||!Number.isFinite(p[k])))
     return error("参数和区间端点必须是有限实数");
   if(!(p.L<p.R))return error("闭区间必须满足 L<R，不能交换或忽略端点");
   if(kind==="log"&&p.L<=0)return error("对数 ln(x) 的定义域要求整段闭区间严格大于0");
   const constant=(kind==="quadratic"&&p.a===0&&p.b===0)||
     (kind==="cubic"&&p.a===0)||
     (kind==="absolute"&&p.a===0)||
     (kind==="sine"&&(p.A===0||p.w===0));
   const candidates=[],stationary=[],nondifferentiable=[];
   const push=(x,type)=>{
     if(!Number.isFinite(x)||x<p.L-1e-10||x>p.R+1e-10)return;
     x=Math.max(p.L,Math.min(p.R,x));
     const y=value(kind,p,x);
     if(!Number.isFinite(y))return;
     const existing=candidates.find(z=>near(z.x,x));
     if(existing){
       // Endpoint inclusion is always recorded, even when derivative also vanishes.
       existing.tags.push(type);return;
     }
     candidates.push({x,value:y,type,tags:[type]});
   };
   push(p.L,"endpoint");push(p.R,"endpoint");
   function interior(x,type){
     if(Object.is(x,-0))x=0; // zero is not a signed mathematical coordinate
     if(x<=p.L+1e-10||x>=p.R-1e-10)return;
     push(x,type);
     if(type==="stationary")stationary.push(x);
     if(type==="nondifferentiable")nondifferentiable.push(x);
   }
   if(!constant){
     if(kind==="quadratic"&&p.a!==0)interior(-p.b/(2*p.a),"stationary");
     if(kind==="cubic"&&p.a!==0){
       interior(-1,"stationary");interior(1,"stationary");
     }
     if(kind==="absolute")interior(p.h,"nondifferentiable");
     if(kind==="sine"){
       const alpha=p.w*p.L+p.phi,beta=p.w*p.R+p.phi;
       const low=Math.min(alpha,beta),high=Math.max(alpha,beta);
       const start=Math.ceil((low-Math.PI/2)/Math.PI-1e-10);
       const end=Math.floor((high-Math.PI/2)/Math.PI+1e-10);
       if(end-start>500)return error("候选极值点过多，超出固定模型展示范围");
       for(let k=start;k<=end;k++)interior((Math.PI/2+k*Math.PI-p.phi)/p.w,"stationary");
     }
   }
   candidates.sort((a,b)=>a.x-b.x);
   stationary.sort((a,b)=>a-b);
   const min=Math.min(...candidates.map(c=>c.value));
   const max=Math.max(...candidates.map(c=>c.value));
   const make=(v)=>({value:v,points:constant?[]:candidates.filter(c=>near(c.value,v)).map(c=>c.x),
      allPoints:constant});
   return {valid:true,kind,L:p.L,R:p.R,closed:true,constant,
     candidates,stationary,nondifferentiable,
     globalMin:make(min),globalMax:make(max),
     criteria:"闭区间连续函数：比较端点、区间内部驻点与不可导点的函数值。",
     isProof:false,finiteExploration:true};
 }
 return Object.freeze({MODELS:[...MODELS],analyze,value,derivative});
});
