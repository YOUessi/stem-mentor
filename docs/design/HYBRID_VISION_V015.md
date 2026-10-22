# v0.15 — 拍照识题（Mac OCR + 公式服务接口 + 按需 VLM）

## 交付状态与边界

本版本位于独立分支 feat/v015-hybrid-question-vision，基于 v0.14 的 iPad 绿色手写工作台开发，不替换正在运行的 main 服务。新增 /vision 页面，工作流程为：图片上传 → Mac Apple Vision 识别 → 公式行路由 → 按需专用公式服务/VLM → 题干与 LaTeX 人工修正（使用内置 MathJax 即时预览） → 明确确认 → 创建离线模拟学习会话 → 跳转 /ipad/study。原本的笔迹不会自动上传至 OCR。

**已实现**：真实的 macOS Apple Vision OCR 编译执行；图片标准化、大小限制与方向处理；JSON 区域证据、置信度和公式候选检测；可配置的 PP-FormulaNet_plus-M 公式微服务接口与独立 worker；按用户明确勾选调用的 OpenAI 兼容图像 VLM 接口；用户纠错界面、题目确认、新建独立自主挑战演示会话；回归测试与 Chrome 浏览器流程。

**未实现/未声称完成**：直接运行在 iPad/iPhone 内部的原生 Apple Vision 模块、自动几何证明、任意数学公式可靠解析、真实学生数据权限、正式的自建 GPU 公式服务上线、付费云 API 接入与模型精度评测。当前 Web/iPad 页面将照片发送到本项目 Mac FastAPI 后端，再调用 macOS Vision；这不是 iPad 真正的纯端侧 OCR。未来需要 iOS 原生 Vision 桥接或合适的浏览器 WASM OCR。

首版不得让 OCR/视觉模型的自然语言结果直接变成已经证明的数学条件。公式输出、VLM 图元以及人工确认的题干均标记 math_verified=false。视觉模型返回的关系只作为 observed_unverified，is_given=false，不能自动当作已知条件。不能把合成测试的通过视为教育效果验证。

## 启动（Mac）

在功能 worktree 中：

    cd ~/Documents/文件/stem-mentor-vision-v015
    ln -s ../stem-mentor/.venv .venv    # 若原工作目录的虚拟环境仍有效
    .venv/bin/python -m pip install -r backend/requirements.txt
    bash scripts/build_vision_ocr.sh
    cd backend
    PYTHONPATH=. ../.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 18915

访问 http://127.0.0.1:18915/vision 或从 /ipad 左侧导航进入拍照识题。上传真实题目会调用 Mac Apple Vision；未配置公式微服务则 LaTeX 待人工纠正，未配置 VLM 或未勾选云端许可时不会执行云端视觉调用。当前面向合成演示，不得上传真实未成年人个人数据。

## 公式服务（可选，独立 GPU 机器/容器）

需单独安装匹配硬件和 CUDA 的 PaddlePaddle 3.x 与 PaddleOCR 3.x。首次运行可能下载模型，不能在未装依赖时宣称完成推理。官方 Python 入口为：

    from paddleocr import FormulaRecognition
    model = FormulaRecognition(model_name="PP-FormulaNet_plus-M")

GPU 机器另起服务：

    export STEM_FORMULA_SERVICE_TOKEN="<server-only-token>"
    python -m uvicorn backend.services.formula_worker:app --host 127.0.0.1 --port 18931

Mac 端通过受保护的隧道/内网代理连接。配置如下（服务地址和令牌均不提交 Git）：

    export STEM_FORMULA_SERVICE_URL=http://127.0.0.1:18931/recognize
    export STEM_FORMULA_SERVICE_TOKEN="<same-token>"

浏览器需勾选「同意发送公式区域」，后端才会将疑似公式区域 PNG 以 image_base64 POST 到该服务。worker 返回 {"latex":"...", "model":"PP-FormulaNet_plus-M", "confidence":null}。worker 不保存图像，公式需人工复核。仅在受信内网或通过安全隧道访问此接口，不要无鉴权暴露公网。

官方 PP-FormulaNet 模块文档：https://www.paddleocr.ai/main/en/version3.x/module_usage/formula_recognition.html

## VLM（可选，按需调用）

    export STEM_VLM_API_URL="https://<provider>/v1/chat/completions"
    export STEM_VLM_API_KEY="<secret>"
    export STEM_VLM_MODEL="<image-capable-model>"

**只有**用户勾选云端 VLM 且题目被判断为涉及图表（或人工勾选「包含图表」）才调用。模型仅提出图元和候选关系，不进行求解、不写入已知条件。没有配置时显示 not_configured，不做虚构性结构填充。钥匙只存在服务端环境变量，图像默认不出本机。API endpoint 属管理员配置，不能接受用户输入的任意 URL。

## 接口与证据结构

- POST /api/vision/recognize — multipart(file, diagram_present=false, allow_formula_service=false, allow_cloud_vlm=false)，输入小于等于 8 MB，支持 PNG/JPEG/WebP。输出 stem、lines(text/confidence/bbox)、expressions(LaTeX 候选或空)、diagram(候选图形关系)、routing(实际服务状态)、uncertain_fields、confirmed=false、math_verified=false。
- POST /api/vision/confirm — 输入人工修订 stem 和可选 expressions；返回 confirmed=true 与 custom_problem（非数学证明）。
- POST /api/sessions — 复用既有自定义题目会话，交由学生自主挑战模式；不会自动调用 VLM 或答案校验。

坐标统一为图像左上角原点、归一化 bbox=[x,y,width,height]。模型计算结果和视觉观察是“待检验假设”，不同于题目明示事实。Apple Vision 不适合直接作为公式 LaTeX 权威来源，如手写上/下标、括号嵌套、字母 x 与乘号 × 的混淆；必须检查并允许人工修正。

### 隐私与安全

JPEG EXIF 元数据通过重编码被剥离；解码限制 2000 万像素、最大边 2200、8 MB 上限；OCR 临时图片仅在 TemporaryDirectory 生命周期存在；默认既不保存上传原图，也不将图片写入 SQLite/笔迹 IndexedDB；无同意则不调用外部公式/VLM 接口。后端测试证明请求未授权时不会调用外部 provider。正式部署仍需账户鉴权、反滥用限流、TLS、未成年人隐私/数据生命周期治理；没有这些之前仅允许合成演示。

## 回归与分阶段验收

    cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest -q tests/test_vision_v015.py
    cd .. && node --check apps/web/vision/vision.js
    STEM_MENTOR_URL=http://127.0.0.1:18915 .venv/bin/python tests/browser/test_vision_v015.py

验收需同时记录：Mac 本机合成 OCR 样例成功、识别中的失误、边界/无授权测试、Chrome 桌面与手机视窗的确认链路、旧教学与 iPad 笔迹功能回归。第二阶段才执行冻结中高考题集评估，统计题干关键条件准确率、LaTeX exact match、图形关系的 precision/recall、实际触发云端次数、端到端 P50/P95、延迟与平均成本；未测前不报告分数。
