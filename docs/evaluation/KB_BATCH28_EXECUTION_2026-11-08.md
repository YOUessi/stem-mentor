# STEM Mentor｜Batch28 开发、数学条件核查与验收（2026-11-08）

## 1. GitHub 基线 / Mac 隔离边界

- **唯一开发与真实测试机器**：授权 YOUTangdeMacBook-Air.local；未在 Tang 上执行任何知识库开发/测试。
- 分支 `feat/kb-batch28-p0-math-condition-review`，独立 worktree `~/Documents/文件/stem-mentor-kb-batch28`。
- GitHub 上游为 Draft PR **#52**（Batch26）最终 HEAD `364133ad3a914766ede1ed388f7e2d64ff6c2c57`。本批 K07 与隔离工作树内正在进行的其他内容建设没有代码共享写入；不覆盖 Batch27 的未提交修改，也不更改 main 的 11 项历史未提交修改。
- 提交目标为基于 #52 的独立 Draft PR，不合并、不 force-push、不伪造教师签名。源码测试 SHA：`f243db2d8cf9c480515dd624524651430c061a1e`，最终远端 HEAD/CI 将在确认后补充。
- 无真实学生数据、无版权教材/课标 PDF 原文、无模型 API 外发；项目自编数学证明与脚本接受后续人工复核。

## 2. 核心成果：从「仅哈希存在」推进到 35 条 P0 的**原命题前提—失效反例—精确输入守卫**

上游保留 **127 条历史 P0**，先前的 SHA 比对仅证明历史文字没有被改变；本批针对原始 P0 步骤人工编写条件说明与数学反例并建立源追溯：

- **35 条不同的**原始 P0 自然语言证明步骤（按旧 claim+reason SHA 验证，不能插入未追踪步骤），关联 **17 类**具体受控数学条件检查；来自对数法则、二次判别式、AM–GM、直线与圆/两圆交点、抛物线、椭圆切线、柯西—施瓦茨、商求导、有限概率、超几何、向量夹角、数学归纳法、费马引理与点面距离。
- 为每类检查分别编写中文数学前提、失效/反例、**合法有限精确输入 + 非法边界输入**：**17 个受控正例通过、17 个非法条件被拒绝**；对大规模有限参数空间做进一步性质测试。
- 完整保留 **92 条没有本批手工条件建议的 P0**，全部 127 条原始 P0 仍 **NOT_FORMALLY_VERIFIED**。这 35 条仅有机器核实的具体输入数学事实和编辑审查建议，**并未被认证为全称命题/完整证明**。
- 在 `docs/evaluation/KB_BATCH28_MATHEMATICAL_DERIVATIONS.md` 撰写 **8 组原创分步数学论证**，明确二次方程 (a\ne0)、抛物线 (p\ne0)、柯西—施瓦茨零向量、对数分别正真数、两圆同心与重合、零测度非空事件交、商求导邻域分母、超几何支撑集等边界。
- 说明符号恒等式、有限参数算术和自然语言证明的不同证据层级，不能将数学运算测试通过视为真实专家审定。

### 对应可执行文件

- `knowledge/proof/batch28_p0_condition_profiles.json`：17 个原创条件/反例档案→35 个原 P0 步骤 ID。
- `backend/app/kb_batch28_condition_oracles.py`：17 个无任意表达式求值的有限有理数运算/定义域守卫（`VERIFIED_FINITE_INSTANCE` / `CONDITIONS_NOT_ESTABLISHED` / `UNSUPPORTED`）；四个权威布尔状态始终为 `false`。
- `scripts/build_kb_batch28_p0_evidence.py`：重验原始自然语言步骤 SHA、拒绝伪审批/重复 ID/陌生风险项/失真条件，重算报表及 `--check` CI。
- `docs/evaluation/KB_BATCH28_P0_CONDITION_REVIEW.json`：35 条具体审查任务、92 项未触及风险、审查和验证类型、冻结来源 SHA 与分别正确/非法的受控见证。
- `backend/tests/test_kb_batch28_p0_evidence.py`：标准样本、反事实/伪造/缺前提、独立 SymPy 交叉核验、有限网格性质等 **1,029 个真实通过的测试**。
- CI 和 `scripts/mac_check.sh` 都加入了可重放的数学审查源同步门禁。旧 2026-10-15 评测快照不纳入代码提交。

### 重要反例（含合法推导边界）

1. 两圆半径相同且圆心重合，公共点有无穷多个；不能因 (d=|r_1-r_2|=0) 直接说内切一点。
2. (x=-2,y=-3,a=2) 的 (xy>0)，但实数 `log(x)` 与 `log(y)` 分别未定义；仅乘积正不保证对数拆分合法。
3. 概率空间 `P(0)=P(2)=1/2, P(1)=0`，事件 `A={0,1}, B={1,2}` 的交集非空，但 (P(A\cap B)=0)，所以并集上界可以取等号。
4. 商函数求导若 `v(x0)=0`，不能对分母进行通分或将导数公式强行应用；`v(x)=x-1,x0=1` 即为拒绝案例。
5. 向量 `v=0` 时不能以 `||v||²` 作分母，但柯西—施瓦茨本身仍成立；必须将零向量退化情形与代数证明分开。

