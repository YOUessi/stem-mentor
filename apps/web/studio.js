"use strict";
/* STEM Mentor · Study Studio v0.6
   Progressive enhancements: no external animations runtime, no model API. */
(function(){
  function draftKey(){return state.sessionId?"stem-draft-"+state.sessionId:null}
  function saveDraft(){const key=draftKey();if(key)localStorage.setItem(key,el("studentInput").value)}
  window.stemSaveDraft=saveDraft;
  window.stemRestoreDraft=function(){
    const key=draftKey();
    el("studentInput").value=key?(localStorage.getItem(key)||""):"";
  };

  // Decorate rather than replace business logic; keep the existing API contracts.
  const baseChat=renderChat;
  renderChat=function(){
    baseChat();
    if((state.session?.turns||[]).length)return;
    const empty=el("chat").querySelector(".empty-chat");
    if(!empty)return;
    const icon=empty.querySelector(".empty-symbol");
    if(icon)icon.textContent="✳";
    const title=empty.querySelector("b");
    if(title)title.textContent="最好的开始，是你先想一步。";
    const para=empty.querySelector("p");
    if(para)para.textContent="这里不会直接放出标准答案。哪怕只有一点观察，我们也可以从那里开始。";
    const cues=pick(empty,"div","starter-cues");
    [
      ["先分析题目条件","我先分析已知条件和问题目标："],
      ["我尝试了一个方法","我想先从已知条件出发，尝试："],
      ["我有一个疑问","这道题我不太理解的地方是："]
    ].forEach(function(pair){
      const button=pick(cues,"button","starter-cue",pair[0]);button.type="button";
      button.onclick=function(){
        const input=el("studentInput");input.value=pair[1];input.focus();
        input.setSelectionRange(input.value.length,input.value.length);saveDraft();
        input.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"center"});
      };
    });
  };
  renderMap=function(){
    const root=el("mindMap");root.replaceChildren();
    const turns=state.session?.turns||[];
    if(!turns.length){pick(root,"div","map-empty","思路不会总是一条直线。每次尝试、卡点、反推和突破，都会记录在这里。");return}
    turns.forEach(function(t,i){
      const node=pick(root,"div","map-node");
      pick(node,"div","map-bullet",String(i+1));
      const content=pick(node,"div");
      pick(content,"b",null,labelFor(t.stage));
      pick(content,"p",null,t.student_text.slice(0,105)+(t.student_text.length>105?"…":""));
      pick(content,"span","map-stage-badge",(t.action||"独立尝试").replaceAll("_"," · "));
    });
  };

  function initSplit(){
    const grid=el("workspaceGrid"),grip=el("splitHandle");if(!grid||!grip)return;
    function update(v){
      const next=Math.max(40,Math.min(65,v));
      grid.style.setProperty("--split-left",String(next)+"%");
      grip.setAttribute("aria-valuenow",String(Math.round(next)));
      localStorage.setItem("stem-workspace-split",String(next));
    }
    const cached=Number(localStorage.getItem("stem-workspace-split"));
    update(Number.isFinite(cached)&&cached>=40?cached:53);
    grip.addEventListener("pointerdown",function(e){
      if(matchMedia("(max-width:1120px)").matches)return;
      e.preventDefault();grip.setPointerCapture(e.pointerId);
      const rect=grid.getBoundingClientRect();
      const move=function(ev){update((ev.clientX-rect.left-12)/(rect.width-13)*100)};
      const cleanup=function(){grip.removeEventListener("pointermove",move)};
      grip.addEventListener("pointermove",move);
      grip.addEventListener("pointerup",cleanup,{once:true});
      grip.addEventListener("pointercancel",cleanup,{once:true});
    });
    grip.addEventListener("keydown",function(e){
      if(e.key!=="ArrowLeft"&&e.key!=="ArrowRight")return;
      e.preventDefault();update(Number(grip.getAttribute("aria-valuenow"))+(e.key==="ArrowRight"?3:-3));
    });
  }
  function initAmbient(){
    const hero=document.querySelector(".workspace-hero");
    if(!hero||matchMedia("(prefers-reduced-motion: reduce)").matches)return;
    hero.addEventListener("pointermove",function(e){
      const box=hero.getBoundingClientRect();
      hero.style.setProperty("--hero-x",Math.round(e.clientX-box.left)+"px");
      hero.style.setProperty("--hero-y",Math.round(e.clientY-box.top)+"px");
    },{passive:true});
  }

  function initPalette(){
    const overlay=el("commandPalette"),field=el("commandSearch"),options=el("commandOptions");
    if(!overlay||!field||!options)return;
    let focusedBefore=null,chosen=0,visible=[];
    const optionsData=[
      {title:"学习工作台",note:"继续正在进行的思考",glyph:"◇",run:function(){return openView("workspace")}},
      {title:"我的解题经历",note:"回顾以前的突破口",glyph:"◷",run:function(){return openView("history")}},
      {title:"易漏考点回忆",note:"学习之后的主动巩固",glyph:"▤",run:function(){return openView("review")}},
      {title:"数学方法库",note:"寻找数学模型与技巧",glyph:"⊞",run:function(){return openView("methods")}},
      {title:"逻辑分析模式",note:"分析本质与方法适用条件",glyph:"◎",run:function(){openView("workspace");return switchMode("ANALYZE")}},
      {title:"推理陪练模式",note:"从卡点引导正推和逆推",glyph:"↝",run:function(){openView("workspace");return switchMode("GUIDE")}},
      {title:"自主挑战模式",note:"先独立尝试、不自动剧透",glyph:"✎",run:function(){openView("workspace");return switchMode("INDEPENDENT")}},
      {title:"返回草稿",note:"继续写出你自己的思路",glyph:"✳",run:function(){openView("workspace");el("studentInput").focus()}}
    ];
    function close(){overlay.hidden=true;field.value="";if(focusedBefore?.focus)focusedBefore.focus()}
    function execute(opt){close();Promise.resolve(opt.run()).catch(function(e){notify(e.message)})}
    function render(){
      visible=optionsData.filter(function(opt){
        return (opt.title+opt.note).toLowerCase().includes(field.value.trim().toLowerCase());
      });
      chosen=Math.min(chosen,Math.max(0,visible.length-1));
      options.replaceChildren();
      if(!visible.length){pick(options,"div","map-empty","没有找到相关操作，换个关键词试试。");return}
      visible.forEach(function(opt,i){
        const b=pick(options,"button","command-option"+(i===chosen?" selected":""));b.type="button";
        pick(b,"span","command-option-icon",opt.glyph);pick(b,"span",null,opt.title);
        pick(b,"small",null,opt.note);b.onclick=function(){execute(opt)};
        b.addEventListener("pointerenter",function(){
          chosen=i;options.querySelectorAll(".command-option").forEach(function(n,j){n.classList.toggle("selected",i===j)});
        });
      });
    }
    function open(){focusedBefore=document.activeElement;chosen=0;field.value="";overlay.hidden=false;render();requestAnimationFrame(function(){field.focus()})}
    el("commandTrigger").addEventListener("click",open);
    el("commandClose").addEventListener("click",close);
    overlay.querySelector(".command-backdrop").addEventListener("click",close);
    field.addEventListener("input",function(){chosen=0;render()});
    field.addEventListener("keydown",function(e){
      if((e.key==="ArrowDown"||e.key==="ArrowUp")&&visible.length){
        e.preventDefault();
        chosen=(chosen+(e.key==="ArrowDown"?1:-1)+visible.length)%visible.length;render();
      }
      if(e.key==="Enter"&&visible[chosen]){e.preventDefault();execute(visible[chosen])}
    });
    document.addEventListener("keydown",function(e){
      if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==="k"){e.preventDefault();overlay.hidden?open():close()}
      if(e.key==="Escape"&&!overlay.hidden){e.preventDefault();close()}
    });
  }

  function initEnhancements(){
    const draft=el("studentInput");if(draft)draft.addEventListener("input",saveDraft);
    initSplit();initAmbient();initPalette();
  }
  document.addEventListener("DOMContentLoaded",initEnhancements);
})();
