"use strict";
/* Green, zero-model-API learning laboratory. Every scene is a fixed, reviewed-later preset. */
(function(root){
  const $=id=>document.getElementById(id);
  const TEAMS=[
    ["function_2d","函数与二维坐标","函数、图像与变化"],
    ["conic_2d","圆锥曲线","直线、圆、椭圆、双曲线、抛物线"],
    ["vector_2d","平面向量","加减、数乘、投影与夹角"],
    ["triangle_2d","三角形与解三角形","三边、三角、SSA 多解"],
    ["space_3d","空间直角坐标系","空间向量、平面与立体几何"],
    ["complex_plane","复平面","复数、运算与旋转"],
    ["venn_logic","集合韦恩图","成员、交并差补与全集"],
    ["number_line","数轴与不等式","开闭区间、集合与解集"]
  ];
  const state={loaded:false,loading:null,data:null,family:"function_2d",preset:null,
    values:{},scene:{},view2d:{zoom:1},view3d:{yaw:38,pitch:36,zoom:1},result:null};
  const make=(parent,tag,cls,txt)=>{
    const e=document.createElement(tag);
    if(cls)e.className=cls;
    if(txt!==undefined)e.textContent=String(txt);
    parent.appendChild(e);return e;
  };
  const fixed=x=>Number.isFinite(x)?x.toFixed(2):"未定义";
  function selectedPreset(){
    return state.data?.presets?.find(p=>p.id===state.preset)||null;
  }
  function activeView(){return $("lab")?.classList.contains("active")}
  function displayError(message){
    const p=$("labMetrics");if(p){p.replaceChildren();make(p,"p","lab-error",message)}
  }
  async function load(){
    if(state.loaded)return;
    if(state.loading)return state.loading;
    state.loading=fetch("/api/math-lab/catalog")
      .then(r=>{if(!r.ok)throw Error("课程工具目录读取失败");return r.json()})
      .then(data=>{
        if(!data.presets?.length||!data.topics?.length||data.no_llm_api!==true)
          throw Error("收到的课程工具目录不符合离线模拟格式");
        state.loaded=true;state.data=data;
        const counts=data.counts;
        $("labSummary").textContent=
          "课程知识清单 "+counts.total_concepts+" 条  ·  动态演示场景 "+counts.scene_presets+
          " 个  ·  已具备基础交互的知识映射 "+counts.interactive_foundations+
          " 条（仅基础，非完整教学）";
        $("labStandardNote").replaceChildren();
        make($("labStandardNote"),"span","","工程覆盖清单参考《"+data.reference+"》；不是逐条官方课标原文，也不代表各省高考命题范围。");
        const a=make($("labStandardNote"),"a","","查看课程标准原始资料");
        a.href=data.reference_url;a.target="_blank";a.rel="noopener noreferrer";
        renderFamilies();renderCurriculum();
        selectFamily(state.family);
      })
      .catch(e=>{state.loading=null;displayError(e.message);throw e});
    return state.loading;
  }
  function renderFamilies(){
    const place=$("labFamilies");place.replaceChildren();
    for(const [id,name,desc] of TEAMS){
      const b=make(place,"button","lab-family-tab","");
      b.dataset.family=id;b.type="button";b.setAttribute("role","tab");
      make(b,"strong","",name);make(b,"small","",desc);
      b.onclick=()=>selectFamily(id);
    }
  }
  function selectFamily(family,desired){
    state.family=family;
    $("labFamilies").querySelectorAll(".lab-family-tab").forEach(button=>{
      const yes=button.dataset.family===family;
      button.classList.toggle("active",yes);button.setAttribute("aria-selected",String(yes));
    });
    const list=state.data?.presets?.filter(p=>p.tool===family)||[];
    if(!list.length){displayError("这一类动态实验仍在建设中。");return}
    const select=$("labPreset");select.replaceChildren();
    for(const preset of list){
      const option=make(select,"option","",preset.title);option.value=preset.id;
    }
    const pick=list.find(p=>p.id===desired)||list[0];
    select.value=pick.id;
    selectPreset(pick.id);
  }
  function selectPreset(id){
    const preset=state.data?.presets?.find(p=>p.id===id);
    if(!preset)return;
    state.family=preset.tool;state.preset=id;state.scene={assist:false};
    $("labExtraControls").replaceChildren();$("labExtraControls").hidden=true;
    $("labAlternativeView").replaceChildren();$("labAlternativeView").hidden=true;
    const extra=preset.assist_default===false;
    $("labAssistControl").hidden=!extra;$("labAssistToggle").checked=false;
    $("labAssistLabel").textContent=["complex_plane","venn_logic","number_line"].includes(preset.tool)?"显示运算结果 / 解集（先猜想，再核对）":preset.id.startsWith("derivative-")?"显示解析切线（先猜想，再核对）":preset.id.startsWith("3d-section-")?"显示切平面与法向量（可选）":"显示辅助图形（自主核对）";
    state.values=Object.fromEntries(preset.params.map(p=>[p.key,p.value]));
    state.view2d={zoom:1};state.view3d={yaw:38,pitch:36,zoom:1};
    $("labPreset").value=id;$("lab2dZoom").value="1";
    $("labYaw").value="38";$("labPitch").value="36";$("lab3dZoom").value="1";
    $("labTitle").textContent=preset.title;
    $("labDescription").textContent=preset.description;
    $("labSceneHint").textContent="这是一份可调的数学模型。请先预测参数变化的效果，再拖动、旋转或比较数值。";
    $("lab2dControls").hidden=preset.tool==="space_3d"||preset.tool==="triangle_2d"||preset.id==="unit-circle"||["venn_logic","number_line"].includes(preset.tool);
    $("lab3dControls").hidden=preset.tool!=="space_3d";
    const params=$("labParameterControls");params.replaceChildren();
    if(!preset.params.length){
      make(params,"p","lab-param-empty","自由拖动图中各个顶点，观察角度、边长与面积如何变化。");
    }
    for(const p of preset.params){
      const block=make(params,"div","lab-param","");
      const label=make(block,"label","lab-param-header","");
      label.setAttribute("for","labParam_"+p.key);
      make(label,"span","",p.label);
      const choiceLabel=value=>p.options?.find(o=>o.value===value)?.label??fixed(value);
      const val=make(label,"output","lab-param-value",choiceLabel(p.value));
      const input=make(block,p.options?"select":"input",p.options?"lab-param-choice":"lab-param-range","");
      input.id="labParam_"+p.key;input.setAttribute("aria-label",p.label);
      if(p.options){
        for(const option of p.options){const item=make(input,"option","",option.label);item.value=String(option.value)}
      }else{
        input.type="range";input.min=p.min;input.max=p.max;input.step=p.step;
        const row=make(block,"div","lab-param-bounds","");
        make(row,"span","",String(p.min));make(row,"span","",String(p.max));
      }
      input.value=String(p.value);
      input.addEventListener(p.options?"change":"input",()=>{
        const value=Number(input.value);
        if(!Number.isFinite(value)||p.options&&!p.options.some(o=>o.value===value))return;
        state.values[p.key]=value;val.textContent=choiceLabel(value);draw();
      });
    }
    draw();
  }
  async function formula(latex){
    if(state.formulaSource===latex)return;
    state.formulaSource=latex;
    const box=$("labFormula"),ticket=(state.formulaTicket||0)+1;
    state.formulaTicket=ticket;box.dataset.latex=latex||"";box.setAttribute("aria-busy","true");
    state.formulaQueue=(state.formulaQueue||Promise.resolve()).catch(()=>{}).then(async()=>{
      if(ticket!==state.formulaTicket)return;
      if(root.MathJax?.typesetClear)root.MathJax.typesetClear([box]);
      box.replaceChildren();box.textContent=latex?"\\("+latex+"\\)":"";
      try{await root.MathJax?.typesetPromise?.([box])}
      catch(e){if(ticket===state.formulaTicket)box.textContent=latex||""}
      if(ticket===state.formulaTicket)box.setAttribute("aria-busy","false");
    });
    return state.formulaQueue;
  }
  function metrics(items){
    const box=$("labMetrics");box.replaceChildren();
    for(const value of items||[]){
      make(box,"span","lab-metric",String(value));
    }
    if(!items?.length)make(box,"span","lab-metric","请移动鼠标或改变参数观察数学结构。");
  }
  function draw(){
    const preset=selectedPreset(),node=$("labPlot");if(!preset||!node)return;
    try{
      // Explicitly clear prior scene handlers; SVG root is reused across families.
      node.onpointerdown=node.onpointermove=node.onpointerup=node.onpointercancel=null;node.style.cursor="";
      const scene=state.scene;
      scene.extraControls=$("labExtraControls");
      scene.onSceneChange=()=>{
        const id=scene.extraControls.contains(document.activeElement)?document.activeElement.id:null;
        draw();
        if(id)document.getElementById(id)?.focus({preventScroll:true});
      };
      scene.onParams=patch=>{
        // SVG children are replaced during drawing. Preserve a keyboard user's
        // logical handle without stealing focus from sliders or pointer users.
        const focusedHandle=node.contains(document.activeElement)?
          document.activeElement.getAttribute("data-handle"):null;
        for(const [key,value] of Object.entries(patch)){
          const spec=preset.params.find(v=>v.key===key);if(!spec||!Number.isFinite(value))continue;
          if(spec.options&&!spec.options.some(o=>o.value===value))continue;
          const bounded=Math.max(spec.min,Math.min(spec.max,value));
          const rounded=Number((spec.min+Math.round((bounded-spec.min)/spec.step)*spec.step).toFixed(10));
          state.values[key]=Math.max(spec.min,Math.min(spec.max,rounded));
          const slider=$("labParam_"+key);if(slider){slider.value=String(state.values[key]);slider.closest(".lab-param").querySelector("output").textContent=spec.options?.find(o=>o.value===state.values[key])?.label??fixed(state.values[key]);}
        }
        draw();
        if(focusedHandle){
          const replacement=Array.from(node.querySelectorAll("[data-handle]")).find(
            element=>element.getAttribute("data-handle")===focusedHandle);
          replacement?.focus({preventScroll:true});
        }
      };
      let result;
      if(root.MentorFoundations2D?.supports(preset.id)){
        result=root.MentorFoundations2D.draw(node,preset,state.values,state.view2d,scene);
        $("labCoordinateReadout").textContent=result.coordinateHint||"先观察输入，再主动显示结果。";
      }else if(root.MentorNumberLine?.supports(preset.id)){
        result=root.MentorNumberLine.draw(node,preset,state.values,state.view2d,scene);
        $("labCoordinateReadout").textContent=result.coordinateHint||"空心点不包含端点，实心点包含端点。";
      }else if(root.MentorLabExplorers?.supports(preset.id)){
        result=root.MentorLabExplorers.draw(node,preset,state.values,state.view2d,scene);
        $("labCoordinateReadout").textContent="先观察再开启辅助线；拖动点或参数滑块可同步探索。";
      }else if(preset.tool==="triangle_2d"){
        const scene=state.scene;
        scene.onUpdate=metrics;
        result=root.MentorLabTriangle.draw(node,preset,state.values,scene);
      }else if(preset.tool==="space_3d"){
        const scene=state.scene;
        scene.view=state.view3d;
        scene.onUpdate=(values)=>{
          metrics(values);
          $("labYaw").value=String(Math.round(scene.view.yaw));
          $("labPitch").value=String(Math.round(scene.view.pitch));
          $("labCoordinateReadout").textContent=
            "视角：水平 "+Math.round(scene.view.yaw)+"°，俯视 "+Math.round(scene.view.pitch)+"°，缩放 "+fixed(scene.view.zoom)+" 倍";
        };
        result=root.MentorLab3D.draw(node,preset,state.values,state.view3d,scene);
        $("labCoordinateReadout").textContent="拖拽旋转三维空间，或使用视角滑块；坐标系保持右手定向。";
      }else{
        result=root.MentorLab2D.draw(node,preset,state.values,state.view2d);
        $("labCoordinateReadout").textContent="移动鼠标查看二维坐标；改变参数观察函数或曲线形状。";
      }
      state.result=result;metrics(result.info);formula(result.latex||preset.latex);
    }catch(e){
      console.error("可视化重绘失败",e);
      displayError("当前场景暂不可用，请选择其他实验或重置参数。");
    }
  }
  function pointerCoordinates(e){
    if(state.family==="triangle_2d"||state.family==="space_3d")return;
    const rootSvg=$("labPlot"),result=state.result;
    if(!result?.toWorld)return;
    const matrix=rootSvg.getScreenCTM();if(!matrix)return;
    const point=rootSvg.createSVGPoint();point.x=e.clientX;point.y=e.clientY;
    const local=point.matrixTransform(matrix.inverse()),world=result.toWorld(local.x,local.y);
    const x=world[0],y=world[1],v=result.evaluate?.(x);
    if(result.pointerLabel){$("labCoordinateReadout").textContent=result.pointerLabel(x,y);return;}
    $("labCoordinateReadout").textContent=
     "坐标 (x,y) = ("+fixed(x)+", "+fixed(y)+")"+
     (Number.isFinite(v)?"；所选函数在 x 处的值 ≈ "+fixed(v):"");
  }
  function reset(){
    selectPreset(state.preset);
  }
  function renderCurriculum(){
    if(!state.data)return;
    const level=$("labLevel").value,status=$("labCoverage").value,
      q=$("labTopicSearch").value.trim().toLowerCase();
    const topics=state.data.topics.filter(t=>
      (level==="all"||t.level===level)&&
      (status==="all"||t.status===status)&&
      (t.concept+" "+t.unit+" "+t.theme+" "+t.recommended_tool).toLowerCase().includes(q));
    const place=$("labCurriculumList");place.replaceChildren();
    if(!topics.length){
      make(place,"p","lab-empty","没有匹配的知识点，可以调整筛选范围。");return;
    }
    const count=make(place,"div","lab-results-count",
      "显示 "+topics.length+" / "+state.data.topics.length+" 个知识点（工具支持范围不等于课程掌握）。");
    for(const topic of topics){
      const item=make(place,"article","lab-topic-item","");
      const body=make(item,"div","lab-topic-main","");
      make(body,"b","",topic.concept);
      make(body,"small","",topic.level+" / "+topic.theme+" / "+topic.unit);
      make(body,"small","lab-capability-limit",topic.capability_limits);
      const ready=topic.status==="INTERACTIVE_FOUNDATION";
      const badge=make(item,"span",ready?"lab-topic-tag":"lab-topic-tag planned",
          ready?"已有基础交互":"后续规划");
      badge.title=topic.capability;
      if(ready&&TEAMS.some(x=>x[0]===topic.recommended_tool)){
        const b=make(item,"button","lab-topic-button","打开对应实验");
        b.type="button";b.onclick=()=>{
          selectFamily(topic.recommended_tool,topic.available_presets?.[0]);
          $("labPlotBox").scrollIntoView({block:"center",behavior:"smooth"});
        };
      }
    }
  }
  function suggestForProblem(problemId){
    if(!state.loaded)return;
    const known={
      "ellipse-tangent":"conic-ellipse",
      "hyperbola-tangent":"conic-hyperbola",
      "parabola-tangent":"conic-parabola",
      "triangle-ssa":"tri-ssa",
      "triangle-sas":"tri-free",
      "triangle-sss":"tri-free",
      "derivative-extrema":"derivative-cubic",
      "log-domain":"fn-log",
      "vector-orthogonality":"vec2d-projection"
    };
    const id=known[problemId];
    const preset=state.data.presets.find(p=>p.id===id);
    if(preset)selectFamily(preset.tool,preset.id);
    else if(problemId==="distance-ratio"){
      // Do not reveal a hidden locus type just because the student opened the lab.
      selectFamily("conic_2d","conic-line");
    }
  }
  async function activate(){
    try{await load()}catch(e){displayError(e.message)}
  }
  function init(){
    $("labPreset")?.addEventListener("change",e=>selectPreset(e.target.value));
    $("labReset")?.addEventListener("click",reset);
    $("labAssistToggle")?.addEventListener("change",e=>{state.scene.assist=e.target.checked;draw()});
    for(const id of ["labLevel","labCoverage","labTopicSearch"]){
      $(id)?.addEventListener(id==="labTopicSearch"?"input":"change",renderCurriculum);
    }
    $("lab2dZoom")?.addEventListener("input",e=>{
      state.view2d.zoom=Number(e.target.value);draw();
    });
    for(const [id,key] of [["labYaw","yaw"],["labPitch","pitch"],["lab3dZoom","zoom"]]){
      $(id)?.addEventListener("input",e=>{
        state.view3d[key]=Number(e.target.value);draw();
      });
    }
    $("labPlot")?.addEventListener("pointermove",pointerCoordinates);
  }
  document.addEventListener("DOMContentLoaded",init);
  root.mentorMathLab={activate,suggestForProblem,selectFamily,
    getState:()=>({family:state.family,preset:state.preset,values:{...state.values},
                   view3d:{...state.view3d}})};
})(window);
