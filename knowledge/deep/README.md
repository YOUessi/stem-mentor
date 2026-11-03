# STEM Mentor｜结构化高中数学知识 v1（教研草案）

首批两份 `v1/*.json` 及后续扩充文件均为项目原创内容，**不是教材摘录、教师已审定内容或通用自动证明系统**。2026-11-03 第一批有 28 个完整字段的草案知识单元、18 个命题/定理型和 10 个概念型，内容横跨基础逻辑、代数与函数、三角与向量、三角形、复数、概率统计、计数、数列及导数等主题。这 28 份单元关联了已有工程地图的 42 个不同条目，并不意味着全课标已覆盖。

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


## 2026-11-03 Batch04 增量（叠加 K07 数学证据 PR）

这是在上文 **Batch01 的 28 篇冻结草案**基础上扩容的独立 Draft 工作分支，不是覆盖或重写历史计数。新增五个 `v1/*batch04.json` 文件，共 **58 篇**完整字段的原创草案；当前共 **86 篇**（46 条 theorem、37 条 concept、3 条 method），每篇至少两道教师侧例题、一个反例/非例、错因、提示阶梯和近远迁移；所有 `review.status=REVIEW_PENDING`，**教师审核 0**。新草案涉及函数/三角/向量、概率统计/建模、空间几何/圆锥曲线、选修工程拓展。

**映射数量不代表全课标完备。** 当前 86 份草案与原有 113 个工程知识点全部存在关联（必修 61/61，选择性必修 45/45，旧「选修拓展」7/7）；我们另行初步标记 **23 个已知内容子能力缺口**，包括复数运算、导数几何意义、线面距离、表面积、概率独立、三角图像等。其余 90 个仍是未经专家审校的关联，不是 90 个确定合格的主题。7 条工程拓展不代表选修 A–E 完成。全部 113 个官方原子映射尚未经过真实教研审校，不能说全高中数学课程已完成。

可复现保守审计：

    PYTHONPATH=backend .venv/bin/python scripts/audit_kb_semantic_coverage.py --check
    PYTHONPATH=backend .venv/bin/python scripts/audit_kb_semantic_coverage.py --summary

交付记录：`knowledge/deep/semantic_gaps_batch04.json` 列出 23 个具体缺口及建议新知识 ID；`docs/evaluation/KB_SEMANTIC_COVERAGE_BATCH04.json` 是 113 行自动审计快照；`scripts/audit_kb_semantic_coverage.py` 是 CI 校验门禁。`backend/tests/test_deep_batch04_worked_examples.py` 使用 **116 条**独立数值/几何点验算核对 58 篇新草案各两例，**不等于 116 个完整定理的形式化证明**。`backend/tests/test_kb_semantic_coverage_batch04.py` 检查篡改负例、审校边界和官方课标口径。

此前 K07 冻结证据清单依旧只覆盖 **48 条指定子命题、链接 14 篇旧草案**，不能自动解释为 86 篇已证明。当前学生自由文本推导验证 0，完整自然语言定理形式证明 0，学生端未审稿可用知识 0。

下一批优先补齐 23 个已知子能力缺口、完整官方选修 A–E 课程映射与受控内容，并完善每条定理的逐项证明义务及人工教研审校流程。学生端 RAG/API 在有真实审批以前必须继续拒绝未审证据。

## 2026-11-03 Batch05：补充 23 个已知语义缺口的候选草案

Batch05 在上游 86 篇草案基础上新增 23 个项目原创深度子技能单元，
与 semantic_gaps_batch04.json 中的 23 项建议知识 ID 一一对应。
覆盖集合和逻辑、不等式变形、弧度与三角函数图像/倍角、向量投影，
复数代数/辐角/运算、线面平行/距离/表面积、概率事件/独立性、
统计中位数、协作数学建模、导数定义/切线/极值、焦准线及曲线正则切线。

- 当前 109 篇深度教研草案：52 theorem、50 concept、7 method；全部 REVIEW_PENDING，教师审核 0。
- 23 个初步语义缺口新增全部对应候选草案；gap_draft_candidate_count=23；
  但 gap_review_status 仍全部为 OPEN，known_partial_topic_count 仍为 23。
  这些是草案，尚不能宣布这些语义缺口已经被认证关闭。
