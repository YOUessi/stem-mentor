"use strict";
/* Offline v0.12 probability and statistics exploration: fixed curated models. */
(function(root){
 const NS="http://www.w3.org/2000/svg";
 const P=()=>root.MentorProbabilityMath;
 const SUPPORTED=new Set(["stats-summary","prob-choose","prob-permute","prob-tree","prob-binomial",
   "prob-hypergeo","prob-normal","stats-bernoulli","stats-regression"]);
 const fmt=x=>Number.isFinite(x)?Number(x.toPrecision(6)).toString():"未定义";
 function elem(parent,name,attrs={},value){
   const n=document.createElementNS(NS,name);
   for(const [key,v] of Object.entries(attrs))n.setAttribute(key,String(v));
   if(value!==undefined)n.textContent=String(value);
   parent.appendChild(n);return n;
 }
 function html(parent,name,cls,value){
   const n=document.createElement(name);if(cls)n.className=cls;
   if(value!==undefined)n.textContent=String(value);
   parent.appendChild(n);return n;
 }
 const bound=(v,a,b)=>Math.min(b,Math.max(a,v));
 function axis(svg,{x1=66,y1=60,x2=735,y2=400}={}){
   elem(svg,"line",{x1,y1:y2,x2,y2,class:"lab-prob-axis"});
   elem(svg,"line",{x1,y1,x2:x1,y2,class:"lab-prob-axis"});
   for(let j=0;j<=4;j++){
     const y=y2-(y2-y1)*j/4;
     elem(svg,"line",{x1,y1:y,x2,y2:y,class:"lab-prob-grid"});
   }
 }
 function bars(svg,data,selected,mode="probability"){
   const top=70,bottom=389,max=Math.max(.001,...data.map(p=>p.value));
   const width=660,dataN=data.length,col=width/Math.max(dataN,1);
   axis(svg);
   data.forEach((point,i)=>{
     const x=70+i*col+col*.12;
     const h=(bottom-top)*.9*(point.value/max);
     elem(svg,"rect",{x,y:bottom-h,width:Math.max(2,col*.76),height:h,
       class:i===selected?"lab-prob-bar selected":"lab-prob-bar",
       "data-outcome":point.label,"data-value":point.value});
     if(dataN<=18||i%2===0||i===dataN-1)
       elem(svg,"text",{x:x+col*.38,y:410,class:"lab-prob-tick","text-anchor":"middle"},point.label);
   });
   elem(svg,"text",{x:68,y:30,class:"lab-prob-heading"},
      mode==="count"?"按选择个数列出的计数（柱高只表示有限模型）":"各事件柱高（先猜测，再自主查看精确读数）");
   elem(svg,"text",{x:19,y:70,class:"lab-prob-tick"},fmt(max));
 }
 function strokePath(svg,points,cls){
   const d=points.map((x,i)=>(i?"L":"M")+x[0].toFixed(2)+","+x[1].toFixed(2)).join(" ");
   elem(svg,"path",{d,class:cls});
 }
 function probabilityTree(svg,p){
   elem(svg,"text",{x:32,y:33,class:"lab-prob-heading"},"两阶段事件树：先看条件概率，再合成联合事件");
   const nodes=[
    {x:87,y:235,caption:"开始"},
    {x:296,y:132,caption:"A"}, {x:296,y:339,caption:"非A"},
    {x:602,y:66,caption:"A∩B"}, {x:602,y:180,caption:"A∩非B"},
    {x:602,y:295,caption:"非A∩B"}, {x:602,y:409,caption:"非A∩非B"}
   ];
   for(const [from,to,label] of [
     [0,1,"P(A)="+fmt(p.p)],[0,2,"P(非A)="+fmt(1-p.p)],
     [1,3,p.p===0?"P(B|A)未定义":"P(B|A)="+fmt(p.q1)],
     [1,4,p.p===0?"P(非B|A)未定义":"P(非B|A)="+fmt(1-p.q1)],
     [2,5,p.p===1?"P(B|非A)未定义":"P(B|非A)="+fmt(p.q0)],
     [2,6,p.p===1?"P(非B|非A)未定义":"P(非B|非A)="+fmt(1-p.q0)]
   ]){
     const a=nodes[from],b=nodes[to],mx=(a.x+b.x)/2,my=(a.y+b.y)/2;
     elem(svg,"line",{x1:a.x,y1:a.y,x2:b.x,y2:b.y,class:"lab-prob-branch"});
     elem(svg,"text",{x:mx,y:my-12,class:"lab-prob-label","text-anchor":"middle"},label);
   }
   nodes.forEach((n,i)=>{
     elem(svg,"circle",{cx:n.x,cy:n.y,r:i===0?13:10,class:"lab-prob-node"});
     elem(svg,"text",{x:n.x+16,y:n.y+5,class:"lab-prob-label"},n.caption);
   });
 }
 function drawCurve(svg,points,cls){
   strokePath(svg,points,cls);
 }
 function normal(svg,p,assist){
   const Pcore=P();
   const left=p.mu-4.5*p.sigma,right=p.mu+4.5*p.sigma,maxY=Pcore.normalPdf(p.mu,p.mu,p.sigma);
   const xcoord=x=>66+(x-left)/(right-left)*666;
   const ycoord=y=>392-y/(maxY*1.25)*320;
   axis(svg);
   const samples=Array.from({length:321},(_,i)=>{
     const x=left+(right-left)*i/320;
     return [xcoord(x),ycoord(Pcore.normalPdf(x,p.mu,p.sigma))];
   });
   drawCurve(svg,samples,"lab-prob-density");
   if(assist && p.L<p.R){
     const a=bound(p.L,left,right),b=bound(p.R,left,right);
     if(a<b){
       const data=Array.from({length:161},(_,i)=>{
         const x=a+(b-a)*i/160;
         return [xcoord(x),ycoord(Pcore.normalPdf(x,p.mu,p.sigma))];
       });
       const polygon=[[xcoord(a),392],...data,[xcoord(b),392]];
       elem(svg,"polygon",{points:polygon.map(v=>v.join(",")).join(" "),
         class:"lab-prob-integrated-area"});
     }
   }
   elem(svg,"text",{x:66,y:34,class:"lab-prob-heading"},"正态概率密度曲线：点的高度≠事件概率");
   elem(svg,"text",{x:xcoord(p.mu),y:423,class:"lab-prob-tick","text-anchor":"middle"},"μ="+fmt(p.mu));
 }
 function bernoulli(svg,trajectory,p,assist){
   axis(svg);
   const n=trajectory.length,xx=i=>65+(i-1)/Math.max(n-1,1)*665,
     yy=v=>391-v*290;
   elem(svg,"line",{x1:65,y1:yy(p.p),x2:731,y2:yy(p.p),class:"lab-prob-theory-line"});
   strokePath(svg,trajectory.map(row=>[xx(row.trials),yy(row.frequency)]),"lab-prob-frequency-line");
   elem(svg,"text",{x:67,y:35,class:"lab-prob-heading"},"样本频率曲线 vs 理论概率虚线（固定随机种子）");
   if(assist)elem(svg,"text",{x:548,y:yy(p.p)-12,class:"lab-prob-tick"},"理论p="+fmt(p.p));
 }
 function regression(svg,data,fit,assist){
   axis(svg);
   const max=Math.max(2,...data.map(d=>Math.abs(d.y))),limit=max*1.2;
   const X=x=>66+(x+4)/8*665,Y=y=>230-y/limit*170;
   elem(svg,"line",{x1:66,y1:230,x2:731,y2:230,class:"lab-prob-zero"});
   data.forEach(point=>{
     elem(svg,"circle",{cx:X(point.x),cy:Y(point.y),r:5,class:"lab-prob-scatter"});
   });
   if(assist && fit.valid){
     elem(svg,"line",{x1:X(-4),y1:Y(fit.slope*(-4)+fit.intercept),
       x2:X(4),y2:Y(fit.slope*4+fit.intercept),class:"lab-prob-fit-line"});
   }
   elem(svg,"text",{x:66,y:34,class:"lab-prob-heading"},"合成散点图；回归相关不构成因果证明");
 }
 function seededSynthetic(n,p){
   // Synthetic, repeatable data only; not a real student's scores.
   let state=(p.seed>>>0)||0x9E3779B9;
   function random(){state^=state<<13;state^=state>>>17;state^=state<<5;return (state>>>0)/4294967296}
   return Array.from({length:n},(_,i)=>{
     const x=-3+i*6/Math.max(1,n-1);
     const y=p.slope*x+p.intercept+(random()-.5)*p.noise*2;
     return {x,y};
   });
 }
 function guide(scene,preset){
   const area=scene.extraControls;
   if(!area||scene.lastPreset===preset.id)return;
   scene.lastPreset=preset.id;
   area.replaceChildren();area.hidden=false;
   const section=html(area,"section","lab-prob-prompt");
   html(section,"h3",null,"概率与统计：先预测，再检验");
   html(section,"p",null,preset.prediction_prompt);
   const guess=html(section,"textarea","lab-prob-guess","");
   guess.maxLength=420;guess.rows=2;
   guess.value=scene.guess||"";
   guess.placeholder="我认为改变参数后，这个概率/统计量会……";
   guess.setAttribute("aria-label","我的概率或统计猜想");
   guess.addEventListener("input",()=>{scene.guess=guess.value});
   const button=html(section,"button","btn btn-light","给我一点提示");
   button.type="button";
   const help=html(section,"p","lab-prob-help","当前未请求提示。");
   button.addEventListener("click",()=>{
      scene.helpLevel=Math.min(3,(scene.helpLevel||0)+1);
      help.textContent="提示 "+scene.helpLevel+"/3："+preset.thinking_prompts[scene.helpLevel-1];
   });
   html(section,"small",null,"仅合成概率模型与描述统计；不记录学习成绩或自动判定掌握。");
 }
 function render(rootSvg,preset,p,view,scene){
   const core=P();if(!core)throw Error("离线概率内核不可用");
   const id=preset.id;
   rootSvg.replaceChildren();rootSvg.setAttribute("viewBox","0 0 760 460");
   guide(scene,preset);
   const assist=Boolean(scene.assist),info=[],finish={info,kind:preset.tool,
     latex:preset.latex,coordinateHint:"先预测再改变参数；数值计算结果可自主开启，不用它代替推导。"};
   try{
     if(id==="stats-summary"){
       const values=[p.x1,p.x2,p.x3,p.x4,p.x5];
       const stats=core.statistics(values);
       elem(rootSvg,"line",{x1:65,y1:230,x2:731,y2:230,class:"lab-prob-axis"});
       const maxAbs=Math.max(1,...values.map(x=>Math.abs(x)));
       values.forEach((value,i)=>{
         const x=110+i*122,h=Math.abs(value)/maxAbs*158;
         elem(rootSvg,"rect",{x,y:value>=0?230-h:230,width:68,height:h,
            class:value>=0?"lab-prob-bar":"lab-prob-bar negative",
            "data-sample-index":i+1,"data-value":value});
         elem(rootSvg,"text",{x:x+34,y:415,"text-anchor":"middle",class:"lab-prob-tick"},
            "x"+(i+1)+"="+fmt(value));
       });
       elem(rootSvg,"text",{x:66,y:36,class:"lab-prob-heading"},
         "合成有限样本；均值、中位数、众数和方差并非同一个量");
       info.push("当前是5个可调的合成观察值");
       if(assist){
         info.push("样本均值="+fmt(stats.mean),"中位数="+fmt(stats.median));
         info.push("众数="+(stats.modes.length?stats.modes.map(fmt).join("、"):"无重复众数"));
         info.push("总体方差(分母n)="+fmt(stats.populationVariance));
         info.push("样本方差(分母n−1)="+fmt(stats.sampleVariance));
         info.push("样本标准差="+fmt(stats.sampleStdDev));
       }
     }else if(id==="prob-choose"||id==="prob-permute"){
       const n=p.n,k=p.k;
       const count=id==="prob-choose"?core.choose:core.permutations;
       const barsData=Array.from({length:n+1},(_,x)=>({label:String(x),value:count(n,x)}));
       bars(rootSvg,barsData,k,"count");
       info.push("计数随 k 变化；观察排列顺序是否重要");
       if(assist){
         info.push(k>n?"k>n：该选择不可能":"当前 "+(id==="prob-choose"?"组合数":"排列数")+"="+fmt(count(n,k)));
       }
     }else if(id==="prob-tree"){
       const tree=core.twoStageTree(p.p,p.q1,p.q0);
       probabilityTree(rootSvg,p);
       info.push("四条路径涵盖所有两阶段可能事件");
       if(tree.undefinedConditionalFirst)info.push("P(A)=0 时 P(B|A) 与 P(非B|A) 均未定义；仅用于零权重分支示意");
       if(tree.undefinedConditionalNotFirst)info.push("P(A)=1 时 P(B|非A) 与 P(非B|非A) 均未定义；仅用于零权重分支示意");
       if(assist){
          info.push("联合概率四叶="+tree.leaves.map(fmt).join("，"));
          info.push("第二阶段成功总概率="+fmt(tree.probabilitySecond));
          info.push("独立性判断（固定模型）="+(tree.independent?"是":"否"));
       }
     }else if(id==="prob-binomial"){
       const r=core.binomialSummary(p.n,p.p);
       const data=r.pmf.map((v,i)=>({label:String(i),value:v}));
       bars(rootSvg,data,p.k);
       info.push("n次独立重复试验，X 表示成功次数");
       if(assist){
         info.push("P(X="+p.k+")="+fmt(core.binomial(p.n,p.p,p.k)));
         info.push("归一化ΣP="+fmt(r.total));
         info.push("均值="+fmt(r.mean),"方差="+fmt(r.variance));
       }
     }else if(id==="prob-hypergeo"){
       const r=core.hypergeometricSummary(p.N,p.K,p.n);
       bars(rootSvg,r.pmf.map((v,i)=>({label:String(i),value:v})),p.k);
       info.push("超几何：从有限总体不放回抽取 n 个");
       if(assist){
         info.push("P(X="+p.k+")="+fmt(core.hypergeometric(p.N,p.K,p.n,p.k)));
         info.push("归一化ΣP="+fmt(r.total));
         info.push("理论均值="+fmt(r.mean),"方差="+fmt(r.variance));
       }
     }else if(id==="prob-normal"){
       normal(rootSvg,p,assist);
       info.push("曲线纵轴是密度，而不是单点概率");
       if(assist){
         if(p.L>=p.R)info.push("无效观测区间：L<R 必须满足");
         else info.push("近似区间概率P(L≤X≤R)="+fmt(core.normalInterval(p.L,p.R,p.mu,p.sigma)));
       }
     }else if(id==="stats-bernoulli"){
       const trajectory=core.bernoulliTrajectory(p.p,p.n,p.seed);
       bernoulli(rootSvg,trajectory,p,assist);
       info.push("每次模拟使用同一个种子，同样参数得到同样频率路径");
       if(assist){
         const summary=core.simulateBernoulli(p.p,p.n,p.seed);
         info.push("理论概率="+fmt(summary.theoreticalProbability));
         info.push("模拟频率="+fmt(summary.frequency));
         info.push("成功次数="+summary.successes+" / "+summary.trials);
       }
     }else if(id==="stats-regression"){
       const data=seededSynthetic(p.n,p),fit=core.regression(data.map(x=>x.x),data.map(x=>x.y));
       regression(rootSvg,data,fit,assist);
       info.push("合成数据，仅用于观察线性趋势；样本相关不等于因果");
       if(assist && fit.valid){
         info.push("样本回归斜率="+fmt(fit.slope),"截距="+fmt(fit.intercept));
         info.push("相关系数 r="+fmt(fit.r));
       }
     }else throw new Error("未支持的概率统计场景");
   }catch(e){
     rootSvg.replaceChildren();
     elem(rootSvg,"text",{x:55,y:180,class:"lab-prob-invalid"},"参数无效："+e.message);
     info.push("参数不满足概率模型："+e.message);
     finish.valid=false;
   }
   return finish;
 }
 root.MentorLabProbability={supports:id=>SUPPORTED.has(id),draw:render};
})(window);
