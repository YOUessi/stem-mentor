# STEM Mentor — 个性化理科思维培优系统

面向中高考理科培优的长期个人教学 Agent，核心目标是培养学生**脱离 AI 后的审题、策略选择、突破口发现与跨题迁移能力**。当前版本为**不使用任何模型 API 的规则模拟 Web App**，不等于通用 AI 教师。

## 立即运行

本机需要 Python 3.12+。

```bash
git clone https://github.com/YOUessi/stem-mentor.git
cd stem-mentor
python -m pip install -r backend/requirements.txt
cd backend
PYTHONPATH=. python -m pytest -q
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

打开 [http://127.0.0.1:8000](http://127.0.0.1:8000)。或在仓库根目录运行 `docker compose up --build` 后访问同一地址。**无需设置 API key。**

## 已实现并具备自动测试的模拟能力

- 响应式网页：题目/草稿/师生互动/思维探索轨迹、方法库、个人解题经历与易漏考点。
- 三种共用同一会话的学习模式：逻辑分析（ANALYZE）、推理陪练（GUIDE）、自主挑战（INDEPENDENT）。
- 六道可审计的数学题卡 + 四张方法卡 + 五个微考点；自定义题仅使用明确标识的保守通用启发。
- SQLite 持久化学生模拟账号、学习会话/原始尝试、模式切换、历史经历与复习计划。
- 新题回忆只针对**同一学生真实保存**、共享数学方法和深层结构的历史题；不会根据题目出现相同字词虚构旧题。
- 自主模式无求助不提前泄露提示；非线性正推/逆推策略根据学生输入的显式信号切换。
- 间隔回忆按有限关键词规则判断，**不能替代完整答案评价**；所存的完成记录只表示学生自述，非独立正确证据。
- SymPy 在固定审核案例上检查恒等关系；对任意学生推导不声称已完成数学证明。
- FastAPI 交互 API、Docker、GitHub Actions CI、10 个后端回归场景及 JS 语法校验。

## 设计与过程记录

[产品需求](docs/requirements/PRD.md) · [24 项功能验收](docs/requirements/FEATURE_SPEC.md) · [系统架构](docs/design/ARCHITECTURE.md) · [教学决策策略](docs/design/TUTOR_POLICY.md) · [数据模型](docs/design/DATA_MODEL.md) · [对话需求与设计决定](docs/decisions/CONVERSATION_DECISIONS.md) · [评测计划](docs/evaluation/TEST_PLAN.md) · [实施路线](docs/planning/ROADMAP.md) · [隐私与安全](docs/security/PRIVACY.md) · [2026-10-15 开发日志](docs/logs/2026-10-15-implementation.md)。

## 当前局限

这只是**限定数学题卡 + 确定性规则**模拟：尚未接真实 LLM、完整数学 RAG、知识追踪模型、自动任意数学推理、用户认证、未成年人正式试用或真实学习效果评估。仓库为公开仓库，请勿提交任何真实学生数据、授权未明的教材或密钥。
