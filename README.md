# STEM Mentor — 个人化理科思维培优系统

## v0.12 开发中：概率、计数与统计（2026-10-19）

v0.12 的独立 Mac 开发目录 ~/Documents/文件/stem-mentor-v012 中已有9个固定场景：
排列/组合、两阶段概率树、二项/超几何分布、正态密度与区间概率、固定种子伯努利频率、
样本均值/中位数/众数/方差、合成散点回归。
数学内核运行在本地浏览器和Node，仍保留第一版绿色界面、全部既有教学功能，不使用 Tang 或 LLM API。

注意：这是独立开发分支，尚未发布到 main 正式网页。当前71个场景/11工具族属于开发状态，
并非已经全部通过远端CI或教师审核。

- [数学设计与边界](docs/design/PROBABILITY_STATISTICS_V012.md)
- [日期开发日志](docs/logs/2026-10-19-v012.md)
- [开发计划](docs/planning/2026-10-19-v012-plan.md)


## v0.11b：闭区间函数最值与端点比较（2026-10-19）

**延续原绿色护眼学习工作台。** 在高中数学实验室的函数类别中新增5个受控场景：二次、三次、绝对值、正弦、对数的闭区间最值。

- 在绿色阴影区间内绘图，标注端点L/R；学生先写猜想，再逐级寻求提示，主动开启候选点与极值比较。
- 数学内核显式比较区间端点、驻点、不可导点，处理参数退化、相同极值在多个位置取得、常值函数和对数定义域限制。
- 现有57场景完整保留；本阶段合计62场景、9类工具。课程工程知识条目113，其中63条有基础场景映射、50条规划。**这些不是已完成的全套高考教学。**
- Python/Node与Mac Chrome按真实测试运行，记录见 [v0.11b 数学实现](docs/design/CLOSED_EXTREMA_V011B.md) 和 [日期日志](docs/logs/2026-10-19-v011b.md)。
- 当前仍不接模型API、不使用Tang、不调用付费服务，不存真实学生数据。



## v0.11：有限数列、递推与启发式思考（2026-10-19）

**绿色学习工作台不变，仅新增离线数学实验室类别「数列与递推」。**
- 八种可调场景：等差、等比、q=1/0/−1 边界、一阶与两项递推、部分和、有限项增长比较、递推平衡点。
- 第 n 项和部分和均从 n=1 计数；对公比接近 1 使用稳定的逐项累加，杜绝在 q=1 时错误套用含 1−q 分母的式子。有限数列图不自动证明无穷极限。
- 默认仅观察前五项；学生主动展开结果时才看到后续项、有限部分和图与表格。
- 学生可填写「我的猜想」、选择思考阶段并请求逐层启发；当前辅导模式用于透明规则决策。自助观察不增加成绩/掌握度，不把规则提示称为真正大模型理解。
- 项目累计 **57 个可视化场景、9 类工具、113 条课程工程知识**；其中63条链接到基本探索工具，50条待专项开发，所有材料仍待教师审核。
- 仅 MacBook Air `~/Documents/文件/stem-mentor`，无 LLM API，不使用 Tang。

[数列桌面实测截图](docs/assets/v011-sequence-arithmetic.jpg) · [数列递推截图](docs/assets/v011-sequence-recurrence.jpg) · [手机端截图](docs/assets/v011-sequence-mobile.jpg)。

设计与边界：[v0.11 数列学习机制](docs/design/SEQUENCES_V011.md)；[执行与测试日志](docs/logs/2026-10-19-v011.md)；[实施计划](docs/planning/2026-10-19-v011-plan.md)。



## v0.10：复平面、韦恩图、实区间与不等式

**已发布：PR #8；Mac 本地服务版本0.10.0，原学习数据库保留。**

沿第一版绿色/米白界面，在MacBook Air继续实现，无新增网络依赖、无LLM API。新增10个受控场景，现49场景、8个工具族。113条工程知识清单中59条绑定具体基础实验、54条仍规划；不是完整高中授课实现。

- 复平面：复数点、模/主辐角/共轭、四则运算、旋转与缩放；除零和零复数辐角明确未定义。
- 有限集合：成员可编辑、真实交并差补、相对全集U与德摩根关系；手机显示完整双圆及四区域文字。
- 数轴：开闭端点、射线、单点、空集、交并差及相对整个实数集的补集；端点可拖动/连续键盘操作。
- 不等式：一次、二次、绝对值的数值参数解集；重根和退化情况单独处理。小数系数判别式符号按十进制输入精确判断，根仍是近似显示。

先形成猜想，再主动勾选显示结果；实验不写成绩或已掌握状态。复数/区间选择使用明确下拉框，不要求记住无意义的数字选项。

[设计与数学边界](docs/design/FOUNDATION_EXPLORERS_V010.md) · [执行计划](docs/planning/2026-10-19-v010-execution-plan.md) · [日期日志](docs/logs/2026-10-19-v010.md) · [测试结果与原始证据](evaluations/results/2026-10-19-v010.json)

完整并发验收：`bash scripts/check_v010.sh --with-browser`。数学Node、Python回归和隔离Chrome为三个独立进程，不是独立AI子Agent。新旧场景同时回归，不将“计算内核完成”误报为“页面已发布”。


## 历史迭代：v0.9 数学探究工具（2026-10-19）

