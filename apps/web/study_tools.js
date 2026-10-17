"use strict";
/* STEM Mentor green learning tools v0.7.
   Offline math typesetting, exploratory geometry, and evidence-safe thought graph.
   Mathematics shown to students is limited to problem givens or their own attempts.
*/
(function () {
  const SVG_NS = "http://www.w3.org/2000/svg";
  const state = {
    lastSession: null, currentProblem: null, activeSession: null, mathTicket: 0,
    graphTicket: 0, geometry: null, pendingLoad: 0
  };
  const $ = id => document.getElementById(id);
  const bounded = (v,lo,hi) => Math.min(hi,Math.max(lo,v));
  const text = (parent,tag,cls,value) => {
    const node = document.createElement(tag);
    if(cls) node.className=cls;
    if(value!==undefined)node.textContent=String(value);
    parent.appendChild(node);return node;
  };
  const svg = (parent,tag,attrs={},content) => {
    const node=document.createElementNS(SVG_NS,tag);
    for(const [name,value] of Object.entries(attrs))node.setAttribute(name,String(value));
    if(content!==undefined)node.textContent=String(content);
    parent.appendChild(node);return node;
  };

  async function typeset(root) {
    if(!root || !window.MathJax?.typesetPromise)return;
    try {
      if(window.MathJax.typesetClear) window.MathJax.typesetClear([root]);
      await window.MathJax.typesetPromise([root]);
    } catch(e) {
      // Never hide or erase student text when rendering is unavailable.
      console.warn("本地公式排版暂不可用，保留原始表达式。",e);
    }
  }

  function renderFormula(latex) {
    const box=$("problemFormula"), target=$("problemFormulaMath");
    if(!box||!target)return;
    if(!latex){box.hidden=true;target.replaceChildren();return}
    box.hidden=false;
    target.textContent="\\("+latex+"\\)";
    typeset(target);
  }

  const ALLOWED_COMMANDS=new Set(["frac","dfrac","tfrac","sqrt","ge","geq","le","leq",
    "ne","neq","times","cdot","sin","cos","tan","log","ln","sum","prod","theta",
    "alpha","beta","gamma","pi","in","mathbb","vec","angle","overline","left",
    "right","pm","infty","neq","rightarrow","to","div","int"]);
  function validatePreview(source) {
    if(source.length>300)return false;
    for(const match of source.matchAll(/\\([a-zA-Z]+)/g))
      if(!ALLOWED_COMMANDS.has(match[1]))return false;
    // No HTML or unsafe TeX extension commands. All student content enters via textContent.
    return !/[<>]/.test(source);
  }

  async function renderPreview() {
    const target=$("studentMathPreview"),input=$("studentInput");
    if(!target || !input)return;
    const value=input.value.slice(0,2500);
    const regex=/\\\(([\s\S]*?)\\\)/g;
    target.replaceChildren();
    let cursor=0,count=0,match,hasFormula=false;
    while((match=regex.exec(value)) && count<6) {
      if(match.index>cursor)text(target,"span","",value.slice(cursor,match.index));
      if(!validatePreview(match[1])){
        text(target,"span","math-preview-warning",match[0]+"（含未支持的数学指令）");
      }else{
        const node=text(target,"span","preview-math","\\("+match[1]+"\\)");
        node.dataset.mathFragment="true";
        hasFormula=true;
      }
      cursor=regex.lastIndex;count++;
    }
    if(value.length>cursor)text(target,"span","",value.slice(cursor));
    if(!value)text(target,"span","", "在草稿中用 \\( 与 \\) 包裹公式，即可查看排版。");
    if(count>=6 && regex.exec(value))text(target,"span","math-preview-warning","（仅预览前六个公式）");
    if(hasFormula)await typeset(target);
  }

  function insertSnippet(snippet) {
    const input=$("studentInput");if(!input)return;
    const start=input.selectionStart,end=input.selectionEnd;
    const insert="\\("+snippet+"\\)";
    input.value=input.value.slice(0,start)+insert+input.value.slice(end);
    input.focus();
    input.setSelectionRange(start+2,start+2);
    renderPreview();
  }

  function geometryReadout(scene) {
    const target=$("geometryReadout");if(!target)return;
    const [x,y]=scene.P;
    if(scene.config.kind==="two_foci"){
      const [A,B]=scene.config.foci;
      const da=Math.hypot(x-A[0],y-A[1]),db=Math.hypot(x-B[0],y-B[1]);
      const isRatio=scene.config.measure==="ratio";
      const value=isRatio?(db<1e-8?Infinity:da/db):da+db;
      const label=isRatio?"PA / PB":"PA + PB";
      const targetValue=scene.config.target;
      const valueText=Number.isFinite(value)?value.toFixed(2):"未定义（PB=0）";
      target.textContent=label+" ≈ "+valueText+"；题目条件 "+label+" = "+targetValue.toFixed(2)+"。"+
       (Math.abs(value-targetValue)<.12?" 已接近题目条件。":" 继续移动，观察如何接近条件。");
    }else{
      const a=scene.config.a,b=scene.config.b;
      const v=x*x/(a*a)+y*y/(b*b);
      target.textContent="当前 P("+x.toFixed(2)+", "+y.toFixed(2)+")；代入已知曲线左边 ≈ "+v.toFixed(2)+
        "（题目给出右边为 1）。可以观察什么时候点位于曲线上。";
    }
  }

  const screenPoint=([x,y])=>[285+x*25,146-y*25];
  const fromScreen=([x,y])=>[(x-285)/25,(146-y)/25];
  function focusPath(scene) {
    if(scene.config.kind==="conic"){
      const {a,b}=scene.config;
      return Array.from({length:130},(_,i)=>{
        const theta=i*Math.PI*2/129;
        return [a*Math.cos(theta),b*Math.sin(theta)];
      });
    }
    return null; // Never draw an unseen locus automatically for a two-focus problem.
  }
  function constrainPoint(scene,[x,y]) {
    if(scene.config.kind==="conic"){
      const a=scene.config.a,b=scene.config.b;
      const angle=Math.atan2(y/b,x/a);
      return [a*Math.cos(angle),b*Math.sin(angle)];
    }
    const [A,B]=scene.config.foci,mid=[(A[0]+B[0])/2,(A[1]+B[1])/2];
    if(scene.config.measure==="ratio"){
      const k=scene.config.target,k2=k*k;
      if(Math.abs(k-1)<1e-7) return [mid[0],y];
      const cx=(A[0]-k2*B[0])/(1-k2),cy=(A[1]-k2*B[1])/(1-k2);
      const r=k*Math.hypot(A[0]-B[0],A[1]-B[1])/Math.abs(1-k2);
      const angle=Math.atan2(y-cy,x-cx);
      return [cx+r*Math.cos(angle),cy+r*Math.sin(angle)];
    }
    const total=scene.config.target;
    const c=Math.hypot(A[0]-B[0],A[1]-B[1])/2;
    const a=total/2,b=Math.sqrt(Math.max(0,a*a-c*c));
    const center=mid;
    const theta=Math.atan2((y-center[1])/Math.max(b,.1),(x-center[0])/a);
    return [center[0]+a*Math.cos(theta),center[1]+b*Math.sin(theta)];
  }
  function pathPoints(points,close=false) {
    if(!points.length)return "";
    return points.map((v,i)=>{
      const [x,y]=screenPoint(v);
      return (i?"L":"M")+x.toFixed(2)+" "+y.toFixed(2);
    }).join(" ")+(close?" Z":"");
  }
  function drawGeometry(scene) {
    const root=$("geometrySvg");root.replaceChildren();
    root.setAttribute("viewBox","0 0 620 280");
    for(let x=10;x<=610;x+=50)svg(root,"line",{class:"geogrid",x1:x,y1:0,x2:x,y2:280});
    for(let y=21;y<=271;y+=50)svg(root,"line",{class:"geogrid",x1:0,y1:y,x2:620,y2:y});
    svg(root,"line",{class:"geoaxis",x1:0,y1:146,x2:620,y2:146});
    svg(root,"line",{class:"geoaxis",x1:285,y1:0,x2:285,y2:280});
    svg(root,"text",{x:597,y:140,class:"geonote"},"x");
    svg(root,"text",{x:293,y:14,class:"geonote"},"y");
    svg(root,"text",{x:269,y:161,class:"geonote"},"O");
    const curve=focusPath(scene);
    if(curve)svg(root,"path",{d:pathPoints(curve),class:"geocurve"});
    if(scene.config.kind==="two_foci"){
      scene.config.foci.forEach((v,i)=>{
        const [fx,fy]=screenPoint(v),[px,py]=screenPoint(scene.P);
        svg(root,"line",{class:"geolink",x1:fx,y1:fy,x2:px,y2:py});
        svg(root,"circle",{class:"geofocus",cx:fx,cy:fy,r:5});
        svg(root,"text",{class:"geolabel",x:fx+8,y:fy-8},i?"B":"A");
      });
    }
    if(scene.trail.length>1)svg(root,"path",{class:"geotrace",d:pathPoints(scene.trail)});
    const [px,py]=screenPoint(scene.P);
    svg(root,"circle",{cx:px,cy:py,r:17,fill:"transparent","data-drag-point":"true"});
    svg(root,"circle",{class:"geop",cx:px,cy:py,r:7,"data-drag-point":"true"});
    svg(root,"text",{class:"geolabel",x:px+9,y:py-12,"pointer-events":"none"},"P");
    svg(root,"text",{class:"geonote",x:16,y:24},scene.constrained?"已选择沿条件探索 · 当前仅显示自己拖动过的路径":"自由拖动 · 观察条件如何变化");
    geometryReadout(scene);
    $("geometryConstrain").classList.toggle("selected",scene.constrained);
    $("geometryFree").classList.toggle("selected",!scene.constrained);
    $("geometryConstrain").textContent=scene.config.kind==="conic"?"沿已知曲线探索（主动选择）":"沿题目条件探索（主动选择）";
  }

  function sceneFor(config) {
    return {config:config,P:[...config.initial],constrained:false,trail:[],dragging:false};
  }

  function useGeometry(config) {
    const panel=$("geometryPanel"),details=$("geometryDetails");
    if(!panel||!details)return;
    if(!config){panel.hidden=true;state.geometry=null;details.open=false;return}
    panel.hidden=false;
    const intro=$("geometryIntro");
    intro.textContent=config.kind==="two_foci"?
      "A、B 是固定点。先自由拖动 P，观察距离关系；需要时再主动选择“沿题目条件探索”。":
      "椭圆是题目给定的曲线。拖动 P，观察点与已知方程的关系；不直接显示切线公式。";
    const scene=state.geometry=sceneFor(config);
    drawGeometry(scene);
  }

  function setGeometryMode(constrained) {
    const scene=state.geometry;if(!scene)return;
    scene.constrained=constrained;
    scene.trail=[];
    if(constrained)scene.P=constrainPoint(scene,scene.P);
    drawGeometry(scene);
  }

  function clearGeometry(){
    const scene=state.geometry;if(!scene)return;
    scene.trail=[];
    drawGeometry(scene);
  }

  function geometryPointer(event,phase) {
    const scene=state.geometry,root=$("geometrySvg");if(!scene)return;
    if(phase==="up"){scene.dragging=false;return}
    if(phase==="down"){
      scene.dragging=true;
      root.setPointerCapture?.(event.pointerId);
    }else if(!scene.dragging)return;
    event.preventDefault();
    const matrix=root.getScreenCTM();
    if(!matrix)return;
    const point=root.createSVGPoint();
    point.x=event.clientX;point.y=event.clientY;
    const local=point.matrixTransform(matrix.inverse());
    const proposed=fromScreen([local.x,local.y]);
    let next=scene.constrained?constrainPoint(scene,proposed):proposed;
    next=[bounded(next[0],-11,13),bounded(next[1],-5,5)];
    // Clamping is visual viewport only; use full condition projection again
    // only when it falls within visible bounds.
    scene.P=next;
    if(scene.constrained){
      const prev=scene.trail.at(-1);
      if(!prev || Math.hypot(prev[0]-next[0],prev[1]-next[1])>.065)scene.trail.push([...next]);
      if(scene.trail.length>300)scene.trail.shift();
    }
    drawGeometry(scene);
  }

  function initGeometryEvents(){
    const root=$("geometrySvg");if(!root)return;
    root.addEventListener("pointerdown",e=>geometryPointer(e,"down"));
    root.addEventListener("pointermove",e=>geometryPointer(e,"move"));
    root.addEventListener("pointerup",e=>geometryPointer(e,"up"));
    root.addEventListener("pointercancel",e=>geometryPointer(e,"up"));
    $("geometryConstrain").addEventListener("click",()=>setGeometryMode(true));
    $("geometryFree").addEventListener("click",()=>setGeometryMode(false));
    $("geometryClear").addEventListener("click",clearGeometry);
  }

  const STAGE_LABELS={
    START:"起步观察",FORWARD:"正向探索",STUCK:"遇到卡点",
    BACKWARD:"逆向分析",BRIDGE:"寻找桥梁",CALCULATION:"常规计算",REFLECTION:"方法复盘"
  };
  function graphBoxFor(node,index){
    if(node.id==="given")return [25,14,240,54];
    if(node.id==="goal")return [355,14,240,54];
    const role=node.role;
    const x=(role==="FORWARD"||role==="START")?25:role==="BACKWARD"?355:190;
    return [x,95+index*79,240,55];
  }
  const brief=value=>{
    const v=String(value||"").replace(/\s+/g," ");
    return v.length>17?v.slice(0,16)+"…":v;
  };

  function drawThinkingMap(payload,session){
    const root=$("mindMap"),detail=$("mindMapDetail");
    if(!root||!detail)return;
    root.replaceChildren();detail.hidden=true;
    const all=payload.nodes||[];
    const anchors=all.filter(n=>n.id==="given"||n.id==="goal");
    const steps=all.filter(n=>n.origin==="STUDENT");
    const visibleSteps=steps.slice(-15);
    const included=anchors.concat(visibleSteps);
    const positions=new Map();
    const graph=text(root,"div","mind-graph-canvas");
    const drawing=svg(graph,"svg",{
      viewBox:"0 0 625 "+(115+Math.max(1,visibleSteps.length)*79),
      role:"img",
      "aria-label":"思维探索图：上方是已知条件与目标，下方是学生真实思考，虚线不表示数学证明"
    });
    included.forEach((n,i)=>positions.set(n.id,graphBoxFor(n,Math.max(0,i-2))));
    const edges=(payload.edges||[]).filter(e=>positions.has(e.source)&&positions.has(e.target));
    edges.forEach(e=>{
      const from=positions.get(e.source),to=positions.get(e.target);
      const x1=from[0]+from[2]/2,y1=from[1]+from[3],x2=to[0]+to[2]/2,y2=to[1];
      const half=(y1+y2)/2;
      const d="M "+x1+" "+y1+" C "+x1+" "+half+", "+x2+" "+half+", "+x2+" "+y2;
      const user=e.relation==="STUDENT_HYPOTHESIS_UNVERIFIED";
      const line=svg(drawing,"path",{d,class:user?"mind-user-link":"mind-link","data-relation":e.relation||"NOT_PROOF"});
      if(user)svg(line,"title",{},"学生提出的关系（未经证明）："+(e.label||"未填写理由"));
    });

    let linkMode=false,selectedFirst=null;
    const info=message=>{
      detail.replaceChildren();
      text(detail,"div","",message);detail.hidden=false;
    };
    function drawSelected(){
      drawing.querySelectorAll(".mind-vertex").forEach(n=>n.classList.toggle("active",n.dataset.id===selectedFirst));
    }
    async function selectNode(node){
      if(!linkMode){
        detail.replaceChildren();
        text(detail,"strong","",node.id==="given"?"题目已知条件":node.id==="goal"?"问题目标":STAGE_LABELS[node.role]||"学生思路");
        text(detail,"div","",node.statement);
        text(detail,"span","status-warning",node.origin==="STUDENT"?
          "这是学生的原始想法，数学正确性尚未验证。":"此处只展示题目给出的已知和目标，不包含隐藏解答。");
        detail.hidden=false;return;
      }
      if(!selectedFirst){
        selectedFirst=node.id;
        info("已选择起点："+(node.id==="given"?"题目条件":node.id==="goal"?"问题目标":brief(node.statement))+"。请再选择另一节点。");
        drawSelected();return;
      }
      if(selectedFirst===node.id){info("请选另一条思路作为终点。");return}
      const reason=(root.querySelector("#thoughtLinkLabel")?.value||"").trim();
      if(session.completed_at){info("已结束的会话不允许新增思路关联。");return}
      const source=selectedFirst,target=node.id;
      linkMode=false;selectedFirst=null;
      try{
        const response=await fetch("/api/sessions/"+encodeURIComponent(session.id)+"/thinking-links",{
          method:"POST",headers:{"Content-Type":"application/json"},
          body:JSON.stringify({source,target,label:reason})
        });
        if(!response.ok)throw Error("这条关联还没有保存："+response.status);
        info("你提出的关联已经保存，但还没有验证数学正确性。");
        await renderTimeline(session);
      }catch(e){info(e.message)}
    }
    included.forEach(node=>{
      const [x,y,w,h]=positions.get(node.id);
      const anchor=node.id==="given"||node.id==="goal";
      const kind=anchor?"anchor":node.role==="STUCK"?"pending":node.role==="BACKWARD"?"reverse":"normal";
      const element=svg(drawing,"g",{class:"mind-vertex "+kind,"data-id":node.id,
        role:"button",tabindex:0,"aria-label":(anchor?"题目":STAGE_LABELS[node.role]||"学生思考")+": "+brief(node.statement)});
      svg(element,"rect",{x,y,width:w,height:h,rx:10,ry:10});
      svg(element,"text",{x:x+12,y:y+21,class:"mind-title"},
        anchor?(node.id==="given"?"已知条件":"问题目标"):(STAGE_LABELS[node.role]||"思考过程"));
      svg(element,"text",{x:x+12,y:y+41,class:"mind-subtitle"},brief(node.statement));
      element.addEventListener("click",()=>selectNode(node));
      element.addEventListener("keydown",e=>{
        if(e.key==="Enter"||e.key===" "){e.preventDefault();selectNode(node)}
      });
    });
    text(root,"p","mind-graph-legend",
      "灰色虚线表示尝试先后；绿色虚线只是你自己提出的联系。它们都不代表已经证明。");
    if(steps.length>visibleSteps.length)
      text(root,"p","mind-graph-legend","仅显示最近 15 次尝试，早期原始内容仍保存在会话历史中。");
    const mobileAnchors=text(root,"div","mind-mobile-anchors");
    anchors.forEach(node=>{
      const button=text(mobileAnchors,"button","mind-mobile-anchor","");
      button.type="button";
      text(button,"b","",node.id==="given"?"已知条件":"问题目标");
      text(button,"span","",brief(node.statement));
      button.onclick=()=>selectNode(node);
    });
    const controls=text(root,"div","thought-link-panel");
    const action=text(controls,"button","btn btn-light","连接我的两步思路");
    action.type="button";action.disabled=Boolean(session.completed_at)||!visibleSteps.length;
    const reason=text(controls,"input","","");
    reason.id="thoughtLinkLabel";reason.maxLength=100;
    reason.placeholder="两步为什么有关联？（可选）";
    reason.setAttribute("aria-label","思路关联理由（未经验证）");
    action.onclick=()=>{
      linkMode=!linkMode;selectedFirst=null;drawSelected();
      action.textContent=linkMode?"取消连线":"连接我的两步思路";
      info(linkMode?"依次点击两个节点，记录一个待检验的思路联系。":"已取消连线操作。");
    };
    const list=text(root,"div","mind-timeline");
    visibleSteps.forEach((node,i)=>{
      const card=text(list,"button","map-node","");
      card.type="button";card.dataset.nodeId=node.id;
      text(card,"span","map-bullet",String(steps.length-visibleSteps.length+i+1));
      const content=text(card,"span","");
      text(content,"b","",STAGE_LABELS[node.role]||"学生思考");
      text(content,"p","",brief(node.statement));
      card.onclick=()=>selectNode(node);
    });
    edges.filter(e=>e.relation==="STUDENT_HYPOTHESIS_UNVERIFIED").forEach(e=>{
      text(root,"p","mind-graph-legend","待验证的个人猜想："+(e.label||"两步可能有关联"));
    });
  }

  async function renderTimeline(session){
    if(!session?.id)return;
    const ticket=++state.graphTicket;
    try{
      const response=await fetch("/api/sessions/"+encodeURIComponent(session.id)+"/reasoning-map");
      if(!response.ok)throw Error("暂时无法读取思维探索图");
      const data=await response.json();
      if(ticket!==state.graphTicket||session.id!==state.lastSession)return;
      if(data.contains_teacher_solution===true)throw Error("不能在学生侧展示隐藏解法");
      drawThinkingMap(data,session);
    }catch(e){
      if(ticket!==state.graphTicket)return;
      const root=$("mindMap");if(root){
        root.replaceChildren();
        text(root,"div","map-empty","思维图暂时不可用。原始学习对话仍然保存在会话中。");
      }
      console.warn("思维图加载失败",e);
    }
  }

  function draftKey(session){
    return session?.id&&session?.student_id?
      "stem-v07-draft:"+session.student_id+":"+session.id:null;
  }
  function saveDraft(){
    const key=draftKey(state.activeSession);
    if(key)try{localStorage.setItem(key,$("studentInput").value.slice(0,4000))}catch(e){}
  }
  function clearDraft(){
    const key=draftKey(state.activeSession);
    if(key)try{localStorage.removeItem(key)}catch(e){}
  }
  async function renderSession(session){
    if(!session)return;
    const problemId=session.problem?.id||null;
    const changed=session.id!==state.lastSession||problemId!==state.currentProblem;
    if(changed)try{
      const saved=localStorage.getItem(draftKey(session));
      $("studentInput").value=saved||"";
    }catch(e){}
    state.lastSession=session.id;
    state.activeSession=session;
    if(changed){
      state.currentProblem=problemId;
      state.pendingLoad++;
      useGeometry(null);
      renderFormula(null);
      if(problemId){
        const ticket=state.pendingLoad;
        try{
          const response=await fetch("/api/study/visual/"+encodeURIComponent(problemId));
          if(response.ok){
            const card=await response.json();
            if(ticket!==state.pendingLoad||state.lastSession!==session.id)return;
            if(card.teacher_solution_included===true)throw Error("教师专用内容不能显示");
            renderFormula(card.latex);
            useGeometry(card.geometry||null);
          }
        }catch(e){
          console.warn("题目可视化加载失败，不影响原有学习对话",e);
        }
      }
    }
    await renderTimeline(session);
    if($("mathPreviewDetails")?.open)await renderPreview();
  }

  function initStudyTools(){
    $("mathPreviewDetails")?.addEventListener("toggle",e=>{
      if(e.target.open)renderPreview();
    });
    $("studentInput")?.addEventListener("input",()=>{
      saveDraft();
      if($("mathPreviewDetails")?.open)renderPreview();
    });
    document.querySelectorAll("[data-math-snippet]").forEach(b=>{
      b.addEventListener("click",()=>insertSnippet(b.dataset.mathSnippet));
    });
    initGeometryEvents();
  }

  window.studyTools={renderSession,renderPreview,renderTimeline,clearDraft,saveDraft};
  document.addEventListener("DOMContentLoaded",initStudyTools);
})();
