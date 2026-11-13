# KB Batch64｜14份数学深度草案、14项课程能力栏目候选关联与精确数学边界

执行日期：2026-11-09。源码、知识内容、验证与所有测试仅在授权 MacBook Air 的独立 worktree 执行；没有使用 Tang，也没有在 Mac 主仓 main 开发或合并。所有学生可见/教师批准状态保持关闭。

## GitHub 基线与进度

- 先读取 GitHub #17–#27 的当前 Open 状态及 Draft PR #88；Batch63 GitHub HEAD 为 `f28854ef1bb4df472c3d1af46ad98c58e0b2cf67`，其 Git Tree `4de588441194ab5d9f496d4fd107463f66b0bcca` 与本机 Batch63 经过完整测试的 tree 一致。
- Batch64 最初在 Mac 的独立 worktree `stem-mentor-kb-batch64` 编写并真实测试源码，源码提交 `38cc5a22c034d6465edba391669c4af4362ef16d`。
- 因之前 Batch63 使用 GitHub-native 补链提交，源测试分支与 GitHub PR #88 提交历史分叉，但 Git Tree 相同。为了保证 PR 仅包含本批变更，新建另一个独立 Mac worktree，从 GitHub #88 的真实 HEAD 创建 `feat/kb-batch64-deep-content-competency` 并 cherry-pick 等价源码提交 `e3f31ae`，验证两者源码 tree 同为 `3b52a35163510b0ba8373987c0db0e9fcf53f503`。没有 force push、重写 main 或合并 main。
- 最终日志/报告提交 SHA 以 GitHub 远端核对为准。

## K00/K01：保留课标范围可信边界，14项独立能力/教学栏目只有候选例题链接

- 读取 `KB_BATCH62_NONATOM_REQUIREMENTS.json` 的14个来源栏目及 Batch63 62项临时拆分假设；基于已锁定课标来源窗口SHA，不引用或上传课标全文。
- 为14项内容/学业/教学栏目分别建立2条人工编写的**候选教学例题关联**，共28条关联边，在 `curriculum/highschool_math/k00_batch64_competency_proposal_matrix.json` 中逐条关联来源锚点、原始行SHA、候选讲义与例题。
- 14个栏目全部继续 `UNMAPPED`，它们本来不等同于14个知识原子；28条关联边不能冒充28条学业要求。栏目全文、跨页及未编号要求尚未完成正式核对，未调用真实教师审核。
- 七轨 COMPULSORY、SELECTIVE_COMPULSORY、ELECTIVE_A–E 的官方独立数学原子分母仍为 `null`，不把旧113条工程映射、428条候选锚点、344条来源线索或本批讲义算作已经完成的官方分母。

## K02–K06：14份结构化原创数学深度草案

新增 `knowledge/editorial_review/kb_batch64_deep_lessons.json`，14个主题分别为：
1. 集合判定性、元素属于；2. 子集、真子集和双向包含；3. 全集与相对补集；4. 充分必要条件方向；
5. 非负基本不等式与等号；6. 函数定义域、单值对应；7. 指数函数底数及单调；8. 对数换底的非零分母；
9. 单位圆与正切定义域；10. 非退化三角周期模型；11. 简单随机抽样的组合等可能；12. 复数实虚部分离；
13. 函数建模、残差与外推风险；14. 直线与平面平行判定的包含例外。

每份独立提供数学对象与适用域、正式陈述或候选定理、先修、3个逐步说明及理由、2个原创教师例题（合计28）、典型错法与错因、至少1个边界反例（合计14）、3级提示（合计42）、近/远迁移。42条有依据的推演步骤**并不是42条机器形式证明认证**。

所有条目 `REVIEW_PENDING`、`TEACHER_ONLY`、`NOT_FORMALLY_CERTIFIED`、`student_publishable=false`，不加入正式学生检索索引。不因文本结构完整或有限算例通过就声称教师批准或学生解题步骤获得验证。

## K07：14类有限精确数学见证

