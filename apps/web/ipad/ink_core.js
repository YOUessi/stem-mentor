"use strict";
/* Synthetic/local-only vector notebook document engine.
 * There is NO OCR, cloud sync, mathematical proof checking, or account auth.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==="object"&&module.exports)module.exports=api;
  root.MentorInkCore=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
 const VERSION=1,MAX_PAGES=50,MAX_STROKES_PER_PAGE=1800,MAX_POINTS_PER_STROKE=2500;
 const MAX_XY=1000000,MIN_ZOOM=.45,MAX_ZOOM=3.5;
 const finite=x=>typeof x==="number"&&Number.isFinite(x);
 const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
 const clone=x=>JSON.parse(JSON.stringify(x));
 function assertPoint(p){
   if(!p||!finite(p.x)||!finite(p.y)||Math.abs(p.x)>MAX_XY||Math.abs(p.y)>MAX_XY)
     throw new TypeError("无效的笔迹坐标");
   const pressure=finite(p.p)?clamp(p.p,.1,1):.5;
   return {x:p.x,y:p.y,p:pressure};
 }
 function newDocument(studentId,sessionId){
   if(typeof studentId!=="string"||!studentId||typeof sessionId!=="string"||!sessionId)
     throw new Error("笔记必须绑定合成学生与有效学习会话");
   return {version:VERSION,studentId,sessionId,activePageId:"page-1",
     pages:[{id:"page-1",strokes:[]}],updatedAt:new Date().toISOString()};
 }
 function createStroke(id,tool,color,width,points){
   if(typeof id!=="string"||!id||!["pen","highlighter"].includes(tool))
     throw new Error("无效的笔迹ID或绘制工具");
   if(!/^#[0-9a-fA-F]{6}$/.test(color)||!finite(width)||width<.3||width>40)
     throw new Error("笔迹画笔参数无效");
   if(!Array.isArray(points)||points.length<1||points.length>MAX_POINTS_PER_STROKE)
     throw new RangeError("笔迹采样点数超出上限");
   return {id,tool,color,width,points:points.map(assertPoint)};
 }
 function page(d){return d.pages.find(x=>x.id===d.activePageId)}
 function modify(d,fn){
   const next=clone(d);
   fn(next);
   next.updatedAt=new Date().toISOString();
   return next;
 }
 function appendStroke(doc,stroke){
   validateDocument(doc,doc.studentId,doc.sessionId);
   const checked=createStroke(stroke.id,stroke.tool,stroke.color,stroke.width,stroke.points);
   const current=page(doc);
   if(current.strokes.length>=MAX_STROKES_PER_PAGE)throw new RangeError("本页笔画数量已达上限");
   if(current.strokes.some(x=>x.id===stroke.id))throw new Error("重复笔画ID");
   return modify(doc,d=>page(d).strokes.push(checked));
 }
 function addPage(doc,id){
   validateDocument(doc,doc.studentId,doc.sessionId);
   const name=id||"page-"+(doc.pages.length+1);
   if(doc.pages.length>=MAX_PAGES)throw new RangeError("页面数量超过上限");
   if(!name||doc.pages.some(p=>p.id===name))throw new Error("页面ID重复");
   return modify(doc,d=>{d.pages.push({id:name,strokes:[]});d.activePageId=name});
 }
 function setPage(doc,pageId){
   if(!doc.pages.some(p=>p.id===pageId))throw new Error("页面不存在");
   if(doc.activePageId===pageId)return doc;
   return modify(doc,d=>d.activePageId=pageId);
 }
 function translateStroke(s,dx,dy){
   if(!finite(dx)||!finite(dy))throw new Error("无效的移动量");
   return {...s,points:s.points.map(p=>assertPoint({x:p.x+dx,y:p.y+dy,p:p.p}))};
 }
 function pointSegDistSq(p,a,b){
   const dx=b.x-a.x,dy=b.y-a.y,len=dx*dx+dy*dy;
   const t=len?clamp(((p.x-a.x)*dx+(p.y-a.y)*dy)/len,0,1):0;
   const xx=p.x-(a.x+dx*t),yy=p.y-(a.y+dy*t);
   return xx*xx+yy*yy;
 }
 function eraseNear(doc,x,y,radius){
   if(!finite(x)||!finite(y)||!finite(radius)||radius<=0||radius>300)
     throw new Error("无效橡皮参数");
   const center={x,y};
   const strokes=page(doc).strokes;
   const kept=strokes.filter(s=>{
     const r2=(radius+s.width/2)**2;
     if(s.points.length===1)return pointSegDistSq(center,s.points[0],s.points[0])>r2;
     for(let i=1;i<s.points.length;i++)
       if(pointSegDistSq(center,s.points[i-1],s.points[i])<=r2)return false;
     return true;
   });
   if(kept.length===strokes.length)return doc;
   return modify(doc,d=>{page(d).strokes=kept});
 }
 function inside(p,poly){
   let result=false;
   for(let i=0,j=poly.length-1;i<poly.length;j=i++){
     const a=poly[i],b=poly[j];
     if(((a.y>p.y)!==(b.y>p.y)) &&
        (p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x))result=!result;
   }
   return result;
 }
 function selectLasso(doc,polygon){
   if(!Array.isArray(polygon)||polygon.length<3)return [];
   polygon.forEach(assertPoint);
   return page(doc).strokes.filter(s=>s.points.some(p=>inside(p,polygon))).map(s=>s.id);
 }
 function moveStrokes(doc,ids,dx,dy){
   if(!ids?.length||(!dx&&!dy))return doc;
   const members=new Set(ids);
   if(!page(doc).strokes.some(s=>members.has(s.id)))return doc;
   return modify(doc,d=>{page(d).strokes=page(d).strokes.map(s=>
     members.has(s.id)?translateStroke(s,dx,dy):s)});
 }
 function validateDocument(raw,studentId,sessionId){
   if(!raw||raw.version!==VERSION||raw.studentId!==studentId||raw.sessionId!==sessionId)
     throw new Error("笔记身份或会话归属不一致");
   if(!Array.isArray(raw.pages)||!raw.pages.length||raw.pages.length>MAX_PAGES)
     throw new Error("笔记页面数据错误");
   if(!raw.pages.some(p=>p.id===raw.activePageId))
     throw new Error("笔记当前页不存在");
   const pageIds=new Set(),strokeIds=new Set();
   for(const p of raw.pages){
     if(!p||typeof p.id!=="string"||pageIds.has(p.id)||!Array.isArray(p.strokes)
        ||p.strokes.length>MAX_STROKES_PER_PAGE)throw new Error("笔记页面数据无效");
     pageIds.add(p.id);
     for(const s of p.strokes){
       if(strokeIds.has(s.id))throw new Error("笔画编号重复");
       strokeIds.add(s.id);
       createStroke(s.id,s.tool,s.color,s.width,s.points);
     }
   }
   return raw;
 }
 function toWorld(x,y,view){
   const z=view.zoom;
   if(!finite(z)||z<=0)throw new Error("缩放比例无效");
   return {x:(x-view.panX)/z,y:(y-view.panY)/z};
 }
 function toScreen(x,y,view){return {x:x*view.zoom+view.panX,y:y*view.zoom+view.panY}}
 function zoomAt(view,z,pivot){
   const target=clamp(z,MIN_ZOOM,MAX_ZOOM);
   const world=toWorld(pivot.x,pivot.y,view);
   return {zoom:target,panX:pivot.x-world.x*target,panY:pivot.y-world.y*target};
 }
 function history(initial,maxUndo=55){
   let current=clone(initial),past=[],future=[];
   return {
     current:()=>current,
     apply(fn){
       const newDoc=fn(current);
       if(newDoc===current||JSON.stringify(newDoc)===JSON.stringify(current))return false;
       past.push(clone(current));
       if(past.length>maxUndo)past.shift();
       current=clone(newDoc);future=[];return true;
     },
     undo(){
       if(!past.length)return false;
       future.push(clone(current));current=past.pop();return true;
     },
     redo(){
       if(!future.length)return false;
       past.push(clone(current));current=future.pop();return true;
     },
     canUndo:()=>past.length>0,canRedo:()=>future.length>0
   };
 }
 return Object.freeze({VERSION,MAX_STROKES_PER_PAGE,MAX_POINTS_PER_STROKE,MAX_PAGES,
   MIN_ZOOM,MAX_ZOOM,newDocument,createStroke,appendStroke,
   addPage,setPage,eraseNear,selectLasso,moveStrokes,validateDocument,
   toWorld,toScreen,zoomAt,history});
});
