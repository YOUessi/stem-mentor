"use strict";
/* Closed-interval extrema explorer: show mathematical candidates only after opt-in. */
(function(root){
 const NS="http://www.w3.org/2000/svg";
 const items={
  "extrema-quadratic":"quadratic","extrema-cubic":"cubic",
  "extrema-absolute":"absolute","extrema-sine":"sine","extrema-log":"log"
 };
 const M=()=>root.MentorExtremaMath;
 const fmt=n=>Number.isFinite(n)?Number(n.toPrecision(6)).toString():"未定义";
 function svg(parent,tag,attrs={},txt){
  const el=document.createElementNS(NS,tag);
  for(const [k,v] of Object.entries(attrs))el.setAttribute(k,String(v));
  if(txt!==undefined)el.textContent=String(txt);
  parent.appendChild(el);return el;
 }
 function add(parent,tag,cls,txt){
   const el=document.createElement(tag);if(cls)el.className=cls;
   if(txt!==undefined)el.textContent=String(txt);
   parent.appendChild(el);return el;
 }
 function newControls(scene,preset){
   if(!scene.extraControls)return;
   if(scene.drawnPreset===preset.id)return;
   scene.drawnPreset=preset.id;scene.extraControls.replaceChildren();
   scene.extraControls.hidden=false;
   const section=add(scene.extraControls,"section","lab-extrema-panel");
   add(section,"h3",null,"先找候选点，再作全局比较");
   add(section,"p",null,preset.prediction_prompt);
   const input=add(section,"textarea","lab-extrema-guess","");
   input.rows=2;input.maxLength=450;input.placeholder="我猜最值在……，理由是……";
   input.setAttribute("aria-label","我的最值候选猜想");
   input.value=scene.guess||"";
   input.addEventListener("input",()=>{scene.guess=input.value});
   const hint=add(section,"button","btn btn-light","请求下一个思考提示");
   hint.type="button";
   const info=add(section,"p","lab-extrema-hint","默认没有提示。先判断可能的候选位置。");
   hint.addEventListener("click",()=>{
     scene.hintLevel=Math.min(3,(scene.hintLevel||0)+1);
     info.textContent="提示 "+scene.hintLevel+"/3："+preset.thinking_prompts[scene.hintLevel-1];
   });
   add(section,"small",null,"只是有限的固定数学模型；观察与猜想不会计入成绩或掌握状态。");
 }
 function draw(el,preset,p,view,scene){
   const lib=M();if(!lib)throw Error("闭区间数学内核未加载");
   const kind=items[preset.id];
   if(!kind)throw Error("没有此闭区间最值场景");
   newControls(scene,preset);
   const result=lib.analyze(kind,p);
   el.replaceChildren();el.setAttribute("viewBox","0 0 760 460");
   svg(el,"rect",{x:0,y:0,width:760,height:460,fill:"#fcfefb"});
   if(!result.valid){
     svg(el,"text",{x:80,y:168,class:"lab-extrema-error"},result.error);
     svg(el,"text",{x:80,y:199,class:"lab-extrema-note"},"请修改闭区间端点与函数定义域。此处不显示不存在的最值。");
     return {info:["无合法闭区间："+result.error],kind:"function_2d",
       coordinateHint:result.error,latex:preset.latex,valid:false};
   }
   const W=760,H=460,xx0=62,xx1=735,yy0=55,yy1=411;
   const xmin=Math.min(-4,p.L-.5),xmax=Math.max(4,p.R+.5);
   const xcoord=x=>xx0+(x-xmin)*(xx1-xx0)/(xmax-xmin);
   // Fit the finite y-range to prevent peaks outside the viewport.
   let ymin=Math.min(0,result.globalMin.value),ymax=Math.max(0,result.globalMax.value);
   const buffer=Math.max(1,(ymax-ymin)*.12);
   ymin-=buffer;ymax+=buffer;
   const ycoord=y=>yy1-(y-ymin)*(yy1-yy0)/(ymax-ymin);
   const plot=svg(el,"g",{"data-extrema-kind":kind});
   const rangeX=xcoord(p.R)-xcoord(p.L);
   svg(plot,"rect",{x:xcoord(p.L),y:yy0,width:rangeX,height:yy1-yy0,class:"lab-extrema-interval"});
   for(let i=0;i<=8;i++){
     const x=xmin+(xmax-xmin)*i/8;
     const xpx=xcoord(x);
     svg(plot,"line",{x1:xpx,y1:yy0,x2:xpx,y2:yy1,class:"lab-extrema-grid"});
     svg(plot,"text",{x:xpx,y:yy1+19,class:"lab-extrema-tick","text-anchor":"middle"},fmt(x));
   }
   for(let j=0;j<=4;j++){
     const y=ymin+(ymax-ymin)*j/4,yp=ycoord(y);
     svg(plot,"line",{x1:xx0,y1:yp,x2:xx1,y2:yp,class:"lab-extrema-grid"});
     svg(plot,"text",{x:xx0-7,y:yp+4,class:"lab-extrema-tick","text-anchor":"end"},fmt(y));
   }
   if(ymin<=0&&ymax>=0){
     svg(plot,"line",{x1:xx0,y1:ycoord(0),x2:xx1,y2:ycoord(0),class:"lab-extrema-axis"});
   }
   if(xmin<=0&&xmax>=0){
     svg(plot,"line",{x1:xcoord(0),y1:yy0,x2:xcoord(0),y2:yy1,class:"lab-extrema-axis"});
   }
   let d="";
   for(let i=0;i<=360;i++){
      const x=p.L+(p.R-p.L)*i/360;
      const y=lib.value(kind,p,x);
      if(Number.isFinite(y))
         d+=(d?" L":"M")+xcoord(x).toFixed(2)+","+ycoord(y).toFixed(2);
   }
   svg(plot,"path",{d,class:"lab-extrema-curve"});
   for(const [x,label] of [[p.L,"L"],[p.R,"R"]]){
     const y=lib.value(kind,p,x);
     svg(plot,"line",{x1:xcoord(x),y1:yy0,x2:xcoord(x),y2:yy1,
        class:"lab-extrema-endline"});
     svg(plot,"circle",{cx:xcoord(x),cy:ycoord(y),r:5,class:"lab-extrema-endpoint"});
     svg(plot,"text",{x:xcoord(x),y:yy0-9,"text-anchor":"middle",
        class:"lab-extrema-title"},label);
   }
   if(scene.assist){
     for(const pt of result.candidates){
       const e=svg(plot,"circle",{cx:xcoord(pt.x),cy:ycoord(pt.value),r:7,
          class:pt.tags.includes("nondifferentiable")?"lab-extrema-cusp":"lab-extrema-candidate",
          "data-extrema-point":"true","data-type":pt.type,
          "data-x":pt.x,"data-value":pt.value,tabindex:0,role:"button",
          "aria-label":"候选 x="+fmt(pt.x)+" f(x)="+fmt(pt.value)});
       svg(e,"title",{},pt.tags.join(" + ")+": f("+fmt(pt.x)+")="+fmt(pt.value));
     }
   }
   const metrics=[
       "闭区间 ["+fmt(p.L)+", "+fmt(p.R)+"]",
       "图像限于闭区间内；端点用 L、R 标记",
       scene.assist?"已显示端点、驻点与不可导点候选":"先比较可能的候选点，再自主勾选完整比较"
   ];
   if(scene.assist){
     metrics.push("候选数："+result.candidates.length+
       "（驻点 "+result.stationary.length+"、不可导点 "+result.nondifferentiable.length+"）");
     if(result.constant)metrics.push("常值函数：区间内每一点都取到相同最大和最小值");
     metrics.push("全局最小值："+fmt(result.globalMin.value)+
       (result.globalMin.allPoints?"（所有 x∈区间）":"，位置："+result.globalMin.points.map(fmt).join("，")));
     metrics.push("全局最大值："+fmt(result.globalMax.value)+
       (result.globalMax.allPoints?"（所有 x∈区间）":"，位置："+result.globalMax.points.map(fmt).join("，")));
     metrics.push("极值候选不能只看 f′(x)=0；还要比较端点和不可导点");
   }
   return {info:metrics,kind:"function_2d",valid:true,latex:preset.latex,
     coordinateHint:"绿色阴影仅指题目闭区间，L/R 是两端点。先预测，再主动显示候选比较。",
     evaluate:x=>lib.value(kind,p,x),
     toWorld:(sx,sy)=>[
       xmin+(sx-xx0)*(xmax-xmin)/(xx1-xx0),
       ymin+(yy1-sy)*(ymax-ymin)/(yy1-yy0)
     ]};
 }
 root.MentorLabExtrema={supports:id=>Boolean(items[id]),draw};
})(window);