## 3. Mac 真实测试与错误修复

所有结果来自独立 Batch28 worktree 的执行，不使用 GitHub CI 结果反推本地测试。

| 检验 | 最终实际结果 |
|---|---|
| Batch28 定向 pytest | **1,029 passed** |
| Mac 后端全量 pytest（含历史回归） | **26,262 passed, 0 failed, 1 第三方 warning，86.78 秒** |
| Node | **111/111 passed** |
| Tutor 策略 | **33/33 passed** |
| 检索困难负例 | **40/40 passed；Top3 22/22** |
| CI 审计生成脚本（含新 Batch28） | **均通过** |
| Chrome/Playwright 浏览器 | `15 个 Chrome/Playwright 脚本通过 + 浏览器 pytest 2 passed；完整脚本退出码 0（iPad 仅指针模拟，并非真机）` |
| 远端 GitHub Actions | `源码提交 GitHub Actions [#42439940636](https://github.com/YOUessi/stem-mentor/actions/runs/42439940636) 已核实 completed/success；最终报告提交的 CI 须独立复核` |

终态日志：
- `evaluations/results/2026-11-08-kb-batch28/python-targeted.log`；
- `evaluations/results/2026-11-08-kb-batch28/mac-check.log`；
- `evaluations/results/2026-11-08-kb-batch28/browser.log`；
- `evaluations/results/2026-11-08-kb-batch28/initial-failures-and-fixes.md`。

实际失败与修复均如实记录：首次使用系统 Python 缺 `pydantic`，切到现有 Mac 项目 `.venv`；首次文案长度门禁过高，校正具体数学说明最低长度；点面距离算子错误地将三个向量解包为两变量，修正并复测；首次 pytest 未设置 `PYTHONPATH` 导致 `app` 不可导入，使用仓库 CI 的标准 `backend + PYTHONPATH=.` 命令后 1,029 全通过。所有失败属于编写期间被发现并修复的软件/环境错误，**不能据此宣称 35 条原始自然语言证明已获认证**。

## 4. 当前未完成的完整知识库门槛

- 深度讲义草案：**287**（**本批新增 0**）；全部 `REVIEW_PENDING` 且教师解答 `TEACHER_ONLY`。
- 证明总队列：**538 条未形式认证**；历史 P0 **127 条**（本批仅有 **35 条**新增具体编辑条件资料，**0 条正式证明认证**），10 组历史冲突仍未由独立专家裁决。
- 先修图：Batch26 提出 31 个待审链接，133 个原无显式链接，其中 102 个尚无候选；本批不篡改老师未审核的先修边。
- 课程 K00：官方课标 61 页机器抽取有 **315 vs 317 编号位置漂移**，仍缺少逐原页图文/未编号条款拆分与真实核验；必修、选择性必修、选修 A–E 官方知识原子分母全部为 `null`，不能以工程 178 主题、287 草案或编号出现次数替代。
- 教师真实批准：**0**，学生正式深度知识发布：**0**。学生自由解题步骤验证没有因为有限 oracle 运行而变更。
- K08 学生知识检索不从新 `knowledge/proof/` 读取任何待审专家档案；本批只是编辑/CI 侧审查证据，不对学生开放 P0 解法。

## 5. 下一批应继续的依赖任务

K07 按同样严格的原文 SHA/数学条件/反例/独立检查模板审查剩余 **92** 条历史 P0，并对 10 组冲突开展原命题条件比较与外部数学审查，而不是新增更多仅形式漂亮的自然语言结论。K00 仍要逐页完成官方要求与选修 A–E 未编号原子拆分，特别是印刷页 52 的两条提取差异。K01/K02–K06 需继续全章节教学内容、题族、先修和 near/far 迁移的系统性建设，并严格防止只拿深度草案数字冒充已审核全量覆盖。K08/K09 延续学生防剧透与正式教师审核的硬门禁。全部 Issues #17–#27 仍为 OPEN，PR 保留 Draft。

## 6. GitHub 事实源与远端审计

- 实际 Mac 测试源码提交：`f243db2d8cf9c480515dd624524651430c061a1e`
- 最终远端 Draft PR：`https://github.com/YOUessi/stem-mentor/pull/53`
- 最终 GitHub HEAD：`源码 commit f243db2d8cf9c480515dd624524651430c061a1e 已推送并核实；追加报告的最终 commit 请以 PR #53 最新 HEAD 和 Issues 记录为准`
- CI 状态及链接：`源码提交 GitHub Actions [#42439940636](https://github.com/YOUessi/stem-mentor/actions/runs/42439940636) 已核实 completed/success；最终报告提交的 CI 须独立复核`

以上占位符只会在远端实际提交与验证后更新，不能猜测 PR 或 CI 结果。
