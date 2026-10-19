/* v0.10 real number-line visualization consumes the tested interval algebra only. */
(function(root){
 'use strict';
 const NS='http://www.w3.org/2000/svg',M=root.MentorIntervalMath;
 const IDS=new Set(['interval-single','interval-operations','ineq-linear','ineq-quadratic','ineq-absolute']);
 const REL=['lt','le','gt','ge'],SYMBOL=['<','≤','>','≥'];
 const fmt=n=>Number.isFinite(n)?String(Number(n.toPrecision(6))):n<0?'−∞':'+∞';
 function svg(parent,tag,attrs={},label){
   const n=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));
   if(label!==undefined)n.textContent=String(label);parent.appendChild(n);return n;
 }
 function entered(p,prefix=''){
   return M.interval(p[prefix+'lc']===2?-Infinity:p[prefix+'lo'],p[prefix+'rc']===2?Infinity:p[prefix+'hi'],
                    p[prefix+'lc']===1,p[prefix+'rc']===1);
 }
 function model(preset,p){
   if(preset.id==='interval-single'){const a=entered(p);return {rows:[{label:'输入 I',parts:a,prefix:''}],solution:null,input:a};}
   if(preset.id==='interval-operations'){
     const a=entered(p,'a'),b=entered(p,'b');
     const op=[()=>M.intersect(a,b),()=>M.union(a,b),()=>M.difference(a,b),()=>M.complement(a)];
     return {rows:[{label:'输入 A',parts:a,prefix:'a'},{label:'输入 B',parts:b,prefix:'b'}],
       solution:op[p.op](),expression:['A ∩ B','A ∪ B','A ∖ B','ℝ ∖ A'][p.op]};
   }
   const relation=REL[p.relation];let solved,expression,left;
   if(preset.id==='ineq-linear'){
     solved=M.solveLinear(p.a,p.b,relation);expression=fmt(p.a)+'x + ('+fmt(p.b)+') '+SYMBOL[p.relation]+' 0';left=p.a*p.probe+p.b;
   }else if(preset.id==='ineq-quadratic'){
     solved=M.solveQuadratic(p.a,p.b,p.c,relation);expression=fmt(p.a)+'x² + ('+fmt(p.b)+')x + ('+fmt(p.c)+') '+SYMBOL[p.relation]+' 0';left=p.a*p.probe*p.probe+p.b*p.probe+p.c;
   }else{
     solved=M.solveAbs(p.h,p.r,relation);expression='|x − ('+fmt(p.h)+')| '+SYMBOL[p.relation]+' '+fmt(p.r);left=Math.abs(p.probe-p.h);
   }
   return {rows:[],solution:solved.intervals,solved,expression,left};
 }
 function makeScale(data,p,show){
   const values=[-6,6,p.probe];
   for(const row of data.rows){
     values.push(p[row.prefix+'lo'],p[row.prefix+'hi']);
     for(const part of row.parts)values.push(part.lo,part.hi);
   }
   if(show)for(const part of data.solution||[])values.push(part.lo,part.hi);
   const finite=values.filter(Number.isFinite);let lo=Math.min(...finite),hi=Math.max(...finite);
   const padding=Math.max(1,(hi-lo)*.1);lo-=padding;hi+=padding;
   const x=v=>70+(v-lo)/(hi-lo)*620;
   return {lo,hi,x,world:px=>lo+(px-70)*(hi-lo)/620};
 }
 function ticks(parent,scale,y){
   svg(parent,'line',{x1:38,x2:727,y1:y,y2:y,class:'lab-axis'});
   const approx=(scale.hi-scale.lo)/10,power=10**Math.floor(Math.log10(approx));
   const step=[1,2,5,10].find(v=>v*power>=approx)*power;
   for(let k=Math.ceil(scale.lo/step);k*step<=scale.hi;k++){
     const val=k*step,x=scale.x(val);
     svg(parent,'line',{x1:x,x2:x,y1:y-5,y2:y+5,class:'lab-num-tick'});
     svg(parent,'text',{x,y:y+24,'text-anchor':'middle',class:'lab-tick-label'},fmt(val));
   }
   svg(parent,'text',{x:735,y:y+5,class:'lab-axis-label'},'x');
 }
 function end(parent,scale,value,y,closed,result){
   if(!Number.isFinite(value)){
     const x=value<0?40:720,direction=value<0?-1:1;
     svg(parent,'path',{d:'M '+(x-direction*10)+' '+(y-6)+' L '+x+' '+y+' L '+(x-direction*10)+' '+(y+6),
       class:'lab-interval-arrow'+(result?' result':''),'data-infinite-end':value<0?'left':'right'});return;
   }
   svg(parent,'circle',{cx:scale.x(value),cy:y,r:6,class:'lab-interval-end '+(closed?'closed':'open')+(result?' result':''),'data-endpoint':fmt(value),'data-closed':String(closed)});
 }
 function plotParts(parent,scale,parts,y,result=false,inputHandles=false){
   if(!parts.length){svg(parent,'text',{x:380,y:y-15,'text-anchor':'middle',class:'lab-num-empty'},'∅ 空集');return;}
   for(const part of parts){
     const a=Number.isFinite(part.lo)?scale.x(part.lo):40,b=Number.isFinite(part.hi)?scale.x(part.hi):720;
     svg(parent,'line',{x1:a,x2:b,y1:y,y2:y,class:'lab-interval-segment'+(result?' result':''),'data-interval':M.format([part])});
     if(!inputHandles||!Number.isFinite(part.lo))end(parent,scale,part.lo,y,part.loClosed,result);
     if(part.hi!==part.lo&&(!inputHandles||!Number.isFinite(part.hi)))end(parent,scale,part.hi,y,part.hiClosed,result);
   }
 }
 function handle(parent,scale,value,y,key,closed,p,scene){
   const circle=svg(parent,'circle',{cx:scale.x(value),cy:y,r:8,
     class:'lab-interval-handle '+(closed?'closed':'open'),'data-handle':key,role:'button',tabindex:0,
     'aria-label':key+' 端点 '+fmt(value)+'，方向键可调整'});
   circle.addEventListener('keydown',e=>{
     if(e.key!=='ArrowRight'&&e.key!=='ArrowLeft')return;e.preventDefault();
     scene.onParams({[key]:p[key]+(e.key==='ArrowRight'?.1:-.1)});
   });
 }
 function draw(rootSvg,preset,p,view,scene){
   rootSvg.replaceChildren();rootSvg.setAttribute('viewBox','0 0 760 460');
   const data=model(preset,p),scale=makeScale(data,p,scene.assist),isSingle=preset.id==='interval-single';
   const info=[],rows=data.rows.length===2?[140,245]:[225];
   svg(rootSvg,'text',{x:35,y:31,class:'lab-scene-label'},'实数轴：空心排除、实心包含；无穷箭头表示延伸，不是屏幕边界处的端点。');
   data.rows.forEach((row,i)=>{
     const y=rows[i];ticks(rootSvg,scale,y);
     svg(rootSvg,'text',{x:42,y:y-41,class:'lab-axis-label'},row.label+' = '+M.format(row.parts));
     plotParts(rootSvg,scale,row.parts,y,false,true);
     for(const [side,mode] of [['lo','lc'],['hi','rc']]){
       const key=row.prefix+side,code=p[row.prefix+mode];
       const input=document.getElementById('labParam_'+key);if(input)input.disabled=code===2;
       if(code!==2)handle(rootSvg,scale,p[key],y,key,code===1,p,scene);
     }
     info.push(row.label+' = '+M.format(row.parts));
   });
   if(data.solution!==null&&scene.assist){
     const y=data.rows.length?350:247;
     ticks(rootSvg,scale,y);plotParts(rootSvg,scale,data.solution,y,true);
     svg(rootSvg,'text',{x:42,y:y-51,class:'lab-num-caption'},(data.expression||'')+'  的结果 / 解集：');
     svg(rootSvg,'text',{x:42,y:y-26,class:'lab-num-solution',id:'labSolutionText'},M.format(data.solution));
     info.push('解集 = '+M.format(data.solution));
     info.push('探针 x='+fmt(p.probe)+(M.contains(data.solution,p.probe)?' 属于结果':' 不属于结果'));
   }else if(data.solution!==null){
     const y=data.rows.length?350:247;ticks(rootSvg,scale,y);
     svg(rootSvg,'text',{x:42,y:y-35,class:'lab-num-prompt'},'结果尚未展示。先形成自己的猜想，再勾选上方的核对开关。');
     info.push('结果未展示：先独立判断，再主动核对');
   }
   if(!data.rows.length){
     svg(rootSvg,'text',{x:42,y:77,class:'lab-num-equation'},data.expression);
     info.push('当前不等式：'+data.expression,'探针 x='+fmt(p.probe)+' 时左侧值 ≈ '+fmt(data.left));
     if(scene.assist&&data.solved.kind==='CONSTANT')info.push('系数退化：当前为常值命题');
     if(scene.assist&&data.solved.kind==='LINEAR'&&preset.id==='ineq-quadratic')info.push('a=0，已按一次不等式处理');
   }
   if(isSingle)info.push('探针 x='+fmt(p.probe)+(M.contains(data.input,p.probe)?' 属于输入区间':' 不属于输入区间'));
   const px=scale.x(p.probe);
   svg(rootSvg,'line',{x1:px,x2:px,y1:94,y2:385,class:'lab-probe-line','pointer-events':'none'});
   svg(rootSvg,'text',{x:px,y:407,'text-anchor':'middle',class:'lab-num-caption'},'探针 '+fmt(p.probe));
   svg(rootSvg,'text',{x:35,y:443,class:'lab-scene-label'},'输入端点可拖动；解集来自数学内核，根与刻度使用约 6 位有效数字显示，不构成推导证明。');
   rootSvg.onpointerdown=e=>{
     const key=e.target.closest?.('[data-handle]')?.getAttribute('data-handle');
     if(!key)return;scene.drag={key,scale};rootSvg.setPointerCapture(e.pointerId);e.preventDefault();
   };
   rootSvg.onpointermove=e=>{
     if(!scene.drag)return;e.preventDefault();const matrix=rootSvg.getScreenCTM();if(!matrix)return;
     const pt=rootSvg.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;
     const local=pt.matrixTransform(matrix.inverse());scene.onParams({[scene.drag.key]:scene.drag.scale.world(local.x)});
   };
   rootSvg.onpointerup=rootSvg.onpointercancel=()=>{scene.drag=null};
   const rel=['<',String.raw`\leq`,'>',String.raw`\geq`][p.relation];
   const latex=preset.id==='interval-operations'?[String.raw`A\cap B`,String.raw`A\cup B`,String.raw`A\setminus B`,String.raw`\mathbb R\setminus A`][p.op]:
     preset.id==='interval-single'?preset.latex:
     preset.id==='ineq-linear'?String.raw`ax+b\;`+rel+'0':
     preset.id==='ineq-quadratic'?String.raw`ax^2+bx+c\;`+rel+'0':String.raw`|x-h|\;`+rel+'r';
   return {info,latex,kind:'number_line',coordinateHint:'区间补集相对于整条 ℝ；输入逆序端点时为空，不擅自交换左右。',
     toWorld:(x,y)=>[scale.world(x),0],pointerLabel:x=>'当前数轴位置 x ≈ '+fmt(x)+(scene.assist&&data.solution!==null?(M.contains(data.solution,x)?'；属于结果':'；不属于结果'):'')};
 }
 root.MentorNumberLine={supports:id=>IDS.has(id),draw};
})(window);
