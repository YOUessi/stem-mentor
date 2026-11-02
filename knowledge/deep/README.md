# STEM Mentor｜结构化高中数学知识 v1（教研草案）

这里的两份 `v1/*.json` 文件是项目原创内容，**不是教材摘录、教师已审定内容或通用自动证明系统**。2026-11-03 第一批有 28 个完整字段的草案知识单元、18 个命题/定理型和 10 个概念型，内容横跨基础逻辑、代数与函数、三角与向量、三角形、复数、概率统计、计数、数列及导数等主题。这 28 份单元关联了已有工程地图的 42 个不同条目，并不意味着全课标已覆盖。

## 结构

- `kind=concept` 必备数学定义、论域和符号、>=2 条解释/理由、边界和非例；定义不需要捏造形式证明。
- `kind=theorem` 必备完整陈述、假设、>=3 条带理由的证明步骤、退化/失效例；证明内容是待审教研草案，不应误称机械形式证明。
- `kind=method` 预留明确方法使用前提和依据、>=3 条合理性说明。
- 所有类型须提供至少 2 例教师侧带步骤示例、典型误区、反例/非例、分层提示、near/far 迁移和来源/许可。
- `prerequisite_lesson_ids` 必须指向已存在知识条目且构成无环图； `prerequisites` 中的文字可以包含尚未建成的前置定义，表示**未满足的后续内容要求**。
- 教师解法和完整证明被固定为 `teacher_solution_visibility=TEACHER_ONLY`；本项目没有教师身份鉴权，**不应开放未审核的教师预览 API**。
- 审核状态一律为 `REVIEW_PENDING`，无一获真实教师审核；Schema 通过和数值校验通过都不代表人工教研通过。

## 可复现命令（仅 Mac 工作树）

```bash
# 默认工作树中 .venv 与用户主项目虚拟环境独立部署；下例使用显式环境
PYTHONPATH=backend /path/to/python scripts/build_kb_coverage.py --summary
PYTHONPATH=backend /path/to/python scripts/build_kb_coverage.py --output docs/evaluation/KB_COVERAGE_BATCH01.json
cd backend && PYTHONPATH=. /path/to/python -m pytest -q tests/test_deep_knowledge_v1.py
```

诊断 API：`GET /api/knowledge/depth/coverage` **仅返回数量和审核状态**，不返回未审核的题目解答、反例或证明正文；不会让模型自动决定学生做题对错。原有 26 张离线方法卡及 Tutor 流程保持不变，尚未从这个新深度库向学生直接提供教学答案。

## 验收边界

- K00 的课程映射依据 `curriculum/highschool_math/official_scope_v1.json` 进行高层结构比对。已有的 113 条 `HS-MATH-...` 是项目设计的工程索引；不是官方原子知识点数量。课程标准包括必修/选择性必修/选修 A–E；已有 7 条「选修拓展」仍没有分配到 A–E 具体子类。
- `scripts/build_kb_coverage.py` 输出全 113 条逐项映射及缺失列表。即使有对应内容，没有真实教师签字也不能标记审核通过。
- `backend/app/deep_knowledge.py` 采用 Pydantic 强类型和跨文档 ID 依赖检验，禁止缺条件、伪审校、无许可证、匿名完整解法及自相矛盾的知识连接。
- `backend/tests/test_deep_knowledge_v1.py` 包含来源/权限/先修 DAG/审核/课程覆盖和受控代数恒等、概率边界、几何例题的负面测试。数值与符号测试只覆盖列出的特定结论，尚不能形式化验证 28 篇所有自然语言证明。
- 下一批优先补全尚缺的 71 条工程映射内容，逐课标细化新原子条目，并为选修 A–E 建立真实的课题映射；当有教师身份与审核证据时再逐篇审校和解锁。
