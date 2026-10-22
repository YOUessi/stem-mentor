# v0.16 专用数学 OCR 与冻结基准

本增量位于独立开发分支 feat/v016-math-ocr-evaluation，基于 v0.15。Mac Apple Vision 负责前置文字识别，疑似公式区域经用户明确授权后转发至 Tang 专用 PP-FormulaNet_plus-M GPU 服务；图表云 VLM 单独授权。识别结果均保持待人工确认，不能视为数学证明。当前 Apple Vision 运行于 Mac Web 服务端，并非 iPad 原生端侧 OCR。

## 冻结数据（只适合合成评测）

evaluations/formula_v016/frozen_manifest.json 包含 22 个项目自编合成数学表达式任务，18 个不同公式另附 4 个低对比度/模糊/轻微旋转样本。覆盖代数、分式、根式、求根公式、三角、对数、导数、积分、极限、求和、组合、区间、数列、向量、圆锥曲线和概率。**这些不是正式中高考真题或真实学生手写照片。**

每例有 ID、所属题型、合成 LaTeX 真值及渲染方式；原始 manifest SHA256 在 backend/tests/test_formula_metrics_v016.py 中冻结，改动须新版本。用 Matplotlib/Pillow 生成图片和含每张 SHA256 的 index（图片不提交）；benchmark 在运行前校验全部 hash。

生成：python3 evaluations/formula_v016/generate.py --out evaluations/formula_v016/generated

评测：.venv/bin/python evaluations/formula_v016/benchmark.py --images evaluations/formula_v016/generated --out evaluations/formula_v016/local_results.json --device gpu:0

统计 raw exact match、仅字体排版归一化 exact match、LaTeX 字符错误率、失败数、推理 P50/P95、各类公式/视觉扰动分组。归一化不等于数学等价。失败必须计入总分母，模型没跑完则不得报告整体指标。首次模型加载时延单独记录。后续必须补充许可明确、人工双标的真实试卷/手写图片集，才能讨论真实场景准确率。

## Tang 模型和部署

Tang 使用隔离目录 ~/projects/stem-mentor-formula-v016 和独立 Python 3.10 .venv，不碰全局环境。驱动 580 兼容官方 cu126 Paddle wheel。GPU Paddle 3.3.0；公式模型 PP-FormulaNet_plus-M。模型复用 Paddle 缓存，不将权重复制到项目目录。官方 API 为 FormulaRecognition(model_name="PP-FormulaNet_plus-M")，result.json.res.rec_formula 为模型 LaTeX 输出。

安装依赖请参阅 scripts/tang_formula_install_v016.sh。镜像安装需确保 Pillow、PaddleOCR 3.3.2、FastAPI/Uvicorn 等在同一个隔离环境。GPU 服务序列化单模型访问并要求 token，监听仅 127.0.0.1:18931。需要运行时占用 GPU；其他模型训练繁忙时不要同时运行 OCR。

启动：
    cd ~/projects/stem-mentor-formula-v016
    set -a; source .formula.env; set +a
    .venv/bin/python -m uvicorn backend.services.formula_worker:app --host 127.0.0.1 --port 18931

Mac 本地入口：http://127.0.0.1:18916/vision
    cd ~/Documents/文件/stem-mentor-vision-v016
    bash scripts/build_vision_ocr.sh
    set -a; source ~/.config/stem-mentor/v016-formula.env; set +a
    cd backend
    PYTHONPATH=. ../.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 18916

API /api/vision/status 只返回是否配置，不泄露 token。鉴权、非法图片处理及采样测试在 backend/tests 运行。

## 安全连接

当前两台机器经同一 LAN。Tang 后端仅监听 127.0.0.1，不将 HTTP 暴露公网。Mac 通过 SSH 本地端口转发 127.0.0.1:18931 访问；独立密钥 ~/.ssh/stem_mentor_formula_v016 的 authorized_keys 被限制为来源 192.168.110.85、强制 /bin/false 且只能向 Tang 的 127.0.0.1:18931 转发。Mac IP 变化后需要重新授权；撤销授权只需删除 Tang ~/.ssh/authorized_keys 中 stem-formula-v016-port-forward-only 条目。密钥不允许执行远程命令，不能转发其他端口。

Mac 机密保存在 ~/.config/stem-mentor/v016-formula.env；Tang 保存在服务目录 .formula.env，权限 600，严禁提交 Git。worker 无 token 返回 503，token 错误返回 401，坏图返回 422；不保存请求图像。浏览器需明确勾选公式外发许可，仅路由出来的公式候选区域经隧道发送到 Tang。VLM 未配置时不得将其算作已运行。

## 重要边界与改进

第一阶段识别仍可能把字母 x 混为 ×、遗漏复杂上标。公式服务只处理路由选中的区域，不能自行补全题目未知条件。还需后续冻结真实评测集、合法版权/隐私治理、手写真机测试、真正 iPad 端内本地 OCR 与真实 VLM 图表正确性测试；这些均不应被当前合成测试通过所替代。

参考：PaddleOCR 官方 FormulaRecognition 文档 https://www.paddleocr.ai/main/en/version3.x/module_usage/formula_recognition.html 及官方 PaddlePaddle GPU 安装文档 https://github.com/PaddlePaddle/docs/blob/develop/docs/install/pip/linux-pip_en.md

## v0.16 后续集成修复（Mac 端）

更多实际 GPU 模型运行结果与误差案例记录在 evaluations/formula_v016/RESULTS_20261023.md：22/22 条产生非空结果，严格字符串 exact match 6/22，轻度排版归一化 7/22，LaTeX 字符错误率 0.296；冷模型加载约 5.62 秒，纯模型单样本 P50 约 85.2ms、P95 约 195.38ms。**这些是合成单公式的基准，不是整题准确率。**

本轮只在 Mac 工作区修复了公式区域聚焦：使用 Apple Vision substring boundingBox，局部候选仅留 0.4% 的水平边距，识别页面会展示原始区域小图方便校对；没有明确数学符号的低置信度纯文本不会错误路由到公式模型。模型失败后同请求中的其它候选使用熔断降级，减少无效联网，并保留手工编辑与数学验证状态 false。页面状态接口单独展示配置和在线探测结果；默认只对本机 SSH 隧道的 loopback 健康端点发 GET，不向任意远程 URL 做探测，不发送图片。Tang 仅作独立模型推理，代码版本管理与所有实现均在 Mac。

可复验：在 Mac 运行 bash scripts/build_vision_ocr.sh、cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest -q，浏览器运行 tests/browser/test_vision_mixed_v016.py，测试合成混排题的裁剪、人工修订与创建 iPad 学习会话。模型因离线未实际回复时，不得把公式 OCR 视作完成；系统应安全提示、人工接管。

## Mac 端实测复验入口

当 Tang 上的 GPU OCR 服务已启动且本机 SSH 隧道连通，在 Mac worktree 执行：

    .venv/bin/python scripts/check_formula_e2e_v016.py --url http://127.0.0.1:18916

脚本用两张完全合成的题干与公式混排图测试 Mac Apple Vision、substring 区域坐标、服务授权、Tang 公式 OCR、返回 JSON 字段及人工复核标志。失败时明确报错，不冒充成功。结果只写入 Mac 的 gitignored artifacts 目录，不上传私有图片或 token。

实际观察：ASCII 幂符号可能被模型误识别为导数撇号；使用真正的印刷上标时，专用数学 OCR 能纠正普通 Apple Vision 漏掉的上标（这两个样例的详细结果见 RESULTS_20261023.md）。Tang 是可选推理后端，项目源码仍只在 Mac 开发。
