# STEM Mentor v0.14 拟议教学知识模型（待实施）

日期：2026-10-20
状态：**DESIGN ONLY；尚未作为运行中的数据库架构或 RAG 数据格式上线。**

## 核心目标

让知识从“名字+简述+画板链接”升级为**有数学条件、有可检验推导、有反例、有不同层级教学动作、有合法来源**的教学知识体系，支撑高中数学113条工程目录逐项建设，同时预留物理与化学扩展。

当前知识材料现状见 [知识完整性审计](../evaluation/KNOWLEDGE_BASE_AUDIT_2026-10-20.md)。本设计不改变 v0.13 正在运行的离线学生模拟系统。

## 一、领域对象

| 对象 | 关键字段 | 必须分开的数学/教学含义 |
| --- | --- | --- |
| `Concept` | concept_id, title, grade, prerequisites, definitions, scope, notation | 概念/定义不是解题技巧 |
| `Theorem` | theorem_id, original_statement, hypotheses, conclusion, proof, equality_conditions, counterexamples, source | 定理必须先写原命题、逐项假设，再讨论应用 |
| `Method` | method_id, triggers, obligations, applicable_conditions, invalid_conditions, alternative_methods, hint_ladder | 方法候选不是定理；“想到了方法”不等于条件成立 |
| `ProblemFamily` | family_id, structure_tags, method_tags, variants, frozen_split, difficulty, reviews | 题目文字相似≠数学结构相似 |
| `WorkedExample` | problem_id, original_prompt, conditions, teacher_solution, verification, false_attempts | 解答在教师侧；学生侧按提示预算渐进披露 |
| `Misconception` | misconception_id, symptom, logical_error, counterexample, repair_question | 需要基于学生真实尝试判别，不由关键词直接贴标签 |
| `MicroPoint` | micro_id, recall_question, validity_boundary, spacing_policy, evidence | 微考点提醒与已掌握状态必须区分 |
| `TeachingAction` | action_id, preconditions, student_mode, hint_level, next_check, exit_condition | 教学决策须避免重复、过度帮助与未经求助提前介入 |
| `StudentEpisode` | student_id, session_id, attempt_id, model_events, source_hints, created_at | 学生个人记录与公开教学文档是两个数据域；不可跨学生检索 |

## 二、每篇可用于教学的知识文档必备字段

通用元信息：

```yaml
doc_id: math.hs.sequence.geometric.finite_sum
curriculum_ids: [HS-MATH-...]
version: 1.0.0
status: DRAFT               # DRAFT -> REVIEW_PENDING -> APPROVED
knowledge_type: theorem
subject: 高中数学
source:
  kind: PROJECT_AUTHORED
  reference: STEM Mentor 自编数列知识草案
  permission: PROJECT_AUTHORED
  author: PROJECT_AUTHOR
  reviewer: null
  reviewed_at: null
license_status: REQUIRES_EDITORIAL_VALIDATION
visibility: TEACHER_FULL_STUDENT_SCOPED_HINTS
```

教学内容字段：

1. `prerequisites`：先修定义和必要计算能力；列出引用知识的ID而不只有自然语言。
2. `definition`：用域、量词和数学对象明确概念，附直观解释及图形。
3. `theorem.original_statement`：先给完整数学表述，再单独列假设、结论、等号条件。
4. `proof.steps`：每步写依据、条件和从何推得，不允许把逆命题、必要条件直接当等价。
5. `applicability`：可用条件、失效条件、退化情况及对应反例。
6. `worked_examples`：不少于一个完整教师侧例题与验证结果；学生侧只看到题目和按需层级提示。
7. `common_errors`：真实数学错误、为什么错、最小修复性追问及反例。
8. `hint_ladder`：观察→向目标逆推→桥梁→条件核验→仅在教学许可后提供具体计算；每层都有退出条件。
9. `transfer`：同结构不同参数、跨表征、不同题型的近/远变式；标注适用边界。
10. `review`：微考点、自主复述、学生能否离开帮助复用方法的冻结评测，不与单次点击混同。
11. `provenance`：原文出处、页码/链接、引用许可、版本、审批记录、纠错历史。

## 三、如何对真实教学文本实施 RAG

推荐的“分层检索”而非一锅混合：

- **课程层**：按版本、学校年级、地区考试范围检索课程原子ID，但工程目录不得被误称为官方逐字课标。
- **定理层**：按题目已知与候选定理假设逐项对照。没有条件证据时返回 `CONDITIONS_NOT_ESTABLISHED`，不能自动认定定理成立。
- **方法/题族层**：结构特征、适用条件、失效条件、典型错因等。只在通过条件与课程许可后给学生最小提示。
- **个人学习层**：需身份认证且受独立权限保护；当前只有合成模拟数据，不允许并入公共文档索引。

索引更新工程要求：知识文档必须版本化；新增/更新/撤回时重建或增量更新被影响的检索索引，旧 `doc_id/version` 的评分和教学引用保持可追溯；过时缓存失效后再提供新内容。未经审核/版权不明的文档即使命中，也不可被自动当作权威答案。

全文/表格/公式/图示需保留原始结构与关联关系：数学公式与文字同位、图表标题与对应证明定位，禁止简单固定字符切块打断假设与结论。未来添加 PDF 等教材资源必须先核实授权。

## 四、学生可见性（强约束）

- 学生请求“先给一点提示”：只返回限定提示层与来源，并询问下一步，不提供完整 `teacher_solution`。
- 自主挑战：未经求助不主动剧透方法或历史题名。定理全文是否可见取决于当前学生显式请求和教学动作。
- 纠错反馈：允许指出哪条应用条件未验证，不能把自然语言错误“确诊”为证明失败。
- 证明与算式自动验证仅在明确的受控数学范围内启用；超出范围返回 `UNSUPPORTED`。
- 自我评价、查看答案、视频播放、几何拖动都不等于学生已经掌握数学结论。

## 五、验收里程碑（仍未完成）

| 阶段 | 验收物 | 通过标准 |
| --- | --- | --- |
| K1 | 可验证JSON Schema与内容审核工具 | 每一篇知识内容可检查必填、ID、来源许可、数学适用条件 |
| K2 | 20—30个自编高频知识点完整讲义 | 定义/定理/条件/证明/反例/错解/提示/变式齐备，教师审核PENDING与APPROVED严格分离 |
| K3 | 题族与错因关联图 | 能拒绝只靠同关键词造成的错误迁移 |
| K4 | 可用的多层RAG | 更新知识后索引刷新/版本追溯/撤回生效，且无教师侧完整解法泄漏 |
| K5 | 真实审阅后的评测与学生研究 | 有授权的教师审阅与无提示新题/延迟迁移测试，成绩与提示次数分开 |

示例知识讲义：`knowledge/lessons/geometric-series-finite-sum-DRAFT.md`。它是项目自编、待审核的原型，不会因放入文件夹自动进入运行时的26条方法卡索引。
