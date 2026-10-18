/* Green v0.9: planar vectors, unit circle and secant-to-tangent explorers. */
(function(root){
 'use strict';
 const M=root.MentorExplorationMath,NS='http://www.w3.org/2000/svg';
 const ids=new Set(['vec2d-add','vec2d-projection','unit-circle','derivative-quadratic','derivative-cubic','derivative-log','derivative-abs']);
 const fmt=(x,d=3)=>Number.isFinite(x)?(Math.abs(x)<1e-12?0:x).toFixed(d):'未定义';
 function e(parent,tag,attrs={},text){const n=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=String(text);parent.appendChild(n);return n}
 function line(svg,a,b,cls){return e(svg,'line',{x1:a[0],y1:a[1],x2:b[0],y2:b[1],class:cls})}
 function label(svg,p,t,cls='lab-axis-label'){return e(svg,'text',{x:p[0]+9,y:p[1]-9,class:cls},t)}
 function arrow(svg,a,b,cls){
   line(svg,a,b,cls);const dx=b[0]-a[0],dy=b[1]-a[1],L=Math.hypot(dx,dy);if(L<1e-8)return;
   const ux=dx/L,uy=dy/L,q=[b[0]-10*ux,b[1]-10*uy];
   e(svg,'polygon',{points:[b,[q[0]-4*uy,q[1]+4*ux],[q[0]+4*uy,q[1]-4*ux]].map(v=>v.join(',')).join(' '),class:'lab-arrow-tip'});
 }
 function bind(svg,scene,preset,view,params,pick){
   svg.onpointerdown=ev=>{const n=ev.target.closest?.('[data-handle]');if(!n)return;scene.handle=n.dataset.handle;svg.setPointerCapture(ev.pointerId);ev.preventDefault()};
   svg.onpointermove=ev=>{
     if(!scene.handle)return;
     const mat=svg.getScreenCTM();if(!mat)return;const p=svg.createSVGPoint();p.x=ev.clientX;p.y=ev.clientY;const local=p.matrixTransform(mat.inverse());
     const patch=pick(scene.handle,[local.x,local.y]);scene.onParams?.(patch);ev.preventDefault();
   };
   svg.onpointerup=svg.onpointercancel=()=>{scene.handle=null};
 }
 function vectorScene(svg,preset,p,view,scene){
   const C=root.MentorLab2D.context(svg,view.zoom||1),xy=v=>[C.tx(v[0]),C.ty(v[1])];
   root.MentorLab2D.drawGrid(C);
   const a=[p.ax,p.ay],b=[p.bx,p.by],v=M.vectorMetrics(a,b,p.k),O=xy([0,0]);
   arrow(svg,O,xy(a),'lab-vector-a');arrow(svg,O,xy(b),'lab-vector-b');
   for(const [name,pt] of [['a',a],['b',b]]){
     const q=xy(pt);const n=e(svg,'circle',{cx:q[0],cy:q[1],r:9,class:'lab-vector-handle','data-handle':name,tabindex:0,role:'slider','aria-label':'拖动向量 '+name+' 的端点'});label(svg,q,name);
     n.onkeydown=ev=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(ev.key))return;ev.preventDefault();const dx=ev.key==='ArrowLeft'?-.1:ev.key==='ArrowRight'?.1:0,dy=ev.key==='ArrowDown'?-.1:ev.key==='ArrowUp'?.1:0;scene.onParams?.({[name+'x']:pt[0]+dx,[name+'y']:pt[1]+dy})};
   }
   const info=['a=('+fmt(a[0])+','+fmt(a[1])+')','b=('+fmt(b[0])+','+fmt(b[1])+')','a·b='+fmt(v.dot),
     '|a|='+fmt(v.lengthA),'|b|='+fmt(v.lengthB),'夹角='+ (v.angleDegrees===null?'未定义（零向量）':fmt(v.angleDegrees)+'°')];
   if(scene.assist){
     if(preset.id==='vec2d-add'){
       const sum=xy(v.sum);line(svg,xy(a),sum,'lab-explore-dashed');line(svg,xy(b),sum,'lab-explore-dashed');
       arrow(svg,O,sum,'lab-resultant');label(svg,sum,'a+b');arrow(svg,O,xy(v.scaled),'lab-scaled-vector');label(svg,xy(v.scaled),'ka');
       info.push('a+b=('+v.sum.map(x=>fmt(x)).join(',')+')','a-b=('+v.difference.map(x=>fmt(x)).join(',')+')','k='+fmt(p.k));
     }else if(v.projection){
       arrow(svg,O,xy(v.projection),'lab-projection');line(svg,xy(a),xy(v.projection),'lab-explore-dashed');label(svg,xy(v.projection),'H');
       info.push('投影长度（有向）='+fmt(v.projectionScalar),'a = proj_b(a) + 垂直分量');
     }else info.push('不能投影到零向量：方向未定义');
   }else info.push('自主勾选辅助图形后，核对自己的加法或投影猜想');
   bind(svg,scene,preset,view,p,(handle,point)=>{const q=C.world(...point);return {[handle+'x']:q[0],[handle+'y']:q[1]}});
   return {info,kind:'vector_2d',toWorld:(x,y)=>C.world(x,y)};
 }
 function unitScene(svg,preset,p,view,scene){
   const U=M.unitCircle(p.theta),center=[198,230],r=116;
   line(svg,[37,230],[353,230],'lab-axis');line(svg,[198,57],[198,391],'lab-axis');
   e(svg,'circle',{cx:198,cy:230,r,class:'lab-unit-circle'});
   const pt=[198+r*U.cos,230-r*U.sin];arrow(svg,center,pt,'lab-vector-a');
   line(svg,pt,[pt[0],230],'lab-explore-dashed');line(svg,pt,[198,pt[1]],'lab-explore-dashed');
   e(svg,'circle',{cx:pt[0],cy:pt[1],r:9,class:'lab-unit-point','data-handle':'theta',tabindex:0,role:'slider','aria-label':'单位圆角度：用方向键调整'});
   label(svg,pt,'P');label(svg,[312,244],'1');label(svg,[191,108],'1');
   e(svg,'text',{x:30,y:28,class:'lab-scene-label'},'单位圆 → 坐标 → 正弦/余弦');
   e(svg,'text',{x:43,y:421,class:'lab-axis-label'},'θ='+fmt(p.theta,0)+'° = '+fmt(U.radians)+' rad');
   const X=t=>415+t*305/(Math.PI*2),Y=v=>230-v*94;
   line(svg,[405,230],[742,230],'lab-axis');line(svg,[415,101],[415,360],'lab-axis');
   ['sin θ','cos θ'].forEach((v,i)=>e(svg,'text',{x:432+i*105,y:78,class:i?'lab-cos-label':'lab-axis-label'},v));
   for(const [fn,cls] of [[Math.sin,'lab-linked-sin'],[Math.cos,'lab-linked-cos']]){
     const points=Array.from({length:161},(_,i)=>{const t=i*Math.PI*2/160;return [X(t),Y(fn(t))]});
     e(svg,'path',{class:cls,d:points.map((v,i)=>(i?'L':'M')+v.join(' ')).join(' ')});
   }
   const t=U.normalizedDegrees*Math.PI/180;
   line(svg,[X(t),113],[X(t),347],'lab-explore-dashed');
   for(const [y,cls] of [[U.sin,'lab-linked-sin-dot'],[U.cos,'lab-linked-cos-dot']])e(svg,'circle',{cx:X(t),cy:Y(y),r:5,class:cls});
   e(svg,'text',{x:706,y:249,class:'lab-tick-label'},'2π');
   if(scene.assist){
     line(svg,[center[0]+r,62],[center[0]+r,389],'lab-unit-tangent');
     if(U.tan!==null&&Math.abs(U.tan)<=1.4){const q=[center[0]+r,center[1]-r*U.tan];line(svg,center,q,'lab-explore-dashed');e(svg,'circle',{cx:q[0],cy:q[1],r:5,class:'lab-focus'})}
   }
   const axes={X_POS:'x 正半轴',X_NEG:'x 负半轴',Y_POS:'y 正半轴',Y_NEG:'y 负半轴'};
   const info=['sin θ='+fmt(U.sin),'cos θ='+fmt(U.cos),'tan θ='+fmt(U.tan),U.quadrant?'第 '+U.quadrant+' 象限':axes[U.axis],
       'sin²θ+cos²θ='+fmt(U.sin*U.sin+U.cos*U.cos),U.tan===null?'正切未定义：cos θ=0':'度数可跨多圈；相同终边对应相同坐标'];
   svg.querySelector('.lab-unit-point').onkeydown=ev=>{if(ev.key==='ArrowLeft'||ev.key==='ArrowRight'){ev.preventDefault();scene.onParams?.({theta:p.theta+(ev.key==='ArrowRight'?1:-1)})}};
   bind(svg,scene,preset,view,p,(_handle,point)=>{const a=Math.atan2(center[1]-point[1],point[0]-center[0])*180/Math.PI;return {theta:a+360*Math.round((p.theta-a)/360)}});
   return {info,kind:'function_2d',toWorld:(x,y)=>[(x-198)/r,(230-y)/r]};
 }
 function derivativeScene(svg,preset,p,view,scene){
   const K=preset.id.replace('derivative-',''),C=root.MentorLab2D.context(svg,view.zoom||1),f=x=>M.functionValue(K,x);
   root.MentorLab2D.drawGrid(C);root.MentorLab2D.curve(C,root.MentorLab2D.samples(f,C,650),'lab-main-curve');
   const q=M.derivativeInfo(K,p.x,p.h),info=['基点 x='+fmt(p.x),'增量 h='+fmt(p.h)];
   if(q.domainValid){
     root.MentorLab2D.point(svg,C,p.x,q.y,'lab-focus','P');
     if(q.nextY!==null)root.MentorLab2D.point(svg,C,q.nextX,q.nextY,'lab-mark','Q');
     if(q.secantValid){root.MentorLab2D.curve(C,root.MentorLab2D.samples(x=>q.y+q.secantSlope*(x-p.x),C),'lab-secant');info.push('割线斜率 Δy/Δx='+fmt(q.secantSlope))}
     else info.push(p.h===0?'h=0，割线未定义（不能直接用 0 作分母）':'Q 越出定义域，不显示割线');
     if(q.differentiable){
       if(scene.assist){root.MentorLab2D.curve(C,root.MentorLab2D.samples(x=>q.y+q.tangentSlope*(x-p.x),C),'lab-tangent');info.push('解析导数 f\'(x)='+fmt(q.tangentSlope));if(q.secantValid)info.push('斜率差='+fmt(q.secantSlope-q.tangentSlope,5))}
       else info.push('先观察差商，再自主显示解析切线核对');
     }else info.push('该点不可导：左右斜率不同，不画虚假的唯一切线');
   }else info.push('P 不在实数定义域中，切线与割线都不可用');
   return {info,kind:'function_2d',toWorld:(x,y)=>C.world(x,y),evaluate:f};
 }
 function draw(svg,preset,params,view,scene){
   svg.replaceChildren();svg.setAttribute('viewBox','0 0 760 460');
   if(preset.id.startsWith('vec2d-'))return vectorScene(svg,preset,params,view,scene);
   if(preset.id==='unit-circle')return unitScene(svg,preset,params,view,scene);
   return derivativeScene(svg,preset,params,view,scene);
 }
 root.MentorLabExplorers={supports:id=>ids.has(id),draw};
})(window);
