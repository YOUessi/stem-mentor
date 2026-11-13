# STEM Mentor｜Batch79 实际执行与数学验收证据（2026-11-10）

## 事实源与执行环境

- 唯一开发、内容生产和测试设备：授权 MacBook Air（`YOUTangdeMacBook-Air.local`）。
- 独立工作树：`~/Documents/文件/stem-mentor-kb-batch79`，分支 `feat/kb-batch79-proof-conditions-guard`。
- 基线：Mac Batch78 `99a0f8413604d424d98a0049095c5e1b67c5b4ae`；对应 GitHub #103 的已审核等价 Git Tree `064c9dfd14e07d8c537b4f52ccafe2688b4be349`。Batch79 须堆叠到 #103，绝不合并 main。
- Mac 主仓原有 11 项修改保留，未使用 Tang，未上传真实学生数据或教材 PDF。

## K07 × K01 × K06：本批可审查成果

- 按 Batch78 冻结来源账本 `docs/evaluation/KB_BATCH78_PROOF_DEBT_MATRIX.json`（SHA256 `da5fec7f7da73c3c9d602e9cf8b29c2ec3c943f3929196eea768d0bb3c4215d5`）对 538 条历史证明步骤做逐 ID/SHA 核对；选择其中 **12 条独立的 P0 高风险历史步骤**，不重复 Batch78 既有的 16 条。
- **12 篇原创教师审查证明卡**：AM–GM 前提与等号、二维 Cauchy–Schwarz、等比和 q≠1、复合函数定义域、Bayes 条件概率、介值存在性、抛物线焦点准线、等差和、实圆配平方、OLS 非退化、经验方差仿射变换、余弦定理三角形条件。
- 每卡有明确数学命题、全部必要前提、3 步待教师核准论证、违反前提的反例、常见错误、2 道原创教师侧题（其中一道为前提失效审查）、3 级无直接答案提示、近与远迁移；合计 **12 卡 / 24 道教师侧题 / 36 步 / 12 组失效反例 / 36 提示 / 24 迁移**。
- `backend/app/kb_batch79_math.py`：12 种受限整数/分数精确实例检查；拒绝未定义、超限、错误维数、分母 0、退化圆/三角形、OLS 零方差、伪精确浮点/布尔值和任意字符串，不使用 eval/sympify 解析学生表达式。
- `scripts/build_kb_batch79_proof_conditions.py`：关联历史每步 SHA、冻结账本 SHA、12 卡正反见证；强制 `REVIEW_PENDING` / `TEACHER_ONLY` / `NOT_FORMALLY_VERIFIED`，拒绝伪造教师签核、正式课程知识 ID、证明认证及学生发布。
- K08：专项测试用**非空批准索引混合检索**，12 卡的教师完整解答不得泄漏给学生。
- 这些 **12 条新增链接 + 16 条原有链接 = 28 条高风险审查卡**，不是 28 条一般证明已获认证。原始 538 步形式认证仍为 **0**。

## 实际 Mac 测试（证据文件均在本分支）

| 测试或检查 | 实际结果 | 原始记录 |
|---|---|---|
| Batch79 生成器回放 | EXIT 0 | `evaluations/results/2026-11-10-kb-batch79/generated_check.log` / `.exit` |
| Batch79 专项 | **2,448 passed，0 failed** | `evaluations/results/2026-11-10-kb-batch79/specialty_final.log` |
| 完整 Python | **52,272 passed，5 skipped，1 warning，0 failed** | `evaluations/results/2026-11-10-kb-batch79/mac_full_verified.log` |
| Node | **111/111 pass** | 同上 |
| Tutor 策略 | **33/33 pass** | 同上 |
| RAG 困难负例 / Top3 | **40/40、22/22 pass** | 同上 |
| 离线 Chrome/Playwright / 浏览器 pytest | **15 脚本、2 passed** | `evaluations/results/2026-11-10-kb-batch79/mac_browser_final.log` |
| Mac 完整与浏览器脚本 | **EXIT 0 / EXIT 0** | `mac_full_verified.exit` / `mac_browser_final.exit` |

2,448 项专项测试**已经包含在** 52,272 项全量 Python 通过数中，不可重复相加。Chrome 测试基于模拟 iPad 交互，不代表真实 iPad 实机验证。测试使用离线合成数据。

### 发现并修复的失败

首次专项测试 `specialty_initial_failed.log`：**12 failed / 2,352 passed**；原因为冻结账本被篡改后的 SHA 未被生成逻辑拒绝。修改生成器以重新核验冻结账本完整 SHA 后，完成负例验证并重新运行专项测试，最终 **2,448 passed**。原始失败日志保留而不是删除。

完整回归还经过冻结产物与报告更新后的多次重放：`mac_full_preprovenance.log`、`mac_full_pre_hint.log`、`mac_full_verified.log`，对应退出码均为 0。Chrome 最终重跑退出码为 0。

## 明确不能宣称的成果和剩余缺口

- **K00**：61/61页来源机器分区已覆盖，但七轨官方课程原子分母仍 **全部未知**；教师逐页完整原子化审核仍 0/61。
- **K07**：538 条历史步骤没有得到形式化定理证明；12 项仅完成带前提的编辑审查、有限实例机器见证与人审草案。10 组历史数学冲突仍未裁决。
- **K09**：真实教师批准 0，学生端深度知识发布 0。教师答案依旧不能出现在正式学生检索索引。
- **K08**：此次为规则与检索隔离回归；未进行真实模型 API 对照、真实教师验收或学生学习增益评估。

## 后续严格验收任务

1. 在 #18 中对 61 页课标逐条/跨页原子化，独立建立必修、选择性必修、选修 A–E 分母；不要将项目来源区间数视为官方知识原子数。
2. 在 #25 中处理剩余 P0 步骤的前提、例外和严格证明，保留每步的原始 SHA 与数学条件，优先审查 10 组尚未裁决的冲突。
3. 在 #26/#27 用真实且合法授权的 API 执行冻结题集与规则 baseline 对照；独立评估前提正确率、证明越权、提示泄漏、来源引用、成本和延迟。
4. 仍需真实教师签字才允许 `APPROVED`；所有卡仅 `REVIEW_PENDING`。

GitHub PR、远端 commit 与 Git Tree 经独立 GitHub 读回核实后应写入 #17/#18–#27 的本批交付评论；本地数学内容已由上述原始日志测试。
