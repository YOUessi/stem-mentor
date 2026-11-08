# STEM Mentor | Batch39 实际执行报告（2026-11-08）

## 执行环境与 GitHub 事实源

- 唯一代码/内容开发及测试机器：授权 MacBook Air，隔离 worktree `~/Documents/文件/stem-mentor-kb-batch39`；主仓 `~/Documents/文件/stem-mentor` 原始 11 项未提交修改不触碰，不使用 Tang，不调用 GPU、第三方生成 API 或真实学生数据。
- 功能分支：`feat/kb-batch39-seven-partial-closure`，基于 Batch38 Draft PR #63 的 GitHub HEAD `dfecf2536d73d22f7e2be75274557157e0427d7d`；新 Draft PR #64：https://github.com/YOUessi/stem-mentor/pull/64 ；不合并 main、不强推。
- Mac 实测源码 commit：`7457990d3b39884f3e79d57a8491d2e691e01c73`，tree `835c6ba2cb1f6bf939be6b93c1bb806b5ccf3351`。
- Mac 直接 `git -c http.version=HTTP/1.1 push` 在 90 秒后返回 `Empty reply from server`，exit 128；不据此冒充 GitHub 已收到 Mac commit。通过原生 GitHub Git 对象接口上传 **9/9 Mac 字节级一致的 Git blobs**，保留脚本 `100755` 模式；GitHub 源码 commit `7da7a41e6c8451e064b2c278a9ed389b79b17675`，远端源码 tree 与 Mac 完全相同：`835c6ba2cb1f6bf939be6b93c1bb806b5ccf3351`。

## 本批交付范围：完成剩余七条 PARTIAL_SCOPE 编辑候选的独立教师稿

先读取 Issues #17–#27 和最近 PR #63/#62/#61，确认全部 11 个 issue 仍为 OPEN。K00 官方原子化分母仍是最重阻断；上一轮冻结的 47 条历史关联中 27 条属于 `PARTIAL_SCOPE`，Batch38 已建立 20 篇独立新稿，本批补齐 **剩余七篇**（选修 C：3 篇，选修 D：4 篇）：

1. `KB33-C-P065-A005`：有限经典命题逻辑模型中的相容性、独立性与语义完备性，反例 `Σ={p}` 存在两个 q 赋值，不能推出 q 或其否定。
2. `KB33-C-P067-A004`：抽样框覆盖、非应答和测量误差的不同机制，采用四人均值（总体 25、响应 15）和恒定测量偏差 +5 说明不能混为一谈。
3. `KB33-C-P068-A004`：未随机缺失下不可识别性与分组加权的附加假设；相同响应记录可对应总体均值 5 或 55，禁止无条件称无偏恢复。
4. `KB33-D-P071-A001`：十二平均律正公比 `r^12=2` 与 `r=2^(1/12)` 的理想模型，区别等差赫兹增量和等比音程，限制现实调律推断。
5. `KB33-D-P071-A004`：固定坐标与复合顺序下水平平移、y 轴反射通常不交换；分别算出点 (2,3) 变换为 (-1,3) 与 (-3,3)，而平移 0 时交换。
6. `KB33-D-P072-A001`：针孔投影 `(fX/Z,fY/Z)` 的 Z>0 定义域、深度缩放与非保距性；对 Z=0 严格拒绝。
7. `KB33-D-P073-A002`：理想单循环图 `K_n` 边着色：偶数 n 需要 n−1 轮，奇数 n 需要 n 轮，轮转构造并逐边检查。

每篇均有前提与符号、三步有依据的论证、具体反例与错因、两道原创教师例题、定制三级非剧透提示、近远迁移和限制说明。新增合计 **7 篇独立审核稿、14 道教师例题、7 个错误反例、21 个提示阶段及 14 个迁移任务**。累计 **27/27 条 PARTIAL_SCOPE 目标都有独立补稿**，但这只是编辑审查材料，不代表 27/27 条旧关联已获得内容等价认证，更非官方课标覆盖认证。

## Schema、验证器与隔离门禁

