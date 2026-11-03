# STEM Mentor Batch05｜23 个语义缺口候选单元与数学旁路验收

日期：2026-11-03（MacBook Air）
基线：直接基于远端 Draft PR #30 HEAD 21cad7223b6216ac64c80d9d4d7d4b97bdfeac65（Git tree cb3861595613c8df4b2595868540f2adcbbf621c）；源文件来自 Mac 的隔离 Batch05 草案工作树。
发布验证目录：~/Documents/文件/stem-mentor-kb-batch05-release，分支 feat/kb-batch05-semantic-depth-release；原 Batch05 草案工作树保留未修改。
**原主仓的未提交改动与 Batch02 的尚未冻结候选完全没有修改。无 Tang、无外部模型 API、无真实学生数据。**

## 本批实际交付

1. 从 Batch04 已列出的 23 项编辑初审缺口出发，建立 23 篇具体知识候选（本批 6 theorem、13 concept、4 method），逐一核对唯一课程 ID。
   源头生成脚本：scripts/build_semantic_gap_batch05.py；可读 JSON：knowledge/deep/v1/semantic_gap_subskills_batch05.json。
2. 每篇具备详细数学定义或定理、前提/域、证明步骤或完整解释、一个明确反例或无效用法、两道教师例题、
   常见错误及修正追问、3 级提示、near/far 变式、来源许可和 REVIEW_PENDING。
3. 本批 46 道教师例题均新增独立的精确符号/离散概率/几何数值点验算；整篇证明仍未形式化验证。
   文件：backend/tests/test_deep_batch05_semantic_math.py；另加 backend/tests/test_deep_batch05_theorem_subclaims.py 针对双倍角恒等、投影正交、复数除法、线面位置、条件概率、切线一次近似分别提供狭义独立验证，**不代表全定理证明通过**。
4. 修改保守课程语义覆盖审计：区分缺口没有新草案 vs 已有新草案但未经审校。
   23 项全部为 GAP_DRAFT_CANDIDATE_UNREVIEWED，缺口 status 仍 OPEN，绝不因 ID 存在自动宣布关闭。
   老 Batch04 覆盖快照保留，新 Batch05 的 113 行证据快照单独生成。
5. CI 新增原创源脚本 --check 防漂移门禁，保留冻结 48 条数学子命题的旧 K07 测试和完整回归。
   学生端继续只能获取数量统计，教师完整解答不能被未认证 API 自动访问。

## 可复现精确计数

- 原深度草案 86；新增 23；合计 **109**（52 theorem、50 concept、7 method）。
- 旧工程课程映射 113 条，全部有至少一个草案链接，但该分母**不是**教育部官方原子知识点数。
- 编辑初审缺口 23：草案候选存在 23，尚无草案候选 0，真正审核关闭 0。
- 正式教师审核 APPROVED 0；整篇自然语言证明的形式验证 0；学生自由文本推导可信验证 0。
- 正式选修 A–E 的课程原子级映射审核 0（既有 7 条旧拓展主题不能作为全量选修）。

## Mac 实际验证

- source checksum: python scripts/build_semantic_gap_batch05.py --check → PASS，23 条原创候选完整匹配。
- K07: PYTHONPATH=backend .venv/bin/python scripts/audit_deep_math_evidence.py --check → PASS，48 条特定数学子命题。
- semantic audit: PYTHONPATH=backend .venv/bin/python scripts/audit_kb_semantic_coverage.py --check → PASS，23 项仍 OPEN。
- Python: cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest -q → **756 passed, 1 warning**，
  包含本轮 46 条例题旁路独立 oracle、23 个反例/来源检查，以及新增六个定理的狭义数学子命题独立验算；远端发布基线的原始重跑日志见 kb-batch05/pytest_release.log，草案目录首轮验收见 kb-batch05/pytest.log。
- Node: node --test tests/node/*.test.cjs → **111/111 passed**；发布基线复测日志见 kb-batch05/node_release.log，草案验证日志见 kb-batch05/node.log。
- Chrome: bash scripts/mac_browser_check.sh → **exit 0**，通过绿色学习工作台、
  数学画板 v0.8–v0.12、迁移记录、iPad 虚拟触控/压感和最终 2 个审阅脚本；
  仅软件模拟，不等于真实 iPad/Apple Pencil；发布基线复测日志见 kb-batch05/chrome_release.log，草案验证日志见 kb-batch05/chrome.log。
- 发布工作树首轮执行浏览器测试时因新工作树尚未链接 Mac 已有的本地虚拟环境而退出 2（非代码失败）；只添加 gitignore 的 .venv 软链接并重跑全套 Chrome，不修改主仓或 Python 依赖。
- git diff --check → PASS。
- 初次编写发现三处反例说明过短、一个建模拟合反例的数值未复算，
  均已修改并在新的 75 条 Batch05 专项测试中重新通过。
- Node、Chrome 原有场景无变化，仍单独完整运行验证未回归。

## 验收限制与下一批计划

新 23 篇是**可审核的编辑候选**，不是教师通过的教材讲义，更不是已证明的完整教学能力。
审核脚本把候选存在与人工确认分离，保护了“相似标题不等于内容充分”的审计原则。

下一批：
1. 依据官方课程标准逐章确认**真实原子课程**并建立可追溯分母，尤其核实选修 A–E 每个独立方向；
2. 将课程条件-证明义务-反例数据细化到每个定理，优先审查本轮六个 theorem 的正反方向合法性；
3. 检查 Batch02 的 39 条未冻结候选及编辑态 RAG 与最新 109 条的 ID/数学冲突，不直接合并；
4. 仅在存在真正独立教师授权/审核来源后，才对 Student Agent 开放相应 APPROVED 知识证据；
   未审草案只能在经过授权的本地教研评估中使用，所有正式生产模型推导必须可回溯和可拒答。
