# STEM Mentor / Batch24：必修、选择性必修深讲义 + K00 来源交叉审计 + K01/K07/K09 门禁

> 执行日期：2026-11-08（MacBook Air，仅授权 Mac 开发与验收）。  
> 独立工作树：`~/Documents/文件/stem-mentor-kb-batch24`；分支：`feat/kb-batch24-source-reconcile-core`。  
> 源基线：Batch23 本地 `81b060f60ac3270c374f8c10e4ec2877e9de47e4`，Git tree `b168704fd9368ce68594f0697d4e37fe403444c8`；对应 GitHub PR #49 远端 `8dc62715c5887872e1d83e138449b5ce040e24f5`。  
> 当前分支属于 **REVIEW_PENDING 实验性内容建设**；本文件并不代表正式教师签字、官方课标全量覆盖或已认证定理证明。

## 1. 先检查原有 GitHub 验收依赖

按顺序读取 GitHub 总任务 #17、子任务 #18–#27、现有 Draft PR #49、Mac worktree、历史评估日志。旧状态：267 篇深度草案、178 条工程课程主题、519 条待验证证明步骤、127 项历史 P0 条件风险、10 组未裁决内容冲突、427 项 K00 来源审查任务、0 项教师批准及 0 项学生端深度内容发布。上一轮独立 PR #49 已通过 CI，但不代表这些审核问题结束。其他原有 Mac 主仓/工作树存在未提交内容，本轮完全未修改。

## 2. K02/K03/K04：20 篇真正结构化的原创基础与选择性必修内容

此次 **20 篇新增，6 篇定理、9 篇方法、5 篇概念；40 道教师侧例题；19 条新增未认证证明步骤**。

必修：量词否定、不等式乘法变号、含参数二次不等式、AM–GM 等号条件、函数自然定义域、奇偶定义域对称、负底数有理幂条件、复合与反函数、诱导公式、正弦两角和、正弦定理含外接圆弦长、棱柱棱锥截面积/体积、古典概型等可能性。

选择性必修：等比数列有限求和的 q=1 退化支、二次方程最高次系数退化、空间方向向量、竖直线斜率不存在、双曲线焦距参数、超几何无放回抽样范围、列联表期望格数和小样本限制。

文件：
- `curriculum/highschool_math/author_seed_batch24.jsonl`：手工原创内容主数据；每条适用域、论证、反例、常见错法、两个教师例题、三级提示、先修关系、近/远迁移。
- `scripts/author_kb_batch24.py`：严格 Pydantic Schema 再现性生成、验证 `--check`。
- `knowledge/deep/v1/core_foundation_batch24.json`：真实进入既有 `lessons()` 深度知识加载与**仅内部可见**草案检索，不扩展学生可见答案。
- `backend/tests/test_kb_batch24_source_core.py`：Schema、反例、来源、不可发布负例，以及有限数学性质样本验证。

注意：本批的学校课程主题 ID 均来自工程目录，**不是 20 个已经独立确认的官方课标原子**；完整证明需要后续数学专业审核和真实教师审核。所有草案保持 `REVIEW_PENDING`、`TEACHER_ONLY`。

## 3. K00：不再将候选清单误用为官方分母

`scripts/build_kb_batch24_scope.py` 读取并固定历史来源 SHA256，生成 `docs/evaluation/KB_BATCH24_SOURCE_CROSSWALK.json`：

- 原 PDF 内容定位的 61 页、315 个编号标记候选；编号候选按必修 114、选择性必修 82、选修 A/B/C 52/51/16，D/E 0；**这些是 PDF 抽取标记不是独立知识原子**。
- 132 条课标页面定位的 *项目自编* 学习目标候选、23 条选修 D/E 非编号标题、28 项尚未核定的编辑缺口；427 项旧审查任务全部保留。
- 为每个编号标记建立其页码/行哈希/同页工程目标候选的**页面级关联**，绝不把同页判作语义等价。对 132 项项目目标也保留相反的同页关联和 PENDING 决定。
- 315 个（页码、行哈希）互异组合中，只有 293 种全局行文本 SHA，**22 种行哈希跨不同页复现**；这仅是文本重用审查线索，不允许自动删掉 22 个官方要求。
- 历史口径 `248` 未能在当前可核实的主数据中找到相应的逐条明细，因此标记 `NOT_REPRODUCED_FROM_THIS_SOURCE`，并未凭空断言 248 与 315 的差异来自同类去重。
- 官方分母（必修、选择性必修、选修 A–E）及覆盖率全部仍为 `null`；PDF 原文中未编号/表格/数学符号仍需独立逐页核对。

此轮校验的是仓库**现存来源抽取材料及其哈希一致性**，不冒充重新阅读/教师复核 188 页课标 PDF。新增了来源页哈希伪造、标记 ID 复制、假装教师批准、来源目标私自批准等负例。

## 4. K01/K07/K08/K09：有限运算验证、审核义务、可复现进度矩阵

`backend/app/kb_batch24_math.py` 增加 8 种**纯精确有理数的有限实例检查**：
`strict_inequality_scale`（乘因子符号）、`quadratic_discriminant`（首项不为零）、`am_gm_nonnegative`（非负条件）、`finite_geometric_sum`（q=1）、`hypergeometric_point_mass`（无放回支持集）、`slope_nonvertical`（排除竖线）、`finite_quantifier_negation`（有限真假值）、`two_by_two_expected_cell`（非零期望格数）。

错误类型、零分母、越界、有害字段、未知运算都返回条件未确立或不支持；每次回答都显式 `student_step_verified=false`、`complete_theorem_certified=false`、`teacher_approved=false`。这不是通用证明器。