- `scripts/author_kb_batch39_remaining.py` 以冻结的 Batch36/38 审计为输入，可复现生成 `knowledge/editorial_review/kb_batch39_remaining.jsonl`、本批完整 Markdown 讲义与 JSON 审核矩阵；`--check` 已接入 Mac `scripts/mac_check.sh` 与 GitHub CI。
- `backend/app/kb_batch39_review.py` 使用完整 ID、SHA256 固定种子、唯一性、先前编辑关联、Pydantic 严格字段检查。证明只能 `NOT_FORMALLY_CERTIFIED`；审批只能 `REVIEW_PENDING`、审核人为空；解答只能 `TEACHER_ONLY`；学生端投影为空。
- `backend/app/kb_batch39_exact.py` 实现 **7 类有限精确验证**：固定有限命题模型、响应均值差、分组权重算术、完整八度的精确频率翻倍、变换复合坐标、投影有理数、2–30 队循环赛程不重边检查。每类都包含非法前提拒绝与未知键/类型/超界负例。对真值表、分组代表性、频率比的可推广性均不作未经证明的认证。
- 以上 **不是自动形式证明、学生自由推导步骤认证、因果/抽样推断认证或教师批准**。

## Mac 实际测试记录

| 阶段 | 测试/结果 | 失败与修复 |
| --- | --- | --- |
| 首次 Batch39 专项 | 60 passed，2 failed | 1 篇针孔投影提示长度不足；八度有限运算对 440Hz 修改测试输入误用严格全局上界。修复细化提示、允许该算子受控 1000 整数范围。 |
| 修复后 Batch39 专项 | **62 passed / 0 failed** | 7 篇字段/来源/审核边界逐条验证；7 算子合法/非法/字段注入/类型等负例；2–30 队全部单循环构造校验。 |
| 完整 Python 回归 | **37,902 passed / 0 failed，1 条第三方弃用警告** | 项目虚拟环境，`cd backend && PYTHONPATH=.`。 |
| Node 测试 | **111/111 passed** | JavaScript 语法检查与 Node 全量。 |
| 教学策略评测 | **33/33 passed** | 合成例子；不等于真实教学增益。 |
| RAG 负例 / Top3 | **40/40、22/22 passed** | 冻结检索测试。 |
| Chrome/Playwright | **15 个独立脚本全部通过** | 临时合成数据库，浏览器真实 Chrome；iPad 只做触控/笔模拟。 |
| 浏览器 pytest | **2 passed** | 和上述脚本同一隔离浏览器执行。 |

- 测试日志：`evaluations/results/2026-11-08-kb-batch39/mac_full_check.log`、`browser.log`、`targeted_first.log`、`targeted_final.log`。
- Mac `scripts/mac_check.sh` 退出码 0；`scripts/mac_browser_check.sh` 退出码 0；新增校验脚本 `--check` 通过，`git diff --cached --check` 通过。
- 源码树已上传远端；最终 GitHub CI 状态以 Actions 最新运行结果为准，不将 Mac 测试混称 GitHub CI。

## 明确尚未达到的发布门槛与下一批

- 已有 287 篇深度旧稿 + 本批累计 84 篇**独立选修审核稿**均未获真实教师签署。新增与原稿不得直接混合算覆盖率；正式教师批准 **0**，学生正式发布 **0**。
- K00 必修、选择性必修、选修 A–E 七个官方知识原子分母仍为 `null`；313 条工程编辑候选不是官方分母。
- 12 条 `CLAUSE_UNVERIFIED` 关联仍需原版课标逐句核验；历史 538 条未形式认证证明步骤及 10 组冲突未解决。
- 下批先核原始课标对应页面和 12 条条款，逐条拆分编号/无编号要求、校准不同 track 的真实原子分母；随后针对 K02/K03/K04 的未覆盖知识补完整讲义、题族/反例/近远迁移，并与 K07 的逐步证明和 K08 的学生防剧透 RAG 门禁联动。维持 Draft PR 直到教师审核与全域发布条件真正满足。
