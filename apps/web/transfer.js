"use strict";
/* Demo-only, voluntary transfer cycle. No answer grading, no model calls. */
(function(root){
  const el=id=>document.getElementById(id);
  let currentId=null, ticket=0, latest=null;
  const make=(parent,tag,cls,content)=>{
    const n=document.createElement(tag);
    if(cls)n.className=cls;
    if(content!==undefined)n.textContent=String(content);
    parent.appendChild(n);return n;
  };
  async function json(path,method="GET",body){
    const r=await fetch(path,{method,headers:{"Content-Type":"application/json"},
      body:body===undefined?undefined:JSON.stringify(body)});
    if(!r.ok){
      const error=await r.json().catch(()=>({detail:"操作未完成"}));
      throw Error(typeof error.detail==="string"?error.detail:"信息填写有误，请检查");
    }
    return r.json();
  }
  function message(parent,text,status="neutral"){
    return make(parent,"p","transfer-status "+status,text);
  }
  function addTextInput(parent,label,placeholder){
    const box=make(parent,"div","transfer-field");
    const lbl=make(box,"label","",label);
    const input=make(box,"textarea","",undefined);
    input.rows=3;input.maxLength=2000;
    input.placeholder=placeholder;input.setAttribute("aria-label",label);
    return input;
  }
  function stages(parent){
    const label=make(parent,"label","transfer-stage","你目前采用的思考方式（自报，非自动识别）");
    const select=make(label,"select");
    select.setAttribute("aria-label","迁移练习思考阶段");
    for(const [value,text] of [
      ["START","观察条件"],["FORWARD","正向尝试"],
      ["STUCK","思路卡住"],["BACKWARD","从目标反推"],
      ["BRIDGE","寻找连接"],["CALCULATION","常规运算"],
      ["REFLECTION","方法复盘"]]){
      const o=make(select,"option","",text);o.value=value;
    }
    return select;
  }
  function button(parent,label,run,primary=false){
    const b=make(parent,"button","btn "+(primary?"btn-primary":"btn-light"),label);
    b.type="button";
    b.addEventListener("click",async()=>{
      b.disabled=true;
      try{await run(b)}catch(e){
        const target=el("transferFeedback");
        if(target)target.textContent=e.message;
        b.disabled=false;
      }
    });
    return b;
  }
  function renderForm(host,phase,session,candidate){
    const container=make(host,"div","transfer-step");
    const label=phase==="BEFORE_RECALL"?"第一阶段：冻结自己的独立思路":
      "第三阶段：记录回忆旧题后的新思路";
    make(container,"h3","",label);
    message(container,phase==="BEFORE_RECALL"?
      "先不看任何历史提示，写下你自己的已知、目标和突破口。冻结后不能覆盖。":
      "比较新旧题的相同结构和不同条件，再写下你的新想法。不要复述旧题答案。");
    const input=addTextInput(container,
      phase==="BEFORE_RECALL"?"无提示独立思路（至少10个字）":"对比前后的新思路（至少10个字）",
      phase==="BEFORE_RECALL"?"我先把条件分成……，考虑从……入手":
      "旧题与这题相同的结构是……；需要特别检查的条件是……");
    const stage=stages(container);
    const feedback=make(container,"p","transfer-feedback");feedback.id="transferFeedback";
    const locked=phase==="BEFORE_RECALL" &&
      (session.mode!=="INDEPENDENT" || session.hint_count>0 ||
       session.turns.some(t=>t.action!=="WAIT"));
    if(locked){
      message(container,
        "当前会话不满足无提示冻结条件。请切换到「自主挑战」，新建一题再尝试；已有导师提示的过程不能伪装成无提示。","warning");
    }
    const action=button(container,phase==="BEFORE_RECALL"?
      "冻结我的无提示尝试":"记录回忆后的思路",async()=>{
      const idea=input.value.trim();
      if(idea.length<10)throw Error("请先写至少十个字符的真实思考过程。");
      await json("/api/sessions/"+encodeURIComponent(session.id)+"/transfer/attempts","POST",{
        phase,attempt_text:idea,self_report_stage:stage.value,
        source_episode_id:phase==="AFTER_RECALL"?candidate?.source_episode_id:null
      });
      feedback.textContent="已保存真实思考过程，但这不代表数学正确。";
      await renderSession(session);
    },true);
    action.disabled=Boolean(session.completed_at)||locked;
  }
  function renderRecords(parent,records){
    if(!records.length)return;
    const list=make(parent,"div","transfer-records");
    for(const record of records){
      const card=make(list,"div","transfer-record");
      make(card,"strong","",record.phase==="BEFORE_RECALL"?
        "已冻结的无提示基线":"旧题回忆后的新思路");
      make(card,"p","",record.attempt_text);
      make(card,"small","",
        "证据："+record.evidence_status+"；未自动判断答案正确。");
    }
  }
  function paint(host,data,session){
    host.replaceChildren();
    const records=data.records||[];
    const before=records.find(x=>x.phase==="BEFORE_RECALL");
    const after=records.find(x=>x.phase==="AFTER_RECALL");
    const top=make(host,"div","transfer-flow");
    const steps=["先独立尝试","再回忆旧题","最后检验迁移"];
    steps.forEach((label,i)=>{
      const c=make(top,"span",i===0&&before||i===1&&data.history_candidate?
        "transfer-flow-done":"transfer-flow-pending",label);
      c.title="学习过程记录，不是正确率或掌握度";
    });
    if(session.completed_at && !before){
      message(host,"这个会话已结束。开始新题才能记录无提示迁移基线。","warning");
    }else if(!before){
      renderForm(host,"BEFORE_RECALL",session,null);
    }else if(!data.history_candidate){
      message(host,
        "已冻结你的独立思路，但没有找到本人确实做过且数学结构足够接近的旧题。不编造历史记忆。","warning");
    }else if(!after && data.phase!=="AFTER_RECALL_READY"){
      const box=make(host,"div","transfer-step");
      make(box,"h3","","第二阶段：主动回忆过去真实做过的题");
      const old=data.history_candidate;
      message(box,"匹配到你的真实旧题：《"+old.prior_problem_title+
        "》。它只是一条自报完成的学习记录，不代表曾解对。");
      message(box,"先想想：那时在哪里改变思路？此题有什么条件不同？");
      button(box,"主动请求旧题回忆",async()=>{
        await root.mentorTransferRecall?.();
      });
    }else if(!after){
      const old=data.history_candidate;
      message(host,"已经主动回忆《"+old.prior_problem_title+"》。现在比较结构与适用条件，不照搬完整解答。");
      renderForm(host,"AFTER_RECALL",session,old);
    }else{
      message(host,"本轮迁移练习已记录完毕。可以对照自己前后的想法，但数学正确性和真正独立迁移尚未验证。","success");
    }
    renderRecords(host,records);
    message(host,data.disclaimer);
  }
  async function renderSession(session){
    if(!session?.id)return;
    const token=++ticket,host=el("transferBody");
    if(!host)return;
    if(currentId!==session.id){
      currentId=session.id;
      host.textContent="正在准备本题的迁移过程……";
    }
    try{
      const data=await json("/api/sessions/"+encodeURIComponent(session.id)+"/transfer");
      if(token!==ticket || session.id!==currentId)return;
      latest=data;
      paint(host,data,session);
    }catch(e){
      if(token===ticket)host.textContent="暂时无法读取迁移记录。原来的解题、历史和数学工具不受影响："+e.message;
    }
  }
  async function renderSummary(studentId){
    const box=el("transferSummaryBox");if(!box||!studentId)return;
    try{
      const data=await json("/api/students/"+encodeURIComponent(studentId)+"/transfer-summary");
      box.replaceChildren();
      const head=make(box,"strong","","迁移学习过程（演示）");
      make(box,"p","",
        "已记录无提示尝试 "+data.baseline_attempts+" 次；回忆后再尝试 "+
        data.post_recall_attempts+" 次。当前正确性未验证，不能据此计算独立掌握率。");
    }catch(e){
      box.textContent="迁移过程汇总暂不可用："+e.message;
    }
  }
  root.MentorTransfer={renderSession,renderSummary};
})(window);
