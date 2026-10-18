"use strict";
/* Hand-built offline XYZ spatial coordinate renderer for high-school geometry. */
(function(root){
 const NS="http://www.w3.org/2000/svg",RAD=Math.PI/180;
 const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 const dist=v=>Math.hypot(...v);
 const add=(a,b)=>a.map((x,i)=>x+b[i]);
 const mid=(a,b)=>a.map((x,i)=>(x+b[i])/2);
 const diff=(a,b)=>a.map((x,i)=>x-b[i]);
 const dot=(a,b)=>a.reduce((z,x,i)=>z+x*b[i],0);
 const css=(tag,parent,attrs={},value)=>{
   const n=document.createElementNS(NS,tag);
   Object.entries(attrs).forEach(([key,val])=>n.setAttribute(key,String(val)));
   if(value!==undefined)n.textContent=String(value);
   parent.appendChild(n);return n;
 };
 const fmt=v=>Number.isFinite(v)?v.toFixed(2):"未定义";
 function makeProjection(yaw=38,pitch=36,zoom=1){
   const a=yaw*RAD,b=pitch*RAD,co=Math.cos(a),si=Math.sin(a),
         cp=Math.cos(b),sp=Math.sin(b),scale=39*zoom;
   function project([x,y,z]){
     const u=co*x-si*y,v=si*x+co*y;
     return [380+u*scale,239-(z*cp-v*sp)*scale,v*cp+z*sp];
   }
   return {project,scale,yaw,pitch,zoom};
 }
 function line(svg,project,a,b,cls){
   const p=project(a),q=project(b);
   return css("line",svg,{x1:p[0],y1:p[1],x2:q[0],y2:q[1],class:cls});
 }
 function shape(svg,project,points,cls){
   return css("polygon",svg,{points:points.map(p=>{
     const v=project(p);return v[0].toFixed(2)+","+v[1].toFixed(2);
   }).join(" "),class:cls});
 }
 function path(svg,project,points,cls){
   const d=points.map((v,i)=>{
     const xy=project(v);
     return (i?"L":"M")+xy[0].toFixed(2)+" "+xy[1].toFixed(2);
   }).join(" ");
   css("path",svg,{d,class:cls});
 }
 function label(svg,project,pos,title,cls="lab-3d-label"){
   const xy=project(pos);
   css("text",svg,{x:xy[0]+8,y:xy[1]-7,class:cls},title);
 }
 function axes(svg,P){
   const proj=P.project;
   // XY base grid; projections are dashed references rather than a filled plane.
   for(let i=-5;i<=5;i++){
     line(svg,proj,[i,-5,0],[i,5,0],"lab-3d-grid");
     line(svg,proj,[-5,i,0],[5,i,0],"lab-3d-grid");
   }
   const pairs=[
     {axis:"x",a:[-5.5,0,0],b:[5.5,0,0],cls:"lab-3d-x"},
     {axis:"y",a:[0,-5.5,0],b:[0,5.5,0],cls:"lab-3d-y"},
     {axis:"z",a:[0,0,-5.5],b:[0,0,5.5],cls:"lab-3d-z"}
   ];
   for(const axis of pairs){
     line(svg,proj,axis.a,axis.b,axis.cls);
     label(svg,proj,axis.b,axis.axis);
   }
   label(svg,proj,[0,0,0],"O");
   for(let k=1;k<=4;k++){
     label(svg,proj,[k,0,0],String(k),"lab-3d-tick");
     label(svg,proj,[0,k,0],String(k),"lab-3d-tick");
     label(svg,proj,[0,0,k],String(k),"lab-3d-tick");
   }
 }
 function point(svg,project,v,name,cls){
   const p=project(v);
   css("circle",svg,{cx:p[0],cy:p[1],r:6,class:cls||"lab-3d-dot"});
   if(name)label(svg,project,v,name);
 }
 function arrow(svg,project,a,b,cls){
   line(svg,project,a,b,cls||"lab-3d-vector");
   const pa=project(a),pb=project(b);
   const delta=[pb[0]-pa[0],pb[1]-pa[1]],l=Math.hypot(...delta);
   if(l<1e-5)return;
   const u=[delta[0]/l,delta[1]/l];
   const q=[pb[0]-u[0]*12,pb[1]-u[1]*12],v=[-u[1],u[0]];
   const tip=[pb[0],pb[1]]; // depth is sorting metadata, never an SVG coordinate
   css("polygon",svg,{
     points:[tip,q.map((x,i)=>x+v[i]*4),q.map((x,i)=>x-v[i]*4)]
       .map(p=>p.join(",")).join(" "),
     class:"lab-3d-arrowhead"
   });
 }
 function baseMetrics(preset,params){
   const id=preset.id,p=params;
   if(id==="3d-point")return ["P=("+p.x+","+p.y+","+p.z+")",
     "距离 OP="+fmt(Math.hypot(p.x,p.y,p.z)),
     "投影点 H=("+p.x+","+p.y+",0)"];
   if(id==="3d-vectors"){
     const a=[p.ax,p.ay,p.az],b=[p.bx,p.by,p.bz],n=dot(a,b),
       norm=dist(a)*dist(b),angle=norm>1e-9?Math.acos(clamp(n/norm,-1,1))/RAD:NaN;
     return ["a·b="+fmt(n),"|a|="+fmt(dist(a)),"|b|="+fmt(dist(b)),
       norm>1e-9?"两向量夹角="+fmt(angle)+"°":"存在零向量：夹角未定义"];
   }
   if(id==="3d-plane")return ["平面 z="+p.p+"x+"+p.q+"y+"+p.r,
      "法向量 (-p,-q,1)=("+(-p.p).toFixed(2)+","+(-p.q).toFixed(2)+",1)",
      "法向量长度="+fmt(Math.hypot(p.p,p.q,1))];
   if(id==="3d-prism")return ["底面积="+fmt(p.w*p.d),
     "高="+fmt(p.h),"体积="+fmt(p.w*p.d*p.h)];
   if(id==="3d-pyramid")return ["底面积="+fmt(p.w*p.d),
      "高="+fmt(p.h),"体积="+fmt(p.w*p.d*p.h/3)];
   if(id==="3d-sphere")return ["半径="+fmt(p.r),
      "球体积≈"+fmt(4*Math.PI*Math.pow(p.r,3)/3)];
   if(id==="3d-cylinder")return ["底圆半径="+fmt(p.r),"高度="+fmt(p.h),
      "体积≈"+fmt(Math.PI*p.r*p.r*p.h)];
   if(id==="3d-cone")return ["底圆半径="+fmt(p.r),"高度="+fmt(p.h),
      "体积≈"+fmt(Math.PI*p.r*p.r*p.h/3)];
   return [];
 }
 function circle(r,z,n=90){
   return Array.from({length:n+1},(_,i)=>[r*Math.cos(2*Math.PI*i/n),
                  r*Math.sin(2*Math.PI*i/n),z]);
 }
 function drawSolid(svg,P,preset,p){
   const project=P.project,id=preset.id;
   if(id==="3d-point"){
     const point3=[p.x,p.y,p.z],foot=[p.x,p.y,0];
     line(svg,project,[0,0,0],foot,"lab-3d-helper");
     line(svg,project,foot,point3,"lab-3d-helper");
     point(svg,project,foot,"H");
     arrow(svg,project,[0,0,0],point3,"lab-3d-vector");
     point(svg,project,point3,"P");
   }else if(id==="3d-vectors"){
     const a=[p.ax,p.ay,p.az],b=[p.bx,p.by,p.bz];
     arrow(svg,project,[0,0,0],a,"lab-3d-vector");
     arrow(svg,project,[0,0,0],b,"lab-3d-vector-alt");
     point(svg,project,a,"A");point(svg,project,b,"B");
   }else if(id==="3d-plane"){
     const f=(x,y)=>[x,y,p.p*x+p.q*y+p.r];
     const a=f(-3,-3),b=f(3,-3),c=f(3,3),d=f(-3,3);
     shape(svg,project,[a,b,c,d],"lab-3d-plane");
     for(let k=-2;k<=2;k++){
       line(svg,project,f(k,-3),f(k,3),"lab-3d-plane-grid");
       line(svg,project,f(-3,k),f(3,k),"lab-3d-plane-grid");
     }
     const v=f(0,0);
     arrow(svg,project,v,add(v,[-p.p*1.6,-p.q*1.6,1.6]),"lab-3d-normal");
     point(svg,project,v,"P0");
     label(svg,project,add(v,[-p.p*1.6,-p.q*1.6,1.6]),"n");
   }else if(id==="3d-prism"||id==="3d-pyramid"){
     const w=p.w/2,d=p.d/2,h=p.h,base=[[-w,-d,0],[w,-d,0],[w,d,0],[-w,d,0]];
     const upper=id==="3d-prism"?base.map(v=>[v[0],v[1],h]):[[0,0,h]];
     const faces=id==="3d-prism"?
      [[base[0],base[1],upper[1],upper[0]],[base[1],base[2],upper[2],upper[1]],
       [base[2],base[3],upper[3],upper[2]],[base[3],base[0],upper[0],upper[3]],
       upper,base]:
      [[base[0],base[1],upper[0]],[base[1],base[2],upper[0]],
       [base[2],base[3],upper[0]],[base[3],base[0],upper[0]],base];
     faces.sort((a,b)=>{
       const za=a.reduce((z,v)=>z+project(v)[2],0)/a.length;
       const zb=b.reduce((z,v)=>z+project(v)[2],0)/b.length;return zb-za;
     });
     for(const face of faces)shape(svg,project,face,"lab-3d-solid-face");
     for(let i=0;i<4;i++){
       line(svg,project,base[i],base[(i+1)%4],"lab-3d-edge");
       if(id==="3d-prism"){
         line(svg,project,upper[i],upper[(i+1)%4],"lab-3d-edge");
         line(svg,project,base[i],upper[i],"lab-3d-edge");
       }else line(svg,project,base[i],upper[0],"lab-3d-edge");
     }
     line(svg,project,[0,0,0],[0,0,h],"lab-3d-helper");
     label(svg,project,[0,0,h],"高 h");
   }else if(id==="3d-sphere"){
     const r=p.r;
     const loops=[];
     for(const zFactor of [-.75,-.4,0,.4,.75]){
       const z=r*zFactor,rr=Math.sqrt(Math.max(0,r*r-z*z));
       loops.push(circle(rr,z));
     }
     for(const theta of [0,Math.PI/4,Math.PI/2,3*Math.PI/4]){
       loops.push(Array.from({length:100},(_,i)=>{
         const phi=2*Math.PI*i/99;
         return [r*Math.cos(phi)*Math.cos(theta),r*Math.cos(phi)*Math.sin(theta),
                 r*Math.sin(phi)];
       }));
     }
     loops.forEach(l=>path(svg,project,l,"lab-3d-wire"));
     arrow(svg,project,[0,0,0],[r,0,0],"lab-3d-normal");
     label(svg,project,[r,0,0],"r");
   }else if(id==="3d-cylinder"||id==="3d-cone"){
     path(svg,project,circle(p.r,0),"lab-3d-wire");
     if(id==="3d-cylinder"){
       path(svg,project,circle(p.r,p.h),"lab-3d-wire");
       for(const angle of [0,Math.PI/2,Math.PI,3*Math.PI/2]){
         const x=p.r*Math.cos(angle),y=p.r*Math.sin(angle);
         line(svg,project,[x,y,0],[x,y,p.h],"lab-3d-edge");
       }
     }else{
       for(const angle of [0,Math.PI/2,Math.PI,3*Math.PI/2]){
         line(svg,project,[p.r*Math.cos(angle),p.r*Math.sin(angle),0],[0,0,p.h],"lab-3d-edge");
       }
     }
     line(svg,project,[0,0,0],[0,0,p.h],"lab-3d-helper");
     label(svg,project,[0,0,p.h],"h");
   }
 }
 function draw(root,preset,params,view,scene){
   root.replaceChildren();
   root.setAttribute("viewBox","0 0 760 460");
   const yaw=view?.yaw??38,pitch=view?.pitch??36,zoom=view?.zoom??1;
   const P=makeProjection(yaw,pitch,zoom);
   axes(root,P);
   drawSolid(root,P,preset,params);
   const info=baseMetrics(preset,params);
   if(scene){
     root.style.cursor="grab";
     root.onpointerdown=e=>{
       scene.dragging={id:e.pointerId,x:e.clientX,y:e.clientY,yaw:scene.view.yaw,pitch:scene.view.pitch};
       root.setPointerCapture(e.pointerId);
       root.style.cursor="grabbing";
       e.preventDefault();
     };
     root.onpointermove=e=>{
       const drag=scene.dragging;
       if(!drag||drag.id!==e.pointerId)return;
       scene.view.yaw=clamp(drag.yaw+(e.clientX-drag.x)*.62,-180,180);
       scene.view.pitch=clamp(drag.pitch+(e.clientY-drag.y)*.34,12,78);
       const s=draw(root,preset,params,scene.view,scene);
       scene.onUpdate?.(s.info,s);
     };
     root.onpointerup=root.onpointercancel=()=>{
       scene.dragging=null;root.style.cursor="grab";
     };
   }
   return {info,kind:"space_3d",project:P.project,projection:P};
 }
 root.MentorLab3D={draw,makeProjection,baseMetrics};
})(window);