沿第一版绿色/米白界面连续开发，只在 MacBook Air `~/Documents/文件/stem-mentor` 运行，不调用 LLM API。

新增 **10 个场景**：平面向量加减/数乘与投影、单位圆联动、四种函数的动态差商/切线、长方体/四棱锥/球的真实平面截面。现共 39 个预设、5 类工具。辅助线与解析切线由学生主动选择，操作本身不被记作解题正确或独立掌握。

113 条工程知识清单中，50 条有具体场景证据，63 条仍规划中；含部分实现的条目同时显示未完成的能力，不把一般坐标画板说成覆盖了二面角或线面角。

- [持续开发任务看板](docs/planning/CONTINUOUS_DELIVERY.md)
- [本轮执行计划及验收标准](docs/planning/2026-10-18-v09-execution-plan.md)
- [数学原理、交互边界与实现](docs/design/GUIDED_EXPLORERS_V09.md)
- [按日期的实施与问题修复记录](docs/logs/2026-10-18-v09.md)
- [本轮验收统计与原始日志](evaluations/results/2026-10-19-v09.json)

并发验收：`bash scripts/check_v09.sh --with-browser`。Node、Python、Chrome 使用独立测试进程和日志；此机制不是多个独立 AI Agent，也不代表对话结束后自动无限运行。当前没有真实学生学习效果数据。


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


## 历史记录：v0.6 Study Studio 前端升级（2026-10-15，已撤回）

以下为已经撤回的 v0.6 设计历史，并非当前生效界面。当前界面为绿色 v0.5，详见文末恢复记录。原 v0.6 设计曾包括：
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


## 界面恢复（2026-10-15）

根据使用反馈，恢复到 v0.6 改版**之前**的 v0.5 绿色护眼学习工作台（`apps/web/index.html`、`styles.css`、`app.js` 均以绿色版本提交 `d5cd3ce` 为基准）。保留最新的数学推理、教学策略、检索、历史学习和考试微考点功能。

此前 v0.6 深色导航和蓝紫色界面**不再启用**；相关视觉研究和截图仅作为历史开发记录，未来不默认恢复。详细变更参见 [2026-10-15 绿色界面恢复日志](docs/logs/2026-10-15-green-ui-restore.md)。

本地启动方式：`bash scripts/mac_start.sh`；自动化验收：`bash scripts/mac_check.sh && bash scripts/mac_browser_check.sh`。


## v0.7 绿色数学学习体验（2026-10-17）

**保留用户指定的第一版绿色护眼设计、白色侧栏和原有双栏工作台**，没有恢复 v0.6 的蓝紫色新版外观。

本轮增加：
- 15 道受控数学题的已知公式 SVG 排版；本地 MathJax 3.2.2，不依赖在线 CDN。
- 学生草稿中有限 LaTeX 命令的可选实时预览，预览与数学验证分离。
- 三类受控 SVG 几何探索：定比轨迹、两焦点距离和、椭圆上的动点；自由拖动、实时数值、主动条件探索与观察路径。
- 更直观的思维图：已知条件、问题目标、正推、卡点、逆向分析；学生可以手动连接两个真实节点，并将其保存为**未验证猜想**。
- 移动端提供文字形式的节点列表与可操作的联系入口；未提交草稿按模拟学生与会话隔离缓存。

所有公式为题目可见内容，未知轨迹的完整形状不会默认绘出；题目与学生推导正确性不因此自动得到证明。

Mac 本地验证命令：bash scripts/mac_check.sh && bash scripts/mac_browser_check.sh。
详细设计见 docs/design/LEARNING_EXPERIENCE_V07.md；研发日志见 docs/logs/2026-10-17-learning-tools.md。

当前仍未启用 LLM API，知识和题目库规模为 15 道受控题与项目自编待审资料，非通用数学解题器。严禁向公开仓库上传真实学生个人数据。


## v0.8：面向整个高中数学的动态实验平台（2026-10-18）

严格保留第一版绿色护眼学习工作台；左侧导航新增“高中数学实验室”，也可从题目处自主进入。不使用模型 API、不调用 Tang。

- 知识点规划：113 条自编工程知识条目（必修、选择性必修、选修拓展），记录关联的数学工具和开发状态；这不是 113 条都已完成。
- 交互工具：函数与二维坐标（12 场景）、直线圆与圆锥曲线（6 场景）、三角形（3 场景）、XYZ 三维坐标与空间几何（8 场景）。
- 功能：参数滑块、数值探针、焦点/准线/渐近线、可拖动三角形、SSA 多解情形、三维旋转/俯视角/缩放、空间点投影/向量/平面/棱柱/球柱锥。
- API：GET /api/math-lab/catalog，数据分别存储在 curriculum/highschool_math/curriculum_map.json 与 visual_presets.json。
- 规划与已支持状态明确区分；所有内容标记项目自编、教师未正式审核。课标来源由课程资料说明，而不是虚构官方逐条考纲。

详见 docs/design/HIGH_SCHOOL_MATH_VISUAL_V08.md 及 docs/logs/2026-10-18-math-lab-v08.md。

验收：

    bash scripts/mac_check.sh
    bash scripts/mac_browser_check.sh

### 下一阶段
依次补充平面向量、数轴/集合韦恩图、复平面、空间截面、数列/动态导数、概率统计与计数原理；最终需教师校验课程内容并开展真实学生无提示迁移评测。现在还不是通用数学证明器，也未接入真实学生数据。