`scripts/build_kb_batch24_integrity.py` + `docs/evaluation/KB_BATCH24_INTEGRITY_AND_PROOFS.json` 实际从 267 历史 + 20 本批合成 287 篇在库草案，从 519 历史 + 19 本批合成 **538 条尚未形式认证步骤**；为新增步骤生成逐步哈希、审查状态及严禁学生发布的审核队列。历史 P0 127 项和冲突 10 组仍全部 OPEN。

`scripts/build_kb_batch24_progress.py` + `docs/evaluation/KB_BATCH24_COURSE_PROGRESS_MATRIX.json` 产生 **178 条逐工程主题机器审计矩阵**，按必修、选择性必修、选修 A–E 和未分配 8 个组分别列示 draft 数、题例数、未认证证明数、审核/发布状态、官方原子分母 `null`。287 篇课稿共形成 **338 条工程目录链接**（一篇可对应多个工程主题），574 道教师侧已有题例；每个工程主题虽已有草案关联，但不代表主题教学完整、课标审查完成或学生已发布。

`docs/evaluation/KB_BATCH24_SEMANTIC_COVERAGE.json` 是当轮**单独新快照**：未改写历史 Batch07/Batch23 冻结快照，23 项原有语义缺口仍 OPEN。GitHub CI 与 `scripts/mac_check.sh` 增加 Batch24 源文、来源、证明、进度四个独立 `--check` 门禁。原有快照脚本与测试修复为过滤“后续 Batch24”或断言当前 287；不能把旧 235/247/267 的历史数字随意改写。

## 5. 真正执行过的测试及失败修复

完整详细证据保留在 `evaluations/results/2026-11-08-kb-batch24/` 目录：

- `backend-initial.log`：首次全量后端 **23,067 passed，20 failed**，均为新增 Batch24 后的既有历史冻表被当作当前实时目录、以及精确 live 计数错误。明确保留原失败记录。
- `targeted-fixes-first.log`、`targeted-fixes-second.log`：先按冻结口径隔离，再独立修复。
- `backend-second.log`：**23,086 passed，1 failed**，唯一失败原因是在运行全量测试时并发修正正弦定理文本，产生一次“生成材料与已加载测试快照不一致”；已按最终源重生成并冻结，不再测试期间并行改动内容。
- `ci-gates-initial.log`、`ci-gates-second.log`、`ci-gates-third.log`、`ci-gates-fourth.log`：依次修复历史冻结快照的 Batch24 排除集，旧口径 32/52 项、旧快照 235/287 混用。
- `ci-gates-final.log`：全部 **41/41 Python 产物一致性/安全门禁通过**。
- `ci-gates-pinned-final.log`：加入冻结来源五账本内容 SHA256 校验后重新完整运行 **41/41 门禁通过**，无失败。
- `pinned-ledger-targeted.log`：对 5 份冻结来源提取账本添加**内容级 SHA256 绑定**（不是仅比对形如 64 位十六进制字符串），新增对**合法格式的伪造行哈希、标记轨道及工程目标改写**的负面攻击；专项 **800 passed，0 failed**。完整账本内容的受控变更需要显式更新固定哈希与重新审核，未验证 PDF 原始抽取忠实度。
- `mac-pinned-final.log`：新增账本哈希门禁后 **Mac Python 全量 23,088 passed / 0 failed / 1 第三方弃用警告**，同时模拟教学策略 **33/33**、检索难负例 **40/40**、Node **111/111**，结束码 0。
- 对两份旧 `evaluations/results/2026-10-15-*.json` 的自动执行时间戳变化，提交前恢复原 Git 版本；本批执行日志单独留存在 Batch24 目录，避免覆盖历史证据。
- `mac-final.log`：首次修复后的 Mac 回归，后端 **23,088 passed**，其后额外加入来源账本固定摘要检测；最终以 `mac-pinned-final.log` 为准。
- `browser-initial.log`：独立 Chrome/Playwright **15 个脚本 + 2 个 pytest 测试通过，EXIT=0**；模拟 iPad 指针不是实体 iPad 测试。只测交互和安全边界，不代表教师审核或数学内容事实认证。
- `git-network-test.log`：Mac 与 GitHub 的远端分支连接实际成功。

**此处源码内的执行记录不是教师审核签字；数学有限例题测试也不能给学生自由书写步骤自动盖章。**

## 6. 没有完成的验收条件 / 下一批

1. **K00**：对 61 页编号及非编号要求逐页做权威“条款 → 可审核原子”拆分，先把必修、选择性必修及选修 A–E 的可核验 **完整原子分母**建出来；选择性开设的 E 不得标成全国必考。单独确认 248 历史口径，否则保持“不明”。
2. **K07**：优先进行 127 项 P0 历史数学风险、19 条新增步骤，以及 10 组冲突的数学与来源独立复核，逐项保存具体定理条件、可证明范围、反例、教师审核记录。
3. **K02/K03/K04/K05/K06**：按照审计缺口进行更多必修/选必全章节新单元、题族与困难问题迁移，扩充当前已有但并非完整的 178 个工程主题，而不是继续制造未审核“覆盖率”。
4. **K08/K09**：完善学生 Agent 多轮提示不泄题及安全评测；只有真实教师批准后再讨论受限学生发布。

**本批没有关闭 K00–K09 任何未完成 issue，没有向 Tang 推送或让 Tang 执行知识建设，没有修改/合并 main，也没有绕过真实教师审核。**
