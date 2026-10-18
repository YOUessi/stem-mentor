/* Actual plane/solid intersections from the tested mathematical kernel. */
(function(root){
 'use strict';
 const M=root.MentorExplorationMath,NS='http://www.w3.org/2000/svg';
 const ids=new Set(['3d-section-prism','3d-section-pyramid','3d-section-sphere']);
 const fmt=n=>Number.isFinite(n)?(Math.abs(n)<1e-12?0:n).toFixed(3):'未定义';
 function node(svg,tag,attrs,text){const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs||{}))e.setAttribute(k,String(v));if(text!==undefined)e.textContent=String(text);svg.appendChild(e);return e}
 function draw(svg,P,preset,p,assist=false){
   const H=root.MentorLab3D.drawing,project=P.project,n=[p.nx,p.ny,p.nz],d=p.t,isSphere=preset.id==='3d-section-sphere';
   const shape=isSphere?'3d-sphere':preset.id==='3d-section-prism'?'3d-prism':'3d-pyramid';
   H.drawSolid(svg,P,{id:shape},{w:4,d:4,h:4,r:p.r});
   let cut;
   if(isSphere)cut=M.sliceSphere(p.r,n,d);
   else{const solid=shape==='3d-prism'?M.boxGeometry(4,4,4):M.pyramidGeometry(4,4,4);cut=M.slicePolyhedron(solid.vertices,solid.edges,n,d)}
   const plane=M.plane(n,d);
   if(!plane)return {info:['零法向量不能定义平面；请令至少一个分量非零。'],cut};
   const center=M.mul(plane.normal,plane.offset),span=isSphere?Math.max(2,p.r*1.3):3.8;
   if(assist){
     const corners=[[-1,-1],[1,-1],[1,1],[-1,1]].map(([a,b])=>M.add(center,M.add(M.mul(plane.u,span*a),M.mul(plane.v,span*b))));
     H.shape(svg,project,corners,'lab-cutting-plane');
     H.arrow(svg,project,center,M.add(center,M.mul(plane.normal,1.2)),'lab-3d-normal');
     H.label(svg,project,M.add(center,M.mul(plane.normal,1.2)),'n');
   }
   const info=['切平面：'+fmt(p.nx)+'x + '+fmt(p.ny)+'y + '+fmt(p.nz)+'z = '+fmt(p.t)];
   if(cut.status==='EMPTY')info.push('平面与立体无交；截面积 0');
   else if(cut.status==='POINT'){
     const xy=project(cut.points[0]);node(svg,'circle',{cx:xy[0],cy:xy[1],r:7,class:'lab-section-point'});
     H.label(svg,project,cut.points[0],'单点');
     info.push(isSphere?'相切：交集是一个点，不是一个圆盘':'退化交集：一个点，不是有面积的截面');
   }else if(cut.status==='SEGMENT'){
     H.line(svg,project,cut.points[0],cut.points[1],'lab-section-edge');
     info.push('交集是一条线段，长度 '+fmt(cut.length),'截面积 0');
   }else if(cut.status==='POLYGON'||cut.status==='CIRCLE'){
     H.shape(svg,project,cut.points,'lab-section-polygon');
     H.path(svg,project,cut.points.concat([cut.points[0]]),'lab-section-edge');
     if(cut.status==='POLYGON'){
       const names={3:'三角形',4:'四边形',5:'五边形',6:'六边形'};
       info.push('真实截面：'+(names[cut.points.length]||cut.points.length+'边形'),'顶点数 '+cut.points.length);
       cut.points.forEach((pt,i)=>{const xy=project(pt);node(svg,'circle',{cx:xy[0],cy:xy[1],r:4,class:'lab-section-point'});H.label(svg,project,pt,String.fromCharCode(65+i))});
     }else info.push('真实截面：圆','截面圆半径 '+fmt(cut.radius));
     info.push('截面积 '+fmt(cut.area)+' 平方单位','周长 '+fmt(cut.perimeter));
   }else info.push('参数无效；不绘制伪造截面');
   info.push('旋转只改变投影，不改变交点和面积；数值观察不是证明');
   return {info,cut};
 }
 root.MentorLabSections={supports:id=>ids.has(id),draw};
})(window);
