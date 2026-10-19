"use strict";
/* Small transparent tutoring policy for finite sequences; no LLM or grading. */
(function(root,factory){
  const policy=factory();
  if(typeof module==="object"&&module.exports)module.exports=policy;
  root.MentorSeqPolicy=policy;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  const MODES=new Set(["ANALYZE","GUIDE","INDEPENDENT"]);
  const STAGES=new Set(["START","FORWARD","STUCK","BACKWARD","CALCULATION","REFLECTION"]);
  function decide({mode="GUIDE",stage="START",helpRequested=false,
    hintLevel=0,hints=[]}={}){
    if(!MODES.has(mode))mode="GUIDE";
    if(!STAGES.has(stage))stage="START";
    const level=Math.max(0,Math.min(3,Number.isFinite(hintLevel)?Math.trunc(hintLevel):0));
    const info=(action,message)=>Object.freeze({action,message,hintLevel:level,
      engine:"RULE_BASED_SIMULATION",student_proof_verified:false});
    if(!helpRequested)return info("WAIT","先独立探索，不自动显示提示。");
    const cue=hints[Math.min(level===0?0:level-1,2)]||"先观察题目中固定与变化的关系。";
    if(stage==="REFLECTION")return info("ASK_TRANSFER",
      "这道题最关键的策略转变在哪里？换一道新题，你还能独立认出这个结构吗？"+cue);
    if(stage==="CALCULATION")return info("CHECK_BOUNDARY",
      "计算时先核对公比是否为1、参数是否退化、负数符号和初值；让计算服务于已有思路。"+cue);
    if(stage==="STUCK"&&level>=3)return info("OFFER_ALTERNATIVE",
      "连续尝试仍然卡住，可以换一种策略：检查前置条件、先做更小的例子，或者从问题目标倒推。请选择一条，暂不展开全部答案。");
    if(stage==="STUCK")return info("ASK_BACKWARD_GOAL",
      "正推暂时卡住了。先从目标反推：你究竟需要第n项、前n项和，还是某个规律？"+cue);
    if(mode==="ANALYZE")return info("ASK_STRUCTURE",
      "先分清题目已知条件、变化量与目标。你能识别相邻项之间的结构吗？"+cue);
    if(mode==="INDEPENDENT")return info("SELF_CHECK",
      "你已经主动求助。先选一个特殊值检验自己的猜想，再决定是否需要更具体的帮助。"+cue);
    if(stage==="BACKWARD")return info("ASK_BRIDGE",
      "目标需要什么中间结论？它能否与前几项中观察到的关系连接起来？"+cue);
    return info("ASK_OBSERVATION",
      "先保留你的探索思路。改变一个参数，观察哪些关系不变、哪些关系改变。"+cue);
  }
  return Object.freeze({decide});
});
