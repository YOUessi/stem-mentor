/* v0.10 complex plane and membership-based Venn diagram. No external service. */
(function(root){
 'use strict';
 const NS='http://www.w3.org/2000/svg',M=root.MentorFoundationsMath;
 const IDS=new Set(['complex-point','complex-operations','complex-rotation','sets-operations','sets-complement']);
 const OPERATIONS=['add','subtract','multiply','divide'];
 const SETOPS=['union','intersection','difference','symmetric','complementA','complementUnion','complementIntersection'];
 const SETLABELS=['A ∪ B','A ∩ B','A ∖ B','A △ B','Cᵤ A','Cᵤ(A ∪ B)','Cᵤ(A ∩ B)'];
 const fmt=x=>Number.isFinite(x)?String(Number(x.toPrecision(6))):'未定义';
 const pair=z=>fmt(z[0])+(z[1]<0?' − ':' + ')+fmt(Math.abs(z[1]))+'i';
 const members=xs=>xs.length?'{'+xs.join(', ')+'}':'∅';
 function svg(parent,tag,attributes={},label){
   const n=document.createElementNS(NS,tag);
   Object.entries(attributes).forEach(([k,v])=>n.setAttribute(k,String(v)));
   if(label!==undefined)n.textContent=String(label);parent.appendChild(n);return n;
 }
 function dom(parent,tag,cls,label){
   const n=document.createElement(tag);if(cls)n.className=cls;
   if(label!==undefined)n.textContent=String(label);parent.appendChild(n);return n;
 }
 function niceStep(x){const base=10**Math.floor(Math.log10(x));return [1,2,5,10].find(k=>k*base>=x)*base;}
 function chart(rootSvg,points,zoom){
   const maxX=Math.max(3,...points.map(p=>Math.abs(p[0]))),maxY=Math.max(3,...points.map(p=>Math.abs(p[1])));
   const scale=Math.min(43*zoom,290/maxX,160/maxY),cx=380,cy=237;
   const C={scale,xy:p=>[cx+p[0]*scale,cy-p[1]*scale],world:(x,y)=>[(x-cx)/scale,(cy-y)/scale]};
   const tick=niceStep(52/scale);
   for(let k=-7;k<=7;k++){
     const val=k*tick,[x,y]=C.xy([val,val]);
     if(x>=28&&x<=728){svg(rootSvg,'line',{x1:x,y1:48,x2:x,y2:417,class:'lab-grid-line'});if(k)svg(rootSvg,'text',{x:x+3,y:253,class:'lab-tick-label'},fmt(val));}
     if(y>=55&&y<=410){svg(rootSvg,'line',{x1:30,y1:y,x2:730,y2:y,class:'lab-grid-line'});if(k)svg(rootSvg,'text',{x:386,y:y-4,class:'lab-tick-label'},fmt(val));}
   }
   svg(rootSvg,'line',{x1:28,y1:cy,x2:733,y2:cy,class:'lab-axis'});
   svg(rootSvg,'line',{x1:cx,y1:45,x2:cx,y2:418,class:'lab-axis'});
   svg(rootSvg,'text',{x:694,y:228,class:'lab-axis-label'},'Re 实轴');
   svg(rootSvg,'text',{x:392,y:45,class:'lab-axis-label'},'Im 虚轴');
   svg(rootSvg,'text',{x:365,y:254,class:'lab-tick-label'},'O');
   svg(rootSvg,'text',{x:30,y:443,class:'lab-scene-label'},'坐标等比例；当前每格 '+fmt(tick)+' 单位，必要时自动适配结果范围。');
   return C;
 }
 function arrow(parent,C,z,cls){
   const [x,y]=C.xy(z),[ox,oy]=C.xy([0,0]);
   svg(parent,'line',{x1:ox,y1:oy,x2:x,y2:y,class:cls,'pointer-events':'none'});
   const len=Math.hypot(x-ox,y-oy);if(len<10)return;
   const ux=(x-ox)/len,uy=(y-oy)/len;
   svg(parent,'polygon',{points:[[x,y],[x-ux*11-uy*4,y-uy*11+ux*4],[x-ux*11+uy*4,y-uy*11-ux*4]].map(v=>v.join(',')).join(' '),class:'lab-complex-arrow','pointer-events':'none'});
 }
 function point(parent,C,z,handle,label){
   const [cx,cy]=C.xy(z);
   const el=svg(parent,'circle',{cx,cy,r:9,class:'lab-complex-handle '+(handle==='w'?'secondary':''),
     'data-handle':handle,tabindex:0,role:'button','aria-label':label+'，方向键调整实部或虚部'});
   svg(parent,'text',{x:cx+12,y:cy-12,class:'lab-axis-label','pointer-events':'none'},label);
   return el;
 }
 function complexDraw(rootSvg,preset,p,view,scene){
   const z=[p.re,p.im],w=[p.wr,p.wi],kind=preset.id,zi=M.complexInfo(z);
   let computation=null;
   if(kind==='complex-point')computation={status:'OK',result:zi.conjugate};
   if(kind==='complex-operations')computation=M.complexOp(z,w,OPERATIONS[p.op]);
   if(kind==='complex-rotation')computation=M.rotateComplex(z,p.theta,p.rho);
   const points=[z];if(kind==='complex-operations')points.push(w);
   if(scene.assist&&computation?.result)points.push(computation.result);
   const C=chart(rootSvg,points,view.zoom||1),info=['z = '+pair(z),'|z| ≈ '+fmt(zi.modulus),
     zi.argument===null?'零复数：辐角未定义':'主辐角 ≈ '+fmt(zi.argument)+' 弧度'];
   arrow(rootSvg,C,z,'lab-complex-vector');
   if(kind==='complex-operations'){arrow(rootSvg,C,w,'lab-complex-vector secondary');info.push('w = '+pair(w));}
   if(kind==='complex-rotation')info.push('旋转 '+fmt(p.theta)+'°；比例 '+fmt(p.rho));
   if(scene.assist&&computation?.status==='OK'){
     const result=computation.result,[cx,cy]=C.xy(result);
     arrow(rootSvg,C,result,'lab-complex-vector result');
     svg(rootSvg,'circle',{cx,cy,r:7,class:'lab-complex-result','data-value':result.map(v=>Math.abs(v)<1e-12?0:v).join(','),'pointer-events':'none'});
     svg(rootSvg,'text',{x:cx+10,y:cy+22,class:'lab-axis-label','pointer-events':'none'},kind==='complex-point'?'共轭 z̄':'结果 R');
     info.push((kind==='complex-point'?'共轭 z̄ = ':'运算结果 = ')+pair(result));
   }else if(scene.assist&&computation?.reason==='ZERO_DIVISOR')info.push('除数为零：复数除法未定义');
   else if(scene.assist&&computation?.status!=='OK')info.push('参数不合法或超出支持的数值范围');
   else info.push('结果未展示：先预测，再主动勾选核对');
   const handles=[['z',z,'z']];if(kind==='complex-operations')handles.push(['w',w,'w']);
   handles.forEach(([name,val,label])=>{
     const el=point(rootSvg,C,val,name,label);
     el.addEventListener('keydown',e=>{
       const axes={ArrowRight:[.1,0],ArrowLeft:[-.1,0],ArrowUp:[0,.1],ArrowDown:[0,-.1]};
       if(!axes[e.key])return;e.preventDefault();
       const [dx,dy]=axes[e.key],keyX=name==='z'?'re':'wr',keyY=name==='z'?'im':'wi';
       scene.onParams({[keyX]:p[keyX]+dx,[keyY]:p[keyY]+dy});
     });
   });
   rootSvg.onpointerdown=e=>{
     const name=e.target.closest?.('[data-handle]')?.getAttribute('data-handle');
     if(name!=='z'&&name!=='w')return;
     scene.drag={name,C};rootSvg.setPointerCapture(e.pointerId);e.preventDefault();
   };
   rootSvg.onpointermove=e=>{
     if(!scene.drag)return;e.preventDefault();const matrix=rootSvg.getScreenCTM();if(!matrix)return;
     const pt=rootSvg.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;
     const loc=pt.matrixTransform(matrix.inverse()),v=scene.drag.C.world(loc.x,loc.y);
     const keys=scene.drag.name==='z'?['re','im']:['wr','wi'];scene.onParams({[keys[0]]:v[0],[keys[1]]:v[1]});
   };
   rootSvg.onpointerup=rootSvg.onpointercancel=()=>{scene.drag=null};
   svg(rootSvg,'text',{x:30,y:25,class:'lab-scene-label'},'拖动复数点，或聚焦后连续使用方向键；数值为近似，不构成数学证明。');
   const latex=kind==='complex-operations'?[String.raw`z+w`,String.raw`z-w`,String.raw`z\cdot w`,String.raw`\frac{z}{w}`][p.op]+String.raw`,\quad z,w\in\mathbb C`:preset.latex;
   return {info,latex,kind:'complex_plane',toWorld:C.world,pointerLabel:(x,y)=>'复平面坐标 Re ≈ '+fmt(x)+'，Im ≈ '+fmt(y),coordinateHint:'复平面两轴等比例；输入点可拖动，结果默认不展示。'};
 }
 function updateMembers(scene,n){
   if(!scene.members)scene.members={A:[1,2,3,5].filter(v=>v<=n),B:[2,4,5,6].filter(v=>v<=n),n};
   if(scene.members.n!==n){
     const gone=[...new Set(scene.members.A.concat(scene.members.B).filter(v=>v>n))];
     scene.members.A=scene.members.A.filter(v=>v<=n);scene.members.B=scene.members.B.filter(v=>v<=n);
     scene.members.n=n;scene.notice=gone.length?'全集变更，已移除越界成员：'+gone.join(', '):'全集已更新；新元素尚未自动加入 A 或 B。';
   }
 }
 function vennDiagram(rootSvg,result,operation,show){
   const defs=svg(rootSvg,'defs');
   for(const [name,cx] of [['a',300],['b',460]]){
     const clip=svg(defs,'clipPath',{id:'v010-clip-'+name});svg(clip,'circle',{cx,cy:232,r:136});
     const mask=svg(defs,'mask',{id:'v010-not-'+name,maskUnits:'userSpaceOnUse',x:20,y:40,width:720,height:380});
     svg(mask,'rect',{x:20,y:40,width:720,height:380,fill:'white'});svg(mask,'circle',{cx,cy:232,r:136,fill:'black'});
   }
   const outside=svg(defs,'mask',{id:'v010-outside',maskUnits:'userSpaceOnUse',x:20,y:40,width:720,height:380});
   svg(outside,'rect',{x:20,y:40,width:720,height:380,fill:'white'});
   [300,460].forEach(cx=>svg(outside,'circle',{cx,cy:232,r:136,fill:'black'}));
   svg(rootSvg,'rect',{x:30,y:48,width:700,height:371,rx:13,class:'lab-venn-universe'});
   const selected=(a,b)=>show&&M.finiteSets([1],a?[1]:[],b?[1]:[],operation).result.length===1;
   const region=(name,attrs,a,b)=>({...attrs,class:'lab-venn-region'+(selected(a,b)?' highlighted':''),'data-region':name});
   svg(rootSvg,'rect',region('neither',{x:30,y:48,width:700,height:371,mask:'url(#v010-outside)'},false,false));
   svg(rootSvg,'circle',region('aOnly',{cx:300,cy:232,r:136,mask:'url(#v010-not-b)'},true,false));
   svg(rootSvg,'circle',region('bOnly',{cx:460,cy:232,r:136,mask:'url(#v010-not-a)'},false,true));
   svg(rootSvg,'circle',region('both',{cx:300,cy:232,r:136,'clip-path':'url(#v010-clip-b)'},true,true));
   [300,460].forEach(cx=>svg(rootSvg,'circle',{cx,cy:232,r:136,class:'lab-venn-outline'}));
   svg(rootSvg,'text',{x:50,y:77,class:'lab-axis-label'},'U = '+members(result.U));
   svg(rootSvg,'text',{x:220,y:121,class:'lab-axis-label'},'A');svg(rootSvg,'text',{x:542,y:121,class:'lab-axis-label'},'B');
   for(const [area,values] of Object.entries(result.regions)){
     values.forEach((value,i)=>{
       let x,y;
       if(area==='both'){x=365+(i%2)*30;y=180+Math.floor(i/2)*22;}
       else if(area==='neither'){x=115+i*44;y=397;}
       else{x=(area==='aOnly'?205:495)+(i%3)*32;y=182+Math.floor(i/3)*28;}
       const g=svg(rootSvg,'g',{'data-member-region':area,'data-element':value});
       svg(g,'circle',{cx:x,cy:y,r:12,class:'lab-venn-member'+(show&&result.result.includes(value)?' selected':'')});
       svg(g,'text',{x,y:y+4,'text-anchor':'middle',class:'lab-venn-member-label'},value);
     });
   }
   svg(rootSvg,'text',{x:30,y:443,class:'lab-scene-label'},'韦恩图按成员归属分区；圆面积和重叠大小不代表基数，也不证明一般定理。');
 }
 function setDraw(rootSvg,preset,p,view,scene){
   const n=Math.round(p.n);updateMembers(scene,n);
   const U=Array.from({length:n},(_,i)=>i+1),operation=SETOPS[p.op];
   const result=M.finiteSets(U,scene.members.A,scene.members.B,operation);
   vennDiagram(rootSvg,result,operation,scene.assist);
   const mobile=document.getElementById('labAlternativeView');mobile.hidden=false;mobile.replaceChildren();
   for(const [key,title] of [['aOnly','只在 A'],['both','同时在 A、B'],['bOnly','只在 B'],['neither','两集合之外（仍在 U 内）']]){
     const card=dom(mobile,'div','lab-set-region-card');dom(card,'strong','',title);dom(card,'span','',members(result.regions[key]));
   }
   const container=scene.extraControls;container.hidden=false;container.replaceChildren();
   dom(container,'strong','lab-set-editor-title','编辑集合成员（只修改本次探究，不记录学习成绩）');
   if(scene.notice)dom(container,'p','lab-set-notice',scene.notice);
   const table=dom(container,'table','lab-set-table');table.id='labSetEditor';
   const row=dom(dom(table,'thead'),'tr');['元素','属于 A','属于 B'].forEach(v=>dom(row,'th','',v));
   const tbody=dom(table,'tbody');
   U.forEach(member=>{
     const tr=dom(tbody,'tr');dom(tr,'th','',member);
     ['A','B'].forEach(set=>{
       const cell=dom(tr,'td'),box=dom(cell,'input');box.type='checkbox';
       box.id='lab-member-'+set+'-'+member;box.dataset.set=set;box.dataset.member=String(member);
       box.checked=scene.members[set].includes(member);box.setAttribute('aria-label','元素 '+member+' 属于集合 '+set);
       box.onchange=()=>{
         scene.members[set]=box.checked?[...new Set(scene.members[set].concat(member))]:scene.members[set].filter(v=>v!==member);
         scene.onSceneChange();
       };
     });
   });
   const output=dom(container,'div','lab-set-result');output.id='labSetResult';output.hidden=!scene.assist;
   if(scene.assist){
     output.dataset.values=result.result.join(',');
     dom(output,'strong','',SETLABELS[p.op]+' = '+members(result.result));
     dom(output,'p','',result.alternate?'德摩根核对：两种成员判断得到 '+members(result.alternate)+'，此为当前有限集合验证。':'结果来自逐个成员判断，不由圆的几何形状决定。');
   }
   const info=['A = '+members(result.A),'B = '+members(result.B),'全集有 '+n+' 个元素',
     result.subsetAinB?'A ⊆ B（按当前成员）':'A 不是 B 的子集'];
   if(!scene.assist)info.push('请先预测运算结果，再勾选显示核对');
   const latex=[String.raw`A\cup B`,String.raw`A\cap B`,String.raw`A\setminus B`,String.raw`A\triangle B`,String.raw`C_U A`,String.raw`C_U(A\cup B)`,String.raw`C_U(A\cap B)`][p.op];
   return {info,latex,kind:'venn_logic',coordinateHint:'在右侧成员表勾选 A/B 归属；调整全集后，越界成员会被移除。'};
 }
 function draw(rootSvg,preset,p,view,scene){
   rootSvg.replaceChildren();rootSvg.setAttribute('viewBox','0 0 760 460');
   return preset.tool==='venn_logic'?setDraw(rootSvg,preset,p,view,scene):complexDraw(rootSvg,preset,p,view,scene);
 }
 root.MentorFoundations2D={supports:id=>IDS.has(id),draw};
})(window);
