"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const ink=require("../../apps/web/ipad/ink_core.js");

test("new document starts with exactly one blank page and supports page separation",()=>{
  const d=ink.newDocument("synthetic-student","session-alpha");
  assert.equal(d.version,1);assert.equal(d.pages.length,1);
  assert.equal(d.pages[0].strokes.length,0);
  let next=ink.addPage(d,"page-two");
  assert.equal(next.pages.length,2);
  assert.equal(next.activePageId,"page-two");
  assert.deepEqual(next.pages[0].strokes,[]);
});
test("screen/world camera preserves point during anchored zoom",()=>{
  let v={zoom:1.3,panX:70,panY:-25};
  const world=ink.toWorld(240,135,v);
  assert.deepEqual(ink.toScreen(world.x,world.y,v),{x:240,y:135});
  const zoomed=ink.zoomAt(v,2.2,{x:240,y:135});
  assert.deepEqual(ink.toScreen(world.x,world.y,zoomed),{x:240,y:135});
  assert.ok(zoomed.zoom<=3.5);
});
test("pressure samples constrained and original pen coordinates preserved",()=>{
 const s=ink.createStroke("s1", "pen", "#2b6242", 3,
  [{x:10,y:10,p:0.2},{x:20,y:12,p:2},{x:30,y:14,p:-1}]);
 assert.deepEqual(s.points.map(x=>x.p),[.2,1,.1]);
 assert.equal(s.points.length,3);
 assert.equal(s.points[0].x,10);
 assert.throws(()=>ink.createStroke("bad", "pen", "red",3,[{x:NaN,y:0,p:.5}]));
});
test("eraser removes intersected strokes but keeps other strokes",()=>{
 let d=ink.newDocument("synthetic-student","session-alpha");
 d=ink.appendStroke(d,ink.createStroke("a","pen","#245b40",3,[{x:0,y:0,p:.5},{x:100,y:0,p:.5}]));
 d=ink.appendStroke(d,ink.createStroke("b","pen","#245b40",3,[{x:0,y:40,p:.5},{x:100,y:40,p:.5}]));
 const next=ink.eraseNear(d,40,4,12);
 assert.deepEqual(next.pages[0].strokes.map(x=>x.id),["b"]);
 assert.deepEqual(d.pages[0].strokes.map(x=>x.id),["a","b"]);
});
test("lasso selects ink by geometry not by stroke number",()=>{
 let d=ink.newDocument("student","sess");
 d=ink.appendStroke(d,ink.createStroke("a","pen","#245b40",3,[{x:20,y:20,p:1},{x:40,y:30,p:1}]));
 d=ink.appendStroke(d,ink.createStroke("b","pen","#245b40",3,[{x:120,y:100,p:1}]));
 const ids=ink.selectLasso(d,[{x:0,y:0},{x:65,y:0},{x:65,y:65},{x:0,y:65}]);
 assert.deepEqual(ids,["a"]);
 const moved=ink.moveStrokes(d,ids,10,-2);
 assert.equal(moved.pages[0].strokes[0].points[0].x,30);
 assert.equal(d.pages[0].strokes[0].points[0].x,20);
});
test("immutable undo/redo, redo discarded after new ink and no-op not committed",()=>{
 const h=ink.history(ink.newDocument("s","t"));
 const a=ink.createStroke("a","pen","#2b6242",3,[{x:1,y:1,p:1}]);
 const b=ink.createStroke("b","pen","#2b6242",3,[{x:2,y:2,p:1}]);
 assert.equal(h.apply(d=>ink.appendStroke(d,a)),true);
 assert.equal(h.apply(d=>ink.appendStroke(d,b)),true);
 assert.equal(h.current().pages[0].strokes.length,2);
 assert.equal(h.undo(),true);assert.equal(h.current().pages[0].strokes.length,1);
 assert.equal(h.redo(),true);assert.equal(h.current().pages[0].strokes.length,2);
 assert.equal(h.undo(),true);
 h.apply(d=>ink.appendStroke(d,b));
 assert.equal(h.redo(),false);
 assert.equal(h.apply(d=>d),false);
});
test("validates schema and prevents cross-student/session document loading",()=>{
 const d=ink.newDocument("student-a","session-a");
 assert.equal(ink.validateDocument(d,"student-a","session-a").pages.length,1);
 assert.throws(()=>ink.validateDocument(d,"student-b","session-a"),/身份|归属/);
 assert.throws(()=>ink.validateDocument(d,"student-a","session-b"),/身份|归属/);
 const bad=JSON.parse(JSON.stringify(d));
 bad.pages[0].strokes.push({id:"x",points:[{x:Infinity,y:0,p:.1}]});
 assert.throws(()=>ink.validateDocument(bad,"student-a","session-a"));
});
test("drawing is limited per session and cannot grow without bound",()=>{
 const large=Array.from({length:ink.MAX_POINTS_PER_STROKE+1},(_,i)=>({x:i,y:0,p:.4}));
 assert.throws(()=>ink.createStroke("over","pen","#255d41",3,large),/上限|太多/);
});