- 每篇单元至少 2 道 teacher-only 例题，新增 46 个独立精确/受限点验算；
  与旧 K07 的 48 条冻结子命题是不同证据，均不等于完整自然语言定理形式化证明。
- 旧 113 条工程目录均有关联草案，但正式官方原子课程映射仍为 0 条通过审核，
  尤其不能把旧 7 条工程拓展当作选修 A–E 全量。
- 新的覆盖快照为 docs/evaluation/KB_COVERAGE_BATCH05.json 和
  docs/evaluation/KB_SEMANTIC_COVERAGE_BATCH05.json；旧 Batch04 快照完整保留。
- 内容源码为 scripts/build_semantic_gap_batch05.py，使用 --check 验证生成文件未漂移；
  CI 也会检查生成器和当前覆盖审计门禁。

复现：python scripts/build_semantic_gap_batch05.py --check；
PYTHONPATH=backend .venv/bin/python scripts/audit_kb_semantic_coverage.py --check；
cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest -q。

未完成硬门槛：逐条正式课标原子映射、正式教师签核、严格数学定理整体验证、
学生权限隔离和已批准内容驱动的教学 Agent。未经审核的证明与教师例题不得开放。

## 2026-11-03 Batch06：Batch02 安全消歧与编辑态检索

这是 **Batch05 的独立堆叠 Draft PR**，不替代既有 109 篇知识草案。

- Batch02 留存 39 篇候选，逐一对照当前 109 篇：29 篇有新 ID 并安全导入；10 篇与既有 ID 冲突，**保留两个原稿等待人类比较，绝不覆盖或自行合并**。源稿原样放在 `knowledge/deep/candidates/batch02/`，每个冲突的源哈希、现行哈希和不同字段记录在 `docs/evaluation/KB_BATCH02_RECONCILIATION.json`。
- 当前仅有 **138 篇原创深度草案**，其中 theorem 58、concept 66、method 14；全部 `REVIEW_PENDING`、教师审核 0、完整自然语言证明正式认证 0、学生自由推导验证 0。
- 原有 26 条方法卡创建 **只读无损桥** `knowledge/deep/legacy_method_bridge_v1.json`，保留各卡先决条件、应用边界和提示，明确 `NEEDS_DEEP_AUTHORING`，不将桥当成新增的 26 篇深度教材。
- 新增本地**编辑态** FTS5 检索 `backend/app/deep_retrieval.py`，以多语言二元词、课程 ID、内容类型过滤候选，只返回知识 ID / 标题 / 审核状态 / 分数和“条件未建立”，不得当作数学可靠性证明。未提供显式本地编辑用途则拒绝访问。这里的 `scope="EDITOR_LOCAL"` 是防误用的本地编程约定，**不是权限认证**：不可暴露成外部 HTTP 接口。
- `student_evidence_lookup` 保持 fail-closed：没有认证过的教师审核就只返回 `NO_APPROVED_EVIDENCE`。所有教师证明和题解仍是 TEACHER_ONLY，不进入学生的对话 Prompt，也不调用真实 LLM API。
- 生成器 `scripts/reconcile_kb_batch02.py --check` 与 `scripts/build_kb_legacy_bridge.py --check` 被加入 CI；另增加教学草案结构、冲突哈希、隔离检索及有限数学独立核对测试。原先保守语义缺口的 23 项 **继续 OPEN**，不因又多了关联草案就标记合格。

本批主要解决 **安全合并、内容来源完整性、审校冲突可追踪、编辑态检索**。它仍不能推出全课标的完整覆盖：既有 113 条仍是工程索引，正式选修 A–E 课程原子没有被逐项确认，不能以 138 篇数量论证课标完备；完整课标核对与合格审核必须继续执行。

复现命令（Mac）：

```bash
PYTHONPATH=backend .venv/bin/python scripts/reconcile_kb_batch02.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_legacy_bridge.py --check
PYTHONPATH=backend .venv/bin/python scripts/audit_kb_semantic_coverage.py --check
PYTHONPATH=backend .venv/bin/python scripts/build_kb_coverage.py --summary
cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest -q
```
