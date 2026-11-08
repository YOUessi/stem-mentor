# STEM Mentor｜Batch38：20 项部分覆盖的选修数学范围修复（2026-11-08）

## 一、任务与基线

本批依据 GitHub #17–#27 的未关闭验收条件和 Draft PR #62 的已提交 Batch37 源码，继续处理 Batch36 冻结审计中 47 条选修旧讲义关联：12 条 `CLAUSE_UNVERIFIED`、27 条 `PARTIAL_SCOPE`、8 条 `CLAIM_MISMATCH`。Batch37 已为 8 条错配增补独立教师审核稿。本批处理 **20/27 条 PARTIAL_SCOPE**，其余 7 条仍在待办；此前 12 条条款未核实风险不随之消失。

本批所有代码、知识稿、实际测试均在授权 **MacBook Air**：`/Users/youtang/Documents/文件/stem-mentor-kb-batch38` 的独立 worktree、`feat/kb-batch38-elective-partial-repair` 分支执行。主仓 `~/Documents/文件/stem-mentor` 的 11 项既有未提交改动未触碰。未使用 Tang，不更改或强推 main，也未传输真实学生数据。

## 二、真实新增原创知识和审核约束

- **20 篇结构化教师审核稿**：选修 A 7、B 9、C 2、D 1、E 1；不是原来 287 篇深度草案的同类计数，也不是官方课标知识原子总数。
- 每稿有数学命题/符号、适用前提、三段带依据的推导、具体反例、常见错法和修复问题、两道带步骤和核对的教师例题、三个**逐篇定制的非剧透数学提示**以及近远迁移。
- 合计 **40 道教师侧例题、20 个具体反例、60 条有差异的分级提示、40 个近远迁移任务**。
- 涉及正项级数和 e、矩阵维度与行变换、线性方程组秩、克拉默法则、连续与混合分布、χ² 渐近使用边界、凸性、单调、偏导与可微、线性规划、自由变量、K-means 局部极值、双因素混杂、投入产出、参数化路径、逆否逻辑、复利、二维保距变换和期末年金。
- 原创内容在 `knowledge/editorial_review/kb_batch38_partial.jsonl`，整篇可读数学审核稿在 `docs/evaluation/KB_BATCH38_PARTIAL_SCOPE_MANUSCRIPTS.md`。由 `scripts/author_kb_batch38_partial.py` 生成；课程候选与 20 个稿件 ID、来源及内容 SHA 在 `KB_BATCH38_PARTIAL_SCOPE_AUDIT.json` 可追溯。
- 所有新稿严格为 `REVIEW_PENDING`、`TEACHER_ONLY`、`NOT_FORMALLY_CERTIFIED`、`student_publishable=false`；不能通过自称模型认证、字段篡改、复制审批人或编辑来源获得发布资格。**没有**将审核稿写入学生权威知识库，也没有将已有 47 条旧稿关联认定为数学等价。

## 三、独立精确数学实例与拒绝门禁

`backend/app/kb_batch38_exact.py` 新增 **14 类有界整数/有理数有限算子**：阶乘部分和、2×2 矩阵乘积、非零行倍乘、2×2 克拉默、线性密度区间积分、两类 χ² 计数、二次凸函数、线性中值定理实例、正方形仿射极值、两点 K-means 平方损失、单行业 Leontief、复利有效利率、2×2 正交等距阵、期末年金（包括零利率分支）。每个算子提供合法实例和非法前提实例，另拒绝缺失/多余字段、错误类型、超界整数以及未知算子。

新添 K-means 两组具体分簇的独立 `Fraction` 验算：局部稳定分组损失 `31/6`，存在另一分组损失 `4`，足以反驳“局部稳定必然全局最优”。这只是 **有限精确算例**，不认证一般定理、不评价任意学生自由文本证明。

`backend/app/kb_batch38_review.py` 对 Pydantic 审核模型、20 个固定目标、种子哈希和未授权学生投影做封闭校验；未知、伪造 APPROVED、错误来源或错误字段均拒绝。K01/K09 审计脚本已加入 `scripts/mac_check.sh` 与 GitHub Actions CI 可复现检查。

## 四、真实测试、失败和修复

- 新增专项测试：**108 passed，0 failed**（`backend/tests/test_kb_batch38_partial_repairs.py`）。覆盖每份稿件绑定、反例/逐步推导/专属提示、SHA、权限篡改、合法/非法数学条件、类型拒绝和具体数学预期值。
- Mac Python 全量：**37,840 passed，0 failed，1 条第三方弃用警告**；原始日志 `evaluations/results/2026-11-08-kb-batch38/mac_full_check.log`。
- Node：**111/111 passed**；教学策略 **33/33**；检索困难负例 **40/40**；检索 Top3 **22/22**。
- Chrome/Playwright 脚本 **15 项通过**，浏览器 pytest **2 passed**；浏览器结果在 `evaluations/results/2026-11-08-kb-batch38/browser.log`。使用临时合成数据库；iPad 是指针模拟，不是真实设备。
- 实际发现并处理：从仓库根目录运行 pytest 导致 `ModuleNotFoundError: app`，调整为 `cd backend && PYTHONPATH=.` 后通过；新增逐篇提示下，5 篇首次未满足最小细化要求，针对数学情境补充真实分层提示后 **108/108** 通过；Git 暂存验收发现四个 Python 文件存在多余尾空行，已修复并通过 `git diff --cached --check`。原始错误和修复过程没有隐藏。
- Mac 全量脚本 `set -euo pipefail` 最终到达 `Offline macOS simulation checks complete`，证明其内部检查全部执行完成。外层临时 zsh 包装脚本误用只读变量名 `status` 导致**包装脚本**返回 1，这发生在已完成的 Mac 检查之后，不是全量测试失败。验收以实际全量日志和子测试完成状态为准。

数学精确检查不能替代教师逐条验证或学习效果测量。未使用 GPU/API、未产生模型费用。

## 五、Git 源码证据与剩余问题

Mac 已通过测试的 Batch38 源码提交：`d8ed1df33b25616240300110c82a5bd24916fb0b`，Git Tree：`3d8c9856240a967bbdd1ff24c540a1de8c408c36`。GitHub 远端 PR/HEAD、树哈希和 CI 仅在实际完成同步及独立回读之后才记录，不能预先宣称成功。

当前**不可宣称完成**的门槛：七个官方课程方向完整原子分母仍为 `null`；287 篇旧深度讲义为未审核草案，49 + 8 + 20 = **77 篇新增的独立教师审核稿**均未获正式教师批准；538 条历史证明步骤未获完整形式认证，10 组历史内容冲突未正式裁决，教师 APPROVED=0、学生端深度正式发布=0。本批只为 20 项历史 PARTIAL_SCOPE 提供有条件的新审核材料，**不等同于把它们变成官方数学等价关联**。

**下一完整开发批次**：补齐 7 条尚无新稿的 PARTIAL_SCOPE 选修目标及其明确假设、反例、迁移题；核查另外 12 条 CLAUSE_UNVERIFIED 的原版课标条款；独立抽核新稿反例及参数边界；加快必修/选择性必修官方逐条分母，修复 538 条证明步骤的真实逻辑风险和 10 组冲突；对照学生检索端的拒答及防剧透，在真实教师签署前保持 unpublished。
