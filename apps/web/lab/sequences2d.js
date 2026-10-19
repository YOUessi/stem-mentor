"use strict";
/* SVG finite sequence studio with opt-in results, guided thought and no grading. */
(function(root){
 const NS="http://www.w3.org/2000/svg";
 const M=()=>root.MentorSeqMath;
 const supported=new Set(["seq-arithmetic","seq-geometric","seq-geometric-edge",
   "seq-linear-recurrence","seq-two-term","seq-partial-sum","seq-growth","seq-fixed-point"]);
 const $=id=>document.getElementById(id);
 function svg(parent,tag,props={},label){
   const el=document.createElementNS(NS,tag);
   for(const [k,v] of Object.entries(props))el.setAttribute(k,String(v));
   if(label!==undefined)el.textContent=String(label);
   parent.appendChild(el);return el;
 }
 function text(parent,tag,cls,label){
   const el=document.createElement(tag);
   if(cls)el.className=cls;
   if(label!==undefined)el.textContent=String(label);
   parent.appendChild(el);return el;
 }
 const fmt=n=>Number.isFinite(n)?
    (Math.abs(n)>999999?Number(n.toPrecision(6)).toExponential(2):
     Number(n.toFixed(6)).toString()):"未定义";
 const qChoice=[1,0,-1,.5,-1.5];
 function seriesFor(preset,v){
   const id=preset.id,n=v.n;
   if(id==="seq-arithmetic")return {primary:M().arithmetic({a1:v.a1,d:v.d},n)};
   if(id==="seq-geometric")return {primary:M().geometric({a1:v.a1,q:v.q},n)};
   if(id==="seq-geometric-edge")return {primary:M().geometric({a1:v.a1,q:qChoice[v.q]},n),q:qChoice[v.q]};
   if(id==="seq-linear-recurrence"||id==="seq-fixed-point")
     return {primary:M().linearRecurrence({a1:v.a1,r:v.r,c:v.c},n)};
   if(id==="seq-two-term")
     return {primary:M().twoTermRecurrence({a1:v.a1,a2:v.a2},n)};
   if(id==="seq-partial-sum"){
     return {primary:v.kind===0?M().arithmetic({a1:v.a1,d:v.d},n):
       M().geometric({a1:v.a1,q:v.q},n),kind:v.kind};
   }
   if(id==="seq-growth"){
     const comparison=M().compare({a1:v.a1,d:v.d,q:v.q},n);
     return {primary:{terms:comparison.arithmetic,sums:comparison.arithmeticSums},
       second:{terms:comparison.geometric,sums:comparison.geometricSums},
       comparison};
   }
   throw new RangeError("无法识别的数列场景");
 }
 function chart(parent,vals,other,n,startY,height,title,scene,kind){
   const plotL=62,plotR=725,plotW=plotR-plotL;
   const x=i=>plotL+(n===1?plotW/2:(i*plotW/(n-1)));
   const all=vals.concat(other||[]);
   const max=Math.max(1,...all.map(a=>Math.abs(a)));
   const limit=Math.max(1e-10,max*1.25);
   const middle=startY+height/2,extent=height*.43;
   const y=v=>middle-v/limit*extent;
   const group=svg(parent,"g",{"data-chart":kind});
   svg(group,"text",{x:14,y:startY+15,class:"lab-seq-heading"},title);
   svg(group,"line",{x1:plotL,y1:middle,x2:plotR,y2:middle,class:"lab-seq-axis"});
   for(let i=0;i<n;i++){
     if(n<=18 || i%2===0 || i===n-1){
       svg(group,"text",{x:x(i),y:startY+height-4,class:"lab-seq-tick",
         "text-anchor":"middle"},i+1);
     }
   }
   svg(group,"text",{x:10,y:middle-5,class:"lab-seq-axis-label"},"0");
   svg(group,"text",{x:plotL-8,y:startY+31,class:"lab-seq-axis-label"},fmt(max));
   const draw=(arr,cls)=>{
     arr.forEach((value,i)=>{
       if(!Number.isFinite(value))return;
       const xp=x(i),yp=y(value);
       svg(group,"line",{x1:xp,y1:middle,x2:xp,y2:yp,class:cls+" lab-seq-stem"});
       const mark=svg(group,"circle",{cx:xp,cy:yp,r:4.8,class:cls+" lab-seq-dot",
         role:"button",tabindex:"0","data-n":i+1,
         "aria-label":(cls==="lab-seq-secondary"?"第二数列 ":"")+
                       "第 "+(i+1)+" 项："+fmt(value)});
       const reveal=()=>{
         const meter=$("labCoordinateReadout");if(meter)meter.textContent=
           (kind==="sum"?"部分和 S":"数列项 a")+"_"+(i+1)+" = "+fmt(value)+
           "（有限项读数，不代表数学证明）";
       };
       mark.addEventListener("focus",reveal);
       mark.addEventListener("click",reveal);
       mark.addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();reveal()}});
     });
   };
   draw(vals,"lab-seq-primary");
   if(other)draw(other,"lab-seq-secondary");
 }
 function makeReflection(scene,preset){
   const area=scene.extraControls;
   if(!area)return;
   if(scene.renderedPreset===preset.id)return;
   scene.renderedPreset=preset.id;
   area.replaceChildren();area.hidden=false;
   const section=text(area,"section","lab-seq-reflection","");
   text(section,"h3","", "思考训练 · 先预测，再验证");
   text(section,"p","",preset.prediction_prompt||"先观察前几项。你觉得接下来会发生什么？");
   const stageWrap=text(section,"label","lab-seq-stage-label","现在属于哪种思考阶段？（学生自选）");
   const stageSelect=text(stageWrap,"select","lab-seq-stage","");
   stageSelect.setAttribute("aria-label","我的数列思考阶段");
   const stages=[
     ["START","观察条件"],["FORWARD","尝试正推"],["STUCK","思路卡住"],
     ["BACKWARD","从目标反推"],["CALCULATION","计算与边界"],["REFLECTION","方法复盘"]
   ];
   for(const [value,label] of stages){
      const option=text(stageSelect,"option","",label);option.value=value;
   }
   stageSelect.value=scene.thinkingStage||"START";
   stageSelect.onchange=()=>{scene.thinkingStage=stageSelect.value};
   const box=text(section,"textarea","lab-seq-prediction","");
   box.rows=3;box.maxLength=500;box.placeholder="只写你的猜想或方法，不需要完整证明。";
   box.setAttribute("aria-label","我的数列猜想（仅本次实验）");
   box.value=scene.prediction||"";
   box.oninput=()=>{scene.prediction=box.value};
   const actions=text(section,"div","lab-seq-actions","");
   const hint=text(actions,"button","btn btn-light","需要一点启发");
   hint.type="button";
   const result=text(section,"p","lab-seq-hint","");
   result.textContent="没有使用提示。调整一个参数，看看你的猜想是否依然成立。";
   hint.onclick=()=>{
     scene.hintLevel=Math.min(3,(scene.hintLevel||0)+1);
     const mode=document.querySelector(".mode.selected")?.dataset.mode||"GUIDE";
     const decision=root.MentorSeqPolicy?.decide({
       mode,stage:scene.thinkingStage||"START",helpRequested:true,
       hintLevel:scene.hintLevel,hints:preset.thinking_prompts
     });
     result.dataset.action=decision?.action||"CURATED_PROMPT";
     result.textContent="启发 "+scene.hintLevel+"/3（"+
       ({ANALYZE:"逻辑分析",GUIDE:"推理陪练",INDEPENDENT:"自主挑战"}[mode]||"推理陪练")+
       "）："+(decision?.message||preset.thinking_prompts[scene.hintLevel-1]);
   };
   const reset=text(actions,"button","btn btn-light","重新独立思考");
   reset.type="button";
   reset.onclick=()=>{
     scene.hintLevel=0;scene.prediction="";scene.thinkingStage="START";box.value="";
     stageSelect.value="START";
     result.textContent="重新开始思考：当前没有使用提示。";
   };
   const note=text(section,"small","", "草稿只保存在当前实验界面内；不计入学生成绩或已掌握知识。");
   note.setAttribute("data-learning-scope","LOCAL_ONLY_NOT_GRADED");
 }
 function renderAlternate(scene,values,assist){
   const place=scene.alternativeView;
   if(!place)return;
   place.replaceChildren();
   place.hidden=false;
   place.classList.add("lab-seq-table-wrapper");
   const table=text(place,"table","lab-seq-table","");
   const thead=text(table,"thead"),head=text(thead,"tr");
   for(const c of ["项号 n","数列项 aₙ",...(assist?["部分和 Sₙ"]:[])])
      text(head,"th","",c);
   const tbody=text(table,"tbody");
   values.terms.forEach((a,i)=>{
     const tr=text(tbody,"tr");
     text(tr,"th","",i+1);
     text(tr,"td","",fmt(a));
     if(assist)text(tr,"td","",fmt(values.sums[i]));
   });
 }
 function draw(rootSvg,preset,params,view,scene){
   const S=M();
   if(!S)throw new Error("数列数学内核尚未加载");
   const data=seriesFor(preset,params);
   const assist=Boolean(scene.assist),n=params.n;
   const amount=assist?n:Math.min(n,5);
   const visibleTerms=data.primary.terms.slice(0,amount);
   rootSvg.replaceChildren();rootSvg.setAttribute("viewBox","0 0 760 460");
   svg(rootSvg,"rect",{x:0,y:0,width:760,height:460,fill:"#fcfefb"});
   const topHeight=assist?210:340;
   chart(rootSvg,visibleTerms,data.second?data.second.terms.slice(0,amount):null,
     assist?n:amount,24,topHeight,"离散数列 aₙ（n 从 1 起）",scene,"term");
   if(assist){
     chart(rootSvg,data.primary.sums.slice(0,amount),
       data.second?data.second.sums.slice(0,amount):null,n,250,185,
       "部分和 Sₙ = a₁ + … + aₙ",scene,"sum");
   }else{
     svg(rootSvg,"text",{x:80,y:402,class:"lab-seq-message"},
       "先根据前 "+amount+" 项预测，再主动选择“显示后续项与部分和”。");
   }
   makeReflection(scene,preset);
   renderAlternate(scene,{terms:visibleTerms,sums:data.primary.sums.slice(0,amount)},assist);
   const info=[
     "当前展示 "+amount+" / "+n+" 项（只展示有限项）",
     "数学对象是离散数列，不是连续函数曲线"
   ];
   if(data.second)info.push("两列分别为等差与等比，比较绝对值应注意负公比");
   if(assist){
     info.push("第 "+n+" 项 aₙ="+fmt(data.primary.terms[n-1]));
     info.push("有限和 Sₙ="+fmt(data.primary.sums[n-1]));
     if(data.primary.special==="Q_ONE")info.push("q=1：每项不变，Sₙ=n·a₁（避免除以 1−q）");
     if(data.primary.special==="Q_ZERO")info.push("q=0：只有第一项可能非零");
     if(data.primary.special==="Q_NEG_ONE")info.push("q=−1：项数奇偶影响部分和");
     if(data.comparison)info.push(data.comparison.firstMagnitudeCrossover?
        "本区间首个等比绝对值较大的项号："+data.comparison.firstMagnitudeCrossover:
        "在这组有限项中未观察到绝对值超越");
     if(preset.id==="seq-fixed-point"){
       const {r,c}=params;
       info.push(r===1?"r=1：常量递推；一般不存在唯一平衡点":
         "候选平衡点 L="+fmt(c/(1-r))+"；图上趋近不等于已证明收敛");
     }
   }
   return {
     info,kind:"sequence_2d",latex:preset.latex,
     coordinateHint:"按 n 逐项观察：第 1 项是 a₁，不要把离散点误连成连续函数。",
     actual:data,shown:visibleTerms,finiteOnly:true
   };
 }
 root.MentorLabSequences={supports:id=>supported.has(id),draw};
})(window);
