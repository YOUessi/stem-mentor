# STEM Mentor — 个人化理科培优系统

面向中高考理科培优的长期个人教学 Agent。**培养学生自己找到解题思路与突破口的能力，而非代写完整答案。**

## 当前版本
- **设计基线 v0.2**：需求、功能、策略、学生记忆、数学方法检索和评测规范已入库。
- **开发方式**：先构建**无模型 API 的确定性模拟版**；不宣称具备通用 AI 数学能力。
- **三种学习模式**：逻辑分析（ANALYZE）、推理陪练（GUIDE）、自主挑战（INDEPENDENT）。
- **共用能力**：个人真实解题经历、方法结构检索、微知识点复习、思维地图、渐退式提示、数学验证（限定范围）。
- **边界**：模拟数据不构成学习效果证据；未经授权教材和真实学生资料不可上传公共仓库。

## 目录
- [产品需求](docs/requirements/PRD.md) · [功能规格和验收](docs/requirements/FEATURE_SPEC.md)
- [技术架构](docs/design/ARCHITECTURE.md) · [教学状态机](docs/design/TUTOR_POLICY.md) · [数据模型](docs/design/DATA_MODEL.md)
- [讨论决策与需求溯源](docs/decisions/CONVERSATION_DECISIONS.md)
- [评测计划](docs/evaluation/TEST_PLAN.md) · [分阶段开发](docs/planning/ROADMAP.md)
- [学生数据与内容安全](docs/security/PRIVACY.md) · [日期工作日志](docs/logs/2026-10-15.md)

## 本地运行（后续模拟版）
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
浏览器打开 http://127.0.0.1:8000/ 。全部教学回复由受限的规则与题目卡片生成，不需要模型密钥。

## 开发原则
1. 基于真实学生当前输入确定下一步教学动作；默认最小提示。
2. 先从已知正推，遇到瓶颈可从目标逆推，寻找桥梁；不线性代做。
3. 不虚构学生做过的历史题，不把 AI 帮助下的作答当作独立掌握。
4. 数学方法需要适用/失效条件、例题/反例、推导、方法关系与审核。
5. 所有验证和实验日志都记录数据版本、运行结果、失败案例和局限。
