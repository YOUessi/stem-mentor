# STEM Mentor — 个人化理科思维培优系统

> **当前交付：可运行的离线模拟 Web App。尚未接入任何 LLM API，不具备任意题目的通用数学智能。**

系统的目标不是让学生看完整答案，而是训练其独立审题、解题策略选择、正推与反推的切换、关键突破口发现及跨题迁移。学生自己的原始尝试被保存，模拟教师默认以最少必要提示回应。

## 本地启动

要求 Python 3.12+：

```bash
git clone https://github.com/YOUessi/stem-mentor.git
cd stem-mentor
python -m pip install -r backend/requirements.txt
cd backend
PYTHONPATH=. pytest -q
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

打开 http://127.0.0.1:8000 ，即可进入浏览器学习工作台。无需注册外部 API，也无需配置密钥。

也可在仓库根目录用 `docker compose up --build` 启动（Dockerfile 已提供，当前执行环境无 Docker，尚未实际验证容器构建）。

## 已实现的规则模拟功能

- 三种教学模式：逻辑分析、推理陪练、自主挑战；切换不丢会话、草稿与原始步骤。
- 十五道结构化数学情境题卡、二十六条项目自编方法/策略资料、十三个微知识点；自定义题仅作保守通用启发。
- 显式教学阶段：起步、正推、卡住、逆推、计算与发现桥梁；允许动态改变教学动作，不按完整解答顺序代做。
- SQLite 持久化学习会话、学生自己的历史解题经历、复习状态；只在真正存在历史记录且结构和方法相似时才引导旧题回忆。
- 手动微考点回忆、有限间隔调度，以及**题目结束后**的相关易漏考点推荐（不打断当前探索）。
- 方法库检索采用本地 FTS5/BM25 与人工标注的数学结构、适用条件过滤；不是在线语义推理。
- 条目级的思维探索轨迹、个人解题经历页面、数学方法页面、响应式移动端布局。
- SymPy 对有限、固定且经过人工审核的代数/几何示例进行验证；任意学生解题过程明确标记 `math_verified=false`。
- 学生自述完成仅存为 `SELF_REPORTED_NOT_VERIFIED`，不能当成正确、理解或掌握的证据。

## 测试

```bash
cd backend && PYTHONPATH=. pytest -q     # v0.5 共 85 项后端回归测试
cd .. && node --check apps/web/app.js     # 前端语法
```

另有真实 Chromium DOM 的交互测试，使用 FastAPI TestClient 代理浏览器请求以适应受限执行环境：

```bash
pip install playwright
# 本机另需 Chromium 浏览器；按需要设置 CHROMIUM_EXECUTABLE
python tests/browser/test_ui.py
```

已验证桌面与手机端交互，脚本默认将图片放在 `artifacts/browser/`（被 Git 忽略）。

## 文档

- [产品需求 PRD](docs/requirements/PRD.md)、[功能规格及验收](docs/requirements/FEATURE_SPEC.md)、[架构](docs/design/ARCHITECTURE.md)、[数据模型](docs/design/DATA_MODEL.md)
- [教学决策规范](docs/design/TUTOR_POLICY.md)、[需求讨论与设计记录](docs/decisions/CONVERSATION_DECISIONS.md)、[质量评测计划](docs/evaluation/TEST_PLAN.md)
- [开发计划](docs/planning/ROADMAP.md)、[隐私和内容安全](docs/security/PRIVACY.md)、[2026-10-15 工程日志](docs/logs/2026-10-15-implementation.md)

## 研发边界

本版不是接入 LLM 的完整教育 Agent。尚未实现真正的数学语义 RAG/模型训练、任意题求解、手写 OCR、正式认证和未成年人数据治理，也没有真实学生教育效果实验。仓库为 **public**，请勿提交真实学生记录、API 密钥或授权未明的教材资料。


## v0.4 结构化教学引擎（2026-10-15）

已新增题目正推/逆推/桥梁关系图、学生思考阶段自报、可审计的教学动作决策、本地 FTS5/BM25 + 数学结构门控检索（8 条项目自编待审核文档）、安全限制的 SymPy 代数等价检查。**仍是规则模拟，不使用模型 API；不是完整的通用数学 Agent。**

- [推理与检索设计](docs/design/REASONING_ENGINE_V04.md)
- [测试报告](docs/evaluation/SYNTHETIC_VALIDATION_20261015.md)
- [开发与修复日志](docs/logs/2026-10-15-v04.md)
- [教学决策场景及结果](evaluations/results/2026-10-15-policy-and-retrieval.json)

`cd backend && PYTHONPATH=. pytest -q && PYTHONPATH=. python evaluate_policy.py`。

## v0.5：MacBook Air 开发环境（2026-10-15）

项目唯一开发与测试设备为 **MacBook Air**，目录 `~/Documents/文件/stem-mentor`。Tang 上本项目工作目录与临时传输包已清理。

```bash
cd ~/Documents/文件/stem-mentor
"$HOME/miniforge3/bin/python" -m venv --system-site-packages .venv
.venv/bin/python -m pip install -r backend/requirements.txt
bash scripts/mac_check.sh
bash scripts/mac_start.sh
```

打开 http://127.0.0.1:8000 即可进行离线规则模拟（不是通用 LLM Agent，不消耗模型 API）。目前含 26 条待教师审核的数学知识资料、15 道受控题卡与相应思路图、13 个微考点，以及四项教师侧、仅限固定示例的代数校验证书。

**Mac 实测**：85 项后端测试通过；33/33 合成教学决策/基础检索测试通过；40/40 结构检索硬例通过。仅说明受控模拟场景通过，不证明真实学生的学习效果。详见 [Mac 迁移和验收日志](docs/logs/2026-10-15-mac-migration.md)。


## v0.6 Study Studio 前端升级（2026-10-15）

这一版仅改造学习工作台的视觉、布局和交互，不改变教学策略 API，也不接入模型：
- 蓝紫/青绿轻量教学视觉、响应式深色侧边导航、数学学习路径概念图、思维轨迹。
- 鼠标拖动或方向键调整左右分栏比例，保存到浏览器本地。
- Command/Ctrl + K 快捷跳转各页面与三种学习模式。
- 每个学习会话的学生未提交草稿可在刷新后恢复；点击导师空态的提示词可以直接进入草稿区。
- 尊重系统减少动效设置，所有内容从本地加载、没有外部 UI CDN。
- 原有 85 项后端测试和合成教学策略检查仍应通过；新增 Chrome 真浏览器适配与交互自动测试。

本机快速检查：bash scripts/mac_check.sh

实际浏览器交互（需要 Mac Google Chrome 和 Playwright）：

    .venv/bin/python -m pip install playwright
    bash scripts/mac_browser_check.sh

[视觉与组件选型调研](docs/design/STUDY_STUDIO_V06.md) · [开发与测试日志](docs/logs/2026-10-15-ui-v06.md)。

注意：参考过 shadcn/ui、Motion、React Bits 等组件库，但当前原生网页尚未集成它们。
