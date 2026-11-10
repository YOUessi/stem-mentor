# STEM Mentor｜Batch88：36组跨轨数学候选关系与有限精确验证（2026-11-11）

## 事实源、环境和边界

- 项目：`YOUessi/stem-mentor` #17–#27。本批始于 Batch87 完整 Mac 提交 `b03392cd22d95d2b81387f26ed7957ca14ba2c0f`，Stacked on [Batch87 PR #112](https://github.com/YOUessi/stem-mentor/pull/112)。
- 唯一实际生产/测试机器：授权 MacBook Air，独立工作树 `~/Documents/文件/stem-mentor-kb-batch88`、分支 `feat/kb-batch88-equivalence-triage`。GitHub只作为远端事实源和CI；Tang未用于课程内容/代码工作，Mac原主仓11项既存未提交修改保留。
- 基线Batch87已完成428/428个项目内部课标原始锚点原创解释，但428个来源行不等于428份课程知识、也不等于官方数学原子分母；其300个数学主题是未经语义等价审查的临时标签。选修E目前识别0来源锚点，不等于官方范围必为0。
- 本批全部状态为`REVIEW_PENDING / EDITOR_ONLY_NOT_TEACHER / NOT_FORMALLY_CERTIFIED`。正式教师批准0、学生权威课程发布0、官方七轨原子分母继续为null、完整教师逐页原子化0/61；不可借有限见证改写审核状态。

## K00+K01：36组跨页/跨轨数学语义对照

新增 `curriculum/highschool_math/kb_batch88_cross_track_editorials.json` 与可重现生成器 `scripts/build_kb_batch88_relations.py`，对**36对、70个不同的临时主题ID**做来源可追溯的逐项对照；**27组潜在主题重叠、9组需保持数学区别**。重点覆盖：

1. **微积分**：二阶导、拉格朗日中值定理、微分与有限增量、Riemann和与积分、牛顿莱布尼茨、定积分面积与截面积体积；严格列出连续、可导、可积、零分母、面积取绝对值等条件。
2. **线性代数与空间几何**：投影与零向量、线性相关、子空间封闭性、矩阵尺寸、行列式、消元、齐次/非齐次解、Cramer非奇异条件；不同课程的数学对象或前提不自动等价。
3. **概率统计**：密度归一化与矩存在性、联合分布独立性、均匀/正态参数、Z检验前提、拟合优度期望频数、二维协方差正定性及单双解释变量OLS区分。
4. **明确不可混同的例子**：驻点≠极值、仅有界≠单调有界收敛、必要条件蕴含方向≠充分条件、现实周期现象≠全域周期函数、平面基底≠三维空间基底。

每组保存原始候选ID、来源页码、来源行 SHA、左右所属课程轨道、共通数学结构、条件/范围差别、原创有限正例、违背前提或应保持区别的反例、待教师审核状态。两侧候选必须属于Batch87冻结300项；自动拒绝伪造教师身份、学生发布、定理形式认证、源身份篡改、隐藏字段、重复或交换配对。导出 `docs/evaluation/KB_BATCH88_PROVISIONAL_RELATIONS.{json,md}`，仍报告语义等价认证数0与正式知识原子分母null，**不把27组“潜在重叠”直接合并为正式原子**。

## K07：11种范围受控的有限精确见证

`backend/app/kb_batch88_relation_oracles.py` 用 Python `Fraction` 和 SymPy，分别受控检验：

- 二次函数MVT割线与导数、有限右端黎曼和与积分差距、有向/无向面积；
- 维数匹配矩阵乘法、仿射水平直线是否为线性子空间、均匀分布方差；
- 二维协方差正定性、二维离散联合权重是否独立、对角三阶Cramer；
- 充分条件是否必要、x³驻点不是极值。

无效输入、缺失必要前提、非整数精确参数一律不产生“已验证一般定理”；未知操作返回`UNSUPPORTED`，前提不足返回`CONDITIONS_NOT_ESTABLISHED`。数值正负见证只认证固定计算实例，不构成全部定理的普适证明，也不认证学生自由解题步骤。

## K08/K09：审查门禁与真实测试

`backend/tests/test_kb_batch88_relations.py`覆盖36项来源SHA与轨道对应、非法审核/发布状态、重复关系、遗漏数学论证、原始JSON重复字段、原子分母篡改、11类精确见证及条件边界。未审核材料不进入正式学生权威索引；本批对每组36个关系均以**非空合成签核教材索引**执行学生检索探测，确保未见教师编辑论证、源ID、对照正例/反例。模拟签核仅用于负面测试，绝不算真实教师审核。

- 独立Mac专项：最初 **482 passed / 0 failed**；新增真实的非空合成签核索引防泄漏测试与6项SymPy交叉核算后，首次 **487 passed / 1 failed / 1 error**（SymPy结构表达式未化简，pytest跨模块fixture未显式导入），修复后 **489 passed / 0 failed**。失败日志保存为 `mac_specialty_initial_failure.log`。
- Mac Python全量已独立复测：**61,302 passed / 5 skipped / 0 failed / 1个第三方警告**；Node **111/111**；Tutor策略 **33/33**；RAG困难负例 **40/40** 与 Top3 **22/22**。Chrome/Playwright **15个脚本通过 + 浏览器pytest 2 passed**。四项Mac专项、全量、浏览器、独立符号复核的最终退出码全部为0。**489项专项属于61,302项Python全量子集，不能重复累加**。GitHub CI仍需独立核验远端提交结果。
- 详细原始日志、独立SymPy复核、失败用例与最终退出码位于`evaluations/results/2026-11-11-kb-batch88/`。独立符号复核10项通过；初始符号实验断言失败保留，说明有限样本假设/表达式等价不能靠文本直接宣称。
- 源码冻结Mac commit：`b62476baa1094a5ef8b15bcc82e7d71f1152d8a0`，对应Git Tree：`fb33962889fbdc7f031c36be8dbc051de94714e2`；源码已正常git push到GitHub独立分支`feat/kb-batch88-equivalence-triage`，Draft PR [#113](https://github.com/YOUessi/stem-mentor/pull/113)（叠加于#112）。正式CI结论以GitHub Actions实际记录为准。

## 尚欠的全项目验收

本批36组关系及有限算例不抵扣官方课标内容核实、未逐页拆解内容、真实教师审校或538个历史未经一般形式认证的步骤。P0历史源步骤64/182已有待审材料，余118；10组冲突未裁决。正式七轨数学原子分母未知，真实教师批准0，学生正式深度发布0。

## Batch89首要计划

在剩余300个暂定主题中继续做跨页/跨轨数学条件实质比较（优先同一概念的不同定义域、充分必要条件）；通过可审核的分层关系类型组织`SAME_WITH_ASSUMPTIONS / SPECIALIZATION / RELATED_DISTINCT`但不自动把暂定标签压成正式知识原子。同步扩展必修和选择性必修完整原创讲义、题族、错因与条件验证，逐个处理未关联的118个历史P0步骤，建设真实教师审核与学生检索授权回归。全量未完成前保持所有Issues和任务Open。
