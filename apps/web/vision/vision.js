"use strict";
/* Photo -> conservative structured draft -> explicit confirmation -> simulation session.
 * No image is stored in the student database; all math remains unverified.
 */
(function () {
  const $ = (id) => document.getElementById(id);
  const state = { previewURL: null, draft: null, confirmedProblem: null, busy: false };
  const labels = {
    ready: "已运行", not_installed: "未安装", not_configured: "未配置",
    skipped_no_consent: "未授权，不调用", skipped_not_needed: "当前无需调用",
    not_needed: "没有检测到公式候选", failed: "运行失败",
    empty_result: "未识别出公式", invalid_region: "区域无效",
    skipped_service_unavailable: "服务不可用，已停止后续请求"
  };
  function status(message, error) {
    $("status").textContent = message;
    $("status").classList.toggle("error", Boolean(error));
  }
  function invalidate() {
    state.confirmedProblem = null;
    $("createPaper").disabled = true;
  }
  async function renderLatex(input, preview) {
    const value = input.value.trim();
    if (!value) { preview.textContent = "在上方输入 LaTeX 后显示预览"; return; }
    try {
      const mathjax = window.MathJax;
      if (!mathjax) { preview.textContent = "公式渲染器尚未加载"; return; }
      if (mathjax.startup && mathjax.startup.promise) await mathjax.startup.promise;
      if (!mathjax.tex2svgPromise) { preview.textContent = "公式渲染暂不可用"; return; }
      const rendered = await mathjax.tex2svgPromise(value, {display:true});
      if (input.value.trim() !== value) return;
      const math = rendered.querySelector("svg");
      if (math) preview.replaceChildren(math);
    } catch (_) {
      preview.textContent = "LaTeX 渲染失败，请检查语法。";
    }
  }
  function makeFormulaCrop(bbox) {
    if (!state.previewURL || !Array.isArray(bbox) || bbox.length !== 4) return null;
    const canvas = document.createElement("canvas");
    canvas.className = "formula-crop";
    canvas.setAttribute("role", "img");
    canvas.setAttribute("aria-label", "原图中对应的公式候选区域，仅在浏览器显示");
    const url = state.previewURL;
    const image = new Image();
    image.onload = function () {
      if (url !== state.previewURL) return;
      const [x, y, w, h] = bbox.map(Number);
      if (![x,y,w,h].every(Number.isFinite) || w <= 0 || h <= 0) return;
      const iw = image.naturalWidth, ih = image.naturalHeight;
      const left = Math.max(0, (x - 0.006) * iw);
      const top = Math.max(0, (y - 0.015) * ih);
      const right = Math.min(iw, (x + w + 0.006) * iw);
      const bottom = Math.min(ih, (y + h + 0.015) * ih);
      const sw = right - left, sh = bottom - top;
      if (sw <= 0 || sh <= 0) return;
      const scale = Math.min(1, 680 / sw);
      canvas.width = Math.max(1, Math.round(sw * scale));
      canvas.height = Math.max(1, Math.round(sh * scale));
      canvas.getContext("2d").drawImage(image, left, top, sw, sh,
                                        0, 0, canvas.width, canvas.height);
    };
    image.src = url;
    return canvas;
  }
  function editor(value, hint, bbox) {
    const box = document.createElement("div");
    box.className = "formula-card";
    const label = document.createElement("small");
    label.textContent = hint || "人工添加的公式（请核对 LaTeX）";
    const input = document.createElement("textarea");
    input.className = "formula-input";
    input.rows = 2;
    input.maxLength = 800;
    input.value = value || "";
    input.placeholder = "例如：\\frac{x^2+1}{2}";
    input.setAttribute("aria-label", "公式 LaTeX 编辑器");
    const preview = document.createElement("div");
    preview.className = "latex-preview";
    preview.setAttribute("aria-label", "公式渲染预览");
    input.addEventListener("input", function () {
      invalidate();
      renderLatex(input, preview);
    });
    const original = makeFormulaCrop(bbox);
    if (original) box.append(label, original, input, preview);
    else box.append(label, input, preview);
    renderLatex(input, preview);
    return box;
  }
  function addExpression(value, hint, bbox) {
    if ($("formulas").querySelectorAll("textarea").length >= 12) {
      status("最多添加 12 条公式，可将其余公式并入题干。", true); return;
    }
    if (!$("formulas").querySelector(".formula-card")) $("formulas").replaceChildren();
    $("formulas").appendChild(editor(value, hint, bbox));
    invalidate();
  }
  function routeResult(data) {
    const root = $("routeInfo");
    root.replaceChildren();
    const info = data.routing || {};
    const rows = [
      "端侧/本地文字 OCR：" + (labels[info.local_ocr] || info.local_ocr || "未知"),
      "疑似数学公式：" + String(info.formula_candidates || 0) + " 处，其中 " +
        String(info.focused_formula_regions || 0) + " 处已精确定位",
      "数学 OCR 路由：" + Object.entries(info.formula_ocr || {})
        .map(function (entry) { return (labels[entry[0]] || entry[0]) + " × " + entry[1]; }).join("，"),
      "视觉图形复核：" + (info.visual_review_recommended ? "建议检查" : "暂未要求"),
      "云端 VLM：" + (labels[info.vlm] || info.vlm || "未知"),
    ];
    for (const message of rows) {
      const line = document.createElement("p");
      line.textContent = message;
      root.appendChild(line);
    }
    if ((data.uncertain_fields || []).length) {
      const warning = document.createElement("p");
      warning.textContent = "待复核：" + data.uncertain_fields.join(" · ");
      root.appendChild(warning);
    }
  }
  function diagramResult(diagram) {
    const root = $("diagramInfo");
    const relations = diagram && Array.isArray(diagram.relations) ? diagram.relations : [];
    root.hidden = relations.length === 0;
    root.replaceChildren();
    if (!relations.length) return;
    const title = document.createElement("strong");
    title.textContent = "视觉候选关系（仅观察，绝非已知条件）";
    root.appendChild(title);
    for (const item of relations) {
      const row = document.createElement("p");
      row.textContent = (item.objects || []).join(" / ") + " · " +
        (item.type || "unknown") + "：" + (item.explanation || "待人工确认");
      root.appendChild(row);
    }
  }
  async function jsonFetch(url, options) {
    const response = await fetch(url, options);
    let data = {};
    try { data = await response.json(); } catch (_) {}
    if (!response.ok) {
      const text = data.detail;
      throw new Error(typeof text === "string" ? text : "请求失败：" + response.status);
    }
    return data;
  }
  jsonFetch("/api/vision/status").then(function (cap) {
    const f = cap.formula_service;
    const formulaStatus = !f.configured ? "未配置" :
      f.reachable === false ? "已配置但当前离线（可人工校对）" :
      f.reachable === null ? "已配置，连接状态未核实" :
      f.model_loaded ? "GPU 模型在线（识别仍需授权）" :
      "服务在线，首次请求将加载模型";
    $("engineStatus").textContent =
      "识别引擎：" + (cap.local_ocr.ready ? "Mac Apple Vision 已就绪" : "Mac OCR 未就绪") +
      " · 数学 OCR：" + formulaStatus +
      " · 云端 VLM：" + (cap.vlm.configured ? "已配置（调用需授权）" : "未配置");
  }).catch(function () {
    $("engineStatus").textContent = "识别服务状态暂不可读取，请使用人工确认。";
  });
  $("questionImage").addEventListener("change", function () {
    if (state.previewURL) URL.revokeObjectURL(state.previewURL);
    const image = this.files && this.files[0];
    if (!image) { $("photoPreview").hidden = true; return; }
    state.previewURL = URL.createObjectURL(image);
    $("photoPreview").src = state.previewURL;
    $("photoPreview").hidden = false;
    invalidate();
  });
  $("questionStem").addEventListener("input", invalidate);
  $("addFormula").addEventListener("click", function () { addExpression("", "自行核对公式结构"); });
  $("recognizeForm").addEventListener("submit", async function (event) {
    event.preventDefault();
    const image = $("questionImage").files[0];
    if (!image) { status("请先上传图片。也可以直接在右侧填写题干。", true); return; }
    if (image.size > 8 * 1024 * 1024) {
      status("图片超过 8 MB，请裁剪后再试。", true); return;
    }
    $("runRecognition").disabled = true;
    invalidate();
    status("正在执行本地文字 OCR，并判断是否需要公式或图形服务…");
    try {
      const form = new FormData();
      form.append("file", image);
      form.append("diagram_present", $("hasDiagram").checked ? "true" : "false");
      form.append("allow_formula_service", $("sendFormula").checked ? "true" : "false");
      form.append("allow_cloud_vlm", $("allowVlm").checked ? "true" : "false");
      const draft = await jsonFetch("/api/vision/recognize", { method: "POST", body: form });
      state.draft = draft;
      $("questionStem").value = draft.stem || "";
      $("formulas").replaceChildren();
      if ((draft.expressions || []).length) {
        for (const exp of draft.expressions) {
          addExpression(exp.latex || "", "OCR 候选：" + (exp.raw_text || "未识别") +
            " · " + (exp.source === "formula_ocr" ? "专用模型候选，请校对" : "尚未获得专用 LaTeX"),
            exp.bbox);
        }
      } else {
        const empty = document.createElement("p");
        empty.className = "hint";
        empty.textContent = "没有得到可用的数学公式；可点击“添加公式”人工填写。";
        $("formulas").appendChild(empty);
      }
      routeResult(draft);
      diagramResult(draft.diagram);
      const failed = Object.keys(draft.routing?.formula_ocr || {}).some(
        key => ["failed", "not_configured", "skipped_service_unavailable"].includes(key));
      status((draft.stem ? "文字识别已生成草稿。" : "未自动获得题干，请人工录入。") +
        (failed ? " 远端公式识别当前不可用，请查看原图区域并人工补充。" : "") +
        " 请检查数字、上/下标及几何条件，再点击确认。");
    } catch (error) {
      status("识别未完成：" + error.message + "。仍可手动输入题目。", true);
    } finally {
      $("runRecognition").disabled = false;
    }
  });
  $("confirmQuestion").addEventListener("click", async function () {
    const stem = $("questionStem").value.trim();
    const expressions = Array.from($("formulas").querySelectorAll(".formula-input"))
      .map(function (el) { return el.value.trim(); })
      .filter(Boolean).map(function (latex) { return { latex: latex }; });
    if (!stem) {
      status("请先填写并核对题干。识别失败时可以直接手动输入。", true); return;
    }
    $("confirmQuestion").disabled = true;
    try {
      const confirmed = await jsonFetch("/api/vision/confirm", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stem: stem, expressions: expressions })
      });
      state.confirmedProblem = confirmed.custom_problem;
      $("createPaper").disabled = false;
      status("题目已由你确认，可以进入手写学习纸。注意：这不表示数学答案或图形条件已验证。");
    } catch (error) { status("确认失败：" + error.message, true); }
    finally { $("confirmQuestion").disabled = false; }
  });
  async function getSimulationStudent() {
    let id = localStorage.getItem("stem-demo-student");
    if (id) {
      try {
        await jsonFetch("/api/students/" + encodeURIComponent(id) + "/dashboard");
        return id;
      } catch (_) { localStorage.removeItem("stem-demo-student"); }
    }
    const created = await jsonFetch("/api/students", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ alias: "识题演示学生" })
    });
    localStorage.setItem("stem-demo-student", created.id);
    return created.id;
  }
  $("createPaper").addEventListener("click", async function () {
    if (!state.confirmedProblem) return;
    $("createPaper").disabled = true;
    try {
      const id = await getSimulationStudent();
      const session = await jsonFetch("/api/sessions", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_id: id,
          custom_problem: state.confirmedProblem, mode: "INDEPENDENT" })
      });
      localStorage.setItem("stem-demo-session", session.id);
      location.href = "/ipad/study?session=" + encodeURIComponent(session.id);
    } catch (error) {
      status("创建演示练习失败：" + error.message, true);
      $("createPaper").disabled = false;
    }
  });
})();
