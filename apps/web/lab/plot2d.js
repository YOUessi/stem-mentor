"use strict";
/* Deterministic offline high-school 2D plotting. No eval, no external requests. */
(function(root){
  const NS="http://www.w3.org/2000/svg";
  function element(parent,name,attrs,content){
    const n=document.createElementNS(NS,name);
    Object.entries(attrs||{}).forEach(pair=>n.setAttribute(pair[0],String(pair[1])));
    if(content!==undefined)n.textContent=String(content);
    parent.appendChild(n);return n;
  }
  const finite=n=>Number.isFinite(n);
  const clip=(x,lo,hi)=>Math.min(hi,Math.max(lo,x));
  function context(svg,zoom){
    const scale=48*zoom, width=760,height=460;
    const tx=x=>width/2+x*scale,ty=y=>height/2-y*scale;
    return {svg,zoom,scale,width,height,tx,ty,world:(px,py)=>[(px-width/2)/scale,(height/2-py)/scale]};
  }
  function rect(parent,x,y,w,h,cls){
    return element(parent,"rect",{x,y,width:w,height:h,class:cls});
  }
  function line(parent,c,x1,y1,x2,y2,opacity){
    return element(parent,"line",{x1,y1,x2,y2,class:c,opacity:opacity===undefined?1:opacity});
  }
  function point(parent,C,x,y,cls="lab-mark",label){
    const p=element(parent,"circle",{cx:C.tx(x),cy:C.ty(y),r:5,class:cls});
    if(label)element(parent,"text",{x:C.tx(x)+8,y:C.ty(y)-10,class:"lab-axis-label"},label);
    return p;
  }
  function drawGrid(C){
    const g=element(C.svg,"g",{class:"lab-grid",role:"presentation"});
    for(let k=-30;k<=30;k++){
      const x=C.tx(k),y=C.ty(k);
      if(x>0&&x<C.width)line(g,"lab-grid-line",x,0,x,C.height);
      if(y>0&&y<C.height)line(g,"lab-grid-line",0,y,C.width,y);
      if(k&&k%2===0){
        if(x>14&&x<C.width-15)element(g,"text",{x:x+3,y:C.ty(0)+14,class:"lab-tick-label"},k);
        if(y>16&&y<C.height-12)element(g,"text",{x:C.tx(0)+7,y:y-4,class:"lab-tick-label"},k);
      }
    }
    line(g,"lab-axis",0,C.ty(0),C.width,C.ty(0));
    line(g,"lab-axis",C.tx(0),0,C.tx(0),C.height);
    element(g,"text",{x:C.width-18,y:C.ty(0)-8,class:"lab-axis-label"},"x");
    element(g,"text",{x:C.tx(0)+9,y:17,class:"lab-axis-label"},"y");
    element(g,"text",{x:C.tx(0)+5,y:C.ty(0)+14,class:"lab-tick-label"},"O");
  }
  function lineWorld(C,a,b,c,d,cls){
    return line(C.svg,cls,C.tx(a),C.ty(b),C.tx(c),C.ty(d));
  }
  function curve(C,points,cls,close){
    const maxX=C.width/C.scale+2,maxY=C.height/C.scale+2;
    let segments=[],part=[],prev=null;
    function flush(){if(part.length>=2)segments.push(part);part=[];prev=null;}
    for(const xy of points){
      if(!xy||!finite(xy[0])||!finite(xy[1])||
         Math.abs(xy[0])>maxX || Math.abs(xy[1])>maxY){flush();continue}
      if(prev&&Math.abs(xy[1]-prev[1])>maxY/3)flush();
      part.push(xy);prev=xy;
    }
    flush();
    if(close&&segments.length===1 && points.length>2)segments[0].push(segments[0][0]);
    for(const arr of segments){
      const d=arr.map((v,i)=>(i?"L":"M")+C.tx(v[0]).toFixed(2)+" "+C.ty(v[1]).toFixed(2)).join(" ");
      element(C.svg,"path",{d,class:cls});
    }
    return segments.length;
  }
  function samples(fun,C,n=500){
    const left=C.world(0,0)[0],right=C.world(C.width,0)[0];
    const vals=[];
    for(let i=0;i<=n;i++){
      const x=left+(right-left)*i/n;
      let y;try{y=fun(x)}catch(e){y=NaN}
      vals.push([x,y]);
    }
    return vals;
  }
  function numericParams(preset,values){
    const p={};
    for(const param of preset.params){
      const raw=Number(values[param.key]??param.value);
      p[param.key]=Number.isFinite(raw)?clip(raw,param.min,param.max):param.value;
    }
    return p;
  }
  function familyFunction(id,p){
    switch(id){
      case "fn-linear": return x=>p.m*x+p.b;
      case "fn-quadratic":return x=>p.a*Math.pow(x-p.h,2)+p.k;
      case "fn-cubic":return x=>p.a*(Math.pow(x,3)-3*x)+p.k;
      case "fn-exp":return x=>(p.a>0&&Math.abs(p.a-1)>1e-8)?Math.pow(p.a,x):NaN;
      case "fn-log":return x=>(x>0&&p.a>0&&Math.abs(p.a-1)>1e-8)?Math.log(x)/Math.log(p.a):NaN;
      case "fn-sin":return x=>p.A*Math.sin(p.w*x+p.phi)+p.k;
      case "fn-cos":return x=>p.A*Math.cos(p.w*x+p.phi);
      case "fn-tan":return x=>Math.abs(Math.cos(p.w*x+p.phi))<.045?NaN:Math.tan(p.w*x+p.phi);
      case "fn-abs":return x=>p.a*Math.abs(x-p.h)+p.k;
      case "fn-inverse":return x=>Math.abs(x-p.h)<.06?NaN:p.a/(x-p.h)+p.k;
      case "fn-sqrt":return x=>(x>=p.h)?Math.sqrt(x-p.h)+p.k:NaN;
      case "fn-piecewise":return x=>x<p.h?p.m*x+p.b:p.a*Math.pow(x-p.h,2)+p.k;
      case "conic-line":return x=>p.m*x+p.b;
      default:return null;
    }
  }
  function statsForFunction(id,p){
    switch(id){
      case "fn-linear": return ["斜率 m = "+p.m.toFixed(2),"纵截距 b = "+p.b.toFixed(2)];
      case "fn-quadratic":return ["顶点 ("+p.h.toFixed(2)+","+p.k.toFixed(2)+")",
        "开口方向："+(p.a>0?"向上":p.a<0?"向下":"已退化为常函数")];
      case "fn-cubic":return ["导函数：a(3x²−3)","函数变化可与导数符号比较"];
      case "fn-exp":return [Math.abs(p.a-1)<1e-8?"底数 a=1 时图像成为常值 1，非通常所称指数函数":("底数 a = "+p.a.toFixed(2)), "y>0"];
      case "fn-log":return [Math.abs(p.a-1)<1e-8?"底数为 1，实数对数无定义":"定义域：x>0","过点 (1,0)"];
      case "fn-sin":return ["周期 T = "+(2*Math.PI/p.w).toFixed(2)+"（弧度单位）",
        "值域 ["+(p.k-Math.abs(p.A)).toFixed(2)+","+(p.k+Math.abs(p.A)).toFixed(2)+"]"];
      case "fn-cos":return ["周期 T = "+(2*Math.PI/p.w).toFixed(2),"角度单位：弧度"];
      case "fn-tan":return ["正切的渐近线不属于函数图像","周期 T = "+(Math.PI/p.w).toFixed(2)];
      case "fn-abs":return ["折点："+p.h.toFixed(2)+","+p.k.toFixed(2)];
      case "fn-inverse":return ["不可取 x="+p.h.toFixed(2),"水平渐近线 y="+p.k.toFixed(2)];
      case "fn-sqrt":return ["定义域 x≥"+p.h.toFixed(2),"起点 y="+p.k.toFixed(2)];
      case "fn-piecewise":{
        const left=p.m*p.h+p.b,right=p.k;
        return ["分段点 x="+p.h.toFixed(2),"左右侧值分别为 "+left.toFixed(2)+" 和 "+right.toFixed(2),
               Math.abs(left-right)<1e-6?"分段点左右接续":"分段点不连续"];
      }
      default:return [];
    }
  }
  function dashed(C,a,b,c,d){
    return lineWorld(C,a,b,c,d,"lab-construction");
  }
  function drawConic(C,id,p){
    const info=[];
    const circle=(center,r,style)=>{
      const pts=Array.from({length:361},(_,i)=>{
        const t=2*Math.PI*i/360;return [center[0]+r*Math.cos(t),center[1]+r*Math.sin(t)];
      });curve(C,pts,style||"lab-main-curve");
    };
    const param=(fun,limit=300,style="lab-main-curve")=>{
      const pts=Array.from({length:limit+1},(_,i)=>fun(i/limit));
      curve(C,pts,style);
    };
    if(id==="conic-circle"){
      circle([p.h,p.k],p.r);
      point(C.svg,C,p.h,p.k,"lab-focus","O");
      dashed(C,p.h,p.k,p.h+p.r,p.k);
      info.push("圆心 ("+p.h+","+p.k+")","半径 r="+p.r);
    }else if(id==="conic-ellipse"){
      param(t=>[p.h+p.a*Math.cos(t*2*Math.PI),p.k+p.b*Math.sin(t*2*Math.PI)],360);
      const major=Math.max(p.a,p.b),minor=Math.min(p.a,p.b);
      const c=Math.sqrt(Math.max(0,major*major-minor*minor));
      const f1=p.a>=p.b?[p.h-c,p.k]:[p.h,p.k-c],f2=p.a>=p.b?[p.h+c,p.k]:[p.h,p.k+c];
      point(C.svg,C,...f1,"lab-focus","F1");
      point(C.svg,C,...f2,"lab-focus","F2");
      info.push("焦距参数 c="+c.toFixed(3),"焦点方向："+(p.a>=p.b?"横轴":"纵轴"));
      if(Math.abs(p.a-p.b)<1e-8)info.push("两轴相等，此时是圆（焦点重合）");
    }else if(id==="conic-hyperbola"){
      for(const side of [-1,1])
        param(t=>{
          const u=(t*2-1)*2.4;
          return [p.h+side*p.a*Math.cosh(u),p.k+p.b*Math.sinh(u)];
        },420);
      const extent=16;
      dashed(C,p.h-extent,p.k-extent*p.b/p.a,p.h+extent,p.k+extent*p.b/p.a);
      dashed(C,p.h-extent,p.k+extent*p.b/p.a,p.h+extent,p.k-extent*p.b/p.a);
      const c=Math.hypot(p.a,p.b);
      point(C.svg,C,p.h-c,p.k,"lab-focus","F1");
      point(C.svg,C,p.h+c,p.k,"lab-focus","F2");
      info.push("焦距参数 c="+c.toFixed(3),"渐近线斜率 ±"+(p.b/p.a).toFixed(3));
    }else if(id==="conic-parabola"){
      param(t=>{
        const u=t*11-5.5;return [p.h+p.p*u*u/4,p.k+p.p*u];
      },480);
      const focus=[p.h+p.p,p.k];
      point(C.svg,C,...focus,"lab-focus","F");
      dashed(C,p.h-p.p,-12,p.h-p.p,12);
      point(C.svg,C,p.h,p.k,"lab-focus","V");
      info.push("焦点 ("+focus[0].toFixed(2)+","+focus[1].toFixed(2)+")",
        "准线 x="+(p.h-p.p).toFixed(2));
    }else if(id==="conic-intersection"){
      circle([p.h,0],p.r,"lab-secondary-curve");
      curve(C,samples(x=>p.m*x+p.b,C),"lab-main-curve");
      const A=1+p.m*p.m,B=-2*p.h+2*p.m*p.b,D=p.h*p.h+p.b*p.b-p.r*p.r;
      const delta=B*B-4*A*D;
      const xs=delta<0?[]:Math.abs(delta)<1e-8?[-B/(2*A)]:
         [(-B+Math.sqrt(delta))/(2*A),(-B-Math.sqrt(delta))/(2*A)];
      for(const x of xs)point(C.svg,C,x,p.m*x+p.b,"lab-focus");
      info.push("交点个数："+xs.length,delta<0?"相离":Math.abs(delta)<1e-8?"相切":"相交");
    }else if(id==="conic-line"){
      curve(C,samples(x=>p.m*x+p.b,C),"lab-main-curve");
      info.push("斜率 "+p.m.toFixed(2),"纵截距 "+p.b.toFixed(2));
    }
    return info;
  }
  function draw(root,preset,values,view){
    root.replaceChildren();
    root.setAttribute("viewBox","0 0 760 460");
    const zoom=view?.zoom||1,C=context(root,zoom),id=preset.id,p=numericParams(preset,values);
    drawGrid(C);
    const info=[];
    let evaluateAtX=null;
    if(preset.tool==="function_2d"||id==="conic-line"){
      const fn=familyFunction(id,p);
      if(fn){
        // Always exclude invalid real-domain points; never eval user-supplied code.
        curve(C,samples(fn,C,690),"lab-main-curve");
        evaluateAtX=fn;
        info.push(...statsForFunction(id,p));
        if(id==="fn-quadratic"){
          point(C.svg,C,p.h,p.k,"lab-focus","V");
          dashed(C,p.h,-9,p.h,9);
        }
        if(id==="fn-inverse"){
          dashed(C,p.h,-9,p.h,9);
          dashed(C,-10,p.k,10,p.k);
        }
        if(id==="fn-piecewise"){
          const left=p.m*p.h+p.b;
          point(C.svg,C,p.h,left,"lab-open-point");
          point(C.svg,C,p.h,p.k,"lab-focus");
        }
        if(id==="fn-log"||id==="fn-exp") info.push("底数在 0 与 1 之间时，单调性可能改变");
      }
    }else{
      info.push(...drawConic(C,id,p));
    }
    return {
      info,
      kind:preset.tool,
      zoom,
      toWorld:(px,py)=>C.world(px,py),
      evaluate:evaluateAtX,
      formula:preset.latex,
      view:C,
      id:preset.id
    };
  }
  root.MentorLab2D={draw,numericParams,familyFunction,conicInfo:statsForFunction,context};
})(window);
