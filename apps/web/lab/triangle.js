"use strict";
/* Student-controlled triangle exploration; numerically checked constraints. */
(function(root){
  const NS="http://www.w3.org/2000/svg";
  const RAD=Math.PI/180;
  const clip=(v,lo,hi)=>Math.min(hi,Math.max(lo,v));
  const hypot=(a,b)=>Math.hypot(a,b);
  const length=(a,b)=>hypot(a[0]-b[0],a[1]-b[1]);
  function svg(parent,tag,attrs,text){
    const n=document.createElementNS(NS,tag);
    for(const k in attrs||{})n.setAttribute(k,String(attrs[k]));
    if(text!==undefined)n.textContent=String(text);
    parent.appendChild(n);return n;
  }
  function C(){const s=38,ox=380,oy=320;return {
    screen:v=>[ox+v[0]*s,oy-v[1]*s],
    world:v=>[(v[0]-ox)/s,(oy-v[1])/s],
    s,ox,oy
  }}
  function fmt(x){return Number.isFinite(x)?x.toFixed(2):"未定义"}
  function angle(p,q,r){
    const u=[p[0]-q[0],p[1]-q[1]],v=[r[0]-q[0],r[1]-q[1]];
    const denom=hypot(...u)*hypot(...v);
    if(denom<1e-8)return NaN;
    return Math.acos(clip((u[0]*v[0]+u[1]*v[1])/denom,-1,1))/RAD;
  }
  function metrics(A,B,D){
    const a=length(B,D),b=length(A,D),c=length(A,B);
    const area=Math.abs((B[0]-A[0])*(D[1]-A[1])-(B[1]-A[1])*(D[0]-A[0]))/2;
    return {a,b,c,area,alpha:angle(B,A,D),beta:angle(A,B,D),gamma:angle(A,D,B)};
  }
  function ssaCandidates(a,b,Adeg){
    if(!(a>0&&b>0&&Adeg>0&&Adeg<180))return [];
    const A=Adeg*RAD,h=b*Math.sin(A),base=b*Math.cos(A);
    if(a<h-1e-8)return [];
    const rootD=Math.sqrt(Math.max(0,a*a-h*h));
    const lengths=[base+rootD,base-rootD];
    const unique=[];
    for(const c of lengths){
      if(c<=1e-7||unique.some(v=>Math.abs(v-c)<1e-7))continue;
      const B=angle([0,0],[c,0],[b*Math.cos(A),b*Math.sin(A)]);
      const C=180-A-B;
      if(B>0&&C>0&&Number.isFinite(B))unique.push(c);
    }
    return unique.sort((x,y)=>y-x);
  }
  function initialPoints(id){
    if(id==="tri-right")return {A:[-3,-2],B:[3,-2],C:[-3,3]};
    return {A:[-4,-2],B:[4,-2],C:[.1,3]};
  }
  function drawGrid(root,c){
    for(let k=-13;k<=13;k++){
      const [x]=c.screen([k,0]);
      if(x>0&&x<760)svg(root,"line",{class:"lab-grid-line",x1:x,y1:0,x2:x,y2:460});
      const [,y]=c.screen([0,k]);
      if(y>0&&y<460)svg(root,"line",{class:"lab-grid-line",x1:0,y1:y,x2:760,y2:y});
    }
    const [x0,y0]=c.screen([0,0]);
    svg(root,"line",{class:"lab-axis",x1:0,y1:y0,x2:760,y2:y0});
    svg(root,"line",{class:"lab-axis",x1:x0,y1:0,x2:x0,y2:460});
    svg(root,"text",{class:"lab-tick-label",x:x0+6,y:y0+14},"O");
  }
  function polygon(root,c,vertices,cls){
    const pts=vertices.map(v=>c.screen(v).map(n=>n.toFixed(1)).join(",")).join(" ");
    svg(root,"polygon",{points:pts,class:cls||"lab-triangle"});
  }
  function vertices(root,c,points,interactive){
    Object.entries(points).forEach(pair=>{
      const [name,p]=pair,xy=c.screen(p);
      svg(root,"circle",{cx:xy[0],cy:xy[1],r:interactive?12:6,class:interactive?"lab-drag-vertex":"lab-mark",
        "data-vertex":interactive?name:""});
      svg(root,"text",{x:xy[0]+10,y:xy[1]-10,class:"lab-axis-label"},name);
    });
  }
  function draw(root,preset,values,scene){
    root.replaceChildren();
    root.setAttribute("viewBox","0 0 760 460");
    const c=C(),id=preset.id,interactive=id!=="tri-ssa";
    scene.id=id;
    if(!scene.points || scene.initialId!==id){
      scene.initialId=id;
      scene.points=initialPoints(id);
      scene.dragging=null;
    }
    drawGrid(root,c);
    let info=[],footnote="";
    if(id==="tri-ssa"){
      const a=+values.a,b=+values.b,Adeg=+values.A;
      const candidates=ssaCandidates(a,b,Adeg);
      const A=[-4.3,-1.7],ang=Adeg*RAD;
      const D=[A[0]+b*Math.cos(ang),A[1]+b*Math.sin(ang)];
      const visual=[...candidates].reverse();
      visual.forEach((side,i)=>{
        const B=[A[0]+side,A[1]];
        polygon(root,c,[A,B,D],i===0?"lab-triangle":"lab-triangle-alt");
        vertices(root,c,{A,B,C:D},false);
      });
      if(!candidates.length){
        svg(root,"line",{class:"lab-secondary",x1:c.screen(A)[0],y1:c.screen(A)[1],
          x2:c.screen(D)[0],y2:c.screen(D)[1]});
        vertices(root,c,{A,C:D},false);
      }
      const label=candidates.length+" 种符合条件的三角形";
      info=["a="+fmt(a),"b="+fmt(b),"∠A="+fmt(Adeg)+"°",label];
      if(candidates.length)info.push("第三边 AB 可取："+candidates.map(fmt).join(" 或 "));
      footnote="SSA 条件需要核对角度与三边正性；此处动态展示数学可能性，不代替逐步推导。";
      scene.ssaCandidates=candidates;
    }else{
      const pts=scene.points;
      polygon(root,c,[pts.A,pts.B,pts.C]);
      vertices(root,c,pts,true);
      const calc=metrics(pts.A,pts.B,pts.C);
      info=["BC（a）="+fmt(calc.a),"AC（b）="+fmt(calc.b),"AB（c）="+fmt(calc.c),
            "∠A="+fmt(calc.alpha)+"°","∠B="+fmt(calc.beta)+"°","∠C="+fmt(calc.gamma)+"°",
            "面积="+fmt(calc.area)];
      if(calc.area<1e-5)info.push("三点接近共线，不是非退化三角形");
      if(id==="tri-right")info.push("约束：AB ⟂ AC（直角在 A 点）");
      footnote="长度、面积、内角由当前顶点重新计算；坐标网格用于辅助观察。";
    }
    if(footnote)svg(root,"text",{x:22,y:26,class:"lab-scene-label"},footnote);
    root.onpointerdown=e=>{
      if(!interactive)return;
      const target=e.target.closest?.("[data-vertex]");
      if(!target||!target.dataset.vertex)return;
      scene.dragging=target.dataset.vertex;
      root.setPointerCapture(e.pointerId);
      e.preventDefault();
    };
    root.onpointermove=e=>{
      if(!interactive||!scene.dragging)return;
      const matrix=root.getScreenCTM();
      if(!matrix)return;
      const pt=root.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;
      const screen=pt.matrixTransform(matrix.inverse());
      const world=c.world([screen.x,screen.y]);
      const next=[clip(world[0],-9.5,9.5),clip(world[1],-3.5,6.8)];
      const ps=scene.points,key=scene.dragging;
      if(id==="tri-right"){
        if(key==="B")next[1]=ps.A[1];
        if(key==="C")next[0]=ps.A[0];
        if(key==="A"){
          const dx=next[0]-ps.A[0],dy=next[1]-ps.A[1];
          ps.B=[ps.B[0]+dx,ps.B[1]+dy];
          ps.C=[ps.C[0]+dx,ps.C[1]+dy];
        }
      }
      ps[key]=next;
      const output=draw(root,preset,values,scene);
      scene.onUpdate?.(output.info);
    };
    root.onpointerup=()=>{scene.dragging=null};
    root.onpointercancel=()=>{scene.dragging=null};
    return {info,kind:"triangle_2d",scene,meta:footnote};
  }
  root.MentorLabTriangle={draw,ssaCandidates,metrics,initialPoints};
})(window);