新增 `backend/app/kb_batch64_exact_witnesses.py`：
集合整数谓词、子集关系、全集补集、有限论域蕴含、有理平方根范围内的AM-GM、有限单值函数表、严格指数次序、对数有理幂等式、单位圆轴角正切、非退化周期的精确归一比例、简单随机抽样组合、复数分量相等、线性模型残差/范围标识，以及z=0平面的直线位置算例。检查对浮点数、布尔伪数、非法定义域、除零、非方有理根、空样本等进行拒绝，不将 unsupported 输入推断为真。

所有见证仅为有限、精确、有界的例题运算核验，绝非一般定理的形式证明，更不能认证学生自由书写的证明。一般定理尚须独立数学推理及教研审核。

## K08：非空批准集合的实际检索安全回归

测试使用已有测试专用签名fixture，构造**非空**批准知识集合而非走空集合提前返回路径，针对14份新草案分别调用现有 `student_evidence_lookup`，断言草案未进入批准索引、候选知识ID不得是新稿、不会泄漏教师解法或未审核内容。本次无真实学生数据、无外部模型API调用；离线安全测试不能替代真实模型成本/数学真实性/延迟评测。

## K09：真实Mac测试及故障处理

| 核验 | 最终结果 |
| --- | --- |
| 新增 Batch64 专项测试 | **121 passed，0 failed** |
| Python 全量（包含121专项） | **45,421 passed，0 failed，1条第三方弃用警告** |
| Node.js | **111/111 passed** |
| Tutor 策略 | **33/33 passed** |
| RAG困难负例 / Top3 | **40/40、22/22 passed** |
| Chrome/Playwright和browser pytest | **15个Chrome/Playwright脚本完成；浏览器pytest 2 passed（合成数据与CDP模拟）** |
| `scripts/mac_check.sh` | **EXIT 0** |
| `scripts/mac_browser_check.sh` | **EXIT 0** |

原始增量、全量、浏览器运行日志以及每个命令的退出码分别留存在 `evaluations/results/2026-11-09-kb-batch64/`，并随分支提交。
初次在新worktree尝试运行单测时，由于该worktree未初始化 `.venv`，命令返回shell `no such file or directory`（无测试实际执行）；随后在**Mac**建立指向既有Batch62 Python环境的worktree本地符号链接，实际增量121项通过，全量45,421项通过。未将此基础环境错误伪装为数学测试失败。

Browser为Mac浏览器/CDP合成数据模拟，不是实体iPad硬件或真实学生长期学习增益验收。未改动Mac主仓11处原有未提交文件。

## 未解决与下一批

- 官方七轨课程原子分母仍未确定，所有条款不能仅凭机器启发式来源片段推出完整覆盖；全文/跨页与35页建模图的教师视觉审查未完成。
- 本批14篇草案数学、教学和课程归属仍待真实教师审核；已有538条历史未认证证明步骤及10项数学冲突尚待逐案裁决，不能自动 APPROVED。
- 下一批优先将14栏目重新核对完整原文及未编号目标，建立真正独立的学业能力测评题族/评分量规，再从62项拆分提案继续跨轨完整深度知识原子；对数学边界错例增加独立符号/几何推理核验及正式教师签核流程；对正式批准数据持续检查混合RAG检索和撤销可追溯性。

## 源码与日志 SHA

- incremental.log SHA256: 79c2283f7db359290fff30eecb57c7156db7d3af547bf492c5a1b7c1df056565; exit=0
- mac_check.log SHA256: 811fad80cc8d60a7fc23e4fcc8e910d062df61233fbcd9f3f7527eae9ce04b17; exit=0
- mac_browser.log SHA256: 57191bda5e7447e445277ac912b2e76e5c464fa81fd6b931d76ab783b03f9997; exit=0
- source_and_gate.log SHA256: 4487f3a9b17ae2336d3c3c9e05e7f71e2be70e5591a6d8fc654b855bc0ddf474; exit=0
