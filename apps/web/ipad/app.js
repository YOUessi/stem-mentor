"use strict";
/* STEM Mentor v0.14A / iPad-first handwriting pilot.
 * Synthetic students only; vector ink is ONLY stored in this browser.
 * No OCR, no model inference, no cloud ink sync or grade writes.
 */
(function(){
  const Core=window.MentorInkCore,Store=window.MentorInkStore;
  const $=id=>document.getElementById(id);
  const state={
    catalog:null,studentId:localStorage.getItem("stem-demo-student"),
    sessionId:localStorage.getItem("stem-demo-session"),
    session:null,store:null,tool:"pen",color:"#2b6544",width:2.5,
    selectedIds:[],selectionPolygon:[],preview:null,
    view:{zoom:1,panX:0,panY:0},fingers:new Map(),gesture:null,
    activePen:null,lastPenTime:0,dirtyRevision:0,
    savedRevision:0,saveQueue:Promise.resolve(),saveTimer:null,
    boardWidth:1,boardHeight:1,penOnly:true,agentOpen:false
  };
  const $home=$("ipadHome"),$study=$("ipadStudy"),$canvas=$("inkCanvas");
  const ctx=$canvas.getContext("2d",{alpha:false});
  const format=x=>Math.round(x*100)/100;
  const uuid=()=>crypto.randomUUID?.()||"stroke-"+Date.now()+"-"+Math.random().toString(16).slice(2);
  const notice=txt=>{
    const el=$("ipadToast");
    el.textContent=txt;el.hidden=false;
    clearTimeout(notice.t);
    notice.t=setTimeout(()=>{el.hidden=true},3300);
  };
  async function request(path,method="GET",body){
    const result=await fetch(path,{method,headers:{"Content-Type":"application/json"},
      body:body===undefined?undefined:JSON.stringify(body)});
    if(!result.ok){
      let err=result.status+" "+result.statusText;
      try{const reply=await result.json();err=reply.detail||err}catch{}
      throw Error(String(err));
    }
    return result.json();
  }
  function setSaveStatus(text,color){
    $("saveStatus").textContent=text;
    $("saveStatus").dataset.state=color||"idle";
  }
  function renderView(){
    const isStudy=location.pathname==="/ipad/study";
    $home.hidden=isStudy;$study.hidden=!isStudy;
    document.body.classList.toggle("in-paper",isStudy);
    if(isStudy)resizePaper();
  }
  async function showHome(){
    await flushSave();
    state.agentOpen=false;
    history.pushState({}, "", "/ipad");
    renderView();
    await updateHome();
  }
  function resetScratchState(){
    state.selectedIds=[];
    state.selectionPolygon=[];
    state.preview=null;
    state.fingers.clear();state.gesture=null;
    state.activePen=null;
    state.view={zoom:1,panX:0,panY:0};
  }
  async function openStudy(sid,{push=true}={}){
    const session=await request("/api/sessions/"+encodeURIComponent(sid));
    if(session.student_id!==state.studentId)
      throw Error("学习会话不属于当前合成学生");
    await flushSave();
    resetScratchState();
    state.session=session;
    state.sessionId=sid;
    localStorage.setItem("stem-demo-session",sid);
    const existing=await Store.load(state.studentId,sid);
    state.store=Core.history(existing||Core.newDocument(state.studentId,sid));
    state.dirtyRevision=0;state.savedRevision=0;
    if(push)history.pushState({}, "", "/ipad/study?session="+encodeURIComponent(sid));
    renderView();
    $("notebookTitle").textContent=session.problem?.title||"手写学习本";
    $("notebookTopic").textContent=
      ({INDEPENDENT:"自主挑战 · 先独立思考",GUIDE:"推理陪练",ANALYZE:"逻辑分析"})[session.mode]||"手写解题";
    $("paperProblemText").textContent=session.problem?.prompt||"请自由记录本题条件与目标";
    $("paperProblem").classList.remove("is-hidden");
    $("agentMode").value=session.mode||"INDEPENDENT";
    $("agentQuestion").value="";
    $("agentStage").value="FORWARD";
    setAgentOpen(false);
    setSaveStatus(existing?"已恢复本机笔迹":"本地新纸");
    pageButtons();renderAgents();paint();updateButtons();
  }
  async function ensureStudent(){
    if(state.studentId){
      try{await request("/api/students/"+encodeURIComponent(state.studentId)+"/dashboard");return}
      catch{localStorage.removeItem("stem-demo-student");state.studentId=null}
    }
    const created=await request("/api/students","POST",{alias:"iPad 演示学生"});
    state.studentId=created.id;
    localStorage.setItem("stem-demo-student",state.studentId);
  }
  function make(tag,cls,textValue){
    const el=document.createElement(tag);
    if(cls)el.className=cls;
    if(textValue!==undefined)el.textContent=String(textValue);
    return el;
  }
  async function updateHome(){
    if(!state.studentId)return;
    const [dashboard,historyData]=await Promise.all([
      request("/api/students/"+encodeURIComponent(state.studentId)+"/dashboard"),
      request("/api/students/"+encodeURIComponent(state.studentId)+"/episodes")
    ]);
    $("statHistory").textContent=dashboard.episodes_count;
    $("statReview").textContent=dashboard.reviews_due_count;
    const root=$("recentSessions");
    root.replaceChildren();
    // Historical episodes are actual records; do not invent mistakes or scores.
    if(!historyData.episodes?.length){
      const empty=make("div","recent-item");
      const text=make("div","recent-body");
      text.appendChild(make("strong",null,"还没有已完成的练习记录"));
      text.appendChild(make("p",null,"从一张新的学习纸开始，慢慢积累自己的思路。"));
      empty.appendChild(make("span","recent-symbol","✎"));
      empty.appendChild(text);root.appendChild(empty);
    }else{
      for(const ep of historyData.episodes.slice(0,6)){
        const row=make("div","recent-item");
        row.appendChild(make("span","recent-symbol","◷"));
        const body=make("div","recent-body");
        body.appendChild(make("strong",null,ep.problem_title||"自定义题目"));
        body.appendChild(make("p",null,"已保存真实练习经历 · 解题正确性未验证"));
        row.appendChild(body);
        // Completed session can still be opened as a local view of its own ink.
        const button=make("button",null,"查看笔记");
        button.type="button";
        button.onclick=()=>openStudy(ep.session_id).catch(e=>notice(e.message));
        row.appendChild(button);root.appendChild(row);
      }
    }
    const current=state.sessionId;
    if(current){
      try{
        const s=await request("/api/sessions/"+encodeURIComponent(current));
        if(s.student_id!==state.studentId)throw Error("属于其他演示学生");
        $("continueWriting").textContent="✎　继续 "+(s.problem?.title||"我的学习");
      }catch{
        state.sessionId=null;localStorage.removeItem("stem-demo-session");
      }
    }
  }
  async function startNewPaper(){
    const pid=$("homeProblem").value;
    if(!pid)throw Error("请先选择一道演示题目");
    const session=await request("/api/sessions","POST",{
      student_id:state.studentId,problem_id:pid,mode:"INDEPENDENT"
    });
    await openStudy(session.id);
  }

  // World coordinates live in ink core, independent of viewport and side panel.
  function screenPoint(event){
    const b=$canvas.getBoundingClientRect();
    return {x:event.clientX-b.left,y:event.clientY-b.top};
  }
  function worldPoint(event){
    const p=screenPoint(event);
    return Core.toWorld(p.x,p.y,state.view);
  }
  function inkSample(event){
    const p=worldPoint(event);
    const pressure=event.pressure>0?event.pressure:.5;
    return {x:format(p.x),y:format(p.y),p:Math.max(.1,Math.min(1,pressure))};
  }
  function renderStroke(s){
    const points=s.points;
    if(!points.length)return;
    ctx.save();
    ctx.strokeStyle=s.color;ctx.fillStyle=s.color;
    ctx.lineJoin="round";ctx.lineCap="round";
    ctx.globalAlpha=s.tool==="highlighter"?.32:1;
    if(points.length===1){
      ctx.beginPath();ctx.arc(points[0].x,points[0].y,
        Math.max(.55,s.width*points[0].p/2),0,Math.PI*2);ctx.fill();
    }else{
      for(let i=1;i<points.length;i++){
        const a=points[i-1],b=points[i];
        ctx.lineWidth=Math.max(.4,s.width*(a.p+b.p)/2);
        ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
      }
    }
    ctx.restore();
  }
  function drawGrid(){
    const w=state.boardWidth,h=state.boardHeight;
    ctx.fillStyle="#fffefa";ctx.fillRect(0,0,w,h);
    const zoom=state.view.zoom,gap=44*zoom;
    if(gap<8)return;
    const xx=((state.view.panX%gap)+gap)%gap;
    const yy=((state.view.panY%gap)+gap)%gap;
    ctx.strokeStyle="rgba(81,140,90,0.10)";ctx.lineWidth=1;
    ctx.beginPath();
    for(let x=xx;x<=w;x+=gap){ctx.moveTo(x,0);ctx.lineTo(x,h)}
    for(let y=yy;y<=h;y+=gap){ctx.moveTo(0,y);ctx.lineTo(w,y)}
    ctx.stroke();
  }
  function paint(){
    if(!$canvas.width||!state.store)return;
    const dpr=Math.min(3,window.devicePixelRatio||1);
    ctx.setTransform(dpr,0,0,dpr,0,0);
    ctx.clearRect(0,0,state.boardWidth,state.boardHeight);
    drawGrid();
    ctx.setTransform(dpr*state.view.zoom,0,0,dpr*state.view.zoom,
      dpr*state.view.panX,dpr*state.view.panY);
    const doc=state.store.current();
    const page=doc.pages.find(p=>p.id===doc.activePageId);
    for(const stroke of page.strokes)renderStroke(stroke);
    if(state.preview?.kind==="pen")renderStroke({
      color:state.preview.color,width:state.preview.width,
      tool:state.preview.tool,points:state.preview.points});
    if(state.selectedIds.length){
      ctx.save();ctx.lineWidth=1/state.view.zoom;
      ctx.strokeStyle="#5596aa";ctx.setLineDash([5/state.view.zoom,4/state.view.zoom]);
      for(const s of page.strokes.filter(x=>state.selectedIds.includes(x.id))){
        const xs=s.points.map(p=>p.x),ys=s.points.map(p=>p.y),pad=7;
        ctx.strokeRect(Math.min(...xs)-pad,Math.min(...ys)-pad,
           Math.max(...xs)-Math.min(...xs)+2*pad,
           Math.max(...ys)-Math.min(...ys)+2*pad);
      }
      ctx.restore();
    }
    if(state.preview?.kind==="lasso"){
      ctx.save();ctx.strokeStyle="#4c98a2";ctx.setLineDash([6/state.view.zoom,4/state.view.zoom]);
      ctx.lineWidth=2/state.view.zoom;ctx.beginPath();
      state.preview.points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));
      ctx.stroke();ctx.restore();
    }
    if(state.preview?.kind==="erase"){
      const p=state.preview.points.at(-1);
      if(p){
        ctx.save();ctx.lineWidth=1/state.view.zoom;ctx.strokeStyle="#c88f6a";
        ctx.beginPath();ctx.arc(p.x,p.y,13/state.view.zoom,0,2*Math.PI);
        ctx.stroke();ctx.restore();
      }
    }
    if(state.preview?.kind==="move"){
      ctx.save();ctx.strokeStyle="#5596aa";ctx.setLineDash([5/state.view.zoom,5/state.view.zoom]);
      const dx=state.preview.dx,dy=state.preview.dy;
      for(const s of page.strokes.filter(x=>state.selectedIds.includes(x.id))){
        const xs=s.points.map(p=>p.x),ys=s.points.map(p=>p.y);
        ctx.strokeRect(Math.min(...xs)+dx-8,Math.min(...ys)+dy-8,
           Math.max(...xs)-Math.min(...xs)+16,Math.max(...ys)-Math.min(...ys)+16);
      }ctx.restore();
    }
    ctx.setTransform(dpr,0,0,dpr,0,0);
    $("paperScale").textContent=Math.round(100*state.view.zoom)+"%";
    $("paperEmpty").hidden=page.strokes.length>0||Boolean(state.preview);
  }
  function resizePaper(){
    const bounds=$("paperViewport").getBoundingClientRect();
    if(bounds.width<2||bounds.height<2)return;
    const dpr=Math.min(3,devicePixelRatio||1);
    state.boardWidth=bounds.width;state.boardHeight=bounds.height;
    $canvas.width=Math.round(bounds.width*dpr);
    $canvas.height=Math.round(bounds.height*dpr);
    paint();
  }
  function scheduleSave(){
    state.dirtyRevision++;
    setSaveStatus("正在本地保存…");
    clearTimeout(state.saveTimer);
    state.saveTimer=setTimeout(()=>{flushSave().catch(()=>{})},350);
  }
  async function flushSave(){
    clearTimeout(state.saveTimer);
    if(!state.store||state.savedRevision===state.dirtyRevision)return state.saveQueue;
    const snapshot=JSON.parse(JSON.stringify(state.store.current()));
    const revision=state.dirtyRevision;
    state.saveQueue=state.saveQueue.catch(()=>{}).then(()=>Store.save(snapshot)).then(()=>{
      state.savedRevision=Math.max(state.savedRevision,revision);
      if(state.savedRevision===state.dirtyRevision)setSaveStatus("已保存在本机","saved");
    }).catch(e=>{
      setSaveStatus("保存失败 · 请先导出笔记","error");
      console.error("本地保存失败（未上传笔迹）",e);
      // Do not silently navigate away from an unsaved ink document.
      throw e;
    });
    return state.saveQueue;
  }
  function applyChange(fn){
    if(state.store?.apply(fn)){
      pageButtons();paint();updateButtons();scheduleSave();
      return true;
    }
    return false;
  }
  function updateButtons(){
    $("undoInk").disabled=!state.store?.canUndo();
    $("redoInk").disabled=!state.store?.canRedo();
    $("selectionInfo").textContent=state.selectedIds.length?
      "已圈选 "+state.selectedIds.length+" 笔。请自己说明这一步的内容或卡点，助教无法自动识别笔迹。":
      "可先用套索选择纸上的某一步；助教目前不会自动识别手写公式。";
  }
  function pageButtons(){
    const root=$("pageNav");root.replaceChildren();
    const doc=state.store.current();
    doc.pages.forEach((p,i)=>{
      const button=make("button","page-pill"+(p.id===doc.activePageId?" selected":""),"第 "+(i+1)+" 页");
      button.type="button";button.setAttribute("aria-current",p.id===doc.activePageId?"page":"false");
      button.onclick=()=>{
        state.selectedIds=[];state.preview=null;
        applyChange(d=>Core.setPage(d,p.id));
      };
      root.appendChild(button);
    });
  }
  function setTool(tool){
    if(!["pen","highlighter","eraser","lasso","pan"].includes(tool))return;
    state.tool=tool;state.preview=null;
    if(tool!=="lasso")state.selectedIds=[];
    for(const b of document.querySelectorAll("[data-tool]")){
      b.classList.toggle("is-selected",b.dataset.tool===tool);
      b.setAttribute("aria-pressed",String(b.dataset.tool===tool));
    }
    $canvas.style.cursor=tool==="pan"?"grab":tool==="eraser"?"cell":tool==="lasso"?"crosshair":"crosshair";
    updateButtons();paint();
  }

  function insidePolygon(p,polygon){
    let inside=false;
    for(let i=0,j=polygon.length-1;i<polygon.length;j=i++){
      const a=polygon[i],b=polygon[j];
      if((a.y>p.y)!==(b.y>p.y)){
        if(p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x)inside=!inside;
      }
    }
    return inside;
  }
  function pointDistance(a,b){return Math.hypot(a.x-b.x,a.y-b.y)}
  function startGesture(){
    const touches=[...state.fingers.values()];
    if(touches.length===1){
      state.gesture={kind:"touch-pan",origin:touches[0],view:{...state.view}};
    }else if(touches.length>=2){
      const [a,b]=touches;
      state.gesture={kind:"touch-pinch",mid:{x:(a.x+b.x)/2,y:(a.y+b.y)/2},
        distance:Math.max(3,pointDistance(a,b)),view:{...state.view}};
    }else state.gesture=null;
  }
  function updateGesture(){
    const g=state.gesture;if(!g)return;
    const touches=[...state.fingers.values()];
    if(g.kind==="touch-pan" && touches.length===1){
      const p=touches[0];
      state.view={...g.view,
        panX:g.view.panX+p.x-g.origin.x,panY:g.view.panY+p.y-g.origin.y};
    }else if(g.kind==="touch-pinch"&&touches.length>=2){
      const [a,b]=touches,mid={x:(a.x+b.x)/2,y:(a.y+b.y)/2};
      const distance=Math.max(3,pointDistance(a,b));
      const zoom=g.view.zoom*distance/g.distance;
      const next=Core.zoomAt(g.view,zoom,g.mid);
      state.view={...next,panX:next.panX+mid.x-g.mid.x,panY:next.panY+mid.y-g.mid.y};
    }else return;
    paint();
  }
  function pointerDown(event){
    if(!state.store||event.defaultPrevented)return;
    const pt=screenPoint(event),world=worldPoint(event);
    if(event.pointerType==="touch"&&(!$("fingerDraw").checked||state.tool==="pan")){
      // Touch is navigation only; reject contact while writing with a pen.
      if(state.activePen||performance.now()-state.lastPenTime<450)return;
      state.fingers.set(event.pointerId,pt);
      startGesture();
      $canvas.setPointerCapture(event.pointerId);
      event.preventDefault();
      return;
    }
    if(state.activePen)return;
    if(event.button!==0 && !(event.pointerType==="mouse"&&event.button===1))return;
    let kind=state.tool;
    if(event.button===1)kind="pan";
    // Deliberate eraser/lasso tools are not forwarded as mathematical events.
    if(kind==="pan"){
      state.activePen={kind:"pan",pointerId:event.pointerId,origin:pt,
        view:{...state.view}};
    }else if(kind==="lasso"){
      if(state.selectedIds.length && insidePolygon(world,state.selectionPolygon)){
        state.activePen={kind:"move",pointerId:event.pointerId,origin:world};
        state.preview={kind:"move",dx:0,dy:0};
      }else{
        state.selectedIds=[];
        state.selectionPolygon=[];
        state.activePen={kind:"lasso",pointerId:event.pointerId};
        state.preview={kind:"lasso",points:[world]};
      }
    }else if(kind==="eraser"){
      state.activePen={kind:"erase",pointerId:event.pointerId};
      state.preview={kind:"erase",points:[world]};
    }else{
      if(event.pointerType==="pen")state.lastPenTime=performance.now();
      const tool=kind==="highlighter"?"highlighter":"pen";
      state.activePen={kind:"pen",pointerId:event.pointerId};
      state.selectedIds=[];state.selectionPolygon=[];
      state.preview={kind:"pen",tool,color:tool==="highlighter"?"#d2b965":state.color,
        width:tool==="highlighter"?state.width*3:state.width,
        points:[inkSample(event)]};
    }
    $canvas.setPointerCapture(event.pointerId);
    event.preventDefault();paint();updateButtons();
  }
  function pointerMove(event){
    const p=screenPoint(event);
    if(state.fingers.has(event.pointerId)){
      state.fingers.set(event.pointerId,p);updateGesture();return;
    }
    const active=state.activePen;
    if(!active||event.pointerId!==active.pointerId)return;
    if(active.kind==="pan"){
      state.view.panX=active.view.panX+p.x-active.origin.x;
      state.view.panY=active.view.panY+p.y-active.origin.y;
    }else if(active.kind==="move"){
      const w=worldPoint(event);
      state.preview.dx=w.x-active.origin.x;
      state.preview.dy=w.y-active.origin.y;
    }else{
      const events=event.getCoalescedEvents?.()||[event];
      for(const ev of events){
        if(!state.preview||state.preview.points.length>=Core.MAX_POINTS_PER_STROKE)break;
        const w=active.kind==="pen"?inkSample(ev):worldPoint(ev);
        const last=state.preview.points.at(-1);
        if(last && pointDistance(last,w)<(1.2/state.view.zoom))continue;
        state.preview.points.push(w);
      }
      if(event.pointerType==="pen")state.lastPenTime=performance.now();
    }
    event.preventDefault();paint();
  }
  function pointerEnd(event){
    if(state.fingers.has(event.pointerId)){
      state.fingers.delete(event.pointerId);
      startGesture();
      return;
    }
    const active=state.activePen;
    if(!active||event.pointerId!==active.pointerId)return;
    const draft=state.preview;
    state.activePen=null;state.preview=null;
    if(event.pointerType==="pen")state.lastPenTime=performance.now();
    try{
      if(active.kind==="pen"&&draft?.points?.length){
        const stroke=Core.createStroke(uuid(),draft.tool,draft.color,draft.width,draft.points);
        applyChange(d=>Core.appendStroke(d,stroke));
      }else if(active.kind==="erase"&&draft?.points?.length){
        applyChange(doc=>{
          let result=doc;
          for(const pt of draft.points.slice(0,220))
            result=Core.eraseNear(result,pt.x,pt.y,13/state.view.zoom);
          return result;
        });
      }else if(active.kind==="lasso"&&draft?.points?.length>=3){
        state.selectionPolygon=[...draft.points];
        state.selectedIds=Core.selectLasso(state.store.current(),state.selectionPolygon);
        notice(state.selectedIds.length?
          "已选择 "+state.selectedIds.length+" 笔，可再次拖动套索区域移动":
          "当前套索内没有笔迹");
      }else if(active.kind==="move"&&draft){
        if(Math.abs(draft.dx)+Math.abs(draft.dy)>1){
          applyChange(d=>Core.moveStrokes(d,state.selectedIds,draft.dx,draft.dy));
          state.selectionPolygon=state.selectionPolygon.map(p=>({
            x:p.x+draft.dx,y:p.y+draft.dy}));
        }
      }
    }catch(e){notice(e.message)}
    paint();updateButtons();
  }
  function undo(){
    if(state.store?.undo()){state.selectedIds=[];state.selectionPolygon=[];
      pageButtons();paint();updateButtons();scheduleSave();}
  }
  function redo(){
    if(state.store?.redo()){state.selectedIds=[];state.selectionPolygon=[];
      pageButtons();paint();updateButtons();scheduleSave();}
  }
  function setAgentOpen(open){
    state.agentOpen=open;
    $("agentPanel").hidden=!open;
    $("toggleAgent").classList.toggle("is-active",open);
    $("toggleAgent").setAttribute("aria-expanded",String(open));
    if(open)renderAgents();
    requestAnimationFrame(resizePaper);
  }
  function renderAgents(){
    if(!state.session)return;
    const root=$("agentDialogue");root.replaceChildren();
    const turns=state.session.turns||[];
    if(!turns.length){
      root.appendChild(make("div","dialogue-placeholder","没有主动求助时，助教保持安静。"));return;
    }
    for(const turn of turns.slice(-12)){
      root.appendChild(make("div","message student",turn.student_text));
      root.appendChild(make("div","message teacher",turn.tutor_message+
        "\n（规则模拟，未自动验证你的笔迹或数学推导）"));
    }
    root.scrollTop=root.scrollHeight;
  }
  async function sendToAgent(){
    if(!state.session||state.session.completed_at){
      notice("此题会话已结束，不能再次提交求助。");return;
    }
    const field=$("agentQuestion"),note=field.value.trim();
    if(!note){
      notice("先用文字简述卡在哪里；目前不能从圈选笔迹自动识别公式。");
      field.focus();return;
    }
    const button=$("sendToAgent");button.disabled=true;
    try{
      await request("/api/sessions/"+encodeURIComponent(state.sessionId)+"/turns","POST",{
        student_text:note,help_requested:true,request_type:"hint",
        self_report_stage:$("agentStage").value
      });
      state.session=await request("/api/sessions/"+encodeURIComponent(state.sessionId));
      field.value="";renderAgents();
      notice("已收到模拟助教提示；手写笔迹未上传，也未得到数学评分。");
    }catch(e){notice("求助失败："+e.message)}
    finally{button.disabled=false}
  }
  async function switchMode(mode){
    if(!state.session||state.session.completed_at){
      notice("已结束的题目不能修改模式。");return;
    }
    try{
      state.session=await request("/api/sessions/"+encodeURIComponent(state.sessionId)+"/mode",
        "PATCH",{mode});
      $("notebookTopic").textContent=
        ({INDEPENDENT:"自主挑战 · 先独立思考",GUIDE:"推理陪练",ANALYZE:"逻辑分析"})[mode];
      notice("教学模式已切换，不会清除本地笔迹");
    }catch(e){notice(e.message);$("agentMode").value=state.session.mode}
  }
  function downloadJSON(){
    if(!state.store)return;
    const raw=JSON.stringify(state.store.current(),null,2);
    const blob=new Blob([raw],{type:"application/json"});
    const url=URL.createObjectURL(blob),a=document.createElement("a");
    a.href=url;a.download="stem-mentor-synthetic-ink-"+state.sessionId.slice(0,8)+".json";
    document.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),900);
    notice("已导出本地笔迹JSON。仅供演示，未自动生成数学识别结果。");
  }
  function initBindings(){
    $("continueWriting").onclick=async()=>{
      try{
        if(state.sessionId)await openStudy(state.sessionId);
        else await startNewPaper();
      }catch(e){notice(e.message)}
    };
    $("startNewPaper").onclick=()=>startNewPaper().catch(e=>notice(e.message));
    $("studyBack").onclick=()=>showHome().catch(e=>notice(e.message));
    $("toggleProblem").onclick=()=>{
      const box=$("paperProblem");
      box.classList.toggle("is-hidden");
      $("toggleProblem").setAttribute("aria-expanded",String(!box.classList.contains("is-hidden")));
    };
    $("toggleAgent").onclick=()=>setAgentOpen(!state.agentOpen);
    $("closeAgent").onclick=()=>setAgentOpen(false);
    $("agentMode").onchange=e=>switchMode(e.target.value);
    $("sendToAgent").onclick=sendToAgent;
    document.querySelectorAll("[data-tool]").forEach(button=>{
      button.onclick=()=>setTool(button.dataset.tool);
    });
    document.querySelectorAll("[data-color]").forEach(button=>{
      button.onclick=()=>{
        state.color=button.dataset.color;
        document.querySelectorAll("[data-color]").forEach(b=>
          b.classList.toggle("selected",b.dataset.color===state.color));
        setTool("pen");
      };
    });
    $("penWidth").oninput=e=>state.width=Number(e.target.value);
    $("fingerDraw").onchange=e=>{
      state.penOnly=!e.target.checked;
      notice(e.target.checked?
        "已开启手指书写：使用双指缩放请切换到平移工具。":
        "已关闭手指书写：手指用于平移和缩放。");
    };
    $("undoInk").onclick=undo;
    $("redoInk").onclick=redo;
    $("addPaperPage").onclick=()=>{
      try{applyChange(d=>Core.addPage(d));notice("已添加新纸页")}catch(e){notice(e.message)}
    };
    $("exportNotebook").onclick=downloadJSON;
    $canvas.addEventListener("pointerdown",pointerDown);
    $canvas.addEventListener("pointermove",pointerMove);
    $canvas.addEventListener("pointerup",pointerEnd);
    $canvas.addEventListener("pointercancel",pointerEnd);
    $canvas.addEventListener("contextmenu",e=>e.preventDefault());
    $canvas.addEventListener("wheel",e=>{
      if(!state.store)return;
      e.preventDefault();
      const p=screenPoint(e);
      state.view=Core.zoomAt(state.view,state.view.zoom*(e.deltaY<0?1.06:.94),p);
      paint();
    },{passive:false});
    window.addEventListener("keydown",event=>{
      if($study.hidden)return;
      if(["INPUT","TEXTAREA","SELECT"].includes(document.activeElement?.tagName))return;
      if((event.metaKey||event.ctrlKey)&&event.key.toLowerCase()==="z"){
        event.preventDefault();
        if(event.shiftKey)redo();else undo();
      }else if(!event.metaKey&&!event.ctrlKey&&!event.altKey){
        const shortcuts={p:"pen",e:"eraser",l:"lasso",h:"highlighter"};
        if(shortcuts[event.key.toLowerCase()])setTool(shortcuts[event.key.toLowerCase()]);
        if(event.key==="Escape"&&state.agentOpen)setAgentOpen(false);
      }
    });
    window.addEventListener("popstate",async()=>{
      const isStudy=location.pathname==="/ipad/study";
      if(isStudy){
        const query=new URL(location.href).searchParams.get("session")||state.sessionId;
        if(query)await openStudy(query,{push:false});
      }else{
        renderView();await updateHome();
      }
    });
    document.addEventListener("visibilitychange",()=>{
      if(document.visibilityState==="hidden")flushSave().catch(()=>{});
    });
    window.addEventListener("pagehide",()=>{flushSave().catch(()=>{})});
    new ResizeObserver(()=>resizePaper()).observe($("paperViewport"));
    window.MentorIpadPilot=Object.freeze({
      snapshot:()=>state.store?JSON.parse(JSON.stringify(state.store.current())):null,
      view:()=>({...state.view}),saved:()=>state.savedRevision===state.dirtyRevision,
      tool:()=>state.tool,agentOpen:()=>state.agentOpen,openStudy
    });
  }
  async function boot(){
    try{
      initBindings();
      state.catalog=await request("/api/catalog");
      await ensureStudent();
      const sel=$("homeProblem");sel.replaceChildren();
      for(const problem of state.catalog.problems){
        const option=make("option",null,problem.title);
        option.value=problem.id;sel.appendChild(option);
      }
      const isStudy=location.pathname==="/ipad/study";
      if(isStudy){
        const params=new URL(location.href).searchParams;
        const id=params.get("session")||state.sessionId;
        if(id)await openStudy(id,{push:false});
        else{history.replaceState({}, "", "/ipad");renderView();await updateHome()}
      }else{
        renderView();await updateHome();
      }
    }catch(e){
      console.error("iPad handwriting pilot initialization failed",e);
      notice("页面初始化失败："+e.message);
    }
  }
  document.addEventListener("DOMContentLoaded",boot);
})();
