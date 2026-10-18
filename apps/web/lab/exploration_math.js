/* Pure offline mathematics shared by renderers and Node truth tests.
 * No DOM, generated answers, model calls, user-code evaluation, or hidden grading.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.MentorExplorationMath=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const EPS=1e-10;
  const finite=Number.isFinite;
  const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
  const add=(a,b)=>a.map((x,i)=>x+b[i]);
  const sub=(a,b)=>a.map((x,i)=>x-b[i]);
  const mul=(a,k)=>a.map(x=>x*k);
  const norm=a=>Math.hypot(...a);
  const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
  const valid=(a,n)=>Array.isArray(a)&&a.length===n&&a.every(finite);
  const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
  function vectorMetrics(a,b,k=1){
    if(!valid(a,2)||!valid(b,2)||!finite(k))return {status:'INVALID'};
    const A=norm(a),B=norm(b),D=dot(a,b),projection=B>EPS?mul(b,D/(B*B)):null;
    return {status:'OK',sum:add(a,b),difference:sub(a,b),scaled:mul(a,k),dot:D,
      lengthA:A,lengthB:B,angleDegrees:A>EPS&&B>EPS?Math.acos(clamp(D/(A*B),-1,1))*180/Math.PI:null,
      projection,projectionScalar:B>EPS?D/B:null,residual:projection?sub(a,projection):null};
  }
  function unitCircle(degrees){
    if(!finite(degrees))return {status:'INVALID'};
    const angle=((degrees%360)+360)%360,r=angle*Math.PI/180;
    const snap=x=>Math.abs(x)<EPS?0:Math.abs(x-1)<EPS?1:Math.abs(x+1)<EPS?-1:x;
    const c=snap(Math.cos(r)),s=snap(Math.sin(r));
    return {status:'OK',point:[c,s],cos:c,sin:s,tan:Math.abs(c)>EPS?s/c:null,
      radians:degrees*Math.PI/180,normalizedDegrees:angle,
      quadrant:c===0||s===0?null:Math.floor(angle/90)+1,
      axis:c===1?'X_POS':c===-1?'X_NEG':s===1?'Y_POS':s===-1?'Y_NEG':null};
  }
  function functionValue(kind,x){
    if(!finite(x))return null;
    switch(kind){
      case 'quadratic':return x*x;
      case 'cubic':return x*x*x-3*x;
      case 'log':return x>0?Math.log(x):null;
      case 'abs':return Math.abs(x);
      default:return null;
    }
  }
  function derivativeInfo(kind,x,h){
    if(!['quadratic','cubic','log','abs'].includes(kind)||!finite(x)||!finite(h))return {status:'INVALID'};
    const raw=functionValue(kind,x),next=functionValue(kind,x+h);
    const y=finite(raw)?raw:null,nextY=finite(next)?next:null;
    const domainValid=y!==null,differentiable=domainValid&&!(kind==='abs'&&x===0);
    const slope=!differentiable?null:kind==='quadratic'?2*x:kind==='cubic'?3*x*x-3:kind==='log'?1/x:Math.sign(x);
    let secantSlope=null;
    if(domainValid&&nextY!==null&&h!==0){
      if(kind==='quadratic')secantSlope=2*x+h;
      else if(kind==='cubic')secantSlope=3*x*x+3*x*h+h*h-3;
      else if(kind==='log')secantSlope=Math.log1p(h/x)/h;
      else secantSlope=x>=0&&x+h>=0?1:x<=0&&x+h<=0?-1:(nextY-y)/h;
    }
    if(!finite(secantSlope))secantSlope=null;
    return {status:'OK',x,h,y,nextX:x+h,nextY,domainValid,differentiable,
      tangentSlope:finite(slope)?slope:null,secantValid:secantSlope!==null,secantSlope,
      reason:!domainValid?'OUTSIDE_REAL_DOMAIN':!differentiable?'CORNER_NOT_DIFFERENTIABLE':h===0?'ZERO_INCREMENT_NO_SECANT':nextY===null?'SECOND_POINT_OUTSIDE_DOMAIN':'DEFINED'};
  }
  function boxGeometry(w,d,H){
    if(![w,d,H].every(x=>finite(x)&&x>0))throw new RangeError('Positive solid dimensions required');
    const base=[[-w/2,-d/2,0],[w/2,-d/2,0],[w/2,d/2,0],[-w/2,d/2,0]];
    const vertices=base.concat(base.map(p=>[p[0],p[1],H]));
    const edges=[];for(let i=0;i<4;i++)edges.push([i,(i+1)%4],[i+4,((i+1)%4)+4],[i,i+4]);
    return {vertices,edges};
  }
  function pyramidGeometry(w,d,H){
    const b=boxGeometry(w,d,H);const vertices=b.vertices.slice(0,4).concat([[0,0,H]]);
    const edges=[];for(let i=0;i<4;i++)edges.push([i,(i+1)%4],[i,4]);
    return {vertices,edges};
  }
  function plane(normal,offset){
    if(!valid(normal,3)||!finite(offset)||norm(normal)<EPS)return null;
    const L=norm(normal),n=mul(normal,1/L),d=offset/L;
    const helper=Math.abs(n[0])<.8?[1,0,0]:[0,1,0];
    const u0=cross(n,helper),u=mul(u0,1/norm(u0)),v=cross(n,u);
    return {normal:n,offset:d,u,v};
  }
  function empty(status,extra={}){return {status,points:[],area:0,perimeter:0,length:0,...extra};}
  function slicePolyhedron(vertices,edges,normal,offset){
    const pl=plane(normal,offset);
    if(!pl||!Array.isArray(vertices)||!vertices.length||!vertices.every(p=>valid(p,3))||!Array.isArray(edges))return empty('INVALID');
    const {normal:n,offset:d,u,v}=pl;
    const scale=Math.max(1,...vertices.map(norm)),tol=1e-9*scale,points=[];
    function insert(p){if(!points.some(q=>norm(sub(p,q))<=tol*4))points.push(p)}
    const signed=vertices.map(p=>dot(n,p)-d);
    for(const e of edges){
      if(!Array.isArray(e)||e.length!==2||!e.every(i=>Number.isInteger(i)&&i>=0&&i<vertices.length))return empty('INVALID');
      const [i,j]=e,a=vertices[i],b=vertices[j],sa=signed[i],sb=signed[j];
      if(Math.abs(sa)<=tol)insert(a.slice());
      if(Math.abs(sb)<=tol)insert(b.slice());
      if((sa<-tol&&sb>tol)||(sa>tol&&sb<-tol)){
        const t=sa/(sa-sb);insert(add(a,mul(sub(b,a),t)));
      }
    }
    const meta={normal:n,offset:d};
    if(!points.length)return empty('EMPTY',meta);
    if(points.length===1)return empty('POINT',{...meta,points});
    if(points.length===2)return empty('SEGMENT',{...meta,points,length:norm(sub(points[1],points[0]))});
    const center=mul(points.reduce((a,p)=>add(a,p),[0,0,0]),1/points.length);
    points.sort((a,b)=>{
      const A=sub(a,center),B=sub(b,center);
      return Math.atan2(dot(A,v),dot(A,u))-Math.atan2(dot(B,v),dot(B,u));
    });
    let area=0,perimeter=0;
    for(let i=0;i<points.length;i++){
      const a=points[i],b=points[(i+1)%points.length];
      area+=dot(cross(sub(a,center),sub(b,center)),n)/2;
      perimeter+=norm(sub(b,a));
    }
    area=Math.abs(area);
    if(area<=tol*tol){
      let pair=[points[0],points[1]],longest=0;
      for(const a of points)for(const b of points){const L=norm(sub(a,b));if(L>longest){pair=[a,b];longest=L}}
      return empty('SEGMENT',{...meta,points:pair,length:longest});
    }
    return {status:'POLYGON',points,area,perimeter,center,...meta};
  }
  function sliceSphere(radius,normal,offset){
    const pl=plane(normal,offset);
    if(!pl||!finite(radius)||radius<=0)return empty('INVALID');
    const {normal:n,offset:d,u,v}=pl,center=mul(n,d),distance=Math.abs(d),tol=1e-9*Math.max(1,radius);
    if(distance>radius+tol)return empty('EMPTY',{normal:n,offset:d});
    if(Math.abs(distance-radius)<=tol)return empty('POINT',{points:[center],center,radius:0,normal:n,offset:d});
    const r=Math.sqrt(Math.max(0,radius*radius-d*d));
    const points=Array.from({length:96},(_,i)=>{
      const t=2*Math.PI*i/96;
      return add(center,add(mul(u,r*Math.cos(t)),mul(v,r*Math.sin(t))));
    });
    return {status:'CIRCLE',points,center,radius:r,area:Math.PI*r*r,perimeter:2*Math.PI*r,normal:n,offset:d};
  }
  return {vectorMetrics,unitCircle,functionValue,derivativeInfo,boxGeometry,pyramidGeometry,
    slicePolyhedron,sliceSphere,plane,add,sub,dot,mul,cross,norm};
});
